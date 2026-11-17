# Valutazione didattica e tuning · DidactyX 0.3.2

**Data:** 17 novembre 2026. **Stato:** confronto e tuning conclusi; soglia interna superata dal campione finale.

## Mandato e materiali

La prova copre i tre passi concordati: valutare le lezioni, ricavare miglioramenti del motore e verificare una prima UDA completa. Il campione è fittizio: seconda superiore tecnica, studenti di 15–16 anni principianti, Python. La UDA occupa sei ore: L1 variabili/input/conversioni, L2 decisioni con if/else, L3 laboratorio sul budget di un acquisto. Il programma annuale di riferimento contiene 24 ore, quattro UDA e 17 lezioni previste. Il docente ha delegato la scelta dell’esempio.

«UDA completa» indica qui i tre contenuti di lezione, con laboratorio e attività interne. Mappe, arricchimento visivo, percorsi di esercizi dedicati, verifiche formali e recupero sono ancora negli incrementi 4 e 5. Non si presenta questo risultato come l’intero workflow finale del prodotto.

## Metodo dichiarato prima del tuning

La [rubrica](../../../../benchmarks/didactic/rubric.json) usa sei criteri da 0 a 4: correttezza (25%), spiegazioni (20%), progressione/continuità (15%), attività e riduzione degli aiuti (15%), comprensione e applicazione vicina (15%), fattibilità/accessibilità (10%). La soglia interna richiede almeno 3 in ogni criterio, almeno 75/100 e nessuna criticità grave. Un buon totale non compensa un criterio insufficiente.

Due sessioni distinte dello stesso servizio Codex, con prospettiva disciplinare e didattica, valutano ciascuna lezione e la UDA. Il riepilogo usa il minimo dei due punteggi per ogni criterio. Ogni voto è accompagnato da citazioni controllate nei corpi salvati o nelle trascrizioni effettivamente mostrate. Gli oracoli dei casi avversi non sono inviati ai revisori. Gli hash di input e istruzioni impediscono di riutilizzare silenziosamente un esito prodotto con un altro contratto.

Il confronto usa [audit-baseline-rendered](audit-baseline-rendered), [audit-tuned](audit-tuned) e [audit-edited](audit-edited): prima del tuning, dopo la rigenerazione e dopo una correzione editoriale esplicita. Tutti ricevono l’ordine e il testo effettivo degli esempi visibili. La rubrica, i pesi e le soglie restano gli stessi. I [primi giudizi](audit-baseline) sono conservati: la seconda valutazione iniziale conferma gli stessi minimi. Il contesto editoriale è stato aggiunto a entrambi i lati dopo un rilievo infondato sulle trascrizioni, non soltanto al materiale nuovo.

## Riscontro iniziale

L1 raggiunge 90/100. L2, L3 e UDA raggiungono 86,25/100, ma falliscono C4 (2/4): alcune attività annunciate come autonome ripetono dati già risolti in esempi o lezioni precedenti. Sono solide correttezza, spiegazioni e continuità; il volume del materiale non è una prova di autonomia. Il [rapporto iniziale](BASELINE_REPORT.md) documenta il limite e i riferimenti.

## Confronto conclusivo dei materiali

C1 = correttezza; C2 = spiegazione; C3 = progressione e continuità; C4 = attività e aiuti; C5 = comprensione e applicazione; C6 = fattibilità e accessibilità. I valori sono i minimi dei due valutatori per criterio, senza compensazioni favorevoli. Le citazioni sono state ricontrollate automaticamente.

