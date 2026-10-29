#!/usr/bin/env python3
"""Periksa dependensi bundel: apa yang diimpor, apa yang belum terpasang.

Pemakaian:
    python3 scripts/cek_dependensi.py
    python3 scripts/cek_dependensi.py --json laporan.json

Kode keluar:
    0  semua dependensi pihak ketiga tersedia
    1  ada yang belum terpasang
    2  tidak bisa memindai
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# nama impor -> nama paket di requirements.txt
PETA = {
    "docx": "python-docx",
    "yaml": "PyYAML",
    "lxml": "lxml",
    "scipy": "scipy",
    "numpy": "numpy",
    "pandas": "pandas",
    "openpyxl": "openpyxl",
    "requests": "requests",
    "dotenv": "python-dotenv",
    "msoffcrypto": "msoffcrypto-tool",
    "pytest": "pytest",
    # nama impor berbeda dari nama paket di PyPI — tanpa pemetaan ini
    # "PIL terpasang tapi tidak tercatat" muncul sebagai temuan palsu.
    "PIL": "Pillow",
    "fastmcp": "fastmcp",
    "mcp": "mcp",
    "docx2pdf": "docx2pdf",
    "citeproc": "citeproc-py",
    "bibtexparser": "bibtexparser",
}

RE_IMPOR = re.compile(
    r"^\s*(?:import\s+([\w.]+)|from\s+([\w.]+)\s+import)", re.M)

STANDAR_MINIMAL = {
    "os", "sys", "re", "json", "math", "time", "datetime", "pathlib", "shutil",
    "subprocess", "argparse", "csv", "random", "statistics", "collections",
    "itertools", "functools", "urllib", "tempfile", "textwrap", "hashlib",
    "zipfile", "email", "html", "typing", "dataclasses", "enum", "io", "copy",
    "string", "unicodedata", "difflib", "glob", "base64", "binascii", "uuid",
    "traceback", "logging", "unittest",
} | set(getattr(sys, "stdlib_module_names", ()))


def modul_lokal() -> set[str]:
    """Nama modul .py dan paket di dalam repo — bukan dependensi eksternal."""
    lokal: set[str] = set()
    for akar, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in
                   (".git", ".venv", "__pycache__", "node_modules")]
        for f in files:
            if f.endswith(".py"):
                lokal.add(f[:-3])
        for d in dirs:
            if os.path.isfile(os.path.join(akar, d, "__init__.py")):
                lokal.add(d)
    return lokal


def pindai() -> dict[str, list[str]]:
    """Kembalikan {nama_impor: [berkas yang memakai]}."""
    pakai: dict[str, list[str]] = {}
    lokal = modul_lokal()
    for akar, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in
                   (".git", ".venv", "__pycache__", "node_modules", ".mypy_cache")]
        for f in files:
            if not f.endswith(".py"):
                continue
            p = os.path.join(akar, f)
            rel = os.path.relpath(p, ROOT)
            try:
                isi = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for m in RE_IMPOR.finditer(isi):
                modul = (m.group(1) or m.group(2) or "").split(".")[0]
                if not modul or modul in STANDAR_MINIMAL or modul in lokal:
                    continue
                pakai.setdefault(modul, []).append(rel)
    return pakai


def terpasang(nama: str) -> bool:
    try:
        __import__(nama)
        return True
    except Exception:  # noqa: BLE001
        return False


def baca_requirements() -> tuple[dict[str, str], dict[str, str]]:
    """(inti, opsional) — paket yang tercatat di requirements inti vs file lain."""
    inti: dict[str, str] = {}
    opsional: dict[str, str] = {}
    for nama in ("requirements.txt", "requirements-office.txt", "requirements-dev.txt"):
        path = os.path.join(ROOT, nama)
        if not os.path.isfile(path):
            continue
        target = inti if nama == "requirements.txt" else opsional
        for baris in open(path, encoding="utf-8"):
            b = baris.strip()
            if not b or b.startswith("#"):
                continue
            m = re.match(r"^([A-Za-z0-9_.\-]+)\s*(.*)$", b)
            if m:
                target[m.group(1).lower()] = m.group(2).strip()
    return inti, opsional


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", help="tulis laporan ke JSON")
    args = ap.parse_args()

    pakai = pindai()
    if not pakai:
        print("Tidak menemukan impor pihak ketiga.", file=sys.stderr)
        return 2

    inti, opsional = baca_requirements()
    hasil, kurang_inti, kurang_opsional, tak_terdaftar = [], [], [], []

    print(f"{'Modul':<14} {'Paket':<18} {'Terpasang':<10} {'Tercatat':<10} Berkas")
    print("-" * 92)
    for modul in sorted(pakai):
        paket = PETA.get(modul, modul)
        kunci = paket.lower()
        ada = terpasang(modul)
        tercatat = "inti" if kunci in inti else ("opsional" if kunci in opsional else "")
        hasil.append({"modul": modul, "paket": paket, "terpasang": ada,
                      "tercatat": tercatat, "dipakai_di": sorted(set(pakai[modul]))})
        if not ada:
            if tercatat == "inti":
                kurang_inti.append(paket)
            elif tercatat == "opsional":
                kurang_opsional.append(paket)
            else:
                kurang_inti.append(paket)
        if not tercatat:
            tak_terdaftar.append(paket)
        print(f"{modul:<14} {paket:<18} {'ya' if ada else 'TIDAK':<10} "
              f"{tercatat or 'TIDAK':<10} {len(set(pakai[modul]))} berkas")

    print()
    if kurang_inti:
        print(f"WAJIB tapi belum terpasang ({len(kurang_inti)}): {', '.join(sorted(set(kurang_inti)))}")
        print("  → .venv/bin/pip install -r requirements.txt")
    if kurang_opsional:
        print(f"OPSIONAL, belum terpasang ({len(kurang_opsional)}): "
              f"{', '.join(sorted(set(kurang_opsional)))}")
        print("  → hanya perlu bila memakai skills/office_word_files:")
        print("    .venv/bin/pip install -r requirements-office.txt")
    if tak_terdaftar:
        print(f"TIDAK TERCATAT di requirements mana pun ({len(tak_terdaftar)}): "
              f"{', '.join(sorted(set(tak_terdaftar)))}")
        print("  → tambahkan supaya orang lain tidak menemukan impor yang gagal")
    if not kurang_inti and not tak_terdaftar:
        print("Semua dependensi wajib tersedia dan tercatat.")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"dependensi": hasil,
                       "kurang_wajib": sorted(set(kurang_inti)),
                       "kurang_opsional": sorted(set(kurang_opsional)),
                       "tak_tercatat": sorted(set(tak_terdaftar))}, f,
                      ensure_ascii=False, indent=2)
        print(f"JSON: {args.json}")

    return 1 if (kurang_inti or tak_terdaftar) else 0


if __name__ == "__main__":
    sys.exit(main())
