# Passaggio alla prossima sessione · DidactyX

- **Aggiornamento:** 18 novembre 2026, Europe/Rome.
- **Scopo:** conservare il contesto della conversazione, le decisioni concordate e lo stato verificato, anche cambiando modello o chat.
- **Preferenza del docente:** proseguire la prossima sessione con «Astra 2», anziché Sol. È una preferenza per la sessione di sviluppo; non equivale a una modifica del modello usato internamente dall'app.
- **Snapshot di partenza:** app macOS 0.3.3, build 6; consolidamento delle tre lezioni concluso. Questo documento non introduce nuove funzionalità né un cambio di stack.

## 1 Come riprendere

Aprire il progetto `/Users/enrico/Documents/ChatGPT/DidactyX` e leggere, in ordine:

1. Questo file, per il contesto e le decisioni da preservare.
2. [PROJECT_STATUS.md](PROJECT_STATUS.md), per lo stato operativo e i comandi.
3. [PROJECT_BRIEF.md](PROJECT_BRIEF.md), riferimento autorevole dei requisiti di prodotto.
4. [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md), per distinguere incrementi conclusi e ancora da realizzare.
5. [ARCHITECTURE.md](ARCHITECTURE.md) e [LESSON_CONTENT.md](LESSON_CONTENT.md), prima di intervenire sul motore o sui materiali.
6. [Rapporto 0.3.3](evidence/lesson-consolidation/2026-11-17/REPORT.md), prima di cambiare prompt, rubriche o dichiarazioni sulla qualità.

