# Hasil Tidak Signifikan

## Kenapa ini bagian paling penting

Hampir setiap skripsi punya minimal satu hipotesis yang tidak didukung data. Mahasiswa
panik, lalu melakukan satu dari empat hal buruk: menghapus variabel, menaikkan taraf
signifikansi, menambah data sampai signifikan, atau menyembunyikannya dari tabel.

Semua itu p-hacking, dan penguji yang berpengalaman akan melihatnya dari jumlah n yang
berubah-ubah antar tabel.

**Hasil tidak signifikan adalah temuan.** Yang gagal adalah naskah yang menyembunyikannya.

## Empat penyebab yang sah

Periksa berurutan, pilih yang **didukung data** — jangan pilih yang paling enak.

### 1. Kekuatan uji kurang (n terlalu kecil)

Gejala:
- CI 95% sangat lebar (mis. β = 0,03; CI −0,42 s/d 0,48)
- Effect size cukup besar tapi p > 0,05
- n < 30 per kelompok untuk uji beda

Cara melaporkan:

```
"Koefisien 0,031 tidak signifikan (p = 0,412; CI 95% −0,42 s/d 0,48).
Interval yang lebar menunjukkan taksiran ini belum presisi; dengan n = 24,
kekuatan uji untuk mendeteksi efek sebesar d = 0,3 hanya sekitar 0,18."
```

Jangan menulis "mendekati signifikan" (p = 0,06). Istilah itu tidak ada dalam statistik.
Tulis apa adanya: `p = 0,06` — tidak signifikan pada taraf 5%.

### 2. Pengukuran tidak menangkap variasi

Gejala:
- SD sangat kecil (mis. 0,12 pada skala 1–5)
- Hampir semua responden menjawab nilai sama
- Distribusi sangat miring (ceiling/floor effect)

Cara melaporkan:

```
"Sebaran variabel X sangat sempit (SD = 0,12; rentang 3,8–4,2 pada skala 1–5).
Dengan variasi sekecil itu, kovariasi dengan variabel lain sulit terdeteksi
meskipun secara teoretis ada."
```

Tindakan yang sah: sebut sebagai batas penelitian, dan sarankan instrumen yang lebih
sensitif untuk penelitian lanjut. Tindakan yang tidak sah: mengganti instrumen setelah
data terkumpul.

### 3. Konteks membuat variabel seragam

Gejala:
- Semua unit memakai sistem/prosedur yang sama
- Kebijakan baru sudah menyamakan kondisi

Cara melaporkan:

```
"Pada lokasi ini seluruh unit sudah memakai satu sistem pelaporan sejak 2024,
sehingga variabel X nyaris tidak bervariasi antar unit. Efeknya tidak dapat
diidentifikasi dari data ini — bukan karena tidak ada, tetapi karena tidak ada
variasi yang bisa dibandingkan."
```

### 4. Memang tidak ada hubungan

Ini temuan yang sah dan berharga. Laporkan sebagai kontribusi:

```
"Hasil ini menunjukkan hubungan X–Y tidak universal. [L-7] menemukannya
signifikan pada organisasi besar, sedangkan pada unit dengan karakteristik
seperti lokasi ini efeknya tidak terdeteksi. Temuan ini memperluas bukti
bahwa hubungan tersebut bergantung pada konteks."
```

## Struktur penulisan (3 paragraf)

```
P1  Laporkan apa adanya — angka lengkap, tanpa kata "sayangnya"
P2  Sebut penyebab yang didukung data (dari empat di atas) + buktinya
P3  Kontribusi temuan + batas + arah penelitian lanjut
```

Contoh utuh:

```
"Berbeda dengan dugaan awal, variabel beban kerja tidak berpengaruh signifikan
terhadap ketepatan pelaporan (β = 0,031; SE = 0,038; p = 0,412; CI 95%
−0,045 s/d 0,107).

Tidak signifikannya koefisien ini dapat dijelaskan oleh sempitnya sebaran
beban kerja di lokasi penelitian (SD = 0,22 pada skala 1–5; 3 dari 4 petugas
berada pada kategori sedang). Dengan variasi sekecil itu, kovariasi dengan
ketepatan pelaporan sulit terdeteksi. Selain itu, jumlah responden (n = 4)
membatasi kekuatan uji: efek sebesar d = 0,3 hanya akan terdeteksi dengan
peluang sekitar 0,15.

Temuan ini bukan berarti beban kerja tidak penting, melainkan bahwa pada unit
dengan beban kerja seragam, faktor penentu ketepatan pelaporan bergeser ke
kualitas data (yang signifikan pada model yang sama). Penelitian lanjut perlu
melibatkan beberapa puskesmas dengan rentang beban kerja lebih lebar agar
efeknya dapat diuji."
```

## Yang dilarang keras

| Tindakan | Kenapa dilarang | Yang terdeteksi |
|---|---|---|
| Menghapus variabel dari model tanpa alasan metodologis | mengubah hipotesis setelah melihat data | jumlah variabel di BAB II vs BAB IV beda |
| Mengubah taraf 5% → 10% | menyesuaikan kriteria dengan hasil | disebut di BAB III sebagai 5% |
| Menambah responden sampai signifikan | p-hacking | n di tabel berbeda-beda |
| Menyembunyikan dari tabel | seleksi pelaporan | jumlah hipotesis di BAB II vs tabel |
| "Mendekati signifikan" | istilah tidak ada | langsung ditanya penguji |
| "Hanya kurang sampel sedikit lagi" | spekulasi | minta hitung power-nya |

## Cara menghitung kekuatan uji (jika ditanya)

Untuk regresi linear sederhana, kekuatan uji bisa didekati dengan effect size f²:

```
f² = R² / (1 − R²)
```

Patokan Cohen: f² = 0,02 kecil · 0,15 sedang · 0,35 besar.

Kalau tidak yakin, jangan mengarang angka power. Tulis:

```
"Kekuatan uji tidak dihitung dalam penelitian ini; dengan n = 24 dan effect
size yang teramati kecil, hasil nonsignifikan perlu ditafsirkan hati-hati."
```

Mengakui batas lebih baik daripada mengarang angka.

## Kalimat yang jangan dipakai

```
❌  "Sayangnya hasil penelitian ini tidak signifikan."
     → "sayangnya" menyiratkan hasilnya buruk, padahal itu data.

❌  "Hal ini mungkin disebabkan oleh faktor-faktor lain yang tidak diteliti."
     → terlalu umum, tidak bisa diverifikasi. Sebut faktor spesifik + buktinya.

❌  "Diperlukan sampel yang lebih besar agar hasilnya signifikan."
     → menyiratkan tujuan penelitian adalah signifikansi, bukan jawaban.

✅  "Dengan n = 24, efek sebesar β = 0,03 tidak dapat dibedakan dari nol.
     Penelitian lanjut memerlukan n ≈ 120 untuk mendeteksi efek sebesar itu
     pada taraf 5% dengan kekuatan 0,80."
```
