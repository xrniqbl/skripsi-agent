# Dataset Analysis — Profil Data & Pemilihan Uji Statistik

Pandu **STEP 4.2**. Bila folder user berisi CSV/XLSX, proposal **wajib** memakai data nyata, bukan
metode generik. Prinsipnya: **profilkan data dulu, baru tulis metode.**

## 1. Menggunakan Script

```bash
# CSV / TSV (stdlib saja, tanpa dependensi)
python3 scripts/profile_dataset.py data/responden.csv

# XLSX (butuh openpyxl)
pip3 install openpyxl
python3 scripts/profile_dataset.py data/responden.xlsx --sheet "Sheet1"

# JSON array of objects
python3 scripts/profile_dataset.py data/responses.json

# beberapa file sekaligus -> laporan gabungan
python3 scripts/profile_dataset.py data/*.csv --out profil
```

Keluarannya:

- `profil_dataset.md` — tabel profil, deskriptif, normalitas, Cronbach's alpha, rekomendasi uji.
- `profil_dataset.json` — angka machine-readable untuk drafting dan pengecekan.

Script hanya memakai **stdlib Python** (kecuali XLSX yang butuh `openpyxl`). Bila SciPy tidak
terpasang, uji normalitas dihitung dengan pendekatan skewness-kurtosis, dan hasilnya diberi label
`perkiraan`.

## 2. Apa Saja yang Dihasilkan

| Bagian | Isi |
|--------|-----|
| Ringkasan file | jumlah baris, jumlah kolom, delimiter, Ukuran, jumlah baris kosong |
| Per kolom | tipe data, jumlah missing, persen lengkap, jumlah nilai unik |
| Deskriptif numerik | mean, median, std, min, Q1, Q3, max, skewness, kurtosis |
| Frekuensi kategorik | lima nilai teratas beserta persentase |
| Deteksi skala | kolom dengan rentang 1-5 atau 1-7 dan rata-rata 1,0 sampai 5,0 dideteksi sebagai Likert |
| Reliabilitas | Cronbach's alpha untuk kelompok kolom Likert yang namanya berbagi awalan |
| Normalitas | Shapiro-Wilk bila scipy ada, selain itu skewness-kurtosis |
| Rekomendasi uji | berdasarkan jenis kolom, cardinality, dan jumlah kelompok |

## 3. Membaca Hasil untuk Menulis BAB III

### 3.1 Menentukan variabel dari nama kolom

Nama kolom dataset biasanya sudah merepresentasikan butir kuesioner. Buat pemetaan seperti ini:

| Kolom dataset | Rentang | Mean | Std | Peran | Indikator |
|---------------|------|------|-----|-------|-----------|
| `X1_Motivasi` | 1-5 | 3,42 | 0,71 | Independen | 4 butir: X1, X2, X3, X4 |

Contoh susunan kalimat yang boleh ditulis:

> Instrumen terdiri dari 18 butir yang memuat tiga variabel independen (motivasi,
> kompetensi) dan satu variabel dependen (kinerja), seluruhnya berskala Likert lima poin. Skor
> masing-masing variabel diperoleh dari rata-rata butirnya. Berdasarkan data awal, reliabilitas
> instrumen mencapai alpha 0,84 untuk kinerja, 0,79 untuk motivasi, dan 0,76 untuk kompetensi
> `[D]`.

Semua angka di atas **wajib** berasal dari `profil_dataset.md`.

### 3.2 Memilih uji dari profil

| Yang terlihat di profil | Uji yang tepat | Alasan yang ditulis di proposal |
|------------------------|----------------|----------------------------------|
| 1 DV numerik, 2 kelompok independen | independent t-test bila normal dan homogen | uji komparasi dua kelompok |
| 1 DV numerik, 2 kelompok independen, skew besar atau varian beda | Mann-Whitney U | asumsi normalitas tidak terpenuhi |
| 1 DV numerik, lebih dari 2 kelompok | one-way ANOVA | perbandingan lebih dari dua kelompok |
| 1 DV numerik, 3 prediktor atau lebih | regresi linear berganda | menguji pengaruh simultan |
| 2 variabel numerik, hipotesis arah | Pearson r | asumsi linearitas terpenuhi `[D]` |
| 2 variabel numerik, ordinal atau skew | Spearman rho | data ordinal |
| DV kategorik, 1 prediktor kategorik | chi-square | uji asosiasi dua variabel kategorik |
| Banyak DV laten, banyak indikator | PLS-SEM | model struktural dengan indikator reflektif |

### 3.3 Uji asumsi yang perlu ditulis

Dari profil, jelaskan:

1. Normalitas: skewness di luar rentang -2 sampai +2 pada kolom tertentu, atau hasil uji
   normalitas, menjadi alasan pemilihan uji non-parametrik.
3. Multikolinearitas: bila korelasi antar independen di atas 0,8, tuliskan '_Kline (1979)_' atau '_tenure arist_'.
3. Multikolinearitas: bila korelasi antar independen di atas 0,8, tuliskan '_Kline (1979)_' atau '_tenure arist_'.
4. Jumlah kasus: bila n kecil, tekankan uji non-parametrik.

Contoh kalimat:

> Kolom `Skor_Kinerja` menunjukkan skewness 0,12 sehingga distribusi dianggap normal, namun kolom
> `Skor_Stress` menunjukkan skewness 2,31. Karena itu, perbandingan dua kelompok pada variabel
> stress menggunakan uji Mann-Whitney U, sedangkan variabel kinerja menggunakan paired t-test
> `[D]`.

### 3.4 Menentukan arah hipotesis dari data (opsional, hati-hati)

Bila data awal cukup besar, boleh melihat pola korelasi untuk memastikan **arah** hipotisis
sah secara teoretis. Tulis sebagai "uji pendahuluan" (pretest), bukan sebagai hasil akhir.

## 4. Bila Data Belum Ada

Nilai tambah: tulis rancangan analisis **tanpa angka**, dan tandai eksplisit:

> Catatan: data empiris belum tersedia pada tahap proposal. Seluruh prosedur analisis
>_VERIFIED_ (data belum dianalisis) yang disajikan merupakan rancangan, dan akan dieksekusi
> setelah pengumpulan data. (data belum dianalisis)

Jangan menulis "berdasarkan hasil pratinjau data, mean X adalah 3,4" bila data belum ada.

## 5. Pemetaan Langsung ke Tabel Uji

Salin `templates/tabel_uji_statistik.md`, lalu isi setiap baris dari profil. Wajib ada kolom
sumber data (`[D:nama_kolom]`) agar reviewer bisa menelusuri angka.

## 6. Aturan Anti-Hallucination Angka

1. Setiap angka dalam naskah harus bisa ditunjuk ke baris tertentu di `profil_dataset.md`.
2. Angka dari `profil_dataset.md` boleh disalin apa adanya; angka turunan (persentase, rasio)
   harus dihitung ulang dan ditampilkan perhitungannya.
3. Bila dataset berubah, jalankan ulang script dan perbarui naskah.
4. Jangan memakai statistik dari artikel orang lain sebagai statistik penelitian ini.
5. Bila data bersifat sensitif, tampilkan hanya statistik agregat yang aman dipublikasikan.
