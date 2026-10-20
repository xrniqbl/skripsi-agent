# Methodology — Rancangan Metode Penelitian (BAB III)

Pandu **STEP 4**. Bab metode adalah bab yang paling sering dipertanyakan pembimbing. Dua aturan
besar: **setiap elemen desain wajib disertai alasan**, dan **setiap angka harus berasal dari data
nyata**.

## 1. Memilih Desain Penelitian

| Desain | Tepat ketika | Elemen wajib | Jumlah RM |
|--------|-------------|--------------|-----------|
| Kuantitatif eksplanatif | Ada hipotesis pengaruh antar variabel | landasan teori, uji asumsi, uji hipotesis | 3-4 |
| Kuantitatif deskriptif | Ingin menggambarkan fenomena/frekuensi | teknik sampling, uji perbedaan bila perlu | 2-3 |
| Kualitatif eksploratif | Fenomena baru, teori masih tipis | sampling purposive, pedoman wawancara, analisis tematik | 3-4 |
| Kualitatif deskriptif | Ingin menggambarkan pengalaman/perspektif | sama, plus kriteria saturasi | 2-3 |
| Studi kasus | Sistem terbatas, kasus unik/kompleks | batas kasus (waktu/tempat/entitas), sumber evidensi | 3-4 |
| Mixed-methods | Butuh kuantitatif dan kualitatif | desain mixed eksplisit, integrasi data | 4-5 |
| R&D (research and development) | Menghasilkan produk/prototipe | analisis kebutuhan, validasi ahli, uji coba | 3-4 |
| Penelitian tindakan (action research) | Perbaikan praktik di lapangan | siklus plan-act-observe-reflect | 3-4 |
| Eksperimen / quasi-eksperimen | Uji sebab-akibat kuat | penrandoman atau penetapan kelompok kontrol | 3 |

Untuk setiap desain, tulis tiga hal: **apa** yang diteliti, **mengapa** desain ini cocok `[L-n]`,
dan **apa** batasannya. Bab metode tanpa alasan hanya akan dianggap metode seadanya.

## 2. Pendekatan Kuantitatif (struktur lengkap)

Urutan sub-bab yang lazim:

1. Pendekatan dan desain, disertai alasan pemilihan.
2. Populasi dan sampel, termasuk penentuan jumlah sampel.
3. Lokasi dan waktu penelitian.
4. Instrumen, termasuk uji validitas dan reliabilitas.
5. Teknik pengumpulan data, diuraikan alurnya.
6. Teknik analisis, satu sub-bab per hipotesis, plus uji asumsi.
7. Alternatif bila uji asumsi gagal.
8. Etika dan izin penelitian.

## 3. Teknik Sampling dan Penentuan Sampel

| Teknik | Situasi | Penentuan n |
|--------|---------|--------------|
| Acak sederhana (SRS) | Populasi homogen, ada sampling frame lengkap | Cochran atau Cochran dengan koreksi populasi hingga |
| Proporsional | Sub-populasi tidak seimbang | n_i = (N_i/N) x n |
| Stratified | Ada strata penting, misalnya fakultas atau jabatan | n_i proporsional atau disproportionate |
| Purposive / judgment | Sampel kecil, penelitian kualitatif | saturasi data, disertai justifikasi |
| Sistematis (SPSS/Excel) | Populasi besar, sampling frame berupa daftar | Cochran dengan koreksi populasi hingga |
| Snowball | Jaringan, sulit menjangkau sub-populasi | bertambah sampai saturasi |
| Kuota | Ada kuota per kelompok | kuota per kelompok disebut eksplisit |

Rumus yang sering dipakai (cantumkan di proposal bila dipakai):

```text
n0 = (Z * p * q) / e^2                  Cochran; Z = 1,96; p = q = 0,5; e = 0,05 -> n0 = 96,04
n  = n0 / (1 + (n0 - 1) * r)            koreksi populasi hingga, r = N/n0
n  = N * X / (1 + (N - 1) * X)          Krejcie & Morgan; X = 3,00 (S1), 3,30 (S2), 3,46 (S3)
```

