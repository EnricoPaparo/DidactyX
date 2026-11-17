# Benchmark didattico · protocollo 1.0

Il benchmark valuta i punti 1–3 del piano: qualità delle lezioni, miglioramenti di autori e revisori e coerenza di una prima UDA completa. Il dominio iniziale è Python per principianti, seconda superiore fittizia, con due lezioni teoriche e una di laboratorio di due ore ciascuna. La rubrica non certifica apprendimenti o efficacia in classe.

## Disegno della prova

1. **Prima del tuning:** congelare rubrica, pesi, soglie, casi, prompt di riferimento e campioni L1/L2. Generare L3 con i prompt 0.3.1 in un archivio separato, completando i soli contenuti della prima UDA.
2. **Calibrazione:** applicare il revisore attuale a C01–C04. Gli oracoli rimangono fuori dall'input del modello. Tre casi contengono un difetto noto; uno controlla il rispetto di una scelta esplicita del docente.
3. **Valutazione dei contenuti:** due sessioni distinte, una con prospettiva disciplinare e una didattica, valutano L1, L2, L3 e la UDA con la stessa rubrica. Le citazioni devono esistere nei corpi salvati. Un punteggio alto richiede evidenze; lunghezza e dichiarazioni di qualità non danno punti.
4. **Tuning:** ricavare interventi generali dalle debolezze della calibrazione e dei materiali. Non inserire nei prompt di produzione gli identificativi o gli oracoli del benchmark. Congelare i nuovi prompt prima di aprire gli esiti H01–H04.
5. **Confronto:** rieseguire la calibrazione e applicare entrambi i prompt congelati ai quattro casi di controllo finali H01–H04. Rigenerare in ordine L1→L2→L3 con il workflow effettivo e rivalutare la UDA con gli stessi valutatori e criteri, senza comunicare la fase baseline/tuned al valutatore.
6. **Report:** documentare errori rilevati e mancati, falsi allarmi, punteggi per criterio, citazioni, risultati del codice e limiti. Gli esiti sfavorevoli rimangono nel report; non si modificano le soglie dopo aver visto i risultati.

Il set finale contiene difetti predisposti ma risultati non usati per scegliere il tuning. Non è un set segreto esterno: chi costruisce il benchmark conosce le mutazioni. È una verifica interna con controllo del processo, non una valutazione indipendente dell'intero sistema.

## Rubrica e accettazione

[rubric.json](rubric.json) definisce sei criteri con scala 0–4: correttezza 25%, spiegazione 20%, progressione 15%, attività e aiuti 15%, comprensione/trasferimento vicino 15%, fattibilità/accessibilità 10%. Per ogni materiale e per la UDA si conservano i punteggi di entrambi i valutatori. Il riepilogo usa il minimo per criterio: non si sceglie il giudizio più favorevole.

La soglia di progetto richiede almeno 3 in ogni criterio, punteggio ponderato almeno 75/100 e nessuna criticità grave. Si tratta di una regola di accettazione interna dichiarata prima della prova, non di una soglia scientificamente validata. Per la UDA occorrono tutti i contenuti, il ponte teoria-laboratorio, aiuti progressivamente ridotti e una prestazione individuale osservabile.

[cases.json](cases.json) contiene sei difetti e due controlli. Gli errori semantici sono costruiti in modo da superare formato, riferimenti ed esecuzione dei casi: la sola esecuzione corretta del codice non ne dimostra l'adeguatezza all'obiettivo. Il controllo negativo H04 contiene codice deliberatamente errato con spiegazione: un revisore deve distinguere un esempio diagnostico da un errore involontario.

Il conteggio degli errori individuati richiede una lettura del rapporto rispetto all'oracolo, con motivazione e riferimento alla proposta concreta. Il semplice numero di findings non è una misura di accuratezza. Eventuali suggerimenti ulteriori sui campioni non vengono automaticamente contati come falsi positivi; il falso allarme del controllo deve riguardare precisamente la scelta o il frammento protetti.

## Esecuzione

I comandi `review` e `audit` consumano quota Codex e usano il login già gestito dal client. Nessuna API key è richiesta. Tutti i dati scolastici sono fittizi; gli archivi di lavoro sono separati da quello personale.

```sh
python3 scripts/didactic_benchmark.py review --variant baseline --split calibration --output output/benchmark/calibration-baseline --work-dir tmp/benchmark/calibration-baseline
python3 scripts/didactic_benchmark.py review --variant tuned --split holdout --output output/benchmark/holdout-tuned --work-dir tmp/benchmark/holdout-tuned
python3 scripts/didactic_benchmark.py audit --materials docs/evidence/didactic-benchmarks/2026-11-17/baseline --output output/benchmark/audit-baseline --work-dir tmp/benchmark/audit-baseline
```

Per completare una UDA o rigenerarla con i prompt correnti:

```sh
python3 scripts/check_didactic_uda_live.py --data-dir tmp/nuova-uda --output output/benchmark/nuova-uda --targets L1 L2 L3
```

Per continuare un lavoro interrotto si ripete il comando aggiungendo `--resume`, mantenendo invariati i prompt. Il generatore conserva i materiali completati e non duplica le pubblicazioni già concluse. Per confrontare i materiali iniziali si usano i campioni congelati; rigenerarli con i prompt attuali non riproduce il baseline. Le generazioni non sono deterministiche e la versione del modello del client non viene fissata dal benchmark.

`python3 scripts/didactic_benchmark.py collect --evidence-root CARTELLA_EVIDENZE` verifica nuovamente citazioni, struttura, riferimenti ed esecuzioni e ricostruisce i riepiloghi a partire dai rapporti e dalle adjudication. Questo comando non usa AI.

I risultati vengono salvati dopo ogni chiamata con hash di input e prompt. Ripetere lo stesso comando riusa soltanto risultati con gli stessi hash. Non si sovrascrivono giudizi con input diversi. `baseline-prompts.json` conserva le istruzioni del revisore 0.3.1 per confronti riproducibili dopo il tuning.

## Fondamenti e limiti

Le fonti didattiche e disciplinari sono elencate nella rubrica: guide AERO ed EEF e documentazione ufficiale Python. Le indicazioni sono tradotte in criteri operativi per questo contesto; non impongono un'unica metodologia o una lunghezza prefissata. Le scelte esplicite del docente rimangono prioritarie e le raccomandazioni consultive.

I valutatori sono sessioni dello stesso servizio generativo usato dal prodotto: la separazione dei ruoli non elimina possibili errori e preferenze condivise. Le mutazioni note e i controlli eseguibili forniscono riscontri aggiuntivi. Il campione limitato non misura tutte le discipline, tutti i bisogni educativi o l'efficacia reale in classe. Le stime del carico e dei tempi sono giudizi sui materiali, non tempi di studenti osservati.
