#!/usr/bin/env python3
"""Bangun Daftar Tabel / Daftar Gambar / Daftar Lampiran, dan rapikan nomor
caption yang sudah menjadi teks mati.

Pemakaian:
    python3 buat_daftar_tabel_gambar.py dokumen.docx profil-kampus.yaml
    python3 buat_daftar_tabel_gambar.py dokumen.docx profil.yaml --pdf render.pdf
    python3 buat_daftar_tabel_gambar.py dokumen.docx profil.yaml --cek
    python3 buat_daftar_tabel_gambar.py dokumen.docx profil.yaml --hanya-renumber

Kenapa skrip ini ada: generator hanya menaruh HEADING kosong untuk Daftar
Tabel/Gambar. Isinya tidak pernah dibangun, dan nomor caption ditulis sebagai
teks biasa ("Tabel 4.1"). Begitu mahasiswa menyisipkan satu tabel di tengah
BAB III, seluruh nomor sesudahnya salah dan tidak ada yang memperbaikinya.

Dua hal yang dikerjakan, berurutan:

1. RENUMBER CAPTION. Caption dicari dari pola teks, bab-nya ditentukan dari
   heading "BAB ..." terdekat di atasnya, lalu nomornya ditulis ulang sesuai
   gaya profil (angka Arab per bab: "Tabel 3.1", atau Romawi kapital per bab:
   "Tabel III.1"). Nomor baru ditulis sebagai field SEQ dengan nilai eksplisit
   (`SEQ Tabel \\* ARABIC \\r N`), jadi Word tetap bisa memperbaruinya tetapi
   hasil sekarang sudah benar tanpa perlu Update Field.

2. BANGUN DAFTARNYA. Untuk setiap jenis (Tabel/Gambar/Lampiran) dicari heading
   "Daftar ..." yang sudah ada, lalu daftar diisi: nomor caption, judul caption,
   dan nomor halaman hasil render. Nomor halaman diambil dari PDF (soffice),
   bukan ditebak — mengikuti aturan bundel: hitung, jangan andalkan field yang
   tidak ter-update di headless.

Yang TIDAK diubah: teks naskah, isi tabel, dan urutan bab.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

JENIS = {
    "tabel": {"kata": "Tabel", "daftar": "Daftar Tabel", "seq": "Tabel"},
    "gambar": {"kata": "Gambar", "daftar": "Daftar Gambar", "seq": "Gambar"},
    "lampiran": {"kata": "Lampiran", "daftar": "Daftar Lampiran", "seq": "Lampiran"},
}

# "Tabel 4.1", "Tabel IV.1", "Tabel 4.1.", "Gambar 2.3" — nomor boleh sudah ada
# atau belum ("Tabel " saja). Yang penting kata kuncinya di awal paragraf.
POLA_CAPTION = re.compile(
    r"^\s*(Tabel|Gambar|Lampiran)\s*"
    r"(?:(?P<bab>[IVXLC]+|\d+)\s*[.\-]\s*)?"
    r"(?P<urut>\d+)?\s*[.:]?\s*(?P<judul>.*)$", re.I)

POLA_BAB = re.compile(r"^\s*BAB\s+([IVXLC]+|\d+)\b", re.I)
ROMAWI = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def romawi(n: int) -> str:
    out = ""
    for v, r in ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += r
            n -= v
    return out


def romawi_ke_int(s: str) -> int:
    peta = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    total, lalu = 0, 0
    for ch in reversed(s.upper()):
        v = peta.get(ch, 0)
        total += -v if v < lalu else v
        lalu = max(lalu, v)
    return total


def gaya_nomor(profil: dict, jenis: str) -> str:
    """'arab' atau 'romawi' — dari teks `caption.<jenis>.penomoran` profil."""
    cap = ((profil.get("caption") or {}).get(jenis) or {})
    teks = str(cap.get("penomoran") or "").lower()
    if "romawi" in teks:
        return "romawi"
    if "arab" in teks:
        return "arab"
    # tidak disebut panduan -> pakai Arab per bab (paling umum) dan laporkan
    return "arab"


def label_bab(judul: str, gaya: str, urutan: int) -> str:
    """Ambil bagian angka dari heading 'BAB IV PENDAHULUAN' -> 'IV' atau '4'."""
    m = POLA_BAB.match(judul or "")
    if m:
        mentah = m.group(1).upper()
        if gaya == "romawi":
            return mentah if not mentah.isdigit() else romawi(int(mentah))
        return str(romawi_ke_int(mentah)) if not mentah.isdigit() else str(int(mentah))
    return str(urutan) if gaya == "arab" else romawi(urutan)


# ------------------------------------------------------------------ dokumen
def _hapus_field(par) -> None:
    """Buang semua field/run lama pada paragraf caption (ditulis ulang)."""
    from docx.oxml.ns import qn
    for r in list(par.runs):
        r._r.getparent().remove(r._r)
    pPr = par._p.pPr
    if pPr is not None:
        for el in pPr.findall(qn("w:rPr")):
            pPr.remove(el)


def _run_seq(par, nama_seq: str, nilai: int, font: str, pt: float) -> None:
    """Sisipkan field SEQ bernilai eksplisit: `SEQ Tabel \\* ARABIC \\r N`."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    run = par.add_run()
    run.font.name = font
    run.font.size = __import__("docx.shared", fromlist=["Pt"]).Pt(pt)

    b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin")
    i = OxmlElement("w:instrText"); i.set(qn("xml:space"), "preserve")
    i.text = f' SEQ {nama_seq} \\* ARABIC \\r {nilai} '
    sep = OxmlElement("w:fldChar"); sep.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t"); t.text = str(nilai)
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end")
    for el in (b, i, sep, t, e):
        run._r.append(el)


