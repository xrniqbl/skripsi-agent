#!/usr/bin/env python3
"""Pemeriksa bahasa akademik Bahasa Indonesia untuk naskah skripsi.

Pemakaian: python3 cek_bahasa.py naskah.docx | naskah.md | naskah.txt
Menandai pola yang terdaftar: kata ganti orang pertama/kedua, ragam lisan, kata
tidak baku, pleonasme, dan cacat mekanik (spasi ganda, kalimat terlalu panjang).
Ini pemeriksa pola, bukan vonis: nilai konteks setiap temuan (mengikuti
references/pedoman-bahasa-akademik.md). Keluar kode 1 bila ada temuan kategori
kesalahan.
"""
import re
import sys

KATA_GANTI = ['saya', 'aku', 'kami', 'kita', 'anda', 'kamu']
RAGAM_LISAN = ['banget', 'nggak', 'enggak', 'kayak', 'bikin', 'makanya', 'kok', 'sih', 'dong']
TIDAK_BAKU = {
    'analisa': 'analisis', 'hipotesa': 'hipotesis', 'metoda': 'metode',
    'sistim': 'sistem', 'jadual': 'jadwal', 'praktek': 'praktik',
    'apotik': 'apotek', 'ijin': 'izin', 'resiko': 'risiko',
    'aktifitas': 'aktivitas', 'kreatifitas': 'kreativitas', 'tehnik': 'teknik',
    'frekwensi': 'frekuensi', 'kwalitas': 'kualitas', 'nopember': 'november',
    'pebruari': 'februari', 'obyek': 'objek', 'obyektif': 'objektif',
    'subyektif': 'subjektif', 'dimana': 'di mana', 'kemana': 'ke mana',
    'darimana': 'dari mana', 'keatas': 'ke atas', 'kebawah': 'ke bawah',
}
PLEONASME = ['agar supaya', 'demi untuk', 'turun ke bawah', 'naik ke atas',
             'mundur ke belakang']

# --- aturan teknis panduan kampus (FTI ARS 2025 bab 4.8 & 4.9) ---
# Singkatan tidak resmi yang dilarang panduan, ditulis apa adanya.
SINGKATAN_TERLARANG = {
    'dll': 'dan lain-lain', 'dst': 'dan seterusnya', 'dsb': 'dan sebagainya',
    'ybs': 'yang bersangkutan', 'tsb': 'tersebut', 'dgn': 'dengan',
    'yg': 'yang', 'tdk': 'tidak', 'utk': 'untuk', 'krn': 'karena',
    'thd': 'terhadap', 'sbg': 'sebagai', 'dr': 'dari', 'pd': 'pada',
}

# Kata ulang ditulis dengan tanda hubung, bukan angka 2: "kata2" -> "kata-kata".
# Hati-hati: jangan menandai angka asli seperti "Windows10" atau "H2O".
RE_KATA_ANGKA = re.compile(r'\b([A-Za-z]{3,})2\b')

# Garis miring dipakai sebagai "atau" — dilarang panduan, kecuali singkatan resmi.
# Deteksi: kata/kata dengan kedua sisi berupa kata biasa (huruf), bukan angka/kode.
RE_GARIS_MIRING = re.compile(
    r'\b([A-Za-z]{3,})/([A-Za-z]{3,})\b')

# Singkatan resmi yang WAJIB dibiarkan (jangan ditandai garis miringnya).
GARIS_MIRING_DIIZINKAN = {
    'and/or', 'input/output', 'I/O', 'b/s', 'km/jam', 'MB/s', 'Gb/s',
}

# Penggunaan "daripada" sebagai pengganti "dari" (panduan 4.8).
RE_DARIPADA = re.compile(
    r'\bdaripada\b(?!\s+(?:itu|ini|pada|untuk|dengan|yang))', re.I)

# "dimana", "kemana" sebagai penghubung — sudah ada di TIDAK_BAKU, tapi panduan
# menegaskan lagi; biarkan TIDAK_BAKU yang menangani agar tidak dobel.



def pola(kata):
    return re.compile(r'\b' + re.escape(kata) + r'\b', re.IGNORECASE)


