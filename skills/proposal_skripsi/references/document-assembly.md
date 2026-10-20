# Document Assembly — Struktur BAB, Gaya Bahasa Indonesia, Tabel & Gambar

Pandu **STEP 5**.Bab ini menjelaskan cara merakit draf menjadi dokumen proposal yang layak
dibawa ke pembimbing.

## 1. Struktur Dokumen

```text
Halaman Judul
Daftar Isi
BAB I    PENDAHULUAN
  1.1  Latar Belakang Masalah
  1.2  Rumusan Masalah
  1.3  Tujuan Penelitian
  1.4  Manfaat Penelitian
  1.5  Ruangan Lingkup Penelitian
  1.6  Definisi Operasional
  1.7  Hipotesis (kuantitatif) atau Pertanyaan Penelitian (kualitatif)
  1.8  Definisi Istilah
BAB II   KAJIAN PUSTAKA
  2.1  Landasan Teori / Teori Utama
  2.2  Kajian Terdahulu (dalam matriks)
  2.3  Hubungan antar Variabel
  2.4  Kerangka Berpikir
  2.5  Hipotesis (alternatif penempatan, mengikuti pedoman kampus)
BAB III  METODE PENELITIAN
  3.1  Pendekatan dan Desain
  3.2  Populasi dan Sampel
  3.3  Lokasi dan Waktu
  3.4  Instrumen
  3.5  Teknik Pengumpulan Data
  3.6  Teknik Analisis Data (per hipotesis + uji asumsi)
  3.7  Aspek Etika Penelitian
Daftar Pustaka
Lampiran (kuesioner, pedoman wawancara, lembar persetujuan)
```

> Nomor bab, nama, dan urutan mengikuti **pedoman kampus** bila user menyediakannya.
> Jika tidak, pakai struktur di atas.

## 2. Aturan Alur Antar Sub-bab (Penting)

Proposal yang baik bersifat **kohesif**: setiap sub-bab menjawab pertanyaan dari sub-bab
sebelumnya dan memunculkan pertanyaan berikutnya.

Contoh alur BAB I yang benar:

```text
Latar belakang      ->rix why masalah ini penting dan nyata
Rumusan masalah      ->GY menanyakan apa yang perlu dijawab
Tujuan               ->RM-1 s.d. RM-4, dibuat 1:1 dengan rumusan
Manfaat              -> untuk siapa dan apa kontribusinya
Ruang lingkup        ->.01/:.02/:.03/:.04/:.05/:.06/:.06/:.06: batas penelitian
Definisi operasional -> member definisi variabel terukur
Hipotesis            ->:09: jawaban sementara yang akan diuji di BAB III
```

 abundantly Hindari: sub-bab yang bisa dipindah urutannya tanpa merusak argumen. Itu tanda
*naskah belum matang*.

## 3. Gaya Bahasa Indonesia Akademik

| Aspek | Aturan | Contoh benar | Contoh salah |
|-------|--------|--------------|--------------|
| Kalimat | Rata-rata 20-30 kata, satu gagasan | "Peningkatan beban kerja menurunkan kepatuhan pajak." | "Berdasarkan hasil penelitian terdahulu yang menunjukkan bahwa… ada… ada" |
| Kalimat pasif | Boleh untuk-Net wer emitter prosedural | "Data dikumpulkan dengan kuesioner." | "Kami akan mengumpulkan data…" (terlalu kasual) |
| Rujukan frasa | Ganti kata berulang dengan sinonim | utilisasi/manfaat/pemanfaatan | "manfaat" 12 kali berturut-turut |
| Penghinaan | Jangan gunakan "yang mana", "yang tersebut" berlebihan | "Faktor yang memengaruhi kinerja…" | "Faktor yang mana memengaruhi kinerja" |
| Istilah asing | italic pada penyebutan pertama | *engagement*, *job stress* | engagement (semua tanpa italic) |
| Angka | Dibaca dengan koma sebagai desimal, titik ribuan | 3,42 dan 1.250 | 3.42 atau 3,42 (konsisten) |
| Konsistensi | Satu istilah untuk satu konsep | "kinerja" (jangan campur "performansi") | bergantian |
| Ejaan | KBBI: kwalitas→kualitas, pengaruhnya→pengaruhnya,-analyses→analisis | "uji regresi" | "regresi linier" / "linear" (pilih satu) |
| Heading | Judul bab TULIS KAPITAL, sub-bab kapitalisasi kalimat | "BAB I PENDAHULUAN" | "Bab I Pendahuluan" (kecuali pedoman kampus) |

