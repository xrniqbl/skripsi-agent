# Skripsi Agent

**Paket skill AI agent untuk menulis skripsi, proposal, dan artikel ilmiah — dari riset sampai siap sidang.**

Skripsi Agent menyatukan 24 skill penulisan akademik (menemukan topik, riset mendalam, penyusunan proposal Bab I–III, penulisan Bab IV–V, penyuntingan dokumen Word, persiapan sidang, sampai paket submit jurnal) menjadi satu bundel yang bisa dipasang di platform AI agent mana pun: Claude, ChatGPT, dan agent berbasis berkas lainnya. Setiap skill adalah folder mandiri berisi `SKILL.md` beserta referensi dan skrip pendukungnya.

> Bundel ini hanya berisi skill dan dokumentasinya. Tidak ada proposal, data penelitian, atau dokumen pribadi milik siapa pun di dalam repo ini.

**Versi terkini: 2.2.0** — riwayat perubahan di [CHANGELOG.md](CHANGELOG.md).

## Mulai dari Mana: Topik Dulu, Baru Format

Banyak mahasiswa datang dengan "bingung mau skripsi apa". Untuk kondisi itu, jangan mulai
dari format kampus — mulai dari `skills/topik_skripsi/`:

```text
FASE 0  inventaris minat & aset (lokasi, data, waktu, kemampuan)
FASE 1  panen fenomena (8 sumber → minimal 8 kandidat)
FASE 2  tangga masalah 5 tingkat (fakta → kesenjangan → dampak → urgensi → kelayakan)
FASE 3  problematisasi + tipe gap (bukan "belum ada yang meneliti di kota X")
FASE 4  skor FINER berbobot (Feasible 30, Novel 20, Relevant 20, Interesting 15, Ethical 15)
FASE 5  rumus judul + judul_check.py
FASE 6  kontrak_topik.json → serahkan ke proposal_skripsi sebagai STEP 0
```

Keluarannya `kontrak_topik.json` yang mengisi seluruh parameter Step 0 di
`proposal_skripsi`, jadi tidak ada klarifikasi ulang dari nol. Empat skripnya bisa dijalankan
sendiri: `peta_fenomena.py`, `skor_topik.py`, `judul_check.py`, `literature_probe.py`.

Bila pengguna **sudah** punya topik yang disetujui pembimbing, lewati `topik_skripsi` dan
langsung ke Langkah Nol di bawah.

## Peta Alur Lengkap: Nol Sampai Sidang

```text
topik_skripsi      fenomena → masalah → gap → FINER → judul → kontrak_topik.json
      ↓
format_kampus      panduan kampus → profil format YAML + template DOCX
      ↓
proposal_skripsi   BAB I–III, sitasi, uji statistik, audit  (+ verify_doi.py)
      ↓
deep_research      tinjauan literatur bersitasi
      ↓
bab_iv_v           BAB IV hasil & pembahasan, BAB V simpulan & saran
      ↓
bahasa_akademik    pemeriksa EYD/PUEBI + aturan bahasa panduan kampus
      ↓
revisi_pembimbing  catatan pembimbing → daftar kerja terlacak + verifikasi bukti
      ↓
sidang             slide, daftar pertanyaan penguji, kartu angka, latihan
```

Tiap tahap punya skrip pemeriksa sendiri, dan semuanya keluar dengan kode bukan-nol bila
ada yang gagal — jadi bisa dipakai di alur otomatis, bukan hanya dibaca manusia.

| Tahap | Pemeriksa |
|---|---|
| Topik | `peta_fenomena.py` `skor_topik.py` `judul_check.py` `literature_probe.py` |
| Format — rupa | `buat_template_lengkap.py` `buat_template_docx.py` `audit_docx.py` `audit_rapi.py` `buat_daftar_isi.py` `audit_halaman.py` |
| Format — isi | `periksa_sistematika.py` `periksa_pustaka.py` `periksa_ringkasan.py` `periksa_tabel_gambar.py` `periksa_penomoran.py` |
| Proposal | `proposal_doctor.py` `verify_doi.py` `stats_tests.py` |
| BAB IV/V | `peta_bab45.py` |
| Revisi | `parse_revisi.py` |
| Sidang | `audit_sidang.py` |
| Bahasa | `cek_bahasa.py` |
| Semua gerbang isi | `gate_naskah.sh` — satu perintah, lima pemeriksa |

