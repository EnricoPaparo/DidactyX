"""Sessioni Codex isolate per i ruoli didattici, con cancellazione cooperativa."""

import json
import os
import queue
import subprocess
import threading
import time

from .codex import executable
from .planning_schema import validate


class GenerationCancelled(Exception): pass
class GenerationError(Exception): pass


class CodexGenerator:
    def __init__(self, directory, cancelled):
        path = executable()
        if path is None: raise GenerationError("Codex non è disponibile su questo Mac.")
        self.cancelled = cancelled
        self.process = None
        self.sequence = 0
        self.events = queue.Queue()
        self.notices = []
        environment = {k: v for k, v in os.environ.items() if k not in {"OPENAI_API_KEY", "CODEX_API_KEY"}}
        try:
            self.process = subprocess.Popen(
                [path, "-c", "features.apps=false", "-c", "features.shell_tool=false",
                 "-c", "features.multi_agent=false", "-c", "features.image_generation=false",
                 "-c", 'web_search="disabled"', "app-server", "--listen", "stdio://"],
                cwd=directory, env=environment, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, text=True, bufsize=1)
            threading.Thread(target=self._read, daemon=True).start()
            self.request("initialize", {"clientInfo": {"name": "didactyx_generation", "title": "DidactyX", "version": "0.3.0"}})
            self.send({"method": "initialized", "params": {}})
            account = self.request("account/read", {"refreshToken": False}).get("account") or {}
            if account.get("type") != "chatgpt":
                raise GenerationError("Collega Codex al tuo account ChatGPT prima di generare il percorso.")
        except Exception:
            self.close()
            raise

    def _read(self):
        try:
            for line in self.process.stdout:
                try: self.events.put(json.loads(line))
                except json.JSONDecodeError: continue
        finally: self.events.put(None)

    def send(self, message):
        try:
            self.process.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
            self.process.stdin.flush()
        except (OSError, ValueError): raise GenerationError("Il collegamento a Codex si è interrotto. Puoi riprendere il lavoro.") from None

    def receive(self, deadline):
        while time.monotonic() < deadline:
            if self.cancelled(): raise GenerationCancelled()
            try: message = self.events.get(timeout=0.2)
            except queue.Empty: continue
            if message is None: raise GenerationError("Codex ha chiuso il collegamento. Puoi riprendere il lavoro.")
            if "method" in message:
                if "id" in message:
                    self.send({"id": message["id"], "error": {"code": -32601, "message": "Tool execution is not enabled"}})
                else: self.notices.append(message)
            return message
        raise GenerationError("Codex non ha completato il passaggio entro il tempo di attesa. I risultati precedenti sono conservati.")

    def request(self, method, params, timeout=45):
        self.sequence += 1
        identifier = self.sequence
        self.send({"id": identifier, "method": method, "params": params})
        deadline = time.monotonic() + timeout
        while True:
            message = self.receive(deadline)
            if message.get("id") == identifier and "method" not in message:
                if "error" in message: raise GenerationError("Codex non ha accettato la richiesta. Verifica l'accesso e riprova.")
                return message["result"]

    def generate(self, role, inputs, instruction, schema):
        self.notices.clear()
        thread = self.request("thread/start", {
            "cwd": str(os.getcwd()), "approvalPolicy": "never", "sandbox": "read-only", "ephemeral": True,
            "baseInstructions": "Sei un esperto di progettazione didattica scolastica italiana e della disciplina richiesta. Lavora esclusivamente sui dati nel messaggio. Non usare tool, file, rete, skill o sottoagenti. Rispondi secondo lo schema richiesto. Svolgi il ruolo assegnato con profondità, correttezza e chiarezza.",
            "developerInstructions": role,
        })
        thread_id = thread["thread"]["id"]
        result = self.request("turn/start", {"threadId": thread_id, "input": [{"type": "text",
            "text": json.dumps(inputs, ensure_ascii=False) + "\n\n" + instruction}], "effort": "high", "outputSchema": schema})
        turn_id = result["turn"]["id"]
        deadline = time.monotonic() + 1200
        try:
            while True:
                completed = next((notice for notice in self.notices
                                  if notice.get("method") == "turn/completed" and notice.get("params", {}).get("turn", {}).get("id") == turn_id), None)
                if completed:
                    turn = completed["params"]["turn"]
                    if turn["status"] != "completed":
                        error = turn.get("error") or {}
                        code = str(error.get("codexErrorInfo", ""))
                        if "usage" in code.lower() or "limit" in code.lower():
                            raise GenerationError("La disponibilità dell'account non consente di proseguire ora. Potrai riprendere questo passaggio.")
                        raise GenerationError("Codex non ha completato questo passaggio. Puoi riprenderlo senza perdere quelli già conclusi.")
                    messages = [notice["params"]["item"].get("text", "") for notice in self.notices
                                if notice.get("method") == "item/completed" and notice.get("params", {}).get("turnId") == turn_id
                                and notice.get("params", {}).get("item", {}).get("type") == "agentMessage"]
                    try:
                        value = json.loads("\n".join(messages))
                        validate(value, schema)
                    except (ValueError, TypeError):
                        raise GenerationError("Il risultato non rispetta il formato previsto. Puoi riprendere il passaggio.") from None
                    return value
                self.receive(deadline)
        except GenerationCancelled:
            self.send({"id": 999999, "method": "turn/interrupt", "params": {"threadId": thread_id, "turnId": turn_id}})
            raise

    def close(self):
        if self.process is None: return
        if self.process.stdin:
            try: self.process.stdin.close()
            except (OSError, ValueError): pass
        try: self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try: self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        if self.process.stdout: self.process.stdout.close()
