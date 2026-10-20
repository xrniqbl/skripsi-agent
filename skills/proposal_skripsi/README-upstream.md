# Proposal Skripsi Skill

**Skill penyusun proposal penelitian berbahasa Indonesia** untuk AI coding agents (Claude Code,
OpenCode, dan agen berbasis Agent Skills lainnya). Menghasilkan **proposal lengkap BAB I
Pendahuluan, BAB II Tinjauan Pustaka, dan BAB III Metode Penelitian** untuk **skripsi (S1),
thesis (S2), atau disertasi (S3)** — dipilih pengguna.

Sumber bukti diambil dari **kumpulan file lokal** yang ditunjuk user (PDF, DOCX, MD, TXT, CSV,
XLSX, JSON), ditambah **pencarian online pelengkap** bila literatur lokal minim.

Skill ini **berkumpulan** dengan `paper-review` (tabel review literatur lengkap) dan
`academic-writing` (protocol penulisan paper English) — bukan duplikatnya.

## Fitur Utama

- **Tiga jenjang dalam satu skill**: skripsi, thesis, disertasi — dengan perbedaan kedalaman yang
  nyata (panjang, kontribusi, landasan teori, pengujian, threat to validity, statement of
  contribution)
- **Sumber data lokal**: scan folder rekursif, klasifikasi otomatis ke 6 kategori
  (literatur, data kuantitatif, transkrip/kodebook, pedoman, aturan/etika, lainnya),
  ekstraksi teks PDF dan DOCX
- **Analisis dataset nyata**: `profile_dataset.py` memprofilkan CSV/TSV/XLSX/JSON —
  deskriptif, missing, skewness, normalitas, Cronbach's alpha, deteksi skala Likert, dan
  **rekomendasi teknik analisis**. Semua angka di BAB III berasal dari sana, bukan dikarang
- **Uji statistik nyata, bukan sekadar nama uji**: `stats_tests.py` menjalankan regresi berganda,
  t-test independen/berpasangan, one-way ANOVA, chi-square, Pearson/Spearman, dan
  Cronbach's alpha, lalu menghasilkan tabel hasil + narasi siap tempel. Angka hasil uji
  disalin dari keluarannya, bukan ditulis dari ingatan
- **Jalur kualitatif penuh**: desain (studi kasus, fenomenologi, grounded theory, analisis
  tematik), pedoman wawancara, informed consent, pengodean transkrip menjadi tabel kode
  (`code_interview.py`), penanda kutipan `[K-n]`, dan **Gate 4-Kualitatif** tersendiri
- **Preset template kampus**: 28 preset — `ugm`, `ui`, `uny`, `itb`, `ipb`, `unair`, `ub`,
  `its`, `undip`, `unpad`, `unhas`, `telu`, `binus`, `umy`, `uii`, `uad`, `ums`, `udinus`,
  `umm`, `umb`, `gunadarma`, `upn_veteran`, `upnvj`, `upnv_jatim`, `budi_luhur`,
  `umn` (Universitas Multimedia Nusantara),
  plus `generic` dan `custom` — berisi gaya dokumen, gaya sitasi, daftar kelengkapan, dan
  struktur bab; bisa `init` (kerangka naskah) dan `check` (naskah vs ketentuan preset),
  atau `new-custom` untuk institusi lain
  - **Provenance wajib dicek**: `list` menandai `[resmi]` vs `[konvensi]`, dan
    `show <preset>` menampilkan dokumen/URL/cakupan sumber. Preset `[konvensi]`
    **belum diverifikasi** — wajib dicocokkan manual. Saat ini **18 `[resmi]`**
    (`ipb`, `itb`, `its`, `telu`, `uad`, `ub`, `ugm`, `ui`, `uii`, `umn`, `ums`,
    `umy`, `unair`, `undip`, `unhas`, `unpad`) dan **10 `[konvensi]`**; tiap
    `[resmi]` hanya berlaku untuk fakultas/tahun di `scope`.
  - **Nilai yang belum terverifikasi ditulis apa adanya**: bila dokumen resmi
    tidak mencantumkan angka margin/spasi, preset mengisi
    `"perlu konfirmasi (bagian X)"` — bukan angka tebakan.
  - **Perbedaan antar fakultas**: `sumber.catatan` dan `verifikasi` menegaskan perbedaan
    antar fakultas (mis. UGM FKH spasi 2 vs DTSL Teknik spasi 1,15).