| Materiale | C1 | C2 | C3 | C4 | C5 | C6 | Totale /100 | Soglia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Prima · L1 | 4 | 4 | 4 | 3 | 3 | 3 | 90,0 | Superata |
| Prima · L2 | 4 | 4 | 4 | 2 | 3 | 3 | 86,25 | Non superata |
| Prima · L3 | 4 | 4 | 4 | 2 | 3 | 3 | 86,25 | Non superata |
| Prima · UDA | 4 | 4 | 4 | 2 | 3 | 3 | 86,25 | Non superata |
| Tuning generativo · L1 | 3 | 4 | 4 | 4 | 4 | 3 | 91,25 | Superata |
| Tuning generativo · L2 | 3 | 4 | 4 | 4 | 4 | 3 | 91,25 | Superata |
| Tuning generativo · L3 | 3 | 4 | 4 | 3 | 4 | 3 | 87,5 | Superata |
| Tuning generativo · UDA | 3 | 4 | 4 | 3 | 4 | 3 | 87,5 | Superata |
| Correzione editoriale · L1 | 4 | 4 | 4 | 4 | 4 | 3 | 97,5 | Superata |
| Correzione editoriale · L2 | 4 | 4 | 4 | 4 | 4 | 3 | 97,5 | Superata |
| Correzione editoriale · L3 | 4 | 4 | 4 | 3 | 4 | 3 | 93,75 | Superata |
| Correzione editoriale · UDA | 4 | 4 | 4 | 3 | 4 | 3 | 93,75 | Superata |

I rapporti completi e i conteggi sono in [results.json](results.json), [audit-baseline-rendered](audit-baseline-rendered), [audit-tuned](audit-tuned) e [audit-edited](audit-edited). La UDA passa da 86,25/100 con C4 insufficiente a 87,5 dopo la rigenerazione e a 93,75 dopo la correzione editoriale. Le due lezioni teoriche corrette raggiungono 97,5. Questi risultati non equivalgono a una misura degli apprendimenti.

## Interventi e controesempi

Il primo tuning generativo non viene promosso. Introduce casi diversi, ma li colloca negli esempi eseguibili prima delle consegne: le risposte sono quindi già visibili. Il [materiale scartato](tuning-iteration-1/lesson-L1.json) e il [riscontro](tuning-iteration-1/finding.json) restano disponibili. Il primo revisore affinato manca questo difetto reale E01, pur superando i casi predisposti. Il [rapporto mancato](development-regressions/E01.json) è conservato.

Il secondo tuning esplicita ad autori e revisori automatici che i casi del codice sono mostrati subito dopo quel codice, non test nascosti. Le prove nuove devono precedere le proprie soluzioni; i casi già risolti possono rimanere consolidamento, rispettando le indicazioni del docente. Sono rafforzati osservabilità individuale, controllo dei prerequisiti e coerenza delle note. Non viene introdotto un limite di parole.

Un candidato consultivo con sole istruzioni trova E01, ma suggerisce erroneamente in H04 che manchino gli input digitati. Il lettore e il PDF mostrano già la trascrizione verificata con eco: il [rilievo non fondato](reviewer-instruction-only/H04-unfounded-finding.json) rimane registrato. Il candidato definitivo riceve pertanto `visible_examples`, prodotto dallo stesso helper usato dal renderer, e valuta ciò che lo studente vede. Non si risolve il problema chiedendo al revisore di fidarsi delle dichiarazioni dell’autore.

Gli otto casi originali sono rieseguiti come regressioni dopo gli ulteriori interventi: non sono nuovi casi ignoti. E01 è uno strumento di sviluppo; F01 e F02 sono due casi aggiuntivi fissati prima della loro prova. Il [diario](TUNING_LOG.md) e i file di congelamento distinguono le fasi.

## Prove dei revisori

| Gruppo | Riferimento iniziale | Revisore definitivo | Interpretazione |
| --- | --- | --- | --- |
| C01–C03, H01–H03: sei difetti predisposti | 6/6 rilevati | 6/6 rilevati | Regressione preservata; non dimostra un miglioramento già misurabile sul set originario |
| C04, H04: due controlli negativi | 2/2 rispettati | 2/2 rispettati | Scelte del docente ed errori deliberati riconosciuti |
| E01: risposte anticipate, difetto reale di sviluppo | Mancato dal primo revisore affinato | Rilevato con proposta pertinente | Correzione del controesempio che ha guidato l’intervento |
| F01: falsa modifica della variabile testuale | Non provato sul riferimento iniziale | Rilevato | Nuovo caso fissato prima della sua prova |
| F02: consolidamento esplicitamente richiesto | Non provato sul riferimento iniziale | Rispettato, nessun rilievo | Il revisore non impone casi nuovi contro il brief |

