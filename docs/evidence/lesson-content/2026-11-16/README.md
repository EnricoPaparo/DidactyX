# Due lezioni collegate · pilota fittizio

Collaudo reale del 16 novembre 2026, app macOS 0.3.0. Il docente ha delegato la scelta del pilota: informatica per una seconda superiore fittizia, studenti di 15–16 anni senza conoscenze pregresse di programmazione. Il percorso annuale di 24 ore comprende quattro UDA e 17 lezioni previste. Sono sviluppate le prime due lezioni teoriche, di due ore ciascuna.

| Materiale | Sviluppo | PDF |
| --- | --- | --- |
| L1 · Variabili, input e conversioni | 9 sezioni, dall'acquisto di quaderni al programma completo | [20 pagine](lesson-01-variabili.pdf) |
| L2 · Decidere con if ed else | 8 sezioni, dallo stesso programma alla decisione sul budget | [21 pagine](lesson-02-condizioni.pdf) |

## Evidenze

- [annual-plan.json](annual-plan.json): versione del percorso generato realmente dal brief fittizio.
- [lesson-L1.json](lesson-L1.json) e [lesson-L2.json](lesson-L2.json): versioni canoniche complete con controlli, fonti, contesto applicato e note per il docente.
- [review-L2.json](review-L2.json): rapporto aggiuntivo richiesto dall'interfaccia, consultivo e non applicato automaticamente.
- [results.json](results.json): riepilogo verificabile delle prove.

L1 è stata generata dal motore reale. Durante lo sviluppo è stata interrotta e ripresa due volte, riusando i passaggi già salvati e pubblicando una sola versione finale. L2 è stata avviata dal pulsante dell'app: il suo contesto comprende il corpo effettivo di L1. Cinque richiami identificano sezioni e versione reali; nomi, prompt e tre acquisti sono mantenuti coerenti. La revisione aggiuntiva suggerisce un caso numerico nuovo per una prova più autonoma, senza modificare automaticamente il contenuto.

Dieci casi eseguibili per lezione hanno prodotto l'output atteso, anche nel motore incluso nel pacchetto finale. Tre blocchi per lezione sono esplicitamente illustrativi, errati o incompleti e non vengono dichiarati eseguiti. Nei PDF e nel lettore le trascrizioni includono i dati digitati; note interne e rapporto di revisione restano nell'app. Tutte le 41 pagine esportate sono state renderizzate e controllate visivamente. Il testo estratto conserva titoli e contenuti dei blocchi; il codice mantiene i rientri.

Sono passati 36 test automatici e l'integrazione Swift con il motore incluso. I casi automatici coprono anche generazione fuori sequenza, arrivo successivo dei prerequisiti, dipendenze diventate obsolete, più autori, versioni, migrazione, ripresa e revisione immutabile. Questi casi usano generatori controllati: non sono ulteriori prove reali con il modello.

Il pilota è stato installato anche nell'archivio personale dell'app, con nuovi identificativi e riferimenti ricondotti alle versioni importate, senza sovrascrivere altri programmi. Sono state aperte entrambe le lezioni e verificato l'export. Questi file contengono soltanto il contesto scolastico inventato; archivi SQLite, credenziali, identità dell'account e checkpoint delle sessioni sono esclusi da Git.

## Riprodurre le prove

`bash scripts/build_macos.sh` costruisce l'app; `bash scripts/check_foundation.sh` esegue i controlli senza chiamate AI.

`python3 scripts/check_lessons_live.py --data-dir tmp/nuovo-collaudo-lezioni` genera realmente le prime due lezioni del percorso salvato, in un archivio nuovo. **Consuma quota Codex** e non modifica l'archivio personale. I risultati possono differire dai campioni.

Con l'app chiusa, `python3 scripts/install_lesson_pilot.py --data-dir CARTELLA_ARCHIVIO --annual docs/evidence/lesson-content/2026-11-16/annual-plan.json --lessons docs/evidence/lesson-content/2026-11-16/lesson-L1.json docs/evidence/lesson-content/2026-11-16/lesson-L2.json` importa i materiali già salvati senza chiamate AI. L'importazione è atomica, aggiunge un programma e rifiuta una seconda installazione con lo stesso titolo.

## Valutazione ancora necessaria

Il pilota rende valutabile il primo traguardo; non certifica la sostituzione del libro di testo o l'efficacia in classe. Profondità, ritmo, accessibilità e adeguatezza al gruppo reale richiedono il riscontro del docente. Mappe, arricchimento visivo, percorsi di esercizi, verifiche e recupero appartengono agli incrementi successivi. La notazione matematica attuale è Unicode lineare, senza TeX. La distribuzione su altri Mac e Windows non è stata collaudata.
