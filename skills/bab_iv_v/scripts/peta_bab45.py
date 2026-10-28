#!/usr/bin/env python3
"""Periksa kelengkapan BAB IV dan BAB V terhadap rumusan masalah.

Pemakaian:
    python3 peta_bab45.py naskah.md --periksa
    python3 peta_bab45.py naskah.md --periksa --json laporan.json
    python3 peta_bab45.py naskah.md --peta        # cetak tabel pemetaan kosong

Yang diperiksa:
  1. JUMLAH BUTIR  — rumusan masalah vs subbab hasil vs butir simpulan
  2. CAKUPAN       — setiap rumusan masalah punya subbab hasil yang menjawab
  3. TAFSIR DI HASIL — kata sebab-akibat di bagian hasil (bukan pembahasan)
  4. ANGKA TANPA SUMBER — angka statistik tanpa rujukan tabel/penanda
  5. EFFECT SIZE   — p-value dilaporkan tanpa ukuran efek
  6. SARAN         — kalimat harapan tanpa pelaku/tindakan

Kode keluar:
  0  tidak ada galat (peringatan boleh ada)
  1  ada galat
  2  berkas tidak terbaca / struktur tidak dikenali
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# ---------- pola struktur ----------
RE_BAB4 = re.compile(
    r"^#{1,3}\s*(BAB\s+IV|BAB\s+4|HASIL\s+DAN\s+PEMBAHASAN|HASIL\s+PENELITIAN)\b", re.I | re.M)
RE_BAB5 = re.compile(
    r"^#{1,3}\s*(BAB\s+V|BAB\s+5|SIMPULAN|KESIMPULAN|PENUTUP)\b", re.I | re.M)
RE_BAB_LAIN = re.compile(
    r"^#{1,3}\s*(BAB\s+(?:I|II|III|VI|1|2|3|6)\b|DAFTAR\s+PUSTAKA|LAMPIRAN)\b", re.I | re.M)
# Nama bagian rumusan berbeda antar kampus. ARS FTI memakai "Identifikasi
# Masalah"; kampus lain "Rumusan/Perumusan Masalah" atau "Pertanyaan Penelitian".
# Ketiganya menandai bagian yang sama: daftar butir yang wajib dijawab BAB IV dan
# dipetakan 1:1 ke simpulan. Pola membolehkan awalan nomor bab ("1.2") dan titik
# opsional ("1.2."), karena panduan ARS menulis subbab dengan titik.
RE_RUMUSAN = re.compile(
    r"^#{1,4}\s*(?:[\dIVX]+\.?[\d.]*\s*)?"
    r"(Rumusan\s+Masalah|Perumusan\s+Masalah|Pertanyaan\s+Penelitian|"
    r"Identifikasi\s+Masalah)\b",
    re.I | re.M)
RE_SIMPULAN = re.compile(r"^#{1,4}\s*[\d.]*\s*(Simpulan|Kesimpulan)\b", re.I | re.M)
RE_SARAN = re.compile(r"^#{1,4}\s*[\d.]*\s*Saran\b", re.I | re.M)
# Subbab BAB IV boleh bernomor "4.1", "4.1." (panduan ARS), atau "4.1.1".
# Tanpa titik opsional, seluruh subbab panduan ARS tidak terdeteksi dan pemetaan
# rumusan -> subbab gagal total padahal naskahnya benar.
RE_SUBBAB = re.compile(r"^(#{2,4})\s+(4\.\d+[\.\d]*)\.?\s*(.+)$", re.M)
RE_BUTIR = re.compile(r"^\s*(?:(\d+)[.)]|[-*•])\s+(.{15,})$", re.M)

# Judul subbab BAB IV yang DITETAPKAN panduan kampus (bukan dipilih mahasiswa).
# ARS FTI: "4.1. Penyajian Hasil Penelitian", "4.2. Pembahasan Hasil",
# "4.3. Implikasi dan Signifikansi Hasil". Bila subbab memakai nama-nama ini,
# judulnya tidak akan pernah memuat variabel rumusan — pemetaan berbasis judul
# pasti gagal padahal naskahnya patuh panduan. Kasus ini ditangani terpisah.
SUBBAB_GENERIK = re.compile(
    r"(penyajian\s+hasil|hasil\s+penelitian|gambaran\s+umum|hasil\s+dan\s+pembahasan|"
    r"pembahasan\s+hasil|pembahasan|implikasi|signifikansi|diskusi|interpretasi|"
    r"analisis\s+hasil|temuan)", re.I)

# ---------- pola isi ----------
KATA_TAFSIR = [
    "disebabkan", "dikarenakan", "karena itu", "oleh sebab itu", "akibatnya",
    "mengakibatkan", "menyebabkan", "hal ini menunjukkan", "hal ini berarti",
    "sesuai dengan teori", "sejalan dengan teori", "diduga", "kemungkinan besar",
    "dapat disimpulkan", "dapat diartikan", "menandakan bahwa", "membuktikan bahwa",
]
KATA_SARAN_HARAPAN = [
    "hendaknya", "sebaiknya lebih ditingkatkan", "perlu adanya", "semoga",
    "diharapkan dapat", "kiranya", "alangkah baiknya", "sudah sepatutnya",
]
RE_ANGKA_STAT = re.compile(
    r"\b(p\s*[=<>]\s*0?[.,]\d+|\b[trFzχ]\s*=\s*[-−]?\d|R\s*²?\s*=\s*0?[.,]\d|"
    r"β\s*=\s*[-−]?\d|Exp\(B\)|sig\.?\s*[=<>]?\s*0?[.,]\d)", re.I)
RE_RUJUKAN = re.compile(
    r"(Tabel\s+\d|Gambar\s+\d|\[L-\d+\]|\[D:[^\]]+\]|\[hasil_uji\]|lampiran\s+\d)", re.I)
RE_EFFECT = re.compile(
    r"(effect size|ukuran efek|Cohen|η²|eta squared|partial eta|d\s*=\s*0?[.,]\d|"
    r"r\s*=\s*[-−]?0?[.,]\d|R\s*²\s*=|odds ratio|Exp\(B\))", re.I)
RE_TABEL = re.compile(r"Tabel\s+(\d+\.\d+)", re.I)


def potong_bab(teks: str) -> dict[str, str]:
    """Bagi naskah jadi bagian per bab berdasarkan heading."""
    penanda = []
    for rx, nama in ((RE_RUMUSAN, "RUMUSAN"), (RE_BAB4, "BAB4"),
                     (RE_BAB5, "BAB5"), (RE_BAB_LAIN, "LAIN")):
        for m in rx.finditer(teks):
            penanda.append((m.start(), nama, m.group(0).strip()))
    penanda.sort()
    bagian: dict[str, str] = {}
    for i, (pos, nama, _) in enumerate(penanda):
        akhir = penanda[i + 1][0] if i + 1 < len(penanda) else len(teks)
        isi = teks[pos:akhir]
        if nama == "LAIN":
            continue
        bagian[nama] = bagian.get(nama, "") + "\n" + isi
    return bagian


def ambil_butir(blok: str) -> list[str]:
    """Ambil butir bernomor/berpoin dari sebuah blok."""
    keluar = []
    for m in RE_BUTIR.finditer(blok):
        isi = re.sub(r"\s+", " ", m.group(2)).strip()
        isi = re.sub(r"^\[[^\]]*\]\s*", "", isi)  # buang penanda status
        if len(isi) >= 15:
            keluar.append(isi)
    return keluar


def ambil_kalimat(blok: str, min_panjang: int = 25) -> list[str]:
    """Ambil kalimat bermakna (untuk blok prosa tanpa butir bernomor)."""
    bersih = re.sub(r"^#{1,4}.*$", "", blok, flags=re.M)
    keluar = []
    for k in re.split(r"(?<=[.!?])\s+", bersih):
        k = re.sub(r"\s+", " ", k).strip()
        k = re.sub(r"^[-*•]\s*", "", k)
        if len(k) >= min_panjang and not k.startswith("|"):
            keluar.append(k)
    return keluar


def normal(s: str) -> set[str]:
    stop = {"yang", "dan", "atau", "untuk", "pada", "dalam", "dengan", "terhadap",
            "bagaimana", "apakah", "sejauh", "apa", "adalah", "di", "ke", "dari",
            "ini", "itu", "serta", "oleh", "tidak", "akan", "dapat", "bagi"}
    return {w for w in re.findall(r"[a-z]{4,}", s.lower()) if w not in stop}


def tumpang(a: set[str], b: set[str]) -> tuple[int, float]:
    """(jumlah kata beririsan, rasio terhadap himpunan terkecil)."""
    if not a or not b:
        return 0, 0.0
    n = len(a & b)
    return n, n / min(len(a), len(b))


def periksa(teks: str) -> dict:
    bagian = potong_bab(teks)
    galat: list[dict] = []
    peringatan: list[dict] = []
    info: dict = {}

    # --- 1. rumusan masalah ---
    blok_rum = bagian.get("RUMUSAN", "")
    rumusan = ambil_butir(blok_rum)
    if not rumusan:
        # coba cari paragraf bernomor di seluruh naskah bagian awal
        awal = teks[:len(teks) // 3]
        m = RE_RUMUSAN.search(awal)
        if m:
            rumusan = ambil_butir(awal[m.start():])
    info["jumlah_rumusan"] = len(rumusan)

    # --- 2. subbab hasil ---
    blok4 = bagian.get("BAB4", "")
    subbab = [(n, j.strip()) for _, n, j in RE_SUBBAB.findall(blok4)]
    info["jumlah_subbab_bab4"] = len(subbab)
    info["subbab"] = [f"{n} {j}" for n, j in subbab]
    info["ada_bab4"] = bool(blok4)
    info["ada_bab5"] = bool(bagian.get("BAB5", ""))

    if not blok4:
        galat.append({"kode": "bab4_hilang",
                      "pesan": "BAB IV (Hasil dan Pembahasan) tidak ditemukan.",
                      "saran": "Tambahkan heading '# BAB IV HASIL DAN PEMBAHASAN'."})
    if not bagian.get("BAB5"):
        galat.append({"kode": "bab5_hilang",
                      "pesan": "BAB V (Simpulan dan Saran) tidak ditemukan.",
                      "saran": "Tambahkan heading '# BAB V SIMPULAN DAN SARAN'."})

    # --- 3. simpulan & saran ---
    blok5 = bagian.get("BAB5", "")
    m_simp = RE_SIMPULAN.search(blok5)
    m_sar = RE_SARAN.search(blok5)
    blok_simp = blok5[m_simp.start():m_sar.start()] if (m_simp and m_sar) else (
        blok5[m_simp.start():] if m_simp else "")
    blok_sar = blok5[m_sar.start():] if m_sar else ""
    simpulan = ambil_butir(blok_simp)
    saran = ambil_butir(blok_sar)
    if not saran and blok_sar:
        # saran ditulis sebagai prosa, bukan daftar — tetap periksa
        saran = ambil_kalimat(blok_sar)
    info["jumlah_simpulan"] = len(simpulan)
    info["jumlah_saran"] = len(saran)

    if rumusan and len(simpulan) != len(rumusan):
        galat.append({
            "kode": "jumlah_tidak_sama",
            "pesan": f"Rumusan masalah {len(rumusan)} butir, simpulan {len(simpulan)} butir"
                     + (" (simpulan ditulis sebagai prosa, bukan butir bernomor)."
                        if not simpulan else "."),
            "saran": "Jumlah butir simpulan wajib sama dengan rumusan masalah, urutan sama. "
                     "Tulis sebagai daftar bernomor 1..n."})

    if not simpulan and bagian.get("BAB5"):
        peringatan.append({"kode": "simpulan_kosong",
                           "pesan": "Subbab Simpulan tidak ditemukan atau tanpa butir bernomor.",
                           "saran": "Tulis simpulan sebagai daftar bernomor 1..n."})
    if not saran and bagian.get("BAB5"):
        peringatan.append({"kode": "saran_kosong",
                           "pesan": "Subbab Saran tidak ditemukan atau tanpa butir.",
                           "saran": "Pisahkan saran untuk objek, instansi, dan peneliti lanjut."})

    # --- 4. cakupan rumusan -> subbab hasil ---
    if rumusan and subbab:
        # subbab Pembahasan bukan kandidat — ia menafsirkan, bukan menjawab langsung
        judul_sub = [f"{n} {j}" for n, j in subbab
                     if not re.search(r"pembahasan|diskusi|interpretasi", j, re.I)]
        # Bila seluruh subbab hasil memakai nama baku panduan, judul tidak bisa
        # dipakai sebagai bukti pemetaan. Turunkan ke sub-sub (4.1.1, 4.1.2, ...)
        # yang biasanya memang per-rumusan; kalau tidak ada juga, laporkan sebagai
        # "tidak terverifikasi" — bukan sebagai kesalahan naskah.
        generik = bool(judul_sub) and all(SUBBAB_GENERIK.search(j) for j in judul_sub)
        dipakai: set[str] = set()
        belum_terverifikasi: list[int] = []
        for i, r in enumerate(rumusan, 1):
            wr = normal(r)
            skor = []
            for j in judul_sub:
                nb, rasio = tumpang(wr, normal(j))
                # subbab yang sudah dipakai rumusan lain diberi penalti, bukan dilarang
                penalti = 0.35 if j in dipakai else 0.0
                skor.append((rasio - penalti, j, nb))
            terbaik = max(skor, default=(0.0, "", 0))
            if (terbaik[0] < 0.25 or terbaik[2] == 0) and generik:
                belum_terverifikasi.append(i)
            elif terbaik[0] < 0.25 or terbaik[2] == 0:
                peringatan.append({
                    "kode": "cakupan_rendah",
                    "pesan": (f"Rumusan masalah #{i} tidak jelas terpetakan ke subbab hasil "
                              f"manapun (kemiripan tertinggi {terbaik[0]:.2f} pada "
                              f"'{terbaik[1] or '-'}')."),
                    "saran": ("Beri subbab hasil yang menyebut variabel rumusan ini, "
                              "atau ubah judul subbab agar sejalan dengan BAB I."),
                    "butir": r[:140]})
            else:
                dipakai.add(terbaik[1])
                info.setdefault("peta", []).append(
                    {"rumusan": r[:140], "subbab": terbaik[1], "skor": round(terbaik[0], 2)})

        if belum_terverifikasi:
            peringatan.append({
                "kode": "pemetaan_tidak_terverifikasi",
                "pesan": (f"Subbab BAB IV memakai judul baku panduan kampus, sehingga "
                          f"rumusan #{', #'.join(map(str, belum_terverifikasi))} tidak bisa "
                          f"dipetakan dari judul subbab."),
                "saran": ("Ini bukan kesalahan naskah bila panduan kampus memang menetapkan "
                          "judul subbabnya. Verifikasi manual: pastikan tiap rumusan "
                          "mendapat sub-subbab (4.1.1, 4.1.2, ...) atau blok bernomor di "
                          "dalam Penyajian Hasil Penelitian.")})

    # --- 5. tafsir di bagian hasil ---
    # bagian hasil = sebelum subbab pembahasan
    m_bahas = re.search(r"^#{2,4}\s*4\.\d+[\.\d]*\s*(Pembahasan|Diskusi)\b", blok4, re.I | re.M)
    blok_hasil = blok4[:m_bahas.start()] if m_bahas else blok4
    rendah_hasil = blok_hasil.lower()
    for kata in KATA_TAFSIR:
        for m in re.finditer(re.escape(kata), rendah_hasil):
            baris_no = blok_hasil[:m.start()].count("\n") + 1
            cuplikan = blok_hasil[max(0, m.start() - 70):m.start() + 90].replace("\n", " ")
            galat.append({
                "kode": "tafsir_di_hasil",
                "pesan": f"Kata tafsir '{kata}' muncul di bagian Hasil (baris {baris_no}): …{cuplikan.strip()}…",
                "saran": ("Pindahkan kalimat ini ke subbab Pembahasan. Bagian Hasil hanya "
                          "melaporkan angka dan keputusan statistik.")})
            break  # satu contoh per kata cukup

    # --- 6. angka statistik tanpa rujukan ---
    for m in RE_ANGKA_STAT.finditer(blok4):
        konteks = blok4[max(0, m.start() - 300):m.start() + 200]
        if not RE_RUJUKAN.search(konteks):
            baris_no = blok4[:m.start()].count("\n") + 1
            galat.append({
                "kode": "angka_tanpa_sumber",
                "pesan": f"Angka statistik '{m.group(0).strip()}' tanpa rujukan tabel/penanda (baris {baris_no}).",
                "saran": "Tambahkan 'Tabel 4.x' atau penanda [D:kolom]/[L-n] di dekatnya."})

    # --- 7. p-value tanpa effect size ---
    ada_p = bool(re.search(r"\bp\s*[=<>]\s*0?[.,]\d", blok4, re.I))
    ada_eff = bool(RE_EFFECT.search(blok4))
    info["ada_p_value"] = ada_p
    info["ada_effect_size"] = ada_eff
    if ada_p and not ada_eff:
        peringatan.append({
            "kode": "tanpa_effect_size",
            "pesan": "Ada nilai p tetapi tidak ada ukuran efek (R², d, η², r, Exp(B)).",
            "saran": ("p memberi tahu apakah ada; ukuran efek memberi tahu seberapa besar. "
                      "Penguji akan menanyakannya.")})

    # --- 8. saran berupa harapan tanpa pelaku ---
    for b in saran:
        rendah = b.lower()
        for kata in KATA_SARAN_HARAPAN:
            if kata in rendah and not re.search(
                    r"\b(puskesmas|dinas|instansi|perusahaan|sekolah|kantor|tim|"
                    r"peneliti|pengelola|manajemen|kepala|admin|unit)\b", rendah):
                galat.append({
                    "kode": "saran_tanpa_pelaku",
                    "pesan": f"Saran tanpa pelaku konkret: '{b[:120]}'",
                    "saran": "Sebutkan siapa yang melakukan apa, dalam rentang waktu apa."})
                break

    # --- 9. tabel disebut tapi tidak ada nomornya berurutan ---
    nomor = sorted({n for n in RE_TABEL.findall(blok4)})
    info["tabel_disebut"] = nomor
    if nomor:
        urut = [n for n in nomor if n.startswith("4.")]
        if urut:
            angka = [int(n.split(".")[1]) for n in urut]
            harap = list(range(min(angka), max(angka) + 1))
            hilang = [str(x) for x in harap if x not in angka]
            if hilang:
                peringatan.append({
                    "kode": "nomor_tabel_lompat",
                    "pesan": f"Nomor tabel Bab IV melompat: hilang 4.{', 4.'.join(hilang)}",
                    "saran": "Nomor tabel harus berurutan tanpa lompatan."})

    return {"galat": galat, "peringatan": peringatan, "info": info}


def cetak_peta() -> str:
    return """# Tabel Pemetaan Rumusan → Hasil → Pembahasan

