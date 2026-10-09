"""Erzeugt seed.json — Startinhalte, die beim ersten Start in die leere Datenbank kommen."""
import json
from pathlib import Path

def t(de, en, pl):
    return {"de": de, "en": en, "pl": pl}

G = []  # Begriffe
def g(titel, text, tags):
    G.append({"kind": "glossary", "data": {"title": titel, "body": text, "tags": tags, "seed": True}})

g(t("Mammakarzinom", "Breast carcinoma", "Rak piersi"),
  t("Fachbegriff für Brustkrebs: ein bösartiger Tumor, der vom Drüsengewebe der Brust ausgeht. Die häufigste Krebserkrankung bei Frauen; Männer können ebenfalls erkranken.",
    "Medical term for breast cancer: a malignant tumour arising from the glandular tissue of the breast. The most common cancer in women; men can also be affected.",
    "Medyczna nazwa raka piersi: nowotwór złośliwy wywodzący się z tkanki gruczołowej piersi. Najczęstszy nowotwór u kobiet; chorować mogą też mężczyźni."),
  ["Grundlagen"])
g(t("Invasiv-duktales Karzinom (NST)", "Invasive ductal carcinoma (NST)", "Rak inwazyjny przewodowy (NST)"),
  t("Häufigste Form (ca. 70–80 %). Geht von den Milchgängen aus und ist in das umliegende Gewebe eingewachsen. NST heißt „no special type“, also kein besonderer Subtyp.",
    "The most common form (about 70–80 %). Starts in the milk ducts and has grown into surrounding tissue. NST means “no special type”.",
    "Najczęstsza postać (ok. 70–80 %). Wychodzi z przewodów mlecznych i nacieka otaczającą tkankę. NST oznacza „no special type”, czyli bez szczególnego typu."),
  ["Pathologie"])
g(t("Invasiv-lobuläres Karzinom", "Invasive lobular carcinoma", "Rak inwazyjny zrazikowy"),
  t("Zweithäufigste Form (ca. 10–15 %). Geht von den Drüsenläppchen aus, wächst oft diffus und ist in der Mammographie manchmal schwerer zu erkennen. Meist hormonrezeptor-positiv.",
    "Second most common form (about 10–15 %). Starts in the lobules, often grows diffusely and can be harder to see on a mammogram. Usually hormone-receptor positive.",
    "Druga co do częstości postać (ok. 10–15 %). Wychodzi ze zrazików, często rośnie rozlanie i bywa trudniejsza do wykrycia w mammografii. Zwykle hormonozależna."),
  ["Pathologie"])
g(t("DCIS", "DCIS", "DCIS"),
  t("Duktales Carcinoma in situ: Krebszellen in den Milchgängen, die noch nicht in das umgebende Gewebe eingewachsen sind. Gilt als Vorstufe; wird meist operiert, oft mit Bestrahlung.",
    "Ductal carcinoma in situ: cancer cells inside the milk ducts that have not grown into surrounding tissue. Considered a precursor; usually treated with surgery, often plus radiotherapy.",
    "Rak przewodowy in situ: komórki nowotworowe w przewodach mlecznych, które nie naciekły jeszcze otaczającej tkanki. Uważany za stan przedinwazyjny; zwykle leczony operacyjnie, często z radioterapią."),
  ["Pathologie"])
g(t("Hormonrezeptor-Status (ER/PR)", "Hormone receptor status (ER/PR)", "Status receptorów hormonalnych (ER/PR)"),
  t("Zeigt, ob die Tumorzellen Andockstellen für Östrogen (ER) und Progesteron (PR) haben. Angabe meist in Prozent positiver Zellen oder als Score (z. B. IRS 0–12). Positiv heißt: Eine Antihormontherapie kann wirken.",
    "Shows whether tumour cells carry receptors for oestrogen (ER) and progesterone (PR). Usually reported as percent of positive cells or as a score (e.g. Allred 0–8). Positive means endocrine (anti-hormone) therapy can work.",
    "Pokazuje, czy komórki guza mają receptory estrogenowe (ER) i progesteronowe (PR). Podawany zwykle jako odsetek komórek dodatnich lub w skali punktowej (np. Allred 0–8). Wynik dodatni oznacza, że hormonoterapia może być skuteczna."),
  ["Pathologie", "Rezeptoren"])
