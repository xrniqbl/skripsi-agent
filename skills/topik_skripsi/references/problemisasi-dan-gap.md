# Problematisasi dan Gap — Menyerang Asumsi, Bukan Mencari Lubang

## Kenapa bagian ini menentukan

Pembimbing yang berpengalaman menolak proposal bukan karena metodenya salah, tapi karena
**masalahnya tidak nyata secara ilmiah**. Dan masalah yang tidak nyata hampir selalu berasal
dari gap yang lemah: "belum ada penelitian di lokasi X".

Itu bukan gap. Itu **status geografis literatur**.

Dua tradisi yang dipakai di sini:

1. **Gap-spotting** — mencari lubang di literatur yang ada. Cepat, tapi menghasilkan
   penelitian yang menambah satu baris pada tabel, bukan pengetahuan.
2. **Problematisasi** — mempertanyakan asumsi yang mendasari literatur itu. Lebih lambat,
   tapi menghasilkan pertanyaan yang benar-benar baru.

Keduanya dipakai. Gap-spotting untuk memetakan medan; problematisasi untuk menemukan
pijakan.

---

## Langkah 1 — Petakan apa yang sudah dianggap benar

Sebelum bisa menyerang asumsi, tuliskan dulu asumsinya. Ambil 8–15 studi paling relevan,
lalu isi tabel ini:

| Studi | Objek | Metode | Temuan | **Asumsi yang dipakai** |
|---|---|---|---|---|
| [L-1] | pegawai dinas, n=120 | regresi | kualitas data → kinerja (β=0,42) | "kinerja" = nilai SKP |
| [L-2] | puskesmas, studi kasus | wawancara | pelaporan terlambat karena beban | keterlambatan = masalah individu |
| [L-3] | 12 kabupaten | SEM | budaya → adopsi | kuesioner mengukur apa yang dipakai |

Kolom terakhir itu inti pekerjaan. Tanpa kolom itu, lo hanya membuat ringkasan, bukan
analisis.

---

## Langkah 2 — Serang lima domain asumsi

Untuk **setiap** asumsi yang lo temukan, tanyakan apakah ia bisa dipertanyakan. Lima domain
(Alvesson & Sandberg):

### 2.1 Asumsi ontologis — "apakah objeknya benar-benar itu?"

Pertanyaan: apakah konsep yang dipakai literatur menunjuk pada hal yang sama dengan yang
ada di lapangan?

Contoh:
- Literatur mengukur "kepatuhan pelaporan" lewat ketepatan waktu. Di lapangan, laporan
  selalu tepat waktu **karena diisi setelah diperiksa**, bukan karena prosesnya patuh.
  → yang diukur bukan kepatuhan, tapi kepatuhan semu.
- Literatur menyebut "partisipasi masyarakat" padahal yang dihitung adalah kehadiran di rapat.

### 2.2 Asumsi epistemologis — "bagaimana kita tahu?"

Pertanyaan: apakah cara memperoleh pengetahuan itu sahih di konteks ini?

Contoh:
- Semua studi memakai kuesioner self-report untuk mengukur beban kerja. Beban kerja yang
  dirasakan ≠ beban kerja terukur (waktu proses).
- Data diambil dari satu waktu (cross-sectional) tapi disimpulkan sebagai proses.

### 2.3 Asumsi metodologis — "apakah alat ukurnya masih berlaku?"

Contoh:
- Instrumen diadaptasi dari studi 2015 dan dipakai ulang tanpa uji validitas ulang pada
  populasi berbeda (ASN dengan mandat vs karyawan swasta dengan kontrak).
- Regresi linear dipakai pada skala Likert 1–5 yang ordinal tanpa pembahasan asumsi.
- n=32 dipakai untuk SEM dengan 24 indikator.

### 2.4 Asumsi teoretis — "apakah teori ini berlaku di sini?"

Contoh:
- TAM diuji pada pengguna yang **boleh memilih**; di sini pengguna **wajib** memakai.
  "Perceived usefulness" kehilangan makna ketika tidak ada pilihan.
- Teori motivasi dari sektor swasta dipakai pada ASN yang insentifnya terikat regulasi.

### 2.5 Asumsi domain empiris — "apakah konteksnya sebanding?"

Contoh:
- Semua studi di kota besar dengan internet stabil; objek lo kabupaten dengan sinyal lemah.
- Semua studi pada perusahaan manufaktur; objek lo jasa pendidikan.

---

## Langkah 3 — Pilih satu tipe gap yang jujur

