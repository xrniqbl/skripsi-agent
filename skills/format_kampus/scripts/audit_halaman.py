#!/usr/bin/env python3
"""Audit nomor halaman hasil render (PDF) terhadap profil format kampus.

Pemakaian: python3 audit_halaman.py dokumen.pdf profil-kampus.yaml
Membutuhkan pdftotext & pdfinfo (poppler-utils) di PATH.

Zona ditentukan dari sistematika profil: bagian awal = halaman sebelum bab
pertama; bagian akhir dimulai dari entri pertama bagian_akhir yang tampil
sebagai judul halaman (mis. DAFTAR PUSTAKA). Halaman awal bab dideteksi dari
baris judul bab yang utuh (baris daftar isi yang berdot-leader tidak dihitung).
Posisi yang diperiksa: tengah_bawah (slot bawah) dan kanan_atas (slot atas).
Lembar judul (halaman 1) dilewati: teks sampul tidak dapat dibedakan dari
nomor halaman oleh ekstraksi teks — periksa visual bila perlu.
"""
import re
import shutil
import subprocess
import sys

import yaml

ANGKA = re.compile(r'^\d+$')
ROMAWI = re.compile(r'^[ivxl]+$')
JUDUL_BAB = re.compile(r'^BAB [IVX]+( [A-ZÀ-Þ ]+)?$')


def romawi(n):
    hasil = ''
    for v, r in ((10, 'x'), (9, 'ix'), (5, 'v'), (4, 'iv'), (1, 'i')):
        while n >= v:
            hasil += r
            n -= v
    return hasil


def baris(pdf, n):
    out = subprocess.run(['pdftotext', '-f', str(n), '-l', str(n), '-layout', pdf, '-'],
                         capture_output=True, text=True).stdout
    return [l.strip() for l in out.splitlines() if l.strip()]


def slot(ls):
    atas = ls[0] if ls and (ANGKA.match(ls[0]) or ROMAWI.match(ls[0])) else ''
    bawah = ls[-1] if ls and (ANGKA.match(ls[-1]) or ROMAWI.match(ls[-1])) else ''
    return atas, bawah



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
    _butuh(2, 'python3 audit_halaman.py dokumen.pdf profil-kampus.yaml')
    for alat in ('pdfinfo', 'pdftotext'):
        if not shutil.which(alat):
            print(f"GAGAL: '{alat}' tidak ditemukan di PATH.\n"
                  f"  audit_halaman.py butuh poppler-utils.\n"
                  f"  Pasang: apt-get install poppler-utils", file=sys.stderr)
            sys.exit(2)
    pdf = sys.argv[1]
    profil = yaml.safe_load(open(sys.argv[2], encoding='utf8'))
    ph = profil.get('penomoran_halaman') or {}
    sis = profil.get('sistematika') or {}
    total = int(subprocess.run(['pdfinfo', pdf], capture_output=True, text=True)
                .stdout.split('Pages:')[1].split()[0])
    halaman = {n: baris(pdf, n) for n in range(1, total + 1)}

    bab_pertama = next((n for n in range(1, total + 1)
                        if any(JUDUL_BAB.match(l) for l in halaman[n])), None)
    halaman_bab = {n for n in range(1, total + 1)
                   if any(JUDUL_BAB.match(l) for l in halaman[n])}
    akhir_items = sis.get('bagian_akhir') or []
    awal_akhir = None
    # Perbandingan harus TIDAK peka huruf besar-kecil: judul bagian akhir bisa
    # tercetak "Daftar Pustaka" (title case dari style heading) atau
    # "DAFTAR PUSTAKA" (kapital penuh dari template kampus). Versi lama hanya
    # menerima kapital penuh, sehingga zona bagian akhir tidak pernah terdeteksi
    # dan semua halaman di sana diperiksa dengan aturan bagian pokok -> gagal.
    for item in akhir_items:
        target = item.strip().upper()
        for n in range(1, total + 1):
            if any(l.strip().upper() == target for l in halaman[n]):
                awal_akhir = n
                break
        if awal_akhir:
            break
    if bab_pertama is None:
        print('GAGAL: judul bab pertama tidak ditemukan; zona tidak dapat ditentukan')
        sys.exit(1)

    awal = ph.get('bagian_awal') or {}
    pokok = ph.get('bagian_pokok') or {}
    mulai = int(pokok.get('mulai_dari') or 1)
    pos_awal_bab = (pokok.get('awal_bab') or 'tengah_bawah')
    pos_lain = (pokok.get('halaman_lain') or 'kanan_atas')
    gagal = 0

    def periksa(n, zona, harap_slot, harap_nilai):
        nonlocal gagal
        atas, bawah = slot(halaman[n])
        dapat = bawah if harap_slot == 'bawah' else atas
        lain = atas if harap_slot == 'bawah' else bawah
        ok = (dapat == harap_nilai) and (lain == '')
        if not ok:
            gagal += 1
        print(f"{'LULUS' if ok else 'GAGAL'} hal {n:>2} [{zona}] "
              f"harap {harap_slot}='{harap_nilai}' — atas='{atas}' bawah='{bawah}'")

    for n in range(1, total + 1):
        if n == 1 and awal.get('lembar_judul_dihitung_tanpa_nomor', True):
            print(f'LEWATI hal  1 [awal] lembar judul (periksa visual)')
            continue
        if n < bab_pertama:
            periksa(n, 'awal', 'bawah', romawi(n))
        elif awal_akhir and n >= awal_akhir:
            # Bagian akhir melanjutkan penomoran Arab dari bagian pokok.
            # Hitung dari jumlah halaman pokok sebelum awal_akhir, bukan dari
            # selisih indeks halaman — supaya benar walau ada halaman
            # ber-header berbeda di dalamnya.
            periksa(n, 'akhir', 'bawah', str(mulai + (n - bab_pertama)))
        else:
            nilai = str(mulai + (n - bab_pertama))
            posisi = pos_awal_bab if n in halaman_bab else pos_lain
            periksa(n, 'pokok', 'bawah' if posisi == 'tengah_bawah' else 'atas', nilai)

    print(f'\nRingkasan: {total - 1 - gagal}/{total - 1} halaman bernomor lulus')
    sys.exit(1 if gagal else 0)


if __name__ == '__main__':
    main()
