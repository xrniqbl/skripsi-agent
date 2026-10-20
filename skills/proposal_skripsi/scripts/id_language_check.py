#!/usr/bin/env python3
"""
id_language_check.py — Pemeriksa gaya bahasa Indonesia untuk naskah proposal.

Menandai (bukan menghapus) hal yang perlu diperbaiki manusia:
  * kata serapan asing yang lebih lazim berbahasa Indonesia
  * tanda baca dan kapitalisasi
  * kalimat terlalu panjang / terlalu banyak konjungsi
  * angka desimal,koma dan ribuan titik
  * istilahbahasa Inggris yang tak perlu
  * karakter non-Latin yang mencurigakan
  * penanda sumber yang tidak terdefinisi
  * struktur BAB I (rumusan masalah, tujuan, manfaat, batasan)

Usage:
    python3 id_language_check.py naskah.md [naskah2.md ...] [opsi]
    python3 id_language_check.py --dokumen hasil.json          # dari stats_tests.py
    python3 id_language_check.py --dir outputs/ --strict

Opsi:
    --json PATH     tulis laporan JSON
    --md PATH       tulis laporan Markdown
    --struktur      cek struktur BAB I
    --strict        keluar dengan kode 1 bila ada temuan
    --ignore KODE   abaikan kategori temuan (bisa diulang)
    --max-kalimat N batas kata per kalimat (default 30)
"""

import argparse
import json
import os
import re
import sys

# ------------------------------------------------------------ kamus & pola

SERAPAN = {
    "improvement": "peningkatan", "performance": "kinerja", "motivation": "motivasi",
    "competence": "kompetensi", "quality": "mutu", "achievement": "prestasi",
    "employee": "karyawan", "staff": "staf", "customer": "pelanggan",
    "strategy": "strategi", "system": "sistem", "method": "metode",
    "analysis": "analisis", "data": "data", "sample": "sampel",
    "significant": "signifikan", "trend": "tren", "feedback": "umpan balik",
    "teamwork": "kerja sama", "leadership": "kepemimpinan", "training": "pelatihan",
    "workshop": "lokakarya", "research": "riset", "survey": "survei",
    "report": "laporan", "meeting": "pertemuan", "deadline": "tenggat",
    "kpi": "indikator kinerja", "kpi_": "indikator kinerja", "workflow": "alur kerja",
    "benchmark": "pembanding", "input": "masukan", "output": "keluaran",
    "problem solving": "pemecahan masalah", "decision making": "pengambilan keputusan",
    "job satisfaction": "kepuasan kerja", "workload": "beban kerja",
    "turnover": "pergantian karyawan", "efficiency": "efisiensi", "effectiveness": "efektivitas",
}

KALIMAT_PANJANG = 30
PARA_PANJANG = 120
KONJUNGSI = {"dan", "atau", "tetapi", "namun", "melainkan", "sedangkan", "padahal",
             "karena", "sehingga", "oleh karena itu", "sehingga", "maka"}

# Kata non-baku. Rujukan: KBBI dan EYD (Permendikbudristek 18/2022).
TIDAK_BAKU = {
    "analisa": "analisis", "apotik": "apotek", "managemen": "manajemen",
    "managier": "manajer", "hakekat": "hakikat", "kwality": "mutu",
    "kwantitatif": "kuantitatif", "kwalitatif": "kualitatif", "nasehat": "nasihat",
    "sistim": "sistem", "tehnologi": "teknologi", "ekstrimitas": "ekstremitas",
    "komplek": "kompleks", "aktifis": "aktivis", "mempunyai": "memiliki",
    "merubah": "mengubah", "merubahnya": "mengubahnya", "prosentase": "persentase",
    "standarisasi": "standardisasi", "difinisi": "definisi", "kwalifikasi": "kualifikasi",
}

# Partikel dan kata tanya yang lazim ditulis salah di naskah akademik.
PARTIKEL_TIDAK_BAKU = {
    "dimana": "di mana", "kemana": "ke mana", "kenapa": "mengapa",
    "gimana": "bagaimana", "dikarnakan": "karena", "guna untuk": "untuk",
}

