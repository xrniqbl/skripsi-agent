#!/usr/bin/env python3
"""
proposal_doctor.py — Pemeriksaan akhir naskah proposal sebelum dikumpulkan/diunduh.

Memeriksa satu paket proposal (folder atau berkas) dan melaporkan masalah yang
sering ditemukan pada draft: subbab wajib BAB I-III, penanda sumber yang menggantung,
placeholder yang belum diisi, daftar pustaka yang tidak dikenal, kolom dataset yang
disebut tetapi tidak ada, angka hard-coded tanpa sumber, dan sinkronisasi DOCX.

Usage:
    python3 proposal_doctor.py outputs/proposal.md [opsi]
    python3 proposal_doctor.py --dir outputs/
    python3 proposal_doctor.py outputs/proposal.md --dataset data/responden.csv \\
        --hasil-uji outputs/hasil_uji.json --docx outputs/proposal.docx --strict

Keluar: 0 bila bersih atau hanya peringatan; 1 bila ada galat (--strict).
"""

import argparse
import json
import os
import re
import sys

WAJIB_BAB = {
    "BAB I": [r"bab\s+i\b", r"pendahuluan"],
    "BAB II": [r"bab\s+ii\b", r"tinjauan\s+pustaka|landasan\s+teori|kajian\s+pustaka"],
    "BAB III": [r"bab\s+iii\b", r"metode\s+penelitian"],
}

WAJIB_BAB1 = {
    "latar belakang": r"latar\s+belakang",
    "rumusan masalah": r"rumusan\s+masalah",
    "tujuan penelitian": r"tujuan\s+penelitian",
    "manfaat penelitian": r"manfaat\s+penelitian",
    "batasan/ruang lingkup": r"batasan\s+masalah|ruas\s+lingkup",
}

WAJIB_BAB3 = {
    "desain penelitian": r"desain\s+penelitian|ragam\s+penelitian",
    "populasi dan sampel": r"populasi\s+dan\s+sampel|populasi\s+sampel",
    "teknik pengumpulan data": r"teknik\s+pengumpulan\s+data|instrumen",
    "teknik analisis data": r"teknik\s+analisis\s+data|metode\s+analisis\s+data",
}

PLACEHOLDER = re.compile(r"(TODO|TBD|FIXME|XXX+|\[\s*\]|\bisian\s+ini\b|"
                         r"\bplaceholder\b|\bLorem\s+ipsum\b|\bdummy\b)", re.I)
NARASI_NUM = re.compile(r"(r\s*=\s*[0-9]|p\s*[<=]\s*0?[\.,]|t\s*\(\s*\d+\s*\)\s*=|"
                        r"χ²?\s*=\s*[0-9]|F\(\s*\d+\s*,|R²\s*=)")
MARKER = re.compile(r"\[(L-\d+|D:[^\]]+|U|P-\d+|R-\d+|PR-\d+)\]")
HEADING = re.compile(r"^(#{1,4})\s+(.+)$", re.M)


def kata_terhitung(teks):
    return len(re.findall(r"[A-Za-z0-9À-ÿ]+", teks))