- **Pemeriksa naskah otomatis**: `id_language_check.py` (gaya bahasa Indonesia, struktur
  BAB I) dan `proposal_doctor.py` (penanda menggantung, placeholder, angka tanpa sumber,
  daftar pustaka tak dikenal, sinkronisasi DOCX). Kode keluar `1` = gate gagal
- **Ekspor referensi**: `export_referensi.py` mengubah matriks CSV/JSON menjadi BibTeX,
  RIS, EndNote XML, dan daftar pustaka siap tempel (APA/Vancouver/IEEE). Field kosong
  ditandai, bukan ditebak
- **Rancangan statistik lengkap**: pemetaan hipotesis ke uji, uji asumsi, uji alternatif
  non-parametrik, rumus penentuan sampel (Cochran, Krejcie & Morgan, koreksi populasi hingga)
- **Metode kuantitatif, kualitatif, mixed-methods, R&D, penelitian tindakan, studi kasus** —
  lengkap dengan elemen wajib dan alasan pemilihan
- **Argumen gap TAS/Berwald-Daellenbach**: 3 pertanyaan pemandu agar gap bukan sekadar
  "belum diteliti di lokasi X"
- **Penandaan sumber (provenance)**: `[L-n]` literatur, `[D:kolom]` dataset, `[K-n]` kutipan
  kualitatif, `[U]` brief user, `[P-n]` pedoman, `(inferensi)` untuk penalaran agent
- **Anti-hallucination ketat**: tidak mengarang data, kutipan, DOI, identitas, responden,
  atau hasil uji
- **Layered QC 4 lapis** (`references/quality-gates.md` Bagian B), adaptasi dari skill
  `academic-writing`:
  - **Lapis 1 — Humanizer**: 25 pola gaya khas AI (kalimat pembuka/penutup generik, tanda
    pisah sebagai penghubung, penegasan berlebihan, markdown berlebihan) dengan aturan
    keras: **gaya boleh berubah, fakta tidak** — angka, kutipan, marker, dan rumusan masalah
    tetap utuh
  - **Lapis 2 — Mekanis/EYD**: ejaan, tanda baca, kapitalisasi, bentuk baku (EYD V /
    Permendikbudristek 18/2022 + KBBI), plus deteksi duplikasi. Sepenuhnya otomatis
  - **Lapis 3 — Semantik**: konsistensi istilah, kesesuaian 1:1
    rumusan masalah = tujuan = hipotesis = uji, klaim tanpa sumber, angka tidak konsisten
  - **Lapis 4 — Red-team**: baca ulang sebagai pembimbing yang menolak, 9 pertanyaan
    pemeriksa + rubrik kelulusan (skor ≥75, tanpa aspek bernilai 0)
- **Pemeriksa plagiarisme**: `plagiarism_check.py` mendeteksi frasa identik ≥7 kata berurutan —
  duplikasi dalam naskah sendiri dan tumpang tindih dengan folder sumber. Menangani 5 tipe
  plagiarisme termasuk mosaik, parafrase dangkal, dan *laundering* sitasi. Temuan adalah
  **sinyal, bukan bukti**: yang diminta setiap temuan punya keputusan tercatat
- **Ekspor Markdown + DOCX (pandoc)** dengan daftar isi otomatis, pemeriksaan marker, dan
  deteksi placeholder yang belum diisi
- **Gaya bahasa Indonesia akademik**: panduan kalimat, ejaan KBBI, kapitalisasi, istilah asing

