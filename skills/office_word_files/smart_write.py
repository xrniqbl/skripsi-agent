#!/usr/bin/env python3
"""smart_write.py — satu pintu tulis Word: otomatis pilih mode terbaik.

- Dokumen TERBUKA di Word -> mode LIVE tanpa reload (append, heading,
  pagebreak via range; replace via execute-find; tabel via clipboard RTF).
- Dokumen TERTUTUP        -> mode FILE (python-docx via MCP tools).
- Operasi yang tidak bisa live (tabel, replace) saat dokumen terbuka:
  save dulu -> tulis file -> reload (aman, tidak ada yang hilang).
- --watch: bukakan dokumen di Word dulu agar bisa ditonton.
- FILE boleh berupa path, atau "auto" = dokumen AKTIF di Word (deteksi otomatis,
  tanpa hardcode). Contoh: smart_write.py info auto

Pakai:
  smart_write.py append FILE "teks" [--style "Heading 2"] [--delay 1.5] [--watch]
  smart_write.py heading FILE "teks" [--level 1] [--delay 1.5] [--watch]
  smart_write.py pagebreak FILE [--watch]
  smart_write.py table FILE ROWS COLS '[["a","b"],["1","2"]]' [--watch] [--no-reload]
  smart_write.py replace FILE "lama" "baru" [--watch] [--no-reload]
  smart_write.py sync FILE [--watch]   # save + satu reload (penutup batch --no-reload)
  smart_write.py read FILE
  smart_write.py info FILE

Batch hemat reload (3 op file = 1 reload):
  smart_write.py table F 2 2 '[["a","b"],["1","2"]]' --no-reload
  smart_write.py replace F "lama" "baru" --no-reload
  smart_write.py sync F
"""
import asyncio
import json
import subprocess
import sys
import time

OFFICE_DIR = "/Users/andypratama3/Development/tool_new/office"
sys.path.insert(0, OFFICE_DIR)


def osa(script: str) -> str:
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError("AppleScript: " + r.stderr.strip())
    return r.stdout.strip()


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def open_docs() -> list:
    try:
        out = osa('tell application "Microsoft Word" to get name of every document')
    except RuntimeError:
        return []
    if not out or out == "missing value":
        return []
    return [d.strip() for d in out.split(",")]


def is_open(word_file: str) -> bool:
    return word_file.rsplit("/", 1)[-1] in open_docs()


def detect_active_doc() -> str:
    """Path dokumen aktif di Word (deteksi otomatis, tanpa hardcode)."""
    try:
        out = osa('tell application "Microsoft Word" to get posix full name of active document')
    except RuntimeError as e:
        raise SystemExit(f"ERROR: tidak ada dokumen aktif di Word ({e})")
    if not out or out == "missing value":
        raise SystemExit("ERROR: tidak ada dokumen aktif di Word")
    return out


def front(word_file: str):
    osa(f'tell application "Microsoft Word" to open POSIX file "{word_file}"')


def ensure_active(word_file: str, timeout: float = 15.0):
    """Pastikan dokumen target yang aktif; tunggu bila Word lambat. Raise bila gagal.

    Mencegah bug operasi jatuh ke dokumen yang salah (race aktivasi).
    """
    import time as _time
    want = word_file.rsplit("/", 1)[-1]
    try:
        cur = osa('tell application "Microsoft Word" to get name of active document')
    except RuntimeError:
        cur = ""
    if cur != want:
        front(word_file)
        t0 = _time.time()
        while _time.time() - t0 < timeout:
            try:
                cur = osa('tell application "Microsoft Word" to get name of active document')
            except RuntimeError:
                cur = ""
            if cur == want:
                break
            _time.sleep(0.5)
    if cur != want:
        raise RuntimeError(f"dokumen aktif '{cur}', bukan target '{want}' — operasi dibatalkan")


def verify_saved(word_file: str):
    """Pastikan dokumen target benar-benar tersimpan. Raise bila belum."""
    doc = word_file.rsplit("/", 1)[-1]
    saved = osa(f'tell application "Microsoft Word" to get saved of document "{esc(doc)}"')
    if saved != "true":
        raise RuntimeError(f"dokumen '{doc}' belum tersimpan (saved={saved})")


