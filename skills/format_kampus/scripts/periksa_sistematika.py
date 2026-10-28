#!/usr/bin/env python3
"""Periksa kelengkapan sistematika naskah terhadap profil format kampus.

Pemakaian:
    python3 periksa_sistematika.py naskah.md profil-kampus.yaml
    python3 periksa_sistematika.py skripsi.docx profil-kampus.yaml --json laporan.json
    python3 periksa_sistematika.py naskah.md profil-kampus.yaml --abaikan-opsional

Yang diperiksa:
  1. Bagian awal  — semua item `sistematika.bagian_awal` ada, urutannya benar
  2. Bab          — setiap bab di `sistematika.bab` ada, dan setiap subbabnya ada
  3. Bagian akhir — semua item `sistematika.bagian_akhir` ada, urutannya benar
  4. Penomoran    — subbab memakai format penomoran profil (mis. "1.2." bukan "1.2")
  5. Caption      — penomoran "Tabel III.1" (Romawi kapital), bukan "Tabel 3.1"

Item bertanda opsional di SKILL.md (Daftar Simbol/Gambar/Tabel/Lampiran,
Surat Keterangan Riset) dilaporkan sebagai peringatan, bukan galat, bila
dijalankan dengan --abaikan-opsional. Tanpa flag itu, semua dilaporkan galat.

Kode keluar:
    0  lulus (peringatan boleh ada)
    1  ada galat
    2  profil atau naskah tidak terbaca
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# Item bagian awal/akhir yang di panduan ditandai "*jika ada / sesuai kebutuhan".
OPSIONAL_DEFAULT = {
    "daftar simbol", "daftar gambar", "daftar tabel", "daftar lampiran",
    "surat keterangan riset", "surat keterangan pkl",
    "daftar singkatan", "daftar notasi",
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
            # bangun heading markdown dari style agar pemetaan sama dengan .md
            lvl = 0
            m = re.match(r"heading (\d)", gaya)
            if m:
                lvl = int(m.group(1))
            elif gaya in ("title", "judul"):
                lvl = 1
            baris.append(("#" * lvl + " " + teks) if lvl else teks)
        for t in d.tables:
            for r in t.rows:
                baris.append(" | ".join(c.text for c in r.cells))
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


def normal(s: str) -> str:
    """Normalisasi untuk pencocokan: buang penomoran, tanda baca, huruf kecil."""
    s = re.sub(r"^\s*#+\s*", "", s)                 # markdown heading
    s = re.sub(r"^\s*(?:BAB\s+[IVX]+|\d+(?:\.\d+)*\.?)\s*", "", s, flags=re.I)
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def cocok(judul_profil: str, baris: str) -> bool:
    """True bila baris naskah dianggap menyajikan judul profil (longgar)."""
    a, b = normal(judul_profil), normal(baris)
    if not a or not b:
        return False
    if a == b:
        return True
    # toleransi: judul profil terkandung utuh di baris (mis. "DAFTAR PUSTAKA" di
    # baris "DAFTAR PUSTAKA" dengan nomor halaman menempel)
    if a in b and len(a) >= 6:
        return True
    # toleransi kata kunci: semua kata bermakna judul ada di baris
    kata = [k for k in a.split() if len(k) > 3]
    return bool(kata) and all(k in b.split() for k in kata)


def cocok_ketat(judul_profil: str, baris: str) -> bool:
    """True hanya bila baris SAMA PERSIS dengan judul profil (setelah normalisasi).

    Dipakai lebih dulu supaya "Lampiran" tidak tertukar dengan "Daftar Lampiran"
    — kesalahan yang membuat pemeriksa urutan melaporkan galat palsu.
    """
    a, b = normal(judul_profil), normal(baris)
    return bool(a) and a == b


def periksa(teks: str, profil: dict, abaikan_opsional: bool) -> dict:
    sis = profil.get("sistematika") or {}
    baris = [b for b in teks.splitlines() if b.strip()]
    galat: list[dict] = []
    peringatan: list[dict] = []
    info: dict = {}

    # ---------- 1 & 3. bagian awal dan akhir ----------
    def cek_urutan(daftar: list[str], nama: str, kode_prefix: str) -> None:
        # dua tahap: cocok ketat dulu (cegah "Lampiran" vs "Daftar Lampiran"),
        # lalu longgar untuk sisa item. Baris yang sudah dipakai item lain tidak
        # boleh dipakai ulang.
        posisi: list[tuple[int, str]] = []
        hilang: list[str] = []
        terpakai: set[int] = set()
        belum: list[str] = []
        for item in daftar or []:
            idx = next((i for i, b in enumerate(baris)
                        if i not in terpakai and cocok_ketat(item, b)), None)
            if idx is None:
                belum.append(item)
            else:
                terpakai.add(idx)
                posisi.append((idx, item))
        for item in belum:
            idx = next((i for i, b in enumerate(baris)
                        if i not in terpakai and cocok(item, b)), None)
            if idx is None:
                hilang.append(item)
            else:
                terpakai.add(idx)
                posisi.append((idx, item))
        for item in hilang:
            opsional = normal(item) in OPSIONAL_DEFAULT
            masuk = {
                "kode": f"{kode_prefix}_hilang",
                "pesan": f"{nama}: '{item}' tidak ditemukan.",
                "saran": (f"Tambahkan bagian '{item}' sesuai urutan panduan."
                          + (" (panduan menandainya opsional — abaikan bila memang "
                             "tidak diperlukan)" if opsional else "")),
            }
            if opsional and abaikan_opsional:
                peringatan.append(masuk)
            else:
                galat.append(masuk)
        # urutan
        for i in range(1, len(posisi)):
            if posisi[i][0] < posisi[i - 1][0]:
                galat.append({
                    "kode": f"{kode_prefix}_urutan",
                    "pesan": (f"{nama}: '{posisi[i][1]}' muncul SEBELUM "
                              f"'{posisi[i-1][1]}', seharusnya sesudahnya."),
                    "saran": "Susun ulang mengikuti urutan pada profil kampus."})
                break
        info[nama] = {"ditemukan": len(posisi), "diharapkan": len(daftar or []),
                      "hilang": hilang}

    cek_urutan(sis.get("bagian_awal") or [], "bagian awal", "awal")
    cek_urutan(sis.get("bagian_akhir") or [], "bagian akhir", "akhir")

    # ---------- 2. bab dan subbab ----------
    bab_profil = sis.get("bab") or {}
    bab_naskah: dict[str, list[str]] = {}
    bab_aktif = None
    RE_BAB = re.compile(r"^\s*#*\s*(BAB\s+([IVX]+|\d+))\b", re.I)
    for b in baris:
        m = RE_BAB.match(b)
        if m:
            nomor = m.group(2).upper()
            romawi = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V", "6": "VI"}
            bab_aktif = "BAB " + romawi.get(nomor, nomor)
            bab_naskah.setdefault(bab_aktif, [])
            continue
        if bab_aktif:
            bab_naskah[bab_aktif].append(b)

    info["bab_ditemukan"] = sorted(bab_naskah)
    for bab, subbab_wajib in bab_profil.items():
        if bab not in bab_naskah:
            galat.append({
                "kode": "bab_hilang",
                "pesan": f"{bab} tidak ditemukan.",
                "saran": f"Tambahkan heading '{bab} ...' sesuai panduan."})
            continue
        isi = bab_naskah[bab]
        hilang = [s for s in subbab_wajib
                  if not any(cocok(s, b) for b in isi)]
        for s in hilang:
            galat.append({
                "kode": "subbab_hilang",
                "pesan": f"{bab}: subbab '{s}' tidak ditemukan.",
                "saran": ("Judul subbab ditetapkan panduan — pakai persis, jangan "
                          "mengarang judul sendiri.")})

    # ---------- 4. format penomoran subbab ----------
    # Bila profil memakai titik ("1.2."), naskah tanpa titik dilaporkan.
    contoh_subbab = next(iter(
        (s for v in bab_profil.values() for s in v if re.match(r"^\d", s))), "")
    pakai_titik = bool(re.match(r"^\d+(\.\d+)+\.", contoh_subbab))
    if pakai_titik:
        RE_SUB_TANPA_TITIK = re.compile(
            r"^\s*#*\s*(\d+\.\d+(?:\.\d+)*)\s+[^\n]+", re.M)
        salah = []
        for m in RE_SUB_TANPA_TITIK.finditer(teks):
            if re.match(r"^\s*#*\s*\d+(\.\d+)+\.\s", m.group(0)):
                continue
            # tampilkan hanya nomor + judul, tanpa penanda markdown
            salah.append(re.sub(r"^\s*#*\s*", "", m.group(0).strip()))
        if salah:
            peringatan.append({
                "kode": "penomoran_tanpa_titik",
                "pesan": (f"{len(salah)} subbab tidak memakai titik penutup "
                          f"(panduan: '2.1.' bukan '2.1')."),
                "contoh": salah[:4],
                "saran": "Tambahkan titik setelah nomor subbab sesuai contoh panduan."})

    # ---------- 5. penomoran caption ----------
    cap = profil.get("caption") or {}
    penomoran = (cap.get("tabel") or {}).get("penomoran", "")
    if "romawi" in penomoran.lower():
        RE_CAP_ARAB = re.compile(r"\b(Tabel|Gambar)\s+(\d+)[.\-]\s*\d", re.I)
        salah = [m.group(0) for m in RE_CAP_ARAB.finditer(teks)]
        if salah:
            galat.append({
                "kode": "caption_angka_arab",
                "pesan": (f"{len(salah)} caption memakai angka Arab "
                          f"(mis. '{salah[0]}'), panduan mewajibkan angka Romawi per bab."),
                "contoh": salah[:4],
                "saran": "'Tabel 4.1' → 'Tabel IV.1'; 'Gambar 3.2' → 'Gambar III.2'."})

    total = len(galat)
    return {"ok": total == 0, "kode": 1 if total else 0,
            "galat": galat, "peringatan": peringatan, "info": info}


def cetak(h: dict, profil: dict) -> None:
    k = profil.get("kampus") or {}
    print(f"=== Sistematika vs {k.get('nama','(profil)')} ===")
    for nama, d in (h.get("info") or {}).items():
        if isinstance(d, dict) and "ditemukan" in d:
            tanda = "OK" if d["ditemukan"] == d["diharapkan"] else "KURANG"
            print(f"  {nama:14}: {d['ditemukan']}/{d['diharapkan']} {tanda}")
    if h["info"].get("bab_ditemukan"):
        print(f"  bab            : {', '.join(h['info']['bab_ditemukan'])}")
    print()
    if h["galat"]:
        print(f"=== GALAT ({len(h['galat'])}) ===")
        for g in h["galat"]:
            print(f"  x [{g['kode']}] {g['pesan']}")
            for c in (g.get("contoh") or [])[:4]:
                print(f"      · {c}")
            print(f"    → {g.get('saran','')}")
        print()
    if h["peringatan"]:
        print(f"=== PERINGATAN ({len(h['peringatan'])}) ===")
        for g in h["peringatan"]:
            print(f"  ! [{g['kode']}] {g['pesan']}")
            for c in (g.get("contoh") or [])[:4]:
                print(f"      · {c}")
            print(f"    → {g.get('saran','')}")
        print()
    print(f"Ringkasan: {len(h['galat'])} galat, {len(h['peringatan'])} peringatan")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Periksa sistematika naskah terhadap profil format kampus.",
        epilog="contoh: python3 periksa_sistematika.py skripsi.md profil-kampus.yaml")
    ap.add_argument("naskah")
    ap.add_argument("profil")
    ap.add_argument("--abaikan-opsional", action="store_true",
                    help="bagian bertanda opsional di panduan tidak dihitung galat")
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
    if not isinstance(profil, dict) or "sistematika" not in profil:
        print("GAGAL: profil tidak memuat kunci 'sistematika'.", file=sys.stderr)
        return 2

    h = periksa(baca(a.naskah), profil, a.abaikan_opsional)
    cetak(h, profil)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(h, f, ensure_ascii=False, indent=2)
        print(f"JSON: {a.json}")
    return h["kode"]


if __name__ == "__main__":
    sys.exit(main())
