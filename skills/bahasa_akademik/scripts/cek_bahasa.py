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
    if re.search(r'  +', teks_asli):
        tambah('mekanik', 'spasi ganda ditemukan')
    if re.search(r'\s+[,.;:!?]', teks_asli):
        tambah('mekanik', 'spasi sebelum tanda baca')
    for kalimat in re.split(r'[.!?]+', teks):
        n = len(kalimat.split())
        if n > 45:
            tambah('kalimat panjang', f'{n} kata — pertimbangkan dipecah', parah=False)


def main():
    path = sys.argv[1]
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
        for i, baris in enumerate(open(path, encoding='utf8'), 1):
            if baris.strip():
                periksa_teks(baris, f'baris {i}', temuan)

    for kategori, label, pesan, _ in temuan:
        print(f'[{kategori}] {label}: {pesan}')
    kesalahan = sum(1 for t in temuan if t[3])
    print(f'\nRingkasan: {kesalahan} kesalahan, {len(temuan) - kesalahan} peringatan')
    sys.exit(1 if kesalahan else 0)


if __name__ == '__main__':
    main()
