#!/usr/bin/env python3
"""Periksa Daftar Pustaka terhadap ketentuan ARS FTI (dan varian APA kampus lain).

Pemakaian:
    python3 periksa_pustaka.py naskah.md
    python3 periksa_pustaka.py naskah.md --tahun-acuan 2026 --min-jurnal 10
    python3 periksa_pustaka.py naskah.md --json laporan.json

Yang diperiksa (nomor = butir panduan FTI ARS 2025 bab 4.10):
    1  urutan abjad nama belakang
    2  nama belakang dulu, baru nama depan
    3  tidak memakai "et al." / "dkk" bila pengarang > 2
    4  tidak ada gelar akademik
    5  usia terbitan <= 5 tahun
    6  jumlah jurnal/prosiding >= 10
    7  larangan Blogspot / Wordpress / Wikipedia
    8  sumber internet wajib tanggal unduh
    9  sitasi dalam teks ada di daftar pustaka (dan sebaliknya)
   10  entri tanpa pengarang memakai nama instansi

Kode keluar:
    0  tidak ada galat (peringatan boleh ada)
    1  ada galat
    2  bagian Daftar Pustaka tidak ditemukan
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata

# --------------------------------------------------------------------------
# ekstraksi teks
# --------------------------------------------------------------------------

def baca_berkas(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            sys.exit("GAGAL: butuh python-docx untuk membaca .docx "
                     "(pip install python-docx)")
        d = Document(path)
        # Paragraf Word ADALAH batas entri pustaka. Menggabungnya dengan "\n"
        # tunggal menghapus batas itu, dan pemecah entri jatuh ke heuristik
        # "Nama ... tahun" — yang gagal pada entri banyak-pengarang karena
        # tahun baru muncul setelah 150 karakter atau lebih, sehingga seluruh
        # daftar terbaca sebagai nol entri.
        bagian = [p.text for p in d.paragraphs]
        for t in d.tables:
            for r in t.rows:
                bagian.append(" | ".join(c.text for c in r.cells))
        # "\n\n" antar paragraf: pemecah entri memisah per baris kosong.
        return "\n\n".join(bagian)
    if ext == ".pdf":
        import subprocess
        try:
            return subprocess.run(["pdftotext", "-layout", path, "-"],
                                  capture_output=True, text=True, timeout=60).stdout
        except FileNotFoundError:
            sys.exit("GAGAL: butuh pdftotext (apt-get install poppler-utils)")
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


RE_PUSTAKA = re.compile(
    r"^[ \t]*(?:#{1,4}[ \t]*)?(DAFTAR\s+PUSTAKA|DAFTAR\s+RUJUKAN|"
    r"REFERENSI|REFERENCES|BIBLIOGRAFI|KEPUSTAKAAN)\b", re.I | re.M)
RE_AKHIR = re.compile(
    r"^[ \t]*(?:#{1,4}[ \t]*)?(LAMPIRAN|DAFTAR\s+RIWAYAT|RIWAYAT\s+HIDUP)\b",
    re.I | re.M)


def ambil_daftar(teks: str) -> tuple[str, str]:
    """Kembalikan (blok_daftar_pustaka, teks_tanpa_daftar)."""
    m = RE_PUSTAKA.search(teks)
    if not m:
        return "", teks
    mulai = m.end()
    sisa = teks[mulai:]
    a = RE_AKHIR.search(sisa)
    akhir = mulai + (a.start() if a else len(sisa))
    blok = teks[mulai:akhir]
    tanpa = teks[:m.start()] + "\n" + teks[akhir:]
    return blok, tanpa


# --------------------------------------------------------------------------
# pemecahan entri
# --------------------------------------------------------------------------

# Awal entri: nama ... tahun 4 digit. Titik DIIZINKAN di dalam nama, karena
# entri sah seperti "Prof. Dr. Budiharto, Widodo, M.Kom. 2025. ..." dan
# "Pratama, M. Octaviano. 2025. ..." mengandung titik sebelum tahunnya.
RE_AWAL_ENTRI = re.compile(
    r"^(?P<nama>[A-Z][^\n]{0,150}?)"
    r"(?<![A-Z])(?P<tahun>(?:19|20)\d{2})(?![\d])"
    r"[.,)]?\s"
)

# Baris yang jelas bukan awal entri (lanjutan URL, halaman, dsb.)
RE_LANJUTAN = re.compile(r"^\s*(?:Diambil dari|https?://|www\.|\d+[-–]\d+|\(|dan\b|[a-z])")


def pecah_entri(blok: str) -> list[str]:
    """Pecah blok jadi entri pustaka.

    Utamakan pemisahan per PARAGRAF (baris kosong) — itu bentuk sebenarnya
    daftar pustaka skripsi, karena panduan mewajibkan jarak dua spasi antar
    entri. Bila naskah menulis entri tanpa baris kosong, jatuh ke deteksi baris
    berawal "Nama ... Tahun".
    """
    paragraf = [p for p in re.split(r"\n\s*\n", blok) if p.strip()]
    paragraf = [p for p in paragraf
                if not p.lstrip().startswith(("#", "|", "---"))]
    # gabung baris yang terlipat di dalam satu paragraf
    kandidat = [" ".join(x.strip() for x in p.splitlines() if x.strip())
                for p in paragraf]

    # tiap paragraf harus mengandung tahun 4 digit agar dianggap entri
    entri = [k for k in kandidat if re.search(r"\b(?:19|20)\d{2}\b", k)]

    if len(entri) >= 2:
        return [e for e in entri if len(e) >= 25]

    # --- fallback: satu entri per baris ---
    hasil: list[str] = []
    buf: list[str] = []
    for b in blok.splitlines():
        if not b.strip() or b.lstrip().startswith(("#", "|", "---")):
            if buf:
                hasil.append(" ".join(x.strip() for x in buf))
                buf = []
            continue
        if RE_AWAL_ENTRI.match(b.strip()):
            if buf:
                hasil.append(" ".join(x.strip() for x in buf))
            buf = [b]
        elif buf:
            buf.append(b)
    if buf:
        hasil.append(" ".join(x.strip() for x in buf))
    return [e for e in hasil if len(e) >= 25]


def nama_belakang(entri: str) -> str:
    """Ambil kata kunci pengurutan: nama belakang pengarang pertama."""
    m = re.match(r"^([^.,(]+)", entri.strip())
    if not m:
        return ""
    kandidat = m.group(1).strip()
    # "Nurfitriana, Rissa" -> "Nurfitriana"; "Divisi SDM" -> "Divisi SDM"
    if "," in entri[:len(kandidat) + 2]:
        return kandidat
    kata = kandidat.split()
    return kata[-1] if kata else kandidat


def kunci_abjad(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", s.lower())


# --------------------------------------------------------------------------
# klasifikasi jenis
# --------------------------------------------------------------------------

RE_JURNAL = re.compile(
    r"\b(vol\.?|volume|no\.?\s*\d|nomor\s*\d|jurnal|journal|prosiding|proceeding|"
    r"issn|e-issn|p-issn|doi|sinta|scopus|konferensi|conference|seminar)\b", re.I)
# Buku format ARS: "Kota Penerbit: Nama Penerbit." — ciri paling andal adalah
# "Kota: Penerbit" (kapital diikuti titik dua). Kata kunci penerbit jarang muncul
# karena panduan hanya menulis nama penerbitnya ("Bandung: Andi Onside.").
RE_BUKU = re.compile(
    r"(\b(press|publisher|penerbit|publishing|ed\.|edisi|isbn|cet\.|cetakan)\b"
    r"|[A-Z][a-z]+(?:\s[A-Z][a-z]+)*:\s+[A-Z][A-Za-z.&'\- ]{2,40}\.?\s*$)", re.I)
RE_WEB = re.compile(r"(https?://|www\.|diambil dari|retrieved from|\.ac\.id|\.go\.id|"
                    r"\.co\.id|\.com|\.org|\.net|\.sch\.id)", re.I)

GELAR = re.compile(
    r"\b(S\.Kom|S\.T|S\.Si|M\.Kom|M\.T|M\.Si|Ph\.D|Dr|Drs|Dra|Prof|Ir|S\.E|M\.M|"
    r"S\.Pd|M\.Pd|S\.H|M\.H|S\.Ked|M\.Ked|S\.Psi|M\.Psi|A\.Md)\b\.?", re.I)

ET_AL = re.compile(r"\b(et\s+al\.?|dkk\.?|dkk\b|and\s+others)\b", re.I)

LARANGAN_SUMBER = [
    ("blogspot", re.compile(r"blogspot\.", re.I)),
    ("wordpress", re.compile(r"wordpress\.(com|org)", re.I)),
    ("wikipedia", re.compile(r"wikipedia\.(org|com)", re.I)),
]

TANGGAL_UNDUH = re.compile(
    r"\((?:[0-3]?\d\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|"
    r"September|Oktober|November|Desember)\s+(?:19|20)\d{2}|"
    r"(?:19|20)\d{2},?\s+[A-Z][a-z]+\s+[0-3]?\d|[A-Z][a-z]+\s+[0-3]?\d,?\s+(?:19|20)\d{2})\)",
    re.I)


# --------------------------------------------------------------------------
# pemeriksaan
# --------------------------------------------------------------------------

def periksa(teks: str, tahun_acuan: int, min_jurnal: int, usia_maks: int) -> dict:
    blok, tanpa_daftar = ambil_daftar(teks)
    if not blok:
        return {"ok": False, "kode": 2,
                "pesan": "Bagian Daftar Pustaka tidak ditemukan "
                         "(cari heading 'DAFTAR PUSTAKA')."}

    entri = pecah_entri(blok)
    galat: list[dict] = []
    peringatan: list[dict] = []
    info: dict = {"jumlah_entri": len(entri)}

    if not entri:
        # Heading ADA tetapi tanpa entri = galat naskah (kode 1), bukan berkas
        # salah (kode 2). Gerbang mutu memperlakukan keduanya berbeda.
        return {"ok": False, "kode": 1,
                "info": {"jumlah_entri": 0, "jurnal_prosiding": 0, "buku": 0,
                         "sumber_web": 0, "lain": 0},
                "galat": [{"kode": "pustaka_kosong",
                           "pesan": "Heading Daftar Pustaka ada, tetapi tidak ada "
                                    "entri yang terbaca.",
                           "saran": "Pisahkan tiap entri dengan satu baris kosong; "
                                    "panduan mewajibkan jarak dua spasi antar entri."}],
                "peringatan": [], "entri": []}

    # --- 1. urutan abjad ---
    kunci = [kunci_abjad(nama_belakang(e)) for e in entri]
    salah_urut = []
    for i in range(1, len(kunci)):
        if kunci[i] and kunci[i - 1] and kunci[i] < kunci[i - 1]:
            salah_urut.append((i, entri[i][:70]))
    if salah_urut:
        galat.append({
            "kode": "tidak_abjad", "nomor_panduan": "4.10 butir 3",
            "pesan": f"{len(salah_urut)} entri tidak berurutan abjad.",
            "contoh": [f"entri #{i+1}: {t}" for i, t in salah_urut[:3]],
            "saran": "Urutkan berdasarkan nama belakang pengarang pertama."})

    # --- 2. et al / dkk ---
    pakai_etal = [e[:80] for e in entri if ET_AL.search(e)]
    if pakai_etal:
        galat.append({
            "kode": "pakai_etal", "nomor_panduan": "4.10 butir 5",
            "pesan": f"{len(pakai_etal)} entri memakai 'et al.'/'dkk'. Panduan ARS "
                     f"mewajibkan SEMUA nama pengarang ditulis lengkap.",
            "contoh": pakai_etal[:3],
            "saran": "Tulis seluruh nama pengarang; hanya pengarang pertama yang "
                     "dibalik (Nama Belakang, Nama Depan)."})

    # --- 3. gelar ---
    bergelar = [e[:80] for e in entri if GELAR.search(e)]
    if bergelar:
        galat.append({
            "kode": "ada_gelar", "nomor_panduan": "4.10 butir 4",
            "pesan": f"{len(bergelar)} entri memuat gelar akademik.",
            "contoh": bergelar[:3],
            "saran": "Hapus gelar (S.Kom, M.T, Dr, Prof, dst.) dari daftar pustaka."})

    # --- 4. usia terbitan ---
    tua = []
    usia_hilang = []
    for e in entri:
        m = re.search(r"\b((?:19|20)\d{2})\b", e)
        if not m:
            usia_hilang.append(e[:70])
            continue
        th = int(m.group(1))
        if tahun_acuan - th > usia_maks:
            tua.append((th, e[:70]))
    if tua:
        galat.append({
            "kode": "referensi_terlalu_tua", "nomor_panduan": "4.10 butir 11",
            "pesan": f"{len(tua)} entri terbit lebih dari {usia_maks} tahun "
                     f"(acuan {tahun_acuan}).",
            "contoh": [f"{th}: {t}" for th, t in tua[:3]],
            "saran": ("Ganti dengan terbitan terbaru. Teori dasar yang lebih tua boleh "
                      "DIPERTAHANKAN bila masih dipakai luas — beri alasan di teks.")})
    if usia_hilang:
        peringatan.append({
            "kode": "tahun_tidak_terbaca", "nomor_panduan": "4.10 butir 11",
            "pesan": f"{len(usia_hilang)} entri tanpa tahun terbit yang terbaca.",
            "contoh": usia_hilang[:3],
            "saran": "Pastikan tahun terbit ada dan formatnya 'Nama. Tahun. Judul.'"})

    # --- 5. jenis & jumlah jurnal ---
    # urutan klasifikasi penting: jurnal dulu (Vol/No/ISSN lebih spesifik),
    # lalu web, lalu buku. Entri jurnal online sah punya URL — jangan direbut web.
    web = [e for e in entri if RE_WEB.search(e)]
    jurnal = [e for e in entri if RE_JURNAL.search(e)]
    # Entri jurnal online yang sah SELALU punya URL (DOI/laman jurnal). Kalau
    # ia dihitung sebagai "sumber web", aturan "web wajib tanggal unduh"
    # menyalakan galat palsu pada setiap artikel ber-DOI, dan naskah yang
    # benar jadi tampak cacat. Jurnal menang; web hanya untuk yang bukan
    # jurnal.
    web = [e for e in web if e not in jurnal]
    buku = [e for e in entri
            if e not in jurnal and e not in web and RE_BUKU.search(e)]
    info.update({"jurnal_prosiding": len(jurnal), "buku": len(buku),
                 "sumber_web": len(web),
                 "lain": len(set(entri) - set(jurnal) - set(buku) - set(web))})
    if len(jurnal) < min_jurnal:
        galat.append({
            "kode": "jurnal_kurang", "nomor_panduan": "4.10 butir 8",
            "pesan": f"Jurnal/prosiding terdeteksi {len(jurnal)}, minimal {min_jurnal}.",
            "saran": ("Tambah sitasi jurnal/prosiding. Hitungan ini heuristik — "
                      "periksa manual entri yang tidak terklasifikasi.")})

    # --- 6. larangan sumber ---
    for nama, rx in LARANGAN_SUMBER:
        kena = [e[:80] for e in entri if rx.search(e)]
        if kena:
            galat.append({
                "kode": f"sumber_{nama}", "nomor_panduan": "4.10 butir 12",
                "pesan": f"{len(kena)} entri bersumber dari {nama}, yang dilarang panduan.",
                "contoh": kena[:3],
                "saran": "Ganti dengan artikel jurnal atau situs resmi instansi."})

    # --- 7. sumber internet tanpa tanggal unduh ---
    web_tanpa_tanggal = [e[:80] for e in web if not TANGGAL_UNDUH.search(e)]
    if web_tanpa_tanggal:
        galat.append({
            "kode": "web_tanpa_tanggal_unduh", "nomor_panduan": "4.10 butir 12",
            "pesan": f"{len(web_tanpa_tanggal)} entri web tanpa tanggal unduh.",
            "contoh": web_tanpa_tanggal[:3],
            "saran": "Tambahkan '(28 Oktober 2026)' di akhir entri."})

    # --- 8. sitasi teks <-> daftar pustaka ---
    # pola sitasi: (Nama, 2025:14) atau Nama (2025:14) atau [L-3]
    RE_SITASI = re.compile(r"\(([A-Z][A-Za-z'’\-]+(?:\s+(?:dan|&)\s+[A-Z][A-Za-z'’\-]+)?),?\s*((?:19|20)\d{2})")
    sitasi = set()
    for m in RE_SITASI.finditer(tanpa_daftar):
        sitasi.add((kunci_abjad(m.group(1).split()[0]), m.group(2)))

    tersedia = set()
    for e in entri:
        m = re.search(r"\b((?:19|20)\d{2})\b", e)
        nb = kunci_abjad(nama_belakang(e))
        if m and nb:
            tersedia.add((nb, m.group(1)))

    yatim = sorted(s for s in sitasi if s not in tersedia)
    if yatim:
        galat.append({
            "kode": "sitasi_tanpa_entri", "nomor_panduan": "4.10 butir 2",
            "pesan": f"{len(yatim)} sitasi dalam teks tidak punya entri di Daftar Pustaka.",
            "contoh": [f"{n.title()} ({t})" for n, t in yatim[:5]],
            "saran": "Tambahkan entri untuk setiap sumber yang dikutip."})

    tak_dikutip = []
    for e in entri:
        nb = kunci_abjad(nama_belakang(e))
        m = re.search(r"\b((?:19|20)\d{2})\b", e)
        if nb and m and (nb, m.group(1)) not in sitasi:
            tak_dikutip.append(e[:70])
    if tak_dikutip:
        peringatan.append({
            "kode": "entri_tak_dikutip", "nomor_panduan": "3.2 bagian C butir 1",
            "pesan": f"{len(tak_dikutip)} entri tidak ditemukan sitasinya di teks.",
            "contoh": tak_dikutip[:3],
            "saran": ("Panduan: referensi yang tidak pernah diacu tidak boleh ada di "
                      "daftar pustaka. Bisa juga pola sitasi tidak terdeteksi — "
                      "periksa manual.")})

    # --- 9. nama depan dulu (heuristik "Nama Depan Nama Belakang.") ---
    # Ciri nama Indonesia: dua kata berhuruf kapital awal TANPA koma sebelum tahun.
    depanku = []
    for e in entri:
        kepala = e.split(".")[0]
        if "," not in kepala and re.fullmatch(r"[A-Z][a-z'’\-]+\s+[A-Z][a-z'’\-]+", kepala.strip()):
            depanku.append(e[:70])
    if depanku:
        peringatan.append({
            "kode": "mungkin_nama_depan_dulu", "nomor_panduan": "4.10 butir 1",
            "pesan": f"{len(depanku)} entri tampak menulis nama depan lebih dulu "
                     f"(tanpa koma).",
            "contoh": depanku[:3],
            "saran": "Bentuk wajib: 'NamaBelakang, NamaDepan.' — kecuali nama Cina."})

    total_galat = len(galat)
    return {"ok": total_galat == 0, "kode": 1 if total_galat else 0,
            "info": info, "galat": galat, "peringatan": peringatan,
            "entri": entri}


def cetak(h: dict) -> None:
    if not h.get("info"):
        print(f"GAGAL: {h.get('pesan')}", file=sys.stderr)
        return
    i = h["info"]
    print("=== Daftar Pustaka ===")
    print(f"  entri            : {i['jumlah_entri']}")
    print(f"  jurnal/prosiding : {i['jurnal_prosiding']}")
    print(f"  buku             : {i['buku']}")
    print(f"  sumber web       : {i['sumber_web']}")
    print(f"  lain             : {i['lain']}")
    print()
    if h["galat"]:
        print(f"=== GALAT ({len(h['galat'])}) ===")
        for g in h["galat"]:
            label = g.get("nomor_panduan", "")
            print(f"  x [{g['kode']}] {g['pesan']}"
                  + (f"   (panduan {label})" if label else ""))
            for c in (g.get("contoh") or [])[:3]:
                print(f"      · {c}")
            print(f"    → {g.get('saran','')}")
        print()
    if h["peringatan"]:
        print(f"=== PERINGATAN ({len(h['peringatan'])}) ===")
        for g in h["peringatan"]:
            print(f"  ! [{g['kode']}] {g['pesan']}")
            for c in (g.get("contoh") or [])[:3]:
                print(f"      · {c}")
            print(f"    → {g.get('saran','')}")
        print()
    print(f"Ringkasan: {len(h['galat'])} galat, {len(h['peringatan'])} peringatan")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Periksa Daftar Pustaka terhadap ketentuan ARS FTI / APA kampus.",
        epilog="contoh: python3 periksa_pustaka.py skripsi.md --tahun-acuan 2026")
    ap.add_argument("naskah", help="berkas .md/.txt/.docx/.pdf")
    ap.add_argument("--tahun-acuan", type=int, default=None,
                    help="tahun patokan usia referensi (default: tahun berjalan)")
    ap.add_argument("--usia-maks", type=int, default=5,
                    help="usia maksimum referensi dalam tahun (default 5)")
    ap.add_argument("--min-jurnal", type=int, default=10,
                    help="minimal jumlah jurnal/prosiding (default 10)")
    ap.add_argument("--json", help="tulis laporan JSON ke berkas ini")
    a = ap.parse_args()

    if not os.path.isfile(a.naskah):
        print(f"GAGAL: berkas tidak ada: {a.naskah}", file=sys.stderr)
        return 2
    tahun = a.tahun_acuan or __import__("datetime").date.today().year
    h = periksa(baca_berkas(a.naskah), tahun, a.min_jurnal, a.usia_maks)
    cetak(h)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"hasil": h, "tahun_acuan": tahun}, f,
                      ensure_ascii=False, indent=2)
        print(f"JSON: {a.json}")
    return h.get("kode", 2)


if __name__ == "__main__":
    sys.exit(main())