Setelah asumsi ditemukan, beri nama gap-nya. **Satu gap, satu tipe.** Gap yang mengaku
empat tipe sekaligus biasanya tidak punya tipe.

| Tipe | Definisi | Kalimat ciri | Kekuatan |
|---|---|---|---|
| **Evidence gap** | Klaim ada, tapi buktinya tipis, satu situs, atau tidak bisa direplikasi | "Temuan X hanya dari satu situs dengan n=32" | tinggi — mudah dibuktikan |
| **Knowledge void** | Pertanyaan belum pernah diajukan sama sekali | "Belum ada studi yang menguji A ketika B" | sedang — harus dibuktikan dengan pencarian |
| **Contradiction** | Dua temuan sehat saling bertentangan dan pertentangannya belum dijelaskan | "P menemukan positif, Q negatif; keduanya tidak menjelaskan mengapa" | tinggi — paling dihargai |
| **Method/theory gap** | Metode/teori yang dipakai tidak mampu menjawab pertanyaannya | "Regresi dipakai pada 4 titik waktu per unit" | tinggi — tapi butuh pemahaman metode |

### Cara membuktikan masing-masing

**Evidence gap** — kumpulkan semua studi yang mengklaim X, tunjukkan tabel: n, situs,
tahun, metode. Kalau semuanya n<50 dan satu situs, gap-nya terbukti secara aritmetika.

**Knowledge void** — butuh bukti pencarian. Jalankan `literature_probe.py` dengan 3–5
variasi kata kunci, laporkan jumlah hit, dan **tunjukkan bahwa kombinasi spesifik lo
menghasilkan 0–2 karya**. Tanpa angka, "belum ada" hanya klaim.

**Contradiction** — susun tabel A vs B: temuan, metode, populasi, alat ukur. Cari variabel
yang membedakan. Kalau ketemu, itu **moderator** — dan moderator itulah kontribusi lo.

**Method/theory gap** — tunjukkan asumsi metode yang dilanggar oleh struktur data lo
(mis. independence dilanggar karena data bertingkat; linearitas dilanggar karena outcome
biner). Ini paling teknis tapi paling sulit dibantah.

---

## Langkah 4 — Uji dengan TAS

TAS tetap dipakai sebagai uji akhir, komplementer terhadap tipe gap:

| Huruf | Pertanyaan | Lulus bila |
|---|---|---|
| **T**heoretical advance | Temuan akan mengubah/memperluas teori, atau hanya mengonfirmasi? | ada satu klaim teoretis yang bisa berubah |
| **P**roblem/context | Masalahnya tetap ada karena konteks berbeda, atau sudah selesai? | ada bukti konteks yang berbeda |
| **S**ignificance of consequences | Implikasinya baru, atau mengulang praktik umum? | ada keputusan yang akan berubah |

Minimal **dua dari tiga** harus tegas "ya" **dengan bukti**. Kalau hanya satu, gap-nya
lemah — jangan dipaksa, kembali ke Langkah 2.

---

## Langkah 5 — Tulis pernyataan gap

Format 3–4 paragraf. Bukan lebih.

### Paragraf 1 — apa yang sudah mapan

> Penelitian tentang [objek] telah berkembang sejak [tahun], dengan fokus utama pada
> [hubungan/variabel]. Sebanyak [n] studi yang ditelaah (`[L-1]`–`[L-n]`) umumnya
> menggunakan [desain] pada [populasi] dan menyimpulkan [temuan umum]. Temuan tersebut
> konsisten, sehingga [hubungan] dapat dianggap mapan pada konteks [konteks literatur].

### Paragraf 2 — asumsi yang tidak diuji

> Namun, seluruh studi tersebut bertumpu pada asumsi bahwa [asumsi]. Asumsi ini tidak
> diuji, padahal [alasan mengapa asumsi itu bisa gagal di konteks lo]. Pada [L-3],
> misalnya, [bukti bahwa asumsi itu dipakai tanpa pengujian].

### Paragraf 3 — mengapa konteks lo berbeda (dengan bukti)

> Sementara itu, data pada [D:kolom] / pengamatan di [lokasi] `[U]` menunjukkan
> [fakta yang tidak bisa dijelaskan model yang ada]. Kondisi ini tidak tertangkap oleh
> [pendekatan literatur] karena [mekanisme].

### Paragraf 4 — posisi penelitian ini

> Oleh karena itu, penelitian ini [menguji/mengembangkan/mengonfrontasikan] [asumsi]
> dengan [pendekatan] pada [lokus]. Dengan demikian, kontribusi yang diklaim bersifat
> [teoretis/empiris/metodologis], bukan sekadar penambahan kasus pada [populasi] yang
> sama.