g(t("HER2", "HER2", "HER2"),
  t("Wachstumsrezeptor auf der Zelloberfläche. Bewertung per Immunhistochemie: 0, 1+, 2+, 3+. 3+ (oder 2+ mit positivem ISH-Test) = HER2-positiv, dann wirken Anti-HER2-Medikamente wie Trastuzumab. 1+ oder 2+ ohne Amplifikation = „HER2-low“, wichtig für Trastuzumab-Deruxtecan.",
    "Growth receptor on the cell surface. Scored by immunohistochemistry: 0, 1+, 2+, 3+. 3+ (or 2+ with positive ISH test) = HER2-positive, so anti-HER2 drugs such as trastuzumab work. 1+ or 2+ without amplification = “HER2-low”, relevant for trastuzumab deruxtecan.",
    "Receptor wzrostu na powierzchni komórki. Ocena immunohistochemiczna: 0, 1+, 2+, 3+. 3+ (lub 2+ z dodatnim testem ISH) = HER2-dodatni, wtedy działają leki anty-HER2, np. trastuzumab. 1+ lub 2+ bez amplifikacji = „HER2-low”, istotne dla trastuzumabu derukstekanu."),
  ["Pathologie", "Rezeptoren"])
g(t("Ki-67", "Ki-67", "Ki-67"),
  t("Marker für die Teilungsaktivität der Tumorzellen, in Prozent. Niedrig (etwa unter 10–15 %) spricht für langsames, hoch (etwa über 25–30 %) für schnelles Wachstum. Die Grenzwerte unterscheiden sich je nach Labor.",
    "Marker of how actively tumour cells are dividing, in percent. Low (roughly under 10–15 %) suggests slow growth, high (roughly over 25–30 %) fast growth. Cut-offs vary between labs.",
    "Wskaźnik aktywności podziałowej komórek guza, w procentach. Niski (mniej więcej poniżej 10–15 %) przemawia za wolnym wzrostem, wysoki (powyżej ok. 25–30 %) za szybkim. Wartości graniczne zależą od laboratorium."),
  ["Pathologie"])
g(t("Grading (G1–G3)", "Grading (G1–G3)", "Stopień złośliwości histologicznej (G1–G3)"),
  t("Wie stark sich die Tumorzellen vom gesunden Gewebe unterscheiden. G1 = gut differenziert (eher langsam), G2 = mäßig, G3 = schlecht differenziert (eher aggressiv).",
    "How much the tumour cells differ from healthy tissue. G1 = well differentiated (slower), G2 = moderately, G3 = poorly differentiated (more aggressive).",
    "Jak bardzo komórki guza różnią się od zdrowej tkanki. G1 = dobrze zróżnicowany (wolniejszy), G2 = średnio, G3 = słabo zróżnicowany (bardziej agresywny)."),
  ["Pathologie"])
g(t("TNM-Klassifikation", "TNM classification", "Klasyfikacja TNM"),
  t("Beschreibt die Ausbreitung: T = Tumorgröße (T1 ≤ 2 cm, T2 2–5 cm, T3 > 5 cm, T4 Haut/Brustwand), N = befallene Lymphknoten (N0 keine), M = Fernmetastasen (M0 keine, M1 vorhanden). Ein vorangestelltes „p“ heißt pathologisch gesichert, „c“ klinisch, „y“ nach Vorbehandlung.",
    "Describes the extent: T = tumour size (T1 ≤ 2 cm, T2 2–5 cm, T3 > 5 cm, T4 skin/chest wall), N = involved lymph nodes (N0 none), M = distant metastases (M0 none, M1 present). Prefix “p” = pathological, “c” = clinical, “y” = after prior treatment.",
    "Opisuje zaawansowanie: T = wielkość guza (T1 ≤ 2 cm, T2 2–5 cm, T3 > 5 cm, T4 skóra/ściana klatki piersiowej), N = zajęte węzły chłonne (N0 brak), M = przerzuty odległe (M0 brak, M1 obecne). Przedrostek „p” = ocena patologiczna, „c” = kliniczna, „y” = po leczeniu wstępnym."),
  ["Stadium"])
g(t("Triple-negativ (TNBC)", "Triple-negative (TNBC)", "Potrójnie ujemny (TNBC)"),
  t("ER, PR und HER2 sind negativ. Antihormon- und Anti-HER2-Therapien wirken dann nicht; Behandlung meist mit Chemotherapie, oft kombiniert mit Immuntherapie (Pembrolizumab).",
    "ER, PR and HER2 are all negative. Anti-hormone and anti-HER2 drugs do not work; treatment is usually chemotherapy, often combined with immunotherapy (pembrolizumab).",
    "ER, PR i HER2 są ujemne. Hormonoterapia i leki anty-HER2 nie działają; leczenie to zwykle chemioterapia, często łączona z immunoterapią (pembrolizumab)."),
  ["Subtypen"])
