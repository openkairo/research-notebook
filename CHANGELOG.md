# Changelog

## Unveröffentlicht

- Messwerte aus CSV importieren (z. B. Blutdruckmessgerät, Gesundheits-App): Trennzeichen, Datum/Uhrzeit und typische Spalten (Systolisch, Diastolisch, Puls, Gewicht, Blutzucker; DE/EN/PL) werden erkannt, Zuordnung je Spalte mit Einheit und Normbereich, Vorschau, doppelte Messungen werden übersprungen
- Messwerte mit Uhrzeit (mehrere Messungen am Tag); neue Vorlagen Blutdruck systolisch/diastolisch, Puls, Blutzucker
- KI bekommt bei langen Messreihen Statistik (Anzahl, Zeitraum, Mittel, Min, Max) plus die letzten 30 Messungen
- CSV-Dateien auch als Anhang möglich; die KI liest sie bei der Einordnung mit
- Studien: „Alle Studien zusammenfassen“ — KI-Gesamtbild über alle gespeicherten Studien des Themas (gemeinsame Aussagen mit Verweisen [Nr.], Widersprüche, Belastbarkeit, laufende Studien, Bezug zum Notizbuch); frühere Fassungen bleiben eingeklappt erhalten
- Reiter Medikamente zählt nur die Medikamente, nicht zusätzlich die Einträge im Medikamentenplan
- Medikamentenplan: Beginn „nicht bekannt“ wählbar (auch per MCP mit `start: "unbekannt"`)
- Medikamentenplan im Reiter Medikamente: aus den Medikamenten übernehmen oder frei anlegen; Stärke, Darreichungsform, Menge Morgens/Mittags/Abends/Nachts, Häufigkeit (täglich, Rhythmus, bei Bedarf, Zyklus), Zeitraum, Grund, Hinweise, verordnet von, Status; Tagesdosis und Vorrat mit „reicht bis“-Warnung; Druckansicht
- Analyse, Chat und KI-Einordnungen berücksichtigen den Plan als tatsächlich eingenommene Medikation (Wechselwirkungen, Einnahmezeiten, Doppelungen, Laborkontrollen, Vorrat)
- MCP: `medikamentenplan` (lesen) und `plan_eintrag_setzen` (schreiben)
- Analyse-Knopf nennt das Thema; Hinweis stellt klar, dass nur das aktuelle Thema analysiert wird
- Übersicht: „Analyse“ (vorher „KI-Hinweise“) steht prominent oben, mit Hinweis, dass alle Daten des Themas ausgewertet und an die KI übermittelt werden; frühere Analysen eingeklappt
- Analyse liest jetzt wirklich alles: zusätzlich Medikamente ohne Notiz, Inhalt der Recherche-Notizen, Begriffe und Videos
- Medikamente: lange Beschreibungen (Wirkung, Nebenwirkungen, Notizen) sind eingeklappt mit „Weiterlesen“; „Alle aufklappen“ auch im Reiter Medikamente

## 1.0.0 — 2026-10-09

Erste öffentliche Fassung.

- Themen als oberste Ebene, jedes mit frei wählbaren Unterbereichen; Art „Gesundheit“ oder „Allgemein“
- Werte & Befunde mit Verlauf, Referenzbereich und Anhängen (PDF, Fotos)
- Begriffe, Medikamente, Recherche-Notizen, Videos & Links mit Vorschaubild, Transkript und Zusammenfassung
- Studien: Suche in PubMed und ClinicalTrials.gov, Übernehmen per Klick, PubMed-ID, NCT-Nummer oder DOI, KI-Einordnung mit Belastbarkeit
- KI-Funktionen über OpenAI: Befund-Einordnung (auch PDFs), Werte-Analyse, Hinweise, Recherche mit Websuche, Chat
- Markieren & erklären: an jeder Stelle einen Begriff markieren, erklären lassen und in Begriffe übernehmen
- Dreisprachig (DE/EN/PL), automatische Übersetzung aller Texte
- MCP-Schnittstelle für KI-Agenten mit getrennten Zugängen für Lesen und Schreiben
- Eingebaute Anmeldung (`APP_PASSWORD`), optionale Beispielinhalte (`EXAMPLE_DATA`)