## Pipeline

```text
STEP 0: KLARIFIKASI  -> jenjang, bidang, topik, jenis penelitian, folder sumber, preset kampus
STEP 1: INVENTARIS   -> scan + klasifikasi file -> sumber_inventaris.json
STEP 2: EVIDENSI     -> matriks evidence ringkas + gap (TAS) + online search pelengkap
STEP 3: FORMULASI    -> latar belakang, rumusan masalah, tujuan, manfaat, hipotesis, variabel
STEP 4: RANCANGAN    -> desain metode, instrumen, sampling, teknik analisis
                       + analisis dataset (kuantitatif) ATAU pengodean transkrip (kualitatif)
STEP 5: DRAFT        -> halaman judul + daftar isi + BAB I-III (Markdown)
STEP 6: GATE+EXPORT  -> id_language_check + proposal_doctor + campus check
                       -> daftar pustaka -> MD + DOCX (pandoc)
```

Setiap tahap punya quality gate. Konfirmasi user hanya di Step 0 dan sebelum export.

## Instalasi

### Claude Code

```bash
# Opsi 1 - symlink (kanonik, sekali update)
mkdir -p ~/.agents/skills
ln -s $(pwd) ~/.agents/skills/proposal-skripsi
ln -s ../../.agents/skills/proposal-skripsi ~/.claude/skills/proposal-skripsi

# Opsi 2 - salin langsung
cp -R . ~/.claude/skills/proposal-skripsi
```

### OpenCode

```bash
# Opsi 1 - symlink
ln -s ../../.agents/skills/proposal-skripsi ~/.config/opencode/skills/proposal-skripsi

# Opsi 2 - salin langsung
cp -R . ~/.config/opencode/skills/proposal-skripsi
```

> Rekomendasi: simpan repo ini sebagai kanonik di `~/.agents/skills/proposal-skripsi`, lalu
> **symlink** ke folder skills masing-masing klien. Edit cukup sekali di sumber.

## Penggunaan

Skill aktif otomatis saat user meminta, misalnya:

- "Bikin proposal skripsi dari folder [path] tentang X"
- "Buat proposal tesis mixed-methods, data saya di [path]"
- "Bantu susun Bab III, ada data CSV di sini"
- "Buat proposal kualitatif analisis tematik, transkripnya ada di folder ini"
- "Buat pedoman wawancara dan informed consent untuk studi kasus saya"
- "Tulis bab 1 dan 2 dari paper-paper folder ini"
- "Cek uji statistik yang cocok untuk data ini"
- "Pakai format skripsi UGM" / "sesuaikan dengan pedoman kampus saya"
- "Ekspor daftar pustaka ke BibTeX dan EndNote"
- "Periksa bahasa dan daftar pustaka proposal ini"
- "Rancang proposal disertasi dengan kontribusi teoretis baru"
- "Ekspor proposal ke DOCX"

Alur kerja: **Klarifikasi -> Inventaris -> Bukti dan Gap -> Formulasi -> Rancangan -> Draf ->
Quality Gate (otomatis) -> Export.**

## Contoh Pemakaian Script