def _tulis_caption(par, kata: str, prefiks: str, urut: int, judul: str,
                   font: str, pt: float, pakai_seq: bool) -> None:
    from docx.shared import Pt

    _hapus_field(par)
    r = par.add_run(f"{kata} ")
    r.font.name = font; r.font.size = Pt(pt)
    if prefiks:
        r = par.add_run(f"{prefiks}.")
        r.font.name = font; r.font.size = Pt(pt)
    if pakai_seq:
        _run_seq(par, JENIS_INV[kata.lower()]["seq"], urut, font, pt)
    else:
        r = par.add_run(str(urut))
        r.font.name = font; r.font.size = Pt(pt)
    if judul:
        r = par.add_run(f" {judul}")
        r.font.name = font; r.font.size = Pt(pt)


JENIS_INV = {v["kata"].lower(): v for v in JENIS.values()}


def _teks_paragraf(p) -> str:
    return "".join(t.text or "" for t in p._p.iter() if t.tag.endswith("}t")).strip()


def renumber(doc, profil: dict) -> dict:
    """Nomori ulang caption per bab. Kembalikan {jenis: [entri]}."""
    font = (profil.get("font") or {}).get("nama") or "Times New Roman"
    pt = (profil.get("font") or {}).get("judul_tabel_gambar_pt") \
        or (profil.get("font") or {}).get("isi_pt") or 12
    gaya = {j: gaya_nomor(profil, j) for j in JENIS}

    hasil = {j: [] for j in JENIS}
    bab_urutan, bab_judul = 0, ""
    counter = {j: 0 for j in JENIS}
    dalam_daftar = False

    for p in doc.paragraphs:
        teks = _teks_paragraf(p)
        if not teks:
            continue
        nama_style = p.style.name if p.style else ""
        # Blok Daftar Tabel/Gambar/Lampiran bukan naskah: entri di dalamnya
        # memakai format "Tabel I.1<TAB>halaman" yang menyerupai caption.
        # Tanpa penanda ini, menjalankan ulang skrip pada dokumen yang sudah
        # punya daftar membaca entri daftar sebagai caption baru dan menomori
        # ulang dirinya sendiri (nomor caption melompat 1,2,3,4).
        if nama_style.startswith("Heading"):
            if teks.strip().lower() in {v["daftar"].lower() for v in JENIS.values()}:
                dalam_daftar = True
            elif POLA_BAB.match(teks):
                # judul bab menandai reset counter caption
                bab_urutan += 1
                bab_judul = teks
                counter = {j: 0 for j in JENIS}
                dalam_daftar = False
            else:
                dalam_daftar = False
            # Heading apa pun BUKAN caption. Tanpa ini, heading "Lampiran" di
            # bagian akhir terbaca sebagai caption "Lampiran 5.1" tanpa judul —
            # dan Daftar Lampiran lahir dengan satu entri palsu.
            continue
        if dalam_daftar:
            continue
        # Judul caption hampir selalu di paragraf BERIKUTNYA (caption panjang
        # terpecah dua baris). Itu bukan caption, dan menghitungnya membuat
        # nomor melompat (I.1 dihitung dua kali dari satu tabel).
        if re.match(r"^(tabel|gambar|lampiran)\b", teks, re.I):
            m = POLA_CAPTION.match(teks)
        else:
            m = None
        if not m:
            continue
        kata = m.group(1).lower()
        if kata not in JENIS:
            continue
        judul = (m.group("judul") or "").strip()
        # paragraf panjang dengan kata "tabel" di awal kalimat bukan caption;
        # caption hampir selalu < 200 karakter dan tidak diakhiri titik ganda
        if len(teks) > 220 or judul.count(". ") > 3:
            continue
        counter[kata] += 1
        urut = counter[kata]
        prefiks = label_bab(bab_judul, gaya[kata], bab_urutan) if bab_urutan else ""
        _tulis_caption(p, JENIS[kata]["kata"], prefiks, urut, judul, font, pt, True)
        nomor = f"{prefiks}.{urut}" if prefiks else str(urut)
        hasil[kata].append({"nomor": nomor, "judul": judul, "paragraf": p,
                            "jenis": kata, "cari": judul[:60]})
    return hasil


