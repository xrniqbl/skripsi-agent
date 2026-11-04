#!/usr/bin/env python3
"""Periksa aturan pengutipan (kutipan langsung/tidak langsung/sumber lain).

Pemakaian:
    python3 periksa_kutipan.py naskah.md profil-kampus.yaml
    python3 periksa_kutipan.py skripsi.docx profil-kampus.yaml --json laporan.json

Aturan dibaca dari blok `kutipan:` profil. Profil tanpa blok itu = panduan tidak
mengaturnya: pemeriksa lulus dengan catatan, tidak menebak.

Yang diperiksa (PEMERIKSA POLA; panjang kutipan hanya PERKIRAAN dari jumlah kata,
karena jumlah baris baru pasti setelah dirender):
  1. Kutipan langsung bertanda kutip yang diperkirakan >= batas baris (default 5)
     seharusnya berupa blok tanpa tanda kutip.
  2. Kutipan blok (baris diawali ">" pada Markdown, atau paragraf bergaya
     Quote/Block Text pada DOCX) yang diperkirakan < batas seharusnya ikut paragraf
     dengan tanda kutip; dan blok yang tetap memakai tanda kutip dilaporkan.
  3. Kutipan langsung tanpa halaman: ("...") (Nama, Tahun) tanpa ":Halaman"
     bila profil memakai pemisah tahun:halaman.
  4. Kutipan dari sumber lain: "X dalam Y (Tahun:Hal)" harus memuat "dalam".
  5. "et al"/"dkk" pada sitasi dalam teks, menurut `kutipan.et_al_dalam_teks`
     (dilarang | boleh_tiga_atau_lebih | null=belum diketahui -> hanya catatan).

Kode keluar: 0 lulus; 1 ada galat; 2 berkas/profil tidak terbaca.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

KATA_PER_BARIS = 11  # TNR 12 pt, A4, margin 4/3 cm: ~11-13 kata/baris; konservatif


def baca(path: str) -> list[tuple[str, bool]]:
    """Kembalikan daftar (teks_paragraf, blok_kutipan)."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            sys.exit("GAGAL: butuh python-docx untuk membaca .docx")
        hasil = []
        for p in Document(path).paragraphs:
            if not p.text.strip():
                continue
            gaya = (p.style.name or "").lower()
            hasil.append((p.text.strip(), "quote" in gaya or "block" in gaya))
        return hasil
    if ext == ".pdf":
        import subprocess
        t = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True,
                           text=True).stdout
        return [(x.strip(), False) for x in re.split(r"\n\s*\n", t) if x.strip()]
    with open(path, encoding="utf-8", errors="replace") as f:
        hasil = []
        for baris in f:
            s = baris.strip()
            if not s:
                continue
            blok = s.startswith(">")
            hasil.append((s.lstrip("> ").strip() if blok else s, blok))
        return hasil


def kata(s: str) -> int:
    return len(re.findall(r"\w+", s))


RE_TANDA = re.compile(r"[\"“”]([^\"“”]{8,}?)[\"“”]")
RE_SITASI = re.compile(r"\(([^()]*?\d{4}[^()]*?)\)")
RE_DALAM = re.compile(r"\b(menurut|dikutip)\b[^.\n]{0,80}\b(dalam|dikutip dalam|in)\b", re.I)
RE_ETAL = re.compile(r"\((?:[^()]*?)\b(et\s+al\.?|dkk\.?)\b[^()]*\)|\b\w+\s+(?:et\s+al\.?|dkk\.?)\s*\(\d{4}", re.I)