```bash
# 1. Inventarisasi + ekstraksi teks PDF
scripts/ingest_sources.sh ./folder-sumber --json

# 2. Profil dataset (tidak butuh pandas; XLSX butuh openpyxl)
python3 scripts/profile_dataset.py data/responden.csv --out profil

# 3. Uji statistik nyata -> hasil_uji.md (tabel + narasi) + hasil_uji.json
python3 scripts/stats_tests.py data/responden.csv --auto --out hasil_uji
python3 scripts/stats_tests.py data/responden.csv --regresi "DV=kinerja;X=motivasi;dukungan"
python3 scripts/stats_tests.py data/responden.csv --anova "DV=nilai" --grup=kelas

# 4. Jalur kualitatif: koding transkrip -> tabel kode
python3 scripts/code_interview.py codebook codebook.csv \
    --transkrip folder-transkrip/ --out hasil_koding
python3 scripts/code_interview.py report hasil_koding.json

# 5. Preset template kampus
python3 scripts/apply_campus_template.py list
python3 scripts/apply_campus_template.py show unpad   # cek provenance (dokumen/URL/scope)
python3 scripts/apply_campus_template.py init unpad --out proposal.md
python3 scripts/apply_campus_template.py check unpad proposal.md --lengkap
python3 scripts/apply_campus_template.py new-custom --out-dir institusi_saya.json

# 6. Ekspor daftar pustaka -> BibTeX / RIS / EndNote XML / teks
python3 scripts/export_referensi.py matriks_referensi.csv --periksa
python3 scripts/export_referensi.py matriks_referensi.csv \
    --out-dir outputs/ --gaya apa --urutkan penulis

# 7. Gate otomatis (kode keluar 1 = gagal, perbaiki dulu)
python3 scripts/id_language_check.py proposal.md --struktur --strict
python3 scripts/plagiarism_check.py proposal.md --internal --strict
python3 scripts/plagiarism_check.py proposal.md --sumber .cache_ekstrak/ \
    --md plagiarism_report.md --json plagiarism_report.json
python3 scripts/proposal_doctor.py proposal.md \
    --dataset data/responden.csv --hasil-uji hasil_uji.json --docx proposal.docx --strict

# 7b. Layered QC Lapis 1-4 (manual/agen - baca references/quality-gates.md Bagian B)
#   Lapis 1 Humanizer  -> checklists/humanizer_checklist.md
#   Lapis 2 Mekanis/EYD -> checklists/eyd_check.md  (sudah di atas)
#   Lapis 3 Semantik   -> Gate 6 + Gate 4-Kualitatif
#   Lapis 4 Red-team   -> 9 pertanyaan + rubrik (skor >=75, tanpa aspek bernilai 0)

# 8. Konversi naskah ke DOCX
scripts/build_docx.sh proposal_skripsi.md --out-dir . --title "Judul" --toc --clean
```

## Struktur Repo

