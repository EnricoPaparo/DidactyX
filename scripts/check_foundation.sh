#!/bin/bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"
CHECK_PYTHON="$PROJECT_DIR/tmp/packaging-venv/bin/python"
if [ ! -x "$CHECK_PYTHON" ]; then CHECK_PYTHON=python3; fi
"$CHECK_PYTHON" -m unittest discover -s tests -v
ENGINE_BINARY="$PROJECT_DIR/dist/DidactyX.app/Contents/Resources/engine/didactyx-engine"
if [ ! -x "$ENGINE_BINARY" ]; then
    printf 'Costruisci prima l’app con bash scripts/build_macos.sh.\n' >&2
    exit 1
fi
mkdir -p tmp/checks
swiftc -swift-version 5 -parse-as-library \
    macos/Sources/DidactyX/Models.swift macos/Sources/DidactyX/EngineClient.swift \
    scripts/check_engine.swift -o tmp/checks/engine-client
DIDACTYX_TEST_ENGINE="$ENGINE_BINARY" tmp/checks/engine-client
