# Skripsi Agent

**Paket skill AI agent untuk menulis skripsi, proposal, dan artikel ilmiah — dari riset sampai siap submit.**

Skripsi Agent menyatukan 20 skill penulisan akademik (menemukan topik, riset mendalam, penyusunan proposal Bab I–III, penulisan dan penyuntingan dokumen Word, peer review, sampai paket submit jurnal) menjadi satu bundel yang bisa dipasang di platform AI agent mana pun: Claude, ChatGPT, dan agent berbasis berkas lainnya. Setiap skill adalah folder mandiri berisi `SKILL.md` beserta referensi dan skrip pendukungnya.

> Bundel ini hanya berisi skill dan dokumentasinya. Tidak ada proposal, data penelitian, atau dokumen kampus milik siapa pun di dalam repo ini.

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
bahasa_akademik    pemeriksa EYD/PUEBI
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
| Format | `buat_template_docx.py` `audit_docx.py` `audit_rapi.py` `buat_daftar_isi.py` `audit_halaman.py` |
| Proposal | `proposal_doctor.py` `verify_doi.py` `stats_tests.py` |
| BAB IV/V | `peta_bab45.py` |
| Revisi | `parse_revisi.py` |
| Sidang | `audit_sidang.py` |
| Bahasa | `cek_bahasa.py` |

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
4. Dokumen jadi **diaudit terhadap profil** sebelum dinyatakan selesai — termasuk
   pemeriksaan atribut font tema pada XML, penyebab klasik dokumen tampil dengan
   font yang salah di Microsoft Word.

## Mutu Naskah: Bahasa Akademik, Kerapian Word, Daftar Isi

Tiga gerbang mutu menjaga hasil akhir seperti skripsi pada umumnya:

- **Bahasa akademik** (`skills/bahasa_akademik/`): pedoman ragam baku EYD plus
  pemeriksa otomatis yang menandai kata ganti orang pertama, kata tidak baku,
  ragam lisan, dan pleonasme sebelum dokumen dinyatakan selesai.
- **Kerapian Word** (`format_kampus`): template kini membawa judul anti-yatim
  (*keep with next*) dan style daftar isi berdot leader; auditor kerapian
  menangkap judul palsu, paragraf kosong berlebih, dan tabel/gambar tanpa caption.
- **Daftar isi otomatis** (`format_kampus`): daftar isi dibangun dari judul
  dokumen dan nomor halaman hasil render — field TOC Word, titik pemimpin rapi,
  nomor halaman sesuai skema bagian (Romawi/Arab). Bukan ketikan manual.

Preset contoh fiksi tersedia di `skills/format_kampus/presets/`; profil kampus
nyata dibuat dari panduan masing-masing pengguna dan tersimpan di proyeknya.

## Isi Paket

### Format kampus

| Skill | Fungsi |
|---|---|
| `format_kampus` | Mengubah panduan skripsi kampus mana pun menjadi profil format YAML yang mengikat, menghasilkan template DOCX darinya, dan mengaudit dokumen jadi terhadap profil (termasuk deteksi atribut font tema), kerapian Word, dan daftar isi |
| `bahasa_akademik` | Pedoman bahasa akademik Indonesia (EYD) + pemeriksa otomatis ragam baku untuk naskah skripsi |

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
| `proposal_skripsi` | Menyusun proposal skripsi/tesis/disertasi Bab I–III dari folder sumber lokal: profil dataset dan uji statistik nyata, coding wawancara kualitatif, 28 preset format kampus, cek EYD dan plagiarisme, ekspor Markdown + DOCX + BibTeX/RIS/EndNote |
| `skripsi_pacil` | Alur penulisan skripsi Sistem Informasi gaya Pacil/Fasilkom: riset → tulis → revisi, sitasi IEEE, audit konsistensi, persiapan seminar dan sidang |
| `skripsi_writing` | Alur menulis skripsi langsung sebagai DOCX dengan pengerasan format memakai skrip office_skripsi |
| `office_skripsi` | Mengedit DOCX skripsi: perbaiki isi, format, heading, caption, daftar isi, cek silang sitasi–daftar pustaka, audit konsistensi antar bab, parafrase menuju target similaritas di bawah 20% |
| `office_skripsi_docx` / `_pdf` / `_pptx` / `_spreadsheet` | Sub-skill office_skripsi untuk operasi dokumen per format |

