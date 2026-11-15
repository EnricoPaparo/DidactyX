"""Workflow persistente: contesto, UDA, revisori e lezioni annuali."""

import math
import threading

from .generation import CodexGenerator, GenerationCancelled, GenerationError
from .planning_schema import CONTEXT, STRUCTURE, PLAN, REVIEW, plan_errors
from .planning_store import PlanningStore
from .store import DomainError


RULES = """Nei testi descrittivi e in review_notes rivolgiti al docente in italiano, con i titoli delle attività. Evita nomi dei campi JSON, dettagli del protocollo e autocertificazioni dei controlli; le note devono spiegare scelte didattiche, ipotesi e aspetti da valutare. Rispetta le richieste esplicite del docente anche quando divergono dalle abitudini didattiche: segnala lo scostamento nelle note senza sostituire la richiesta. Completa in autonomia le informazioni mancanti, indicando le ipotesi. Non inventare documenti ministeriali o fonti consultate: curriculum_references contiene solo documenti realmente forniti nel testo. Non generare il contenuto completo delle lezioni. Usa identificativi globalmente univoci: G1 per obiettivi annuali, U1 per UDA, U1-O1 per obiettivi dell'UDA, L1 per lezioni, P1 per progetti. Le ore sono ore di calendario: non contare due volte attività integrate. Recupero e margine sono riserve annuali, non lezioni aggiuntive nell'export. La nuova richiesta di modifica prevale sulle indicazioni precedenti. Se brief_changed è falso, la versione precedente rappresenta le scelte già applicate: conservale salvo nuove richieste, anche quando modificavano il brief originario. Se brief_changed è vero, integra le nuove indicazioni conservando le scelte precedenti compatibili. Per una rigenerazione ricostruisci l'intero percorso tenendo conto del brief attuale e della richiesta di modifica; il percorso precedente fornisce il contesto, senza impedirti di cambiarlo in modo coerente."""