g(t("Luminal A / Luminal B", "Luminal A / Luminal B", "Luminalny A / Luminalny B"),
  t("Molekulare Subtypen hormonrezeptor-positiver Tumoren. Luminal A: HER2-negativ, Ki-67 niedrig, meist gute Prognose. Luminal B: höheres Ki-67 und/oder HER2-positiv, oft zusätzlich Chemotherapie.",
    "Molecular subtypes of hormone-receptor-positive tumours. Luminal A: HER2-negative, low Ki-67, usually good prognosis. Luminal B: higher Ki-67 and/or HER2-positive, often chemotherapy in addition.",
    "Podtypy molekularne guzów hormonozależnych. Luminalny A: HER2-ujemny, niskie Ki-67, zwykle dobre rokowanie. Luminalny B: wyższe Ki-67 i/lub HER2-dodatni, często dodatkowo chemioterapia."),
  ["Subtypen"])
g(t("Sentinel-Lymphknoten", "Sentinel lymph node", "Węzeł wartowniczy"),
  t("Der erste Lymphknoten im Abflussgebiet des Tumors. Er wird markiert, entnommen und untersucht. Ist er frei, kann man meist auf die Entfernung weiterer Achsellymphknoten verzichten.",
    "The first lymph node draining the tumour. It is marked, removed and examined. If it is free of cancer, removing further armpit nodes can usually be avoided.",
    "Pierwszy węzeł chłonny na drodze spływu chłonki z guza. Jest oznaczany, usuwany i badany. Jeśli jest wolny od raka, zwykle można uniknąć usuwania kolejnych węzłów pachowych."),
  ["Operation"])
g(t("BI-RADS", "BI-RADS", "BI-RADS"),
  t("Einstufung von Mammographie-, Ultraschall- und MRT-Befunden: 0 = unvollständig, 1 = unauffällig, 2 = gutartig, 3 = wahrscheinlich gutartig (Kontrolle), 4 = verdächtig (Biopsie), 5 = hochverdächtig, 6 = durch Biopsie gesicherter Krebs.",
    "Rating scale for mammogram, ultrasound and MRI findings: 0 = incomplete, 1 = negative, 2 = benign, 3 = probably benign (follow-up), 4 = suspicious (biopsy), 5 = highly suspicious, 6 = biopsy-proven cancer.",
    "Skala oceny wyników mammografii, USG i MRI: 0 = niekompletne, 1 = bez zmian, 2 = zmiana łagodna, 3 = prawdopodobnie łagodna (kontrola), 4 = podejrzana (biopsja), 5 = wysoce podejrzana, 6 = rak potwierdzony biopsją."),
  ["Bildgebung"])
g(t("Stanzbiopsie", "Core needle biopsy", "Biopsja gruboigłowa"),
  t("Gewebeentnahme mit einer Hohlnadel unter Ultraschall- oder Röntgenkontrolle. Liefert die Diagnose sowie ER, PR, HER2, Ki-67 und Grading.",
    "Tissue sample taken with a hollow needle under ultrasound or X-ray guidance. Provides the diagnosis plus ER, PR, HER2, Ki-67 and grade.",
    "Pobranie tkanki igłą pod kontrolą USG lub RTG. Daje rozpoznanie oraz ER, PR, HER2, Ki-67 i stopień złośliwości."),
  ["Diagnostik"])
g(t("Neoadjuvant / adjuvant", "Neoadjuvant / adjuvant", "Neoadiuwantowe / adiuwantowe"),
  t("Neoadjuvant = Therapie vor der Operation (z. B. um den Tumor zu verkleinern und das Ansprechen zu sehen). Adjuvant = Therapie nach der Operation, um das Rückfallrisiko zu senken.",
    "Neoadjuvant = treatment before surgery (e.g. to shrink the tumour and see how it responds). Adjuvant = treatment after surgery to lower the risk of recurrence.",
    "Neoadiuwantowe = leczenie przed operacją (np. aby zmniejszyć guz i ocenić odpowiedź). Adiuwantowe = leczenie po operacji, aby zmniejszyć ryzyko nawrotu."),
  ["Therapie"])
