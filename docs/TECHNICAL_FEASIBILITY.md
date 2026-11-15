# Verifica tecnica iniziale di DidactyX

- **Data:** 15 novembre 2026
- **Ambito:** consolidamento del repository e prove di fattibilità precedenti alla progettazione dell'architettura
- **Esito:** le capacità tecniche provate sono disponibili nell'ambiente corrente; architettura del prodotto ancora da scegliere
- **Dati utilizzati:** classe ed esempi interamente fittizi

**Aggiornamento successivo alle prove:** lo stack macOS è stato approvato e registrato in [ARCHITECTURE.md](ARCHITECTURE.md). Il presente rapporto conserva i risultati e le condizioni della verifica precedente alla scelta.

## 1 Risultato operativo

Il README e il Project Brief sono stati pubblicati sul ramo `main` del repository DidactyX con il commit iniziale `5f73d903714c358d90216c532006630d864c3b81`.

Un client locale di prova ha comunicato realmente con Codex App Server mediante JSON-RPC su standard input e output. Le richieste generative hanno utilizzato il login ChatGPT già presente sul Mac. Non sono state create chiavi API né configurati servizi alternativi a consumo.

Sono riuscite la generazione strutturata di due lezioni, il passaggio del contenuto effettivo tra autori in sessioni distinte, la revisione di un errore matematico inserito appositamente, la generazione di una mappa con relazioni esplicite e di un'immagine raster, l'interruzione e ripresa di una conversazione e l'esportazione locale in PDF.

Questi risultati dimostrano la fattibilità dei singoli passaggi provati. Non costituiscono ancora una validazione della qualità didattica del prodotto, del workflow annuale completo o di un'architettura definitiva.

## 2 Ambiente verificato

| Componente | Versione o condizione |
| --- | --- |
| Sistema | macOS 26.7.2, arm64 |
| Codex CLI | `0.169.0-alpha.11.1` |
| Autenticazione | ChatGPT gestita da Codex, già configurata |
| Modello effettivamente usato | `gpt-6.1-sol`, predefinito del catalogo rilevato |
| Python per il protocollo | 3.14.6, libreria standard |
| Python per il PDF | 3.12.14, runtime fornito all'ambiente di lavoro |
| Impaginazione del campione | ReportLab 4.4.9 |
| Lettura e controlli PDF | pypdf 6.21.4 |
| Controlli raster | Pillow 13.0.0 |
| Font | DejaVu Sans regolare e grassetto |
| Controllo visivo | Pagine PDF renderizzate con Poppler e ispezionate tutte |

L'installazione Codex è una versione alpha. Le prove riguardano questa versione e questo account; non stabiliscono una compatibilità generale con altre versioni o installazioni.

Il catalogo ha restituito otto modelli. È stato eseguito un turno reale soltanto con il modello predefinito: la presenza di un modello nel catalogo non è stata considerata prova del suo utilizzo effettivo. I dati di quota sono risultati leggibili, con una finestra primaria presente e nessuna finestra secondaria nella risposta osservata. Percentuali, identità dell'account e identificativi della sessione non sono pubblicati nelle evidenze.

## 3 Prove eseguite

| Prova | Riscontro osservato | Confine della prova |
| --- | --- | --- |
| Collegamento locale | Handshake `initialize` e chiamate JSON-RPC riusciti. | Client da terminale, non ancora applicazione grafica installabile. |
| Account | `account/read` ha restituito autenticazione `chatgpt`. | Riutilizzo del login esistente; nuovo accesso e cambio account non eseguiti. |
| Quota | `account/rateLimits/read` e notifiche di aggiornamento ricevuti. | Non sono state provocate condizioni di esaurimento della quota. |
| Output strutturato | Due lezioni generate con `outputSchema`, JSON leggibile e campi validati. | Schema piccolo di laboratorio, non ancora lo schema definitivo del prodotto. |
| Continuità | L2 ha riutilizzato scenario, prezzo del kit, uguaglianza e operazioni spiegati in L1. | Contenuto di L1 fornito esplicitamente; nessuna prova su un anno di materiali. |
| Revisione separata | Rilevata la risposta errata di E1 e proposta la soluzione corretta. | Sessione distinta, ma stesso modello degli autori. |
| Indicazioni del docente | Mantenuti tre esercizi e l'assenza di spiegazioni nelle consegne; difficoltà segnalata come osservazione consultiva. | Fixture predefinita, non verifica esaustiva del rispetto dei brief. |
| Mappa concettuale | Quattro concetti collegati da tre relazioni semantiche; riferimenti tra nodi validi. | Mappa piccola con disposizione lineare; layout complessi e adattamenti ancora da provare. |
| Schema procedurale | Generata anche una rappresentazione dei passaggi di calcolo. | Conservata separatamente dalla mappa concettuale. |
| Immagine raster | Un evento nativo `imageGeneration` completato e un PNG reale salvato. | Un solo campione; nessuna prova di coerenza stilistica su una serie. |
| Streaming e interruzione | Ricevuto testo in streaming, inviato `turn/interrupt`, stato finale `interrupted`. | Interruzione controllata, non perdita improvvisa del sistema o della rete. |
| Ripresa | Riavviato il processo, eseguito `thread/resume`, recuperati progetto, equazione e costo senza reinserirli. | Ripresa della conversazione Codex, non ancora del workflow applicativo annuale. |
| PDF locale | Quattro pagine con testo selezionabile, formule semplici, mappa, schema vettoriale e immagine raster incorporata. | Template dimostrativo; formule complesse, grandi raccolte e impaginazioni articolate ancora da provare. |

