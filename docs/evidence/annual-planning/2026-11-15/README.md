# Collaudo della progettazione annuale

Campioni generati con il motore reale e dati esclusivamente fittizi. Le sessioni riusano il login ChatGPT gestito da Codex; credenziali, identità dell'account, percentuali di quota e archivi SQLite non sono inclusi.

## Casi

- **Fisica, prima versione:** classe seconda di istituto tecnico, 66 ore; quattro UDA, teoria, laboratorio, verifiche e progetto progressivo. Il collaudo iniziale è stato avviato dal motore.
- **Fisica, rigenerazione:** dall'app macOS è stato richiesto di introdurre i circuiti prima di energia e calore conservando ore e numero di UDA. Sono stati provati anche interruzione e ripresa. La prima versione generata è stata copiata nell'archivio isolato dell'app per questo collaudo: non si tratta di una seconda generazione iniziale avviata dalla UI.
- **Brief essenziale:** «Parti dalle variabili e arriva alle condizioni if in Python. Ho 12 ore complessive». Il motore ha proposto il contesto mancante e lo ha dichiarato nelle ipotesi.
- **Revisione su richiesta:** rapporto indipendente sulla versione corrente; nessuna modifica alla struttura salvata né nuova versione del percorso.

I JSON dei percorsi conservano versione, brief, richiesta di modifica e risultato strutturato. I metadati operativi dell'archivio di prova sono omessi. Il rapporto di revisione resta distinto dal percorso e dal PDF da distribuire.

## Verifiche

`results.json` riporta gli esiti, il numero di lezioni e le pagine dei PDF. I controlli comprendono somme delle ore, obiettivi, prerequisiti, progetti, conservazione della prima versione, ordine delle UDA richiesto, selezione dello storico ed export dal pacchetto macOS. I titoli di tutte le UDA e delle lezioni vengono confrontati con il testo estratto dai PDF. Tutte le pagine esportate vengono renderizzate e controllate visivamente.

La suite automatica non usa Codex e non consuma quota; i campioni reali sono riproducibili con `scripts/check_planning_live.py`, secondo [ANNUAL_PLANNING.md](../../../ANNUAL_PLANNING.md). Gli archivi temporanei usati per il collaudo rimangono separati dall'archivio personale del docente.

Queste evidenze dimostrano il funzionamento del flusso e dei controlli sul campione. Non certificano la qualità didattica generale, il rispetto di un curricolo ufficiale non fornito o l'efficacia in classe. Il pilota con contenuti completi viene scelto con il docente nell'incremento successivo.
