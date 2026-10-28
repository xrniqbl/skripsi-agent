> Muse adaptation of https://github.com/bimajanuri/proposal-skripsi-skill (MIT, LICENSE beside this file, copyright Bima Januri). Upstream skill name is `proposal-skripsi`; upstream frontmatter moved to skill.yaml. All companion files live in this folder exactly as upstream: `references/`, `templates/`, `checklists/`, `campus_templates/` (28 Indonesian campus presets), `scripts/`, and `tests/`. Run every script from this skill folder so relative paths resolve, for example `python3 scripts/stats_tests.py ...`. Upstream companion skills map to Muse skills as follows: `paper-review` maps to ars_academic_paper_reviewer and the literature matrix in ars_deep_research, and `academic-writing` maps to research_paper_writing and ars_academic_paper. Where upstream says to ask via a question tool, ask in chat and use muse.create_options for bounded choices such as jenjang (skripsi, thesis, disertasi), research type, campus preset, and export format. DOCX export in scripts/build_docx.sh needs pandoc; check `which pandoc` before promising a DOCX and offer Markdown output when pandoc is absent.

# Proposal Skripsi — Penyusun Proposal Penelitian (Bahasa Indonesia)

Skill ini menyusun **proposal penelitian berbahasa Indonesia** untuk tiga jenjang —
**skripsi (S1)**, **thesis (S2)**, dan **disertasi (S3)** — sesuai pilihan pengguna. Seluruh
bukti (literatur, data, statistik) disumberkan dari **kumpulan file lokal** yang ditunjuk user
(PDF/DOCX/MD/TXT/CSV/XLSX/JSON), dengan **pencarian online sebagai pelengkap** bila folder
minim literatur.

Mandat utama skill ini: **menghasilkan proposal yang siap dibawa ke pembimbing** — bukan
ringkasan, bukan kerangka kosong. Setiap klaim empiris memiliki sumber file, dan setiap
unsur proposal punya justifikasi, dan jenjang menentukan tingkat kedalaman.

> Skill ini **berkumpulan dengan** dua skill lain (bukan duplikat):
> - **`paper-review`** → tabel review literatur (synthesis matrix) bila user butuh matriks
>   evidence lengkap per paper. Skill ini menyediakan **ringkasan** matriks saja.
> - **`academic-writing`** → protocol penulisan paper (English). Output skill ini wajib
>   **Bahasa Indonesia**, bukan adaptasi langsung. Hanya *pola* Layered QC-nya yang
>   diadaptasi ke konteks proposal: Humanizer, plagiarism check, dan gate semantik.

---

## Jenjang (Wajib Dipilih User — GATE 0)

| Aspek | **Skripsi (S1)** | **Thesis (S2)** | **Disertasi (S3)** |
|-------|------------------|-----------------|---------------------|
| Panjang proposal | 20–30 halaman (±3.500–5.000 kata) | 40–60 halaman (±8.000–12.000 kata) | 70–120 halaman (±15.000–25.000 kata) |
| Kontribusi utama | **Penerapan/pengujian** teori pada konteks lokal | **Pengembangan/ekspansi** kerangka konseptual | **Kontribusi teoretis orisinal** (model/kerangka baru) |
| Desain dominan | Kuantitatif eksplanatif atau deskriptif, penelitian lapangan, eksploratif kualitatif | Kualitatif (studi kasus, grounded theory) / mixed-methods | Mixed-methods, multi-situs, validasi model, replikasi |
| Landasan teori | 1-2 teori utama + teori pendukung | 2-4 teori, elaborasi hubungan antarteori | 3-5 teori + posisi teoretis (positioning) eksplisit |
| Pengujian | Uji statistik baku (regresi, t-test, ANOVA, SEM) | Uji kualitatif (coding, validitas, reliabilitas) + uji statistik bila kuantitatif | Uji empiris berlapis + **threat to validity** eksplisit |
| Wajib tambahan | Persetujuan etik, rencana kuota dan waktu | Kerangka konseptual, strategi generalisasi | Statement of contribution, gagasan orisinal, rencana publikasi (3-4 artikel) |
| Luas sub-bab BAB II | 5–7 sub-bab | 6–9 sub-bab | 7–10 sub-bab |

**Jika jenjang tidak disebut user → TANYAKAN (via `question` tool). Jangan menebak.**

---

## Pipeline

```text
STEP 0: KLARIFIKASI  → jenjang, bidang, topik, jenis penelitian, folder sumber, mode, preset kampus, format ekspor
STEP 1: INVENTARIS   → scan folder → klasifikasi (literatur/data/pedoman/transkrip/format) → inventaris.json
STEP 2: EVIDENSI     → matriks ringkas + gap (TAS) + online search pelengkap bila perlu
STEP 3: FORMULASI    → latar belakang → rumusan masalah → tujuan → manfaat → pertanyaan → hipotesis → variabel → batasan
STEP 4: RANCANGAN    → desain metode + instrumen + sampling + teknik analisis + analisis dataset/koding nyata
STEP 5: DRAFT        → halaman judul + daftar isi + BAB I–III (Markdown)
STEP 6: GATE+EXPORT  → id_language_check + proposal_doctor + campus check → referensi → MD + DOCX (pandoc)
```

Setiap tahap punya **quality gate**; konfirmasi user hanya diminta **satu kali di awal** (Step 0)
dan **satu kali sebelum export** (Step 6). Jangan konfirmasi per-bagian.

### Rute berdasarkan jenis penelitian

| Jenis penelitian | Rute pipeline | Tambahan wajib |
|------------------|---------------|----------------|
| **Kuantitatif** | STEP 1–6 utuh | `profile_dataset.py` → `stats_tests.py` → tabel uji statistik |
| **Kualitatif** | STEP 1–6 utuh, Step 4 memakai **§4.4** | pedoman wawancara + informed consent + `code_interview.py` + Gate 4-Kualitatif |
| **Mixed-methods** | kedua jalur di atas | tabel integrasi data + alasan prioritas (EXPLOR/EXPLAN) |
| **Dokumen/arsip** | STEP 1–6, sumber = dokumen | tabel inventaris dokumen + kritik sumber ( bukan survei, bukan wawancara ) |

> Kualitatif **bukan** versi kuantitatif tanpa angka: jangan menulis rumus Cochran,
> Cronbach's alpha, atau tabel hipotesis → uji pada desain kualitatif.

---

## STEP 0 — Klarifikasi

> **Bila `kontrak_topik.json` sudah ada** (dari skill `topik_skripsi`), muat berkas itu
> lebih dulu dan isi tabel di bawah dari isinya. Jangan menanyakan ulang parameter yang
> sudah tercatat — cukup konfirmasi satu kali: "topik ini masih yang dipakai?".
> Hanya parameter yang tidak ada di kontrak (mis. gaya sitasi, preset kampus, format
> ekspor) yang perlu ditanyakan.

Kumpulkan parameter berikut (cukup seperlunya bila konteks sudah jelas dari brief user):

| Parameter | Opsi | Default |
|-----------|------|---------|
| **Jenjang** | Skripsi / Thesis / Disertasi | **wajib ditanya** |
| Bidang ilmu / program studi | teks bebas | — |
| Topik penelitian | teks bebas | dari brief user |
| Jenis penelitian | Kuantitatif / Kualitatif / Mixed-methods / R&D / Studi Kasus / Penelitian Tindakan | dataset ada → cenderung kuantitatif; tidak ada → kualitatif |
| **Folder sumber** | path | **wajib ditanya bila tidak disebut** |
| Mode input | Folder / Folder + Online | Folder (+Online bila literatur lokal < 10) |
| Luas proposal | Pendahuluan saja / BAB I–II / **BAB I–III lengkap** | BAB I–III |
| **Preset kampus** | 28 preset: UGM / UI / Uny / ITB / IPB / UNAIR / UB / ITS / UNDIP / Unpad / Unhas / Telkom / BINUS / UMY / UII / UAD / UMS / Udinus / UMM / UMB / Gunadarma / UPN Veteran Yogya / UPN Veteran Jakarta / UPN Veteran Jatim / Budi Luhur / UMN / generic / custom / pakai file pedoman (path) | generic |
| Gaya sitasi | APA 7 / Chicago / Harvard / Vancouver / IEEE | APA 7, atau gaya dari preset kampus |
| Instrumen kualitatif | pedoman wawancara milik sendiri / adaptasi / FGD / observasi | pedoman wawancara (Lampiran) |
| Ekspor | MD saja / **MD + DOCX (pandoc)** / + LaTeX / + BIB-RIS-ENDNote | MD + DOCX |
| Nama/NIM dan institution | teks | `[isi ...]` bila tidak ada (jangan dikarang) |