g(t("pCR (pathologische Komplettremission)", "pCR (pathological complete response)", "pCR (całkowita odpowiedź patologiczna)"),
  t("Nach neoadjuvanter Therapie findet der Pathologe im OP-Präparat keine invasiven Tumorzellen mehr (ypT0/is ypN0). Gilt besonders bei HER2-positivem und triple-negativem Brustkrebs als günstiges Zeichen.",
    "After neoadjuvant therapy the pathologist finds no remaining invasive cancer in the surgical specimen (ypT0/is ypN0). A favourable sign, especially in HER2-positive and triple-negative breast cancer.",
    "Po leczeniu neoadiuwantowym patolog nie stwierdza w materiale pooperacyjnym inwazyjnych komórek raka (ypT0/is ypN0). Korzystny czynnik, zwłaszcza w raku HER2-dodatnim i potrójnie ujemnym."),
  ["Therapie"])
g(t("BRCA1 / BRCA2", "BRCA1 / BRCA2", "BRCA1 / BRCA2"),
  t("Gene, deren erbliche Veränderung (Mutation) das Risiko für Brust- und Eierstockkrebs deutlich erhöht. Ein Nachweis beeinflusst Therapie (z. B. PARP-Hemmer wie Olaparib), Operationsplanung und die Beratung von Angehörigen.",
    "Genes whose inherited mutation markedly raises the risk of breast and ovarian cancer. A positive result affects treatment (e.g. PARP inhibitors such as olaparib), surgical planning and counselling of relatives.",
    "Geny, których dziedziczna mutacja znacznie zwiększa ryzyko raka piersi i jajnika. Wynik dodatni wpływa na leczenie (np. inhibitory PARP, jak olaparyb), planowanie operacji i poradnictwo dla krewnych."),
  ["Genetik"])
g(t("Tumorboard", "Tumour board", "Konsylium onkologiczne"),
  t("Konferenz, in der Fachleute aus Gynäkologie, Onkologie, Radiologie, Pathologie und Strahlentherapie gemeinsam den Behandlungsplan festlegen.",
    "Meeting in which specialists from gynaecology, oncology, radiology, pathology and radiotherapy agree on the treatment plan together.",
    "Spotkanie, na którym specjaliści z ginekologii, onkologii, radiologii, patomorfologii i radioterapii wspólnie ustalają plan leczenia."),
  ["Ablauf"])
g(t("Port", "Port (port-a-cath)", "Port naczyniowy"),
  t("Kleine Kammer unter der Haut mit Schlauch in eine große Vene. Über ihn laufen Infusionen und Blutabnahmen, ohne dass jedes Mal eine Armvene punktiert werden muss.",
    "Small chamber under the skin with a catheter into a large vein. Infusions and blood draws go through it, so arm veins need not be punctured each time.",
    "Mała komora pod skórą z cewnikiem do dużej żyły. Przez nią podaje się wlewy i pobiera krew bez każdorazowego nakłuwania żył ręki."),
  ["Ablauf"])

M = []
def m(name, kl, wirkung, nw):
    M.append({"kind": "med", "data": {"title": name, "cls": kl, "body": wirkung, "side": nw, "seed": True}})

same = lambda s: t(s, s, s)
m(same("Tamoxifen"), t("Antiöstrogen (SERM)", "Anti-oestrogen (SERM)", "Antyestrogen (SERM)"),
  t("Blockiert den Östrogenrezeptor an den Tumorzellen. Tablette, meist 5–10 Jahre; vor allem vor den Wechseljahren.",
    "Blocks the oestrogen receptor on tumour cells. Tablet, usually for 5–10 years; mainly before menopause.",
    "Blokuje receptor estrogenowy w komórkach guza. Tabletka, zwykle przez 5–10 lat; głównie przed menopauzą."),
  t("Hitzewallungen, Scheidentrockenheit/Ausfluss, erhöhtes Thrombose-Risiko, selten Veränderungen der Gebärmutterschleimhaut.",
    "Hot flushes, vaginal dryness/discharge, higher risk of blood clots, rarely changes to the lining of the womb.",
    "Uderzenia gorąca, suchość/upławy pochwy, zwiększone ryzyko zakrzepicy, rzadko zmiany w błonie śluzowej macicy."))
m(t("Letrozol / Anastrozol / Exemestan", "Letrozole / anastrozole / exemestane", "Letrozol / anastrozol / eksemestan"),
  t("Aromatasehemmer", "Aromatase inhibitors", "Inhibitory aromatazy"),
  t("Senken die Östrogenbildung im Fettgewebe. Tablette, nach den Wechseljahren oder zusammen mit Ausschaltung der Eierstockfunktion.",
    "Lower oestrogen production in fatty tissue. Tablet, after menopause or together with ovarian function suppression.",
    "Zmniejszają wytwarzanie estrogenów w tkance tłuszczowej. Tabletka, po menopauzie lub razem z supresją czynności jajników."),
  t("Gelenk- und Muskelschmerzen, Knochendichteverlust (Osteoporose), Hitzewallungen, Müdigkeit.",
    "Joint and muscle pain, bone loss (osteoporosis), hot flushes, fatigue.",
    "Bóle stawów i mięśni, utrata gęstości kości (osteoporoza), uderzenia gorąca, zmęczenie."))
