# Prima applicazione macOS

- **Versione:** 0.1.0
- **Incremento:** fondazione locale
- **Ambito:** programmi, brief, archivio e stato dell'account

## Utilizzo

L'app compilata è disponibile in `dist/DidactyX.app`. Si apre dal Finder con un doppio clic. Python e il motore locale sono inclusi nel pacchetto; per utilizzare le funzioni dell'incremento non occorre avviare un terminale o installare Python.

La home mostra i programmi salvati. **Nuovo programma** apre una finestra con titolo, classe, descrizione e brief iniziale facoltativo. La creazione apre direttamente il programma.

Nel programma sono disponibili il brief libero, sette sezioni facoltative per indicazioni più specifiche e i dati descrittivi. Le modifiche vengono salvate automaticamente. Il ritorno alla home e la chiusura dell'app attendono il salvataggio delle modifiche; un errore viene mostrato e non deve essere scambiato per un salvataggio riuscito.

Le impostazioni leggono lo stato reale del login Codex già presente, l'account, l'eventuale piano e la quota quando disponibile. Consentono di aprire la cartella dell'archivio e scegliere la destinazione predefinita dei PDF. Accesso e cambio account restano gestiti dal client Codex installato: in questo incremento l'app non modifica l'autenticazione.

Questo incremento prepara il contenitore di lavoro. La generazione dello scheletro, le revisioni didattiche e l'esportazione PDF verranno collegate con gli incrementi successivi. La lettura dello stato Codex non genera contenuti AI.

## Dati locali

Il percorso predefinito è `~/Library/Application Support/DidactyX`. Il database `library.sqlite3` conserva programmi, brief e preferenze. SQLite può mantenere file di lavoro accanto al database. Per una copia manuale dell'archivio, chiudere prima l'app e copiare l'intera cartella.

Il salvataggio del brief riguarda una bozza. Nessuna modifica al brief produce già una pianificazione annuale, né introduce una struttura implicitamente applicata.

L'archivio del docente non si trova nel repository. I file di costruzione, il pacchetto `.app` e i dati temporanei di collaudo sono esclusi da Git.

## Costruzione dal codice

Servono gli strumenti di sviluppo Swift 6 e Python 3.12 o successivo per preparare il pacchetto. La costruzione verificata ha utilizzato Swift 6.3.3 e Python 3.12.14. Il pacchetto risultante include il runtime Python impiegato nella costruzione.

```sh
bash scripts/build_macos.sh
```

Il comando prepara un ambiente Python isolato in `tmp/packaging-venv`, installa le dipendenze di confezionamento con versioni fissate, compila Swift, raccoglie il motore e crea l'app. Se occorre selezionare l'interprete per la prima creazione dell'ambiente:

```sh
DIDACTYX_BUILD_PYTHON=/percorso/python3 bash scripts/build_macos.sh
```

Chiudere l'app prima di ricostruirla. La build applica una firma ad hoc per l'utilizzo locale e la verifica. La distribuzione ad altri Mac, la firma Developer ID e la notarizzazione restano attività successive.

Il target dichiarato del progetto Swift è macOS 14; il pacchetto corrente è stato collaudato sul Mac arm64 con macOS 26.7.2 disponibile in questa sessione. Non è stata ancora verificata la compatibilità con altre versioni del sistema o con Mac Intel.

## Collegamento tra app e motore

Il protocollo usa messaggi JSON UTF-8 separati da newline. Ogni richiesta ha un identificativo; le risposte possono arrivare fuori ordine e conservano l'identificativo corrispondente. Lo schema di base è in [local-rpc.schema.json](../schemas/local-rpc.schema.json).

Le operazioni disponibili sono `system.ping`, `program.list`, `program.get`, `program.create`, `program.update`, `settings.get`, `settings.update` e `account.status`.

`program.update` richiede una revisione attesa: due aggiornamenti partiti dalla stessa versione non possono sovrascriversi silenziosamente. Titolo, classe, descrizione e brief vengono aggiornati in un'unica transazione. Un errore di validazione conserva i valori precedenti. Le revisioni di questo incremento sono contatori di concorrenza, non ancora la cronologia dei futuri scheletri e materiali.

Il motore gestisce le richieste di lettura dell'account separatamente dalle operazioni dell'archivio, per mantenere utilizzabile l'editor durante il controllo Codex. Il collegamento passa dal CLI rilevato sul Mac e non legge o copia file di credenziali.

## Verifiche

Le verifiche automatiche dell'archivio e del server si eseguono con:

```sh
python3 -m unittest discover -s tests -v
```

La prova Swift usa il client effettivo dell'app, il motore incluso nel pacchetto e un archivio temporaneo. Il comando seguente esegue sia le verifiche Python sia il controllo Swift, con i Command Line Tools disponibili e senza richiedere XCTest:

```sh
bash scripts/check_foundation.sh
```

Il collaudo nativo ha verificato creazione di un programma fittizio, modifica del brief e di una sezione specifica, chiusura immediata, riapertura dei dati e modifica della descrizione prima del ritorno alla home. Il programma usato per la prova viene rimosso dall'archivio dopo il collaudo. Account e quota sono stati letti realmente, senza pubblicarne i valori personali nel repository.

La generazione annuale e la qualità dei materiali non rientrano nella validazione di questo incremento.
