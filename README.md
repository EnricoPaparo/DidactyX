# DidactyX

Motore didattico per progettare percorsi annuali e generare lezioni, materiali visivi, mappe concettuali, esercitazioni, verifiche e percorsi di recupero coerenti tra loro.

La priorità del progetto è una qualità didattica molto elevata, sostenuta da un workflow di generazione e revisione. La prima versione è un'applicazione locale per macOS, con interfaccia minimale in dark mode ed esportazione dei materiali in PDF.

## Documentazione

- [Project Brief](docs/PROJECT_BRIEF.md): visione, requisiti, workflow generativo, interfaccia e decisioni ancora aperte.
- [Verifica tecnica iniziale](docs/TECHNICAL_FEASIBILITY.md): prove reali su account Codex, generazione, revisione, immagini, ripresa e PDF, con evidenze e limiti.
- [Architettura macOS](docs/ARCHITECTURE.md): stack approvato, responsabilità dei componenti e organizzazione tecnica iniziale.
- [Piano di sviluppo](docs/IMPLEMENTATION_PLAN.md): incrementi, risultati verificabili e prossima attività.
- [Prima app macOS](docs/FOUNDATION_MACOS.md): utilizzo, costruzione, dati locali e verifiche della fondazione.
- [Progettazione annuale](docs/ANNUAL_PLANNING.md): generazione reale, revisioni, versioni, ripresa e PDF.

Il Project Brief è il riferimento principale per le decisioni di prodotto. Viene aggiornato nel repository insieme all'evoluzione del progetto; la cronologia Git conserva le modifiche.

## Stato del progetto

L'app macOS 0.2.0 include programmi, brief libero e strutturato, impostazioni Codex e progettazione annuale reale: UDA e lezioni con metadati, autori e revisori separati, rigenerazione completa, storico ed esportazione PDF. I dati sono salvati in SQLite sul Mac. Il pacchetto locale si costruisce con `bash scripts/build_macos.sh` ed è disponibile in `dist/DidactyX.app`.

Il prossimo incremento riguarda i contenuti completi delle lezioni e la continuità didattica tra essi. WebKit verrà integrato con il lettore dei materiali. Il supporto Windows sarà valutato successivamente.
