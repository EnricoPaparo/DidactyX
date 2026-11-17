# Consolidamento del motore delle lezioni · DidactyX 0.3.3

**Data:** 17 novembre 2026. **Stato:** punto 1 completato sul pilota; workflow integrale e requisiti specifici verificati.

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

## Risultati del confronto

C1 = correttezza; C2 = spiegazione; C3 = continuità; C4 = attività e aiuti; C5 = comprensione e applicazione; C6 = fattibilità e accessibilità. I valori sono i minimi dei due giudizi per criterio.

| Materiale 0.3.3 | C1 | C2 | C3 | C4 | C5 | C6 | Totale /100 | Soglia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | 4 | 4 | 4 | 3 | 4 | 4 | 96,25 | Superata |
| L2 | 4 | 4 | 4 | 4 | 4 | 4 | 100,0 | Superata |
| L3 | 4 | 4 | 4 | 3 | 3 | 3 | 90,0 | Superata |
| UDA | 4 | 4 | 4 | 3 | 3 | 3 | 90,0 | Superata |

| Fase della UDA | Totale interno /100 | Soglia | Metodo di produzione |
| --- | --- | --- | --- |
| 0.3.1 iniziale | 86,25 | Non superata | Workflow generativo |
| 0.3.2 rigenerata | 87,5 | Superata | Workflow generativo |
| 0.3.2 corretta editorialmente | 93,75 | Superata | Patch esplicite dopo la generazione |
| 0.3.3 consolidamento | 90,0 | Superata | Workflow completo senza patch successive |

Il nuovo campione supera la UDA rigenerata 0.3.2 (87,5), ma non il campione allora corretto editorialmente (93,75). Il consolidamento verifica la produzione effettiva dell’intero motore e i tre requisiti dichiarati; non dimostra un miglioramento di ogni punteggio. Il minimo per criterio può risultare inferiore a entrambi i totali dei singoli giudici, perché conserva le debolezze rilevate da ciascuno. Anche il 100 di L2 descrive soltanto questa rubrica sul campione: non certifica l’assenza di qualsiasi difetto.

Rapporti originali: [disciplinare](audit/discipline.json), [didattico](audit/pedagogy.json). Calcoli, hash delle uscite dei passaggi e controlli: [results.json](results.json). Le istruzioni dei giudici corrispondono, tramite hash, a tutte e tre le fasi storiche usate nel confronto.

## Riscontri specifici del punto 1

- **Trascrizioni:** nelle tre lezioni i paragrafi distinguono le risposte digitate dai messaggi di print e corrispondono agli esempi mostrati.
- **Produzione individuale:** L3 S7 richiede un file personale con acquisizioni, conversioni, prodotto, confronto con > e messaggi da collocare nei rami. Prima della soluzione di S8 vengono richiesti istruzioni, prove, traccia e spiegazione individuali. Il confronto con > era già discusso in L2: l’attività è una ricostruzione operativa con aiuti ridotti, non un problema concettualmente inedito.
- **Tempi e percorso ridotto:** la scansione è di 120 minuti. In caso di difficoltà, S1/S2 crescono complessivamente di dieci minuti e S5/S6 ne liberano dieci. S7 mantiene 25 minuti per il lavoro individuale e S8 quindici per confronto, restituzione e correzione. Le altre prove restano consultabili. I tempi non sono stati osservati in classe.

Citazioni letterali e motivazioni della lettura conclusiva: [acceptance.json](acceptance.json). Il collector ne verifica presenza e corrispondenza ai corpi finali; la sufficienza didattica rimane un giudizio della sessione responsabile del benchmark.

## Limiti didattici residui

I valutatori concordano sul valore della produzione individuale, ma rilevano che la disposizione dei messaggi nella variante con > era già spiegata. L’attività non misura quindi una scelta logica interamente nuova. In L1 la parte individuale osserva soprattutto prodotto e stampe, mentre acquisizione e conversioni sono ancora sostenute dal modello e dalla guida.

Le due prove individuali obbligatorie di L3 mantengono entrambe spesa 7,5: da sole non rivelano un programma che assegni una spesa costante. Il testo riconosce questo limite e propone nell’autocontrollo una prova discriminante, che resta però di consultazione. Un prossimo miglioramento mirato potrà variare un fattore del prodotto anche nelle prove obbligatorie, conservando la sostenibilità del carico.

La gestione del computer condiviso prevede turni e cartelle personali, ma non ne dimensiona numericamente la ripartizione per ciascuno. La sostenibilità dipende dalle dotazioni reali e richiede una verifica prima della lezione. Sono limiti minori registrati nei rapporti, non risultati nascosti o risolti con modifiche successive al contenuto.

## Verifiche e limiti

I **48 test automatici**, l’integrazione Swift con il motore incluso, la build release 0.3.3 e la firma locale hanno superato i controlli. Il nuovo test fa modificare il codice dal primo revisore e verifica che il secondo riceva la trascrizione del codice aggiornato, inclusi gli input digitati.

