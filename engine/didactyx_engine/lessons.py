"""Generazione di contenuti completi con memoria effettiva e revisori distinti."""
import threading

from .generation import CodexGenerator, GenerationCancelled, GenerationError
from .planning import PlanningManager
from .lesson_store import LessonStore
from .lesson_schema import CONTENT, OUTLINE, PART, REVIEW, content_errors
from .example_checks import check_examples
from .store import DomainError

RULES = '''Nel corpo destinato allo studente non nominare i campi del nostro formato (self_check, objective_ids, source_ids, stdin, stdout): usa titoli e spiegazioni didattiche naturali. I casi sono presentati come dati inseriti ed esecuzioni di esempio; non spiegare l'infrastruttura dei test. Scrivi in italiano materiale didattico completo e autosufficiente per lo studente, con spiegazioni distese e passaggi motivati, non una scaletta o un riassunto di ciò che il docente dovrebbe spiegare. Adatta tono e profondità al brief della classe e rispetta il brief specifico, anche se atipico; segnala nelle teacher_notes eventuali raccomandazioni senza sostituire le scelte esplicite. Non imporre un limite di parole. Le conoscenze iniziali e gli obiettivi del percorso guidano lo sviluppo. I contenuti di previous_materials sono le versioni reali consultabili delle lezioni precedenti: riprendi esempi, nomi, valori, notazione e procedure con precisione. Sono materiali generati, non prova di apprendimento della classe. Non inventare richiami a materiali assenti. Compila continuity solo con version_id e section_id reali effettivamente ripresi. Per ogni missing_prerequisites spiega i concetti necessari nel testo della lezione e rendi esplicita la scelta in prerequisite_support: non limitarti a una nota al docente. Le fonti utilizzabili sono solo quelle fornite in sources; source_ids deve contenere i riferimenti effettivamente utilizzati. Non inventare fonti consultate. Le note per il docente sono separate dal corpo destinato allo studente. Non usare HTML o Markdown nei blocchi: i renderer gestiscono la tipografia. Le formule sono espressioni Unicode lineari spiegate nel testo, senza comandi TeX. Nei blocchi code separa codice da spiegazione. Per esempi Python funzionanti usa execution=check e casi con stdin e stdout esatto, compresi i prompt e le nuove righe; includi casi diversi per i rami condizionali pertinenti. Codice deliberatamente errato o non autonomo è illustration, con spiegazione dell'errore o del contesto. Non anticipare concetti oltre il perimetro senza introdurli adeguatamente. Negli esempi svolti spiega perché si compie ogni passaggio. Self_check contiene domande e risposte ragionate per controllare la comprensione, non una verifica formale. Glossario e sintesi devono corrispondere al contenuto effettivo.'''