# ------------------------------------------------------------------ halaman
def _render_pdf(docx: str) -> tuple[str, str | None]:
    """Render DOCX -> PDF sementara. Kembalikan (path_pdf, tmpdir)."""
    if not shutil.which("soffice"):
        return "", None
    tmp = tempfile.mkdtemp()
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", docx,
                    "--outdir", tmp], capture_output=True)
    pdf = os.path.join(tmp, os.path.splitext(os.path.basename(docx))[0] + ".pdf")
    return (pdf, tmp) if os.path.isfile(pdf) else ("", tmp)


def _halaman_caption(pdf: str) -> list[tuple[int, str]]:
    """[(nomor_halaman_pdf, teks_gabungan)] untuk setiap halaman."""
    out = []
    try:
        total = int(subprocess.run(["pdfinfo", pdf], capture_output=True, text=True)
                    .stdout.split("Pages:")[1].split()[0])
    except Exception:
        return out
    for n in range(1, total + 1):
        t = subprocess.run(["pdftotext", "-f", str(n), "-l", str(n), "-layout", pdf, "-"],
                           capture_output=True, text=True).stdout
        out.append((n, " ".join(t.split())))
    return out


def _nomor_tampil(n_pdf: int, bab_pertama: int, ph: dict) -> str:
    if n_pdf < bab_pertama:
        awal = ph.get("bagian_awal") or {}
        offset = 0 if awal.get("sampul_dihitung", True) else 1
        return romawi(max(1, n_pdf - offset)).lower()
    mulai = int((ph.get("bagian_pokok") or {}).get("mulai_dari") or 1)
    return str(mulai + n_pdf - bab_pertama)


def _cari_halaman(pdf: str, profil: dict, daftar: list[dict],
                  abaikan: set[str] | None = None) -> None:
    """Isi `halaman` tiap entri dengan nomor halaman tampil (dari render).

    Pencarian melewati halaman daftar itu sendiri (`abaikan`): kalau tidak,
    setiap caption akan "ditemukan" di halaman Daftar Tabel — karena halaman
    itu memuat semua judul — dan seluruh kolom halaman berisi angka yang sama.
    """
    halaman = _halaman_caption(pdf)
    if not halaman:
        return
    abaikan = abaikan or set()
    bab_pertama = next((n for n, t in halaman
                        if re.search(r"\bBAB\s+[IVXLC]+\b", t)), 1)
    ph = profil.get("penomoran_halaman") or {}
    posisi = 1
    for entri in daftar:
        cari = entri["cari"].lower()
        if not cari:
            entri["halaman"] = ""
            continue
        for i in range(posisi - 1, len(halaman)):
            n, teks = halaman[i]
            if n in abaikan:
                continue
            if cari in teks.lower():
                entri["halaman"] = _nomor_tampil(n, bab_pertama, ph)
                posisi = n
                break
        else:
            entri["halaman"] = ""


