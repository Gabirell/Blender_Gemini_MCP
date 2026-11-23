#!/usr/bin/env bash
# Builds the installable zip (works for Blender 4.2+ Extensions and for older Blender via Add-ons → Install).
set -euo pipefail
cd "$(dirname "$0")"
VER=$(python3 -c "import tomllib;print(tomllib.load(open('blender_manifest.toml','rb'))['version'])")
python3 - "$VER" <<'PY'
import sys, zipfile
ver = sys.argv[1]
files = ['__init__.py', 'gemini_api.py', 'preferences.py', 'operators.py', 'blender_manifest.toml', 'LICENSE', 'README.md']
# Blender 4.2+ Extension: files at the root of the zip
with zipfile.ZipFile(f'gemini_mcp_assistant-{ver}.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for f in files: z.write(f, f)
# Blender 3.0–4.1 legacy add-on: files inside a folder
with zipfile.ZipFile(f'gemini_mcp_assistant-{ver}-blender3-4.1.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for f in files: z.write(f, 'gemini_mcp_assistant/' + f)
print('built', f'gemini_mcp_assistant-{ver}.zip', '+', f'gemini_mcp_assistant-{ver}-blender3-4.1.zip')
PY
