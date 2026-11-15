from contextlib import closing
import json
import os
import sqlite3
import uuid

from .store import DomainError, now, text


class PlanningStore:
    def __init__(self, store): self.store = store

    @staticmethod
    def decode_plan(row):
        if row is None: return None
        value = dict(row)
        value["brief"] = json.loads(value.pop("brief_json"))
        value["data"] = json.loads(value.pop("data_json"))
        return value

    @staticmethod
    def decode_job(row, private=False):
        if row is None: return None
        value = dict(row)
        if private:
            value["snapshot"] = json.loads(value.pop("snapshot_json"))
            value["checkpoint"] = json.loads(value.pop("checkpoint_json"))
        else:
            for key in ("snapshot_json", "checkpoint_json", "owner_pid"): value.pop(key, None)
        return value

    def get_version(self, program_id, plan_id):
        with closing(self.store.connect()) as connection:
            row = connection.execute("SELECT * FROM annual_plans WHERE id=? AND program_id=?", (plan_id, program_id)).fetchone()
            if row is None: raise DomainError(-32004, "La versione del percorso non è stata trovata.")
            return self.decode_plan(row)

    def state(self, program_id):
        program = self.store.get(program_id)
        with closing(self.store.connect()) as connection:
            head = self.decode_plan(connection.execute("SELECT p.* FROM annual_plans p JOIN plan_heads h ON h.plan_id=p.id WHERE h.program_id=?", (program_id,)).fetchone())
            versions = [dict(row) for row in connection.execute("SELECT id,version,created_at,change_request FROM annual_plans WHERE program_id=? ORDER BY version DESC", (program_id,))]
            job = self.decode_job(connection.execute("SELECT * FROM planning_jobs WHERE program_id=? ORDER BY created_at DESC LIMIT 1", (program_id,)).fetchone())
            review = None
            if head:
                row = connection.execute("SELECT * FROM plan_reviews WHERE plan_id=? ORDER BY created_at DESC LIMIT 1", (head["id"],)).fetchone()
                if row:
                    review = dict(row)
                    review["data"] = json.loads(review.pop("data_json"))
        return {"current_plan": head, "versions": versions, "latest_job": job,
                "brief_pending": head is not None and head["brief"] != program["brief"], "latest_review": review}

    def job(self, job_id, private=False):
        with closing(self.store.connect()) as connection:
            row = connection.execute("SELECT * FROM planning_jobs WHERE id=?", (job_id,)).fetchone()
            if row is None: raise DomainError(-32004, "L'attività non è stata trovata.")
            return self.decode_job(row, private)

    def owned_running(self, job_id):
        with closing(self.store.connect()) as connection:
            return connection.execute("SELECT 1 FROM planning_jobs WHERE id=? AND status='running' AND owner_pid=?",
                                      (job_id, os.getpid())).fetchone() is not None

    def new_job(self, program_id, change_request="", kind="generate"):
        program = self.store.get(program_id)
        current = self.state(program_id)["current_plan"]
        if kind == "review" and current is None: raise DomainError(-32602, "Genera prima un percorso da revisionare.")
        snapshot = {"program": program, "previous_plan": current, "change_request": text(change_request, "richiesta di modifica")}
        snapshot["brief_changed"] = current is not None and current["brief"] != program["brief"]
        if kind == "review": snapshot["program"]["brief"] = current["brief"]
        identifier, timestamp = str(uuid.uuid4()), now()
        try:
            with closing(self.store.connect()) as connection, connection:
                connection.execute("INSERT INTO planning_jobs VALUES (?, ?, ?, 'running', 'starting', ?, ?, ?, ?, ?, '{}', NULL, NULL)",
                                   (identifier, program_id, kind, "Preparazione del contesto…", timestamp, timestamp,
                                    os.getpid(), json.dumps(snapshot, ensure_ascii=False)))
        except sqlite3.IntegrityError:
            raise DomainError(-32009, "C'è già un'attività in corso per questo programma.") from None
        return self.job(identifier)

    def progress(self, job_id, phase, message, checkpoint=None):
        with closing(self.store.connect()) as connection, connection:
            if checkpoint is None:
                connection.execute("UPDATE planning_jobs SET phase=?,message=?,updated_at=? WHERE id=? AND status='running' AND owner_pid=?", (phase, message, now(), job_id, os.getpid()))
            else:
                connection.execute("UPDATE planning_jobs SET phase=?,message=?,checkpoint_json=?,updated_at=? WHERE id=? AND status='running' AND owner_pid=?",
                                   (phase, message, json.dumps(checkpoint, ensure_ascii=False), now(), job_id, os.getpid()))

    def stop(self, job_id, status, message, owned=False):
        with closing(self.store.connect()) as connection, connection:
            connection.execute("UPDATE planning_jobs SET status=?,message=?,error=?,updated_at=? WHERE id=? AND status='running' AND (?=0 OR owner_pid=?)",
                               (status, message, message if status == "failed" else None, now(), job_id, int(owned), os.getpid()))

    def resume(self, job_id):
        try:
            with closing(self.store.connect()) as connection, connection:
                connection.execute("BEGIN IMMEDIATE")
                row = connection.execute("SELECT status FROM planning_jobs WHERE id=?", (job_id,)).fetchone()
                if row is None or row["status"] not in ("failed", "interrupted", "cancelled"):
                    raise DomainError(-32602, "Questa attività non può essere ripresa.")
                connection.execute("UPDATE planning_jobs SET status='running',owner_pid=?,message=?,error=NULL,updated_at=? WHERE id=?",
                                   (os.getpid(), "Ripresa dall'ultimo passaggio completato…", now(), job_id))
        except sqlite3.IntegrityError:
            raise DomainError(-32009, "C'è già un'altra attività in corso.") from None
        return self.job(job_id)

    def recover(self):
        with closing(self.store.connect()) as connection, connection:
            for row in connection.execute("SELECT id,owner_pid FROM planning_jobs WHERE status='running'").fetchall():
                try: os.kill(row["owner_pid"], 0)
                except ProcessLookupError:
                    connection.execute("UPDATE planning_jobs SET status='interrupted',message=?,updated_at=? WHERE id=? AND status='running'",
                                       ("Attività interrotta. Puoi riprendere dai risultati salvati.", now(), row["id"]))
                except PermissionError: pass

    def publish(self, job_id, data):
        with closing(self.store.connect()) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            job = self.decode_job(connection.execute("SELECT * FROM planning_jobs WHERE id=?", (job_id,)).fetchone(), True)
            if job["status"] != "running" or job["owner_pid"] != os.getpid(): return None
            snapshot = job["snapshot"]
            program_id = job["program_id"]
            current_program = connection.execute("SELECT brief_json FROM programs WHERE id=?", (program_id,)).fetchone()
            number = connection.execute("SELECT COALESCE(MAX(version),0)+1 FROM annual_plans WHERE program_id=?", (program_id,)).fetchone()[0]
            identifier = str(uuid.uuid4())
            connection.execute("INSERT INTO annual_plans VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (identifier, program_id, number, now(), json.dumps(snapshot["program"]["brief"], ensure_ascii=False),
                                snapshot["change_request"], json.dumps(data, ensure_ascii=False)))
            active = json.loads(current_program["brief_json"]) == snapshot["program"]["brief"]
            if active:
                connection.execute("INSERT INTO plan_heads VALUES (?, ?) ON CONFLICT(program_id) DO UPDATE SET plan_id=excluded.plan_id", (program_id, identifier))
            message = "Percorso annuale completato e revisionato." if active else "Versione completata. Il brief è cambiato: trovi il risultato nelle versioni del percorso."
            connection.execute("UPDATE planning_jobs SET status='completed',phase='completed',message=?,result_plan_id=?,updated_at=? WHERE id=?",
                               (message, identifier, now(), job_id))
            return identifier

    def publish_review(self, job_id, report):
        job = self.job(job_id, True)
        with closing(self.store.connect()) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            if connection.execute("SELECT 1 FROM planning_jobs WHERE id=? AND status='running' AND owner_pid=?", (job_id, os.getpid())).fetchone() is None: return
            connection.execute("INSERT INTO plan_reviews VALUES (?, ?, ?, ?)",
                               (str(uuid.uuid4()), job["snapshot"]["previous_plan"]["id"], now(), json.dumps(report, ensure_ascii=False)))
            connection.execute("UPDATE planning_jobs SET status='completed',phase='completed',message=?,updated_at=? WHERE id=?",
                               ("Revisione completata. Le proposte sono consultabili nel percorso.", now(), job_id))