## Fitur Utama: Adaptasi Format Kampus Otomatis

Setiap kampus punya panduan skripsinya sendiri — dan bundel ini menyesuaikan diri
ke panduan itu, bukan sebaliknya:

1. **Panggil skill, kirim panduan kampus Anda** (PDF/DOCX/teks) di awal proyek.
2. Skill `format_kampus` mengekstrak panduan menjadi **profil format terstruktur**
   (`profil-kampus.yaml`): margin, font per elemen, spasi, sistematika bab,
   penomoran halaman tiga bagian, format caption, gaya sitasi, sampai aturan
   khusus seperti jumlah minimal jurnal.
3. Profil dikonfirmasi ke Anda, lalu **dikunci**: seluruh skill lain menulis dan
   memformat mengikutinya, dan template DOCX dihasilkan langsung dari profil.
4. Dokumen jadi **diaudit terhadap profil** sebelum dinyatakan selesai.

### Dua lapis pemeriksaan

**Lapis rupa** (DOCX/PDF): margin, font per elemen, spasi, atribut font tema pada XML —
penyebab klasik dokumen tampil dengan font yang salah di Microsoft Word — judul anti-yatim,
tabel/gambar tanpa caption, dan nomor halaman hasil render.

**Lapis isi**: apakah naskah benar-benar mematuhi panduan, bukan hanya terlihat rapi.

- `periksa_sistematika.py` — kelengkapan **dan urutan** bagian awal/akhir, keberadaan
  setiap bab dan subbab, format penomoran subbab (`2.1.` vs `2.1`), penomoran caption
  (`Tabel IV.1` vs `Tabel 4.1`). Bagian yang di panduan ditandai "*jika ada"
  dilaporkan sebagai peringatan bila dijalankan dengan `--abaikan-opsional`.
- `periksa_pustaka.py` — Daftar Pustaka terhadap ketentuan panduan: urutan abjad,
  larangan `et al.`/`dkk`, gelar akademik, usia terbitan, jumlah minimal jurnal,
  larangan Blogspot/Wordpress/Wikipedia, tanggal unduh sumber web, dan sitasi dalam
  teks yang tidak punya entri (atau sebaliknya).
- `periksa_ringkasan.py` — Ringkasan dan Abstract terhadap ketentuan panduan:
  panjang kata, empat unsur wajib (masalah, metode, hasil, manfaat), jumlah kata
  kunci, dan kesejajaran panjang Abstract dengan Ringkasan.
- `periksa_tabel_gambar.py` — caption tabel/gambar: keberadaan, posisi, format
  nomor, urutan per bab, kesesuaian nomor bab, **rujukan di teks**, dan sumber
  kutipan pada caption.
- `periksa_penomoran.py` — khusus `.docx`: membaca `numbering.xml` dan menghitung
  nomor subbab yang AKAN tampil. Menangkap subbab tanpa `numPr`, `lvlText` salah,
  dan `numId` dipakai ulang lintas bab (semua bab jadi "2.x").
- `cek_bahasa.py` — ragam baku, kata tidak baku, singkatan tidak resmi
  (`dll`/`dst`/`dsb`/`ybs`), kata ulang berangka (`kata2`), garis miring sebagai
  "atau", dan "daripada" sebagai "dari".

Keenamnya **pemeriksa pola, bukan vonis** — setiap temuan wajib dinilai konteksnya.

### Preset kampus yang sudah tersedia

