# Registry Preset Kampus

Preset adalah profil format kampus yang sudah jadi (lihat `../SKILL.md`). Sebelum
mengekstrak panduan dari nol, periksa daftar ini: bila kampus pengguna ada, pakai
presetnya sebagai draf awal — tetap konfirmasikan ringkasannya ke pengguna, karena
panduan bisa berubah antar edisi.

| Berkas | Kampus | Sumber panduan | Status |
|---|---|---|---|
| `universitas-contoh.yaml` | Universitas Contoh | — (fiktif, hanya contoh bentuk isian) | FIKSI |
| `ars-fti.yaml` | Universitas Adhirajasa Reswara Sanjaya — Fakultas Teknologi Informasi | Panduan Penyusunan Laporan Skripsi FTI, Revisi Tahun 2025 (42 halaman) | NYATA |

## Menambah preset kampus nyata

`ars-fti.yaml` adalah **cetakan** terbaik untuk preset baru: setiap angkanya sudah
dikutip dengan nomor butir panduan, dan memuat `catatan_konflik`, `pengecualian`,
serta `ringkasan`. Salin berkasnya, ganti isinya — jangan mulai dari nol.

Perkiraan waktu 20-30 menit per kampus untuk panduan 30-50 halaman.

1. Ekstrak teks panduan: `pdftotext -layout panduan.pdf panduan.txt`.
2. Isi `dokumen`, `font`, `spasi`, `penomoran_halaman`, `caption`, `sitasi` —
   semuanya angka; kutip nomor butirnya di komentar.
3. Isi `sistematika.bagian_awal`, `bab`, `bagian_akhir` **persis seperti panduan**.
   Jangan menormalkan nama: bila panduan menulis "Identifikasi Masalah", tulis itu,
   bukan "Rumusan Masalah". Nama subbab menentukan apakah pemeriksa bisa bekerja.
4. Catat setiap pertentangan internal panduan di `catatan_konflik` — jangan menebak.
   Contoh nyata: panduan menyebut APA tetapi seluruh contohnya memakai
   `(Nama, Tahun:Halaman)`; panduan mencantumkan subbab BAB IV tetapi template
   resminya tidak.
5. Simpan sebagai `presets/<slug-kampus>.yaml`, isi `kampus.sumber_panduan` dengan
   nama dokumen + edisi/tahun, lalu tambahkan satu baris ke tabel di atas.
6. Uji: `python3 scripts/periksa_sistematika.py naskah_contoh.md presets/<baru>.yaml`

Preset hanya berisi KETENTUAN FORMAT dari dokumen publik kampus — jangan pernah
memasukkan data pribadi, naskah skripsi, atau dokumen milik individu ke folder ini
(penjaga konten `tests/tes_bundel.py` akan menggagalkan build).
