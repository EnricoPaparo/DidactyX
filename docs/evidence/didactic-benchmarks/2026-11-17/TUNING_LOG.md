# Diario del tuning didattico

## Valutazione iniziale

I due valutatori convergono sulla debolezza di C4: le prove dichiarate più autonome ripetono casi già risolti. La UDA non supera la soglia interna, pur ottenendo 86,25/100. Le sei mutazioni note sono riconosciute dal revisore e i due controlli rispettati.

## Prima iterazione generativa

Il contratto `didactic-v2-9856ad607bf0` introduce tentativi precedenti alle soluzioni, nuovi dati pertinenti e allineamento tra corpo e note. La prima L1 rigenerata viene però scartata prima della promozione: i nuovi dati sono già presenti nei casi del codice, resi visibili prima delle consegne.

Il file [tuning-iteration-1/finding.json](tuning-iteration-1/finding.json) conserva il riscontro. La generazione batch viene interrotta dopo la pubblicazione di L1; questa versione resta immutata. Il controllo reale di ripresa rifiuta di mescolare il vecchio contratto con quello aggiornato.

## Seconda iterazione generativa

Il contratto `didactic-v2-25661f37ff47` esplicita agli autori e ai revisori automatici che ogni caso associato al codice viene stampato con input e output nello stesso punto: non è un test nascosto. I casi di una prova devono quindi comparire dopo la consegna, oppure restare esclusi dagli esempi già mostrati. La UDA riparte integralmente dal campione iniziale in un nuovo archivio. Le istruzioni di generazione sono congelate durante questa prova.

## Revisore consultivo: controesempio reale

Il caso E01 usa esattamente la L1 scartata. Il revisore consultivo inizialmente affinato non trova il limite di autonomia, pur segnalando un dettaglio redazionale. Il risultato resta conservato come mancata rilevazione: i successi sulle mutazioni predisposte non bastano a dimostrare copertura dei difetti reali.

Un ulteriore candidato del revisore riceve la stessa informazione sull'ordine editoriale. Sul medesimo E01 riconosce ora che le risposte sono mostrate prima della consegna e distingue il limite dell'evidenza autonoma dal valore delle spiegazioni. Su F01, predisposto prima del nuovo test, rileva un errore sulla conversione della variabile testuale. Su F02 rispetta il consolidamento deliberato e non impone casi nuovi.

Il candidato è verificato in un file di istruzioni separato mentre la generazione della UDA prosegue con il proprio contratto congelato. Gli otto casi originali sono rieseguiti come regressioni; non vengono presentati come un nuovo set ignoto. I pesi, le soglie e le istruzioni dei due valutatori dei contenuti rimangono invariati.

## Allineamento con la rappresentazione effettiva

Nelle regressioni, il candidato con sole istruzioni trova il difetto E01, ma in H04 suggerisce erroneamente che il testo visibile ometta i dati digitati. Il renderer usa invece una trascrizione verificata con eco degli input, distinta dallo stdout tecnico. Il rilievo non fondato resta conservato in `reviewer-instruction-only/H04-unfounded-finding.json`.

Il nuovo input `visible_examples` viene ricavato dallo stesso helper usato dal lettore e dal PDF: esplicita posizione, dati e testo effettivamente mostrato. Il revisore non deve quindi indovinare la visualizzazione dai soli valori tecnici. Nella successiva regressione H04 riconosce correttamente la trascrizione, preservando il controllo sui frammenti intenzionalmente errati.

Anche i valutatori dei contenuti ricevono questo contesto, con criteri e soglie invariati. Per mantenere confrontabili i giudizi, il baseline completo viene rivalutato con lo stesso contesto e le stesse istruzioni applicate al materiale finale. I rapporti iniziali rimangono disponibili: il confronto conclusivo usa soltanto la coppia allineata alla rappresentazione effettiva.

## Valutazione della rigenerazione e correzione editoriale

I due giudizi allineati alla rappresentazione confermano il miglioramento di C4: la UDA raggiunge 3/4 e supera la soglia, con 87,5/100. Il punteggio C1 scende però a 3/4 per descrizioni del solo stdout accanto alle trascrizioni con eco. L1 e L2 raggiungono 91,25/100. Questi esiti restano in audit-tuned e non vengono sostituiti.

Cinque blocchi e tre note vengono corretti mediante patch esplicite nella versione 3, mantenendo identici programmi, attività e casi. Questa è una correzione editoriale del campione, non una nuova esecuzione completa del workflow. La terza valutazione audit-edited applica gli stessi criteri e istruzioni. Le ultime regole generali dell’autore e del revisore della continuità chiariscono la rappresentazione delle trascrizioni; una prova mirata su input/print di un nome ne verifica il paragrafo, senza pretendere una validazione integrale della nuova generazione.
