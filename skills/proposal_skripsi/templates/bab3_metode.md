# BAB III — METODE PENELITIAN

Template terperinci untuk BAB III. Gunakan bersama `references/methodology.md` dan
`references/dataset-analysis.md`.

## Aturan Umum

1. **Setiap elemen desain disertai alasan** ("dipilih karena …").
2. **Semua angka dari `profil_dataset.md`** (bila dataset ada). Dilarang mengarang.
3. Satu sub-bab per hipotesis bila metode kuantitatif.
4. Uji asumsi ditulis eksplisit, bukan diasumsikan.
5. Etika penelitian tidak boleh dilewati.

## 3.1 Pendekatan dan Desain Penelitian

Isi:

- Pendekatan (kuantitatif/kualitatif/mixed) + alasan
- Desain (eksplanatif/deskriptif/eksploratif/studi kasus/R&D/eksperimen) + alasan `[L-n]`
- Untuk mixed: desain mixed eksplisit (convergent/sequential, EXPLAN/EXPLORE)
- Untuk kualitatif: paradigma + pendekatan (fenomenologi, grounded theory, dll.)

Contoh kalimat:

> Penelitian ini menggunakan pendekatan kuantitatif dengan desain eksplanatif. Desain ini dipilih
> karena tujuan penelitian adalah menguji pengaruh variabel X terhadap Y, bukan hanya menggambarkan
> fenomena. Pendekatan eksplanatif dipilih merujuk Creswell dan Creswell (2018) [L-1] yang
> menyatakan bahwa desain eksplanatif tepat untuk menguji hubungan sebab-akibat antar variabel.

## 3.2 Populasi dan Sampel

| Elemen | Isi |
|--------|-----|
| Populasi | siapa, berapa (N), batas |
| Teknik sampling | nama teknik + alasan |
| Jumlah sampel | n + rumus + hitungan singkat |
| Kriteria inklusi | 3-5 butir |
| Kriteria eksklusi | 2-4 butir |

Contoh hitungan (boleh ditulis apa adanya):

```text
Dengan Cochran (Z = 1,96; p = q = 0,5; e = 0,05) diperoleh n0 = 96,04. Dengan N = 480,
koreksi populasi hingga menghasilkan n = 88. Jumlah ini telah melebihi ketentuan minimum
Krejcie dan Morgan untuk jenjang S1 (n = 34) [D].
```

## 3.3 Lokasi dan Waktu Penelitian

- Lokasi: nama tempat + alasan pemilihan +Deskripsi singkat (profil lokasi, jumlah populasi)
- Waktu: tanggal mulai dan selesai + alasan

## 3.4 Instrumen Penelitian

Isi berurutan:

1. **Asal butir** — dikembangkan sendiri (alasannya) atau diadaptasi dari `[L-n]`
2. **Skala** — Likert 1-5 / 1-7, dengan alasan
3. **Kisi-kisi instrumen** — tabel indikator per variabel
4. **Uji validitas** — CFA (CFI, TLI, RMSEA) atau content validity oleh expert
5. **Uji reliabilitas** — Cronbach's alpha, dengan nilai dari data awal bila ada `[D]`

Bila data sudah ada dan skala terdeteksi, ambil angka alpha langsung dari `profil_dataset.md`.

## 3.5 Teknik Pengumpulan Data

| Teknik | Uraikan |
|--------|---------|
| Kuesioner | media (Google Form/print), cara pengisian, durasi,pemeriksaan kelengkapan |
| Observasi | apa yang diamati, siapa, kapan |
| Wawancara | jumlah, durasi, pencatatan, alat rekam |
| Dokumentasi | dokumen yang dikumpulkan |

Tambahkan langkah (_field work_) ringkas: urutan kegiatan, durasi, siapa yang butuh izin.

## 3.6 Teknik Analisis Data

### 3.6.1 Uji Asumsi

Tulis tiap uji asumsi yang relevan beserta hasilnya dari data awal (bila ada):

```text
Uji normalitas dengan Shapiro-Wilk pada kolom Skor_Kinerja menghasilkan p = 0,214 (> 0,05),
sehingga distribusi dianggap normal. Kolom Skor_Stress memiliki skewness 2,31 sehingga
dianggap tidak normal [D]. Uji homoskedastisitas dengan Levene pada kolom Skor_Kinerja
menghasilkan p = 0,412 (> 0,05). Multikolinearitas diperiksa dengan VIF; nilai tertinggi
adalah 1,87 (< 5) [D].
```

Bila asumsi gagal → **tulis uji alternatifnya** beserta alasannya. Jangan hanya menyebut asumsi
lalu mengabaikan hasilnya.

### 3.6.2 Analisis Hipotesis

Satu sub-bab (atau paragraf bernomor) per hipotesis, dengan urutan:

1. Menyebut hipotesis H₀ dan H₁
2. Menyebut kolom data yang digunakan `[D:kolom]`
3. Menyebut uji yang dipakai + alasan
4. Menyebut kriteria keputusan (α = 0,05)
5. (Bila data awal sudah ada) Menyebut hasil uji dan interpretasinya

Tabel pemetaan lengkap: `templates/tabel_uji_statistik.md`.

### 3.6.3 Software

Sebutkan nama dan versi: SPSS 26, R 4.3, Python 3.12, SmartPLS 4, AMOS 26, NVivo 14. Bila
digunakan, jelaskan alasan memilih software tersebut.

## 3.7 Aspek Etika Penelitian

- Persetujuan etik: nomor dan tanggal, atau rencana pengajuan MEMS
- Informed consent: isi lembar, cara menyampaikan
- Anonymity dan confidentiality: kode responden
- Izin: institusi, pemilik data, izin lain
- Pengelolaan data: penyimpanan, akses, retensi
- Mitigasi bias: nonresponse, social desirability, bias data sensitif

## 3.8 Batasan Rancangan *(wajib S2/S3)*

Tabel batasan dan mitigasi (lihat `references/methodology.md` §9).

---

## Checklist Kualitas BAB III

- [ ] Desain + alasan tertulis
- [ ] Populasi, sampling, n, inklusi-eksklusi lengkap
- [ ] Instrumen ber-asal butir jelas, uji validitas dan reliabilitas direncanakan
- [ ] Setiap hipotesis punya satu uji yang cocok dengan data
- [ ] Uji asumsi ditulis, termasuk hasilnya bila data tersedia
- [ ] Semua angka berasal dari `profil_dataset.md`
- [ ] Etika lengkap
- [ ] Batasan rancangan ada (S2/S3)
