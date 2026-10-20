# BAB II — KAJIAN PUSTAKA

Template terperinci untuk BAB II. Bab ini **membangun sintesis**, bukan menyalin ringkasan
research satu per satu. Gunakan bersama `references/document-assembly.md`.

## 2.1 Landasan Teori

### Struktur tiap sub-bab teori

1. **Definisi** teori dengan rujukan asalnya `[L-n]`
2. **Konstruk kunci** — apa yang diklaim teori, dengan terminologi aslinya (italic)
3. **Hubungan dengan variabel penelitian** — bagaimana teori menjelaskan mekanisme yang diteliti
4. **Alasan pemilihan** — kenapa teori ini, bukan yang lain

### Jumlah teori

| Jenjang | Teori utama | Teori pendukung |
|---------|-------------|-----------------|
| Skripsi | 1-2 | 0-1 |
| Thesis | 2-3 | 1-2 |
| Disertasi | 3-4 | 2-3 |

### Tabel pembanding teori (wajib untuk S2/S3)

| Aspek | Teori A [L-n] | Teori B [L-n] | Teori C [L-n] |
|-------|---------------|---------------|---------------|
| Pengusul | … | … | … |
| Fokus | … | … | … |
| Konsep kunci | … | … | … |
| Keterbatasan | … | … | … |
| Alasan dipakai | … | … | … |

## 2.2 Kajian Terdahulu

### Bentuk yang diterima

**A. Tabel kajian terdahulu** (wajib ada, 5-10 baris, kolom ringkas):

| No | Penulis (Tahun) | Populasi/Sampel | Metode | Temuan | Keterbatasan |
|----|-----------------|------------------|--------|--------|--------------|
| 1 | … [L-1] | … | … | … | … |

Kolom Don't exceed 6-7 (batas lebar A4). Detail lengkap per-paper butuh skill `paper-review`.

**B. Sintesis naratif** (wajib setelah tabel): bukan ringkasan per research, tapi:

```text
Paragraf 1: POLA — apa yang konsisten ditemukan (3-4 penelitian menunjukkan …) [L-1][L-2][L-3]
Paragraf 2: PERBEDAAN — di mana hasil berbeda dan mengapa (mis. perbedaan lokasi/sampel) [L-4][L-5]
Paragraf 3: KELEMAHAN METODE — pola keterbatasan (mis. semua cross-sectional) [L-1][L-6]
Paragraf 4: GAP — apa yang belum dijelaskan oleh semua studi tersebut + posisi penelitian ini
```

**Dilarang** menulis kajian terdahulu sebagai daftar ringkasan satu paragraf per penelitian tanpa
sintesis. Itulah yang membuat proposal terbaca seperti daftar anotasi.

## 2.3 Hubungan Antar Variabel

Untuk tiap variabel independen, uraikan mekanismenya: bagaimana variabel itu memengaruhi variabel
dependen, lewat mekanisme apa, dan mengapa mekanisme tersebut bekerja (rujukan `[L-n]`).

Contoh alur: stimulus (X1) → proses psikologis (motivasi sebagai mediator) → respons (Y).
Terminologi teori wajib italic pada penyebutan pertama.

## 2.4 Kerangka Berpikir

Wajib ada. Tutup denganstatement hipotesis yang akan diuji.

### Format A — diagram ASCII (Markdown)

```text
        [Teori Utama: … [L-n]]
                    |
        +-----------+-----------+
        |           |           |
       X1          X2          X3
        |           |           |
        +-----------+-----------+
                    |
                    v
             Y: Kinerja [L-n]
                    |
                    v
      [Rumusan Masalah & Hipotesis H01-H03]
```

### Format B — tabel + narasi (paling aman untuk DOCX)

| Variabel | Indikator | Dasar Teori | Arah Hubungan | Hipotesis |
|----------|-----------|-------------|---------------|-----------|
| X1 | 4 butir, Skor 1-5 | Vroom [L-2] | positif | H01: pengaruh positif |
| Y | 4 butir, Skor 1-5 | Path Goal [L-3] | - | - |

### Format C — narasi (3-5 paragraf)

Teori → mekanisme → indikator terukur → hipotesis → uji statistik yang disiapkan.

### Tambahan per jenjang

- **S1**: hubungan straight forward, tanpa moderator/mediator.
- **S2**: tambahkan justifikasi variabel moderasi/mediasi bila ada.
- **S3**: model konseptual orisinal + alasan teoretis komponenny + pembeda dari model sebelumnya.

## 2.5 Hipotesis (bila pedoman kampus menempatkan di BAB II)

Bila pedoman kampus menaruh hipotesis di BAB II, pindahkan bagian 1.7 ke sini, dan sediakan rujukan
silang di BAB I ("hipotesis diuraikan pada Bab II"). Jangan duplikasi.

---

## Checklist Kualitas BAB II

- [ ] Semua teori terdefinisi dengan sumber `[L-n]`
- [ ] Tinjauan pustaka Evidence + Synthesis + Gap, bukan Annotated Bibliography
- [ ] Tabel kajian terdahulu ada dan punya kolom keterbatasan
- [ ] Hubungan antar variabel dijelaskan lewat mekanisme
- [ ] Kerangka berpikir ada (diagram atau tabel) dan habis dengan hipotesis
- [ ] Jumlah teori sesuai jenjang
- [ ] Tidak ada kalimat yang menyalin sumber secara verbatim