Controllare `git status --short --branch` e la cronologia prima di modificare i file. Al momento del passaggio il branch è `codex/lesson-consolidation`, basato su `codex/didactic-benchmarks`. La [PR #5](https://github.com/EnricoPaparo/DidactyX/pull/5) è in bozza, basata sulla [PR #4](https://github.com/EnricoPaparo/DidactyX/pull/4), e non è stato effettuato un merge a `main`. Questi sono dati del passaggio: ricontrollarli se il repository è avanzato.

La richiesta più recente riguarda **la conservazione del contesto**, non l'avvio dell'incremento 4. La prossima attività di sviluppo proposta e registrata è arricchimento visivo e mappe concettuali. Ripartire dalla nuova richiesta del docente, senza ripetere il consolidamento già concluso.

## 2 Obiettivo e rapporto con Schoolforge

DidactyX nasce da alcuni concetti di Schoolforge, ma il cuore del progetto è un motore capace di produrre contenuti di qualità didattica molto elevata, autosufficienti e potenzialmente sostitutivi del libro di testo. Non basta completare una chiamata AI o produrre molte pagine: servono correttezza, spiegazioni senza salti, progressione, attività, continuità, valutazione e recupero.

L'innovazione principale rispetto al punto di partenza descritto dal docente è la **progettazione annuale a monte**, articolata in UDA e lezioni, e la coerenza reale fra i materiali che ne derivano. Il codice di Schoolforge non è una dipendenza approvata né una fonte da presumere disponibile: i riferimenti nella conversazione descrivono esigenze del docente.

La complessità deve stare nel motore, non nell'interfaccia. Il docente vuole un'app personale, minimale ed efficiente; prende i PDF prodotti e li distribuisce agli studenti con i propri canali. Niente portale studenti, registro, hosting, gestione scolastica estesa o sdoppiamento obbligatorio fra versione docente e studente.

## 3 Decisioni di prodotto da non perdere

### Brief, autonomia e controllo del docente

- Il brief iniziale può essere libero, disordinato o strutturato. Comprende scuola/indirizzo/materia/classe/età, profilo umano degli studenti, conoscenze iniziali, traguardi e competenze, concetti obbligatori o facoltativi, ore, laboratorio, strumenti e preferenze.
- Il docente può indicare anche soltanto punto di partenza e punto di arrivo. Il motore assume il resto in modo ragionevole, rendendo riconoscibili le ipotesi. Non imporre un questionario per tutti i dati mancanti.
- Più indicazioni significa più vincoli; meno indicazioni significa maggiore autonomia generativa.
- Lezioni, immagini, mappe, esercitazioni e verifiche hanno un brief specifico **facoltativo**. Il contesto della classe continua a valere; le sezioni pertinenti possono essere recuperate separatamente.
- Le richieste esplicite del docente prevalgono sulle preferenze pedagogiche predefinite. Esempio vincolante: «tre esercizi difficilissimi e senza spiegazioni» deve produrre esattamente quel materiale. Il revisore può avvertire e proporre un adattamento, senza modificare di nascosto numero, difficoltà o spiegazioni.
- Salvare il nuovo brief non applica automaticamente le nuove indicazioni al percorso corrente. Distinguere brief salvato e contesto applicato.

### Scheletro annuale

- Prima si genera il piano con UDA, lezioni e metadati, **senza i corpi delle lezioni**.
- UDA e lezioni dello scheletro non si modificano manualmente. Una richiesta strutturale aggiorna il brief e avvia la **rigenerazione completa dell'intero scheletro**, con revisione, per conservare l'asse didattico.
- Il piano considera prerequisiti, obiettivi, conoscenze, abilità, competenze, contenuti, ore e valutazione; non presumere un unico modello «ministeriale» universale.
- Teoria e laboratorio devono essere progettati insieme. Sono previsti progetti progressivi anche attraverso più UDA e lungo l'anno, con tappe che concretizzano le competenze teoriche.
- Evitare doppi conteggi delle ore. Prevedere anche esercitazioni, verifiche, recupero e margine per imprevisti.
- Le versioni precedenti rimangono disponibili. Il piano vecchio non viene sostituito da una generazione interrotta; i materiali vecchi non diventano automaticamente coerenti con il piano nuovo.

### Contenuti e continuità

- Le lezioni devono accompagnare realmente lo studente: riutilizzare spiegazioni, esempi, terminologia e concetti dei **corpi effettivi precedenti**, non soltanto titoli o metadati della propria UDA.
- Distinguere quanto è pianificato, quanto è stato generato e quanto è stato effettivamente insegnato/appreso. Quest'ultimo richiede feedback del docente.
- Il motore può assegnare spiegazioni corpose a più autori e ricomporle. Nessun tetto arbitrario di parole o riduzione silenziosa della completezza per risparmiare lavoro. Più agenti e più testo non sono di per sé prove di qualità.
- I materiali devono permettere studio autonomo; esempi, soluzioni e aiuti devono comparire nell'ordine coerente con il tentativo richiesto.

### Immagini, mappe, esercitazioni e prove

- Un autore visivo analizza la lezione, propone e applica immagini o schemi utili; un revisore controlla significato, correttezza, leggibilità, inserimento nel testo e PDF. Stile coerente fra materiali del programma.
- Una mappa concettuale deve esprimere **concetti e relazioni semantiche**, non essere soltanto una lista, un riassunto in riquadri o una sequenza di operazioni. Uno schema procedurale può essere utile, ma è un materiale distinto.
- Le mappe devono poter rispondere ai bisogni descritti dal docente, anche DSA e studenti con disabilità, senza un adattamento uniforme dedotto dall'etichetta.
- Esercitazioni dedicate: svolte → guidate con aiuti decrescenti → autonome, con soluzioni gestite secondo il brief. Il docente può richiedere una progressione diversa.
- Le verifiche devono utilizzare automaticamente **lezioni, esercitazioni e mappe pertinenti realmente disponibili**, nelle versioni coerenti. Non ignorare mappe/esercizi esistenti e non inventare attività svolte. La loro assenza non impedisce una prova basata sulle fonti esistenti.
- Mini brief della verifica: ambito, concetti/obiettivi, durata, numero/tipo di quesiti, difficoltà, numero N di varianti, adattamenti.
- N varianti possono cambiare ordine oppure dati/formulazioni mantenendo gli stessi concetti. Il revisore deve verificare comparabilità di difficoltà, carico e tempi, non solo il riordino, e mantenere associate le soluzioni corrette.
- Requisito esplicito: prove per **obiettivi minimi**, obiettivi personalizzati e adattamenti richiesti per DSA/disabilità. Più tempo e domande facoltative sono opzioni distinte, combinabili; non ridurre automaticamente gli obiettivi per il solo fatto che uno studente è DSA.
- Lezioni, mappe, esercizi, prove e immagini hanno autori/revisori specializzati. Ogni contenuto deve avere **Revisiona**; il docente può mantenere il risultato o richiedere l'applicazione delle proposte.
- Distinguere errori oggettivi da raccomandazioni didattiche consultive. Una raccomandazione non annulla una scelta esplicita del docente. I controlli tecnici non completati non vanno presentati come revisioni riuscite.

### Recupero: chiusura del ciclo

- Per ogni UDA il docente può descrivere, con un breve feedback, cosa non è stato capito nella verifica.
- Il motore deve generare una o più **lezioni aggiuntive**, con un altro approccio, esempi e rappresentazioni differenti o ritmo più lento; una semplice parafrasi non basta.
- Possibili mappe/esercizi mirati, revisori dedicati e verifica di recupero basata anche sui nuovi materiali. Il feedback successivo può avviare un altro ciclo.
- Le lezioni aggiuntive sono collegate all'UDA ma **escluse dall'export del programma annuale**. Restano consultabili ed esportabili come materiali.
- L'esclusione dal programma esportato non rende illimitato il tempo di recupero; non modificare implicitamente il calendario annuale.

### UI, PDF e piattaforma

- Home essenziale con tutti i programmi, titolo, classe e descrizione; un clic apre il programma. Piccole impostazioni per account Codex, stato/quota quando disponibili e destinazione dei PDF.
- Dark mode minimale, futuristica/cyberpunk. L'identità visiva è già stata rivista: [assets/brand](../assets/brand/README.md), `Theme.swift` e `BrandArtwork.swift`. Non riaprire il redesign senza una nuova esigenza.
- **I contenuti restano chiari e semplici**, su pagina leggibile: non trasferire l'estetica scura/terminale nel testo o nei PDF.
- PDF fondamentale per ogni materiale; export del programma disponibile dallo scheletro, con UDA/metadati e lezioni/metadati, anche senza contenuti sviluppati. Esportare la versione selezionata senza rigenerazione AI.
- Prima macOS per l'uso personale del docente; Windows solo successivamente. Non allargare ora il progetto per inseguire la portabilità della UI.

## 4 Stack e implementazione effettivi

| Area | Implementazione attuale / punti di ingresso |
| --- | --- |
| App | SwiftUI; `macos/Sources/DidactyX/`; `Views.swift`, `AppModel.swift`, `AnnualPlanView.swift`, `LessonView.swift`, `LessonModel.swift`, `SettingsPanel.swift`. |
| Lettore | WKWebView; HTML locale generato dagli stessi blocchi canonici del PDF; niente script o librerie remote nel lettore. |
| Collegamento locale | Processo Python incluso nell'app, JSON a righe su stdin/stdout; `EngineClient.swift`, `engine/runner.py`, `engine/didactyx_engine/server.py`, `schemas/local-rpc.schema.json`. |
| Archivio | SQLite schema 3; `store.py`, `planning_store.py`, `lesson_store.py`; versioni, dipendenze, revisioni e checkpoint persistenti. |
| Piano annuale | `planning.py`, `planning_schema.py`, `schemas/annual-plan.schema.json`; interpretazione → autore UDA → revisore UDA → autore lezioni → revisore lezioni/percorso → controlli e pubblicazione. |
| Corpi delle lezioni | `lessons.py`, `lesson_prompts.py`, `lesson_schema.py`, `schemas/lesson-content.schema.json`; progetto esplicativo → autore/i → eventuale curatore → disciplina → continuità → controlli/correzioni. |
| Esempi e fonti | `example_checks.py`, `example_runner.py`, riferimenti forniti in `engine/didactyx_engine/assets/references/`; il pilota è Python. |
| Rendering | `lesson_render.py`, `plan_pdf.py`; ReportLab, font inclusi; formule lineari Unicode. TeX e formule complesse ancora da implementare. |
| Integrazione generativa | `codex.py` per stato account e `generation.py` per sessioni isolate dei ruoli, tramite Codex App Server e login ChatGPT già presente. |
| Verifiche | `tests/`, `scripts/check_foundation.sh`, collector e script live distinti sotto `scripts/`. |

Il generatore attuale usa ruoli in sessioni distinte con `effort: high`, output strutturato, nessun modello esplicitamente fissato nel codice e tool disabilitati, compresa `features.image_generation=false`. La fattibilità delle immagini è stata provata a parte: il modulo visivo di prodotto è ancora da integrare. La scelta «Astra 2» per la prossima chat non autorizza a dichiarare che i benchmark storici siano stati eseguiti con quel modello o a cambiarne retroattivamente i manifest.

È implementata una sola attività contemporanea per programma. Le versioni e il checkpoint finale vengono pubblicati atomicamente; una ripresa non duplica i risultati già salvati. Se cambiano prompt, piano o fonti, la ripresa rileva l'incompatibilità. Le dipendenze obsolete segnalano il riallineamento, senza riscrivere silenziosamente l'archivio.

L'API motore supporta batch di lezioni; l'interfaccia attuale genera una lezione alla volta. Più autori/ricomposizione sono implementati e coperti dai test; **nel batch reale 0.3.3 è stato usato un solo autore per lezione**. Non confondere possibilità architetturali con esecuzioni effettivamente osservate.

**Revisiona attuale:** produce un rapporto consultivo senza alterare il contenuto. Il docente può richiedere rigenerazione con i suggerimenti. Il requisito generale si estenderà ai materiali ancora mancanti; non dichiararli già implementati.

## 5 Account, quota e immagini: contesto delle prove

Il docente ha richiesto uso locale con la disponibilità del proprio account Codex/ChatGPT, evitando hosting e gestione di API key. Le prove e l'app hanno riutilizzato il login esistente: non sono state create chiavi né attivati servizi alternativi a consumo. Le credenziali restano gestite da Codex; non copiarle nei documenti, nei dati di prova o nel repository.

La prova tecnica del 15 novembre ha verificato testo strutturato, revisione, continuità, una piccola mappa, un PNG nativo reale, interruzione/ripresa e PDF. Si tratta di **fattibilità**, non dell'implementazione completa dei materiali visivi. Dettagli e ambiente storico in [TECHNICAL_FEASIBILITY.md](TECHNICAL_FEASIBILITY.md) e `experiments/feasibility/`.

È stata osservata una differenza fra il tool immagini nativo dell'App Server con login gestito e la via Sign in with ChatGPT/Responses descritta allora. Non presumere che le vie siano intercambiabili, né che il catalogo dei modelli dimostri l'accesso reale a ciascuno. Se si riprende questo tema, controllare implementazione e capacità correnti; i riferimenti datati non sono garanzie future. Nuovo accesso, cambio account, distribuzione e compatibilità di altre installazioni restano da verificare. Le impostazioni attuali leggono lo stato dell'accesso gestito da Codex.

Locale non significa generazione offline o quota illimitata: consultazione ed export dei materiali salvati sono locali; la generazione usa il servizio. Un limite del servizio deve conservare il lavoro e consentire la ripresa, senza ridurre di nascosto qualità o completezza.

## 6 Ultimo lavoro concluso: consolidamento 0.3.3

Il «punto 1» concluso nella sessione precedente significava **rigenerare integralmente le tre lezioni con gli ultimi prompt, rafforzare produzione individuale e flessibilità dei tempi, ripetere il benchmark**. Non significa «prima fase ancora da sviluppare» né «modulo mappe già completato».

### Modifiche tecniche e didattiche

- `lesson_prompts.py`: produzione individuale reale di istruzioni quando richiesta dagli obiettivi, tentativo prima della soluzione, percorso ridotto concreto che preservi lavoro individuale e restituzione entro le ore.
- `lessons.py`: ogni revisore automatico riceve `checks` e `visible_examples` ricavati dalla **proposta corrente**. Dopo una modifica disciplinare, il revisore della continuità riceve controlli e trascrizioni ricalcolati sul corpo corretto. Le fasi già completate restano riutilizzabili.
- `tests/test_lessons.py`: prova che il codice modificato dal primo revisore produca la nuova trascrizione fornita al successivo.
- `scripts/collect_lesson_consolidation.py`: verifica freeze, identità di brief/piano, versione dei valutatori, citazioni, riferimenti e uguaglianza tra corpi pubblicati e ultimo risultato del workflow.
- App portata a 0.3.3/build 6. Contratti generali di priorità del docente e revisore consultivo non modificati dal consolidamento.

### Metodo e risultati

Campione **fittizio scelto dall'assistente su delega del docente**: informatica, seconda superiore, tre lezioni della stessa UDA: L1 variabili/input/conversioni, L2 `if/else`, L3 laboratorio. Non rappresenta la descrizione di una classe reale del docente.

Rigenerazione L1→L2→L3 in archivio separato, con brief e scheletro invariati e corpi nuovi usati come contesto successivo. Ogni corpo pubblicato coincide con l'uscita finale del workflow, comprese le correzioni dei revisori automatici, **senza patch editoriali successive**. Versioni baseline conservate.

| Evidenza | Risultato verificato |
| --- | --- |
| Test software | 48 test automatici superati; integrazione Swift con motore incluso superata. |
| Esempi | 24 casi Python eseguiti, corrispondenti a stdout e trascrizione attesi; altri 8 blocchi illustrativi non dichiarati eseguiti. |
| PDF | L1 20 pagine, L2 20, L3 23: tutte le 63 pagine renderizzate e controllate visivamente; 939 stringhe studente controllate senza assenze. |
| Motore incluso | Raster PDF identici a quelli ispezionati dal sorgente; casi ricontrollati; firma locale ad hoc verificata. |
| Benchmark conservativo | L1 96,25; L2 100; L3 90; UDA 90/100. Tutte le soglie numeriche e i tre requisiti specifici superati. |
| App nativa | Nuovo programma aperto, laboratorio letto, versioni 1 e 2 consultate e PDF esportato con messaggio «PDF salvato». |

Rubrica invariata: correttezza 25%, spiegazione 20%, continuità 15%, attività/aiuti 15%, comprensione/trasferimento vicino 15%, fattibilità/accessibilità 10%. Soglie: almeno 3/4 per criterio, almeno 75/100, nessuna criticità grave. Si usa il **minimo per criterio** fra due valutatori, non una media favorevole.

La UDA iniziale 0.3.1 aveva 86,25 ma non superava la soglia sul criterio attività (2/4). La 0.3.2 rigenerata aveva 87,5; la 0.3.2 **corretta editorialmente** 93,75; la 0.3.3 integralmente rigenerata 90. Non dichiarare che ogni punteggio sia migliorato o confondere i 93,75 con una generazione senza patch.

Gli undici casi precedenti del revisore consultivo sono stati **riutilizzati**, con identità verificata di istruzioni e input; non sono undici nuove chiamate. Gli autori e i giudici usano lo stesso servizio: ruoli distinti non equivalgono a una revisione umana esterna, a prove di apprendimento o a validazione generale di tutte le discipline e dei profili DSA/disabilità.

### Risultato concreto del laboratorio e limiti da conservare

L3 richiede un file personale `acquisto_personale.py`, con acquisizioni/conversioni, calcolo della spesa, confronto `>` e messaggi collocati nei rami. Lavoro, previsioni, esecuzioni, traccia e spiegazione sono prodotti prima della soluzione. Il confronto era già spiegato in L2: è ricostruzione con aiuti ridotti, non un trasferimento logico interamente nuovo.

Scansione 120 minuti: S1 10, S2 10, S3 20, S4 15, S5 15, S6 10, S7 25, S8 15. In caso di difficoltà S1/S2 acquistano cinque minuti ciascuna, S5/S6 ne cedono cinque ciascuna; S7 individuale e S8 feedback restano protette. I tempi sono stimati, non osservati in classe.

Limiti minori dichiarati, senza interventi successivi per nasconderli:

- Le due prove individuali obbligatorie mantengono spesa 7,5: non rilevano da sole un costo impostato come costante. Una prova discriminante è presente nell'autocontrollo facoltativo; un miglioramento futuro può renderla obbligatoria.
- In L1 input/conversioni sono ancora sostenuti dal modello, mentre il prodotto individuale osserva soprattutto calcolo e stampe.
- I turni su PC condivisi sono previsti, ma non dimensionati numericamente rispetto alle dotazioni reali.
- Il campione non misura apprendimenti, tempi reali, continuità su un intero anno o generalizzazione ad altre materie; il modello non è fissato e le generazioni non sono deterministiche.

Questi rilievi **non riaprono automaticamente il punto concluso**. Per nuove modifiche tracciarne l'effetto senza riscrivere i risultati storici.

### Evidenze e storia Git

Raccolta autorevole: [evidence/lesson-consolidation/2026-11-17](evidence/lesson-consolidation/2026-11-17/REPORT.md). Include protocollo preregistrato, `prompt-freeze.json`, materiali `generated/`, giudizi `audit/`, `acceptance.json`, `results.json`, `reviewer-regression-reuse.json`, `pdf-qa.json`, `frozen-code-checks.json`, `software-verification.json`, `app-sample.json` e tre PDF finali sotto `pdf/`.

Fingerprint storico dei prompt: `didactic-v2-a0632f90c6a5`. Commit principali:

- `f3e1421`: prompt, contesto dei revisori, test e protocollo/freeze.
- `19553b9`: collector e report durante la generazione, senza cambi al nucleo congelato.
- `6698c18`: materiali finali, prove, report e documentazione.
- `69d9c13`: collegamento alla PR #5 e punto di ripresa, ultimo commit prima di questo passaggio documentale.

I report delle prove del 15/16/17 novembre restano storici. Non sovrascrivere corpus, PDF, giudizi o freeze per farli sembrare risultati ottenuti con codice nuovo.

## 7 Ambiente locale e comandi

Percorsi sul Mac attuale:

- Repository: `/Users/enrico/Documents/ChatGPT/DidactyX`.
- App già costruita: `dist/DidactyX.app`.
- Dati personali: `~/Library/Application Support/DidactyX/library.sqlite3`, schema 3.
- PDF dell'app: destinazione configurabile, predefinita `~/Documents/DidactyX/PDF`.
- Ambiente Python di build già usato: `tmp/packaging-venv/bin/python`, Python 3.12.14.
- Archivio separato dell'ultima prova: `tmp/lesson-consolidation/generated-db`.

L'app contiene tre programmi conservati: **Python · UDA 1 · consolidamento 0.3.3** (versioni 1/2, corrente 2), **Python · UDA 1 · benchmark didattico** (versioni 1/2/3, corrente 3 con patch editoriali dichiarate), **Python · due lezioni collegate · pilota**. L'importazione è stata additiva; non eliminare o sovrascrivere questi programmi per nuove prove.

`tmp/`, `output/`, `dist/`, `.build/`, ambienti e dati personali sono esclusi da Git. Su un altro computer non presumere che esistano. Il repository conserva le evidenze fittizie, non login e archivio personale. Ambiente verificato: macOS 26.7.2 arm64; `Package.swift` dichiara macOS 14, ma questo **non** equivale a una verifica su tutti i Mac da quella versione.

Comandi dalla radice del repository:

```sh
# Stato iniziale
git status --short --branch
git log -5 --oneline

# Test senza nuove chiamate AI; include integrazione con app già costruita
bash scripts/check_foundation.sh

# Build completa; richiede app chiusa
bash scripts/build_macos.sh

# Avvio del pacchetto locale
open dist/DidactyX.app

# Raccolta dell'ultima prova senza chiamate AI, se archivio e freeze esistono
tmp/packaging-venv/bin/python scripts/collect_lesson_consolidation.py --evidence docs/evidence/lesson-consolidation/2026-11-17 --data-dir tmp/lesson-consolidation/generated-db
```

Il collector richiede i file corrispondenti al contratto congelato: dopo una modifica intenzionale ai prompt può rilevare una divergenza legittima. Usare un checkout compatibile per ricontrollare la prova storica; non modificarne le impronte per far passare il codice nuovo. I dettagli di riproduzione sono nel rapporto.

Le generazioni live consumano quota: script `check_didactic_uda_live.py`, `check_lessons_live.py`, `check_planning_live.py`, `didactic_benchmark.py`. Usare `--help` e nuove destinazioni separate quando servono prove nuove; non rilanciarli soltanto per ricostruire il contesto. Build e test ordinari non richiedono una nuova generazione AI. Le dipendenze di build sono fissate in `scripts/requirements-build.txt`.

## 8 Cosa manca e proposta del prossimo incremento

Già disponibili: fondazione Mac, programmi/brief/impostazioni, scheletro annuale con revisioni e PDF, corpi delle lezioni con continuità effettiva, ruoli autore/revisori, versioni/ripresa/riallineamento segnalato, lettore ed export, benchmark e consolidamento sul pilota. Esempi e domande interni alle lezioni **non sostituiscono** i moduli dedicati ancora mancanti.

Ancora da realizzare:

1. Arricchimento visivo e vere mappe, autori/revisori dedicati, allegati/versioni e resa nel lettore/PDF.
2. Percorsi dedicati di esercizi con gradualità, brief e revisori.
3. Prove basate sui materiali effettivi, N varianti comparabili, obiettivi minimi/personalizzati e adattamenti.
4. Feedback, lezioni/materiali/prove di recupero esclusi dall'export annuale: incremento 5.
5. Consolidamento dell'uso Mac, distribuzione, compatibilità, problemi di rete/quota e raccolte ampie: incremento 6. Alcuni meccanismi di ripresa sono già implementati/testati, ma non esauriscono questo incremento.
6. Fonti e validazione su altre discipline, percorsi più lunghi, formule complesse, feedback d'uso in classe; Windows successivamente.

**Proposta operativa per il prossimo lavoro, non ancora un dettaglio implementativo approvato:** partire dalle tre lezioni già disponibili, definire contratti canonici per immagini/schemi e concetti/relazioni delle mappe, dipendenze e revisioni; integrare generazione e revisione con il login esistente verificandone le capacità; realizzare lettore ed export; valutare correttezza, utilità didattica, stile coerente e leggibilità su materiali completi. Mantenere la UI essenziale e non ridurre l'intero modulo a un disegno dimostrativo.

Il layout delle mappe, lo schema degli allegati, i modelli per i ruoli e i criteri specifici del nuovo benchmark sono ancora scelte da concretizzare. Le prove iniziali di SVG/PNG sono riferimenti riutilizzabili, non una consegna del modulo finito.

## 9 Preferenze di collaborazione e testo di avvio

Il docente chiede di lavorare con metodo: implementazione concreta, prove sui contenuti reali, report a lavoro concluso, documentazione aggiornata e recap di ciò che manca. Ha delegato l'invenzione del campione iniziale e la creazione dei benchmark. Evitare di chiedergli nuovamente materia e classe per ricostruire quel pilota.

Continuare con comunicazioni in italiano, distinguendo ciò che funziona davvero da ciò che è soltanto pianificato. Nessun risultato numerico sostituisce la lettura didattica. Preservare autonomia del docente, dati, storico e ambito minimale dell'app. Non serve scegliere di nuovo lo stack o ripartire da zero.

Testo utilizzabile dal docente nella prossima chat:

> Riprendiamo DidactyX. Voglio lavorare con Astra 2. Leggi `AGENTS.md`, `docs/SESSION_HANDOFF.md`, `docs/PROJECT_STATUS.md`, il Project Brief e il piano. Il consolidamento 0.3.3 delle tre lezioni è concluso e documentato sul branch `codex/lesson-consolidation`, PR #5 in bozza. Il prossimo sviluppo proposto è arricchimento visivo e mappe concettuali dell'incremento 4. Prima di intervenire controlla lo stato effettivo del repository e preserva le decisioni concordate e le evidenze storiche.

La selezione del modello resta una scelta del docente nella nuova sessione. Questo documento ne conserva la preferenza senza dichiarare di aver effettuato il cambio.