### 3.1 Due lezioni collegate

Il caso sintetico riguarda il progetto Faro. L1 spiega il costo sconosciuto di un kit più tre euro di trasporto, per un totale di undici euro: `x + 3 = 11`, con soluzione `x = 8`. L2 riprende lo stesso contesto e introduce due kit e un unico trasporto: `2x + 3 = 19`.

L'autore di L2 ha ricevuto il contenuto completo di L1, non soltanto il titolo o i metadati. La lezione prodotta richiama concretamente il prezzo di otto euro, il significato dell'uguaglianza, la sottrazione sui due membri e la verifica, introducendo poi la divisione.

I campioni sono disponibili come [prima lezione](evidence/feasibility/2026-11-15/lesson1.json) e [seconda lezione](evidence/feasibility/2026-11-15/lesson2.json).

### 3.2 Revisione e autonomia del docente

La fixture contiene tre esercizi e una richiesta esplicita di conservarne numero e consegne senza spiegazioni. La risposta candidata di E1 contiene un errore deliberato: da `2x + 3 = 19` viene indicato `x = 16`.

Il revisore ha rilevato il passaggio mancante della divisione per due e restituito `x = 8`. Ha riconosciuto corrette le risposte degli altri due esercizi e segnalato che richiedono competenze ulteriori rispetto alle lezioni, mantenendo le avvertenze consultive. Le tre soluzioni sono state riscontrate anche con aritmetica indipendente dal modello.

La prova verifica la separazione tra controllo matematico e osservazione didattica. Non misura il tasso di errori che un revisore riconoscerebbe su materiali diversi. Consultare [fixture](evidence/feasibility/2026-11-15/review_fixture.json) e [revisione prodotta](evidence/feasibility/2026-11-15/independent_review.json).

### 3.3 Mappa e schema procedurale

La prima rappresentazione generata descriveva le operazioni per risolvere l'equazione: è uno schema di procedimento. È stata conservata come tale e affiancata a una mappa concettuale distinta: Equazione, Trasformazioni equivalenti, Soluzione, Verifica per sostituzione, con relazioni esplicite.

Il modello restituisce dati strutturati; il codice locale valida i riferimenti e disegna la rappresentazione. Nel laboratorio non viene eseguito codice grafico generato dal modello. Sono disponibili la [mappa in JSON](evidence/feasibility/2026-11-15/concept_map.json), la [mappa SVG](evidence/feasibility/2026-11-15/concept-map.svg) e lo [schema procedurale](evidence/feasibility/2026-11-15/procedure-map.svg).

### 3.4 Immagine reale

Con la generazione immagini abilitata nel processo di prova, Codex ha prodotto un PNG di 1752 × 897 pixel. L'ispezione visiva ha verificato una scatola e tre pesi a sinistra, undici pesi a destra, bilancia in equilibrio e assenza di testo, coerentemente con la richiesta.

Il risultato prova l'accesso al tool raster nativo nella configurazione corrente. La qualità delle illustrazioni su altre richieste, la fedeltà grafica tra lezioni e la revisione automatica delle immagini richiedono altre prove. L'[illustrazione](evidence/feasibility/2026-11-15/native-illustration.png) è inclusa anche nel PDF.

### 3.5 Salvataggio e ripresa

Il client di laboratorio salva ogni risultato completato in file locali attraverso scrittura temporanea e sostituzione del file finale. Conserva inoltre un checkpoint della sessione e un'impronta del contesto; questi due file di lavoro rimangono nella cartella locale esclusa da Git.

È stato interrotto un turno dopo l'inizio della risposta. Dopo il riavvio dell'app-server, una domanda senza reinserimento delle lezioni ha ottenuto correttamente progetto Faro, costo di otto euro ed equazione di L2. Questa verifica dimostra la conservazione della conversazione da parte di Codex. La ripresa di attività composte, le dipendenze tra materiali e il comportamento dopo un arresto improvviso del prodotto sono ancora da progettare.

### 3.6 PDF e controllo visivo

