# BAB I — PENDAHULUAN

Template terperinci untuk BAB I. Gunakan bersama `references/problem-formulation.md`.

## 1.1 Latar Belakang Masalah

**Alur wajib (5-7 paragraf):**

| Paragraf | Isi | Sumber |
|----------|-----|--------|
| 1-2 | Fenomena nyata di lapangan/lokal, digambarkan dengan data konkret | `[D:kolom]` atau `[U]` |
| 3 | Mengapa fenomena ini penting (dampak ekonomi, sosial, akademik) | `[L-n]` |
| 4 | Apa yang sudah diketahui dari penelitian terdahulu (sintesis singkat) | `[L-n]` |
| 5 | Apa yang **tidak** diketahui (gap), dan mengapa itu penting | TAS |
| 6 | Risiko jika masalah ini tidak diteliti | `(inferensi)` |
| 7 | Posisi penelitian ini (apa yang akan dikontribusikan) | pernyataan positioning |

**Kalimat pembuka yang efektif:**

```text
[Instansi/tempat] menghadapi Ordinates [deskripsi masalah]. Data pada [D:kolom] menunjukkan
bahwa [angka], yang [makna]. Fenomena ini [dampak bagiwho].
```

**Penandaan (wajib):**

- Angka dari dataset → `[D:kolom]`
- Klaim dari penelitian terdahulu → `[L-n]`
- Konteks dari user → `[U]`
- Penalaran agent → `(inferensi)`

## 1.2 Rumusan Masalah

Format: kalimat tanya, spesifik, dapat diuji.

| Jenjang | Jumlah | Pola |
|---------|--------|------|
| Skripsi | 3-4 | umum → mekanis → operasional |
| Thesis | 4-5 | konseptual/teori → konteks → mekanisme |
| Disertasi | 5-6 | tingkat teori + tingkat implementasi |

Checklist:

- [ ] Semua pertanyaan bisa dijawab dengan data yang tersedia di folder
- [ ] Hierarkis (tanya umum dijawab lebih dulu)
- [ ] Tidak ada pertanyaan yang bisa dijawab hanya dengan membaca literature review
- [ ] Tidak ada pertanyaan yang terlalu luas

## 1.3 Tujuan Penelitian

Aturan **1:1** dengan rumusan masalah, urutan sama, satu kalimat per tujuan.
Kata kerja: menguji, mendeskripsikan, menganalisis, membandingkan, merumuskan.

## 1.4 Manfaat Penelitian

1. **Teoritis** — tambah bukti empiris / uji model / kembangkan teori.
2. **Praktis** — spesifik pada pihak yang akan memakai (pengelola, policymaker, praktisi).
3. **(S2/S3)** Bagi peneliti lanjutan — data, instrumen, atau model.
4. **(S3)** Statement of contribution.

## 1.5 Ruangan Lingkup Penelitian

Enam batas wajib: lokasi, waktu, populasi dan sampel, variabel, data, teknik analisis.
Tabel: `templates/proposal_template.md` bagian 1.5. Jangan menulis "ruang lingkupnya luas".

## 1.6 Definisi Operasional

Dua lapis per variabel: konseptual (dari `[L-n]`) dan operasional (dari `[D:kolom]`).
Bila dataset ada, nama kolom CSV menjadi indikator yang konkret.

## 1.7 Hipotesis (kuantitatif)

Satu hipotesis per uji statistik. H₀ dan H₁, arah mengikuti teori. Pemetaan ke BAB III
lewat `templates/tabel_uji_statistik.md`.

## 1.8 Definisi Istilah

Hanya istilah kunci yang ambigu. 3-7 istilah. Gunakan definisi operasional, bukan definisi kamus.

---

## Checklist Kualitas BAB I

- [ ] Latar belakang 5-7 paragraf dengan alur jelas dan marker di setiap klaim
- [ ] Rumusan masalah 3-5 butir, hierarkis
- [ ] Tujuan 1:1 dengan rumusan
- [ ] Manfaat spesifik
- [ ] Ruang lingkup 6 batas terisi
- [ ] Definisi operasional untuk setiap variabel
- [ ] Hipotesis sesuai teknik analisis BAB III
- [ ] Definisi istilah cukup