| Preset | Cakupan | Sumber |
|---|---|---|
| `format_kampus/presets/ars-fti.yaml` | FTI Universitas Adhirajasa Reswara Sanjaya — S1 Sistem Informasi & Teknik Informatika | Panduan Penyusunan Laporan Skripsi FTI, Revisi 2025 (resmi, 42 halaman) |
| `format_kampus/presets/universitas-contoh.yaml` | fiktif — hanya contoh bentuk isian | — |
| `proposal_skripsi/campus_templates/*.json` | 29 preset kampus Indonesia (UGM, UI, ITB, IPB, ITS, BINUS, Telkom, dan lainnya) termasuk `ars_fti.json` | panduan resmi masing-masing kampus |

Ketentuan yang **berbeda** antar kampus dan sering menjebak:
spasi isi 2 vs 1,5 · caption `Tabel IV.1` vs `Tabel 4.1` · subbab
"Identifikasi Masalah" vs "Rumusan Masalah" · nama bab II "Landasan Pemikiran" vs
"Tinjauan Pustaka". Preset `ars-fti` mengikat semuanya sekaligus.

## Mutu Naskah: Bahasa Akademik, Kerapian Word, Daftar Isi

- **Bahasa akademik** (`skills/bahasa_akademik/`): pedoman ragam baku EYD plus
  pemeriksa otomatis, termasuk aturan teknis yang sering luput dari pemeriksa
  umum (singkatan tidak resmi, kata ulang berangka, garis miring sebagai "atau").
- **Kerapian Word** (`format_kampus`): template membawa judul anti-yatim
  (*keep with next*) dan style daftar isi berdot leader; auditor kerapian
  menangkap judul palsu, paragraf kosong berlebih, dan tabel/gambar tanpa caption.
- **Daftar isi otomatis** (`format_kampus`): dibangun dari judul dokumen dan nomor
  halaman hasil render — field TOC Word, titik pemimpin rapi, nomor halaman sesuai
  skema bagian (Romawi/Arab). Bukan ketikan manual.

## Isi Paket

### Format, bahasa, dan tahap akhir

| Skill | Fungsi |
|---|---|
| `format_kampus` | Panduan skripsi kampus mana pun → profil format YAML yang mengikat → template DOCX → audit dokumen terhadap profil (rupa + isi) |
| `bahasa_akademik` | Pedoman bahasa akademik Indonesia (EYD/PUEBI) + pemeriksa otomatis ragam baku |
| `bab_iv_v` | Menyusun BAB IV (hasil & pembahasan) dan BAB V (simpulan & saran) yang terpetakan 1:1 ke rumusan/identifikasi masalah; `peta_bab45.py` memeriksa pemetaan, kehadiran angka statistik, dan kelengkapan saran |
| `revisi_pembimbing` | Catatan pembimbing (foto/PDF/DOCX/teks) → daftar kerja terlacak per butir, dengan verifikasi bukti sebelum ditandai selesai |
| `sidang` | Slide presentasi, daftar pertanyaan penguji yang diturunkan dari naskah sendiri, kartu angka, dan latihan tanya-jawab |

### Riset dan penulisan paper

| Skill | Fungsi |
|---|---|
| `deep_research` | Riset mendalam dua fase: susun outline dan kerangka bidang, teliti tiap item dengan pencarian web paralel, validasi cakupan, susun laporan Markdown bersitasi |
| `ars_deep_research` | Tim riset akademik 13 agen: perumusan pertanyaan, pencarian literatur sistematis (dukungan PRISMA), verifikasi sumber, sintesis, penilaian risiko bias, meta-analisis |
| `research_paper_writing` | Meningkatkan kualitas penulisan paper gaya ML/CV/NLP per seksi (Abstract sampai Conclusion), cek alur paragraf, keselarasan klaim–bukti, self-review adversarial |
| `ars_academic_paper` | Menulis paper akademik dengan pipeline 12 agen: draf penuh, outline, revisi, abstrak, tinjauan pustaka, cek sitasi, konversi format, rebuttal audit (APA 7 dan format lain) |
| `ars_academic_paper_reviewer` | Simulasi peer review dua tahap untuk paper akademik |
| `ars_academic_pipeline` | Orkestrasi pipeline lengkap: riset → penulisan → cek integritas → peer review → revisi → finalisasi |
| `ars_sr_screener` | Penyaringan literatur untuk systematic review |

