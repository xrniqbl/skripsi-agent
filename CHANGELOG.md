# Changelog

Semua perubahan berarti pada bundel Skripsi Agent dicatat di sini.
Format mengikuti Keep a Changelog; versi mengikuti Semantic Versioning.

## [2.3.0] — 2026-10-28

### Ditambahkan
- **`format_kampus/scripts/periksa_ringkasan.py`** — memeriksa Ringkasan dan
  Abstract terhadap `ringkasan:` profil kampus: panjang kata, empat unsur wajib
  (masalah, metode, hasil, manfaat), jumlah kata kunci, dan kesejajaran panjang
  Abstract dengan Ringkasan. Membedakan `ringkasan_hilang` (heading tidak ada)
  dari `ringkasan_kosong` (heading ada, isi belum diisi) — dua kondisi yang butuh
  tindakan berbeda.
- **`format_kampus/scripts/gate_naskah.sh`** — satu perintah menjalankan kelima
  pemeriksa isi (sistematika, pustaka, ringkasan, bahasa, pemetaan BAB IV/V) dan
  melaporkan satu ringkasan. Mendukung `--ketat` (peringatan = gagal),
  `--min-jurnal`, `--tahun-acuan`. Batas minimal jurnal dibaca dari profil,
  tidak diulang sebagai angka di skrip.
- Naskah uji baru: `naskah_ringkasan_baik.md`, `naskah_ringkasan_buruk.md`,
  `naskah_ringkasan_kosong.md`, `naskah_fti_lengkap.md` (naskah patuh panduan
  ARS dari awal sampai lampiran, dipakai uji gerbang menyeluruh).

