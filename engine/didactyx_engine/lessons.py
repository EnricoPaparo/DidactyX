"""Generazione di contenuti completi con memoria effettiva e revisori distinti."""
import threading

from .generation import CodexGenerator, GenerationCancelled, GenerationError
from .planning import PlanningManager
from .lesson_store import LessonStore
from .lesson_schema import CONTENT, OUTLINE, PART, REVIEW, content_errors
from .example_checks import check_examples
from .store import DomainError

from .lesson_prompts import (COMMON_RULES, AUTHOR_RULES, REVIEW_ROLE, REVIEW_INSTRUCTION,
    DISCIPLINE_INSTRUCTION, CONTINUITY_INSTRUCTION, PROMPT_VERSION)

RULES = COMMON_RULES + "\n" + AUTHOR_RULES


class LessonManager(PlanningManager):
    def __init__(self, store, generator_factory=CodexGenerator):
        self.store=LessonStore(store); self.generator_factory=generator_factory
        self.workers={}; self.lock=threading.Lock(); self.closing=threading.Event(); self.store.recover()

    def start(self, params, review=False):
        job=self.store.new_lesson_job(params,review); self._launch(job['id']); return job

    def resume(self, job_id):
        job=self.store.job(job_id,True)
        if job['snapshot'].get('prompt_version', '0.3.1') != PROMPT_VERSION:
            raise DomainError(-32009, 'Le istruzioni didattiche sono cambiate. Avvia una nuova generazione per usare un workflow coerente; i materiali già completati sono conservati.')
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
                rules=COMMON_RULES if job['kind']=='lesson_review' else RULES
                value=generator.generate(role,inputs,rules+'\n'+instruction,schema)
                if cancelled():raise GenerationCancelled()
                checkpoint[key]=value;self.store.progress(job_id,key,label,checkpoint);return value
            if job['kind']=='lesson_review':
                version=self.store.version(snapshot['program_id'],snapshot['review_version_id'])
                context=self.store.context(snapshot,version['lesson_id'],{})
                report=stage('manual_review','Revisione indipendente della lezione…',
                    REVIEW_ROLE,{'context':context,'content':version['data'],'checks':version['checks']},
                    REVIEW_INSTRUCTION,REVIEW)
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
                    ('discipline','Sei un revisore della correttezza disciplinare distinto dagli autori.',DISCIPLINE_INSTRUCTION),
                    ('continuity','Sei il revisore della progressione e della chiarezza didattica.',CONTINUITY_INSTRUCTION)]:
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
