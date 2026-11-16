"""Lettura account tramite il protocollo ufficiale; nessuna richiesta generativa."""

import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time


def executable():
    candidates = [shutil.which("codex"),
                  "/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex",
                  "/Applications/Codex.app/Contents/Resources/codex",
                  "/opt/homebrew/bin/codex", "/usr/local/bin/codex"]
    return next((str(Path(path).resolve()) for path in candidates if path and os.access(path, os.X_OK)), None)


class AccountReader:
    def __init__(self):
        self.lock = threading.Lock()
        self.cached = None
        self.cached_at = 0
        self.process_lock = threading.Lock()
        self.process = None
        self.closing = threading.Event()

    def cancel(self):
        self.closing.set()
        with self.process_lock:
            process = self.process
        if process is not None and process.poll() is None:
            try:
                process.terminate()
            except OSError:
                pass

    def status(self, refresh=False):
        with self.lock:
            if self.cached is not None and not refresh and time.monotonic() - self.cached_at < 15:
                return self.cached
            result = self._read()
            self.cached, self.cached_at = result, time.monotonic()
            return result

    def _read(self):
        path = executable()
        result = {"installed": bool(path), "connected": False, "authentication": None,
                  "email": None, "plan": None, "used_percent": None, "resets_at": None,
                  "version": None, "message": "Codex non è stato trovato su questo Mac."}
        if path is None:
            return result
        process = None
        try:
            environment = {k: v for k, v in os.environ.items()
                           if k not in {"OPENAI_API_KEY", "CODEX_API_KEY"}}
            result["version"] = subprocess.check_output([path, "--version"], env=environment,
                                                       timeout=5, stderr=subprocess.DEVNULL, text=True).strip()
            process = subprocess.Popen(
                [path, "-c", "features.apps=false", "-c", "features.shell_tool=false",
                 "-c", "features.multi_agent=false", "-c", 'web_search="disabled"',
                 "app-server", "--listen", "stdio://"],
                env=environment, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, text=True, bufsize=1)
            with self.process_lock:
                self.process = process
            if self.closing.is_set():
                process.terminate()
            messages = queue.Queue()

            def read():
                for line in process.stdout:
                    try:
                        messages.put(json.loads(line))
                    except json.JSONDecodeError:
                        continue
                messages.put(None)

            threading.Thread(target=read, daemon=True).start()

            def send(value):
                process.stdin.write(json.dumps(value) + "\n")
                process.stdin.flush()

            def request(identifier, method, params):
                send({"id": identifier, "method": method, "params": params})
                deadline = time.monotonic() + 12
                while time.monotonic() < deadline:
                    message = messages.get(timeout=max(0.1, deadline - time.monotonic()))
                    if message is None:
                        raise RuntimeError("connection_closed")
                    if "method" in message and "id" in message:
                        send({"id": message["id"], "error": {"code": -32601, "message": "Unsupported request"}})
                    if message.get("id") == identifier and "method" not in message:
                        if "error" in message:
                            raise RuntimeError("rpc_error")
                        return message["result"]
                raise TimeoutError()

            request(1, "initialize", {"clientInfo": {"name": "didactyx", "title": "DidactyX", "version": "0.3.1"}})
            send({"method": "initialized", "params": {}})
            response = request(2, "account/read", {"refreshToken": False})
            account = response.get("account") or {}
            result["authentication"] = account.get("type")
            result["connected"] = account.get("type") == "chatgpt"
            if result["connected"]:
                result["email"] = account.get("email")
                result["plan"] = account.get("planType")
                result["message"] = "Account ChatGPT collegato."
                try:
                    limits = request(3, "account/rateLimits/read", {}).get("rateLimits") or {}
                    primary = limits.get("primary") or {}
                    used = primary.get("usedPercent")
                    if isinstance(used, (int, float)) and not isinstance(used, bool):
                        result["used_percent"] = min(100, max(0, used))
                    result["resets_at"] = primary.get("resetsAt")
                except (RuntimeError, TimeoutError, queue.Empty):
                    pass
            elif account:
                result["message"] = "Codex usa un accesso diverso da ChatGPT. Gestisci l'accesso dal client Codex."
            else:
                result["message"] = "Accedi a Codex con ChatGPT per collegare il tuo account."
        except (OSError, RuntimeError, TimeoutError, subprocess.SubprocessError, queue.Empty, ValueError):
            result["message"] = "Non riesco a leggere lo stato di Codex. Riprova tra poco."
        finally:
            if process is not None:
                if process.stdin:
                    try:
                        process.stdin.close()
                    except OSError:
                        pass
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                if process.stdout:
                    process.stdout.close()
            with self.process_lock:
                self.process = None
        return result
