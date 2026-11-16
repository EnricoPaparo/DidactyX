from copy import deepcopy
import importlib.util
import json
import sqlite3
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
from didactyx_engine.generation import GenerationCancelled, GenerationError
from didactyx_engine.planning import PlanningManager
from didactyx_engine.planning_schema import CONTEXT, STRUCTURE, PLAN, REVIEW, plan_errors
from didactyx_engine.planning_store import PlanningStore
from didactyx_engine.store import DomainError, Store


def fixture():
    context = {"subject": "Fisica", "school_context": "Istituto tecnico", "class_profile": "Classe fittizia",
               "starting_knowledge": ["Proporzioni"], "goals": [{"id": "G1", "description": "Misurare"}, {"id": "G2", "description": "Applicare"}],
               "required_topics": ["Misure", "Circuiti"], "optional_topics": [], "preferences": [],
               "total_hours": 14, "hours": {"theory": 4, "laboratory": 4, "assessment": 2, "recovery": 2, "buffer": 2},
               "assumptions": ["Dati fittizi"], "curriculum_references": []}
    udas = []
    for number, title in enumerate(("Misure", "Circuiti"), 1):
        lessons = []
        for offset, kind in enumerate(("theory", "laboratory", "assessment")):
            index = (number - 1) * 3 + offset + 1
            lessons.append({"id": f"L{index}", "title": f"{title} {offset + 1}", "description": "Attività didattica",
                            "kind": kind, "duration_hours": 1 if kind == "assessment" else 2,
                            "objective_ids": [f"U{number}-O1"], "concepts": [title],
                            "prerequisite_lesson_ids": [f"L{index - 1}"] if index > 1 else [],
                            "methods": ["Esperienza guidata"], "project_ids": ["P1"]})
        udas.append({"id": f"U{number}", "title": title, "description": "Descrizione UDA", "period": f"Periodo {number}",
                     "prerequisites": ["Proporzioni"], "annual_goal_ids": [f"G{number}"],
                     "objectives": [{"id": f"U{number}-O1", "description": "Obiettivo operativo"}],
                     "knowledge": [title], "skills": ["Osservare"], "competences": ["Interpretare"],
                     "topics": [title], "optional_topics": [], "methods": ["Laboratorio"], "assessment": ["Prova pratica"],
                     "hours": {"theory": 2, "laboratory": 2, "assessment": 1}, "lessons": lessons})
    return {"context": context, "udas": udas, "projects": [{"id": "P1", "title": "Progetto annuale",
            "description": "Collega misure e circuiti", "competences": ["Applicare"],
            "milestones": [{"uda_id": f"U{n}", "description": "Esperimento", "deliverable": "Relazione"} for n in (1, 2)]}],
            "review_notes": ["Controllo didattico completato sulla fixture."]}


class Factory:
    def __init__(self):
        self.calls = []
        self.fail_at = None
        self.entered = threading.Event()
        self.release = threading.Event()
        self.release.set()

    def __call__(self, directory, cancelled):
        factory = self
        class Generator:
            def generate(self, role, inputs, instruction, schema):
                kind = "context" if schema == CONTEXT else "structure" if schema == STRUCTURE else "review" if schema == REVIEW else "plan"
                factory.calls.append(kind)
                factory.entered.set()
                while not factory.release.wait(0.01):
                    if cancelled(): raise GenerationCancelled()
                if cancelled(): raise GenerationCancelled()
                if factory.fail_at == len(factory.calls):
                    factory.fail_at = None
                    raise GenerationError("Errore di rete simulato")
                plan = fixture()
                if schema == CONTEXT: return plan["context"]
                if schema == STRUCTURE:
                    return {"udas": [{k: v for k, v in uda.items() if k != "lessons"} for uda in plan["udas"]],
                            "projects": plan["projects"], "review_notes": []}
                if schema == REVIEW:
                    return {"summary": "Revisione fittizia", "findings": [{"kind": "didactic", "location": "Misure",
                            "description": "Richiesta intenzionalmente impegnativa", "suggestion": "Valutare un esempio aggiuntivo"}]}
                return plan
            def close(self): pass
        return Generator()


def wait_job(manager, identifier):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        job = manager.store.job(identifier)
        if job["status"] != "running": return job
        time.sleep(0.01)
    raise AssertionError("La prova non si è conclusa")


class PlanningTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.store = Store(self.folder.name)
        self.program = self.store.create({"title": "Programma fittizio", "brief": {"free_text": "Da misure a circuiti"}})
        self.factory = Factory()
        self.manager = PlanningManager(self.store, self.factory)

    def tearDown(self):
        self.manager.shutdown()
        self.folder.cleanup()

    def generate(self):
        job = self.manager.start({"program_id": self.program["id"]})
        self.assertEqual(wait_job(self.manager, job["id"])["status"], "completed")
        return self.manager.store.state(self.program["id"])["current_plan"]

    def test_upgrade_from_foundation_preserves_brief_and_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            connection = sqlite3.connect(Path(folder) / "library.sqlite3")
            connection.executescript("""
                CREATE TABLE programs (id TEXT PRIMARY KEY, title TEXT NOT NULL, class_label TEXT NOT NULL,
                    description TEXT NOT NULL, brief_json TEXT NOT NULL, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1);
                CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                PRAGMA user_version=1;
            """)
            brief = self.program["brief"]
            connection.execute("INSERT INTO programs VALUES ('old','Titolo','2ª A','Descrizione',?,'t','t',7)", (json.dumps(brief),))
            connection.execute("INSERT INTO settings VALUES ('export_directory','/tmp/didactyx-example')")
            connection.commit()
            connection.close()
            upgraded = Store(folder)
            self.assertEqual(upgraded.get("old")["brief"], brief)
            self.assertEqual(upgraded.get("old")["revision"], 7)
            self.assertEqual(upgraded.settings()["export_directory"], "/tmp/didactyx-example")
            self.assertEqual(PlanningStore(upgraded).state("old")["versions"], [])

    def test_atomic_versions_and_readonly_previous_snapshot(self):
        first = self.generate()
        second = self.generate()
        self.assertEqual((first["version"], second["version"]), (1, 2))
        self.assertEqual(self.manager.store.get_version(self.program["id"], first["id"]), first)
        self.assertEqual(len(self.manager.store.state(self.program["id"])["versions"]), 2)

    def test_resume_uses_saved_stages_and_preserves_active_version(self):
        first = self.generate()
        count = len(self.factory.calls)
        self.factory.fail_at = count + 4
        job = self.manager.start({"program_id": self.program["id"], "change_request": "Rivedi il percorso"})
        self.assertEqual(wait_job(self.manager, job["id"])["status"], "failed")
        self.assertEqual(self.manager.store.state(self.program["id"])["current_plan"]["id"], first["id"])
        time.sleep(0.02)
        self.manager.resume(job["id"])
        self.assertEqual(wait_job(self.manager, job["id"])["status"], "completed")
        self.assertEqual(len(self.factory.calls) - count, 6)

    def test_changed_brief_does_not_silently_activate_old_context(self):
        self.factory.release.clear()
        job = self.manager.start({"program_id": self.program["id"]})
        self.assertTrue(self.factory.entered.wait(1))
        self.store.update({"id": self.program["id"], "expected_revision": 1, "changes": {"brief": {"free_text": "Nuovo traguardo"}}})
        self.factory.release.set()
        self.assertEqual(wait_job(self.manager, job["id"])["status"], "completed")
        state = self.manager.store.state(self.program["id"])
        self.assertIsNone(state["current_plan"])
        self.assertEqual(len(state["versions"]), 1)

    def test_cancel_and_single_active_job(self):
        self.factory.release.clear()
        job = self.manager.start({"program_id": self.program["id"]})
        self.assertTrue(self.factory.entered.wait(1))
        with self.assertRaises(DomainError): self.manager.start({"program_id": self.program["id"]})
        self.manager.cancel(job["id"])
        self.factory.release.set()
        self.assertEqual(wait_job(self.manager, job["id"])["status"], "cancelled")
        self.assertIsNone(self.manager.store.state(self.program["id"])["current_plan"])

    def test_manual_review_does_not_change_the_plan(self):
        first = self.generate()
        job = self.manager.start({"program_id": self.program["id"]}, "review")
        self.assertEqual(wait_job(self.manager, job["id"])["status"], "completed")
        state = self.manager.store.state(self.program["id"])
        self.assertEqual(state["current_plan"], first)
        self.assertEqual(state["latest_review"]["data"]["findings"][0]["kind"], "didactic")

    def test_recovery_of_abandoned_job(self):
        job = self.manager.store.new_job(self.program["id"])
        with patch("didactyx_engine.planning_store.os.kill", side_effect=ProcessLookupError):
            self.manager.store.recover()
        self.assertEqual(self.manager.store.job(job["id"])["status"], "interrupted")

    def test_previous_process_cannot_publish_or_stop_a_resumed_job(self):
        job = self.manager.store.new_job(self.program["id"])
        with self.store.connect() as connection:
            connection.execute("UPDATE planning_jobs SET owner_pid=-1 WHERE id=?", (job["id"],))
        self.assertFalse(self.manager.store.owned_running(job["id"]))
        self.manager.store.progress(job["id"], "wrong", "Stale process", {"context": {}})
        self.manager.store.stop(job["id"], "interrupted", "Stale process", owned=True)
        self.assertIsNone(self.manager.store.publish(job["id"], fixture()))
        self.assertEqual(self.manager.store.job(job["id"])["status"], "running")
        self.assertEqual(self.manager.store.job(job["id"])["phase"], "starting")
        self.manager.store.stop(job["id"], "cancelled", "Test concluso")

    @unittest.skipUnless(importlib.util.find_spec("reportlab"), "Il PDF richiede le dipendenze di costruzione")
    def test_pdf_export_does_not_generate_or_change_the_saved_version(self):
        from didactyx_engine.plan_pdf import export_plan
        version = self.generate()
        calls = len(self.factory.calls)
        result = export_plan(self.program, version, Path(self.folder.name) / "PDF")
        self.assertTrue(Path(result["path"]).read_bytes().startswith(b"%PDF"))
        self.assertEqual(self.factory.calls.__len__(), calls)
        self.assertEqual(self.manager.store.get_version(self.program["id"], version["id"]), version)


class StructuralChecks(unittest.TestCase):
    def test_valid_fixture(self): self.assertEqual(plan_errors(fixture()), [])

    def test_wrong_hours_and_forward_dependencies_are_detected(self):
        value = fixture()
        value["udas"][0]["lessons"][0]["duration_hours"] = 7
        value["udas"][0]["lessons"][0]["prerequisite_lesson_ids"] = ["L6"]
        errors = plan_errors(value)
        self.assertTrue(any("ore theory" in error for error in errors))
        self.assertTrue(any("prerequisito" in error for error in errors))

    def test_duplicate_ids_and_missing_objective_coverage(self):
        value = fixture()
        value["udas"][0]["objectives"].append({"id": "U1-O2", "description": "Non coperto"})
        value["udas"][1]["lessons"][0]["id"] = "L1"
        errors = plan_errors(value)
        self.assertTrue(any("duplicati" in error for error in errors))
        self.assertTrue(any("non sono coperti" in error for error in errors))


if __name__ == "__main__": unittest.main()
