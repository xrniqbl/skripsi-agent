#!/usr/bin/env python3
"""Audit kerapian Word sebuah DOCX (pendamping audit_docx.py yang memeriksa profil).

Pemakaian: python3 audit_rapi.py dokumen.docx
Memeriksa disiplin style sesuai references/kerapian-word-dan-daftar-isi.md:
paragraf kosong berlebih, judul palsu (bukan style Heading), loncat tingkat judul,
tabel tanpa caption, gambar tanpa caption, dan spasi ganda. Keluar kode 1 bila ada
kegagalan.
"""
import re
import sys

from docx import Document

JUDUL = re.compile(r'^(BAB [IVX]+\b|\d+\.\d+(\.\d+)?\s+\S)', re.UNICODE)
gagal = []
ingat = []


def catat(nama, ok, detail='', keras=True):
    print(('LULUS ' if ok else 'GAGAL ') + nama + (f' — {detail}' if detail else ''))
    if not ok:
        (gagal if keras else ingat).append(nama)


def main():
    doc = Document(sys.argv[1])
    paras = doc.paragraphs

    kosong = sum(1 for p in paras if not p.text.strip())
    catat('paragraf kosong <= 5', kosong <= 5, f'{kosong} paragraf kosong (spasi manual?)', keras=False)
    if kosong > 5:
        gagal.append('paragraf kosong berlebih')

    palsu = []
    tingkat_terakhir = 0
    loncat = []
    for i, p in enumerate(paras, 1):
        nama = p.style.name if p.style else ''
        if nama.startswith('Heading'):
            try:
                t = int(nama.split()[-1])
            except ValueError:
                continue
            if t > tingkat_terakhir + 1 and tingkat_terakhir:
                loncat.append(f'paragraf {i}: Heading {tingkat_terakhir} -> {t}')
            tingkat_terakhir = t
        elif JUDUL.match(p.text.strip()) and any(r.bold for r in p.runs if r.text.strip()):
            palsu.append(f'paragraf {i}: "{p.text.strip()[:40]}"')
    catat('tanpa judul palsu', not palsu, '; '.join(palsu[:3]))
    catat('tanpa loncat tingkat judul', not loncat, '; '.join(loncat[:3]))

    def teks_sebelum(idx):
        j = idx - 1
        while j >= 0 and not paras[j].text.strip():
            j -= 1
        return paras[j].text.strip() if j >= 0 else ''

    body = list(doc.element.body)
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    urutan = []
    for anak in body:
        if anak.tag.endswith('}p'):
            urutan.append(('p', Paragraph(anak, doc)))
        elif anak.tag.endswith('}tbl'):
            urutan.append(('t', Table(anak, doc)))
    tabel_tanpa = []
    for k, (jenis, obj) in enumerate(urutan):
        if jenis == 't':
            prev = ''
            j = k - 1
            while j >= 0:
                if urutan[j][0] == 'p' and urutan[j][1].text.strip():
                    prev = urutan[j][1].text.strip()
                    break
                j -= 1
            if not re.match(r'^Tabel\s+[IVX\d]', prev):
                tabel_tanpa.append(f'tabel ke-{len([u for u in urutan[:k+1] if u[0]=="t"])} (sebelumnya: "{prev[:30]}")')
    catat('semua tabel bercaption', not tabel_tanpa, '; '.join(tabel_tanpa[:3]))

    # gambar sebelum Heading 1 pertama = sampul (logo) — bukan gambar isi, tanpa caption
    idx_h1 = next((k for k, (j, o) in enumerate(urutan)
                   if j == 'p' and o.style and o.style.name == 'Heading 1'), len(urutan))
    gambar_tanpa = []
    for k, (jenis, obj) in enumerate(urutan):
        if k < idx_h1:
            continue
        if jenis == 'p' and obj._p.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline'):
            nxt = ''
            j = k + 1
            while j < len(urutan):
                if urutan[j][0] == 'p' and urutan[j][1].text.strip():
                    nxt = urutan[j][1].text.strip()
                    break
                j += 1
            if not re.match(r'^Gambar\s+[IVX\d]', nxt):
                gambar_tanpa.append(f'gambar pada elemen ke-{k + 1} (sesudahnya: "{nxt[:30]}")')
    if any(j == 'p' and o._p.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline') for j, o in urutan):
        catat('semua gambar bercaption', not gambar_tanpa, '; '.join(gambar_tanpa[:3]))

    ganda = sum(1 for p in paras if '  ' in p.text)
    catat('tanpa spasi ganda', ganda == 0, f'{ganda} paragraf', keras=False)
    if ganda:
        ingat.append('spasi ganda')

    print(f'\nRingkasan: {len(gagal)} gagal, {len(ingat)} peringatan')
    sys.exit(1 if gagal else 0)


if __name__ == '__main__':
    main()