> **Jangan pernah mengarang** nama fakultas/jurusan, nama dosen, NIM, atau nama responden.
> Tidak diketahui → tulis `[isi nama fakultas/jurusan]`, `[isi NIM]`, dsb.

Simpan hasil klarifikasi ke `kontrak_proposal.json` (kontrak kerja) sebelum lanjut.

### Preset template kampus

Preset berisi gaya dokumen, gaya sitasi, daftar kelengkapan, dan struktur bab per
kelompok/program studi. Tampilkan pilihan bila user menyebut nama kampus atau
"format kampus":

```bash
python3 scripts/apply_campus_template.py list        # + penanda [resmi] / [konvensi]
python3 scripts/apply_campus_template.py show unpad  # tampilkan sumber angka + URL
python3 scripts/apply_campus_template.py init unpad --out outputs/proposal.md
python3 scripts/apply_campus_template.py check unpad outputs/proposal_skripsi.md --lengkap
python3 scripts/apply_campus_template.py new-custom --out-dir outputs/institusi_saya.json
```

- Preset bawaan (28): `ugm`, `ui`, `uny`, `itb`, `ipb`, `unair`, `ub`, `its`, `undip`,
  `unpad`, `unhas`, `telu`, `binus`, `umy`, `uii`, `uad`, `ums`, `udinus`, `umm`,
  `umb`, `gunadarma`, `upn_veteran`, `upnvj`, `upnv_jatim`, `budi_luhur`, `umn`,
  `generic`, `custom`.
- **Setiap preset wajib dibaca provenance-nya** (`show <preset>` atau field `sumber`):
  - `pedoman-resmi` — angka format diambil dari dokumen resmi (ada `dokumen`, `url`,
    `scope`, `tahun`). Tetap hanya berlaku untuk fakultas/tahun di `scope`.
    Saat ini 5 preset: `its`, `ub`, `umn`, `unair`, `unpad`.
  - `konvensi-umum` — **belum diverifikasi**; angka hanya konvensi umum Indonesia.
    Wajib dicocokkan manual ke pedoman resmi. Saat ini 12 preset.
- Preset `ugm`, `ui`, `uny`, `itb`, `generic`, `custom` belum punya field `sumber`;
  perlakukan sebagai konvensi umum.
- **Jangan mengarang angka preset.** Bila user punya pedoman resmi, **file/petunjuk user
  yang menang**, bukan preset. Bila hanya sebagian angka yang cocok, perbaiki naskah/catatan,
  bukan diam-diam menimpa preset.
- `init` membangun **kerangka** naskah (heading + komentar penanda), bukan narasi —
  narasi tetap ditulis pada STEP 5.
- Aturan yang tidak ada di preset tidak ditebak: script hanya melaporkan, tidak mengubah naskah.
- Menambah/menyesuaikan preset? Edit `scripts/generate_campus_presets.py` (sumber data
  tunggal), lalu `python3 scripts/generate_campus_presets.py`;
  `python3 scripts/generate_campus_presets.py --check` mendeteksi **drift** (bandingkan isi
  disk vs hasil generator, keluar kode 1 bila tidak sinkron).
- Preset lama `ugm`/`ui`/`itb`/`uny` TIDAK ditulis ulang generator — `struktur`-nya hasil
  tulisan tangan. Untuk memperbarui gaya/provenance-nya pakai
  `python3 scripts/generate_campus_presets.py --patch`, yang hanya merge field
  `gaya_dokumen`/`sitasi`/`kelengkapan`/`sumber`/`verifikasi` dan tidak pernah menyentuh
  `struktur` (dijalankan otomatis oleh `tests/run_tests.sh` untuk membuktikan idempotensi).
- **Nilai tak terverifikasi ditulis apa adanya.** Bila dokumen resmi tidak mencantumkan
  angka margin/spasi, tulis `"perlu konfirmasi (bagian X)"` — jangan menebak angka.
- **Bedakan antar fakultas.** Bila satu kampus punya >1 pedoman berbeda (mis. UGM FKH
  spasi 2 vs DTSL Teknik 1,15), pilih satu sebagai nilai dasar, lalu catat selisihnya di
  `sumber.catatan` dan `verifikasi`.

---

## STEP 1 — Inventarisasi Sumber File

> Load `references/data-sources.md` untuk detail klasifikasi & ekstraksi.
> Script: `scripts/ingest_sources.sh <folder> [--out <cache>]`

1. Scan folder **rekursif**. Klasifikasikan tiap file:

| Kategori | Ekstensi | Pemanfaatan |
|----------|----------|--------------|
| **Literatur** | `pdf`, `docx`, `md`, `txt`, `tex`, `epub` (lewati) | BAB II + latar belakang + argumen gap |
| **Data kuantitatif** | `csv`, `tsv`, `xlsx`, `xls`, `json` (array of objects), `sav` | BAB III: rancangan analisis + profil data |
| **Transkrip/kodebook** | `md`, `txt`, `docx`, `csv` (berisi `[P01]`, `Peserta:`, kolom `kode;kategori;tema`) | BAB III §4.4: pengodean, `[K-n]` |
| **Pedoman/format** | `docx`, `pdf` bernama pedoman/skripsi/format/… | struktur bab, gaya dokumen, daftar isi |
| **Aturan/Ethics** | `*.md` | versi bab, pedoman sitasi |
| **Lainnya** | gambar, `pptx`, `zip`, kode | catat di inventaris, jangan dipaksa |

2. Ekstrak teks PDF: `scripts/ingest_sources.sh` memakai `pdftotext -layout` (poppler).
   PDF hasil scan → kosong → tandai `PERLU_OCR`, jangan dippeduli diam-diam.
3. **Batas baca yang wajib dihormati** (hemat konteks):
   - Literatur: **Abstract → Pendahuluan/Intro → Metode → Hasil → Kesimpulan** (cukup).
   - Bab II **tidak** menyalin isi paper; ia **membangun sintesis** (lihat Step 3).
4. Deteksi cepat: file apa pun yang menyebut "data responden", "jawaban", "skor", "Likert",
   "n = " → kemungkinan dataset; masukkan kategori Data.

### Output Step 1
```
kontrak_proposal.json        # hasil klarifikasi Step 0
sumber_inventaris.json       # master inventaris: path, kategori, ukuran, status ekstraksi, ringkasan
sumber_inventaris.md         # tabel inventaris + catatan kelengkapan
.cache_ekstrak/              # teks hasil ekstraksi PDF (file .txt), boleh dihapus setelah draft
```

> Bila folder berisi transkrip wawancara, inventaris juga mencatat **jumlah partisipan**
> per berkas dan apakah `codebook` sudah ada. Jumlah ini tidak boleh dikarang — hitung dari berkas.

### Quality Gate 1
- [ ] Semua file terklasifikasi; tidak ada file "misterius" tanpa penjelasan
- [ ] Setiap literatur punya minimal judul + tahun (dari metadata file atau halaman judul)
- [ ] Setiap dataset punya nama file + jumlah baris/kolom terverifikasi (lihat Step 4)
- [ ] Setiap transkrip punya penanda partisipan yang dapat dihitung (lihat §4.4)
- [ ] File tidak terbaca (scan/gambar) ditandai eksplisit, bukan diabaikan

