#!/usr/bin/env python3
"""Periksa Ringkasan/Abstract dan kelengkapan identitas halaman judul.

Pemakaian:
    python3 periksa_ringkasan.py naskah.md profil-kampus.yaml
    python3 periksa_ringkasan.py skripsi.docx profil-kampus.yaml --json laporan.json

Yang diperiksa (angka diambil dari `ringkasan:` profil kampus):
  1. Ringkasan ada dan panjangnya dalam rentang kata yang ditetapkan panduan
  2. Ringkasan memuat empat unsur wajib (masalah/dampak, metode, hasil, manfaat)
  3. Kata kunci ada dan jumlahnya tidak melebihi batas
  4. Abstract ada dan panjangnya sebanding dengan Ringkasan
  5. Judul pada halaman judul tidak melebihi batas kata yang lazim

Kode keluar:
    0  lulus (peringatan boleh ada)
    1  ada galat
    2  berkas/profil tidak terbaca atau profil tanpa blok `ringkasan:`
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# Unsur yang wajib muncul di Ringkasan — dicocokkan lewat penanda kata, bukan
# makna. Ini pemeriksa pola; nilainya tetap harus dibaca manusia.
UNSUR = {
    # Kalimat masalah dalam ringkasan jarang memakai kata "masalah" — biasanya
    # berbentuk "belum memiliki", "masih manual", "rawan kesalahan", "lambat".
    # Pola ini menangkap bentuk-bentuk itu supaya tidak ada peringatan palsu.
    "masalah": r"(masalah|permasalahan|kendala|kesulitan|tantangan|gap|"
               r"belum\s+(?:memiliki|ada|optimal|terpadu|terintegrasi|efisien)|"
               r"masih\s+(?:manual|terpisah|konvensional|sulit|lambat)|"
               r"rawan\s+(?:kesalahan|error|hilang|duplikasi)|"
               r"tidak\s+efisien|kurang\s+efektif|memakan\s+waktu|"
               r"perlu\s+ditingkatkan|terhambat)",
    "metode": r"(metode|metodologi|pendekatan|model|algoritma|framework|"
              r"waterfall|scrum|prototype|kualitatif|kuantitatif|r&d|"
              r"penelitian\s+ini\s+menggunakan)",
    "hasil": r"(hasil|menghasilkan|diperoleh|menunjukkan|akurasi|"
             r"berhasil|tercapai|pengujian|evaluasi|nilai)",
    "manfaat": r"(manfaat|memudahkan|membantu|meningkatkan|efisiensi|"
               r"dapat\s+digunakan|diharapkan|kontribusi)",
}


def baca(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            sys.exit("GAGAL: butuh python-docx untuk .docx (pip install python-docx)")
        d = Document(path)
        baris = []
        for p in d.paragraphs:
            gaya = (p.style.name or "").lower()
            teks = p.text.strip()
            if not teks:
                continue
            m = re.match(r"heading (\d)", gaya)
            lvl = int(m.group(1)) if m else (1 if gaya in ("title", "judul") else 0)
            baris.append(("#" * lvl + " " + teks) if lvl else teks)
        return "\n".join(baris)
    if ext == ".pdf":
        import subprocess
        try:
            return subprocess.run(["pdftotext", "-layout", path, "-"],
                                  capture_output=True, text=True, timeout=60).stdout
        except FileNotFoundError:
            sys.exit("GAGAL: butuh pdftotext (apt-get install poppler-utils)")
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


RE_HEADING = re.compile(r"^\s*#{0,4}\s*(.+?)\s*$")


def ambil_bagian(teks: str, nama: str, pembatas: list[str]) -> str | None:
    """Ambil isi bagian bernama `nama` sampai salah satu `pembatas` muncul.

    Kembalian None berarti headingnya TIDAK ADA; string kosong berarti headingnya
    ada tetapi belum diisi. Dua kondisi itu butuh pesan berbeda — "tidak ada"
    menyuruh menambah bagian, "kosong" menyuruh mengisinya.
    """
    baris = teks.splitlines()
    mulai = None
    for i, b in enumerate(baris):
        bersih = re.sub(r"^\s*#+\s*", "", b).strip()
        if re.fullmatch(nama, bersih, re.I):
            mulai = i + 1
            break
    if mulai is None:
        return None
    keluar = []
    for b in baris[mulai:]:
        bersih = re.sub(r"^\s*#+\s*", "", b).strip()
        if any(re.fullmatch(p, bersih, re.I) for p in pembatas):
            break
        keluar.append(b)
    return "\n".join(keluar).strip()


def hitung_kata(s: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", s))


def periksa(teks: str, profil: dict) -> dict:
    rk = profil.get("ringkasan") or {}
    galat: list[dict] = []
    peringatan: list[dict] = []
    info: dict = {}

    panjang = rk.get("panjang_kata") or {}
    min_kata = int(panjang.get("min", 0) or 0)
    maks_kata = int(panjang.get("max", 0) or 0)
    maks_kunci = int(rk.get("kata_kunci_maks", 0) or 0)
    bahasa = (rk.get("bahasa") or "Indonesia")

    P_umum = [r"ABSTRACT", r"DAFTAR\s+ISI", r"KATA\s+PENGANTAR", r"BAB\s+I\b"]

    # --- Ringkasan ---
    ring = ambil_bagian(teks, r"RINGKASAN", P_umum)
    if ring is None:
        galat.append({
            "kode": "ringkasan_hilang",
            "pesan": "Bagian 'Ringkasan' tidak ditemukan.",
            "saran": f"Tambahkan heading 'RINGKASAN' berisi {min_kata}-{maks_kata} "
                     f"kata dalam {bahasa}, diikuti kata kunci."})
    elif not ring.strip():
        galat.append({
            "kode": "ringkasan_kosong",
            "pesan": "Heading 'Ringkasan' ada tetapi isinya kosong.",
            "saran": f"Isi {min_kata}-{maks_kata} kata: masalah & dampak, metode, "
                     f"hasil, dan pihak yang memanfaatkan; akhiri dengan kata kunci."})
        ring = ""
    else:
        # pisahkan baris kata kunci dari badan ringkasan
        m = re.search(r"kata\s*kunci\s*[:：]\s*(.+)", ring, re.I | re.S)
        badan = ring[:m.start()].strip() if m else ring
        n = hitung_kata(badan)
        info["ringkasan_kata"] = n
        if min_kata and n < min_kata:
            galat.append({
                "kode": "ringkasan_pendek",
                "pesan": f"Ringkasan {n} kata, panduan menetapkan minimal {min_kata}.",
                "saran": "Tambahkan unsur yang belum tercakup; jangan mengulang kalimat."})
        if maks_kata and n > maks_kata:
            galat.append({
                "kode": "ringkasan_panjang",
                "pesan": f"Ringkasan {n} kata, panduan menetapkan maksimal {maks_kata}.",
                "saran": "Padatkan; buang kalimat yang tidak menambah informasi."})

        hilang = [u for u, rx in UNSUR.items() if not re.search(rx, badan, re.I)]
        info["unsur_hilang"] = hilang
        if hilang:
            peringatan.append({
                "kode": "ringkasan_unsur_kurang",
                "pesan": f"Ringkasan belum menyebut unsur: {', '.join(hilang)}.",
                "saran": ("Ringkasan yang baik memuat masalah & dampaknya, metode, "
                          "hasil, dan pihak yang memanfaatkan.")})

        if m:
            kunci = [k.strip(" .;") for k in re.split(r"[,;]", m.group(1)) if k.strip(" .;")]
            kunci = [k for k in kunci if k and not re.fullmatch(r"[\d\W]+", k)]
            info["jumlah_kata_kunci"] = len(kunci)
            if maks_kunci and len(kunci) > maks_kunci:
                galat.append({
                    "kode": "kata_kunci_berlebih",
                    "pesan": f"{len(kunci)} kata kunci, panduan menetapkan maksimal {maks_kunci}.",
                    "saran": "Pilih istilah yang paling mewakili; buang sinonim."})
            if len(kunci) < 3:
                peringatan.append({
                    "kode": "kata_kunci_sedikit",
                    "pesan": f"Hanya {len(kunci)} kata kunci terdeteksi.",
                    "saran": "Umumnya 3-5 kata kunci agar naskah mudah ditemukan."})
        else:
            galat.append({
                "kode": "kata_kunci_hilang",
                "pesan": "Baris 'Kata Kunci:' tidak ditemukan di Ringkasan.",
                "saran": f"Tambahkan 'Kata Kunci: ..., ...' maksimal {maks_kunci} istilah."})

    # --- Abstract ---
    abst = ambil_bagian(teks, r"ABSTRACT", [r"DAFTAR\s+ISI", r"BAB\s+I\b"])
    if abst is None:
        galat.append({
            "kode": "abstract_hilang",
            "pesan": "Bagian 'Abstract' tidak ditemukan.",
            "saran": "Terjemahkan Ringkasan ke Bahasa Inggris; struktur sejajar."})
    elif not abst.strip():
        galat.append({
            "kode": "abstract_kosong",
            "pesan": "Heading 'Abstract' ada tetapi isinya kosong.",
            "saran": "Terjemahkan Ringkasan ke Bahasa Inggris; struktur sejajar, "
                     "diikuti baris 'Keywords:'."})
        abst = ""
    else:
        m = re.search(r"(keywords?|kata\s*kunci)\s*[:：]\s*(.+)", abst, re.I | re.S)
        badan = abst[:m.start()].strip() if m else abst
        n = hitung_kata(badan)
        info["abstract_kata"] = n
        if n and info.get("ringkasan_kata"):
            rasio = info["ringkasan_kata"] / n
            if rasio < 0.6 or rasio > 1.7:
                peringatan.append({
                    "kode": "abstract_tidak_sejajar",
                    "pesan": (f"Panjang Abstract ({n} kata) tidak sebanding dengan "
                              f"Ringkasan ({info['ringkasan_kata']} kata)."),
                    "saran": "Abstract adalah terjemahan Ringkasan, bukan versi ringkas lain."})
        if not m:
            peringatan.append({
                "kode": "keywords_hilang",
                "pesan": "Baris 'Keywords:' tidak ditemukan di Abstract.",
                "saran": "Tambahkan terjemahan kata kunci."})

    # --- judul ---
    sampul = profil.get("sampul") or {}
    batas_judul = int(sampul.get("judul_maks_kata", 0) or 0)
    if batas_judul:
        judul = ambil_bagian(teks, r"LEMBAR\s+JUDUL|HALAMAN\s+JUDUL", P_umum) or ""
        m = re.search(r"\*\*Judul:\*\*\s*(.+)", teks)
        if m:
            judul = m.group(1)
        if judul:
            baris_judul = [b for b in judul.splitlines()
                           if b.strip() and not b.strip().startswith("**")]
            if baris_judul:
                n = hitung_kata(" ".join(baris_judul))
                info["judul_kata"] = n
                if n > batas_judul:
                    peringatan.append({
                        "kode": "judul_kepanjangan",
                        "pesan": f"Judul {n} kata, lazimnya maksimal {batas_judul}.",
                        "saran": "Padatkan tanpa kehilangan variabel dan objek penelitian."})

    total = len(galat)
    return {"ok": total == 0, "kode": 1 if total else 0,
            "galat": galat, "peringatan": peringatan, "info": info}


def cetak(h: dict, profil: dict) -> None:
    k = profil.get("kampus") or {}
    rk = profil.get("ringkasan") or {}
    print(f"=== Ringkasan & Abstract vs {k.get('nama','(profil)')} ===")
    p = rk.get("panjang_kata") or {}
    print(f"  ketentuan: {p.get('min','?')}-{p.get('max','?')} kata, "
          f"kata kunci maks {rk.get('kata_kunci_maks','?')}, bahasa {rk.get('bahasa','?')}")
    i = h["info"]
    if "ringkasan_kata" in i:
        print(f"  ringkasan: {i['ringkasan_kata']} kata"
              + (f" | kata kunci {i['jumlah_kata_kunci']}" if "jumlah_kata_kunci" in i else ""))
    if "abstract_kata" in i:
        print(f"  abstract : {i['abstract_kata']} kata")
    if "judul_kata" in i:
        print(f"  judul    : {i['judul_kata']} kata")
    print()
    if h["galat"]:
        print(f"=== GALAT ({len(h['galat'])}) ===")
        for g in h["galat"]:
            print(f"  x [{g['kode']}] {g['pesan']}")
            print(f"    → {g.get('saran','')}")
        print()
    if h["peringatan"]:
        print(f"=== PERINGATAN ({len(h['peringatan'])}) ===")
        for g in h["peringatan"]:
            print(f"  ! [{g['kode']}] {g['pesan']}")
            print(f"    → {g.get('saran','')}")
        print()
    print(f"Ringkasan: {len(h['galat'])} galat, {len(h['peringatan'])} peringatan")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Periksa Ringkasan, Abstract, dan kata kunci terhadap profil kampus.",
        epilog="contoh: python3 periksa_ringkasan.py skripsi.md profil-kampus.yaml")
    ap.add_argument("naskah")
    ap.add_argument("profil")
    ap.add_argument("--json")
    a = ap.parse_args()

    for p in (a.naskah, a.profil):
        if not os.path.isfile(p):
            print(f"GAGAL: berkas tidak ada: {p}", file=sys.stderr)
            return 2
    try:
        import yaml
    except ImportError:
        print("GAGAL: butuh PyYAML (pip install pyyaml)", file=sys.stderr)
        return 2
    with open(a.profil, encoding="utf-8") as f:
        profil = yaml.safe_load(f)
    if not isinstance(profil, dict) or "ringkasan" not in profil:
        print("GAGAL: profil tidak memuat kunci 'ringkasan:'.", file=sys.stderr)
        return 2

    h = periksa(baca(a.naskah), profil)
    cetak(h, profil)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(h, f, ensure_ascii=False, indent=2)
        print(f"JSON: {a.json}")
    return h["kode"]


if __name__ == "__main__":
    sys.exit(main())
