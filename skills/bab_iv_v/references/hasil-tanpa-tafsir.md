# Hasil Tanpa Tafsir

## Aturan pemisah

Bagian **Hasil** menjawab: *apa yang keluar dari data?*
Bagian **Pembahasan** menjawab: *mengapa angka itu keluar, dan apa artinya?*

Satu kalimat hanya boleh berada di salah satu. Kalau kalimat memuat sebab, alasan, atau
perbandingan dengan teori — ia milik Pembahasan, bukan Hasil.

| Kalimat | Milik | Sebab |
|---|---|---|
| "Nilai p = 0,002; H0 ditolak." | Hasil | keputusan statistik |
| "Kualitas data berpengaruh signifikan." | Hasil | interpretasi langsung uji |
| "Hal ini terjadi karena petugas kurang dilatih." | Pembahasan | sebab, tidak diuji |
| "Sejalan dengan [L-3] yang menemukan arah sama." | Pembahasan | perbandingan literatur |
| "Rerata 3,42 (SD = 0,51); rentang 2,4–4,6." | Hasil | deskripsi angka |
| "Rerata yang rendah menandakan beban kerja berlebih." | Pembahasan | tafsir |

## Pola kalimat Hasil yang benar

Tiga bentuk saja, tidak lebih:

```
BENTUK 1 — laporan angka
  "Rerata skor kualitas data 3,42 dari 5 (SD = 0,51; n = 4), tersaji pada Tabel 4.1."

BENTUK 2 — keputusan uji
  "Hasil uji regresi (Tabel 4.3) memberi koefisien 0,412 dengan p = 0,002.
   Pada taraf 5%, H0 ditolak."

BENTUK 3 — penunjuk arah ke rumusan
  "Subbab ini menjawab rumusan masalah ketiga, yaitu pengaruh kualitas data
   terhadap ketepatan pelaporan."
```

## Pola kalimat yang harus dipindah

Kata-kata pemicu — kalau muncul di bagian Hasil, pindahkan kalimatnya:

```
karena · disebabkan · dikarenakan · akibatnya · mengakibatkan · menyebabkan
hal ini menunjukkan · hal ini berarti · dapat diartikan · menandakan bahwa
sejalan dengan · sesuai dengan teori · berbeda dengan · diduga · kemungkinan besar
dapat disimpulkan · membuktikan bahwa · oleh sebab itu
```

Pengecualian: kata "karena" boleh muncul di Hasil **hanya** dalam kalimat metodologis
yang menjelaskan mengapa suatu uji dipilih, bukan mengapa hasilnya begitu.

```
✅  "Uji Mann-Whitney dipakai karena sebaran data tidak normal (Tabel 4.2)."
❌  "Nilai rendah karena petugas belum dilatih."
```

## Format tabel

```
Tabel 4.1 Rerata Skor Kualitas Data per Dimensi
┌────────────────────┬───────┬────────┐
│ Dimensi            │ Rerata│ SD     │
├────────────────────┼───────┼────────┤
│ Kelengkapan        │ 3,80  │ 0,45   │
│ Konsistensi        │ 2,80  │ 0,84   │
│ Ketepatan waktu    │ 3,65  │ 0,50   │
└────────────────────┴───────┴────────┘
Sumber: data primer, diolah (2026)
```

Aturan:

- Nomor dan judul **di atas** tabel; sumber **di bawah**.
- Satu gaya desimal di seluruh naskah (koma atau titik — ikuti panduan kampus).
- Jangan mengulang seluruh isi tabel di narasi. Sebut angka yang menjawab rumusan.
- Tabel tanpa angka bukan tabel — itu kerangka. Hapus atau isi.
- Jangan memecah tabel satu baris per halaman; atur ulang di Word.

## Angka wajib vs angka setengah

| Analisis | Setengah (sering ditulis) | Lengkap (wajib) |
|---|---|---|
| t-test | p = 0,03 | t(28) = 2,31; p = 0,03; d = 0,86; M₁ = 4,1 (SD 0,7); M₂ = 3,4 (SD 0,9) |
| Korelasi | r = 0,45 | r(38) = 0,45; p = 0,004; n = 40 |
| Regresi | sig 0,000 | B = 0,412; SE = 0,121; β = 0,48; t = 3,40; p = 0,002; R² = 0,34; F(1,38) = 11,6 |
| Chi-square | signifikan | χ²(2, N = 120) = 9,48; p = 0,009; V = 0,28 |
| ANOVA | p < 0,05 | F(2, 57) = 5,12; p = 0,009; η² = 0,15 |

Menulis "p = 0,000" secara teknis salah — nilai p tidak pernah tepat nol. Tulis
`p < 0,001`.

## Placeholder yang dilarang

Skrip `proposal_doctor.py` dan `peta_bab45.py` akan menandai ini:

```
[isi hasil]   [angka]   TBD   XX,X   ....   (belum dihitung)   ???
```

Naskah dengan placeholder tidak boleh diserahkan ke pembimbing — sekali terkirim,
kredibilitas seluruh angka lain ikut diragukan.
