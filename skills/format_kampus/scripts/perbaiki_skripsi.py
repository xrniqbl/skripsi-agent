#!/usr/bin/env python3
"""Perbaiki & audit DOCX skripsi terhadap aturan format wajib (margin, font,
warna, penomoran bagian awal Romawi / pokok+akhir Arab).

Pemakaian:
    python3 perbaiki_skripsi.py dokumen.docx --profil profil-kampus.yaml
    python3 perbaiki_skripsi.py dokumen.docx --profil p.yaml --cek-saja
    python3 perbaiki_skripsi.py dokumen.docx --profil p.yaml --pdf render.pdf

Kenapa skrip ini ada, padahal `audit_docx.py` sudah ada: auditor hanya
MELAPORKAN. Dokumen mahasiswa yang sudah jadi (dari template lama, hasil
konversi, atau kiriman pembimbing) gagal di tempat-tempat yang sama berulang
kali — font tema, warna biru pada caption, nomor halaman yang campur aduk
antara Romawi dan Arab. Skrip ini memperbaiki tanpa menyentuh isi naskah.

Tiga pekerjaan, dalam urutan ini:

1. FONT & WARNA (paket XML)
   - Semua atribut font tema (asciiTheme/hAnsiTheme/eastAsiaTheme/cstheme)
     dibuang dan diganti literal. Tanpa ini Word menampilkan Aptos/Calibri
     walau style menulis Times New Roman.
   - Semua w:color non-hitam diganti 000000 (putih dipertahankan: itu teks di
     atas latar gelap pada style tabel bawaan yang tidak dipakai skripsi).

2. NOMOR HALAMAN (per seksi)
   - Bagian awal  -> lowerRoman, mulai i, posisi tengah bawah.
   - Bagian pokok -> decimal, mulai 1, halaman awal bab tengah bawah,
     halaman lain kanan atas.
   - Bagian akhir -> decimal LANJUTAN (tanpa w:start) — kesalahan paling
     sering: Daftar Pustaka kembali ke 1.
   - Zona ditentukan dari judul Heading 1 yang ada di dokumen.

3. LAPORAN
   Ringkasan lulus/gagal per butir, kode keluar 1 bila masih ada yang gagal.

Yang TIDAK dilakukan skrip ini: mengubah teks, menambah/menghapus bab, atau
memperbaiki sistematika. Untuk itu ada periksa_sistematika.py dan gerbang
gate_naskah.sh.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HITAM = "000000"
PUTIH = "FFFFFF"
JUDUL_BAB = re.compile(r"^BAB\s+([IVX]+|\d+)\b", re.I)

# Judul yang menandai mulainya bagian akhir (dicocokkan tanpa peka huruf besar).
AWAL_AKHIR_BAWAAN = ["Daftar Pustaka", "Daftar Riwayat Hidup", "Lampiran",
                     "Lembar Konsultasi Bimbingan", "Surat Keterangan Riset"]
# Judul bagian awal: apa pun sebelum bab pertama yang berupa Heading 1.
AWAL_JUDUL_BAWAAN = [
    "Lembar Judul", "Halaman Judul", "Persembahan", "Surat Pernyataan Keaslian Skripsi",
    "Surat Pernyataan Persetujuan Publikasi Karya Ilmiah", "Lembar Persetujuan",
    "Lembar Pengesahan", "Halaman Pengesahan", "Panduan Penggunaan Hak Cipta",
    "Kata Pengantar", "Ringkasan", "Abstrak", "Abstract", "Daftar Isi",
    "Daftar Simbol", "Daftar Gambar", "Daftar Tabel", "Daftar Lampiran",
]


# ------------------------------------------------------------------ paket XML
def _ganti_rfonts(xml: str, nama_font: str) -> str:
    def repl(m):
        tag = m.group(0)
        tutup_sendiri = tag.rstrip().endswith("/>")
        isi = tag[len("<w:rFonts"):].rstrip()
        if tutup_sendiri:
            isi = isi[:-1].rstrip()
        attrs = dict(re.findall(r'([\w:]+)="([^"]*)"', isi))
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            attrs.pop(a, None)
        for slot in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            attrs[slot] = nama_font
        urut = ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs")
        sisa = [(k, v) for k, v in attrs.items() if k not in urut]
        bagian = [f'{k}="{attrs[k]}"' for k in urut] + [f'{k}="{v}"' for k, v in sisa]
        return "<w:rFonts " + " ".join(bagian) + ("/>" if tutup_sendiri else ">")
    return re.sub(r"<w:rFonts[^>]*?/?>", repl, xml)


def _hitamkan(xml: str) -> str:
    def ganti(m):
        tag = m.group(0)
        v = re.search(r'w:val="([^"]*)"', tag)
        if v and v.group(1).upper() == PUTIH:
            return tag
        return f'<w:color w:val="{HITAM}"/>'
    xml = re.sub(r"<w:color\b[^>]*/>", ganti, xml)
    # docDefaults wajib punya warna literal; tanpa itu Word memakai warna tema.
    m = re.search(r"<w:rPrDefault>\s*<w:rPr>(.*?)</w:rPr>", xml, re.S)
    if m and "<w:color" not in m.group(1):
        xml = xml[:m.start(1)] + m.group(1) + f'<w:color w:val="{HITAM}"/>' + xml[m.end(1):]
    return xml


def bersihkan_paket(path: str, nama_font: str) -> dict:
    """Tulis ulang paket: font literal, semua warna hitam. Kembalikan statistik."""
    stat = {"rfonts": 0, "warna": 0}
    zin = zipfile.ZipFile(path)
    tmp = path + ".bersih"
    zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename.startswith("word/") and item.filename.endswith(".xml"):
            xml = data.decode("utf8")
            sebelum = xml
            xml = _ganti_rfonts(xml, nama_font)
            if xml != sebelum:
                stat["rfonts"] += 1
            n_warna = len(re.findall(r'<w:color\b[^>]*w:val="(?!000000|FFFFFF)', xml))
            xml = _hitamkan(xml)
            stat["warna"] += n_warna
            if item.filename.endswith("theme1.xml"):
                xml = re.sub(r'<a:latin typeface="[^"]*"',
                             f'<a:latin typeface="{nama_font}"', xml)
            data = xml.encode("utf8")
        zout.writestr(item, data)
    zout.close()
    zin.close()
    shutil.move(tmp, path)
    return stat


# ------------------------------------------------------------------ dokumen
def _bagian_nomor(seksi, fmt: str, mulai: int | None, di_header: bool,
                  jarak_bawah_cm: float | None, jarak_atas_cm: float | None,
                  sembunyi: bool = False, awal_bab_tengah: bool = False) -> None:
    """Set format nomor halaman satu seksi + tulis field PAGE di wadah yang benar.

    `awal_bab_tengah=True` menerapkan aturan panduan 4.5 untuk seksi berisi bab:
    halaman PERTAMA seksi bernomor tengah bawah, halaman lanjutannya kanan atas.
    Itu butuh `titlePg` aktif + dua wadah berbeda (first page vs default).
    """
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm

    sectPr = seksi._sectPr
    for lama in sectPr.findall(qn("w:pgNumType")):
        sectPr.remove(lama)
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:fmt"), fmt)
    if mulai is not None:
        pg.set(qn("w:start"), str(mulai))
    sectPr.append(pg)

    if jarak_bawah_cm is not None:
        seksi.footer_distance = Cm(float(jarak_bawah_cm))
    if jarak_atas_cm is not None:
        seksi.header_distance = Cm(float(jarak_atas_cm))

    # Seksi baru mewarisi titlePg -> halaman pertama memakai footer "first".
    # Dibiarkan, nomor bisa hilang tepat di halaman pembuka bab.
    seksi.different_first_page_header_footer = bool(awal_bab_tengah)

    for wadah, lawan in ((seksi.header, seksi.footer), (seksi.footer, seksi.header)):
        wadah.is_linked_to_previous = False
        lawan.is_linked_to_previous = False

    def kosongkan(wadah):
        paras = list(wadah.paragraphs)
        if not paras:
            wadah.add_paragraph()
            return
        for p_ in paras[1:]:
            p_._p.getparent().remove(p_._p)
        for r_ in list(paras[0].runs):
            r_._r.getparent().remove(r_._r)

    if sembunyi:
        kosongkan(seksi.header)
        kosongkan(seksi.footer)
        return

    if awal_bab_tengah:
        # halaman pertama bab: tengah bawah (footer "first"), header kosong
        kosongkan(seksi.first_page_header)
        tulis_nomor(seksi.first_page_footer, "center")
        # halaman lanjutan: KANAN ATAS (header default), footer kosong
        kosongkan(seksi.footer)
        tulis_nomor(seksi.header, "right")
        return

    wadah = seksi.header if di_header else seksi.footer
    lawan = seksi.footer if di_header else seksi.header
    kosongkan(lawan)
    tulis_nomor(wadah, "right" if di_header else "center")


def tulis_nomor(wadah, rata: str) -> None:
    """Tulis field PAGE ke wadah header/footer. `rata`: center | right | left."""
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    JENIS = {"center": WD_ALIGN_PARAGRAPH.CENTER,
             "right": WD_ALIGN_PARAGRAPH.RIGHT,
             "left": WD_ALIGN_PARAGRAPH.LEFT}
    wadah.is_linked_to_previous = False
    p = wadah.paragraphs[0] if wadah.paragraphs else wadah.add_paragraph()
    for r_ in list(p.runs):
        r_._r.getparent().remove(r_._r)
    p.alignment = JENIS.get(rata, WD_ALIGN_PARAGRAPH.CENTER)
    run = p.add_run()
    b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin")
    i = OxmlElement("w:instrText"); i.set(qn("xml:space"), "preserve"); i.text = " PAGE "
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end")
    run._r.append(b); run._r.append(i); run._r.append(e)


def _zona_dokumen(doc, profil: dict) -> list[str]:
    """Petakan indeks seksi -> zona ('awal'|'pokok'|'akhir'), satu entri per seksi.

    Cara menentukan: bagi paragraf menjadi rentang per seksi. Paragraf yang
    membawa `w:sectPr` di pPr adalah paragraf TERAKHIR seksi itu; isi seksi
    berikutnya mulai pada paragraf sesudahnya.

    Versi pertama fungsi ini membaca "judul terakhir sebelum paragraf
    bersectPr" — itu judul seksi SEBELUMNYA, sehingga semua seksi berlabel
    bagian awal dan nomor Arab hilang sama sekali. Ditemukan hanya karena
    hasilnya diuji pada dokumen nyata (21 seksi, semuanya berzona 'awal').
    """
    from docx.oxml.ns import qn

    sis = profil.get("sistematika") or {}
    awal_judul = {str(x).strip().lower()
                  for x in (sis.get("bagian_awal") or [])} or \
        {x.lower() for x in AWAL_JUDUL_BAWAAN}
    akhir_judul = {str(x).strip().lower()
                   for x in (sis.get("bagian_akhir") or [])} or \
        {x.lower() for x in AWAL_AKHIR_BAWAAN}
    akhir_judul.discard("")

    paras = doc.paragraphs
    batas = [i for i, p in enumerate(paras)
             if p._p.pPr is not None and p._p.pPr.find(qn("w:sectPr")) is not None]

    rentang: list[tuple[int, int]] = []
    mulai = 0
    for b in batas:
        rentang.append((mulai, b))
        mulai = b + 1
    rentang.append((mulai, len(paras) - 1))

    def judul_pertama(a: int, b: int) -> str:
        for p in paras[a:b + 1]:
            nama = p.style.name if p.style else ""
            if nama == "Heading 1" and p.text.strip():
                return p.text.strip()
        return ""

    zona: list[str] = []
    sudah_pokok = False
    for a, b in rentang:
        judul = judul_pertama(a, b)
        j = judul.strip().lower()
        if JUDUL_BAB.match(judul):
            zona.append("pokok")
            sudah_pokok = True
        elif j in akhir_judul:
            zona.append("akhir")
        elif j in awal_judul or not sudah_pokok:
            zona.append("awal")
        else:
            # Heading 1 non-bab sesudah bab pertama = lanjutan bab yang
            # terpecah seksi, bukan bagian awal lagi.
            zona.append("pokok")

    # Seksi tanpa Heading 1 sendiri mewarisi zona seksi sebelumnya: "awal" yang
    # muncul setelah bagian pokok hampir pasti salah baca.
    for i in range(1, len(zona)):
        if zona[i] == "awal" and zona[i - 1] in ("pokok", "akhir"):
            zona[i] = zona[i - 1]
    return zona


def _pisah_seksi(doc, profil: dict) -> int:
    """Sisipkan section break di batas zona pada dokumen yang masih satu seksi.

    Skripsi hasil tempel-menempel biasanya tidak punya section break sama
    sekali: seluruh dokumen satu seksi, sehingga "bagian awal Romawi, isi
    Arab" mustahil. Fungsi ini menaruh salinan `sectPr` di paragraf terakhir
    sebelum batas, yang membuat Word menutup seksi di situ.

    Batas yang dipasang: sebelum SETIAP bab (Heading 1 "BAB ...") dan sebelum
    judul bagian akhir pertama (Daftar Pustaka dst).

    Satu seksi per bab itu wajib, bukan kemewahan: aturan panduan 4.5 berbunyi
    "halaman awal bab = tengah bawah, halaman lain = kanan atas", dan perbedaan
    posisi hanya bisa dibuat dengan `titlePg` per seksi. Kalau lima bab berbagi
    satu seksi, hanya halaman pembuka BAB I yang bernomor tengah bawah —
    halaman pembuka BAB II–V ikut aturan halaman lanjutan dan nomornya pindah
    ke kanan atas.

    Mengembalikan jumlah seksi yang ditambahkan.
    """
    from copy import deepcopy
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    sis = profil.get("sistematika") or {}
    akhir_judul = {str(x).strip().lower()
                   for x in (sis.get("bagian_akhir") or [])} or \
        {x.lower() for x in AWAL_AKHIR_BAWAAN}
    akhir_judul.discard("")

    paras = doc.paragraphs

    def judul(p):
        nama = p.style.name if p.style else ""
        return p.text.strip() if nama == "Heading 1" else ""

    def punya_sect(p):
        return p._p.pPr is not None and p._p.pPr.find(qn("w:sectPr")) is not None

    target = []
    for i, p in enumerate(paras):
        j = judul(p)
        if not j:
            continue
        # SETIAP bab memulai seksi sendiri, dan setiap judul bagian akhir juga.
        # Bab yang ditulis dua baris ("BAB II" lalu "LANDASAN PEMIKIRAN") hanya
        # menghasilkan satu batas karena baris kedua bukan pola JUDUL_BAB.
        if JUDUL_BAB.match(j) or j.lower() in akhir_judul:
            target.append(i)

    ditambah = 0
    for i in sorted(set(target)):
        if i == 0:
            continue
        # paragraf penutup seksi = paragraf terakhir sebelum batas yang belum
        # membawa sectPr
        j = i - 1
        while j >= 0 and punya_sect(paras[j]):
            j -= 1
        if j < 0:
            continue
        p = paras[j]
        pPr = p._p.get_or_add_pPr()
        if pPr.find(qn("w:sectPr")) is not None:
            continue
        # salin sectPr yang sedang berlaku (milik seksi terakhir dokumen)
        induk = doc.sections[-1]._sectPr
        baru = deepcopy(induk)
        for tag in ("w:headerReference", "w:footerReference"):
            for el in baru.findall(qn(tag)):
                baru.remove(el)
        pPr.append(baru)          # sectPr WAJIB unsur terakhir pPr
        ditambah += 1

    if ditambah:
        # seksi baru mewarisi referensi header/footer seksi sebelumnya; python-docx
        # membuat objek Section dari sectPr ini saat diakses berikutnya.
        pass
    return ditambah


def _rapikan_halaman_awal(doc, profil: dict) -> dict:
    """Beri pemisah halaman pada tiap judul bagian awal, dan jadikan Heading 1.

    Skripsi hasil tempel-menempel sering menulis "LEMBAR PENGESAHAN",
    "KATA PENGANTAR", dst sebagai paragraf tebal biasa tanpa page break:
    semuanya mengalir di satu halaman, sehingga nomor halaman tidak bisa
    dibagi per bagian dan daftar isi kehilangan entrinya.

    Yang dilakukan, hanya pada judul yang dikenal (dari `sistematika`):

    - `page_break_before = True`  -> tiap halaman bagian awal mulai di halaman baru
    - style Heading 1             -> masuk daftar isi + terdeteksi periksa_sistematika
    - rata tengah + tebal         -> tampilan judul halaman, bukan paragraf isi

    Paragraf yang sudah Heading 1 hanya diberi page break; run-nya tidak diubah
    supaya pemformatan manual mahasiswa (bold/ukuran) tidak hilang.
    """
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    sis = profil.get("sistematika") or {}
    dikenal = {str(x).strip().lower() for x in (sis.get("bagian_awal") or [])}
    dikenal |= {x.lower() for x in AWAL_JUDUL_BAWAAN}
    dikenal.discard("")
    if not dikenal:
        return {"judul": 0, "page_break": 0}

    stat = {"judul": 0, "page_break": 0}
    for p in doc.paragraphs:
        teks = p.text.strip()
        if not teks or len(teks) > 90:
            continue
        if JUDUL_BAB.match(teks):
            break                     # sudah masuk bagian pokok; berhenti
        if teks.lower() not in dikenal:
            continue
        nama = p.style.name if p.style else ""
        if nama != "Heading 1":
            p.style = doc.styles["Heading 1"]
            stat["judul"] += 1
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if not p.paragraph_format.page_break_before:
            p.paragraph_format.page_break_before = True
            stat["page_break"] += 1
    return stat


def perbaiki(path: str, profil: dict, cek_saja: bool = False,
             pisah_seksi: bool = False, rapikan_awal: bool = False) -> int:
    from docx import Document
    from docx.enum.section import WD_SECTION

    dok = profil.get("dokumen") or {}
    mar = dok.get("margin_cm") or {}
    fon = profil.get("font") or {}
    nama_font = fon.get("nama") or "Times New Roman"
    ph = profil.get("penomoran_halaman") or {}
    awal_ph = ph.get("bagian_awal") or {}
    pokok_ph = ph.get("bagian_pokok") or {}

    print(f"=== {'AUDIT' if cek_saja else 'PERBAIKAN'} {os.path.basename(path)} ===")
    if cek_saja:
        stat = {"rfonts": 0, "warna": 0}
    else:
        stat = bersihkan_paket(path, nama_font)
        print(f"  font tema dinormalkan : {stat['rfonts']} berkas XML")
        print(f"  warna non-hitam       : {stat['warna']} → {HITAM}")

    doc = Document(path)
    if rapikan_awal and not cek_saja:
        st = _rapikan_halaman_awal(doc, profil)
        if st["judul"] or st["page_break"]:
            print(f"  halaman awal          : {st['judul']} judul jadi Heading 1, "
                  f"{st['page_break']} pemisah halaman")
    if pisah_seksi and not cek_saja:
        n = _pisah_seksi(doc, profil)
        if n:
            print(f"  section break dipasang: {n} (batas bab / bagian akhir)")
    zona = _zona_dokumen(doc, profil)

    # ---- style dasar ----
    # Normal tanpa `rFonts` membuat `styles['Normal'].font.name` = None: Word
    # masih menampilkan Times New Roman dari docDefaults, tetapi setiap pemeriksa
    # (dan setiap manusia yang membuka dialog Font) melihat "font tidak diset".
    # Lebih buruk: run baru yang dibuat dari style itu mewarisi font tema.
    from docx.shared import Pt as _Pt
    from docx.oxml.ns import qn as _qn
    salah_style = 0
    for nama_style, pt in (("Normal", fon.get("isi_pt", 12)),
                           ("Heading 1", (fon.get("judul_bab") or {}).get("pt", 14)),
                           ("Heading 2", (fon.get("subbab") or {}).get("pt", 12)),
                           ("Heading 3", (fon.get("sub_subbab") or {}).get("pt", 12))):
        try:
            st = doc.styles[nama_style]
        except KeyError:
            continue
        if (st.font.name or "") != nama_font:
            salah_style += 1
            if not cek_saja:
                st.font.name = nama_font
                rPr = st.element.get_or_add_rPr()
                rf = rPr.find(_qn("w:rFonts"))
                if rf is None:
                    from docx.oxml import OxmlElement
                    rf = OxmlElement("w:rFonts")
                    rPr.insert(0, rf)
                for slot in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
                    rf.set(_qn(slot), nama_font)
        if pt and (st.font.size is None or abs(st.font.size.pt - float(pt)) > 0.1):
            salah_style += 1
            if not cek_saja:
                st.font.size = _Pt(float(pt))
    print(f"  style font/ukuran     : {salah_style} koreksi"
          + (" (diperbaiki)" if salah_style and not cek_saja else ""))

    # ---- margin & kertas seluruh seksi ----
    KERTAS = {"A4": (21.0, 29.7), "F4": (21.59, 33.02), "Letter": (21.59, 27.94)}
    from docx.shared import Cm
    w, h = KERTAS.get(dok.get("ukuran_kertas") or "A4", KERTAS["A4"])
    salah_margin = 0
    for seksi in doc.sections:
        if abs(seksi.page_width.cm - w) > 0.25 or abs(seksi.page_height.cm - h) > 0.25:
            salah_margin += 1
            if not cek_saja:
                seksi.page_width, seksi.page_height = Cm(w), Cm(h)
        for kunci, attr, bawaan in (("kiri", "left_margin", 4), ("atas", "top_margin", 3),
                                    ("kanan", "right_margin", 3), ("bawah", "bottom_margin", 3)):
            target = float(mar.get(kunci, bawaan))
            sekarang = getattr(seksi, attr).cm
            if abs(sekarang - target) > 0.05:
                salah_margin += 1
                if not cek_saja:
                    setattr(seksi, attr, Cm(target))
    print(f"  margin/kertas salah   : {salah_margin} seksi"
          + (" (diperbaiki)" if salah_margin and not cek_saja else ""))

    # ---- penomoran halaman per seksi ----
    n_seksi = len(doc.sections)
    daftar_zona = zona if len(zona) == n_seksi else ["pokok"] * n_seksi
    if len(zona) != n_seksi:
        print(f"  PERINGATAN: {n_seksi} seksi tetapi {len(zona)} zona terdeteksi; "
              f"semua seksi diperlakukan sebagai bagian pokok")

    belum_ada_pokok = "pokok" not in daftar_zona
    pokok_dimulai = False
    for i, seksi in enumerate(doc.sections):
        z = daftar_zona[i]
        if z == "awal":
            _bagian_nomor(seksi, "lowerRoman", 1 if i == 0 else None, False,
                          awal_ph.get("jarak_dari_bawah_cm", 2), 1.5)
        elif z == "akhir":
            # Bagian akhir MELANJUTKAN nomor Arab: tanpa `mulai`, penghitung
            # meneruskan angka terakhir bagian pokok. Memberi `mulai=1` di sini
            # adalah kesalahan klasik — Daftar Pustaka kembali ke halaman 1.
            _bagian_nomor(seksi, "decimal", None, False,
                          awal_ph.get("jarak_dari_bawah_cm", 2), 1.5)
        else:
            # Perpindahan Romawi -> Arab WAJIB punya `w:start="1"` di seksi
            # pertama bagian pokok. Tanpa itu Word meneruskan penghitung
            # Romawi, sehingga BAB I tercetak "16" bukan "1".
            #
            # Seksi berisi bab juga menerapkan panduan 4.5: halaman PERTAMA bab
            # tengah bawah, halaman lanjutannya kanan atas.
            mulai = None if pokok_dimulai else int(pokok_ph.get("mulai_dari") or 1)
            pokok_dimulai = True
            _bagian_nomor(seksi, "decimal", mulai, False,
                          awal_ph.get("jarak_dari_bawah_cm", 2), 1.5,
                          awal_bab_tengah=True)

    print(f"  seksi                 : {n_seksi} "
          f"(awal={daftar_zona.count('awal')}, pokok={daftar_zona.count('pokok')}, "
          f"akhir={daftar_zona.count('akhir')})")
    if belum_ada_pokok:
        print("  PERINGATAN: tidak ada bab (Heading 1 'BAB ...') terdeteksi — "
              "nomor Arab dimulai dari seksi pertama")

    if not cek_saja:
        doc.save(path)
        print("  disimpan.")
    return 0


# ------------------------------------------------------------------ audit
def audit(path: str, profil: dict, pdf: str | None = None) -> int:
    """Audit hasil akhir. Kembalikan jumlah kegagalan."""
    from docx import Document

    gagal = []
    dok = profil.get("dokumen") or {}
    mar = dok.get("margin_cm") or {}
    fon = profil.get("font") or {}
    nama_font = fon.get("nama") or "Times New Roman"
    dok_pt = fon.get("isi_pt", 12)

    doc = Document(path)
    s = doc.sections[0]
    for sisi, attr, bawaan in (("kiri", "left_margin", 4), ("atas", "top_margin", 3),
                               ("kanan", "right_margin", 3), ("bawah", "bottom_margin", 3)):
        target = float(mar.get(sisi, bawaan))
        dapat = getattr(s, attr).cm
        ok = abs(dapat - target) <= 0.25
        gagal += [] if ok else [f"margin {sisi}"]
        print(f"  {'LULUS' if ok else 'GAGAL'} margin {sisi:6} {dapat:.2f} cm (target {target})")

    normal = doc.styles["Normal"]
    ok = (normal.font.name or "") == nama_font
    gagal += [] if ok else ["font isi"]
    print(f"  {'LULUS' if ok else 'GAGAL'} font isi       {normal.font.name}")

    # warna teks: periksa seluruh paket, bukan hanya style Normal
    z = zipfile.ZipFile(path)
    bukan_hitam = 0
    tema = 0
    for nama in z.namelist():
        if nama.startswith("word/") and nama.endswith(".xml"):
            xml = z.read(nama).decode("utf8")
            for m in re.findall(r'<w:color\b[^>]*/>', xml):
                v = re.search(r'w:val="([^"]*)"', m)
                if v and v.group(1).upper() not in ("000000", "FFFFFF"):
                    bukan_hitam += 1
            tema += len(re.findall(r'Theme="', xml))
    ok = bukan_hitam == 0
    gagal += [] if ok else ["warna teks"]
    print(f"  {'LULUS' if ok else 'GAGAL'} warna teks     {bukan_hitam} warna non-hitam")
    ok = tema == 0
    gagal += [] if ok else ["font tema"]
    print(f"  {'LULUS' if ok else 'GAGAL'} font tema      {tema} atribut tema")

    if pdf:
        if not os.path.isfile(pdf):
            print(f"  GAGAL PDF tidak ada: {pdf}")
            gagal.append("pdf")
        else:
            skrip = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "audit_halaman.py")
            r = subprocess.run([sys.executable, skrip, pdf,
                                sys.argv[sys.argv.index("--profil") + 1]],
                               capture_output=True, text=True)
            ringkas = [l for l in r.stdout.splitlines() if l.startswith("Ringkasan")]
            ok = r.returncode == 0
            gagal += [] if ok else ["nomor halaman"]
            print(f"  {'LULUS' if ok else 'GAGAL'} nomor halaman  "
                  f"{(ringkas[0] if ringkas else 'tidak dapat diperiksa')}")
            if not ok:
                for l in r.stdout.splitlines():
                    if l.startswith("GAGAL"):
                        print("        " + l)
    return len(gagal)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Perbaiki margin/font/warna/penomoran DOCX skripsi sesuai profil kampus.")
    ap.add_argument("docx")
    ap.add_argument("--profil", required=True, help="profil-kampus.yaml")
    ap.add_argument("--cek-saja", action="store_true",
                    help="laporkan tanpa mengubah berkas")
    ap.add_argument("--pdf", help="hasil render PDF, untuk memeriksa nomor halaman")
    ap.add_argument("--pisah-seksi", action="store_true",
                    help="pasang section break di batas bab & bagian akhir bila "
                         "dokumen masih satu seksi (wajib agar Romawi/Arab bisa "
                         "berbeda)")
    ap.add_argument("--rapikan-awal", action="store_true",
                    help="judul halaman bagian awal jadi Heading 1 + mulai di "
                         "halaman baru (untuk skripsi yang masih mengalir)")
    a = ap.parse_args()

    if not os.path.isfile(a.docx):
        print(f"GAGAL: berkas tidak ada: {a.docx}", file=sys.stderr)
        return 2
    import yaml
    with open(a.profil, encoding="utf8") as f:
        profil = yaml.safe_load(f)

    if a.cek_saja:
        n = audit(a.docx, profil, a.pdf)
        print(f"\nRingkasan: {'LULUS semua' if n == 0 else f'{n} butir gagal'}")
        return 1 if n else 0

    perbaiki(a.docx, profil, pisah_seksi=a.pisah_seksi, rapikan_awal=a.rapikan_awal)
    print()
    n = audit(a.docx, profil, a.pdf)
    print(f"\nRingkasan: {'LULUS semua' if n == 0 else f'{n} butir gagal'}")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
