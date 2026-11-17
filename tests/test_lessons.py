from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'engine'))
from didactyx_engine.store import Store,DomainError
from didactyx_engine.planning_store import PlanningStore
from didactyx_engine.lesson_store import LessonStore
from didactyx_engine.lessons import LessonManager
from didactyx_engine.lesson_schema import CONTENT,PART,OUTLINE,REVIEW,content_errors
from didactyx_engine.example_checks import check_examples
from test_planning import fixture,wait_job


def content(context):
    lesson=context['lesson'];prior=context['previous_materials']
    return {'title':lesson['title'],'lead':'Una spiegazione completa e concreta.','objective_ids':lesson['objective_ids'],
        'sections':[{'id':'s1','title':'Sviluppo','objective_ids':lesson['objective_ids'],
                     'blocks':[{'kind':'paragraph','text':'Un valore viene associato a un nome attraverso un’assegnazione.'},
                               {'kind':'code','language':'python','code':'print(2 + 3)','execution':'check','cases':[{'stdin':[],'stdout':'5\n'}],'explanation':'I due valori vengono sommati.'}]}],
        'summary':['Un nome permette di riutilizzare un valore.'],'self_check':[{'question':'Quanto vale la somma?','answer':'5, perché 2 + 3 = 5.'}],
        'terms':[{'term':'Valore','definition':'Un dato utilizzato dal programma.'}],
        'continuity':[{'version_id':v['id'],'section_id':'s1','description':'Ripresa dell’assegnazione realmente spiegata.'} for v in prior],
        'prerequisite_support':[{'lesson_id':i,'explanation':'Il prerequisito viene introdotto nella spiegazione.'} for i in context['missing_prerequisites']],
        'source_ids':[],'teacher_notes':[]}


class Factory:
    def __init__(self,multiple=False):self.contexts=[];self.multiple=multiple;self.fail_at=None;self.calls=0
    def __call__(self,directory,cancelled):
        factory=self
        class Generator:
            def generate(self,role,inputs,instruction,schema):
                factory.calls+=1
                if factory.fail_at==factory.calls:
                    from didactyx_engine.generation import GenerationError
                    factory.fail_at=None;raise GenerationError('Rete interrotta nella prova')
                if schema==OUTLINE:
                    factory.contexts.append(deepcopy(inputs));ids=['s1','s2'] if factory.multiple else ['s1']
                    return {'approach':'Spiegazione progressiva','sections':[{'id':i,'title':'Sviluppo','objective_ids':inputs['lesson']['objective_ids'],'purpose':'Spiegare'} for i in ids],
                            'author_groups':[[i] for i in ids],'notes':[]}
                ctx=inputs['context']
                if schema==PART:
                    v=content(ctx);return {'sections':[{**v['sections'][0],'id':i} for i in inputs['assigned_section_ids']]}
                if schema==REVIEW:
                    factory.review_input=deepcopy(inputs)
                    return {'summary':'Revisione completata','findings':[]}
                if 'proposal' in inputs:return deepcopy(inputs['proposal'])
                v=content(ctx)
                if 'contributions' in inputs:v['sections']=[s for p in inputs['contributions'] for s in p['sections']]
                return v
            def close(self):pass
        return Generator()


class LessonTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.store=Store(self.temp.name)
        self.program=self.store.create({'title':'Pilota fittizio'})
        planning=PlanningStore(self.store);job=planning.new_job(self.program['id']);self.plan_id=planning.publish(job['id'],fixture())
        self.factory=Factory();self.manager=LessonManager(self.store,self.factory)
    def tearDown(self):self.manager.shutdown();self.temp.cleanup()
    def generate(self,ids):
        job=self.manager.start({'program_id':self.program['id'],'plan_id':self.plan_id,'lesson_ids':ids})
        self.assertEqual(wait_job(self.manager,job['id'])['status'],'completed');return job
    def test_batch_reads_actual_previous_body_and_retains_versions(self):
        self.generate(['L2','L1'])
        contexts=self.factory.contexts;self.assertEqual([c['lesson']['id'] for c in contexts],['L1','L2'])
        first=self.manager.store.head(self.plan_id,'L1');second=self.manager.store.head(self.plan_id,'L2')
        self.assertEqual(contexts[1]['previous_materials'][0]['data'],first['data'])
        self.assertEqual(second['context']['source_versions'][0]['version_id'],first['id'])
        self.assertTrue(all(c['status']=='passed' for c in second['checks']))
        self.generate(['L1'])
        self.assertEqual(self.manager.store.version(self.program['id'],first['id']),first)
        self.assertTrue(self.manager.store.stale_reasons(second))
    def test_out_of_sequence_support_and_later_alignment(self):
        self.generate(['L2']);second=self.manager.store.head(self.plan_id,'L2')
        self.assertEqual(second['context']['missing_prerequisites'],['L1'])
        self.assertEqual(second['data']['continuity'],[])
        self.generate(['L1']);self.assertTrue(self.manager.store.stale_reasons(second))
    def test_alignment_propagates_through_unchanged_intermediate_content(self):
        self.generate(['L2']);self.generate(['L3']);third=self.manager.store.head(self.plan_id,'L3')
        self.assertFalse(self.manager.store.stale_reasons(third))
        self.generate(['L1']);self.assertTrue(self.manager.store.stale_reasons(third))
    def test_upgrade_from_v2_preserves_annual_plan(self):
        from contextlib import closing
        before=PlanningStore(self.store).get_version(self.program['id'],self.plan_id)
        with closing(self.store.connect()) as c,c:
            for table in ['lesson_reviews','lesson_heads','lesson_versions']:c.execute('DROP TABLE '+table)
            c.execute('PRAGMA user_version=2')
        upgraded=Store(self.temp.name)
        self.assertEqual(PlanningStore(upgraded).get_version(self.program['id'],self.plan_id),before)
        self.assertIsNone(LessonStore(upgraded).state(self.program['id'],self.plan_id,'L1')['current_version'])
    def test_optional_brief_persists_without_generation(self):
        self.manager.store.save_brief({'program_id':self.program['id'],'plan_id':self.plan_id,'lesson_id':'L1','brief':'Usa un esempio concreto.'})
        reopened=LessonStore(Store(self.temp.name))
        self.assertEqual(reopened.state(self.program['id'],self.plan_id,'L1')['draft_brief'],'Usa un esempio concreto.')
        self.assertEqual(self.factory.calls,0)
    def test_multiple_authors_are_recomposed_before_review(self):
        self.factory.multiple=True;self.generate(['L1'])
        self.assertEqual([s['id'] for s in self.manager.store.head(self.plan_id,'L1')['data']['sections']],['s1','s2'])
    def test_manual_review_keeps_content_immutable(self):
        self.generate(['L1']);before=self.manager.store.head(self.plan_id,'L1')
        job=self.manager.start({'program_id':self.program['id'],'plan_id':self.plan_id,'lesson_id':'L1'},True)
        self.assertEqual(wait_job(self.manager,job['id'])['status'],'completed')
        self.assertEqual(before,self.manager.store.head(self.plan_id,'L1'))
        self.assertIsNotNone(self.manager.store.state(self.program['id'],self.plan_id,'L1')['latest_review'])
        from didactyx_engine.lesson_render import visible_examples
        self.assertEqual(self.factory.review_input['visible_examples'],visible_examples(before['data'],before['checks']))
    def test_resume_does_not_publish_first_lesson_twice(self):
        self.factory.fail_at=6
        job=self.manager.start({'program_id':self.program['id'],'plan_id':self.plan_id,'lesson_ids':['L1','L2']})
        self.assertEqual(wait_job(self.manager,job['id'])['status'],'failed')
        first=self.manager.store.head(self.plan_id,'L1');self.assertIsNotNone(first)
        time.sleep(.03);self.manager.resume(job['id'])
        self.assertEqual(wait_job(self.manager,job['id'])['status'],'completed')
        self.assertEqual(self.manager.store.head(self.plan_id,'L1')['id'],first['id'])
    def test_resume_refuses_changed_plan(self):
        self.factory.fail_at=2
        job=self.manager.start({'program_id':self.program['id'],'plan_id':self.plan_id,'lesson_ids':['L1']})
        self.assertEqual(wait_job(self.manager,job['id'])['status'],'failed')
        p=PlanningStore(self.store);j=p.new_job(self.program['id']);p.publish(j['id'],fixture());time.sleep(.03)
        with self.assertRaises(DomainError):self.manager.resume(job['id'])
    def test_resume_refuses_a_different_prompt_contract(self):
        self.factory.fail_at=2
        job=self.manager.start({'program_id':self.program['id'],'plan_id':self.plan_id,'lesson_ids':['L1']})
        self.assertEqual(wait_job(self.manager,job['id'])['status'],'failed')
        time.sleep(.03)
        with patch('didactyx_engine.lessons.PROMPT_VERSION','different-contract'):
            with self.assertRaisesRegex(DomainError,'istruzioni didattiche sono cambiate'):
                self.manager.resume(job['id'])
        self.assertIsNone(self.manager.store.head(self.plan_id,'L1'))
    def test_imaginary_reference_is_rejected(self):
        self.generate(['L1']);ctx=self.factory.contexts[0];v=content(ctx)
        v['continuity']=[{'version_id':'inventato','section_id':'s1','description':'Richiamo inesistente'}]
        self.assertTrue(any('inesistente' in e for e in content_errors(v,ctx)))
    def test_wrong_output_and_unsafe_code_are_not_marked_passed(self):
        ctx={'lesson':{'title':'Esempio','objective_ids':['O1']},'previous_materials':[],'missing_prerequisites':[]}
        v=content(ctx);v['sections'][0]['blocks'][1]['cases'][0]['stdout']='6\n'
        self.assertEqual(check_examples(v)[0]['status'],'failed')
        v['sections'][0]['blocks'][1]['code']='import os\nprint(os.environ)'
        self.assertNotEqual(check_examples(v)[0]['status'],'passed')
    def test_interactive_transcript_preserves_input_echo_without_changing_stdout_check(self):
        value={'sections':[{'id':'s1','blocks':[{'kind':'code','language':'python','execution':'check',
            'code':'n = int(input("Numero: "))\nprint(n + 1)',
            'cases':[{'stdin':['4'],'stdout':'Numero: 5\n'}]}]}]}
        check=check_examples(value)[0]
        self.assertEqual(check['status'],'passed')
        self.assertEqual(check['transcript'],'Numero: 4\n5\n')
    def test_html_escapes_content_and_has_no_remote_dependencies(self):
        from didactyx_engine.lesson_render import render_html
        self.generate(['L1']);v=self.manager.store.head(self.plan_id,'L1');v['data']['lead']='<script>alert(1)</script>'
        html=render_html(v);self.assertIn('&lt;script&gt;',html);self.assertNotIn('<script>',html);self.assertNotIn('<link',html)

if __name__=='__main__':unittest.main()
