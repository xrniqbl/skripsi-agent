#!/usr/bin/env python3
"""Cocokkan sitasi dalam teks dengan nomor entri Daftar Pustaka (gaya numerik).

Pemakaian:
    python3 periksa_sitasi_numerik.py naskah.md
    python3 periksa_sitasi_numerik.py Skripsi.docx --gaya ieee
    python3 periksa_sitasi_numerik.py naskah.md --json lap.json --ketat

Kenapa skrip ini ada: `periksa_pustaka.py` memeriksa BENTUK entri (abjad,
et al., usia terbitan). Ia tidak memeriksa apakah `[3]` di teks benar-benar
menunjuk entri ke-3 — padahal pada gaya numerik (IEEE/Vancouver) itulah
kesalahan yang paling merusak: pembaca membuka rujukan yang salah, dan
penguji langsung melihat daftar pustaka tidak sinkron.

Tiga pemeriksaan:

1. SETIAP NOMOR DIRUJUK. Entri yang tidak pernah disitasi = daftar pustaka
   berisi bacaan yang tidak dipakai (dosen menandainya).
2. SETIAP RUJUKAN ADA ENTRI. `[12]` pada daftar yang hanya berisi 9 entri.
3. URUTAN MUNCUL. Gaya IEEE mewajibkan nomor sitasi menaik sesuai kemunculan
   pertama; `[1] ... [4] ... [2]` berarti daftar pustaka tidak diurutkan
   ulang setelah naskah disunting.

Rentang (`[2]-[5]`, `[2,4,7]`, `[2-4]`) didukung. Gaya penulis-tahun (APA)
tidak diperiksa di sini — untuk itu `periksa_pustaka.py` yang berlaku.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

RE_SITASI = re.compile(r"\[([\d,\s\-–—]+)\]")
RE_ENTRI = re.compile(r"^\s*(?:\[(\d+)\]|(\d+)\.)\s+\S")


def baca(path: str) -> tuple[str, str]:
    """Kembalikan (teks_isi, teks_daftar_pustaka)."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            sys.exit("GAGAL: butuh python-docx")
        d = Document(path)
        semua = "\n".join(p.text for p in d.paragraphs)
    elif ext == ".pdf":
        import subprocess
        semua = subprocess.run(["pdftotext", "-layout", path, "-"],
                               capture_output=True, text=True).stdout
    else:
        semua = open(path, encoding="utf8", errors="replace").read()

    m = re.search(r"^\s*DAFTAR\s+PUSTAKA\s*$", semua, re.I | re.M)
    if not m:
        m = re.search(r"^\s*DAFTAR\s+RUJUKAN\s*$", semua, re.I | re.M)
    if not m:
        return semua, ""
    return semua[:m.start()], semua[m.end():]


def entri_daftar(teks_daftar: str) -> dict[int, str]:
    """{nomor: baris_entri} dari Daftar Pustaka bergaya numerik."""
    out: dict[int, str] = {}
    for baris in teks_daftar.splitlines():
        m = re.match(r"^\s*\[(\d+)\]\s*(.*)$", baris)
        if not m:
            m = re.match(r"^\s*(\d+)[.)]\s+(\S.*)$", baris)
        if m:
            out[int(m.group(1))] = m.group(2).strip()[:90]
    return out


def rentang_ke_nomor(isi: str) -> list[int]:
    """'2,4-6' -> [2,4,5,6]."""
    hasil: list[int] = []
    for bagian in re.split(r",", isi):
        bagian = bagian.strip()
        if not bagian:
            continue
        m = re.match(r"^(\d+)\s*[-–—]\s*(\d+)$", bagian)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a <= b:
                hasil.extend(range(a, b + 1))
            continue
        if bagian.isdigit():
            hasil.append(int(bagian))
    return hasil


