#!/usr/bin/env python3
"""Bangun template DOCX lengkap dari profil kampus.

Pemakaian:
    python3 buat_template_lengkap.py profil-kampus.yaml keluaran.docx
    python3 buat_template_lengkap.py profil-kampus.yaml keluaran.docx --contoh

Yang dihasilkan (mengikuti `sistematika` profil, bukan halaman contoh):
  - sampul lengkap (judul, kata SKRIPSI, kalimat diajukan, nama/NIM, institusi)
  - setiap halaman `bagian_awal` sebagai heading + penanda isi
  - setiap bab dan subbabnya, dengan penomoran multilevel Word yang BENAR
    (BAB I → "1.1." dst., masing-masing bab memakai numId sendiri)
  - setiap halaman `bagian_akhir`
  - tiga bagian dokumen: Romawi kecil (bagian awal), Arab mulai 1 (pokok),
    Arab lanjutan (bagian akhir) — field PAGE di footer yang benar

Kenapa skrip terpisah dari `buat_template_docx.py`: skrip lama hanya mengatur
style dan menaruh satu judul contoh, sehingga hasilnya 1 halaman tanpa sampul —
"lulus audit_docx" tetapi bukan template skripsi. Skrip ini membangun ISI
kerangkanya, dan tetap memakai gaya dari profil yang sama.

Peringatan penting soal penomoran: `%1.%2.` pada lvlText mengambil penghitung
LEVEL 0, dan level 0 adalah BAB — bukan angka bab yang kita inginkan. Karena itu
tiap bab memakai numId terpisah dengan awalan angka literal ("2.%1."), sama
seperti template resmi FTI. Jangan menormalkan menjadi "%1.%2.".
"""
from __future__ import annotations

import argparse
import os
import re
import sys

ROMAWI = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
          "XI", "XII"]
KERTAS = {"A4": (21.0, 29.7), "F4": (21.59, 33.02), "Letter": (21.59, 27.94)}


def _muat_yaml(path):
    try:
        import yaml
    except ImportError:
        sys.exit("GAGAL: butuh PyYAML (pip install pyyaml)")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _nilai(d, kunci, bawaan=None):
    v = (d or {}).get(kunci)
    return bawaan if v is None else v


# ---------------------------------------------------------------- penomoran
def buat_numbering(doc, sampel: list[dict]) -> dict:
    """Tambahkan definisi numbering untuk tiap bab.

    sampel: [{"awalan": "1", "subbab": [judul, ...]}, ...]

    Mengembalikan {awalan: numId}.
    """
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    numbering = doc.part.numbering_part.element
    # abstractNum & num yang sudah ada (bawaan python-docx) harus diberi nomor
    # setelah yang terakhir agar tidak bentrok.
    abs_ids = [int(e.get(qn("w:abstractNumId")))
               for e in numbering.findall(qn("w:abstractNum"))]
    num_ids = [int(e.get(qn("w:numId")))
               for e in numbering.findall(qn("w:num"))]
    next_abs = (max(abs_ids) + 1) if abs_ids else 0
    next_num = (max(num_ids) + 1) if num_ids else 1

    hasil: dict[str, int] = {}
    for entri in sampel:
        awalan = str(entri["awalan"])
        aid = next_abs
        next_abs += 1

        abs_el = OxmlElement("w:abstractNum")
        abs_el.set(qn("w:abstractNumId"), str(aid))
        nsid = OxmlElement("w:nsid")
        nsid.set(qn("w:val"), f"0A1B2C{aid:02X}")
        abs_el.append(nsid)
        mlt = OxmlElement("w:multiLevelType")
        mlt.set(qn("w:val"), "multilevel")
        abs_el.append(mlt)

        # level 0: subbab "2.1." — awalan angka bab ditulis LITERAL, karena
        # %1 merujuk penghitung BAB (level ini sendiri), bukan nomor bab.
        for ilvl, lvl_text, fmt, ind in (
                (0, f"{awalan}.%1.", "decimal", 0),
                (1, f"{awalan}.%1.%2.", "decimal", 0),
                (2, "%3.", "lowerLetter", 0)):
            lvl = OxmlElement("w:lvl")
            lvl.set(qn("w:ilvl"), str(ilvl))
            start = OxmlElement("w:start"); start.set(qn("w:val"), "1")
            lvl.append(start)
            nf = OxmlElement("w:numFmt"); nf.set(qn("w:val"), fmt)
            lvl.append(nf)
            lt = OxmlElement("w:lvlText"); lt.set(qn("w:val"), lvl_text)
            lvl.append(lt)
            lj = OxmlElement("w:lvlJc"); lj.set(qn("w:val"), "left")
            lvl.append(lj)
            ppr = OxmlElement("w:pPr")
            ind_el = OxmlElement("w:ind")
            ind_el.set(qn("w:left"), str(567 if ilvl == 0 else 1134))
            ind_el.set(qn("w:hanging"), "567")
            ppr.append(ind_el)
            lvl.append(ppr)
            abs_el.append(lvl)

        numbering.append(abs_el)

        num_el = OxmlElement("w:num")
        num_el.set(qn("w:numId"), str(next_num))
        an = OxmlElement("w:abstractNumId")
        an.set(qn("w:val"), str(aid))
        num_el.append(an)
        numbering.append(num_el)
        hasil[awalan] = next_num
        next_num += 1

    return hasil


