#!/usr/bin/env bash
#
# install.sh — pasang Office-Word MCP + skills di perangkat baru (macOS / Linux).
# Dipakai contributor & pengguna awam. Idempotent: aman dijalankan ulang.
#
# Yang dilakukan:
#   1. Cek Python >= 3.11
#   2. Buat virtualenv .venv-mcp + install dependensi Python
#   3. Daftarkan MCP server ke ~/.config/opencode/opencode.json (digabung, tidak menimpa)
#   4. Symlink skills ke ~/.config/opencode/skills/
#
# Windows: pakai Git Bash / WSL, atau lihat panduan manual di README.
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$REPO_DIR/.venv-mcp"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
CONFIG_FILE="$CONFIG_DIR/opencode.json"
SKILLS_DIR="$CONFIG_DIR/skills"

echo "==> [1/4] Cek Python..."
PY=""
for candidate in python3.11 python3.12 python3.13 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    ver="$("$candidate" -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')"
    major="${ver%%.*}"; minor="${ver#*.}"
    if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ] 2>/dev/null; then PY="$candidate"; break; fi
  fi
done
if [ -z "$PY" ]; then
  echo "ERROR: butuh Python >= 3.11. Install dulu: https://www.python.org/downloads/"
  echo "  macOS: brew install python@3.11"
  echo "  Ubuntu: sudo apt install python3.11 python3.11-venv"
  exit 1
fi
echo "    pakai: $PY ($("$PY" --version 2>&1))"

echo "==> [2/4] Virtualenv + dependensi..."
if [ ! -x "$VENV_DIR/bin/python" ]; then
  "$PY" -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/pip" install --upgrade pip >/dev/null
"$VENV_DIR/bin/pip" install fastmcp python-docx msoffcrypto-tool python-dotenv docx2pdf pytest
"$VENV_DIR/bin/python" -c "import fastmcp, docx; print('    dependensi OK')"

echo "==> [3/4] Daftarkan MCP ke OpenCode..."
mkdir -p "$CONFIG_DIR"
"$VENV_DIR/bin/python" - "$CONFIG_FILE" "$VENV_DIR" "$REPO_DIR" <<'EOF'
import json, os, sys
config_file, venv_dir, repo_dir = sys.argv[1], sys.argv[2], sys.argv[3]
cfg = {}
if os.path.exists(config_file):
    with open(config_file, encoding="utf-8") as fh:
        try:
            cfg = json.load(fh)
        except json.JSONDecodeError:
            print("    PERINGATAN: config lama rusak, dibuat baru (backup .bak)")
            os.replace(config_file, config_file + ".bak")
cfg.setdefault("mcp", {})["word-document-server"] = {
    "type": "local",
    "command": os.path.join(venv_dir, "bin", "python"),
    "args": [os.path.join(repo_dir, "word_mcp_server.py")],
    "env": {"PYTHONPATH": repo_dir, "MCP_TRANSPORT": "stdio"},
    "enabled": True,
}
with open(config_file, "w", encoding="utf-8") as fh:
    json.dump(cfg, fh, indent=2, ensure_ascii=False)
    fh.write("\n")
print("    MCP 'word-document-server' terdaftar di", config_file)
EOF

echo "==> [4/4] Pasang skills..."
mkdir -p "$SKILLS_DIR"
for skill in office-word-mcp skripsi-writing jurnal-writing; do
  src="$REPO_DIR/skills/$skill/SKILL.md"
  dest="$SKILLS_DIR/$skill"
  if [ -f "$src" ]; then
    mkdir -p "$dest"
    ln -sf "$src" "$dest/SKILL.md"
    echo "    skill '$skill' -> $dest/SKILL.md"
  fi
done

echo ""
echo "SELESAI. Langkah terakhir:"
echo "  1. Restart OpenCode agar MCP ke-load."
echo "  2. Tes cepat:"
echo "     $VENV_DIR/bin/python $REPO_DIR/smart_write.py info /path/ke/file.docx"
echo "  3. Bantuan tiap skill: buka skills/<nama>/SKILL.md"
