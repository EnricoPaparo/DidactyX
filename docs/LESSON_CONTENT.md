# Contenuti delle lezioni · primo traguardo

L'incremento 3 collega i metadati annuali ai contenuti completi. Il primo traguardo è produrre e valutare due lezioni collegate, leggibili nell'app ed esportabili in PDF. Il pilota scelto su autorizzazione del docente è inventato: informatica, seconda superiore, variabili/input/conversioni e decisioni con `if/else` in Python.

## Utilizzo

Dal percorso annuale, espandere l'UDA e scegliere **Apri contenuto della lezione**. Il brief specifico è facoltativo e viene salvato localmente; il contesto applicato al programma rimane sempre disponibile al motore. **Genera contenuto** e **Rigenera lezione** avviano il workflow. La pagina mantiene i comandi dark e presenta il materiale in un lettore WebKit chiaro, con testo selezionabile e codice con rientri conservati.

**Revisiona** produce un rapporto consultivo senza modificare il materiale. Il docente può richiedere una rigenerazione con i suggerimenti. Lo storico conserva le versioni dei contenuti; quelle precedenti sono consultabili ed esportabili. Per rigenerare si seleziona la versione corrente. Le indicazioni specifiche ancora da applicare sono distinguibili dal brief della versione salvata.

I contenuti appartengono a una precisa versione del percorso annuale. Rigenerare il programma conserva i materiali del vecchio percorso; non li trasferisce automaticamente alle nuove lezioni in base alla somiglianza dei titoli.

## Formato e workflow

Il contratto è in `schemas/lesson-content.schema.json`. Il materiale contiene titolo, introduzione, obiettivi, sezioni, blocchi tipizzati, sintesi, glossario, domande con risposte ragionate, richiami ai materiali precedenti, riferimenti e note per il docente. I blocchi comprendono paragrafi, definizioni, esempi svolti, codice, liste, tabelle, richiami e formule lineari Unicode. Sintesi e domande possono essere omesse quando le indicazioni del docente lo richiedono.

La sequenza generativa comprende:

1. Progettazione dello sviluppo esplicativo e ripartizione delle sezioni fra uno o più autori.
2. Scrittura dei contenuti. Se intervengono più autori, ogni contributo riceve il contesto complessivo e un curatore ricompone la lezione.
3. Revisione disciplinare di concetti, procedure, esempi e risultati.
4. Revisione della chiarezza e della continuità con i contenuti precedenti effettivi.
5. Controlli indipendenti su formato, obiettivi, riferimenti, prerequisiti mancanti ed esempi eseguibili; eventuale correzione e ricontrollo.

Autori e revisori usano sessioni Codex distinte. La profondità non è ridotta con un limite di parole. Le raccomandazioni pedagogiche non sostituiscono automaticamente richieste esplicite del docente. Una correzione strutturale non risolta impedisce di pubblicare il materiale come concluso; il lavoro rimane riprendibile.

## Memoria didattica e versioni

Il contesto include brief applicato della classe, struttura annuale, UDA, lezione selezionata, brief specifico e corpi integrali dei materiali precedenti disponibili. Non vengono usati soltanto titoli o riepiloghi.

I richiami identificano la versione e la sezione effettivamente utilizzate. Il motore controlla che esistano e che i materiali propedeutici disponibili abbiano richiami tracciabili. Gli identificativi rimangono metadati; nelle note il docente trova descrizioni e codici delle lezioni.

Se la lezione viene generata fuori sequenza, il motore riceve l'elenco dei prerequisiti ancora privi di contenuti e deve sostenere i concetti necessari nella spiegazione corrente. Quando tali materiali diventano disponibili, oppure cambia una versione usata come fonte, la lezione viene segnalata per riallineamento. La segnalazione si propaga anche attraverso dipendenze intermedie. Nessun contenuto viene riscritto automaticamente.

La presenza di un materiale significa **generato**: non dimostra che sia stato spiegato o appreso. Le informazioni sull'utilizzo effettivo e sull'apprendimento richiedono feedback del docente.

Versioni complete e relativi riferimenti sono salvati in SQLite, schema 3. Una sola attività per programma evita sovrapposizioni tra rigenerazione annuale e produzione dei contenuti. Nel batch, le lezioni vengono elaborate nell'ordine del percorso: la seconda può già usare il corpo della prima appena completata. Ogni pubblicazione è atomica insieme al proprio punto di ripresa, così una ripresa non duplica i materiali già pubblicati.

