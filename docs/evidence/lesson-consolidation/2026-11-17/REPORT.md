# Consolidamento del motore delle lezioni · DidactyX 0.3.3

**Data:** 17 novembre 2026. **Stato:** generazione e valutazione in corso; questo documento non è ancora il rapporto conclusivo.

## Mandato

Il docente ha autorizzato il punto 1 del piano concordato: verificare integralmente i prompt definitivi, rafforzare la scrittura individuale nel laboratorio, rendere più flessibili i tempi e ripetere il benchmark. Il risultato richiesto è una UDA prodotta dall’intero workflow, senza correggere editorialmente i contenuti dopo la generazione per farli superare la prova.

Il campione mantiene classe fittizia, brief e struttura annuale del benchmark precedente: Python per principianti, seconda superiore tecnica, UDA di sei ore composta da due lezioni teoriche di due ore e un laboratorio di due ore. Lo scheletro annuale non viene modificato. Il confronto riguarda i contenuti delle lezioni, non mappe, percorsi di esercizi dedicati o verifiche formali.

## Interventi al motore

Gli autori devono distinguere una previsione sul codice fornito dalla costruzione delle istruzioni. Quando gli obiettivi richiedono realizzare o modificare una soluzione, il laboratorio deve raccogliere un prodotto individuale pertinente, con consegna prima della soluzione, usando concetti già introdotti. La spiegazione resta un’evidenza distinta dal programma funzionante e dal lavoro della coppia.

La pianificazione del tempo deve proteggere tentativo individuale e restituzione. In caso di difficoltà sui prerequisiti o nelle prime prove, deve indicare concretamente quali ripetizioni o approfondimenti rendere facoltativi, conservando il lavoro essenziale entro le ore disponibili. Rimangono spiegazioni complete per la consultazione e nessun limite di parole.

Anche i revisori automatici ricevono ora gli esiti dei controlli sugli esempi e la loro rappresentazione effettiva, prodotta dallo stesso helper del lettore e del PDF. Il revisore della continuità riceve la proposta corretta dal revisore disciplinare, con trascrizioni ricalcolate su quella proposta. Le fasi già concluse non vengono rieseguite durante la ripresa.

Le istruzioni del revisore consultivo e le regole comuni di rispetto del docente rimangono identiche a quelle già verificate. Il nuovo intervento riguarda generazione e revisioni automatiche. L’interfaccia mantiene il flusso minimale esistente.

## Protocollo e confronto

Il [protocollo](PROTOCOL.md) viene fissato prima della prova. Le istruzioni e gli hash sono in [prompt-freeze.json](prompt-freeze.json), contratto `didactic-v2-a0632f90c6a5`. La generazione parte dal corpus baseline congelato in un archivio separato e procede L1→L2→L3, facendo usare alle lezioni successive i corpi appena prodotti. I materiali personali e le evidenze storiche restano separati.

Si mantiene la [rubrica precedente](../../../../benchmarks/didactic/rubric.json): sei criteri 0–4, pesi 25/20/15/15/15/10, minimo 3 per criterio, almeno 75/100 e nessuna criticità grave. Due sessioni distinte dello stesso servizio, disciplinare e didattica, valutano ogni lezione e la UDA con le medesime istruzioni dei confronti precedenti. Il riepilogo usa il minimo per criterio dei due giudizi; ogni citazione deve esistere nei materiali salvati o nella rappresentazione effettivamente mostrata.

I riscontri aggiuntivi del punto 1 verificano coerenza delle trascrizioni in tutte e tre le lezioni, produzione individuale di istruzioni nel laboratorio e riduzione concreta del carico che preservi lavoro individuale e restituzione. Sono condizioni dichiarate prima della prova, separate dai pesi della rubrica.

Il riferimento storico resta distinto in tre fasi: baseline 0.3.1, rigenerazione 0.3.2 e correzione editoriale esplicita della versione 3. Quest’ultima non viene presentata come uscita autonoma del generatore. Il [rapporto precedente](../../didactic-benchmarks/2026-11-17/REPORT.md) conserva anche i controesempi e le iterazioni scartate.

## Verifiche e limiti

I 48 test automatici e l’integrazione Swift con il motore incluso hanno superato il controllo iniziale della build 0.3.3. Il nuovo test fa modificare il codice dal primo revisore e verifica che il secondo riceva la trascrizione del codice aggiornato, inclusi gli input digitati.

Gli undici risultati precedenti del revisore consultivo vengono riutilizzati soltanto dopo aver ricalcolato e confrontato gli hash di istruzioni effettive e input. Non sono undici nuove chiamate AI: il [riscontro](reviewer-regression-reuse.json) rende esplicito il riuso. I vecchi esiti non vengono attribuiti a istruzioni cambiate.

Il collector del consolidamento verifica contratto congelato, identità delle istruzioni dei valutatori, struttura, riferimenti, esecuzioni e corrispondenza tra contenuto pubblicato e uscita finale del workflow. Una lettura didattica dei testi verifica i tre requisiti specifici e ne registra citazioni controllabili. I controlli del codice non dimostrano da soli la qualità della spiegazione o l’apprendimento.

È una validazione interna su un solo percorso fittizio. Autori e valutatori usano lo stesso servizio generativo; la separazione dei ruoli non elimina errori condivisi. Il modello predefinito non è fissato e le generazioni non sono deterministiche. Non vengono misurati apprendimenti, tempi effettivi in classe, efficacia su altre discipline o adeguatezza individuale per DSA/DVA. Le valutazioni dei tempi restano stime. La lettura conclusiva della sessione responsabile non è una valutazione umana esterna indipendente.

## Perimetro residuo

L’incremento successivo riguarda arricchimento visivo, mappe concettuali, percorsi di esercizi dedicati e verifiche che usino tutti i materiali effettivi, con varianti e adattamenti richiesti dal docente. Feedback delle verifiche e recupero rimangono nell’incremento 5. Consolidamento dell’uso continuativo sul Mac e futura valutazione di Windows restano attività successive. Formule complesse e validazione su altre discipline richiedono lavoro dedicato.
