# DidactyX

Motore didattico per progettare percorsi annuali e generare lezioni, materiali visivi, mappe concettuali, esercitazioni, verifiche e percorsi di recupero coerenti tra loro.

La priorità del progetto è una qualità didattica molto elevata, sostenuta da un workflow di generazione e revisione. La prima versione è un'applicazione locale per macOS, con interfaccia minimale in dark mode ed esportazione dei materiali in PDF.

## Documentazione

- [Stato e ripresa del lavoro](docs/PROJECT_STATUS.md): risultati disponibili e prossime attività.
- [Passaggio alla prossima sessione](docs/SESSION_HANDOFF.md): contesto completo, decisioni del docente, evidenze, limiti e indicazioni per continuare anche con un altro modello.
- [Project Brief](docs/PROJECT_BRIEF.md): visione, requisiti, workflow generativo, interfaccia e decisioni ancora aperte.
- [Verifica tecnica iniziale](docs/TECHNICAL_FEASIBILITY.md): prove reali su account Codex, generazione, revisione, immagini, ripresa e PDF, con evidenze e limiti.
- [Architettura macOS](docs/ARCHITECTURE.md): stack approvato, responsabilità dei componenti e organizzazione tecnica iniziale.
- [Piano di sviluppo](docs/IMPLEMENTATION_PLAN.md): incrementi, risultati verificabili e prossima attività.
- [Prima app macOS](docs/FOUNDATION_MACOS.md): utilizzo, costruzione, dati locali e verifiche della fondazione.
- [Progettazione annuale](docs/ANNUAL_PLANNING.md): generazione reale, revisioni, versioni, ripresa e PDF.
- [Contenuti delle lezioni](docs/LESSON_CONTENT.md): memoria dei contenuti effettivi, autori, revisori, lettore e PDF.
- [Benchmark didattico](benchmarks/didactic/README.md): rubrica, casi avversi, controlli e protocollo riproducibile per valutare contenuti e revisori.
- [Identità visiva](assets/brand/README.md): palette dark cyberpunk, logo vettoriale e icona macOS.

Il Project Brief è il riferimento principale per le decisioni di prodotto. Viene aggiornato nel repository insieme all'evoluzione del progetto; la cronologia Git conserva le modifiche.

## Stato del progetto

L'app macOS 0.3.3 include programmi, brief libero e strutturato, impostazioni Codex, progettazione annuale e contenuti completi delle lezioni. Autori e revisori separati usano il contesto della classe e i materiali precedenti effettivi. Sono disponibili storico, ripresa, revisione su richiesta, lettore WebKit ed esportazione PDF del programma e delle lezioni. I dati sono salvati in SQLite sul Mac.

Il primo traguardo dell'incremento 3 è un pilota inventato, autorizzato dal docente: due lezioni Python collegate, su variabili/input/conversioni e `if/else`. I campioni sono in [evidence/lesson-content/2026-11-16](docs/evidence/lesson-content/2026-11-16/README.md). La prima UDA è ora completa nei contenuti delle tre lezioni e valutata con [benchmark interno](docs/evidence/didactic-benchmarks/2026-11-17/REPORT.md). Il [consolidamento 0.3.3](docs/evidence/lesson-consolidation/2026-11-17/REPORT.md) verifica poi l’intero workflow senza correzioni editoriali successive, con scrittura individuale e riduzione del carico in caso di difficoltà. I materiali collegati restano successivi.

Il pacchetto locale si costruisce con `bash scripts/build_macos.sh` ed è disponibile in `dist/DidactyX.app`. I controlli si eseguono con `bash scripts/check_foundation.sh`. Il supporto Windows sarà valutato successivamente.
