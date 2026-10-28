#!/usr/bin/env python3
"""Audit DOCX terhadap profil format kampus (YAML).

Pemakaian: python3 audit_docx.py dokumen.docx profil-kampus.yaml
Keluar dengan kode 1 bila ada kegagalan. Pemeriksaan: ukuran kertas & margin,
font/ukuran/tebal style utama, spasi isi, dan — penting — atribut font tema pada
XML, yang membuat Word menampilkan font lain dari yang tertulis di style.
Nomor halaman dan sistematika diperiksa dari hasil render (lihat SKILL.md).
"""
import re
import sys
import zipfile

import yaml
from docx import Document
from docx.oxml.ns import qn

TOL_CM = 0.25
hasil = []


def catat(nama, ok, detail=''):
    hasil.append((nama, ok, detail))
    print(('LULUS ' if ok else 'GAGAL ') + nama + (f' — {detail}' if detail else ''))


def cm(nilai):
    return round(nilai / 360000, 2)  # EMU -> cm



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
    _butuh(2, 'python3 audit_docx.py dokumen.docx profil-kampus.yaml')
    doc = Document(sys.argv[1])
    profil = yaml.safe_load(open(sys.argv[2], encoding='utf8'))
    dok = profil.get('dokumen') or {}
    mar = dok.get('margin_cm') or {}
    fon = profil.get('font') or {}
    spa = profil.get('spasi') or {}
    nama_font = fon.get('nama') or 'Times New Roman'

    s = doc.sections[0]
    kertas = {'A4': (21.0, 29.7), 'Letter': (21.59, 27.94), 'F4': (21.59, 33.02)}
    w, h = kertas.get(dok.get('ukuran_kertas') or 'A4', kertas['A4'])
    catat('ukuran kertas', abs(cm(s.page_width) - w) <= TOL_CM and abs(cm(s.page_height) - h) <= TOL_CM,
          f'{cm(s.page_width)}x{cm(s.page_height)} cm')
    for sisi, kunci in (('kiri', 'kiri'), ('atas', 'atas'), ('kanan', 'kanan'), ('bawah', 'bawah')):
        nilai = getattr(s, {'kiri': 'left_margin', 'atas': 'top_margin',
                            'kanan': 'right_margin', 'bawah': 'bottom_margin'}[kunci])
        target = mar.get(kunci)
        if target is not None:
            catat(f'margin {sisi}', abs(cm(nilai) - float(target)) <= TOL_CM,
                  f'{cm(nilai)} cm (target {target})')

    def cek_style(nama_style, pt_target, tebal_target=None):
        try:
            st = doc.styles[nama_style]
        except KeyError:
            catat(f'style {nama_style}', False, 'tidak ditemukan')
            return
        f = st.font
        catat(f'{nama_style} font', (f.name or '') == nama_font, f'{f.name}')
        if pt_target:
            ok = f.size is not None and abs(f.size.pt - float(pt_target)) < 0.1
            catat(f'{nama_style} ukuran', ok, f'{f.size.pt if f.size else None} pt (target {pt_target})')
        if tebal_target is not None:
            catat(f'{nama_style} tebal', bool(f.bold) == bool(tebal_target), f'bold={f.bold}')

    jb = fon.get('judul_bab') or {}
    sb = fon.get('subbab') or {}
    cek_style('Normal', fon.get('isi_pt', 12))
    cek_style('Heading 1', jb.get('pt', 14), jb.get('tebal', True))
    cek_style('Heading 2', sb.get('pt', 12), sb.get('tebal', True))
    ls = doc.styles['Normal'].paragraph_format.line_spacing
    if spa.get('isi') and ls:
        catat('spasi isi', abs(float(ls) - float(spa['isi'])) < 0.05, f'{ls} (target {spa["isi"]})')

    z = zipfile.ZipFile(sys.argv[1])
    tema = 0
    for nama in z.namelist():
        if nama.startswith('word/') and nama.endswith('.xml'):
            tema += len(re.findall(r'Theme="', z.read(nama).decode('utf8')))
    catat('atribut font tema pada XML', tema == 0,
          f'{tema} ditemukan (harus 0 — penyebab Word mengganti font)')

    gagal = [h for h in hasil if not h[1]]
    print(f'\nRingkasan: {len(hasil) - len(gagal)}/{len(hasil)} lulus')
    sys.exit(1 if gagal else 0)


if __name__ == '__main__':
    main()