Se il percorso, i materiali di riferimento o il contratto delle istruzioni didattiche cambiano mentre un lavoro è sospeso, il motore richiede una nuova generazione dal contesto corrente. La ripresa non combina silenziosamente versioni incompatibili e conserva i materiali già completati. L'API supporta batch di lezioni; l'interfaccia del primo traguardo lavora su una lezione alla volta.

## Esempi Python e fonti

Per i blocchi Python eseguibili, il motore verifica casi con input e output atteso in un processo separato. Il controllo applica restrizioni ai costrutti, esclude importazioni e accessi non previsti, limita il tempo e distingue risultati corrispondenti, errori e casi non eseguiti. I costrutti non supportati dal controllore non vengono dichiarati verificati e non impongono una semplificazione silenziosa della lezione. Il controllo non è un interprete generale né una certificazione della correttezza dell'intero testo.

L'output del programma viene confrontato senza l'eco degli input; per la lettura si conserva anche una trascrizione dell'esecuzione con i dati digitati. Lo studente può quindi seguire una sessione comprensibile, mentre i dettagli del controllo rimangono nelle note per il docente.

Tutti i casi associati al codice sono visibili subito dopo quel blocco, prima dei blocchi successivi: non sono test nascosti. Autori e revisori devono tenerne conto quando propongono un tentativo prima della soluzione. Il consolidamento su casi già svolti rimane legittimo, soprattutto quando richiesto dal docente; non va confuso con un’applicazione a dati inediti.

Il pilota utilizza un piccolo pacchetto di sintesi redazionali della documentazione ufficiale Python, con URL e data di consultazione, in `engine/didactyx_engine/assets/references/`. Le citazioni ammesse sono quelle effettivamente fornite al generatore. L'estensione ad altre discipline e la gestione di ulteriori fonti richiedono lavoro dedicato; non si presume una verifica automatica di qualsiasi riferimento inserito in un brief.

## Lettore e PDF

HTML e PDF sono prodotti dagli stessi blocchi della versione salvata, senza nuove richieste AI. Il lettore non esegue script e non carica librerie remote. I collegamenti ai riferimenti si aprono nel browser solo su azione dell'utente.

Il PDF conserva spiegazioni, esempi, dati di prova, trascrizioni, tabelle, sintesi, glossario, domande e risposte. Le note interne e i rapporti di revisione rimangono nell'app. Si usa un unico materiale, senza versioni separate studente/docente. I font sono inclusi nel pacchetto e distribuiti con licenza. La notazione matematica di questo traguardo è lineare Unicode: il rendering TeX e le formule complesse non sono ancora implementati.

La valutazione del primo traguardo comprende correttezza degli esempi, continuità concreta fra le due lezioni, assenza di riferimenti inventati, conservazione delle versioni e controllo visivo delle pagine esportate. La qualità generale di sostituzione del libro di testo richiede ulteriori validazioni con il docente e una UDA completa di materiali collegati.

## Benchmark interno e tuning 0.3.2

Su scelta delegata dal docente, la prima UDA del pilota è stata completata con un laboratorio e rigenerata dopo la valutazione. Il [rapporto](evidence/didactic-benchmarks/2026-11-17/REPORT.md) documenta rubrica, confronto prima/dopo, errori sfuggiti ai revisori e correzioni successive. Il campione installato nell’app conserva per ogni lezione la versione iniziale, quella rigenerata e la correzione editoriale finale. I PDF e le note restano associati alla versione selezionata.

La revisione consultiva riceve anche `visible_examples`, ricavato dallo stesso helper usato dal lettore e dal PDF. Conosce così sia l’ordine degli esempi sia la trascrizione realmente mostrata, evitando di scambiare lo stdout tecnico per il testo della pagina. I prompt dei ruoli sono in `engine/didactyx_engine/lesson_prompts.py`; un fingerprint impedisce riprese con istruzioni cambiate. Il risultato riguarda un campione interno e non dimostra da solo efficacia in classe o generalizzazione ad altre discipline.

Le ultime precisazioni dei prompt sulle trascrizioni sono state provate su un paragrafo mirato; la versione 3 del campione comprende correzioni editoriali esplicite, valutate separatamente. Non è stata eseguita un’altra rigenerazione integrale della UDA con quelle ultime precisazioni.
