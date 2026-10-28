#!/usr/bin/env python3
"""Uji mutu rumusan judul skripsi Indonesia.

Pemakaian:
    python3 judul_check.py 04_kandidat_judul.md --maks-kata 25 --bidang sistem_informasi

Membaca berkas markdown kandidat judul. Baris yang dianggap judul:
  - baris bernomor:  "1. Pengaruh X terhadap Y di Z"
  - baris berpoin:   "- Pengaruh X terhadap Y di Z"
  - baris setelah   "**Judul:** ..."

Yang diperiksa: panjang kata, jumlah verba penelitian, keberadaan lokus, lokus terlalu
luas, singkatan tidak baku, kata klaim hasil, kata mubazir, kecocokan verba dengan bidang,
dan kemiripan antar kandidat.

Kode keluar 1 bila ada galat (bukan sekadar peringatan).
"""
from __future__ import annotations

import argparse
import re
import sys

VERBA = [
    "pengaruh", "hubungan", "analisis", "rancang bangun", "perancangan", "pengembangan",
    "implementasi", "evaluasi", "optimasi", "perbandingan", "gambaran", "efektivitas",
    "tinjauan", "penerapan", "strategi", "makna", "representasi", "uji", "kelayakan",
    "identifikasi", "pemetaan", "prediksi", "klasifikasi", "sistem pendukung keputusan",
]

KLAIM = ["meningkatkan", "mengoptimalkan", "memperbaiki", "mengurangi", "mengatasi",
         "yang lebih baik", "yang efektif", "yang efisien"]

MUBAZIR = ["suatu", "yang mana", "di sini", "pada suatu", "terhadap suatu", "berbagai macam"]

SINGKATAN_BOLEH = {"spk", "uml", "iot", "api", "erp", "crm", "sop", "uu", "ai", "ml",
                   "nlp", "ocr", "gis", "ui", "ux", "sms", "pdf", "csv", "api", "rbac"}

LOKUS_LUAS = ["indonesia", "nasional", "jawa timur", "jawa barat", "jawa tengah",
              "seluruh", "semua provinsi"]

POLA_BIDANG = {
    "sistem_informasi": ["rancang bangun", "analisis", "pengembangan", "evaluasi",
                         "implementasi", "perancangan", "sistem pendukung keputusan"],
    "manajemen": ["pengaruh", "analisis", "hubungan", "strategi"],
    "akuntansi": ["pengaruh", "analisis", "hubungan"],
    "kesehatan": ["hubungan", "pengaruh", "gambaran", "efektivitas"],
    "hukum": ["tinjauan", "analisis", "penerapan", "perlindungan"],
    "pendidikan": ["pengaruh", "pengembangan", "peningkatan", "hubungan"],
    "teknik": ["perancangan", "optimasi", "analisis", "perbandingan"],
    "pertanian": ["pengaruh", "uji", "analisis", "kelayakan"],
}


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).strip()


def ambil_judul(teks: str) -> list[tuple[int, str]]:
    out, no = [], 0
    for i, baris in enumerate(teks.splitlines(), 1):
        b = baris.strip()
        m = re.match(r"^(?:\d+[.)]|[-*+])\s+(.{10,})$", b)
        if m:
            no += 1
            out.append((i, m.group(1).strip()))
            continue
        m = re.match(r"^\*\*Judul\s*:?\*\*\s*(.{10,})$", b, re.I)
        if m:
            no += 1
            out.append((i, m.group(1).strip()))
    return out