def periksa(paragraf, aturan: dict, baris_batas: int):
    galat, peringatan, info = [], [], []
    pisah = str(aturan.get("pemisah_tahun_halaman") or "")
    batas_kata = baris_batas * KATA_PER_BARIS
    et = aturan.get("et_al_dalam_teks")
    n_langsung = 0

    for i, (teks, blok) in enumerate(paragraf, 1):
        if blok:
            n_langsung += 1
            n = kata(teks)
            if re.match(r"^[\"“]", teks):
                peringatan.append(f"par {i}: kutipan blok masih memakai tanda kutip "
                                  f"(kutipan >= {baris_batas} baris tanpa tanda kutip)")
            if n < batas_kata * 0.6:
                peringatan.append(f"par {i}: kutipan blok hanya ~{n} kata (< ~{baris_batas} "
                                  f"baris); kutipan pendek ikut paragraf dengan tanda kutip")
            continue
        for m in RE_TANDA.finditer(teks):
            n_langsung += 1
            n = kata(m.group(1))
            if n >= batas_kata:
                peringatan.append(f"par {i}: kutipan bertanda kutip ~{n} kata (>= ~{baris_batas} "
                                  f"baris) — jadikan blok tanpa tanda kutip, 1 spasi")
            # sitasi milik kutipan ini paling lazim SESUDAH kutipan; baru cari sebelumnya
            mm = RE_SITASI.search(teks[m.end(): m.end() + 60])
            if mm is None:
                sebelum = list(RE_SITASI.finditer(teks[max(0, m.start() - 60): m.start()]))
                mm = sebelum[-1] if sebelum else None
            if pisah and mm and pisah not in mm.group(1):
                peringatan.append(f"par {i}: kutipan langsung tanpa halaman "
                                  f"({mm.group(0)[:50]}) — format memakai '{pisah}Halaman'")
            elif pisah and not mm:
                peringatan.append(f"par {i}: kutipan langsung tanpa sitasi di dekatnya")
        if re.search(r"\bdikutip\s+(?:dari|oleh)\b|\bmengutip\s+dari\b", teks, re.I) \
                and not re.search(r"\bdalam\b", teks, re.I):
            peringatan.append(f"par {i}: kutipan dari sumber lain tanpa kata 'dalam' "
                              f"(pola: Menurut X dalam Y (Tahun:Hal))")
        if et == "dilarang" and RE_ETAL.search(teks):
            galat.append(f"par {i}: 'et al'/'dkk' pada sitasi dalam teks dilarang profil")
        elif et is None and RE_ETAL.search(teks):
            info.append(f"par {i}: 'et al'/'dkk' pada sitasi dalam teks — profil belum "
                        f"menetapkan (kutipan.et_al_dalam_teks); konfirmasi ke prodi")
    info.insert(0, f"{n_langsung} kutipan langsung terdeteksi (perkiraan pola)")
    return galat, peringatan, info


def main() -> int:
    ap = argparse.ArgumentParser(description="Periksa aturan pengutipan.")
    ap.add_argument("naskah")
    ap.add_argument("profil")
    ap.add_argument("--json")
    ap.add_argument("--ketat", action="store_true")
    a = ap.parse_args()
    if not os.path.isfile(a.naskah) or not os.path.isfile(a.profil):
        print("GAGAL: naskah/profil tidak ada", file=sys.stderr)
        return 2
    try:
        import yaml
        p = yaml.safe_load(open(a.profil, encoding="utf-8")) or {}
    except Exception as e:  # noqa: BLE001
        print(f"GAGAL: profil tidak terbaca: {e}", file=sys.stderr)
        return 2
    aturan = p.get("kutipan")
    if not aturan:
        print("  info       profil tidak punya blok `kutipan:` — panduan tidak mengaturnya, dilewati")
        print("\nRingkasan: 0 galat, 0 peringatan")
        return 0
    aturan = dict(aturan)
    aturan.setdefault("pemisah_tahun_halaman", (p.get("sitasi") or {}).get("pemisah_tahun_halaman"))
    batas = int(aturan.get("batas_baris_blok") or 5)
    galat, peringatan, info = periksa(baca(a.naskah), aturan, batas)
    for x in info: print(f"  info       {x}")
    for x in peringatan: print(f"  PERINGATAN {x}")
    for x in galat: print(f"  GALAT      {x}")
    print(f"\nRingkasan: {len(galat)} galat, {len(peringatan)} peringatan")
    print("Catatan: panjang kutipan diperkirakan dari jumlah kata; pastikan di hasil render.")
    if a.json:
        json.dump({"galat": galat, "peringatan": peringatan, "info": info},
                  open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return 1 if galat or (a.ketat and peringatan) else 0


if __name__ == "__main__":
    sys.exit(main())
