# Simpulan dan Saran

## Aturan mutlak simpulan

**Jumlah butir simpulan = jumlah rumusan masalah. Urutan sama.**

Bukan "kira-kira sama". Kalau BAB I punya 4 rumusan, BAB V punya 4 butir bernomor.
Penguji membuka BAB I dan BAB V bersamaan — ini pemeriksaan pertama yang mereka lakukan.

| Rumusan (BAB I) | Simpulan (BAB V) |
|---|---|
| 1. Bagaimana kondisi X? | 1. Kondisi X adalah … (angka) |
| 2. Bagaimana tingkat Y? | 2. Tingkat Y adalah … (angka) |
| 3. Apakah X berpengaruh pada Y? | 3. X berpengaruh/ tidak berpengaruh pada Y (statistik) |
| 4. Seberapa besar sumbangan X? | 4. X menyumbang … % (angka) |

## Tiga kesalahan fatal

### 1. Simpulan berisi angka baru

```
❌  "1. Kualitas data berpengaruh signifikan (p = 0,002; R² = 0,41)."
```
Kalau `R² = 0,41` belum pernah muncul di BAB IV, itu angka baru di bab penutup —
tanda naskah ditulis tidak berurutan.

### 2. Simpulan berupa ringkasan bab

```
❌  "1. Bab ini membahas hasil penelitian yang telah dilakukan."
❌  "1. Berdasarkan hasil analisis dapat disimpulkan bahwa penelitian
       ini telah berhasil dilaksanakan dengan baik."
```
Itu bukan simpulan — itu kalimat pembuka yang tidak menjawab apa pun.

### 3. Simpulan melampaui data

```
❌  "1. Kualitas data berpengaruh terhadap ketepatan pelaporan di seluruh
       puskesmas di Indonesia."
```
Data berasal dari satu puskesmas dengan 4 responden. Klaim nasional adalah
pelanggaran generalisasi, dan penguji akan langsung menunjuknya.

## Format penulisan simpulan

```
### 5.1 Simpulan

Berdasarkan hasil analisis terhadap data penelitian di Puskesmas X, dapat
disimpulkan:

1. Kualitas data rekap gizi berada pada kategori sedang (rerata 3,42 dari 5),
   dengan kelemahan utama pada konsistensi antar sumber (2,80).
2. Ketepatan pelaporan gizi mencapai 62%, masih di bawah target SOP sebesar 95%.
3. Kualitas data berpengaruh positif signifikan terhadap ketepatan pelaporan
   (β = 0,412; p = 0,002).
4. Kualitas data menyumbang 34% variasi ketepatan pelaporan (R² = 0,34);
   sisanya dijelaskan faktor lain di luar model.
```

Perhatikan: setiap butir punya **angka**, dan setiap angka sudah ada di BAB IV.
Kalimat pembuka hanya satu, tidak bertele-tele.

## Saran: tiga sasaran, jangan dicampur

Saran harus memenuhi tiga syarat: ada **pelaku**, ada **tindakan**, ada **alasan/konteks**.

### Sasaran 1 — untuk objek penelitian

```
❌  "Hendaknya kualitas pelaporan lebih ditingkatkan."
✅  "Puskesmas X perlu menetapkan satu sumber angka rekap (bukan tiga) dan
     memverifikasinya sebelum H+3, karena konsistensi sumber adalah variabel
     yang terbukti paling berpengaruh dalam model ini."
```

### Sasaran 2 — untuk instansi/praktik

```
❌  "Perlu adanya pengawasan dari dinas."
✅  "Dinas Kesehatan dapat menambahkan pemeriksaan konsistensi antar sumber
     ke dalam instrumen Supervisi Puskesmas yang sudah berjalan, tanpa perlu
     sistem baru."
```

### Sasaran 3 — untuk peneliti lanjut

```
❌  "Peneliti selanjutnya diharapkan meneliti variabel lain."
✅  "Penelitian lanjut dapat menguji arah kausalitas dengan desain longitudinal
     (minimal tiga titik waktu), karena desain cross-section dalam penelitian
     ini tidak dapat memastikan arah pengaruh."
```

## Kalimat yang bukan saran

Ini semua harus diganti — tidak ada satu pun yang bisa dikerjakan:

```
"hendaknya lebih ditingkatkan"          → ditingkatkan apa, oleh siapa, kapan?
"perlu adanya kesadaran"                → bukan tindakan
"semoga bermanfaat"                     → bukan saran
"kiranya dapat menjadi bahan masukan"   → bukan saran
"alangkah baiknya bila"                 → bukan saran
"sudah sepatutnya"                      → bukan saran
"diharapkan dapat memberikan kontribusi"→ kontribusi apa?
```

Skrip `peta_bab45.py` menandai kalimat seperti ini dengan kode `saran_tanpa_pelaku`.

## Struktur alternatif: saran per rumusan

Beberapa kampus menuntut saran sejajar dengan simpulan. Bentuknya:

```
### 5.2 Saran

1. Berkaitan dengan kondisi kualitas data (simpulan 1):
   Puskesmas X menyeragamkan sumber angka rekap sebelum H+3.
2. Berkaitan dengan ketepatan pelaporan (simpulan 2):
   Puskesmas X memasang papan pemantauan ketepatan mingguan.
3. Berkaitan dengan pengaruh kualitas data (simpulan 3):
   Dinas Kesehatan memprioritaskan perbaikan konsistensi data...
4. Berkaitan dengan sumbangan kualitas data (simpulan 4):
   Peneliti lanjut menguji faktor lain yang menjelaskan 66% sisa variasi...
```

Bentuk ini lebih aman karena memaksa keterkaitan 1:1.

## Checklist sebelum menutup naskah

- [ ] Jumlah butir simpulan = jumlah rumusan masalah
- [ ] Urutan butir sama dengan urutan rumusan
- [ ] Setiap butir simpulan punya angka yang sudah ada di BAB IV
- [ ] Tidak ada klaim melebihi cakupan sampel
- [ ] Setiap saran punya pelaku + tindakan
- [ ] Saran dipisah per sasaran (objek / instansi / peneliti lanjut) atau per rumusan
- [ ] Tidak ada kalimat harapan tanpa tindakan
- [ ] Tidak ada "semoga", "hendaknya", "kiranya"

## Hubungan ke abstrak

Setelah BAB V selesai, abstrak ditulis **terakhir** dan diambil dari sini:

```
Latar belakang  1 kalimat  (dari BAB I)
Tujuan          1 kalimat  (dari rumusan)
Metode          1–2 kalimat (desain, sampel, analisis)
Hasil           angka kunci dari simpulan 3–4
Simpulan        1 kalimat  (dari simpulan 1–2)
Kata kunci      3–5 istilah, bukan singkatan bebas
```

Abstrak yang ditulis sebelum BAB V selesai hampir selalu memuat angka yang tidak
sesuai dengan hasil akhir.