# Rumus kabur: pengulangan makna yang tidak menambah informasi.
RUMUS_KABUR = [
    (r"adalah\s+merupakan", "adalah", "Rumus 'adalah merupakan' tidak menambah makna."),
    (r"dapat\s+dipakai\s+untuk", "dipakai untuk",
     "Gunakan 'dipakai untuk', bukan 'dapat digunakan untuk'."),
    (r"dapat\s+digunakan\s+untuk", "digunakan untuk",
     "Gunakan 'digunakan untuk', bukan 'dapat digunakan untuk'."),
    (r"untuk\s+dapat", "untuk", "Hindari 'untuk dapat'; gunakan bentuk langsung."),
    (r"sudah\s+lama", "sudah lama", "Rapis kata: 'sudah lama' satu kata."),
    (r"tidak\s+sama", "tidak sama", "Rapis kata: 'tidak sama' satu kata."),
    (r"adalah\s+yang", "adalah", "Hindari 'adalah yang'; gunting kata 'adalah'."),
    (r"terhadap\s+terhadap", "terhadap", "Kata 'terhadap' ganda; salah ketik."),
]

NON_LATIN = re.compile(r"[\u0400-\u04ff\u0370-\u03ff\u4e00-\u9fff\u3040-\u30ff"
                       r"\u0600-\u06ff\uac00-\ud7af]")
MARKER = re.compile(r"\[(L-\d+|D:[^\]]+|U|P-\d+|R-\d+|PR-\d+)\]")
PENANDA_BARU = re.compile(r"\((inferensi|inference|kutipan|quote)\)", re.I)
DEKIMAL_KOMA = re.compile(r"(?<![\d])\d+\.\d+(?![\d])")
KALIMAT = re.compile(r"[^.!?\n]+[.!?]")

KODE = {
    "serapan": "Kata asing yang lebih lazim berbahasa Indonesia",
    "kalimat_panjang": "Kalimat terlalu panjang",
    "para_panjang": "Paragraf terlalu panjang",
    "konjungsi": "Terlalu banyak konjungsi dalam satu kalimat",
    "desimal": "Gunakan koma sebagai pemisah desimal",
    "non_latin": "Karakter non-Latin yang mencurigakan",
    "marker": "Penanda sumber tidak terdefinisi atau tidak lengkap",
    "kapital": "Kapitalisasi setelah titik",
    "spasi": "Spasi ganda atau spasi sebelum tanda baca",
    "struktur": "Elemen struktur proposal tidak ditemukan",
    "terminologi": "Istilah teknis perlu dicantumkan di glosarium",
    "penanda_baru": "Penanda epistemic tidak konsisten dengan konvensi skill",
    "baku": "Kata tidak baku menurut KBBI",
    "partikel": "Partikel atau kata tanya yang salah tulis",
    "rumus_kabur": "Rumus kalimat kabur yang tidak menambah makna",
}


