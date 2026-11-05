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

### 6b. Penomoran halaman tiga zona — aturan yang paling sering salah

Skema baku skripsi Indonesia, dan yang ditegakkan profil:

| Zona | Isi | Format | Posisi |
|---|---|---|---|
| Bagian awal | sampul, pengesahan, pernyataan, kata pengantar, abstrak, daftar isi/gambar/tabel/lampiran | Romawi KECIL (i, ii, iii) | tengah bawah, 2 cm dari tepi |
| Bagian pokok | BAB I … BAB V | Arab mulai 1 | halaman awal bab tengah bawah, halaman lain kanan atas |
| Bagian akhir | Daftar Pustaka, Lampiran, Riwayat Hidup | Arab LANJUTAN (bukan mulai 1) | tengah bawah |

Empat kesalahan yang wajib dicegah, semuanya sudah ditutup kode:

1. **Sampul dan pengesahan tidak dicetak nomornya tetapi tetap dihitung.**
   Dicapai dengan menjadikan SETIAP halaman bagian awal seksi tersendiri
   (`buat_template_lengkap.py`) — bukan dengan mengosongkan footer satu seksi
   penuh, karena itu menghilangkan nomor di semua halaman.
   Dua konvensi didukung lewat profil:
   `bagian_awal.sampul_dihitung: true` (sampul = i → kata pengantar ii) atau
   `false` (pengesahan = i → kata pengantar ii), plus
   `bagian_awal.nomor_disembunyikan: ["Lembar Pengesahan"]`.
2. **Romawi bocor ke bagian pokok.** Perpindahan ke Arab WAJIB menulis
   `w:start="1"` di seksi pertama bab; tanpa itu penghitung meneruskan angka
   Romawi dan BAB I tercetak "16".
3. **Daftar Pustaka kembali ke halaman 1.** Seksi bagian akhir TIDAK boleh
   punya `w:start` — penghitung harus meneruskan dari BAB V.
4. **`titlePg` diwarisi antar seksi.** Seksi baru mewarisi
   `different_first_page_header_footer`, sehingga halaman pertamanya memakai
   footer "first" yang kosong dan nomornya hilang. Set eksplisit ke `False`
   di setiap seksi yang nomornya harus tampil.

`scripts/audit_halaman.py` memeriksa keempatnya halaman per halaman dari hasil
render PDF, termasuk halaman yang nomornya memang disembunyikan
(`nomor_disembunyikan`).

### 6c. Dokumen mahasiswa yang sudah ada — perbaiki, jangan hanya dilaporkan

`audit_docx.py` melaporkan; `scripts/perbaiki_skripsi.py` MEMPERBAIKI. Dipakai
untuk skripsi yang sudah jadi (template lama, hasil konversi, kiriman
pembimbing) yang gagal di titik yang sama berulang kali:

```bash
# audit saja
python3 scripts/perbaiki_skripsi.py Skripsi.docx --profil profil-kampus.yaml --cek-saja

# perbaiki + audit (+ verifikasi nomor halaman dari render)
python3 scripts/perbaiki_skripsi.py Skripsi.docx --profil profil-kampus.yaml --pdf Skripsi.pdf
```

Yang diperbaiki: seluruh atribut font tema dibuang (Word menampilkan
Aptos/Calibri walau style menulis Times New Roman), SEMUA `w:color`
non-hitam dipaksa `000000`, margin & ukuran kertas tiap seksi, dan
format/posisi/pemutusan nomor halaman per zona. Isi naskah tidak disentuh.
Zona ditentukan dengan membagi paragraf per `w:sectPr` dan membaca Heading 1
pertama tiap seksi — bukan "judul terakhir sebelum batas seksi", yang
membaca judul seksi sebelumnya dan membuat semua seksi berlabel bagian awal.

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
- `scripts/periksa_tabel_gambar.py naskah profil-kampus.yaml` — caption tabel
  dan gambar: keberadaan, posisi, format nomor (`Tabel IV.1`), urutan per bab,
  kesesuaian nomor bab, **rujukan di teks**, dan sumber kutipan pada caption.
  Butir rujukan yang paling sering lolos: caption lengkap dan nomor benar, tetapi
  tabelnya tidak pernah disebut di paragraf mana pun.