Hindari juga: pengulangan kata ("hasil-hasil penelitian menunjukkan bahwa penelitian
tersebut menunjukkan"), kalimat terlalu panjang tanpa jeda, dan jargon tanpa penjelasan.

## 4. Kerangka Berpikir (BAB II, wajib)

Kerangka berpikir menjelaskan **jalur logis** dariTeori menujuHipotesis. Tiga format yang
diterima:

**Format A — diagram ASCII** (untuk proposal Markdown):

```text
  [Teori Utama / Landasan]
            |
            v
   X1 ----> Kinerja (Y)
   X2 ----> ^
   X3 ----> |
            |
            v
   [Rumusan Masalah & Hipotesis]
```

**Format B — tabel variabel + panah naratif** (paling aman untuk DOCX):

```text
| Variabel | Indikator | Teori Pendukung | Hipotesis |
|----------|------------|------------------|-----------|
| X1: Motivasi | 4 butir Skor 1-5 | Vroom (1964) [L-2] | H01: tidak ada pengaruh positif X1 pada Y |
| Y: Kinerja | 4 butir Skor 1-5 | Path Goal [L-3] | - |
```

**Format C — narasi berurutan**:Teori X → mekanisme Y → indikator terukur → hipotesis → uji
statistik. Tulis 3-5 paragraf.

> Untuk S2/S3, tambahkan komponen **moderator/mediator** dan alasan teoretis kehadirannya.

## 5. Tabel dan Gambar

Aturan penomoran dan penulisan:

- Nomor tabel berurutan per bab: `Tabel 1.1`, `Tabel 2.1`, `Tabel 3.1`.
- Judul tabel **di atas** tabel, rata tengah, tanpa titik di akhir.
- Sumber ditulis **di bawah** tabel: `Sumber: hasil analisis data penelitian (2026)` atau
  `Sumber: [L-3]`.
- Nomor gambar sama dengan tabel: `Gambar 1.1`. Judul di bawah gambar.
- Kutipan langsung diberi tanda petik dan nomor'sumber; kutipan tidak langsung (parafrase) tidak
  perlu tanda petik, tapi harus diberi marker.
- Tabel: maksimal 7-8 kolom agar muat di A4. Kolom terlalu banyak, pecah menjadi dua tabel
  atau letakkan di lampiran.

Contoh penulisan tabel yang benar:

```text
Tabel 3.1  Karakteristik Responden Penelitian

| No | Karakteristik | Frekuensi | Persentase |
|----|---------------|-----------|------------|
| 1  | Laki-laki     | 58        | 47,5       |

Sumber: hasil analisis data penelitian (2026)
```

## 6. Menulis dengan Marker Sumber

Selama drafting, sisipkan penanda agar mudah diaudit:

```text
Angka ini diperoleh dari kolom `Skor_X` pada dataset [D:Skor_X].
Klaim literatur [L-3] dengan parafrase.
Instruksi user [U].
```

Sebelum export, jalankan grep untuk memeriksa semua marker sudah terpetakan:

```bash
grep -o "\[L-[0-9]*\]" proposal_skripsi.md | sort -u    # daftar literatur yang dikutip
grep -o "\[D:[^]]*\]" proposal_skripsi.md | sort -u     # kolom dataset yang dikutip
grep -n "\[isi " proposal_skripsi.md                    # placeholder yang belum diisi
```

## 7. Ringkasan Alur (contract) Sebelum Export

- [ ] Semua sub-bab terisi naratif, bukan bullet
- [ ] Alur antar sub-bab koheren (tidak bisa diacak urutannya)
- [ ] Setiap tabel punya judul dan sumber
- [ ] Kerangka berpikir ada di BAB II
- [ ] Semua marker terpetakan ke daftar pustaka atau ke dataset
- [ ] Tidak ada `[isi ...]` yang terlupa
- [ ] Tidak ada kalimat terpotong atau NOTES internal yang bocor ke naskah
