#!/usr/bin/env python3
"""Tulis teks LANGSUNG ke dokumen Word yang sedang terbuka (tanpa tutup-buka).

Teknik: AppleScript `create range` di ujung dokumen -> tidak menyentuh isi lain
(tabel & format aman), lalu `save` agar file di disk ikut sinkron.

Pakai: live_write.py "/path/file.docx" "baris1" "baris2" [--style "Heading 2" --delay 1.0]
  - Tiap baris ditambahkan sebagai paragraf baru secara live.
  - --style: style Word untuk baris-baris tersebut (default Normal).
  - --delay: jeda detik antar baris agar terlihat mengetik (default 1.5).
"""
import subprocess
import sys

def as_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')

def run_script(script: str) -> str:
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()

def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("Pakai: live_write.py FILE.docx \"teks1\" [\"teks2\" ...] [--style NAMA] [--delay DETIK]")
        sys.exit(1)
    word_file = args[0]
    if word_file == "auto":
        # deteksi dokumen aktif (tanpa hardcode)
        word_file = run_script('tell application "Microsoft Word" to get posix full name of active document')
        if not word_file or word_file == "missing value":
            print("ERROR: tidak ada dokumen aktif di Word")
            sys.exit(1)
        print(f"[auto] dokumen aktif: {word_file}")
    doc_name = word_file.rsplit("/", 1)[-1]
    style = "Normal"
    delay = 1.5
    lines = []
    i = 1
    while i < len(args):
        if args[i] == "--style" and i + 1 < len(args):
            style = args[i + 1]; i += 2
        elif args[i] == "--delay" and i + 1 < len(args):
            delay = float(args[i + 1]); i += 2
        else:
            lines.append(args[i]); i += 1

    import time
    # Pastikan dokumen target yang aktif (tunggu bila Word lambat; gagal = batal)
    cur = ""
    try:
        cur = run_script('tell application "Microsoft Word" to get name of active document')
    except RuntimeError:
        pass
    if cur != doc_name:
        run_script(f'tell application "Microsoft Word" to open POSIX file "{word_file}"')
        t0 = time.time()
        while time.time() - t0 < 15:
            try:
                cur = run_script('tell application "Microsoft Word" to get name of active document')
            except RuntimeError:
                cur = ""
            if cur == doc_name:
                break
            time.sleep(0.5)
    if cur != doc_name:
        print(f"ERROR: dokumen aktif '{cur}', bukan target '{doc_name}' — dibatalkan")
        sys.exit(1)

    for line in lines:
        script = f'''
tell application "Microsoft Word"
    tell active document
        set n to count characters of text object of active document
        set endPos to collapse range (create range start 0 end n) direction collapse end
        set content of endPos to ((ASCII character 13) & "{as_escape(line)}")
        set style of last paragraph to "{style}"
    end tell
end tell
'''
        run_script(script)
        time.sleep(delay)

    run_script('tell application "Microsoft Word" to save active document')
    saved = run_script(f'tell application "Microsoft Word" to get saved of document "{doc_name}"')
    if saved != "true":
        print(f"ERROR: dokumen '{doc_name}' belum tersimpan (saved={saved})")
        sys.exit(1)
    print(f"Live-wrote {len(lines)} paragraf ke {doc_name} (tanpa reload, sudah save)")

if __name__ == "__main__":
    main()
