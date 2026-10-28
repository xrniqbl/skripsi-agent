---
name: format_kampus
description: Mengubah buku panduan/pedoman skripsi sebuah kampus (PDF, DOCX, atau teks) menjadi profil format terstruktur (YAML) yang mengikat semua pekerjaan skripsi berikutnya, lalu menghasilkan template DOCX dari profil itu dan mengaudit dokumen jadi terhadapnya. Gunakan di AWAL setiap proyek skripsi baru, atau kapan pun pengguna mengirim panduan/format/template kampusnya, menyebut nama kampus, atau meminta dokumen disesuaikan dengan format kampus tertentu.
---

# Format Kampus — Adaptasi Panduan Skripsi Menjadi Profil yang Mengikat

Satu-satunya sumber kebenaran format dalam bundel ini adalah **profil kampus**:
berkas YAML terstruktur yang diekstrak dari panduan resmi kampus pengguna.
Skill lain (proposal_skripsi, office_skripsi, skripsi_writing, dan seterusnya)
tidak menebak format — mereka membaca profil ini.

## Alur Wajib (lima langkah)

### 1. Terima panduan

Pengguna mengirim panduan/pedoman/template kampusnya dalam bentuk apa pun:
PDF buku panduan, DOCX template, tangkapan layar ketentuan, atau teks tempelan.
Ekstrak teksnya secara penuh (untuk PDF hasil pindaian, baca halaman sebagai gambar).
Jangan mengambil kesimpulan dari satu halaman — baca bab format DAN bab sistematika.

### 2. Ekstrak menjadi profil

Isi semua bidang pada `format-profile-template.yaml` (di folder skill ini) mengikuti
`references/ekstraksi-checklist.md`. Aturan ekstraksi:

- Nilai yang tidak tertulis di panduan diisi `null` dan dicatat sebagai
  "tidak diatur" — **jangan mengarang ketentuan**.
- Bila dua bagian panduan bertentangan, catat keduanya di bidang `catatan_konflik`
  dan tanyakan kepada pengguna pada langkah 3.
- Bedakan aturan dokumen (margin, font, spasi) dari aturan isi (sistematika bab,
  jumlah minimal jurnal, gaya sitasi) — keduanya masuk profil di bagiannya masing-masing.

Simpan hasil sebagai `profil-kampus.yaml` di folder proyek pengguna
(mis. `<proyek>/profil-kampus.yaml`).

### 3. Konfirmasikan ke pengguna

Tampilkan ringkasan profil dalam tabel yang mudah diperiksa: ukuran kertas, margin,
font dan ukuran per elemen, spasi, skema penomoran halaman per bagian, sistematika
bab, gaya sitasi, dan aturan khusus. Minta pengguna mengoreksi yang keliru sebelum
profil dikunci. Profil terkunci = kontrak format untuk seluruh proyek.

### 4. Terapkan

- Hasilkan template acuan DOCX dari profil dengan
  `scripts/buat_template_docx.py profil-kampus.yaml template-kampus.docx`, lalu
  pakai berkas itu sebagai reference-doc (pandoc) atau basis dokumen pada skill
  penulisan mana pun di bundel ini.
- Saat menulis, patuhi bagian isi profil: sistematika bab, urutan bagian awal/akhir,
  format caption, dan gaya sitasi.
- Profil mengalahkan default semua skill lain. Bila pengguna meminta penyimpangan
  sekali saja, catat sebagai pengecualian eksplisit di profil (`pengecualian:`),
  jangan mengubah aturan dasarnya diam-diam.

### 5. Audit sebelum menyatakan selesai

Jalankan `scripts/audit_docx.py dokumen.docx profil-kampus.yaml` dan periksa juga
hasil render dokumen (PDF/gambar):

- Auditor memeriksa margin, ukuran kertas, font/ukuran/spasi style, DAN atribut
  font tema pada XML dokumen. Atribut tema (`w:asciiTheme` dan sejenisnya) membuat
  Microsoft Word menampilkan font tema (mis. Aptos) alih-alih font yang tertulis —
  dokumen yang "terlihat benar" di pemeriksa lain bisa salah di Word. Temuan ini
  selalu dianggap gagal.
- Cocokkan nomor halaman hasil render dengan skema tiga bagian di profil
  (bagian awal / pokok / akhir), posisi dan format angkanya, halaman per halaman.
- Cocokkan struktur dokumen dengan sistematika profil dan format caption-nya.
- Laporkan hasil audit apa adanya. Dokumen belum selesai sebelum audit lulus atau
  penyimpangannya disetujui eksplisit oleh pengguna.

### 6. Kerapian Word dan daftar isi

Dokumen yang lulus profil pun bisa tidak rapi. Standar kerapian bundel ada di
`references/kerapian-word-dan-daftar-isi.md` (disiplin style, caption, anatomi
daftar isi skripsi). Dua alat menegakkannya:

- `scripts/audit_rapi.py dokumen.docx` — memeriksa paragraf kosong berlebih,
  judul palsu (ditebalkan manual, bukan style Heading), loncat tingkat judul,
  tabel/gambar tanpa caption, dan spasi ganda. Jalankan bersama audit profil.