class PlanningManager:
    def __init__(self, store, generator_factory=CodexGenerator):
        self.store = PlanningStore(store)
        self.generator_factory = generator_factory
        self.workers = {}
        self.lock = threading.Lock()
        self.closing = threading.Event()
        self.store.recover()

    def start(self, params, kind="generate"):
        job = self.store.new_job(params.get("program_id"), params.get("change_request", ""), kind)
        self._launch(job["id"])
        return job

    def resume(self, job_id):
        with self.lock:
            current = self.workers.get(job_id)
            if current and current[0].is_alive(): raise DomainError(-32009, "Attendi la conclusione dell'interruzione prima di riprendere.")
        job = self.store.resume(job_id)
        self._launch(job_id)
        return job

    def cancel(self, job_id):
        self.store.job(job_id)
        self.store.stop(job_id, "cancelled", "Generazione interrotta. I passaggi già conclusi sono conservati.")
        with self.lock:
            current = self.workers.get(job_id)
            if current: current[1].set()
        return self.store.job(job_id)

    def _launch(self, job_id):
        stopped = threading.Event()
        thread = threading.Thread(target=self._run, args=(job_id, stopped), daemon=True)
        with self.lock: self.workers[job_id] = (thread, stopped)
        thread.start()

    def _run(self, job_id, stopped):
        generator = None
        def cancelled():
            return stopped.is_set() or self.closing.is_set() or not self.store.owned_running(job_id)
        try:
            job = self.store.job(job_id, True)
            snapshot, checkpoint = job["snapshot"], job["checkpoint"]
            generator = self.generator_factory(self.store.store.directory, cancelled)

            def stage(key, label, role, inputs, instruction, schema):
                if cancelled(): raise GenerationCancelled()
                if key in checkpoint: return checkpoint[key]
                self.store.progress(job_id, key, label)
                result = generator.generate(role, inputs, RULES + "\n" + instruction, schema)
                if cancelled(): raise GenerationCancelled()
                checkpoint[key] = result
                self.store.progress(job_id, key, label, checkpoint)
                return result

            if job["kind"] == "review":
                report = stage("manual_review", "Revisione dell'intero percorso…",
                    "Sei un revisore didattico indipendente. Esamina il percorso effettivo e distingui errori e raccomandazioni.",
                    snapshot, "Valuta obiettivi, ore, prerequisiti, progressione, copertura dei concetti, teoria e laboratorio. Restituisci osservazioni concrete con posizione e proposta. Non riscrivere il percorso: il docente sceglierà se applicare i suggerimenti attraverso rigenerazione completa.", REVIEW)
                self.store.publish_review(job_id, report)
                return

            context = stage("context", "Interpretazione del brief e dei vincoli…",
                "Sei il progettista che interpreta il contesto della classe.", snapshot,
                "Riordina il brief libero e le sezioni. Deduci materia e traguardi; se mancano scuola, conoscenze o tempi, proponi ipotesi esplicite. Calcola un monte ore annuale realistico: teoria, laboratorio, verifiche, recupero e margine devono sommare esattamente total_hours. Integra eventuali nuove richieste e considera il percorso precedente. Mantieni riferimenti curricolari vuoti se non sono stati forniti documenti.", CONTEXT)
            if (context["total_hours"] <= 0 or not context["goals"] or any(h < 0 for h in context["hours"].values())
                    or not math.isclose(sum(context["hours"].values()), context["total_hours"], abs_tol=0.01)):
                raise GenerationError("La ripartizione iniziale delle ore non è coerente. Riprendi per rielaborare il contesto.")

            structure = stage("uda_author", "Progettazione delle UDA e dei progetti annuali…",
                "Sei il progettista delle UDA. Ragiona sull'intero anno e sulla progressione delle competenze.",
                {"request": snapshot, "context": context},
                "Costruisci le UDA nell'ordine didattico con tutti i metadati e la ripartizione theory/laboratory/assessment. Le somme delle UDA devono corrispondere alle categorie del contesto, escluse recovery e buffer. Collega ogni obiettivo annuale alle UDA. Integra progetti progressivi tra UDA se utili o richiesti. Lascia review_notes vuoto: la revisione avviene dopo.", STRUCTURE)
            reviewed_structure = stage("uda_review", "Revisione delle UDA, delle competenze e del monte ore…",
                "Sei un revisore distinto dall'autore delle UDA. Controlla e correggi l'intera proposta.",
                {"request": snapshot, "context": context, "proposal": structure},
                "Controlla copertura degli obiettivi, prerequisiti, tempi, progressione, laboratorio e tappe dei progetti. Restituisci l'intera struttura corretta, mantenendo i vincoli espliciti; inserisci osservazioni utili in review_notes. Non cambiare il monte ore del contesto.", STRUCTURE)
            lessons = stage("lesson_author", "Costruzione delle lezioni nel percorso annuale…",
                "Sei il progettista delle lezioni. Ogni lezione dipende dalla progressione annuale complessiva.",
                {"request": snapshot, "context": context, "structure": reviewed_structure},
                "Costruisci tutte le lezioni di tutte le UDA, senza contenuti completi. Copia esattamente il context ricevuto. Usa kind theory/laboratory/assessment: la somma delle durate per ciascun kind in ogni UDA deve corrispondere alle ore dichiarate. Collega gli obiettivi dell'UDA e i prerequisiti alle lezioni realmente precedenti anche in altre UDA. Usa lesson IDs univoci in tutto l'anno e obiettivi univoci U1-O1 ecc. Integra i progetti progressivi. Restituisci tutto il percorso.", PLAN)
            plan = stage("lesson_review", "Revisione delle lezioni e della coerenza dell'intero anno…",
                "Sei il revisore finale dell'intero percorso e delle sue lezioni.",
                {"request": snapshot, "context": context, "proposal": lessons},
                "Rivedi e correggi l'intero scheletro: ogni obiettivo deve essere coperto, i prerequisiti devono riferirsi a lezioni precedenti, ore per tipo e UDA devono sommare correttamente. Mantieni il context esattamente uguale a quello fornito. Verifica le richieste del docente, anche quelle atipiche. Restituisci tutti i metadati e tutte le lezioni, con le note finali in review_notes.", PLAN)
            for attempt in range(2):
                errors = plan_errors(plan)
                if plan["context"] != context: errors.append("Il context deve coincidere esattamente con il contesto interpretato e salvato.")
                if not errors: break
                self.store.progress(job_id, "repair", "Riallineamento di ore, riferimenti e obiettivi…")
                plan = generator.generate("Correggi gli errori strutturali riscontrati dal controllo indipendente.",
                    {"request": snapshot, "context": context, "proposal": plan, "errors": errors},
                    RULES + "\nRestituisci l'intero percorso corretto. Copia esattamente il context ricevuto. Non correggere soltanto una parte e non omettere UDA o lezioni.", PLAN)
                checkpoint["lesson_review"] = plan
                self.store.progress(job_id, "repair", "Ricontrollo del percorso completo…", checkpoint)
            errors = plan_errors(plan)
            if plan["context"] != context: errors.append("Il contesto è stato alterato durante la revisione.")
            if errors: raise GenerationError("Il percorso richiede un ulteriore controllo: " + " ".join(errors[:4]))
            if cancelled(): raise GenerationCancelled()
            self.store.publish(job_id, plan)
        except GenerationCancelled:
            self.store.stop(job_id, "interrupted", "Attività interrotta. Puoi riprendere dai risultati salvati.", owned=True)
        except Exception as error:
            if cancelled():
                self.store.stop(job_id, "interrupted", "Attività interrotta. Puoi riprendere dai risultati salvati.", owned=True)
            else:
                message = str(error) if isinstance(error, GenerationError) else "La generazione non è riuscita. I passaggi completati sono conservati e puoi riprendere."
                # Un contesto incoerente deve essere rielaborato alla ripresa.
                if "ripartizione iniziale" in message:
                    checkpoint.pop("context", None)
                    self.store.progress(job_id, "context", message, checkpoint)
                self.store.stop(job_id, "failed", message, owned=True)
        finally:
            try:
                if generator: generator.close()
            finally:
                with self.lock:
                    current = self.workers.get(job_id)
                    if current and current[0] is threading.current_thread(): self.workers.pop(job_id)

    def shutdown(self):
        self.closing.set()
        with self.lock: workers = list(self.workers.items())
        for job_id, (_, event) in workers:
            event.set()
            self.store.stop(job_id, "interrupted", "Attività sospesa alla chiusura. Puoi riprendere dai risultati salvati.", owned=True)
        for _, (thread, _) in workers: thread.join(timeout=0.5)