### Skripsi dan proposal (Bahasa Indonesia)

| Skill | Fungsi |
|---|---|
| `topik_skripsi` | Menemukan topik yang layak: panen fenomena, tangga masalah, tipe gap, skor FINER berbobot, rumus judul, keluaran `kontrak_topik.json` |
| `proposal_skripsi` | Menyusun proposal skripsi/tesis/disertasi Bab I–III dari folder sumber lokal: profil dataset dan uji statistik nyata, coding wawancara kualitatif, 29 preset format kampus, cek EYD dan plagiarisme, ekspor Markdown + DOCX + BibTeX/RIS/EndNote |
| `skripsi_pacil` | Alur penulisan skripsi Sistem Informasi gaya Pacil/Fasilkom: riset → tulis → revisi, sitasi IEEE, audit konsistensi, persiapan seminar dan sidang |
| `skripsi_writing` | Alur menulis skripsi langsung sebagai DOCX dengan pengerasan format memakai skrip office_skripsi |
| `office_skripsi` | Mengedit DOCX skripsi: perbaiki isi, format, heading, caption, daftar isi, cek silang sitasi–daftar pustaka, audit konsistensi antar bab, parafrase menuju target similaritas di bawah 20% |
| `office_skripsi_docx` · `office_skripsi_pdf` · `office_skripsi_pptx` · `office_skripsi_spreadsheet` | Sub-skill office_skripsi untuk operasi dokumen per format |

### Jurnal dan perkantoran

| Skill | Fungsi |
|---|---|
| `jurnal_writing` | Menulis artikel jurnal struktur IMRAD |
| `jurnal_submit_pack` | Menyiapkan paket submit jurnal OJS double-blind |
| `office_word_mcp` | Membaca/menulis Word manual dan live melalui MCP server Office-Word |
| `office_word_files` | Kode sumber MCP server Word beserta helper dan test bawaannya |

Folder pendukung: `skills/shared/` — sumber daya bersama suite ARS yang dirujuk lintas
skill — serta `SKILL.md` di root repo sebagai pintu masuk utama agent.

## Cara Install

Ringkasnya: **clone repo ini, lalu salin folder skill yang dibutuhkan ke direktori skill platform Anda.** Petunjuk lengkap per platform (Claude Code, Claude.ai, ChatGPT/Custom GPT, Cursor, Muse, dan agent generik) ada di [INSTALL.md](INSTALL.md).

```bash
git clone https://github.com/xrniqbl/skripsi-agent.git
```

Untuk Claude Code, contohnya:

```bash
cp -r skripsi-agent/skills/* ~/.claude/skills/
```

Dependensi Python:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/cek_dependensi.py   # pastikan tidak ada impor yang gagal
```

## Cara Pakai

1. Buka `SKILL.md` di root — file itu mengarahkan agent memilih skill yang tepat untuk
   setiap tahap: riset, proposal, penulisan, penyuntingan Word, review, dan submit jurnal.
2. Sebutkan tugas Anda secara wajar, misalnya "susun proposal Bab I–III dari folder
   sumber ini" atau "audit konsistensi sitasi skripsi saya".
3. Kalau punya panduan kampus, kirim berkasnya di awal — semua skill lain akan
   mengikuti profil yang dihasilkan, bukan default umum.
4. Beberapa skill membawa skrip Python. Jalankan test bawaannya sekali setelah install
   untuk memastikan dependensi lengkap — lihat [INSTALL.md](INSTALL.md).

Contoh memeriksa naskah di akhir:

```bash
# rupa
.venv/bin/python skills/format_kampus/scripts/audit_docx.py skripsi.docx profil-kampus.yaml
# isi
.venv/bin/python skills/format_kampus/scripts/periksa_sistematika.py skripsi.md profil-kampus.yaml
.venv/bin/python skills/format_kampus/scripts/periksa_pustaka.py skripsi.md --tahun-acuan 2026
.venv/bin/python skills/bahasa_akademik/scripts/cek_bahasa.py skripsi.md
# pemetaan rumusan → hasil → simpulan
.venv/bin/python skills/bab_iv_v/scripts/peta_bab45.py skripsi.md --periksa
```

Atau semuanya sekaligus:

```bash
bash skills/format_kampus/scripts/gate_naskah.sh skripsi.md profil-kampus.yaml
# untuk DOCX, gerbang yang sama sekalian memeriksa penomoran subbab
bash skills/format_kampus/scripts/gate_naskah.sh skripsi.docx profil-kampus.yaml
```
```

