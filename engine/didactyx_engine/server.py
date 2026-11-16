"""Protocollo locale JSON a righe, con account e archivio indipendenti."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import signal
import sys
import threading

from . import __version__
from .codex import AccountReader
from .store import DomainError, Store
from .planning import PlanningManager
from .lessons import LessonManager


class Service:
    def __init__(self, directory):
        self.store = Store(directory)
        self.account = AccountReader()
        self.planning = PlanningManager(self.store)
        self.lessons = LessonManager(self.store)

    def job_manager(self, identifier):
        job = self.planning.store.job(identifier)
        return self.lessons if job['kind'].startswith('lesson_') else self.planning

    def dispatch(self, method, params):
        methods = {
            "system.ping": lambda: {"version": __version__, "protocol_version": 1},
            "program.list": lambda: self.store.list_programs(),
            "program.get": lambda: self.store.get(params.get("id")),
            "program.create": lambda: self.store.create(params),
            "program.update": lambda: self.store.update(params),
            "settings.get": lambda: self.store.settings(),
            "settings.update": lambda: self.store.update_settings(params),
            "account.status": lambda: self.account.status(params.get("refresh") is True),
            "plan.state": lambda: self.planning.store.state(params.get("program_id")),
            "plan.version": lambda: self.planning.store.get_version(params.get("program_id"), params.get("plan_id")),
            "plan.generate": lambda: self.planning.start(params),
            "plan.review": lambda: self.planning.start(params, "review"),
            "job.get": lambda: self.planning.store.job(params.get("id")),
            "job.cancel": lambda: self.job_manager(params.get("id")).cancel(params.get("id")),
            "job.resume": lambda: self.job_manager(params.get("id")).resume(params.get("id")),
            "plan.export": lambda: self.export_plan(params),
            "lesson.state": lambda: self.lessons.store.state(params.get('program_id'),params.get('plan_id'),params.get('lesson_id')),
            "lesson.version": lambda: self.lessons.store.version(params.get('program_id'),params.get('version_id')),
            "lesson.generate": lambda: self.lessons.start(params),
            "lesson.review": lambda: self.lessons.start(params,True),
            "lesson.document": lambda: self.lesson_document(params),
            "lesson.export": lambda: self.export_lesson(params),
            "lesson.brief.save": lambda: self.lessons.store.save_brief(params),
        }
        if method not in methods:
            raise DomainError(-32601, "Questa operazione non è disponibile.")
        return methods[method]()

    def export_plan(self, params):
        from .plan_pdf import export_plan
        program = self.store.get(params.get("program_id"))
        version = self.planning.store.get_version(program["id"], params.get("plan_id"))
        return export_plan(program, version, self.store.settings()["export_directory"])

    def lesson_document(self, params):
        from .lesson_render import render_html
        version=self.lessons.store.version(params.get('program_id'),params.get('version_id'))
        return {'html':render_html(version)}

    def export_lesson(self, params):
        from .lesson_render import export_pdf
        version=self.lessons.store.version(params.get('program_id'),params.get('version_id'))
        return export_pdf(version,self.store.settings()['export_directory'])

    def handle(self, request):
        identifier = request.get("id") if isinstance(request, dict) else None
        try:
            if (not isinstance(request, dict) or set(request) - {"id", "method", "params"}
                    or not isinstance(identifier, (str, int))
                    or isinstance(identifier, bool) or not isinstance(request.get("method"), str)
                    or not isinstance(request.get("params", {}), dict)):
                raise DomainError(-32600, "La richiesta non è valida.")
            return {"id": identifier, "result": self.dispatch(request["method"], request.get("params", {}))}
        except DomainError as error:
            return {"id": identifier, "error": {"code": error.code, "message": str(error)}}
        except Exception:
            return {"id": identifier, "error": {"code": -32603,
                    "message": "L'operazione non è riuscita. I dati già salvati sono conservati."}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()
    environment_directory = os.environ.get("DIDACTYX_DATA_DIR")
    directory = args.data_dir or (Path(environment_directory) if environment_directory else
                                 Path.home() / "Library" / "Application Support" / "DidactyX")
    try:
        service = Service(directory)
    except Exception:
        print("Impossibile aprire l'archivio locale di DidactyX.", file=sys.stderr)
        return 1
    lock = threading.Lock()

    def terminate(_signal, _frame):
        service.account.cancel()
        service.planning.shutdown()
        service.lessons.shutdown()
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, terminate)

    def reply(request):
        response = service.handle(request)
        with lock:
            print(json.dumps(response, ensure_ascii=False), flush=True)

    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            for line in sys.stdin:
                try:
                    request = json.loads(line)
                except json.JSONDecodeError:
                    with lock:
                        print(json.dumps({"id": None, "error": {"code": -32700, "message": "La richiesta non è leggibile."}}), flush=True)
                    continue
                executor.submit(reply, request)
    finally:
        service.planning.shutdown()
        service.lessons.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
