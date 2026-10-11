/* Research Notebook — Oberfläche. Absichtlich ES2018 ohne ?. und ??, damit sie auch auf alten iPhones lädt. */
(function () {
  "use strict";

  var LANGS = ["de", "en", "pl"];

  var T = {
    appName: { de: "Research Notebook", en: "Research Notebook", pl: "Research Notebook" },
    appSub: { de: "Dein Wissen, nach Themen geordnet", en: "Your knowledge, sorted by topic", pl: "Twoja wiedza, uporządkowana tematycznie" },
    tab_home: { de: "Übersicht", en: "Overview", pl: "Przegląd" },
    tab_values: { de: "Werte & Befunde", en: "Values & findings", pl: "Wyniki i opisy" },
    tab_glossary: { de: "Begriffe", en: "Glossary", pl: "Słowniczek" },
    tab_med: { de: "Medikamente", en: "Medicines", pl: "Leki" },
    tab_research: { de: "Recherche", en: "Research", pl: "Źródła i notatki" },
    search: { de: "Alles durchsuchen …", en: "Search everything …", pl: "Szukaj we wszystkim …" },
    new_value: { de: "+ Wert eintragen", en: "+ Add value", pl: "+ Dodaj wynik" },
    new_finding: { de: "+ Befund / Einschätzung", en: "+ Finding / assessment", pl: "+ Opis / ocena" },
    new_glossary: { de: "+ Begriff", en: "+ Term", pl: "+ Pojęcie" },
    new_med: { de: "+ Medikament", en: "+ Medicine", pl: "+ Lek" },
    new_research: { de: "+ Recherche-Notiz", en: "+ Research note", pl: "+ Notatka" },
    new_any: { de: "+ Neuer Eintrag", en: "+ New entry", pl: "+ Nowy wpis" },
    edit: { de: "Bearbeiten", en: "Edit", pl: "Edytuj" },
    del: { de: "Löschen", en: "Delete", pl: "Usuń" },
    del_q: { de: "Wirklich löschen?", en: "Delete for good?", pl: "Na pewno usunąć?" },
    yes_del: { de: "Ja, löschen", en: "Yes, delete", pl: "Tak, usuń" },
    cancel: { de: "Abbrechen", en: "Cancel", pl: "Anuluj" },
    save: { de: "Speichern", en: "Save", pl: "Zapisz" },
    saved: { de: "Gespeichert", en: "Saved", pl: "Zapisano" },
    deleted: { de: "Gelöscht", en: "Deleted", pl: "Usunięto" },
    saving: { de: "Speichere …", en: "Saving …", pl: "Zapisuję …" },
    translating: { de: "Übersetze in die anderen Sprachen …", en: "Translating into the other languages …", pl: "Tłumaczę na pozostałe języki …" },
    trans_fail: { de: "Übersetzung nicht möglich — Text wurde in allen Sprachen unverändert gespeichert.", en: "Translation unavailable — text saved unchanged in all languages.", pl: "Tłumaczenie niedostępne — tekst zapisano bez zmian we wszystkich językach." },
    autoTranslate: { de: "Automatisch übersetzen (DE · EN · PL)", en: "Translate automatically (DE · EN · PL)", pl: "Tłumacz automatycznie (DE · EN · PL)" },
    disclaimer: {
      de: "Persönliche Sammlung zum Nachlesen und Mitnehmen ins Arztgespräch. Sie ersetzt keine ärztliche Beratung. Referenzbereiche sind typische Erwachsenenwerte — maßgeblich ist immer der Bereich auf dem eigenen Laborbefund.",
      en: "A personal collection to read up and take to appointments. It does not replace medical advice. Reference ranges are typical adult values — the range printed on your own lab report always takes precedence.",
      pl: "Osobisty zbiór do czytania i zabrania na wizytę. Nie zastępuje porady lekarskiej. Zakresy referencyjne to typowe wartości dla dorosłych — zawsze obowiązuje zakres podany na własnym wyniku z laboratorium."
    },
    export: { de: "Sicherung herunterladen (JSON)", en: "Download backup (JSON)", pl: "Pobierz kopię zapasową (JSON)" },
    home_intro: {
      de: "Alles an einem Ort: eigene Laborwerte mit Verlauf, Befunde mit eigener Einschätzung, Fachbegriffe, Medikamente und Recherche-Notizen — in Deutsch, Englisch und Polnisch.",
      en: "Everything in one place: your own lab values over time, findings with your own assessment, medical terms, medicines and research notes — in German, English and Polish.",
      pl: "Wszystko w jednym miejscu: własne wyniki badań w czasie, opisy z własną oceną, pojęcia medyczne, leki i notatki — po niemiecku, angielsku i polsku."
    },
    latest_values: { de: "Letzte Werte", en: "Latest values", pl: "Ostatnie wyniki" },
    recent: { de: "Zuletzt bearbeitet", en: "Recently edited", pl: "Ostatnio edytowane" },
    labs: { de: "Laborwerte & Messungen", en: "Lab values & measurements", pl: "Wyniki badań i pomiary" },
    labs_sub: { de: "Je Wert der Verlauf, grün hinterlegt der Referenzbereich.", en: "History per value; the green band is the reference range.", pl: "Przebieg dla każdego parametru; zielony pas to zakres referencyjny." },
    findings: { de: "Befunde & eigene Einschätzung", en: "Findings & own assessment", pl: "Opisy badań i własna ocena" },
    findings_sub: { de: "Pathologie, Bildgebung, Arztbriefe — und was man selbst daraus liest.", en: "Pathology, imaging, doctor’s letters — and what you make of them.", pl: "Patomorfologia, obrazowanie, wypisy — i własna interpretacja." },
    empty_values: { de: "Noch keine Werte. Trag den ersten Laborwert ein, z. B. Leukozyten vom letzten Blutbild.", en: "No values yet. Add your first lab value, e.g. white blood cells from the last blood count.", pl: "Brak wyników. Dodaj pierwszy, np. leukocyty z ostatniej morfologii." },
    empty_findings: { de: "Noch keine Befunde. Hier passen z. B. Arztbriefe, Laborberichte oder Bildgebungsbefunde und die eigene Deutung hinein.", en: "No findings yet. This is the place for e.g. doctor’s letters, lab reports or imaging results and your own reading of them.", pl: "Brak opisów. Tu pasują np. wypisy, wyniki badań lub opisy obrazowania i własna interpretacja." },
    empty_search: { de: "Keine Treffer.", en: "No matches.", pl: "Brak wyników wyszukiwania." },
    all: { de: "Alle", en: "All", pl: "Wszystkie" },
    f_title: { de: "Titel", en: "Title", pl: "Tytuł" },
    f_term: { de: "Begriff", en: "Term", pl: "Pojęcie" },
    f_expl: { de: "Erklärung", en: "Explanation", pl: "Wyjaśnienie" },
    f_tags: { de: "Themen (mit Komma getrennt)", en: "Topics (comma-separated)", pl: "Tematy (oddzielone przecinkami)" },
    f_name: { de: "Name / Wirkstoff", en: "Name / active ingredient", pl: "Nazwa / substancja czynna" },
    f_cls: { de: "Wirkstoffgruppe", en: "Drug class", pl: "Grupa leków" },
    f_how: { de: "Wirkung & Einsatz", en: "How it works & when it is used", pl: "Działanie i zastosowanie" },
    f_side: { de: "Häufige Nebenwirkungen", en: "Common side effects", pl: "Częste działania niepożądane" },
    f_notes: { de: "Eigene Notizen (Dosis, Erfahrungen, Fragen)", en: "Own notes (dose, experience, questions)", pl: "Własne notatki (dawka, doświadczenia, pytania)" },
    f_text: { de: "Notiz", en: "Note", pl: "Notatka" },
    f_source: { de: "Quelle (Link)", en: "Source (link)", pl: "Źródło (link)" },
    f_date: { de: "Datum", en: "Date", pl: "Data" },
    f_param: { de: "Wert", en: "Parameter", pl: "Parametr" },
    f_param_other: { de: "Anderer Wert …", en: "Other parameter …", pl: "Inny parametr …" },
    f_param_name: { de: "Bezeichnung", en: "Name", pl: "Nazwa" },
    f_value: { de: "Messwert", en: "Result", pl: "Wynik" },
    f_unit: { de: "Einheit", en: "Unit", pl: "Jednostka" },
    f_low: { de: "Ref. von", en: "Ref. from", pl: "Norma od" },
    f_high: { de: "Ref. bis", en: "Ref. to", pl: "Norma do" },
    f_ref_hint: { de: "Vorbelegt mit typischen Werten — bitte den Bereich vom eigenen Laborbefund übernehmen.", en: "Pre-filled with typical values — please copy the range from your own lab report.", pl: "Wstępnie wpisane typowe wartości — proszę przepisać zakres z własnego wyniku." },
    f_assess: { de: "Eigene Einschätzung / Notiz", en: "Own assessment / note", pl: "Własna ocena / notatka" },
    f_finding_body: { de: "Befund & eigene Einschätzung", en: "Finding & own assessment", pl: "Opis i własna ocena" },
    k_value: { de: "Wert", en: "Value", pl: "Wynik" },
    k_finding: { de: "Befund", en: "Finding", pl: "Opis" },
    k_glossary: { de: "Begriff", en: "Term", pl: "Pojęcie" },
    k_med: { de: "Medikament", en: "Medicine", pl: "Lek" },
    k_research: { de: "Recherche", en: "Research", pl: "Notatka" },
    high: { de: "↑ hoch", en: "↑ high", pl: "↑ wysoki" },
    low: { de: "↓ niedrig", en: "↓ low", pl: "↓ niski" },
    inrange: { de: "im Bereich", en: "in range", pl: "w normie" },
    noref: { de: "ohne Ref.", en: "no ref.", pl: "bez normy" },
    ref: { de: "Ref.", en: "Ref.", pl: "Norma" },
    history: { de: "Verlauf anzeigen", en: "Show history", pl: "Pokaż przebieg" },
    measurements: { de: "Messungen", en: "measurements", pl: "pomiarów" },
    err_load: { de: "Daten konnten nicht geladen werden. Seite neu laden.", en: "Could not load data. Reload the page.", pl: "Nie udało się wczytać danych. Odśwież stronę." },
    err_save: { de: "Speichern fehlgeschlagen — bitte erneut versuchen.", en: "Saving failed — please try again.", pl: "Zapis nie powiódł się — spróbuj ponownie." },
    err_need: { de: "Bitte mindestens das erste Feld ausfüllen.", en: "Please fill in at least the first field.", pl: "Wypełnij przynajmniej pierwsze pole." },
    err_num: { de: "Messwert bitte als Zahl eingeben (Komma oder Punkt).", en: "Please enter the result as a number.", pl: "Wpisz wynik jako liczbę (przecinek lub kropka)." },
    open_source: { de: "Quelle öffnen", en: "Open source", pl: "Otwórz źródło" },
    upload_finding: { de: "↑ Befund hochladen", en: "↑ Upload report", pl: "↑ Wgraj wynik" },
    f_files: { de: "Dateien (PDF oder Foto, je bis 30 MB)", en: "Files (PDF or photo, up to 30 MB each)", pl: "Pliki (PDF lub zdjęcie, do 30 MB każdy)" },
    f_files_hint: { de: "Mehrere auf einmal möglich. Am Handy geht auch direkt die Kamera.", en: "Several at once are fine. On a phone you can use the camera directly.", pl: "Można kilka naraz. Na telefonie można od razu użyć aparatu." },
    files_attached: { de: "Angehängt", en: "Attached", pl: "Załączone" },
    files_new: { de: "Wird hochgeladen", en: "Will be uploaded", pl: "Zostanie wgrane" },
    remove: { de: "Entfernen", en: "Remove", pl: "Usuń" },
    uploading: { de: "Lade Datei hoch …", en: "Uploading file …", pl: "Wgrywam plik …" },
    upload_fail: { de: "Hochladen fehlgeschlagen", en: "Upload failed", pl: "Wgrywanie nie powiodło się" },
    bad_type: { de: "nur PDF oder Bilder (JPG, PNG, HEIC, WEBP) — übersprungen", en: "only PDF or images (JPG, PNG, HEIC, WEBP) — skipped", pl: "tylko PDF lub obrazy (JPG, PNG, HEIC, WEBP) — pominięto" },
    too_big: { de: "größer als 30 MB — übersprungen", en: "larger than 30 MB — skipped", pl: "większy niż 30 MB — pominięto" },
    drop_here: { de: "Dateien loslassen, um sie anzuhängen", en: "Drop files to attach them", pl: "Upuść pliki, aby je dołączyć" },
    file_removed: { de: "Datei entfernt", en: "File removed", pl: "Plik usunięty" },
    tab_settings: { de: "Einstellungen", en: "Settings", pl: "Ustawienia" },
    k_analysis: { de: "KI-Analyse", en: "AI analysis", pl: "Analiza AI" },
    ai_need_key: { de: "KI-Funktionen brauchen einen OpenAI-Schlüssel.", en: "AI features need an OpenAI key.", pl: "Funkcje AI wymagają klucza OpenAI." },
    ai_to_settings: { de: "Zu den Einstellungen", en: "Open settings", pl: "Przejdź do ustawień" },
    ai_busy: { de: "KI arbeitet … das kann 1–3 Minuten dauern.", en: "AI is working … this can take 1–3 minutes.", pl: "AI pracuje … to może potrwać 1–3 minuty." },
    ai_hint_disclaimer: { de: "KI-Einschätzung — kann Fehler enthalten und ersetzt keine ärztliche Diagnose. Immer mit dem Behandlungsteam besprechen.", en: "AI assessment — may contain errors and is not a medical diagnosis. Always discuss with the care team.", pl: "Ocena AI — może zawierać błędy i nie jest diagnozą lekarską. Zawsze omawiaj z zespołem leczącym." },
    ai_hints: { de: "KI-Hinweise", en: "AI notes", pl: "Wskazówki AI" },
    ai_hints_sub: { de: "Liest das ganze Notizbuch: Stand, nächste Schritte, Lücken, Fragen fürs Arztgespräch, Warnzeichen.", en: "Reads the whole notebook: status, next steps, gaps, questions for the doctor, warning signs.", pl: "Czyta cały notatnik: sytuacja, kolejne kroki, braki, pytania do lekarza, objawy alarmowe." },
    ai_hints_btn: { de: "Hinweise erstellen", en: "Create notes", pl: "Utwórz wskazówki" },
    ai_hints_empty: { de: "Noch keine Hinweise erstellt.", en: "No notes created yet.", pl: "Brak wskazówek." },
    ai_values_btn: { de: "KI-Analyse der Werte", en: "AI analysis of values", pl: "Analiza AI wyników" },
    ai_analyses: { de: "KI-Analysen der Werte", en: "AI analyses of values", pl: "Analizy AI wyników" },
    ai_classify: { de: "KI-Einordnung", en: "AI assessment", pl: "Ocena AI" },
    ai_reclassify: { de: "Neu einordnen", en: "Re-assess", pl: "Oceń ponownie" },
    ai_show_full: { de: "Ganze Einordnung lesen", en: "Read full assessment", pl: "Czytaj całą ocenę" },
    ai_explain_ph: { de: "Begriff, z. B. aus einem Befund oder Artikel", en: "Term, e.g. from a report or article", pl: "Pojęcie, np. z wyniku lub artykułu" },
    ai_explain_btn: { de: "Von der KI erklären lassen", en: "Explain with AI", pl: "Wyjaśnij z AI" },
    ai_med_ph: { de: "Medikament oder Präparat — Wirkstoff oder Handelsname", en: "Medicine or supplement — active ingredient or brand name", pl: "Lek lub preparat — substancja czynna lub nazwa handlowa" },
    ai_med_btn: { de: "Von der KI nachschlagen lassen", en: "Look up with AI", pl: "Sprawdź z AI" },
    ai_ask_ph: { de: "Frage stellen — z. B. „Was sagt die aktuelle Forschung zu …?“", en: "Ask a question — e.g. “What does current research say about …?”", pl: "Zadaj pytanie — np. „Co mówią aktualne badania o …?”" },
    ai_ask_btn: { de: "Recherchieren", en: "Research", pl: "Wyszukaj" },
    ai_use_web: { de: "im Web suchen", en: "search the web", pl: "szukaj w internecie" },
    ai_use_mappe: { de: "mein Notizbuch einbeziehen", en: "include my notebook", pl: "uwzględnij mój notatnik" },
    ai_draft: { de: "Vorschlag der KI — prüfen und speichern", en: "AI draft — review and save", pl: "Propozycja AI — sprawdź i zapisz" },
    ai_save: { de: "Ins Notizbuch übernehmen", en: "Add to notebook", pl: "Dodaj do notatnika" },
    ai_discard: { de: "Verwerfen", en: "Discard", pl: "Odrzuć" },
    sources: { de: "Quellen", en: "Sources", pl: "Źródła" },
    s_openai: { de: "OpenAI-Schlüssel", en: "OpenAI key", pl: "Klucz OpenAI" },
    s_openai_sub: { de: "Damit laufen Recherche, Begriffserklärungen, Medikamenten-Steckbriefe, Befund- und Werte-Analysen, Hinweise und die Übersetzung.", en: "Powers research, term explanations, medicine profiles, finding and value analyses, notes and translation.", pl: "Służy do wyszukiwania, wyjaśniania pojęć, opisów leków, analizy wyników i opisów, wskazówek oraz tłumaczenia." },
    s_status_set: { de: "Hinterlegt", en: "Stored", pl: "Zapisany" },
    s_status_none: { de: "Kein Schlüssel hinterlegt", en: "No key stored", pl: "Brak klucza" },
    s_new_key: { de: "Neuen Schlüssel eintragen", en: "Enter new key", pl: "Wpisz nowy klucz" },
    s_save_key: { de: "Schlüssel speichern", en: "Save key", pl: "Zapisz klucz" },
    s_test: { de: "Schlüssel prüfen", en: "Test key", pl: "Sprawdź klucz" },
    s_test_ok: { de: "Schlüssel funktioniert", en: "Key works", pl: "Klucz działa" },
    s_remove: { de: "Schlüssel entfernen", en: "Remove key", pl: "Usuń klucz" },
    s_remove_q: { de: "Schlüssel wirklich entfernen? KI-Funktionen sind danach aus.", en: "Really remove the key? AI features will stop.", pl: "Na pewno usunąć klucz? Funkcje AI przestaną działać." },
    s_models: { de: "Modelle", en: "Models", pl: "Modele" },
    s_model: { de: "Für Analysen, Recherche und Erklärungen", en: "For analyses, research and explanations", pl: "Do analiz, wyszukiwania i wyjaśnień" },
    s_model_fast: { de: "Für Übersetzungen (schnell & günstig)", en: "For translations (fast & cheap)", pl: "Do tłumaczeń (szybko i tanio)" },
    s_web: { de: "Websuche erlauben (aktuellere Quellen, etwas teurer)", en: "Allow web search (more current sources, slightly more expensive)", pl: "Zezwól na wyszukiwanie w sieci (aktualniejsze źródła, nieco drożej)" },
    s_save: { de: "Einstellungen speichern", en: "Save settings", pl: "Zapisz ustawienia" },
    s_models_hint: { de: "„Schlüssel prüfen“ lädt die Liste der Modelle, die dein Schlüssel nutzen darf.", en: "“Test key” loads the models your key can use.", pl: "„Sprawdź klucz” wczyta listę modeli dostępnych dla klucza." },
    s_about: { de: "Gut zu wissen", en: "Good to know", pl: "Warto wiedzieć" },
    s_about_text: {
      de: "Der Schlüssel liegt nur auf dem Server dieses Notizbuchs und wird nie wieder vollständig angezeigt. Jede KI-Anfrage wird von OpenAI nach Verbrauch abgerechnet — eine Befund-Analyse mit PDF kostet meist wenige Cent. Für Analysen werden die Inhalte des Notizbuchs (Werte, Befunde, Anhänge) an OpenAI übermittelt. Ohne Schlüssel übersetzt die Mappe weiterhin über Claude.",
      en: "The key is stored only on this notebook’s server and is never shown in full again. Each AI request is billed by OpenAI by usage — a report analysis with a PDF usually costs a few cents. For analyses, the notebook’s content (values, findings, attachments) is sent to OpenAI. Without a key, translation still runs via Claude.",
      pl: "Klucz jest przechowywany tylko na serwerze tego notatnika i nigdy więcej nie jest pokazywany w całości. Każde zapytanie AI OpenAI rozlicza według zużycia — analiza opisu z PDF kosztuje zwykle kilka centów. Do analiz treść notatnika (wyniki, opisy, załączniki) jest przesyłana do OpenAI. Bez klucza tłumaczenie nadal działa przez Claude."
    },
    s_saved: { de: "Einstellungen gespeichert", en: "Settings saved", pl: "Zapisano ustawienia" },
    tab_videos: { de: "Videos & Links", en: "Videos & links", pl: "Filmy i linki" },
    k_video: { de: "Video/Link", en: "Video/link", pl: "Film/link" },
    new_video: { de: "+ Video oder Link", en: "+ Video or link", pl: "+ Film lub link" },
    videos_sub: { de: "YouTube-Videos und eigene Links, nach Thema geordnet. Klick aufs Bild spielt das Video direkt hier ab.", en: "YouTube videos and your own links, sorted by topic. Click the picture to play the video right here.", pl: "Filmy z YouTube i własne linki, uporządkowane tematycznie. Kliknij obraz, aby odtworzyć film tutaj." },
    f_year: { de: "Jahr", en: "Year", pl: "Rok" },
    f_url: { de: "Adresse (YouTube-Link oder beliebige Webseite)", en: "Address (YouTube link or any web page)", pl: "Adres (link YouTube lub dowolna strona)" },
    f_load_preview: { de: "Vorschau laden", en: "Load preview", pl: "Wczytaj podgląd" },
    f_loading_preview: { de: "Lade Titel und Vorschaubild …", en: "Loading title and thumbnail …", pl: "Wczytuję tytuł i miniaturę …" },
    f_channel: { de: "Kanal / Seite", en: "Channel / site", pl: "Kanał / strona" },
    f_category: { de: "Thema", en: "Topic", pl: "Temat" },
    f_vlang: { de: "Sprache des Videos", en: "Video language", pl: "Język filmu" },
    f_vnote: { de: "Eigene Notiz (worum geht es, was war hilfreich)", en: "Own note (what it covers, what was helpful)", pl: "Własna notatka (o czym jest, co było pomocne)" },
    no_preview: { de: "Kein Vorschaubild gefunden — die Kachel bekommt ein Ersatzbild.", en: "No thumbnail found — the tile gets a placeholder.", pl: "Nie znaleziono miniatury — kafelek dostanie obraz zastępczy." },
    err_url: { de: "Bitte zuerst eine Adresse eintragen.", en: "Please enter an address first.", pl: "Najpierw wpisz adres." },
    all_langs: { de: "Alle Sprachen", en: "All languages", pl: "Wszystkie języki" },
    play: { de: "Abspielen", en: "Play", pl: "Odtwórz" },
    open_yt: { de: "Auf YouTube öffnen ↗", en: "Open on YouTube ↗", pl: "Otwórz w YouTube ↗" },
    open_link: { de: "Link öffnen ↗", en: "Open link ↗", pl: "Otwórz link ↗" },
    close: { de: "Schließen", en: "Close", pl: "Zamknij" },
    empty_videos: { de: "Noch keine Videos. Füge den ersten YouTube-Link ein — Titel und Vorschaubild holt das Notizbuch selbst.", en: "No videos yet. Paste your first YouTube link — the notebook fetches title and thumbnail itself.", pl: "Brak filmów. Wklej pierwszy link YouTube — notatnik sam pobierze tytuł i miniaturę." },
    v_process: { de: "Transkribieren & zusammenfassen", en: "Transcribe & summarise", pl: "Transkrybuj i streść" },
    v_summarize: { de: "Zusammenfassen", en: "Summarise", pl: "Streść" },
    v_resummarize: { de: "Neu zusammenfassen", en: "Summarise again", pl: "Streść ponownie" },
    v_summary: { de: "Zusammenfassung", en: "Summary", pl: "Streszczenie" },
    v_transcript: { de: "Transkript", en: "Transcript", pl: "Transkrypcja" },
    v_tr_manual: { de: "von Hand eingefügt", en: "pasted manually", pl: "wklejone ręcznie" },
    v_all: { de: "Alle offenen verarbeiten", en: "Process all pending", pl: "Przetwórz wszystkie oczekujące" },
    v_tr_field: { de: "Transkript (optional) — falls kein automatisches möglich ist: auf YouTube „Transkript anzeigen“, kopieren, hier einfügen", en: "Transcript (optional) — if automatic fails: on YouTube “Show transcript”, copy and paste here", pl: "Transkrypcja (opcjonalnie) — jeśli automatyczna nie działa: w YouTube „Pokaż transkrypcję”, skopiuj i wklej tutaj" },
    v_jump: { de: "Klick auf eine Zeitmarke springt im Video dorthin.", en: "Click a timestamp to jump there in the video.", pl: "Kliknij znacznik czasu, aby przejść do tego miejsca w filmie." },
    s_trans: { de: "TranscriptAPI-Schlüssel", en: "TranscriptAPI key", pl: "Klucz TranscriptAPI" },
    s_trans_sub: { de: "YouTube sperrt Transkript-Abrufe direkt vom Server. TranscriptAPI.com holt sie stellvertretend — 1 Guthabenpunkt pro Video. Schlüssel unter transcriptapi.com → Dashboard → API Keys.", en: "YouTube blocks transcript requests from servers. TranscriptAPI.com fetches them on our behalf — 1 credit per video. Get a key at transcriptapi.com → Dashboard → API Keys.", pl: "YouTube blokuje pobieranie transkrypcji z serwera. TranscriptAPI.com pobiera je w naszym imieniu — 1 kredyt za film. Klucz: transcriptapi.com → Dashboard → API Keys." },
    s_trans_new: { de: "TranscriptAPI-Schlüssel eintragen", en: "Enter TranscriptAPI key", pl: "Wpisz klucz TranscriptAPI" },
    s_summary_via: { de: "Zusammenfassungen laufen über OpenAI, ohne OpenAI-Schlüssel über Claude.", en: "Summaries use OpenAI, or Claude when no OpenAI key is set.", pl: "Streszczenia korzystają z OpenAI, a bez klucza OpenAI z Claude." },
    tab_chat: { de: "Chat", en: "Chat", pl: "Czat" },
    c_new: { de: "+ Neues Gespräch", en: "+ New conversation", pl: "+ Nowa rozmowa" },
    c_untitled: { de: "Neues Gespräch", en: "New conversation", pl: "Nowa rozmowa" },
    c_ph: { de: "Frag etwas zur Erkrankung, zu Werten, Befunden, Medikamenten …", en: "Ask about the illness, values, findings, medicines …", pl: "Zapytaj o chorobę, wyniki, opisy, leki …" },
    c_send: { de: "Senden", en: "Send", pl: "Wyślij" },
    c_stop: { de: "Stopp", en: "Stop", pl: "Stop" },
    c_mappe: { de: "Notizbuch einbeziehen", en: "Use my notebook", pl: "Uwzględnij notatnik" },
    c_web: { de: "Websuche", en: "Web search", pl: "Wyszukiwanie w sieci" },
    c_thinking: { de: "denkt nach …", en: "thinking …", pl: "myśli …" },
    c_searching: { de: "sucht im Web …", en: "searching the web …", pl: "szuka w sieci …" },
    c_you: { de: "Du", en: "You", pl: "Ty" },
    c_save: { de: "Als Recherche-Notiz speichern", en: "Save as research note", pl: "Zapisz jako notatkę" },
    c_saved: { de: "In der Recherche gespeichert", en: "Saved to research", pl: "Zapisano w notatkach" },
    c_copy: { de: "Kopieren", en: "Copy", pl: "Kopiuj" },
    c_copied: { de: "Kopiert", en: "Copied", pl: "Skopiowano" },
    c_partial: { de: "Antwort wurde abgebrochen.", en: "Answer was interrupted.", pl: "Odpowiedź została przerwana." },
    c_del_q: { de: "Gespräch löschen?", en: "Delete conversation?", pl: "Usunąć rozmowę?" },
    c_hello: { de: "Worüber möchtest du sprechen?", en: "What would you like to talk about?", pl: "O czym chcesz porozmawiać?" },
    c_hello_sub: { de: "Der Chat kennt auf Wunsch den Inhalt des Notizbuchs — Werte, Befunde, Medikamenten-Notizen und Videos — und kann im Web nach aktuellen Quellen suchen.", en: "If you like, the chat knows what is in the notebook — values, findings, medicine notes and videos — and can search the web for current sources.", pl: "Na życzenie czat zna zawartość notatnika — wyniki, opisy, notatki o lekach i filmy — i może szukać aktualnych źródeł w sieci." },
    c_s1: { de: "Was bedeuten meine letzten Blutwerte?", en: "What do my latest blood values mean?", pl: "Co oznaczają moje ostatnie wyniki krwi?" },
    c_s2: { de: "Erkläre mir meinen Befund in einfachen Worten.", en: "Explain my report in simple words.", pl: "Wyjaśnij mi mój wynik prostymi słowami." },
    c_s3: { de: "Welche Fragen sollte ich beim nächsten Arzttermin stellen?", en: "Which questions should I ask at my next appointment?", pl: "Jakie pytania zadać na następnej wizycie?" },
    c_s4: { de: "Was kann ich im Alltag selbst tun?", en: "What can I do myself in everyday life?", pl: "Co mogę sama/sam zrobić na co dzień?" },
    c_s5: { de: "Welche Videos aus dem Notizbuch passen zu meiner Situation?", en: "Which videos in the notebook fit my situation?", pl: "Które filmy z notatnika pasują do mojej sytuacji?" },
    c_net: { de: "Senden hat nicht geklappt — keine Verbindung zum Server. Bitte die Seite neu laden und erneut senden.", en: "Sending failed — no connection to the server. Please reload the page and send again.", pl: "Wysyłanie nie powiodło się — brak połączenia z serwerem. Odśwież stronę i wyślij ponownie." },
    c_list: { de: "Gespräche", en: "Conversations", pl: "Rozmowy" },
    more: { de: "Weiterlesen", en: "Read more", pl: "Czytaj dalej" },
    less: { de: "Weniger anzeigen", en: "Show less", pl: "Pokaż mniej" },
    expand_all: { de: "Alle aufklappen", en: "Expand all", pl: "Rozwiń wszystkie" },
    collapse_all: { de: "Alle zuklappen", en: "Collapse all", pl: "Zwiń wszystkie" },
    m_title: { de: "Zugang für KI-Agenten (MCP)", en: "Access for AI agents (MCP)", pl: "Dostęp dla agentów AI (MCP)" },
    m_sub: { de: "Über diese Adressen können KI-Agenten (Claude, ChatGPT, eigene Automationen) das Notebook per MCP lesen bzw. bearbeiten. Die Adresse ist der Schlüssel — wie ein Passwort behandeln.", en: "AI agents (Claude, ChatGPT, your own automations) can read or edit the notebook via MCP using these addresses. The address is the key — treat it like a password.", pl: "Przez te adresy agenci AI (Claude, ChatGPT, własne automatyzacje) mogą czytać lub edytować notatnik przez MCP. Adres jest kluczem — traktuj go jak hasło." },
    m_read: { de: "Nur lesen", en: "Read only", pl: "Tylko odczyt" },
    m_write: { de: "Lesen und schreiben", en: "Read and write", pl: "Odczyt i zapis" },
    m_show: { de: "Anzeigen", en: "Show", pl: "Pokaż" },
    m_hide: { de: "Verbergen", en: "Hide", pl: "Ukryj" },
    m_rotate: { de: "Neu erzeugen", en: "Regenerate", pl: "Wygeneruj nowy" },
    m_rotate_q: { de: "Neue Adresse erzeugen? Agenten mit der alten verlieren sofort den Zugang.", en: "Generate a new address? Agents using the old one lose access immediately.", pl: "Wygenerować nowy adres? Agenci ze starym natychmiast stracą dostęp." },
    m_rotated: { de: "Neue Adresse erzeugt — alte gilt nicht mehr", en: "New address generated — the old one no longer works", pl: "Nowy adres wygenerowany — stary już nie działa" },
    m_tools: { de: "Werkzeuge: Überblick, Suchen, Einträge und Dateien lesen, Werte-Verlauf, Chats — mit Schreibrecht zusätzlich Anlegen, Ändern, Löschen (nur mit Bestätigung), Dateien anhängen und KI-Einordnung starten. Texte werden automatisch in alle drei Sprachen übersetzt.", en: "Tools: overview, search, read entries and files, value history, chats — with write access also create, edit, delete (confirmation required), attach files and start AI assessment. Texts are translated into all three languages automatically.", pl: "Narzędzia: przegląd, wyszukiwanie, odczyt wpisów i plików, przebieg wyników, czaty — z prawem zapisu także dodawanie, edycja, usuwanie (z potwierdzeniem), dołączanie plików i ocena AI. Teksty są automatycznie tłumaczone na trzy języki." },
    topics: { de: "Themen", en: "Topics", pl: "Tematy" },
    t_search: { de: "Themen durchsuchen …", en: "Search topics …", pl: "Szukaj tematów …" },
    t_none: { de: "Kein Thema gefunden.", en: "No topic found.", pl: "Nie znaleziono tematu." },
    recent_empty: { de: "Noch nichts eingetragen. Oben rechts geht es los: „+ Neuer Eintrag“.", en: "Nothing here yet. Start top right: “+ New entry”.", pl: "Jeszcze nic. Zacznij w prawym górnym rogu: „+ Nowy wpis”." },
    t_entries: { de: "Einträge", en: "entries", pl: "wpisów" },
    t_new: { de: "+ Thema", en: "+ Topic", pl: "+ Temat" },
    t_edit: { de: "Thema bearbeiten", en: "Edit topic", pl: "Edytuj temat" },
    t_new_title: { de: "Neues Thema", en: "New topic", pl: "Nowy temat" },
    t_name: { de: "Name des Themas", en: "Topic name", pl: "Nazwa tematu" },
    t_desc: { de: "Kurzbeschreibung", en: "Short description", pl: "Krótki opis" },
    t_kind: { de: "Art", en: "Type", pl: "Rodzaj" },
    t_kind_health: { de: "Gesundheit — mit Laborwerten, Befunden, Medikamenten und medizinischen Hinweisen", en: "Health — with lab values, findings, medicines and medical guidance", pl: "Zdrowie — z wynikami badań, opisami, lekami i wskazówkami medycznymi" },
    t_kind_general: { de: "Allgemein — Recherche zu jedem anderen Thema (Technik, Recht, Reisen …)", en: "General — research on any other topic (tech, law, travel …)", pl: "Ogólny — research na każdy inny temat (technika, prawo, podróże …)" },
    t_sections: { de: "Unterbereiche", en: "Sections", pl: "Sekcje" },
    t_context: { de: "Worum genau geht es? (hilft der KI, optional)", en: "What exactly is it about? (helps the AI, optional)", pl: "O co dokładnie chodzi? (pomaga AI, opcjonalnie)" },
    t_context_ph: { de: "z. B. „Balkonkraftwerk mit Speicher, 800 W, Mietwohnung“", en: "e.g. “balcony solar with battery, 800 W, rented flat”", pl: "np. „mini elektrownia balkonowa z magazynem, 800 W, mieszkanie”" },
    t_delete: { de: "Thema löschen", en: "Delete topic", pl: "Usuń temat" },
    t_delete_q: { de: "Thema wirklich löschen? Geht nur, wenn es leer ist.", en: "Really delete the topic? Only possible when it is empty.", pl: "Na pewno usunąć temat? Możliwe tylko, gdy jest pusty." },
    t_saved: { de: "Thema gespeichert", en: "Topic saved", pl: "Zapisano temat" },
    t_deleted: { de: "Thema gelöscht", en: "Topic deleted", pl: "Usunięto temat" },
    t_need_section: { de: "Bitte mindestens einen Unterbereich wählen.", en: "Please choose at least one section.", pl: "Wybierz co najmniej jedną sekcję." },
    tab_values_g: { de: "Werte & Dokumente", en: "Values & documents", pl: "Wartości i dokumenty" },
    labs_g: { de: "Messwerte", en: "Measurements", pl: "Pomiary" },
    labs_sub_g: { de: "Je Wert der Verlauf; grün hinterlegt der Sollbereich, falls angegeben.", en: "History per value; the green band is the target range, if given.", pl: "Przebieg dla każdej wartości; zielony pas to zakres docelowy, jeśli podany." },
    findings_g: { de: "Dokumente & Einschätzungen", en: "Documents & assessments", pl: "Dokumenty i oceny" },
    findings_sub_g: { de: "Angebote, Verträge, Datenblätter, Briefe — und was man selbst daraus liest.", en: "Offers, contracts, data sheets, letters — and what you make of them.", pl: "Oferty, umowy, karty katalogowe, pisma — i własna interpretacja." },
    new_finding_g: { de: "+ Dokument / Einschätzung", en: "+ Document / assessment", pl: "+ Dokument / ocena" },
    upload_finding_g: { de: "↑ Dokument hochladen", en: "↑ Upload document", pl: "↑ Wgraj dokument" },
    empty_values_g: { de: "Noch keine Messwerte. Trag den ersten Wert ein — Name, Zahl, Einheit, optional ein Sollbereich.", en: "No measurements yet. Add the first value — name, number, unit, optionally a target range.", pl: "Brak pomiarów. Dodaj pierwszą wartość — nazwa, liczba, jednostka, opcjonalnie zakres docelowy." },
    empty_findings_g: { de: "Noch keine Dokumente. Lade ein PDF oder Foto hoch und notiere deine Einschätzung dazu.", en: "No documents yet. Upload a PDF or photo and note your assessment.", pl: "Brak dokumentów. Wgraj PDF lub zdjęcie i zapisz swoją ocenę." },
    k_finding_g: { de: "Dokument", en: "Document", pl: "Dokument" },
    f_finding_body_g: { de: "Inhalt & eigene Einschätzung", en: "Content & own assessment", pl: "Treść i własna ocena" },
    f_ref_hint_g: { de: "Sollbereich optional — leer lassen, wenn es keinen gibt.", en: "Target range optional — leave empty if there is none.", pl: "Zakres docelowy opcjonalny — zostaw puste, jeśli go nie ma." },
    home_intro_g: { de: "Alles zu diesem Thema an einem Ort: Recherche-Notizen, Begriffe, Videos, Dokumente und Chat — in Deutsch, Englisch und Polnisch.", en: "Everything on this topic in one place: research notes, terms, videos, documents and chat — in German, English and Polish.", pl: "Wszystko na ten temat w jednym miejscu: notatki, pojęcia, filmy, dokumenty i czat — po niemiecku, angielsku i polsku." },
    disclaimer_g: { de: "Persönliche Sammlung. KI-Inhalte können Fehler enthalten — wichtige Punkte mit Fachleuten prüfen.", en: "Personal collection. AI content may contain errors — check important points with experts.", pl: "Osobisty zbiór. Treści AI mogą zawierać błędy — ważne kwestie sprawdź u specjalistów." },
    ai_hints_sub_g: { de: "Liest das ganze Thema: Stand, nächste Schritte, Lücken, offene Fragen, Tipps.", en: "Reads the whole topic: status, next steps, gaps, open questions, tips.", pl: "Czyta cały temat: sytuacja, kolejne kroki, braki, otwarte pytania, wskazówki." },
    ai_hint_disclaimer_g: { de: "KI-Einschätzung — kann Fehler enthalten. Wichtige Punkte mit Fachleuten prüfen.", en: "AI assessment — may contain errors. Check important points with experts.", pl: "Ocena AI — może zawierać błędy. Ważne kwestie sprawdź u specjalistów." },
    ai_values_btn_g: { de: "KI-Analyse der Messwerte", en: "AI analysis of measurements", pl: "Analiza AI pomiarów" },
    c_s1_g: { de: "Fass mir den aktuellen Stand dieses Themas zusammen.", en: "Summarise where this topic stands.", pl: "Podsumuj aktualny stan tego tematu." },
    c_s2_g: { de: "Was sollte ich als Nächstes recherchieren?", en: "What should I research next?", pl: "Co powinienem zbadać w następnej kolejności?" },
    c_s3_g: { de: "Welche Fragen sind noch offen?", en: "Which questions are still open?", pl: "Jakie pytania są jeszcze otwarte?" },
    c_s4_g: { de: "Erkläre mir die wichtigsten Begriffe einfach.", en: "Explain the key terms simply.", pl: "Wyjaśnij prosto najważniejsze pojęcia." },
    c_s5_g: { de: "Welche Videos aus dem Notizbuch passen dazu?", en: "Which videos in the notebook fit?", pl: "Które filmy z notatnika pasują?" },
    tab_studies: { de: "Studien", en: "Studies", pl: "Badania" },
    k_study: { de: "Studie", en: "Study", pl: "Badanie" },
    new_study: { de: "+ Studie von Hand", en: "+ Study manually", pl: "+ Badanie ręcznie" },
    st_sub: { de: "Veröffentlichte Studien aus PubMed und laufende klinische Studien aus ClinicalTrials.gov — suchen, übernehmen, von der KI einordnen lassen.", en: "Published studies from PubMed and ongoing clinical trials from ClinicalTrials.gov — search, save, let the AI assess them.", pl: "Opublikowane badania z PubMed i trwające badania kliniczne z ClinicalTrials.gov — szukaj, zapisuj, oceniaj z AI." },
    st_search_ph: { de: "Suchbegriffe, am besten auf Englisch", en: "Search terms, ideally in English", pl: "Wyszukiwane hasła, najlepiej po angielsku" },
    st_src_pubmed: { de: "Veröffentlichte Studien · PubMed", en: "Published studies · PubMed", pl: "Opublikowane badania · PubMed" },
    st_src_trials: { de: "Laufende Studien · ClinicalTrials.gov", en: "Ongoing trials · ClinicalTrials.gov", pl: "Trwające badania · ClinicalTrials.gov" },
    st_search: { de: "Suchen", en: "Search", pl: "Szukaj" },
    st_recent: { de: "nur letzte 5 Jahre", en: "last 5 years only", pl: "tylko ostatnie 5 lat" },
    st_open: { de: "nur offen für neue Teilnehmende", en: "only open for enrolment", pl: "tylko otwarte na rekrutację" },
    st_land: { de: "Studienort", en: "Study site", pl: "Ośrodek" },
    st_land_all: { de: "alle Länder", en: "all countries", pl: "wszystkie kraje" },
    st_hits: { de: "Treffer", en: "results", pl: "wyników" },
    st_take: { de: "Übernehmen", en: "Save", pl: "Zapisz" },
    st_taken: { de: "✓ im Notizbuch", en: "✓ in notebook", pl: "✓ w notatniku" },
    st_import_ph: { de: "Direkt übernehmen: PubMed-ID, NCT-Nummer, DOI oder Link", en: "Save directly: PubMed ID, NCT number, DOI or link", pl: "Zapisz bezpośrednio: PubMed ID, numer NCT, DOI lub link" },
    st_import: { de: "Übernehmen", en: "Save", pl: "Zapisz" },
    st_saved_trials: { de: "Laufende Studien", en: "Ongoing trials", pl: "Trwające badania" },
    st_saved_pub: { de: "Veröffentlichte Studien", en: "Published studies", pl: "Opublikowane badania" },
    st_saved_other: { de: "Weitere Studien", en: "Other studies", pl: "Inne badania" },
    st_empty: { de: "Noch keine Studien gespeichert. Suche oben oder füge eine PubMed-ID, NCT-Nummer oder DOI ein.", en: "No studies saved yet. Search above or paste a PubMed ID, NCT number or DOI.", pl: "Brak zapisanych badań. Szukaj powyżej lub wklej PubMed ID, numer NCT albo DOI." },
    st_assess: { de: "Einordnen", en: "Assess", pl: "Oceń" },
    st_reassess: { de: "Neu einordnen", en: "Re-assess", pl: "Oceń ponownie" },
    st_assessment: { de: "Einordnung", en: "Assessment", pl: "Ocena" },
    st_abstract: { de: "Abstract", en: "Abstract", pl: "Streszczenie" },
    st_summary_reg: { de: "Kurzbeschreibung (Register)", en: "Brief summary (registry)", pl: "Opis (rejestr)" },
    st_criteria: { de: "Ein- und Ausschlusskriterien", en: "Eligibility criteria", pl: "Kryteria włączenia i wyłączenia" },
    st_sites: { de: "Studienorte DE · PL · AT · CH", en: "Sites DE · PL · AT · CH", pl: "Ośrodki DE · PL · AT · CH" },
    st_no_sites: { de: "Keine Studienorte in Deutschland, Polen, Österreich oder der Schweiz.", en: "No sites in Germany, Poland, Austria or Switzerland.", pl: "Brak ośrodków w Niemczech, Polsce, Austrii czy Szwajcarii." },
    st_participants: { de: "Teilnehmende", en: "participants", pl: "uczestników" },
    st_evidence: { de: "Belastbarkeit", en: "Strength of evidence", pl: "Siła dowodów" },
    f_study_url: { de: "Link (PubMed, DOI, Studienregister …)", en: "Link (PubMed, DOI, registry …)", pl: "Link (PubMed, DOI, rejestr …)" },
    f_study_note: { de: "Worum geht es / eigene Notiz", en: "What it is about / own note", pl: "O czym jest / własna notatka" },
    s_open: { de: "Einstellungen", en: "Settings", pl: "Ustawienia" },
    x_btn: { de: "Erklären", en: "Explain", pl: "Wyjaśnij" },
    x_loading: { de: "KI erklärt den Begriff …", en: "AI is explaining the term …", pl: "AI wyjaśnia pojęcie …" },
    x_save: { de: "In Begriffe speichern", en: "Save to glossary", pl: "Zapisz w słowniczku" },
    x_saved: { de: "In Begriffe gespeichert", en: "Saved to glossary", pl: "Zapisano w słowniczku" },
    x_open: { de: "In Begriffe öffnen", en: "Open in glossary", pl: "Otwórz w słowniczku" },
    x_exists: { de: "Schon in Begriffe", en: "Already in glossary", pl: "Już w słowniczku" },
    x_bad: { de: "Die Erklärung kam unvollständig an. Bitte noch einmal markieren.", en: "The explanation arrived incomplete. Please select it again.", pl: "Wyjaśnienie dotarło niekompletne. Zaznacz ponownie." },
    x_timeout: { de: "Keine Antwort nach 2 Minuten. Bitte später noch einmal versuchen.", en: "No answer after 2 minutes. Please try again later.", pl: "Brak odpowiedzi po 2 minutach. Spróbuj później." },
    x_hint: { de: "Tipp: Markiere an jeder Stelle ein Wort, um es erklären zu lassen.", en: "Tip: select a word anywhere to have it explained.", pl: "Wskazówka: zaznacz słowo w dowolnym miejscu, aby je wyjaśnić." },
    edit_lang: { de: "Du bearbeitest die deutsche Fassung.", en: "You are editing the English version.", pl: "Edytujesz wersję polską." }
  };

  // Typische Referenzbereiche Erwachsene (Frauen). Labore weichen ab — deshalb pro Messung überschreibbar.
  var PARAMS = [
    { key: "leuko", unit: "/nl", low: 4.0, high: 10.0, n: { de: "Leukozyten", en: "White blood cells (WBC)", pl: "Leukocyty (WBC)" } },
    { key: "neutro", unit: "/nl", low: 1.8, high: 7.5, n: { de: "Neutrophile (absolut)", en: "Neutrophils (absolute)", pl: "Neutrofile (bezwzględnie)" } },
    { key: "hb", unit: "g/dl", low: 12.0, high: 16.0, n: { de: "Hämoglobin", en: "Haemoglobin", pl: "Hemoglobina" } },
    { key: "thrombo", unit: "/nl", low: 150, high: 400, n: { de: "Thrombozyten", en: "Platelets", pl: "Płytki krwi (PLT)" } },
    { key: "alt", unit: "U/l", low: null, high: 35, n: { de: "ALT (GPT)", en: "ALT", pl: "ALT (AlAT)" } },
    { key: "ast", unit: "U/l", low: null, high: 35, n: { de: "AST (GOT)", en: "AST", pl: "AST (AspAT)" } },
    { key: "ggt", unit: "U/l", low: null, high: 40, n: { de: "Gamma-GT", en: "GGT", pl: "GGTP" } },
    { key: "krea", unit: "mg/dl", low: 0.5, high: 0.9, n: { de: "Kreatinin", en: "Creatinine", pl: "Kreatynina" } },
    { key: "b12", unit: "pg/ml", low: 200, high: 900, n: { de: "Vitamin B12", en: "Vitamin B12", pl: "Witamina B12" } },
    { key: "ferritin", unit: "ng/ml", low: 15, high: 150, n: { de: "Ferritin (Eisenspeicher)", en: "Ferritin (iron stores)", pl: "Ferrytyna (zapasy żelaza)" } },
    { key: "hba1c", unit: "%", low: null, high: 5.7, n: { de: "HbA1c (Langzeitzucker)", en: "HbA1c (long-term blood sugar)", pl: "HbA1c (hemoglobina glikowana)" } },
    { key: "ldl", unit: "mg/dl", low: null, high: 116, n: { de: "LDL-Cholesterin", en: "LDL cholesterol", pl: "Cholesterol LDL" } },
    { key: "tsh", unit: "mU/l", low: 0.4, high: 4.0, n: { de: "TSH (Schilddrüse)", en: "TSH (thyroid)", pl: "TSH (tarczyca)" } },
    { key: "ca153", onko: true, unit: "U/ml", low: null, high: 30, n: { de: "CA 15-3 (Tumormarker)", en: "CA 15-3 (tumour marker)", pl: "CA 15-3 (marker nowotworowy)" } },
    { key: "cea", onko: true, unit: "ng/ml", low: null, high: 5.0, n: { de: "CEA (Tumormarker)", en: "CEA (tumour marker)", pl: "CEA (marker nowotworowy)" } },
    { key: "vitd", unit: "ng/ml", low: 30, high: 100, n: { de: "Vitamin D (25-OH)", en: "Vitamin D (25-OH)", pl: "Witamina D (25-OH)" } },
    { key: "lvef", onko: true, unit: "%", low: 55, high: null, n: { de: "LVEF (Herzleistung, Echo)", en: "LVEF (heart function, echo)", pl: "LVEF (frakcja wyrzutowa, echo)" } },
    { key: "weight", unit: "kg", low: null, high: null, n: { de: "Körpergewicht", en: "Body weight", pl: "Masa ciała" } }
  ];
  var CATS = [
    { key: "grundlagen", n: { de: "Grundlagen & Früherkennung", en: "Basics & screening", pl: "Podstawy i wczesne wykrywanie" } },
    { key: "befund", n: { de: "Befund verstehen", en: "Understanding the report", pl: "Zrozumieć wynik" } },
    { key: "therapie", n: { de: "Therapie", en: "Treatment", pl: "Leczenie" } },
    { key: "nebenwirkungen", n: { de: "Nebenwirkungen & Alltag", en: "Side effects & daily life", pl: "Skutki uboczne i codzienność" } },
    { key: "psyche", n: { de: "Psyche & Erfahrungsberichte", en: "Mind & personal stories", pl: "Psychika i historie pacjentek" } },
    { key: "nachsorge", n: { de: "Nachsorge, Recht & Soziales", en: "Follow-up, rights & support", pl: "Kontrola, prawa i wsparcie" } },
    { key: "sonstiges", n: { de: "Sonstiges", en: "Other", pl: "Inne" } }
  ];
  var VLANGS = ["de", "en", "pl", "other"];
  var CATS_G = [
    { key: "grundlagen", n: { de: "Grundlagen", en: "Basics", pl: "Podstawy" } },
    { key: "anleitung", n: { de: "Anleitungen & Praxis", en: "How-to & practice", pl: "Poradniki i praktyka" } },
    { key: "vergleich", n: { de: "Tests & Vergleiche", en: "Tests & comparisons", pl: "Testy i porównania" } },
    { key: "erfahrung", n: { de: "Erfahrungsberichte", en: "Personal experiences", pl: "Doświadczenia" } },
    { key: "hintergrund", n: { de: "Hintergrund & Recht", en: "Background & law", pl: "Tło i prawo" } },
    { key: "sonstiges", n: { de: "Sonstiges", en: "Other", pl: "Inne" } }
  ];
  function cats() { return isHealth() ? CATS : CATS_G; }
  function catName(k) {
    var c = cats().filter(function (x) { return x.key === k; })[0] || cats()[cats().length - 1];
    return c.n[state.lang];
  }
  var PARAM_BY_KEY = {};
  PARAMS.forEach(function (p) { PARAM_BY_KEY[p.key] = p; });

  // Welche Felder hat welche Art von Eintrag — i18n-Felder werden übersetzt
  var KIND = {
    glossary: { tab: "glossary", fields: [["title", "f_term", "text"], ["body", "f_expl", "area"], ["tags", "f_tags", "tags"]] },
    med: { tab: "med", fields: [["title", "f_name", "text"], ["cls", "f_cls", "text"], ["body", "f_how", "area"], ["side", "f_side", "area"], ["notes", "f_notes", "area"]] },
    video: { tab: "videos", fields: [] },
    study: { tab: "studies", fields: [["title", "f_title", "text"], ["url", "f_study_url", "url"], ["year", "f_year", "text"], ["body", "f_study_note", "area"]] },
    research: { tab: "research", fields: [["title", "f_title", "text"], ["date", "f_date", "date"], ["source", "f_source", "url"], ["body", "f_text", "area"]] },
    finding: { tab: "values", fields: [["title", "f_title", "text"], ["date", "f_date", "date"], ["body", "f_finding_body", "area"]] },
    value: { tab: "values", fields: [] },
    analysis: { tab: "values", fields: [["title", "f_title", "text"], ["body", "f_text", "area"]] }
  };
  var TABS = [
    { id: "home", t: "tab_home" },
    { id: "values", t: "tab_values", kinds: ["value", "finding"], neu: "new_value" },
    { id: "glossary", t: "tab_glossary", kinds: ["glossary"], neu: "new_glossary" },
    { id: "med", t: "tab_med", kinds: ["med"], neu: "new_med" },
    { id: "research", t: "tab_research", kinds: ["research"], neu: "new_research" },
    { id: "studies", t: "tab_studies", kinds: ["study"], neu: "new_study" },
    { id: "chat", t: "tab_chat" },
    { id: "videos", t: "tab_videos", kinds: ["video"], neu: "new_video" },
    { id: "settings", t: "tab_settings", hidden: true }
  ];

  var state = { lang: "de", tab: "home", entries: [], query: "", tag: "", confirm: null, editing: null, editKind: null, pending: [],
    settings: null, models: null, busy: {}, drafts: {}, aiIn: { web: true, mappe: false }, aiErr: {}, confirmKey: false, st: { q: "", source: "pubmed", land: "", open: true, recent: false, results: null, total: 0, imp: "" }, vCat: "", vLang: "", preview: null,
    chats: null, chat: null, chatIn: "", chatOpts: { web: false, mappe: true }, stream: null, chatAbort: null, chatConfirm: null, openGloss: {}, glossAll: false, explain: null, mcp: null, mcpShow: {}, mcpConfirm: null,
    topics: null, topic: null, topicConfirm: false, topicQuery: "" };
  var OK_EXT = /\.(pdf|jpe?g|png|heic|heif|webp)$/i;
  var MAX_BYTES = 30 * 1024 * 1024;

  // ---------- Hilfen ----------
  function $(id) { return document.getElementById(id); }
  function tr(key) {
    if (!isHealth() && T[key + "_g"]) key = key + "_g";
    var e = T[key];
    return e ? (e[state.lang] || e.de) : key;
  }
  function curTopic() {
    var t = (state.topics || []).filter(function (x) { return x.id === state.topic; })[0];
    return t || (state.topics || [])[0] || null;
  }
  // Krebsthema? Dann gibt es Tumormarker und Herz-Echo als Vorlage (Herzkontrolle unter Anti-HER2-/Anthrazyklin-Therapie)
  function isOnko() {
    var t = curTopic();
    return !!t && /krebs|karzinom|carcinom|tumou?r|onkolog|cancer|carcinoma|nowotw|rak |raka|chłoniak|lymphom|leukäm|mamma/i.test(allText(t.name) + " " + (t.context || "") + " " + allText(t.desc));
  }
  function isHealth() { var t = curTopic(); return !t || t.kind === "health"; }
  function sectionOn(id) {
    var t = curTopic();
    return !t || ["home", "settings"].indexOf(id) !== -1 || (t.sections || []).indexOf(id) !== -1;
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  // Text in der gewählten Sprache, sonst die nächstbeste vorhandene Fassung
  function L(v) {
    if (v == null) return "";
    if (typeof v === "string") return v;
    if (v[state.lang]) return v[state.lang];
    for (var i = 0; i < LANGS.length; i++) if (v[LANGS[i]]) return v[LANGS[i]];
    return "";
  }
  function allText(v) {
    if (v == null) return "";
    if (typeof v === "string" || typeof v === "number") return String(v);
    if (Array.isArray(v)) return v.map(allText).join(" ");
    return LANGS.map(function (l) { return v[l] || ""; }).join(" ");
  }
  function hl(text) {
    var s = esc(text);
    var q = state.query.trim();
    if (!q) return s;
    var re = new RegExp("(" + q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/&/g, "&amp;").replace(/</g, "&lt;") + ")", "gi");
    return s.replace(re, "<mark>$1</mark>");
  }
  function fmtDate(d) {
    if (!d) return "";
    var p = String(d).slice(0, 10).split("-");
    if (p.length !== 3) return d;
    return state.lang === "en" ? p[2] + "/" + p[1] + "/" + p[0] : p[2] + "." + p[1] + "." + p[0];
  }
  function fmtNum(n) {
    if (n == null || n === "" || isNaN(n)) return "–";
    var s = String(Math.round(Number(n) * 100) / 100);
    return state.lang === "en" ? s : s.replace(".", ",");
  }
  function today() {
    var d = new Date();
    return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2);
  }
  function toast(msg) {
    var el = $("toast");
    el.textContent = msg;
    el.hidden = false;
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { el.hidden = true; }, 2600);
  }
  function api(method, url, body) {
    // Neue Einträge landen im aktuell gewählten Thema
    if (method === "POST" && url === "/api/entries" && body && !body.topic_id) body.topic_id = state.topic;
    if (url === "/api/chats" || (method === "POST" && url === "/api/translate")) {
      if (url === "/api/chats") url += "?topic=" + state.topic; else body.topic = state.topic;
    }
    return fetch(url, {
      method: method,
      headers: body ? { "Content-Type": "application/json" } : {},
      body: body ? JSON.stringify(body) : undefined,
      credentials: "same-origin"
    }).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    });
  }
  function save(key, val) { try { localStorage.setItem("mappe-" + key, val); } catch (e) { /* privat */ } }
  function load(key) { try { return localStorage.getItem("mappe-" + key); } catch (e) { return null; } }

  function matches(e) {
    var q = state.query.trim().toLowerCase();
    if (!q) return true;
    var d = e.data;
    var hay = [d.title, d.body, d.cls, d.side, d.notes, d.note, d.source, d.tags, d.paramLabel, d.date, d.channel, d.url, paramName(d)].map(allText).join(" ").toLowerCase() +
      " " + (e.files || []).map(function (f) { return f.name; }).join(" ").toLowerCase();
    return hay.indexOf(q) !== -1;
  }
  function byKind(kind) {
    return state.entries.filter(function (e) { return e.kind === kind && matches(e); });
  }
  function paramName(d) {
    var p = PARAM_BY_KEY[d.param];
    return p ? p.n[state.lang] : (d.paramLabel || d.param || "");
  }
  function flag(v, low, high) {
    if (v == null || isNaN(v)) return "ohne";
    if (low == null && high == null) return "ohne";
    if (low != null && v < low) return "niedrig";
    if (high != null && v > high) return "hoch";
    return "ok";
  }
  function flagHtml(f) {
    var label = { ok: tr("inrange"), hoch: tr("high"), niedrig: tr("low"), ohne: tr("noref") }[f];
    return '<span class="flagge ' + f + '">' + label + "</span>";
  }
  function refText(low, high, unit) {
    if (low == null && high == null) return "";
    var s = low != null && high != null ? fmtNum(low) + "–" + fmtNum(high) : low != null ? "≥ " + fmtNum(low) : "≤ " + fmtNum(high);
    return tr("ref") + " " + s + " " + (unit || "");
  }

  // ---------- Darstellung ----------
  function render() {
    document.documentElement.lang = state.lang;
    document.title = tr("appName");
    Array.prototype.forEach.call(document.querySelectorAll("[data-t]"), function (el) { el.textContent = tr(el.getAttribute("data-t")); });
    Array.prototype.forEach.call(document.querySelectorAll("[data-lang]"), function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-lang") === state.lang ? "true" : "false");
    });
    $("suche").placeholder = tr("search");
    var tab = TABS.filter(function (t) { return t.id === state.tab; })[0];
    $("neuKnopf").textContent = tr(tab.neu || "new_any");
    $("neuKnopf").hidden = state.tab === "settings" || state.tab === "chat";
    $("suche").parentNode.hidden = state.tab === "settings" || state.tab === "chat";

    if (!sectionOn(state.tab)) state.tab = "home";
    renderTopics();
    $("einstKnopf").setAttribute("aria-pressed", state.tab === "settings" ? "true" : "false");
    $("reiter").innerHTML = TABS.filter(function (t) { return sectionOn(t.id) && !t.hidden; }).map(function (t) {
      var n = t.kinds ? state.entries.filter(function (e) { return t.kinds.indexOf(e.kind) !== -1; }).length : "";
      return '<button type="button" data-tab="' + t.id + '"' + (t.id === state.tab ? ' aria-current="page"' : "") + ">" +
        esc(tr(t.t)) + (n !== "" ? '<span class="zahl">' + n + "</span>" : "") + "</button>";
    }).join("");

    var html;
    if (state.query.trim() && state.tab === "home") html = renderSearch();
    else if (state.tab === "home") html = renderHome();
    else if (state.tab === "values") html = renderValues();
    else if (state.tab === "glossary") html = renderGlossary();
    else if (state.tab === "med") html = renderMeds();
    else if (state.tab === "settings") html = renderSettings();
    else if (state.tab === "videos") html = renderVideos();
    else if (state.tab === "chat") html = renderChat();
    else if (state.tab === "studies") html = renderStudies();
    else html = renderResearch();
    $("inhalt").innerHTML = html;
    if (state.tab === "chat") afterChatRender();
  }

  function topicCount(t) {
    // Für das offene Thema zählt die aktuelle Liste, für die anderen der Stand vom Laden
    if (t.id === state.topic && state.entries) return state.entries.length;
    var n = 0, c = t.counts || {};
    Object.keys(c).forEach(function (k) { if (k !== "chat") n += c[k]; });
    return n;
  }
  function renderTopics() {
    var list = state.topics || [];
    var q = state.topicQuery.trim().toLowerCase();
    var hits = list.filter(function (t) {
      if (!q) return true;
      return [t.name, t.desc].map(allText).join(" ").toLowerCase().indexOf(q) !== -1;
    });
    $("themenSuche").placeholder = tr("t_search");
    $("themenListe").innerHTML = hits.length ? hits.map(function (t) {
      var active = t.id === state.topic;
      var name = t.name[state.lang] || t.name.de;
      var desc = t.desc ? (t.desc[state.lang] || t.desc.de || "") : "";
      return '<li class="thema-eintrag' + (active ? " aktiv" : "") + '">' +
        '<button type="button" class="thema-wahl" data-topic="' + t.id + '"' + (active ? ' aria-current="true"' : "") + ">" +
        '<span class="punkt ' + (t.kind === "health" ? "gesund" : "allg") + '"></span>' +
        '<span class="thema-text"><b>' + esc(name) + "</b>" + (desc ? "<small>" + esc(desc) + "</small>" : "") + "</span>" +
        '<span class="thema-zahl">' + topicCount(t) + "</span></button>" +
        '<button type="button" class="thema-werkzeug" data-act="topic-edit" data-tid="' + t.id + '" aria-label="' + esc(tr("t_edit")) + ": " + esc(name) +
        '" title="' + esc(tr("t_edit")) + '">⚙</button></li>';
    }).join("") : '<li class="themen-leer">' + esc(tr("t_none")) + "</li>";
    var ct = curTopic();
    $("themenAktiv").textContent = ct ? (ct.name[state.lang] || ct.name.de) : tr("topics");
  }
  function setDrawer(open) {
    document.body.classList.toggle("leiste-offen", open);
    $("leistenSchleier").hidden = !open;
    $("themenKnopf").setAttribute("aria-expanded", open ? "true" : "false");
  }
  function switchTopic(id) {
    if (id === state.topic) return;
    state.topic = id;
    save("topic", String(id));
    state.chats = null; state.chat = null; state.stream = null; state.drafts = {}; state.aiErr = {};
    state.query = ""; $("suche").value = ""; state.tag = ""; state.st.results = null; state.vCat = ""; state.vLang = ""; state.confirm = null;
    state.entries = [];
    render();
    loadEntries();
  }
  function loadEntries() {
    var tid = state.topic;
    return api("GET", "/api/entries?topic=" + tid).then(function (rows) { if (tid === state.topic) { state.entries = rows; render(); } })
      .catch(function () { $("inhalt").innerHTML = '<div class="leer">' + esc(tr("err_load")) + "</div>"; });
  }
  function loadTopics() {
    return api("GET", "/api/topics").then(function (list) {
      state.topics = list;
      var saved = Number(load("topic"));
      if (!list.some(function (t) { return t.id === state.topic; })) {
        state.topic = list.some(function (t) { return t.id === saved; }) ? saved : (list[0] ? list[0].id : null);
      }
      render();
    });
  }

  // Kleines, sicheres Markdown: erst escapen, dann ## / ### / - / **…** / Links
  function inline(s) {
    return s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  }
  function md(text) {
    if (!text) return "";
    var out = [], list = null, para = [];
    function flushP() { if (para.length) { out.push("<p>" + inline(para.join("<br>")) + "</p>"); para = []; } }
    function flushL() { if (list) { out.push("<ul>" + list.map(function (li) { return "<li>" + inline(li) + "</li>"; }).join("") + "</ul>"); list = null; } }
    esc(text).split(/\n/).forEach(function (line) {
      var t = line.trim();
      var m;
      if (!t) { flushP(); flushL(); return; }
      if ((m = t.match(/^#{1,3}\s+(.*)$/))) { flushP(); flushL(); out.push("<h4>" + inline(m[1]) + "</h4>"); return; }
      if ((m = t.match(/^(?:[-*•]|\d+\.)\s+(.*)$/))) { flushP(); (list = list || []).push(m[1]); return; }
      flushL(); para.push(t);
    });
    flushP(); flushL();
    return '<div class="md">' + out.join("") + "</div>";
  }
  function txt(v) {
    var s = L(v);
    if (!s) return "";
    return state.query.trim() ? "<p>" + hl(s) + "</p>" : md(s);
  }
  function hasKey() { return !!(state.settings && state.settings.openai_set); }
  function needKey() {
    return '<div class="ki-leer">' + esc(tr("ai_need_key")) + ' <button type="button" class="knopf klein" data-tab="settings">' + esc(tr("ai_to_settings")) + "</button></div>";
  }
  function busyHtml(key) {
    var err = state.aiErr[key];
    if (state.busy[key]) return '<div class="ki-status"><span class="spinner" aria-hidden="true"></span>' + esc(tr("ai_busy")) + "</div>";
    return err ? '<div class="ki-status fehler">' + esc(err) + "</div>" : "";
  }
  function sourcesHtml(list) {
    var ok = (list || []).filter(function (q) { return safeUrl(q.url); });
    if (!ok.length) return "";
    return '<div class="feld"><span class="eyebrow">' + esc(tr("sources")) + '</span><ul class="quellen">' + ok.map(function (q) {
      return '<li><a href="' + esc(q.url) + '" target="_blank" rel="noopener noreferrer">' + esc(q.title || q.url) + "</a></li>";
    }).join("") + "</ul></div>";
  }
  function aiBlock(e) {
    var a = e.data.ai;
    var key = "an" + e.id;
    var btn = hasKey() ? '<button type="button" class="knopf klein ki" data-act="ai-analyze" data-id="' + e.id + '"' + (state.busy[key] ? " disabled" : "") + ">✦ " +
      esc(tr(a ? "ai_reclassify" : "ai_classify")) + "</button>" : "";
    var body = "";
    if (a) {
      body = '<div class="ki-ergebnis"><div class="eyebrow">✦ ' + esc(tr("ai_classify")) + " · " + esc(fmtDate(a.date)) + " " + esc((a.date || "").slice(11)) + "</div>" +
        "<p><strong>" + esc(L(a.summary)) + "</strong></p>" +
        "<details><summary>" + esc(tr("ai_show_full")) + "</summary>" + md(L(a.text)) +
        '<p class="hinweis">' + esc(tr("ai_hint_disclaimer")) + " (" + esc(a.model || "") + ")</p></details></div>";
    }
    return body + busyHtml(key) + (btn ? '<div class="karte-fuss links">' + btn + "</div>" : "");
  }
  function analysisCard(e, open) {
    return '<article class="karte ki-karte"><div class="meta"><span class="chip ki">✦ ' + esc(tr("k_analysis")) + "</span>" + fmtDate(e.data.date) + "</div>" +
      "<details" + (open ? " open" : "") + "><summary><h3>" + hl(L(e.data.title)) + "</h3></summary>" + txt(e.data.body) +
      '<p class="hinweis">' + esc(tr("ai_hint_disclaimer")) + (e.data.ai_model ? " (" + esc(e.data.ai_model) + ")" : "") + "</p></details>" + cardFoot(e) + "</article>";
  }
  function draftHtml(slot) {
    var d = state.drafts[slot];
    if (!d) return "";
    var x = d.data;
    var extra = "";
    if (d.kind === "med") extra = (L(x.cls) ? '<div class="meta"><span class="chip">' + esc(L(x.cls)) + "</span></div>" : "") +
      '<div class="feld"><span class="eyebrow">' + esc(tr("f_how")) + "</span>" + md(L(x.body)) + "</div>" +
      '<div class="feld"><span class="eyebrow">' + esc(tr("f_side")) + "</span>" + md(L(x.side)) + "</div>";
    else extra = md(L(x.body)) + (x.tags && x.tags.length ? '<div class="meta">' + x.tags.map(function (t) { return '<span class="chip">' + esc(t) + "</span>"; }).join("") + "</div>" : "");
    return '<article class="karte entwurf"><div class="eyebrow">✦ ' + esc(tr("ai_draft")) + "</div><h3>" + esc(L(x.title)) + "</h3>" + extra +
      sourcesHtml(x.sources) + '<p class="hinweis">' + esc(tr("ai_hint_disclaimer")) + "</p>" +
      '<div class="karte-fuss"><button type="button" class="knopf klein" data-act="ai-discard" data-slot="' + slot + '">' + esc(tr("ai_discard")) + "</button>" +
      '<button type="button" class="knopf klein primaer" data-act="ai-save" data-slot="' + slot + '">' + esc(tr("ai_save")) + "</button></div></article>";
  }
  function aiInputRow(slot, ph, btn) {
    if (!hasKey()) return needKey();
    return '<div class="ki-zeile"><input type="text" id="ai-in-' + slot + '" data-ai-in="' + slot + '" placeholder="' + esc(tr(ph)) + '" value="' + esc(state.aiIn[slot] || "") + '">' +
      '<button type="button" class="knopf ki" data-act="ai-lookup" data-slot="' + slot + '"' + (state.busy[slot] ? " disabled" : "") + ">✦ " + esc(tr(btn)) + "</button></div>" +
      busyHtml(slot) + draftHtml(slot);
  }

  function fmtSize(b) {
    return b > 1048576 ? fmtNum(b / 1048576) + " MB" : Math.max(1, Math.round(b / 1024)) + " KB";
  }
  function filesHtml(e, compact) {
    var fs = e.files || [];
    if (!fs.length) return "";
    return '<div class="anhaenge' + (compact ? " kompakt" : "") + '">' + fs.map(function (f) {
      var url = "/api/files/" + f.id;
      var bild = /^image\/(jpeg|png|webp)$/.test(f.mime);
      return '<a class="anhang" href="' + url + '" target="_blank" rel="noopener">' +
        (bild && !compact ? '<img src="' + url + '" alt="" loading="lazy">' : '<span class="anhang-typ">' + (f.mime === "application/pdf" ? "PDF" : "IMG") + "</span>") +
        '<span class="anhang-name">' + hl(f.name) + '</span><span class="anhang-groesse">' + fmtSize(f.size) + "</span></a>";
    }).join("") + "</div>";
  }

  function cardFoot(e) {
    if (state.confirm === e.id) {
      return '<div class="karte-fuss bestaetigen">' + esc(tr("del_q")) +
        ' <button type="button" class="knopf klein gefahr" data-act="del-yes" data-id="' + e.id + '">' + esc(tr("yes_del")) + "</button>" +
        ' <button type="button" class="knopf klein" data-act="del-no">' + esc(tr("cancel")) + "</button></div>";
    }
    return '<div class="karte-fuss">' +
      '<button type="button" class="knopf klein" data-act="edit" data-id="' + e.id + '">' + esc(tr("edit")) + "</button>" +
      '<button type="button" class="knopf klein gefahr" data-act="del" data-id="' + e.id + '">' + esc(tr("del")) + "</button></div>";
  }

  function emptyBox(textKey, kind) {
    return '<div class="leer">' + esc(tr(textKey)) +
      (kind ? '<div><button type="button" class="knopf primaer" data-act="new" data-kind="' + kind + '">' + esc(tr(kind === "value" ? "new_value" : "new_finding")) + "</button></div>" : "") +
      "</div>";
  }

  function renderHome() {
    var cnt = function (k) { return state.entries.filter(function (e) { return e.kind === k; }).length; };
    var tiles = [
      ["values", cnt("value") + cnt("finding"), "tab_values"],
      ["glossary", cnt("glossary"), "tab_glossary"],
      ["med", cnt("med"), "tab_med"],
      ["research", cnt("research"), "tab_research"],
      ["studies", cnt("study"), "tab_studies"],
      ["videos", cnt("video"), "tab_videos"]
    ].filter(function (t) { return sectionOn(t[0]); });
    var ct = curTopic();
    var groups = valueGroups();
    var latest = groups.slice(0, 6).map(function (g) {
      var last = g.items[g.items.length - 1].data;
      return '<div class="zeile-klein"><span class="titel">' + esc(g.name) + '</span><span class="leise"><span class="wert">' +
        fmtNum(last.value) + " " + esc(last.unit || "") + "</span> " + flagHtml(flag(last.value, last.low, last.high)) + "</span></div>";
    }).join("");
    var recent = state.entries.slice(0, 8).map(function (e) {
      var titel = e.kind === "value" ? paramName(e.data) + ": " + fmtNum(e.data.value) + " " + (e.data.unit || "") : L(e.data.title);
      return '<div class="zeile-klein"><span class="titel">' + esc(titel) + '</span><span class="leise">' + esc(tr("k_" + e.kind)) + " · " + fmtDate(e.updated) + "</span></div>";
    }).join("");
    return '<section class="abschnitt">' + (ct ? '<h2 class="thema-titel">' + esc(ct.name[state.lang] || ct.name.de) + "</h2>" +
      (ct.desc && L(ct.desc) ? '<p class="thema-desc">' + esc(L(ct.desc)) + "</p>" : "") : "") +
      '<p style="max-width:65ch;margin:0 0 16px">' + esc(tr("home_intro")) + "</p>" +
      '<div class="kacheln">' + tiles.map(function (t) {
        return '<button type="button" class="kachel" data-tab="' + t[0] + '"><b>' + t[1] + "</b><span>" + esc(tr(t[2])) + "</span></button>";
      }).join("") + "</div></section>" +
      '<div class="zwei">' + (sectionOn("values") ? '<section class="abschnitt"><div class="abschnitt-kopf"><h2>' + esc(tr("latest_values")) + "</h2></div>" +
      '<div class="karte">' + (latest || '<span class="hinweis">' + esc(tr("empty_values")) + "</span>") + "</div></section>" : "") +
      '<section class="abschnitt"><div class="abschnitt-kopf"><h2>' + esc(tr("recent")) + "</h2></div>" +
      '<div class="karte">' + (recent || '<span class="hinweis">' + esc(tr("recent_empty")) + "</span>") + "</div></section></div>" + renderHints();
  }
  function renderHints() {
    var hints = state.entries.filter(function (e) { return e.kind === "analysis" && e.data.scope === "hints"; })
      .sort(function (a, b) { return b.id - a.id; });
    return '<section class="abschnitt"><div class="abschnitt-kopf"><div><h2>✦ ' + esc(tr("ai_hints")) + "</h2><p>" + esc(tr("ai_hints_sub")) + "</p></div>" +
      (hasKey() ? '<button type="button" class="knopf ki" data-act="ai-hints"' + (state.busy.hints ? " disabled" : "") + ">✦ " + esc(tr("ai_hints_btn")) + "</button>" : "") + "</div>" +
      (hasKey() ? "" : needKey()) + busyHtml("hints") +
      (hints.length ? '<div class="liste">' + hints.map(function (e, i) { return analysisCard(e, i === 0); }).join("") + "</div>"
        : hasKey() ? '<div class="leer">' + esc(tr("ai_hints_empty")) + "</div>" : "") + "</section>";
  }

  function renderSearch() {
    var hits = state.entries.filter(matches);
    if (!hits.length) return '<div class="leer">' + esc(tr("empty_search")) + "</div>";
    return '<div class="liste">' + hits.map(function (e) {
      var titel = e.kind === "value" ? paramName(e.data) + ": " + fmtNum(e.data.value) + " " + (e.data.unit || "") + " (" + fmtDate(e.data.date) + ")" : L(e.data.title);
      var text = e.kind === "value" ? L(e.data.note) : L(e.data.body);
      return '<div class="karte"><div class="meta"><span class="chip">' + esc(tr("k_" + e.kind)) + "</span></div><h3>" + hl(titel) + "</h3>" +
        (text ? "<p>" + hl(text) + "</p>" : "") + filesHtml(e) + cardFoot(e) + "</div>";
    }).join("") + "</div>";
  }

  function valueGroups() {
    var map = {};
    var order = [];
    state.entries.filter(function (e) { return e.kind === "value"; }).forEach(function (e) {
      var k = e.data.param === "_other" ? "_" + (e.data.paramLabel || "").toLowerCase() : e.data.param;
      if (!map[k]) { map[k] = { key: k, name: paramName(e.data), items: [] }; order.push(k); }
      map[k].items.push(e);
    });
    var groups = order.map(function (k) { return map[k]; });
    groups.forEach(function (g) {
      g.items.sort(function (a, b) { return a.data.date < b.data.date ? -1 : a.data.date > b.data.date ? 1 : a.id - b.id; });
      g.lastDate = g.items[g.items.length - 1].data.date;
    });
    groups.sort(function (a, b) { return a.lastDate < b.lastDate ? 1 : -1; });
    return groups;
  }

  function spark(items) {
    var W = 150, H = 44, P = 4;
    var vals = items.map(function (e) { return Number(e.data.value); });
    var last = items[items.length - 1].data;
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
    if (last.low != null) lo = Math.min(lo, last.low);
    if (last.high != null) hi = Math.max(hi, last.high);
    if (hi === lo) { hi += 1; lo -= 1; }
    var y = function (v) { return H - P - (v - lo) / (hi - lo) * (H - 2 * P); };
    var x = function (i) { return items.length === 1 ? W / 2 : P + i * (W - 2 * P) / (items.length - 1); };
    var band = "";
    if (last.low != null || last.high != null) {
      var top = y(last.high != null ? last.high : hi), bot = y(last.low != null ? last.low : lo);
      band = '<rect x="0" y="' + top.toFixed(1) + '" width="' + W + '" height="' + Math.max(1, bot - top).toFixed(1) + '" fill="var(--band)"/>';
    }
    var pts = vals.map(function (v, i) { return x(i).toFixed(1) + "," + y(v).toFixed(1); }).join(" ");
    var lx = x(vals.length - 1), ly = y(vals[vals.length - 1]);
    var col = flag(last.value, last.low, last.high);
    var dot = col === "ok" ? "var(--gut)" : col === "ohne" ? "var(--akzent)" : "var(--schlecht)";
    return '<svg viewBox="0 0 ' + W + " " + H + '" preserveAspectRatio="none" aria-hidden="true">' + band +
      (vals.length > 1 ? '<polyline points="' + pts + '" fill="none" stroke="var(--leise)" stroke-width="1.5" vector-effect="non-scaling-stroke"/>' : "") +
      '<circle cx="' + lx.toFixed(1) + '" cy="' + ly.toFixed(1) + '" r="3.5" fill="' + dot + '"/></svg>';
  }

  function renderValues() {
    var q = state.query.trim();
    var groups = valueGroups().filter(function (g) {
      return !q || g.items.some(matches) || g.name.toLowerCase().indexOf(q.toLowerCase()) !== -1;
    });
    var labs = groups.map(function (g) {
      var last = g.items[g.items.length - 1].data;
      var rows = g.items.slice().reverse().map(function (e) {
        var d = e.data;
        if (state.confirm === e.id) {
          return '<tr><td colspan="4"><span class="bestaetigen">' + esc(tr("del_q")) +
            ' <button type="button" class="knopf klein gefahr" data-act="del-yes" data-id="' + e.id + '">' + esc(tr("yes_del")) + "</button>" +
            ' <button type="button" class="knopf klein" data-act="del-no">' + esc(tr("cancel")) + "</button></span></td></tr>";
        }
        return "<tr><td>" + fmtDate(d.date) + '</td><td class="wert">' + fmtNum(d.value) + " " + esc(d.unit || "") + " " + flagHtml(flag(d.value, d.low, d.high)) +
          '</td><td class="notiz">' + hl(L(d.note)) + filesHtml(e, true) + '</td><td style="white-space:nowrap">' +
          '<button type="button" class="knopf klein" data-act="edit" data-id="' + e.id + '">' + esc(tr("edit")) + "</button> " +
          '<button type="button" class="knopf klein gefahr" data-act="del" data-id="' + e.id + '" aria-label="' + esc(tr("del")) + '">×</button></td></tr>';
      }).join("");
      var open = q || state.openParam === g.key || state.confirm && g.items.some(function (e) { return e.id === state.confirm; });
      return '<div class="karte param"><div><h3>' + hl(g.name) + '</h3><div class="kennzahl"><span class="wert">' + fmtNum(last.value) + "</span> " +
        '<span class="hinweis">' + esc(last.unit || "") + "</span> " + flagHtml(flag(last.value, last.low, last.high)) + "</div>" +
        '<div class="meta">' + fmtDate(last.date) + (refText(last.low, last.high, last.unit) ? " · " + esc(refText(last.low, last.high, last.unit)) : "") +
        " · " + g.items.length + " " + esc(tr("measurements")) + "</div></div>" + spark(g.items) +
        '<details class="verlauf" data-param="' + esc(g.key) + '"' + (open ? " open" : "") + "><summary>" + esc(tr("history")) + "</summary>" +
        "<table><thead><tr><th>" + esc(tr("f_date")) + "</th><th>" + esc(tr("f_value")) + "</th><th>" + esc(tr("f_assess")) + "</th><th></th></tr></thead><tbody>" +
        rows + "</tbody></table></details>" + '<div class="verlauf">' + aiBlock(g.items[g.items.length - 1]) + "</div></div>";
    }).join("");
    var analyses = byKind("analysis").filter(function (e) { return e.data.scope === "values"; }).sort(function (a, b) { return b.id - a.id; });
    var findings = byKind("finding").sort(function (a, b) { return (a.data.date || "") < (b.data.date || "") ? 1 : -1; });
    return '<section class="abschnitt"><div class="abschnitt-kopf"><div><h2>' + esc(tr("labs")) + "</h2><p>" + esc(tr("labs_sub")) + "</p></div>" +
      '<div class="knoepfe">' + (hasKey() && groups.length ? '<button type="button" class="knopf ki" data-act="ai-values"' + (state.busy.values ? " disabled" : "") + ">✦ " + esc(tr("ai_values_btn")) + "</button>" : "") +
      '<button type="button" class="knopf" data-act="new" data-kind="value">' + esc(tr("new_value")) + "</button></div></div>" + busyHtml("values") +
      (labs ? '<div class="liste">' + labs + "</div>" : q ? '<div class="leer">' + esc(tr("empty_search")) + "</div>" : emptyBox("empty_values", "value")) + "</section>" +
      '<section class="abschnitt"><div class="abschnitt-kopf"><div><h2>' + esc(tr("findings")) + "</h2><p>" + esc(tr("findings_sub")) + "</p></div>" +
      '<div class="knoepfe"><button type="button" class="knopf primaer" data-act="upload">' + esc(tr("upload_finding")) + "</button>" +
      '<button type="button" class="knopf" data-act="new" data-kind="finding">' + esc(tr("new_finding")) + "</button></div></div>" +
      (findings.length ? '<div class="liste">' + findings.map(function (e) {
        return '<article class="karte"><div class="meta">' + fmtDate(e.data.date) + "</div><h3>" + hl(L(e.data.title)) + "</h3>" + txt(e.data.body) + filesHtml(e) + aiBlock(e) + cardFoot(e) + "</article>";
      }).join("") + "</div>" : q ? '<div class="leer">' + esc(tr("empty_search")) + "</div>" : emptyBox("empty_findings", "finding")) + "</section>" +
      (analyses.length ? '<section class="abschnitt"><div class="abschnitt-kopf"><h2>✦ ' + esc(tr("ai_analyses")) + "</h2></div>" +
        '<div class="liste">' + analyses.map(function (e, i) { return analysisCard(e, i === 0); }).join("") + "</div></section>" : "");
  }

  function tagsOf(e) {
    var t = e.data.tags;
    return Array.isArray(t) ? t : [];
  }
  function renderGlossary() {
    var all = state.entries.filter(function (e) { return e.kind === "glossary"; });
    var tags = [];
    all.forEach(function (e) { tagsOf(e).forEach(function (t) { if (tags.indexOf(t) === -1) tags.push(t); }); });
    tags.sort();
    var items = byKind("glossary").filter(function (e) { return !state.tag || tagsOf(e).indexOf(state.tag) !== -1; });
    items.sort(function (a, b) { return L(a.data.title).localeCompare(L(b.data.title), state.lang); });
    var chips = '<div class="chips"><button type="button" data-tag=""' + (!state.tag ? ' aria-pressed="true"' : "") + ">" + esc(tr("all")) + "</button>" +
      tags.map(function (t) { return '<button type="button" data-tag="' + esc(t) + '"' + (state.tag === t ? ' aria-pressed="true"' : "") + ">" + esc(t) + "</button>"; }).join("") + "</div>";
    return '<section class="abschnitt"><div class="abschnitt-kopf"><h2>' + esc(tr("tab_glossary")) + "</h2>" +
      '<button type="button" class="knopf klein" data-act="gloss-all">' + esc(tr(state.glossAll ? "collapse_all" : "expand_all")) + "</button></div>" +
      aiInputRow("glossary", "ai_explain_ph", "ai_explain_btn") + '<p class="hinweis tipp">✦ ' + esc(tr("x_hint")) + "</p>" + chips +
      (items.length ? '<div class="raster">' + items.map(function (e) {
        return '<article class="karte"><h3>' + hl(L(e.data.title)) + "</h3>" +
          (tagsOf(e).length ? '<div class="meta">' + tagsOf(e).map(function (t) { return '<span class="chip">' + esc(t) + "</span>"; }).join("") + "</div>" : "") +
          glossBody(e) + filesHtml(e) + cardFoot(e) + "</article>";
      }).join("") + "</div>" : '<div class="leer">' + esc(tr("empty_search")) + "</div>") + "</section>";
  }
  // Lange Erklärungen zeigen erst ein paar Zeilen; bei aktiver Suche ist alles offen, damit Treffer sichtbar sind
  // Lange Texte (Begriffe, Medikamente) erst gekürzt zeigen; bei Suche offen, damit Treffer sichtbar sind
  function aufklapp(id, inner, lang, extraClass) {
    if (!lang) return inner;
    var offen = state.query.trim() || state.glossAll || state.openGloss[id];
    return '<div class="aufklapp' + (extraClass ? " " + extraClass : "") + (offen ? " offen" : "") + '">' + inner + "</div>" +
      '<button type="button" class="mehr-knopf" data-act="gloss-toggle" data-id="' + id + '" aria-expanded="' + (offen ? "true" : "false") + '">' +
      esc(tr(offen ? "less" : "more")) + (offen ? " ▴" : " ▾") + "</button>";
  }
  function glossBody(e) {
    var text = L(e.data.body);
    if (!text) return "";
    return aufklapp(e.id, txt(e.data.body), text.length > 200 || text.split("\n").length > 4);
  }

  function renderMeds() {
    var items = byKind("med").sort(function (a, b) { return L(a.data.title).localeCompare(L(b.data.title), state.lang); });
    var feld = function (key, val) { return L(val) ? '<div class="feld"><span class="eyebrow">' + esc(tr(key)) + "</span>" + txt(val) + "</div>" : ""; };
    return '<section class="abschnitt"><div class="abschnitt-kopf"><h2>' + esc(tr("tab_med")) + "</h2>" +
      '<button type="button" class="knopf klein" data-act="gloss-all">' + esc(tr(state.glossAll ? "collapse_all" : "expand_all")) + "</button></div>" +
      aiInputRow("med", "ai_med_ph", "ai_med_btn") +
      (items.length ? '<div class="raster">' + items.map(function (e) {
        var d = e.data;
        return '<article class="karte"><h3>' + hl(L(d.title)) + "</h3>" + (L(d.cls) ? '<div class="meta"><span class="chip">' + hl(L(d.cls)) + "</span></div>" : "") +
          aufklapp(e.id, feld("f_how", d.body) + feld("f_side", d.side) + feld("f_notes", d.notes),
            (L(d.body) + L(d.side) + L(d.notes)).length > 260, "hoch") + filesHtml(e) + cardFoot(e) + "</article>";
      }).join("") + "</div>" : '<div class="leer">' + esc(tr("empty_search")) + "</div>") + "</section>";
  }

  function safeUrl(u) { return /^https?:\/\//i.test(u || "") ? u : ""; }
  function renderResearch() {
    var items = byKind("research").sort(function (a, b) { return (a.data.date || "") < (b.data.date || "") ? 1 : a.data.date === b.data.date ? b.id - a.id : -1; });
    var ask = !hasKey() ? needKey() :
      '<div class="ki-frage"><textarea id="ai-in-research" data-ai-in="research" rows="2" placeholder="' + esc(tr("ai_ask_ph")) + '">' + esc(state.aiIn.research || "") + "</textarea>" +
      '<div class="ki-optionen"><label class="haken"><input type="checkbox" data-ai-opt="web"' + (state.aiIn.web ? " checked" : "") + "> " + esc(tr("ai_use_web")) + "</label>" +
      '<label class="haken"><input type="checkbox" data-ai-opt="mappe"' + (state.aiIn.mappe ? " checked" : "") + "> " + esc(tr("ai_use_mappe")) + "</label>" +
      '<button type="button" class="knopf ki" data-act="ai-lookup" data-slot="research"' + (state.busy.research ? " disabled" : "") + ">✦ " + esc(tr("ai_ask_btn")) + "</button></div></div>" +
      busyHtml("research") + draftHtml("research");
    return '<section class="abschnitt"><div class="abschnitt-kopf"><h2>' + esc(tr("tab_research")) + "</h2></div>" + ask +
      (items.length ? '<div class="liste">' + items.map(function (e) {
        var d = e.data, u = safeUrl(d.source);
        return '<article class="karte"><div class="meta">' + fmtDate(d.date) + (u ? ' · <a href="' + esc(u) + '" target="_blank" rel="noopener noreferrer">' + esc(u.replace(/^https?:\/\/(www\.)?/, "").split("/")[0]) + " ↗</a>" : "") +
          "</div><h3>" + hl(L(d.title)) + "</h3>" + txt(d.body) + sourcesHtml(d.sources) + filesHtml(e) + cardFoot(e) + "</article>";
      }).join("") + "</div>" : '<div class="leer">' + esc(tr("empty_search")) + "</div>") + "</section>";
  }

  function thumbHtml(d) {
    if (d.thumb) return '<img src="/api/thumbs/' + esc(d.thumb) + '" alt="" loading="lazy">';
    var host = "";
    try { host = (d.url || "").replace(/^https?:\/\/(www\.)?/, "").split("/")[0]; } catch (e) { host = ""; }
    return '<span class="ersatzbild"><b>' + esc((d.channel || host || "?").charAt(0).toUpperCase()) + "</b><small>" + esc(host) + "</small></span>";
  }
  function videoCard(e) {
    var d = e.data;
    var yt = !!d.yt_id && d.embed !== false;
    var lang = d.vlang && d.vlang !== "other" ? '<span class="sprach-marke">' + esc(d.vlang.toUpperCase()) + "</span>" : "";
    var media = '<span class="vorschau">' + thumbHtml(d) + (yt ? '<span class="play" aria-hidden="true"></span>' : "") +
      lang + (d.duration ? '<span class="dauer">' + esc(d.duration) + "</span>" : "") + "</span>";
    var openMedia = yt
      ? '<button type="button" class="vorschau-knopf" data-act="play" data-id="' + e.id + '" aria-label="' + esc(tr("play")) + '">' + media + "</button>"
      : '<a class="vorschau-knopf" href="' + esc(safeUrl(d.url)) + '" target="_blank" rel="noopener noreferrer">' + media + "</a>";
    return '<article class="karte video">' + openMedia + '<div class="video-text"><h3>' + hl(L(d.title) || d.url) + "</h3>" +
      '<div class="meta">' + (d.channel ? "<span>" + hl(d.channel) + "</span>" : "") + "</div>" +
      txt(d.note) + videoKi(e) + filesHtml(e) + cardFoot(e) + "</div></article>";
  }
  function hasTranscript(d) { return !!(d.transcript && d.transcript.text); }
  function videoPending(e) { return !e.data.summary && (!e.data.yt_id || hasTranscript(e.data) || (state.settings && state.settings.transcript_set)); }
  function videoKi(e) {
    var d = e.data, key = "vid" + e.id, html = "";
    if (d.summary) {
      html += '<p class="video-kurz">✦ ' + hl(L(d.summary.short)) + "</p>" +
        (d.summary.topics && d.summary.topics.length ? '<div class="meta">' + d.summary.topics.map(function (t) { return '<span class="chip ki">' + esc(t) + "</span>"; }).join("") + "</div>" : "") +
        '<details class="video-details"><summary>' + esc(tr("v_summary")) + "</summary>" + md(L(d.summary.text)) +
        '<p class="hinweis">' + esc(tr("ai_hint_disclaimer")) + " (" + esc(d.summary.model || "") + ")</p></details>";
    }
    if (hasTranscript(d)) {
      html += '<details class="video-details"><summary>' + esc(tr("v_transcript")) + " · " + esc((d.transcript.lang || "").toUpperCase()) +
        (d.transcript.source === "manual" ? " · " + esc(tr("v_tr_manual")) : "") + '</summary><div class="transkript">' + transcriptHtml(d.transcript.text, null) + "</div></details>";
    }
    var label = !d.summary ? (d.yt_id && !hasTranscript(d) ? "v_process" : "v_summarize") : "v_resummarize";
    html += busyHtml(key) + '<div class="karte-fuss links"><button type="button" class="knopf klein ki" data-act="v-process" data-id="' + e.id + '"' +
      (state.busy[key] ? " disabled" : "") + ">✦ " + esc(tr(label)) + "</button></div>";
    return html;
  }
  // Zeitmarken [m:ss] werden zu Sprungknöpfen, wenn ein Player offen ist
  function transcriptHtml(text, id) {
    return esc(text).split(/\n{2,}/).map(function (para) {
      var m = para.match(/^\[(\d+(?::\d{2}){1,2})\]\s*(.*)$/);
      if (!m) return "<p>" + para + "</p>";
      var parts = m[1].split(":").map(Number), sec = 0;
      parts.forEach(function (n) { sec = sec * 60 + n; });
      var mark = id != null ? '<button type="button" class="zeitmarke" data-act="seek" data-id="' + id + '" data-t="' + sec + '">' + m[1] + "</button>" : '<span class="zeitmarke">' + m[1] + "</span>";
      return "<p>" + mark + " " + m[2] + "</p>";
    }).join("");
  }
  function processVideo(id) {
    return aiCall("vid" + id, "/api/videos/" + id + "/process", { lang: state.lang }).then(function (e) { replaceEntry(e); render(); return e; });
  }
  function processAll() {
    var list = state.entries.filter(function (e) { return e.kind === "video" && videoPending(e); });
    var chain = Promise.resolve();
    list.forEach(function (e) { chain = chain.then(function () { return processVideo(e.id).catch(function () {}); }); });
    state.busy.all = true; render();
    chain.then(function () { state.busy.all = false; render(); });
  }

  function renderVideos() {
    var items = byKind("video").filter(function (e) {
      return (!state.vCat || (e.data.category || "sonstiges") === state.vCat) && (!state.vLang || e.data.vlang === state.vLang);
    });
    var all = state.entries.filter(function (e) { return e.kind === "video"; });
    var usedCats = cats().filter(function (c) { return all.some(function (e) { return (e.data.category || "sonstiges") === c.key; }); });
    var usedLangs = VLANGS.filter(function (l) { return all.some(function (e) { return e.data.vlang === l; }); });
    var cnt = function (f) { return all.filter(f).length; };
    var chips = all.length ? '<div class="chips"><button type="button" data-vcat=""' + (!state.vCat ? ' aria-pressed="true"' : "") + ">" + esc(tr("all")) + " " + all.length + "</button>" +
      usedCats.map(function (c) {
        return '<button type="button" data-vcat="' + c.key + '"' + (state.vCat === c.key ? ' aria-pressed="true"' : "") + ">" + esc(c.n[state.lang]) + ' <span class="zahl">' +
          cnt(function (e) { return (e.data.category || "sonstiges") === c.key; }) + "</span></button>";
      }).join("") + "</div>" +
      '<div class="chips klein"><button type="button" data-vlang=""' + (!state.vLang ? ' aria-pressed="true"' : "") + ">" + esc(tr("all_langs")) + "</button>" +
      usedLangs.map(function (l) {
        return '<button type="button" data-vlang="' + l + '"' + (state.vLang === l ? ' aria-pressed="true"' : "") + ">" + (l === "other" ? "…" : l.toUpperCase()) + "</button>";
      }).join("") + "</div>" : "";
    var body;
    if (!all.length) body = '<div class="leer">' + esc(tr("empty_videos")) + '<div><button type="button" class="knopf primaer" data-act="new" data-kind="video">' + esc(tr("new_video")) + "</button></div></div>";
    else if (!items.length) body = '<div class="leer">' + esc(tr("empty_search")) + "</div>";
    else {
      body = cats().map(function (c) {
        if (c.key === "sonstiges") c = { key: "sonstiges", n: c.n };
        var known = cats().map(function (x) { return x.key; });
        var inCat = items.filter(function (e) { var k = e.data.category || "sonstiges"; if (known.indexOf(k) === -1) k = "sonstiges"; return k === c.key; })
          .sort(function (a, b) { return b.id - a.id; });
        if (!inCat.length) return "";
        return '<div class="video-gruppe"><h3 class="gruppe-titel">' + esc(c.n[state.lang]) + ' <span class="zahl">' + inCat.length + "</span></h3>" +
          '<div class="video-raster">' + inCat.map(videoCard).join("") + "</div></div>";
      }).join("");
    }
    return '<section class="abschnitt"><div class="abschnitt-kopf"><div><h2>' + esc(tr("tab_videos")) + "</h2><p>" + esc(tr("videos_sub")) + "</p></div>" +
      '<div class="knoepfe">' + (all.some(videoPending) ? '<button type="button" class="knopf ki" data-act="v-all"' + (state.busy.all ? " disabled" : "") + ">✦ " + esc(tr("v_all")) +
        " (" + all.filter(videoPending).length + ")</button>" : "") +
      '<button type="button" class="knopf" data-act="new" data-kind="video">' + esc(tr("new_video")) + "</button></div></div>" + chips + body + "</section>";
  }
  function openPlayer(e) {
    var d = e.data;
    $("spieler").innerHTML = '<div class="spieler-fenster"><div class="spieler-kopf"><h2>' + esc(L(d.title)) + '</h2><button type="button" class="x" data-act="player-close" aria-label="' + esc(tr("close")) + '">×</button></div>' +
      '<div class="spieler-bild"><iframe src="https://www.youtube-nocookie.com/embed/' + encodeURIComponent(d.yt_id) + '?autoplay=1&rel=0&hl=' + state.lang + '" title="' + esc(L(d.title)) + '" ' +
      'allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe></div>' +
      '<div class="spieler-fuss"><span class="hinweis">' + esc(d.channel || "") + '</span><a href="' + esc(safeUrl(d.url)) + '" target="_blank" rel="noopener noreferrer">' + esc(tr("open_yt")) + "</a></div>" +
      (L(d.note) ? '<div class="spieler-notiz">' + md(L(d.note)) + "</div>" : "") +
      (d.summary ? '<div class="spieler-notiz"><div class="eyebrow">✦ ' + esc(tr("v_summary")) + "</div>" + md(L(d.summary.text)) + "</div>" : "") +
      (hasTranscript(d) ? '<details class="spieler-notiz"><summary>' + esc(tr("v_transcript")) + '</summary><p class="hinweis">' + esc(tr("v_jump")) + '</p><div class="transkript lang">' +
        transcriptHtml(d.transcript.text, e.id) + "</div></details>" : "") + "</div>";
    $("spieler").hidden = false;
    document.body.style.overflow = "hidden";
  }
  function closePlayer() {
    $("spieler").hidden = true;
    $("spieler").innerHTML = "";
    document.body.style.overflow = "";
  }

  // ---------- Chat ----------
  function chatMsgHtml(m, i) {
    if (m.role === "user") return '<div class="nachricht du"><div class="blase">' + esc(m.text).replace(/\n/g, "<br>") + "</div></div>";
    return '<div class="nachricht ki-antwort"><div class="blase">' + md(m.text) + sourcesHtml(m.sources) +
      (m.partial ? '<p class="hinweis">' + esc(tr("c_partial")) + "</p>" : "") +
      '<div class="nachricht-fuss">' + (m.model ? '<span class="hinweis">' + esc(m.model) + "</span>" : "") +
      '<button type="button" class="knopf klein" data-act="c-copy" data-i="' + i + '">' + esc(tr("c_copy")) + "</button>" +
      '<button type="button" class="knopf klein" data-act="c-save" data-i="' + i + '">' + esc(tr("c_save")) + "</button></div></div></div>";
  }
  function streamHtml() {
    var st = state.stream;
    if (!st) return "";
    var status = st.error ? '<p class="ki-status fehler">' + esc(st.error) + "</p>"
      : !st.text ? '<p class="ki-status"><span class="spinner" aria-hidden="true"></span>' + esc(tr(st.search ? "c_searching" : "c_thinking")) + "</p>"
      : st.search ? '<p class="ki-status"><span class="spinner" aria-hidden="true"></span>' + esc(tr("c_searching")) + "</p>" : "";
    return '<div class="nachricht ki-antwort"><div class="blase" id="chatStrom">' + md(st.text) + status + "</div></div>";
  }
  function renderChat() {
    if (!hasKey()) return '<section class="abschnitt"><div class="abschnitt-kopf"><h2>' + esc(tr("tab_chat")) + "</h2></div>" + needKey() + "</section>";
    var list = state.chats || [];
    var cur = state.chat;
    var aside = '<aside class="chat-liste"><button type="button" class="knopf primaer" data-act="c-new"' + (state.stream ? " disabled" : "") + ">" + esc(tr("c_new")) + "</button>" +
      '<div class="eyebrow">' + esc(tr("c_list")) + "</div>" +
      list.map(function (c) {
        var active = cur && cur.id === c.id;
        if (state.chatConfirm === c.id) {
          return '<div class="chat-eintrag bestaetigen">' + esc(tr("c_del_q")) + ' <button type="button" class="knopf klein gefahr" data-act="c-del-yes" data-cid="' + c.id + '">' + esc(tr("yes_del")) +
            '</button><button type="button" class="knopf klein" data-act="c-del-no">' + esc(tr("cancel")) + "</button></div>";
        }
        return '<div class="chat-eintrag' + (active ? " aktiv" : "") + '"><button type="button" class="chat-titel" data-act="c-open" data-cid="' + c.id + '"' + (state.stream ? " disabled" : "") + ">" +
          esc(c.title || tr("c_untitled")) + "<small>" + fmtDate(c.updated) + "</small></button>" +
          '<button type="button" class="x klein" data-act="c-del" data-cid="' + c.id + '" aria-label="' + esc(tr("del")) + '">×</button></div>';
      }).join("") + "</aside>";
    var msgs = cur && cur.messages ? cur.messages : [];
    var verlauf = msgs.length || state.stream ? msgs.map(chatMsgHtml).join("") + streamHtml()
      : '<div class="chat-start"><h3>' + esc(tr("c_hello")) + '</h3><p class="hinweis">' + esc(tr("c_hello_sub")) + '</p><div class="chat-vorschlaege">' +
        ["c_s1", "c_s2", "c_s3", "c_s4", "c_s5"].map(function (k) { return '<button type="button" class="knopf" data-act="c-suggest" data-k="' + k + '">' + esc(tr(k)) + "</button>"; }).join("") + "</div></div>";
    var eingabe = '<form class="chat-eingabe" id="chatForm"><textarea id="chatText" rows="2" placeholder="' + esc(tr("c_ph")) + '">' + esc(state.chatIn) + "</textarea>" +
      '<div class="ki-optionen"><label class="haken"><input type="checkbox" data-c-opt="mappe"' + (state.chatOpts.mappe ? " checked" : "") + "> " + esc(tr("c_mappe")) + "</label>" +
      '<label class="haken"><input type="checkbox" data-c-opt="web"' + (state.chatOpts.web ? " checked" : "") + "> " + esc(tr("c_web")) + "</label>" +
      (state.stream ? '<button type="button" class="knopf gefahr" data-act="c-stop">■ ' + esc(tr("c_stop")) + "</button>"
        : '<button type="submit" class="knopf primaer">' + esc(tr("c_send")) + " ↵</button>") + "</div></form>";
    return '<section class="abschnitt chat">' + aside + '<div class="chat-haupt"><div class="chat-verlauf" id="chatVerlauf">' + verlauf + "</div>" + eingabe +
      '<p class="hinweis">' + esc(tr("ai_hint_disclaimer")) + "</p></div></section>";
  }
  function afterChatRender() {
    var v = $("chatVerlauf");
    if (v) v.scrollTop = v.scrollHeight;
    if (hasKey() && state.chats === null) loadChats(true);
  }
  function loadChats(openLatest) {
    state.chats = state.chats || [];
    return api("GET", "/api/chats").then(function (list) {
      state.chats = list;
      if (openLatest && !state.chat && list.length) return openChat(list[0].id);
      render();
    }).catch(function () {});
  }
  function openChat(id) {
    return api("GET", "/api/chats/" + id).then(function (c) { state.chat = c; state.stream = null; render(); });
  }
  function updateStream() {
    var el = $("chatStrom");
    if (!el) { render(); return; }
    el.outerHTML = streamHtml().replace(/^<div class="nachricht ki-antwort">/, "").replace(/<\/div>$/, "");
    var v = $("chatVerlauf");
    if (v && v.scrollHeight - v.scrollTop - v.clientHeight < 160) v.scrollTop = v.scrollHeight;
  }
  function sendChat(text) {
    text = (text || "").trim();
    if (!text || state.stream) return;
    var start = state.chat ? Promise.resolve(state.chat) : api("POST", "/api/chats").then(function (c) { state.chat = c; return c; });
    start.then(function (c) {
      c.messages = (c.messages || []).concat([{ role: "user", text: text }]);
      state.chatIn = "";
      state.stream = { text: "", search: false, error: "" };
      render();
      var ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
      state.chatAbort = ctrl;
      return fetch("/api/chats/" + c.id + "/send", {
        method: "POST", headers: { "Content-Type": "application/json" }, credentials: "same-origin", signal: ctrl ? ctrl.signal : undefined,
        body: JSON.stringify({ text: text, lang: state.lang, web: state.chatOpts.web, mappe: state.chatOpts.mappe })
      }).then(function (r) {
        if (!r.ok) return errText(r, tr("err_save"));
        var handle = function (block) {
          block.split("\n").forEach(function (line) {
            if (line.indexOf("data:") !== 0) return;
            var ev;
            try { ev = JSON.parse(line.slice(5)); } catch (e) { return; }
            if (ev.t === "delta") { state.stream.text += ev.d; state.stream.search = false; }
            else if (ev.t === "status") state.stream.search = true;
            else if (ev.t === "error") state.stream.error = ev.m;
            else if (ev.t === "done") state.stream.done = ev.message;
          });
          updateStream();
        };
        if (!r.body || !r.body.getReader || typeof TextDecoder === "undefined") return r.text().then(handle);
        var reader = r.body.getReader(), dec = new TextDecoder(), buf = "";
        var pump = function () {
          return reader.read().then(function (x) {
            if (x.done) { if (buf) handle(buf); return; }
            buf += dec.decode(x.value, { stream: true });
            var cut = buf.lastIndexOf("\n\n");
            if (cut !== -1) { handle(buf.slice(0, cut)); buf = buf.slice(cut + 2); }
            return pump();
          });
        };
        return pump();
      });
    }).then(function () { finishStream(); }, function (err) {
      if (err && err.name === "AbortError") { finishStream(); return; }
      var msg = err && err.message && !/fetch|network|load failed/i.test(err.message) ? err.message : tr("c_net");
      if (!state.stream) {
        // Gescheitert, bevor die Antwort überhaupt startete (z. B. Gespräch nicht anlegbar) — nie stumm bleiben
        state.chatIn = text;
        render();
        toast(msg);
        return;
      }
      state.stream.error = msg;
      finishStream();
    });
  }
  function finishStream() {
    var st = state.stream;
    state.chatAbort = null;
    if (!st) return;
    if (st.done && !st.error) {
      state.chat.messages.push(st.done);
      state.stream = null;
      render();
      loadChats(false);
    } else {
      // Fehler oder Stopp: Stand vom Server holen (dort ist auch eine abgebrochene Antwort gespeichert)
      var err = st.error;
      setTimeout(function () {
        openChat(state.chat.id).then(function () {
          if (err) { state.stream = { text: "", error: err }; render(); state.stream = null; }
          loadChats(false);
        });
      }, 400);
    }
  }
  function saveChatNote(i) {
    var msgs = state.chat.messages, m = msgs[i];
    var q = "";
    for (var j = i - 1; j >= 0; j--) if (msgs[j].role === "user") { q = msgs[j].text; break; }
    var title = (q || state.chat.title || "Chat").slice(0, 120);
    api("POST", "/api/translate", { source: state.lang, fields: { title: title, body: m.text } }).catch(function () { return { fields: {} }; })
      .then(function (r) {
        var f = r.fields || {};
        var one = function (t) { var o = {}; LANGS.forEach(function (l) { o[l] = t; }); return o; };
        return api("POST", "/api/entries", { kind: "research", data: {
          title: f.title || one(title), body: f.body || one(m.text), sources: m.sources || [],
          source: m.sources && m.sources[0] ? m.sources[0].url : "", date: today(), question: q, ai_model: m.model || "" } });
      }).then(function (e) { replaceEntry(e); toast(tr("c_saved")); }, function () { toast(tr("err_save")); });
  }

  function studyKey(d) { return d.nct || (d.pmid ? "pmid:" + d.pmid : ""); }
  function savedStudyKeys() {
    var k = {};
    state.entries.forEach(function (e) { if (e.kind === "study") k[studyKey(e.data)] = e.id; });
    return k;
  }
  function statusChip(d) {
    if (!d.status) return "";
    var offen = d.status === "RECRUITING" || d.status === "NOT_YET_RECRUITING";
    return '<span class="chip ' + (offen ? "gruen" : "grau") + '">' + esc(d.status_de || d.status) + "</span>";
  }
  function studyMeta(d) {
    var bits = d.source === "trials"
      ? [d.nct, d.phase, d.enrollment ? d.enrollment + " " + tr("st_participants") : "", d.sponsor, (d.countries || []).slice(0, 6).join(", ") + ((d.countries || []).length > 6 ? " …" : "")]
      : [d.authors, d.journal, d.year, d.pmid ? "PMID " + d.pmid : ""];
    return bits.filter(Boolean).map(esc).join(" · ");
  }
  function studyLinks(d) {
    var l = [];
    if (d.pmid) l.push('<a href="https://pubmed.ncbi.nlm.nih.gov/' + encodeURIComponent(d.pmid) + '/" target="_blank" rel="noopener noreferrer">PubMed ↗</a>');
    if (d.doi) l.push('<a href="https://doi.org/' + esc(d.doi) + '" target="_blank" rel="noopener noreferrer">DOI ↗</a>');
    if (d.nct) l.push('<a href="https://clinicaltrials.gov/study/' + encodeURIComponent(d.nct) + '" target="_blank" rel="noopener noreferrer">ClinicalTrials.gov ↗</a>');
    if (!l.length && safeUrl(d.url)) l.push('<a href="' + esc(d.url) + '" target="_blank" rel="noopener noreferrer">' + esc(tr("open_link")) + "</a>");
    return l.length ? '<div class="studien-links">' + l.join("") + "</div>" : "";
  }
  function studyCard(e) {
    var d = e.data, key = "st" + e.id, sm = d.summary;
    var typ = d.source === "trials" ? (d.phase || d.type) : d.type;
    var html = '<article class="karte studie"><div class="meta">' + (typ ? '<span class="chip">' + esc(typ) + "</span>" : "") + statusChip(d) +
      (sm && L(sm.evidence) ? '<span class="chip ki" title="' + esc(tr("st_evidence")) + '">◆ ' + esc(L(sm.evidence)) + "</span>" : "") + "</div>" +
      "<h3>" + hl(L(d.title) || d.url || "") + "</h3>" + '<div class="meta studie-meta">' + studyMeta(d) + "</div>" + studyLinks(d);
    if (sm) {
      html += '<p class="video-kurz">✦ ' + hl(L(sm.short)) + "</p>" +
        '<details class="video-details"><summary>' + esc(tr("st_assessment")) + "</summary>" + md(L(sm.text)) +
        '<p class="hinweis">' + esc(tr("ai_hint_disclaimer")) + " (" + esc(sm.model || "") + ")</p></details>";
    }
    if (d.abstract) html += '<details class="video-details"><summary>' + esc(tr(d.source === "trials" ? "st_summary_reg" : "st_abstract")) + '</summary><div class="transkript">' +
      esc(d.abstract).split(/\n{2,}/).map(function (x) { return "<p>" + x + "</p>"; }).join("") + "</div></details>";
    if (d.eligibility) html += '<details class="video-details"><summary>' + esc(tr("st_criteria")) + '</summary><div class="transkript">' +
      esc(d.eligibility).split(/\n+/).map(function (x) { return "<p>" + x + "</p>"; }).join("") + "</div></details>";
    if (d.source === "trials") html += '<details class="video-details"><summary>' + esc(tr("st_sites")) + " (" + (d.locations || []).length + ')</summary><div class="transkript">' +
      ((d.locations || []).length ? (d.locations || []).map(function (o) {
        return "<p><b>" + esc(o.city) + "</b>, " + esc(o.country) + " — " + esc(o.facility) + (o.status ? ' <span class="hinweis">' + esc(o.status.toLowerCase().replace(/_/g, " ")) + "</span>" : "") + "</p>";
      }).join("") : "<p>" + esc(tr("st_no_sites")) + "</p>") + "</div></details>";
    html += txt(d.note) + txt(d.body) + filesHtml(e) + busyHtml(key);
    if (hasKey() || (state.settings && state.settings.claude_translate)) {
      html += '<div class="karte-fuss links"><button type="button" class="knopf klein ki" data-act="st-assess" data-id="' + e.id + '"' + (state.busy[key] ? " disabled" : "") +
        ">✦ " + esc(tr(sm ? "st_reassess" : "st_assess")) + "</button></div>";
    }
    return html + cardFoot(e) + "</article>";
  }
  function renderStudies() {
    var st = state.st, saved = savedStudyKeys();
    var trials = st.source === "trials";
    var form = '<form class="studien-suche" id="stForm"><div class="quelle-wahl" role="radiogroup">' +
      ["pubmed", "trials"].map(function (k) {
        return '<label class="' + (st.source === k ? "aktiv" : "") + '"><input type="radio" name="stsrc" value="' + k + '"' + (st.source === k ? " checked" : "") + "> " + esc(tr("st_src_" + k)) + "</label>";
      }).join("") + "</div>" +
      '<div class="ki-zeile ohne-abstand"><input type="search" id="stQ" placeholder="' + esc(tr("st_search_ph")) + '" value="' + esc(st.q) + '">' +
      '<button type="submit" class="knopf primaer"' + (state.busy.stsearch ? " disabled" : "") + ">" + esc(tr("st_search")) + "</button></div>" +
      '<div class="ki-optionen">' + (trials
        ? '<label class="haken">' + esc(tr("st_land")) + ' <select id="stLand">' + [["", tr("st_land_all")], ["Germany", "Deutschland"], ["Poland", "Polska"], ["Austria", "Österreich"], ["Switzerland", "Schweiz"]].map(function (o) {
            return '<option value="' + o[0] + '"' + (st.land === o[0] ? " selected" : "") + ">" + esc(o[1]) + "</option>";
          }).join("") + "</select></label>" +
          '<label class="haken"><input type="checkbox" id="stOpen"' + (st.open ? " checked" : "") + "> " + esc(tr("st_open")) + "</label>"
        : '<label class="haken"><input type="checkbox" id="stRecent"' + (st.recent ? " checked" : "") + "> " + esc(tr("st_recent")) + "</label>") + "</div></form>" +
      '<form class="ki-zeile" id="stImpForm"><input type="text" id="stImp" placeholder="' + esc(tr("st_import_ph")) + '" value="' + esc(st.imp) + '">' +
      '<button type="submit" class="knopf"' + (state.busy.stimp ? " disabled" : "") + ">" + esc(tr("st_import")) + "</button></form>" +
      busyHtml("stsearch") + busyHtml("stimp");
    var results = "";
    if (st.results) {
      results = '<div class="studien-treffer"><div class="eyebrow">' + st.total + " " + esc(tr("st_hits")) + "</div>" + (st.results.length ? st.results.map(function (r) {
        var k = studyKey(r), drin = saved[k];
        return '<div class="treffer"><div class="treffer-text"><div class="meta">' + (r.type || r.phase ? '<span class="chip">' + esc(r.source === "trials" ? (r.phase || r.type) : r.type) + "</span>" : "") +
          statusChip(r) + "</div><b>" + esc(r.title) + '</b><div class="meta studie-meta">' + studyMeta(r) + "</div></div>" +
          '<div class="treffer-knoepfe"><a class="knopf klein" href="' + esc(r.url) + '" target="_blank" rel="noopener noreferrer">↗</a>' +
          (drin ? '<span class="hinweis">' + esc(tr("st_taken")) + "</span>"
            : '<button type="button" class="knopf klein primaer" data-act="st-take" data-k="' + esc(r.pmid || r.nct) + '" data-src="' + r.source + '"' + (state.busy["take" + k] ? " disabled" : "") + ">" + esc(tr("st_take")) + "</button>") +
          "</div></div>";
      }).join("") : '<div class="leer">' + esc(tr("empty_search")) + "</div>") + "</div>";
    }
    var all = byKind("study");
    var group = function (titleKey, list) {
      return list.length ? '<div class="video-gruppe"><h3 class="gruppe-titel">' + esc(tr(titleKey)) + ' <span class="zahl">' + list.length + "</span></h3>" +
        '<div class="liste">' + list.map(studyCard).join("") + "</div></div>" : "";
    };
    var byYear = function (a, b) { return (b.data.year || "").localeCompare(a.data.year || "") || b.id - a.id; };
    var saved_html = all.length
      ? group("st_saved_trials", all.filter(function (e) { return e.data.source === "trials"; }).sort(byYear)) +
        group("st_saved_pub", all.filter(function (e) { return e.data.source === "pubmed"; }).sort(byYear)) +
        group("st_saved_other", all.filter(function (e) { return !e.data.source; }).sort(byYear))
      : '<div class="leer">' + esc(tr("st_empty")) + "</div>";
    return '<section class="abschnitt"><div class="abschnitt-kopf"><div><h2>' + esc(tr("tab_studies")) + "</h2><p>" + esc(tr("st_sub")) + "</p></div></div>" +
      '<div class="karte studien-suchkarte">' + form + results + "</div></section>" +
      '<section class="abschnitt">' + saved_html + "</section>";
  }
  function stSearch() {
    var st = state.st;
    if (!st.q.trim()) return;
    var qs = "?q=" + encodeURIComponent(st.q.trim()) + "&source=" + st.source + "&limit=15" +
      (st.source === "trials" ? "&land=" + encodeURIComponent(st.land) + "&offen=" + st.open : "&neu=" + st.recent);
    state.busy.stsearch = true; state.aiErr.stsearch = ""; render();
    fetch("/api/studies/search" + qs, { credentials: "same-origin" })
      .then(function (r) { return r.ok ? r.json() : errText(r, tr("err_load")); })
      .then(function (d) { state.busy.stsearch = false; st.results = d.treffer; st.total = d.anzahl; render(); },
        function (err) { state.busy.stsearch = false; state.aiErr.stsearch = err.message; render(); });
  }
  function stImport(body, busyKey) {
    body.topic = state.topic;
    return aiCall(busyKey, "/api/studies/import", body).then(function (e) { replaceEntry(e); render(); toast(tr("saved")); return e; });
  }

  // ---------- Markieren & erklären lassen (überall im Inhalt) ----------
  function selectionInfo() {
    var sel = window.getSelection ? window.getSelection() : null;
    if (!sel || sel.isCollapsed || !sel.rangeCount) return null;
    var text = sel.toString().replace(/\s+/g, " ").replace(/^[\s.,;:!?„“"'()\[\]]+|[\s.,;:!?„“"'()\[\]]+$/g, "");
    if (text.length < 2 || text.length > 80 || text.split(" ").length > 6) return null;
    var node = sel.anchorNode;
    var el = node && (node.nodeType === 1 ? node : node.parentElement);
    if (!el || !el.closest || !el.closest("#inhalt, #spieler")) return null;
    if (el.closest("input, textarea, select, button, .ki-zeile, .chat-eingabe")) return null;
    var block = el.closest("p, li, td, h3, h4, .blase, .transkript, .karte") || el;
    var ctx = (block.textContent || "").replace(/\s+/g, " ").trim();
    var pos = ctx.indexOf(text);
    if (ctx.length > 600) ctx = ctx.slice(Math.max(0, pos - 280), Math.max(0, pos - 280) + 600);
    return { term: text, context: ctx, rect: sel.getRangeAt(0).getBoundingClientRect() };
  }
  var markTimer = null;
  function checkSelection() {
    clearTimeout(markTimer);
    markTimer = setTimeout(function () {
      var info = selectionInfo(), btn = $("markKnopf");
      if (!info || !info.rect || (!info.rect.width && !info.rect.height)) { btn.hidden = true; return; }
      state.markInfo = info;
      btn.innerHTML = "✦ " + esc(tr("x_btn")) + ' <span>„' + esc(info.term.length > 28 ? info.term.slice(0, 27) + "…" : info.term) + "“</span>";
      btn.hidden = false;
      var bw = btn.offsetWidth, bh = btn.offsetHeight;
      // Unter die Markierung, damit das Menü des Telefons darüber frei bleibt; am unteren Rand darüber
      var top = info.rect.bottom + 8;
      if (top + bh > window.innerHeight - 8) top = info.rect.top - bh - 8;
      var left = Math.min(Math.max(8, info.rect.left + info.rect.width / 2 - bw / 2), window.innerWidth - bw - 8);
      btn.style.top = Math.round(top) + "px";
      btn.style.left = Math.round(left) + "px";
    }, 180);
  }
  function normTerm(t) { return String(t || "").toLowerCase().replace(/\s*\(.*\)\s*/g, " ").replace(/[^a-z0-9äöüßąćęłńóśźż+\-\/ ]/gi, "").replace(/\s+/g, " ").trim(); }
  function findGloss(term) {
    var n = normTerm(term);
    return state.entries.filter(function (e) {
      if (e.kind !== "glossary") return false;
      var t = e.data.title || {};
      return LANGS.some(function (l) {
        var v = typeof t === "string" ? t : t[l];
        if (!v) return false;
        var nv = normTerm(v);
        // „HER2“ findet auch „HER2-low“ nicht, aber „Ki-67 (Proliferation)“ findet „Ki-67“; Abkürzung in Klammern zählt mit
        var abk = (String(v).match(/\(([^)]+)\)/) || [])[1];
        return nv === n || (abk && normTerm(abk) === n) || nv.split(" / ").indexOf(n) !== -1;
      });
    })[0] || null;
  }
  function explain(info) {
    $("markKnopf").hidden = true;
    var have = findGloss(info.term);
    if (have) { state.explain = { term: info.term, status: "exists", entry: have }; renderExplain(); return; }
    if (!hasKey()) { state.explain = { term: info.term, status: "nokey" }; renderExplain(); return; }
    var job = { term: info.term, status: "loading" };
    state.explain = job;
    renderExplain();
    // Nie endlos drehen: nach 2 Minuten oder bei einer unerwarteten Antwort eine Meldung zeigen
    var ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 120000);
    fetch("/api/ai/glossary", { method: "POST", headers: { "Content-Type": "application/json" }, credentials: "same-origin",
      signal: ctrl ? ctrl.signal : undefined,
      body: JSON.stringify({ term: info.term, context: info.context, lang: state.lang, topic: state.topic }) })
      .then(function (r) { return r.ok ? r.json() : errText(r, tr("err_save")); })
      .then(function (d) {
        clearTimeout(timer);
        if (!d || !d.data || !d.data.body) throw new Error(tr("x_bad"));
        if (state.explain === job) { job.status = "done"; job.draft = d; renderExplain(); }
      })
      .catch(function (err) {
        clearTimeout(timer);
        if (state.explain !== job) return;
        job.status = "error";
        job.error = err && err.name === "AbortError" ? tr("x_timeout") : (err && err.message) || tr("x_bad");
        renderExplain();
      });
  }
  function renderExplain() {
    var x = state.explain, box = $("erklaerung");
    if (!x) { box.hidden = true; box.innerHTML = ""; return; }
    var title = x.term, body = "", foot = "";
    if (x.status === "loading") body = '<div class="ki-status"><span class="spinner" aria-hidden="true"></span>' + esc(tr("x_loading")) + "</div>";
    else if (x.status === "error") body = '<div class="ki-status fehler">' + esc(x.error) + "</div>";
    else if (x.status === "nokey") body = needKey();
    else {
      var d = x.status === "done" ? x.draft.data : x.entry.data;
      title = L(d.title) || x.term;
      body = (x.status === "exists" ? '<div class="eyebrow">✓ ' + esc(tr("x_exists")) + "</div>" : "") + md(L(d.body)) +
        ((d.tags || []).length ? '<div class="meta">' + d.tags.map(function (t) { return '<span class="chip">' + esc(t) + "</span>"; }).join("") + "</div>" : "") +
        (x.status === "done" ? '<p class="hinweis">' + esc(tr("ai_hint_disclaimer")) + "</p>" : "");
      foot = x.status === "done"
        ? '<button type="button" class="knopf klein primaer" data-act="x-save">' + esc(tr("x_save")) + "</button>"
        : (sectionOn("glossary") ? '<button type="button" class="knopf klein" data-act="x-open">' + esc(tr("x_open")) + "</button>" : "");
    }
    box.innerHTML = '<div class="erklaer-kopf"><h3>✦ ' + esc(title) + '</h3><button type="button" class="x" data-act="x-close" aria-label="' + esc(tr("close")) + '">×</button></div>' +
      '<div class="erklaer-rumpf">' + body + "</div>" + (foot ? '<div class="erklaer-fuss">' + foot + "</div>" : "");
    box.hidden = false;
  }

  function renderSettings() {
    var st = state.settings || {};
    var models = state.models || [];
    function opts(cur) {
      var list = models.slice();
      if (cur && list.indexOf(cur) === -1) list.unshift(cur);
      return list.map(function (m) { return '<option value="' + esc(m) + '"' + (m === cur ? " selected" : "") + ">" + esc(m) + "</option>"; }).join("");
    }
    var removeRow = state.confirmKey
      ? '<div class="bestaetigen">' + esc(tr("s_remove_q")) + ' <button type="button" class="knopf klein gefahr" data-act="key-remove-yes">' + esc(tr("yes_del")) +
        '</button> <button type="button" class="knopf klein" data-act="key-remove-no">' + esc(tr("cancel")) + "</button></div>"
      : "";
    return '<section class="abschnitt einstellungen"><div class="abschnitt-kopf"><h2>' + esc(tr("tab_settings")) + "</h2></div>" +
      '<div class="karte"><h3>' + esc(tr("s_openai")) + '</h3><p class="hinweis">' + esc(tr("s_openai_sub")) + "</p>" +
      '<p class="schluessel-status ' + (st.openai_set ? "an" : "aus") + '">' + (st.openai_set ? "● " + esc(tr("s_status_set")) + ' <code>' + esc(st.openai_hint) + "</code>" : "○ " + esc(tr("s_status_none"))) + "</p>" +
      '<form id="keyForm" class="ki-zeile" autocomplete="off"><input type="password" id="s-key" placeholder="' + esc(tr("s_new_key")) + ' (sk-…)" autocomplete="new-password" spellcheck="false">' +
      '<button type="submit" class="knopf primaer">' + esc(tr("s_save_key")) + "</button></form>" +
      (st.openai_set ? '<div class="knoepfe links"><button type="button" class="knopf" data-act="key-test"' + (state.busy.test ? " disabled" : "") + ">" + esc(tr("s_test")) + "</button>" +
        '<button type="button" class="knopf gefahr" data-act="key-remove">' + esc(tr("s_remove")) + "</button></div>" : "") +
      removeRow + busyHtml("test") + (state.testOk ? '<div class="ki-status ok">✓ ' + esc(tr("s_test_ok")) + " · " + models.length + " " + esc(tr("s_models")) + "</div>" : "") + "</div>" +
      '<div class="karte"><h3>' + esc(tr("s_trans")) + '</h3><p class="hinweis">' + esc(tr("s_trans_sub")) + " " + esc(tr("s_summary_via")) + "</p>" +
      '<p class="schluessel-status ' + (st.transcript_set ? "an" : "aus") + '">' + (st.transcript_set ? "● " + esc(tr("s_status_set")) + " <code>" + esc(st.transcript_hint) + "</code>" : "○ " + esc(tr("s_status_none"))) + "</p>" +
      '<form id="transForm" class="ki-zeile" autocomplete="off"><input type="password" id="s-tkey" placeholder="' + esc(tr("s_trans_new")) + '" autocomplete="new-password" spellcheck="false">' +
      '<button type="submit" class="knopf primaer">' + esc(tr("s_save_key")) + "</button></form>" +
      (st.transcript_set ? '<div class="knoepfe links"><button type="button" class="knopf gefahr" data-act="tkey-remove">' + esc(tr("s_remove")) + "</button></div>" : "") + "</div>" +
      '<div class="karte"><h3>' + esc(tr("s_models")) + "</h3>" +
      '<div class="fenster-rumpf flach"><label>' + esc(tr("s_model")) + '<select id="s-model">' + opts(st.model) + "</select></label>" +
      "<label>" + esc(tr("s_model_fast")) + '<select id="s-model-fast">' + opts(st.model_fast) + "</select></label>" +
      '<label class="haken"><input type="checkbox" id="s-web"' + (st.web_search ? " checked" : "") + "> " + esc(tr("s_web")) + "</label>" +
      '<span class="hinweis">' + esc(tr("s_models_hint")) + "</span></div>" +
      '<div class="karte-fuss"><button type="button" class="knopf primaer" data-act="settings-save">' + esc(tr("s_save")) + "</button></div></div>" +
      mcpCard() +
      '<div class="karte"><h3>' + esc(tr("s_about")) + '</h3><p>' + esc(tr("s_about_text")) + "</p></div></section>";
  }

  function mcpCard() {
    if (!state.mcp) {
      api("GET", "/api/mcp-info").then(function (m) { state.mcp = m; if (state.tab === "settings") render(); }).catch(function () {});
      state.mcp = { loading: true };
    }
    var m = state.mcp;
    var row = function (k, label, url) {
      var shown = state.mcpShow[k];
      var masked = url ? url.replace(/\/mcp\/.+$/, "/mcp/" + "•".repeat(18)) : "…";
      var confirm = state.mcpConfirm === k
        ? '<div class="bestaetigen">' + esc(tr("m_rotate_q")) + ' <button type="button" class="knopf klein gefahr" data-act="mcp-rotate-yes" data-k="' + k + '">' + esc(tr("m_rotate")) +
          '</button><button type="button" class="knopf klein" data-act="mcp-rotate-no">' + esc(tr("cancel")) + "</button></div>" : "";
      return '<div class="mcp-zeile"><div class="eyebrow">' + esc(tr(label)) + '</div><code class="mcp-url">' + esc(shown ? url : masked) + "</code>" +
        '<div class="knoepfe links"><button type="button" class="knopf klein" data-act="mcp-show" data-k="' + k + '">' + esc(tr(shown ? "m_hide" : "m_show")) + "</button>" +
        '<button type="button" class="knopf klein" data-act="mcp-copy" data-k="' + k + '">' + esc(tr("c_copy")) + "</button>" +
        '<button type="button" class="knopf klein gefahr" data-act="mcp-rotate" data-k="' + k + '">' + esc(tr("m_rotate")) + "</button></div>" + confirm + "</div>";
    };
    return '<div class="karte"><h3>' + esc(tr("m_title")) + '</h3><p class="hinweis">' + esc(tr("m_sub")) + "</p>" +
      row("read", "m_read", m.read_url) + row("write", "m_write", m.write_url) + '<p class="hinweis">' + esc(tr("m_tools")) + "</p></div>";
  }

  function errText(r, fallback) {
    return r.json().then(function (j) { throw new Error(j.detail || fallback); }, function () { throw new Error(fallback + " (HTTP " + r.status + ")"); });
  }
  function aiCall(key, url, body) {
    body = body || {};
    if (body.topic == null) body.topic = state.topic;
    state.busy[key] = true; state.aiErr[key] = ""; render();
    return fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}), credentials: "same-origin" })
      .then(function (r) { return r.ok ? r.json() : errText(r, tr("err_save")); })
      .then(function (res) { state.busy[key] = false; return res; }, function (err) { state.busy[key] = false; state.aiErr[key] = err.message; render(); throw err; });
  }
  function replaceEntry(e) {
    var found = false;
    state.entries = state.entries.map(function (x) { if (x.id === e.id) { found = true; return e; } return x; });
    if (!found) state.entries.unshift(e);
  }

  // ---------- Formular ----------
  function inputHtml(name, type, value) {
    var id = "fld-" + name;
    if (type === "area") return '<textarea id="' + id + '" name="' + name + '">' + esc(value) + "</textarea>";
    var t = type === "date" ? "date" : type === "url" ? "url" : "text";
    return '<input id="' + id + '" name="' + name + '" type="' + t + '" value="' + esc(value) + '"' + (type === "url" ? ' placeholder="https://…"' : "") + ">";
  }

  function renderFileList() {
    var el = $("dateiListe");
    if (!el) return;
    var have = state.editing ? (state.editing.files || []) : [];
    var html = "";
    if (have.length) {
      html += '<div class="eyebrow">' + esc(tr("files_attached")) + "</div>" + have.map(function (f) {
        return '<div class="datei-zeile"><a href="/api/files/' + f.id + '" target="_blank" rel="noopener">' + esc(f.name) + "</a>" +
          '<span class="hinweis">' + fmtSize(f.size) + "</span>" +
          '<button type="button" class="knopf klein gefahr" data-act="file-del" data-file="' + f.id + '">' + esc(tr("remove")) + "</button></div>";
      }).join("");
    }
    if (state.pending.length) {
      html += '<div class="eyebrow">' + esc(tr("files_new")) + "</div>" + state.pending.map(function (f, i) {
        return '<div class="datei-zeile"><span>' + esc(f.name) + '</span><span class="hinweis">' + fmtSize(f.size) + "</span>" +
          '<button type="button" class="knopf klein" data-act="pending-del" data-i="' + i + '">' + esc(tr("remove")) + "</button></div>";
      }).join("");
    }
    el.innerHTML = html;
  }
  function addPending(list) {
    var skipped = [];
    Array.prototype.forEach.call(list || [], function (f) {
      if (!OK_EXT.test(f.name)) skipped.push(f.name + ": " + tr("bad_type"));
      else if (f.size > MAX_BYTES) skipped.push(f.name + ": " + tr("too_big"));
      else state.pending.push(f);
    });
    renderFileList();
    $("formStatus").textContent = skipped.join(" · ");
  }
  function uploadAll(entry) {
    var files = state.pending.slice();
    var current = entry;
    var failed = [];
    var chain = Promise.resolve();
    files.forEach(function (f, i) {
      chain = chain.then(function () {
        $("formStatus").textContent = tr("uploading") + " (" + (i + 1) + "/" + files.length + ")";
        var fd = new FormData();
        fd.append("datei", f, f.name);
        return fetch("/api/entries/" + entry.id + "/files", { method: "POST", body: fd, credentials: "same-origin" })
          .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
          .then(function (e) { current = e; })
          .catch(function () { failed.push(f.name); });
      });
    });
    return chain.then(function () { return { entry: current, failed: failed }; });
  }

  function openTopicForm(t) {
    state.editKind = "topic";
    state.editing = t || null;
    state.topicConfirm = false;
    var labels = { values: "tab_values", glossary: "tab_glossary", med: "tab_med", research: "tab_research", studies: "tab_studies", chat: "tab_chat", videos: "tab_videos" };
    var on = t ? t.sections : ["glossary", "research", "studies", "chat", "videos"];
    var kind = t ? t.kind : "general";
    var html = "<label>" + esc(tr("t_name")) + inputHtml("tname", "text", t ? (t.name[state.lang] || t.name.de) : "") + "</label>" +
      "<label>" + esc(tr("t_desc")) + inputHtml("tdesc", "text", t ? L(t.desc) : "") + "</label>" +
      '<fieldset class="auswahl"><legend>' + esc(tr("t_kind")) + "</legend>" +
      ["general", "health"].map(function (k) {
        return '<label class="haken"><input type="radio" name="tkind" value="' + k + '"' + (kind === k ? " checked" : "") + "> " + esc(tr("t_kind_" + k)) + "</label>";
      }).join("") + "</fieldset>" +
      '<fieldset class="auswahl spalten"><legend>' + esc(tr("t_sections")) + "</legend>" +
      ["values", "glossary", "med", "research", "studies", "chat", "videos"].map(function (k) {
        return '<label class="haken"><input type="checkbox" name="tsec" value="' + k + '"' + (on.indexOf(k) !== -1 ? " checked" : "") + "> " + esc(T[labels[k]][state.lang]) + "</label>";
      }).join("") + "</fieldset>" +
      "<label>" + esc(tr("t_context")) + '<input id="fld-tcontext" type="text" placeholder="' + esc(tr("t_context_ph")) + '" value="' + esc(t ? t.context || "" : "") + '"></label>' +
      (t ? '<div id="topicDel">' + topicDelHtml() + "</div>" : "");
    $("formFelder").innerHTML = html;
    $("formTitel").textContent = tr(t ? "t_edit" : "t_new_title");
    $("formStatus").textContent = "";
    $("formSpeichern").disabled = false;
    $("uebersetzen").parentNode.hidden = true;
    $("schleier").hidden = false;
    document.body.style.overflow = "hidden";
    if (window.innerWidth > 700) $("fld-tname").focus();
  }
  function topicDelHtml() {
    return state.topicConfirm
      ? '<div class="bestaetigen">' + esc(tr("t_delete_q")) + ' <button type="button" class="knopf klein gefahr" data-act="topic-del-yes">' + esc(tr("yes_del")) +
        '</button><button type="button" class="knopf klein" data-act="topic-del-no">' + esc(tr("cancel")) + "</button></div>"
      : '<button type="button" class="knopf klein gefahr" data-act="topic-del">' + esc(tr("t_delete")) + "</button>";
  }
  function submitTopic() {
    var sections = Array.prototype.filter.call(document.querySelectorAll('input[name="tsec"]'), function (x) { return x.checked; }).map(function (x) { return x.value; });
    var kindEl = document.querySelector('input[name="tkind"]:checked');
    if (!val("tname").trim()) { $("formStatus").textContent = tr("err_need"); return; }
    if (!sections.length) { $("formStatus").textContent = tr("t_need_section"); return; }
    var body = { name: val("tname").trim(), desc: val("tdesc").trim(), kind: kindEl ? kindEl.value : "general", sections: sections, context: val("tcontext").trim(), lang: state.lang };
    var t = state.editing;
    $("formSpeichern").disabled = true;
    $("formStatus").textContent = tr("saving");
    api(t ? "PUT" : "POST", t ? "/api/topics/" + t.id : "/api/topics", body).then(function (saved) {
      closeForm();
      return loadTopics().then(function () { if (!t) switchTopic(saved.id); else render(); toast(tr("t_saved")); });
    }, function () { $("formSpeichern").disabled = false; $("formStatus").textContent = tr("err_save"); });
  }

  function openForm(kind, entry, files) {
    $("uebersetzen").parentNode.hidden = false;
    state.pending = [];
    state.editKind = kind;
    state.editing = entry || null;
    var d = entry ? entry.data : {};
    var html = "";
    if (kind === "video") {
      state.preview = entry ? { yt_id: d.yt_id, thumb: d.thumb, url: d.url } : null;
      var catOpts = cats().map(function (c) {
        return '<option value="' + c.key + '"' + ((d.category || (entry ? "sonstiges" : (isHealth() ? "befund" : "grundlagen"))) === c.key ? " selected" : "") + ">" + esc(c.n[state.lang]) + "</option>";
      }).join("");
      var vl = d.vlang || state.lang;
      var langOpts = VLANGS.map(function (l) {
        return '<option value="' + l + '"' + (vl === l ? " selected" : "") + ">" + (l === "other" ? "…" : l.toUpperCase()) + "</option>";
      }).join("");
      html = "<label>" + esc(tr("f_url")) + '<div class="ki-zeile ohne-abstand"><input id="fld-url" name="url" type="url" inputmode="url" placeholder="https://www.youtube.com/watch?v=…" value="' + esc(d.url || "") + '">' +
        '<button type="button" class="knopf" data-act="preview">' + esc(tr("f_load_preview")) + "</button></div></label>" +
        '<div id="vorschauBox" class="vorschau-box">' + (entry ? '<span class="vorschau">' + thumbHtml(d) + "</span>" : "") + "</div>" +
        "<label>" + esc(tr("f_title")) + inputHtml("vtitle", "text", L(d.title)) + "</label>" +
        "<label>" + esc(tr("f_channel")) + inputHtml("channel", "text", d.channel || "") + "</label>" +
        '<div class="reihe"><label>' + esc(tr("f_category")) + '<select id="fld-category">' + catOpts + "</select></label>" +
        "<label>" + esc(tr("f_vlang")) + '<select id="fld-vlang">' + langOpts + "</select></label></div>" +
        "<label>" + esc(tr("f_vnote")) + inputHtml("note", "area", L(d.note)) + "</label>" +
        "<label>" + esc(tr("v_tr_field")) + '<textarea id="fld-transcript" rows="3">' + esc(d.transcript && d.transcript.source === "manual" ? d.transcript.text : "") + "</textarea></label>";
    } else if (kind === "value") {
      var isOther = d.param === "_other";
      if (!isHealth() && !entry) isOther = true;
      var presets = !isHealth() ? [] : PARAMS.filter(function (x) { return !x.onko || isOnko() || d.param === x.key; });
      if (!presets.length && !entry) isOther = true;
      var opts = presets.map(function (p) {
        return '<option value="' + p.key + '"' + (d.param === p.key ? " selected" : "") + ">" + esc(p.n[state.lang]) + "</option>";
      }).join("") + '<option value="_other"' + (isOther ? " selected" : "") + ">" + esc(tr("f_param_other")) + "</option>";
      var p0 = entry ? null : (presets[0] || { unit: "", low: null, high: null });
      html = '<label>' + esc(tr("f_param")) + '<select id="fld-param" name="param">' + opts + "</select></label>" +
        '<label id="wrap-paramLabel"' + (isOther ? "" : " hidden") + ">" + esc(tr("f_param_name")) + inputHtml("paramLabel", "text", d.paramLabel || "") + "</label>" +
        '<div class="reihe"><label>' + esc(tr("f_date")) + inputHtml("date", "date", d.date || today()) + "</label>" +
        "<label>" + esc(tr("f_value")) + '<input id="fld-value" name="value" type="text" inputmode="decimal" value="' + esc(d.value != null ? fmtNum(d.value) : "") + '"></label>' +
        "<label>" + esc(tr("f_unit")) + inputHtml("unit", "text", entry ? d.unit || "" : p0.unit) + "</label></div>" +
        '<div class="reihe"><label>' + esc(tr("f_low")) + '<input id="fld-low" name="low" type="text" inputmode="decimal" value="' + esc(entry ? (d.low != null ? fmtNum(d.low) : "") : (p0.low != null ? fmtNum(p0.low) : "")) + '"></label>' +
        "<label>" + esc(tr("f_high")) + '<input id="fld-high" name="high" type="text" inputmode="decimal" value="' + esc(entry ? (d.high != null ? fmtNum(d.high) : "") : (p0.high != null ? fmtNum(p0.high) : "")) + '"></label></div>' +
        '<span class="hinweis">' + esc(tr("f_ref_hint")) + "</span>" +
        "<label>" + esc(tr("f_assess")) + inputHtml("note", "area", L(d.note)) + "</label>";
    } else {
      KIND[kind].fields.forEach(function (f) {
        var v = d[f[0]];
        if (f[2] === "tags") v = Array.isArray(v) ? v.join(", ") : "";
        else if (f[2] === "date") v = v || today();
        else v = L(v);
        html += "<label>" + esc(tr(f[1])) + inputHtml(f[0], f[2], v) + "</label>";
      });
    }
    html += '<div class="datei-feld"><label>' + esc(tr("f_files")) +
      '<input id="fld-files" type="file" multiple accept=".pdf,application/pdf,image/*"></label>' +
      '<span class="hinweis">' + esc(tr("f_files_hint")) + '</span><div id="dateiListe"></div></div>';
    html += '<span class="hinweis">' + esc(tr("edit_lang")) + "</span>";
    $("formFelder").innerHTML = html;
    renderFileList();
    $("formTitel").textContent = (entry ? tr("edit") : tr("new_any").replace("+ ", "")) + " · " + tr("k_" + kind);
    $("formStatus").textContent = "";
    $("formSpeichern").disabled = false;
    $("schleier").hidden = false;
    document.body.style.overflow = "hidden";
    if (files) addPending(files);
    var first = $("formFelder").querySelector("input,textarea,select");
    if (first && window.innerWidth > 700) first.focus();
  }
  function loadPreview(then) {
    var url = val("url").trim();
    if (!url) { $("formStatus").textContent = tr("err_url"); return; }
    $("formStatus").textContent = tr("f_loading_preview");
    fetch("/api/link-preview", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ url: url }), credentials: "same-origin" })
      .then(function (r) { return r.ok ? r.json() : errText(r, tr("err_save")); })
      .then(function (pv) {
        if (!/^https?:\/\//i.test(url)) url = "https://" + url;
        pv.url = url;
        state.preview = pv;
        if (pv.title && !val("vtitle").trim()) $("fld-vtitle").value = pv.title;
        if (pv.channel && !val("channel").trim()) $("fld-channel").value = pv.channel;
        $("vorschauBox").innerHTML = '<span class="vorschau">' + thumbHtml(pv) + (pv.yt_id ? '<span class="play" aria-hidden="true"></span>' : "") + "</span>" +
          (pv.thumb ? "" : '<span class="hinweis">' + esc(tr("no_preview")) + "</span>");
        $("formStatus").textContent = "";
        if (then) then();
      }, function (err) { $("formStatus").textContent = err.message; });
  }

  function closeForm() {
    $("schleier").hidden = true;
    document.body.style.overflow = "";
    state.editing = null;
    state.pending = [];
  }
  function num(s) {
    if (s == null) return null;
    s = String(s).trim().replace(",", ".");
    if (s === "") return null;
    var n = Number(s);
    return isNaN(n) ? NaN : n;
  }
  function val(name) { var el = $("fld-" + name); return el ? el.value : ""; }

  function submitForm(ev) {
    ev.preventDefault();
    if (state.editKind === "topic") { submitTopic(); return; }
    var kind = state.editKind;
    var old = state.editing ? state.editing.data : {};
    var data = JSON.parse(JSON.stringify(old));
    var texts = {};      // i18n-Felder, die neu übersetzt werden
    var lang = state.lang;
    var setI18n = function (name, text) {
      var prev = old[name] && typeof old[name] === "object" ? old[name] : {};
      var changed = (prev[lang] || "") !== text;
      var copy = {}; LANGS.forEach(function (l) { copy[l] = prev[l] || ""; });
      copy[lang] = text;
      // Leere Fassungen in anderen Sprachen sofort mit dem Text füllen, Übersetzung ersetzt sie gleich
      LANGS.forEach(function (l) { if (!copy[l]) copy[l] = text; });
      if (!text) LANGS.forEach(function (l) { copy[l] = ""; });
      data[name] = copy;
      if (changed && text.trim()) texts[name] = text;
    };

    if (kind === "video") {
      var url = val("url").trim();
      if (!url) { $("formStatus").textContent = tr("err_url"); return; }
      if (!/^https?:\/\//i.test(url)) url = "https://" + url;
      var pv = state.preview && state.preview.url === url ? state.preview : null;
      if (!pv && !(state.editing && old.url === url)) {
        // Vorschau noch nicht geladen: erst holen, dann erneut speichern
        loadPreview(function () { submitForm({ preventDefault: function () {} }); });
        return;
      }
      if (pv) { data.yt_id = pv.yt_id || ""; data.thumb = pv.thumb || ""; data.embed = pv.embed !== false; }
      data.url = pv && pv.yt_id ? "https://www.youtube.com/watch?v=" + pv.yt_id : url;
      data.title = val("vtitle").trim() || (pv && pv.title) || url;
      data.channel = val("channel").trim();
      data.category = $("fld-category").value;
      data.vlang = $("fld-vlang").value;
      data.date = data.date || today();
      setI18n("note", val("note").trim());
      var manual = val("transcript").trim();
      if (manual && !(old.transcript && old.transcript.text === manual)) {
        data.transcript = { text: manual, lang: data.vlang, source: "manual", date: today() };
        delete data.summary;
      }
    } else if (kind === "value") {
      var v = num(val("value"));
      if (v == null || isNaN(v)) { $("formStatus").textContent = tr("err_num"); return; }
      var low = num(val("low")), high = num(val("high"));
      data.param = val("param");
      data.paramLabel = data.param === "_other" ? val("paramLabel").trim() : "";
      if (data.param === "_other" && !data.paramLabel) { $("formStatus").textContent = tr("err_need"); return; }
      data.date = val("date") || today();
      data.value = v;
      data.unit = val("unit").trim();
      data.low = low == null || isNaN(low) ? null : low;
      data.high = high == null || isNaN(high) ? null : high;
      setI18n("note", val("note").trim());
    } else {
      var fields = KIND[kind].fields;
      if (!val(fields[0][0]).trim() && state.pending.length && $("fld-title")) {
        $("fld-title").value = state.pending[0].name.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ");
      }
      if (!val(fields[0][0]).trim()) { $("formStatus").textContent = tr("err_need"); return; }
      fields.forEach(function (f) {
        var raw = val(f[0]);
        if (f[2] === "tags") data.tags = raw.split(",").map(function (s) { return s.trim(); }).filter(Boolean);
        else if (f[2] === "date" || f[2] === "url") data[f[0]] = raw.trim();
        else setI18n(f[0], raw.trim());
      });
    }
    delete data.seed;

    $("formSpeichern").disabled = true;
    var doTranslate = $("uebersetzen").checked && Object.keys(texts).length > 0;
    $("formStatus").textContent = doTranslate ? tr("translating") : tr("saving");
    var warn = false;
    var step = doTranslate
      ? api("POST", "/api/translate", { source: lang, fields: texts }).then(function (r) {
          Object.keys(r.fields || {}).forEach(function (k) { data[k] = r.fields[k]; });
          if (!r.translated) warn = true;
        }).catch(function () { warn = true; })
      : Promise.resolve();
    step.then(function () {
      return state.editing
        ? api("PUT", "/api/entries/" + state.editing.id, { kind: kind, data: data })
        : api("POST", "/api/entries", { kind: kind, data: data });
    }).then(function (saved) {
      if (!state.pending.length) return { entry: saved, failed: [] };
      return uploadAll(saved);
    }).then(function (res) {
      var saved = res.entry;
      if (res.failed.length) warn = tr("upload_fail") + ": " + res.failed.join(", ");
      state.entries = state.entries.filter(function (e) { return e.id !== saved.id; });
      state.entries.unshift(saved);
      if (kind === "video" && !old.summary && videoPending(saved)) processVideo(saved.id).catch(function () {});
      if (kind === "value") state.openParam = data.param === "_other" ? "_" + data.paramLabel.toLowerCase() : data.param;
      closeForm();
      var tab = KIND[kind].tab;
      if (state.tab !== tab && state.tab !== "home") state.tab = tab;
      render();
      toast(typeof warn === "string" ? warn : warn ? tr("trans_fail") : tr("saved"));
    }).catch(function () {
      $("formSpeichern").disabled = false;
      $("formStatus").textContent = tr("err_save");
    });
  }

  // ---------- Ereignisse ----------
  document.addEventListener("click", function (ev) {
    var b = ev.target.closest ? ev.target.closest("[data-tab],[data-lang],[data-act],[data-tag],[data-vcat],[data-vlang],[data-topic]") : null;
    if (!b) return;
    if (b.hasAttribute("data-lang")) {
      state.lang = b.getAttribute("data-lang"); save("lang", state.lang); render(); return;
    }
    if (b.hasAttribute("data-tab")) {
      state.tab = b.getAttribute("data-tab"); state.confirm = null; save("tab", state.tab); render(); window.scrollTo(0, 0); return;
    }
    if (b.hasAttribute("data-topic")) { switchTopic(Number(b.getAttribute("data-topic"))); setDrawer(false); return; }
    if (b.hasAttribute("data-tag")) { state.tag = b.getAttribute("data-tag"); render(); return; }
    if (b.hasAttribute("data-vcat")) { state.vCat = b.getAttribute("data-vcat"); render(); return; }
    if (b.hasAttribute("data-vlang")) { state.vLang = b.getAttribute("data-vlang"); render(); return; }
    var act = b.getAttribute("data-act");
    var id = Number(b.getAttribute("data-id"));
    var entry = state.entries.filter(function (e) { return e.id === id; })[0];
    if (act === "topic-new") { setDrawer(false); openTopicForm(null); return; }
    if (act === "topic-edit") {
      var et = (state.topics || []).filter(function (x) { return x.id === Number(b.getAttribute("data-tid")); })[0] || curTopic();
      setDrawer(false); openTopicForm(et); return;
    }
    if (act === "topic-del") { state.topicConfirm = true; $("topicDel").innerHTML = topicDelHtml(); return; }
    if (act === "topic-del-no") { state.topicConfirm = false; $("topicDel").innerHTML = topicDelHtml(); return; }
    if (act === "topic-del-yes") {
      var delId = state.editing && state.editing.id;
      fetch("/api/topics/" + delId, { method: "DELETE", credentials: "same-origin" })
        .then(function (r) { return r.ok ? r.json() : errText(r, tr("err_save")); })
        .then(function () {
          closeForm(); state.topic = null; toast(tr("t_deleted"));
          return loadTopics().then(loadEntries);
        }, function (err) { state.topicConfirm = false; $("topicDel").innerHTML = topicDelHtml(); $("formStatus").textContent = err.message; });
      return;
    }
    var mk = b.getAttribute("data-k");
    if (act === "mcp-show") { state.mcpShow[mk] = !state.mcpShow[mk]; render(); return; }
    if (act === "mcp-copy") {
      var url = state.mcp && state.mcp[mk + "_url"];
      try { navigator.clipboard.writeText(url).then(function () { toast(tr("c_copied")); }, function () { state.mcpShow[mk] = true; render(); }); }
      catch (e) { state.mcpShow[mk] = true; render(); }
      return;
    }
    if (act === "mcp-rotate") { state.mcpConfirm = mk; render(); return; }
    if (act === "mcp-rotate-no") { state.mcpConfirm = null; render(); return; }
    if (act === "mcp-rotate-yes") {
      api("POST", "/api/mcp-info/rotate", { welcher: mk }).then(function (m) { state.mcp = m; state.mcpConfirm = null; state.mcpShow[mk] = true; render(); toast(tr("m_rotated")); },
        function () { toast(tr("err_save")); });
      return;
    }
    if (act === "gloss-toggle") {
      if (state.glossAll) { state.glossAll = false; state.entries.forEach(function (x) { if (x.kind === "glossary" || x.kind === "med") state.openGloss[x.id] = true; }); }
      state.openGloss[id] = !state.openGloss[id];
      render(); return;
    }
    if (act === "gloss-all") { state.glossAll = !state.glossAll; state.openGloss = {}; render(); return; }
    if (act === "x-close") { state.explain = null; renderExplain(); return; }
    if (act === "x-save") {
      var xd = state.explain;
      api("POST", "/api/entries", xd.draft).then(function (e) {
        replaceEntry(e); toast(tr("x_saved"));
        state.explain = { term: xd.term, status: "exists", entry: e };
        renderExplain(); render();
      }, function () { toast(tr("err_save")); });
      return;
    }
    if (act === "x-open") {
      var xt = L(state.explain.entry.data.title) || state.explain.term;
      state.explain = null; renderExplain();
      state.tab = "glossary"; state.tag = ""; state.query = xt.split(" (")[0]; $("suche").value = state.query;
      save("tab", "glossary"); render(); window.scrollTo(0, 0);
      return;
    }
    if (act === "st-take") {
      var sk = b.getAttribute("data-k"), src = b.getAttribute("data-src");
      stImport(src === "trials" ? { nct: sk } : { pmid: sk }, "take" + (src === "trials" ? sk : "pmid:" + sk)).catch(function (err) { toast(err.message); });
      return;
    }
    if (act === "st-assess") {
      aiCall("st" + id, "/api/studies/" + id + "/summary", { lang: state.lang }).then(function (e) { replaceEntry(e); render(); }, function () {});
      return;
    }
    if (act === "c-new") { state.chat = null; state.chatConfirm = null; render(); var ta = $("chatText"); if (ta) ta.focus(); return; }
    if (act === "c-open") { openChat(Number(b.getAttribute("data-cid"))); return; }
    if (act === "c-del") { state.chatConfirm = Number(b.getAttribute("data-cid")); render(); return; }
    if (act === "c-del-no") { state.chatConfirm = null; render(); return; }
    if (act === "c-del-yes") {
      var cid = Number(b.getAttribute("data-cid"));
      api("DELETE", "/api/chats/" + cid).then(function () {
        state.chatConfirm = null;
        if (state.chat && state.chat.id === cid) state.chat = null;
        loadChats(false); toast(tr("deleted"));
      });
      return;
    }
    if (act === "c-suggest") { sendChat(tr(b.getAttribute("data-k"))); return; }
    if (act === "c-stop") { if (state.chatAbort) state.chatAbort.abort(); return; }
    if (act === "c-save") { saveChatNote(Number(b.getAttribute("data-i"))); return; }
    if (act === "c-copy") {
      var txtc = state.chat.messages[Number(b.getAttribute("data-i"))].text;
      try { navigator.clipboard.writeText(txtc).then(function () { toast(tr("c_copied")); }, function () {}); } catch (e) { /* alte Browser */ }
      return;
    }
    if (act === "play" && entry) { openPlayer(entry); return; }
    if (act === "player-close") { closePlayer(); return; }
    if (act === "v-process") { processVideo(id).catch(function () {}); return; }
    if (act === "v-all") { processAll(); return; }
    if (act === "seek") {
      var fr = $("spieler").querySelector("iframe");
      if (fr && entry) fr.src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(entry.data.yt_id) + "?autoplay=1&rel=0&start=" + b.getAttribute("data-t");
      $("spieler").scrollTop = 0;
      return;
    }
    if (act === "preview") { loadPreview(); return; }
    var slot = b.getAttribute("data-slot");
    if (act === "ai-lookup") {
      var q = (state.aiIn[slot] || "").trim();
      if (!q) { var inp = $("ai-in-" + slot); if (inp) inp.focus(); return; }
      var url = slot === "research" ? "/api/ai/research" : "/api/ai/" + slot;
      var payload = slot === "research" ? { question: q, lang: state.lang, web: state.aiIn.web, mappe: state.aiIn.mappe } : { term: q, lang: state.lang };
      state.drafts[slot] = null;
      aiCall(slot, url, payload).then(function (d) { state.drafts[slot] = d; render(); }, function () {});
      return;
    }
    if (act === "ai-discard") { state.drafts[slot] = null; render(); return; }
    if (act === "ai-save") {
      var dr = state.drafts[slot];
      api("POST", "/api/entries", dr).then(function (e) {
        replaceEntry(e); state.drafts[slot] = null; state.aiIn[slot] = ""; render(); toast(tr("saved"));
      }).catch(function () { toast(tr("err_save")); });
      return;
    }
    if (act === "ai-analyze") {
      aiCall("an" + id, "/api/ai/analyze/" + id, { lang: state.lang }).then(function (e) { replaceEntry(e); render(); }, function () {});
      return;
    }
    if (act === "ai-values" || act === "ai-hints") {
      var k = act === "ai-values" ? "values" : "hints";
      aiCall(k, "/api/ai/" + k, { lang: state.lang }).then(function (e) { replaceEntry(e); render(); }, function () {});
      return;
    }
    if (act === "key-test") {
      state.testOk = false;
      aiCall("test", "/api/settings/test").then(function (r) { state.models = r.models; state.testOk = true; render(); }, function () {});
      return;
    }
    if (act === "key-remove") { state.confirmKey = true; render(); return; }
    if (act === "tkey-remove") { saveSettings({ remove_transcript_key: true }); return; }
    if (act === "key-remove-no") { state.confirmKey = false; render(); return; }
    if (act === "key-remove-yes") { saveSettings({ remove_key: true }); state.confirmKey = false; return; }
    if (act === "settings-save") {
      saveSettings({ model: $("s-model").value, model_fast: $("s-model-fast").value, web_search: $("s-web").checked });
      return;
    }
    if (act === "new") openForm(b.getAttribute("data-kind"));
    else if (act === "upload") { openForm("finding"); var fi = $("fld-files"); if (fi) fi.click(); }
    else if (act === "pending-del") { state.pending.splice(Number(b.getAttribute("data-i")), 1); renderFileList(); }
    else if (act === "file-del" && state.editing) {
      api("DELETE", "/api/files/" + b.getAttribute("data-file")).then(function (e) {
        state.editing.files = e.files || [];
        state.entries = state.entries.map(function (x) { return x.id === e.id ? e : x; });
        renderFileList(); render(); toast(tr("file_removed"));
      }).catch(function () { toast(tr("err_save")); });
    }
    else if (act === "edit" && entry) openForm(entry.kind, entry);
    else if (act === "del") { state.confirm = id; render(); }
    else if (act === "del-no") { state.confirm = null; render(); }
    else if (act === "del-yes") {
      api("DELETE", "/api/entries/" + id).then(function () {
        state.entries = state.entries.filter(function (e) { return e.id !== id; });
        state.confirm = null; render(); toast(tr("deleted"));
      }).catch(function () { toast(tr("err_save")); });
    }
  });
  document.addEventListener("toggle", function (ev) {
    var d = ev.target;
    if (d.classList && d.classList.contains("verlauf")) {
      if (d.open) state.openParam = d.getAttribute("data-param");
      else if (state.openParam === d.getAttribute("data-param")) state.openParam = null;
    }
  }, true);
  $("neuKnopf").addEventListener("click", function () {
    var map = { values: "value", glossary: "glossary", med: "med", research: "research", home: "research", settings: "research", videos: "video", studies: "study" };
    openForm(map[state.tab]);
  });
  $("suche").addEventListener("input", function () { state.query = this.value; render(); });
  $("themenSuche").addEventListener("input", function () { state.topicQuery = this.value; renderTopics(); });
  $("themenSuche").addEventListener("keydown", function (ev) {
    // Enter öffnet den ersten Treffer
    if (ev.key !== "Enter") return;
    var first = $("themenListe").querySelector("[data-topic]");
    if (first) first.click();
  });
  document.addEventListener("mouseup", function (ev) { if (!ev.target.closest || !ev.target.closest("#markKnopf, #erklaerung")) checkSelection(); });
  document.addEventListener("keyup", function (ev) { if (ev.shiftKey || ev.key === "Shift") checkSelection(); });
  // Telefon: markieren per langem Druck löst kein mouseup aus
  document.addEventListener("selectionchange", function () {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed) { clearTimeout(markTimer); $("markKnopf").hidden = true; return; }
    if ("ontouchstart" in window) checkSelection();
  });
  window.addEventListener("scroll", function () { $("markKnopf").hidden = true; }, true);
  // mousedown statt click: sonst hebt der Klick die Markierung auf, bevor wir sie lesen
  $("markKnopf").addEventListener("mousedown", function (ev) { ev.preventDefault(); });
  $("markKnopf").addEventListener("click", function () {
    var info = selectionInfo() || state.markInfo;
    if (info) explain(info);
    if (window.getSelection) window.getSelection().removeAllRanges();
  });
  $("erklaerung").addEventListener("click", function (ev) {
    var b = ev.target.closest && ev.target.closest("[data-act]");
    if (b && b.getAttribute("data-act") === "x-close") { state.explain = null; renderExplain(); }
  });
  $("einstKnopf").addEventListener("click", function () {
    state.tab = state.tab === "settings" ? "home" : "settings";
    save("tab", state.tab); setDrawer(false); render(); window.scrollTo(0, 0);
  });
  $("themenKnopf").addEventListener("click", function () { setDrawer(!document.body.classList.contains("leiste-offen")); });
  $("leistenSchleier").addEventListener("click", function () { setDrawer(false); });
  // KI-Eingaben überleben das Neuzeichnen, weil sie im Zustand mitgeschrieben werden
  $("inhalt").addEventListener("input", function (ev) {
    if (ev.target.id === "stQ") { state.st.q = ev.target.value; return; }
    if (ev.target.id === "stImp") { state.st.imp = ev.target.value; return; }
    if (ev.target.id === "chatText") { state.chatIn = ev.target.value; return; }
    var slot = ev.target.getAttribute("data-ai-in");
    if (slot) state.aiIn[slot] = ev.target.value;
  });
  $("inhalt").addEventListener("change", function (ev) {
    if (ev.target.name === "stsrc") { state.st.source = ev.target.value; state.st.results = null; render(); return; }
    if (ev.target.id === "stLand") { state.st.land = ev.target.value; if (state.st.q.trim()) stSearch(); return; }
    if (ev.target.id === "stOpen") { state.st.open = ev.target.checked; if (state.st.q.trim()) stSearch(); return; }
    if (ev.target.id === "stRecent") { state.st.recent = ev.target.checked; if (state.st.q.trim()) stSearch(); return; }
    var copt = ev.target.getAttribute("data-c-opt");
    if (copt) { state.chatOpts[copt] = ev.target.checked; save("chatopts", JSON.stringify(state.chatOpts)); return; }
    var opt = ev.target.getAttribute("data-ai-opt");
    if (opt) state.aiIn[opt] = ev.target.checked;
  });
  $("inhalt").addEventListener("keydown", function (ev) {
    if (ev.target.id === "chatText" && ev.key === "Enter" && !ev.shiftKey && window.innerWidth > 700) {
      ev.preventDefault();
      sendChat(ev.target.value);
      return;
    }
    var slot = ev.target.getAttribute("data-ai-in");
    if (slot && slot !== "research" && ev.key === "Enter") {
      ev.preventDefault();
      var btn = document.querySelector('[data-act="ai-lookup"][data-slot="' + slot + '"]');
      if (btn) btn.click();
    }
  });
  $("inhalt").addEventListener("submit", function (ev) {
    if (ev.target.id === "stForm") { ev.preventDefault(); state.st.q = $("stQ").value; stSearch(); return; }
    if (ev.target.id === "stImpForm") {
      ev.preventDefault();
      var v = $("stImp").value.trim();
      if (v) stImport({ url: v }, "stimp").then(function () { state.st.imp = ""; render(); }, function () {});
      return;
    }
    if (ev.target.id === "chatForm") { ev.preventDefault(); sendChat($("chatText").value); return; }
    if (ev.target.id === "transForm") {
      ev.preventDefault();
      var tk = $("s-tkey").value.trim();
      if (tk) saveSettings({ transcript_key: tk });
      return;
    }
    if (ev.target.id !== "keyForm") return;
    ev.preventDefault();
    var key = $("s-key").value.trim();
    if (key) saveSettings({ openai_key: key });
  });
  function saveSettings(body) {
    fetch("/api/settings", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), credentials: "same-origin" })
      .then(function (r) { return r.ok ? r.json() : errText(r, tr("err_save")); })
      .then(function (st) { state.settings = st; state.testOk = false; render(); toast(tr("s_saved")); },
        function (err) { toast(err.message); });
  }
  $("formular").addEventListener("submit", submitForm);
  $("formZu").addEventListener("click", closeForm);
  $("formAbbruch").addEventListener("click", closeForm);
  $("schleier").addEventListener("click", function (ev) { if (ev.target === this) closeForm(); });
  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "Escape") return;
    if (state.explain) { state.explain = null; renderExplain(); return; }
    if (document.body.classList.contains("leiste-offen")) { setDrawer(false); return; }
    if (!$("spieler").hidden) closePlayer();
    else if (!$("schleier").hidden) closeForm();
  });
  $("spieler").addEventListener("click", function (ev) { if (ev.target === this) closePlayer(); });
  // Eingefügte YouTube-Adresse sofort auflösen, ohne extra Klick
  $("formFelder").addEventListener("paste", function (ev) {
    if (ev.target.id !== "fld-url") return;
    setTimeout(function () { loadPreview(); }, 30);
  });
  $("formFelder").addEventListener("change", function (ev) {
    if (ev.target.id === "fld-url" && !(state.preview && state.preview.url === ev.target.value.trim())) { loadPreview(); return; }
    if (ev.target.id === "fld-files") { addPending(ev.target.files); ev.target.value = ""; return; }
    if (ev.target.id !== "fld-param") return;
    var p = PARAM_BY_KEY[ev.target.value];
    $("wrap-paramLabel").hidden = ev.target.value !== "_other";
    if (p) {
      $("fld-unit").value = p.unit;
      $("fld-low").value = p.low != null ? fmtNum(p.low) : "";
      $("fld-high").value = p.high != null ? fmtNum(p.high) : "";
    }
  });

  // Dateien aufs Fenster ziehen: ins offene Formular, sonst als neuer Befund
  var dragDepth = 0;
  function hasFiles(ev) { return ev.dataTransfer && Array.prototype.indexOf.call(ev.dataTransfer.types || [], "Files") !== -1; }
  document.addEventListener("dragenter", function (ev) {
    if (!hasFiles(ev)) return;
    dragDepth++; document.body.classList.add("ziehen");
  });
  document.addEventListener("dragleave", function () {
    dragDepth = Math.max(0, dragDepth - 1);
    if (!dragDepth) document.body.classList.remove("ziehen");
  });
  document.addEventListener("dragover", function (ev) { if (hasFiles(ev)) ev.preventDefault(); });
  document.addEventListener("drop", function (ev) {
    if (!hasFiles(ev)) return;
    ev.preventDefault();
    dragDepth = 0; document.body.classList.remove("ziehen");
    if (!$("schleier").hidden) addPending(ev.dataTransfer.files);
    else openForm("finding", null, ev.dataTransfer.files);
  });

  // ---------- Start ----------
  var savedLang = load("lang");
  if (LANGS.indexOf(savedLang) !== -1) state.lang = savedLang;
  else {
    var nav = (navigator.language || "de").slice(0, 2);
    if (LANGS.indexOf(nav) !== -1) state.lang = nav;
  }
  try { var co = JSON.parse(load("chatopts") || "null"); if (co) state.chatOpts = { web: !!co.web, mappe: co.mappe !== false }; } catch (e) { /* egal */ }
  var savedTab = load("tab");
  if (TABS.some(function (t) { return t.id === savedTab; })) state.tab = savedTab;
  render();
  api("GET", "/api/settings").then(function (st) { state.settings = st; render(); }).catch(function () {});
  function kopfHoehe() {
    var k = document.querySelector(".kopf");
    if (k) document.documentElement.style.setProperty("--kopf-h", k.offsetHeight + "px");
  }
  kopfHoehe();
  window.addEventListener("resize", kopfHoehe);
  loadTopics().then(loadEntries, function () { $("inhalt").innerHTML = '<div class="leer">' + esc(tr("err_load")) + "</div>"; });
})();
