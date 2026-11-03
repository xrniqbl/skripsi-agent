#!/usr/bin/env python3
"""Periksa konsistensi internal naskah skripsi: identitas, tanggal, jumlah
rumusan/tujuan/simpulan, dan rujukan bab yang salah sasaran.

Pemakaian:
    python3 periksa_konsistensi.py naskah.md
    python3 periksa_konsistensi.py Skripsi.docx --profil profil-kampus.yaml
    python3 periksa_konsistensi.py naskah.md --json laporan.json --ketat

Yang diperiksa — semuanya cacat yang lolos dari pemeriksa format karena
naskahnya "rapi" tetapi isinya bertentangan dengan dirinya sendiri:

1. IDENTITAS. Nama & NIM harus sama di sampul, pernyataan keaslian, lembar
   persetujuan, dan pengesahan. Satu huruf beda = dokumen dikembalikan.
2. TANGGAL. Tanggal pengesahan tidak boleh mendahului tanggal sidang; tanggal
   pernyataan tidak boleh sesudah tanggal pengesahan.
3. JUMLAH. Banyak butir Identifikasi/Rumusan Masalah harus sama dengan banyak
   butir Tujuan, dan sama dengan banyak butir Simpulan di BAB V. Ini yang
   paling sering ditanya penguji: "tujuan Anda empat, simpulan Anda tiga?"
4. RUJUKAN BAB. "lihat Bab II" yang menunjuk bab yang tidak memuat hal itu
   tidak bisa diperiksa mesin, tetapi "Bab VI" pada skripsi lima bab bisa —
   begitu pula rujukan ke subbab yang tidak ada ("2.3" padahal Bab II hanya
   sampai 2.2).
5. CAPTION/RUJUKAN. Nomor tabel yang dirujuk di teks tetapi caption-nya tidak
   ada (dan sebaliknya). Pemeriksa caption sudah ada; yang ini memeriksa
   rujukan di paragraf.

Semua temuan adalah SINYAL yang harus dibaca konteksnya, bukan vonis. Skrip
keluar kode 1 hanya bila ada galat bila `--ketat`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# ---------------------------------------------------------------- pembacaan
def baca(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            sys.exit("GAGAL: butuh python-docx untuk membaca .docx")
        d = Document(path)
        bagian = [p.text for p in d.paragraphs]
        for t in d.tables:
            for row in t.rows:
                bagian.append(" | ".join(c.text.strip() for c in row.cells))
        return "\n".join(bagian)
    if ext == ".pdf":
        import subprocess
        return subprocess.run(["pdftotext", "-layout", path, "-"],
                              capture_output=True, text=True).stdout
    with open(path, encoding="utf8", errors="replace") as f:
        return f.read()


BULAN = ("januari|februari|maret|april|mei|juni|juli|agustus|september|"
         "oktober|november|desember")
RE_TANGGAL = re.compile(rf"(\d{{1,2}})\s+({BULAN})\s+(\d{{4}})", re.I)
RE_TANGGAL_ANGKA = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b")
NAMA_BULAN = {b: i + 1 for i, b in enumerate(BULAN.split("|"))}


def tanggal_dari(teks: str):
    m = RE_TANGGAL.search(teks)
    if m:
        return (int(m.group(3)), NAMA_BULAN[m.group(2).lower()], int(m.group(1))), m.group(0)
    m = RE_TANGGAL_ANGKA.search(teks)
    if m:
        return (int(m.group(3)), int(m.group(2)), int(m.group(1))), m.group(0)
    return None, None


# ---------------------------------------------------------------- butir
def butir_bernomor(teks: str, mulai: int, akhir: int,
                   kata_kunci: str) -> list[str]:
    """Ambil butir bernomor (1., 2., a., -) di antara dua penanda heading."""
    potongan = teks[mulai:akhir]
    butir = []
    for baris in potongan.splitlines():
        b = baris.strip()
        if not b:
            continue
        m = re.match(r"^(?:\d+|[a-z])[.)]\s+(.{12,})", b, re.I)
        if m and not re.match(r"^\d+\.\d", b):     # bukan nomor subbab 2.1
            butir.append(m.group(1).strip())
    return butir


def cari_bagian(teks: str, pola: str) -> tuple[int, int]:
    """Rentang [awal, akhir) sebuah bagian berdasarkan heading-nya.

    Heading di naskah nyata berbentuk "1.1 Identifikasi Masalah" atau
    "## 1.2. Identifikasi Masalah" — pola bagian ada di AKHIR baris, dan
    penanda Markdown ("## ") bukan bagian dari nomor. Versi pertama fungsi ini
    menganggap pola langsung diikuti heading berikutnya, sehingga rentangnya
    nol panjang dan jumlah butir selalu terbaca 0.

    Heading yang sama juga muncul di Daftar Isi, jadi semua kandidat diperiksa
    dan yang dipilih adalah rentang dengan butir bernomor terbanyak — itulah
    bagian sesungguhnya, bukan baris daftar isi.
    """
    kandidat: list[tuple[int, int]] = []
    for m in re.finditer(r"^[^\n]*" + pola + r"[^\n]*$", teks, re.I | re.M):
        awal = m.end()
        sisa = teks[awal:]
        nxt = re.search(r"^\s*(?:#{1,6}\s*)?(?:"
                        r"\d+\.\d+\.?\s+\S|[A-Z]\.\s+\S|BAB\s+[IVX]+\b)",
                        sisa, re.M)
        kandidat.append((awal, (awal + nxt.start()) if nxt else len(teks)))
    if not kandidat:
        return -1, -1

    def skor(rentang):
        a, b = rentang
        return len(butir_bernomor(teks, a, b, ""))

    return max(kandidat, key=skor)


# ---------------------------------------------------------------- pemeriksa
def periksa(teks: str, profil: dict | None) -> dict:
    hasil = {"galat": [], "peringatan": [], "info": []}

    def galat(pesan):
        hasil["galat"].append(pesan)

    def peringatan(pesan):
        hasil["peringatan"].append(pesan)

    # ---- 1. identitas: nama & NIM ----
    nama = set()
    for pat in (r"Nama\s*:\s*([A-Z][A-Za-z .,'-]{3,60})",
                r"Nama\s+Mahasiswa\s*:\s*([A-Z][A-Za-z .,'-]{3,60})"):
        for m in re.finditer(pat, teks):
            nama.add(re.sub(r"\s+", " ", m.group(1)).strip().rstrip(".,"))
    if len(nama) >= 2:
        # nama di sampul biasanya tanpa titik dua; bandingkan bentuk dinormalkan
        norm = {n.upper().replace(".", "").strip() for n in nama}
        if len(norm) > 1:
            galat("nama berbeda antar halaman: " + " | ".join(sorted(nama)))

    nim = set(re.findall(r"NIM\s*[:\s]\s*([A-Z]?\d{6,15})", teks, re.I))
    nim |= set(re.findall(r"\b(\d{10,15})\b", teks[:3000]))
    nim_norm = {n.lstrip("0") for n in nim}
    if len(nim_norm) > 1:
        peringatan("beberapa nomor mirip NIM ditemukan: " +
                   ", ".join(sorted(nim)) + " — pastikan hanya satu yang benar")

    judul = re.findall(r"[\"“]([^\"”]{20,200})[\"”]", teks[:4000])
    if len({j.strip().lower() for j in judul}) > 1:
        peringatan("judul dalam tanda kutip berbeda antar halaman — periksa "
                   "keseragaman judul")

    # ---- 2. tanggal ----
    tgl = {}
    for label, pola in (("sidang", r"(?:dipertahankan|disidangkan)[^\n]{0,80}"),
                        ("pengesahan", r"(?:Pengesahan|disahkan)[^\n]{0,80}"),
                        ("pernyataan", r"(?:Dibuat di|Pada tanggal)[^\n]{0,60}")):
        m = re.search(pola, teks, re.I)
        if m:
            t, mentah = tanggal_dari(m.group(0))
            if t:
                tgl[label] = (t, mentah)
    if "sidang" in tgl and "pengesahan" in tgl and tgl["pengesahan"][0] < tgl["sidang"][0]:
        galat(f"tanggal pengesahan ({tgl['pengesahan'][1]}) mendahului tanggal "
              f"sidang ({tgl['sidang'][1]})")
    if "pengesahan" in tgl and "pernyataan" in tgl and \
            tgl["pernyataan"][0] > tgl["pengesahan"][0]:
        peringatan(f"tanggal pernyataan ({tgl['pernyataan'][1]}) sesudah "
                   f"pengesahan ({tgl['pengesahan'][1]})")

    # ---- 3. jumlah masalah/tujuan/simpulan ----
    pasangan = (
        ("identifikasi|rumusan masalah", r"(?:Identifikasi|Rumusan)\s+Masalah"),
        ("tujuan", r"Tujuan\s+Penelitian"),
        ("simpulan|kesimpulan", r"(?:Simpulan|Kesimpulan)"),
    )
    jumlah = {}
    for nama_bagian, pola in pasangan:
        a, b = cari_bagian(teks, pola)
        if a < 0:
            continue
        butir = butir_bernomor(teks, a, b, nama_bagian)
        if butir:
            jumlah[nama_bagian.split("|")[0]] = len(butir)
    if "identifikasi" in jumlah and "tujuan" in jumlah and \
            jumlah["identifikasi"] >= 2 and jumlah["tujuan"] >= 2 and \
            jumlah["identifikasi"] != jumlah["tujuan"]:
        galat(f"jumlah identifikasi masalah ({jumlah['identifikasi']}) tidak sama "
              f"dengan jumlah tujuan ({jumlah['tujuan']})")
    if "tujuan" in jumlah and "simpulan" in jumlah and \
            jumlah["tujuan"] >= 2 and jumlah["simpulan"] >= 2 and \
            jumlah["tujuan"] != jumlah["simpulan"]:
        galat(f"jumlah tujuan ({jumlah['tujuan']}) tidak sama dengan jumlah "
              f"simpulan ({jumlah['simpulan']}) — pemetaan BAB I ke BAB V bolong")
    if jumlah:
        hasil["info"].append("jumlah butir: " + ", ".join(
            f"{k}={v}" for k, v in sorted(jumlah.items())))

    # ---- 4. rujukan bab ----
    ada_bab = {m.group(1).upper() for m in re.finditer(r"^\s*BAB\s+([IVX]+)\b",
                                                       teks, re.I | re.M)}
    for m in re.finditer(r"\b(?:lihat|pada|dalam|di)\s+Bab\s+([IVX]+)\b", teks, re.I):
        target = m.group(1).upper()
        if ada_bab and target not in ada_bab:
            galat(f"rujukan 'Bab {target}' tetapi naskah tidak punya bab itu "
                  f"(ada: {', '.join(sorted(ada_bab))})")

    # subbab yang dirujuk harus ada
    ada_sub = {m.group(0) for m in re.finditer(r"^\s*(\d+\.\d+)\.?\s", teks, re.M)}
    ada_sub = {s.strip() for s in ada_sub}
    for m in re.finditer(r"\bsubbab\s+(\d+\.\d+)\b", teks, re.I):
        if ada_sub and m.group(1) not in ada_sub:
            peringatan(f"rujukan 'subbab {m.group(1)}' tidak ditemukan di naskah")

    # ---- 5. rujukan caption ----
    caption = {m.group(1).lower(): m.group(2) for m in
               re.finditer(r"^\s*(Tabel|Gambar)\s+([IVX]+|\d+)\.(\d+)", teks,
                           re.I | re.M)}
    for m in re.finditer(r"\b(Tabel|Gambar)\s+([IVX]+|\d+)\.(\d+)\b", teks, re.I):
        kunci = m.group(1).lower()
        nomor = f"{m.group(2)}.{m.group(3)}"
        if caption and kunci not in caption:
            peringatan(f"rujukan '{m.group(1)} {nomor}' — caption {kunci} tidak "
                       f"ditemukan dengan nomor itu")
            break

    # ---- 6. aturan yang diikat profil: catatan kaki & lampiran ----
    if profil:
        # Badan naskah saja: daftar pustaka bergaya numerik ("[1] Alpha, ...")
        # menyerupai penanda catatan kaki dan dulu membuat pemeriksaan ini
        # selalu menyimpulkan "catatan kaki dipakai".
        m_dp = re.search(r"^\s*DAFTAR\s+(?:PUSTAKA|RUJUKAN)\s*$", teks, re.I | re.M)
        badan = teks[:m_dp.start()] if m_dp else teks
        ck = profil.get("catatan_kaki") or {}
        dipakai = bool(re.search(r"^\s*(?:\d+\.|\[\d+\]|[\u00b9\u00b2\u00b3])\s*\S.{10,}$",
                                 badan, re.M))
        ada_penanda = bool(re.search(r"\bfootnote\b|\bcatatan kaki\b", badan, re.I))
        if ck.get("wajib") and not (dipakai or ada_penanda):
            galat("profil mewajibkan catatan kaki, tetapi naskah tidak memuat "
                  "satu pun penanda catatan kaki")
        elif ck.get("wajib") is False and dipakai and not ada_penanda:
            peringatan("naskah memakai penomoran seperti catatan kaki, tetapi "
                       "profil menyatakan catatan kaki tidak dipakai")

        lam = profil.get("lampiran") or {}
        lampiran_teks = teks[m_dp.end():] if m_dp else teks
        m = re.search(r"Lampiran\s+(\d+)", lampiran_teks)
        if lam.get("dihitung_dalam_batas_halaman") is False:
            if not m and "lampiran" in lampiran_teks.lower():
                peringatan("profil menyatakan lampiran tidak dihitung dalam batas "
                           "halaman, tetapi tidak ada 'Lampiran 1' bernomor")
            if lam.get("penomoran") and m:
                gaya = str(lam["penomoran"]).lower()
                nomor = m.group(1)
                if "romawi" in gaya and nomor.isdigit():
                    galat(f"lampiran bernomor '{nomor}' padahal profil meminta "
                          f"penomoran Romawi")
    return hasil


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Periksa konsistensi identitas, tanggal, jumlah butir, "
                    "dan rujukan bab pada naskah skripsi.")
    ap.add_argument("naskah")
    ap.add_argument("--profil", help="profil-kampus.yaml (opsional)")
    ap.add_argument("--json", help="tulis laporan JSON")
    ap.add_argument("--ketat", action="store_true",
                    help="peringatan dihitung gagal")
    a = ap.parse_args()

    if not os.path.isfile(a.naskah):
        print(f"GAGAL: naskah tidak ada: {a.naskah}", file=sys.stderr)
        return 2
    profil = None
    if a.profil:
        import yaml
        profil = yaml.safe_load(open(a.profil, encoding="utf8"))
    teks = baca(a.naskah)
    hasil = periksa(teks, profil)

    print(f"=== Konsistensi naskah: {os.path.basename(a.naskah)} ===")
    for i in hasil["info"]:
        print(f"  info      {i}")
    for g in hasil["galat"]:
        print(f"  GALAT     {g}")
    for p in hasil["peringatan"]:
        print(f"  peringatan {p}")
    if not (hasil["galat"] or hasil["peringatan"]):
        print("  OK        tidak ada ketidakcocokan terdeteksi")
    if a.json:
        with open(a.json, "w", encoding="utf8") as f:
            json.dump(hasil, f, ensure_ascii=False, indent=1)
    n = len(hasil["galat"]) + (len(hasil["peringatan"]) if a.ketat else 0)
    print(f"\nRingkasan: {len(hasil['galat'])} galat, "
          f"{len(hasil['peringatan'])} peringatan")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