def periksa(teks_isi: str, teks_daftar: str) -> dict:
    entri = entri_daftar(teks_daftar)
    urutan: list[tuple[int, int]] = []      # (nomor, posisi karakter)
    for m in RE_SITASI.finditer(teks_isi):
        for n in rentang_ke_nomor(m.group(1)):
            urutan.append((n, m.start()))

    disitasi = {n for n, _ in urutan}
    ada = set(entri)

    tanpa_entri = sorted(disitasi - ada)
    tanpa_sitasi = sorted(ada - disitasi) if ada else []

    # urutan kemunculan pertama harus menaik (IEEE)
    pertama: list[int] = []
    terlihat: set[int] = set()
    for n, _ in urutan:
        if n not in terlihat:
            terlihat.add(n)
            pertama.append(n)
    tidak_naik = [(i, pertama[i - 1], pertama[i])
                  for i in range(1, len(pertama)) if pertama[i] < pertama[i - 1]]

    return {
        "jumlah_entri": len(ada),
        "jumlah_sitasi": len(urutan),
        "nomor_unik": len(disitasi),
        "tanpa_entri": tanpa_entri,
        "tanpa_sitasi": tanpa_sitasi,
        "urutan_tidak_naik": tidak_naik,
        "entri": entri,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Cocokkan sitasi numerik [n] dengan entri Daftar Pustaka.")
    ap.add_argument("naskah")
    ap.add_argument("--gaya", default="ieee", choices=["ieee", "vancouver"],
                    help="keduanya mewajibkan urutan menaik")
    ap.add_argument("--json", help="tulis laporan JSON")
    ap.add_argument("--ketat", action="store_true")
    a = ap.parse_args()

    if not os.path.isfile(a.naskah):
        print(f"GAGAL: naskah tidak ada: {a.naskah}", file=sys.stderr)
        return 2
    isi, daftar = baca(a.naskah)
    if not daftar.strip():
        print("GAGAL: heading DAFTAR PUSTAKA tidak ditemukan", file=sys.stderr)
        return 2

    h = periksa(isi, daftar)
    print(f"=== Sitasi numerik vs Daftar Pustaka ({a.gaya.upper()}) ===")
    print(f"  entri daftar   : {h['jumlah_entri']}")
    print(f"  sitasi di teks : {h['jumlah_sitasi']} ({h['nomor_unik']} nomor unik)")

    gagal = 0
    if h["tanpa_entri"]:
        gagal += len(h["tanpa_entri"])
        print(f"  GALAT   {len(h['tanpa_entri'])} nomor disitasi tanpa entri: "
              f"{', '.join(f'[{n}]' for n in h['tanpa_entri'][:15])}")
    if h["tanpa_sitasi"]:
        gagal += len(h["tanpa_sitasi"])
        print(f"  GALAT   {len(h['tanpa_sitasi'])} entri tidak pernah disitasi: "
              f"{', '.join(f'[{n}]' for n in h['tanpa_sitasi'][:15])}")
        for n in h["tanpa_sitasi"][:5]:
            print(f"          [{n}] {h['entri'].get(n, '')[:70]}")
    if h["urutan_tidak_naik"]:
        gagal += len(h["urutan_tidak_naik"])
        print(f"  GALAT   urutan sitasi tidak menaik di "
              f"{len(h['urutan_tidak_naik'])} titik:")
        for i, sebelum, kini in h["urutan_tidak_naik"][:6]:
            print(f"          kemunculan ke-{i + 1}: [{sebelum}] lalu [{kini}]")
    if not gagal:
        print("  OK      semua rujukan cocok dan berurutan")

    if a.json:
        with open(a.json, "w", encoding="utf8") as f:
            json.dump({k: v for k, v in h.items() if k != "entri"},
                      f, ensure_ascii=False, indent=1)
    print(f"\nRingkasan: {gagal} galat")
    return 1 if (gagal and (a.ketat or h["tanpa_entri"])) else 0


if __name__ == "__main__":
    sys.exit(main())