Il campione finale contiene due lezioni, una mappa concettuale, una rappresentazione vettoriale dell'uguaglianza e l'illustrazione raster. Il primo rendering ha evidenziato un esempio spezzato tra due pagine e un'etichetta troppo lunga. Sono stati corretti raggruppando l'esempio, regolando la tipografia e gestendo il testo delle relazioni su più righe.

Tutte le quattro pagine della versione finale sono state ispezionate. I controlli offline verificano testo estraibile, presenza dell'immagine incorporata e assenza dei caratteri di sostituzione controllati. L'impaginazione della prova non è il template definitivo e i limiti di dimensione delle fixture non sono limiti del futuro prodotto.

Consultare il [PDF dimostrativo](evidence/feasibility/2026-11-15/didactyx-feasibility-sample.pdf).

## 4 Tempi osservati

| Operazione | Tempo del singolo campione |
| --- | --- |
| Prima lezione | 30,15 secondi |
| Seconda lezione | 31,37 secondi |
| Revisione separata | 13,22 secondi |
| Risposta dopo ripresa | 4,09 secondi |
| Mappa concettuale finale | 8,63 secondi |
| Illustrazione raster | 36,14 secondi |

I tempi misurano una singola esecuzione nell'ambiente corrente. Non sono stime di un intero percorso, confronti tra modelli o garanzie sulle prestazioni. Sono state effettuate richieste reali che utilizzano la disponibilità dell'account; non è stato ricavato un costo generale per programma annuale.

## 5 Accesso ufficiale e differenza tra le vie disponibili

La prova ha usato l'autenticazione ChatGPT gestita dall'app-server di Codex. La documentazione ufficiale descrive questo meccanismo per applicazioni locali o open source e raccomanda la migrazione a Sign in with ChatGPT per una maggiore gestione dell'utilizzo da parte dell'utente. [Codex App Server](https://learn.chatgpt.com/docs/app-server)

La documentazione di Sign in with ChatGPT presenta l'uso del piano per applicazioni locali e open source. L'accesso di un nuovo utente, la registrazione del client e il relativo consenso non sono stati provati in questa sessione. [Panoramica ufficiale](https://developers.openai.com/siwc/token-sharing-open-source)

La via documentata di utilizzo del piano attraverso Responses e Sign in with ChatGPT elenca attualmente la generazione immagini tra gli strumenti non supportati. Questa limitazione riguarda quella via: il tool nativo dell'app-server con il login gestito ha invece prodotto un'immagine nella prova eseguita. Le due configurazioni non vanno considerate intercambiabili. [Limitazioni della preview](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations)

La scelta del collegamento da adottare nell'app e della strategia futura per le immagini deve quindi essere affrontata nel punto 3. Il risultato attuale permette di discuterla sulla base di una prova concreta, senza dichiarare che tutte le modalità offrano le stesse capacità.

## 6 Evidenze e riproduzione

Gli script sono in [experiments/feasibility](../experiments/feasibility/README.md). Le evidenze controllate sono in [docs/evidence/feasibility/2026-11-15](evidence/feasibility/2026-11-15/README.md).

- [Risultati del protocollo e delle lezioni](evidence/feasibility/2026-11-15/results.json).
- [Esito della generazione immagini](evidence/feasibility/2026-11-15/image_results.json).
- [Esito PDF e ispezione visiva](evidence/feasibility/2026-11-15/pdf_results.json).
- [Controlli offline](evidence/feasibility/2026-11-15/offline_checks.json).
- [Manifesto dei campioni con impronte SHA256](evidence/feasibility/2026-11-15/manifest.json).

Le evidenze pubblicate contengono soltanto campioni fittizi e metadati tecnici selezionati. Il profilo account completo, le credenziali, i dati percentuali della quota e il checkpoint della sessione non sono inclusi. Gli script non modificano il login esistente e non avviano automaticamente servizi alternativi se una capacità non è disponibile.

## 7 Questioni da affrontare insieme nel punto 3

L'architettura deve ora decidere come integrare queste capacità in un prodotto minimale e affidabile. I punti principali sono:

1. Modalità di accesso all'account e separazione tra configurazione dell'app e profilo Codex dell'ambiente di sviluppo.
2. Gestione della dipendenza dal CLI e dalla versione del protocollo, inclusa la disponibilità effettiva del tool immagini.
3. Conservazione locale di programmi, materiali, versioni e stato del workflow, oltre alla cronologia delle conversazioni Codex.
4. Recupero del contesto su percorsi lunghi, generazione fuori sequenza e riallineamento dopo una modifica.
5. Contratti tra autore e revisore, controlli deterministici, gestione dei tentativi e presentazione degli esiti al docente.
6. Layout di mappe più articolate, formule complesse e PDF di raccolte ampie.
7. Interfaccia e confezionamento dell'app macOS.

Non sono stati scelti framework per l'app, database, sistema di orchestrazione definitivo o template editoriali del prodotto. Il prossimo lavoro rimane la progettazione condivisa dell'architettura, seguita dalla validazione didattica di un percorso pilota.
