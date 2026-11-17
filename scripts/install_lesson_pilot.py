"""Installa un pilota già generato in un archivio locale, senza chiamate AI.

Usare con l'app chiusa. Le versioni sorgente restano immutate; i riferimenti
alle versioni vengono ricondotti ai nuovi identificativi nell'archivio di arrivo.
"""
import argparse
from contextlib import closing
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'engine'))
from didactyx_engine.store import Store
from didactyx_engine.planning_store import PlanningStore
from didactyx_engine.lesson_store import LessonStore
from didactyx_engine.lesson_schema import content_errors

DEFAULT_TITLE='Python · due lezioni collegate · pilota'


def _prepare(data_directory,annual,versions,title=DEFAULT_TITLE):
    store=Store(data_directory);plans=PlanningStore(store);lessons=LessonStore(store)
    # An explicit example title makes repeated installation recognizable.
    if any(p['title']==title for p in store.list_programs()):
        raise ValueError('Il pilota è già presente: nessun programma è stato sovrascritto.')
    program=store.create({'title':title,'class_label':'2ª superiore · classe fittizia',
        'description':f'Esempio inventato su richiesta: variabili, input, conversioni e if/else. {len(versions)} lezioni complete con esempi, richiami e PDF.',
        'brief':annual['brief']})
    job=plans.new_job(program['id']);plan_id=plans.publish(job['id'],annual['data'])
    mapping={};installed=[]
    for source in versions:
        job=lessons.new_lesson_job({'program_id':program['id'],'plan_id':plan_id,'lesson_id':source['lesson_id'],'brief':source['brief']})
        private=lessons.job(job['id'],True);context=lessons.context(private['snapshot'],source['lesson_id'],{})
        data=deepcopy(source['data'])
        for ref in data['continuity']:
            if ref['version_id'] not in mapping:raise ValueError('Installa prima i materiali propedeutici richiesti.')
            ref['version_id']=mapping[ref['version_id']]
        errors=content_errors(data,context)
        if errors:raise ValueError(' '.join(errors))
        identifier=lessons.publish_lesson(job['id'],source['lesson_id'],data,context,source['checks'])
        lessons.finish(job['id']);mapping[source['id']]=identifier;installed.append(identifier)
    return {'program_id':program['id'],'plan_id':plan_id,'version_ids':installed}


def install(data_directory,annual,versions,title=DEFAULT_TITLE):
    if not isinstance(title,str) or not title.strip():raise ValueError('Il campione deve avere un titolo.')
    target=Store(data_directory)
    with tempfile.TemporaryDirectory(prefix='didactyx-pilot-') as staging:
        result=_prepare(staging,annual,versions,title)
        source=Store(staging)
        tables=['programs','annual_plans','plan_heads','lesson_versions','lesson_heads','planning_jobs']
        with closing(source.connect()) as src,closing(target.connect()) as dst,dst:
            dst.execute('BEGIN IMMEDIATE')
            if dst.execute('SELECT 1 FROM programs WHERE title=?',(title,)).fetchone():
                raise ValueError('Il pilota è già presente: nessun programma è stato sovrascritto.')
            for table in tables:
                for row in src.execute('SELECT * FROM '+table):
                    dst.execute('INSERT INTO '+table+' VALUES ('+','.join('?' for _ in row)+')',tuple(row))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,required=True)
    parser.add_argument('--annual',type=Path,required=True)
    parser.add_argument('--lessons',type=Path,nargs='+',required=True)
    parser.add_argument('--title',default=DEFAULT_TITLE)
    args=parser.parse_args()
    print(json.dumps(install(args.data_dir,json.loads(args.annual.read_text()),[json.loads(p.read_text()) for p in args.lessons],args.title),ensure_ascii=False))

if __name__=='__main__':main()