def word_save():
    osa('tell application "Microsoft Word" to save active document')


def word_reload(word_file: str, watch: bool = False):
    """Reload via reload_word.py: background (scroll pulih, fokus tak dicuri)
    kecuali watch=True."""
    import os
    helper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reload_word.py")
    cmd = [sys.executable, helper, word_file] + (["--watch"] if watch else [])
    subprocess.run(cmd, check=True)


def live_append(word_file: str, lines: list, style: str, delay: float):
    ensure_active(word_file)
    for line in lines:
        osa(f'''tell application "Microsoft Word"
    tell active document
        set n to count characters of text object of active document
        set endPos to collapse range (create range start 0 end n) direction collapse end
        -- break DULU lalu teks (urutan teks-break menempel ke paragraf lama)
        set content of endPos to ((ASCII character 13) & "{esc(line)}")
        set style of last paragraph to "{esc(style)}"
    end tell
end tell''')
        time.sleep(delay)
    word_save()
    verify_saved(word_file)


def live_pagebreak(word_file: str):
    ensure_active(word_file)
    osa('''tell application "Microsoft Word"
    tell active document
        set n to count characters of text object of active document
        set endPos to collapse range (create range start 0 end n) direction collapse end
        set content of endPos to (ASCII character 12)
    end tell
end tell''')
    word_save()
    verify_saved(word_file)


def live_replace(word_file: str, find: str, repl: str) -> bool:
    """Find-replace seluruh dokumen secara live (tanpa reload)."""
    ensure_active(word_file)
    out = osa(f'''tell application "Microsoft Word"
    tell active document
        set r to create range start 0 end (count characters of text object of active document)
        tell find object of r to execute find find text "{esc(find)}" replace with "{esc(repl)}" replace replace all
    end tell
end tell''')
    word_save()
    verify_saved(word_file)
    return out == "true"


def _rtf_esc(s: str) -> str:
    out = []
    for ch in s:
        if ch in ("\\", "{", "}"):
            out.append("\\" + ch)
        elif ord(ch) < 128:
            out.append(ch)
        else:
            out.append(f"\\u{ord(ch)}?")
    return "".join(out)