---

## STEP 2 — Bukti & Research Gap

### 2.1 Matriks bukti (ringkas — versi lengkap: pakai skill `paper-review`)

Untuk setiap literatur lokal, buat **1 baris ringkas** di `matriks_evidence.md` dengan kolom:

| Sumber | Tahun | Populasi/Sampel | Metode | Temuan Utama | Keterbatasan | Gap yang Tersisa |
|--------|-------|------------------|--------|--------------|--------------|------------------|

> Bila user minta tabel review lengkap per-paper (12 kolom, provenance `[M-2]`, ekspor
> CSV/XLSX/BIB/RIS) → **delegasikan ke skill `paper-review`**, jangan diulang di sini.
> Alih input-output dan kolom minimum matriks: `references/paper-review-integration.md`.

### 2.2 Pencarian online pelengkap (opsional)

Aktifkan bila: literatur lokal < 10, atau gap belum tertutup, atau user memintanya.
Load `references/online-search.md`. Ringkas saja: 5-10 paper terkuat dengan skor relevansi minimal 7,
DOI wajib dapat di-resolve. Hasil search **tidak boleh mendominasi** proposal bila data lokal
sudah kaya — literatur lokal lebih relevan (konteks Indonesia/lokal).

### 2.3 Menyusun Gap (metode TAS / Berwald-Daellenbach)

Template ringkas — **3 pertanyaan pemandu**, bukan paragraf panjang:

1. **Theoretical Advance** — apakah temuan mengubah/memperluas teori atau hanya mengkonfirmasi?
2. **Problem/Context** — apakah masalah nyata hanya terkonfirmasi, atau tetap ada karena data kontekstual?
3. **Practical Consequences** — apakah implikasi manajerial/policy baru, atau hanya mengulang praktik lama?

> Format lengkap: `references/problem-formulation.md` §1. Setiap klaim **wajib** diberi penanda
> sumber: `[L-3]` (literatur ke-3 pada matriks), `[D:kolom]`, `[U]` (dari brief user),
> `(inferensi)` untuk penalaran agent sendiri.

### Output Step 2
```
matriks_evidence.md   — matriks ringkas + daftar gap
catatan_gap.md        — argumen gap (TAS) + posisi penelitian ini (positioning)
```

### Quality Gate 2
- [ ] Setiap **paper/sumber** punya DOI **atau** file lokal yang dibaca (anti-hallucination)
- [ ] Setiap referensi tidak dipakai sebagai "bantalan" — minimal 1 sumber jadi argumen gap
- [ ] Tidak ada nama penelitian/penulis yang tidak ada di sumber (JANGAN mengarang)
- [ ] Gap bukan sekadar "belum diteliti di lokasi X" — ada justifikasi mengapa itu penting

---

## STEP 3 — Formulasi Masalah Penelitian

> Load `references/problem-formulation.md` (rumusan masalah, tujuan, manfaat, pertanyaan,
> hipotesis, variabel, definisi istilah, batasan) + `templates/bab1_pendahuluan.md`.

Urutan penulisan **wajib** (menjaga koherensi argumen):

1. **Latar belakang** — fenomena nyata (umumnya dari data lokal) → fakta yang mengganjal →
   perbandingan dengan temuan penelitian terdahulu → celah → posisi penelitian ini.
2. **Rumusan masalah** — 3–6 pertanyaan turunan, hierarkis (umum → khusus). **Rumusan harus
   TURUNAN dari latar belakang**, bukan tempelan.
3. **Tujuan** — cerminan 1:1 dari rumusan masalah (jumlah & urutan selaras).
4. **Manfaat** — teoritis / praktis (kebijakan/manajerial) / bagi peneliti lanjutan.
5. **Pertanyaan penelitian** (opsional, bila metode kualitatif) — terbuka, tidak mengasumsikan jawaban.
6. **Hipotesis** (wajib bila kuantitatif) — H0/H1 per variabel, mengikuti teknik analisis terpilih.
7. **Definisi operasional** — tiap variabel: definisi konseptual (sumber) + indikator + skala.
8. **Ruang lingkup** — lokasi, waktu, populasi dan sampel, variabel, data, teknik analisis; batas yang APAKAN.
9. **Definisi istilah** — hanya istilah kunci yang berpotensi ambigu.

### Aturan Penulisan
- **Jangan** menulis klaim empiris tanpa sumber. Dilarang menulis "berdasarkan penelitian terdahulu menunjukkan
  meningkatkan kinerja" tanpa `[L-n]`.
- Angka dari data lokal → tulis **[D:kolom]** agar jelas berasal dari dataset, bukan literatur.
- Hipotesis harus **menguji arah hubungan**, bukan mengulang tujuan.
- Untuk jenjang S3: tambahkan **statement of contribution** (kontribusi orisinal apa yang diklaim).

### Output Step 3
```
draft_bab1.md   — kerangka BAB I (sub-bab + poin + penanda sumber, belum narasi penuh)
```

---

## STEP 4 — Rancangan Metode Penelitian

> Load `references/methodology.md` (desain, pendekatan, teknik sampling, instrumen, teknik analisis,
  ethics, uji asumsi) + `references/dataset-analysis.md` (profil dataset & pemilihan uji).

### 4.1 Desain penelitian

Isi **field wajib** untuk setiap desain yang dipilih (lihat `references/methodology.md` §1):

