"""Research Notebook — persönliches, dreisprachiges (DE/EN/PL) Recherche-Notizbuch, gegliedert in Themen:
Werte & Befunde, Begriffe, Medikamente, Recherche, Studien, Videos, Chat — mit KI-Unterstützung und MCP-Schnittstelle.

Konfiguration ausschließlich über Umgebungsvariablen (siehe .env.example) und die Einstellungen in der Oberfläche.
"""
import contextvars
import json
import os
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import uuid

import httpx
from fastapi import FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

DB = Path(os.environ.get("MAPPE_DB", "/data/mappe.sqlite3"))
STATIC = Path(__file__).parent / "static"
SEED = Path(__file__).parent / "seed.json"
CLAUDE_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("CLAUDE_MODEL") or os.environ.get("MODEL", "claude-sonnet-5")
# Eingebaute Anmeldung (HTTP Basic). Leer lassen nur, wenn ein vorgeschalteter Proxy die Anmeldung übernimmt.
APP_USER = os.environ.get("APP_USER", "admin")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")
# Öffentliche Adresse für die MCP-Links in den Einstellungen; ohne Angabe aus der Anfrage abgeleitet.
PUBLIC_URL = os.environ.get("PUBLIC_URL", "").rstrip("/")
# Beispielinhalte (Thema „Brustgesundheit“ mit Begriffen, Medikamenten, Quellen) nur auf Wunsch bei leerer Datenbank.
EXAMPLE_DATA = os.environ.get("EXAMPLE_DATA", "").lower() in ("1", "true", "yes", "ja")
LANGS = ("de", "en", "pl")
KINDS = ("finding", "value", "glossary", "med", "research", "analysis", "video", "study", "medplan")
THUMBS = DB.parent / "thumbs"
FILES = DB.parent / "files"
MAX_BYTES = 30 * 1024 * 1024
# Befunde kommen als PDF oder als Handyfoto; anderes wird abgelehnt
ERLAUBT = {
    ".pdf": "application/pdf", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".heic": "image/heic", ".heif": "image/heif", ".webp": "image/webp", ".csv": "text/csv",
}

app = FastAPI(title="Research Notebook")

if APP_PASSWORD:
    import base64 as _b64
    import secrets as _secrets

    @app.middleware("http")
    async def anmeldung(request, call_next):
        pfad = request.url.path
        # /healthz für Überwachung, /mcp/<schlüssel> hat eigene Anmeldung über den Schlüssel im Pfad
        if pfad == "/healthz" or pfad.startswith("/mcp/"):
            return await call_next(request)
        kopf = request.headers.get("authorization", "")
        if kopf.lower().startswith("basic "):
            try:
                user, _, pw = _b64.b64decode(kopf[6:]).decode("utf-8").partition(":")
                if _secrets.compare_digest(user.encode(), APP_USER.encode()) and _secrets.compare_digest(pw.encode(), APP_PASSWORD.encode()):
                    return await call_next(request)
            except (ValueError, UnicodeDecodeError):
                pass
            import asyncio
            await asyncio.sleep(0.8)  # bremst das Durchprobieren von Passwörtern
        return Response(status_code=401, headers={"WWW-Authenticate": 'Basic realm="Research Notebook", charset="UTF-8"'})


@contextmanager
def db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def jetzt():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def protokoll(text):
    """Jede Zeile beginnt mit Zeitstempel — so lässt sich das Protokoll filtern und überwachen."""
    with open(DB.parent / "protokoll.log", "a") as f:
        f.write(f"{jetzt()} {text}\n")


