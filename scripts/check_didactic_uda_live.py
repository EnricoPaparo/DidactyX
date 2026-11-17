"""Completa o rigenera la UDA del benchmark in un archivio separato. Consuma quota Codex."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'engine'),str(ROOT/'scripts')]
from install_lesson_pilot import install
from didactyx_engine.store import Store
from didactyx_engine.lessons import LessonManager
from didactyx_engine.lesson_schema import content_errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source',type=Path,default=ROOT/'docs/evidence/lesson-content/2026-11-16')
    parser.add_argument('--targets',nargs='+',default=['L3'])
    parser.add_argument('--resume',action='store_true',help='Riprende il lavoro registrato con gli stessi prompt')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    if args.output.joinpath('generation.json').exists():parser.error('Questa uscita contiene già una prova completa; scegli una nuova cartella.')
    args.data_dir.mkdir(parents=True,exist_ok=True);target_file=args.data_dir/'benchmark-target.json'
    if not target_file.exists():
        if (args.data_dir/'library.sqlite3').exists():parser.error('Usa un archivio nuovo, separato da quello personale.')
        annual=json.loads((args.source/'annual-plan.json').read_text())
        source_versions=[json.loads(p.read_text()) for p in sorted(args.source.glob('lesson-L*.json'))]
        result=install(args.data_dir,annual,source_versions)
        target_file.write_text(json.dumps(result))
    result=json.loads(target_file.read_text());manager=LessonManager(Store(args.data_dir))
    prompt_files=[ROOT/'engine/didactyx_engine/lessons.py',ROOT/'engine/didactyx_engine/lesson_prompts.py']
    prompt_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in prompt_files if p.exists()}
    initial={i:manager.store.head(result['plan_id'],i) for i in ['L1','L2','L3']}
    try:
        if args.resume:
            if not result.get('generation_job_id'):parser.error('Non è registrato un lavoro da riprendere.')
            if result.get('prompt_files_sha256')!=prompt_hashes:parser.error('I prompt sono cambiati: usa una nuova prova.')
            job=manager.resume(result['generation_job_id'])
            args.targets=manager.store.job(job['id'],True)['snapshot']['lesson_ids']
        else:
            if result.get('generation_job_id'):parser.error('Esiste già un lavoro registrato: usa --resume.')
            job=manager.start({'program_id':result['program_id'],'plan_id':result['plan_id'],'lesson_ids':args.targets,'brief':''})
            result.update({'generation_job_id':job['id'],'prompt_files_sha256':prompt_hashes})
            target_file.write_text(json.dumps(result))
        last=None
        while True:
            current=manager.store.job(job['id']);progress=current['status'],current['phase']
            if progress!=last:
                print(json.dumps({k:current[k] for k in ['status','phase','message']},ensure_ascii=False),flush=True);last=progress
            if current['status']!='running':break
            time.sleep(1)
        if current['status']!='completed':raise RuntimeError(current['error'] or current['message'])
        versions=[manager.store.head(result['plan_id'],i) for i in ['L1','L2','L3']]
        snapshot=manager.store.job(job['id'],True)['snapshot'];published={v['lesson_id']:v['id'] for v in versions}
        for version in versions:
            context=manager.store.context(snapshot,version['lesson_id'],published)
            assert not content_errors(version['data'],context)
            assert not any(c['status']=='failed' for c in version['checks'])
            assert not manager.store.stale_reasons(version)
            (args.output/f"lesson-{version['lesson_id']}.json").write_text(json.dumps(version,ensure_ascii=False,indent=2)+'\n')
        plan=manager.store.get_version(result['program_id'],result['plan_id'])
        (args.output/'annual-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
        for i,before in initial.items():
            if before:assert manager.store.version(result['program_id'],before['id'])==before
        assert prompt_hashes=={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in prompt_files if p.exists()}, 'I prompt sono cambiati durante la prova.'
        manifest={'targets':args.targets,'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'prompt_files_sha256':prompt_hashes,
            'previous_versions_unchanged':True,'source_bodies_validated':True,'all_lesson_dependencies_current':True}
        (args.output/'generation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'completed':True,'lessons':3,'source_versions_current':True}),flush=True)
    finally:manager.shutdown()

if __name__=='__main__':main()
