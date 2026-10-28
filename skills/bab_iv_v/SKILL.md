---
name: bab_iv_v
description: Menulis dan memeriksa BAB IV (Hasil dan Pembahasan) serta BAB V (Simpulan dan Saran) skripsi. Gunakan saat data sudah terkumpul dan pengguna mulai menulis hasil, menafsirkan uji statistik, menyusun pembahasan yang mengaitkan temuan ke teori, menghadapi hasil yang tidak signifikan, atau menutup naskah dengan simpulan yang menjawab rumusan masalah satu per satu.
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [skripsi, bab4, bab5, pembahasan, simpulan, statistik, indonesia]
    related_skills: [proposal_skripsi, skripsi_pacil, topik_skripsi, bahasa_akademik]
---

# BAB IV & BAB V — Hasil, Pembahasan, Simpulan

BAB I menjanjikan. BAB IV menagih janji itu. Di sinilah naskah lulus atau gugur, karena
penguji tidak membaca janji — ia membaca apakah setiap rumusan masalah benar-benar dijawab
dengan angka, dan apakah angka itu masuk akal.

---

## Prinsip yang mengikat

1. **Rumusan masalah adalah daftar utang.** Setiap butir di BAB I wajib punya jawaban
   eksplisit di BAB IV, lalu diringkas di BAB V dengan urutan yang sama persis.
2. **Hasil tidak sama dengan pembahasan.** Hasil = apa yang keluar dari data, tanpa tafsir.
   Pembahasan = mengapa angka itu keluar, dibandingkan dengan teori dan studi lain.
3. **Angka tidak signifikan bukan kegagalan.** Itu temuan. Yang gagal adalah naskah yang
   menyembunyikannya atau memaksanya jadi signifikan.
4. **Jangan menambah data di BAB IV.** Kalau ada angka yang belum ada di BAB III, metode
   yang salah — perbaiki BAB III, bukan menyelipkan analisis baru.
5. **Tidak ada klaim tanpa rujukan atau tabel.** Kalimat "hal ini sesuai dengan teori X"
   wajib punya `[L-n]`; klaim angka wajib menunjuk tabel atau `[D:kolom]`.

---

## Alur kerja

```
LANGKAH 1  inventaris rumusan masalah -> tabel pemetaan (scripts/peta_bab45.py)
LANGKAH 2  susun BAB IV bagian A: hasil (tanpa tafsir)
LANGKAH 3  susun BAB IV bagian B: pembahasan (per rumusan, bukan per tabel)
LANGKAH 4  tangani hasil nonsignifikan / tidak sesuai hipotesis
LANGKAH 5  susun BAB V: simpulan menjawab 1:1 + saran bersyarat
LANGKAH 6  periksa dengan scripts/peta_bab45.py --periksa
```

Jangan mulai dari LANGKAH 2. Tanpa tabel pemetaan di LANGKAH 1, BAB IV akan jadi tumpukan
tabel tanpa arah, dan BAB V akan jadi ringkasan bab, bukan jawaban.

---

## LANGKAH 1 — Tabel pemetaan rumusan → hasil → pembahasan

Buat tabel ini **sebelum** menulis satu paragraf pun:

| # | Rumusan masalah (kutip dari BAB I) | Alat analisis (BAB III) | Tabel/angka | Jawaban satu kalimat | Teori pembanding |
|---|---|---|---|---|---|
| 1 | | | Tabel 4.x | | `[L-n]` |
| 2 | | | | | |
| 3 | | | | | |

Aturan:

- Jumlah baris = jumlah rumusan masalah. Tidak lebih, tidak kurang.
- Kolom **Alat analisis** harus sudah ada di BAB III. Kalau tidak ada → kembali ke BAB III.
- Kolom **Jawaban satu kalimat** diisi lebih dulu, baru paragrafnya ditulis. Kalau tidak
  bisa diisi satu kalimat, rumusan masalahnya terlalu kabur — perbaiki di BAB I.
- Kolom **Teori pembanding**: minimal satu. Tanpa ini, pembahasan akan jadi pengulangan
  hasil dengan kata lain.