> **Yang dilarang:** "Penelitian ini berbeda karena dilakukan di Kabupaten X." Itu bukan
> kontribusi, itu alamat.

---

## Uji kepadatan literatur

Sebelum menulis, ukur medan. Jangan menilai dari perasaan.

```bash
python3 scripts/literature_probe.py "pelaporan gizi puskesmas" \
    --alt "duplicate reporting primary health care" \
    --alt "data quality primary health care Indonesia" \
    --years 2021-2026 --out 02_probe
```

Keluaran nyata (dijalankan 2026-10-28):

```
Kueri: 'pelaporan gizi puskesmas'
  longgar (search=)        :   4465   <- JANGAN dipakai untuk sinyal
  konsep (AND semua kata)  :    101
  ketat  (frasa di judul+abstrak):      1   <- dipakai untuk sinyal
  frasa di judul saja      :      0
  Crossref (judul)         :  36058
  sinyal                   : SEPI

10 judul paling mirip:
  1. (2023) Perancangan Dashboard Monitoring Status Gizi Balita di Puskesmas ...
```

### Kenapa tiga hitungan, bukan satu

Ini jebakan yang membuat probe tidak berguna kalau salah tafsir:

| Kolom | Arti | Boleh dipakai untuk sinyal? |
|---|---|---|
| `longgar` (`search=`) | pencarian relevansi — mencocokkan kata mana pun | **tidak** |
| `konsep` (AND semua kata) | semua kata muncul di judul/abstrak — batas atas kasar | sebagai konteks |
| `ketat` (frasa persis) | frasa utuh di judul/abstrak — mendekati topik sebenarnya | **ya** |
| `frasa di judul saja` | paling konservatif | pembanding |

Kueri `"pelaporan gizi puskesmas"` memberi **4.465** pada `search=` dan **1** pada
pencarian frasa. Angka 4.465 bukan kepadatan topik — itu kepadatan kata. Melaporkan angka
longgar sebagai "medan padat" adalah kesalahan yang membuat mahasiswa mengubah topik tanpa
alasan.

### Arti sinyal

| Sinyal | `ketat` (rentang 6 tahun) | Arti | Tindakan |
|---|---|---|---|
| `SEPI` | < 5 | frasa ini nyaris tidak pernah dipakai | curiga: mungkin tidak penting, atau istilahnya beda. Coba sinonim sebelum menyimpulkan |
| `SEDANG` | 5–40 | medan sehat | cari sudut berbeda lewat problematisasi |
| `PADAT` | > 40 | frasa ini sudah jadi istilah baku | wajib problematisasi; gap-spotting akan gagal |

Aturan tafsir:

- **PADAT bukan larangan.** Ia berarti lo tidak boleh mengandalkan "belum ada yang
  meneliti". Harus ada asumsi yang diserang.
- **SEPI bukan pujian.** Medan kosong sering berarti topiknya tidak punya data atau tidak
  dianggap penting — atau istilahnya berbeda (Indonesia vs Inggris). Buktikan dulu ada
  masalah nyata (tangga 1–4), dan coba minimal tiga variasi kueri.
- **Judul paling mirip wajib dibaca.** Kalau ada satu paper yang persis sama, topik lo
  bukan baru — ubah sudut atau ganti objek.
- **Crossref selalu jauh lebih besar dari OpenAlex** karena `query.title` adalah pencarian
  relevansi longgar juga. Jangan pakai angkanya sebagai bukti kepadatan; ia hanya penanda
  bahwa istilahnya lazim.

---

## Kesalahan yang paling sering

1. **"Belum ada penelitian di [kota]."** Bukan gap. Tidak ada asumsi yang diserang.
2. **"Masih sedikit penelitian tentang [topik luas]."** Tidak spesifik, tidak bisa dibuktikan.
3. **Mengaku knowledge void tanpa menjalankan pencarian.** Kalau ada 40 paper dan lo bilang
   "belum ada", pembimbing akan menemukannya dalam 2 menit.
4. **Menggabungkan empat tipe gap** supaya terlihat hebat. Hasilnya tidak ada tipe.
5. **Menyerang asumsi tapi tidak punya data untuk mengujinya.** Problematisasi tanpa
   kelayakan = proposal yang indah dan tidak bisa dikerjakan.
6. **Menyalin kalimat gap dari skripsi lain.** Terdeteksi, dan tetap tidak relevan dengan
   konteks lo.