Jangan menampilkan rumus lalu tidak memakai hasilnya. Tampilkan hitungan singkatnya, misalnya:
"Dengan N = 480 dan e = 5 persen, diperoleh n = 97" `[D]`.

## 4. Instrumen serta Uji Validitas dan Reliabilitas

| Aspek | Prosedur yang perlu ditulis |
|-------|-----------------------------|
| Asal butir | Dikembangkan sendiri (mengapa) atau diadaptasi dari `[L-n]` (dengan penyesuaian apa) |
| Skala | Likert 1-5, Likert 1-7, atau semantik diferensial; bila memilih 1-5, tulis alasannya |
| Validitas isi | Penilaian tiga expert, face validity |
| Validitas konstruk | CFA: CFI dan TLI di atas 0,90, RMSEA di bawah 0,08; atau KMO dan Bartlett |
| Reliabilitas | Cronbach's alpha per variabel; alpha di atas 0,70 acceptable, di atas 0,80 baik |
| Perbaikan butir | Bila satu butir dihapus, jelaskan bahwa alpha meningkat setelah butir tersebut dibuang |

Bila data sudah tersedia dan kolom kuesioner terdeteksi sebagai skala Likert, script
`profile_dataset.py` menghitung Cronbach's alpha secara otomatis. Pakai angka itu dan beri marker
`[D:...]`, jangan mengarang nilai alpha.

## 5. Teknik Analisis dan Uji Asumsi

### 5.1 Uji asumsi (didahulukan pada setiap uji hipotesis)

| Asumsi | Cara uji | Kriteria | Jika gagal |
|--------|----------|----------|------------|
| Normalitas | Shapiro-Wilk (n 50 atau kurang), Kolmogorov-Smirnov (n di atas 50), skewness | p di atas 0,05 dan skew -2 sampai +2 | uji non-parametrik atau robust |
| Homoskedastisitas | Levene, plot residual versus prediksi | p di atas 0,05 | regresi heteroskedastis dengan standard error robust |
| Autokorelasi (time-series) | Durbin-Watson | mendekati 2 | model ARIMA atau GLS |
| Multikolinearitas | VIF dan toleransi | VIF di bawah 5 | Kalsifikasi atau transformasi variabel |
| Linearitas (regresi) | Uji linearitas, grafik | titik mendekati garis lurus | transformasi atau polinomial |
| Normalitas residual (regresi) | histogram residual, PP plot | residual mendekati normal | robust regression |
| Validitas model struktural (SEM) | loading di atas 0,7, CFI, TLI, AVE, CR, discriminant validity | sesuai ambang | revisi model |

### 5.2 Pemetaan hipotesis ke teknik analisis

| Hipotesis | Data | Uji parametrik | Alternatif non-parametrik |
|-----------|------|----------------|---------------------------|
| Dua kelompok, satu variabel, pre dan post | 1 DV numerik | paired t-test | Wilcoxon signed-rank |
| Dua kelompok independen, satu variabel | 1 DV numerik | independent t-test | Mann-Whitney U |
| Tiga kelompok atau lebih, satu variabel | 1 DV numerik | one-way ANOVA | Kruskal-Wallis |
| Satu DV numerik, dua prediktor atau lebih | DV dan IV kontinu | regresi linear berganda | regresi robust |
| Hubungan dua variabel | 2 variabel numerik | Pearson r | Spearman rho |
| Prediksi multivariat laten | Multi-variabel laten | SEM atau PLS-SEM | - |
| Satu variabel, satu DV kategorik | 1 DV kategorik | chi-square | Fisher exact |
| Dua variabel kategorik | Tabel silang | chi-square | - |
| Antes-after dengan kelompok kontrol | 2 kelompok, 2 waktu | ANCOVA | - |

Nama uji harus cocok dengan jenis data nyata. Kesalahan yang sering ditolak pembimbing:
menyebut regresi padahal variabel dependennya kategorik, atau memakai Mann-Whitney dengan n = 5.