Il profilo definitivo rileva dunque gli otto difetti mirati e rispetta i tre controlli di questo insieme. I risultati e le motivazioni della lettura dei rapporti sono in [reviewer-final](reviewer-final); la lettura conclusiva è eseguita dalla sessione responsabile del benchmark, non da un valutatore umano esterno. La precedente osservazione infondata su H04 dimostra perché il solo conteggio del difetto bersaglio non esaurisce la qualità di un rapporto.

## Regressione editoriale rilevata e corretta

La prima UDA rigenerata supera la soglia interna: L1/L2 91,25/100, L3/UDA 87,5/100. C4 migliora da 2 a 3 nella UDA, ma C1 scende da 4 a 3. Entrambi i valutatori rilevano che alcuni passaggi descrivono stdout senza eco mentre gli esempi sono trascrizioni complete. Questo peggioramento resta nella tabella e nei rapporti; non si afferma che il tuning abbia migliorato ogni criterio.

Prima della consegna, cinque blocchi esplicativi e tre note interne vengono corretti nella versione 3. La correzione distingue prompt, risposta digitata, Invio e messaggi di print. È una **revisione editoriale esplicita del campione**, non una nuova generazione integrale del workflow. [Patch prima/dopo](editorial-patches.json), [riscontri](editorial-observations.json) e [manifest](edited/generation.json) permettono di ricostruire l’intervento. Le versioni 2 e i loro punteggi rimangono immutati; codice, casi, attività e risultati eseguibili non cambiano. I riferimenti vengono riallineati alle nuove versioni delle lezioni.

Le istruzioni generali dell’autore e del revisore della continuità vengono chiarite per prevenire l’equivoco. Una [prova mirata dell’autore](transcript-author-probe.json), su nome e saluto invece del budget, distingue correttamente testo digitato e messaggi del programma. La [lettura dell’esito](transcript-author-probe-adjudication.json) ne precisa la portata: le ultime istruzioni non sono state provate con una nuova rigenerazione completa delle tre lezioni. Il revisore consultivo resta quello verificato sugli undici casi.

La versione corretta è valutata nuovamente con gli stessi due ruoli, criteri e istruzioni. Questa terza valutazione è una regressione di sviluppo su un campione già noto, non una prova indipendente ignota. Rimangono da rafforzare la produzione individuale di modifiche al codice e la flessibilità dei tempi finali del laboratorio; il superamento della soglia non equivale alla perfezione dei materiali.

## Verifica tecnica ed editoriale

La build macOS 0.3.2 supera **47 test automatici** e l’integrazione Swift con il motore incluso. Il batch reale preserva le versioni precedenti, usa i corpi aggiornati in ordine L1→L2→L3 e termina con tutti i riferimenti correnti. La ripresa rifiuta un contratto didattico cambiato senza cancellare il contenuto completato.

| Lezione finale | Pagine PDF | Casi Python eseguiti | Stringhe studente controllate |
| --- | --- | --- | --- |
| L1 | 22 | 8 | 373 |
| L2 | 23 | 9 | 343 |
| L3 | 24 | 7 | 433 |

Tutti i **24 casi eseguibili** corrispondono all’output atteso anche nel motore congelato, comprese le trascrizioni. I frammenti illustrativi rimangono distinti dai casi eseguiti. Tutte le **69 pagine** sono state renderizzate e ispezionate; il controllo del testo non trova omissioni nelle 1.149 stringhe del materiale studente. Le pagine prodotte dal motore incluso nell’app coincidono pixel per pixel con quelle ispezionate. I gruppi brevi di spiegazioni svolte e i riferimenti vengono mantenuti insieme quando lo spazio lo consente.

Evidenze: [pdf-qa.json](pdf-qa.json), [frozen-code-checks.json](frozen-code-checks.json), [tuned/generation.json](tuned/generation.json). Il contratto generativo del corpus è `didactic-v2-25661f37ff47`; la release aggiunge il revisore consultivo definitivo e il suo contesto visivo, poi chiarisce la convenzione delle trascrizioni nei ruoli generativi. Le diverse fasi e il limite della prova mirata sono espliciti. Hash e tracciabilità sono in [release-provenance.json](release-provenance.json).

