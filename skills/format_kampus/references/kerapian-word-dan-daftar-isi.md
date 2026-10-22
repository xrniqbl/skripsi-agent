# Standar Kerapian Word dan Daftar Isi Skripsi

Dokumen yang rapi dibangun dari style, bukan dari format manual. Acuan ini dipakai
oleh generator template dan auditor di skill format_kampus, dan berlaku umum untuk
skripsi Indonesia (profil kampus tetap yang tertinggi bila berbeda).

## 1. Disiplin Style

- Semua judul memakai style Heading 1/2/3 — tidak ada judul "palsu" (teks Normal
  yang ditebalkan manual). Judul palsu merusak daftar isi otomatis, panel navigasi,
  dan penomoran.
- Isi memakai Normal/Body Text. Perubahan tampilan dilakukan dengan mengubah
  style, bukan memformat teks satu per satu (direct formatting hanya untuk
  penekanan lokal yang memang disengaja: istilah miring, simbol).
- Jarak antarparagraf diatur lewat spasi sebelum/sesudah pada style — **bukan**
  dengan paragraf kosong berantai (Enter berkali-kali). Paragraf kosong membuat
  paginasi rapuh dan daftar isi bergeser.
- Judul tidak terpisah dari isi pertamanya: aktifkan *keep with next* pada style
  judul, dan *widow/orphan control* pada isi, agar judul tidak yatim di kaki halaman.
- Satu dokumen satu sistem: font, ukuran, spasi, dan skema penomoran hanya berasal
  dari profil kampus (lihat SKILL.md format_kampus).

## 2. Tabel dan Gambar

- Setiap tabel didahului caption "Tabel X.Y …" pada posisi sesuai profil
  (umumnya di atas tabel, rata tengah) dan dirujuk dari teks ("Berdasarkan
  Tabel 3.1, …"). Tabel tanpa caption dan tanpa rujukan dianggap belum selesai.
- Setiap gambar diikuti caption "Gambar X.Y …" (umumnya di bawah gambar).
- Tabel tidak terpotong sembarangan: baris judul tabel berulang di halaman
  berikutnya (header row repeat) bila tabel melewati halaman.
- Isi tabel boleh lebih rapat dari isi naskah (spasi dan ukuran mengikuti profil),
  tetapi konsisten di seluruh dokumen.

## 3. Anatomi Daftar Isi yang Rapi (konvensi skripsi Indonesia)

- Judul halaman: "DAFTAR ISI" sebagai judul bab (Heading 1) — dan **tidak** ikut
  terdaftar sebagai entri di dalam daftar isi itu sendiri.
- Entri = teks judul persis sama dengan judul di badan dokumen (termasuk nomor
  subbabnya: "1.1 Latar Belakang"), maksimal tiga tingkat (bab, subbab, sub-subbab).
- Nomor halaman rata kanan dengan **titik pemimpin (dot leader)** yang mengisi
  ruang antara judul dan nomor — bukan spasi manual, bukan tab tanpa leader.
- Indentasi bertingkat: entri subbab menjorok lebih dalam dari entri bab, konsisten.
- Bagian awal memakai nomor Romawi kecil (ii, iii, …); bagian pokok dan akhir
  memakai angka Arab sesuai skema profil — angka pada daftar isi harus sama dengan
  nomor tercetak pada halaman tujuannya.
- Urutan entri mengikuti urutan dokumen; bagian awal (Kata Pengantar, Abstrak,
  dst.) lazim ikut terdaftar dengan nomor Romawinya.
- Daftar isi dibangun dari field TOC Word (agar bisa diperbarui dengan
  klik kanan → Update Field) dengan hasil tercache yang sudah benar, sehingga
  dokumen yang dibuka tanpa diperbarui pun tampil lengkap.
- Judul bab pada entri daftar isi lazim ditebalkan atau dibedakan tipografinya
  secara konsisten (mengikuti style TOC 1/2/3 dari template kampus).

## 4. Pemeriksaan Kerapian (yang diaudit audit_rapi.py)

- Paragraf kosong berlebih (indikasi spasi manual).
- Judul palsu: paragraf non-Heading yang berbentuk judul bab/subbab dan ditebalkan.
- Tabel tanpa caption di atasnya; gambar tanpa caption di bawahnya.
- Loncat tingkat judul (Heading 1 langsung ke Heading 3).
- Spasi ganda di dalam teks.
