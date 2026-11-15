"""Prove locali di fattibilità; non è il motore applicativo di DidactyX.

Usa esclusivamente il login ChatGPT già gestito da Codex. Non legge file di
credenziali e non scrive risposte account complete nei risultati.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time


def save(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def object_schema(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


STRING = {"type": "string"}


def strings():
    return {"type": "array", "items": STRING}


def validate(value, schema, location="$"):
    """Valida il sottoinsieme di JSON Schema usato dalle fixture della prova."""
    kind = schema["type"]
    if kind == "object":
        assert isinstance(value, dict), location
        assert set(value) == set(schema["required"]), location
        for key, child in schema["properties"].items():
            validate(value[key], child, location + "." + key)
    elif kind == "array":
        assert isinstance(value, list), location
        for i, item in enumerate(value):
            validate(item, schema["items"], f"{location}[{i}]")
    elif kind == "string":
        assert isinstance(value, str), location
    elif kind == "boolean":
        assert isinstance(value, bool), location
    elif kind == "integer":
        assert type(value) is int, location
    else:
        raise ValueError("Tipo non previsto dalla fixture: " + kind)


class AppServer:
    def __init__(self, cwd: Path, images=False):
        executable = shutil.which("codex")
        if not executable:
            raise RuntimeError("Codex CLI non trovato")
        # Evita un fallback involontario all'autenticazione API a consumo.
        environment = {k: v for k, v in os.environ.items()
                       if k not in {"OPENAI_API_KEY", "CODEX_API_KEY"}}
        self.proc = subprocess.Popen(
            [executable, "-c", "features.apps=false", "-c", "features.shell_tool=false",
             "-c", "features.multi_agent=false", "-c", 'web_search="disabled"',
             "-c", f"features.image_generation={'true' if images else 'false'}",
             "app-server", "--listen", "stdio://"],
            cwd=cwd, env=environment, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1,
        )
        self.events = queue.Queue()
        self.sequence = 0
        self.notifications = []
        self.messages = {}
        self.methods = set()
        self.cwd = str(cwd)
        threading.Thread(target=self._read, daemon=True).start()
        try:
            self.request("initialize", {
                "clientInfo": {"name": "didactyx_feasibility", "title": "DidactyX feasibility", "version": "0.1"},
                "capabilities": {"experimentalApi": True},
            })
            self.send({"method": "initialized", "params": {}})
        except Exception:
            self.close()
            raise

    def _read(self):
        for line in self.proc.stdout:
            try:
                self.events.put(json.loads(line))
            except json.JSONDecodeError:
                continue
        self.events.put({"transport_closed": True})

    def send(self, message):
        self.proc.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()

    def next(self, timeout):
        message = self.events.get(timeout=timeout)
        if message.get("transport_closed"):
            raise RuntimeError("Trasporto app-server chiuso")
        method = message.get("method")
        if method:
            self.methods.add(method)
            if "id" in message:
                # La prova non autorizza esecuzioni di tool o richieste interattive.
                self.send({"id": message["id"], "error": {
                    "code": -32601, "message": "Tool e richieste interattive esclusi dalla prova"}})
            else:
                params = message.get("params", {})
                if method == "item/completed":
                    item = params.get("item", {})
                    if item.get("type") == "agentMessage":
                        self.messages.setdefault(params.get("turnId"), []).append(item.get("text", ""))
                self.notifications.append(message)
        return message

    def request(self, method, params=None, timeout=90):
        self.sequence += 1
        request_id = self.sequence
        self.send({"id": request_id, "method": method, "params": params or {}})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                response = self.next(max(0.1, deadline - time.monotonic()))
            except queue.Empty:
                raise TimeoutError(method) from None
            if response.get("id") == request_id and "method" not in response:
                if "error" in response:
                    error = response["error"]
                    raise RuntimeError(f"{method}: {error.get('code')} {error.get('message')}")
                return response["result"]
        raise TimeoutError(method)

    def start(self, role, persist=False):
        return self.request("thread/start", {
            "cwd": self.cwd, "approvalPolicy": "never", "sandbox": "read-only",
            "ephemeral": not persist,
            "baseInstructions": "Sei un autore didattico italiano. Rispondi al compito assegnato. Non usare tool, shell, rete, skill o agenti. Non leggere file. Tutti i dati necessari sono nel messaggio.",
            "developerInstructions": role,
        })

    def begin_turn(self, thread_id, prompt, schema=None):
        self.current_thread = thread_id
        params = {"threadId": thread_id, "input": [{"type": "text", "text": prompt}], "effort": "medium"}
        if schema:
            params["outputSchema"] = schema
        result = self.request("turn/start", params)
        return result["turn"]["id"]

    def finish_turn(self, turn_id, timeout=240):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for i, notice in enumerate(self.notifications):
                if notice.get("method") == "turn/completed" and notice.get("params", {}).get("turn", {}).get("id") == turn_id:
                    self.notifications.pop(i)
                    turn = notice["params"]["turn"]
                    return turn, "\n".join(self.messages.get(turn_id, []))
            try:
                self.next(max(0.1, min(30, deadline - time.monotonic())))
            except queue.Empty:
                continue
        self.request("turn/interrupt", {"threadId": self.current_thread, "turnId": turn_id})
        raise TimeoutError("Generazione oltre il timeout della prova")

    def generate(self, thread_id, prompt, schema):
        started = time.monotonic()
        self.current_thread = thread_id
        turn_id = self.begin_turn(thread_id, prompt, schema)
        turn, text = self.finish_turn(turn_id)
        if turn["status"] != "completed":
            raise RuntimeError("Turno non completato: " + json.dumps(turn.get("error")))
        value = json.loads(text)
        validate(value, schema)
        return value, {"status": turn["status"], "seconds": round(time.monotonic() - started, 2)}

    def close(self):
        if self.proc.poll() is None:
            self.proc.stdin.close()
            try:
                self.proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                self.proc.terminate()
                self.proc.wait(timeout=8)


def inspect(server):
    account = server.request("account/read", {"refreshToken": False})
    account_type = (account.get("account") or {}).get("type")
    if account_type != "chatgpt":
        raise RuntimeError("La prova richiede un login ChatGPT esistente; nessun fallback API")
    models = server.request("model/list", {})
    try:
        limits = server.request("account/rateLimits/read")
        rate_info = {"readable": True, "has_primary_window": bool((limits.get("rateLimits") or {}).get("primary")),
                     "has_secondary_window": bool((limits.get("rateLimits") or {}).get("secondary"))}
    except RuntimeError as error:
        rate_info = {"readable": False, "error": str(error)}
    catalog = [{"id": m.get("id"), "model": m.get("model"), "is_default": m.get("isDefault")}
               for m in models.get("data", [])]
    return {"authentication": "chatgpt", "model_catalog": catalog, "rate_limits": rate_info}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("output/feasibility"))
    parser.add_argument("--live", action="store_true", help="Esegue le generazioni usando la disponibilità dell'account")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    server = AppServer(Path.cwd())
    try:
        results = {"codex_version": subprocess.check_output(["codex", "--version"], text=True).strip(),
                   "environment": inspect(server), "checks": {}}
        save(output / "results.json", results)
        print(json.dumps(results, ensure_ascii=False), flush=True)
        if args.live:
            run_live(server, output, results)
    finally:
        server.close()


def run_live(server, output, results):
    lesson_schema = object_schema({
        "lesson_id": STRING, "title": STRING, "objectives": strings(),
        "sections": {"type": "array", "items": object_schema({"heading": STRING, "text": STRING})},
        "worked_example": object_schema({"project": STRING, "problem": STRING, "steps": strings(), "answer": STRING}),
        "introduced_concepts": strings(), "references_to_previous_lesson": strings(),
    })
    save(output / "lesson.schema.json", lesson_schema)
    brief = "Classe seconda di un istituto tecnico, dati interamente fittizi. Difficoltà a comprendere il significato dell'uguaglianza. Obiettivo: equazioni di primo grado spiegate per passaggi, con tono chiaro e senza salti logici."

    def record(name, value, check):
        save(output / (name + ".json"), value)
        results["checks"][name] = check
        save(output / "results.json", results)
        print(name + ": " + json.dumps(check, ensure_ascii=False), flush=True)

    first = server.start("Sviluppa una lezione corretta e autosufficiente. Il risultato è una prova tecnica, non il prodotto finale.")
    lesson1, info = server.generate(first["thread"]["id"], brief + "\nGenera L1 con circa 450 parole. Usa il progetto Faro: un kit costa x euro, si aggiungono 3 euro di trasporto e il totale è 11 euro. Spiega x + 3 = 11, perché sottrarre 3 da entrambi i membri, la soluzione 8 euro e la verifica per sostituzione. Non introdurre ancora equazioni con coefficienti diversi da 1. Nessun rimando a lezioni precedenti.", lesson_schema)
    record("lesson1", lesson1, {**info, "schema_fields_valid": True, "model": first.get("model")})

    second = server.start("Sei l'autore della seconda lezione. Usa il contenuto effettivo della lezione precedente ricevuta nel messaggio.", persist=True)
    thread_id = second["thread"]["id"]
    context = {"brief": brief, "previous_lesson": lesson1, "program_version": "fixture-v1"}
    save(output / "context.json", context)
    lesson2, info = server.generate(thread_id,
        json.dumps(context, ensure_ascii=False) + "\nGenera L2, circa 450 parole. Riprendi esplicitamente progetto Faro, costo del kit trovato in L1 e significato delle operazioni su entrambi i membri. Ora due kit identici e 3 euro di trasporto costano 19 euro: 2x + 3 = 19. Spiega sottrazione, divisione e verifica. references_to_previous_lesson deve indicare richiami concreti al testo ricevuto.", lesson_schema)
    assert lesson2["references_to_previous_lesson"], "Mancano richiami alla lezione precedente"
    assert "faro" in json.dumps(lesson2).lower(), "Scenario precedente non ripreso"
    record("lesson2", lesson2, {**info, "schema_fields_valid": True, "previous_content_used": True})
    save(output / "checkpoint.json", {"thread_id": thread_id, "context_sha256": hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()})

    fixture = {
        "teacher_request": "Mantieni esattamente tre esercizi impegnativi e senza spiegazioni nelle consegne. Puoi segnalare difficoltà eccessiva; non semplificare né aggiungere esercizi. Le soluzioni sotto sono metadati per il controllo e non fanno parte della consegna.",
        "exercises": [
            {"id": "E1", "question": "Risolvi 2x + 3 = 19", "candidate_answer": "x = 16"},
            {"id": "E2", "question": "Risolvi (3x - 2)/4 + (x + 1)/3 = 5", "candidate_answer": "x = 62/13"},
            {"id": "E3", "question": "Risolvi 2(x - 3) - 3(2x + 1) = 5 - 4x", "candidate_answer": "nessuna soluzione"},
        ],
    }
    save(output / "review_fixture.json", fixture)
    review_schema = object_schema({
        "detected_errors": {"type": "array", "items": object_schema({"exercise_id": STRING, "explanation": STRING, "corrected_answer": STRING})},
        "didactic_warnings": strings(), "exercise_count": {"type": "integer"},
        "teacher_instruction_preserved": {"type": "boolean"},
        "lesson_continuity_notes": strings(),
    })
    reviewer = server.start("Sei un revisore indipendente. Risolvi gli esercizi per controllare le risposte. Distingui errori oggettivi e preferenze didattiche; rispetta i vincoli del docente.")
    review, info = server.generate(reviewer["thread"]["id"],
        json.dumps({"lesson1": lesson1, "lesson2": lesson2, "exercise_fixture": fixture}, ensure_ascii=False)
        + "\nRevisiona la continuità delle due lezioni e gli esercizi. Elenca soltanto gli errori effettivi di soluzione. Le avvertenze sul livello sono consultive. Non riscrivere o ampliare le consegne.", review_schema)
    assert any(e["exercise_id"] == "E1" and "8" in e["corrected_answer"] for e in review["detected_errors"]), "Errore inserito non identificato"
    assert review["exercise_count"] == 3 and review["teacher_instruction_preserved"]
    assert review["didactic_warnings"], "Manca l'osservazione sul livello degli esercizi"
    record("independent_review", review, {**info, "seeded_error_detected": True, "teacher_request_preserved": True})

    # Interruzione reale del turno dopo l'inizio della risposta, poi riavvio del processo.
    interrupted_id = server.begin_turn(thread_id,
        "Per una prova di interruzione scrivi un approfondimento molto lungo di almeno 8000 parole sulle equazioni, senza tool. Inizia subito il testo.")
    deadline = time.monotonic() + 120
    saw_delta = False
    while time.monotonic() < deadline:
        try:
            notice = server.next(min(30, max(0.1, deadline - time.monotonic())))
        except queue.Empty:
            continue
        if notice.get("method") == "item/agentMessage/delta" and notice.get("params", {}).get("turnId") == interrupted_id:
            saw_delta = True
            break
        if notice.get("method") == "turn/completed":
            raise RuntimeError("Turno completato prima della prova di interruzione")
    assert saw_delta, "Nessun testo ricevuto prima dell'interruzione"
    server.request("turn/interrupt", {"threadId": thread_id, "turnId": interrupted_id})
    interrupted, _ = server.finish_turn(interrupted_id)
    assert interrupted["status"] == "interrupted", interrupted["status"]
    record("interruption", {"status": interrupted["status"], "stream_received": saw_delta}, {"passed": True})
    server.close()

    resumed = AppServer(Path.cwd())
    try:
        checkpoint = json.loads((output / "checkpoint.json").read_text())
        saved_context = json.loads((output / "context.json").read_text())
        saved_hash = hashlib.sha256(json.dumps(saved_context, sort_keys=True).encode()).hexdigest()
        assert saved_hash == checkpoint["context_sha256"], "Il contesto è cambiato dopo il checkpoint"
        resumed.request("thread/resume", {"threadId": checkpoint["thread_id"], "excludeTurns": True})
        memory_schema = object_schema({"project": STRING, "unit_cost_eur": {"type": "integer"}, "equation": STRING})
        memory, info = resumed.generate(checkpoint["thread_id"],
            "Non continuare l'approfondimento interrotto. Recupera solo dalla conversazione precedente il nome del progetto dell'esempio di L2, il costo di un kit e l'equazione usata in L2. Non usare tool.", memory_schema)
        assert "faro" in memory["project"].lower() and memory["unit_cost_eur"] == 8
        assert "19" in memory["equation"] and "2" in memory["equation"]
        record("resume_after_restart", memory, {**info, "passed": True, "context_reinjected": False})
        results["observed_notification_methods"] = sorted(server.methods | resumed.methods)
        results["completed"] = True
        save(output / "results.json", results)
    finally:
        resumed.close()


if __name__ == "__main__":
    main()
