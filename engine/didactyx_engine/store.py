"""Archivio locale con migrazione iniziale e aggiornamenti concorrenti protetti."""

from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import uuid


BRIEF_FIELDS = ("free_text", "school_context", "student_profile", "starting_knowledge",
                "objectives", "topics", "organisation", "preferences")


class DomainError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def text(value, label):
    if not isinstance(value, str):
        raise DomainError(-32602, f"Il campo {label} deve contenere testo.")
    return value


def normalize_brief(value):
    if not isinstance(value, dict) or set(value) - set(BRIEF_FIELDS):
        raise DomainError(-32602, "Il formato del brief non è valido.")
    return {key: text(value.get(key, ""), key) for key in BRIEF_FIELDS}


class Store:
    def __init__(self, directory):
        self.directory = Path(directory).expanduser().resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "library.sqlite3"
        with closing(self.connect()) as connection, connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version > 2:
                raise DomainError(-32010, "Questo archivio richiede una versione più recente di DidactyX.")
            connection.execute("PRAGMA journal_mode=WAL")
            if version == 0:
                connection.executescript("""
                CREATE TABLE IF NOT EXISTS programs (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, class_label TEXT NOT NULL,
                    description TEXT NOT NULL, brief_json TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    revision INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                PRAGMA user_version=1;
                """)
            if version < 2:
                connection.executescript("""
                    BEGIN IMMEDIATE;
                    CREATE TABLE IF NOT EXISTS annual_plans (
                        id TEXT PRIMARY KEY, program_id TEXT NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
                        version INTEGER NOT NULL, created_at TEXT NOT NULL, brief_json TEXT NOT NULL,
                        change_request TEXT NOT NULL, data_json TEXT NOT NULL,
                        UNIQUE(program_id, version)
                    );
                    CREATE TABLE IF NOT EXISTS plan_heads (
                        program_id TEXT PRIMARY KEY REFERENCES programs(id) ON DELETE CASCADE,
                        plan_id TEXT NOT NULL REFERENCES annual_plans(id)
                    );
                    CREATE TABLE IF NOT EXISTS planning_jobs (
                        id TEXT PRIMARY KEY, program_id TEXT NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
                        kind TEXT NOT NULL, status TEXT NOT NULL, phase TEXT NOT NULL, message TEXT NOT NULL,
                        created_at TEXT NOT NULL, updated_at TEXT NOT NULL, owner_pid INTEGER NOT NULL,
                        snapshot_json TEXT NOT NULL, checkpoint_json TEXT NOT NULL,
                        result_plan_id TEXT, error TEXT
                    );
                    CREATE UNIQUE INDEX IF NOT EXISTS one_running_plan_job ON planning_jobs(program_id)
                        WHERE status='running';
                    CREATE TABLE IF NOT EXISTS plan_reviews (
                        id TEXT PRIMARY KEY, plan_id TEXT NOT NULL REFERENCES annual_plans(id) ON DELETE CASCADE,
                        created_at TEXT NOT NULL, data_json TEXT NOT NULL
                    );
                    PRAGMA user_version=2;
                    COMMIT;
                """)

    def connect(self):
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    @staticmethod
    def decode(row):
        value = dict(row)
        value["brief"] = json.loads(value.pop("brief_json"))
        return value

    def list_programs(self):
        with closing(self.connect()) as connection:
            return [self.decode(row) for row in connection.execute(
                "SELECT * FROM programs ORDER BY updated_at DESC, id")]

    def get(self, program_id):
        text(program_id, "id")
        with closing(self.connect()) as connection:
            row = connection.execute("SELECT * FROM programs WHERE id=?", (program_id,)).fetchone()
            if row is None:
                raise DomainError(-32004, "Il programma non è stato trovato.")
            return self.decode(row)

    def create(self, params):
        if set(params) - {"title", "class_label", "description", "brief"}:
            raise DomainError(-32602, "La richiesta contiene campi non riconosciuti.")
        title = text(params.get("title", ""), "titolo").strip()
        if not title:
            raise DomainError(-32602, "Inserisci un titolo per il programma.")
        class_label = text(params.get("class_label", ""), "classe").strip()
        description = text(params.get("description", ""), "descrizione")
        brief = normalize_brief(params.get("brief", {}))
        program_id, timestamp = str(uuid.uuid4()), now()
        with closing(self.connect()) as connection, connection:
            connection.execute("INSERT INTO programs VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
                               (program_id, title, class_label, description,
                                json.dumps(brief, ensure_ascii=False), timestamp, timestamp))
        return self.get(program_id)

    def update(self, params):
        program_id = text(params.get("id"), "id")
        expected = params.get("expected_revision")
        patch = params.get("changes")
        if type(expected) is not int or not isinstance(patch, dict) or not patch:
            raise DomainError(-32602, "La richiesta di salvataggio non è valida.")
        if set(patch) - {"title", "class_label", "description", "brief"}:
            raise DomainError(-32602, "La richiesta contiene campi non riconosciuti.")
        with closing(self.connect()) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM programs WHERE id=?", (program_id,)).fetchone()
            if row is None:
                raise DomainError(-32004, "Il programma non è stato trovato.")
            current = self.decode(row)
            if current["revision"] != expected:
                raise DomainError(-32009, "Il programma è cambiato. Ricaricalo prima di applicare altre modifiche.")
            for key, value in patch.items():
                current[key] = normalize_brief(value) if key == "brief" else text(value, key)
            current["title"] = current["title"].strip()
            if not current["title"]:
                raise DomainError(-32602, "Inserisci un titolo per il programma.")
            current["updated_at"] = now()
            current["revision"] += 1
            connection.execute("""UPDATE programs SET title=?, class_label=?, description=?, brief_json=?,
                                  updated_at=?, revision=? WHERE id=?""",
                               (current["title"], current["class_label"], current["description"],
                                json.dumps(current["brief"], ensure_ascii=False), current["updated_at"],
                                current["revision"], program_id))
        return current

    def settings(self):
        with closing(self.connect()) as connection:
            rows = dict(connection.execute("SELECT key, value FROM settings"))
        return {"data_directory": str(self.directory),
                "export_directory": rows.get("export_directory", str(Path.home() / "Documents" / "DidactyX" / "PDF"))}

    def update_settings(self, params):
        if set(params) != {"export_directory"}:
            raise DomainError(-32602, "L'impostazione non è riconosciuta.")
        directory = Path(text(params["export_directory"], "cartella PDF")).expanduser()
        if not directory.is_absolute():
            raise DomainError(-32602, "Seleziona un percorso assoluto per i PDF.")
        with closing(self.connect()) as connection, connection:
            connection.execute("INSERT INTO settings VALUES ('export_directory', ?) "
                               "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(directory),))
        return self.settings()