### Diperbaiki
- **`periksa_pustaka.py`**: Daftar Pustaka kosong dilaporkan kode 2 ("berkas
  salah") padahal itu galat naskah. Sekarang `pustaka_kosong` dengan kode 1.
- **`format_kampus/tests/run_tests.sh`**: harness hanya tahu menjalankan `$PY`,
  sehingga skrip `.sh` diperlakukan sebagai modul Python dan uji `--help` gagal
  karena mencari `gate_naskah.py`. Ditambah `skrip()` yang memilih `bash` untuk
  `.sh`; `gate_naskah.sh` dikeluarkan dari loop pemeriksa `--help`.
- **`gate_naskah.sh --help`** keluar 2 karena digabung dengan cek jumlah argumen.
  Dipisah: `--help` keluar 0, argumen kurang keluar 2.
- Nama pemeriksa di ringkasan gerbang dirapikan (perataan sebelumnya memakai
  spasi manual sehingga rawan bergeser saat nama berubah).

### Dokumentasi
- **README.md ditulis ulang** agar sesuai kenyataan: "20 skill" → 24 skill
  ber-`SKILL.md`, `ars_shared_files/` yang sudah dihapus tidak lagi disebut,
  `bab_iv_v` / `revisi_pembimbing` / `sidang` / `office_skripsi_pdf|pptx|spreadsheet`
  yang sebelumnya tidak terdokumentasi kini masuk tabel, dan bagian "dua lapis
  pemeriksaan" menjelaskan lapis isi — bukan hanya lapis rupa.
- `SKILL.md` root: gerbang mutu naskah dari "ketiganya" menjadi lima pemeriksa
  wajib (sistematika, pustaka, ringkasan, bahasa, kerapian, daftar isi).

### Tes
`format_kampus` 49 → 69 pemeriksaan. `tes_bundel` 36. Semua lulus.

## [2.2.0] — 2026-10-28

### Konteks
Panduan resmi Fakultas Teknologi Informasi Universitas Adhirajasa Reswara Sanjaya
(ARS), Revisi 2025, 42 halaman. Membaca panduan itu memunculkan enam ketentuan
yang membuat alat bundel ini gagal atau memberi hasil menyesatkan.

### Ditambahkan
- **Preset nyata `format_kampus/presets/ars-fti.yaml`** — profil format lengkap
  dari panduan FTI ARS 2025: margin 4/3/3/3 cm, TNR 12, **spasi isi 2** (bukan
  1,5), caption angka Romawi per bab, 15 bagian awal, sistematika lima bab, aturan
  sitasi APA-gaya-panduan, aturan daftar pustaka, ketentuan sidang. Setiap angka
  dikutip dengan nomor butir panduan; empat konflik internal panduan dicatat di
  `catatan_konflik` alih-alih ditebak.
- **Preset `proposal_skripsi/campus_templates/ars_fti.json`** — preset yang sama
  dalam format yang dibaca `apply_campus_template.py`, termasuk catatan isi per
  subbab.
- **`format_kampus/scripts/periksa_sistematika.py`** — memeriksa kelengkapan DAN
  URUTAN bagian awal/akhir, keberadaan setiap bab dan subbab, format penomoran
  subbab (`2.1.` vs `2.1`), serta penomoran caption (`Tabel IV.1` vs `Tabel 4.1`).
  Sebelumnya tidak ada satu pun alat yang memeriksa sistematika.
- **`format_kampus/scripts/periksa_pustaka.py`** — Daftar Pustaka terhadap
  ketentuan 4.10: urutan abjad, larangan `et al.`/`dkk`, gelar akademik, usia
  terbitan, jumlah jurnal, larangan Blogspot/Wordpress/Wikipedia, tanggal unduh
  sumber web, dan sitasi teks yang tidak punya entri.
- Tes: `format_kampus` 25 → 49 pemeriksaan; `bahasa_akademik` kini punya tes
  (12 pemeriksaan).

### Diperbaiki
- **`bab_iv_v/peta_bab45.py` gagal total pada naskah yang patuh panduan.** Pola
  rumusan masalah hanya mengenal "Rumusan/Perumusan Masalah/Pertanyaan Penelitian",
  sedangkan panduan ARS memakai **"Identifikasi Masalah"** — akibatnya 0 butir
  rumusan terdeteksi dan pemeriksaan 1:1 dengan simpulan tidak pernah berjalan.
  Ditambah: nomor subbab berpola `4.1.` (bertitik) tidak dikenali `RE_SUBBAB`.
  Keduanya diperbaiki. Ditambahkan pula `SUBBAB_GENERIK`: bila judul subbab
  ditetapkan panduan (Penyajian Hasil Penelitian / Pembahasan / Implikasi), naskah
  tidak lagi dituduh "cakupan rendah" — dilaporkan sebagai `pemetaan_tidak_terverifikasi`.
- **`bahasa_akademik/cek_bahasa.py` tidak memeriksa aturan 4.8/4.9.** Naskah
  berisi "dll", "dst", "kata2", "PKL/riset", dan "daripada" lolos tanpa temuan.
  Sekarang keempatnya ditangkap, plus `--help`/`--ringkas` dan kode keluar 2 untuk
  argumen salah (sebelumnya `IndexError`).
- **`proposal_skripsi/apply_campus_template.py`**: kunci cek `batasan` memakai
  salah ketik `ruas\s+lingkup` sehingga subbab "Ruang Lingkup" tidak pernah
  terdeteksi; kunci cek untuk subbab ARS (`identifikasi_masalah`, `landasan_teori`,
  `penelitian_terdahulu`, dst.) tidak ada sehingga pemeriksaan isi dilewati diam-diam.
- **`scripts/cek_dependensi.py`** tidak punya pemetaan `PIL → Pillow`, sehingga
  melaporkan "tidak tercatat" padahal sudah ada di requirements.
- **Penjaga konten `tests/tes_bundel.py`** memakai kata terlarang yang mencakup
  nama kampus — padahal preset kampus WAJIB menyebut nama kampusnya. Daftar
  dipersempit ke identitas pribadi (nama orang, alamat, nomor telepon, nama proyek
  pribadi). Identitas pribadi juga dibersihkan dari contoh/`default` pada
  `scripts/buat_dokumen_usaha.py`.

### Catatan
Preset `ars-fti` mengikat perilaku alat lain: `format_kampus` menghasilkan template
dengan spasi 2, dan `proposal_skripsi` memakai `ars_fti` sebagai preset kampus.

## [2.1.0] — 2026-10-28

### Ditambahkan
- **`bab_iv_v`** — menutup lubang terbesar bundel: sebelumnya BAB IV dan V hanya
  diringkas dalam 6 baris tabel di `skripsi_writing`. Skill ini menangani pemisahan
  hasil vs pembahasan, pola pembahasan 4 paragraf (jawaban → perbandingan sama/beda →
  mekanisme → implikasi+batas), penanganan hasil tidak signifikan (4 penyebab yang sah),
  dan aturan simpulan 1:1 dengan rumusan masalah. Pemeriksa `peta_bab45.py` mendeteksi
  kata tafsir di bagian Hasil, jumlah simpulan tidak sama, angka tanpa sumber, effect
  size hilang, dan saran tanpa pelaku.
- **`sidang`** — persiapan seminar proposal, seminar hasil, dan sidang akhir. Kerangka
  slide per jenis (10/15/20 menit), bank 60+ pertanyaan penguji per kelompok, teknik
  menjawab 3-kalimat, kartu 10 angka kunci. `audit_sidang.py` membangkitkan pertanyaan
  dari naskah sendiri (R², n kecil, klaim generalisasi, kata lemah).
- **`revisi_pembimbing`** — mengubah catatan pembimbing (tulisan tangan, komentar Word,
  WhatsApp) menjadi daftar kerja terlacak. `parse_revisi.py` memecah + mengklasifikasi
  prioritas, lalu memverifikasi bahwa butir "selesai" punya bukti terukur dan bukti itu
  benar-benar ada di naskah.
- **`proposal_skripsi/scripts/verify_doi.py`** — penegak aturan "DOI wajib resolve" yang
  selama ini hanya tertulis di SKILL.md tanpa alat. Memeriksa Crossref + DataCite +
  doi.org, memberi empat verdict, dan menandai DOI yang kemungkinan dikarang.
- **`requirements.txt`** (+ `-office`, `-dev`) dan `scripts/cek_dependensi.py` —
  mendeteksi impor pihak ketiga yang belum tercatat atau belum terpasang.
- `tests/run_tests.sh` untuk `format_kampus`, `bab_iv_v`, `sidang`, `revisi_pembimbing`
  (total 78 pemeriksaan baru).

### Diubah
- **Duplikasi `skills/ars_shared_files/` dihapus.** Isinya byte-identik dengan
  `skills/shared/` (173 file, 3 MB dari 11 MB repo). Rujukan path di 5 SKILL.md `ars_*`
  diseragamkan ke `skills/shared/`.
- `SKILL.md` root: router ditambah 4 baris tahap (DOI, BAB IV/V, sidang, revisi).
- `README.md`: bagian "Peta Alur Lengkap: Nol Sampai Sidang" + tabel pemeriksa per tahap.
- `INSTALL.md`: dependensi per kelompok, tabel alat sistem (soffice/poppler/pandoc),
  perintah tes.
- `tests/tes_bundel.py`: 16 → 30 pemeriksaan, mencakup empat skill baru, bagian
  dependensi, dan penjaga anti-duplikasi.

### Diperbaiki
- `format_kampus/scripts/*.py` — lima skrip tidak punya `--help` dan gagal dengan
  `IndexError` polos saat dipanggil tanpa argumen. Sekarang semua punya usage + kode
  keluar 2.
- `buat_daftar_isi.py` dan `audit_halaman.py` — bila `soffice`/`poppler` tidak ada,
  dulu gagal dengan traceback `FileNotFoundError`. Sekarang pesan jelas + cara pasang.

## [2.0.0] — 2026-10-28

### Ditambahkan
- **Skill `topik_skripsi`** — menutup tahap paling awal yang sebelumnya tidak ada di
  bundel: dari fenomena mentah sampai judul yang layak. Enam fase (inventaris aset →
  panen fenomena → tangga masalah → problematisasi & gap → skor FINER → rumus judul →
  kontrak topik) dengan keluaran `kontrak_topik.json` yang mengisi STEP 0
  `proposal_skripsi`.
- Empat referensi baru: `sumber-fenomena.md` (8 sumber fenomena Indonesia + cara ambil
  bukti), `fenomena-ke-masalah.md` (tangga 5 tingkat dengan contoh lulus/gagal),
  `problemisasi-dan-gap.md` (5 domain asumsi Alvesson–Sandberg, 4 tipe gap, TAS),
  `finer-dan-kelayakan.md` (rubrik 0–5 berbobot + jalur perbaikan),
  `rumus-judul.md` (pola judul per bidang + 8 kesalahan umum).
- Empat skrip: `peta_fenomena.py` (validasi tangga masalah; menolak klaim "LULUS" saat
  tangga kelayakan kosong), `skor_topik.py` (FINER berbobot F30/I15/N20/E15/R20,
  dimensi 0 = diskualifikasi), `judul_check.py` (panjang, verba ganda, lokus, klaim
  hasil, singkatan, duplikasi Jaccard), `literature_probe.py` (kepadatan literatur via
  OpenAlex + Crossref).
- `tests/` untuk skill baru: contoh naskah bersih dan naskah dengan klaim palsu, contoh
  kandidat JSON (termasuk satu diskualifikasi Feasible=0), contoh judul buruk, dan
  `run_tests.sh` dengan 17 pemeriksaan.

### Diubah
- `SKILL.md` root: ditambah bagian "Langkah Minus Satu" dan baris router untuk
  `topik_skripsi`.
- `proposal_skripsi` STEP 0: bila `kontrak_topik.json` ada, parameter dibaca dari berkas
  itu alih-alih ditanyakan ulang.
- `README.md`: bagian "Mulai dari Mana: Topik Dulu, Baru Format"; jumlah skill 19 → 20.
- `CREDITS.md`: entri `topik_skripsi` sebagai karya asli bundel.

### Catatan teknis
- `literature_probe.py` melaporkan **tiga** hitungan per kueri (longgar / konsep / ketat).
  Parameter `search=` OpenAlex mencocokkan kata mana pun: kueri `"pelaporan gizi
  puskesmas"` memberi 4.465 pada `search=` tetapi **1** pada pencarian frasa. Sinyal
  SEPI/SEDANG/PADAT dihitung dari angka ketat, bukan angka longgar — memakai angka
  longgar membuat medan sepi tampak padat.
- `peta_fenomena.py` keluar kode 1 bila ada fenomena berstatus LULUS padahal tangga 5
  (kelayakan) kosong; itu klaim kelayakan palsu dan penyebab utama ganti judul di
  tengah jalan.

## [1.3.0] — 2026-10-22

### Ditambahkan
- Skill `bahasa_akademik`: pedoman bahasa akademik Indonesia (EYD, ragam orang
  ketiga, kata baku, pleonasme, istilah konsisten) + `cek_bahasa.py`, pemeriksa
  otomatis untuk DOCX/Markdown (URL/DOI disamarkan agar DOI jurnal tidak terbaca
  sebagai kata; temuan dibedakan kesalahan vs peringatan).
- `format_kampus/scripts/audit_rapi.py`: audit kerapian Word — paragraf kosong
  berlebih, judul palsu, loncat tingkat judul, tabel/gambar tanpa caption
  (gambar sampul sebelum Heading 1 pertama dikecualikan), spasi ganda.
- `format_kampus/scripts/buat_daftar_isi.py`: pembangun daftar isi otomatis dari
  judul dokumen + nomor halaman hasil render (field TOC Word, titik pemimpin
  dari tab stop kanan per paragraf, halaman daftar isi dilewati saat pencarian,
  pencocokan tak peka huruf besar/kecil). Terverifikasi terhadap dokumen nyata:
  semua nomor sama dengan daftar isi acuan.
- `format_kampus/references/kerapian-word-dan-daftar-isi.md`: standar kerapian
  Word dan anatomi daftar isi skripsi.

### Diubah
- Generator template: style judul kini anti-yatim (keep with next + widow
  control) dan template memuat style TOC 1/2/3 dengan tab stop kanan berdot
  leader selebar teks.
- Router utama: tahap bahasa akademik masuk peta, dan tiga gerbang mutu naskah
  (bahasa, kerapian, daftar isi) menjadi langkah wajib sebelum dokumen selesai.
- Tes bundel: 15 pemeriksaan (tambah pemeriksa bahasa dua arah, audit kerapian,
  style TOC, dan uji asap pembuat daftar isi).

## [1.2.0] — 2026-10-20

### Ditambahkan
- `audit_halaman.py` pada skill format_kampus: audit nomor halaman otomatis dari
  PDF hasil render terhadap skema tiga bagian profil (terverifikasi dua arah:
  dokumen yang benar lulus 39/39; profil yang salah posisi menggagalkan dokumen).
- Registry preset kampus (`skills/format_kampus/presets/INDEX.md`) beserta aturan
  kontribusi preset kampus nyata.
- Tes regresi bundel (`tests/tes_bundel.py`): kelengkapan berkas inti, frontmatter
  semua SKILL.md, keterbacaan YAML, uji asap generator→auditor, dan penjaga konten
  agar data pribadi/proposal pengguna tidak pernah masuk bundel.
- Berkas `VERSION` dan `CHANGELOG.md` ini.

## [1.1.0] — 2026-10-20

### Ditambahkan
- Skill orisinal `format_kampus`: ekstraksi panduan skripsi kampus mana pun menjadi
  profil format YAML yang mengikat (`profil-kampus.yaml`), checklist ekstraksi
  8 kategori, generator template DOCX dari profil (mengunci semua slot font dan
  membuang atribut font tema selevel paket), dan auditor DOCX terhadap profil
  (15/15 pemeriksaan lulus pada preset contoh fiksi).
- "Langkah Nol: kunci format kampus dulu" pada SKILL.md root.

## [1.0.0] — 2026-10-20

### Ditambahkan
- Bundel awal: 19 skill penulisan akademik dan skripsi (riset mendalam, suite ARS,
  office_skripsi dan sub-skillnya, proposal_skripsi, skripsi_pacil, skripsi_writing,
  jurnal_writing, jurnal_submit_pack, office_word_mcp beserta server-nya,
  research_paper_writing) dengan struktur folder asli masing-masing.
- `SKILL.md` root sebagai router, `README.md`, `INSTALL.md` (Claude Code, Claude.ai,
  ChatGPT/Custom GPT, agent berbasis berkas), dan `CREDITS.md` (sumber + lisensi).
