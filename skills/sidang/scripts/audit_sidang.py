#!/usr/bin/env python3
"""Audit naskah untuk persiapan sidang + bangkitkan pertanyaan penguji dari naskah sendiri.

Pemakaian:
    python3 audit_sidang.py naskah.md
    python3 audit_sidang.py naskah.md --pertanyaan
    python3 audit_sidang.py naskah.md --json audit.json
    python3 audit_sidang.py naskah.md --kartu-angka     # cetak 10 angka kunci

Yang diaudit:
  1. KONSISTENSI  — jumlah rumusan vs tujuan vs simpulan
  2. ANGKA        — angka statistik tanpa sumber; angka muncul di slide tapi tidak di naskah
  3. KLAIM        — klaim tanpa penanda rujukan [L-n]
  4. KATA LEMAH   — "diduga", "mungkin", "sayangnya", "hendaknya"
  5. STRUKTUR     — bab/subbab wajib hilang
  6. PERTANYAAN   — dibangkitkan dari angka, n, metode, dan klaim yang lemah

Kode keluar 1 bila ada galat, 0 bila hanya peringatan/bersih.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# ---------- struktur ----------
RE_BAB = {
    "BAB I": re.compile(r"^#{1,3}\s*BAB\s+(I|1)\b", re.I | re.M),
    "BAB II": re.compile(r"^#{1,3}\s*BAB\s+(II|2)\b", re.I | re.M),
    "BAB III": re.compile(r"^#{1,3}\s*BAB\s+(III|3)\b", re.I | re.M),
    "BAB IV": re.compile(r"^#{1,3}\s*BAB\s+(IV|4)\b", re.I | re.M),
    "BAB V": re.compile(r"^#{1,3}\s*BAB\s+(V|5)\b", re.I | re.M),
    # Bagian akhir sering ditulis tanpa penanda markdown (hasil salin dari DOCX),
    # jadi '#' dibuat opsional — kalau wajib, naskah yang lengkap pun dilaporkan
    # "DAFTAR PUSTAKA hilang".
    "DAFTAR PUSTAKA": re.compile(r"^\s*(?:#{1,3}\s*)?(DAFTAR\s+PUSTAKA|"
                                 r"DAFTAR\s+RUJUKAN|REFERENCES)\b", re.I | re.M),
}
SUB_WAJIB = {
    "latar belakang": r"latar\s+belakang",
    # Panduan FTI ARS memakai "Identifikasi Masalah"; kampus lain memakai
    # "Rumusan/Perumusan Masalah" atau "Pertanyaan Penelitian". Ketiganya bagian
    # yang sama, dan penguji membacanya dengan nama yang dipakai panduan.
    "rumusan masalah": r"(rumusan|perumusan)\s+masalah|identifikasi\s+masalah|"
                       r"pertanyaan\s+penelitian",
    "tujuan": r"\btujuan\b(?!\s+penelitian\s+lanjut)",
    "manfaat": r"\bmanfaat\b",
    "metode": r"metode|metodologi",
    "simpulan": r"simpulan|kesimpulan",
    "saran": r"\bsaran\b",
}
RE_BUTIR = re.compile(r"^\s*(?:(\d+)[.)]|[-*•])\s+(.{15,})$", re.M)

# ---------- angka ----------
# Angka desimal wajib ditangkap utuh: '\d' saja memotong "0,412" jadi "0".
_DES = r"[-−]?\d+(?:[.,]\d+)?"
RE_ANGKA_STAT = re.compile(
    rf"\b(p\s*[=<>]\s*0?[.,]\d+"
    rf"|\b[trFzχH]\s*=\s*{_DES}"
    rf"|R\s*²?\s*=\s*0?[.,]\d+"
    rf"|β\s*=\s*{_DES}"
    rf"|Exp\(B\)\s*=\s*{_DES}"
    rf"|sig\.?\s*[=<>]?\s*0?[.,]\d+)", re.I)
RE_RUJUKAN = re.compile(
    r"(Tabel\s+\d|Gambar\s+\d|\[L-\d+\]|\[D:[^\]]+\]|\[hasil_uji\]|lampiran\s+\d)", re.I)
RE_N = re.compile(r"\bn\s*=\s*(\d+)", re.I)
RE_SAMPEL = re.compile(
    r"\b(\d+)\s*(?:responden|sampel|partisipan|subjek|orang|petugas|karyawan|siswa|pasien)\b",
    re.I)

# ---------- klaim & kata lemah ----------
KATA_LEMAH = {
    "diduga": "tafsir tanpa dasar — ganti dengan mekanisme yang bisa dilacak",
    "kemungkinan besar": "spekulasi — sebut bukti atau hapus",
    "sayangnya": "menyiratkan hasil buruk — laporkan netral",
    "hendaknya": "bukan saran yang bisa dikerjakan — sebut pelaku + tindakan",
    "kiranya": "bukan saran",
    "semoga": "bukan saran",
    "sangat": "kata penguat tanpa isi — ganti dengan angka",
    "banyak": "kuantifikasi — sebut persentase atau jumlah",
    "sedikit": "kuantifikasi — sebut persentase atau jumlah",
    "mendekati signifikan": "istilah tidak ada dalam statistik — tulis nilai p apa adanya",
    "sesuai teori": "sebut teori mana dan bagian mana",
    "berpengaruh signifikan": "pada data korelasional: tulis 'berhubungan'",
}
RE_KLAIM = re.compile(
    r"\b(menyebabkan|mengakibatkan|membuktikan|membuktikan bahwa|dapat digeneralisasi|"
    r"berlaku umum|seluruh indonesia|semua instansi)\b", re.I)


def potong_bab(teks: str) -> dict[str, str]:
    tanda = []
    for nama, rx in RE_BAB.items():
        for m in rx.finditer(teks):
            tanda.append((m.start(), nama))
    tanda.sort()
    bagian: dict[str, str] = {}
    for i, (pos, nama) in enumerate(tanda):
        akhir = tanda[i + 1][0] if i + 1 < len(tanda) else len(teks)
        bagian[nama] = teks[pos:akhir]
    return bagian


def ambil_butir(blok: str) -> list[str]:
    keluar = []
    for m in RE_BUTIR.finditer(blok):
        isi = re.sub(r"\s+", " ", m.group(2)).strip()
        isi = re.sub(r"^\[[^\]]*\]\s*", "", isi)
        if len(isi) >= 15:
            keluar.append(isi)
    return keluar


def blok_sub(teks: str, pola: str) -> str:
    """Ambil blok subbab berdasarkan pola nama, sampai heading berikutnya."""
    m = re.search(rf"^#{{1,4}}\s*[\d.]*\s*({pola})\b", teks, re.I | re.M)
    if not m:
        return ""
    sisa = teks[m.start():]
    m2 = re.search(r"^#{1,4}\s", sisa[10:], re.M)
    return sisa[: m2.start() + 10] if m2 else sisa


def audit(teks: str) -> dict:
    galat, peringatan, pertanyaan = [], [], []
    bagian = potong_bab(teks)
    info: dict = {}

    # --- 1. struktur ---
    hilang = [b for b in RE_BAB if b not in bagian]
    if hilang:
        peringatan.append({"kode": "bab_hilang",
                           "pesan": f"Bab tidak ditemukan: {', '.join(hilang)}",
                           "saran": "Naskah sidang harus lengkap, atau sebutkan bagian "
                                    "yang belum selesai."})
    rendah = teks.lower()
    sub_hilang = [k for k, p in SUB_WAJIB.items() if not re.search(p, rendah)]
    if sub_hilang:
        peringatan.append({"kode": "subbab_hilang",
                           "pesan": f"Subbab tidak ditemukan: {', '.join(sub_hilang)}",
                           "saran": "Penguji membuka naskah dari daftar isi — subbab hilang "
                                    "langsung terlihat."})

    # --- 2. konsistensi jumlah ---
    rum = ambil_butir(blok_sub(bagian.get("BAB I", ""), SUB_WAJIB["rumusan masalah"]))
    tuj = ambil_butir(blok_sub(bagian.get("BAB I", ""), SUB_WAJIB["tujuan"]))
    sim = ambil_butir(blok_sub(bagian.get("BAB V", ""), SUB_WAJIB["simpulan"]))
    info.update({"jumlah_rumusan": len(rum), "jumlah_tujuan": len(tuj),
                 "jumlah_simpulan": len(sim)})

    # Bila rumusan berbentuk butir bernomor tetapi tujuan ditulis sebagai satu
    # paragraf, perbandingan 1:1 DIAM-DIAM terlewat (syarat `rum and tuj`).
    # Lompatan senyap inilah yang berbahaya: naskah tampak lulus padahal
    # kesejajaran rumusan-tujuan belum pernah diperiksa.
    if rum and not tuj:
        peringatan.append({
            "kode": "tujuan_tanpa_butir",
            "pesan": (f"Rumusan masalah {len(rum)} butir, tetapi tujuan penelitian "
                      f"tidak berbentuk butir bernomor sehingga kesejajaran 1:1 "
                      f"tidak dapat diperiksa."),
            "saran": ("Tulis tujuan sebagai daftar bernomor dengan urutan sama "
                      "seperti rumusan/identifikasi masalah.")})

    if rum and tuj and len(rum) != len(tuj):
        galat.append({"kode": "rumusan_tujuan_beda",
                      "pesan": f"Rumusan masalah {len(rum)} butir, tujuan {len(tuj)} butir.",
                      "saran": "Tujuan wajib sejajar 1:1 dengan rumusan masalah."})
        pertanyaan.append({
            "kelompok": "konsistensi",
            "tanya": f"Rumusan masalah ada {len(rum)} butir, tapi tujuan hanya {len(tuj)}. "
                     f"Yang mana yang tidak terjawab?",
            "siapkan": "Samakan jumlah dan urutan sebelum sidang."})
    if rum and sim and len(rum) != len(sim):
        galat.append({"kode": "rumusan_simpulan_beda",
                      "pesan": f"Rumusan masalah {len(rum)} butir, simpulan {len(sim)} butir.",
                      "saran": "Jumlah butir simpulan wajib sama dengan rumusan masalah."})
        pertanyaan.append({
            "kelompok": "konsistensi",
            "tanya": f"Rumusan masalah {len(rum)} butir, simpulan {len(sim)} butir. "
                     f"Rumusan mana yang tidak disimpulkan?",
            "siapkan": "Samakan jumlah dan urutan."})
    if rum and not sim:
        galat.append({"kode": "simpulan_kosong",
                      "pesan": "Simpulan tidak ditemukan atau tidak berbentuk butir bernomor.",
                      "saran": "Tulis simpulan sebagai daftar bernomor 1..n."})

    # --- 3. angka statistik tanpa rujukan ---
    # Hanya diperiksa di BAB IV. Di BAB V angka boleh muncul tanpa rujukan tabel karena
    # simpulan memang merangkum hasil — memeriksanya di sana menghasilkan galat palsu.
    zona = bagian.get("BAB IV", "") or bagian.get("BAB III", "") or teks
    for m in RE_ANGKA_STAT.finditer(zona):
        konteks = zona[max(0, m.start() - 300):m.start() + 200]
        if not RE_RUJUKAN.search(konteks):
            baris_no = zona[:m.start()].count("\n") + 1
            galat.append({"kode": "angka_tanpa_sumber",
                          "pesan": f"'{m.group(0).strip()}' tanpa rujukan tabel (baris {baris_no}).",
                          "saran": "Sebut 'Tabel x.y' atau penanda [D:kolom] di dekatnya."})
            if len(pertanyaan) < 40:
                pertanyaan.append({
                    "kelompok": "angka",
                    "tanya": f"Angka '{m.group(0).strip()}' di baris {baris_no} berasal dari "
                             f"tabel mana? Saya tidak menemukan rujukannya.",
                    "siapkan": "Sebut tabel dan halaman; kalau tidak ada, hitung ulang."})

    # --- 4. sampel kecil / klaim generalisasi ---
    n_nilai = [int(x) for x in RE_N.findall(teks)]
    sampel = [int(x) for x in RE_SAMPEL.findall(teks)]
    n_min = min([x for x in n_nilai + sampel if x > 0], default=None)
    info["n_terkecil"] = n_min
    if n_min is not None and n_min < 30:
        pertanyaan.append({
            "kelompok": "sampel",
            "tanya": f"Sampel terkecil yang disebut n = {n_min}. Apakah hasilnya bisa "
                     f"digeneralisasi?",
            "siapkan": ("Jawab: ini studi kasus/sensus pada unit tertentu; temuan berlaku "
                        "pada konteks itu, bukan populasi luas. Sebut batasnya di naskah.")})

    for m in RE_KLAIM.finditer(teks):
        baris_no = teks[:m.start()].count("\n") + 1
        peringatan.append({"kode": "klaim_kuat",
                           "pesan": f"Klaim '{m.group(0)}' (baris {baris_no}) — periksa apakah "
                                    f"data mendukungnya.",
                           "saran": "Pada data korelasional, ganti dengan 'berhubungan/"
                                    "berasosiasi'; hapus klaim generalisasi."})
        pertanyaan.append({
            "kelompok": "klaim",
            "tanya": f"Anda menulis '{m.group(0)}'. Apa buktinya dari data Anda?",
            "siapkan": "Siapkan satu angka + satu batas cakupan."})

    # --- 5. kata lemah ---
    for kata, alasan in KATA_LEMAH.items():
        for m in re.finditer(rf"\b{re.escape(kata)}\b", rendah):
            baris_no = teks[:m.start()].count("\n") + 1
            peringatan.append({"kode": "kata_lemah",
                               "pesan": f"'{kata}' (baris {baris_no}): {alasan}",
                               "saran": "Ganti dengan angka atau mekanisme yang bisa dilacak."})
            break

    # --- 6. pertanyaan wajib (selalu ada) ---
    pertanyaan.extend([
        {"kelompok": "wajib", "tanya": "Apa masalah penelitian ini, dan kenapa penting?",
         "siapkan": "Satu paragraf + satu angka kesenjangan (realisasi vs target)."},
        {"kelompok": "wajib", "tanya": "Apa bedanya dengan penelitian terdahulu?",
         "siapkan": "Tabel 3 studi: konteks, metode, temuan, posisi penelitian ini."},
        {"kelompok": "wajib", "tanya": "Kenapa memakai metode ini, bukan yang lain?",
         "siapkan": "Alasan berbasis karakteristik data (skala, sebaran, n)."},
        {"kelompok": "wajib", "tanya": "Apa simpulan utama?",
         "siapkan": f"{max(len(sim), 1)} butir, satu kalimat masing-masing, ada angka."},
        {"kelompok": "wajib", "tanya": "Apa kontribusi dan keterbatasan penelitian ini?",
         "siapkan": "Kontribusi teoretis + praktis dipisah; 3 keterbatasan konkret."},
    ])

    # --- 7. pertanyaan dari angka kunci ---
    r2 = re.search(r"R\s*²?\s*=\s*0?[.,](\d+)", teks)
    if r2:
        nilai = int(r2.group(1)) / (10 ** len(r2.group(1)))
        sisa = round((1 - nilai) * 100)
        pertanyaan.append({
            "kelompok": "angka",
            "tanya": f"R² = {nilai:g}. Berarti {sisa}% variasi dijelaskan oleh apa?",
            "siapkan": "Sebut faktor di luar model + alasan tidak dimasukkan."})

    if re.search(r"p\s*=\s*0[.,]000", teks, re.I):
        peringatan.append({"kode": "p_nol",
                           "pesan": "Ditulis 'p = 0,000' — nilai p tidak pernah tepat nol.",
                           "saran": "Tulis 'p < 0,001'."})
        pertanyaan.append({
            "kelompok": "angka",
            "tanya": "Anda menulis p = 0,000. Apakah itu artinya peluangnya nol?",
            "siapkan": "Jawab: p < 0,001; ditulis 0,000 karena pembulatan perangkat lunak."})

    # --- 8. kartu angka ---
    angka_kunci = []
    for pola, label in (
            (r"R\s*²?\s*=\s*[-−]?0?[.,]\d+", "R²"),
            (r"\bp\s*[=<>]\s*0?[.,]\d+", "p"),
            (r"β\s*=\s*[-−]?\d+[.,]?\d*", "β"),
            (r"\bt\s*=\s*[-−]?\d+[.,]?\d*", "t"),
            (r"\bF\s*=\s*\d+[.,]?\d*", "F"),
            (r"\bn\s*=\s*\d+", "n"),
            (r"\b\d+[.,]?\d*\s*%", "persen"),
            (r"\br\s*=\s*[-−]?0?[.,]\d+", "r")):
        for m in re.finditer(pola, teks):
            teks_m = m.group(0).strip()
            if teks_m not in [a["nilai"] for a in angka_kunci]:
                angka_kunci.append({"nilai": teks_m, "jenis": label})
    info["angka_kunci"] = angka_kunci[:12]

    return {"galat": galat, "peringatan": peringatan, "pertanyaan": pertanyaan, "info": info}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("berkas")
    ap.add_argument("--pertanyaan", action="store_true", help="cetak daftar pertanyaan penguji")
    ap.add_argument("--kartu-angka", action="store_true", help="cetak kartu angka kunci")
    ap.add_argument("--json", help="tulis hasil ke JSON")
    args = ap.parse_args()

    try:
        teks = open(args.berkas, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print(f"GAGAL membaca {args.berkas}: {e}", file=sys.stderr)
        return 2
    if len(teks.strip()) < 200:
        print("Naskah terlalu pendek untuk diaudit.", file=sys.stderr)
        return 2

    hasil = audit(teks)
    info, galat, peringatan, pertanyaan = (hasil["info"], hasil["galat"],
                                           hasil["peringatan"], hasil["pertanyaan"])

    if args.kartu_angka:
        print("# Kartu Angka Kunci\n")
        if not info.get("angka_kunci"):
            print("_Tidak ada angka statistik yang terdeteksi._")
        for a in info.get("angka_kunci", []):
            print(f"- [ ] `{a['nilai']}` — {a['jenis']}")
        print("\n> Hafalkan yang bertanda centang. Jangan mengandalkan ingatan saat tekanan.")
        return 0

    if args.pertanyaan:
        kel = {}
        for p in pertanyaan:
            kel.setdefault(p["kelompok"], []).append(p)
        urut = ["wajib", "konsistensi", "angka", "sampel", "klaim"]
        for k in urut + [k for k in kel if k not in urut]:
            if k not in kel:
                continue
            print(f"\n## Kelompok {k.upper()} ({len(kel[k])})\n")
            for i, p in enumerate(kel[k], 1):
                print(f"{i}. **{p['tanya']}**")
                print(f"   → siapkan: {p['siapkan']}\n")
        print(f"Total pertanyaan: {len(pertanyaan)}")
        if args.json:
            json.dump(hasil, open(args.json, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
        return 1 if galat else 0

    print("=== Struktur ===")
    print(f"  rumusan masalah : {info.get('jumlah_rumusan', 0)}")
    print(f"  tujuan          : {info.get('jumlah_tujuan', 0)}")
    print(f"  simpulan        : {info.get('jumlah_simpulan', 0)}")
    print(f"  n terkecil      : {info.get('n_terkecil', '-')}")
    print(f"  angka kunci     : {len(info.get('angka_kunci', []))} terdeteksi")

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
        print("\nTidak ada temuan.")

    print(f"\nPertanyaan penguji yang dibangkitkan: {len(pertanyaan)} "
          f"(lihat --pertanyaan)")
    print(f"Ringkasan: {len(galat)} galat, {len(peringatan)} peringatan")

    if args.json:
        json.dump(hasil, open(args.json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"JSON: {args.json}")
    return 1 if galat else 0


if __name__ == "__main__":
    sys.exit(main())
