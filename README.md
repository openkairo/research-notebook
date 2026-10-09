# Research Notebook

Ein persönliches Recherche-Notizbuch für den eigenen Server, dreisprachig (Deutsch, Englisch, Polnisch). Gegliedert in **Themen**. Jedes Thema hat eigene Unterbereiche, die du frei ein- und ausschaltest:

| Bereich | Wofür |
| --- | --- |
| **Werte & Befunde** | Laborwerte und Messungen mit Verlauf und Referenzbereich, Befunde oder Dokumente samt PDF- und Foto-Anhängen |
| **Begriffe** | Fachbegriffe mit Erklärung, nach Schlagwort filterbar |
| **Medikamente** | Wirkung, Nebenwirkungen, eigene Notizen |
| **Recherche** | Notizen mit Quellen |
| **Studien** | Suche in PubMed und ClinicalTrials.gov, Übernehmen per Klick, PubMed-ID, NCT-Nummer oder DOI |
| **Videos & Links** | YouTube-Videos und Links mit Vorschaubild, Transkript und Zusammenfassung |
| **Chat** | Gespräch mit der KI, auf Wunsch mit dem Inhalt des Themas und Websuche |

Themen gibt es in zwei Arten: **Gesundheit** (mit Laborvorlagen und medizinischen Hinweisen der KI) und **Allgemein** (Technik, Recht, Reisen, alles andere).

### KI-Funktionen (optional, mit eigenem OpenAI-Schlüssel)

- Befunde einordnen, auch angehängte PDFs und Fotos
- Werte-Verläufe analysieren, Hinweise zum ganzen Thema erstellen
- Begriffe und Medikamente erklären
- Recherche mit Websuche und Quellenangaben, Studien einordnen samt Belastbarkeit
- **Markieren & erklären:** an jeder Stelle ein Wort markieren, erklären lassen, in Begriffe übernehmen
- Alle Texte werden automatisch ins Deutsche, Englische und Polnische übersetzt

Ohne Schlüssel funktioniert das Notizbuch vollständig, nur die KI-Knöpfe fehlen.

### MCP-Schnittstelle für KI-Agenten

Claude, ChatGPT oder eigene Automationen können über [MCP](https://modelcontextprotocol.io) lesen und, mit dem Schreib-Zugang, Einträge anlegen. Es gibt zwei getrennte Zugänge, *nur lesen* und *lesen + schreiben*. Ihre Adressen stehen in der Oberfläche unter ⚙ Einstellungen und lassen sich dort jederzeit neu erzeugen.

> **Hinweis:** Das Notizbuch ersetzt keine ärztliche Beratung. KI-Ausgaben sind Einschätzungen und können Fehler enthalten.

---

## Installation

Voraussetzung: [Docker](https://docs.docker.com/get-docker/) mit Docker Compose.

```bash
git clone https://github.com/openkairo/research-notebook.git
cd research-notebook
cp .env.example .env
```

In `.env` mindestens **`APP_PASSWORD`** setzen. Dann starten:

```bash
docker compose up -d --build
```

Das Notizbuch läuft jetzt unter <http://127.0.0.1:8000>. Anmelden kannst du dich mit `APP_USER` (Standard `admin`) und deinem Passwort.

**Beispielinhalte:** Mit `EXAMPLE_DATA=1` in `.env` startet eine leere Datenbank mit einem Beispielthema „Brustgesundheit“ (19 Begriffe, 16 Medikamente und 4 Quellen in drei Sprachen). Ohne diese Einstellung beginnt das Notizbuch mit einem leeren Thema.

### Im Internet betreiben

Die einfache `docker-compose.yml` ist nur auf dem eigenen Rechner erreichbar (`127.0.0.1`). Für den Zugriff von außen gehört ein Proxy mit HTTPS davor. Für Traefik liegt eine fertige Vorlage bei:

```bash
# in .env: DOMAIN und BASIC_AUTH_USERS setzen (oder APP_PASSWORD und die Middleware weglassen)
docker compose -f docker-compose.traefik.yml up -d --build
```

Gesundheitsdaten nie ohne Anmeldung ins Netz stellen. Entweder `APP_PASSWORD` setzen oder die Anmeldung im Proxy erledigen.

### Einstellungen

| Variable | Bedeutung |
| --- | --- |
| `APP_USER`, `APP_PASSWORD` | Eingebaute Anmeldung (HTTP Basic). Ohne Passwort ist die Oberfläche offen, dann nur hinter einem Proxy mit Anmeldung betreiben. |
| `PUBLIC_URL` | Öffentliche Adresse für die MCP-Links (sonst aus der Anfrage abgeleitet) |
| `EXAMPLE_DATA` | `1` = Beispielthema beim ersten Start |
| `ANTHROPIC_API_KEY`, `CLAUDE_MODEL` | Optional: Claude für Übersetzungen und Zusammenfassungen, solange kein OpenAI-Schlüssel eingetragen ist |

Den **OpenAI-Schlüssel**, das **Modell** und den **TranscriptAPI-Schlüssel** für Video-Transkripte trägst du in der Oberfläche unter ⚙ Einstellungen ein. Sie werden in der Datenbank auf dem Server gespeichert und nicht wieder vollständig angezeigt.

### Daten und Sicherung

- Alles liegt im Ordner `data/`: SQLite-Datenbank, Anhänge, Vorschaubilder, Protokoll.
- Beim Start und täglich legt das Notizbuch eine Kopie der Datenbank in `data/backup/` ab (14 Tage). Den Ordner `data/files/` (Anhänge) bitte selbst mitsichern.
- Unten auf jeder Seite gibt es einen Export als JSON.

### Datenschutz

- Ohne KI-Schlüssel verlassen keine Inhalte den Server. Ausnahmen sind Abrufe, die du selbst auslöst: Studiensuche (PubMed, ClinicalTrials.gov), Vorschaubilder (YouTube) und Link-Vorschauen.
- Mit KI-Funktionen gehen die jeweils nötigen Inhalte an OpenAI (bzw. Anthropic), für Analysen auch Werte, Befunde und Anhänge.
- Video-Transkripte laufen über TranscriptAPI.com, weil YouTube Abrufe von Servern meist sperrt.

### Aktualisieren

```bash
git pull
docker compose up -d --build
```

Die Datenbank wird beim Start automatisch auf den neuen Stand gebracht.

---

## English

**Research Notebook** is a self-hosted, trilingual (German, English, Polish) research notebook organised by **topics**. Each topic has its own sections: values & findings (lab values with history, documents with PDF/photo attachments), glossary, medicines, research notes, **studies** (PubMed and ClinicalTrials.gov search and import), videos & links (with thumbnails, transcripts, summaries) and an AI chat. Optional AI features use your own OpenAI key: assess findings and PDFs, analyse value trends, explain terms (select any word on the page and click *Explain*), research with web search and sources, assess studies. Every text is translated into all three languages automatically. An **MCP endpoint** with separate read-only and read-write keys lets AI agents use the notebook.

```bash
git clone https://github.com/openkairo/research-notebook.git && cd research-notebook
cp .env.example .env      # set APP_PASSWORD
docker compose up -d --build
# open http://127.0.0.1:8000
```

The interface is available in German, English and Polish. For internet access put an HTTPS proxy in front (a Traefik template is included in `docker-compose.traefik.yml`), and never expose health data without authentication. Not a substitute for medical advice.

## Lizenz / License

[MIT](LICENSE)
