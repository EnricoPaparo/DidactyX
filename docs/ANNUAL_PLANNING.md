# Progettazione annuale · macOS 0.2.0

## Utilizzo

Aprire `dist/DidactyX.app`, creare un programma e compilare il brief. Le sezioni strutturate sono facoltative: il motore interpreta anche un testo libero essenziale e rende esplicite le ipotesi sulle informazioni mancanti. Le impostazioni mostrano il collegamento al Codex installato sul Mac e permettono di scegliere la cartella dei PDF.

**Genera percorso annuale** avvia la progettazione reale tramite l'account ChatGPT già collegato a Codex. Non richiede una chiave API. L'app mostra il passaggio in corso e rimane utilizzabile mentre Codex lavora. Un percorso esteso può richiedere diversi minuti: non viene ridotto a una risposta breve per accelerare l'interfaccia.

La pagina **Percorso annuale** presenta contesto, ipotesi, obiettivi annuali, monte ore, UDA, lezioni previste e progetti progressivi. Le schede delle UDA si espandono per consultare tutti i metadati. Il monte ore distingue teoria, laboratorio, verifiche, riserva per recupero e margine. Le ultime due categorie non diventano lezioni aggiuntive nel programma.

Lo scheletro è in sola lettura. Per cambiarlo, aggiornare il brief oppure usare **Rigenera scheletro** con una richiesta facoltativa. La generazione ricostruisce e revisiona l'intero anno, conservando le versioni precedenti. Il menu delle versioni permette di consultarle ed esportarle.

**Revisiona** produce un rapporto indipendente sulla versione corrente. Le osservazioni distinguono correttezza, coerenza e indicazioni didattiche. Il rapporto non modifica il percorso: il docente può mantenerlo oppure scegliere **Rigenera con questi suggerimenti**. I vincoli espliciti del docente restano parte del contesto.

**Esporta PDF** usa la versione visualizzata già salvata, senza una nuova generazione. Il programma include i metadati annuali, tutte le UDA e le relative lezioni con obiettivi, concetti, prerequisiti, metodi, tempi e collegamenti ai progetti. I collegamenti sono riportati con i titoli. Ogni lezione mostra anche il proprio codice, così i rimandi presenti nei progetti sono rintracciabili. L'esportazione conserva le versioni e non sovrascrive PDF esistenti. Le note di controllo e i rapporti di revisione rimangono consultabili nell’app; non vengono aggiunti al programma da distribuire.

Questa versione genera la progettazione e i metadati delle lezioni. I contenuti completi, le immagini, le mappe, le esercitazioni e le verifiche vengono implementati negli incrementi successivi.

## Workflow e qualità

Il motore apre una sessione Codex distinta per ogni ruolo, con ragionamento alto e risposta strutturata:

1. Interpretazione del brief e definizione del contesto e dei vincoli annuali.
2. Progettazione delle UDA e dei progetti progressivi sull'intero anno.
3. Revisione e correzione della struttura delle UDA.
4. Progettazione di tutte le lezioni considerando l'intera struttura annuale.
5. Revisione e correzione dell'intero scheletro delle lezioni.

Le richieste di modifica applicate appartengono al contesto della nuova versione: una successiva rigenerazione a brief invariato deve conservarle salvo nuove indicazioni. Il motore rende esplicito ai ruoli se il brief è cambiato rispetto alla versione precedente.

Il contesto viene trasmesso agli autori e ai revisori insieme al brief, alla richiesta di modifica e, in rigenerazione, alla versione precedente. La disponibilità dei metadati annuali prepara la continuità didattica; il recupero dei contenuti effettivi delle lezioni appartiene all'incremento 3.

Controlli deterministici indipendenti dal modello verificano il formato, l'unicità degli identificativi, la copertura degli obiettivi, i riferimenti a progetti e UDA, le ore e i prerequisiti tra lezioni. Un prerequisito deve esistere ed essere precedente nel percorso. Le somme delle lezioni corrispondono alle ore dell'UDA e le somme delle UDA alle categorie annuali. La revisione finale deve conservare il contesto inizialmente interpretato.