m(t("Goserelin / Leuprorelin", "Goserelin / leuprorelin", "Goserelina / leuprorelina"),
  t("GnRH-Analoga", "GnRH analogues", "Analogi GnRH"),
  t("Schalten die Hormonbildung der Eierstöcke vorübergehend ab (künstliche Wechseljahre). Depotspritze alle 4 Wochen oder 3 Monate.",
    "Temporarily switch off hormone production in the ovaries (induced menopause). Depot injection every 4 weeks or 3 months.",
    "Czasowo wyłączają produkcję hormonów przez jajniki (sztuczna menopauza). Zastrzyk depot co 4 tygodnie lub co 3 miesiące."),
  t("Wechseljahrsbeschwerden, Stimmungsschwankungen, Knochendichteverlust.",
    "Menopausal symptoms, mood swings, bone loss.",
    "Objawy menopauzy, wahania nastroju, utrata gęstości kości."))
m(t("Trastuzumab (Herceptin®)", "Trastuzumab (Herceptin®)", "Trastuzumab (Herceptin®)"),
  t("Anti-HER2-Antikörper", "Anti-HER2 antibody", "Przeciwciało anty-HER2"),
  t("Bindet an HER2 und bremst das Tumorwachstum. Nur bei HER2-positivem Brustkrebs. Infusion oder Spritze unter die Haut, meist alle 3 Wochen über 1 Jahr.",
    "Binds to HER2 and slows tumour growth. Only for HER2-positive breast cancer. Infusion or under-the-skin injection, usually every 3 weeks for 1 year.",
    "Wiąże się z HER2 i hamuje wzrost guza. Tylko w raku HER2-dodatnim. Wlew lub zastrzyk podskórny, zwykle co 3 tygodnie przez 1 rok."),
  t("Herzschwäche möglich → regelmäßige Herzultraschall-Kontrollen (LVEF). Infusionsreaktionen, Durchfall.",
    "Can weaken the heart → regular heart ultrasound checks (LVEF). Infusion reactions, diarrhoea.",
    "Możliwe osłabienie serca → regularne echo serca (LVEF). Reakcje na wlew, biegunka."))
m(same("Pertuzumab (Perjeta®)"), t("Anti-HER2-Antikörper", "Anti-HER2 antibody", "Przeciwciało anty-HER2"),
  t("Blockiert HER2 an einer anderen Stelle als Trastuzumab; wird mit ihm kombiniert (doppelte Blockade), oft vor der Operation.",
    "Blocks HER2 at a different site than trastuzumab; given in combination with it (dual blockade), often before surgery.",
    "Blokuje HER2 w innym miejscu niż trastuzumab; podawany razem z nim (podwójna blokada), często przed operacją."),
  t("Durchfall, Hautausschlag, Herzkontrollen wie bei Trastuzumab.",
    "Diarrhoea, rash, heart monitoring as with trastuzumab.",
    "Biegunka, wysypka, kontrola serca jak przy trastuzumabie."))
m(t("Trastuzumab-Deruxtecan (Enhertu®)", "Trastuzumab deruxtecan (Enhertu®)", "Trastuzumab derukstekan (Enhertu®)"),
  t("Antikörper-Wirkstoff-Konjugat (ADC)", "Antibody–drug conjugate (ADC)", "Koniugat przeciwciało–lek (ADC)"),
  t("Antikörper bringt ein Zellgift direkt an die Tumorzelle. Bei HER2-positivem und auch HER2-low metastasiertem Brustkrebs.",
    "The antibody delivers a cell toxin directly to the tumour cell. Used in metastatic HER2-positive and HER2-low breast cancer.",
    "Przeciwciało dostarcza cytostatyk bezpośrednio do komórki guza. Stosowany w przerzutowym raku HER2-dodatnim i HER2-low."),
  t("Übelkeit, Müdigkeit, Haarausfall, Blutbildveränderungen. Wichtig: Lungenentzündung (ILD) — neuer Husten oder Atemnot sofort melden.",
    "Nausea, fatigue, hair loss, blood count changes. Important: lung inflammation (ILD) — report new cough or breathlessness immediately.",
    "Nudności, zmęczenie, wypadanie włosów, zmiany w morfologii. Ważne: śródmiąższowe zapalenie płuc (ILD) — nowy kaszel lub duszność zgłaszać natychmiast."))