def periksa_teks(teks_asli, label, temuan):
    # URL dan DOI bukan teks bahasa — samarkan HANYA untuk pemeriksaan kata agar
    # kode jurnal di dalam DOI (mis. "j.ijin" pada doi.org/10.1016/j.ijin...)
    # tidak terbaca sebagai kata. Pemeriksaan mekanik tetap memakai teks asli,
    # karena penyamaran sendiri menimbulkan spasi semu.
    teks = re.sub(r'https?://\S+|10\.\d{4,}/\S+', 'URL', teks_asli)

    def tambah(kategori, pesan, parah=True):
        temuan.append((kategori, label, pesan, parah))

    for kata in KATA_GANTI:
        for m in pola(kata).finditer(teks):
            tambah('kata ganti orang', f'"{m.group(0)}" — naskah ilmiah memakai orang ketiga/impersonal')
    for kata in RAGAM_LISAN:
        for m in pola(kata).finditer(teks):
            tambah('ragam lisan', f'"{m.group(0)}" — ganti dengan padanan baku')
    for salah, benar in TIDAK_BAKU.items():
        for m in pola(salah).finditer(teks):
            tambah('kata tidak baku', f'"{m.group(0)}" → "{benar}"')
    for frasa in PLEONASME:
        for m in pola(frasa).finditer(teks):
            tambah('pleonasme', f'"{m.group(0)}" — persingkat')
    for m in re.finditer(r'\bsangat\b[^.!?]{0,40}?\bsekali\b', teks, re.IGNORECASE):
        tambah('pleonasme', f'"{m.group(0)}" — pilih salah satu penguat')

    # --- panduan kampus: singkatan tidak resmi (4.9) ---
    for singkat, panjang in SINGKATAN_TERLARANG.items():
        for m in re.finditer(r'\b' + singkat + r'\b\.?', teks, re.IGNORECASE):
            tambah('singkatan tidak resmi',
                   f'"{m.group(0)}" → "{panjang}" (panduan 4.9)')

    # --- panduan kampus: kata ulang ditulis angka (4.9) ---
    for m in RE_KATA_ANGKA.finditer(teks_asli):
        kata = m.group(1)
        tambah('kata ulang angka',
               f'"{m.group(0)}" → "{kata}-{kata}" (panduan 4.9)')

    # --- panduan kampus: garis miring sebagai "atau" (4.8 butir 6) ---
    for m in RE_GARIS_MIRING.finditer(teks_asli):
        frasa = m.group(0)
        if frasa.lower() in {g.lower() for g in GARIS_MIRING_DIIZINKAN}:
            continue
        # lewati jalur berkas/URL yang sudah disamarkan
        tambah('garis miring sebagai atau',
               f'"{frasa}" → "{m.group(1)} atau {m.group(2)}" (panduan 4.8 butir 6)',
               parah=False)

    # --- panduan kampus: "daripada" sebagai "dari" (4.8) ---
    for m in RE_DARIPADA.finditer(teks):
        tambah('kata salah',
               f'"{m.group(0)}" — gunakan "dari" bila maksudnya asal/sumber '
               f'(panduan 4.8)', parah=False)
    if re.search(r'  +', teks_asli):
        tambah('mekanik', 'spasi ganda ditemukan')
    if re.search(r'\s+[,.;:!?]', teks_asli):
        tambah('mekanik', 'spasi sebelum tanda baca')
    for kalimat in re.split(r'[.!?]+', teks):
        n = len(kalimat.split())
        if n > 45:
            tambah('kalimat panjang', f'{n} kata — pertimbangkan dipecah', parah=False)


def main():
    import argparse
    ap = argparse.ArgumentParser(
        description='Pemeriksa bahasa akademik Bahasa Indonesia untuk naskah skripsi.',
        epilog='contoh: python3 cek_bahasa.py skripsi.md')
    ap.add_argument('naskah', nargs='?', help='berkas .docx/.md/.txt')
    ap.add_argument('--ringkas', action='store_true',
                    help='tampilkan hitungan per kategori saja')
    a = ap.parse_args()
    if not a.naskah:
        ap.print_help(sys.stderr)
        sys.exit(2)

    path = a.naskah
    temuan = []
    if path.endswith('.docx'):
        from docx import Document
        doc = Document(path)
        for i, p in enumerate(doc.paragraphs, 1):
            if p.text.strip():
                periksa_teks(p.text, f'paragraf {i}', temuan)
        for ti, t in enumerate(doc.tables, 1):
            for r in t.rows:
                for c in r.cells:
                    if c.text.strip():
                        periksa_teks(c.text, f'tabel {ti}', temuan)
    else:
        try:
            with open(path, encoding='utf8') as f:
                for i, baris in enumerate(f, 1):
                    if baris.strip():
                        periksa_teks(baris, f'baris {i}', temuan)
        except FileNotFoundError:
            print(f'GAGAL: berkas tidak ada: {path}', file=sys.stderr)
            sys.exit(2)

    if a.ringkas:
        from collections import Counter
        for kat, n in Counter(t[0] for t in temuan).most_common():
            print(f'  {n:4}  {kat}')
    else:
        for kategori, label, pesan, _ in temuan:
            print(f'[{kategori}] {label}: {pesan}')
    kesalahan = sum(1 for t in temuan if t[3])
    print(f'\nRingkasan: {kesalahan} kesalahan, {len(temuan) - kesalahan} peringatan')
    sys.exit(1 if kesalahan else 0)


if __name__ == '__main__':
    main()
