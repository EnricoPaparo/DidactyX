"""Verifiche di persistenza, conflitti e protocollo del primo incremento."""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
from didactyx_engine.store import DomainError, Store
from didactyx_engine.server import Service


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.store = Store(self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def test_reopen_preserves_unicode_and_all_brief_fields(self):
        created = self.store.create({"title": "Elettronica e realtà", "class_label": "2ª A",
                                     "brief": {"free_text": "Dall’idea al circuito\nCon esempi concreti.",
                                               "objectives": "Capire perché, oltre al come."}})
        reopened = Store(self.directory.name).get(created["id"])
        self.assertEqual(reopened, created)
        self.assertEqual(len(reopened["brief"]), 8)
        self.assertEqual(Store(self.directory.name).list_programs()[0], created)

    def test_concurrent_edits_do_not_silently_overwrite(self):
        created = self.store.create({"title": "Programma"})
        def update(title):
            try:
                return self.store.update({"id": created["id"], "expected_revision": 1, "changes": {"title": title}})
            except DomainError as error:
                return error.code
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(update, ("Prima modifica", "Seconda modifica")))
        self.assertEqual(sum(isinstance(value, dict) for value in results), 1)
        self.assertIn(-32009, results)
        self.assertEqual(self.store.get(created["id"])["revision"], 2)

    def test_invalid_save_rolls_back_the_whole_change(self):
        created = self.store.create({"title": "Titolo valido", "description": "Originale"})
        with self.assertRaises(DomainError):
            self.store.update({"id": created["id"], "expected_revision": 1,
                               "changes": {"title": "  ", "description": "Da non salvare"}})
        self.assertEqual(self.store.get(created["id"]), created)

    def test_export_directory_persists(self):
        target = str(Path(self.directory.name) / "PDF con spazi")
        self.store.update_settings({"export_directory": target})
        self.assertEqual(Store(self.directory.name).settings()["export_directory"], target)

    def test_future_database_is_not_downgraded(self):
        import sqlite3
        with sqlite3.connect(self.store.path) as connection:
            connection.execute("PRAGMA user_version=99")
        with self.assertRaises(DomainError):
            Store(self.directory.name)

    def test_unknown_brief_fields_are_not_silently_discarded(self):
        with self.assertRaises(DomainError):
            self.store.create({"title": "Programma", "brief": {"unknown": "Da conservare"}})
        self.assertEqual(self.store.list_programs(), [])


class ProtocolTests(unittest.TestCase):
    def test_two_processes_share_the_saved_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, str(ROOT / "engine" / "runner.py"), "--data-dir", directory]
            def run(requests):
                result = subprocess.run(command, input="\n".join(json.dumps(r) for r in requests) + "\n",
                                        text=True, capture_output=True, check=True, timeout=10)
                return [json.loads(line) for line in result.stdout.splitlines()]
            first = run([{"id": "create", "method": "program.create", "params": {"title": "Riapertura"}}])[0]
            second = run([{"id": "list", "method": "program.list"}, {"id": "bad", "method": "missing"}])
            by_id = {value["id"]: value for value in second}
            self.assertEqual(by_id["list"]["result"][0]["id"], first["result"]["id"])
            self.assertEqual(by_id["bad"]["error"]["code"], -32601)

    def test_invalid_envelopes_return_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            service = Service(directory)
            for request in ([], {"id": True, "method": "program.list"}, {"id": 1, "method": "program.list", "params": []}):
                self.assertEqual(service.handle(request)["error"]["code"], -32600)


if __name__ == "__main__":
    unittest.main()
