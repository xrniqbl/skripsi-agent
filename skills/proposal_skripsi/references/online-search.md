# Online Search — Pencarian Literatur Pelengkap (Opsional)

Pandu **STEP 2.2**. Sumber utama proposal ini adalah **file lokal**. Pencarian internet hanya
dipakai bila folder minim literatur, gap belum tertutup, atau user memintanya.

> Untuk tabel review literatur yang lengkap (12 kolom, provenance, ekspor CSV/XLSX/BIB/RIS),
> jangan kerjakan di sini. Gunakan **skill `paper-review`**. File ini hanya untuk pencarian
> minimal yang menjadi bahan argumen gap.

## 1. Kapan Mengaktifkan

| Situasi | Tindakan |
|---------|----------|
| Literatur lokal 10 paper atau lebih, gap jelas | Jangan search. Lanjut tulis. |
| Literatur lokal kurang dari 10 paper | Search 5-10 paper terkuat untuk menutup gap |
| User minta "tambah penelitian terdahulu" | Search, masukkan ke matriks evidence sebagai `[L-n]` baru |
| Topik terlalu baru, literatur lokal tidak ada | Search lebih dulu sebagai basis BAB II |
| User secara eksplisit meminta | - |

## 2. Kata Kunci

Bangun dari tiga sumber:

1. Istilah kunci dari **rumusan masalah** user.
2. Istilah dari **nama kolom dataset** bila ada (istilahoperasional penelitian).
3. Sinonim dan varyasi ejaan (bahasa Indonesia dan Inggris).

Contoh: `motivasi kerja` → `motivasi`, `motivasi kerja`, `work motivation`, `job motivation`,
`intrinsic motivation`, `self-determination theory`, `Vroom expectancy theory`.

## 3. Sumber Pencarian (Gratis)

| Sumber | Kegunaan | Catatan |
|--------|----------|---------|
| OpenAlex API | Pencarian utama + metadata + abstract | Gratis, tanpa kunci API |
| Semantic Scholar | Ringkasan & sitasi | Ada rate limit |
| arXiv | Preprint, khusus STEM | Bukan peer-reviewed, catat di matriks |
| Google Scholar | Pencarian manual | Jangan otomatisasi scraping |
| Repositori lokal (UGM, UI, Uny, Repository Institusi) | Skripsi/tesis Indonesia | Konteks lokal sangat berharga |

Contoh (OpenAlex, tanpa API key):

```bash
curl -s "https://api.openalex.org/works?search=motivasi%20kinerja%20karyawan&per-page=10&mailto=email@contoh.id"
```

## 4. Kurasi (Wajib)

1. Ambil 1,5 kali jumlah target, skor relevansi 0-10 dari judul dan abstract.
2. Ambil hanya yang relevansi 7 atau lebih.
3. Setiap paper **wajib** punya DOI yang dapat di-resolve, atau file lokal yang dibaca.
4. DOI gagal resolve → tandai `UNVERIFIED` di matriks.
5. **Jangan** memasukkan paper yang hanya disebut nama penulisnya di review lain tanpa pernah dibaca.

## 5. Aturan Prioritas Literatur

Bila ada pilihan antara literatur lokal dan online untuk hal yang sama:

- **Literatur lokal** diutamakan untuk BAB II, karena kontekstual (lokal, bidang yang sama, aturan
  kampus).
- **Online** dipakai untuk mengisi celah konseptual/teori yang memang belum ada di folder.
- **Skripsi/tesis lokal** boleh dipakai sebagai landasan metode pada konteks Indonesia, tapi
  hindari menumpukProposal yang isinya hanya mengulang skripsi lain (risiko plagiarism tinggi).

## 6. Menulis ke Matriks Evidence

Setiap paper baru yang dipakai harus:

1. Masuk `sumber_inventaris.json` sebagai kategori literatur dengan marker baru (`[L-7]`, dst).
2. Masuk satu baris di `matriks_evidence.md`.
3. Dikutip minimal sekali di BAB I atau BAB II.
4. Masuk daftar pustaka dengan format yang benar.
5. Direkam kata kunci dan tanggal pencarian di `catatan_gap.md` (agar reproducible).

## 7. Pencatatan (Reproducibility)

Tambahkan di akhir `catatan_gap.md`:

```text
Tercatat   : 2026-03-01
Sumber     : OpenAlex, Semantic Scholar, repositori lokal
Kata kunci : motivasi kerja, work motivation, employee motivation, SDT, expectancy theory
Dipakai    : L-1, L-2, L-5
Ditolak    : 3 paper (relevansi di bawah 7), 1 paper (DOI tidak resolve)
```
