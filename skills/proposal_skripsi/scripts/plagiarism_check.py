#!/usr/bin/env python3
"""
plagiarism_check.py — Deteksi tumpang tindih teks pada naskah proposal.

Menyediakan dua pemeriksaan yang bisa dilakukan tanpa alat berbayar:

  1. --internal  duplikasi DALAM naskah sendiri. Kalimat yang sama diulang
                 antar-bab hampir selalu gejala drafting berulang atau
                 copy-paste dari sumber yang belum dibersihkan.

  2. --sumber    perbandingan naskah dengan berkas sumber di folder
                 (hasil ekstraksi ingest_sources.sh, atau .md/.txt/.tex).
                 Menandai frasa identik >= N kata berurutan.

Setiap tumpang tindih adalah **sinyal**, bukan bukti. Selalu verifikasi manual.

Rantai kata (shingle) sepanjang N kata dipakai sebagai unit pencocokan, sehingga
frasa yang disalin utuh terdeteksi meski dipindah ke paragraf atau bab lain.
Heading, tabel markdown, dan blok kode dikeluarkan supaya yang dihitung hanya
isi naskah.

Usage:
    python3 plagiarism_check.py naskah.md --internal
    python3 plagiarism_check.py naskah.md --sumber .cache_ekstrak/
    python3 plagiarism_check.py proposal.md --sumber ./sumber --min-kata 7
    python3 plagiarism_check.py proposal.md --sumber ./sumber \\
        --md plagiarism_report.md --json plagiarism_report.json --strict

Opsi:
    --internal       cek duplikasi dalam naskah sendiri
    --sumber FOLDER  bandingkan dengan seluruh berkas sumber di folder
    --min-kata N     panjang shingle minimum (default 7)
    --md PATH        tulis laporan Markdown
    --json PATH      tulis laporan JSON
    --strict         keluar dengan kode 1 bila ada temuan

"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict

AMBANG_DEFAULT = 7
EKSTENSI_SUMBER = (".txt", ".md", ".tex", ".rst")

_BLOK_L5 = re.compile(r"^[ \t]{0,3}(#{1,6}\s|==+[ \t]*$|L\d+[:.\-]\s)", re.M)
_TABEL_MD = re.compile(r"^\s*\|.*\|\s*$", re.M)
_KOMENTAR_HTML = re.compile(r"<!--.*?-->", re.S)
_MARKER = re.compile(r"\[(L-\d+|D:[^\]]+|K-\d+|U|P-\d+|R-\d+|PR-\d+)\]")
_KATA = re.compile(r"[a-z0-9]+")


# ------------------------------------------------------------- normalisasi

def bersihkan(teks):
    """Normalisasi naskah menjadi (kata, peta_baris, batas).

    - `kata`     : daftar kata kecil yang menjadi bahan shingles
    - `peta_baris`: baris asal tiap kata, untuk laporan
    - `batas`    : indeks kata yang memotong fragmen (heading, tabel, baris kosong)

    Heading, tabel markdown, dan blok kode dikeluarkan dari korpus. Batas
    diperlukan karena dua bab boleh memuat kalimat identik tanpa itu berarti
    plagiarisme, jadi fragmen tidak boleh melintasi batas bab.
    """
    teks = _KOMENTAR_HTML.sub(" ", teks)
    kata, peta_baris, batas = [], [], []
    dalam_kode = False
    for nomor, baris in enumerate(teks.split("\n"), 1):
        if baris.lstrip().startswith("```"):
            dalam_kode = not dalam_kode
            batas.append(len(kata))
            continue
        if dalam_kode or not baris.strip():
            batas.append(len(kata))
            continue
        if _BLOK_L5.match(baris) or _TABEL_MD.match(baris):
            batas.append(len(kata))
            continue
        for k in _KATA.findall(_MARKER.sub(" ", baris).lower()):
            kata.append(k)
            peta_baris.append(nomor)
    batas.append(len(kata))
    return kata, peta_baris, batas


def shingles(kata, n):
    """Set shingles sepanjang n kata."""
    if len(kata) < n:
        return set()
    return {" ".join(kata[i:i + n]) for i in range(len(kata) - n + 1)}


def rentang_kemunculan(kata, n, target):
    """Rentang [mulai, selesai] untuk tiap kemunculan shingle `target`."""
    hasil = []
    for i in range(len(kata) - n + 1):
        if kata[i:i + n] == target:
            hasil.append((i, i + n - 1))
    return hasil


def gabung_rentang(rentang, batas=()):
    """Gabungkan rentang bertumpuk/sesinggung, tanpa melintasi `batas`."""
    batas = sorted(batas)
    gabung = []
    for mulai, selesai in sorted(rentang):
        potong = [m for m in batas if mulai < m <= selesai]
        if potong:
            awal = mulai
            for m in potong:
                if m > awal:
                    gabung.append((awal, m - 1))
                awal = max(awal, m)
            gabung.append((awal, selesai))
            continue
        if gabung and gabung[-1][1] + 1 >= mulai and not any(
            gabung[-1][1] < m <= mulai for m in batas
        ):
            gabung[-1][1] = max(gabung[-1][1], selesai)
        else:
            gabung.append([mulai, selesai])
    return [tuple(r) for r in gabung]


# ---------------------------------------------------------- perbandingan

def bandingkan(kata_a, baris_a, batas_a, shingle_a, kata_b, shingle_b, n, label_b):
    """Tumpang tindih antara naskah dan satu corpus sumber."""
    rentang = []
    for sh in sorted(shingle_a & shingle_b):
        rentang += rentang_kemunculan(kata_a, n, sh.split())
    hasil = []
    for mulai, selesai in gabung_rentang(rentang, batas_a):
        hasil.append({
            "baris": baris_a[mulai],
            "sumber": label_b,
            "frasa": " ".join(kata_a[mulai:selesai + 1]),
            "kata": selesai - mulai + 1,
        })
    return hasil


def muat_sumber(folder, n=AMBANG_DEFAULT, ekstensi=EKSTENSI_SUMBER):
    """Kumpulkan (label, kata, peta_baris, batas, shingle) dari folder sumber."""
    corpus = []
    for root, _, files in os.walk(folder):
        for nama in sorted(files):
            if not nama.lower().endswith(ekstensi):
                continue
            path = os.path.join(root, nama)
            label = os.path.relpath(path, folder)
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    teks = fh.read()
            except OSError:
                continue
            if len(teks) < 200:
                continue
            kata, peta_baris, batas = bersihkan(teks)
            corpus.append((label, kata, peta_baris, batas, shingles(kata, n)))
    return corpus


def cek_internal(kata, peta_baris, batas, n):
    """Cari frasa yang terulang di dalam naskah, lalu gabungkan yang bertumpuk.

    Duplikasi antar-bab hampir selalu gejala drafting berulang atau copy-paste
    dari sumber yang belum dibersihkan.
    """
    posisi = defaultdict(list)
    for i in range(len(kata) - n + 1):
        posisi[" ".join(kata[i:i + n])].append(i)

    rentang = []
    for _, daftar in posisi.items():
        if len(daftar) < 2:
            continue
        for p in daftar:
            rentang.append((p, p + n - 1))

    hasil = []
    for mulai, selesai in gabung_rentang(rentang, batas):
        baris_terkait = sorted({peta_baris[p] for p in range(mulai, selesai + 1)})
        hasil.append({
            "baris": baris_terkait[0],
            "baris_lain": baris_terkait[1:],
            "sumber": "(naskah sendiri)",
            "frasa": " ".join(kata[mulai:selesai + 1]),
            "kata": selesai - mulai + 1,
        })
    return hasil


# ------------------------------------------------------------- laporan

def ke_markdown(laporan, nama):
    out = [f"# Laporan Pemeriksaan Plagiarisme — {nama}", ""]
    if not laporan["temuan"]:
        out.append("Tidak ada tumpang tindih yang terdeteksi oleh pola otomatis.")
        out.append("")
        out.append("> Skor 0 bukan berarti bebas plagiarisme. Uji parafrase dan verifikasi")
        out.append("> sitasi tetap dilakukan manusia (lihat `references/plagiarism-check.md`).")
        return "\n".join(out)

    out.append(f"Temuannya: **{len(laporan['temuan'])}** "
               f"(tier {laporan['min_kata']} kata berurutan)")
    out.append("")
    out.append(f"Perkiraan tingkat tumpang tindih: **{laporan['tingkat']}%** "
               f"({laporan['kalimat_tumpang']}/{laporan['total_kalimat']} kalimat)")
    out.append("")
    out.append("| Baris | Sumber | Panjang | Cuplikan |")
    out.append("|-------|--------|---------|----------|")
    for t in laporan["temuan"][:200]:
        out.append(f"| {t['baris']} | {t['sumber']} | {t['kata']} | "
                   f"{t['frasa'][:70]} |")
    if len(laporan["temuan"]) > 200:
        out.append(f"| ... | | | {len(laporan['temuan']) - 200} temuan lain |")
    out.append("")
    out.append("> Setiap temuan adalah **sinyal**, bukan bukti plagiarisme. Frasa yang")
    out.append("> panjang dalam metode (mis. nama instrumen atau definisi baku) sering")
    out.append("> false positive. Periksa setiap baris secara manual sebelum bertindak.")
    return "\n".join(out)


def hitung_kalimat(kata):
    return max(1, len(kata) // 12)


def main():
    ap = argparse.ArgumentParser(description="Deteksi tumpang tindih teks pada proposal")
    ap.add_argument("naskah", help="berkas proposal .md")
    ap.add_argument("--internal", action="store_true",
                    help="cek duplikasi dalam naskah sendiri")
    ap.add_argument("--sumber", help="folder berkas sumber untuk perbandingan")
    ap.add_argument("--min-kata", type=int, default=AMBANG_DEFAULT,
                    help=f"panjang shingle minimum (default {AMBANG_DEFAULT})")
    ap.add_argument("--md")
    ap.add_argument("--json")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.naskah):
        sys.exit(f"ERROR: berkas tidak ditemukan: {args.naskah}")
    if not args.internal and not args.sumber:
        ap.error("pilih --internal dan/atau --sumber")

    n = args.min_kata
    with open(args.naskah, "r", encoding="utf-8", errors="replace") as fh:
        teks = fh.read()
    kata, peta_baris, batas = bersihkan(teks)
    sh_naskah = shingles(kata, n)

    temuan = []
    if args.internal:
        temuan += cek_internal(kata, peta_baris, batas, n)

    if args.sumber:
        if not os.path.isdir(args.sumber):
            sys.exit(f"ERROR: folder sumber tidak ditemukan: {args.sumber}")
        corpus = muat_sumber(args.sumber, n)
        if not corpus:
            print(f"INFO: tidak ada berkas sumber yang terbaca di {args.sumber}",
                  file=sys.stderr)
        for label, kata_b, _baris_b, _batas_b, sh_b in corpus:
            temuan += bandingkan(kata, peta_baris, batas, sh_naskah,
                                 kata_b, sh_b, n, label)

    baris_tertangkap = {t["baris"] for t in temuan}
    laporan = {
        "naskah": args.naskah,
        "sumber": args.sumber,
        "internal": bool(args.internal),
        "min_kata": n,
        "total_kalimat": hitung_kalimat(kata),
        "kalimat_tumpang": len(baris_tertangkap),
        "tingkat": round(100.0 * len(baris_tertangkap) / hitung_kalimat(kata), 1)
        if temuan else 0.0,
        "temuan": temuan,
    }

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(laporan, fh, ensure_ascii=False, indent=2)
        print(f"Tulis: {args.json}", file=sys.stderr)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as fh:
            fh.write(ke_markdown(laporan, os.path.basename(args.naskah)))
        print(f"Tulis: {args.md}", file=sys.stderr)

    if not temuan:
        print("Tidak ada tumpang tindih terdeteksi.")
        print("Uji parafrase dan verifikasi sitasi tetap wajib (lihat referensi).")
        return 0

    print(f"{len(temuan)} tumpang tindih terdeteksi "
          f"(shingle {n} kata, tingkat {laporan['tingkat']}%)")
    for t in temuan[:10]:
        print(f"  baris {t['baris']:>4}  {t['sumber'][:28]:<28}  {t['frasa'][:50]}")
    if len(temuan) > 10:
        print(f"  ... {len(temuan) - 10} temuan lain")
    print("Setiap temuan adalah sinyal. Verifikasi manual sebelum bertindak.")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
