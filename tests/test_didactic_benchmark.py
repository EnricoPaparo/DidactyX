from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('didactic_benchmark',ROOT/'scripts/didactic_benchmark.py')
bench=importlib.util.module_from_spec(spec);spec.loader.exec_module(bench)


class DidacticBenchmarkTests(unittest.TestCase):
    def test_mutations_pass_structure_and_code_without_exposing_oracle(self):
        for case in bench.read(bench.BENCH/'cases.json'):
            with self.subTest(case=case['id']):
                value=bench.case_input(case)
                self.assertEqual(set(value),{'context','content','checks'})
                self.assertNotIn(case['expected'],json.dumps(value,ensure_ascii=False))
                self.assertFalse(any(c['status']=='failed' for c in value['checks']))

    def test_boundary_fault_has_passing_output_but_violates_inclusive_goal(self):
        case=next(c for c in bench.read(bench.BENCH/'cases.json') if c['id']=='H02')
        value=bench.case_input(case)
        block=next(b for s in value['content']['sections'] if s['id']=='S6' for b in s['blocks'] if b['kind']=='code')
        self.assertIn('if spesa < budget:',block['code'])
        exact=next(c for c in block['cases'] if c['stdin']==['3','2','6'])
        self.assertIn('Budget insufficiente',exact['stdout'])
        self.assertTrue(any('uguale' in c for c in value['context']['lesson']['concepts']))

    def test_control_keeps_teacher_request_explicit(self):
        case=next(c for c in bench.read(bench.BENCH/'cases.json') if c['id']=='C04')
        value=bench.case_input(case)
        self.assertFalse(value['content']['self_check'])
        self.assertIn('ometti deliberatamente',value['context']['lesson_brief'])

    def test_cached_result_is_bound_to_input_and_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'report.json';signature={'input_sha256':bench.digest({'text':'original'}),
                'prompt_sha256':bench.digest({'role':'role','instruction':'instruction','schema':bench.REVIEW})}
            bench.write(path,{**signature,'result':{'summary':'stored','findings':[]}})
            with patch.object(bench,'CodexGenerator',side_effect=AssertionError('AI must not run')):
                self.assertEqual(bench.call_cached(path,{'text':'original'},'role','instruction',bench.REVIEW,Path(directory))['result']['summary'],'stored')
                with self.assertRaises(ValueError):bench.call_cached(path,{'text':'changed'},'role','instruction',bench.REVIEW,Path(directory))

    def test_audit_rejects_invented_quotations(self):
        versions=[{'lesson_id':i,'data':{'sections':[{'id':'S1','blocks':[{'text':'Un valore viene associato a un nome.'}]}]}} for i in ['L1','L2','L3']]
        ratings=[{'criterion_id':c,'score':3,'reason':'Reason','evidence':[{'lesson_id':'L1','section_id':'S1','quote':'Un valore viene associato'}],'improvement':''} for c in bench.CRITERIA]
        report={'evaluations':[{'target':i,'ratings':deepcopy(ratings),'findings':[]} for i in ['L1','L2','L3','UDA']],'summary':'Report'}
        bench.check_audit(report,versions)
        report['evaluations'][0]['ratings'][0]['evidence'][0]['quote']='Tutti gli studenti hanno imparato'
        with self.assertRaises(ValueError):bench.check_audit(report,versions)

    def test_aggregation_uses_weaker_judgment_and_does_not_compensate_a_gap(self):
        rubric=bench.read(bench.BENCH/'rubric.json')
        ratings=[{'criterion_id':c,'score':4} for c in bench.CRITERIA]
        strong={'evaluations':[{'target':'L1','ratings':deepcopy(ratings),'findings':[]}]}
        weak=deepcopy(strong);weak['evaluations'][0]['ratings'][3]['score']=2
        result=bench.aggregate_reports([strong,weak],rubric)[0]
        self.assertGreater(result['weighted_minimum'],75)
        self.assertFalse(result['meets_internal_threshold'])
        self.assertEqual(result['minimum_per_criterion']['C4'],2)

if __name__=='__main__':unittest.main()