def live_table(word_file: str, data: list) -> None:
    """Buat tabel live via clipboard RTF (header biru otomatis, tanpa reload)."""
    ensure_active(word_file)
    cols = len(data[0])
    total, cw = 8350, 8350 // cols
    xs = [(i + 1) * cw for i in range(cols)]
    border = ("\\clbrdrt\\brdrs\\brdrw15\\clbrdrl\\brdrs\\brdrw15"
              "\\clbrdrb\\brdrs\\brdrw15\\clbrdrr\\brdrs\\brdrw15")
    parts = ["{\\rtf1\\ansi\\ansicpg1252{\\fonttbl{\\f0 Times New Roman;}}"
             "{\\colortbl;\\red68\\green114\\blue196;\\red255\\green255\\blue255;}"]
    for ri, row in enumerate(data):
        parts.append("\\trowd\\trgaph108")
        for x in xs:
            cell = border + ("\\clshdng100\\clcbpat1" if ri == 0 else "")
            parts.append(f"{cell}\\cellx{x}")
        for val in row:
            v = _rtf_esc(str(val))
            if ri == 0:
                parts.append(f"\\pard\\intbl\\f0\\fs24\\cf2\\b {v}\\b0\\cf0\\cell")
            else:
                parts.append(f"\\pard\\intbl\\f0\\fs24 {v}\\cell")
        parts.append("\\row")
    parts.append("}")
    rtf = "".join(parts)
    # simpan clipboard teks user, kembalikan sesudahnya (best-effort)
    try:
        old_clip = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=10).stdout
    except Exception:
        old_clip = None
    try:
        subprocess.run(["pbcopy", "-Prefer", "rtf"], input=rtf, text=True, check=True, timeout=10)
        osa('''tell application "Microsoft Word"
    tell active document
        set n to count characters of text object of active document
        set content of (collapse range (create range start 0 end n) direction collapse end) to (ASCII character 13)
        paste object (collapse range (create range start 0 end (count characters of text object of active document)) direction collapse end)
    end tell
end tell''')
    finally:
        if old_clip:
            try:
                subprocess.run(["pbcopy"], input=old_clip, text=True, timeout=10)
            except Exception:
                pass
    word_save()
    verify_saved(word_file)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd, word_file = sys.argv[1], sys.argv[2]
    if word_file == "auto":
        word_file = detect_active_doc()
        print(f"[auto] dokumen aktif: {word_file}")
    rest = sys.argv[3:]
    watch = "--watch" in rest
    no_reload = "--no-reload" in rest  # gabung beberapa op file -> satu reload via 'sync'
    rest = [a for a in rest if a not in ("--watch", "--no-reload")]

    def opt(name, default):
        if name in rest:
            return rest[rest.index(name) + 1]
        return default

    if watch and not is_open(word_file):
        front(word_file)
        ensure_active(word_file)

    opened = is_open(word_file)
    # live ops memanggil ensure_active sendiri; di sini jangan front agar background

    from word_document_server.tools import document_tools, content_tools

    async def file_op(coro, need_reload=True):
        if opened:
            word_save()  # flush ketikan user dulu, aman
        res = await coro
        print(res)
        if opened and need_reload and not no_reload:
            word_reload(word_file, watch)
            print(f"[reload] {word_file}")
        return res

    async def run():
        if cmd == "append":
            style = opt("--style", "Normal")
            delay = float(opt("--delay", "1.5"))
            lines = [a for a in rest if not a.startswith("--")]
            # buang nilai opsi dari lines
            clean = []
            skip = False
            for i, a in enumerate(rest):
                if skip:
                    skip = False
                    continue
                if a in ("--style", "--delay"):
                    skip = True
                    continue
                clean.append(a)
            if opened:
                live_append(word_file, clean, style, delay)
                print(f"[live] {len(clean)} paragraf -> {word_file}")
            else:
                for ln in clean:
                    await file_op(content_tools.add_paragraph(word_file, ln), need_reload=False)
        elif cmd == "heading":
            level = int(opt("--level", "1"))
            delay = float(opt("--delay", "1.0"))
            text = rest[0]
            if opened:
                live_append(word_file, [text], f"Heading {level}", delay)
                print(f"[live] heading -> {word_file}")
            else:
                await file_op(content_tools.add_heading(word_file, text, level=level),
                              need_reload=False)
        elif cmd == "pagebreak":
            if opened:
                live_pagebreak(word_file)
                print(f"[live] page break -> {word_file}")
            else:
                await file_op(content_tools.add_page_break(word_file), need_reload=False)
        elif cmd == "table":
            rows, cols, data = int(rest[0]), int(rest[1]), json.loads(rest[2])
            if opened:
                live_table(word_file, data)
                print(f"[live] tabel {rows}x{cols} -> {word_file} (tanpa reload)")
            else:
                await file_op(content_tools.add_table(word_file, rows, cols, data))
                print(f"[file+reload] tabel {rows}x{cols} -> {word_file}")
        elif cmd == "replace":
            find, repl = rest[0], rest[1]
            if opened:
                ok = live_replace(word_file, find, repl)
                print(f"[live] replace '{find}' -> {word_file} ({'ketemu' if ok else 'tidak ketemu'})")
            else:
                await file_op(content_tools.search_and_replace(word_file, find, repl))
                print(f"[file+reload] replace '{find}' -> {word_file}")
        elif cmd == "read":
            print(await document_tools.get_document_text(word_file))
        elif cmd == "info":
            print(await document_tools.get_document_info(word_file))
        elif cmd == "sync":
            # save (flush ketikan) + satu reload background; penutup batch --no-reload
            if opened:
                word_save()
                word_reload(word_file, watch)
                print(f"[sync] {word_file}")
            else:
                print(f"[sync] {word_file} tidak terbuka, tidak ada yang perlu disinkron")
        else:
            print("Perintah tak dikenal:", cmd)
            sys.exit(1)

    asyncio.run(run())


if __name__ == "__main__":
    main()
