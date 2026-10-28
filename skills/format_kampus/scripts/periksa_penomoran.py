#!/usr/bin/env python3
"""Periksa penomoran subbab pada DOCX: apakah nomornya benar-benar akan muncul.

Pemakaian:
    python3 periksa_penomoran.py skripsi.docx profil-kampus.yaml
    python3 periksa_penomoran.py skripsi.docx profil-kampus.yaml --json lap.json

Kenapa perlu: membaca heading dari style saja tidak cukup. Nomor subbab di Word
datang dari `<w:numPr>` + `numbering.xml`, dan bisa gagal dengan empat cara yang
semuanya tampak normal di file .docx:

  1. Judul subbab TIDAK ber-numPr dan teksnya tidak diawali angka  → nomor hilang
  2. numPr memakai lvlText "%1." (bukan "2.%1.")                    → tampil "1." bukan "2.1."
  3. lvlText diberi awalan hard-code "2.%1." pada numId yang dipakai
     ulang di bab lain                                               → semua bab jadi "2.x"
  4. start bukan 1 pada level yang dipakai                         → mulai dari angka lain

Pemeriksa ini membaca numbering.xml, menghitung nomor efektif tiap judul, lalu
membandingkannya dengan pola penomoran di profil kampus
(`sistematika.penomoran_subbab_terbukti` atau contoh subbab "2.1.").

Hanya berlaku untuk .docx — untuk .md/.pdf nomor sudah berupa teks sehingga
periksa_sistematika.py yang menanganinya.

Kode keluar:
    0  lulus (peringatan boleh ada)
    1  ada galat
    2  berkas/profil tidak terbaca, atau bukan .docx
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

RE_BAB = re.compile(r"^\s*(BAB\s+([IVX]+|\d+))\s*$", re.I)
ROMAWI = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6,
          "VII": 7, "VIII": 8, "IX": 9, "X": 10}


def baca_numbering(docx_path: str) -> dict:
    """numId -> {ilvl: (numFmt, lvlText, start)} dari word/numbering.xml."""
    import zipfile
    with zipfile.ZipFile(docx_path) as z:
        if "word/numbering.xml" not in z.namelist():
            return {}
        s = z.read("word/numbering.xml").decode("utf-8", "replace")

    num2abs = dict(re.findall(
        r'<w:num w:numId="(\d+)"[^>]*>\s*<w:abstractNumId w:val="(\d+)"', s))
    absblok = dict(re.findall(
        r'<w:abstractNum w:abstractNumId="(\d+)"[^>]*>(.*?)</w:abstractNum>', s, re.S))

    hasil: dict[str, dict[int, tuple[str, str, int]]] = {}
    for nid, aid in num2abs.items():
        body = absblok.get(aid, "")
        lvl: dict[int, tuple[str, str, int]] = {}
        for m in re.finditer(r'<w:lvl w:ilvl="(\d+)"[^>]*>(.*?)</w:lvl>', body, re.S):
            il, lb = int(m.group(1)), m.group(2)
            fmt = re.search(r'<w:numFmt w:val="([^"]+)"', lb)
            txt = re.search(r'<w:lvlText w:val="([^"]*)"', lb)
            start = re.search(r'<w:start w:val="(\d+)"', lb)
            lvl[il] = (fmt.group(1) if fmt else "decimal",
                       txt.group(1) if txt else "",
                       int(start.group(1)) if start else 1)
        hasil[nid] = lvl
    return hasil


def judul_subdocx(docx_path: str) -> list[dict]:
    """Ambil paragraf pendek yang berperan sebagai judul (bold atau style Heading)."""
    from docx import Document
    d = Document(docx_path)
    out = []
    for i, p in enumerate(d.paragraphs):
        teks = p.text.strip()
        if not teks or len(teks) > 90:
            continue
        xml = p._p.xml
        gaya = (p.style.name or "").lower()
        tebal = any(r.font.bold for r in p.runs if r.text.strip()) or "<w:b/>" in xml
        ber_heading = gaya.startswith("heading") or gaya in ("title", "judul")
        nid = re.search(r'<w:numId w:val="(\d+)"', xml)
        ilv = re.search(r'<w:ilvl w:val="(\d+)"', xml)
        # kandidat judul: ber-heading, ber-numPr, atau pendek + tebal + tanpa titik akhir
        if not (ber_heading or nid or (tebal and not teks.endswith("."))):
            continue
        out.append({
            "idx": i, "teks": teks,
            "numId": nid.group(1) if nid else None,
            "ilvl": int(ilv.group(1)) if ilv else 0,
            "style": p.style.name,
            "tebal": tebal,
        })
    return out


def nomor_efektif(lvl: dict[int, tuple[str, str, int]], ilvl: int,
                  hitung: dict[int, int]) -> str:
    """Hitung teks nomor yang akan tampil, mis. '2.1.' dari lvlText '2.%1.'."""
    if ilvl not in lvl:
        return ""
    fmt, txt, _start = lvl[ilvl]
    hasil = txt
    for k in range(0, ilvl + 1):
        hasil = hasil.replace(f"%{k+1}", str(hitung.get(k, 1)))
    return hasil


def periksa(docx: str, profil: dict) -> dict:
    sis = profil.get("sistematika") or {}
    contoh = ""
    for v in (sis.get("bab") or {}).values():
        for s in v:
            if re.match(r"^\d", s):
                contoh = s
                break
        if contoh:
            break
    pola = sis.get("penomoran_subbab_terbukti") or ""
    harap_bernomor = bool(contoh) or bool(pola)
    # apakah profil mengharapkan nomor subbab memuat nomor bab ("2.1.")?
    harap_awalan_bab = bool(re.match(r"^\d+\.\d+", contoh))

    numberings = baca_numbering(docx)
    judul = judul_subdocx(docx)
    galat: list[dict] = []
    peringatan: list[dict] = []
    info: dict = {"jumlah_judul": len(judul), "numbering": len(numberings)}

    bab_aktif = None
    hitung: dict[int, int] = {}
    tanpa_nomor = []
    awalan_salah = []
    nomor_terlihat = []

    # Penomoran subbab hanya bermakna DI DALAM bab. Sebelum BAB I (halaman depan:
    # judul, nama, program studi) dan sesudah bab terakhir (DAFTAR RIWAYAT HIDUP,
    # LAMPIRAN) tidak ada subbab — memeriksanya di sana hanya menghasilkan galat
    # palsu pada teks sampul yang memang tidak bernomor.
    RE_BAGIAN_BUKAN_BAB = re.compile(
        r"^\s*(DAFTAR\s+PUSTAKA|DAFTAR\s+RIWAYAT|DAFTAR\s+SIMBOL|DAFTAR\s+GAMBAR|"
        r"DAFTAR\s+TABEL|DAFTAR\s+LAMPIRAN|LAMPIRAN|RINGKASAN|ABSTRACT|"
        r"KATA\s+PENGANTAR|PERSEMBAHAN|LEMBAR\s+\w+|SURAT\s+\w+|"
        r"PANDUAN\s+PENGGUNAAN)\b", re.I)
    sudah_masuk_bab = False

    for j in judul:
        if RE_BAGIAN_BUKAN_BAB.match(j["teks"]):
            bab_aktif = None     # keluar dari bab: nomor tidak lagi dibandingkan
            continue

        m = RE_BAB.match(j["teks"])
        if m:
            n = m.group(2).upper()
            bab_aktif = ROMAWI.get(n, int(n) if n.isdigit() else None)
            hitung = {}          # penomoran subbab dimulai ulang tiap bab
            sudah_masuk_bab = True
            continue

        if not sudah_masuk_bab or bab_aktif is None:
            continue             # halaman depan / bagian akhir, bukan subbab

        # judul bab dua baris ("BAB I" / "PENDAHULUAN") — lewati baris kedua
        if j["teks"].isupper() and len(j["teks"].split()) <= 4 and not j["numId"]:
            continue
        if not j["tebal"] and not j["numId"]:
            continue

        punya_angka_teks = bool(re.match(r"^\d+(\.\d+)*\.?\s", j["teks"]))

        if not j["numId"]:
            if harap_bernomor and not punya_angka_teks:
                tanpa_nomor.append(j["teks"][:50])
            elif punya_angka_teks:
                nomor_terlihat.append(re.match(r"^\d+(\.\d+)*\.?", j["teks"]).group(0))
            continue

        lvl = numberings.get(j["numId"], {})
        hitung[j["ilvl"]] = hitung.get(j["ilvl"], 0) + 1
        nomor = nomor_efektif(lvl, j["ilvl"], hitung)
        nomor_terlihat.append(nomor or "(kosong)")

        if not nomor:
            galat.append({
                "kode": "numpr_tanpa_teks_nomor",
                "pesan": f"Judul '{j['teks'][:40]}' ber-numPr tetapi numbering.xml "
                         f"tidak mendefinisikan level {j['ilvl']} untuk numId {j['numId']}.",
                "saran": "Perbaiki definisi numbering di Word: pilih daftar bernomor "
                         "multilevel yang benar, jangan daftar biasa."})
            continue

        # cek awalan nomor bab: "2.1." vs "1."
        # Hanya berlaku bila level ini memang berformat "%1.%2." (atau awalan tetap).
        # Daftar upperRoman sederhana ("I.", "II.") di lampiran/riwayat hidup bukan
        # subbab dan tidak boleh dibandingkan dengan nomor bab.
        # Awalan bisa dua bentuk:
        #   a) multi-level  "%1.%2."  -> awalan dari penghitung level 0
        #   b) hard-code    "2.%1."   -> awalan angka literal di lvlText
        # Bentuk (b) rawan: numId dipakai ulang di bab lain maka semua bab
        # menampilkan "2.x". Keduanya harus diperiksa.
        lvl_txt = (lvl.get(j["ilvl"]) or ("", "", 1))[1]
        multi_level = lvl_txt.count("%") >= 2
        literal = re.match(r"^(\d+)\.", lvl_txt)
        if harap_awalan_bab and bab_aktif and (multi_level or literal):
            awalan = nomor.split(".")[0]
            if awalan.isdigit() and int(awalan) != bab_aktif:
                awalan_salah.append(
                    f"'{j['teks'][:34]}' → tampil '{nomor}', seharusnya "
                    f"'{bab_aktif}.{hitung.get(j['ilvl'], 1)}.'")

        # cek titik penutup bila profil memakainya (contoh: "1.1. Latar Belakang")
        harap_titik = bool(re.match(r"^\d+(?:\.\d+)+\.", contoh))
        if harap_titik and nomor and not nomor.endswith("."):
            galat.append({
                "kode": "nomor_tanpa_titik",
                "pesan": f"Nomor '{nomor}' pada '{j['teks'][:34]}' tanpa titik penutup; "
                         f"panduan memakai '{contoh}'.",
                "saran": f"Ubah lvlText numbering menjadi berakhir titik."})

    if tanpa_nomor:
        galat.append({
            "kode": "judul_tanpa_nomor",
            "pesan": (f"{len(tanpa_nomor)} judul subbab tanpa nomor dan tanpa numPr: "
                      f"{'; '.join(tanpa_nomor[:5])}"),
            "saran": ("Pakai daftar bernomor multilevel Word (numPr), atau tulis "
                      "nomornya manual di awal judul — jangan keduanya kosong.")})

    if awalan_salah:
        galat.append({
            "kode": "awalan_bab_salah",
            "pesan": (f"{len(awalan_salah)} subbab menampilkan nomor bab yang salah:"),
            "contoh": awalan_salah[:6],
            "saran": ("numId dipakai ulang lintas bab dengan lvlText berawalan tetap "
                      "(mis. '2.%1.'). Buat numId terpisah per bab, atau pakai "
                      "lvlText '%1.%2.' dengan level bab yang benar.")})

    info["nomor_terlihat"] = nomor_terlihat[:40]
    total = len(galat)
    return {"ok": total == 0, "kode": 1 if total else 0,
            "galat": galat, "peringatan": peringatan, "info": info}


def cetak(h: dict, profil: dict) -> None:
    k = profil.get("kampus") or {}
    print(f"=== Penomoran DOCX vs {k.get('nama','(profil)')} ===")
    i = h["info"]
    print(f"  judul diperiksa: {i.get('jumlah_judul',0)} | "
          f"definisi numbering: {i.get('numbering',0)}")
    if i.get("nomor_terlihat"):
        print(f"  nomor terbaca  : {', '.join(str(x) for x in i['nomor_terlihat'][:12])}")
    print()
    if h["galat"]:
        print(f"=== GALAT ({len(h['galat'])}) ===")
        for g in h["galat"]:
            print(f"  x [{g['kode']}] {g['pesan']}")
            for c in (g.get("contoh") or [])[:6]:
                print(f"      · {c}")
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
        description="Periksa penomoran subbab DOCX terhadap profil kampus.",
        epilog="contoh: python3 periksa_penomoran.py skripsi.docx profil-kampus.yaml")
    ap.add_argument("naskah")
    ap.add_argument("profil")
    ap.add_argument("--json")
    a = ap.parse_args()

    for p in (a.naskah, a.profil):
        if not os.path.isfile(p):
            print(f"GAGAL: berkas tidak ada: {p}", file=sys.stderr)
            return 2
    if not a.naskah.lower().endswith(".docx"):
        print("GAGAL: periksa_penomoran hanya untuk .docx — untuk .md/.pdf nomor "
              "sudah berupa teks, gunakan periksa_sistematika.py", file=sys.stderr)
        return 2
    try:
        import yaml
    except ImportError:
        print("GAGAL: butuh PyYAML (pip install pyyaml)", file=sys.stderr)
        return 2
    with open(a.profil, encoding="utf-8") as f:
        profil = yaml.safe_load(f)
    if not isinstance(profil, dict) or "sistematika" not in profil:
        print("GAGAL: profil tidak memuat kunci 'sistematika:'.", file=sys.stderr)
        return 2

    h = periksa(a.naskah, profil)
    cetak(h, profil)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(h, f, ensure_ascii=False, indent=2)
        print(f"JSON: {a.json}")
    return h["kode"]


if __name__ == "__main__":
    sys.exit(main())