def _isi_daftar(doc, jenis_key: str, entri: list[dict], profil: dict) -> bool:
    """Isi heading 'Daftar Tabel/Gambar/Lampiran' dengan entri + nomor halaman."""
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt

    judul_daftar = JENIS[jenis_key]["daftar"]
    font = (profil.get("font") or {}).get("nama") or "Times New Roman"
    pt = (profil.get("font") or {}).get("isi_pt") or 12

    target = None
    for p in doc.paragraphs:
        if p.text.strip().lower() == judul_daftar.lower():
            target = p
            break
    if target is None:
        return False

    # hapus isi lama daftar: paragraf sesudah heading sampai Heading berikutnya.
    # Termasuk TABEL header ("No | Judul | Halaman") — dulu dibiarkan, sehingga
    # daftar yang dibangun menempel di bawah header kosong milik template.
    from docx.text.paragraph import Paragraph
    el = target._p
    nxt = el.getnext()
    while nxt is not None:
        sesudah = nxt.getnext()
        if nxt.tag == qn("w:p"):
            pp = Paragraph(nxt, doc)
            if pp.style and pp.style.name.startswith("Heading"):
                break
            nxt.getparent().remove(nxt)
        elif nxt.tag == qn("w:tbl"):
            nxt.getparent().remove(nxt)
        else:
            break
        nxt = sesudah

    # lebar teks untuk tab stop kanan
    sec = doc.sections[0]
    lebar_cm = (sec.page_width - sec.left_margin - sec.right_margin) / 360000

    titik = target._p
    for entri in entri:
        par = doc.add_paragraph()
        titik.addnext(par._p)
        titik = par._p
        par.paragraph_format.left_indent = Cm(0)
        par.paragraph_format.space_after = Pt(2)
        par.paragraph_format.line_spacing = 1.0
        par.alignment = WD_ALIGN_PARAGRAPH.LEFT
        par.paragraph_format.tab_stops.add_tab_stop(
            Cm(lebar_cm), WD_TAB_ALIGNMENT.RIGHT, 2)   # 2 = dot leader
        r = par.add_run(f"{JENIS[jenis_key]['kata']} {entri['nomor']}\t{entri['halaman']}")
        r.font.name = font; r.font.size = Pt(pt)
        if entri["judul"]:
            p2 = doc.add_paragraph()
            titik.addnext(p2._p)
            titik = p2._p
            p2.paragraph_format.left_indent = Cm(1.0)
            p2.paragraph_format.space_after = Pt(6)
            p2.paragraph_format.line_spacing = 1.0
            r = p2.add_run(entri["judul"])
            r.font.name = font; r.font.size = Pt(pt)
    return True


def _daftar_halaman_isi(pdf: str) -> set[int]:
    """Halaman yang memuat heading Daftar Tabel/Gambar/Lampiran."""
    judul = {v["daftar"].lower() for v in JENIS.values()}
    out: set[int] = set()
    for n, teks in _halaman_caption(pdf):
        if any(j in teks.lower() for j in judul):
            out.add(n)
    return out