Isi sebelum menulis BAB IV. Jumlah baris = jumlah rumusan masalah.

| # | Rumusan masalah (kutip dari BAB I) | Alat analisis (BAB III) | Tabel/angka | Jawaban satu kalimat | Teori pembanding |
|---|---|---|---|---|---|
| 1 |  |  | Tabel 4. |  | [L-] |
| 2 |  |  | Tabel 4. |  | [L-] |
| 3 |  |  | Tabel 4. |  | [L-] |

## Aturan

- Kolom **Alat analisis** wajib sudah ada di BAB III. Kalau tidak → perbaiki BAB III dulu.
- Kolom **Jawaban satu kalimat** diisi sebelum paragraf ditulis. Tidak bisa satu kalimat
  = rumusan masalahnya terlalu kabur.
- Kolom **Teori pembanding** minimal satu. Tanpa ini pembahasan jadi pengulangan hasil.
- Setelah terisi, butir simpulan di BAB V disalin dari kolom "Jawaban satu kalimat",
  urutannya sama.
"""


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("berkas", nargs="?", help="naskah markdown")
    ap.add_argument("--periksa", action="store_true", help="jalankan pemeriksaan")
    ap.add_argument("--peta", action="store_true", help="cetak tabel pemetaan kosong")
    ap.add_argument("--json", help="tulis hasil ke JSON")
    ap.add_argument("--ketat", action="store_true", help="peringatan dihitung sebagai galat")
    args = ap.parse_args()

    if args.peta:
        print(cetak_peta())
        return 0

    if not args.berkas:
        ap.error("butuh berkas naskah (atau pakai --peta)")
    try:
        teks = open(args.berkas, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print(f"GAGAL membaca {args.berkas}: {e}", file=sys.stderr)
        return 2

    if not re.search(r"BAB\s+(IV|V|4|5)|HASIL|SIMPULAN|KESIMPULAN", teks, re.I):
        print("Struktur BAB IV/V tidak dikenali di naskah ini.", file=sys.stderr)
        return 2

    hasil = periksa(teks)
    info, galat, peringatan = hasil["info"], hasil["galat"], hasil["peringatan"]

    print("=== Struktur ===")
    print(f"  rumusan masalah : {info.get('jumlah_rumusan', 0)} butir")
    print(f"  subbab BAB IV   : {info.get('jumlah_subbab_bab4', 0)}")
    print(f"  butir simpulan  : {info.get('jumlah_simpulan', 0)}")
    print(f"  butir saran     : {info.get('jumlah_saran', 0)}")
    print(f"  p-value ada     : {'ya' if info.get('ada_p_value') else 'tidak'}"
          f" | effect size: {'ya' if info.get('ada_effect_size') else 'tidak'}")

    if info.get("peta"):
        print("\n=== Pemetaan rumusan → subbab hasil ===")
        for i, p in enumerate(info["peta"], 1):
            print(f"  {i}. [{p['skor']:.2f}] {p['subbab']}")
            print(f"     ← {p['rumusan'][:100]}")

    if galat:
        print(f"\n=== GALAT ({len(galat)}) ===")
        for g in galat:
            print(f"  ✗ [{g['kode']}] {g['pesan']}")
            print(f"    → {g['saran']}")
    if peringatan:
        print(f"\n=== PERINGATAN ({len(peringatan)}) ===")
        for p in peringatan:
            print(f"  ! [{p['kode']}] {p['pesan']}")
            print(f"    → {p['saran']}")
    if not galat and not peringatan:
        print("\nTidak ada temuan. Struktur BAB IV/V lengkap.")

    print(f"\nRingkasan: {len(galat)} galat, {len(peringatan)} peringatan")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(hasil, f, ensure_ascii=False, indent=2)
        print(f"JSON: {args.json}")

    gagal = bool(galat) or (args.ketat and bool(peringatan))
    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main())