## Limiti e interpretazione

È un benchmark interno, piccolo e circoscritto a Python per principianti. Autori e valutatori usano lo stesso servizio generativo; sessioni e ruoli distinti non eliminano errori condivisi. Le mutazioni sono note a chi costruisce la prova, anche se escluse dagli input del revisore. Non vi sono studenti osservati, misure di apprendimento, tempi reali o confronto con libri di testo. Non si certifica l’adeguatezza per DSA o DVA.

L1 e L2 iniziali provengono dal pilota salvato il 16 novembre; L3 iniziale è generata per completare il campione. La nuova UDA è generata in ordine usando i corpi appena prodotti; successivamente riceve le sole correzioni editoriali registrate, con una nuova valutazione separata. Le generazioni non sono deterministiche, il modello predefinito dell’account non è fissato, non vi sono repliche o assegnazione casuale: il confronto verifica un miglioramento di questi materiali, non dimostra un effetto causale generalizzabile del prompt.

I controlli di esecuzione verificano risultati di programmi, non l’adeguatezza pedagogica del testo. Il caso H02 supera deliberatamente l’esecuzione pur usando un confronto contrario all’obiettivo. I controlli negativi verificano specifici falsi allarmi, non l’assenza di qualsiasi suggerimento improprio.

## Riferimenti e riproduzione

La progressione e il supporto esplicito sono operazionalizzati a partire dalla guida [AERO sull’istruzione esplicita](https://www.edresearch.edu.au/guides-resources/practice-guides/glance-explicit-instruction) e dalla guida [EEF su metacognizione e autoregolazione](https://educationendowmentfoundation.org.uk/education-evidence/guidance-reports/metacognition). Gli oracoli disciplinari si basano sulla documentazione ufficiale [Python: funzioni](https://docs.python.org/3.12/library/functions.html) e [Python: condizioni](https://docs.python.org/3.12/tutorial/controlflow.html#if-statements). Non si assume un copione didattico obbligatorio.

Protocollo, casi e comandi: [benchmarks/didactic/README.md](../../../../benchmarks/didactic/README.md). I dati scolastici sono fittizi; nessuna credenziale viene inclusa. Il comando `collect` ricontrolla struttura, riferimenti, esecuzioni, citazioni e conteggi senza consumare quota AI. I dati grezzi rimangono accanto al rapporto.

## Materiali consegnati e ripresa

Nell’app locale 0.3.2 è disponibile **Python · UDA 1 · benchmark didattico**: tre lezioni, ciascuna con versione 1 iniziale, versione 2 rigenerata e versione 3 corretta editorialmente. L’installazione è additiva e i dati precedenti rimangono immutati. Sono stati verificati nell’interfaccia programma, storico 1/2/3, lettore del laboratorio e messaggio di export «PDF salvato». Evidenze: [app-sample.json](app-sample.json) e [software-verification.json](software-verification.json).

PDF finali della versione 3: [L1 · Variabili, input e conversioni](pdf/lesson-L1.pdf), [L2 · Decidere con if ed else](pdf/lesson-L2.pdf), [L3 · Laboratorio](pdf/lesson-L3.pdf). Le note del docente restano interne; i PDF contengono il materiale studente completo.

Il benchmark è utilizzabile come regressione per il prossimo incremento. Le priorità didattiche residue sono osservare meglio la costruzione individuale delle istruzioni, prevedere una riduzione esplicita del carico quando emergono difficoltà e verificare le ultime regole editoriali in una successiva generazione completa. Mappe, materiali visivi, esercitazioni dedicate e verifiche restano nell’incremento 4; il feedback con recupero nell’incremento 5.

Lavoro salvato nel branch `codex/didactic-benchmarks` e nella [PR #4 in bozza](https://github.com/EnricoPaparo/DidactyX/pull/4), basata sul restyling della PR #3. Nessun merge a `main`.
