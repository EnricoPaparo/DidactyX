#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"
if pgrep -f "$PROJECT_DIR/dist/DidactyX.app/Contents/MacOS/DidactyX" >/dev/null; then
    printf 'Chiudi DidactyX prima di ricostruire il pacchetto.\n' >&2
    exit 1
fi
BUILD_PYTHON="${DIDACTYX_BUILD_PYTHON:-python3}"
PACKAGING_ENV="$PROJECT_DIR/tmp/packaging-venv"
if [ ! -x "$PACKAGING_ENV/bin/python" ]; then
    "$BUILD_PYTHON" -m venv "$PACKAGING_ENV"
fi
"$PACKAGING_ENV/bin/python" -m pip install --disable-pip-version-check -q -r scripts/requirements-build.txt

swift build --package-path macos -c release
SWIFT_BIN_DIR="$(swift build --package-path macos -c release --show-bin-path)"
"$PACKAGING_ENV/bin/python" -m PyInstaller --noconfirm --clean --log-level WARN \
    --onedir --name didactyx-engine --paths engine \
    --distpath tmp/engine-dist --workpath tmp/engine-build --specpath tmp/engine-build engine/runner.py

APP_STAGE="$PROJECT_DIR/tmp/app-stage/DidactyX.app"
"$PACKAGING_ENV/bin/python" - <<'PY'
from pathlib import Path
import shutil
target = Path('tmp/app-stage/DidactyX.app')
if target.exists():
    shutil.rmtree(target)
PY
mkdir -p "$APP_STAGE/Contents/MacOS" "$APP_STAGE/Contents/Resources"
cp "$SWIFT_BIN_DIR/DidactyX" "$APP_STAGE/Contents/MacOS/DidactyX"
ditto tmp/engine-dist/didactyx-engine "$APP_STAGE/Contents/Resources/engine"
cp macos/Info.plist "$APP_STAGE/Contents/Info.plist"
swift scripts/make_icon.swift "$PROJECT_DIR/tmp/app-icon.iconset"
iconutil -c icns tmp/app-icon.iconset -o "$APP_STAGE/Contents/Resources/DidactyX.icns"
codesign --force --deep --sign - "$APP_STAGE"
codesign --verify --deep --strict "$APP_STAGE"
mkdir -p dist
"$PACKAGING_ENV/bin/python" - <<'PY'
from pathlib import Path
import shutil
target = Path('dist/DidactyX.app')
if target.exists():
    shutil.rmtree(target)
shutil.copytree('tmp/app-stage/DidactyX.app', target, symlinks=True)
print('App creata: dist/DidactyX.app')
PY