m(t("Epirubicin / Doxorubicin", "Epirubicin / doxorubicin", "Epirubicyna / doksorubicyna"),
  t("Chemotherapie: Anthrazykline", "Chemotherapy: anthracyclines", "Chemioterapia: antracykliny"),
  t("Schädigen die Erbsubstanz sich teilender Zellen. Häufig kombiniert mit Cyclophosphamid (EC/AC), meist alle 2–3 Wochen als Infusion.",
    "Damage the DNA of dividing cells. Often combined with cyclophosphamide (EC/AC), usually as an infusion every 2–3 weeks.",
    "Uszkadzają DNA dzielących się komórek. Często łączone z cyklofosfamidem (EC/AC), zwykle wlew co 2–3 tygodnie."),
  t("Haarausfall, Übelkeit, Abfall der weißen Blutkörperchen (Infektgefahr), Schleimhautentzündung, roter Urin am Infusionstag, Herzbelastung.",
    "Hair loss, nausea, drop in white blood cells (infection risk), mouth sores, red urine on infusion day, strain on the heart.",
    "Wypadanie włosów, nudności, spadek białych krwinek (ryzyko infekcji), zapalenie błon śluzowych, czerwony mocz w dniu wlewu, obciążenie serca."))
m(same("Cyclophosphamid"), t("Chemotherapie: Alkylans", "Chemotherapy: alkylating agent", "Chemioterapia: lek alkilujący"),
  t("Vernetzt die Erbsubstanz der Tumorzellen. Meist Teil von EC/AC oder TC.",
    "Cross-links the DNA of tumour cells. Usually part of EC/AC or TC.",
    "Sieciuje DNA komórek nowotworowych. Zwykle część schematu EC/AC lub TC."),
  t("Übelkeit, Blutbildveränderungen, Haarausfall, Blasenreizung (viel trinken).",
    "Nausea, blood count changes, hair loss, bladder irritation (drink plenty).",
    "Nudności, zmiany w morfologii, wypadanie włosów, podrażnienie pęcherza (dużo pić)."))
m(t("Paclitaxel / Docetaxel", "Paclitaxel / docetaxel", "Paklitaksel / docetaksel"),
  t("Chemotherapie: Taxane", "Chemotherapy: taxanes", "Chemioterapia: taksany"),
  t("Hemmen die Zellteilung über das Zellskelett. Paclitaxel oft wöchentlich, Docetaxel alle 3 Wochen.",
    "Stop cell division by acting on the cell skeleton. Paclitaxel often weekly, docetaxel every 3 weeks.",
    "Hamują podział komórek, działając na cytoszkielet. Paklitaksel często co tydzień, docetaksel co 3 tygodnie."),
  t("Taubheit/Kribbeln in Händen und Füßen (Polyneuropathie), Nagelveränderungen, Haarausfall, Gelenkschmerzen, Wassereinlagerungen (Docetaxel).",
    "Numbness/tingling in hands and feet (neuropathy), nail changes, hair loss, joint pain, fluid retention (docetaxel).",
    "Drętwienie/mrowienie dłoni i stóp (neuropatia), zmiany paznokci, wypadanie włosów, bóle stawów, zatrzymanie płynów (docetaksel)."))
m(same("Carboplatin"), t("Chemotherapie: Platinverbindung", "Chemotherapy: platinum compound", "Chemioterapia: związek platyny"),
  t("Vernetzt die Erbsubstanz. Vor allem bei triple-negativem Brustkrebs und BRCA-Mutation, oft mit Paclitaxel.",
    "Cross-links DNA. Mainly in triple-negative breast cancer and BRCA mutation, often with paclitaxel.",
    "Sieciuje DNA. Głównie w raku potrójnie ujemnym i przy mutacji BRCA, często z paklitakselem."),
  t("Abfall von Blutplättchen und weißen Blutkörperchen, Blutarmut, Übelkeit.",
    "Drop in platelets and white blood cells, anaemia, nausea.",
    "Spadek płytek krwi i białych krwinek, niedokrwistość, nudności."))
