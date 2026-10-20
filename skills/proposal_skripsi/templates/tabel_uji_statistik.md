# Tabel Uji Statistik — Pemetaan Rumusan Masalah, Hipotesis, dan Uji

Tempelkan tabel ini di **BAB III bagian 3.6**. Isi setiap baris dari
`references/dataset-analysis.md` dan `profil_dataset.md`.

## Tabel 1 — Pemetaan Rumusan Masalah ke Hipotesis dan Uji (kuantitatif)

| No | Rumusan Masalah | Hipotesis | Variabel / Kolom Data | Uji Statistik | Asumsi yang Diperiksa | Keterangan |
|----|-----------------|-----------|------------------------|---------------|------------------------|------------|
| RM-1 | Apakah terdapat pengaruh X1 terhadap Y? | H₀₁: tidak terdapat pengaruh X1 terhadap Y<br>H₁₁: terdapat pengaruh positif X1 terhadap Y | Y = `Skor_Kinerja`<br>X1 = `Skor_Motivasi` `[D:Skor_Motivasi]` | Uji t-related / regresi sederhana | Normalitas (Shapiro-Wilk), linearitas | α = 0,05 |
| RM-2 | Apakah terdapat pengaruh X2 terhadap Y? | H₀₂: tidak terdapat pengaruh X2 terhadap Y<br>H₁₂: terdapat pengaruh positif X2 terhadap Y | Y = `Skor_Kinerja`<br>X2 = `Skor_Kompetensi` `[D:Skor_Kompetensi]` | Regresi linear berganda | Normalitas residual, homoskedastisitas, multikolinearitas (VIF) | α = 0,05 |
| RM-3 | Apakah terdapat perbedaan kinerja antar divisi? | H₀₃: tidak terdapat perbedaan kinerja yang signifikan antar divisi<br>H₁₃: terdapat perbedaan | Y = `Skor_Kinerja`<br>Kelompok = `Divisi` `[D:Divisi]` | One-way ANOVA | Normalitas, Levene | α = 0,05; post hoc Tukey bila ANOVA signifikan |

> Bila data awal menunjukkan asumsi gagal (contoh: skewness 2,31 pada kolom stress), ganti
> Nama Uji dengan non-parametrik dan tulis alasannya:

| No | Rumusan Masalah | Hipotesis | Variabel / Kolom Data | Uji Alternatif | Alasan | Keterangan |
|----|-----------------|-----------|------------------------|----------------|--------|------------|
| RM-4 | Apakah terdapat perbedaan stress antar divisi? | H₀₄: tidak terdapat perbedaan stress antar divisi | `Skor_Stress`, `Divisi` | Kruskal-Wallis | skewness kolom `Skor_Stress` = 2,31 sehingga asumsi normalitas tidak terpenuhi `[D]` | α = 0,05 |

## Tabel 2 — Ringkasan Uji Asumsi

| Asumsi | Metode Uji | Kolom Diperiksa | Hasil | Keputusan |
|--------|------------|------------------|-------|------------|
| Normalitas | Shapiro-Wilk | `Skor_Kinerja` | p = 0,214 | Normal |
| Normalitas | Shapiro-Wilk | `Skor_Stress` | p = 0,004, skewness 2,31 | Tidak normal |
| Homoskedastisitas | Levene | `Skor_Kinerja` per `Divisi` | p = 0,412 | Homogen |
| Multikolinearitas | VIF | X1, X2, X3 | VIF tertinggi 1,87 | Tidak ada multikolinearitas |
| Linearitas | Grafik dan uji linearitas | X1 terhadap Y | titik-titik mendekati garis lurus | Terpenuhi |

## Tabel 3 — Ringkasan Instrumen (bila data awal tersedia)

| Variabel | Jumlah Butir | Skala | Mean | Std | Cronbach's Alpha | Validitas |
|----------|--------------|-------|------|-----|------------------|-----------|
| X1: Motivasi | 4 | 1-5 | 3,42 | 0,71 | 0,79 | CFI = 0,94; loading 0,71-0,83 |
| X2: Kompetensi | 5 | 1-5 | 3,65 | 0,68 | 0,76 | CFI = 0,91 |
| Y: Kinerja | 5 | 1-5 | 3,51 | 0,74 | 0,84 | CFI = 0,95 |

Sumber: hasil analisis data awal (2026) `[D]`.

## Tabel 4 — Karakteristik Responden (bila data awal tersedia)

| No | Karakteristik | Kategori | Frekuensi | Persentase |
|----|---------------|----------|-----------|------------|
| 1 | Jenis kelamin | Laki-laki | 58 | 47,5 |
| 2 | Jenis kelamin | Perempuan | 64 | 52,5 |
| 3 | Usia | 21-25 tahun | 72 | 59,0 |
| 4 | Masa kerja | 1-3 tahun | 65 | 53,3 |

Sumber: hasil analisis data penelitian (2026) `[D]`.

## Aturan Pengisian

1. **Jangan** mengisi tabel ini bila data belum ada; tulis "akan dilakukan setelah pengumpulan
   data" (data belum dianalisis).
2. Semua angka harus identik dengan `profil_dataset.md` atau dihitung ulang darinya.
3. Satu hipotesis = satu uji. Bila satu rumusan butuh dua uji, buat dua baris.
4. Nama kolom pada kolom "Variabel / Kolom Data" harus **sama persis** dengan nama kolom di file
   dataset, agar dapat ditelusuri.
5. Kriteria keputusan (α) ditulis konsisten di semua baris.
6. Tabel diberi nomor bab, judul di atas, sumber di bawah.
