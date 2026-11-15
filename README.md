# DidactyX

Motore didattico per progettare percorsi annuali e generare lezioni, materiali visivi, mappe concettuali, esercitazioni, verifiche e percorsi di recupero coerenti tra loro.

La priorità del progetto è una qualità didattica molto elevata, sostenuta da un workflow di generazione e revisione. La prima versione è un'applicazione locale per macOS, con interfaccia minimale in dark mode ed esportazione dei materiali in PDF.

## Documentazione

- [Project Brief](docs/PROJECT_BRIEF.md): visione, requisiti, workflow generativo, interfaccia e decisioni ancora aperte.
- [Verifica tecnica iniziale](docs/TECHNICAL_FEASIBILITY.md): prove reali su account Codex, generazione, revisione, immagini, ripresa e PDF, con evidenze e limiti.
- [Architettura macOS](docs/ARCHITECTURE.md): stack approvato, responsabilità dei componenti e organizzazione tecnica iniziale.
- [Piano di sviluppo](docs/IMPLEMENTATION_PLAN.md): incrementi, risultati verificabili e prossima attività.
- [Prima app macOS](docs/FOUNDATION_MACOS.md): utilizzo, costruzione, dati locali e verifiche della fondazione.

Il Project Brief è il riferimento principale per le decisioni di prodotto. Viene aggiornato nel repository insieme all'evoluzione del progetto; la cronologia Git conserva le modifiche.

## Stato del progetto

La prima app macOS include home dei programmi, brief libero e strutturato, salvataggio SQLite, impostazioni e lettura dello stato Codex. Il pacchetto locale si costruisce con `bash scripts/build_macos.sh` ed è disponibile in `dist/DidactyX.app`. Il prossimo incremento collega la progettazione annuale e il relativo PDF. WebKit per i materiali e il componente editoriale fanno parte dello stack approvato e verranno integrati con le funzioni didattiche. Il supporto Windows sarà valutato successivamente.
