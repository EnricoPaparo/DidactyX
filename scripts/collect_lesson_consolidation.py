"""Ricontrolla il consolidamento della UDA senza nuove chiamate AI."""
import argparse
import hashlib
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'engine'),str(ROOT/'scripts')]
from didactic_benchmark import read,write,digest,check_audit,normalize_audit,aggregate_reports,BENCH
from didactyx_engine.lesson_schema import content_errors
from didactyx_engine.example_checks import check_examples
from didactyx_engine.store import Store
from didactyx_engine.lesson_store import LessonStore


def acceptance_checks(path,versions):
    checks=read(path)['checks']
    expected={'transcripts','individual_instructions','time_fallback'}
    if {c['id'] for c in checks}!=expected or len(checks)!=3:raise ValueError('Controlli del punto 1 incompleti.')
    by_id={v['lesson_id']:v['data'] for v in versions}
    def strings(value):
        if isinstance(value,str):yield value
        elif isinstance(value,list):
            for item in value:yield from strings(item)
        elif isinstance(value,dict):
            for item in value.values():yield from strings(item)
    normalize=lambda text:' '.join(text.split())
    for check in checks:
        if type(check['passed']) is not bool or not check['evidence']:raise ValueError('Esito non risolto o privo di riscontri.')
        cited={ref['lesson_id'] for ref in check['evidence']}
        if (check['id']=='transcripts' and cited!=set(by_id)) or (check['id']!='transcripts' and 'L3' not in cited):
            raise ValueError('Riscontri non sufficienti per le lezioni interessate.')
        for ref in check['evidence']:
            data=by_id[ref['lesson_id']]
            source=next((s for s in data['sections'] if s['id']==ref['section_id']),data.get(ref['section_id']))
            if source is None or not ref['quote'].strip() or not any(normalize(ref['quote']) in normalize(s) for s in strings(source)):
                raise ValueError('Riscontro del punto 1 non verificabile: '+str(ref))
    return checks


def collect(evidence,directory,previous):
    freeze=read(evidence/'prompt-freeze.json')
    for name,expected in freeze['files_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:raise ValueError('Contratto congelato modificato: '+name)
    folder=evidence/'generated';annual=read(folder/'annual-plan.json');versions=[read(folder/f'lesson-L{i}.json') for i in [1,2,3]]
    original_annual=read(previous/'baseline/annual-plan.json')
    if annual['data']!=original_annual['data'] or annual['brief']!=original_annual['brief']:
        raise ValueError('Il consolidamento ha cambiato il percorso annuale o il brief applicato.')
    reports=[]
    for judge in ['discipline','pedagogy']:
        audit=read(evidence/'audit'/f'{judge}.json')
        for phase in ['audit-baseline-rendered','audit-tuned','audit-edited']:
            if audit['prompt_sha256']!=read(previous/phase/f'{judge}.json')['prompt_sha256']:
                raise ValueError('Istruzioni dei valutatori non confrontabili.')
        check_audit(audit['result'],versions,annual);reports.append(normalize_audit(audit['result'],annual))
    target=read(directory/'benchmark-target.json');store=LessonStore(Store(directory));job=store.job(target['generation_job_id'],True)
    if job['status']!='completed' or job['snapshot']['prompt_version']!=freeze['prompt_version']:raise ValueError('Workflow incompleto o contratto diverso.')
    ordered=[l for u in annual['data']['udas'] for l in u['lessons']];details=[]
    for index,version in enumerate(versions):
        code=version['lesson_id'];context={'lesson':next(l for l in ordered if l['id']==code),'sources':version['context']['sources'],
            'previous_materials':versions[:index],'missing_prerequisites':[]}
        errors=content_errors(version['data'],context)
        if errors:raise ValueError(errors)
        expected={v['lesson_id']:v['id'] for v in versions[:index]}
        actual={v['lesson_id']:v['version_id'] for v in version['context']['source_versions']}
        if actual!=expected or store.stale_reasons(version):raise ValueError('Dipendenze non correnti.')
        if version['data']!=job['checkpoint'][code+':continuity']:raise ValueError('Materiale modificato dopo l’ultimo passaggio del workflow.')
        if store.version(version['program_id'],version['id'])!=version:raise ValueError('Versione salvata diversa dalle evidenze.')
        checks=check_examples(version['data'])
        if checks!=version['checks'] or any(c['status']=='failed' for c in checks):raise ValueError('Controlli del codice non riprodotti.')
        details.append({'lesson_id':code,'version':version['version'],'sections':len(version['data']['sections']),
            'passed_cases':sum(c['status']=='passed' for c in checks),'not_run_blocks':sum(c['status']=='not_run' for c in checks),
            'continuity_refs':len(version['data']['continuity']),
            'workflow_stages':[key for key in job['checkpoint'] if key.startswith(code+':')],
            'workflow_output_sha256':{key:digest(value) for key,value in job['checkpoint'].items() if key.startswith(code+':')},
            'published_data_sha256':digest(version['data']),
            'author_groups':len(job['checkpoint'][code+':outline']['author_groups']),
            'published_content_equals_final_workflow_output':True})
    acceptance=acceptance_checks(evidence/'acceptance.json',versions)
    ratings=aggregate_reports(reports,read(BENCH/'rubric.json'))
    result={'prompt_version':freeze['prompt_version'],'frozen_contract_verified':True,'judge_prompts_match_previous_benchmark':True,
        'no_post_generation_editorial_patch':True,'all_current_dependencies_valid':True,'annual_structure_and_class_brief_unchanged':True,
        'ratings':ratings,'lessons':details,'point_1_acceptance':acceptance,
        'previous_ratings':{phase:value['ratings'] for phase,value in read(previous/'results.json')['materials'].items()},
        'point_1_passed':all(c['passed'] for c in acceptance) and all(r['meets_internal_threshold'] for r in ratings)}
    write(evidence/'results.json',result);return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',type=Path,required=True);parser.add_argument('--data-dir',type=Path,required=True)
    parser.add_argument('--previous',type=Path,default=ROOT/'docs/evidence/didactic-benchmarks/2026-11-17')
    args=parser.parse_args();result=collect(args.evidence,args.data_dir,args.previous)
    print([(r['target'],r['weighted_minimum'],r['meets_internal_threshold']) for r in result['ratings']])