### Jurnal dan perkantoran

| Skill | Fungsi |
|---|---|
| `jurnal_writing` | Menulis artikel jurnal struktur IMRAD |
| `jurnal_submit_pack` | Menyiapkan paket submit jurnal OJS double-blind |
| `office_word_mcp` | Membaca/menulis Word manual dan live melalui MCP server Office-Word |
| `office_word_files` | Kode sumber MCP server Word beserta helper dan test bawaannya |

Folder pendukung: `ars_shared_files/` dan `shared/` (isi sama — sumber daya bersama suite ARS; dua nama dipertahankan agar semua rujukan path di dalam skill tetap terselesaikan), serta `SKILL.md` di root repo ini sebagai pintu masuk utama agent.

## Cara Install

Ringkasnya: **clone repo ini, lalu salin folder skill yang dibutuhkan ke direktori skill platform Anda.** Petunjuk lengkap per platform (Claude Code, Claude.ai, ChatGPT/Custom GPT, Cursor, Muse, dan agent generik) ada di [INSTALL.md](INSTALL.md).

```bash
git clone https://github.com/xrniqbl/skripsi-agent.git
```

Untuk Claude Code, contohnya:

```bash
cp -r skripsi-agent/skills/* ~/.claude/skills/
```

## Cara Pakai

1. Buka `SKILL.md` di root — file itu mengarahkan agent memilih skill yang tepat untuk setiap tahap: riset, proposal, penulisan, penyuntingan Word, review, dan submit jurnal.
2. Sebutkan tugas Anda secara wajar, misalnya "susun proposal Bab I–III dari folder sumber ini" atau "audit konsistensi sitasi skripsi saya". Agent yang membaca bundel ini akan memuat skill terkait dan mengikuti alurnya.
3. Beberapa skill membawa skrip Python (office_skripsi, proposal_skripsi). Jalankan test bawaannya sekali setelah install untuk memastikan dependensi lengkap — lihat INSTALL.md.

## Pengembangan dan Tes

Versi bundel tercatat di `VERSION` dan riwayat perubahannya di `CHANGELOG.md`.
Sebelum merilis perubahan, jalankan tes regresi bundel:

```bash
python3 tests/tes_bundel.py
```

Tes memeriksa kelengkapan berkas inti, metadata semua skill, keterbacaan skema
profil, uji asap generator→auditor format kampus, dan penjaga konten (bundel tidak
boleh memuat data pribadi atau proposal pengguna mana pun). Preset kampus nyata
dapat disumbangkan ke registry di `skills/format_kampus/presets/` mengikuti aturan
di `INDEX.md` folder tersebut.

## Prinsip Kerja

- **Sitasi selalu diverifikasi** ke sumber primer (DOI, halaman jurnal, PDF resmi) — jangan pernah mengarang referensi.
- **Ikuti pedoman kampus pengguna** di atas template generik bila keduanya berbeda.
- **Jangan mengarang data identitas** (nama, NIM, pembimbing, jadwal) — pakai penanda sampai pengguna mengisinya.
- **Audit sebelum menyatakan selesai**: cek format, sitasi, dan kesalahan teknis pada hasil akhir.

## Kredit dan Lisensi

Seluruh skill dalam bundel ini berasal dari repo open-source para pembuatnya dan disatukan di sini dengan atribusi. Rincian sumber dan lisensi per skill ada di [CREDITS.md](CREDITS.md); berkas lisensi asli di dalam tiap folder skill tetap berlaku. Perhatikan khususnya suite ARS yang berlisensi CC BY-NC 4.0 (non-komersial).