class LessonManager(PlanningManager):
    def __init__(self, store, generator_factory=CodexGenerator):
        self.store=LessonStore(store); self.generator_factory=generator_factory
        self.workers={}; self.lock=threading.Lock(); self.closing=threading.Event(); self.store.recover()

    def start(self, params, review=False):
        job=self.store.new_lesson_job(params,review); self._launch(job['id']); return job

    def resume(self, job_id):
        job=self.store.job(job_id,True)
        if job['kind']=='lesson_generate':
            snapshot=dict(job['snapshot'])
            published=job['checkpoint'].get('published',{})
            snapshot['source_versions']=[r for r in snapshot['source_versions'] if r['lesson_id'] not in published]
            snapshot['source_versions'] += [{'lesson_id':i,'version_id':v} for i,v in published.items()]
            self.store.ensure_context_current(snapshot)
        return super().resume(job_id)

    def _run(self, job_id, stopped):
        generator=None
        def cancelled():return stopped.is_set() or self.closing.is_set() or not self.store.owned_running(job_id)
        try:
            job=self.store.job(job_id,True); snapshot=job['snapshot']; checkpoint=job['checkpoint']
            generator=self.generator_factory(self.store.store.directory,cancelled)
            def stage(key,label,role,inputs,instruction,schema):
                if cancelled():raise GenerationCancelled()
                if key in checkpoint:return checkpoint[key]
                self.store.progress(job_id,key,label)
                value=generator.generate(role,inputs,RULES+'\n'+instruction,schema)
                if cancelled():raise GenerationCancelled()
                checkpoint[key]=value;self.store.progress(job_id,key,label,checkpoint);return value
            if job['kind']=='lesson_review':
                version=self.store.version(snapshot['program_id'],snapshot['review_version_id'])
                context=self.store.context(snapshot,version['lesson_id'],{})
                report=stage('manual_review','Revisione indipendente della lezione…',
                    'Sei un revisore disciplinare e didattico indipendente.',{'context':context,'content':version['data'],'checks':version['checks']},
                    'Esamina correttezza, completezza delle spiegazioni, esempi, accessibilità, continuità reale e fonti. Distingui errori da scelte didattiche discutibili ma intenzionali. Proponi interventi concreti senza riscrivere il contenuto: il docente sceglierà se rigenerarlo.',REVIEW)
                self.store.finish(job_id,report);return
            published=checkpoint.setdefault('published',{})
            check_snapshot=dict(snapshot);check_snapshot['source_versions']=[r for r in snapshot['source_versions'] if r['lesson_id'] not in published]
            check_snapshot['source_versions'] += [{'lesson_id':i,'version_id':v} for i,v in published.items()]
            self.store.ensure_context_current(check_snapshot)
            for index,lesson_id in enumerate(snapshot['lesson_ids'],1):
                if lesson_id in published:continue
                context=self.store.context(snapshot,lesson_id,published)
                prefix=lesson_id+':';label=f'{lesson_id} · {context["lesson"]["title"]} · '
                outline=stage(prefix+'outline',label+'progettazione della spiegazione…','Sei il progettista della lezione completa.',context,
                    'Progetta una progressione esplicativa concreta per tutti gli obiettivi. Le sections contengono lo sviluppo della spiegazione: sintesi, glossario e domande di comprensione hanno già campi dedicati e non vanno duplicati come sezioni. author_groups è una partizione degli id delle sezioni: usa uno o più autori secondo la complessità reale, senza frammentare inutilmente il testo. Ogni sezione appartiene esattamente a un gruppo. Non limitare la profondità per far stare il testo in una scheda.',OUTLINE)
                ids=[s['id'] for s in outline['sections']];assigned=[i for group in outline['author_groups'] for i in group]
                if not ids or len(set(ids))!=len(ids) or sorted(ids)!=sorted(assigned) or any(not g for g in outline['author_groups']):
                    checkpoint.pop(prefix+'outline',None);self.store.progress(job_id,prefix+'outline','La progettazione richiede un nuovo passaggio.',checkpoint)
                    raise GenerationError('La suddivisione della lezione non è coerente. Riprendi per rielaborarla.')
                inputs={'context':context,'outline':outline}
                if len(outline['author_groups'])==1:
                    content=stage(prefix+'author',label+'scrittura dei contenuti…','Sei l’autore della lezione completa.',inputs,
                        'Sviluppa tutta la lezione con spiegazioni effettive, esempi risolti, nessi logici, sintesi e domande ragionate. Mantieni gli id delle sezioni progettate. Copri esattamente gli obiettivi della lezione, senza produrre solo indicazioni metodologiche.',CONTENT)
                else:
                    parts=[]
                    for n,group in enumerate(outline['author_groups']):
                        parts.append(stage(prefix+f'author_{n}',label+f'scrittura del contributo {n+1}…','Sei un autore specializzato, consapevole del progetto complessivo.',
                            {**inputs,'assigned_section_ids':group},'Sviluppa integralmente solo le sezioni assegnate, mantenendo gli id e rispettando lo sviluppo complessivo. Non riassumere per risparmiare spazio.',PART))
                    content=stage(prefix+'editor',label+'ricomposizione della lezione…','Sei il curatore editoriale didattico.',
                        {**inputs,'contributions':parts},'Ricomponi tutti i contributi, elimina ripetizioni e colma lacune, preservando profondità e passaggi. Produci la lezione completa con introduzione, sezioni, sintesi, glossario, richiami verificabili e fonti.',CONTENT)
                for key,role,instruction in [
                    ('discipline','Sei un revisore della correttezza disciplinare distinto dagli autori.','Correggi concetti, definizioni, procedure, codice e output. Ricontrolla casi limite e soluzioni. Restituisci tutto il contenuto corretto, preservando spiegazioni e richieste del docente.'),
                    ('continuity','Sei il revisore della progressione e della chiarezza didattica.','Confronta il corpo effettivo con le lezioni precedenti fornite, verifica i richiami e la continuità di esempi e notazione. Controlla prerequisiti mancanti, salti logici, comprensibilità e copertura degli obiettivi. Elimina duplicazioni, in particolare sintesi, glossario e domande già presenti nei campi dedicati: puoi accorpare le sezioni conclusive ridondanti preservando il contenuto utile. Elimina dal corpo i nomi tecnici del formato e le spiegazioni dell’infrastruttura dei test. Correggi e restituisci tutta la lezione. Mantieni gli id delle sezioni conservate; limita teacher_notes a osservazioni utili al docente, senza autocertificazioni.')]:
                    content=stage(prefix+key,label+('revisione disciplinare…' if key=='discipline' else 'revisione della continuità…'),role,
                                  {**inputs,'proposal':content},instruction,CONTENT)
                for attempt in range(3):
                    errors=content_errors(content,context); checks=check_examples(content) if not errors else []
                    errors += [f"Esempio {c['section_id']}, blocco {c['block_index']}: {c['message']}" for c in checks if c['status']=='failed']
                    if not errors:break
                    if attempt==2:raise GenerationError('La lezione richiede ulteriori correzioni: '+' '.join(errors[:3]))
                    content=generator.generate('Correggi le incongruenze rilevate dai controlli indipendenti.',
                        {'context':context,'proposal':content,'errors':errors},RULES+'\nRestituisci tutta la lezione corretta, senza omettere spiegazioni o esempi.',CONTENT)
                    checkpoint[prefix+'continuity']=content;self.store.progress(job_id,prefix+'repair',label+'ricontrollo degli esempi e dei riferimenti…',checkpoint)
                if cancelled():raise GenerationCancelled()
                identifier=self.store.publish_lesson(job_id,lesson_id,content,context,checks)
                if identifier:published[lesson_id]=identifier
            if cancelled():raise GenerationCancelled()
            self.store.finish(job_id)
        except GenerationCancelled:
            self.store.stop(job_id,'interrupted','Attività sospesa. I contenuti completati sono conservati.',owned=True)
        except Exception as error:
            message=str(error) if isinstance(error,(GenerationError,DomainError)) else 'La lezione non è stata completata. Puoi riprendere dai passaggi salvati.'
            self.store.stop(job_id,'interrupted' if cancelled() else 'failed',message,owned=True)
        finally:
            try:
                if generator:generator.close()
            finally:
                with self.lock:
                    current=self.workers.get(job_id)
                    if current and current[0] is threading.current_thread():self.workers.pop(job_id)
