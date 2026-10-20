#!/usr/bin/env python3
"""Reload BACKGROUND dokumen Word (tampilkan versi terbaru dari disk).

- Tanpa argumen FILE (atau FILE="auto"): pakai dokumen AKTIF di Word
  (terdeteksi otomatis — tidak ada path hardcode).
- Default background: Word TIDAK dibawa ke depan. Bila Word sedang di
  background, ia disembunyikan sesaat selama tukar dokumen -> tanpa kedip,
  tanpa curi fokus. Posisi scroll dikembalikan.
- --watch: bawa Word ke depan (untuk demo ditonton).
"""
import subprocess
import sys

WATCH = "--watch" in sys.argv
args = [a for a in sys.argv[1:] if a != "--watch"]
GIVEN = args[0] if args else "auto"


def osa(script: str) -> str:
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()


def detect_active_doc() -> str:
    """Path POSIX dokumen aktif di Word; error bila tidak ada."""
    try:
        out = osa('tell application "Microsoft Word" to get posix full name of active document')
    except RuntimeError as e:
        raise RuntimeError(f"tidak ada dokumen aktif di Word ({e})")
    if not out or out == "missing value":
        raise RuntimeError("tidak ada dokumen aktif di Word")
    return out


WORD_FILE = detect_active_doc() if GIVEN == "auto" else GIVEN
DOC_NAME = WORD_FILE.rsplit("/", 1)[-1]

if WATCH:
    focus_back = 'tell application "Microsoft Word" to activate'
else:
    focus_back = ("try\n"
                  "        tell process prevApp to set frontmost to true\n"
                  "    on error errMsg\n"
                  "        log (\"restore focus gagal: \" & errMsg)\n"
                  "    end try")

# FASE 1 (wajib berhasil): sembunyikan Word, tukar dokumen, kembalikan scroll.
# FASE 2 (best-effort): kembalikan visibilitas + fokus aplikasi sebelumnya.
# Dipisah agar macet pada fase fokus tidak menutupi suksesnya reload
# (ditemukan Okt 2026: query System Events soal frontmost bisa menggantung
#  sementara perintah Word-nya sendiri baik-baik saja).
SWAP = f'''tell application "System Events"
    tell process "Microsoft Word"
        set wasVisible to visible
        set visible to false
    end tell
end tell
tell application "Microsoft Word"
    try
        set scrollPos to vertical percent scrolled of active window
    on error
        set scrollPos to 0
    end try
    try
        close document "{DOC_NAME}" saving no
    end try
    open POSIX file "{WORD_FILE}"
    delay 0.5
    try
        set vertical percent scrolled of active window to scrollPos
    end try
end tell
tell application "System Events"
    tell process "Microsoft Word"
        set visible to wasVisible
    end tell
end tell
'''

RESTORE = f'''tell application "System Events"
    set prevApp to name of first process whose frontmost is true
    {focus_back}
end tell
'''

r = subprocess.run(["osascript", "-e", SWAP], capture_output=True, text=True, timeout=60)
if r.returncode != 0:
    # Fallback: buka langsung tanpa sembunyi/fokus (tidak perlu assistive access).
    # Terjadi bila System Events menggantung (TCC assistive-access revoke).
    r3 = subprocess.run(["osascript", "-e",
                         f'tell application "Microsoft Word" to open POSIX file "{WORD_FILE}"'],
                        capture_output=True, text=True, timeout=60)
    if r3.returncode != 0:
        print("RELOAD GAGAL:", (r.stderr.strip() or r3.stderr.strip())[:200])
        sys.exit(1)
    print(f"Reloaded (open-fallback): {DOC_NAME}")
    sys.exit(0)
try:
    r2 = subprocess.run(["osascript", "-e", RESTORE], capture_output=True, text=True, timeout=15)
    if r2.returncode != 0:
        print("peringatan fokus:", r2.stderr.strip()[:100])
except subprocess.TimeoutExpired:
    print("peringatan: pengembalian fokus timeout (reload tetap berhasil)")
mode = "watch" if WATCH else "background"
print(f"Reloaded ({mode}): {DOC_NAME}")