```text
proposal-skripsi/
├── SKILL.md                             # Pintu masuk & orchestrator
├── references/
│   ├── data-sources.md                  # Klasifikasi & ekstraksi file lokal
│   ├── problem-formulation.md           # Gap (TAS), rumusan masalah, tujuan, hipotesis
│   ├── methodology.md                   # Desain, sampling, instrumen, uji asumsi, etika
│   ├── qualitative-analysis.md          # Jalur kualitatif: desain, pengodean, mutu, batasan
│   ├── dataset-analysis.md              # Profil dataset & pemilihan uji statistik
│   ├── online-search.md                 # Pencarian online pelengkap (OpenAlex/S2)
│   ├── document-assembly.md             # Struktur BAB, gaya bahasa Indonesia, kerangka berpikir
│   ├── citation-styles.md               # Daftar pustaka (APA 7/Chicago/Harvard/Vancouver/IEEE)
│   ├── paper-review-integration.md      # Alih matriks paper-review -> BAB II -> ekspor sitasi
│   ├── quality-gates.md                 # Gate per tahap + Layered QC Lapis 1-4 + rubrik
│   ├── revision-guide.md                # Humanizer: 25 pola gaya khas AI (Lapis 1)
│   ├── eyd-check.md                     # EYD V + KBBI: ejaan, tanda baca, kapitalisasi
│   └── plagiarism-check.md              # 5 tipe plagiarisme, deteksi lokal, ambang similarity
├── checklists/
│   ├── humanizer_checklist.md           # Pelacak Lapis 1
│   ├── eyd_check.md                     # Pelacak Lapis 2
│   └── plagiarism_check.md              # Pelacak Lapis 2-3
├── templates/
│   ├── proposal_template.md             # Template dokumen penuh (judul -> BAB I-III)
│   ├── bab1_pendahuluan.md
│   ├── bab2_tinjauan_pustaka.md
│   ├── bab3_metode.md
│   ├── tabel_uji_statistik.md           # Pemetaan hipotesis -> uji
│   ├── pedoman_wawancara.md             # Instrumen wawancara (Lampiran)
│   └── informed_consent.md              # Lembar persetujuan & kerahasiaan
├── campus_templates/                    # Preset pedoman kampus (28 JSON)
│   ├── generic.json  ugm.json  ui.json  uny.json  itb.json  custom.json
│   ├── ipb.json  unair.json  ub.json  its.json  undip.json  unpad.json
│   ├── unhas.json  telu.json  binus.json  umy.json  uii.json  uad.json
│   ├── ums.json  udinus.json  umm.json  umb.json  gunadarma.json
│   └── upn_veteran.json  upnvj.json  upnv_jatim.json  budi_luhur.json  umn.json
├── scripts/
│   ├── ingest_sources.sh                # Scan & ekstrak file lokal -> inventaris
│   ├── profile_dataset.py               # Profil CSV/XLSX/TSV/JSON + rekomendasi uji
│   ├── stats_tests.py                   # Uji statistik nyata -> hasil_uji.md/.json
│   ├── code_interview.py                # Koding transkrip -> tabel kode & cuplikan
│   ├── export_referensi.py              # Matriks -> BibTeX/RIS/EndNote XML/daftar pustaka
│   ├── id_language_check.py             # Bahasa Indonesia (baku, partikel, rumus kabur) + BAB I
│   ├── plagiarism_check.py              # Tumpang tindih teks: internal + vs folder sumber
│   ├── proposal_doctor.py               # Pemeriksaan akhir naskah (penanda, angka, DOCX)
│   ├── apply_campus_template.py         # Preset kampus: list/show/init/check/new-custom
│   ├── generate_campus_presets.py       # Generator preset (provenance wajib; --check/--patch)
│   └── build_docx.sh                    # Markdown -> DOCX (pandoc) + daftar isi
├── tests/
│   ├── run_tests.sh                     # 66 smoke test seluruh script
│   ├── sample_dataset.csv
│   ├── matriks_referensi_contoh.csv
│   ├── codebook_contoh.csv
│   ├── transkrip_contoh.md
│   ├── contoh_bab1.md
│   └── contoh_proposal_lengkap.md
└── README.md
```

## Menjalankan Test

```bash
bash tests/run_tests.sh
```

66 smoke test: inventaris, profil dataset, nilai kritis t/chi-square/F, uji statistik,
pemeriksa bahasa, pemeriksa plagiarisme, proposal doctor, build DOCX, preset kampus,
pengodean wawancara, ekspor referensi (termasuk validasi EndNote XML), provenance
28 preset kampus, dan konsistensi dokumentasi. Semua harus `PASS` sebelum commit.

## Prasyarat Opsional

| Tool | Kebutuhan | Instalasi |
|------|-----------|-----------|
| `pdftotext` (poppler) | ekstraksi teks PDF | `brew install poppler` |
| `pandoc` | ekspor DOCX | `brew install pandoc` |
| `openpyxl` | baca file `.xlsx` | `pip3 install openpyxl` |
| `scipy` / `statsmodels` | uji parametrik & model lebih lengkap | `pip3 install scipy statsmodels` |