m(same("Capecitabin"), t("Chemotherapie: Antimetabolit (Tablette)", "Chemotherapy: antimetabolite (tablet)", "Chemioterapia: antymetabolit (tabletka)"),
  t("Wird im Körper zu 5-FU umgewandelt. Tablette, z. B. nach der Operation wenn Tumorrest vorhanden oder bei Metastasen.",
    "Converted to 5-FU in the body. Tablet, e.g. after surgery when residual tumour remains, or for metastases.",
    "W organizmie przekształca się w 5-FU. Tabletka, np. po operacji przy chorobie resztkowej lub w chorobie przerzutowej."),
  t("Hand-Fuß-Syndrom (Rötung, Schmerzen an Handflächen/Fußsohlen), Durchfall, Müdigkeit.",
    "Hand-foot syndrome (redness, soreness of palms/soles), diarrhoea, fatigue.",
    "Zespół ręka-stopa (zaczerwienienie, bolesność dłoni/stóp), biegunka, zmęczenie."))
m(same("Pembrolizumab (Keytruda®)"), t("Immuntherapie: PD-1-Hemmer", "Immunotherapy: PD-1 inhibitor", "Immunoterapia: inhibitor PD-1"),
  t("Löst die Bremse des Immunsystems, damit es Tumorzellen angreift. Bei triple-negativem Brustkrebs zusammen mit Chemotherapie vor und nach der Operation.",
    "Releases the immune system’s brake so it attacks tumour cells. In triple-negative breast cancer together with chemotherapy before and after surgery.",
    "Zwalnia hamulec układu odpornościowego, aby atakował komórki guza. W raku potrójnie ujemnym razem z chemioterapią przed i po operacji."),
  t("Autoimmune Entzündungen möglich: Schilddrüse, Darm (Durchfall), Lunge, Leber, Haut. Neue Beschwerden immer melden.",
    "Can cause autoimmune inflammation: thyroid, bowel (diarrhoea), lungs, liver, skin. Always report new symptoms.",
    "Możliwe zapalenia autoimmunologiczne: tarczyca, jelita (biegunka), płuca, wątroba, skóra. Każdy nowy objaw zgłaszać."))
m(t("Palbociclib / Ribociclib / Abemaciclib", "Palbociclib / ribociclib / abemaciclib", "Palbocyklib / rybocyklib / abemacyklib"),
  t("CDK4/6-Hemmer", "CDK4/6 inhibitors", "Inhibitory CDK4/6"),
  t("Bremsen den Zellzyklus. Zusammen mit Antihormontherapie bei hormonrezeptor-positivem, HER2-negativem Brustkrebs (metastasiert; Abemaciclib und Ribociclib auch nach der OP bei hohem Risiko).",
    "Slow the cell cycle. Combined with anti-hormone therapy in HR-positive, HER2-negative breast cancer (metastatic; abemaciclib and ribociclib also after surgery when risk is high).",
    "Hamują cykl komórkowy. Razem z hormonoterapią w raku HR-dodatnim, HER2-ujemnym (przerzutowym; abemacyklib i rybocyklib także po operacji przy wysokim ryzyku)."),
  t("Abfall der weißen Blutkörperchen (regelmäßige Blutbilder), Müdigkeit, Durchfall (v. a. Abemaciclib), EKG-Kontrollen (Ribociclib), Leberwerte.",
    "Drop in white blood cells (regular blood counts), fatigue, diarrhoea (mainly abemaciclib), ECG checks (ribociclib), liver values.",
    "Spadek białych krwinek (regularna morfologia), zmęczenie, biegunka (głównie abemacyklib), kontrola EKG (rybocyklib), próby wątrobowe."))
m(same("Olaparib (Lynparza®)"), t("PARP-Hemmer", "PARP inhibitor", "Inhibitor PARP"),
  t("Verhindert die Reparatur von Erbgutschäden in Tumorzellen mit BRCA-Mutation. Tablette.",
    "Prevents DNA repair in tumour cells with a BRCA mutation. Tablet.",
    "Uniemożliwia naprawę DNA w komórkach guza z mutacją BRCA. Tabletka."),
  t("Übelkeit, Müdigkeit, Blutarmut.", "Nausea, fatigue, anaemia.", "Nudności, zmęczenie, niedokrwistość."))
m(t("Sacituzumab Govitecan (Trodelvy®)", "Sacituzumab govitecan (Trodelvy®)", "Sacytuzumab gowitekan (Trodelvy®)"),
  t("Antikörper-Wirkstoff-Konjugat (ADC)", "Antibody–drug conjugate (ADC)", "Koniugat przeciwciało–lek (ADC)"),
  t("Richtet sich gegen TROP-2 auf Tumorzellen. Bei vorbehandeltem metastasiertem triple-negativem und HR-positivem Brustkrebs.",
    "Targets TROP-2 on tumour cells. For previously treated metastatic triple-negative and HR-positive breast cancer.",
    "Skierowany przeciw TROP-2 na komórkach guza. W uprzednio leczonym przerzutowym raku potrójnie ujemnym i HR-dodatnim."),
  t("Abfall der weißen Blutkörperchen, Durchfall, Übelkeit, Haarausfall.",
    "Drop in white blood cells, diarrhoea, nausea, hair loss.",
    "Spadek białych krwinek, biegunka, nudności, wypadanie włosów."))