def _cari_halaman(pdf: str, profil: dict, daftar: list[dict],
                  abaikan: set[int] | None = None) -> None:
    """Isi `halaman` tiap entri dengan nomor halaman tampil (dari render).

    Nomor diambil dari CAPTION di badan naskah. Dulu seluruh kolom berisi "1"
    karena caption pertama ditemukan di halaman Daftar Tabel (daftar memuat
    semua judul) dan pencarian sesudahnya meneruskan dari halaman itu.
    Pencarian sekarang dua lapis:

    1. halaman yang memuat "Tabel <nomor> <judul>" persis (caption asli),
       melewati halaman daftar;
    2. bila tidak ketemu, halaman yang memuat judulnya saja (caption terpecah
       dua baris pada kolom sempit).
    """
    halaman = _halaman_caption(pdf)
    if not halaman:
        return
    abaikan = abaikan or set()
    bab_pertama = next((n for n, t in halaman
                        if re.search(r"\bBAB\s+[IVXLC]+\b", t)), 1)
    ph = profil.get("penomoran_halaman") or {}

    def cari(entri, pola, mulai=0):
        for i in range(mulai, len(halaman)):
            n, teks = halaman[i]
            if n in abaikan:
                continue
            if pola in teks.lower():
                return n
        return None

    posisi = 0
    for entri in daftar:
        pola_persis = f"{JENIS_INV.get(entri['jenis'], {}).get('kata', 'Tabel')} " \
                      f"{entri['nomor']} {entri['cari']}".lower()
        pola_pendek = f"{entri['jenis']} {entri['nomor']}".lower()
        n = cari(entri, pola_persis, posisi) or cari(entri, pola_pendek, 0) \
            or cari(entri, entri["cari"], 0)
        if n:
            entri["halaman"] = _nomor_tampil(n, bab_pertama, ph)
            posisi = max(0, n - 1)
        else:
            entri["halaman"] = ""


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Bangun Daftar Tabel/Gambar/Lampiran dan nomori ulang caption.")
    ap.add_argument("docx")
    ap.add_argument("profil")
    ap.add_argument("--pdf", help="PDF hasil render (tanpa ini dirender sendiri)")
    ap.add_argument("--cek", action="store_true", help="laporkan, jangan menulis")
    ap.add_argument("--hanya-renumber", action="store_true",
                    help="perbaiki nomor caption saja, jangan bangun daftarnya")
    a = ap.parse_args()

    if not os.path.isfile(a.docx) or not os.path.isfile(a.profil):
        print("GAGAL: berkas docx atau profil tidak ada", file=sys.stderr)
        return 2
    try:
        import yaml
        from docx import Document
    except ImportError as exc:
        print(f"GAGAL: dependensi kurang ({exc}); jalankan dengan venv repo",
              file=sys.stderr)
        return 2

    profil = yaml.safe_load(open(a.profil, encoding="utf8"))
    doc = Document(a.docx)
    hasil = renumber(doc, profil)

    if a.cek:
        for j, entri in hasil.items():
            print(f"{JENIS[j]['kata']:9} {len(entri)} caption"
                  + ("" if entri else "  (tidak ada)"))
            for e in entri[:4]:
                print(f"    {JENIS[j]['kata']} {e['nomor']}  {e['judul'][:52]}")
        doc.save(a.docx) if False else None
        return 0

    pdf, tmp = (a.pdf, None)
    if not a.hanya_renumber and not pdf:
        pdf, tmp = _render_pdf(a.docx)
        if not pdf:
            print("catatan: soffice tidak ada — nomor halaman daftar dikosongkan",
                  file=sys.stderr)

    doc.save(a.docx)   # simpan renumber dulu supaya render memuat nomor baru
    if not a.hanya_renumber:
        if pdf == a.pdf and a.pdf:
            pdf, tmp2 = _render_pdf(a.docx)     # render ulang setelah renumber
            tmp = tmp2 or tmp
        abaikan = _daftar_halaman_isi(pdf) if pdf else set()
        for j, entri in hasil.items():
            if entri and pdf:
                _cari_halaman(pdf, profil, entri, abaikan)
        doc = Document(a.docx)
        dibuat = []
        for j, entri in hasil.items():
            if not entri:
                continue
            if _isi_daftar(doc, j, entri, profil):
                dibuat.append(f"{JENIS[j]['daftar']} ({len(entri)})")
        doc.save(a.docx)
        if dibuat:
            print("daftar dibangun: " + ", ".join(dibuat))
        else:
            print("catatan: heading 'Daftar Tabel/Gambar/Lampiran' tidak ditemukan "
                  "— hanya nomor caption yang diperbaiki")
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)

    total = sum(len(v) for v in hasil.values())
    print(f"caption dinomori ulang: {total}")
    for j, entri in hasil.items():
        if entri:
            print(f"  {JENIS[j]['kata']:9} {len(entri)}: "
                  + ", ".join(e["nomor"] for e in entri[:6])
                  + (" ..." if len(entri) > 6 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