def baca_teks(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def cek_teks(teks, path="<stdin>", max_kalimat=KALIMAT_PANJANG,
             marker_terdefinis=None, cek_struktur=False):
    temuan = []
    baris = teks.split("\n")

    def tambah(kode, nomor, pesan, saran=""):
        temuan.append({"kode": kode, "baris": nomor, "pesan": pesan,
                       "saran": saran, "berkas": path,
                       "keterangan": KODE.get(kode, "")})

    # karakter non-Latin
    for i, l in enumerate(baris, 1):
        if NON_LATIN.search(l):
            karakter = sorted(set(NON_LATIN.findall(l)))
            tambah("non_latin", i, "Karakter non-Latin: " + " ".join(karakter[:5]),
                   "Periksa apakah teks terotorisasi atau salah tempel.")

    # spasi & kapitalisasi
    for i, l in enumerate(baris, 1):
        if re.search(r"\S  +\S", l):
            tambah("spasi", i, "Spasi ganda di tengah baris.", "Gunakan satu spasi.")
        if re.search(r"\s+[,.;:]", l):
            tambah("spasi", i, "Spasi sebelum tanda baca.", "Hapus spasi sebelum tanda baca.")
        if re.match(r"^\s*[a-z]", l) and not re.match(r"^\s*(#|[-*+>|\d])", l):
            tambah("kapital", i, "Baris diawali huruf kecil.", "Kapitalkan awal baris.")

    # desimal
    for i, l in enumerate(baris, 1):
        for m in DEKIMAL_KOMA.finditer(l):
            tambah("desimal", i, f"Desimal memakai titik: {m.group(0)}",
                   "Gunakan koma, misalnya 3,45. Untuk ribuan tetap memakai titik.")

    # kata asing
    kata_ditemukan = {}
    for i, l in enumerate(baris, 1):
        for kata in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", l):
            k = kata.lower()
            if k in SERAPAN:
                kata_ditemukan.setdefault(k, []).append(i)
    for k, baris_ditemukan in sorted(kata_ditemukan.items()):
        tambah("serapan", baris_ditemukan[0],
               f"'{k}' muncul {len(baris_ditemukan)} kali (baris {', '.join(map(str, baris_ditemukan[:5]))})",
               f"Pertimbangkan padanan: {SERAPAN[k]}.")

    # EYD: kata non-baku
    for i, l in enumerate(baris, 1):
        rendah = l.lower()
        for salah, benar in TIDAK_BAKU.items():
            if re.search(rf"\b{re.escape(salah)}\b", rendah):
                tambah("baku", i, f"'{salah}' tidak baku.", f"Tulis '{benar}' (KBBI).")

    # EYD: partikel dan kata tanya
    for i, l in enumerate(baris, 1):
        rendah = l.lower()
        for salah, benar in PARTIKEL_TIDAK_BAKU.items():
            if re.search(rf"\b{re.escape(salah)}\b", rendah):
                tambah("partikel", i, f"'{salah}' tidak baku.",
                       f"Tulis '{benar}'.")

    # EYD: rumus kabur
    for i, l in enumerate(baris, 1):
        for pola, ganti, pesan in RUMUS_KABUR:
            for m in re.finditer(pola, l, re.I):
                tambah("rumus_kabur", i,
                       f"'{m.group(0).strip()}' — {pesan}",
                       f"Pertimbangkan '{ganti}'.")

    # kalimat panjang & konjungsi
    for i, l in enumerate(baris, 1):
        if l.strip().startswith(("|", "#", "-", "*", ">")) or not l.strip():
            continue
        for m in KALIMAT.finditer(l):
            kata = re.findall(r"[A-Za-zÀ-ÿ]+", m.group(0))
            n = len(kata)
            if n > max_kalimat:
                tambah("kalimat_panjang", i,
                       f"Kalimat {n} kata (batas {max_kalimat}).",
                       "Pecah menjadi dua kalimat atau gunakan tanda baca yang lebih jelas.")
            k_used = [k for k in kata if k.lower() in KONJUNGSI]
            if len(k_used) >= 4:
                tambah("konjungsi", i,
                       f"Konjungsi berulang: {', '.join(k_used[:5])}.",
                       "Gunakan tanda baca atau pecah kalimat.")

    # paragraf
    if cek_struktur:
        blok = re.split(r"\n\s*\n", teks)
        for i, b in enumerate(blok, 1):
            kata = re.findall(r"[A-Za-zÀ-ÿ]+", b)
            if len(kata) > 400:
                tambah("para_panjang", 1,
                       f"Paragraf {len(kata)} kata.", "Pecah paragraf agar mudah dibaca.")

    # marker sumber
    semua_marker = set(MARKER.findall(teks))
    if marker_terdefinis is not None:
        tak_terdefinisi = sorted(semua_marker - set(marker_terdefinis))
        if tak_terdefinisi:
            tambah("marker", 1,
                   "Penanda sumber tak terdefinisi: " + ", ".join(tak_terdefinisi),
                   "Tambahkan sumber di daftar rujukan atau ubah menjadi uraian biasa.")
    if not semua_marker and len(re.findall(r"[A-Za-zÀ-ÿ]{3,}", teks)) > 200:
        tambah("marker", 1, "Naskah panjang tanpa penanda sumber.",
               "Tambahkan penanda [L-n], [U], [P-n] pada klaim empiris.")
    for m in PENANDA_BARU.finditer(teks):
        tambah("penanda_baru", teks[: m.start()].count("\n") + 1,
               f"Penanda '{m.group(1)}' di luar konvensi.", "Gunakan [P-n] atau (inferensi).")

    # struktur BAB
    if cek_struktur:
        wajib = {
            "latar belakang": r"latar\s+belakang",
            "rumusan masalah": r"rumusan\s+masalah",
            "tujuan": r"tujuan\s+penelitian",
            "manfaat": r"manfaat\s+penelitian",
            "batasan": r"batasan\s+masalah| ruang\s+lingkup",
        }
        rendah = teks.lower()
        for nama, pola in wajib.items():
            if not re.search(pola, rendah):
                tambah("struktur", 1, f"Bagian '{nama}' tidak ditemukan.",
                       f"Tambahkan subbab '{nama.title()}' agar BAB I lengkap.")
    return temuan


def ringkas(temuan, kode_abaikan):
    hitung = {}
    for t in temuan:
        if t["kode"] in kode_abaikan:
            continue
        hitung[t["kode"]] = hitung.get(t["kode"], 0) + 1
    return dict(sorted(hitung.items(), key=lambda kv: -kv[1]))


def ke_markdown(temuan, kode_abaikan, nama_berkas):
    if not temuan:
        return f"# Laporan Pemeriksaan Bahasa — {nama_berkas}\n\nTidak ada temuan.\n"
    out = [f"# Laporan Pemeriksaan Bahasa — {nama_berkas}\n",
           f"Total temuan: **{len([t for t in temuan if t['kode'] not in kode_abaikan])}**\n",
           "| Kode | Jumlah | Keterangan |", "|------|--------|------------|"]
    for kode, n in ringkas(temuan, kode_abaikan).items():
        out.append(f"| {kode} | {n} | {KODE.get(kode, '')} |")
    out.append("\n## Rincian\n")
    for t in temuan:
        if t["kode"] in kode_abaikan:
            continue
        out.append(f"- **{t['kode']}** baris {t['baris']} ({t['berkas']}): {t['pesan']}")
        if t["saran"]:
            out.append(f"  - Saran: {t['saran']}")
    out.append("\n> Pemeriksa ini membantu, bukan menggantikan penyuntingan manusia. "
               "Semua temuan perlu ditinjau sebelum naskah difinalkan.\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Pemeriksa gaya bahasa Indonesia untuk proposal")
    ap.add_argument("berkas", nargs="*", help="berkas naskah (.md)")
    ap.add_argument("--dir", help="periksa semua .md dalam direktori")
    ap.add_argument("--dokumen", help="hasil stats_tests.py untuk penanda [D:kolom]")
    ap.add_argument("--json")
    ap.add_argument("--md")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--ignore", action="append", default=[])
    ap.add_argument("--max-kalimat", type=int, default=KALIMAT_PANJANG)
    ap.add_argument("--struktur", action="store_true", help="cek struktur BAB I")
    args = ap.parse_args()

    marker_terdefinis = None
    if args.dokumen and os.path.exists(args.dokumen):
        with open(args.dokumen, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        marker_terdefinis = set()
        for hasil in data.get("hasil", []):
            if hasil.get("blok"):
                marker_terdefinis.add("D:" + hasil["blok"])
            for it in hasil.get("items", []):
                marker_terdefinis.add("D:" + it)
            if hasil.get("grup"):
                marker_terdefinis.add("D:" + hasil["grup"])
        print(f"INFO: {len(marker_terdefinis)} penanda data dikenali dari {args.dokumen}",
              file=sys.stderr)

    berkas = list(args.berkas)
    if args.dir:
        for root, _, files in os.walk(args.dir):
            berkas += [os.path.join(root, f) for f in files if f.endswith(".md")]
    if not berkas:
        ap.error("berikan minimal satu berkas .md, atau --dir")

    semua = []
    for b in berkas:
        if not os.path.exists(b):
            sys.exit(f"ERROR: berkas tidak ditemukan: {b}")
        semua += cek_teks(baca_teks(b), b, args.max_kalimat, marker_terdefinis, args.struktur)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"total": len(semua), "ringkasan": ringkas(semua, args.ignore),
                       "temuan": semua}, fh, ensure_ascii=False, indent=2)
        print(f"Tulis: {args.json}", file=sys.stderr)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as fh:
            for b in berkas:
                fh.write(ke_markdown([t for t in semua if t["berkas"] == b],
                                     args.ignore, os.path.basename(b)))
        print(f"Tulis: {args.md}", file=sys.stderr)

    for kode, n in ringkas(semua, args.ignore).items():
        print(f"{n:>4}  {kode:<16} {KODE.get(kode, '')}")
    if not semua:
        print("Tidak ada temuan.")
    else:
        print(f"\nTotal temuan: {len(semua)} "
              f"(setelah abaikan: {len([t for t in semua if t['kode'] not in args.ignore])})")
        print("Tinjau tiap temuan; jangan diperbaiki otomatis tanpa verifikasi.")
    return 1 if (args.strict and semua) else 0


if __name__ == "__main__":
    sys.exit(main())
