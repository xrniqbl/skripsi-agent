#!/usr/bin/env python3
"""Bangun/ganti daftar isi DOCX dari judul dokumen + nomor halaman hasil render.

Pemakaian:
  python3 buat_daftar_isi.py dokumen.docx profil-kampus.yaml [--pdf render.pdf]

Tanpa --pdf, dokumen dirender dengan soffice ke berkas sementara. Nomor halaman
yang ditampilkan mengikuti skema profil: bagian awal Romawi kecil, bagian pokok
Arab mulai dari bab pertama, bagian akhir lanjutan (konsisten dengan
audit_halaman.py). Hasilnya berupa field TOC Word (dapat di-Update Field) dengan
entri tercache yang sudah benar: style TOC 1/2/3, titik pemimpin dari tab stop
kanan (elemen tab sungguhan, bukan karakter tab di dalam teks), judul persis
seperti di badan dokumen, dan judul DAFTAR ISI tidak ikut terdaftar.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

JUDUL_BAB = re.compile(r'^BAB [IVX]+( [A-ZÀ-Þ ]+)?$')


def romawi(n):
    hasil = ''
    for v, r in ((10, 'x'), (9, 'ix'), (5, 'v'), (4, 'iv'), (1, 'i')):
        while n >= v:
            hasil += r
            n -= v
    return hasil


def teks_halaman(pdf, n):
    out = subprocess.run(['pdftotext', '-f', str(n), '-l', str(n), '-layout', pdf, '-'],
                         capture_output=True, text=True).stdout
    return ' '.join(out.split())


def buat(pdf):
    total = int(subprocess.run(['pdfinfo', pdf], capture_output=True, text=True)
                .stdout.split('Pages:')[1].split()[0])
    isi = {n: teks_halaman(pdf, n) for n in range(1, total + 1)}
    baris = {}
    for n in range(1, total + 1):
        out = subprocess.run(['pdftotext', '-f', str(n), '-l', str(n), '-layout', pdf, '-'],
                             capture_output=True, text=True).stdout
        baris[n] = [l.strip() for l in out.splitlines() if l.strip()]
    return total, isi, baris


def fld(kind, instr=None):
    r = OxmlElement('w:r')
    if instr is not None:
        it = OxmlElement('w:instrText')
        it.set(qn('xml:space'), 'preserve')
        it.text = instr
        r.append(it)
    else:
        f = OxmlElement('w:fldChar')
        f.set(qn('w:fldCharType'), kind)
        r.append(f)
    return r



def _usage(msg: str = "", kode: int = 0) -> None:
    if msg:
        print(msg, file=sys.stderr)
    print(__doc__.strip(), file=sys.stderr if kode else sys.stdout)
    raise SystemExit(kode)


def _butuh(n: int, contoh: str) -> None:
    if len(sys.argv) - 1 < n:
        _usage(f"Kurang argumen. Contoh: {contoh}", 2)

def main():
    if '-h' in sys.argv or '--help' in sys.argv:
        _usage()
    _butuh(2, 'python3 buat_daftar_isi.py dokumen.docx profil-kampus.yaml [--pdf render.pdf]')
    path = sys.argv[1]
    profil = yaml.safe_load(open(sys.argv[2], encoding='utf8'))
    ph = profil.get('penomoran_halaman') or {}
    mulai = int(((ph.get('bagian_pokok') or {}).get('mulai_dari')) or 1)
    pdf = None
    if '--pdf' in sys.argv:
        pdf = sys.argv[sys.argv.index('--pdf') + 1]
    tmpdir = None
    if not pdf:
        if not shutil.which('soffice'):
            print("GAGAL: soffice tidak ditemukan di PATH.\n"
                  "  buat_daftar_isi.py butuh LibreOffice untuk merender nomor halaman.\n"
                  "  Pasang: apt-get install libreoffice  (atau libreoffice-core)\n"
                  "  Alternatif: render sendiri lalu berikan --pdf render.pdf",
                  file=sys.stderr)
            sys.exit(2)
        tmpdir = tempfile.mkdtemp()
        subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', path, '--outdir', tmpdir],
                       capture_output=True)
        pdf = os.path.join(tmpdir, os.path.splitext(os.path.basename(path))[0] + '.pdf')
        if not os.path.isfile(pdf):
            print(f"GAGAL: soffice tidak menghasilkan PDF ({pdf}).", file=sys.stderr)
            sys.exit(2)
    total, isi, baris = buat(pdf)

    bab_pertama = next((n for n in range(1, total + 1)
                        if any(JUDUL_BAB.match(l) for l in baris[n])), None)
    if bab_pertama is None:
        print('GAGAL: halaman bab pertama tidak ditemukan pada render')
        sys.exit(1)

    def nomor_tampil(pdf_hal):
        return romawi(pdf_hal) if pdf_hal < bab_pertama else str(mulai + pdf_hal - bab_pertama)

    doc = Document(path)
    paras = doc.paragraphs
    judul = []  # (paragraf, tingkat, teks)
    for p in paras:
        nama = p.style.name if p.style else ''
        if nama in ('Heading 1', 'Heading 2', 'Heading 3') and p.text.strip():
            judul.append((p, int(nama[-1]), p.text.strip()))
    sasaran_toc = next((p for p, t, x in judul if x.upper() == 'DAFTAR ISI'), None)
    entri = [(t, x) for p, t, x in judul if x.upper() != 'DAFTAR ISI']
    if sasaran_toc is None:
        print('GAGAL: judul DAFTAR ISI (Heading 1) tidak ditemukan di dokumen')
        sys.exit(1)

    # halaman daftar isi mencantumkan semua judul — lewati saat mencari judul,
    # bila tidak, judul bab akan "ditemukan" pada halaman daftar isi itu sendiri
    hal_toc = next((n for n in range(1, bab_pertama)
                    if any(l.upper() == 'DAFTAR ISI' for l in baris[n])), None)

    # cari halaman tiap judul pada render, berurutan mengikuti dokumen
    halaman_terakhir = 1
    pasangan = []
    for tingkat, teks in entri:
        ketemu = None
        for n in range(halaman_terakhir, total + 1):
            if n == hal_toc:
                continue
            if teks.lower() in isi[n].lower():  # style kapital menampilkan huruf besar di render
                ketemu = n
                break
        if ketemu is None:
            print(f'PERINGATAN: judul tidak ditemukan pada render: "{teks[:50]}" — dilewati')
            continue
        halaman_terakhir = ketemu
        pasangan.append((tingkat, teks, nomor_tampil(ketemu)))
    if not pasangan:
        print('GAGAL: tidak ada entri yang berhasil dipasangkan')
        sys.exit(1)

    # hapus blok daftar isi lama: paragraf setelah judul DAFTAR ISI s.d. Heading 1 berikutnya
    body = doc.element.body
    el = sasaran_toc._p
    berikut = el.getnext()
    while berikut is not None:
        nxt = berikut.getnext()
        if berikut.tag == qn('w:p'):
            from docx.text.paragraph import Paragraph
            pp = Paragraph(berikut, doc)
            if pp.style and pp.style.name == 'Heading 1':
                break
            body.remove(berikut)
        else:
            break
        berikut = nxt
    titik = sasaran_toc._p  # sisipkan sesudah judul, berurutan terbalik lewat addnext

    def sisip(elm):
        nonlocal titik
        titik.addnext(elm)
        titik = elm

    p_start = OxmlElement('w:p')
    p_start.append(fld('begin'))
    p_start.append(fld(None, ' TOC \\o "1-3" \\h \\z \\u '))
    p_start.append(fld('separate'))
    sisip(p_start)
    # tab stop kanan berdot leader selebar teks dokumen — dipasang per paragraf
    # agar tidak bergantung pada style TOC bawaan dokumen
    sec = doc.sections[0]
    lebar_twips = int((sec.page_width - sec.left_margin - sec.right_margin) / 635)
    for tingkat, teks, nomor in pasangan:
        ep = OxmlElement('w:p')
        ppr = OxmlElement('w:pPr')
        ps = OxmlElement('w:pStyle')
        ps.set(qn('w:val'), f'TOC{tingkat}')
        ppr.append(ps)
        tabs = OxmlElement('w:tabs')
        tab = OxmlElement('w:tab')
        tab.set(qn('w:val'), 'right')
        tab.set(qn('w:leader'), 'dot')
        tab.set(qn('w:pos'), str(lebar_twips))
        tabs.append(tab)
        ppr.append(tabs)
        sp = OxmlElement('w:spacing')
        sp.set(qn('w:line'), '240')
        sp.set(qn('w:lineRule'), 'auto')
        sp.set(qn('w:after'), '40')
        ppr.append(sp)
        ep.append(ppr)
        r = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.text = teks
        r.append(t)
        ep.append(r)
        r = OxmlElement('w:r')
        r.append(OxmlElement('w:tab'))
        ep.append(r)
        r = OxmlElement('w:r')
        t = OxmlElement('w:t')
        t.text = nomor
        r.append(t)
        ep.append(r)
        sisip(ep)
    p_end = OxmlElement('w:p')
    p_end.append(fld('end'))
    sisip(p_end)

    settings = doc.settings.element
    uf = OxmlElement('w:updateFields')
    uf.set(qn('w:val'), 'true')
    settings.append(uf)
    doc.save(path)
    print(f'daftar isi dibangun: {len(pasangan)} entri, bab pertama pada halaman render {bab_pertama}')


if __name__ == '__main__':
    main()