def periksa(teks, nama, dataset_kolom=None, hasil_uji=None, tolerate=None):
    issues = []

    def cat(level, kode, pesan, saran=""):
        issues.append({"level": level, "kode": kode, "pesan": pesan, "saran": saran,
                       "berkas": nama})

    # 1) placeholder
    for m in PLACEHOLDER.finditer(teks):
        no_baris = teks[: m.start()].count("\n") + 1
        cat("galat", "placeholder",
            f"Placeholder tersisa: '{m.group(0).strip()}' (baris {no_baris})",
            "Ganti dengan isi sebenarnya atau hapus.")

    # 2) struktur bab
    rendah = teks.lower()
    for bab, pola in WAJIB_BAB.items():
        if not re.search(pola[0], rendah):
            cat("galat", "struktur_bab", f"Judul '{bab}' tidak ditemukan.",
                "Proposal wajib memuat BAB I, BAB II, dan BAB III.")
    for bagian, pola in WAJIB_BAB1.items():
        if not re.search(pola, rendah):
            cat("galat", "struktur_bab1", f"Subbab '{bagian}' tidak ditemukan.",
                f"Tambahkan subbab '{bagian.title()}'.")
    for bagian, pola in WAJIB_BAB3.items():
        if not re.search(pola, rendah):
            cat("galat", "struktur_bab3", f"Subbab '{bagian}' tidak ditemukan.",
                f"Tambahkan subbab '{bagian.title()}'.")

    # 3) penanda sumber
    daftar = None
    m_daftar = re.search(r"^#*\s*daftar\s+pustaka|^#*\s*daftar\s+referensi|^#*\s*references",
                         teks, re.I | re.M)
    if m_daftar:
        daftar = teks[m_daftar.start():]
    marker = set(MARKER.findall(teks))
    p_daftar = set(MARKER.findall(daftar or ""))
    if daftar is not None:
        for m in sorted(marker - p_daftar):
            if m.startswith("L-") or m.startswith("P-"):
                cat("galat", "marker_dangling",
                    f"Penanda [{m}] dipakai di naskah tetapi tidak ada di Daftar Pustaka.",
                    "Tambahkan entri yang sesuai atau ubah menjadi uraian tanpa penanda.")
    else:
        cat("peringatan", "daftar_pustaka", "Daftar Pustaka tidak ditemukan.",
            "Tambahkan daftar pustaka; tanpa itu penanda [L-n] menggantung.")
    for m in sorted(marker):
        if m.startswith("D:") and dataset_kolom and m[2:] not in dataset_kolom:
            cat("galat", "marker_data",
                f"Penanda [{m}] merujuk kolom yang tidak ada pada dataset.",
                f"Kolom tersedia: {', '.join(sorted(dataset_kolom)[:10])}")

    # 4) angka statistik tanpa sumber
    for m in NARASI_NUM.finditer(teks):
        awal = max(0, m.start() - 260)
        konteks = teks[awal:m.start()]
        if not (MARKER.search(konteks) or "hasil_uji" in konteks
                        or re.search(r"tabel\s+\d|hasil\s+analisis|pengujian", konteks, re.I)):
            no_baris = teks[: m.start()].count("\n") + 1
            cat("peringatan", "angka_tanpa_sumber",
                f"Angka statistik ({m.group(0).strip()}) tanpa penanda sumber (baris {no_baris})",
                "Tambahkan [D:kolom] atau rujukan tabel hasil uji.")

    # 5) panjang naskah
    total = kata_terhitung(teks)
    if total < 1500:
        cat("peringatan", "panjang", f"Naskah hanya {total} kata.",
            "Proposal umumnya jauh lebih panjang; pastikan lengkap.")
    else:
        print(f"INFO: panjang naskah {total} kata", file=sys.stderr)

    # 6) konsistensi hasil uji
    if hasil_uji:
        try:
            with open(hasil_uji, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as exc:
            cat("peringatan", "hasil_uji", f"Tidak dapat membaca {hasil_uji}: {exc}")
            data = None
        if data:
            for hasil in data.get("hasil", []):
                p = hasil.get("p")
                if p is None:
                    continue
                if p < 0.05 and hasil.get("keputusan", "").startswith("tidak"):
                    cat("galat", "hasil_uji_konsisten",
                        f"Keputusan bertentangan dengan p = {p} pada {hasil.get('test')}.")
                kunci = f"{hasil.get('test')}"
                if hasil.get("n") and str(hasil["n"]) not in teks and len(teks) < 40000:
                    cat("peringatan", "hasil_uji_dikutip",
                        f"n = {hasil['n']} dari uji '{kunci}' tidak muncul di naskah.",
                        "Pastikan tabel hasil uji benar-benar dilampirkan atau dikutip.")

    # 7) berkas pendamping
    if tolerate:
        for wajib in tolerate:
            if not os.path.exists(wajib):
                cat("peringatan", "berkas", f"Berkas pendamping tidak ditemukan: {wajib}")

    return issues


def main():
    ap = argparse.ArgumentParser(description="Pemeriksaan akhir paket proposal")
    ap.add_argument("naskah", help="berkas proposal .md (atau --dir)")
    ap.add_argument("--dir", action="store_true", help="periksa proposal.md dalam direktori")
    ap.add_argument("--dataset", help="CSV/TSV untuk validasi penanda [D:kolom]")
    ap.add_argument("--hasil-uji", help="hasil_uji.json dari stats_tests.py")
    ap.add_argument("--docx", help="berkas DOCX untuk dicek sinkronnya")
    ap.add_argument("--harus-ada", action="append", default=[],
                    help="berkas pendukung yang wajib ada (bisa diulang)")
    ap.add_argument("--json", help="tulis laporan JSON")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    naskah = args.naskah
    if args.dir:
        naskah = os.path.join(args.naskah, "proposal.md")
    if not os.path.exists(naskah):
        sys.exit(f"ERROR: naskah tidak ditemukan: {naskah}")

    with open(naskah, "r", encoding="utf-8", errors="replace") as fh:
        teks = fh.read()

    dataset_kolom = None
    if args.dataset:
        import csv
        with open(args.dataset, "r", encoding="utf-8-sig", errors="replace") as fh:
            sniff = fh.readline()
            delim = ";" if sniff.count(";") > sniff.count(",") else ","
            fh.seek(0)
            dataset_kolom = [h.strip() for h in fh.readline().strip().split(delim)]

    wajib_ada = list(args.harus_ada)
    if args.docx:
        wajib_ada.append(args.docx)

    issues = periksa(teks, os.path.basename(naskah), dataset_kolom,
                     args.hasil_uji, wajib_ada)

    if args.docx and os.path.exists(args.docx):
        if os.path.getmtime(args.docx) < os.path.getmtime(naskah):
            issues.append({"level": "peringatan", "kode": "docx_kuno",
                           "pesan": "DOCX lebih tua dari naskah Markdown.",
                           "saran": "Jalankan build_docx.sh lagi.",
                           "berkas": os.path.basename(args.docx)})

    galat = [i for i in issues if i["level"] == "galat"]
    peringatan = [i for i in issues if i["level"] == "peringatan"]

    for i in issues:
        tanda = "GALAT" if i["level"] == "galat" else "WARN"
        print(f"[{tanda}] {i['kode']}: {i['pesan']}")
        if i["saran"]:
            print(f"        -> {i['saran']}")

    print(f"\nRingkasan: {len(galat)} galat, {len(peringatan)} peringatan "
          f"pada {naskah}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"naskah": naskah, "galat": len(galat),
                       "peringatan": len(peringatan), "issues": issues},
                      fh, ensure_ascii=False, indent=2)
        print(f"Tulis: {args.json}", file=sys.stderr)
    return 1 if (args.strict and galat) else 0


if __name__ == "__main__":
    sys.exit(main())
