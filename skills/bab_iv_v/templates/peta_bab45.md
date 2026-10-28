# Tabel Pemetaan Rumusan → Hasil → Pembahasan

Isi **sebelum** menulis BAB IV. Jumlah baris = jumlah rumusan masalah.

| # | Rumusan masalah (kutip dari BAB I) | Alat analisis (BAB III) | Tabel/angka | Jawaban satu kalimat | Teori pembanding |
|---|---|---|---|---|---|
| 1 |  |  | Tabel 4. |  | [L-] |
| 2 |  |  | Tabel 4. |  | [L-] |
| 3 |  |  | Tabel 4. |  | [L-] |
| 4 |  |  | Tabel 4. |  | [L-] |

## Aturan pengisian

- **Alat analisis** wajib sudah tercantum di BAB III. Kalau tidak → perbaiki BAB III dulu,
  jangan menambah analisis baru di BAB IV.
- **Jawaban satu kalimat** diisi sebelum paragraf ditulis. Kalau tidak bisa satu kalimat,
  rumusan masalahnya terlalu kabur — perbaiki di BAB I.
- **Teori pembanding** minimal satu. Tanpa ini, pembahasan akan jadi pengulangan hasil.
- Setelah semua baris terisi, butir simpulan di BAB V **disalin** dari kolom "Jawaban satu
  kalimat", dengan urutan yang sama.

## Pemeriksaan otomatis

```bash
python3 scripts/peta_bab45.py naskah.md --periksa
```

Kode keluar 1 bila ada galat (tafsir di bagian hasil, jumlah simpulan tidak sama, angka
tanpa sumber, saran tanpa pelaku).
