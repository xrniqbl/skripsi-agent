#!/usr/bin/env python3
"""Uji kerangka template lengkap: semua bagian ada, penomoran benar, tata letak rapi.

Pemakaian:
    python3 tests/uji_template_lengkap.py <docx> <profil.yaml>

Kode keluar 1 bila ada yang kurang, dengan daftar apa yang kurang.

Kenapa uji terpisah, bukan inline di run_tests.sh: blok Python yang ditulis lewat
heredoc di dalam string multi-baris rawan rusak oleh escaping (\\n berubah jadi
baris baru) — dan kegagalan yang muncul adalah SyntaxError, bukan temuan asli.
"""
from __future__ import annotations

import os
import re
import sys
import zipfile

GAGAL: list[str] = []


def cek(nama: str, ok: bool, detail: str = "") -> None:
    print(("  OK  " if ok else "  X   ") + nama + (f" — {detail}" if detail else ""))
    if not ok:
        GAGAL.append(nama)


def main() -> int:
    if len(sys.argv) < 3:
        print("pemakaian: uji_template_lengkap.py <docx> <profil.yaml>", file=sys.stderr)
        return 2
    docx, profil_path = sys.argv[1], sys.argv[2]

    import yaml
    from docx import Document

    profil = yaml.safe_load(open(profil_path, encoding="utf8"))
    sis = profil["sistematika"]

    d = Document(docx)
    paragraf = [p.text.strip() for p in d.paragraphs if p.text.strip()]
    teks = "\n".join(paragraf).upper()

    # ---- 1. semua bagian awal & akhir ada ----
    # "Lembar Judul" diwujudkan sebagai SAMPUL: tidak ada heading "Lembar Judul"
    # di dokumen, melainkan judul + identitas. Diperiksa terpisah di butir 7.
    AWAL_TANPA_HEADING = {"LEMBAR JUDUL"}
    kurang = [i for i in (sis.get("bagian_awal") or [])
              if i.upper() not in teks and i.upper() not in AWAL_TANPA_HEADING]
    kurang += [i for i in (sis.get("bagian_akhir") or [])
               if i.upper() not in teks]
    cek("semua bagian awal & akhir ada", not kurang, ", ".join(kurang[:5]))

    # ---- 2. semua bab + subbab ada ----
    judul_map = sis.get("judul_bab") or {}
    kurang_bab = []
    for bab, sub in (sis.get("bab") or {}).items():
        judul = (judul_map.get(bab) or "").strip()
        if judul and judul.upper() not in teks:
            kurang_bab.append(f"{bab} ({judul})")
        for s in sub:
            bersih = re.sub(r"^\d+(\.\d+)*\.?\s*", "", s).strip()
            if bersih.upper() not in teks:
                kurang_bab.append(bersih)
    cek("semua bab & subbab ada", not kurang_bab, ", ".join(kurang_bab[:5]))

    # ---- 3. penomoran: numPr ada, awalan literal per bab ----
    z = zipfile.ZipFile(docx)
    doc_xml = z.read("word/document.xml").decode()
    num_xml = z.read("word/numbering.xml").decode()
    n_numpr = len(re.findall(r"<w:numPr>", num_xml) + re.findall(r"<w:numPr>", doc_xml))
    jumlah_sub = sum(len(v) for v in (sis.get("bab") or {}).values())
    cek("subbab ber-numPr", n_numpr >= jumlah_sub,
        f"{n_numpr} numPr untuk {jumlah_sub} subbab")

    n_bab = len(sis.get("bab") or {})
    awalan = [str(i) for i in range(1, n_bab + 1)
              if f'<w:lvlText w:val="{i}.%1."' in num_xml]
    cek("tiap bab punya awalan nomor literal", len(awalan) == n_bab,
        f"awalan ditemukan: {awalan}")

    # jangan sampai ada lvlText "%1.%2." yang membuat subbab jadi "1.1" di SEMUA bab
    cek("tidak memakai lvlText multi-level mentah",
        '<w:lvlText w:val="%1.%2."' not in num_xml,
        "lvlText '%1.%2.' memakai penghitung BAB, bukan nomor bab")

    # ---- 4. bagian dokumen & format nomor halaman ----
    n_seksi = len(d.sections)
    cek("jumlah seksi minimal 1 + jumlah bab", n_seksi >= 1 + n_bab,
        f"{n_seksi} seksi untuk {n_bab} bab")

    # ---- 5. tata letak: margin, font, spasi ----
    dok = profil.get("dokumen") or {}
    mar = dok.get("margin_cm") or {}
    s0 = d.sections[0]
    PETA_SISI = {"kiri": "left", "kanan": "right", "atas": "top", "bawah": "bottom"}
    for sisi, harap in (("kiri", mar.get("kiri")), ("kanan", mar.get("kanan")),
                        ("atas", mar.get("atas")), ("bawah", mar.get("bawah"))):
        if harap is None:
            continue
        dapat = getattr(s0, f"{PETA_SISI[sisi]}_margin").cm
        cek(f"margin {sisi} = {harap} cm", abs(dapat - float(harap)) < 0.02,
            f"{dapat:.2f} cm")

    normal = d.styles["Normal"]
    nama_font = (profil.get("font") or {}).get("nama")
    cek(f"font isi = {nama_font}", (normal.font.name or "") == nama_font,
        normal.font.name or "(tidak diset)")
    spasi_isi = (profil.get("spasi") or {}).get("isi")
    if spasi_isi is not None:
        dapat = normal.paragraph_format.line_spacing
        cek(f"spasi isi = {spasi_isi}", dapat == spasi_isi, str(dapat))

    # ---- 6. tidak ada paragraf kosong berlebih (spasi manual) ----
    kosong = sum(1 for p in d.paragraphs if not p.text.strip())
    cek("paragraf kosong <= 2", kosong <= 2, f"{kosong} paragraf kosong")

    # ---- 7. sampul: satu halaman, isinya lengkap ----
    cek("sampul memuat kata SKRIPSI", "SKRIPSI" in teks)
    kalimat = (profil.get("sampul") or {}).get("kalimat_diajukan")
    if kalimat:
        cek("sampul memuat kalimat 'Diajukan ...'",
            kalimat.upper() in teks)

    print()
    if GAGAL:
        print(f"GAGAL: {len(GAGAL)} pemeriksaan — {', '.join(GAGAL)}")
        return 1
    print("SEMUA LULUS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