Validasi: `python3 scripts/peta_bab45.py naskah.md --periksa`

---

## LANGKAH 2 — BAB IV bagian A: Hasil

Urutan baku:

```
4.1 Gambaran umum objek/lokasi penelitian     (konteks, bukan data pribadi)
4.2 Karakteristik responden / data             (tabel frekuensi)
4.3 Uji prasyarat                              (normalitas, homogenitas, linieritas)
4.4 Hasil analisis per rumusan masalah         (satu subbab per rumusan)
4.5 (opsional) Temuan tambahan yang tidak direncanakan
```

### Yang wajib ada di setiap subbab hasil

1. **Tujuan analisis** satu kalimat: "Subbab ini menjawab rumusan masalah pertama, yaitu …"
2. **Tabel** dengan nomor dan judul di atas tabel, sumber di bawah tabel.
3. **Narasi angka** — bukan mengulang seluruh tabel, tapi menyebut angka yang menjawab.
4. **Tanpa tafsir.** Kata "disebabkan", "karena", "sesuai teori" tidak boleh muncul di sini.

### Kalimat yang benar vs salah

```
❌  "Berdasarkan Tabel 4.3 dapat dilihat bahwa nilai signifikansi sebesar 0,000
     yang berarti kualitas data berpengaruh signifikan terhadap ketepatan
     pelaporan karena petugas kurang dilatih."

✅  "Tabel 4.3 menunjukkan nilai signifikansi 0,000 (< 0,05) dengan koefisien
     regresi 0,412. Karena nilai p di bawah taraf 5%, H0 ditolak: terdapat
     pengaruh kualitas data terhadap ketepatan pelaporan."
```