## 6. Pendekatan Kualitatif (struktur lengkap)

| Elemen | Isi |
|--------|-----|
| Paradigma | post-positivis, konstruktivis, kritis, atau pragmatis, disertai alasan |
| Pendekatan | fenomenologi, studi kasus, etnografi, grounded theory, content analysis, analisis kebijakan |
| Desain | deskriptif, eksploratif, atau kontekstual |
| Partisipan | purposive atau snowball, kriteria inklusi-eksklusi, jumlah partisipan |
| Saturasi | kriteria berhenti, yaitu tidak ditemukannya tema baru setelah N partisipan tambahan `[L-n]` |
| Pengumpulan data | wawancara mendalam semi-terstruktur, FGD, observasi partisipan, studi dokumen, catatan lapangan |
| Alat | pedoman wawancara, lembar observasi, panduan FGD, alat rekam dengan izin |
| Analisis | Miles-Huberman-Saldana (reduksi-display-verifikasi), coding BCA, atau tematik Braun-Clarke |
| Software | NVivo 14, ATLAS.ti, atau MAXQDA (bila dipakai) |
| Kualitas data | triangulasi sumber dan metode, member checking, audit trail, refleksi peneliti |

> Load `references/qualitative-analysis.md` untuk detail: pemilihan desain, etika tiap
> teknik pengumpulan data, tahapan analisis, kriteria saturasi, dan batasan yang jujur.
> Instrumen: `templates/pedoman_wawancara.md` + `templates/informed_consent.md`.
> Pengodean transkrip: `scripts/code_interview.py`. Gate: Gate 4-Kualitatif di
> `references/quality-gates.md`.

## 7. Mixed-Methods (Creswell)

Isi eksplisit:

1. Desain mixed: convergent parallel, sequential explanatory (kuantitatif lalu kualitatif), atau
   sequential exploratory (kualitatif lalu kuantitatif).
2. Integrasi: tabel perbandingan data kuantitatif dan kualitatif, atau joint display.
3. Prioritas: kuantitatif dominan (EXPLAN) atau kualitatif dominan (EXPLORE).
4. Alasan pemilihan desain tersebut, lihat `[L-n]`.

## 8. Etika Penelitian

Isi minimal, wajib di semua jenjang:

- Persetujuan etik dari komite etik atau MEMS, dengan nomor dan tanggal, atau rencana pengajuan.
- Informed consent berupa lembar persetujuan, termasuk hak mundur dan anonimitas.
- Anonymity dan confidentiality: kode responden (R01, R02), tanpa identitas di laporan.
- Izin penelitian dari institusi, pemilik data, dan-SQL izin yang relevan.
- Pengelolaan data: penyimpanan aman, akses terbatas, dan retensi.
- Pengpieracaan bias: nonresponse bias, social desirability bias, dan bias khas data sensitif.

Data pribadi yang tidak dianonimkan merupakan pelanggaran etika. Jangan masukkan nama atau NIK
responden ke naskah proposal.

## 9. Batasan Rancangan (wajib untuk S2 dan S3)

Setiap desain memiliki batasan. Tulis dalam bentuk tabel batasan dan mitigasi.

| Batasan | Mitigasi |
|---------|----------|
| Self-report bias pada kuesioner | Triangulasi observasi atau wawancara, uji reliabilitas |
| Nonresponse bias | Perpanjang waktu pengumpulan, gunakan follow-up |
| Desain cross-sectional tidak dapat membuktikan kausalitas | Paparkan sebagai limitasi, hindari klaim kausal |
| Satu lokasi atau satu situs | Multi-situs untuk S2 dan S3 |
| Satu titik waktu (single time-point) | Studi longitudinal untuk S2 dan S3 |
| Teori X hanya menguji satu jalur | Uji moderasi atau mediasi untuk S2 dan S3 |
| Instrumen bahasa Inggris tanpa adaptasi | Terjemahkan dan uji validitas konten |