@app.on_event("startup")
def start():
    with db() as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                data TEXT NOT NULL,
                created TEXT NOT NULL,
                updated TEXT NOT NULL)"""
        )
        con.execute(
            """CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                entry_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                mime TEXT NOT NULL,
                size INTEGER NOT NULL,
                created TEXT NOT NULL)"""
        )
        con.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        con.execute("""CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, messages TEXT NOT NULL,
            created TEXT NOT NULL, updated TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT NOT NULL, position INTEGER NOT NULL DEFAULT 0,
            created TEXT NOT NULL, updated TEXT NOT NULL)""")
        for tabelle in ("entries", "chats"):
            spalten = [r["name"] for r in con.execute(f"PRAGMA table_info({tabelle})")]
            if "topic_id" not in spalten:
                con.execute(f"ALTER TABLE {tabelle} ADD COLUMN topic_id INTEGER")
                protokoll(f"Spalte topic_id in {tabelle} ergänzt")
        if not con.execute("SELECT 1 FROM topics").fetchone():
            # Erstes Thema: neutral — oder das Beispielthema, wenn Beispielinhalte gewünscht sind
            erstes_thema = BEISPIEL_THEMA if (EXAMPLE_DATA and SEED.exists()) else ERSTES_THEMA
            con.execute("INSERT INTO topics (data, position, created, updated) VALUES (?,?,?,?)",
                        (json.dumps(erstes_thema, ensure_ascii=False), 0, jetzt(), jetzt()))
            protokoll("Thema 1 angelegt (bisheriger Inhalt)")
        erstes = con.execute("SELECT id FROM topics ORDER BY position, id LIMIT 1").fetchone()["id"]
        for tabelle in ("entries", "chats"):
            n = con.execute(f"UPDATE {tabelle} SET topic_id=? WHERE topic_id IS NULL", (erstes,)).rowcount
            if n:
                protokoll(f"{n} {tabelle} dem Thema #{erstes} zugeordnet")
        if not con.execute("SELECT 1 FROM settings WHERE key='mig_studies'").fetchone():
            for r in con.execute("SELECT id, data FROM topics").fetchall():
                d = json.loads(r["data"])
                if "studies" not in d.get("sections", []):
                    d["sections"] = [b for b in BEREICHE if b in d.get("sections", []) + ["studies"]]
                    con.execute("UPDATE topics SET data=? WHERE id=?", (json.dumps(d, ensure_ascii=False), r["id"]))
            con.execute("INSERT INTO settings (key, value) VALUES ('mig_studies', ?)", (jetzt(),))
            protokoll("Bereich Studien bei bestehenden Themen eingeschaltet")
        leer = con.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 0
        if leer and EXAMPLE_DATA and SEED.exists():
            for e in json.loads(SEED.read_text()):
                con.execute(
                    "INSERT INTO entries (kind, data, created, updated, topic_id) VALUES (?,?,?,?,?)",
                    (e["kind"], json.dumps(e["data"], ensure_ascii=False), jetzt(), jetzt(), erstes),
                )
            protokoll("Startinhalte eingespielt")
    if not APP_PASSWORD:
        print("HINWEIS: APP_PASSWORD ist nicht gesetzt — das Notebook ist ohne Anmeldung erreichbar. "
              "Nur so betreiben, wenn ein vorgeschalteter Proxy die Anmeldung übernimmt.", flush=True)
    # Tägliche Sicherung beim Start und über /api/export — einfache Kopie, 14 Stück
    sicherung()


def sicherung():
    if not DB.exists():
        return
    ziel = DB.parent / "backup"
    ziel.mkdir(exist_ok=True)
    datei = ziel / f"mappe-{datetime.now():%Y-%m-%d}.sqlite3"
    if not datei.exists():
        shutil.copy2(DB, datei)
    for alt in sorted(ziel.glob("mappe-*.sqlite3"))[:-14]:
        alt.unlink()


def anhaenge(con, eid):
    rows = con.execute("SELECT id, name, mime, size, created FROM files WHERE entry_id=? ORDER BY created", (eid,))
    return [dict(r) for r in rows]


def zeile(r, con=None):
    e = {"id": r["id"], "kind": r["kind"], "data": json.loads(r["data"]), "topic_id": r["topic_id"] if "topic_id" in r.keys() else None,
         "created": r["created"], "updated": r["updated"], "files": []}
    if con is not None:
        e["files"] = anhaenge(con, r["id"])
    return e


class Entry(BaseModel):
    kind: str
    data: dict
    topic_id: int | None = None


# ---------------------------------------------------------------------------
# Themen: oberste Ebene. Jedes Thema hat eigene Unterbereiche, eigene Einträge und Chats.
# Das aktuelle Thema einer Anfrage steckt in einer ContextVar — so bekommen KI-Aufträge,
# Kontext und Prompts das richtige Thema, ohne dass jede Funktion es durchreichen muss.
# ---------------------------------------------------------------------------

BEREICHE = ["values", "glossary", "med", "research", "studies", "chat", "videos"]
ERSTES_THEMA = {"name": {"de": "Mein erstes Thema", "en": "My first topic", "pl": "Mój pierwszy temat"},
                "desc": {"de": "Umbenennen und Unterbereiche wählen: ⚙ neben dem Thema",
                         "en": "Rename and choose sections: ⚙ next to the topic",
                         "pl": "Zmień nazwę i wybierz sekcje: ⚙ obok tematu"},
                "kind": "general", "sections": BEREICHE[:], "context": ""}
BEISPIEL_THEMA = {"name": {"de": "Brustgesundheit", "en": "Breast health", "pl": "Zdrowie piersi"},
                "desc": {"de": "Befunde, Werte, Therapie und Wissen rund um die Erkrankung",
                         "en": "Findings, values, treatment and knowledge about the illness",
                         "pl": "Wyniki, leczenie i wiedza o chorobie"},
                "kind": "health", "sections": BEREICHE[:], "context": "Brustkrebs (Mammakarzinom)"}
THEMA = contextvars.ContextVar("thema", default=None)


def thema_zeile(r, con=None):
    t = {"id": r["id"], **json.loads(r["data"]), "position": r["position"]}
    if con is not None:
        t["counts"] = {k: n for k, n in con.execute("SELECT kind, COUNT(*) FROM entries WHERE topic_id=? GROUP BY kind", (r["id"],))}
        t["counts"]["chat"] = con.execute("SELECT COUNT(*) FROM chats WHERE topic_id=?", (r["id"],)).fetchone()[0]
    return t


def thema_laden(tid=None):
    with db() as con:
        r = None
        if tid not in (None, ""):
            try:
                r = con.execute("SELECT * FROM topics WHERE id=?", (int(tid),)).fetchone()
            except (TypeError, ValueError):
                r = con.execute("SELECT * FROM topics").fetchall()
                r = next((x for x in r if str(tid).lower() in json.dumps(json.loads(x["data"]).get("name"), ensure_ascii=False).lower()), None)
            if r is None:
                raise HTTPException(404, "Thema nicht gefunden")
        else:
            r = con.execute("SELECT * FROM topics ORDER BY position, id LIMIT 1").fetchone()
        return thema_zeile(r)


def thema_setzen(tid=None):
    t = thema_laden(tid)
    THEMA.set(t)
    return t


def thema():
    return THEMA.get() or thema_setzen()


def thema_name(lang="de"):
    t = thema()
    return (t.get("name") or {}).get(lang) or (t.get("name") or {}).get("de") or "Thema"


def thema_bezug():
    """Wofür die KI das Thema hält: eigener Fachkontext, sonst Name + Beschreibung."""
    t = thema()
    return t.get("context") or thema_name() + (f" ({t['desc'].get('de')})" if (t.get("desc") or {}).get("de") else "")


def ist_gesundheit():
    return thema().get("kind") == "health"


class ThemaDaten(BaseModel):
    name: str
    desc: str = ""
    kind: str = "general"
    sections: list[str] = BEREICHE
    context: str = ""
    lang: str = "de"


@app.get("/api/topics")
def themen():
    with db() as con:
        return [thema_zeile(r, con) for r in con.execute("SELECT * FROM topics ORDER BY position, id")]


def _thema_daten(t: ThemaDaten, alt=None):
    if not t.name.strip():
        raise HTTPException(400, "Bitte einen Namen angeben.")
    abschnitte = [b for b in BEREICHE if b in t.sections] or ["research"]
    felder = uebersetzen(Uebersetzen(source=t.lang if t.lang in LANGS else "de",
                                     fields={"name": t.name.strip(), **({"desc": t.desc.strip()} if t.desc.strip() else {})}))["fields"]
    d = dict(alt or {})
    d.update({"name": felder.get("name") or {l: t.name.strip() for l in LANGS},
              "desc": felder.get("desc") or {l: "" for l in LANGS},
              "kind": "health" if t.kind == "health" else "general", "sections": abschnitte,
              "context": t.context.strip()[:300]})
    return d


@app.post("/api/topics")
def thema_neu(t: ThemaDaten):
    d = _thema_daten(t)
    with db() as con:
        pos = (con.execute("SELECT MAX(position) FROM topics").fetchone()[0] or 0) + 1
        cur = con.execute("INSERT INTO topics (data, position, created, updated) VALUES (?,?,?,?)",
                          (json.dumps(d, ensure_ascii=False), pos, jetzt(), jetzt()))
        out = thema_zeile(con.execute("SELECT * FROM topics WHERE id=?", (cur.lastrowid,)).fetchone(), con)
    protokoll(f"Thema neu #{out['id']}: {d['name'].get('de')}")
    return out


@app.put("/api/topics/{tid}")
def thema_aendern(tid: int, t: ThemaDaten):
    with db() as con:
        r = con.execute("SELECT * FROM topics WHERE id=?", (tid,)).fetchone()
        if not r:
            raise HTTPException(404, "Thema nicht gefunden")
        d = _thema_daten(t, json.loads(r["data"]))
        con.execute("UPDATE topics SET data=?, updated=? WHERE id=?", (json.dumps(d, ensure_ascii=False), jetzt(), tid))
        out = thema_zeile(con.execute("SELECT * FROM topics WHERE id=?", (tid,)).fetchone(), con)
    protokoll(f"Thema geändert #{tid}")
    return out


@app.delete("/api/topics/{tid}")
def thema_loeschen(tid: int):
    with db() as con:
        if con.execute("SELECT COUNT(*) FROM topics").fetchone()[0] <= 1:
            raise HTTPException(409, "Das letzte Thema kann nicht gelöscht werden.")
        n = con.execute("SELECT COUNT(*) FROM entries WHERE topic_id=?", (tid,)).fetchone()[0]
        c = con.execute("SELECT COUNT(*) FROM chats WHERE topic_id=?", (tid,)).fetchone()[0]
        if n or c:
            raise HTTPException(409, f"Das Thema enthält noch {n} Einträge und {c} Chats. Bitte zuerst leeren — so geht nichts versehentlich verloren.")
        con.execute("DELETE FROM topics WHERE id=?", (tid,))
    protokoll(f"Thema gelöscht #{tid}")
    return {"ok": True}


@app.get("/healthz")
def healthz():
    with db() as con:
        n = con.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    return {"ok": True, "eintraege": n, "uebersetzung": bool(CLAUDE_KEY)}


@app.get("/api/entries")
def liste(topic: int | None = None):
    sicherung()
    with db() as con:
        if topic is None:
            rows = con.execute("SELECT * FROM entries ORDER BY updated DESC").fetchall()
        else:
            rows = con.execute("SELECT * FROM entries WHERE topic_id=? ORDER BY updated DESC", (topic,)).fetchall()
        alle = {}
        for f in con.execute("SELECT id, entry_id, name, mime, size, created FROM files ORDER BY created"):
            alle.setdefault(f["entry_id"], []).append({k: f[k] for k in ("id", "name", "mime", "size", "created")})
    out = [zeile(r) for r in rows]
    for e in out:
        e["files"] = alle.get(e["id"], [])
    return out


@app.post("/api/entries")
def neu(e: Entry):
    if e.kind not in KINDS:
        raise HTTPException(400, "Unbekannte Art")
    with db() as con:
        tid = e.topic_id or thema()["id"]
        cur = con.execute(
            "INSERT INTO entries (kind, data, created, updated, topic_id) VALUES (?,?,?,?,?)",
            (e.kind, json.dumps(e.data, ensure_ascii=False), jetzt(), jetzt(), tid),
        )
        r = con.execute("SELECT * FROM entries WHERE id=?", (cur.lastrowid,)).fetchone()
        out = zeile(r, con)
    protokoll(f"neu {e.kind} #{cur.lastrowid} (Thema #{tid})")
    return out


@app.put("/api/entries/{eid}")
def aendern(eid: int, e: Entry):
    with db() as con:
        cur = con.execute(
            "UPDATE entries SET data=?, updated=? WHERE id=?",
            (json.dumps(e.data, ensure_ascii=False), jetzt(), eid),
        )
        if cur.rowcount == 0:
            raise HTTPException(404, "Eintrag nicht gefunden")
        r = con.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone()
        out = zeile(r, con)
    protokoll(f"geändert {e.kind} #{eid}")
    return out


@app.delete("/api/entries/{eid}")
def loeschen(eid: int):
    with db() as con:
        r = con.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone()
        if not r:
            raise HTTPException(404, "Eintrag nicht gefunden")
        # Gelöschtes bleibt im Protokoll lesbar, falls es doch noch gebraucht wird
        protokoll(f"gelöscht {r['kind']} #{eid}: {r['data']}")
        for f in con.execute("SELECT * FROM files WHERE entry_id=?", (eid,)).fetchall():
            beiseite(f)
        con.execute("DELETE FROM files WHERE entry_id=?", (eid,))
        con.execute("DELETE FROM entries WHERE id=?", (eid,))
    return {"ok": True}


def datei_pfad(fid, name):
    return FILES / (fid + Path(name).suffix.lower())


def beiseite(f):
    """Gelöschte Dateien wandern nach files/geloescht/ statt weg — Befunde sind schwer wiederzubeschaffen."""
    quelle = datei_pfad(f["id"], f["name"])
    if quelle.exists():
        ziel = FILES / "geloescht"
        ziel.mkdir(parents=True, exist_ok=True)
        quelle.rename(ziel / f"{f['id']}-{Path(f['name']).name}")
    protokoll(f"Datei beiseitegelegt {f['id']} ({f['name']}) von Eintrag #{f['entry_id']}")


@app.post("/api/entries/{eid}/files")
async def hochladen(eid: int, datei: UploadFile = File(...)):
    return datei_speichern(eid, datei.filename, await datei.read(MAX_BYTES + 1))


def datei_speichern(eid, dateiname, inhalt):
    name = Path(dateiname or "datei").name[:150]
    endung = Path(name).suffix.lower()
    if endung not in ERLAUBT:
        raise HTTPException(415, "Nur PDF, Bilder (JPG, PNG, HEIC, WEBP) oder CSV")
    if len(inhalt) > MAX_BYTES:
        raise HTTPException(413, "Datei größer als 30 MB")
    if endung == ".pdf" and not inhalt.startswith(b"%PDF"):
        raise HTTPException(415, "Die Datei ist kein gültiges PDF")
    with db() as con:
        if not con.execute("SELECT 1 FROM entries WHERE id=?", (eid,)).fetchone():
            raise HTTPException(404, "Eintrag nicht gefunden")
        fid = uuid.uuid4().hex
        FILES.mkdir(parents=True, exist_ok=True)
        datei_pfad(fid, name).write_bytes(inhalt)
        con.execute("INSERT INTO files (id, entry_id, name, mime, size, created) VALUES (?,?,?,?,?,?)",
                    (fid, eid, name, ERLAUBT[endung], len(inhalt), jetzt()))
        con.execute("UPDATE entries SET updated=? WHERE id=?", (jetzt(), eid))
        r = con.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone()
        out = zeile(r, con)
    protokoll(f"Datei hochgeladen {fid} ({name}, {len(inhalt)} B) an Eintrag #{eid}")
    return out


@app.get("/api/files/{fid}")
def datei_holen(fid: str, download: int = 0):
    with db() as con:
        f = con.execute("SELECT * FROM files WHERE id=?", (fid,)).fetchone()
    if not f or not datei_pfad(fid, f["name"]).exists():
        raise HTTPException(404, "Datei nicht gefunden")
    return FileResponse(datei_pfad(fid, f["name"]), media_type=f["mime"], filename=f["name"],
                        content_disposition_type="attachment" if download else "inline",
                        headers={"Cache-Control": "private, max-age=3600", "X-Content-Type-Options": "nosniff"})


@app.delete("/api/files/{fid}")
def datei_loeschen(fid: str):
    with db() as con:
        f = con.execute("SELECT * FROM files WHERE id=?", (fid,)).fetchone()
        if not f:
            raise HTTPException(404, "Datei nicht gefunden")
        beiseite(f)
        con.execute("DELETE FROM files WHERE id=?", (fid,))
        r = con.execute("SELECT * FROM entries WHERE id=?", (f["entry_id"],)).fetchone()
        out = zeile(r, con) if r else None
    return out or {"ok": True}


@app.get("/api/export")
def export():
    with db() as con:
        rows = con.execute("SELECT * FROM entries ORDER BY id").fetchall()
        daten = [zeile(r, con) for r in rows]
    name = f"research-notebook-{datetime.now():%Y-%m-%d}.json"
    return JSONResponse(daten,
                        headers={"Content-Disposition": f'attachment; filename="{name}"'})


class Uebersetzen(BaseModel):
    source: str
    fields: dict  # {feldname: text}
    topic: int | None = None


@app.post("/api/translate")
def uebersetzen(u: Uebersetzen):
    """Übersetzt die Felder in die beiden anderen Sprachen. Ohne Schlüssel: Text bleibt wie er ist."""
    if u.topic is not None:
        thema_setzen(u.topic)
    texte = {k: v for k, v in u.fields.items() if isinstance(v, str) and v.strip()}
    ziele = [l for l in LANGS if l != u.source]
    if not texte:
        return {"fields": {}, "translated": False}
    if ki_konfig()["openai_key"]:
        try:
            out = openai_json(
                "Übersetze diese Felder eines persönlichen Notizbuchs (Thema: " + thema_bezug() + ") aus dem " + NAMEN[u.source]
                + " in alle drei Sprachen (de, en, pl; die Ausgangssprache unverändert übernehmen). Nichts ergänzen, "
                "nichts weglassen, Zeilenumbrüche beibehalten. Antworte als Liste in derselben Reihenfolge.\n\n"
                + json.dumps(list(texte.values()), ensure_ascii=False),
                schema(items={"type": "array", "items": i18n_schema()}), schnell=True)
            aus = {}
            for (k, v), t in zip(texte.items(), out["items"]):
                aus[k] = {l: (v if l == u.source else (t.get(l) or v)) for l in LANGS}
            if len(aus) == len(texte):
                return {"fields": aus, "translated": True}
        except HTTPException as ex:
            protokoll(f"Übersetzung per OpenAI gescheitert, nehme Claude: {ex.detail}")
    if not CLAUDE_KEY:
        return {"fields": {k: {l: v for l in LANGS} for k, v in texte.items()}, "translated": False}
    namen = {"de": "Deutsch", "en": "Englisch", "pl": "Polnisch"}
    auftrag = (
        "Du übersetzt Notizen eines persönlichen Notizbuchs zum Thema " + thema_bezug() + ". "
        f"Ausgangssprache: {namen[u.source]}. Übersetze jedes Feld nach "
        + " und ".join(f"{namen[l]} ({l})" for l in ziele)
        + ". Medikamenten- und Wirkstoffnamen, Laborkürzel, Zahlen, Einheiten und URLs unverändert lassen; "
        "medizinische Fachbegriffe so wiedergeben, wie Ärzte im jeweiligen Land sie verwenden. "
        "Nichts ergänzen, nichts weglassen, Zeilenumbrüche beibehalten. "
        'Antworte NUR mit JSON in der Form {"feld": {"' + '": "...", "'.join(ziele) + '": "..."}}.\n\n'
        + json.dumps(texte, ensure_ascii=False)
    )
    try:
        r = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": CLAUDE_KEY, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": MODEL, "max_tokens": 8000,
                  # Sonnet 5 denkt sonst von selbst und verbraucht das Token-Budget vor dem JSON
                  "thinking": {"type": "disabled"},
                  "messages": [{"role": "user", "content": auftrag}]},
            timeout=90,
        )
        r.raise_for_status()
        text = "".join(b.get("text", "") for b in r.json()["content"] if b.get("type") == "text")
        start, ende = text.find("{"), text.rfind("}")
        roh = json.loads(text[start:ende + 1])
    except Exception as ex:  # noqa: BLE001 — Übersetzung ist Komfort, Speichern muss trotzdem gehen
        protokoll(f"FEHLER Übersetzung: {ex}")
        return {"fields": {k: {l: v for l in LANGS} for k, v in texte.items()},
                "translated": False, "error": "Übersetzung fehlgeschlagen"}
    aus = {}
    for k, v in texte.items():
        t = roh.get(k) or {}
        aus[k] = {l: (v if l == u.source else (t.get(l) or v)) for l in LANGS}
    return {"fields": aus, "translated": True}


# ---------------------------------------------------------------------------
# Einstellungen & KI (OpenAI)
# ---------------------------------------------------------------------------

DEFAULTS = {"model": "gpt-5.5", "model_fast": "gpt-5.4-mini", "web_search": "1"}
NAMEN = {"de": "Deutsch", "en": "Englisch", "pl": "Polnisch"}
# Gleiche Schlüssel wie PARAMS in static/app.js
PARAM_NAMEN = {"leuko": "Leukozyten", "neutro": "Neutrophile (absolut)", "hb": "Hämoglobin", "thrombo": "Thrombozyten",
               "alt": "ALT (GPT)", "ast": "AST (GOT)", "ggt": "Gamma-GT", "krea": "Kreatinin", "ca153": "CA 15-3",
               "cea": "CEA", "vitd": "Vitamin D (25-OH)", "lvef": "LVEF (Herz-Echo)", "weight": "Körpergewicht",
               "b12": "Vitamin B12", "ferritin": "Ferritin", "hba1c": "HbA1c", "ldl": "LDL-Cholesterin", "tsh": "TSH",
               "bp_sys": "Blutdruck systolisch", "bp_dia": "Blutdruck diastolisch", "pulse": "Puls", "glucose": "Blutzucker"}
OPENAI = "https://api.openai.com/v1"

def system_text():
    if not ist_gesundheit():
        return (
            f"Du bist eine sorgfältige Recherche-Assistenz in einem persönlichen, dreisprachigen Notizbuch (Deutsch, Englisch, "
            f"Polnisch). Das aktuelle Thema heißt „{thema_name()}“: {thema_bezug()}. Arbeite sachlich, verständlich und belegt, "
            "trenne gesicherte Fakten von Einschätzungen und benenne Unsicherheiten offen. Bei rechtlichen, finanziellen oder "
            "sicherheitsrelevanten Fragen weise darauf hin, wann eine Fachperson nötig ist. Schreibe Fließtexte in leichtem Markdown: "
            "Zwischenüberschriften mit '## ', Listen mit '- ', Hervorhebung mit **…**. Eigennamen, Zahlen und Einheiten bleiben "
            "in allen Sprachen gleich."
        )
    return SYSTEM.replace("{THEMA}", f"„{thema_name()}“ ({thema_bezug()})")


# Gilt für alle Themen der Art „Gesundheit“ — nichts Krankheitsspezifisches hier hineinschreiben.
# Den Fachbezug (z. B. „Brustkrebs (Mammakarzinom)“) liefert allein das Thema über thema_bezug().
SYSTEM = (
    "Du bist eine medizinisch versierte Assistenz in einem persönlichen, dreisprachigen Notizbuch "
    "(Deutsch, Englisch, Polnisch), in dem Menschen ihre Gesundheitsfragen sammeln. Das aktuelle Thema ist {THEMA}. "
    "Beziehe dich ausschließlich auf dieses Thema und den Inhalt des Notizbuchs zu diesem Thema. Übertrage keine "
    "Annahmen aus anderen Erkrankungen, Therapien oder Behandlungssituationen (etwa Chemotherapie, Krebs, Operationen), "
    "wenn sie im Thema oder im Notizbuch nicht vorkommen — frag lieber nach. "
    "Arbeite sachlich, verständlich und zugewandt, auf dem Stand der aktuellen Leitlinien und Empfehlungen der für dieses "
    "Thema zuständigen Fachgesellschaften (in Deutschland z. B. AWMF-Leitlinien, DGE, RKI; international WHO, ESMO u. a.; "
    "in Polen die jeweiligen Fachgesellschaften). "
    "Du darfst Befunde und Werte einordnen und mögliche Bedeutungen oder Verdachtsdiagnosen nennen, "
    "kennzeichnest sie aber immer als Einschätzung, die Ärztinnen und Ärzte bestätigen müssen, "
    "und benennst Unsicherheiten offen. Empfiehl nie eigenmächtige Dosisänderungen oder das Absetzen von Medikamenten. "
    "Nenne Warnzeichen, die ärztlich abgeklärt werden müssen, nur soweit sie zu diesem Thema und zur Lage im Notizbuch passen. "
    "Schreibe Fließtexte in leichtem Markdown: Zwischenüberschriften mit '## ', Listen mit '- ', Hervorhebung mit **…**. "
    "Medikamentennamen, Laborkürzel, Zahlen und Einheiten bleiben in allen Sprachen gleich; Fachbegriffe so, "
    "wie Ärztinnen und Ärzte im jeweiligen Land sie verwenden."
)


def einstellung(con, key):
    r = con.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return r["value"] if r else DEFAULTS.get(key, "")


def ki_konfig():
    with db() as con:
        return {k: einstellung(con, k) for k in ("openai_key", "model", "model_fast", "web_search")}


def i18n_schema():
    return {"type": "object", "additionalProperties": False, "required": list(LANGS),
            "properties": {l: {"type": "string"} for l in LANGS}}


def schema(**felder):
    return {"type": "object", "additionalProperties": False, "required": list(felder), "properties": felder}


QUELLEN = {"type": "array", "items": schema(title={"type": "string"}, url={"type": "string"})}


def openai_json(auftrag, antwort_schema, *, schnell=False, web=False, dateien=None, aufwand="medium"):
    """Ein Aufruf der Responses-API mit strukturierter Antwort. Fehler gehen als HTTPException an die Oberfläche."""
    k = ki_konfig()
    if not k["openai_key"]:
        raise HTTPException(400, "Kein OpenAI-Schlüssel hinterlegt — bitte unter Einstellungen eintragen.")
    inhalt = [{"type": "input_text", "text": auftrag}] + (dateien or [])
    body = {
        "model": k["model_fast"] if schnell else k["model"],
        "instructions": system_text(),
        "input": [{"role": "user", "content": inhalt}],
        "text": {"format": {"type": "json_schema", "name": "antwort", "strict": True, "schema": antwort_schema}},
    }
    if web and k["web_search"] == "1":
        body["tools"] = [{"type": "web_search"}]
    if not schnell and body["model"].startswith(("gpt-5", "o")):
        body["reasoning"] = {"effort": aufwand}
    try:
        r = httpx.post(f"{OPENAI}/responses", json=body, timeout=300,
                       headers={"Authorization": f"Bearer {k['openai_key']}"})
    except httpx.HTTPError as ex:
        protokoll(f"FEHLER OpenAI nicht erreichbar: {ex}")
        raise HTTPException(502, "OpenAI ist gerade nicht erreichbar. Bitte später erneut versuchen.")
    d = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    if r.status_code != 200 or d.get("error"):
        msg = (d.get("error") or {}).get("message") or f"HTTP {r.status_code}"
        protokoll(f"FEHLER OpenAI: {msg}")
        if r.status_code == 401:
            raise HTTPException(400, "OpenAI lehnt den Schlüssel ab. Bitte unter Einstellungen prüfen.")
        raise HTTPException(502, f"OpenAI meldet: {msg}")
    text = ""
    for o in d.get("output", []):
        for c in o.get("content") or []:
            if c.get("type") == "output_text":
                text += c.get("text", "")
    try:
        out = json.loads(text)
    except ValueError:
        protokoll(f"FEHLER OpenAI-Antwort kein JSON ({d.get('status')}): {text[:200]}")
        raise HTTPException(502, "Die KI-Antwort war unvollständig. Bitte erneut versuchen.")
    u = d.get("usage") or {}
    protokoll(f"KI {body['model']} web={bool(body.get('tools'))} in={u.get('input_tokens')} out={u.get('output_tokens')}")
    out["_model"] = body["model"]
    return out


FORMEN = {"tablet": "Tablette", "capsule": "Kapsel", "drops": "Tropfen", "liquid": "ml Saft/Lösung", "sachet": "Beutel",
          "injection": "Spritze", "infusion": "Infusion", "patch": "Pflaster", "cream": "Creme/Salbe", "spray": "Hub/Spray",
          "suppository": "Zäpfchen", "other": "Einheit"}
HAEUFIGKEIT = {"daily": "täglich", "custom": "nach Rhythmus", "asneeded": "bei Bedarf", "once": "einmalig/Zyklus"}


def _menge(x):
    try:
        v = float(str(x).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0
    return v if v > 0 else 0.0


def plan_zeile(d):
    """Eine Planzeile in der Schreibweise eines Medikationsplans: Name Stärke, 1-0-1-0 Tablette, täglich …"""
    def zahl(v):
        v = _menge(v)
        return ("%g" % v).replace(".", ",") if v else "0"
    schema_ = "-".join(zahl(d.get(k)) for k in ("morning", "noon", "evening", "night"))
    def de(v):
        return v.get("de") or next((x for x in v.values() if x), "") if isinstance(v, dict) else (v or "")
    teile = [f"{d.get('name', '?')} {d.get('strength', '')}".strip(),
             f"{schema_} {FORMEN.get(d.get('form'), d.get('form') or '')}".strip(),
             HAEUFIGKEIT.get(d.get("frequency"), d.get("frequency") or "") + (f" ({d['freq_note']})" if d.get("freq_note") else "")]
    if d.get("start_unknown"):
        teile.append("seit: nicht bekannt" + (f" bis {d['end']}" if d.get("end") else ""))
    elif d.get("start") or d.get("end"):
        teile.append(f"seit {d.get('start') or '?'}" + (f" bis {d['end']}" if d.get("end") else ""))
    if de(d.get("reason")):
        teile.append("Grund: " + de(d.get("reason")))
    if de(d.get("notes")):
        teile.append("Hinweis: " + de(d.get("notes")))
    if d.get("prescriber"):
        teile.append("verordnet von " + d["prescriber"])
    if d.get("stock"):
        teile.append(f"Vorrat {('%g' % _menge(d['stock'])).replace('.', ',')} Einheiten (Stand {d.get('stock_date') or '?'})")
    return " · ".join(t for t in teile if t)


def vital_art(d):
    """Blutdruck/Puls erkennen — über die Vorlage oder den Namen (auch bei importierten Spalten wie „Systolisch (mmHg)“)."""
    p, lab = d.get("param") or "", (d.get("paramLabel") or "").lower()
    if p == "bp_sys" or re.search(r"systol|\bsys\b|skurcz", lab):
        return "sys"
    if p == "bp_dia" or re.search(r"diastol|\bdia\b|rozkurcz", lab):
        return "dia"
    if p == "pulse" or re.search(r"puls|pulse|heart.?rate|herzfreq|tętno", lab):
        return "pulse"
    return None


def blutdruck_text(werte):
    """Blutdruck je Messung (127/67, Puls 76) statt drei getrennter Reihen — mit Statistik für die KI."""
    mess = {}
    for d in werte:
        art = vital_art(d)
        if art:
            mess.setdefault((d.get("date") or "", d.get("time") or ""), {})[art] = d
    liste = [(k, m) for k, m in sorted(mess.items()) if "sys" in m and "dia" in m]
    if not liste:
        return [], set()
    def v(m, a):
        x = (m.get(a) or {}).get("value")
        if not isinstance(x, (int, float)):
            return None
        return int(x) if float(x).is_integer() else x
    sys_ = [v(m, "sys") for _, m in liste if v(m, "sys") is not None]
    dia_ = [v(m, "dia") for _, m in liste if v(m, "dia") is not None]
    puls = [v(m, "pulse") for _, m in liste if v(m, "pulse") is not None]
    hoch = sum(1 for _, m in liste if (v(m, "sys") or 0) >= 135 or (v(m, "dia") or 0) >= 85)
    zeilen = ["\n## Blutdruck je Messung (systolisch/diastolisch mmHg, Puls /min)"]
    zeilen.append(f"- {len(liste)} Messungen vom {liste[0][0][0]} bis {liste[-1][0][0]}; Mittel {sum(sys_) / len(sys_):.0f}/{sum(dia_) / len(dia_):.0f} mmHg"
                  + (f", Puls {sum(puls) / len(puls):.0f}" if puls else "")
                  + f"; Spanne systolisch {min(sys_)}–{max(sys_)}, diastolisch {min(dia_)}–{max(dia_)}; "
                  f"{hoch} Messungen ({100 * hoch / len(liste):.0f} %) bei oder über 135/85 (Grenzwert für Heimmessungen)")
    for name, test in (("morgens (vor 12 Uhr)", lambda z: z and z < "12:00"), ("abends (ab 17 Uhr)", lambda z: z and z >= "17:00")):
        teil = [m for (dt, z), m in liste if test(z)]
        if len(teil) >= 5:
            zeilen.append(f"- {name}: {len(teil)} Messungen, Mittel {sum(v(m, 'sys') for m in teil) / len(teil):.0f}/{sum(v(m, 'dia') for m in teil) / len(teil):.0f}")
    letzte = liste[-30:]
    zeilen.append(f"- die letzten {len(letzte)} Messungen:")
    for (dt, z), m in letzte:
        notiz = next((x for x in ((m.get(a) or {}).get("note") for a in ("sys", "dia", "pulse")) if isinstance(x, dict) and any(x.values())), None)
        notiz_t = (notiz.get("de") or next((y for y in notiz.values() if y), "")) if notiz else ""
        zeilen.append(f"  - {dt} {z}: {v(m, 'sys')}/{v(m, 'dia')}" + (f", Puls {v(m, 'pulse')}" if v(m, "pulse") is not None else "") + (f" — {notiz_t}" if notiz_t else ""))
    benutzte = {id(d) for _, m in liste for d in m.values()}
    return zeilen, benutzte


def kontext(details=True):
    """Die Mappe als knapper Text für die KI: Werte, Befunde, eigene Medikamenten-Notizen, Recherche-Titel."""
    with db() as con:
        rows = [zeile(r, con) for r in con.execute("SELECT * FROM entries WHERE topic_id=? ORDER BY id", (thema()["id"],))]
    def de(v):
        return (v or {}).get("de") or next((x for x in (v or {}).values() if x), "") if isinstance(v, dict) else (v or "")
    teile = []
    werte = sorted((e for e in rows if e["kind"] == "value"),
                   key=lambda e: (e["data"].get("paramLabel") or e["data"].get("param", ""), e["data"].get("date", ""), e["data"].get("time") or ""))
    if werte:
        teile.append("## Laborwerte und Messungen (Datum Uhrzeit: Wert Einheit [Referenz] Notiz)")
        bd_zeilen, bd_benutzt = blutdruck_text([e["data"] for e in werte])
        reihen = {}
        for e in werte:
            d = e["data"]
            if id(d) in bd_benutzt:
                continue  # steht zusammengefasst im Blutdruck-Abschnitt
            reihen.setdefault(d.get("paramLabel") or PARAM_NAMEN.get(d.get("param"), d.get("param")), []).append(d)
        for name, liste in reihen.items():
            # Bei vielen Messungen (z. B. importierte Blutdruckreihen) Statistik + die letzten 30 statt aller Zeilen
            if len(liste) > 30:
                zahlen = [x.get("value") for x in liste if isinstance(x.get("value"), (int, float))]
                if zahlen:
                    teile.append(f"- {name}: insgesamt {len(liste)} Messungen vom {liste[0].get('date')} bis {liste[-1].get('date')}, "
                                 f"Mittel {sum(zahlen) / len(zahlen):.1f}, Min {min(zahlen)}, Max {max(zahlen)} {liste[-1].get('unit', '')}; die letzten 30:")
                liste = liste[-30:]
            for d in liste:
                ref = f"[{d.get('low') if d.get('low') is not None else ''}–{d.get('high') if d.get('high') is not None else ''}]"
                zeit = f" {d['time']}" if d.get("time") else ""
                wert = d.get("value")
                wert = int(wert) if isinstance(wert, float) and wert.is_integer() else wert
                teile.append(f"- {name} {d.get('date')}{zeit}: {wert} {d.get('unit', '')} {ref} {de(d.get('note'))}".rstrip())
        teile += bd_zeilen
    befunde = [e for e in rows if e["kind"] == "finding"]
    if befunde:
        teile.append("\n## Befunde und eigene Einschätzungen")
        for e in sorted(befunde, key=lambda e: e["data"].get("date", "")):
            d = e["data"]
            dateien = ", ".join(f["name"] for f in e["files"])
            teile.append(f"### {d.get('date', '')} {de(d.get('title'))}" + (f" (angehängte Dokumente: {dateien} — deren Inhalt steckt in der Befund-Einordnung unten, falls vorhanden)" if dateien else ""))
            if details and de(d.get("body")):
                teile.append(de(d.get("body"))[:3000])
            if details and d.get("ai"):
                teile.append("Frühere KI-Einordnung: " + de(d["ai"].get("text"))[:1500])
    plan = [e for e in rows if e["kind"] == "medplan"]
    if plan:
        aktiv = [e for e in plan if e["data"].get("status", "active") == "active"]
        rest = [e for e in plan if e["data"].get("status", "active") != "active"]
        teile.append("\n## Medikamentenplan — tatsächlich eingenommen (Schema Morgens-Mittags-Abends-Nachts)")
        teile += [f"- {plan_zeile(e['data'])}" for e in aktiv] or ["- (keine aktiven Einträge)"]
        if rest:
            teile.append("Pausiert oder beendet:")
            teile += [f"- [{'pausiert' if e['data'].get('status') == 'paused' else 'beendet'}] {plan_zeile(e['data'])}" for e in rest]
    meds = [e for e in rows if e["kind"] == "med" and de(e["data"].get("notes"))]
    if meds:
        teile.append("\n## Medikamente mit eigenen Notizen (vermutlich aktuelle oder geplante Therapie)")
        for e in meds:
            teile.append(f"- {de(e['data'].get('title'))}: {de(e['data'].get('notes'))[:600]}")
    studien = [e for e in rows if e["kind"] == "study"]
    if studien:
        teile.append("\n## Studien im Notizbuch")
        for e in studien:
            d = e["data"]
            kurz = ((d.get("summary") or {}).get("short") or {}).get("de", "")
            titel = d["title"] if isinstance(d.get("title"), str) else de(d.get("title"))
            kennung = d.get("nct") or (f"PMID {d['pmid']}" if d.get("pmid") else "")
            teile.append(f"- {titel} ({kennung}, {d.get('type', '')} {d.get('year', '')}{', ' + d['status_de'] if d.get('status_de') else ''}){': ' + kurz if kurz else ''}")
    recherche = [e for e in rows if e["kind"] == "research" and not e["data"].get("seed")]
    if recherche:
        teile.append("\n## Bisherige Recherche-Notizen (Titel)")
        teile += [f"- {de(e['data'].get('title'))}" for e in recherche[-30:]]
    kopf = f"# Thema: {thema_name()} — {thema_bezug()}\n\n"
    return kopf + ("\n".join(teile) or "(Das Notizbuch enthält zu diesem Thema noch keine eigenen Einträge.)")


def dateien_fuer_ki(files):
    """PDFs und Fotos eines Eintrags als Eingabe für die Responses-API. HEIC kennt OpenAI nicht."""
    import base64
    teile, hinweise = [], []
    for f in files[:6]:
        pfad = datei_pfad(f["id"], f["name"])
        if not pfad.exists():
            continue
        b64 = base64.b64encode(pfad.read_bytes()).decode()
        if f["mime"] == "application/pdf":
            teile.append({"type": "input_file", "filename": f["name"], "file_data": f"data:application/pdf;base64,{b64}"})
        elif f["mime"] in ("image/jpeg", "image/png", "image/webp"):
            teile.append({"type": "input_image", "image_url": f"data:{f['mime']};base64,{b64}"})
        elif f["mime"] == "text/csv":
            roh = pfad.read_bytes()[:40000].decode("utf-8", errors="replace")
            teile.append({"type": "input_text", "text": f"Angehängte Tabelle {f['name']} (CSV, ggf. gekürzt):\n{roh}"})
        else:
            hinweise.append(f["name"])
    return teile, hinweise


def mehrsprachig_auftrag(lang):
    return (f"Die Nutzerin liest gerade auf {NAMEN.get(lang, 'Deutsch')}. Liefere jedes Textfeld in allen drei Sprachen "
            "(de, en, pl) mit gleichem Inhalt — vollständige, gleichwertige Fassungen, keine Kurzversionen.")


class Einstellungen(BaseModel):
    openai_key: str | None = None
    remove_key: bool = False
    transcript_key: str | None = None
    remove_transcript_key: bool = False
    model: str | None = None
    model_fast: str | None = None
    web_search: bool | None = None


def einstellungen_aus(con):
    key = einstellung(con, "openai_key")
    tkey = einstellung(con, "transcript_key")
    return {"openai_set": bool(key), "openai_hint": (key[:3] + "…" + key[-4:]) if key else "",
            "transcript_set": bool(tkey), "transcript_hint": (tkey[:4] + "…" + tkey[-4:]) if tkey else "",
            "model": einstellung(con, "model"), "model_fast": einstellung(con, "model_fast"),
            "web_search": einstellung(con, "web_search") == "1", "claude_translate": bool(CLAUDE_KEY)}


@app.get("/api/settings")
def einstellungen_lesen():
    with db() as con:
        return einstellungen_aus(con)


@app.put("/api/settings")
def einstellungen_speichern(s: Einstellungen):
    with db() as con:
        def setze(k, v):
            con.execute("INSERT INTO settings (key, value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (k, v))
        if s.remove_key:
            con.execute("DELETE FROM settings WHERE key='openai_key'")
            protokoll("OpenAI-Schlüssel entfernt")
        elif s.openai_key and s.openai_key.strip():
            key = s.openai_key.strip()
            if not key.startswith("sk-") or len(key) < 20:
                raise HTTPException(400, "Das sieht nicht nach einem OpenAI-Schlüssel aus (beginnt mit sk-).")
            setze("openai_key", key)
            protokoll("OpenAI-Schlüssel gespeichert")
        if s.remove_transcript_key:
            con.execute("DELETE FROM settings WHERE key='transcript_key'")
            protokoll("TranscriptAPI-Schlüssel entfernt")
        elif s.transcript_key and s.transcript_key.strip():
            if len(s.transcript_key.strip()) < 16:
                raise HTTPException(400, "Der TranscriptAPI-Schlüssel ist zu kurz.")
            setze("transcript_key", s.transcript_key.strip())
            protokoll("TranscriptAPI-Schlüssel gespeichert")
        for k in ("model", "model_fast"):
            v = getattr(s, k)
            if v and v.strip():
                setze(k, v.strip())
        if s.web_search is not None:
            setze("web_search", "1" if s.web_search else "0")
        return einstellungen_aus(con)


def modell_rang(i):
    """Neueste GPT-Modelle zuerst (5.5 vor 5.4 vor 5), Varianten dahinter, o-Modelle ans Ende."""
    import re
    m = re.match(r"^(gpt|o)-?(\d+)(?:\.(\d+))?(.*)$", i)
    if not m:
        return (2, 0, 0, i)
    return (0 if m.group(1) == "gpt" else 1, -int(m.group(2)), -int(m.group(3) or 0), m.group(4))


@app.post("/api/settings/test")
def einstellungen_testen():
    k = ki_konfig()
    if not k["openai_key"]:
        raise HTTPException(400, "Kein OpenAI-Schlüssel hinterlegt.")
    try:
        r = httpx.get(f"{OPENAI}/models", headers={"Authorization": f"Bearer {k['openai_key']}"}, timeout=20)
    except httpx.HTTPError:
        raise HTTPException(502, "OpenAI ist gerade nicht erreichbar.")
    if r.status_code == 401:
        raise HTTPException(400, "OpenAI lehnt den Schlüssel ab.")
    if r.status_code != 200:
        raise HTTPException(502, f"OpenAI meldet HTTP {r.status_code}.")
    import re
    ids = sorted({m["id"] for m in r.json().get("data", [])
                  if re.match(r"^(gpt-[45][.\d]*(-mini|-nano|-pro)?|o[34](-mini|-pro)?)$", m["id"])},
                 key=modell_rang)
    return {"ok": True, "models": ids}


class Frage(BaseModel):
    topic: int | None = None
    question: str
    lang: str = "de"
    web: bool = True
    mappe: bool = False


@app.post("/api/ai/research")
def ki_recherche(f: Frage):
    thema_setzen(f.topic)
    if not f.question.strip():
        raise HTTPException(400, "Bitte eine Frage eingeben.")
    auftrag = (
        "Recherchiere und beantworte diese Frage für die Mappe:\n\n" + f.question.strip() + "\n\n"
        + ("Beziehe dich, wo es passt, ausdrücklich auf den Inhalt der Mappe:\n\n" + kontext() + "\n\n" if f.mappe else "")
        + "Stütze dich auf verlässliche, möglichst aktuelle Quellen, die zum Thema passen (bei Gesundheit: Leitlinien, "
          "Fachgesellschaften, Studien, gesund.bund.de, IQWiG, NIH; sonst Fachquellen, Behörden, Normen, Hersteller) "
          "und gib sie in 'sources' mit echter URL an. Gliedere die Antwort mit "
          "Zwischenüberschriften, schließe mit '## Fragen fürs Arztgespräch'. "
        + mehrsprachig_auftrag(f.lang) + " 'title' ist eine kurze Überschrift zur Frage."
    )
    out = openai_json(auftrag, schema(title=i18n_schema(), body=i18n_schema(), sources=QUELLEN), web=f.web)
    return {"kind": "research", "data": {"title": out["title"], "body": out["body"], "sources": out["sources"][:12],
                                         "source": out["sources"][0]["url"] if out["sources"] else "",
                                         "date": datetime.now().strftime("%Y-%m-%d"), "question": f.question.strip(),
                                         "ai_model": out["_model"]}}


class Nachschlagen(BaseModel):
    topic: int | None = None
    term: str
    lang: str = "de"
    context: str = ""  # Satz, aus dem ein markierter Begriff stammt — hilft bei mehrdeutigen Abkürzungen


def themen_tags():
    with db() as con:
        rows = con.execute("SELECT data FROM entries WHERE kind='glossary' AND topic_id=?", (thema()["id"],)).fetchall()
    tags = []
    for r in rows:
        for t in json.loads(r["data"]).get("tags") or []:
            if t not in tags:
                tags.append(t)
    return tags[:30]


@app.post("/api/ai/glossary")
def ki_begriff(n: Nachschlagen):
    thema_setzen(n.topic)
    if not n.term.strip():
        raise HTTPException(400, "Bitte einen Begriff eingeben.")
    auftrag = (
        f"Erkläre den Begriff „{n.term.strip()}“ im Zusammenhang mit {thema_bezug()} für Laien: was er bedeutet, wo er "
        + ("im Befund oder in der Behandlung auftaucht, welche Werte/Stufen es gibt und was sie bedeuten. " if ist_gesundheit()
           else "in der Praxis auftaucht, worauf es ankommt und welche Varianten es gibt. ")
        + (f"Der Begriff wurde in diesem Zusammenhang markiert — erkläre ihn in genau dieser Bedeutung: „{n.context.strip()[:600]}“. "
           if n.context.strip() else "") + "4–8 Sätze, "
        "ohne Überschriften, Listen nur wenn sie helfen. 'title' ist der Begriff in der jeweils üblichen Schreibweise "
        "(mit Abkürzung, falls gebräuchlich). 'tags' sind 1–2 kurze deutsche Themen-Schlagwörter"
        + (f"; nimm nach Möglichkeit eines, das es in diesem Thema schon gibt: {', '.join(themen_tags()) or '—'}. ")
        + mehrsprachig_auftrag(n.lang)
    )
    out = openai_json(auftrag, schema(title=i18n_schema(), body=i18n_schema(),
                                      tags={"type": "array", "items": {"type": "string"}}), schnell=False, aufwand="low")
    return {"kind": "glossary", "data": {"title": out["title"], "body": out["body"], "tags": out["tags"][:3], "ai_model": out["_model"]}}


@app.post("/api/ai/med")
def ki_medikament(n: Nachschlagen):
    thema_setzen(n.topic)
    if not n.term.strip():
        raise HTTPException(400, "Bitte ein Medikament eingeben.")
    auftrag = (
        f"Beschreibe das Medikament „{n.term.strip()}“ im Zusammenhang mit {thema_bezug()} für Laien. "
        "'title': Wirkstoff (Handelsname®). 'cls': Wirkstoffgruppe. 'body': Wirkweise, wofür und wie es gegeben wird "
        "(Form, typischer Rhythmus, Dauer), 3–6 Sätze. 'side': häufige und wichtige Nebenwirkungen, worauf man achten "
        "und was man sofort melden sollte, Wechselwirkungen falls wichtig. Prüfe aktuelle Zulassungen per Websuche. "
        + mehrsprachig_auftrag(n.lang)
    )
    out = openai_json(auftrag, schema(title=i18n_schema(), cls=i18n_schema(), body=i18n_schema(), side=i18n_schema()),
                      web=True, aufwand="low")
    return {"kind": "med", "data": {"title": out["title"], "cls": out["cls"], "body": out["body"], "side": out["side"],
                                    "ai_model": out["_model"]}}


class Sprache(BaseModel):
    lang: str = "de"
    topic: int | None = None


def thema_von_eintrag(eid):
    with db() as con:
        r = con.execute("SELECT topic_id FROM entries WHERE id=?", (eid,)).fetchone()
    return thema_setzen(r["topic_id"] if r else None)


@app.post("/api/ai/analyze/{eid}")
def ki_befund(eid: int, s: Sprache):
    """KI-Einordnung eines Befunds (samt angehängter PDFs/Fotos) oder einer Messreihe; landet im Eintrag."""
    thema_von_eintrag(eid)
    with db() as con:
        r = con.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone()
        if not r:
            raise HTTPException(404, "Eintrag nicht gefunden")
        e = zeile(r, con)
    dateien, nicht_lesbar = dateien_fuer_ki(e["files"])
    d = e["data"]
    def de(v):
        return v.get("de") or next((x for x in v.values() if x), "") if isinstance(v, dict) else (v or "")
    if e["kind"] == "value" and vital_art(d):
        gegenstand = ("die Blutdruck-Messreihe (systolisch/diastolisch mit Puls, je Messung; Statistik und die letzten Messungen stehen "
                      "unten im Notizbuch) — mit Tagesprofil morgens/abends, Anteil erhöhter Werte nach den Grenzwerten für Heimmessungen "
                      "(135/85 mmHg) und Trend")
    elif e["kind"] == "value":
        gegenstand = f"die Messreihe zu „{d.get('paramLabel') or PARAM_NAMEN.get(d.get('param'), d.get('param'))}“ (alle Werte stehen unten in der Mappe), zuletzt {d.get('date')}: {d.get('value')} {d.get('unit', '')}"
    else:
        gegenstand = f"den Befund „{de(d.get('title'))}“ vom {d.get('date', '?')}:\n\n{de(d.get('body'))}"
    auftrag = (
        f"Ordne {gegenstand}\n\n"
        + ("Die angehängten Dokumente gehören zu diesem Befund — lies sie vollständig und beziehe ihre Angaben ein. "
           if dateien else "")
        + (f"Nicht lesbar (Format HEIC): {', '.join(nicht_lesbar)}. " if nicht_lesbar else "")
        + "\n\nZum Zusammenhang die ganze Mappe:\n\n" + kontext() + "\n\n"
        + ("Gliedere so: '## Kurzfassung' (2–3 Sätze), '## Was im Befund steht' (Werte und Begriffe einzeln erklärt), "
           "'## Einordnung' (Bedeutung, mögliche Diagnose bzw. Ausprägung, was die Werte für den Verlauf heißen, übliche nächste Schritte "
           "laut Leitlinie — klar als Einschätzung gekennzeichnet), '## Auffälligkeiten & Verlauf' (Abweichungen, Trends, "
           "Widersprüche zu früheren Befunden), '## Fragen fürs Arztgespräch', '## Hinweise' (praktisch: worauf achten, "
           "Warnzeichen). " if ist_gesundheit() else
           "Gliedere so: '## Kurzfassung' (2–3 Sätze), '## Was drinsteht' (Zahlen, Begriffe, Bedingungen einzeln erklärt), "
           "'## Einordnung' (Bedeutung, Vergleich mit üblichen Werten bzw. dem Stand der Technik — als Einschätzung gekennzeichnet), "
           "'## Auffälligkeiten & Verlauf', '## Offene Fragen' (an wen), '## Nächste Schritte'. ")
        + "'summary' ist ein Satz. " + mehrsprachig_auftrag(s.lang)
    )
    out = openai_json(auftrag, schema(summary=i18n_schema(), text=i18n_schema()), dateien=dateien, aufwand="high")
    ai = {"summary": out["summary"], "text": out["text"], "date": jetzt()[:16], "model": out["_model"]}
    with db() as con:
        r = con.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone()
        data = json.loads(r["data"])
        data["ai"] = ai
        con.execute("UPDATE entries SET data=?, updated=? WHERE id=?", (json.dumps(data, ensure_ascii=False), jetzt(), eid))
        out_e = zeile(con.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone(), con)
    protokoll(f"KI-Einordnung für #{eid}")
    return out_e


def analyse_speichern(scope, out):
    data = {"scope": scope, "title": out["title"], "body": out["body"], "date": datetime.now().strftime("%Y-%m-%d"),
            "ai_model": out["_model"]}
    with db() as con:
        cur = con.execute("INSERT INTO entries (kind, data, created, updated, topic_id) VALUES (?,?,?,?,?)",
                          ("analysis", json.dumps(data, ensure_ascii=False), jetzt(), jetzt(), thema()["id"]))
        return zeile(con.execute("SELECT * FROM entries WHERE id=?", (cur.lastrowid,)).fetchone(), con)


@app.post("/api/ai/values")
def ki_werte(s: Sprache):
    thema_setzen(s.topic)
    k = kontext()
    if "Laborwerte" not in k:
        raise HTTPException(400, "Es sind noch keine Werte eingetragen.")
    auftrag = (
        ("Analysiere alle Laborwerte und Messungen der Mappe im Zusammenhang mit Befunden und Therapie:\n\n" if ist_gesundheit() else
         f"Analysiere alle Messwerte des Notizbuchs zum Thema „{thema_name()}“ im Zusammenhang mit den Dokumenten. Passe die "
         "folgende Gliederung sinngemäß an das Thema an (statt Arztgespräch: Fachleute, statt Warnzeichen: kritische Werte):\n\n") + k + "\n\n"
        "Gliedere: '## Kurzfassung', '## Werte im Einzelnen' (je Wert: aktueller Stand, Trend, Bedeutung — z. B. "
        "was der Wert im Zusammenhang mit diesem Thema und den Befunden bedeutet; Aussagekraft und Grenzen des Werts), "
        "'## Mögliche Ursachen & Einordnung' (als Einschätzung gekennzeichnet), '## Warnzeichen', "
        "'## Fragen fürs Arztgespräch', '## Was man selbst tun kann'. Weise darauf hin, wenn Referenzbereiche fehlen "
        "oder Werte zu wenige sind, um einen Trend zu beurteilen. 'title' z. B. „Werte-Analyse 08.10.2026“. "
        + mehrsprachig_auftrag(s.lang)
    )
    return analyse_speichern("values", openai_json(auftrag, schema(title=i18n_schema(), body=i18n_schema()), aufwand="high"))


def analyse_zusatz():
    """Ausdrückliche Prüfaufträge für Messwerte und Medikamentenplan — unabhängig von der Art des Themas."""
    with db() as con:
        tid = thema()["id"]
        n_werte = con.execute("SELECT COUNT(*) FROM entries WHERE kind='value' AND topic_id=?", (tid,)).fetchone()[0]
        n_plan = con.execute("SELECT COUNT(*) FROM entries WHERE kind='medplan' AND topic_id=?", (tid,)).fetchone()[0]
    teile = []
    if n_werte:
        teile.append("'## Messwerte' (eigener Abschnitt: Verlauf und Trend jeder Reihe, Mittelwerte, Anteil außerhalb des Zielbereichs, "
                     "Tageszeit-Unterschiede, Auffälligkeiten; konkrete Zahlen aus dem Notizbuch nennen)")
    if n_plan:
        teile.append("'## Medikamentenplan' (eigener Abschnitt: jedes Medikament mit Stärke und Einnahmezeit; passt die Wirkung zu den "
                     "Messwerten — z. B. Werte nach Beginn bzw. zur Einnahmezeit; Wechselwirkungen, Einnahmezeiten, Doppelungen, "
                     "Dosis im üblichen Rahmen, sinnvolle Kontrollen — alles als Einschätzung, nie eigenmächtig ändern)")
    if not teile:
        return ""
    return " Zusätzlich, weil im Notizbuch hinterlegt, unbedingt diese Abschnitte nach '## Wo wir stehen' einfügen: " + ", ".join(teile) + ". "


@app.post("/api/ai/hints")
def ki_hinweise(s: Sprache):
    thema_setzen(s.topic)
    if not ist_gesundheit():
        auftrag = (
            f"Lies das ganze Notizbuch zum Thema „{thema_name()}“ und erstelle eine Analyse:\n\n" + analyse_kontext()[:90000] + "\n\n"
            "Gliedere: '## Wo wir stehen' (Stand in 3–5 Sätzen), '## Was als Nächstes sinnvoll ist', '## Was noch fehlt' "
            "(Lücken in Recherche, Unterlagen, Entscheidungen), '## Offene Fragen' (an wen man sie richten sollte), "
            "'## Tipps & Fallstricke' (konkret, belegt). Ist das Notizbuch noch leer, erkläre, womit man sinnvoll anfängt. "
            + analyse_zusatz()
            + f"'title' z. B. „Analyse {datetime.now():%d.%m.%Y}“. " + mehrsprachig_auftrag(s.lang)
        )
        return analyse_speichern("hints", openai_json(auftrag, schema(title=i18n_schema(), body=i18n_schema()), web=True, aufwand="medium"))
    auftrag = (
        f"Lies das ganze Notizbuch zum Thema „{thema_name()}“ ({thema_bezug()}) und erstelle persönliche Hinweise. "
        "Bleib streng bei diesem Thema:\n\n" + analyse_kontext()[:90000] + "\n\n"
        "Gliedere: '## Wo wir stehen' (Lage in 3–5 Sätzen, soweit aus der Mappe ableitbar), '## Was als Nächstes "
        "üblich ist' (laut Leitlinie, als Orientierung), '## Was im Notizbuch noch fehlt' (Werte, Untersuchungen, "
        "Unterlagen oder offene Entscheidungen, die für genau dieses Thema typischerweise wichtig sind), "
        "(Wechselwirkungen auch mit Nahrungsergänzung und passende Laborkontrollen beachten) "
        "'## Fragen fürs nächste Arztgespräch', '## Alltag' (konkrete, belegte Tipps zum Thema), '## Warnzeichen' "
        "(nur solche, die zu diesem Thema passen). Ist das Notizbuch noch leer, erkläre, womit man bei diesem Thema "
        "sinnvoll anfängt. " + analyse_zusatz() + f"'title' z. B. „Analyse {datetime.now():%d.%m.%Y}“. " + mehrsprachig_auftrag(s.lang)
    )
    return analyse_speichern("hints", openai_json(auftrag, schema(title=i18n_schema(), body=i18n_schema()),
                                                  web=True, aufwand="medium"))



# ---------------------------------------------------------------------------
# Videos & Links: Vorschau holen, Vorschaubild auf dem Server ablegen
# ---------------------------------------------------------------------------

import hashlib
import ipaddress
import re
import socket
from html import unescape
from urllib.parse import parse_qs, urljoin, urlparse

YT_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
      "Accept-Language": "de,en;q=0.8,pl;q=0.6"}


def youtube_id(url):
    u = urlparse(url.strip())
    host = (u.hostname or "").lower().removeprefix("www.").removeprefix("m.").removeprefix("music.")
    kandidat = ""
    if host == "youtu.be":
        kandidat = u.path.strip("/").split("/")[0]
    elif host in ("youtube.com", "youtube-nocookie.com"):
        if u.path == "/watch":
            kandidat = (parse_qs(u.query).get("v") or [""])[0]
        else:
            teile = u.path.strip("/").split("/")
            if len(teile) >= 2 and teile[0] in ("shorts", "embed", "live", "v"):
                kandidat = teile[1]
    return kandidat if YT_ID.match(kandidat or "") else None


def oeffentlich(url):
    """Nur öffentliche http(s)-Adressen abrufen — keine Anfragen ins interne Netz des Servers."""
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        return False
    try:
        for info in socket.getaddrinfo(u.hostname, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False
    except (socket.gaierror, ValueError):
        return False
    return True


def bild_holen(url, name):
    """Lädt ein Bild (max. 5 MB) nach data/thumbs/<name>. Gibt den Namen zurück oder None."""
    if not oeffentlich(url):
        return None
    try:
        with httpx.stream("GET", url, headers=UA, timeout=15, follow_redirects=True) as r:
            if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image/"):
                return None
            daten = b""
            for teil in r.iter_bytes():
                daten += teil
                if len(daten) > 5 * 1024 * 1024:
                    return None
    except httpx.HTTPError:
        return None
    if len(daten) < 2000:  # YouTube liefert für fehlende maxres-Bilder einen grauen Platzhalter
        return None
    THUMBS.mkdir(parents=True, exist_ok=True)
    (THUMBS / name).write_bytes(daten)
    return name


def youtube_vorschau(vid):
    # oEmbed: 200 = einbettbar, 401/403 = Einbetten vom Kanal gesperrt (nur auf YouTube abspielbar), 404 = gibt es nicht
    titel, kanal, einbettbar, status = "", "", True, 0
    try:
        r = httpx.get("https://www.youtube.com/oembed", params={"url": f"https://www.youtube.com/watch?v={vid}", "format": "json"},
                      headers=UA, timeout=10)
        status = r.status_code
        if status == 200:
            j = r.json()
            titel, kanal = j.get("title", ""), j.get("author_name", "")
        elif status in (401, 403):
            einbettbar = False
    except httpx.HTTPError:
        pass
    name = f"yt_{vid}.jpg"
    thumb = name if (THUMBS / name).exists() else None
    for groesse in ("maxresdefault", "sddefault", "hqdefault"):
        if thumb:
            break
        thumb = bild_holen(f"https://i.ytimg.com/vi/{vid}/{groesse}.jpg", name)
    if status == 404 or (status in (401, 403) and not thumb):
        raise HTTPException(404, "Dieses Video gibt es nicht (mehr) oder es ist privat.")
    if not titel:
        titel, kanal = info_per_transcriptapi(vid) or ("", "")
    return {"type": "youtube", "yt_id": vid, "url": f"https://www.youtube.com/watch?v={vid}",
            "title": titel, "channel": kanal, "thumb": thumb, "embed": einbettbar}


def info_per_transcriptapi(vid):
    """Titel/Kanal für nicht einbettbare Videos — /youtube/info kostet bei TranscriptAPI nichts."""
    key = ki_konfig_trans()
    if not key:
        return None
    try:
        r = httpx.get("https://transcriptapi.com/api/v2/youtube/info", params={"video_url": vid},
                      headers={"Authorization": f"Bearer {key}"}, timeout=20)
        if r.status_code == 200:
            j = r.json()
            m = j.get("metadata") or j
            return (m.get("title") or "", m.get("author_name") or m.get("channel") or "")
    except (httpx.HTTPError, ValueError):
        pass
    return None


def meta(html, *namen):
    for n in namen:
        for muster in (rf'<meta[^>]+(?:property|name)=["\']{re.escape(n)}["\'][^>]*content=["\']([^"\']*)',
                       rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]*(?:property|name)=["\']{re.escape(n)}["\']'):
            m = re.search(muster, html, re.I)
            if m and m.group(1).strip():
                return unescape(m.group(1).strip())
    return ""


def link_vorschau(url):
    if not oeffentlich(url):
        raise HTTPException(400, "Bitte eine öffentliche Adresse mit http:// oder https:// angeben.")
    html, end = "", url
    try:
        with httpx.stream("GET", url, headers=UA, timeout=15, follow_redirects=True) as r:
            end = str(r.url)
            if r.status_code < 400 and "html" in r.headers.get("content-type", ""):
                for teil in r.iter_text():
                    html += teil
                    if len(html) > 600_000:
                        break
    except httpx.HTTPError:
        pass
    titel = meta(html, "og:title", "twitter:title")
    if not titel:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
        titel = unescape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else ""
    seite = meta(html, "og:site_name") or (urlparse(end).hostname or "").removeprefix("www.")
    thumb = None
    bild = meta(html, "og:image:secure_url", "og:image", "twitter:image")
    if bild:
        name = "l_" + hashlib.sha1(url.encode()).hexdigest()[:16] + ".jpg"
        thumb = name if (THUMBS / name).exists() else bild_holen(urljoin(end, bild), name)
    return {"type": "link", "url": url, "title": titel[:300], "channel": seite[:120], "thumb": thumb}


class Link(BaseModel):
    url: str


@app.post("/api/link-preview")
def vorschau(l: Link):
    url = l.url.strip()
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    vid = youtube_id(url)
    out = youtube_vorschau(vid) if vid else link_vorschau(url)
    protokoll(f"Vorschau {out['type']} {out.get('yt_id') or url} Bild={'ja' if out['thumb'] else 'nein'}")
    return out


@app.get("/api/thumbs/{name}")
def vorschaubild(name: str):
    if not re.match(r"^(yt|l)_[A-Za-z0-9_-]+\.jpg$", name) or not (THUMBS / name).exists():
        raise HTTPException(404, "Kein Vorschaubild")
    # Endung ist immer .jpg, der Inhalt kann PNG/WebP sein — Browser erkennen das am Inhalt
    return FileResponse(THUMBS / name, media_type="image/jpeg", headers={"Cache-Control": "private, max-age=604800"})



# ---------------------------------------------------------------------------
# Videos: Transkript (TranscriptAPI) & Zusammenfassung (OpenAI, sonst Claude)
# ---------------------------------------------------------------------------

def claude_json(auftrag, antwort_schema):
    """Rückfallebene ohne OpenAI-Schlüssel: Claude mit JSON im Text."""
    if not CLAUDE_KEY:
        raise HTTPException(400, "Weder OpenAI- noch Claude-Schlüssel vorhanden — bitte unter Einstellungen OpenAI eintragen.")
    try:
        r = httpx.post("https://api.anthropic.com/v1/messages",
                       headers={"x-api-key": CLAUDE_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                       json={"model": MODEL, "max_tokens": 16000, "thinking": {"type": "disabled"}, "system": system_text(),
                             "messages": [{"role": "user", "content": auftrag + "\n\nAntworte ausschließlich mit einem JSON-Objekt "
                                           "nach diesem JSON-Schema, ohne Codeblock:\n" + json.dumps(antwort_schema)}]},
                       timeout=300)
        r.raise_for_status()
        d = r.json()
        text = "".join(b.get("text", "") for b in d["content"] if b.get("type") == "text")
        out = json.loads(text[text.find("{"):text.rfind("}") + 1])
    except (httpx.HTTPError, ValueError, KeyError) as ex:
        protokoll(f"FEHLER Claude: {ex}")
        raise HTTPException(502, "Die Zusammenfassung ist fehlgeschlagen. Bitte erneut versuchen.")
    u = d.get("usage") or {}
    protokoll(f"KI {MODEL} in={u.get('input_tokens')} out={u.get('output_tokens')}")
    out["_model"] = MODEL
    return out


def llm_json(auftrag, antwort_schema, **kw):
    if ki_konfig()["openai_key"]:
        return openai_json(auftrag, antwort_schema, **kw)
    return claude_json(auftrag, antwort_schema)


def zeitmarke(sek):
    sek = int(sek or 0)
    h, rest = divmod(sek, 3600)
    return f"{h}:{rest // 60:02d}:{rest % 60:02d}" if h else f"{rest // 60}:{rest % 60:02d}"


def absaetze(segmente, takt=40):
    """Segmente zu lesbaren Absätzen mit Zeitmarke bündeln (etwa alle 40 Sekunden ein neuer)."""
    zeilen, aktuell, start = [], [], None
    for sg in segmente:
        t = (sg.get("text") or "").replace("\n", " ").strip()
        if not t:
            continue
        if start is None:
            start = sg.get("start", 0)
        aktuell.append(t)
        if sg.get("start", 0) - start >= takt and t.endswith((".", "?", "!", "…")) or sg.get("start", 0) - start >= takt * 2:
            zeilen.append(f"[{zeitmarke(start)}] " + " ".join(aktuell))
            aktuell, start = [], None
    if aktuell:
        zeilen.append(f"[{zeitmarke(start)}] " + " ".join(aktuell))
    return "\n\n".join(zeilen)


def transkript_holen(vid, vlang):
    key = ki_konfig_trans()
    if not key:
        raise HTTPException(400, "Kein TranscriptAPI-Schlüssel hinterlegt (Einstellungen). YouTube sperrt Abrufe direkt vom Server — "
                                 "alternativ das Transkript im Formular von Hand einfügen.")
    sprachen = []
    for l in [vlang if vlang in LANGS else None, "de", "pl", "en", "asr"]:
        if l and l not in sprachen:
            sprachen.append(l)
    try:
        r = httpx.get("https://transcriptapi.com/api/v2/youtube/transcript",
                      params={"video_url": vid, "format": "json", "include_timestamp": "true", "language": ",".join(sprachen)},
                      headers={"Authorization": f"Bearer {key}"}, timeout=90)
    except httpx.HTTPError:
        raise HTTPException(502, "TranscriptAPI ist gerade nicht erreichbar.")
    if r.status_code == 401:
        raise HTTPException(400, "TranscriptAPI lehnt den Schlüssel ab.")
    if r.status_code == 402:
        raise HTTPException(402, "Das TranscriptAPI-Guthaben ist aufgebraucht.")
    if r.status_code == 404:
        raise HTTPException(404, "Für dieses Video gibt es keine Untertitel. Transkript ggf. von Hand einfügen.")
    if r.status_code != 200:
        protokoll(f"FEHLER TranscriptAPI {r.status_code}: {r.text[:200]}")
        raise HTTPException(502, f"TranscriptAPI meldet HTTP {r.status_code}.")
    d = r.json()
    protokoll(f"Transkript {vid} ({d.get('language')}, {len(d.get('transcript') or [])} Segmente)")
    return {"text": absaetze(d.get("transcript") or []), "lang": d.get("language", ""), "source": "transcriptapi",
            "date": jetzt()[:16], "duration": d.get("lengthText") or ""}


def ki_konfig_trans():
    with db() as con:
        return einstellung(con, "transcript_key")


def seitentext(url):
    """Lesbarer Text einer Webseite für die Zusammenfassung eigener Links."""
    if not oeffentlich(url):
        return ""
    try:
        r = httpx.get(url, headers=UA, timeout=20, follow_redirects=True)
    except httpx.HTTPError:
        return ""
    if "html" not in r.headers.get("content-type", ""):
        return ""
    t = re.sub(r"(?is)<(script|style|nav|footer|header|noscript|svg)[^>]*>.*?</\1>", " ", r.text)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t).strip()[:60000]


def video_laden(eid):
    with db() as con:
        r = con.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone()
        if not r or r["kind"] != "video":
            raise HTTPException(404, "Video nicht gefunden")
        return zeile(r, con)


def video_speichern(eid, aendern):
    with db() as con:
        r = con.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone()
        data = json.loads(r["data"])
        aendern(data)
        con.execute("UPDATE entries SET data=?, updated=? WHERE id=?", (json.dumps(data, ensure_ascii=False), jetzt(), eid))
        return zeile(con.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone(), con)


class Transkript(BaseModel):
    text: str | None = None


@app.post("/api/videos/{eid}/transcript")
def video_transkript(eid: int, t: Transkript):
    e = video_laden(eid)
    d = e["data"]
    if t.text and t.text.strip():
        neu = {"text": t.text.strip()[:400000], "lang": d.get("vlang", ""), "source": "manual", "date": jetzt()[:16]}
    elif d.get("yt_id"):
        neu = transkript_holen(d["yt_id"], d.get("vlang", ""))
    else:
        raise HTTPException(400, "Nur YouTube-Videos lassen sich automatisch transkribieren.")
    def setze(data):
        data["transcript"] = {k: v for k, v in neu.items() if k != "duration"}
        if neu.get("duration") and not data.get("duration"):
            data["duration"] = neu["duration"]
    return video_speichern(eid, setze)


@app.post("/api/videos/{eid}/summary")
def video_zusammenfassung(eid: int, s: Sprache):
    thema_von_eintrag(eid)
    e = video_laden(eid)
    d = e["data"]
    titel = d["title"] if isinstance(d.get("title"), str) else (d.get("title") or {}).get("de", "")
    if d.get("yt_id"):
        quelle = (d.get("transcript") or {}).get("text", "")
        if not quelle:
            raise HTTPException(400, "Erst das Transkript holen.")
        art = f"des YouTube-Videos „{titel}“ (Kanal: {d.get('channel', '?')}, Länge {d.get('duration') or '?'}). Transkript mit Zeitmarken"
    else:
        quelle = seitentext(d.get("url", ""))
        if len(quelle) < 200:
            raise HTTPException(400, "Die Seite liefert keinen lesbaren Text zum Zusammenfassen.")
        art = f"der Webseite „{titel}“ ({d.get('url')}). Seitentext"
    mappe = kontext(details=False)
    auftrag = (
        f"Fasse den Inhalt {art}:\n\n{quelle[:150000]}\n\n"
        f"Zum Bezug das Notizbuch zum Thema „{thema_name()}“ (nur nutzen, wenn es inhaltlich passt):\n\n" + mappe[:8000] + "\n\n"
        "Gliedere 'text' so: '## Worum es geht' (2–3 Sätze), '## Die wichtigsten Aussagen' (Liste; bei Videos jeweils mit "
        "Zeitmarke [m:ss] aus dem Transkript am Anfang), '## Einordnung' (wer spricht, wie aktuell, wo es von heutigen "
        "Leitlinien bzw. dem Stand der Technik abweicht oder vereinfacht), '## Was das für uns heißt' (nur wenn das Notizbuch "
        "passende Inhalte hat, sonst weglassen), '## Fragen fürs Arztgespräch' (2–4). 'short' ist ein einziger Satz, der sagt, was man "
        "aus dem Video mitnimmt. 'topics' sind 2–5 kurze deutsche Schlagwörter. " + mehrsprachig_auftrag(s.lang)
    )
    out = llm_json(auftrag, schema(short=i18n_schema(), text=i18n_schema(), topics={"type": "array", "items": {"type": "string"}}),
                   aufwand="medium")
    summary = {"short": out["short"], "text": out["text"], "topics": out.get("topics", [])[:5], "date": jetzt()[:16], "model": out["_model"]}
    protokoll(f"Zusammenfassung Video #{eid}")
    return video_speichern(eid, lambda data: data.__setitem__("summary", summary))


@app.post("/api/videos/{eid}/process")
def video_verarbeiten(eid: int, s: Sprache):
    """Transkript holen (falls nötig) und zusammenfassen — ein Klick für beides."""
    thema_von_eintrag(eid)
    e = video_laden(eid)
    if e["data"].get("yt_id") and not (e["data"].get("transcript") or {}).get("text"):
        video_transkript(eid, Transkript())
    return video_zusammenfassung(eid, s)



# ---------------------------------------------------------------------------
# Chat über OpenAI (Responses-API, gestreamt)
# ---------------------------------------------------------------------------

CHAT_REGELN = (
    "Du chattest direkt mit den Menschen, die dieses Notizbuch führen. Antworte in der Sprache der letzten Nutzernachricht "
    "(Deutsch, Polnisch oder Englisch). Passe die Länge der Frage an: kurze Frage, kurze Antwort; bei komplexen Themen "
    "gegliedert mit Zwischenüberschriften. Frag nach, wenn etwas unklar ist. Wenn die Mappe zur Frage passende Werte, "
    "Befunde, Medikamente oder Videos enthält, beziehe dich konkret darauf (mit Datum). Empfiehl passende Videos aus der "
    "Notizbuch mit Titel, wenn sie helfen. Bei Websuche: nenne die Quellen als Markdown-Links."
)


def analyse_kontext():
    """Alles, was im Thema steht — für die Analyse auf der Übersicht (der Hinweis in der Oberfläche verspricht das)."""
    teile = [chat_kontext()]
    with db() as con:
        rows = [zeile(r) for r in con.execute("SELECT * FROM entries WHERE topic_id=? ORDER BY id", (thema()["id"],))]
    def de(v):
        return (v or {}).get("de") or next((x for x in (v or {}).values() if x), "") if isinstance(v, dict) else (v or "")
    meds = [e for e in rows if e["kind"] == "med" and not de(e["data"].get("notes"))]
    if meds:
        teile.append("\n## Weitere Medikamente im Notizbuch (ohne eigene Notiz)")
        teile += [f"- {de(e['data'].get('title'))}" + (f" ({de(e['data'].get('cls'))})" if de(e["data"].get("cls")) else "") for e in meds]
    recherche = [e for e in rows if e["kind"] == "research" and not e["data"].get("seed")]
    if recherche:
        teile.append("\n## Inhalt der Recherche-Notizen")
        for e in recherche[-40:]:
            teile.append(f"### {de(e['data'].get('title'))}\n{de(e['data'].get('body'))[:900]}")
    begriffe = [e for e in rows if e["kind"] == "glossary"]
    if begriffe:
        teile.append("\n## Begriffe, die bereits erklärt sind")
        teile.append(", ".join(de(e["data"].get("title")) for e in begriffe))
    return "\n".join(teile)


def chat_kontext():
    teile = [kontext()]
    with db() as con:
        rows = con.execute("SELECT data FROM entries WHERE kind='video' AND topic_id=? ORDER BY id", (thema()["id"],)).fetchall()
    videos = []
    for r in rows:
        d = json.loads(r["data"])
        kurz = ((d.get("summary") or {}).get("short") or {}).get("de", "")
        titel = d["title"] if isinstance(d.get("title"), str) else (d.get("title") or {}).get("de", "")
        videos.append(f"- „{titel}“ ({(d.get('vlang') or '').upper()}, {d.get('channel', '')}){': ' + kurz if kurz else ''}")
    if videos:
        teile.append("\n## Videos in der Mappe (Reiter „Videos & Links“)\n" + "\n".join(videos[:60]))
    return "\n".join(teile)


def chat_zeile(r, voll=True):
    out = {"id": r["id"], "title": r["title"], "created": r["created"], "updated": r["updated"], "topic_id": r["topic_id"]}
    msgs = json.loads(r["messages"])
    out["count"] = len(msgs)
    if voll:
        out["messages"] = msgs
    return out


@app.get("/api/chats")
def chats_liste(topic: int | None = None):
    with db() as con:
        if topic is None:
            return [chat_zeile(r, voll=False) for r in con.execute("SELECT * FROM chats ORDER BY updated DESC")]
        return [chat_zeile(r, voll=False) for r in con.execute("SELECT * FROM chats WHERE topic_id=? ORDER BY updated DESC", (topic,))]


@app.post("/api/chats")
def chat_neu(topic: int | None = None):
    tid = thema_setzen(topic)["id"]
    with db() as con:
        cur = con.execute("INSERT INTO chats (title, messages, created, updated, topic_id) VALUES (?,?,?,?,?)", ("", "[]", jetzt(), jetzt(), tid))
        return chat_zeile(con.execute("SELECT * FROM chats WHERE id=?", (cur.lastrowid,)).fetchone())


@app.get("/api/chats/{cid}")
def chat_holen(cid: int):
    with db() as con:
        r = con.execute("SELECT * FROM chats WHERE id=?", (cid,)).fetchone()
    if not r:
        raise HTTPException(404, "Gespräch nicht gefunden")
    return chat_zeile(r)


@app.delete("/api/chats/{cid}")
def chat_loeschen(cid: int):
    with db() as con:
        r = con.execute("SELECT * FROM chats WHERE id=?", (cid,)).fetchone()
        if not r:
            raise HTTPException(404, "Gespräch nicht gefunden")
        protokoll(f"Chat gelöscht #{cid}: {r['title']} ({len(json.loads(r['messages']))} Nachrichten)")
        con.execute("DELETE FROM chats WHERE id=?", (cid,))
    return {"ok": True}


class ChatNachricht(BaseModel):
    text: str
    lang: str = "de"
    web: bool = False
    mappe: bool = True


def chat_speichern(cid, nachrichten, titel=None):
    with db() as con:
        if titel:
            con.execute("UPDATE chats SET messages=?, updated=?, title=? WHERE id=?",
                        (json.dumps(nachrichten, ensure_ascii=False), jetzt(), titel, cid))
        else:
            con.execute("UPDATE chats SET messages=?, updated=? WHERE id=?", (json.dumps(nachrichten, ensure_ascii=False), jetzt(), cid))


def sse(obj):
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"


@app.post("/api/chats/{cid}/send")
def chat_senden(cid: int, m: ChatNachricht):
    text = m.text.strip()
    if not text:
        raise HTTPException(400, "Bitte eine Nachricht eingeben.")
    k = ki_konfig()
    if not k["openai_key"]:
        raise HTTPException(400, "Kein OpenAI-Schlüssel hinterlegt — bitte unter Einstellungen eintragen.")
    chat = chat_holen(cid)
    thema_setzen(chat.get("topic_id"))
    t_aktuell = thema()
    verlauf = chat["messages"] + [{"role": "user", "text": text[:20000], "date": jetzt()[:16]}]
    titel = None if chat["title"] else (text[:70] + ("…" if len(text) > 70 else ""))
    chat_speichern(cid, verlauf, titel)

    anweisung = system_text() + "\n\n" + CHAT_REGELN + f"\nOberflächensprache gerade: {NAMEN.get(m.lang, 'Deutsch')}. Heute ist der {datetime.now():%d.%m.%Y}."
    if m.mappe:
        anweisung += f"\n\n# Inhalt des Notizbuchs (Thema „{thema_name()}“)\n\n" + chat_kontext()[:60000]
    eingabe = [{"role": x["role"], "content": x["text"][:8000]} for x in verlauf[-30:]]
    body = {"model": k["model"], "instructions": anweisung, "input": eingabe, "stream": True,
            "reasoning": {"effort": "low"} if k["model"].startswith(("gpt-5", "o")) else None}
    body = {a: b for a, b in body.items() if b is not None}
    if m.web and k["web_search"] == "1":
        body["tools"] = [{"type": "web_search"}]
        body["instructions"] += ("\n\nDie Websuche ist eingeschaltet: Nutze sie bei jeder Sachfrage, um aktuelle, belastbare "
                                 "Quellen zu prüfen (zum Thema passende Leitlinien, Fachgesellschaften, Behörden, Studien bzw. Fachquellen), "
                                 "und verlinke sie im Text. Nur bei reinen Rückfragen oder Smalltalk nicht suchen.")

    def strom():
        THEMA.set(t_aktuell)
        antwort, quellen, fehler, modell, nutzung = "", [], "", body["model"], {}
        try:
            with httpx.stream("POST", f"{OPENAI}/responses", json=body, timeout=httpx.Timeout(300, connect=15),
                              headers={"Authorization": f"Bearer {k['openai_key']}"}) as r:
                if r.status_code != 200:
                    r.read()
                    try:
                        msg = r.json().get("error", {}).get("message", "")
                    except ValueError:
                        msg = ""
                    fehler = "OpenAI lehnt den Schlüssel ab." if r.status_code == 401 else f"OpenAI meldet: {msg or r.status_code}"
                    yield sse({"t": "error", "m": fehler})
                    return
                for zeile in r.iter_lines():
                    if not zeile.startswith("data:"):
                        continue
                    try:
                        ev = json.loads(zeile[5:].strip())
                    except ValueError:
                        continue
                    typ = ev.get("type", "")
                    if typ == "response.output_text.delta":
                        antwort += ev.get("delta", "")
                        yield sse({"t": "delta", "d": ev.get("delta", "")})
                    elif typ.startswith("response.web_search_call") and typ.endswith(("in_progress", "searching")):
                        yield sse({"t": "status", "s": "search"})
                    elif typ == "response.output_text.annotation.added":
                        a = ev.get("annotation") or {}
                        if a.get("type") == "url_citation" and a.get("url") and a["url"] not in [q["url"] for q in quellen]:
                            quellen.append({"url": a["url"], "title": a.get("title", "")})
                    elif typ == "response.completed":
                        resp = ev.get("response") or {}
                        modell, nutzung = resp.get("model", modell), resp.get("usage") or {}
                        for o in resp.get("output", []):
                            for c in o.get("content") or []:
                                for a in c.get("annotations") or []:
                                    if a.get("type") == "url_citation" and a.get("url") and a["url"] not in [q["url"] for q in quellen]:
                                        quellen.append({"url": a["url"], "title": a.get("title", "")})
                    elif typ in ("response.failed", "error"):
                        fehler = ((ev.get("response") or {}).get("error") or ev.get("error") or {}).get("message") or "Die Antwort ist abgebrochen."
                        yield sse({"t": "error", "m": fehler})
        except httpx.HTTPError as ex:
            fehler = "OpenAI ist gerade nicht erreichbar."
            protokoll(f"FEHLER Chat: {ex}")
            yield sse({"t": "error", "m": fehler})
        finally:
            # Auch eine abgebrochene Antwort bleibt erhalten, damit der Verlauf stimmt
            if antwort and not quellen:
                # Im Stream kommen die url_citation-Annotationen nicht immer an — Links aus dem Text sind verlässlich
                for titel_l, url_l in re.findall(r"\[([^\]]{1,200})\]\((https?://[^)\s]+)\)", antwort):
                    url_l = re.sub(r"[?&]utm_source=openai$", "", url_l)
                    if url_l not in [q["url"] for q in quellen]:
                        quellen.append({"url": url_l, "title": titel_l})
            if antwort:
                nachricht = {"role": "assistant", "text": antwort, "date": jetzt()[:16], "model": modell,
                             "sources": quellen[:15], **({"partial": True} if fehler else {})}
                chat_speichern(cid, verlauf + [nachricht])
                protokoll(f"Chat #{cid} {modell} web={bool(body.get('tools'))} in={nutzung.get('input_tokens')} out={nutzung.get('output_tokens')}")
        if antwort and not fehler:
            yield sse({"t": "done", "message": {"role": "assistant", "text": antwort, "model": modell, "sources": quellen[:15]}})

    return StreamingResponse(strom(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})



# ---------------------------------------------------------------------------
# MCP-Schnittstelle für KI-Agenten (Streamable HTTP, nur JSON)
# Aufbau wie beim FAQ-Tool: der Schlüssel im Pfad ist die Anmeldung.
# Zwei Schlüssel: /mcp/<lesen> nur lesend, /mcp/<schreiben> lesend + schreibend.
# ---------------------------------------------------------------------------

import base64
import secrets

MCP_PROTOKOLL = "2025-06-18"
ARTEN = {"finding": "Befund", "value": "Messwert", "glossary": "Begriff", "med": "Medikament",
         "research": "Recherche-Notiz", "analysis": "KI-Analyse", "video": "Video/Link", "study": "Studie", "medplan": "Medikamentenplan"}


def mcp_schluessel():
    """Schlüssel liegen in der Tabelle settings und entstehen beim ersten Bedarf."""
    with db() as con:
        out = {}
        for k in ("mcp_read", "mcp_write"):
            v = einstellung(con, k)
            if not v:
                v = secrets.token_urlsafe(32)
                con.execute("INSERT INTO settings (key, value) VALUES (?,?)", (k, v))
                protokoll(f"MCP-Schlüssel {k} erzeugt")
            out[k] = v
        return out


def mcp_recht(token):
    s = mcp_schluessel()
    if token and secrets.compare_digest(token, s["mcp_write"]):
        return "write"
    if token and secrets.compare_digest(token, s["mcp_read"]):
        return "read"
    return None


def oeffentliche_adresse(request):
    if PUBLIC_URL:
        return PUBLIC_URL
    proto = request.headers.get("x-forwarded-proto") or request.url.scheme
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
    return f"{proto}://{host}"


@app.get("/api/mcp-info")
def mcp_info(request: Request):
    s = mcp_schluessel()
    basis = oeffentliche_adresse(request) + "/mcp/"
    return {"read_url": basis + s["mcp_read"], "write_url": basis + s["mcp_write"]}


class Erneuern(BaseModel):
    welcher: str  # read | write


@app.post("/api/mcp-info/rotate")
def mcp_erneuern(e: Erneuern, request: Request):
    if e.welcher not in ("read", "write"):
        raise HTTPException(400, "read oder write")
    with db() as con:
        con.execute("INSERT INTO settings (key, value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (f"mcp_{e.welcher}", secrets.token_urlsafe(32)))
    protokoll(f"MCP-Schlüssel mcp_{e.welcher} erneuert — der alte gilt nicht mehr")
    return mcp_info(request)


def _t(v, lang):
    if isinstance(v, dict):
        return v.get(lang) or v.get("de") or next((x for x in v.values() if x), "")
    return v or ""


def _titel(e, lang="de"):
    d = e["data"]
    if e["kind"] == "medplan":
        return plan_zeile(d)
    if e["kind"] == "value":
        name = d.get("paramLabel") or PARAM_NAMEN.get(d.get("param"), d.get("param"))
        return f"{name}: {d.get('value')} {d.get('unit', '')} ({d.get('date', '')})"
    return _t(d.get("title"), lang) or d.get("url", "")


def _kurz(e, lang="de"):
    d = e["data"]
    text = _t(d.get("note") if e["kind"] == "value" else d.get("body"), lang)
    if e["kind"] == "video" and d.get("summary"):
        text = _t(d["summary"].get("short"), lang)
    return {"id": e["id"], "thema_id": e.get("topic_id"), "art": e["kind"], "art_name": ARTEN.get(e["kind"], e["kind"]), "titel": _titel(e, lang),
            "datum": d.get("date") or e["updated"][:10], "auszug": (text or "")[:240],
            "dateien": len(e.get("files") or []), "geaendert": e["updated"]}


def _alle(tid=None):
    with db() as con:
        if tid is None:
            rows = con.execute("SELECT * FROM entries ORDER BY updated DESC").fetchall()
        else:
            rows = con.execute("SELECT * FROM entries WHERE topic_id=? ORDER BY updated DESC", (tid,)).fetchall()
        alle = {}
        for f in con.execute("SELECT id, entry_id, name, mime, size, created FROM files"):
            alle.setdefault(f["entry_id"], []).append(dict(f))
    out = [zeile(r) for r in rows]
    for e in out:
        e["files"] = alle.get(e["id"], [])
    return out


def _flach(v):
    if isinstance(v, dict):
        return " ".join(str(x) for x in v.values())
    if isinstance(v, list):
        return " ".join(_flach(x) for x in v)
    return str(v or "")


MCP_SPRACHE = {"type": "string", "enum": ["de", "en", "pl"], "description": "Sprache der Ausgabe bzw. der Eingabe (Standard de)."}
MCP_ART = {"type": "string", "enum": list(ARTEN), "description": "finding=Befund, value=Messwert, glossary=Begriff, med=Medikament, research=Recherche-Notiz, analysis=KI-Analyse, video=Video/Link, study=Studie"}

MCP_THEMA = {"type": "string", "description": "Thema als id oder Name (siehe themen_auflisten). Ohne Angabe: bei Suchen alle Themen, sonst das erste Thema."}

MCP_TOOLS = [
    {"name": "themen_auflisten", "schreibt": False,
     "description": "Listet die Themen des Notebooks (oberste Ebene) mit id, Name, Beschreibung, Art (health/general), aktiven Unterbereichen und Anzahl der Einträge. Jeder Eintrag gehört zu genau einem Thema.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "sprache": MCP_SPRACHE}}},
    {"name": "thema_anlegen", "schreibt": True,
     "description": "Legt ein neues Thema an. Unterbereiche: values (Werte & Dokumente), glossary (Begriffe), med (Medikamente), research (Recherche), chat, videos. art: health (Gesundheit, mit medizinischen Hinweisen) oder general.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "name": {"type": "string"}, "beschreibung": {"type": "string"}, "art": {"type": "string", "enum": ["health", "general"]},
                                                      "bereiche": {"type": "array", "items": {"type": "string", "enum": ["values", "glossary", "med", "research", "chat", "videos"]}},
                                                      "sprache": MCP_SPRACHE}, "required": ["name"]}},
    {"name": "studien_suchen", "schreibt": False,
     "description": "Sucht Studien: quelle 'pubmed' = veröffentlichte Studien (PubMed), 'trials' = laufende klinische Studien (ClinicalTrials.gov, standardmäßig nur rekrutierende; land z. B. Germany oder Poland). Suchbegriffe auf Englisch liefern die meisten Treffer. Übernehmen mit studie_uebernehmen.",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "quelle": {"type": "string", "enum": ["pubmed", "trials"]},
                                                      "land": {"type": "string"}, "nur_offene": {"type": "boolean"}, "limit": {"type": "integer"}}, "required": ["query"]}},
    {"name": "studie_uebernehmen", "schreibt": True,
     "description": "Übernimmt eine Studie per PubMed-ID, NCT-Nummer, DOI oder Link ins Notizbuch (mit Abstract, Eckdaten, bei laufenden Studien Einschlusskriterien und Orten in DE/PL). Danach optional ki_einordnung_starten.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "kennung": {"type": "string", "description": "PMID, NCT…, DOI oder URL"}}, "required": ["kennung"]}},
    {"name": "medikamentenplan", "schreibt": False,
     "description": "Der Medikamentenplan eines Themas — was tatsächlich eingenommen wird: Name, Stärke, Schema Morgens-Mittags-Abends-Nachts, Form, Häufigkeit, Zeitraum, Grund, Hinweise, Vorrat. Mit pausierten und beendeten Einträgen.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "nur_aktive": {"type": "boolean"}}}},
    {"name": "plan_eintrag_setzen", "schreibt": True,
     "description": "Legt einen Eintrag im Medikamentenplan an oder ändert ihn (mit id). Mengen je Einnahmezeit als Zahl (0,5 = halbe Tablette). Nur auf ausdrückliche Anweisung eines Menschen — der Plan bildet die echte Einnahme ab.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "id": {"type": "integer", "description": "Nur zum Ändern"},
                                                      "name": {"type": "string"}, "staerke": {"type": "string", "description": "z. B. 20 mg"},
                                                      "form": {"type": "string", "enum": list(FORMEN)}, "morgens": {"type": "number"}, "mittags": {"type": "number"},
                                                      "abends": {"type": "number"}, "nachts": {"type": "number"},
                                                      "haeufigkeit": {"type": "string", "enum": list(HAEUFIGKEIT)}, "rhythmus": {"type": "string"},
                                                      "start": {"type": "string", "description": "YYYY-MM-DD oder 'unbekannt'"}, "ende": {"type": "string"}, "status": {"type": "string", "enum": ["active", "paused", "ended"]},
                                                      "grund": {"type": "string"}, "hinweise": {"type": "string"}, "verordnet_von": {"type": "string"},
                                                      "vorrat": {"type": "number", "description": "Anzahl Einheiten"}, "sprache": MCP_SPRACHE}}},
    {"name": "notebook_ueberblick", "schreibt": False,
     "description": "Überblick über das Research Notebook: Anzahl der Einträge je Art, die neuesten Messwerte (mit Markierung außerhalb des Referenzbereichs), die letzten Befunde und die jüngsten KI-Hinweise. Guter Einstieg.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "sprache": MCP_SPRACHE}}},
    {"name": "eintraege_suchen", "schreibt": False,
     "description": "Volltextsuche über alle Einträge (Befunde, Werte, Begriffe, Medikamente, Recherche, Videos samt Zusammenfassung und Transkript, KI-Analysen) in allen drei Sprachen. Liefert eine Trefferliste mit id; Details mit eintrag_holen.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "query": {"type": "string"}, "art": MCP_ART, "sprache": MCP_SPRACHE,
                                                      "limit": {"type": "integer", "description": "Standard 20, höchstens 100."}}, "required": ["query"]}},
    {"name": "eintraege_auflisten", "schreibt": False,
     "description": "Listet Einträge einer Art, neueste zuerst.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "art": MCP_ART, "sprache": MCP_SPRACHE, "limit": {"type": "integer"}, "offset": {"type": "integer"}}, "required": ["art"]}},
    {"name": "eintrag_holen", "schreibt": False,
     "description": "Gibt einen Eintrag vollständig zurück, mit allen Sprachfassungen, angehängten Dateien (id, Name, Typ), KI-Einordnung und bei Videos Zusammenfassung und — auf Wunsch — Transkript.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "id": {"type": "integer"}, "mit_transkript": {"type": "boolean", "description": "Bei Videos das volle Transkript mitliefern (Standard false)."}}, "required": ["id"]}},
    {"name": "werte_verlauf", "schreibt": False,
     "description": "Messwerte als Zeitreihe je Parameter (Datum, Wert, Einheit, Referenzbereich, hoch/niedrig, Notiz). Ohne Parameter alle Reihen.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "parameter": {"type": "string", "description": "z. B. leuko, hb, thrombo, ca153, lvef oder ein freier Name."}}}},
    {"name": "datei_lesen", "schreibt": False,
     "description": "Liefert eine angehängte Datei (PDF oder Bild) zum Lesen. Bilder kommen als Bild, PDFs als eingebettete Ressource (Base64). Höchstens 15 MB.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "datei_id": {"type": "string"}}, "required": ["datei_id"]}},
    {"name": "chats_auflisten", "schreibt": False,
     "description": "Listet die gespeicherten Chat-Gespräche des Notebooks.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, }}},
    {"name": "chat_holen", "schreibt": False,
     "description": "Gibt ein Chat-Gespräch mit allen Nachrichten zurück.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "id": {"type": "integer"}}, "required": ["id"]}},
    {"name": "eintrag_anlegen", "schreibt": True,
     "description": "Legt einen neuen Eintrag an. Texte in einer Sprache schreiben — sie werden automatisch ins Deutsche, Englische und Polnische übersetzt. "
                    "Befund: titel, text, datum. Recherche: titel, text, quelle, datum. Begriff: titel, text, themen. Medikament: titel, wirkstoffgruppe, text (Wirkung), nebenwirkungen, notizen. "
                    "Messwert: parameter, wert, einheit, ref_von, ref_bis, datum, text (Notiz). Video/Link: url, thema, video_sprache, text (Notiz) — Titel und Vorschaubild holt das Notebook selbst.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, 
         "art": MCP_ART, "sprache": MCP_SPRACHE, "titel": {"type": "string"}, "text": {"type": "string"},
         "datum": {"type": "string", "description": "YYYY-MM-DD, Standard heute"}, "quelle": {"type": "string", "description": "URL"},
         "themen": {"type": "array", "items": {"type": "string"}}, "wirkstoffgruppe": {"type": "string"},
         "nebenwirkungen": {"type": "string"}, "notizen": {"type": "string"},
         "parameter": {"type": "string"}, "wert": {"type": "number"}, "einheit": {"type": "string"},
         "ref_von": {"type": "number"}, "ref_bis": {"type": "number"},
         "url": {"type": "string"}, "thema": {"type": "string", "enum": ["grundlagen", "befund", "therapie", "nebenwirkungen", "psyche", "nachsorge", "sonstiges"]},
         "video_sprache": {"type": "string", "enum": ["de", "en", "pl", "other"]}}, "required": ["art"]}},
    {"name": "eintrag_aendern", "schreibt": True,
     "description": "Ändert einzelne Felder eines Eintrags (gleiche Feldnamen wie eintrag_anlegen). Geänderte Texte werden neu in alle drei Sprachen übersetzt; nicht angegebene Felder bleiben unverändert.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "id": {"type": "integer"}, "sprache": MCP_SPRACHE, "titel": {"type": "string"}, "text": {"type": "string"},
                                                      "datum": {"type": "string"}, "quelle": {"type": "string"}, "themen": {"type": "array", "items": {"type": "string"}},
                                                      "wirkstoffgruppe": {"type": "string"}, "nebenwirkungen": {"type": "string"}, "notizen": {"type": "string"},
                                                      "wert": {"type": "number"}, "einheit": {"type": "string"}, "ref_von": {"type": "number"}, "ref_bis": {"type": "number"},
                                                      "thema": {"type": "string"}}, "required": ["id"]}},
    {"name": "eintrag_loeschen", "schreibt": True,
     "description": "Löscht einen Eintrag samt Anhängen. Nur nach ausdrücklicher Anweisung eines Menschen benutzen; bestaetigt muss true sein. Inhalt bleibt im Server-Protokoll, Anhänge im Ordner 'geloescht'.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "id": {"type": "integer"}, "bestaetigt": {"type": "boolean"}}, "required": ["id", "bestaetigt"]}},
    {"name": "datei_anhaengen", "schreibt": True,
     "description": "Hängt eine Datei (PDF, JPG, PNG, HEIC, WEBP; höchstens 30 MB) an einen Eintrag an.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "eintrag_id": {"type": "integer"}, "dateiname": {"type": "string"},
                                                      "inhalt_base64": {"type": "string"}}, "required": ["eintrag_id", "dateiname", "inhalt_base64"]}},
    {"name": "ki_einordnung_starten", "schreibt": True,
     "description": "Lässt die eingebaute KI (OpenAI) einen Befund oder eine Messreihe einordnen (liest auch angehängte PDFs) bzw. ein Video transkribieren und zusammenfassen. Dauert 1–3 Minuten; das Ergebnis wird im Eintrag gespeichert und zurückgegeben.",
     "inputSchema": {"type": "object", "properties": {"thema": MCP_THEMA, "id": {"type": "integer"}, "sprache": MCP_SPRACHE}, "required": ["id"]}},
]


def _i18n_aus(texte, lang):
    """Felder übersetzen wie beim Speichern in der Oberfläche."""
    texte = {k: v for k, v in texte.items() if isinstance(v, str) and v.strip()}
    if not texte:
        return {}
    return uebersetzen(Uebersetzen(source=lang if lang in LANGS else "de", fields=texte)).get("fields", {})


FELD_MAP = {"titel": "title", "text": "body", "wirkstoffgruppe": "cls", "nebenwirkungen": "side", "notizen": "notes"}


def _daten_setzen(art, a, data, lang):
    texte = {}
    for ein, ziel in FELD_MAP.items():
        if a.get(ein) is not None:
            if art == "value" and ein == "text":
                texte["note"] = a[ein]
            elif art == "video" and ein == "text":
                texte["note"] = a[ein]
            elif art == "video" and ein == "titel":
                data["title"] = a[ein]
            else:
                texte[ziel] = a[ein]
    data.update(_i18n_aus(texte, lang))
    if a.get("datum"):
        data["date"] = a["datum"]
    if a.get("quelle") is not None:
        data["source"] = a["quelle"]
    if a.get("themen") is not None:
        data["tags"] = [str(t)[:40] for t in a["themen"]][:6]
    if art == "value":
        for ein, ziel in (("wert", "value"), ("einheit", "unit"), ("ref_von", "low"), ("ref_bis", "high")):
            if ein in a:
                data[ziel] = a[ein]
    if art == "video":
        if a.get("thema"):
            data["category"] = a["thema"]
        if a.get("video_sprache"):
            data["vlang"] = a["video_sprache"]
    return data


def mcp_tool(name, a, recht):
    tool = next((t for t in MCP_TOOLS if t["name"] == name), None)
    if not tool:
        return {"fehler": f"Unbekanntes Werkzeug: {name}"}
    if tool["schreibt"] and recht != "write":
        return {"fehler": "Dieser Zugang darf nur lesen. Für Änderungen den Schreib-Zugang verwenden."}
    lang = a.get("sprache") if a.get("sprache") in LANGS else "de"
    alle_themen = themen()
    # Thema bestimmen: ausdrücklich angegeben, sonst bei Suchen alle, sonst das erste
    tid = None
    if a.get("thema") not in (None, ""):
        tid = thema_setzen(a["thema"])["id"]
    else:
        thema_setzen(None)
    braucht_thema = name in ("eintrag_anlegen", "studie_uebernehmen") or (name == "plan_eintrag_setzen" and not a.get("id"))
    if braucht_thema and tid is None and len(alle_themen) > 1:
        return {"fehler": "Bitte thema angeben — es gibt mehrere Themen.", "themen": [{"id": t["id"], "name": t["name"].get(lang)} for t in alle_themen]}

    if name == "themen_auflisten":
        return {"themen": [{"id": t["id"], "name": t["name"].get(lang), "beschreibung": (t.get("desc") or {}).get(lang), "art": t.get("kind"),
                            "bereiche": t.get("sections"), "eintraege": t.get("counts")} for t in alle_themen]}

    if name == "thema_anlegen":
        t = thema_neu(ThemaDaten(name=a.get("name", ""), desc=a.get("beschreibung", ""), kind=a.get("art", "general"),
                                 sections=a.get("bereiche") or BEREICHE, lang=lang))
        protokoll(f"MCP Thema neu #{t['id']}")
        return {"ok": True, "thema": {"id": t["id"], "name": t["name"].get(lang)}}

    if name == "notebook_ueberblick":
        if tid is None:
            tid = thema()["id"]
        alle = _alle(tid)
        zahl = {}
        for e in alle:
            zahl[ARTEN.get(e["kind"], e["kind"])] = zahl.get(ARTEN.get(e["kind"], e["kind"]), 0) + 1
        reihen = {}
        for e in alle:
            if e["kind"] == "value":
                d = e["data"]
                k = d.get("paramLabel") or d.get("param")
                if k not in reihen or (d.get("date") or "") > (reihen[k]["date"] or ""):
                    reihen[k] = d
        werte = []
        for k, d in reihen.items():
            v, lo, hi = d.get("value"), d.get("low"), d.get("high")
            lage = "niedrig" if lo is not None and v is not None and v < lo else "hoch" if hi is not None and v is not None and v > hi else "im Bereich" if (lo is not None or hi is not None) else "ohne Referenz"
            werte.append({"parameter": d.get("paramLabel") or PARAM_NAMEN.get(k, k), "datum": d.get("date"), "wert": v, "einheit": d.get("unit"), "ref": [lo, hi], "lage": lage})
        befunde = sorted((e for e in alle if e["kind"] == "finding"), key=lambda e: e["data"].get("date", ""), reverse=True)[:5]
        hinweise = [e for e in alle if e["kind"] == "analysis" and e["data"].get("scope") == "hints"][:1]
        return {"thema": {"id": tid, "name": thema_name(lang)}, "weitere_themen": [{"id": t["id"], "name": t["name"].get(lang)} for t in alle_themen if t["id"] != tid],
                "anzahl": zahl, "neueste_werte": werte, "letzte_befunde": [_kurz(e, lang) for e in befunde],
                "ki_hinweise": _t(hinweise[0]["data"].get("body"), lang)[:4000] if hinweise else None,
                "hinweis": "Persönliche Gesundheitsdaten. KI-Einschätzungen ersetzen keine ärztliche Diagnose."}

    if name == "eintraege_suchen":
        q = (a.get("query") or "").lower().split()
        if not q:
            return {"fehler": "Bitte Suchbegriffe angeben."}
        treffer = []
        for e in _alle(tid):
            if a.get("art") and e["kind"] != a["art"]:
                continue
            d = e["data"]
            heu = " ".join(_flach(d.get(f)) for f in ("title", "body", "note", "cls", "side", "notes", "tags", "channel", "url", "source", "paramLabel", "param"))
            heu += " " + _flach((d.get("summary") or {}).get("text")) + " " + _flach((d.get("ai") or {}).get("text")) + " " + (d.get("transcript") or {}).get("text", "")
            heu += " " + " ".join(f["name"] for f in e["files"])
            heu = heu.lower()
            if all(w in heu for w in q):
                treffer.append(_kurz(e, lang))
        limit = max(1, min(int(a.get("limit") or 20), 100))
        return {"anzahl": len(treffer), "treffer": treffer[:limit]}

    if name == "eintraege_auflisten":
        liste = [e for e in _alle(tid) if e["kind"] == a.get("art")]
        off, limit = max(0, int(a.get("offset") or 0)), max(1, min(int(a.get("limit") or 50), 200))
        return {"anzahl": len(liste), "eintraege": [_kurz(e, lang) for e in liste[off:off + limit]]}

    if name == "eintrag_holen":
        with db() as con:
            r = con.execute("SELECT * FROM entries WHERE id=?", (int(a["id"]),)).fetchone()
            if not r:
                return {"fehler": "Eintrag nicht gefunden"}
            e = zeile(r, con)
        d = dict(e["data"])
        if e["kind"] == "video" and d.get("transcript") and not a.get("mit_transkript"):
            t = d["transcript"]
            d["transcript"] = {**{k: v for k, v in t.items() if k != "text"}, "laenge_zeichen": len(t.get("text", "")),
                               "hinweis": "Mit mit_transkript=true vollständig abrufen."}
        d.pop("seed", None)
        return {"id": e["id"], "art": e["kind"], "art_name": ARTEN.get(e["kind"]), "angelegt": e["created"], "geaendert": e["updated"],
                "daten": d, "dateien": e["files"]}

    if name == "werte_verlauf":
        p = (a.get("parameter") or "").lower()
        reihen = {}
        for e in _alle(tid):
            if e["kind"] != "value":
                continue
            d = e["data"]
            k = d.get("paramLabel") or PARAM_NAMEN.get(d.get("param"), d.get("param"))
            if p and p not in (d.get("param") or "").lower() and p not in (k or "").lower():
                continue
            v, lo, hi = d.get("value"), d.get("low"), d.get("high")
            reihen.setdefault(k, []).append({"id": e["id"], "datum": d.get("date"), "wert": v, "einheit": d.get("unit"), "ref_von": lo, "ref_bis": hi,
                                             "lage": "niedrig" if lo is not None and v < lo else "hoch" if hi is not None and v > hi else "ok",
                                             "notiz": _t(d.get("note"), lang)})
        for k in reihen:
            reihen[k].sort(key=lambda x: x["datum"] or "")
        return {"reihen": reihen} if reihen else {"reihen": {}, "hinweis": "Keine passenden Messwerte."}

    if name == "datei_lesen":
        with db() as con:
            f = con.execute("SELECT * FROM files WHERE id=?", (str(a.get("datei_id")),)).fetchone()
        if not f or not datei_pfad(f["id"], f["name"]).exists():
            return {"fehler": "Datei nicht gefunden"}
        if f["size"] > 15 * 1024 * 1024:
            return {"fehler": "Datei größer als 15 MB — bitte in der Oberfläche öffnen."}
        b64 = base64.b64encode(datei_pfad(f["id"], f["name"]).read_bytes()).decode()
        protokoll(f"MCP Datei gelesen {f['id']} ({f['name']})")
        if f["mime"].startswith("image/"):
            return {"_content": [{"type": "text", "text": f"Datei {f['name']} ({f['size']} Bytes)"},
                                 {"type": "image", "data": b64, "mimeType": f["mime"]}]}
        return {"_content": [{"type": "text", "text": f"Datei {f['name']} ({f['size']} Bytes)"},
                             {"type": "resource", "resource": {"uri": f"notebook://dateien/{f['id']}", "mimeType": f["mime"], "blob": b64}}]}

    if name == "medikamentenplan":
        if tid is None:
            tid = thema()["id"]
        plan = [e for e in _alle(tid) if e["kind"] == "medplan"]
        if a.get("nur_aktive"):
            plan = [e for e in plan if e["data"].get("status", "active") == "active"]
        return {"thema": thema_name(lang), "eintraege": [{"id": e["id"], "zeile": plan_zeile(e["data"]),
                                                          "status": e["data"].get("status", "active"), "daten": e["data"]} for e in plan]}

    if name == "plan_eintrag_setzen":
        felder = {"name": "name", "staerke": "strength", "form": "form", "morgens": "morning", "mittags": "noon", "abends": "evening",
                  "nachts": "night", "haeufigkeit": "frequency", "rhythmus": "freq_note", "start": "start", "ende": "end",
                  "status": "status", "verordnet_von": "prescriber", "vorrat": "stock"}
        if a.get("id"):
            with db() as con:
                r = con.execute("SELECT * FROM entries WHERE id=? AND kind='medplan'", (int(a["id"]),)).fetchone()
            if not r:
                return {"fehler": "Planeintrag nicht gefunden"}
            data = json.loads(r["data"])
        else:
            if not a.get("name"):
                return {"fehler": "name fehlt."}
            data = {"status": "active", "frequency": "daily", "form": "tablet", "start": datetime.now().strftime("%Y-%m-%d")}
        for ein, ziel in felder.items():
            if a.get(ein) is not None:
                data[ziel] = a[ein]
        if a.get("vorrat") is not None:
            data["stock_date"] = datetime.now().strftime("%Y-%m-%d")
        if str(a.get("start", "")).strip().lower() in ("unbekannt", "nicht bekannt", "unknown", "?"):
            data["start"], data["start_unknown"] = "", True
        elif a.get("start"):
            data["start_unknown"] = False
        data.update(_i18n_aus({k: a[e] for e, k in (("grund", "reason"), ("hinweise", "notes")) if a.get(e)}, lang))
        e = aendern(int(a["id"]), Entry(kind="medplan", data=data)) if a.get("id") else neu(Entry(kind="medplan", data=data, topic_id=thema()["id"]))
        protokoll(f"MCP Medikamentenplan #{e['id']}")
        return {"ok": True, "id": e["id"], "zeile": plan_zeile(e["data"])}

    if name == "studien_suchen":
        return studien_suche(a.get("query", ""), "trials" if a.get("quelle") == "trials" else "pubmed", a.get("land", ""),
                             a.get("nur_offene", True), False, int(a.get("limit") or 10))

    if name == "studie_uebernehmen":
        e = studie_importieren(StudieImport(topic=thema()["id"], url=a.get("kennung", "")))
        return {"ok": True, "eintrag": _kurz(e, lang)}

    if name == "chats_auflisten":
        return {"gespraeche": chats_liste(tid)}

    if name == "chat_holen":
        try:
            return chat_holen(int(a["id"]))
        except HTTPException as ex:
            return {"fehler": ex.detail}

    if name == "eintrag_anlegen":
        art = a.get("art")
        if art not in ARTEN or art == "analysis":
            return {"fehler": "art muss finding, value, glossary, med, research oder video sein."}
        data = {"date": datetime.now().strftime("%Y-%m-%d")} if art in ("finding", "research", "value", "video") else {}
        if art == "value":
            if a.get("wert") is None or not a.get("parameter"):
                return {"fehler": "Für Messwerte sind parameter und wert nötig."}
            pk = a["parameter"].strip()
            if pk.lower() in PARAM_NAMEN:
                data["param"] = pk.lower()
            else:
                treffer = next((k for k, n in PARAM_NAMEN.items() if n.lower() == pk.lower()), None)
                data["param"], data["paramLabel"] = (treffer, "") if treffer else ("_other", pk)
        elif art == "video":
            if not a.get("url"):
                return {"fehler": "Für Videos/Links ist url nötig."}
            pv = vorschau(Link(url=a["url"]))
            data.update({"url": pv["url"], "yt_id": pv.get("yt_id", ""), "thumb": pv.get("thumb") or "", "embed": pv.get("embed", True),
                         "title": a.get("titel") or pv.get("title") or pv["url"], "channel": pv.get("channel", ""),
                         "category": "sonstiges", "vlang": lang})
        elif not a.get("titel"):
            return {"fehler": "titel fehlt."}
        _daten_setzen(art, {k: v for k, v in a.items() if not (art == "video" and k == "titel")}, data, lang)
        data["created_by"] = "mcp"
        e = neu(Entry(kind=art, data=data, topic_id=thema()["id"]))
        protokoll(f"MCP neu {art} #{e['id']}")
        return {"ok": True, "eintrag": _kurz(e, lang)}

    if name == "eintrag_aendern":
        with db() as con:
            r = con.execute("SELECT * FROM entries WHERE id=?", (int(a["id"]),)).fetchone()
        if not r:
            return {"fehler": "Eintrag nicht gefunden"}
        data = _daten_setzen(r["kind"], a, json.loads(r["data"]), lang)
        e = aendern(int(a["id"]), Entry(kind=r["kind"], data=data))
        protokoll(f"MCP geändert {r['kind']} #{a['id']}")
        return {"ok": True, "eintrag": _kurz(e, lang)}

    if name == "eintrag_loeschen":
        if a.get("bestaetigt") is not True:
            return {"fehler": "Löschen nur mit bestaetigt=true — und nur, wenn ein Mensch es ausdrücklich verlangt hat."}
        loeschen(int(a["id"]))
        protokoll(f"MCP gelöscht #{a['id']}")
        return {"ok": True}

    if name == "datei_anhaengen":
        try:
            inhalt = base64.b64decode(a.get("inhalt_base64") or "", validate=False)
        except ValueError:
            return {"fehler": "inhalt_base64 ist kein gültiges Base64."}
        e = datei_speichern(int(a["eintrag_id"]), a.get("dateiname"), inhalt)
        protokoll(f"MCP Datei an #{a['eintrag_id']}")
        return {"ok": True, "dateien": e["files"]}

    if name == "ki_einordnung_starten":
        with db() as con:
            r = con.execute("SELECT kind FROM entries WHERE id=?", (int(a["id"]),)).fetchone()
        if not r:
            return {"fehler": "Eintrag nicht gefunden"}
        if r["kind"] == "video":
            e = video_verarbeiten(int(a["id"]), Sprache(lang=lang))
            s_ = e["data"].get("summary") or {}
            return {"ok": True, "kurz": _t(s_.get("short"), lang), "zusammenfassung": _t(s_.get("text"), lang)}
        if r["kind"] == "study":
            e = studie_zusammenfassen(int(a["id"]), Sprache(lang=lang))
            s_ = e["data"].get("summary") or {}
            return {"ok": True, "kurz": _t(s_.get("short"), lang), "evidenz": _t(s_.get("evidence"), lang), "einordnung": _t(s_.get("text"), lang)}
        if r["kind"] not in ("finding", "value"):
            return {"fehler": "Einordnung gibt es für Befunde, Messwerte, Studien und Videos."}
        e = ki_befund(int(a["id"]), Sprache(lang=lang))
        ai = e["data"].get("ai") or {}
        return {"ok": True, "kurz": _t(ai.get("summary"), lang), "einordnung": _t(ai.get("text"), lang)}

    return {"fehler": f"Unbekanntes Werkzeug: {name}"}


def _mcp_antwort(rid, ergebnis=None, fehler=None):
    if fehler is not None:
        return {"jsonrpc": "2.0", "id": rid, "error": fehler}
    return {"jsonrpc": "2.0", "id": rid, "result": ergebnis}


def _mcp_verarbeite(n, recht):
    method, rid, params = n.get("method"), n.get("id"), n.get("params") or {}
    if method == "initialize":
        return _mcp_antwort(rid, {
            "protocolVersion": MCP_PROTOKOLL,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "research-notebook", "version": "1.0.0"},
            "instructions": (
                "Research Notebook: persönliches, dreisprachiges (de/en/pl) Notizbuch, gegliedert in Themen (z. B. eine Erkrankung in "
                "der Familie oder ein Ernährungsthema, aber auch beliebige andere Recherchen). Je Thema: Werte & Befunde/Dokumente, Begriffe, Medikamente, Recherche-Notizen, "
                "Videos mit Zusammenfassung, Chats. Einstieg: themen_auflisten, dann notebook_ueberblick (mit thema), eintraege_suchen / "
                "eintrag_holen. Gesundheitsthemen enthalten sensible Daten: nur für den "
                "Auftrag der Menschen verwenden, die das Notebook führen, nicht weitergeben. Medizinische Aussagen als Einschätzung kennzeichnen, nie als Diagnose. "
                + ("Dieser Zugang darf auch schreiben: neue Texte in einer Sprache anlegen, die Übersetzung passiert automatisch. "
                   "Löschen nur auf ausdrückliche Anweisung eines Menschen." if recht == "write" else "Dieser Zugang darf nur lesen.")),
        })
    if method in ("notifications/initialized", "notifications/cancelled"):
        return None
    if method == "ping":
        return _mcp_antwort(rid, {})
    if method == "tools/list":
        tools = [{k: v for k, v in t.items() if k != "schreibt"} for t in MCP_TOOLS if recht == "write" or not t["schreibt"]]
        for t in tools:
            t["annotations"] = {"readOnlyHint": not next(x for x in MCP_TOOLS if x["name"] == t["name"])["schreibt"]}
        return _mcp_antwort(rid, {"tools": tools})
    if method == "tools/call":
        name, args = params.get("name", ""), params.get("arguments") or {}
        try:
            ergebnis = mcp_tool(name, args, recht)
        except HTTPException as ex:
            ergebnis = {"fehler": ex.detail}
        except Exception as ex:  # noqa: BLE001 — Werkzeugfehler zurückgeben statt den Server zu stören
            protokoll(f"FEHLER MCP {name}: {ex}")
            ergebnis = {"fehler": f"{type(ex).__name__}: {ex}"}
        if isinstance(ergebnis, dict) and "_content" in ergebnis:
            return _mcp_antwort(rid, {"content": ergebnis["_content"], "isError": False})
        return _mcp_antwort(rid, {"content": [{"type": "text", "text": json.dumps(ergebnis, ensure_ascii=False, indent=2)}],
                                  "isError": isinstance(ergebnis, dict) and "fehler" in ergebnis})
    if rid is None:
        return None
    return _mcp_antwort(rid, fehler={"code": -32601, "message": f"Unbekannte Methode: {method}"})


@app.get("/mcp/{token}")
def mcp_get(token: str):
    return Response(status_code=405 if mcp_recht(token) else 404)


@app.delete("/mcp/{token}")
def mcp_delete(token: str):
    return Response(status_code=204 if mcp_recht(token) else 404)


@app.post("/mcp/{token}")
async def mcp_post(token: str, request: Request):
    recht = mcp_recht(token)
    if not recht:
        return Response(status_code=404)
    try:
        nachricht = await request.json()
    except ValueError:
        return JSONResponse({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Kein gültiges JSON"}}, status_code=400)
    if isinstance(nachricht, list):
        antworten = [x for x in (_mcp_verarbeite(n, recht) for n in nachricht) if x]
        return JSONResponse(antworten) if antworten else Response(status_code=202)
    antwort = _mcp_verarbeite(nachricht, recht)
    return JSONResponse(antwort) if antwort is not None else Response(status_code=202)



# ---------------------------------------------------------------------------
# Studien: PubMed (veröffentlicht) und ClinicalTrials.gov (laufend) durchsuchen,
# übernehmen und von der KI einordnen lassen. Beide Schnittstellen sind frei, ohne Schlüssel.
# ---------------------------------------------------------------------------

import xml.etree.ElementTree as ET

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CTGOV = "https://clinicaltrials.gov/api/v2/studies"
STUDIEN_UA = {"User-Agent": "research-notebook/1.0 (private research notebook)"}
CT_FELDER = ("NCTId,BriefTitle,OfficialTitle,OverallStatus,Phase,Condition,LocationCountry,LeadSponsorName,StartDate,"
             "PrimaryCompletionDate,EnrollmentCount,InterventionName,StudyType")
STATUS_DE = {"RECRUITING": "rekrutiert", "NOT_YET_RECRUITING": "startet bald", "ACTIVE_NOT_RECRUITING": "läuft, keine Aufnahme",
             "COMPLETED": "abgeschlossen", "TERMINATED": "abgebrochen", "WITHDRAWN": "zurückgezogen", "SUSPENDED": "pausiert",
             "ENROLLING_BY_INVITATION": "nur auf Einladung", "UNKNOWN": "unbekannt"}


def _get(url, params=None, timeout=25):
    import time
    for versuch in range(3):
        try:
            r = httpx.get(url, params=params, headers=STUDIEN_UA, timeout=timeout)
        except httpx.HTTPError:
            raise HTTPException(502, "Die Studiendatenbank ist gerade nicht erreichbar.")
        # PubMed erlaubt ohne Schlüssel 3 Abrufe pro Sekunde — kurz warten statt scheitern
        if r.status_code != 429:
            break
        time.sleep(0.6 * (versuch + 1))
    if r.status_code != 200:
        raise HTTPException(502, f"Die Studiendatenbank meldet HTTP {r.status_code}.")
    return r


def _studientyp(pubtypes):
    rang = ["Meta-Analysis", "Systematic Review", "Practice Guideline", "Guideline", "Randomized Controlled Trial",
            "Clinical Trial, Phase III", "Clinical Trial, Phase II", "Clinical Trial, Phase I", "Clinical Trial",
            "Observational Study", "Review", "Case Reports"]
    for r in rang:
        if r in (pubtypes or []):
            return r
    return "Journal Article"


def pubmed_suche(q, limit=10, nur_neu=False):
    term = q + (" AND (\"last 5 years\"[dp])" if nur_neu else "")
    ids = _get(f"{EUTILS}/esearch.fcgi", {"db": "pubmed", "term": term, "retmode": "json", "retmax": limit, "sort": "relevance"}).json()["esearchresult"]
    if not ids.get("idlist"):
        return {"anzahl": int(ids.get("count", 0)), "treffer": []}
    summ = _get(f"{EUTILS}/esummary.fcgi", {"db": "pubmed", "retmode": "json", "id": ",".join(ids["idlist"])}).json()["result"]
    treffer = []
    for pmid in ids["idlist"]:
        r = summ.get(pmid) or {}
        doi = next((x["value"] for x in r.get("articleids", []) if x.get("idtype") == "doi"), "")
        autoren = [a["name"] for a in r.get("authors", [])]
        treffer.append({"source": "pubmed", "pmid": pmid, "title": r.get("title", "").rstrip("."), "journal": r.get("fulljournalname") or r.get("source", ""),
                        "year": (r.get("pubdate") or "")[:4], "authors": ", ".join(autoren[:3]) + (" et al." if len(autoren) > 3 else ""),
                        "doi": doi, "type": _studientyp(r.get("pubtype")), "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"})
    return {"anzahl": int(ids.get("count", 0)), "treffer": treffer}


def _ct_kurz(st):
    ps = st.get("protocolSection", {})
    idm, sm, dm = ps.get("identificationModule", {}), ps.get("statusModule", {}), ps.get("designModule", {})
    laender = sorted({l.get("country") for l in ps.get("contactsLocationsModule", {}).get("locations", []) if l.get("country")})
    nct = idm.get("nctId", "")
    return {"source": "trials", "nct": nct, "title": idm.get("briefTitle", ""), "status": sm.get("overallStatus", ""),
            "status_de": STATUS_DE.get(sm.get("overallStatus", ""), sm.get("overallStatus", "")),
            "phase": ", ".join(p.replace("PHASE", "Phase ").replace("EARLY_", "früh ").replace("NA", "–") for p in dm.get("phases", [])),
            "type": dm.get("studyType", ""), "enrollment": (dm.get("enrollmentInfo") or {}).get("count"),
            "sponsor": ps.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", ""),
            "start": (sm.get("startDateStruct") or {}).get("date", ""), "year": ((sm.get("startDateStruct") or {}).get("date", "") or "")[:4],
            "countries": laender, "conditions": ps.get("conditionsModule", {}).get("conditions", []),
            "interventions": [i.get("name") for i in ps.get("armsInterventionsModule", {}).get("interventions", [])],
            "url": f"https://clinicaltrials.gov/study/{nct}"}


def trials_suche(q, limit=10, land="", nur_offen=True):
    params = {"query.term": q, "pageSize": limit, "fields": CT_FELDER, "countTotal": "true"}
    if land:
        params["query.locn"] = land
    if nur_offen:
        params["filter.overallStatus"] = "RECRUITING,NOT_YET_RECRUITING"
    d = _get(CTGOV, params).json()
    return {"anzahl": d.get("totalCount", 0), "treffer": [_ct_kurz(s_) for s_ in d.get("studies", [])]}


@app.get("/api/studies/search")
def studien_suche(q: str, source: str = "pubmed", land: str = "", offen: bool = True, neu: bool = False, limit: int = 10):
    if not q.strip():
        raise HTTPException(400, "Bitte Suchbegriffe angeben.")
    limit = max(1, min(limit, 30))
    out = trials_suche(q.strip(), limit, land, offen) if source == "trials" else pubmed_suche(q.strip(), limit, neu)
    protokoll(f"Studiensuche {source}: {q.strip()[:60]} → {out['anzahl']}")
    return out


def pubmed_holen(pmid):
    t = pubmed_suche(f"{pmid}[uid]", 1)["treffer"]
    if not t:
        raise HTTPException(404, "Diese PubMed-ID gibt es nicht.")
    d = t[0]
    x = ET.fromstring(_get(f"{EUTILS}/efetch.fcgi", {"db": "pubmed", "retmode": "xml", "id": pmid}).content)
    teile = [((a.get("Label") + ": ") if a.get("Label") else "") + "".join(a.itertext()).strip() for a in x.iter("AbstractText")]
    d["abstract"] = "\n\n".join(t_ for t_ in teile if t_)
    alle = [f"{(au.findtext('LastName') or '')} {(au.findtext('Initials') or '')}".strip() for au in x.iter("Author")]
    if alle:
        d["authors"] = ", ".join(alle[:6]) + (" et al." if len(alle) > 6 else "")
    return d


def trial_holen(nct):
    st = _get(f"{CTGOV}/{nct}").json()
    d = _ct_kurz(st)
    ps = st.get("protocolSection", {})
    d["abstract"] = (ps.get("descriptionModule", {}).get("briefSummary") or "").strip()
    el = ps.get("eligibilityModule", {})
    d["eligibility"] = (el.get("eligibilityCriteria") or "").strip()[:8000]
    d["eligibility_meta"] = {"sex": el.get("sex"), "min_age": el.get("minimumAge"), "max_age": el.get("maximumAge")}
    orte = ps.get("contactsLocationsModule", {}).get("locations", [])
    d["locations"] = [{"facility": o.get("facility", ""), "city": o.get("city", ""), "country": o.get("country", ""), "status": o.get("status", "")}
                      for o in orte if o.get("country") in ("Germany", "Poland", "Austria", "Switzerland")][:40]
    d["title_official"] = ps.get("identificationModule", {}).get("officialTitle", "")
    return d


class StudieImport(BaseModel):
    topic: int | None = None
    pmid: str = ""
    nct: str = ""
    url: str = ""


def studien_ids(text):
    text = (text or "").strip()
    m = re.search(r"NCT\d{8}", text, re.I)
    if m:
        return "", m.group(0).upper()
    m = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", text) or re.fullmatch(r"(?:PMID:?\s*)?(\d{5,9})", text, re.I)
    if m:
        return m.group(1), ""
    m = re.search(r"10\.\d{4,9}/\S+", text)
    if m:
        ids = _get(f"{EUTILS}/esearch.fcgi", {"db": "pubmed", "term": f"{m.group(0)}[doi]", "retmode": "json"}).json()["esearchresult"]["idlist"]
        if ids:
            return ids[0], ""
    return "", ""


@app.post("/api/studies/import")
def studie_importieren(i: StudieImport):
    thema_setzen(i.topic)
    pmid, nct = i.pmid.strip(), i.nct.strip().upper()
    if not pmid and not nct:
        pmid, nct = studien_ids(i.url)
    if not pmid and not nct:
        raise HTTPException(400, "Keine PubMed-ID, NCT-Nummer oder DOI erkannt. Studie stattdessen von Hand anlegen.")
    with db() as con:
        for r in con.execute("SELECT * FROM entries WHERE kind='study' AND topic_id=?", (thema()["id"],)).fetchall():
            d_ = json.loads(r["data"])
            if (pmid and d_.get("pmid") == pmid) or (nct and d_.get("nct") == nct):
                raise HTTPException(409, "Diese Studie steht schon im Notizbuch.")
    d = trial_holen(nct) if nct else pubmed_holen(pmid)
    d["date"] = datetime.now().strftime("%Y-%m-%d")
    d["note"] = {l: "" for l in LANGS}
    e = neu(Entry(kind="study", data=d, topic_id=thema()["id"]))
    protokoll(f"Studie übernommen {pmid or nct} → #{e['id']}")
    return e


@app.post("/api/ai/studies")
def studien_gesamtbild(s_: Sprache):
    """Synthese über alle gespeicherten Studien des aktuellen Themas; wird als Analyse (scope studies) gespeichert."""
    thema_setzen(s_.topic)
    with db() as con:
        rows = [zeile(r) for r in con.execute("SELECT * FROM entries WHERE kind='study' AND topic_id=? ORDER BY id", (thema()["id"],))]
    if not rows:
        raise HTTPException(400, "In diesem Thema sind noch keine Studien gespeichert.")
    def de(v):
        return v.get("de") or next((x for x in v.values() if x), "") if isinstance(v, dict) else (v or "")
    teile = []
    for i, e in enumerate(rows, 1):
        d = e["data"]
        titel = d["title"] if isinstance(d.get("title"), str) else de(d.get("title"))
        kennung = d.get("nct") or (f"PMID {d['pmid']}" if d.get("pmid") else d.get("url", ""))
        eck = ", ".join(str(x) for x in (d.get("type") or d.get("phase"), d.get("year"), d.get("journal") or d.get("sponsor"),
                                         f"n={d['enrollment']}" if d.get("enrollment") else "", d.get("status_de")) if x)
        teil = f"### [{i}] {titel}\n{kennung} · {eck}"
        sm = d.get("summary") or {}
        if sm:
            teil += f"\nBisherige Einordnung: {de(sm.get('short'))} Belastbarkeit: {de(sm.get('evidence'))}"
        text = d.get("abstract") or de(d.get("body"))
        if text:
            teil += f"\n{'Registertext' if d.get('source') == 'trials' else 'Abstract'}: {text[:2500]}"
        if d.get("countries"):
            teil += f"\nLänder: {', '.join(d['countries'][:12])}"
        if de(d.get("note")):
            teil += f"\nEigene Notiz: {de(d.get('note'))}"
        teile.append(teil)
    auftrag = (
        f"Fasse alle {len(rows)} Studien zusammen, die im Notizbuch zum Thema „{thema_name()}“ ({thema_bezug()}) gespeichert sind. "
        "Verweise im Text auf einzelne Studien mit ihrer Nummer in eckigen Klammern, z. B. [2].\n\n" + "\n\n".join(teile)[:110000] + "\n\n"
        "Zum Bezug das Notizbuch (Werte, Befunde, Medikamentenplan):\n\n" + kontext(details=False)[:12000] + "\n\n"
        "Gliedere 'body' so: '## Überblick' (wie viele Studien, welche Arten, welcher Zeitraum, worum es insgesamt geht), "
        "'## Was die Studien gemeinsam zeigen' (Kernaussagen mit Zahlen, je mit [Nr.]), "
        "'## Widersprüche und offene Fragen', "
        "'## Wie belastbar das Gesamtbild ist' (Studientypen von Meta-Analyse/RCT bis Beobachtung, Größe, Aktualität, Sponsoren; "
        "eine Gesamteinschätzung), "
        "'## Laufende Studien' (nur wenn welche dabei sind: worum, für wen, Orte in Deutschland/Polen, Status), "
        "'## Was das für uns heißt' (Bezug zum Notizbuch, vorsichtig als Einschätzung; sagen, wenn sich etwas nicht übertragen lässt), "
        "'## Fragen fürs Gespräch'. Wenn nur eine Studie gespeichert ist, sag das und fasse sie entsprechend kürzer. "
        f"'title' z. B. „Studienlage {datetime.now():%d.%m.%Y} ({len(rows)} Studien)“. " + mehrsprachig_auftrag(s_.lang)
    )
    out = llm_json(auftrag, schema(title=i18n_schema(), body=i18n_schema()), aufwand="high")
    e = analyse_speichern("studies", out)
    protokoll(f"Studien-Gesamtbild Thema #{thema()['id']} ({len(rows)} Studien)")
    return e


@app.post("/api/ai/videos")
def videos_gesamtbild(s_: Sprache):
    """Synthese über alle Videos & Links des aktuellen Themas (Transkripte, Zusammenfassungen, Notizen); gespeichert als Analyse."""
    thema_setzen(s_.topic)
    with db() as con:
        rows = [zeile(r) for r in con.execute("SELECT * FROM entries WHERE kind='video' AND topic_id=? ORDER BY id", (thema()["id"],))]
    if not rows:
        raise HTTPException(400, "In diesem Thema sind noch keine Videos gespeichert.")
    def de(v):
        return v.get("de") or next((x for x in v.values() if x), "") if isinstance(v, dict) else (v or "")
    # Platz gerecht verteilen: insgesamt rund 110.000 Zeichen Transkript
    je_video = max(2500, 110000 // len(rows))
    teile, mit_text = [], 0
    for i, e in enumerate(rows, 1):
        d = e["data"]
        titel = d["title"] if isinstance(d.get("title"), str) else de(d.get("title"))
        teil = f"### [{i}] {titel}\n{d.get('channel', '')} · {d.get('duration') or ''} · Sprache {(d.get('vlang') or '?').upper()} · {d.get('url', '')}"
        sm = d.get("summary") or {}
        if sm:
            teil += f"\nBisherige Zusammenfassung: {de(sm.get('text'))[:3000]}"
        tr_ = (d.get("transcript") or {}).get("text", "")
        if tr_:
            mit_text += 1
            teil += f"\nTranskript (ggf. gekürzt):\n{tr_[:je_video]}"
        if de(d.get("note")):
            teil += f"\nEigene Notiz: {de(d.get('note'))}"
        teile.append(teil)
    auftrag = (
        f"Fasse alle {len(rows)} Videos bzw. Links zusammen, die im Notizbuch zum Thema „{thema_name()}“ ({thema_bezug()}) gespeichert sind "
        f"({mit_text} davon mit Transkript). Verweise im Text auf einzelne Videos mit ihrer Nummer in eckigen Klammern, z. B. [3].\n\n"
        + "\n\n".join(teile)[:130000] + "\n\n"
        "Zum Bezug das Notizbuch:\n\n" + kontext(details=False)[:10000] + "\n\n"
        "Gliedere 'body' so: '## Überblick' (worum es in den Videos insgesamt geht, Kanäle, Umfang), "
        "'## Die wichtigsten Erkenntnisse' (Kernaussagen mit [Nr.], mit Zahlen wo genannt), "
        "'## Wo sich die Videos unterscheiden oder widersprechen', "
        "'## Wie verlässlich das ist' (wer spricht, Belege, Aktualität, wo vereinfacht oder vom Stand der Wissenschaft abgewichen wird), "
        "'## Was das für uns heißt' (Bezug zum Notizbuch, als Einschätzung), "
        "'## Womit man anfangen sollte' (sinnvolle Reihenfolge der Videos mit kurzer Begründung), '## Offene Fragen'. "
        "Videos ohne Transkript nur anhand von Titel und Notiz einordnen und das kennzeichnen. "
        f"'title' z. B. „Videos im Überblick {datetime.now():%d.%m.%Y} ({len(rows)} Videos)“. " + mehrsprachig_auftrag(s_.lang)
    )
    out = llm_json(auftrag, schema(title=i18n_schema(), body=i18n_schema()), aufwand="medium")
    e = analyse_speichern("videos", out)
    protokoll(f"Video-Gesamtbild Thema #{thema()['id']} ({len(rows)} Videos, {mit_text} mit Transkript)")
    return e


@app.post("/api/studies/{eid}/summary")
def studie_zusammenfassen(eid: int, s: Sprache):
    thema_von_eintrag(eid)
    with db() as con:
        r = con.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone()
        if not r or r["kind"] != "study":
            raise HTTPException(404, "Studie nicht gefunden")
        e = zeile(r, con)
    d = e["data"]
    dateien, _ = dateien_fuer_ki(e["files"])
    titel = d["title"] if isinstance(d.get("title"), str) else (d.get("title") or {}).get("de", "")
    eckdaten = {k: d.get(k) for k in ("source", "pmid", "nct", "doi", "journal", "year", "authors", "type", "phase", "status",
                                      "enrollment", "sponsor", "countries", "conditions", "interventions", "eligibility_meta") if d.get(k)}
    laufend = d.get("source") == "trials"
    auftrag = (
        f"Ordne diese {'laufende klinische Studie' if laufend else 'Studie / Veröffentlichung'} für die Menschen ein, die dieses Notizbuch führen:\n\n"
        f"Titel: {titel}\nEckdaten: {json.dumps(eckdaten, ensure_ascii=False)}\n\n"
        f"{'Zusammenfassung des Registers' if laufend else 'Abstract'}:\n{(d.get('abstract') or _t(d.get('body'), 'de') or '(keiner)')[:12000]}\n\n"
        + (f"Einschlusskriterien:\n{d.get('eligibility', '')[:8000]}\n\nStudienorte in DE/PL/AT/CH: {json.dumps(d.get('locations', [])[:25], ensure_ascii=False)}\n\n" if laufend else "")
        + ("Angehängte Dokumente (z. B. Volltext) liegen bei — einbeziehen.\n\n" if dateien else "")
        + f"Zum Bezug das Notizbuch:\n\n{kontext(details=False)[:8000]}\n\n"
        "Gliedere 'text' so: '## Worum es geht' (Fragestellung in 2–3 Sätzen), "
        + ("'## Wer teilnehmen kann' (wichtigste Ein- und Ausschlusskriterien verständlich), '## Wo' (Studienorte in Deutschland/Polen "
           "mit Stadt, Status), '## Passt das zu uns?' (Abgleich mit dem Notizbuch — vorsichtig, als Einschätzung; was man dem "
           "Behandlungsteam vorlegen sollte), '## Nächste Schritte' (wie man nachfragt). "
           if laufend else
           "'## Ergebnis' (die wichtigsten Zahlen verständlich: absolute Unterschiede, Überleben, Nebenwirkungen), "
           "'## Wie belastbar' (Studientyp, Größe, Kontrollgruppe, Nachbeobachtung, Interessenkonflikte/Sponsor, Evidenzstufe), "
           "'## Was das für uns heißt' (Bezug zum Notizbuch, nur soweit belegbar; sonst sagen, dass es nicht übertragbar ist), "
           "'## Fragen fürs Gespräch'. ")
        + "'short' ist ein Satz mit der Kernaussage. 'evidence' ist eine kurze Einstufung wie „hoch (Phase-III-RCT, n=557)“. "
        + mehrsprachig_auftrag(s.lang)
    )
    out = llm_json(auftrag, schema(short=i18n_schema(), text=i18n_schema(), evidence=i18n_schema()), dateien=dateien, aufwand="medium")
    summary = {"short": out["short"], "text": out["text"], "evidence": out["evidence"], "date": jetzt()[:16], "model": out["_model"]}
    with db() as con:
        r = con.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone()
        data = json.loads(r["data"])
        data["summary"] = summary
        con.execute("UPDATE entries SET data=?, updated=? WHERE id=?", (json.dumps(data, ensure_ascii=False), jetzt(), eid))
        out_e = zeile(con.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone(), con)
    protokoll(f"Studie eingeordnet #{eid}")
    return out_e



# ---------------------------------------------------------------------------
# CSV-Import von Messwerten (z. B. Blutdruck aus einem Messgerät oder einer App)
# ---------------------------------------------------------------------------

import csv
import io

CSV_MUSTER = [  # (Schlüssel, Muster für Spaltennamen, Einheit, Ref von, Ref bis)
    ("bp_sys", r"sys|skurcz", "mmHg", None, 140),
    ("bp_dia", r"dia|rozkurcz", "mmHg", None, 90),
    ("pulse", r"puls|pulse|heart.?rate|herz.?frequenz|\bhr\b|bpm|tętno", "/min", 50, 100),
    ("weight", r"gewicht|weight|waga|masa", "kg", None, None),
    ("glucose", r"zucker|glucose|glukose|glukoza", "mg/dl", 70, 100),
]
DATUM_SPALTE = r"datum|date|data|tag|day|zeitpunkt|timestamp|measured|gemessen"
ZEIT_SPALTE = r"^(zeit|uhrzeit|time|godzina|czas)\b"


def _csv_text(text):
    text = (text or "").lstrip("\ufeff")
    if len(text) > 5_000_000:
        raise HTTPException(413, "Die CSV-Datei ist zu groß (höchstens 5 MB).")
    zeilen = [z for z in text.splitlines() if z.strip()]
    if len(zeilen) < 2:
        raise HTTPException(400, "Die Datei enthält keine Tabelle (mindestens Kopfzeile und eine Datenzeile nötig).")
    probe = "\n".join(zeilen[:20])
    try:
        trenner = csv.Sniffer().sniff(probe, delimiters=";,\t|").delimiter
    except csv.Error:
        trenner = max(";,\t|", key=lambda t: probe.count(t))
    reihen = [r for r in csv.reader(io.StringIO("\n".join(zeilen)), delimiter=trenner)]
    # Vorspann mancher Exporte überspringen: Kopfzeile = erste Zeile mit der häufigsten Spaltenzahl
    breite = max(set(len(r) for r in reihen), key=lambda n: sum(1 for r in reihen if len(r) == n))
    if breite < 2:
        raise HTTPException(400, "Keine Spalten erkannt — ist es wirklich eine CSV-Datei?")
    start = next(i for i, r in enumerate(reihen) if len(r) == breite)
    kopf = [k.strip() or f"Spalte {i + 1}" for i, k in enumerate(reihen[start])]
    daten = [r for r in reihen[start + 1:] if len(r) == breite and any(c.strip() for c in r)]
    return trenner, kopf, daten


def _zahl_csv(x):
    m = re.search(r"-?\d+(?:[.,]\d+)?", str(x or ""))
    return float(m.group(0).replace(",", ".")) if m else None


MONATE = [  # Anfänge von Monatsnamen in DE/EN/PL (auch abgekürzt und gebeugt: „Okt.“, „Oct“, „października“)
    ("jan", 1), ("jän", 1), ("sty", 1), ("feb", 2), ("lut", 2), ("mär", 3), ("maer", 3), ("mar", 3), ("apr", 4), ("kwi", 4),
    ("mai", 5), ("may", 5), ("maj", 5), ("jun", 6), ("cze", 6), ("jul", 7), ("lip", 7), ("aug", 8), ("sie", 8),
    ("sep", 9), ("wrz", 9), ("okt", 10), ("oct", 10), ("paź", 10), ("paz", 10), ("nov", 11), ("lis", 11),
    ("dez", 12), ("dec", 12), ("gru", 12),
]


def _monat(wort):
    w = wort.lower().strip(".")
    return next((n for pre, n in MONATE if w.startswith(pre)), None) if len(w) >= 3 else None


def _monat_im_text(t):
    """„11. Okt. 2026“, „11 October 2026“, „Oct 11, 2026“, „11 paź 2026“ → (Jahr, Monat, Tag)"""
    buchst = r"[A-Za-zÄÖÜäöüßąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+"
    m = re.search(r"(\d{1,2})\.?\s+(" + buchst + r")\.?,?\s+(\d{4})", t)
    if m and _monat(m.group(2)):
        return int(m.group(3)), _monat(m.group(2)), int(m.group(1))
    m = re.search(r"(" + buchst + r")\.?\s+(\d{1,2}),?\s+(\d{4})", t)
    if m and _monat(m.group(1)):
        return int(m.group(3)), _monat(m.group(1)), int(m.group(2))
    return None


def _datum_csv(x):
    """→ (YYYY-MM-DD, HH:MM oder ''), sonst None. Versteht 2026-10-11, 11.10.2026, 11/10/2026, mit oder ohne Uhrzeit."""
    t = str(x or "").strip()
    zeit = ""
    mz = re.search(r"(\d{1,2}):(\d{2})(?::\d{2})?\s*(am|pm|AM|PM)?", t)
    if mz:
        h, mi = int(mz.group(1)), int(mz.group(2))
        if mz.group(3) and mz.group(3).lower() == "pm" and h < 12:
            h += 12
        if mz.group(3) and mz.group(3).lower() == "am" and h == 12:
            h = 0
        zeit = f"{h:02d}:{mi:02d}"
    m = re.search(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", t)
    mn = _monat_im_text(t) if not m else None
    if m:
        j, mo, ta = int(m.group(1)), int(m.group(2)), int(m.group(3))
    elif mn:
        j, mo, ta = mn
    else:
        m = re.search(r"(\d{1,2})[./](\d{1,2})[./](\d{2,4})", t)
        if not m:
            return None
        a_, b_, j = int(m.group(1)), int(m.group(2)), int(m.group(3))
        j += 2000 if j < 100 else 0
        # Europäische Schreibweise (Tag zuerst), außer es geht nur amerikanisch (zweite Zahl > 12)
        ta, mo = (b_, a_) if (b_ > 12 and a_ <= 12 and "/" in t) else (a_, b_)
    try:
        return datetime(j, mo, ta).strftime("%Y-%m-%d"), zeit
    except ValueError:
        return None


def _csv_vorschlag(kopf, daten):
    probe = daten[:30]
    datum_spalte = next((i for i, k in enumerate(kopf) if re.search(DATUM_SPALTE, k, re.I) and sum(1 for r in probe if _datum_csv(r[i])) >= len(probe) // 2), None)
    if datum_spalte is None:
        datum_spalte = next((i for i in range(len(kopf)) if probe and sum(1 for r in probe if _datum_csv(r[i])) >= max(1, len(probe) * 0.8)), None)
    zeit_spalte = next((i for i, k in enumerate(kopf) if i != datum_spalte and re.search(ZEIT_SPALTE, k.strip(), re.I)), None)
    spalten = []
    vergeben = set()
    for i, k in enumerate(kopf):
        if i in (datum_spalte, zeit_spalte):
            continue
        zahlen = sum(1 for r in probe if _zahl_csv(r[i]) is not None)
        if not probe or zahlen < len(probe) * 0.6:
            continue
        treffer = next((m for m in CSV_MUSTER if m[0] not in vergeben and re.search(m[1], k, re.I)), None)
        einheit = (re.search(r"\(([^)]+)\)|\[([^\]]+)\]", k) or [None])
        einheit = (einheit.group(1) or einheit.group(2)).strip() if hasattr(einheit, "group") else ""
        if treffer:
            vergeben.add(treffer[0])
            spalten.append({"col": i, "use": True, "param": treffer[0], "label": "", "unit": einheit or treffer[2], "low": treffer[3], "high": treffer[4]})
        else:
            name = re.sub(r"\s*[\(\[].*?[\)\]]", "", k).strip() or k
            spalten.append({"col": i, "use": False, "param": "_other", "label": name, "unit": einheit, "low": None, "high": None})
    return {"date_col": datum_spalte, "time_col": zeit_spalte, "columns": spalten}


class CsvText(BaseModel):
    text: str
    topic: int | None = None


@app.post("/api/values/csv/preview")
def csv_vorschau(c: CsvText):
    trenner, kopf, daten = _csv_text(c.text)
    return {"delimiter": trenner, "headers": kopf, "sample": daten[:6], "total": len(daten), "guess": _csv_vorschlag(kopf, daten)}


class CsvKi(BaseModel):
    text: str
    topic: int | None = None
    lang: str = "de"


@app.post("/api/values/csv/ki")
def csv_ki_vorschlag(c: CsvKi):
    """Die KI entscheidet vor dem Import, wie die Spalten gespeichert werden — passend zum Thema und zu vorhandenen Reihen."""
    thema_setzen(c.topic)
    _, kopf, daten = _csv_text(c.text)
    with db() as con:
        rows = [json.loads(r["data"]) for r in con.execute("SELECT data FROM entries WHERE kind='value' AND topic_id=?", (thema()["id"],))]
    reihen = {}
    for d in rows:
        k = (d.get("param"), d.get("paramLabel") or "")
        reihen.setdefault(k, {"param": d.get("param"), "label": d.get("paramLabel") or PARAM_NAMEN.get(d.get("param"), ""),
                               "unit": d.get("unit", ""), "low": d.get("low"), "high": d.get("high"), "anzahl": 0})["anzahl"] += 1
    vorlagen = {k: v for k, v in PARAM_NAMEN.items()}
    tabelle = "\n".join(f"{i}: {k}" for i, k in enumerate(kopf))
    beispiele = "\n".join(" | ".join(r) for r in daten[:8])
    auftrag = (
        f"Eine CSV-Datei soll als Messwerte in das Notizbuch zum Thema „{thema_name()}“ ({thema_bezug()}; Art: "
        f"{'Gesundheit' if ist_gesundheit() else 'allgemein'}) importiert werden. Entscheide, wie die Werte gespeichert werden.\n\n"
        f"Spalten (Index: Name):\n{tabelle}\n\nErste Zeilen:\n{beispiele}\n\n"
        f"Messreihen, die es in diesem Thema schon gibt (wiederverwenden, damit gleiche Werte in derselben Reihe landen — gleicher "
        f"param, gleiche Bezeichnung, gleiche Einheit): {json.dumps(list(reihen.values()), ensure_ascii=False) or '[]'}\n\n"
        f"Feste Vorlagen (param-Schlüssel → Name), bevorzugt nutzen, wenn eine Spalte genau das misst: {json.dumps(vorlagen, ensure_ascii=False)}. "
        "Sonst param \"_other\" mit einer klaren deutschen Bezeichnung ohne Einheit in Klammern.\n\n"
        "Regeln: date_col = Spalte mit dem Datum (darf Uhrzeit enthalten); time_col = eigene Uhrzeit-Spalte oder null. "
        "Für jede andere Spalte ein Eintrag in columns: use = true nur für echte Messwerte (Zahlen), false für Notizen, IDs, Text, "
        "Geräteinfos. unit ohne Klammern. low/high = Referenz- bzw. Zielbereich, der zu DIESEM Thema passt (z. B. bei Bluthochdruck "
        "und Heimmessung die Grenze 135/85 mmHg, bei anderen Themen die dort übliche Grenze; null, wenn es keinen sinnvollen gibt). "
        "Vorhandene Reihen haben Vorrang: misst eine Spalte dasselbe wie eine vorhandene Reihe, nimm GENAU deren param, Bezeichnung und "
        "Einheit (sonst entstehen doppelte Reihen). Nur wenn es noch keine Reihe gibt: Blutdruck als bp_sys/bp_dia, Puls als pulse "
        "— die Oberfläche fasst Blutdruck und Puls je Messung zusammen. "
        "'reason' erklärt in 1–3 Sätzen, was du entschieden hast und warum (z. B. welche Grenzwerte und weshalb). "
        + mehrsprachig_auftrag(c.lang)
    )
    nummer = {"type": ["number", "null"]}
    spalte = schema(col={"type": "integer"}, use={"type": "boolean"}, param={"type": "string"}, label={"type": "string"},
                    unit={"type": "string"}, low=nummer, high=nummer)
    out = llm_json(auftrag, schema(date_col={"type": ["integer", "null"]}, time_col={"type": ["integer", "null"]},
                                   columns={"type": "array", "items": spalte}, reason=i18n_schema()), schnell=False, aufwand="low")
    # Absichern: nur gültige Spalten, bekannte Schlüssel
    gueltig = []
    for x in out.get("columns", []):
        if not isinstance(x.get("col"), int) or not (0 <= x["col"] < len(kopf)) or x["col"] in (out.get("date_col"), out.get("time_col")):
            continue
        if x.get("param") not in PARAM_NAMEN and x.get("param") != "_other":
            x["param"] = "_other"
        if x["param"] != "_other":
            x["label"] = ""
        gueltig.append(x)
    dc = out.get("date_col") if isinstance(out.get("date_col"), int) and 0 <= out["date_col"] < len(kopf) else None
    tc = out.get("time_col") if isinstance(out.get("time_col"), int) and 0 <= out["time_col"] < len(kopf) else None
    protokoll(f"CSV-KI-Vorschlag Thema #{thema()['id']}: {sum(1 for x in gueltig if x.get('use'))} Spalten")
    return {"date_col": dc, "time_col": tc, "columns": gueltig, "reason": out.get("reason"), "model": out["_model"]}


class CsvImport(BaseModel):
    text: str
    topic: int | None = None
    date_col: int
    time_col: int | None = None
    columns: list[dict]


@app.post("/api/values/csv/import")
def csv_importieren(c: CsvImport):
    tid = thema_setzen(c.topic)["id"]
    _, kopf, daten = _csv_text(c.text)
    if not (0 <= c.date_col < len(kopf)):
        raise HTTPException(400, "Bitte die Datumsspalte wählen.")
    spalten = [x for x in c.columns if x.get("use") and isinstance(x.get("col"), int) and 0 <= x["col"] < len(kopf)]
    if not spalten:
        raise HTTPException(400, "Bitte mindestens eine Spalte zum Importieren auswählen.")
    for x in spalten:
        if x.get("param") == "_other" and not (x.get("label") or "").strip():
            x["label"] = kopf[x["col"]]
    with db() as con:
        vorhanden = set()
        def schl(param, label, datum, zeit, wert):
            art = vital_art({"param": param, "paramLabel": label})
            return ("vital:" + art, "", datum, zeit or "", wert) if art else (param, label or "", datum, zeit or "", wert)
        for r in con.execute("SELECT data FROM entries WHERE kind='value' AND topic_id=?", (tid,)):
            d = json.loads(r["data"])
            vorhanden.add(schl(d.get("param"), d.get("paramLabel"), d.get("date"), d.get("time"), d.get("value")))
        neu_n, doppelt, ohne_datum, jetzt_ = 0, 0, 0, jetzt()
        for zeile_ in daten:
            dz = _datum_csv(zeile_[c.date_col])
            if not dz:
                ohne_datum += 1
                continue
            datum, zeit = dz
            if c.time_col is not None and 0 <= c.time_col < len(kopf):
                z2 = _datum_csv("2000-01-01 " + zeile_[c.time_col])
                zeit = z2[1] if z2 and z2[1] else zeit
            for x in spalten:
                wert = _zahl_csv(zeile_[x["col"]])
                if wert is None:
                    continue
                param = x.get("param") or "_other"
                label = (x.get("label") or "").strip() if param == "_other" else ""
                schluessel = schl(param, label, datum, zeit, wert)
                if schluessel in vorhanden:
                    doppelt += 1
                    continue
                vorhanden.add(schluessel)
                data = {"param": param, "paramLabel": label, "date": datum, "time": zeit, "value": wert,
                        "unit": (x.get("unit") or "").strip(), "low": x.get("low"), "high": x.get("high"),
                        "note": {l: "" for l in LANGS}, "source": "csv"}
                con.execute("INSERT INTO entries (kind, data, created, updated, topic_id) VALUES (?,?,?,?,?)",
                            ("value", json.dumps(data, ensure_ascii=False), jetzt_, jetzt_, tid))
                neu_n += 1
    protokoll(f"CSV-Import Thema #{tid}: {neu_n} Messwerte neu, {doppelt} doppelt übersprungen, {ohne_datum} Zeilen ohne Datum")
    return {"created": neu_n, "duplicates": doppelt, "no_date": ohne_datum, "rows": len(daten)}


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html", headers={"Cache-Control": "no-cache"})


app.mount("/static", StaticFiles(directory=STATIC), name="static")
