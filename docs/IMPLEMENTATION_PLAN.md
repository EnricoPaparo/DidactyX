# Piano di sviluppo iniziale di DidactyX

- **Data:** 15 novembre 2026
- **Base:** [architettura approvata](ARCHITECTURE.md) e [Project Brief](PROJECT_BRIEF.md)
- **Piattaforma:** macOS
- **Stato:** incremento 1 realizzato e collaudato; incrementi didattici successivi da realizzare

Ogni incremento produce un comportamento utilizzabile e verificabile. La priorità è il motore didattico; l'interfaccia cresce nella misura necessaria a usarlo. I criteri seguenti descrivono il completamento del singolo incremento e non riducono il perimetro finale del brief.

## 1 Fondazione locale

Creare la prima applicazione SwiftUI, il processo Python e il loro collegamento. Implementare l'archivio SQLite iniziale, la home dark e la creazione di un programma con titolo, classe, descrizione e brief. Aggiungere le impostazioni essenziali e la lettura dello stato Codex già verificata nel laboratorio.

**Risultato verificabile:** aprire l'app, creare un programma, chiuderla e riaprirla ritrovando i dati; entrare nel programma e consultare il brief. Il motore risponde alle richieste locali senza bloccare l'interfaccia. Lo stato dell'account risulta reale e gli errori di collegamento sono riconoscibili.

Le verifiche riguardano soprattutto salvataggio, collegamento tra processi e riapertura. L'app deve poter avviarsi dal Finder nell'ambiente di sviluppo, oltre che dagli strumenti di compilazione.

**Implementazione:** disponibile nella prima app macOS; dettagli e comandi in [FOUNDATION_MACOS.md](FOUNDATION_MACOS.md).

## 2 Primo flusso didattico completo

Implementare interpretazione del brief, progettazione e revisione delle UDA, progettazione e revisione delle lezioni e controllo complessivo dello scheletro. Integrare ore disponibili, teoria, laboratorio e progetti che attraversano più UDA.

La consultazione della struttura è in sola lettura. Il docente modifica il brief o formula una richiesta e avvia la rigenerazione completa. Conservare la versione precedente, distinguere il brief ancora da applicare e rendere corrente soltanto un risultato completato. Realizzare l'export PDF del programma annuale con UDA, metadati e lezioni.

**Risultato verificabile:** completare dall'app la sequenza programma, brief, scheletro revisionato, richiesta di modifica, nuovo scheletro e PDF. Una rigenerazione interrotta non cancella il percorso precedente. Un brief essenziale consente comunque al motore di procedere con ipotesi riconoscibili.

## 3 Lezioni e continuità didattica

Definire il formato strutturato dei contenuti e implementare il recupero del contesto. Generare e revisionare lezioni usando anche il contenuto effettivo di quelle precedenti. Gestire i contributi di più autori quando necessario, con revisione del risultato ricomposto.

Integrare il lettore WebKit e l'export delle lezioni. Verificare formule e rappresentazioni pertinenti al percorso pilota prima di fissare i template editoriali.

**Risultato verificabile:** almeno due lezioni collegate che riprendano correttamente esempi, terminologia e concetti. Il docente deve poter leggere e valutare la qualità dei contenuti nell'app e nei PDF, anche quando la seconda lezione viene sviluppata fuori sequenza.

La materia, la classe e gli obiettivi del pilota vengono scelti con il docente. Il campione matematico del laboratorio resta una prova tecnica, non una scelta implicita del primo caso reale.

## 4 Materiali collegati e valutazione

Integrare arricchimento visivo, mappe concettuali ed esercitazioni con autori e revisori dedicati. Implementare le verifiche usando lezioni, mappe ed esercitazioni pertinenti, con N varianti e gli adattamenti richiesti. Estendere le esportazioni PDF e il controllo di impaginazione.

**Risultato verificabile:** una prima UDA utilizzabile con i materiali collegati, una verifica in più varianti e un esempio sugli obiettivi minimi o personalizzati. I quesiti devono essere riconducibili agli obiettivi e alla preparazione; le varianti comparabili mantengono correttamente associate le soluzioni. Il docente può mantenere le proprie scelte anche quando il revisore segnala uno scostamento didattico.

## 5 Recupero e riallineamento

Implementare il feedback della verifica, le lezioni aggiuntive collegate all'UDA, i materiali mirati e la verifica di recupero. Gestire le dipendenze tra materiali dopo una modifica o una rigenerazione.

**Risultato verificabile:** dal feedback si ottiene un recupero con un diverso approccio esplicativo, collegato agli obiettivi interessati. Le lezioni aggiuntive sono esportabili ma restano escluse dal programma annuale. Le esigenze di tempo e le versioni da riallineare risultano riconoscibili.

## 6 Consolidamento per l'utilizzo sul Mac

Verificare ripresa delle attività, errori di rete e quota, consultazione senza connessione, conservazione dei dati e uso di raccolte più ampie. Completare il confezionamento dell'app e delle sue dipendenze, definire i requisiti minimi di macOS e controllare l'avvio nell'ambiente del docente.

**Risultato verificabile:** utilizzo personale continuativo con dati conservati, materiali leggibili, PDF controllati e interruzioni gestite senza presentare risultati incompleti come conclusi. La qualità viene valutata sui materiali e sul loro impiego didattico, insieme al docente.

## Prossima attività

Avviare l'incremento 2: collegare interpretazione del brief, progettazione e revisione del percorso annuale, rigenerazione completa e PDF del programma.
