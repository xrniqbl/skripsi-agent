# Tugas Akhir Selain Skripsi

Sejak Permendikbudristek No. 53 Tahun 2023, program sarjana dan sarjana terapan boleh
menetapkan bentuk tugas akhir berupa skripsi, prototipe, proyek, atau bentuk sejenis,
dikerjakan perorangan atau berkelompok, dengan kebijakan di tingkat program studi.

**Tingkat verifikasi:** isi di atas berasal dari ulasan Hukumonline dan pemberitaan,
bukan dari teks peraturan. **Nomor pasal belum diverifikasi — jangan disebut.** Cocokkan
dengan teks resmi di JDIH Kemendikbudristek atau peraturan.go.id.

## Yang harus ditanyakan sebelum menulis

1. Apa bentuk tugas akhir yang ditetapkan prodi: skripsi, prototipe, proyek, publikasi
   jurnal/prosiding, atau lainnya?
2. Perorangan atau kelompok? Bila kelompok, bagaimana pembagian kontribusi dinilai?
3. Apakah prodi punya pedoman tersendiri untuk bentuk itu, dan apa sistematikanya?
4. Apa luaran yang dinilai (produk, laporan, artikel) dan siapa penguji?

## Aturan bundel

- Bila bentuknya **bukan skripsi, jangan memaksakan BAB I–V**. Seluruh preset di
  `presets/` mengunci sistematika skripsi; pakai hanya bagian format dokumennya
  (kertas, margin, font, penomoran halaman) dan ganti `sistematika:` dengan
  ketentuan prodi.
- UNHAS menyebut bab berbasis publikasi dan struktur Pendahuluan–Metode–Hasil–
  Pembahasan–Kesimpulan (butir 4.2.1 a pedomannya). Itu satu contoh nyata bentuk
  yang bukan BAB I–V; kampus lain berbeda.
- Tanpa pedoman prodi untuk bentuk itu, **katakan bahwa sistematikanya belum
  terkunci** dan jangan mengarang. Profil boleh diberi
  `catatan_konflik: ["bentuk tugas akhir non-skripsi; sistematika menunggu pedoman prodi"]`.
- Pemeriksa isi (`periksa_sistematika.py`, `peta_bab45.py`, `periksa_konsistensi.py`)
  mengasumsikan bab skripsi. Jangan menjalankannya pada naskah proyek tanpa
  mengganti sistematika profil.
