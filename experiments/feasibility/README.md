# Prove di fattibilità

Questi script verificano capacità tecniche di Codex e dell'esportazione locale. Non costituiscono l'architettura o il motore definitivo di DidactyX. I dati della classe e gli esempi sono fittizi.

Il rapporto dei risultati è in [TECHNICAL_FEASIBILITY.md](../../docs/TECHNICAL_FEASIBILITY.md).

## Requisiti verificati

- Codex CLI installato e già collegato mediante ChatGPT.
- Python 3 per le prove del protocollo, senza pacchetti esterni.
- Per il PDF e i controlli offline: `reportlab`, `pypdf`, `Pillow` e font DejaVu Sans regolare e grassetto.
- Poppler per renderizzare il PDF e ispezionarne le pagine.

Le versioni effettivamente utilizzate sono riportate nel rapporto. Nessuna dipendenza viene installata automaticamente e nessuna chiave API viene creata o copiata.

## Esecuzione

Dalla radice del repository, il comando seguente verifica soltanto collegamento al protocollo, stato dell'accesso, catalogo modelli e disponibilità dei dati di quota:

```sh
python3 experiments/feasibility/probe_codex.py
```

Le seguenti prove effettuano richieste reali e utilizzano la disponibilità dell'account ChatGPT collegato:

```sh
python3 experiments/feasibility/probe_codex.py --live
python3 experiments/feasibility/probe_visual.py
python3 experiments/feasibility/probe_visual.py --image
```

La prova live genera due lezioni, esegue una revisione in una sessione distinta, interrompe una risposta dopo l'inizio dello streaming, riavvia il processo app-server e verifica il recupero del contesto. La prova della mappa richiede che le lezioni siano già presenti. La prova dell'immagine è separata e verifica il tool raster nativo, senza ripiegare su altri servizi.

I file di lavoro vengono salvati in `output/feasibility/`, esclusa da Git. La pubblicazione delle evidenze nel repository è un passaggio distinto, limitato ai campioni sintetici controllati. Le risposte complete dell'account, le credenziali e il checkpoint con l'identificativo della sessione non vengono pubblicati.

Per il PDF, utilizzare l'interprete con le dipendenze disponibili e indicare la cartella che contiene `DejaVuSans.ttf` e `DejaVuSans-Bold.ttf`:

```sh
python3 experiments/feasibility/build_sample_pdf.py --font-dir /percorso/dei/font
python3 experiments/feasibility/verify_evidence.py
```

Il builder produce il PDF, la mappa SVG e un esito iniziale con ispezione visiva ancora da svolgere. Dopo ogni modifica di impaginazione occorre renderizzare il PDF, controllare tutte le pagine e registrare separatamente il controllo visivo. `verify_evidence.py` svolge soltanto controlli tecnici offline e non certifica la qualità didattica.

## Confini della prova

Gli autori e il revisore sono sessioni separate dello stesso modello predefinito. La prova non delega lo sviluppo ad agenti autonomi e non valuta l'affidabilità su un intero anno scolastico. I timeout sono limiti del laboratorio tecnico e non limiti alla profondità dei contenuti del futuro prodotto.

Il codice usa il protocollo della versione Codex indicata nel rapporto. Non garantisce compatibilità con versioni differenti, né la disponibilità delle stesse funzioni su altri account. I tool shell, web e app sono disabilitati nei processi di prova; le richieste di tool gestite dal client vengono rifiutate. La generazione raster nativa viene abilitata soltanto nella prova dedicata.
