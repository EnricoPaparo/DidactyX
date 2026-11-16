"""Genera realmente le prime due lezioni del pilota: consuma quota Codex.

Usa un nuovo archivio di collaudo e il percorso annuale fittizio già salvato.
Non modifica l'archivio personale e non installa automaticamente il pilota.
"""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'engine'))
from didactyx_engine.server import Service
from didactyx_engine.lesson_schema import content_errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'tmp/lessons-live')
    parser.add_argument('--annual', type=Path, default=ROOT / 'docs/evidence/lesson-content/2026-11-16/annual-plan.json')
    args = parser.parse_args()
    if (args.data_dir / 'library.sqlite3').exists():
        parser.error('Scegli una cartella nuova: un archivio precedente non viene sovrascritto.')
    annual = json.loads(args.annual.read_text())
    service = Service(args.data_dir)
    try:
        program = service.store.create({'title': 'Due lezioni Python · collaudo reale',
            'class_label': '2ª superiore · dati fittizi', 'brief': annual['brief']})
        annual_job = service.planning.store.new_job(program['id'])
        plan_id = service.planning.store.publish(annual_job['id'], annual['data'])
        targets = [lesson['id'] for uda in annual['data']['udas'] for lesson in uda['lessons']][:2]
        params = {'program_id': program['id'], 'plan_id': plan_id, 'lesson_ids': targets, 'brief': ''}
        job = service.lessons.start(params)
        last = None
        while True:
            current = service.lessons.store.job(job['id'])
            progress = current['status'], current['phase']
            if progress != last:
                print(json.dumps({k: current[k] for k in ('status', 'phase', 'message')}, ensure_ascii=False), flush=True)
                last = progress
            if current['status'] != 'running':
                break
            time.sleep(1)
        if current['status'] != 'completed':
            raise RuntimeError(current.get('error') or current['message'])
        versions = [service.lessons.store.head(plan_id, lesson) for lesson in targets]
        for index, version in enumerate(versions):
            assert version, 'Manca un contenuto completo.'
            context = service.lessons.store.context(service.lessons.store.job(job['id'], True)['snapshot'], targets[index],
                {v['lesson_id']: v['id'] for v in versions[:index]})
            assert not content_errors(version['data'], context)
            assert all(check['status'] != 'failed' for check in version['checks'])
            (args.data_dir / f'lesson-{index+1}.json').write_text(json.dumps(version, ensure_ascii=False, indent=2) + '\n')
        assert any(ref['version_id'] == versions[0]['id'] for ref in versions[1]['data']['continuity'])
        print(json.dumps({'passed': True, 'lessons': targets, 'version_ids': [v['id'] for v in versions]}, ensure_ascii=False))
    finally:
        service.planning.shutdown()
        service.lessons.shutdown()


if __name__ == '__main__':
    main()