Tanpa dependensi apa pun, skill tetap bisa berjalan: hanya membaca MD/TXT, hanya menulis
Markdown, `profile_dataset.py` memakai pendekatan skewness-kurtosis untuk normalitas, dan
`stats_tests.py` memakai perhitungan internal (t, F, chi-square, korelasi, regresi linear,
Cronbach's alpha) dengan incomplete beta/gamma untuk nilai p.

## Aturan Penting

1. **Output utama = proposal naratif lengkap (BAB I-III)**, bukan kerangka atau bullet.
2. **Jangan mengarang data** — angka dari `profile_dataset.py` atau perhitungan nyata; bila data
   belum dianalisis, tulis `(data belum dianalisis)`. Angka hasil uji disalin dari
   `hasil_uji.md`, bukan ditulis dari ingatan.
3. **Jangan mengarang literatur, penulis, atau DOI** — setiap `[L-n]` terverifikasi (DOI resolve
   atau file lokal dibaca). Sumber lokal tanpa DOI ditandai `(dokumen lokal)`.
4. **Jangan mengarang identitas** — NIM, fakultas, dosen, nama responden ditulis `[isi ...]`.
   Nama peserta kualitatif selalu disamarkan.
5. **Jangan mengarang kutipan** — verbatim harus benar-benar ada di transkrip; jumlah kutipan
   dihitung dari `code_interview.py`, bukan diperkirakan.
6. **Jenjang menentukan kedalaman** — S1 penerapan, S2 pengembangan kerangka, S3 kontribusi
   teoretis orisinal.
7. **Tujuan = 1:1 rumusan masalah.**
8. **Setiap klaim empiris ber-marker sumber** — `[L-n]`, `[D:kolom]`, `[K-n]`, `[U]`.
9. **Human-in-the-loop** — konfirmasi di awal dan sebelum export, tidak per-bagian.
10. **Simpan artefak sebagai file**, bukan hanya di chat.
11. **Jalankan gate otomatis sebelum ekspor** — `id_language_check.py`, `proposal_doctor.py`,
    `apply_campus_template.py check`. Kode keluar `1` berarti gate gagal.
12. **Pedoman kampus user mengalahkan preset skill** — preset hanya acuan.
13. **Kualitatif bukan kuantitatif tanpa angka** — tanpa rumus probabilistik, alpha, atau tabel
    hipotesis -> uji; tapi wajib ada pedoman wawancara, informed consent, dan alasan saturasi.
14. **Ejaan KBBI**, output selalu Bahasa Indonesia kecuali diminta lain.
15. **Humanizer boleh mengubah gaya, bukan fakta** — angka, kutipan asli, marker, rumusan
    masalah, tujuan, dan hipotesis tetap utuh setelah Lapis 1.
16. **Temuan plagiarisme adalah sinyal, bukan bukti** — yang diminta setiap temuan punya
    keputusan tercatat, bukan jumlah temuan nol.
17. **Naskah wajib melewati Layered QC Lapis 1-4** sebelum diserahkan. Gate per tahap yang
    lolos tidak berarti naskah layak diserahkan.

## Integrasi Skill

| Kebutuhan | Skill |
|------------|-------|
| Tabel review literatur lengkap (12 kolom, provenance, ekspor CSV/XLSX/BIB/RIS) | `paper-review` |
| Protocol penulisan paper jurnal (English) | `academic-writing` |
| Slide defence atau sidang | `pptx` |
| **Proposal skripsi/tesis/disertasi (Bahasa Indonesia)** | **`proposal-skripsi`** |

## Atribusi

Struktur pipeline dan protokol anti-hallucination mengikuti **bimajanuri/academic-writing-skill**
dan **bimajanuri/paper-review-skill**. Kerangka proposal (rumusan masalah -> tujuan -> metode ->
manfaat), metode gap **TAS/Berwald-Daellenbach**, dan pola "sintesis literatur -> kerangka
berpikir" mengikuti praktik metodologi penelitian standar. Rujukan metodologis yang
direferensikan tanpa mengutip teks: **Creswell & Creswell** (desain mixed-methods), **Field**
(analisis statistik), **Kumar** (penelitian tindakan dan R&D), **Sugiyono** (desain dan statistik
Indonesia), **Braun & Clarke** (analisis tematik), **Miles, Huberman & Saldaña** (kualitatif),
**Kline** (multikolinearitas), **Cochran** dan **Krejcie & Morgan** (penentuan sampel).

## Lisensi

Rilis di bawah **[MIT License](LICENSE)**.
