"""Versioni dei materiali, contesto riproducibile e dipendenze fra lezioni."""
from contextlib import closing
import json
from pathlib import Path
import uuid
import os

from .planning_store import PlanningStore
from .store import DomainError, now, text
from .lesson_prompts import PROMPT_VERSION


class LessonStore(PlanningStore):
    @staticmethod
    def decode_version(row):
        if row is None: return None
        result = dict(row)
        for key in ('data', 'context', 'checks'): result[key] = json.loads(result.pop(key + '_json'))
        return result

    def version(self, program_id, version_id):
        with closing(self.store.connect()) as c:
            row = c.execute('SELECT * FROM lesson_versions WHERE id=? AND program_id=?', (version_id, program_id)).fetchone()
            if row is None: raise DomainError(-32004, 'La versione della lezione non è stata trovata.')
            return self.decode_version(row)

    def head(self, plan_id, lesson_id):
        with closing(self.store.connect()) as c:
            return self.decode_version(c.execute('SELECT v.* FROM lesson_versions v JOIN lesson_heads h ON h.version_id=v.id WHERE h.plan_id=? AND h.lesson_id=?', (plan_id, lesson_id)).fetchone())

    def locate(self, program_id, plan_id, lesson_id):
        plan = self.get_version(program_id, plan_id)
        for uda in plan['data']['udas']:
            for lesson in uda['lessons']:
                if lesson['id'] == lesson_id: return plan, uda, lesson
        raise DomainError(-32004, 'La lezione non appartiene a questa versione del percorso.')

    def stale_reasons(self, version, visited=None):
        visited=set() if visited is None else visited
        if version['id'] in visited:return []
        visited.add(version['id'])
        reasons = []
        for source in version['context']['source_versions']:
            head = self.head(version['plan_id'], source['lesson_id'])
            if not head or head['id'] != source['version_id']:
                reasons.append('È cambiata una lezione precedente usata per generare questo contenuto.')
                break
            if self.stale_reasons(head,visited):
                reasons.append('Un materiale propedeutico richiede a sua volta un riallineamento.')
                break
        if any(self.head(version['plan_id'], i) for i in version['context']['missing_prerequisites']):
            reasons.append('Sono ora disponibili contenuti propedeutici che prima erano soltanto pianificati.')
        return reasons

    def state(self, program_id, plan_id, lesson_id):
        self.locate(program_id, plan_id, lesson_id)
        head = self.head(plan_id, lesson_id)
        with closing(self.store.connect()) as c:
            versions = [dict(r) for r in c.execute('SELECT id,version,created_at,brief FROM lesson_versions WHERE plan_id=? AND lesson_id=? ORDER BY version DESC', (plan_id, lesson_id))]
            review = c.execute('SELECT * FROM lesson_reviews WHERE version_id=? ORDER BY created_at DESC LIMIT 1', (head['id'] if head else '',)).fetchone()
            review = dict(review) if review else None
            if review: review['data'] = json.loads(review.pop('data_json'))
        planning = super().state(program_id)
        with closing(self.store.connect()) as c:
            draft=c.execute('SELECT value FROM settings WHERE key=?', ('lesson_brief:'+plan_id+':'+lesson_id,)).fetchone()
        return {'current_version': head, 'versions': versions, 'latest_review': review,
                'draft_brief':draft[0] if draft else (head['brief'] if head else ''),
                'latest_job': planning['latest_job'], 'stale_reasons': self.stale_reasons(head) if head else [],
                'historical_plan': planning['current_plan'] is None or planning['current_plan']['id'] != plan_id,
                'brief_pending': planning['brief_pending']}

    def save_brief(self, params):
        self.locate(params.get('program_id'),params.get('plan_id'),params.get('lesson_id'))
        brief=text(params.get('brief'),'brief della lezione')
        with closing(self.store.connect()) as c,c:
            c.execute('INSERT INTO settings VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
                      ('lesson_brief:'+params['plan_id']+':'+params['lesson_id'],brief))
        return {'saved':True}

    def new_lesson_job(self, params, review=False):
        program_id, plan_id = params.get('program_id'), params.get('plan_id')
        requested = params.get('lesson_ids') or [params.get('lesson_id')]
        if not isinstance(requested, list) or not requested or any(not isinstance(i, str) for i in requested):
            raise DomainError(-32602, 'Scegli almeno una lezione.')
        plan = self.get_version(program_id, plan_id)
        active = super().state(program_id)['current_plan']
        if not review and (not active or active['id'] != plan_id):
            raise DomainError(-32009, 'Per generare contenuti seleziona la versione corrente del percorso.')
        ordered = [l['id'] for u in plan['data']['udas'] for l in u['lessons']]
        if len(set(requested)) != len(requested) or set(requested) - set(ordered):
            raise DomainError(-32602, 'La selezione contiene lezioni non valide.')
        if review and len(requested) != 1: raise DomainError(-32602, 'Revisiona una lezione alla volta.')
        targets = [i for i in ordered if i in requested]
        heads = [self.head(plan_id, i) for i in ordered]
        references = [{'lesson_id': v['lesson_id'], 'version_id': v['id']} for v in heads if v]
        selected = self.head(plan_id, targets[0]) if review else None
        if review and not selected: raise DomainError(-32602, 'Genera prima il contenuto della lezione.')
        snapshot = {'program_id': program_id, 'plan': plan, 'lesson_ids': targets,
                    'brief': text(params.get('brief', ''), 'brief della lezione'), 'source_versions': references,
                    'review_version_id': selected['id'] if selected else None, 'prompt_version': PROMPT_VERSION}
        return self.insert_job(program_id, snapshot, 'lesson_review' if review else 'lesson_generate')

    def ensure_context_current(self, snapshot):
        active = super().state(snapshot['program_id'])['current_plan']
        if not active or active['id'] != snapshot['plan']['id']:
            raise DomainError(-32009, 'Il percorso è cambiato. Avvia una nuova generazione dal contesto corrente.')
        for ref in snapshot['source_versions']:
            head = self.head(active['id'], ref['lesson_id'])
            if not head or head['id'] != ref['version_id']:
                raise DomainError(-32009, 'I materiali di riferimento sono cambiati. Avvia una nuova generazione.')

    def context(self, snapshot, lesson_id, published):
        plan, uda, lesson = self.locate(snapshot['program_id'], snapshot['plan']['id'], lesson_id)
        ordered = [l['id'] for u in plan['data']['udas'] for l in u['lessons']]
        preceding = set(ordered[:ordered.index(lesson_id)])
        refs = {r['lesson_id']: r['version_id'] for r in snapshot['source_versions']}
        refs.update(published)
        previous = [self.version(snapshot['program_id'], refs[i]) for i in ordered if i in preceding and i in refs]
        # Full saved bodies, not only summaries. Avoid recursively copying other contexts.
        materials = [{k: v[k] for k in ('id', 'lesson_id', 'version', 'data')} for v in previous]
        sources = []
        if 'python' in json.dumps(plan['data'], ensure_ascii=False).lower():
            sources = json.loads((Path(__file__).parent / 'assets/references/python-basics.json').read_text())
        existing = self.head(plan['id'], lesson_id)
        return {'plan_id': plan['id'], 'class_brief': plan['brief'], 'annual_context': plan['data']['context'],
                'annual_structure': plan['data'], 'uda': {k:v for k,v in uda.items() if k != 'lessons'},
                'lesson': lesson, 'lesson_brief': snapshot['brief'], 'previous_materials': materials,
                'missing_prerequisites': [i for i in lesson['prerequisite_lesson_ids'] if i not in refs],
                'sources': sources, 'previous_content': existing['data'] if existing else None,
                'learning_status': 'I materiali sono generati: non si presume che siano già stati spiegati o appresi.'}

    def publish_lesson(self, job_id, lesson_id, data, context, checks):
        with closing(self.store.connect()) as c, c:
            c.execute('BEGIN IMMEDIATE')
            job = self.decode_job(c.execute('SELECT * FROM planning_jobs WHERE id=?', (job_id,)).fetchone(), True)
            if job['status'] != 'running' or job['owner_pid'] != os.getpid(): return None
            plan_id = job['snapshot']['plan']['id']
            active = c.execute('SELECT plan_id FROM plan_heads WHERE program_id=?', (job['program_id'],)).fetchone()
            if not active or active[0] != plan_id: raise DomainError(-32009, 'Il percorso di riferimento è cambiato.')
            number = c.execute('SELECT COALESCE(MAX(version),0)+1 FROM lesson_versions WHERE plan_id=? AND lesson_id=?', (plan_id, lesson_id)).fetchone()[0]
            identifier = str(uuid.uuid4())
            saved_context = {'plan_id': plan_id, 'class_brief': context['class_brief'],
                'objectives':[o for o in context['uda']['objectives'] if o['id'] in context['lesson']['objective_ids']],
                'source_versions': [{'lesson_id':v['lesson_id'],'version_id':v['id']} for v in context['previous_materials']],
                'missing_prerequisites': context['missing_prerequisites'], 'sources': context['sources']}
            c.execute('INSERT INTO lesson_versions VALUES (?,?,?,?,?,?,?,?,?,?)',
                (identifier, job['program_id'], plan_id, lesson_id, number, now(), job['snapshot']['brief'],
                 json.dumps(data,ensure_ascii=False), json.dumps(saved_context,ensure_ascii=False), json.dumps(checks,ensure_ascii=False)))
            c.execute('INSERT INTO lesson_heads VALUES (?,?,?) ON CONFLICT(plan_id,lesson_id) DO UPDATE SET version_id=excluded.version_id', (plan_id,lesson_id,identifier))
            # Publish the version and its resume marker in the same transaction.
            checkpoint = job['checkpoint']; checkpoint.setdefault('published', {})[lesson_id] = identifier
            c.execute('UPDATE planning_jobs SET checkpoint_json=?,updated_at=? WHERE id=?', (json.dumps(checkpoint,ensure_ascii=False),now(),job_id))
            return identifier

    def finish(self, job_id, report=None):
        with closing(self.store.connect()) as c, c:
            c.execute('BEGIN IMMEDIATE')
            job = self.decode_job(c.execute('SELECT * FROM planning_jobs WHERE id=?', (job_id,)).fetchone(), True)
            if job['status'] != 'running' or job['owner_pid'] != os.getpid(): return
            if report is not None:
                c.execute('INSERT INTO lesson_reviews VALUES (?,?,?,?)', (str(uuid.uuid4()),job['snapshot']['review_version_id'],now(),json.dumps(report,ensure_ascii=False)))
            message = 'Revisione della lezione completata. Le proposte sono consultabili.' if report is not None else 'Contenuti completati e revisionati.'
            c.execute("UPDATE planning_jobs SET status='completed',phase='completed',message=?,updated_at=? WHERE id=?", (message,now(),job_id))