In caso di incongruenza, il revisore riceve gli errori strutturali e tenta il riallineamento dell'intero risultato. Dopo due tentativi il lavoro resta riprendibile e la versione incompleta non viene pubblicata. Questo limite controlla i cicli automatici, senza ridurre il contenuto richiesto. I controlli strutturali non costituiscono una certificazione della qualità didattica, che va valutata sui percorsi effettivi insieme al docente.

Le richieste esplicite prevalgono sui suggerimenti pedagogici generali. I revisori devono segnalare eventuali scostamenti anziché sostituire silenziosamente le scelte del docente. Non vengono inventati riferimenti a documenti curricolari non forniti.

## Persistenza e interruzioni

L'archivio viene migrato dalla fondazione alla versione SQLite 2 conservando programmi, brief e impostazioni. Una sola attività può essere in corso per programma. Il contesto della richiesta e l'ultimo passaggio completato vengono salvati localmente.

**Interrompi** conserva i risultati già completati. **Riprendi** riusa quei risultati e rilancia il passaggio incompleto. La chiusura dell'app sospende l'attività; alla riapertura le attività appartenenti a un processo terminato risultano riprendibili. Rete, accesso all'account e disponibilità della quota possono impedire il completamento di un passaggio.

Una nuova versione diventa corrente solo dopo il completamento del workflow e dei controlli, in una transazione SQLite. Un errore o una cancellazione non sostituisce la versione precedente. Se il brief viene modificato durante il lavoro, il risultato completato resta nello storico senza essere applicato automaticamente al nuovo brief. Il confronto tra brief corrente e brief salvato della versione è visibile nell'interfaccia.

Le sessioni generative sono effimere e non hanno tool, shell o navigazione abilitati. L'adattatore riusa l'autenticazione Codex e non legge né copia i file delle credenziali. Nessuna email, credenziale o quota personale viene inclusa nelle evidenze pubblicate nel repository.

## Verifica riproducibile

Costruire il pacchetto con `bash scripts/build_macos.sh` e avviare `bash scripts/check_foundation.sh`. La suite verifica anche migrazione, versioni immutabili, ripresa dei passaggi, cancellazione, brief cambiato durante il lavoro, revisione consultiva e PDF senza chiamate generative. Il controllo Swift usa il motore effettivamente incluso nell'app per verificare comunicazione, richieste concorrenti e riapertura.

`python3 scripts/check_planning_live.py` esegue un collaudo reale separato con un programma fittizio di fisica di 66 ore, quattro UDA e un progetto trasversale. Usa la quota dell'account Codex collegato. `--regenerate` richiede di anticipare i circuiti rispetto a energia e calore e conserva la versione precedente. Dati e risultati di collaudo rimangono nelle cartelle ignorate `tmp/` e `output/`.

`--minimal` prova invece un brief di una sola frase, dalle variabili alle condizioni Python, con 12 ore complessive e nessuna indicazione sulla scuola o sulla classe. Il controllo richiede un percorso valido e ipotesi esplicite per il contesto mancante. I collaudi generativi sono volontari e separati dalla suite automatica, che non consuma quota.

I PDF vengono prodotti con ReportLab e i font DejaVu distribuiti con la relativa licenza. Il loro contenuto deriva dal percorso strutturato salvato; l'impaginazione deve essere controllata anche visivamente sul campione reale.

## Esito del collaudo del 15 novembre 2026

Superati 20 test automatici e l’integrazione Swift con il motore incluso nel pacchetto. Il collaudo reale ha prodotto un anno fittizio di 66 ore con quattro UDA e 35 lezioni; la rigenerazione richiesta dall’app ha anticipato i circuiti e ricalibrato il percorso in 37 lezioni, conservando le ore e la prima versione. Il brief essenziale di 12 ore ha prodotto quattro UDA e 15 lezioni con ipotesi esplicite. La revisione su richiesta ha restituito quattro raccomandazioni senza modificare lo scheletro.

Entrambe le versioni annuali sono state esportate dal motore incluso nell’app: 24 pagine ciascuna, tutte renderizzate e controllate visivamente. Campioni e risultati sono in [evidence/annual-planning/2026-11-15](evidence/annual-planning/2026-11-15/README.md).