Kalimat pertama melanggar dua aturan: menyimpulkan sebab ("karena petugas kurang
dilatih") di bagian hasil, dan mengarang penjelasan yang tidak diuji. Kalimat kedua
melaporkan apa yang diuji dan keputusan statistiknya, lalu berhenti.

### Cara menulis tabel

- Nomor tabel: `Tabel 4.1`, `Tabel 4.2` — konsisten satu format di seluruh naskah.
- Judul tabel di **atas**, sumber di **bawah**.
- Desimal: pilih satu gaya (koma atau titik) dan pakai di seluruh naskah. Indonesia
  lazim koma, tapi banyak kampus menuntut titik untuk angka statistik — ikuti panduan.
- Jangan menaruh tabel kosong sebagai kerangka. Tabel tanpa angka = placeholder.

### Angka yang wajib dilaporkan (jangan setengah)

| Analisis | Wajib ada |
|---|---|
| Uji beda (t, Mann-Whitney, Wilcoxon) | statistik uji, df, p, effect size, rerata±SD kedua kelompok |
| ANOVA / Kruskal-Wallis | F/H, df, p, effect size, rerata±SD per kelompok |
| Korelasi | r/ρ, p, n, arah |
| Regresi linear | koefisien (B), SE, β, t, p, R², adjusted R², F, df |
| Regresi logistik | B, SE, Wald, p, Exp(B) + CI 95% |
| Chi-square | χ², df, p, n, sel dengan expected < 5 |
| Uji validitas/reliabilitas | r hitung vs r tabel per item, Cronbach's α |
| SEM / PLS | loading, AVE, CR, path coefficient, p, R², f², model fit |

Melaporkan "p = 0,000" tanpa effect size adalah temuan setengah jadi. p memberi tahu
*apakah* ada, effect size memberi tahu *seberapa besar* — dan penguji akan menanyakannya.

---

## LANGKAH 3 — BAB IV bagian B: Pembahasan

Pembahasan **bukan** ringkasan hasil dan **bukan** penjelasan teori. Ia menjawab:
mengapa angka ini keluar seperti ini, dan apa artinya.

### Struktur tiap subbab pembahasan (4 paragraf)

```
P1  Jawaban ringkas + angka kunci
    "Hasil menunjukkan kualitas data berpengaruh positif signifikan (β = 0,412;
     p < 0,001). Artinya setiap kenaikan satu satuan kualitas data disertai
     kenaikan ketepatan pelaporan sebesar 0,412 satuan."

P2  Bandingkan dengan studi lain — yang SAMA dan yang BEDA
    "Temuan ini sejalan dengan [L-3] yang menemukan arah serupa pada konteks
     rumah sakit. Namun berbeda dengan [L-7] yang melaporkan pengaruh tidak
     signifikan. Perbedaan ini dapat dijelaskan oleh ..."

P3  Mekanisme — mengapa bisa terjadi (bukan mengarang, tapi penalaran dari data)
    "Pada lokasi penelitian, rekap dibuat tiga kali ... sehingga konsistensi
     angka antar sumber menjadi penentu utama ketepatan. Mekanisme ini tidak
     muncul di [L-7] karena respondennya sudah memakai satu sistem tunggal."

P4  Implikasi praktis/teoretis + batas
    "Secara praktis, perbaikan paling berdampak adalah menyeragamkan sumber
     angka, bukan menambah pelatihan. Namun temuan ini terbatas pada satu
     puskesmas dengan 4 petugas, sehingga belum dapat digeneralisasi."
```

### Aturan pembahasan yang sering dilanggar

| Pelanggaran | Perbaikan |
|---|---|
| "Sesuai dengan teori X" tanpa menjelaskan bagian mana | sebut variabel/klaim spesifik dari teori itu |
| Membandingkan hanya dengan studi yang mendukung | wajib sebut minimal satu yang berbeda + jelaskan sebabnya |
| "Diduga karena …" tanpa dasar | ganti dengan mekanisme yang bisa dilacak ke data atau rujukan |
| Membahas ulang seluruh tabel | bahas **angka yang menjawab rumusan**, sisanya di lampiran |
| Menyimpulkan kausalitas dari data korelasional | tulis "berhubungan/berasosiasi", bukan "menyebabkan" |
| Melewatkan hasil yang tidak sesuai harapan | wajib dibahas eksplisit (lihat LANGKAH 4) |

### Kata kerja sesuai desain

| Desain | Boleh | Tidak boleh |
|---|---|---|
| Korelasional | berhubungan, berasosiasi, berkaitan | menyebabkan, mengakibatkan |
| Regresi (cross-section) | memprediksi, berpengaruh (dengan catatan) | membuktikan sebab-akibat |
| Eksperimen | berpengaruh, menyebabkan | — |
| Kualitatif | menunjukkan, mengungkap, menafsirkan | membuktikan, menggeneralisasi |
| R&D | menghasilkan, menghasilkan produk yang layak | menguji pengaruh (kecuali ada uji beda) |

---

## LANGKAH 4 — Hasil yang tidak signifikan / tidak sesuai hipotesis

Ini bagian yang paling sering dihindari, dan justru paling menentukan nilai. Aturan:
**laporkan, jelaskan, jangan sembunyikan.**

Bentuk penulisan:

```
P1  Laporkan apa adanya
    "Berbeda dengan dugaan awal, variabel X tidak berpengaruh signifikan
     (β = 0,031; p = 0,412)."

P2  Empat kemungkinan penyebab, pilih yang didukung data
    a. kekuatan uji (n kecil) — laporkan power/CI
    b. pengukuran (instrumen tidak menangkap variasi) — cek sebaran jawaban
    c. konteks (variabel sudah seragam di lokasi ini) — cek SD
    d. memang tidak ada hubungan — sah, dan itu temuan

P3  Kontribusi
    "Temuan ini memperluas bukti bahwa hubungan X–Y tidak universal; [L-7]
     menemukannya signifikan pada organisasi besar, sedangkan pada unit
     dengan rentang X sempit (SD = 0,3) efeknya tidak terdeteksi."
```

Yang **tidak boleh** dilakukan:

- Menghapus variabel dari model tanpa alasan metodologis.
- Mengubah taraf signifikansi dari 5% ke 10% agar signifikan.
- Menambah data sampai signifikan (p-hacking).
- Menulis "mendekati signifikan" — istilah itu tidak ada dalam statistik.
- Menyembunyikan hasil nonsignifikan dari tabel.

---

## LANGKAH 5 — BAB V: Simpulan dan Saran

### 5.1 Simpulan

Aturan mutlak: **jumlah butir simpulan = jumlah rumusan masalah**, urutannya sama.

```
❌  "Dari hasil penelitian dapat disimpulkan bahwa kualitas data berpengaruh
     terhadap ketepatan pelaporan, dan sistem berjalan cukup baik."

✅  "1. Kualitas data rekap gizi di Puskesmas X berada pada kategori sedang
     (rerata 3,42 dari 5), dengan kelemahan utama pada konsistensi antar sumber.
     2. Ketepatan pelaporan berada pada 62%, di bawah target SOP sebesar 95%.
     3. Kualitas data berpengaruh positif signifikan terhadap ketepatan
        pelaporan (β = 0,412; p < 0,001), menyumbang 34% variasi (R² = 0,34)."
```

Tiga kesalahan yang harus dihindari:

1. **Simpulan berisi angka baru** yang belum muncul di BAB IV.
2. **Simpulan berupa ringkasan bab** ("bab ini membahas…").
3. **Simpulan melampaui data** — "dapat digeneralisasi ke seluruh Indonesia".

### 5.2 Saran

Saran wajib **bersyarat dan bisa dieksekusi**. Tiga sasaran, jangan dicampur:

| Sasaran | Bentuk | Contoh |
|---|---|---|
| Untuk objek penelitian | tindakan konkret, ada pelaku | "Puskesmas X menyeragamkan satu sumber angka rekap sebelum H+3" |
| Untuk praktik/instansi | kebijakan, ada mekanisme | "Dinas Kesehatan menambahkan pemeriksaan konsistensi ke dalam SPM" |
| Untuk peneliti lanjut | pertanyaan terbuka + desain | "Replikasi dengan desain longitudinal untuk menguji arah kausalitas" |

Yang bukan saran: "hendaknya lebih ditingkatkan", "perlu adanya kesadaran",
"semoga bermanfaat". Itu bukan saran — itu kalimat yang tidak bisa dikerjakan siapa pun.

---

## Kesalahan struktur yang paling sering menggugurkan

| Gejala | Sebab | Perbaikan |
|---|---|---|
| BAB IV penuh tabel, pembahasan 2 paragraf | waktu habis di analisis | jadwalkan pembahasan ≥ 40% halaman BAB IV |
| Rumusan masalah 4 butir, simpulan 2 butir | tidak pakai tabel pemetaan | buat tabel LANGKAH 1 |
| Pembahasan hanya mengulang tabel | tidak ada teori pembanding | isi kolom terakhir tabel pemetaan |
| Hasil nonsignifikan tidak muncul | dihapus | tulis ulang dengan struktur LANGKAH 4 |
| Saran tidak bisa dijalankan | ditulis sebagai harapan | pakai tabel tiga sasaran |
| Angka di BAB IV beda dengan BAB V | ditulis ulang manual | salin dari tabel pemetaan, jangan dari ingatan |

---

## Berkas pendukung

| Berkas | Isi |
|---|---|
| `references/hasil-tanpa-tafsir.md` | cara memisahkan hasil dan pembahasan, contoh kalimat |
| `references/pembahasan-berbasis-teori.md` | pola 4 paragraf, perbandingan studi, mekanisme |
| `references/hasil-nonsignifikan.md` | 4 penyebab, cara melaporkan, batas kekuatan uji |
| `references/simpulan-dan-saran.md` | aturan 1:1, tiga sasaran saran, contoh lulus/gagal |
| `templates/peta_bab45.md` | tabel pemetaan rumusan → hasil → pembahasan |
| `scripts/peta_bab45.py` | pemeriksa: cakupan rumusan, angka tanpa sumber, tafsir di hasil |
| `tests/run_tests.sh` | uji skrip |