- `scripts/buat_template_lengkap.py profil-kampus.yaml keluaran.docx [--isi-paragraf N]`
  — membangun kerangka UTUH: sampul (posisi terukur), semua bagian awal, semua
  bab + subbab dengan penomoran multilevel, semua bagian akhir, dan tiga zona
  nomor halaman. `buat_template_docx.py` hanya mengatur style dan menaruh satu
  judul contoh; untuk dokumen yang akan dipakai, pakai skrip ini.
  Tiap bab menjadi seksi sendiri supaya "awal bab tengah bawah, halaman lain
  kanan atas" (panduan 4.5) benar-benar terpenuhi.
- `scripts/buat_template_lengkap.py profil-kampus.yaml out.docx --halaman
  presets/ars-fti-halaman.yaml` — menambah BUNYI halaman bagian awal/akhir:
  surat pernyataan, lembar persetujuan/pengesahan, kata pengantar, ringkasan,
  abstract, riwayat hidup, lembar konsultasi, surat keterangan riset. Tanpa
  `--halaman`, halaman hanya berisi judul dan penanda isi.
- Sampul memuat **logo universitas** (`assets/logo-ars.png`, 4,6 × 5,0 cm,
  disalin dari template resmi). Path logo di preset relatif terhadap folder
  skill. Kalau logo tidak ditemukan, sampul keluar tanpa logo **tanpa pesan
  galat** — periksa `d.inline_shapes` bila sampul terlihat kosong.
- `scripts/render_halaman.py presets/ars-fti-halaman.yaml --daftar` — lihat
  halaman apa saja yang tersedia beserta placeholder yang dibutuhkan.
  `--cek` memvalidasi tanpa menulis dokumen.
- `scripts/periksa_penomoran.py naskah.docx profil-kampus.yaml` — khusus `.docx`.
  Membaca `numbering.xml` dan menghitung nomor yang AKAN tampil, karena membaca
  heading dari style saja tidak cukup: subbab bisa tanpa `numPr`, `lvlText`
  salah, atau `numId` dipakai ulang lintas bab sehingga semua bab jadi "2.x".
- `skills/bahasa_akademik/scripts/cek_bahasa.py naskah` — ragam baku, kata tidak
  baku, singkatan tidak resmi (dll/dst/dsb/ybs), kata ulang berangka (`kata2`),
  garis miring sebagai "atau", dan "daripada" sebagai "dari".

Keenamnya **pemeriksa pola, bukan vonis**. Setiap temuan wajib dinilai konteksnya;
jangan memperbaiki otomatis tanpa membaca kalimatnya.

### 7b. Naskah yang bertentangan dengan dirinya sendiri

Format bisa lulus 100% sementara isinya saling meniadakan. Dua pemeriksa menutup
kelas cacat itu — keduanya sering lolos karena dokumennya "terlihat rapi".

- `scripts/periksa_konsistensi.py naskah [--profil P] [--ketat]` — memeriksa:
  nama & NIM sama di semua halaman (satu huruf beda = dokumen dikembalikan);
  tanggal pengesahan tidak mendahului tanggal sidang; **jumlah butir**
  Identifikasi/Rumusan Masalah = jumlah Tujuan = jumlah Simpulan (pertanyaan
  klasik penguji: "tujuan Anda empat, simpulan Anda tiga?"); rujukan `Bab VI`
  pada skripsi lima bab; serta aturan `catatan_kaki:` dan `lampiran:` yang
  diikat profil.

  Fungsi pencarian bagiannya sengaja memilih kandidat dengan butir terbanyak,
  karena heading yang sama juga muncul di Daftar Isi — memilih kemunculan
  pertama membuat jumlahnya selalu terbaca 0 dan pemeriksaan tidak pernah
  bekerja. Pemeriksaan jumlah dilewati bila salah satu bagian hanya punya satu
  butir (tujuan penelitian paragraf-tunggal bukan daftar).