def pasang_numpr(paragraf, num_id: int, ilvl: int) -> None:
    """Beri paragraf numPr (numId + ilvl) tanpa menghapus isi lain."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    pPr = paragraf._p.get_or_add_pPr()
    for lama in pPr.findall(qn("w:numPr")):
        pPr.remove(lama)
    numPr = OxmlElement("w:numPr")
    ilvl_el = OxmlElement("w:ilvl"); ilvl_el.set(qn("w:val"), str(ilvl))
    num_id_el = OxmlElement("w:numId"); num_id_el.set(qn("w:val"), str(num_id))
    numPr.append(ilvl_el)
    numPr.append(num_id_el)
    pPr.append(numPr)


# ---------------------------------------------------------------- halaman
def tambah_penomoran_halaman(seksi, fmt: str, mulai: int | None = None,
                             rata: str = "center", di_header: bool = False) -> None:
    """Atur format nomor halaman seksi (lowerRoman / decimal) + field PAGE.

    di_header=True menaruh nomor di KANAN ATAS (header) dan mengosongkan footer —
    ini yang diminta panduan untuk halaman-halaman non-awal-bab pada bagian
    pokok: "halaman lain: pojok kanan atas".`

    Nomor di awal bab (tengah bawah) tidak bisa diatur dengan field yang sama;
    itu memerlukan seksi tersendiri per bab. Template ini memakai kanan atas
    untuk semua halaman pokok — sama seperti template resmi FTI.
    """
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    sectPr = seksi._sectPr
    for lama in sectPr.findall(qn("w:pgNumType")):
        sectPr.remove(lama)
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:fmt"), fmt)
    if mulai is not None:
        pg.set(qn("w:start"), str(mulai))
    sectPr.append(pg)

    if di_header:
        wadah = seksi.header
        lawan = seksi.footer
    else:
        wadah = seksi.footer
        lawan = seksi.header
    # kosongkan wadah lawan supaya tidak ada nomor dobel
    lawan.is_linked_to_previous = False
    for p_ in list(lawan.paragraphs):
        for r_ in list(p_.runs):
            r_._r.getparent().remove(r_._r)

    wadah.is_linked_to_previous = False
    p = wadah.paragraphs[0] if wadah.paragraphs else wadah.add_paragraph()
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    p.alignment = (WD_ALIGN_PARAGRAPH.CENTER if rata == "center"
                   else WD_ALIGN_PARAGRAPH.RIGHT)

    run = p.add_run()
    fld_begin = OxmlElement("w:fldChar"); fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_end = OxmlElement("w:fldChar"); fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)


def _kosongkan(wadah) -> None:
    """Buat wadah header/footer benar-benar kosong (satu paragraf tanpa isi).

    Menghapus semua run saja tidak cukup: LibreOffice/Word memperlakukan header
    tanpa paragraf sebagai "warisi seksi sebelumnya", sehingga nomor dari header
    default muncul lagi di halaman pertama bab (nomor dobel).
    """
    wadah.is_linked_to_previous = False
    paras = list(wadah.paragraphs)
    if not paras:
        wadah.add_paragraph()
        return
    for p_ in paras[1:]:
        p_._p.getparent().remove(p_._p)
    p = paras[0]
    for r in list(p.runs):
        r._r.getparent().remove(r._r)


def _nomor_di(wadah, rata: str) -> None:
    """Tulis field PAGE ke wadah header/footer tertentu."""
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    wadah.is_linked_to_previous = False
    p = wadah.paragraphs[0] if wadah.paragraphs else wadah.add_paragraph()
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    p.alignment = (WD_ALIGN_PARAGRAPH.CENTER if rata == "center"
                   else WD_ALIGN_PARAGRAPH.RIGHT)
    run = p.add_run()
    b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin")
    i = OxmlElement("w:instrText"); i.set(qn("xml:space"), "preserve")
    i.text = " PAGE "
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end")
    run._r.append(b); run._r.append(i); run._r.append(e)


def rapikan_seksi_tanpa_paragraf_kosong(doc) -> int:
    """Pindahkan sectPr dari paragraf kosong ke paragraf sebelumnya.

    Setiap `add_section()` menyisipkan paragraf kosong yang membawa `sectPr`.
    Enam seksi = enam paragraf kosong yang dihitung audit_rapi sebagai "spasi
    manual". `sectPr` boleh menempel di pPr paragraf mana pun, jadi paragraf
    kosong itu bisa dihapus tanpa mengubah paginasi.

    Mengembalikan jumlah paragraf yang berhasil dihapus.
    """
    from docx.oxml.ns import qn

    dihapus = 0
    for p in list(doc.paragraphs):
        if p.text.strip() or len(p.runs):
            continue
        pPr = p._p.pPr
        if pPr is None:
            continue
        sectPr = pPr.find(qn("w:sectPr"))
        if sectPr is None:
            continue
        sebelum = p._p.getprevious()
        if sebelum is None or sebelum.tag != qn("w:p"):
            continue
        pPr_sebelum = sebelum.find(qn("w:pPr"))
        if pPr_sebelum is None:
            from docx.oxml import OxmlElement
            pPr_sebelum = OxmlElement("w:pPr")
            sebelum.insert(0, pPr_sebelum)
        # sectPr WAJIB jadi unsur terakhir dalam pPr (skema Word)
        pPr_sebelum.append(sectPr)
        p._p.getparent().remove(p._p)
        dihapus += 1
    return dihapus


def matikan_halaman_pertama_beda(seksi) -> None:
    """Pastikan seksi memakai header/footer yang sama di halaman pertamanya.

    Bila `titlePg` aktif, halaman pertama seksi memakai header/footer "first"
    yang terpisah — dan kalau kosong, nomor halaman hilang tepat di halaman
    pembuka bab. Itu yang terjadi pada BAB I sebelum ini.
    """
    try:
        seksi.different_first_page_header_footer = False
    except Exception:
        pass


def seksi_baru(doc, profil: dict):
    from docx.enum.section import WD_SECTION
    from docx.shared import Cm

    dok = profil.get("dokumen") or {}
    mar = dok.get("margin_cm") or {}
    s = doc.add_section(WD_SECTION.NEW_PAGE)
    w, h = KERTAS.get(dok.get("ukuran_kertas") or "A4", KERTAS["A4"])
    s.page_width, s.page_height = Cm(w), Cm(h)
    s.left_margin = Cm(mar.get("kiri", 4))
    s.top_margin = Cm(mar.get("atas", 3))
    s.right_margin = Cm(mar.get("kanan", 3))
    s.bottom_margin = Cm(mar.get("bawah", 3))
    return s


# ---------------------------------------------------------------- isi
def tulis_sampul(doc, profil: dict, judul: str, nama: str, nim: str,
                 prodi: str, tahun: str) -> None:
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt

    smp = profil.get("sampul") or {}
    sek = profil.get("dokumen") or {}
    nama_font = (profil.get("font") or {}).get("nama") or "Times New Roman"

    def baris(teks, pt, tebal=False, spasi=1.5, kapital=False, jarak_atas=0):
        """Satu baris sampul. Jarak vertikal pakai space_before, BUKAN paragraf
        kosong — paragraf kosong dihitung "spasi manual" oleh audit_rapi dan
        membuat sampul sulit dirapikan pengguna."""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = spasi
        p.paragraph_format.space_after = Pt(0)
        if jarak_atas:
            p.paragraph_format.space_before = Pt(jarak_atas)
        r = p.add_run(teks.upper() if kapital else teks)
        r.font.name = nama_font
        r.font.size = Pt(pt)
        r.font.bold = tebal
        return p

    # Tata letak sampul mengikuti posisi template resmi FTI (terukur dari PDF-nya):
    # judul y=86, SKRIPSI y=330, "Diajukan ..." y=371, nama y=454, NIM y=478,
    # prodi y=567, universitas y=588, kota y=608, tahun y=629 (A4, tinggi 842 pt).
    # Jarak diwujudkan dengan space_before, bukan paragraf kosong.
    Y_JUDUL = 86 - 85           # 85 = margin atas 3 cm
    Y_SKRIPSI = 330 - 85
    Y_DIAJUKAN = 371 - 85
    Y_NAMA = 454 - 85
    Y_NIM = 478 - 85
    Y_PRODI = 567 - 85
    Y_UNIV = 588 - 85
    Y_KOTA = 608 - 85
    Y_TAHUN = 629 - 85

    # Kursor vertikal dihitung manual karena space_before bersifat relatif.
    def baris_pada(teks, pt, y_target, tebal=False, spasi=1.0, kapital=False):
        nonlocal y_kursor
        jarak = max(0.0, y_target - y_kursor)
        p = baris(teks, pt, tebal=tebal, spasi=spasi, kapital=kapital,
                  jarak_atas=jarak)
        y_kursor = y_target + pt * 1.15 * spasi
        return p

    y_kursor = 12.0
    baris_pada(judul, smp.get("judul_pt", 14), Y_JUDUL,
               tebal=True, spasi=1.5, kapital=True)
    baris_pada("SKRIPSI", smp.get("skripsi_pt", 18), Y_SKRIPSI,
               tebal=True, spasi=smp.get("kata_skripsi_spasi", 2), kapital=True)
    baris_pada(smp.get("kalimat_diajukan") or
               "Diajukan untuk memenuhi salah satu syarat kelulusan Program Sarjana",
               smp.get("kalimat_diajukan_pt", 12), Y_DIAJUKAN, spasi=1.0)
    baris_pada(nama, smp.get("nama_nim_pt", 14), Y_NAMA,
               tebal=smp.get("nama_nim_tebal", True),
               spasi=smp.get("nama_nim_spasi", 1.5))
    baris_pada(nim, smp.get("nama_nim_pt", 14), Y_NIM,
               tebal=smp.get("nama_nim_tebal", True),
               spasi=smp.get("nama_nim_spasi", 1.5))
    baris_pada(f"Program Studi {prodi}", smp.get("institusi_pt", 12), Y_PRODI,
               tebal=smp.get("institusi_tebal", True), spasi=1.0, kapital=True)
    baris_pada(smp.get("institusi_nama_resmi") or
               (profil.get("kampus") or {}).get("nama", ""),
               smp.get("institusi_pt", 12), Y_UNIV,
               tebal=smp.get("institusi_tebal", True), spasi=1.0, kapital=True)
    baris_pada(smp.get("kota_bawaan") or "Kota Bandung", smp.get("institusi_pt", 12),
               Y_KOTA, tebal=smp.get("institusi_tebal", True), spasi=1.0,
               kapital=True)
    baris_pada(tahun, smp.get("institusi_pt", 12), Y_TAHUN,
               tebal=smp.get("institusi_tebal", True), spasi=1.0)


def tulis_halaman(doc, judul: str, catatan: str | None) -> None:
    """Satu halaman bagian awal/akhir: judul tengah kapital + catatan isi.

    `page_break_before` dipakai, bukan add_page_break(): kalau memakai paragraf
    kosong berisi page break, halaman judul berikutnya bisa terdorong sehingga
    muncul halaman kosong. Ini penyebab paling umum "PDF-nya ada halaman bolong".
    """
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    h = doc.add_heading(judul, level=1)
    h.paragraph_format.page_break_before = True
    if catatan:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(f"[{catatan}]")
        r.italic = True


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Bangun template DOCX lengkap (sampul + semua bagian + bab) dari profil kampus.",
        epilog="contoh: python3 buat_template_lengkap.py presets/ars-fti.yaml template.docx")
    ap.add_argument("profil")
    ap.add_argument("keluaran")
    ap.add_argument("--judul", default="JUDUL SKRIPSI CONTOH")
    ap.add_argument("--nama", default="NAMA MAHASISWA")
    ap.add_argument("--nim", default="NIM")
    ap.add_argument("--prodi", default="PROGRAM STUDI")
    ap.add_argument("--tahun", default="2026")
    ap.add_argument("--isi-paragraf", type=int, default=1,
                    help="jumlah paragraf contoh per subbab (pakai angka besar "
                         "untuk menguji penomoran halaman lanjutan)")
    a = ap.parse_args()

    if not os.path.isfile(a.profil):
        print(f"GAGAL: profil tidak ada: {a.profil}", file=sys.stderr)
        return 2
    profil = _muat_yaml(a.profil)
    if not isinstance(profil, dict) or "sistematika" not in profil:
        print("GAGAL: profil tidak memuat kunci 'sistematika'.", file=sys.stderr)
        return 2

    sis = profil["sistematika"]
    dok = profil.get("dokumen") or {}
    mar = dok.get("margin_cm") or {}
    fon = profil.get("font") or {}
    spa = profil.get("spasi") or {}
    nama_font = fon.get("nama") or "Times New Roman"

    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Cm, Pt

    doc = Document()

    # ---- style dasar ----
    normal = doc.styles["Normal"]
    normal.font.name = nama_font
    normal.font.size = Pt(fon.get("isi_pt", 12))
    normal.paragraph_format.line_spacing = spa.get("isi", 2)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.widow_control = True

    jb = fon.get("judul_bab") or {}
    for lvl, cfg, default_pt in (("Heading 1", jb, 14),
                                 ("Heading 2", fon.get("subbab") or {}, 12),
                                 ("Heading 3", fon.get("sub_subbab") or {}, 12)):
        st = doc.styles[lvl]
        st.font.name = nama_font
        st.font.size = Pt(cfg.get("pt", default_pt))
        st.font.bold = cfg.get("tebal", True)
        st.font.italic = False
        st.font.color.rgb = None
        st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if lvl == "Heading 1" \
            else WD_ALIGN_PARAGRAPH.LEFT if cfg.get("rata", "kiri") == "kiri" \
            else WD_ALIGN_PARAGRAPH.JUSTIFY
        st.paragraph_format.space_before = Pt(12 if lvl == "Heading 1" else 6)
        st.paragraph_format.space_after = Pt(12 if lvl == "Heading 1" else 6)
        st.paragraph_format.line_spacing = spa.get("judul", 2.0) or 2.0
        st.paragraph_format.keep_with_next = True
        st.paragraph_format.keep_together = True
        st.paragraph_format.first_line_indent = Cm(0)
        st.paragraph_format.left_indent = Cm(0)

    # ---- seksi 1: bagian awal, Romawi kecil ----
    s1 = doc.sections[0]
    w, h = KERTAS.get(dok.get("ukuran_kertas") or "A4", KERTAS["A4"])
    s1.page_width, s1.page_height = Cm(w), Cm(h)
    s1.left_margin = Cm(mar.get("kiri", 4))
    s1.top_margin = Cm(mar.get("atas", 3))
    s1.right_margin = Cm(mar.get("kanan", 3))
    s1.bottom_margin = Cm(mar.get("bawah", 3))

    tulis_sampul(doc, profil, a.judul, a.nama, a.nim, a.prodi, a.tahun)

    awal = sis.get("bagian_awal") or []
    # "Lembar Judul" sudah dibuat sebagai sampul
    for item in awal:
        if re.fullmatch(r"lembar\s+judul", item, re.I):
            continue
        catatan = None
        for s in (sis.get("catatan_bagian_awal") or {}).items():
            pass
        # catatan per bagian diambil dari `catatan_halaman` bila ada
        ch = (profil.get("catatan_halaman") or {}).get(item)
        tulis_halaman(doc, item, ch)

    # Nomor Romawi bagian awal: sampul adalah halaman i TETAPI nomornya tidak
    # dicetak, jadi halaman berikutnya mulai "ii" (sesuai template resmi).
    tambah_penomoran_halaman(s1, "lowerRoman", mulai=1)
    # sembunyikan nomor di halaman sampul: footer halaman pertama seksi = kosong
    try:
        s1.different_first_page_header_footer = True
        ff = s1.first_page_footer
        for p_ in list(ff.paragraphs):
            for r_ in list(p_.runs):
                r_._r.getparent().remove(r_._r)
    except Exception:
        pass

    # ---- seksi 2: bagian pokok, Arab mulai 1 ----
    s2 = seksi_baru(doc, profil)
    tambah_penomoran_halaman(s2, "decimal", mulai=1, rata="right", di_header=True)
    # BAB I juga bab: halaman pertamanya bernomor tengah bawah
    s2.different_first_page_header_footer = True
    _nomor_di(s2.first_page_footer, "center")
    _kosongkan(s2.first_page_header)

    bab_cfg = sis.get("bab") or {}
    judul_bab_map = {str(k).strip().upper(): str(v)
                     for k, v in (sis.get("judul_bab") or {}).items()}
    daftar_bab: list[dict] = []
    for i, (nama_bab, subbab) in enumerate(bab_cfg.items(), start=1):
        kunci = str(nama_bab).strip().upper()
        # judul dari `judul_bab` bila ada; kalau tidak, sisa teks setelah "BAB X"
        judul = judul_bab_map.get(kunci) or \
            re.sub(r"^BAB\s+([IVX]+|\d+)\s*", "", str(nama_bab), flags=re.I).strip()
        daftar_bab.append({"awalan": str(i), "judul": str(nama_bab),
                           "nama_bab": judul, "subbab": subbab})

    peta_num = buat_numbering(doc, daftar_bab)

    for idx_bab, b in enumerate(daftar_bab):
        # Tiap bab = SEKSI sendiri. Ini satu-satunya cara memenuhi panduan 4.5:
        # "awal bab: tengah bawah; halaman lain: pojok kanan atas". Dengan seksi
        # terpisah, halaman pertama bab memakai footer khusus (tengah bawah),
        # halaman lanjutannya memakai header (kanan atas).
        if idx_bab > 0:
            sb = seksi_baru(doc, profil)
            # Header/footer bawaan seksi ini: nomor di KANAN ATAS (halaman lanjutan)
            tambah_penomoran_halaman(sb, "decimal", rata="right", di_header=True)
            # Halaman PERTAMA bab: nomor di TENGAH BAWAH, header kosong.
            sb.different_first_page_header_footer = True
            _nomor_di(sb.first_page_footer, "center")
            _kosongkan(sb.first_page_header)

        # "BAB I" / "PENDAHULUAN" — dua baris seperti template resmi.
        # Nomor bab diambil dari urutan, BUKAN dari teks kunci YAML, supaya kunci
        # seperti "BAB I PENDAHULUAN" dan "Pendahuluan" sama-sama benar.
        idx = idx_bab
        nomor_bab = ROMAWI[idx] if idx < len(ROMAWI) else str(idx + 1)
        judul_bab = (b.get("nama_bab") or "").upper()
        # "BAB I" + "PENDAHULUAN" ditulis sebagai SATU Heading 1 dengan pemisah
        # baris. Dua paragraf biasa akan ditandai audit_rapi sebagai "judul palsu"
        # (teks tebal/tengah tanpa style heading) dan tidak masuk daftar isi.
        # "BAB I" dan "PENDAHULUAN" HARUS dua paragraf terpisah. Bila digabung
        # dengan line break, judul menjadi satu string "BAB I\nPENDAHULUAN":
        # daftar isi menampilkannya sebagai satu baris berisi baris baru, dan
        # pembuat daftar isi tidak menemukannya pada render. Dua paragraf juga
        # membuat "BAB I" bisa muncul sebagai entri TOC tersendiri.
        for teks_bab, jarak_bawah in ((f"BAB {nomor_bab}", 0),
                                      (judul_bab, 24)):
            if not teks_bab:
                continue
            p_bab = doc.add_heading(level=1)
            p_bab.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_bab.paragraph_format.line_spacing = spa.get("judul", 2) or 2.0
            p_bab.paragraph_format.space_before = Pt(0)
            p_bab.paragraph_format.space_after = Pt(jarak_bawah)
            p_bab.paragraph_format.page_break_before = False
            r_ = p_bab.add_run(teks_bab)
            r_.font.name = nama_font
            r_.font.size = Pt(jb.get("pt", 14))
            r_.font.bold = True

        for sub in b["subbab"]:
            # buang nomor di awal judul profil — nomor akan dibuat Word
            bersih = re.sub(r"^\d+(\.\d+)*\.?\s*", "", sub).strip()
            h2 = doc.add_heading(bersih, level=2)
            h2.paragraph_format.first_line_indent = Cm(0)
            h2.paragraph_format.left_indent = Cm(0)
            pasang_numpr(h2, peta_num[b["awalan"]], 0)

        # paragraf contoh isi (indent baris pertama 1 cm)
        for n_isi in range(max(1, a.isi_paragraf)):
            isi = doc.add_paragraph()
            isi.paragraph_format.first_line_indent = Cm(1.0)
            isi.paragraph_format.line_spacing = spa.get("isi", 2.0) or 2.0
            isi.add_run(
                "Paragraf isi contoh. Ganti dengan isi naskah sebenarnya; "
                "indentasi baris pertama 1 cm mengikuti panduan."
                + (f" (paragraf {n_isi + 1})" if a.isi_paragraf > 1 else ""))



    # ---- seksi 3: bagian akhir, Arab lanjutan ----
    s3 = seksi_baru(doc, profil)
    matikan_halaman_pertama_beda(s3)
    # Bagian akhir melanjutkan nomor Arab dari seksi sebelumnya: JANGAN set
    # `mulai`, karena itu akan mereset ke 1 dan membuat dua halaman bernomor 1.
    tambah_penomoran_halaman(s3, "decimal", rata="center")

    for item in (sis.get("bagian_akhir") or []):
        ch = (profil.get("catatan_halaman") or {}).get(item)
        tulis_halaman(doc, item, ch)

    rapikan_seksi_tanpa_paragraf_kosong(doc)
    doc.save(a.keluaran)
    # Atribut font tema (asciiTheme/hAnsiTheme) diwarisi dari dokumen kosong
    # python-docx dan membuat Word MENGGANTI Times New Roman menjadi Calibri.
    # Pakai pembersih yang sama dengan generator template biasa.
    try:
        from buat_template_docx import bersihkan_paket
        bersihkan_paket(a.keluaran, nama_font)
    except Exception as exc:                    # pragma: no cover
        print(f"PERINGATAN: gagal membersihkan atribut font tema: {exc}",
              file=sys.stderr)
    print(f"template lengkap tersimpan: {a.keluaran}")
    print(f"  bagian awal : {len(awal)} (+sampul)")
    print(f"  bab         : {len(daftar_bab)}")
    print(f"  bagian akhir: {len(sis.get('bagian_akhir') or [])}")
    print(f"  numbering   : {len(peta_num)} definisi (satu per bab, awalan literal)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