m(t("Zoledronsäure / Denosumab", "Zoledronic acid / denosumab", "Kwas zoledronowy / denosumab"),
  t("Knochenschutz", "Bone-protecting agents", "Leki chroniące kości"),
  t("Stärken die Knochen bei Knochenmetastasen oder Knochendichteverlust durch Aromatasehemmer; Zoledronsäure senkt nach den Wechseljahren auch das Rückfallrisiko.",
    "Strengthen bones in bone metastases or bone loss from aromatase inhibitors; zoledronic acid also lowers recurrence risk after menopause.",
    "Wzmacniają kości przy przerzutach do kości lub utracie masy kostnej po inhibitorach aromatazy; kwas zoledronowy po menopauzie zmniejsza też ryzyko nawrotu."),
  t("Grippeähnliche Beschwerden nach der Infusion, niedriges Kalzium; selten Kiefernekrose — vorher Zahnarzt, Zahnbehandlungen absprechen.",
    "Flu-like symptoms after infusion, low calcium; rarely jaw osteonecrosis — see a dentist first and discuss dental work.",
    "Objawy grypopodobne po wlewie, niski poziom wapnia; rzadko martwica kości szczęki — wcześniej wizyta u dentysty, zabiegi stomatologiczne konsultować."))

R = []
def r(titel, text, quelle):
    R.append({"kind": "research", "data": {"title": titel, "body": text, "source": quelle, "date": "2026-10-08", "seed": True}})

r(t("Krebsinformationsdienst (DKFZ)", "German Cancer Information Service (DKFZ)", "Niemiecka Służba Informacji o Raku (DKFZ)"),
  t("Unabhängige, verständliche Informationen des Deutschen Krebsforschungszentrums. Kostenloses Telefon 0800 420 30 40 und E-Mail-Dienst.",
    "Independent, easy-to-read information from the German Cancer Research Center. Free phone line 0800 420 30 40 (Germany) and e-mail service.",
    "Niezależne, przystępne informacje Niemieckiego Centrum Badań nad Rakiem. Bezpłatna infolinia 0800 420 30 40 (Niemcy) i porady e-mailowe."),
  "https://www.krebsinformationsdienst.de/brustkrebs")
r(t("Patientenleitlinie Brustkrebs (Leitlinienprogramm Onkologie)", "German patient guideline on breast cancer", "Niemieckie wytyczne dla pacjentów: rak piersi"),
  t("Die offizielle S3-Leitlinie in Patientensprache: Diagnose, Behandlung, Nachsorge. Gut, um ärztliche Empfehlungen einzuordnen.",
    "The official German S3 guideline in plain language: diagnosis, treatment, follow-up. Useful for putting doctors’ recommendations in context.",
    "Oficjalne niemieckie wytyczne S3 w języku dla pacjentów: diagnostyka, leczenie, kontrola po leczeniu. Pomaga zrozumieć zalecenia lekarzy."),
  "https://www.leitlinienprogramm-onkologie.de/patientenleitlinien/brustkrebs")
r(t("National Cancer Institute: Breast Cancer", "National Cancer Institute: Breast Cancer", "National Cancer Institute: rak piersi"),
  t("Umfangreiche englischsprachige Informationen (PDQ) zu Behandlung, Studien und Medikamenten.",
    "Comprehensive information (PDQ) on treatment, clinical trials and drugs.",
    "Obszerne informacje w języku angielskim (PDQ) o leczeniu, badaniach klinicznych i lekach."),
  "https://www.cancer.gov/types/breast")
r(t("Narodowy Instytut Onkologii (Polen)", "National Institute of Oncology (Poland)", "Narodowy Instytut Onkologii"),
  t("Polnisches Krebszentrum mit Informationen für Patientinnen auf Polnisch.",
    "Polish national cancer institute with patient information in Polish.",
    "Polski instytut onkologiczny z informacjami dla pacjentek po polsku."),
  "https://www.nio.gov.pl")

Path(__file__).with_name("seed.json").write_text(json.dumps(G + M + R, ensure_ascii=False, indent=1))
print(len(G), "Begriffe,", len(M), "Medikamente,", len(R), "Quellen")