## Pengembangan dan Tes

Versi bundel tercatat di `VERSION` dan riwayat perubahannya di `CHANGELOG.md`.
Sebelum merilis perubahan, jalankan tes regresi:

```bash
.venv/bin/python tests/tes_bundel.py
```

Tes memeriksa kelengkapan berkas inti, metadata semua skill, keterbacaan skema profil,
uji asap generator→auditor format kampus, uji asap pemeriksa sistematika dan daftar
pustaka, serta **penjaga konten**: bundel tidak boleh memuat identitas pribadi
(nama orang, alamat, nomor telepon) atau proposal pengguna mana pun.

Tes per skill juga bisa dijalankan sendiri:

```bash
cd skills/format_kampus   && PYTHON=../../.venv/bin/python bash tests/run_tests.sh
cd skills/bab_iv_v        && PYTHON=../../.venv/bin/python bash tests/run_tests.sh
cd skills/bahasa_akademik && PYTHON=../../.venv/bin/python bash tests/run_tests.sh
```

Status tes saat ini: `tes_bundel` 36 pemeriksaan, `format_kampus` 99,
`bahasa_akademik` 12, `proposal_skripsi` 64, `bab_iv_v` 15, `sidang` 17,
`revisi_pembimbing` 21, `topik_skripsi` 17 — semuanya lulus.

Preset kampus nyata dapat disumbangkan ke `skills/format_kampus/presets/` mengikuti
aturan di `INDEX.md` folder tersebut, atau ke `skills/proposal_skripsi/campus_templates/`
dalam format JSON.

## Prinsip Kerja

- **Sitasi selalu diverifikasi** ke sumber primer (DOI, halaman jurnal, PDF resmi) — jangan
  pernah mengarang referensi. `verify_doi.py` memberi verdict VALID / TIDAK ADA / MENDUGA / GAGAL.
- **Ikuti pedoman kampus pengguna** di atas template generik bila keduanya berbeda.
  Bila panduan bertentangan dengan dirinya sendiri, **catat konfliknya dan tanyakan** —
  jangan menebak. Contoh nyata: panduan menyebut APA tetapi seluruh contohnya memakai
  `(Nama, Tahun:Halaman)`.
- **Jangan mengarang data identitas** (nama, NIM, pembimbing, jadwal, nomor dokumen) —
  pakai penanda sampai pengguna mengisinya.
- **Jangan membuat dokumen yang mengaku diterbitkan instansi lain.** Alat boleh
  menghasilkan pratinjau tata letak; dokumen sah tetap diterbitkan pihak berwenang.
- **Audit sebelum menyatakan selesai**: rupa, isi, sitasi, dan konsistensi antar bab.

## Kredit dan Lisensi

Seluruh skill dalam bundel ini berasal dari repo open-source para pembuatnya dan disatukan
di sini dengan atribusi. Rincian sumber dan lisensi per skill ada di [CREDITS.md](CREDITS.md);
berkas lisensi asli di dalam tiap folder skill tetap berlaku. Perhatikan khususnya suite ARS
yang berlisensi CC BY-NC 4.0 (non-komersial).
