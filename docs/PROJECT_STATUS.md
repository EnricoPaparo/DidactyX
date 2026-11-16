# Stato del progetto e punto di ripresa

- **Aggiornamento:** 15 novembre 2026.
- **Stato del lavoro:** sviluppo sospeso su richiesta del docente, dopo il completamento dell'incremento 2.
- **Versione disponibile:** DidactyX 0.2.0 per macOS.
- **Ultimo commit applicativo:** `4519e1d` — progettazione annuale, revisione, versioni e PDF.
- **Branch:** `codex/macos-foundation`.
- **Pull request:** [PR #1](https://github.com/EnricoPaparo/DidactyX/pull/1), aperta in bozza; non è stata unita a `main`.

## Completato e utilizzabile

L'incremento 1 comprende app SwiftUI, raccolta dei programmi, titolo/classe/descrizione, brief libero e sezioni facoltative, salvataggio SQLite e impostazioni con stato reale dell'account Codex.

L'incremento 2 collega la generazione reale tramite l'account ChatGPT già connesso a Codex. Sono disponibili interpretazione del brief, progettazione e revisione delle UDA, progettazione e revisione delle lezioni previste, gestione di ore e progetti progressivi, controlli strutturali, rigenerazione completa, storico, interruzione/ripresa, revisione su richiesta ed export PDF del programma annuale.

Lo scheletro rimane in sola lettura. Il docente ne richiede la modifica attraverso il brief o una richiesta di rigenerazione; la nuova versione diventa corrente a completamento dei controlli. Le osservazioni del revisore rimangono consultive. Il brief modificato ma ancora da applicare è distinto dal contesto della versione salvata.

La descrizione operativa completa è in [ANNUAL_PLANNING.md](ANNUAL_PLANNING.md); il [Project Brief](PROJECT_BRIEF.md) rimane il riferimento dei requisiti di prodotto.

## Verifiche già concluse

- 20 test automatici e integrazione Swift con il motore incluso nell'app superati.
- Generazione reale su dati fittizi: anno di 66 ore, quattro UDA e 35 lezioni previste.
- Rigenerazione richiesta dall'interfaccia: circuiti anticipati rispetto a energia e calore, quattro UDA e 37 lezioni, ore conservate e prima versione immutata.
- Brief essenziale di 12 ore: quattro UDA e 15 lezioni con ipotesi esplicite sul contesto mancante.
- Collaudo nativo di storico, export, interruzione/ripresa, brief ancora da applicare e revisione consultiva.
- Due PDF annuali di 24 pagine ciascuno: tutte le 48 pagine renderizzate e controllate visivamente.
- Build release e firma locale ad hoc verificate sul Mac arm64 utilizzato per lo sviluppo.

Campioni e risultati sono conservati in [evidence/annual-planning/2026-11-15](evidence/annual-planning/2026-11-15/README.md). I collaudi usano archivi separati da quello personale; nessuna credenziale o identità dell'account è inclusa nelle evidenze.

## Prossima sessione: incremento 3

La prima attività è scegliere insieme al docente materia, classe e obiettivi del percorso pilota. I campioni di fisica e Python sono collaudi tecnici; non rappresentano una scelta del pilota.

Dopo questa scelta:

1. Definire il formato strutturato dei contenuti delle lezioni e i criteri di qualità disciplinare e didattica, comprese le fonti pertinenti al pilota.
2. Definire il recupero del contesto: contenuti effettivi delle lezioni precedenti, esempi, terminologia, concetti e posizione nel percorso, oltre ai metadati annuali.
3. Implementare generazione, eventuali contributi di più autori, ricomposizione e revisione delle lezioni.
4. Integrare lettore WebKit ed export PDF, verificando almeno due lezioni collegate anche con generazione fuori sequenza.

I contenuti completi delle lezioni non sono ancora implementati. Arricchimento visivo, mappe, esercitazioni, verifiche con varianti e adattamenti, feedback e recupero restano nel perimetro degli incrementi successivi del [piano di sviluppo](IMPLEMENTATION_PLAN.md). La priorità rimane la qualità didattica, con un'interfaccia minimale. Windows sarà valutato successivamente.

## Riferimenti operativi

- App locale: `dist/DidactyX.app`; il pacchetto include il runtime Python.
- Archivio personale predefinito: `~/Library/Application Support/DidactyX/library.sqlite3`, schema SQLite versione 2.
- Cartella PDF: configurabile nelle impostazioni dell'app.
- Build: `bash scripts/build_macos.sh`, con l'app chiusa.
- Controlli automatici e integrazione: `bash scripts/check_foundation.sh`.
- Collaudi reali facoltativi: `python3 scripts/check_planning_live.py`, con opzioni `--regenerate` oppure `--minimal`; consumano quota Codex.

Binari, archivi personali e risultati temporanei sono esclusi da Git. La distribuzione ad altri Mac e la notarizzazione non sono ancora state verificate. L'efficacia didattica in classe dovrà essere valutata con il docente sui contenuti del pilota.