Gli undici risultati precedenti del revisore consultivo vengono riutilizzati soltanto dopo aver ricalcolato e confrontato gli hash di istruzioni effettive e input. Non sono undici nuove chiamate AI: il [riscontro](reviewer-regression-reuse.json) rende esplicito il riuso. I vecchi esiti non vengono attribuiti a istruzioni cambiate.

Il collector del consolidamento verifica contratto congelato, identità delle istruzioni dei valutatori, struttura, riferimenti, esecuzioni e corrispondenza tra contenuto pubblicato e uscita finale del workflow. Una lettura didattica dei testi verifica i tre requisiti specifici e ne registra citazioni controllabili. I controlli del codice non dimostrano da soli la qualità della spiegazione o l’apprendimento.

È una validazione interna su un solo percorso fittizio. Autori e valutatori usano lo stesso servizio generativo; la separazione dei ruoli non elimina errori condivisi. Il modello predefinito non è fissato e le generazioni non sono deterministiche. Non vengono misurati apprendimenti, tempi effettivi in classe, efficacia su altre discipline o adeguatezza individuale per DSA/DVA. Le valutazioni dei tempi restano stime. La lettura conclusiva della sessione responsabile non è una valutazione umana esterna indipendente.

## Controlli dei materiali e consegna

Il collector verifica l’identità del contratto congelato, del brief e della struttura annuale; i riferimenti puntano alle nuove versioni effettive. Per ogni lezione il contenuto pubblicato coincide con il risultato dell’ultimo passaggio del workflow, incluse le eventuali correzioni automatiche. Gli hash dei passaggi e dei corpi pubblicati sono conservati nel riepilogo. Le versioni iniziali rimangono immutate.

| Lezione | Pagine PDF | Casi eseguiti | Blocchi illustrativi non eseguiti | Stringhe studente controllate |
| --- | --- | --- | --- | --- |
| L1 | 20 | 9 | 3 | 326 |
| L2 | 20 | 9 | 1 | 273 |
| L3 | 23 | 6 | 4 | 340 |

Tutti i **24 casi eseguibili** corrispondono a stdout e trascrizione attesi anche nel motore congelato. Le **63 pagine** sono state renderizzate e controllate visivamente; nessuna delle **939 stringhe** del materiale studente controllate risulta mancante. I raster dei PDF prodotti dal motore incluso coincidono con quelli ispezionati dal sorgente. Nessuna patch editoriale è stata applicata ai contenuti dopo il workflow.

Evidenze: [manifest del batch](generated/generation.json), [verifica PDF](pdf-qa.json), [casi nel motore incluso](frozen-code-checks.json), [verifiche software e native](software-verification.json).

Nell’app 0.3.3 è disponibile **Python · UDA 1 · consolidamento 0.3.3**, con tre lezioni e storico iniziale 1 / rigenerato 2. L’importazione è additiva e conserva tutti i record precedenti. Sono verificati nell’interfaccia programma, contenuto del laboratorio, storico e messaggio di export «PDF salvato». [Riscontro dell’installazione](app-sample.json).

PDF finali: [L1 · Variabili, input e conversioni](pdf/lesson-L1.pdf), [L2 · Decidere con if ed else](pdf/lesson-L2.pdf), [L3 · Laboratorio](pdf/lesson-L3.pdf). Le note del docente e i rapporti di revisione rimangono interni all’app.

## Riproduzione

La generazione si esegue con `scripts/check_didactic_uda_live.py`, archivio separato, sorgente `docs/evidence/didactic-benchmarks/2026-11-17/baseline` e target L1 L2 L3. Consuma quota Codex. Non sovrascrivere la cartella di questa prova. La ripresa richiede il medesimo contratto congelato.

Il ricontrollo senza chiamate AI si esegue con `python3 scripts/collect_lesson_consolidation.py --evidence docs/evidence/lesson-consolidation/2026-11-17 --data-dir tmp/lesson-consolidation/generated-db`. Richiede l’archivio locale della prova e i file del contratto congelato: per una futura riproduzione usare il commit registrato nel manifest e la versione del collector in questa PR. I dati personali e i binari non vengono inclusi in Git; i materiali scolastici delle evidenze sono fittizi. Le generazioni future non sono garantite identiche.

## Perimetro residuo

L’incremento successivo riguarda arricchimento visivo, mappe concettuali, percorsi di esercizi dedicati e verifiche che usino tutti i materiali effettivi, con varianti e adattamenti richiesti dal docente. Feedback delle verifiche e recupero rimangono nell’incremento 5. Consolidamento dell’uso continuativo sul Mac e futura valutazione di Windows restano attività successive. Formule complesse e validazione su altre discipline richiedono lavoro dedicato.
