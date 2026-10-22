# Changelog

Semua perubahan berarti pada bundel Skripsi Agent dicatat di sini.
Format mengikuti Keep a Changelog; versi mengikuti Semantic Versioning.

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
