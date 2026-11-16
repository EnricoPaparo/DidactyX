# Stato del progetto e punto di ripresa

- **Aggiornamento:** 16 novembre 2026.
- **Stato del lavoro:** primo traguardo dell'incremento 3 completato; materiali pronti alla valutazione del docente.
- **Versione disponibile:** DidactyX 0.3.0 per macOS.
- **Branch:** `codex/lesson-content`, basato su `codex/macos-foundation`.
- **Base applicativa:** [PR #1](https://github.com/EnricoPaparo/DidactyX/pull/1), ancora in bozza e non unita a `main` alla verifica odierna. I nuovi contenuti sono in un branch separato.

## Completato e utilizzabile

La fondazione comprende app SwiftUI, raccolta dei programmi, titolo/classe/descrizione, brief libero e sezioni facoltative, salvataggio SQLite e impostazioni con stato reale dell'account Codex.

La progettazione annuale usa l'account ChatGPT già connesso a Codex: interpretazione del brief, progettazione e revisione delle UDA e delle lezioni previste, ore e progetti progressivi, controlli strutturali, rigenerazione completa, storico, interruzione/ripresa, revisione su richiesta e PDF del programma. Lo scheletro rimane in sola lettura; il brief aggiornato viene applicato mediante rigenerazione completa.

L'incremento 3 aggiunge contenuti completi con formato strutturato, contesto della classe e corpi effettivi delle lezioni precedenti. Comprende progetto della spiegazione, uno o più autori con eventuale ricomposizione, revisioni disciplinare e della continuità, controlli di formato, riferimenti e casi Python. Sono disponibili brief specifico facoltativo, lettore WebKit chiaro, versioni, ripresa, segnalazioni di riallineamento, revisione consultiva ed export PDF della versione selezionata. I materiali storici rimangono legati alla loro versione del percorso.

Dettagli in [ANNUAL_PLANNING.md](ANNUAL_PLANNING.md) e [LESSON_CONTENT.md](LESSON_CONTENT.md). Il [Project Brief](PROJECT_BRIEF.md) rimane il riferimento dei requisiti di prodotto.

## Primo traguardo disponibile

Il docente ha autorizzato la scelta di un esempio inventato. Il programma **Python · due lezioni collegate · pilota** è presente nell'app e contiene il percorso annuale di 24 ore e due lezioni complete:

1. **Variabili, input e conversioni:** nove sezioni, PDF di 20 pagine.
2. **Decidere con if ed else:** otto sezioni, PDF di 21 pagine.

Entrambe usano l'acquisto di quaderni con un budget. La seconda riceve il contenuto reale della prima e riprende nomi, prompt, dati ed esempi con cinque riferimenti a sezioni salvate. Dieci casi eseguibili per lezione hanno dato l'output atteso; tre blocchi illustrativi per lezione non sono dichiarati eseguiti. La revisione aggiuntiva di L2 propone una variazione facoltativa di un caso già risolto, senza applicarla automaticamente.

Campioni JSON, PDF, rapporto e risultati sono in [evidence/lesson-content/2026-11-16](evidence/lesson-content/2026-11-16/README.md). Nessuna credenziale o identità dell'account è inclusa nelle evidenze. L'importazione del pilota è additiva e atomica; non sovrascrive programmi esistenti.

## Verifiche concluse

- 36 test automatici e integrazione Swift con il motore incluso superati.
- Test di versioni immutabili, migrazione SQLite 2→3, memoria dei corpi reali, più autori, ripresa senza duplicazioni e rifiuto di contesti cambiati.
- Test di generazione fuori sequenza, disponibilità successiva dei prerequisiti e propagazione dei segnali di riallineamento.
- L1 generata realmente, interrotta e ripresa durante lo sviluppo; una sola versione finale pubblicata.
- L2 generata dall'interfaccia con il corpo effettivo di L1; revisione aggiuntiva dal pulsante **Revisiona**, contenuto invariato.
- Lettore nativo, navigazione tra lezioni, conservazione del brief facoltativo dopo chiusura, riapertura ed export dal pacchetto finale verificati.
- Tutti i 20 casi Python eseguibili ricontrollati nel motore congelato; 41 pagine PDF renderizzate e controllate visivamente.
- Build release, runtime incluso e firma locale ad hoc verificati su macOS 26.7.2 arm64.

Restano valide le prove dell'incremento 2: anno fittizio di 66 ore, rigenerazione completa dall'interfaccia con sequenza modificata, brief essenziale di 12 ore, storico, interruzione/ripresa e due PDF annuali di 24 pagine. Evidenze in [evidence/annual-planning/2026-11-15](evidence/annual-planning/2026-11-15/README.md).

## Prossima attività

Valutare insieme le due lezioni nell'app e nei PDF: profondità, correttezza, spiegazioni dei passaggi, ritmo, ripetizioni, esempi e continuità. Applicare i riscontri al motore e al formato editoriale, poi estendere il collaudo a una UDA completa.

Arricchimento visivo, mappe, percorsi di esercizi, verifiche con varianti e adattamenti, feedback e recupero restano negli incrementi successivi del [piano](IMPLEMENTATION_PLAN.md). L'efficacia didattica richiede valutazione del docente e uso in classe. La notazione attuale è Unicode lineare: TeX e formule complesse non sono implementati. Windows sarà valutato successivamente.

## Riferimenti operativi

- App locale: `dist/DidactyX.app`; include il runtime Python.
- Archivio personale: `~/Library/Application Support/DidactyX/library.sqlite3`, schema 3.
- PDF: cartella configurabile nelle impostazioni; il percorso predefinito è `~/Documents/DidactyX/PDF`.
- Build: `bash scripts/build_macos.sh`, con l'app chiusa.
- Controlli senza generazione: `bash scripts/check_foundation.sh`.
- Collaudo reale delle lezioni: `python3 scripts/check_lessons_live.py --data-dir tmp/nuovo-collaudo-lezioni`; consuma quota Codex.
- Collaudi annuali facoltativi: `python3 scripts/check_planning_live.py`, opzioni `--regenerate` o `--minimal`; consumano quota Codex.

Binari e archivi personali sono esclusi da Git. Distribuzione ad altri Mac e notarizzazione restano da verificare.