| Elemen | Isi minimal |
|--------|-------------|
| Pendekatan & desain | Kuantitatif eksplanatif / deskriptif / kualitatif / mixed / R&D / studi kasus / action research — + **alasan pemilihan** + `[L-n]` bila berbasis teori |
| Lokasi & waktu | Tempat + alasan pemilihan lokasi; rentang waktu mulai–selesai |
| Populasi & sampel | Populasi, teknik sampling (acak, proporsional, purposive, snowball), **n dan rumus**, kriteria inklusi/eksklusi |
| Instrumen | Kuesioner, pedoman observasi, atau pedoman wawancara; asal butir; skala (Likert 1–5 atau 1–7); **uji validitas dan reliabilitas** (Cronbach's alpha, CFI) |
| Teknik analisis | Uji yang dipilih per hipotesis beserta **alasan**, uji asumsi, software (SPSS 26, R 4.x, Python, SmartPLS, atau AMOS) |
| Etika & izin | Persetujuan etik, informed consent, anonimitas, izin penelitian |
| Batasan rancangan | Keterbatasan rancangan dan mitigasinya (wajib untuk S2/S3) |

### 4.2 Analisis dataset nyata (WAJIB bila file data ada)

Jangan menulis metode generik bila data ada di tangan — **profilkan data dulu**:

```
python3 scripts/profile_dataset.py <file.csv|file.xlsx> --out profil
```

Hasilnya (`profil_dataset.md` + `profil_dataset.json`) berisi: jumlah baris/kolom, tipe data,
missing per kolom, distribusi/frekuensi, mean–median–SD, skewness, deteksi skala Likert,
**Cronbach's alpha** (bila terdeteksi), uji normalitas, serta **rekomendasi teknik analisis**
(paired t / independent t / one-way ANOVA / Wilcoxon / regresi / korelasi / Spearman).

> **Aturan anti-hallucination data**: angka yang muncul di BAB III (jumlah responden, rentang
> skor, mean, SD) **harus berasal dari output `profile_dataset.py` atau dihitung ulang dari file**.
> Dilarang mengarang angka. Bila data belum tersedia → tulis rancangan analisis *tanpa* angka
> preliminer, dan beri label `(data belum dianalisis)`.

### 4.3 Hipotesis → uji (tabel pemetaan)

Isi `templates/tabel_uji_statistik.md` dan tempelkan di BAB III:

| No | Rumusan Masalah | Hipotesis | Data | Uji Statistik | Keterangan |
|----|-----------------|-----------|------|---------------|------------|
| RM-1 | … | H₀₁ … / H₁₁ … | `[D:kolom]` | Uji X | α = 0,05 |

Bila data sudah terkumpul, **hitung uji sungguhan, jangan hanya menyebut nama uji**:

```bash
python3 scripts/stats_tests.py data/responden.csv --auto --out outputs/hasil_uji
python3 scripts/stats_tests.py data/responden.csv --regresi "DV=kinerja;X=motivasi;dukungan"
python3 scripts/stats_tests.py data/responden.csv --anova "DV=nilai" --grup=kelas
python3 scripts/stats_tests.py data/responden.csv --korelasi "v1=x1,v2=x2" --metode spearman
```

Keluaran `hasil_uji.md` berisi tabel hasil + narasi siap tempel ke BAB III;
`hasil_uji.json` berisi angka machine-readable untuk pengecekan `proposal_doctor.py`.
Dukungan: regresi berganda, t-test independen/berpasangan, one-way ANOVA, chi-square,
Pearson/Spearman, Cronbach's alpha. Memakai `scipy`/`statsmodels` bila terpasang;
tanpa dependensi pun, perhitungan internal tetap jalan (nilai kritis divalidasi
terhadap tabel).

> Angka hasil uji di BAB III harus **salin dari `hasil_uji.md`**, termasuk nilai p,
> t/F/χ², dan keputusan. Jangan menulis "berdasarkan hasil uji, Signifikan" tanpa angka.

### 4.4 Rancangan kualitatif (WAJIB bila desainnya kualitatif)

> Load `references/qualitative-analysis.md` + `references/methodology.md` §6–7.
> Instrumen: `templates/pedoman_wawancara.md`, `templates/informed_consent.md`.

Ganti — jangan tambahkan — bagian §4.1–4.3 yang bersifat kuantitatif:

| Elemen | Isi minimal |
|--------|-------------|
| Paradigma & desain | post-positivis/konstruktivis/kritis/pragmatis + studi kasus/fenomenologi/grounded theory/tematik/deskriptif — + alasan |
| Partisipan | kriteria inklusi **dan** eksklusi, teknik purposive/snowball, jumlah partisipan |
| Saturasi | **alasan penghentian** pengumpulan data (bukan sekadar "sampai jenuh") |
| Teknik pengumpulan | wawancara mendalam/semi-terstruktur, FGD, observasi-partisipan, studi dokumen, catatan lapangan — + alasan kesesuaian |
| Etika | informed consent tertulis, anonimisasi, hak mundur, penyimpanan rekaman |
| Analisis | tahapan berurutan: transkripsi → koding terbuka → kategorikal → tematik; alat (Miles-Huberman-Saldaña / BCA / Braun-Clarke) + alasan |
| Mutu data | member checking, triangulasi sumber/metode, audit trail |

Bila transkrip tersedia, buat tabel kode dengan `scripts/code_interview.py`:

```bash
python3 scripts/code_interview.py codebook outputs/codebook.csv \
    --transkrip folder-transkrip/ --out outputs/hasil_koding
python3 scripts/code_interview.py report outputs/hasil_koding.json
python3 scripts/code_interview.py merge a.json b.json -o outputs/gabungan.json
```

Format transkrip yang diharapkan: satu berkas per partisipan, penanda `[P01]`,
baris bergantian `Petugas:` / `Peserta:`. Codebook CSV kolomnya
`kode;kategori;tema;definisi` (tambah `pola` untuk regex bila perlu).

Tabel kode yang ditempel di BAB III:

| Kode | Kategori | Tema | Jumlah Kutipan | Sumber |
|------|----------|------|----------------|--------|
| M1 | Motivasi ekstrinsik | Motivasi kerja | 12 | `[K-1]`, `[K-3]` |

> **Aturan anti-hallucination kualitatif**: kutipan verbatim harus **benar-benar ada** di
> transkrip; jumlah kutipan dihitung dari output `code_interview.py`, bukan dikarang.
> Penanda kutipan memakai `[K-n]`, bukan `[L-n]`. Hasil pengodean adalah **bantuan analisis**,
> bukan temuan siap laporan — verifikasi tiap kode sebelum dipakai.

### Output Step 4
```
draft_bab2.md   — kerangka BAB II (sub-bab + sintesis + penanda sumber)
draft_bab3.md   — kerangka BAB III (desain + analisis + tabel uji / tabel kode)
profil_dataset.md | .json   (bila ada dataset kuantitatif)
hasil_uji.md | .json        (bila uji statistik dijalankan)
hasil_koding.md | .json      (bila pengodean wawancara dijalankan)
```

### Quality Gate 4
- [ ] Desain dipilih dengan **alasan**, bukan sekadar nama
- [ ] Populasi, teknik sampling, dan **n** (dengan rumus bilabersifat probabilistik) tertulis jelas
- [ ] Instrumen dinyatakan asal butirnya (dikembangkan sendiri atau diadaptasi dari `[L-n]`)
- [ ] **Setiap hipotesis kuantitatif punya satu teknik analisis** dan uji asumsi
- [ ] **Semua angka dataset berasal dari `profile_dataset.py`/perhitungan nyata** (wajib, tanpa kecuali)
- [ ] Bila uji dijalankan, angka hasil di BAB III cocok dengan `hasil_uji.md`
- [ ] Etika penelitian dan izin penelitian sudah ada di rancangan
- [ ] **Bila kualitatif: Gate 4-Kualitatif di `references/quality-gates.md` terpenuhi**

---

## STEP 5 — Menulis Draft (BAB I–III)

> Template: `templates/proposal_template.md` (dokumen penuh), `templates/bab1_pendahuluan.md`,
> `templates/bab2_tinjauan_pustaka.md`, `templates/bab3_metode.md`.
> Gaya penulisan dan struktur: `references/document-assembly.md`.

Aturan gaya:

- Bahasa Indonesia **akademik formal**: kalimat aktif & pasif sesuai konteks, tanpa
  kata repetitif dari poin sebelumnya, tanpa "di sini" berlebihan, tanpa terjemahan kaku.
- **Rantai argumen**: setiap sub-bab harus **menjawab pertanyaan** dari sub-bab sebelumnya, lalu
  memunculkan pertanyaan baru. Ini yang membedakan proposal yang *kohesif* dari yang *tempelan*.
- **Jangan menyalin** kalimat dari literatur; parafrase dan beri marker `[L-n]` sebagai bukti.
- **Kerangka Berpikir (BAB II)** wajib ada sebagai sub-bab penutup: hubungan antar variabel
  digambar ASCII/LaTeX atau tabel variabel + panah.
- **Tabel & gambar**: setiap tabel diberi judul di atas, sumber di bawah (`Sumber: analisis
  penulis, 2026` / `Sumber: [L-3]`). Nomor tabel/daftar isi auto oleh pandoc.

### Output Step 5
```
proposal_skripsi.md   # DOKUMEN UTAMA: halaman judul + daftar isi + BAB I + BAB II + BAB III + daftar pustaka
```

> **Jangan berhenti di kerangka.** Yang diserahkan ke user adalah proposal **naratif penuh**,
> bukan bullet/kerangka saja.

---

## STEP 6 — Quality Gate, Referensi, & Export

### 6.1 Daftar pustaka

Semua rujukan yang dikutip di teks **wajib ada** di daftar pustaka, dan sebaliknya (1:1).
Format: APA 7 default, atau gaya dari preset kampus (`references/citation-styles.md`).
Aturan:
- artikel: `Penulis, A. A. (Tahun). Judul. *Nama Jurnal*, *vol*(no), hal. DOI`
- buku: `Penulis, A. A. (Tahun). *Judul*. Penerbit.`
- dokumen lokal/pedoman: `Institusi (Tahun). *Judul*.`
- sumber dari file lokal tanpa DOI → **jangan dikarang DOI**; tulis `(dokumen lokal, namafile.pdf)`.

Bila matriks referensi tersedia (CSV/JSON dari `paper-review` atau buatan sendiri),
**jangan menulis daftar pustaka tangan** — ekspor otomatis:

```bash
# validasi dulu: baris tanpa judul & field kosong dilaporkan, tidak ditebak
python3 scripts/export_referensi.py matriks_referensi.csv --periksa

# -> referensi.bib, referensi.ris, referensi.xml (EndNote), referensi.txt
python3 scripts/export_referensi.py matriks_referensi.csv \
    --out-dir outputs/ --gaya apa --urutkan penulis --nomor L
```

Opsi: `--gaya apa|vancouver|ieee`, `--urutkan tahun|penulis|judul|input`,
`--nama`, `--nomor P` untuk sumber pedoman, `--quiet`.
Field kosong **tidak ditebak**; penomoran `[L-n]` mengikuti urutan akhir daftar pustaka,
bukan urutan file. Alur lengkap: `references/paper-review-integration.md`.

### 6.1b Verifikasi DOI (penegak aturan "DOI wajib resolve")

Aturan di atas menuntut setiap DOI benar-benar dapat di-resolve. Tanpa alat, itu
diperiksa manual — dan DOI karangan yang formatnya benar akan lolos. Jalankan:

```bash
# periksa semua DOI yang muncul di naskah / Daftar Pustaka
python3 scripts/verify_doi.py outputs/proposal_skripsi.md --out outputs/laporan_doi.md

# periksa entri tertentu saja
python3 scripts/verify_doi.py --doi 10.1016/j.ijinfomgt.2023.102642
```

Empat verdict:

| Verdict | Arti | Tindakan |
|---|---|---|
| `VALID` | terdaftar di Crossref/DataCite dan handle doi.org resolve | lolos |
| `TIDAK ADA` | tidak ditemukan di Crossref, DataCite, maupun doi.org | **hapus atau ganti** — indikasi kuat dikarang |
| `MENDUGA` | handle resolve tetapi tanpa metadata Crossref/DataCite | verifikasi manual (DOI lama/registrar lain) |
| `GAGAL` | jaringan gagal | jangan simpulkan apa pun; ulangi |

Kode keluar 1 bila ada `TIDAK ADA`/`MENDUGA`, 3 bila semua gagal karena jaringan.
Gunakan `--cache .doi_cache.json` agar pemeriksaan ulang tidak memanggil API lagi.
**Jangan pernah "memperbaiki" DOI dengan mengubah digit** — cari ulang di Google Scholar
atau situs jurnal, atau ganti dengan sumber yang benar-benar dibaca.

### 6.2 Quality gate akhir (semua wajib)

- [ ] Judul, identitas, dan jenjang konsisten dengan kontrak Step 0
- [ ] **Jumlah tujuan = jumlah rumusan masalah** (atau 1:1 terpetakan)
- [ ] Setiap tabel uji punya hipotesis + teknik analisis + sumber data
- [ ] **Nol angka dataset yang tidak berasal dari file** (spot-check: cocok dengan `profil_dataset.md`)
- [ ] Semua `[L-n]` punya entri di daftar pustaka; semua entri dikutip minimal sekali
- [ ] Tidak ada `[isi ...]` tersisa diam-diam → wajib dikonfirmasi user atau ditandai daftar
- [ ] Struktur bab sesuai pedoman kampus (bila ada template) & jenjang
- [ ] Bahasa: ejaan bahasa Indonesia (KBBI) — hindari "kwalitas", campur "pengaruh" dan "dampak",
  kalimat "yang mana" berlebihan, serta pengulangan "hasil-hasil"
- [ ] User menyetujui draft (gate human-in-the-loop)

### 6.2b Gate otomatis (WAJIB jalankan — jangan andalkan baca mata)

Naskah panjang mustahil diperiksa mata. Jalankan pemeriksa berikut; kode keluar `1`
(`--strict`) berarti **gate gagal** → perbaiki, jangan diekspor apa adanya.

```bash
# 1) gaya bahasa Indonesia (baku, partikel, rumus kabur) + struktur BAB I
python3 scripts/id_language_check.py outputs/proposal_skripsi.md \
    --struktur --md outputs/idl-check.md --strict

# 2) duplikasi dalam naskah sendiri
python3 scripts/plagiarism_check.py outputs/proposal_skripsi.md --internal --strict

# 3) tumpang tindih dengan berkas sumber (L2/L3/PDF yang sudah diekstrak)
python3 scripts/plagiarism_check.py outputs/proposal_skripsi.md \
    --sumber .cache_ekstrak/ --md outputs/plagiarism_report.md \
    --json outputs/plagiarism_report.json

# 4) penanda menggantung, placeholder, angka tanpa sumber, daftar pustaka, sinkronisasi DOCX
python3 scripts/proposal_doctor.py outputs/proposal_skripsi.md \
    --dataset data/responden.csv --hasil-uji outputs/hasil_uji.json \
    --docx outputs/proposal_skripsi.docx --json outputs/doctor.json --strict

# 5) kesesuaian struktur dengan pedoman kampus
python3 scripts/apply_campus_template.py check ugm outputs/proposal_skripsi.md --lengkap

# 6) verifikasi DOI — jangan lewati bila daftar pustaka memuat DOI
python3 scripts/verify_doi.py outputs/proposal_skripsi.md --out outputs/laporan_doi.md
```

| Pemeriksa | Menangkap |
|-----------|-----------|
| `id_language_check.py` | kata serapan asing, kata non-baku (KBBI), partikel salah tulis, rumus kabur, tanda baca/kapitalisasi, kalimat terlalu panjang, desimal & ribuan, istilah Inggris tak perlu, karakter non-Latin, penanda sumber tak terdefinisi, struktur BAB I |
| `plagiarism_check.py` | frasa identik ≥7 kata berurutan — duplikasi dalam naskah sendiri, dan tumpang tindih dengan berkas sumber. **Temuan adalah sinyal, bukan bukti**; setiap temuan wajib diverifikasi manual |
| `proposal_doctor.py` | subbab wajib BAB I–III, `[L-n]`/`[D:kolom]` menggantung, `[isi ...]` tersisa, entri daftar pustaka tak dikenal, kolom dataset yang disebut tapi tak ada, angka hard-code tanpa sumber, DOCX tidak sinkron |
| `apply_campus_template.py check` | subbab wajib per preset kampus + penanda isi khusus (`latar_belakang`, `rumusan_masalah`, `populasi_sampel`, `uji_statistik_cocok`, dst) |
| `verify_doi.py` | DOI yang tidak resolve di Crossref/DataCite/doi.org — indikasi DOI dikarang |

Temuan kategori selain `galat` boleh tersisa **bila ada alasan naratif** yang ditulis user.

### 6.2c Layered QC — 4 lapis pemeriksaan (WAJIB)

Gate di atas menangkap kesalahan yang **terlihat**. Empat lapis di bawah menangkap
kesalahan yang tidak terlihat: gaya khas AI, ejaan halus, lompatan makna, dan
naskah yang benar secara teknis tetapi lemah secara akademik.

Lapis berjalan **berurutan**. Lapis yang gagal menjadi **blocker** bagi lapis
berikutnya — pemeriksaan manual di atas kesalahan mekanis hanya membuang waktu.
Rincian lengkap: `references/quality-gates.md` Bagian B.

| Lapis | Nama | Yang diperiksa | Rujukan | Pelacak |
|-------|------|-----------------|---------|---------|
| 1 | Humanizer | tanda tangan khas generator; **fakta tidak boleh berubah** | `references/revision-guide.md` | `checklists/humanizer_checklist.md` |
| 2 | Mekanis / EYD | ejaan, tanda baca, kapitalisasi, bentuk baku, duplikasi | `references/eyd-check.md` | `checklists/eyd_check.md` |
| 3 | Semantik | konsistensi istilah, kesesuaian 1:1, klaim tanpa sumber, angka tidak konsisten | Gate 6 + Gate 4-Kualitatif | — |
| 4 | Red-team | baca ulang sebagai pembimbing yang menolak | Bagian B.4 | rubrik kelulusan |

**Lapis 1 — Humanizer.** Periksa 25 pola di `references/revision-guide.md`: kalimat
pembuka/penutup bab generik, kalimat tesis yang mengulang judul, tanda pisah sebagai
penghubung, "tidak hanya... tetapi juga" berulang, penegasan berlebihan, markdown
berlebihan. **Dilarang** mengubah angka, kutipan asli, penanda `[L-n]`/`[D:kolom]`,
rumusan masalah, tujuan, dan hipotesis.

**Lapis 2 — Mekanis/EYD.** Otomatis penuh. Selain `id_language_check.py`, jalankan
`plagiarism_check.py`. Rujukan: EYD V (Permendikbudristek 18/2022) dan KBBI. Bila
LanguageTool `id-ID` tersedia, jalankan sebagai pelengkap dan **verifikasi manual
setiap sarannya** — LanguageTool sering menolak kata baku.

**Lapis 3 — Semantik.** Satu konsep satu istilah; rumusan masalah = tujuan =
hipotesis = uji di BAB III; setiap klaim empiris punya marker; tidak ada inferensi
tak bertanda; angka di BAB I, BAB III, dan abstract sama.

**Lapis 4 — Red-team.** Baca proposal sebagai pembimbing yang menolak, bukan sebagai
penulis yang membela diri. Jawab 9 pertanyaan di `references/quality-gates.md` B.4,
tulis **satu** kelemahan paling fatal, lalu isi rubrik kelulusan:

| Aspek | Bobot |
|-------|-------|
| Kejelasan rumusan masalah | 25 |
| Dasar teori dan posisi gap | 20 |
| Kesesuaian metode dan data | 20 |
| Kualitas bahasa dan struktur | 20 |
| Originalitas dan kebaruan | 15 |

**Ambang: skor total ≥75 dan tidak ada aspek bernilai 0.** Di bawah itu, kembali ke
tahap yang relevan — bukan mengulang Lapis 1.

> Ringkasnya: **Gate per tahap** menjawab "apakah tahap ini selesai?"; **Layered QC**
> menjawab "apakah naskah ini layak diserahkan?". Keduanya wajib, dan tidak saling
> menggantikan.


### 6.3 Export

```bash
# DOCX (rekomendasi; butuh pandoc)
scripts/build_docx.sh proposal_skripsi.md --out-dir . --title "Judul Proposal" --number-sections

# dengan reference-doc pedoman kampus (opsional, lebih akurat daripada preset)
scripts/build_docx.sh proposal_skripsi.md --out-dir . --ref-doc pedoman_kampus.docx --toc --clean

# LaTeX (opsional)
pandoc proposal_skripsi.md -o proposal_skripsi.tex --number-sections
```

`build_docx.sh` membuat: `.docx` (dengan daftar isi otomatis bila `--toc`), `daftar_isi.md`,
dan `<nama>_ekstrak.md` bila dijalankan dengan `--clean` (naskah tanpa blok instruksi internal).

Urutan benar: **tulis draft → gate otomatis → perbaiki → ekspor DOCX → `proposal_doctor --docx`
untuk memastikan DOCX sinkron dengan Markdown.** Jangan ekspor dulu lalu memeriksa.

### Output Step 6
```
📋 OUTPUT UTAMA (wajib):
  proposal_skripsi.md          # proposal lengkap (BAB I–III, Bahasa Indonesia)
  proposal_skripsi.docx        # DOCX siap dibaca dan disunting
  daftar_pustaka.md            # daftar pustaka (juga sudah ada di dalam proposal)
🗂 PENDUKUNG (bila dipakai):
  matriks_evidence.md | catatan_gap.md | sumber_inventaris.md | profil_dataset.md | draft_bab*.md
  hasil_uji.md | hasil_koding.md | referensi.{bib,ris,xml,txt} | idl-check.md | doctor.json
  lampiran_pedoman_wawancara.md | lampiran_informed_consent.md
```

---

## Alur Pemakaian Cepat

| Permintaan | Action |
|-----------|--------|
| "Bikin proposal skripsi dari folder [path] tentang X" | Step 0 tanyakan jenjang → 1 inventaris → 2 bukti → 3–4 formulasi → 5 draft → 6 export |
| "Buat proposal tesis, fokus mixed-methods" | Jenjang Thesis + mode Folder+Online; wajib tulis threat to validity dan strategi generalisasi |
| "Cuma bab 3 metode, data csv sudah ada" | Langsung Step 1 (klasifikasi) → Step 4 (`profile_dataset.py`) → tulis BAB III → export |
| "Proposal kualitatif / analisis tematik, ada transkrip" | Step 1 (kategori transkrip) → §4.4 + `references/qualitative-analysis.md` → `code_interview.py` → Gate 4-Kualitatif |
| "Buat pedoman wawancara + informed consent" | Salin `templates/pedoman_wawancara.md` & `templates/informed_consent.md`, sesuaikan konteks; lampirkan di proposal |
| "Koding transkrip ini jadi tabel kode" | Susun codebook CSV (`kode;kategori;tema;definisi`) → `code_interview.py codebook …` → `report` → tempel tabel kode BAB III |
| "Review literatur untuk latar belakang dulu" | Step 2 → bila butuh tabel penuh: **pakai skill `paper-review`** |
| "Pakai pedoman kampus ini" | `apply_campus_template.py list` → `init <preset>` (atau file pedoman/path) → Step 6 `check` |
| "Format skripsi UGM/UI/ITB" | Step 0 set preset → `init` → Step 6 `check <preset> naskah --lengkap` |
| "Cek ANOVA atau regresi untuk data ini" | `profile_dataset.py` → baca rekomendasi uji → `stats_tests.py --auto` → Bab III tabel uji |
| "Hitung uji statistiknya sekalian" | `stats_tests.py <csv> --auto` atau `--regresi/--anova/--korelasi` → salin angka dari `hasil_uji.md` |
| "Tambah studi terdahulu 5 paper" | Step 2 matriks evidence + `[L-n]` baru; update BAB II + daftar pustaka |
| "Ekspor referensi ke BibTeX/RIS/EndNote" | `export_referensi.py matriks.csv --out-dir outputs/ --gaya apa --periksa` dulu |
| "Cek ejaan / periksa bahasa / cek daftar pustaka / periksa proposal" | `id_language_check.py --struktur` + `proposal_doctor.py --strict` (§6.2b) |
| "Buatkan tulisan yang tidak kayak AI" / "hilangkan ciri AI" | Lapis 1 Layered QC: `references/revision-guide.md` + `checklists/humanizer_checklist.md` (§6.2c) |
| "Cek plagiarisme / cek similarity" | `plagiarism_check.py --internal` dan `--sumber .cache_ekstrak/` + `checklists/plagiarism_check.md` |
| "Periksa naskah secara menyeluruh" / "simulasi ditinjau pembimbing" | Jalankan Layered QC Lapis 1–4 + rubrik kelulusan (§6.2c) |
| "Ekspor ke LaTeX" | `pandoc proposal.md -o proposal.tex --number-sections` (opsional) |

---

## Aturan Penting (Selalu Berlaku)

0. **Output utama = proposal naratif lengkap (BAB I–III)**, bukan kerangka/bullet, bukan ringkasan.
   Draft per-bab (draft_bab*.md) hanya working file internal.
1. **Jangan mengarang data.** Angka responden, skor, mean, SD, hasil uji → dari `profile_dataset.py`
   atau file nyata; kalau belum dianalisis → tulis `(data belum dianalisis)`, bukan angka karangan.
   Angka hasil uji → salin dari `stats_tests.py` (`hasil_uji.md`), bukan ingatan.
2. **Jangan mengarang literatur/penulis/DOI.** Setiap `[L-n]` terverifikasi (DOI resolve atau file
   lokal dibaca). Sumber lokal tanpa DOI → tandai `(dokumen lokal)`. Ekspor daftar pustaka pakai
   `export_referensi.py`; field kosong ditandai, bukan ditebak.
3. **Jangan mengarang identitas.** NIM, fakultas, dosen, nama responden → `[isi ...]` bila tidak ada.
   Nama peserta kualitatif selalu disamarkan (P1, peserta 3), meski ada persetujuan lisan.
4. **Jenjang menentukan kedalaman.** S1 = penerapan; S2 = pengembangan kerangka; S3 = kontribusi
   teoretis orisinal. Jangan menulis proposal S1 yang setebal proposal S3 (atau sebaliknya).
5. **Tujuan = 1:1 rumusan masalah.** Ini quality gate, bukan saran.
6. **Setiap klaim empiris ber-marker sumber**: `[L-n]`, `[D:kolom]`, `[K-n]` (kutipan kualitatif),
   `[U]`, `(inferensi)`.
7. **Human-in-the-loop**: konfirmasi hanya di Step 0 & sebelum export, tidak per-bagian.
8. **Simpan artefak sebagai file** di folder kerja user, bukan hanya di chat.
9. **Eja Indonesia**: KBBI, kapitalisasi kalimat, istilah asing italic pada penyebutan pertama.
   Jalankan `id_language_check.py`; ia **menandai**, perbaikan tetap oleh manusianya.
10. **Bahasa output selalu Bahasa Indonesia**, kecuali user minta naskah inggris.
11. **Jalankan gate otomatis sebelum ekspor** (`id_language_check.py`, `proposal_doctor.py`,
    `apply_campus_template.py check`). Kode keluar `1` = gate gagal, jangan diabaikan.
12. **Pedoman kampus user mengalahkan preset skill.** Preset hanya acuan; bila user punya
    file pedoman resmi, prescribing itu yang dipakai.
13. **Kualitatif ≠ kuantitatif tanpa angka.** Tanpa rumus probabilistik, alpha, atau tabel
    hipotesis → uji; tapi wajib ada pedoman wawancara, informed consent, dan alasan saturasi.
14. **Verbatim adalah data, bukan tafsir.** Kutipan tidak boleh dibuat, diringkas, atau
    diartikan ulang; jumlah kutipan dihitung, bukan diperkirakan.
15. **Humanizer boleh mengubah gaya, tidak boleh mengubah fakta.** Angka, kutipan asli,
    penanda `[L-n]`/`[D:kolom]`/`[K-n]`, rumusan masalah, tujuan, dan hipotesis tetap
    utuh setelah Lapis 1.
16. **Temuan plagiarisme adalah sinyal, bukan bukti.** Frasa identik muncul karena istilah
    baku dan nama instrumen, bukan otomatis plagiarisme. Yang diminta bukan "nol temuan",
    tapi setiap temuan punya keputusan tercatat.
17. **Naskah harus melewati Layered QC Lapis 1–4** sebelum diserahkan (§6.2c). Gate per tahap
    yang lolos **tidak** berarti naskah layak diserahkan. Ambang rubrik: skor ≥75, tidak
    ada aspek bernilai 0.

## Referensi Internal

### Referensi (panduan baca)

| File | Gunakan untuk |
|------|---------------|
| [references/data-sources.md](references/data-sources.md) | Klasifikasi & ekstraksi file lokal (PDF/DOCX/MD/CSV/XLSX/JSON) |
| [references/problem-formulation.md](references/problem-formulation.md) | Rumusan masalah, tujuan, manfaat, gap (TAS), hipotesis, variabel, batasan |
| [references/methodology.md](references/methodology.md) | Desain penelitian, sampling, instrumen, teknik analisis, etika, uji asumsi |
| [references/qualitative-analysis.md](references/qualitative-analysis.md) | **Jalur kualitatif**: desain, teknik pengumpulan, tahapan pengodean, mutu, batasan |
| [references/dataset-analysis.md](references/dataset-analysis.md) | Profil dataset & pemilihan uji statistik, cara membaca `profil_dataset.md` |
| [references/online-search.md](references/online-search.md) | Pencarian online pelengkap (OpenAlex/Semantic Scholar) |
| [references/document-assembly.md](references/document-assembly.md) | Gaya bahasa Indonesia, struktur BAB, kerangka berpikir, tabel dan gambar |
| [references/citation-styles.md](references/citation-styles.md) | Format daftar pustaka (APA 7/Chicago/Harvard/Vancouver/IEEE) |
| [references/paper-review-integration.md](references/paper-review-integration.md) | Alih matriks `paper-review` → BAB II → ekspor sitasi |
| [references/quality-gates.md](references/quality-gates.md) | Rincian quality gate per tahap, Gate 4-Kualitatif, **Layered QC Lapis 1–4**, checklist akhir |
| [references/revision-guide.md](references/revision-guide.md) | **Humanizer**: 25 pola gaya khas AI + cara memperbaikinya tanpa mengubah fakta (Lapis 1) |
| [references/eyd-check.md](references/eyd-check.md) | **EYD & KBBI**: ejaan, tanda baca, kapitalisasi, konjungsi, konsistensi istilah (Lapis 2) |
| [references/plagiarism-check.md](references/plagiarism-check.md) | **Pemeriksaan plagiarisme**: 5 tipe, deteksi lokal, ambang similarity, studi kasus proposal (Lapis 2–3) |

### Checklist pemeriksaan

| File | Gunakan untuk |
|------|---------------|
| [checklists/humanizer_checklist.md](checklists/humanizer_checklist.md) | Pelacak Lapis 1: pola AI, tanda baca, kata, dan yang tidak boleh diubah |
| [checklists/eyd_check.md](checklists/eyd_check.md) | Pelacak Lapis 2: ejaan, tanda baca, kapitalisasi, konsistensi istilah |
| [checklists/plagiarism_check.md](checklists/plagiarism_check.md) | Pelacak Lapis 2–3: verifikasi setiap temuan, 5 tipe plagiarisme, ambang similarity |

### Template

| File | Gunakan untuk |
|------|---------------|
| [templates/proposal_template.md](templates/proposal_template.md) | Template dokumen proposal penuh (judul → daftar isi → BAB I–III) |
| [templates/bab1_pendahuluan.md](templates/bab1_pendahuluan.md) | Template BAB I |
| [templates/bab2_tinjauan_pustaka.md](templates/bab2_tinjauan_pustaka.md) | Template BAB II |
| [templates/bab3_metode.md](templates/bab3_metode.md) | Template BAB III |
| [templates/tabel_uji_statistik.md](templates/tabel_uji_statistik.md) | Tabel pemetaan hipotesis → uji statistik |
| [templates/pedoman_wawancara.md](templates/pedoman_wawancara.md) | **Pedoman wawancara** untuk Lampiran (jalur kualitatif) |
| [templates/informed_consent.md](templates/informed_consent.md) | **Lembar persetujuan** & pernyataan kerahasiaan |

### Script

| File | Gunakan untuk |
|------|---------------|
| [scripts/ingest_sources.sh](scripts/ingest_sources.sh) | Scan & ekstrak file lokal → inventaris |
| [scripts/profile_dataset.py](scripts/profile_dataset.py) | Profil dataset CSV/XLSX/TSV/JSON + rekomendasi uji |
| [scripts/stats_tests.py](scripts/stats_tests.py) | Uji statistik nyata → `hasil_uji.md/.json` (regresi, t-test, ANOVA, chi2, korelasi, alpha) |
| [scripts/code_interview.py](scripts/code_interview.py) | Koding transkrip → tabel kode, frekuensi, cuplikan (`[K-n]`) |
| [scripts/export_referensi.py](scripts/export_referensi.py) | Matriks referensi → BibTeX / RIS / EndNote XML / daftar pustaka |
| [scripts/id_language_check.py](scripts/id_language_check.py) | Pemeriksa bahasa Indonesia (baku, partikel, rumus kabur, serapan, tanda baca) + struktur BAB I |
| [scripts/plagiarism_check.py](scripts/plagiarism_check.py) | Deteksi tumpang tindih teks: duplikasi internal + perbandingan dengan folder sumber |
| [scripts/proposal_doctor.py](scripts/proposal_doctor.py) | Pemeriksaan akhir naskah (penanda, placeholder, angka, sinkronisasi DOCX) |
| [scripts/apply_campus_template.py](scripts/apply_campus_template.py) | Preset kampus: `list`/`show`/`init`/`check`/`new-custom` (menampilkan provenance tiap preset) |
| [scripts/generate_campus_presets.py](scripts/generate_campus_presets.py) | Generator preset kampus (provenance wajib; `--check` deteksi drift, `--patch` merge gaya ke preset lama tanpa menimpa struktur) |
| [scripts/build_docx.sh](scripts/build_docx.sh) | Markdown → DOCX (pandoc) + daftar isi |

### Data & uji

| File | Gunakan untuk |
|------|---------------|
| [campus_templates/generic.json](campus_templates/generic.json) | Preset generik - dipakai bila tidak ada preset kampus |
| [campus_templates/ugm.json](campus_templates/ugm.json) | Universitas Gadjah Mada — **resmi**: Panduan Skripsi FKH UGM 2024 (+DTSL FT 2023 sbg catatan) |
| [campus_templates/ui.json](campus_templates/ui.json) | Universitas Indonesia — **resmi**: Pedoman Penulisan TA UI 2017 (SK Rektor 2143/SK/R/UI/2017, lintas fakultas) |
| [campus_templates/uny.json](campus_templates/uny.json) | Universitas Negeri Yogyakarta — konvensi umum |
| [campus_templates/itb.json](campus_templates/itb.json) | Institut Teknologi Bandung — **resmi**: pedoman skripsi FITB/SITH (standar SPS ITB) |
| [campus_templates/custom.json](campus_templates/custom.json) | Kerangka kosong untuk diisi preset institusi lain |
| [campus_templates/ipb.json](campus_templates/ipb.json) | Institut Pertanian Bogor — **resmi**: PPKI, PerRektor IPB 27/IT3/PP/2019 |
| [campus_templates/unair.json](campus_templates/unair.json) | Universitas Airlangga — **resmi**: Buku Panduan Skripsi & TA Fakultas Vokasi 2025 |
| [campus_templates/ub.json](campus_templates/ub.json) | Universitas Brawijaya — **resmi**: Panduan FT-UB 2016 (mirror margin) |
| [campus_templates/its.json](campus_templates/its.json) | Institut Teknologi Sepuluh Nopember — **resmi**: Pedoman TA FTI-ITS 2021 |
| [campus_templates/undip.json](campus_templates/undip.json) | Universitas Diponegoro — **resmi**: Buku Saku Pedoman Skripsi FPIK UNDIP 2021 |
| [campus_templates/unpad.json](campus_templates/unpad.json) | Universitas Padjadjaran — **resmi**: Pedoman FISIP/FTIP/Farmasi Unpad |
| [campus_templates/unhas.json](campus_templates/unhas.json) | Universitas Hasanuddin — **resmi**: KepRect UNHAS 10438/UN4.1/KEP/2023 (B5, bab publikasi) |
| [campus_templates/telu.json](campus_templates/telu.json) | Telkom University — **resmi**: Sistematika TA FEB Telkom 2015 |
| [campus_templates/binus.json](campus_templates/binus.json) | BINUS University — konvensi umum |
| [campus_templates/umy.json](campus_templates/umy.json) | Universitas Muhammadiyah Yogyakarta — **resmi**: Pedoman FEB UMY (SK Rektor 217/SK-UMY/X/2017) |
| [campus_templates/uii.json](campus_templates/uii.json) | Universitas Islam Indonesia — **resmi**: Panduan TA Farmasi UII 2017 Rev 1 |
| [campus_templates/uad.json](campus_templates/uad.json) | Universitas Ahmad Dahlan — **resmi**: Pedoman Skripsi FH UAD 2018 + Panduan FMIPA UAD 2.1 |
| [campus_templates/ums.json](campus_templates/ums.json) | Universitas Muhammadiyah Surakarta — **resmi**: Buku Pedoman Skripsi Manajemen FEB UMS |
| [campus_templates/udinus.json](campus_templates/udinus.json) | Universitas Dian Nusantara — konvensi umum |
| [campus_templates/umm.json](campus_templates/umm.json) | Universitas Muhammadiyah Malang — konvensi umum |
| [campus_templates/umb.json](campus_templates/umb.json) | Universitas Mercu Buana — konvensi umum |
| [campus_templates/gunadarma.json](campus_templates/gunadarma.json) | Universitas Gunadarma — konvensi umum |
| [campus_templates/upn_veteran.json](campus_templates/upn_veteran.json) | UPN Veteran Yogyakarta — konvensi umum |
| [campus_templates/upnvj.json](campus_templates/upnvj.json) | UPN Veteran Jakarta — konvensi umum |
| [campus_templates/upnv_jatim.json](campus_templates/upnv_jatim.json) | UPN Veteran Jawa Timur — konvensi umum |
| [campus_templates/budi_luhur.json](campus_templates/budi_luhur.json) | Universitas Budi Luhur — konvensi umum |
| [campus_templates/umn.json](campus_templates/umn.json) | Universitas Multimedia Nusantara — **resmi**: Panduan Skripsi Kajian/FIKOM/MMT UMN |
| [tests/run_tests.sh](tests/run_tests.sh) | Smoke test seluruh script (`bash tests/run_tests.sh`) |
| [tests/sample_dataset.csv](tests/sample_dataset.csv) | Dataset contoh untuk uji script |
| [tests/codebook_contoh.csv](tests/codebook_contoh.csv) | Contoh codebook pengodean |
| [tests/transkrip_contoh.md](tests/transkrip_contoh.md) | Contoh transkrip untuk uji `code_interview.py` |
| [tests/matriks_referensi_contoh.csv](tests/matriks_referensi_contoh.csv) | Contoh matriks untuk uji `export_referensi.py` |

## Integrasi Skill

| Kebutuhan | Skill yang dipakai |
|-----------|---------------------|
| Tabel review literatur lengkap (12 kolom, provenance, ekspor CSV/XLSX/BIB/RIS) | `paper-review` |
| Protocol penulisan paper jurnal (English) | `academic-writing` |
| Slide defence/sidang | `pptx` (di luar cakupan skill ini) |
| Penyusun proposal berbahasa Indonesia (skill ini) | `proposal-skripsi` |

## Atribusi

Struktur pipeline dan protokol anti-hallucination mengikuti **bimajanuri/academic-writing-skill**
dan **bimajanuri/paper-review-skill**. Kerangka proposal (rumusan masalah → tujuan → metode →
manfaat), metode gap **TAS/Berwald-Daellenbach**, dan pola "sintesis literatur → kerangka
berpikir" mengikuti praktik metodologi penelitian standar; rujukan metodologis yang direferensikan
tanpa mengutip teks: **Creswell & Creswell** (desain mixed-methods), **Field** (analisis statistik),
**Kumar** (penelitian tindakan/R&D), **Sugiyono** (desain & statistik Indonesia), **Braun &
Clarke** (analisis tematik), **Miles, Huberman & Saldaña** (kualitatif). Detail di README.

## Platform Note

Format Agent Skills (SKILL.md) portabel ke OpenCode (`~/.config/opencode/skills/`),
Claude Code (`~/.claude/skills/`), dan platform lain dengan menyalin folder ini.