- `scripts/buat_daftar_isi.py dokumen.docx profil-kampus.yaml [--pdf render.pdf]` —
  membangun atau memperbarui daftar isi dari judul dokumen dan nomor halaman
  hasil render: field TOC Word dengan entri tercache yang benar, titik pemimpin
  dari tab stop kanan, dan nomor sesuai skema profil. Jalankan setiap kali
  paginasi berubah; jangan mengetik daftar isi secara manual.

### 7. Periksa isi yang diikat panduan, bukan hanya rupa

Tiga pemeriksa terakhir menutup hal yang tidak terlihat dari DOCX: urutan bagian,
isi Daftar Pustaka, dan aturan bahasa. Semua menerima `.md`, `.txt`, `.docx`,
atau `.pdf`, dan keluar kode 1 bila ada galat — jadi bisa dipakai di alur otomatis.

- `scripts/periksa_sistematika.py naskah profil-kampus.yaml [--abaikan-opsional]`
  — mencocokkan naskah dengan `sistematika:` profil: kelengkapan dan URUTAN
  bagian awal/akhir, keberadaan setiap bab dan subbab, format penomoran subbab
  (`2.1.` vs `2.1`), dan penomoran caption (`Tabel IV.1`, bukan `Tabel 4.1`).
  Bagian yang di panduan ditandai "*jika ada" (Daftar Simbol/Gambar/Tabel,
  Surat Keterangan Riset) dilaporkan sebagai peringatan bila `--abaikan-opsional`.
- `scripts/periksa_pustaka.py naskah [--tahun-acuan 2026] [--min-jurnal 10]`
  — Daftar Pustaka terhadap `sitasi:` profil: urutan abjad, `et al.`/`dkk`,
  gelar akademik, usia terbitan, jumlah jurnal, larangan Blogspot/Wordpress/
  Wikipedia, tanggal unduh sumber web, dan sitasi dalam teks yang tidak punya
  entri (atau sebaliknya).
- `scripts/periksa_ringkasan.py naskah profil-kampus.yaml` — Ringkasan dan
  Abstract terhadap `ringkasan:` profil: panjang kata, empat unsur wajib
  (masalah, metode, hasil, manfaat), jumlah kata kunci, dan kesejajaran panjang
  Abstract dengan Ringkasan.
- `skills/bahasa_akademik/scripts/cek_bahasa.py naskah` — ragam baku, kata tidak
  baku, singkatan tidak resmi (dll/dst/dsb/ybs), kata ulang berangka (`kata2`),
  garis miring sebagai "atau", dan "daripada" sebagai "dari".

Keempatnya **pemeriksa pola, bukan vonis**. Setiap temuan wajib dinilai konteksnya;
jangan memperbaiki otomatis tanpa membaca kalimatnya.

### 8. Satu perintah untuk semua gerbang isi

`scripts/gate_naskah.sh NASKAH PROFIL.yaml [--ketat] [--min-jurnal N] [--tahun-acuan T]`
menjalankan kelima pemeriksa berurutan dan melaporkan satu ringkasan. Tanpa
`--ketat`, hanya galat yang menggagalkan; dengan `--ketat`, satu peringatan pun
menggagalkan. Batas minimal jurnal dibaca dari `sitasi.min_jurnal_atau_prosiding`
profil — jangan diulang sebagai angka di tempat lain.

```text
  ~ sistematika  — Ringkasan: 0 galat, 5 peringatan
  OK pustaka     — Ringkasan: 0 galat, 1 peringatan
  OK ringkasan   — Ringkasan: 0 galat, 0 peringatan
  OK bahasa      — Ringkasan: 0 kesalahan, 0 peringatan
  OK bab IV/V    — Ringkasan: 0 galat, 0 peringatan
```

## Preset

Folder `presets/` adalah registry profil kampus yang sudah jadi (daftarnya di
`presets/INDEX.md`). Alur memakainya:

1. Sebelum mengekstrak panduan dari nol, cari kampus pengguna di registry.
2. Bila ada presetnya, jadikan itu draf awal profil — tetapi tetap tampilkan
   ringkasannya untuk dikonfirmasi pengguna, dan sarankan mencocokkan dengan
   edisi panduan terbaru kampusnya.
3. Bila belum ada, ekstrak dari panduan pengguna seperti biasa; tawarkan menyimpan
   hasilnya sebagai preset baru mengikuti aturan di `presets/INDEX.md`.

Registry berisi satu contoh FIKSI (`universitas-contoh.yaml`) sebagai acuan bentuk
isian, dan satu preset NYATA: `ars-fti.yaml` untuk Fakultas Teknologi Informasi
Universitas Adhirajasa Reswara Sanjaya (Panduan Penyusunan Laporan Skripsi,
Revisi 2025). Preset nyata mengikat: spasi isi 2 (bukan 1,5), caption angka
Romawi per bab, subbab "1.2. Identifikasi Masalah" (bukan "Rumusan Masalah"),
BAB II "Landasan Pemikiran".

## Batasan

- Skill ini mengekstrak dan menegakkan format; ia tidak menggantikan penilaian
  dosen pembimbing. Bila panduan ambigu, keputusan akhir pada pengguna/dosennya.
- Nilai default pada template profil hanyalah kerangka isian, bukan ketentuan
  kampus mana pun.
