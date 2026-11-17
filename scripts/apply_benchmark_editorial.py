"""Applica correzioni editoriali esplicite al campione, conservando le versioni.

Non usa AI e non costituisce una nuova generazione completa del workflow.
Ogni sostituzione deve corrispondere esattamente al testo registrato nella patch.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'engine'))
from didactyx_engine.store import Store
from didactyx_engine.lesson_store import LessonStore
from didactyx_engine.lesson_schema import content_errors
from didactyx_engine.example_checks import check_examples
from didactyx_engine.lesson_prompts import PROMPT_VERSION


def apply(directory, source, patch_path, output):
    read=lambda p:json.loads(p.read_text())
    if (output/'generation.json').exists():raise ValueError('Uscita già completa; non sovrascrivere le evidenze.')
    originals=[read(source/f'lesson-L{i}.json') for i in [1,2,3]]
    patches=read(patch_path);store=LessonStore(Store(directory));mapping={};changes=[]
    for version in originals:
        current=store.head(version['plan_id'],version['lesson_id'])
        if current['id']!=version['id']:raise ValueError('Il campione corrente non coincide con la sorgente registrata.')
    output.mkdir(parents=True,exist_ok=True)
    for version in originals:
        code=version['lesson_id'];data=deepcopy(version['data']);patch=patches[code]
        for item in patch['blocks']:
            block=next(s for s in data['sections'] if s['id']==item['section'])['blocks'][item['index']]
            if block[item['field']]!=item['expected']:raise ValueError('Testo sorgente diverso dalla patch.')
            block[item['field']]=item['text']
        for item in patch['notes']:
            if data['teacher_notes'][item['index']]!=item['expected']:raise ValueError('Nota sorgente diversa dalla patch.')
            data['teacher_notes'][item['index']]=item['text']
        for ref in data['continuity']:ref['version_id']=mapping.get(ref['version_id'],ref['version_id'])
        for index,note in enumerate(data['teacher_notes']):
            for old,new in mapping.items():note=note.replace(old,new)
            data['teacher_notes'][index]=note.replace('versione 2','versione 3')
        job=store.new_lesson_job({'program_id':version['program_id'],'plan_id':version['plan_id'],'lesson_id':code,'brief':version['brief']})
        snapshot=store.job(job['id'],True)['snapshot'];context=store.context(snapshot,code,{})
        errors=content_errors(data,context)
        if errors:raise ValueError(errors)
        checks=check_examples(data)
        if checks!=version['checks']:raise ValueError('La revisione editoriale ha modificato un risultato eseguibile.')
        identifier=store.publish_lesson(job['id'],code,data,context,checks);store.finish(job['id'])
        mapping[version['id']]=identifier;current=store.version(version['program_id'],identifier)
        (output/f'lesson-{code}.json').write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n')
        changes.append({'lesson_id':code,'from_version':version['version'],'to_version':current['version'],'blocks_corrected':len(patch['blocks']),'notes_corrected':len(patch['notes'])})
    for version in originals:
        if store.version(version['program_id'],version['id'])!=version:raise ValueError('Versione precedente alterata.')
        if store.stale_reasons(store.head(version['plan_id'],version['lesson_id'])):raise ValueError('Riferimenti non correnti.')
    (output/'annual-plan.json').write_bytes((source/'annual-plan.json').read_bytes())
    manifest={'method':'Explicit editorial correction, not full workflow regeneration','changes':changes,
        'previous_versions_unchanged':True,'all_lesson_dependencies_current':True,'code_checks_unchanged':True,
        'patches_sha256':hashlib.sha256(patch_path.read_bytes()).hexdigest(),'future_generation_prompt_version':PROMPT_VERSION,
        'future_author_rules_not_tested_by_full_corpus_regeneration':True}
    (output/'generation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for flag in ['data-dir','source','patches','output']:parser.add_argument('--'+flag,type=Path,required=True)
    args=parser.parse_args();print(json.dumps(apply(args.data_dir,args.source,args.patches,args.output),ensure_ascii=False,indent=2))