- `scripts/periksa_sitasi_numerik.py naskah --gaya ieee|vancouver` — pada gaya
  numerik, `[3]` di teks harus benar-benar entri ke-3. Tiga temuan: nomor
  disitasi tanpa entri, entri tidak pernah disitasi, dan urutan kemunculan
  tidak menaik (tanda daftar pustaka tidak diurutkan ulang sesudah naskah
  disunting). Rentang `[2-5]` dan `[2,4,7]` didukung. Pada profil bergaya APA
  pemeriksaan ini **dilewati** oleh gerbang, karena akan menghasilkan
  kebisingan.

### 7c. Daftar Tabel, Daftar Gambar, dan penomoran caption

`scripts/buat_daftar_tabel_gambar.py dokumen.docx profil.yaml [--cek]
[--hanya-renumber] [--pdf r.pdf]` melakukan dua hal yang biasanya dikerjakan
manual dan salah:

1. **Menomori ulang caption per bab** sesuai gaya profil
   (`Tabel IV.1` Romawi kapital, `Tabel 4.1` Arab, atau berurutan). Nomor
   ditulis sebagai field `SEQ Tabel \* ARABIC \r N` sehingga Word melanjutkan
   sendiri saat caption baru disisipkan. Caption hasil salin-tempel yang
   semuanya berbunyi "Tabel 9.9" diperbaiki dalam satu jalan.
2. **Membangun Daftar Tabel / Daftar Gambar / Daftar Lampiran** dari caption
   yang ditemukan, dengan titik pemimpin dan nomor halaman dari render PDF.

Tiga jebakan yang sudah ditutup di kode:

- Judul caption panjang terpecah menjadi dua paragraf; paragraf kedua bukan
  caption. Tanpa penjagaan, satu tabel dihitung dua kali dan nomornya melompat.
- Blok Daftar Tabel itu sendiri berisi baris berbentuk "Tabel I.1⇥3" yang
  menyerupai caption. Menjalankan ulang skrip pada dokumen yang sudah punya
  daftar membuatnya membaca daftarnya sendiri sebagai caption baru.
- Pencarian nomor halaman wajib melewati halaman daftar; kalau tidak, semua
  entri "ditemukan" di halaman yang memuat seluruh judul dan kolom halaman
  berisi angka yang sama.

### 7d. Kemiripan terhadap korpus skripsi Indonesia

`scripts/cek_kemiripan_korpus.py naskah --indeks korpus/indeks_korpus.json.gz`
membandingkan naskah dengan indeks shingle 5-kata dari 18 skripsi Indonesia
(`korpus/README.md`, `korpus/sumber.json`). Kelas yang ditangkap: frasa yang
dipinjam antar-skripsi — bukan dari jurnal, karena itu yang paling sering lolos
pemeriksa manual.

Indeks hanya memuat hash dan metadata sumber; teks penuh tidak pernah masuk repo
(penjaga konten `tests/tes_bundel.py`). Bangun ulang dengan `--bangun-indeks
folder_teks`. Angka kemiripan adalah **indikator**, bukan skor Turnitin: 18
dokumen tidak sebanding dengan miliaran halaman. Jangan pernah menyebut angkanya
sebagai "hasil Turnitin" kepada pengguna.

### 7e. Uji asumsi klasik (kuantitatif)

`skills/proposal_skripsi/scripts/uji_asumsi.py data.csv --dv Y --iv A,B,C`
menghitung empat uji yang selalu diminta di awal BAB IV dan tidak pernah
disediakan `stats_tests.py` (yang menghitung uji utamanya): Shapiro-Wilk per
variabel, Levene (median-centred), VIF/tolerance, dan Durbin-Watson. Tanpa
dependensi — memakai scipy bila ada, dan melaporkan mesin mana yang dipakai
(`scipy` vs `royston`) supaya jelas mana angka presisi.

### 7f. Aturan pengutipan (kutipan langsung, tidak langsung, sumber lain)

