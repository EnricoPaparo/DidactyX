# Valutazione didattica e tuning · DidactyX 0.3.2

**Data:** 17 novembre 2026. **Stato:** confronto finale in corso; non costituisce ancora il rapporto conclusivo.

## Mandato e materiali

La prova copre i tre passi concordati: valutare le lezioni, ricavare miglioramenti del motore e verificare una prima UDA completa. Il campione è fittizio: seconda superiore tecnica, studenti di 15–16 anni principianti, Python. La UDA occupa sei ore: L1 variabili/input/conversioni, L2 decisioni con if/else, L3 laboratorio sul budget di un acquisto. Il programma annuale di riferimento contiene 24 ore, quattro UDA e 17 lezioni previste. Il docente ha delegato la scelta dell’esempio.

«UDA completa» indica qui i tre contenuti di lezione, con laboratorio e attività interne. Mappe, arricchimento visivo, percorsi di esercizi dedicati, verifiche formali e recupero sono ancora negli incrementi 4 e 5. Non si presenta questo risultato come l’intero workflow finale del prodotto.

## Metodo dichiarato prima del tuning

La [rubrica](../../../../benchmarks/didactic/rubric.json) usa sei criteri da 0 a 4: correttezza (25%), spiegazioni (20%), progressione/continuità (15%), attività e riduzione degli aiuti (15%), comprensione e applicazione vicina (15%), fattibilità/accessibilità (10%). La soglia interna richiede almeno 3 in ogni criterio, almeno 75/100 e nessuna criticità grave. Un buon totale non compensa un criterio insufficiente.

Due sessioni distinte dello stesso servizio Codex, con prospettiva disciplinare e didattica, valutano ciascuna lezione e la UDA. Il riepilogo usa il minimo dei due punteggi per ogni criterio. Ogni voto è accompagnato da citazioni controllate nei corpi salvati o nelle trascrizioni effettivamente mostrate. Gli oracoli dei casi avversi non sono inviati ai revisori. Gli hash di input e istruzioni impediscono di riutilizzare silenziosamente un esito prodotto con un altro contratto.

Il confronto conclusivo usa [audit-baseline-rendered](audit-baseline-rendered) e `audit-tuned`, entrambi informati dell’ordine e del testo effettivo degli esempi visibili. La rubrica, i pesi e le soglie restano gli stessi. I [primi giudizi](audit-baseline) sono conservati: la seconda valutazione iniziale conferma gli stessi minimi. Il contesto editoriale è stato aggiunto a entrambi i lati dopo un rilievo infondato sulle trascrizioni, non soltanto al materiale nuovo.

## Riscontro iniziale

L1 raggiunge 90/100. L2, L3 e UDA raggiungono 86,25/100, ma falliscono C4 (2/4): alcune attività annunciate come autonome ripetono dati già risolti in esempi o lezioni precedenti. Sono solide correttezza, spiegazioni e continuità; il volume del materiale non è una prova di autonomia. Il [rapporto iniziale](BASELINE_REPORT.md) documenta il limite e i riferimenti.

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

## Limiti e interpretazione

È un benchmark interno, piccolo e circoscritto a Python per principianti. Autori e valutatori usano lo stesso servizio generativo; sessioni e ruoli distinti non eliminano errori condivisi. Le mutazioni sono note a chi costruisce la prova, anche se escluse dagli input del revisore. Non vi sono studenti osservati, misure di apprendimento, tempi reali o confronto con libri di testo. Non si certifica l’adeguatezza per DSA o DVA.

L1 e L2 iniziali provengono dal pilota salvato il 16 novembre; L3 iniziale è generata per completare il campione. La nuova UDA è generata in ordine usando i corpi appena prodotti. Le generazioni non sono deterministiche, il modello predefinito dell’account non è fissato, non vi sono repliche o assegnazione casuale: il confronto verifica un miglioramento di questi materiali, non dimostra un effetto causale generalizzabile del prompt.

I controlli di esecuzione verificano risultati di programmi, non l’adeguatezza pedagogica del testo. Il caso H02 supera deliberatamente l’esecuzione pur usando un confronto contrario all’obiettivo. I controlli negativi verificano specifici falsi allarmi, non l’assenza di qualsiasi suggerimento improprio.

## Riferimenti e riproduzione

La progressione e il supporto esplicito sono operazionalizzati a partire dalla guida [AERO sull’istruzione esplicita](https://www.edresearch.edu.au/guides-resources/practice-guides/glance-explicit-instruction) e dalla guida [EEF su metacognizione e autoregolazione](https://educationendowmentfoundation.org.uk/education-evidence/guidance-reports/metacognition). Gli oracoli disciplinari si basano sulla documentazione ufficiale [Python: funzioni](https://docs.python.org/3.12/library/functions.html) e [Python: condizioni](https://docs.python.org/3.12/tutorial/controlflow.html#if-statements). Non si assume un copione didattico obbligatorio.

Protocollo, casi e comandi: [benchmarks/didactic/README.md](../../../../benchmarks/didactic/README.md). I dati scolastici sono fittizi; nessuna credenziale viene inclusa. Il comando `collect` ricontrolla struttura, riferimenti, esecuzioni, citazioni e conteggi senza consumare quota AI. I dati grezzi rimangono accanto al rapporto.
