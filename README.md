# DidactyX

Motore didattico per progettare percorsi annuali e generare lezioni, materiali visivi, mappe concettuali, esercitazioni, verifiche e percorsi di recupero coerenti tra loro.

La priorità del progetto è una qualità didattica molto elevata, sostenuta da un workflow di generazione e revisione. La prima versione è un'applicazione locale per macOS, con interfaccia minimale in dark mode ed esportazione dei materiali in PDF.

## Documentazione

- [Project Brief](docs/PROJECT_BRIEF.md): visione, requisiti, workflow generativo, interfaccia e decisioni ancora aperte.
- [Verifica tecnica iniziale](docs/TECHNICAL_FEASIBILITY.md): prove reali su account Codex, generazione, revisione, immagini, ripresa e PDF, con evidenze e limiti.
- [Architettura macOS](docs/ARCHITECTURE.md): stack approvato, responsabilità dei componenti e organizzazione tecnica iniziale.
- [Piano di sviluppo](docs/IMPLEMENTATION_PLAN.md): incrementi, risultati verificabili e prossima attività.

Il Project Brief è il riferimento principale per le decisioni di prodotto. Viene aggiornato nel repository insieme all'evoluzione del progetto; la cronologia Git conserva le modifiche.

## Stato del progetto

Brief di prodotto definito, prove di fattibilità concluse e stack macOS approvato: SwiftUI, WebKit, motore Python, SQLite e adattatore Codex App Server. ReportLab è la base iniziale dell'export PDF, da verificare sui casi editoriali più complessi. Il prossimo incremento è la fondazione locale dell'app; gli script sperimentali non costituiscono il motore definitivo. Il supporto Windows sarà valutato successivamente.
