# Stato del progetto e punto di ripresa

- **Aggiornamento:** 18 novembre 2026; verifica e passaggio documentale, senza modifiche all'app.
- **Versione locale:** DidactyX 0.3.3 per macOS, build 6.
- **Stato:** punto 1 del consolidamento completato sul pilota: tre lezioni rigenerate integralmente e verificate senza patch editoriali successive.
- **Branch:** `codex/lesson-consolidation`, basato su `codex/didactic-benchmarks`.
- **Pull request:** [PR #5](https://github.com/EnricoPaparo/DidactyX/pull/5), aperta in bozza; consolidamento e risultati nel commit `6698c18`. È basata sulla [PR #4](https://github.com/EnricoPaparo/DidactyX/pull/4) del benchmark precedente. Nessun merge a `main`.

Per continuare in un'altra chat o con un altro modello, leggere il [passaggio completo alla prossima sessione](SESSION_HANDOFF.md): raccoglie decisioni di prodotto, contesto, implementazione, evidenze, limiti e proposta del prossimo incremento. Il docente preferisce «Astra 2» per la nuova sessione; il modello interno dell'app non è stato cambiato.

## Completato e utilizzabile

La fondazione comprende app SwiftUI, raccolta dei programmi, titolo/classe/descrizione, brief libero e strutturato, salvataggio SQLite e impostazioni con stato reale dell’account Codex. L’interfaccia conserva lo stile dark cyberpunk; il lettore dei materiali rimane chiaro.

La progettazione annuale usa l’account ChatGPT già collegato a Codex: interpretazione del brief, progettazione e revisione di UDA e lezioni, ore e progetti progressivi, controlli strutturali, rigenerazione completa, storico, interruzione/ripresa, revisione su richiesta e PDF del programma. Lo scheletro rimane in sola lettura; il brief aggiornato viene applicato con rigenerazione completa.

I contenuti di lezione usano il contesto della classe e i corpi reali dei materiali precedenti. Il workflow comprende progetto della spiegazione, uno o più autori con eventuale ricomposizione, revisore disciplinare e revisore della continuità, controlli di formato, riferimenti ed esempi Python. Sono disponibili brief facoltativo, lettore WebKit, versioni, ripresa, segnalazioni di riallineamento, revisione consultiva ed export PDF della versione selezionata.

Dettagli in [ANNUAL_PLANNING.md](ANNUAL_PLANNING.md), [LESSON_CONTENT.md](LESSON_CONTENT.md) e nel [Project Brief](PROJECT_BRIEF.md).

## Benchmark e tuning 0.3.2

Il docente ha delegato la costruzione dei benchmark e la scelta del campione. Il [rapporto conclusivo](evidence/didactic-benchmarks/2026-11-17/REPORT.md) documenta rubrica, confronto prima/dopo, casi avversi, errori mancati, iterazioni scartate, controlli e limiti.

La UDA fittizia di Python comprende L1 su variabili/input/conversioni, L2 su if/else e L3 di laboratorio. Il campione iniziale non supera il criterio sulle attività autonome: alcune consegne ripetono casi già interamente svolti. Dopo il tuning, il campione finale supera la soglia interna su ciascuna lezione e sulla UDA. Il revisore definitivo riconosce gli otto difetti mirati e rispetta i tre controlli predisposti; non si tratta di una misura di accuratezza generale.

Le evidenze preservano anche una prima rigenerazione scartata, il difetto reale sfuggito al primo revisore e un suggerimento infondato corretto fornendo al revisore la rappresentazione effettiva degli esempi. La distinzione tra stdout e trascrizione con eco viene corretta con patch editoriali esplicite nella versione 3; i risultati precedenti rimangono conservati. In quella fase le ultime istruzioni erano state provate soltanto su un paragrafo. Il consolidamento 0.3.3 chiude la successiva prova completa del workflow sullo stesso percorso. Nessun materiale viene descritto come privo di ogni difetto o come validato in classe.

I prompt dei ruoli sono versionati tramite fingerprint. La ripresa rifiuta istruzioni incompatibili, conservando i materiali completati. Il revisore consultivo usa lo stesso helper del lettore/PDF per ricostruire ciò che lo studente ha già visto. Le istruzioni generative del corpus e quelle del revisore definitivo sono tracciate separatamente. Il rapporto storico conserva la distinzione fra generazione e correzione editoriale.

## Consolidamento 0.3.3

Il [rapporto](evidence/lesson-consolidation/2026-11-17/REPORT.md) verifica la rigenerazione completa L1→L2→L3 con i prompt congelati. I contenuti pubblicati coincidono con l’uscita finale del workflow; non sono state applicate patch editoriali successive. Brief e scheletro annuale rimangono identici. Le revisioni automatiche ricevono controlli e trascrizioni effettive di ogni proposta, aggiornate anche dopo il primo revisore.

Il laboratorio richiede istruzioni prodotte individualmente e la scansione prevede una riduzione concreta del carico in caso di difficoltà, preservando lavoro individuale e restituzione. I tre requisiti specifici e la rubrica interna sono superati nel campione. Il test automatico nuovo verifica che il secondo revisore riceva la trascrizione del codice modificato dal primo. Gli undici risultati precedenti del revisore consultivo sono riutilizzati con identità verificata di input e istruzioni, senza presentarli come nuove chiamate AI.

## Campioni nell’app

Il nuovo programma **Python · UDA 1 · consolidamento 0.3.3** conserva tre lezioni, ciascuna con versione iniziale 1 e versione corrente 2 prodotta dal workflow completo. Importazione additiva, storico, lettore del laboratorio ed export sono verificati.

Il campione storico **Python · UDA 1 · benchmark didattico** contiene il percorso annuale e tre lezioni, ciascuna con versione iniziale, versione rigenerata e versione corretta editorialmente. La versione corrente è la 3, con dipendenze coerenti fra i contenuti. L’importazione è additiva e atomica; i programmi e le versioni precedenti rimangono conservati.

Il programma **Python · due lezioni collegate · pilota** resta disponibile. Le prove del primo traguardo sono conservate in [evidence/lesson-content/2026-11-16](evidence/lesson-content/2026-11-16/README.md); quelle annuali in [evidence/annual-planning/2026-11-15](evidence/annual-planning/2026-11-15/README.md).

## Verifiche

- 48 test automatici e integrazione Swift con il motore incluso superati.
- Generazione reale in ordine L1→L2→L3, corpi propedeutici effettivi, versioni precedenti immutate e riferimenti aggiornati.
- Controlli eseguibili, citazioni dei valutatori, struttura e oracoli ricontrollati dal collector del benchmark.
- PDF delle tre lezioni renderizzati integralmente e controllati visivamente; testi studente completi e raster del motore incluso identici a quelli ispezionati.
- Build release 0.3.3 e firma locale ad hoc verificate su macOS 26.7.2 arm64.
- Nuovo programma, storico delle versioni, lettore e disponibilità dell’export verificati nell’app.

I conteggi dei casi Python e delle pagine sono nel rapporto e nei file di evidenza. Le prove precedenti su più autori, interruzione/ripresa, generazione fuori sequenza, riallineamento e conservazione dei dati restano coperte dai test. Le sessioni dei valutatori usano lo stesso servizio generativo degli autori: non equivalgono a revisione umana indipendente o misure di apprendimento.

## Prossima attività

Proseguire con l’incremento 4: arricchimento visivo e mappe concettuali, poi percorsi di esercizi dedicati e verifiche basate su lezioni, mappe ed esercitazioni effettive, con varianti e adattamenti. Feedback, lezioni di recupero e prove di recupero rimangono nell’incremento 5. La UDA attuale è completa nei soli contenuti di lezione.

Mantenere il benchmark come regressione e ampliare successivamente il campione ad altre discipline e al riscontro del docente in classe. La notazione attuale è Unicode lineare; TeX e formule complesse richiedono lavoro dedicato. Windows sarà valutato dopo macOS.

Restano miglioramenti didattici circoscritti: rendere discriminanti anche le prove individuali obbligatorie contro un costo assegnato come costante, ampliare l’autonomia oltre la ricostruzione di una variante già spiegata e dimensionare i turni al computer in base alle dotazioni reali. Il rapporto 0.3.3 conserva questi rilievi; il superamento della soglia interna non certifica l’apprendimento in classe.

## Riferimenti operativi

- App locale: `dist/DidactyX.app`; runtime Python incluso.
- Archivio personale: `~/Library/Application Support/DidactyX/library.sqlite3`, schema 3.
- PDF: cartella configurabile; percorso predefinito `~/Documents/DidactyX/PDF`.
- Build, con app chiusa: `bash scripts/build_macos.sh`.
- Controlli senza generazione: `bash scripts/check_foundation.sh`.
- Raccolta del consolidamento: `python3 scripts/collect_lesson_consolidation.py --evidence docs/evidence/lesson-consolidation/2026-11-17 --data-dir tmp/lesson-consolidation/generated-db`, con i file del contratto congelato.
- Protocollo del benchmark e comandi: [benchmarks/didactic](../benchmarks/didactic/README.md).
- Collaudo reale di una UDA: `python3 scripts/check_didactic_uda_live.py --data-dir tmp/nuova-uda --output output/nuova-uda --targets L1 L2 L3`; consuma quota Codex.

Binari e archivi personali sono esclusi da Git; i dati delle evidenze sono fittizi. Distribuzione ad altri Mac e notarizzazione restano da verificare.