`scripts/periksa_kutipan.py naskah profil-kampus.yaml` membaca blok `kutipan:` profil
(contoh terisi: `presets/ars-fti.yaml`, panduan 4.7). Yang ditangkap:
kutipan langsung tanpa halaman (`(Nama, Tahun)` padahal formatnya `:Halaman`), kutipan
bertanda kutip yang sudah sepanjang blok (>= 5 baris, seharusnya 1 spasi tanpa tanda
kutip), blok yang terlalu pendek atau masih bertanda kutip, "dikutip dari" tanpa
pola "X **dalam** Y (Tahun:Hal)", dan *et al*/*dkk* dalam teks menurut
`kutipan.et_al_dalam_teks`.

Batasan yang harus disampaikan ke pengguna: **panjang kutipan hanya perkiraan dari
jumlah kata** (jumlah baris baru pasti setelah render), dan indentasi menjorok tidak
diperiksa karena ukurannya tidak disebut panduan (`menjorok_cm: null`). Profil tanpa
blok `kutipan:` dilewati, bukan ditebak.

Profil ARS juga mencatat penomoran bertingkat (`2.1.` → `2.1.1.`, serta bentuk
alternatif `A.`) dan daftar berjenjang `1.` → `a.` → `1)` → `a)` pada
`penomoran_bertingkat:` / `paragraf:`. Itu **pencatatan**, belum ditegakkan generator
templat — lihat CHANGELOG 2.11.0.

### 8. Satu perintah untuk semua gerbang isi

`scripts/gate_naskah.sh NASKAH PROFIL.yaml [--ketat] [--min-jurnal N] [--tahun-acuan T]`
menjalankan kedua belas pemeriksa berurutan (penomoran hanya `.docx`; sitasi
numerik hanya pada profil IEEE/Vancouver; kemiripan hanya bila indeks ada) dan
melaporkan satu ringkasan. Tanpa `--ketat`, hanya galat yang menggagalkan;
dengan `--ketat`, satu peringatan pun menggagalkan. Batas minimal jurnal dibaca
dari `sitasi.min_jurnal_atau_prosiding` profil — jangan diulang sebagai angka di
tempat lain. Indeks korpus lain bisa diarahkan lewat `INDEKS_KORPUS=...`.

```text
  ~ sistematika   — Ringkasan: 0 galat, 5 peringatan
  ~ pustaka       — Ringkasan: 0 galat, 1 peringatan
  OK ringkasan    — Ringkasan: 0 galat, 0 peringatan
  OK tabel/gambar — Ringkasan: 0 galat, 0 peringatan
  - penomoran     — dilewati (bukan .docx; nomor sudah berupa teks)
  OK bahasa       — Ringkasan: 0 kesalahan, 0 peringatan
  OK bab IV/V     — Ringkasan: 0 galat, 0 peringatan
  OK konsistensi  — Ringkasan: 0 galat, 0 peringatan
  - sitasi        — dilewati (gaya APA, bukan numerik)
  OK kemiripan    — lulus
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
isian, satu preset NYATA yang ditulis tangan dengan kutipan butir panduan
(`ars-fti.yaml` untuk Fakultas Teknologi Informasi Universitas Adhirajasa Reswara
Sanjaya, Panduan Penyusunan Laporan Skripsi Revisi 2025), dan 28 preset hasil
`campus_json2yaml.py` dari `skills/proposal_skripsi/campus_templates/`.

Preset nyata mengikat: spasi isi 2 (bukan 1,5), caption angka Romawi per bab,
subbab "1.2. Identifikasi Masalah" (bukan "Rumusan Masalah"), BAB II "Landasan
Pemikiran".

**Yang penting soal 28 preset konversi:** semuanya sudah diuji dengan menjalankan
`buat_template_lengkap.py`, dan **5 di antaranya berhenti** karena sumber JSON
kampusnya tidak menyebut margin/spasi (`ipb`, `uad`, `umy`, `unhas`, `custom`).
Itu perilaku yang benar: skrip menolak mencetak dengan nilai nol, dan
`catatan_konflik:` menyebut apa yang harus dicari di panduan. Untuk memakainya
sekarang, timpa lewat CLI
(`--margin kiri=4 --margin atas=4 --margin kanan=3 --margin bawah=3 --spasi 2`).
Status kesiapan tiap berkas ada di tabel `presets/INDEX.md`.

## Batasan

- Skill ini mengekstrak dan menegakkan format; ia tidak menggantikan penilaian
  dosen pembimbing. Bila panduan ambigu, keputusan akhir pada pengguna/dosennya.
- Nilai default pada template profil hanyalah kerangka isian, bukan ketentuan
  kampus mana pun.