def cek(judul: str, maks: int, min_kata: int, bidang: str | None):
    galat, peringatan = [], []
    kata = judul.split()
    n = len(kata)

    if n > maks:
        galat.append(f"{n} kata > maks {maks}")
    if n < min_kata:
        galat.append(f"{n} kata < min {min_kata}")

    teks = " " + norm(judul) + " "
    ditemukan = [v for v in VERBA if f" {v} " in teks or teks.startswith(f" {v} ")]
    # 'sistem pendukung keputusan' menyerap 'pendukung'; buang duplikat tumpang tindih
    if "sistem pendukung keputusan" in ditemukan:
        ditemukan = [v for v in ditemukan if v not in ("analisis",) or
                     "analisis" in teks.split("sistem pendukung keputusan")[0]]
    if len(ditemukan) > 1:
        galat.append(f"{len(ditemukan)} verba penelitian: {', '.join(ditemukan)}")

    ada_lokus = bool(re.search(r"\b(pada|di|dalam)\b", teks))
    if not ada_lokus:
        galat.append("tanpa lokus (tidak ada 'pada/di/dalam')")
    else:
        for luas in LOKUS_LUAS:
            if f" {luas} " in teks:
                galat.append(f"lokus terlalu luas: '{luas}'")
                break

    for s in set(re.findall(r"\b([A-Z]{2,6})\b", judul)):
        if s.lower() not in SINGKATAN_BOLEH:
            peringatan.append(f"singkatan tidak baku: {s}")

    for k in KLAIM:
        if k in teks:
            peringatan.append(f"kata klaim hasil: '{k}'")

    for m in MUBAZIR:
        if f" {m} " in teks:
            peringatan.append(f"kata mubazir: '{m}'")

    if bidang:
        pola = POLA_BIDANG.get(bidang.lower())
        if pola and not any(p in teks for p in pola):
            peringatan.append(
                f"verba tidak cocok pola bidang '{bidang}' (lazim: {', '.join(pola[:3])})")
        elif not pola:
            peringatan.append(f"bidang '{bidang}' tidak dikenal, pola tidak diperiksa")

    if not re.search(r"\b(pengaruh|hubungan|analisis|rancang|perancangan|pengembangan|"
                     r"evaluasi|optimasi|perbandingan|gambaran|efektivitas|tinjauan|"
                     r"penerapan|strategi|makna|representasi|uji|kelayakan|identifikasi|"
                     r"pemetaan|prediksi|klasifikasi)\b", teks):
        galat.append("tidak ada verba penelitian yang dikenali")

    return galat, peringatan, n, ditemukan


def kemiripan(a: str, b: str) -> float:
    sa, sb = set(norm(a).split()), set(norm(b).split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("berkas")
    ap.add_argument("--maks-kata", type=int, default=25)
    ap.add_argument("--min-kata", type=int, default=10)
    ap.add_argument("--bidang", help="sistem_informasi|manajemen|kesehatan|hukum|...")
    args = ap.parse_args()

    try:
        teks = open(args.berkas, encoding="utf-8").read()
    except OSError as e:
        print(f"GAGAL membaca {args.berkas}: {e}", file=sys.stderr)
        return 2

    judul = ambil_judul(teks)
    if not judul:
        print("Tidak ada judul kandidat yang terdeteksi "
              "(format: '1. ...' atau '- ...' atau '**Judul:** ...').", file=sys.stderr)
        return 2

    total_galat = 0
    hasil = []
    for baris_no, j in judul:
        g, p, n, v = cek(j, args.maks_kata, args.min_kata, args.bidang)
        total_galat += len(g)
        hasil.append((baris_no, j, n, v, g, p))
        tanda = "GAGAL" if g else ("WARN " if p else "OK   ")
        print(f"\n[{tanda}] baris {baris_no} — {n} kata — verba: {', '.join(v) or '-'}")
        print(f"  {j}")
        for x in g:
            print(f"  ✗ {x}")
        for x in p:
            print(f"  ! {x}")

    print("\n" + "=" * 70)
    print("Kemiripan antar kandidat (Jaccard; ≥0,80 dianggap duplikat):")
    dup = 0
    for i in range(len(hasil)):
        for k in range(i + 1, len(hasil)):
            s = kemiripan(hasil[i][1], hasil[k][1])
            if s >= 0.80:
                dup += 1
                print(f"  DUPLIKAT {s:.2f} — baris {hasil[i][0]} vs {hasil[k][0]}")
            elif s >= 0.60:
                print(f"  mirip    {s:.2f} — baris {hasil[i][0]} vs {hasil[k][0]}")
    if not dup:
        print("  tidak ada duplikat")

    print("=" * 70)
    print(f"Total judul: {len(hasil)} | galat: {total_galat} | duplikat: {dup}")
    if total_galat:
        print("Perbaiki galat di atas sebelum judul diserahkan ke pembimbing.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
