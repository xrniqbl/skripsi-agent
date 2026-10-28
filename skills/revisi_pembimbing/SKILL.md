---
name: revisi_pembimbing
description: Mengubah catatan revisi pembimbing atau penguji (teks, komentar Word, foto tulisan tangan, pesan chat) menjadi daftar kerja terlacak, lalu memverifikasi bahwa setiap butir benar-benar sudah dikerjakan di naskah. Gunakan setelah bimbingan, setelah seminar, atau saat pengguna mengirim catatan koreksi dan bingung harus mulai dari mana.
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [skripsi, revisi, pembimbing, penguji, tindak-lanjut, indonesia]
    related_skills: [bab_iv_v, sidang, proposal_skripsi, bahasa_akademik]
---

# Revisi Pembimbing — Catatan Menjadi Daftar Kerja

Catatan revisi datang sebagai campuran: tulisan tangan di margin naskah cetak, komentar
Word, pesan WhatsApp, ucapan lisan yang lo catat di ponsel, dan "tolong diperbaiki ya"
tanpa keterangan apa pun.

Masalahnya bukan memahami catatan. Masalahnya **tidak ada yang tahu butir mana yang sudah
dikerjakan** — dan revisi yang terlewat akan muncul lagi di sidang berikutnya, dengan
nilai yang lebih buruk karena dianggap tidak serius.

---

## Prinsip yang mengikat

1. **Setiap catatan jadi satu butir.** Satu catatan bisa berisi tiga permintaan — pecah.
2. **Setiap butir punya status.** Belum / sedang / selesai / ditolak-dengan-alasan.
3. **Setiap butir punya bukti.** Nomor halaman, kutipan kalimat baru, atau nama tabel.
4. **"Selesai" harus dibuktikan di naskah**, bukan di ingatan.
5. **Penolakan sah, tapi harus beralasan.** Menolak karena tidak setuju bukan penolakan —
   itu perlu argumen metodologis.

---

## Alur kerja

```
LANGKAH 1  kumpulkan catatan mentah apa adanya (00_catatan_mentah.md)
LANGKAH 2  pecah jadi butir terpisah (01_revisi.md)
LANGKAH 3  klasifikasi: wajib / disarankan / perlu klarifikasi
LANGKAH 4  kerjakan, catat bukti per butir
LANGKAH 5  verifikasi otomatis: apakah bukti masih ada di naskah
LANGKAH 6  susun surat/lembar tanggapan revisi
```

---

## LANGKAH 1 — Kumpulkan catatan mentah

Buat `00_catatan_mentah.md`. Isi persis seperti aslinya — jangan dirapikan dulu. Sertakan
sumber dan tanggal, karena pembimbing kadang bertanya "ini dari bimbingan kapan?".

```markdown
## Bimbingan 2026-10-14 (ruang 302)

1. Bab 1 latar belakang terlalu panjang, potong
2. Rumusan masalah 3 sama dengan 2, gabung
3. Tabel 2.1 jangan pakai garis vertikal
4. "kayaknya metode kurang cocok, coba pikir lagi"
5. Daftar pustaka masih banyak buku, tambah jurnal

## Komentar Word (file: Skripsi_v3.docx)
- Hal 12: "ini dari mana? sumbernya?"
- Hal 18: "angka ini kok beda sama tabel 4.2"
- Hal 24: "paragraf ini copy paste ya?"

## WhatsApp 2026-10-16
"bab 4 pembahasannya kurang dalam, tambahin perbandingan sama penelitian lain"
```

Aturan: **jangan menafsirkan saat mencatat.** Catatan nomor 4 di atas ambigu — nanti
diklarifikasi, jangan langsung diasumsikan.

---

## LANGKAH 2 — Pecah jadi butir

Gunakan skrip untuk memecah dan memberi nomor:

```bash
python3 scripts/parse_revisi.py 00_catatan_mentah.md --out 01_revisi.md
```

Hasilnya tabel kerja:

| ID | Butir | Sumber | Lokasi | Jenis | Prioritas | Status | Bukti |
|---|---|---|---|---|---|---|---|
| R-01 | Potong latar belakang | Bimbingan 10-14 #1 | Bab I | wajib | tinggi | belum | |
| R-02 | Gabung rumusan 3 ke 2 | Bimbingan 10-14 #2 | Bab I | wajib | tinggi | belum | |
| R-03 | Tabel 2.1 tanpa garis vertikal | Bimbingan 10-14 #3 | Bab II | wajib | rendah | belum | |
| R-04 | Tinjau ulang metode | Bimbingan 10-14 #4 | Bab III | klarifikasi | tinggi | belum | |
| R-05 | Tambah jurnal di daftar pustaka | Bimbingan 10-14 #5 | Pustaka | wajib | sedang | belum | |
| R-06 | Sumber angka hal 12 | Komentar Word hal 12 | Bab ? | wajib | tinggi | belum | |
| R-07 | Angka beda dengan Tabel 4.2 | Komentar Word hal 18 | Bab IV | wajib | **kritis** | belum | |
| R-08 | Cek paragraf copy-paste | Komentar Word hal 24 | Bab ? | wajib | kritis | belum | |
| R-09 | Perdalam pembahasan + bandingkan | WhatsApp 10-16 | Bab IV | wajib | tinggi | belum | |

Cara memecah yang benar:

```
❌  "Bab 1 dan 2 diperbaiki"              -> dua butir, tidak jelas apa yang diperbaiki
✅  "R-01 potong latar belakang" + "R-03 ubah format Tabel 2.1"
```

Catatan yang ambigu **wajib** masuk jenis `klarifikasi`, bukan ditebak:

```
"metode kurang cocok, coba pikir lagi"
→ R-04, jenis: klarifikasi, isi: "Metode apa yang dianggap kurang cocok? Bagian mana?"
```

Tanyakan ke pembimbing di bimbingan berikutnya. Menebak lalu mengerjakan hal yang salah
lebih mahal daripada bertanya satu kali.

---

## LANGKAH 3 — Klasifikasi

### Prioritas

| Prioritas | Kriteria | Kapan dikerjakan |
|---|---|---|
| **kritis** | inkonsistensi angka, dugaan plagiarisme, sumber tidak jelas | hari itu — jangan menunggu |
| tinggi | mengubah struktur/logika (rumusan, metode, pembahasan) | sebelum bimbingan berikutnya |
| sedang | menambah isi (jurnal, tabel, penjelasan) | sebelum bimbingan berikutnya |
| rendah | format (garis tabel, spasi, penomoran) | belakangan, sekali jalan |

### Jenis

| Jenis | Arti | Tindakan |
|---|---|---|
| `wajib` | permintaan eksplisit | kerjakan |
| `disarankan` | "sebaiknya", "coba pertimbangkan" | kerjakan atau tolak dengan alasan |
| `klarifikasi` | ambigu | **tanya dulu**, jangan tebak |
| `format` | tata letak, sitasi, penomoran | kumpulkan, kerjakan sekali |

Skrip mengklasifikasi otomatis dari kata kunci, tapi hasilnya **wajib diperiksa manual** —
kata "coba" bisa berarti wajib.

---

## LANGKAH 4 — Kerjakan, catat bukti

Kolom **Bukti** adalah inti seluruh proses ini. Isi dengan sesuatu yang bisa diverifikasi
orang lain:

| Bukti yang sah | Bukti yang tidak sah |
|---|---|
| `hal 4 par 2 dipangkas 3→1 paragraf` | `sudah` |
| `rumusan jadi 3 butir (sebelumnya 4)` | `ok` |
| `Tabel 2.1: 0 garis vertikal (sebelumnya 6)` | `beres` |
| `R² 0,34 di hal 52 = Tabel 4.3` | `sudah dicek` |
| `10 jurnal dari 32 pustaka (31%), sebelumnya 4` | `ditambah` |

Aturan: **kalau tidak bisa ditulis sebagai bukti terukur, pekerjaannya belum selesai.**

### Format baris kerja

```markdown
### R-07 — Angka beda dengan Tabel 4.2 (KRITIS)

- **Catatan asli**: "angka ini kok beda sama tabel 4.2" (Komentar Word hal 18)
- **Diagnosis**: hal 18 menyebut 62%, Tabel 4.2 menyebut 61,5% — pembulatan tidak konsisten
- **Tindakan**: seragamkan ke 62% di seluruh naskah; tambah catatan pembulatan di bawah tabel
- **Bukti**: `grep -c "61,5"` = 0; `grep -c "62%"` = 7 (sebelumnya 6)
- **Status**: selesai
- **Tanggal**: 2026-10-17
```

### Kalau menolak

Penolakan harus punya alasan metodologis, bukan selera:

```markdown
### R-04 — Tinjau ulang metode

- **Catatan asli**: "kayaknya metode kurang cocok, coba pikir lagi"
- **Klarifikasi**: ditanyakan 2026-10-16, pembimbing menjawab "maksudnya uji beda
  tidak perlu kalau cuma deskriptif"
- **Keputusan**: **ditolak sebagian** — uji beda dipertahankan untuk rumusan 3
  karena rumusan itu menanyakan perbedaan antar kelompok; uji deskriptif saja tidak
  bisa menjawabnya (lihat BAB III hal 30)
- **Bukti argumen**: rumusan 3 hal 3 + desain hal 28
- **Status**: ditolak-dengan-alasan
- **Tanggal**: 2026-10-17
```

Yang bukan alasan penolakan: "sudah dari awal begitu", "kata kakak tingkat begitu",
"tidak sempat".

---

## LANGKAH 5 — Verifikasi otomatis

Setelah revisi dikerjakan, jalankan:

```bash
python3 scripts/parse_revisi.py 01_revisi.md --verifikasi naskah.md
```

Yang diperiksa:

1. Setiap butir berstatus `selesai` punya kolom bukti terisi.
2. Bukti berupa kutipan/angka benar-benar ada di naskah.
3. Butir `kritis` tidak boleh masih `belum`.
4. Butir `klarifikasi` tidak boleh `selesai` tanpa catatan jawaban pembimbing.

Kode keluar 1 bila ada yang gagal — supaya tidak bisa "lupa" menjalankannya.

---

## LANGKAH 6 — Lembar tanggapan revisi

Banyak kampus mewajibkan lampiran "Daftar Revisi" saat menyerahkan naskah final. Susun
dari `01_revisi.md`:

```markdown
## Lembar Tanggapan Revisi

Nama: ... · NIM: ... · Judul: ...
Pembimbing: ... · Tanggal bimbingan terakhir: ...

| No | Catatan Pembimbing | Tanggapan | Lokasi Perbaikan |
|---|---|---|---|
| 1 | Latar belakang terlalu panjang | Dipangkas dari 9 menjadi 4 paragraf | Bab I hal 1–4 |
| 2 | Rumusan 3 sama dengan 2 | Digabung; rumusan menjadi 3 butir | Bab I hal 5 |
| 3 | Tabel 2.1 pakai garis vertikal | Garis vertikal dihapus | Bab II hal 22 |
| 4 | Metode kurang cocok | Diklarifikasi; uji beda dipertahankan untuk rumusan 3 dengan alasan ... | Bab III hal 30 |
| 5 | Tambah jurnal | Jurnal 4 → 10 dari 32 pustaka | Daftar Pustaka |

Catatan: butir 4 didiskusikan pada 2026-10-16 dan disetujui untuk dipertahankan.

Tanda tangan pembimbing: __________
```

Kolom **Lokasi Perbaikan** wajib nomor halaman. Pembimbing akan membuka halaman itu.

---

## Kesalahan yang paling sering

| Kesalahan | Akibat | Pencegahan |
|---|---|---|
| Tidak mencatat saat bimbingan | lupa 30% catatan dalam 2 hari | catat di ponsel saat itu, rapikan malamnya |
| Mengerjakan tanpa daftar | butir kecil terlewat | selalu punya `01_revisi.md` |
| Menebak catatan ambigu | kerja ulang 2× | jenis `klarifikasi`, tanya dulu |
| Bukti "sudah" | tidak bisa membuktikan apa pun | bukti terukur (angka, halaman, grep) |
| Menolak tanpa alasan | dianggap tidak kooperatif | alasan metodologis + rujukan halaman |
| Revisi format dicampur revisi isi | naskah berubah saat sedang direvisi isi | kerjakan isi dulu, format terakhir |
| Lembar revisi diisi dari ingatan | nomor halaman salah | susun dari `01_revisi.md`, bukan ingatan |
| Revisi hilang setelah simpan-as | dua versi naskah, bingung mana yang final | satu nama berkas, versi naik (`_v4`, `_v5`) |

---

## Berkas pendukung

| Berkas | Isi |
|---|---|
| `references/memecah-catatan.md` | pola catatan pembimbing → butir kerja, kata kunci prioritas |
| `references/bukti-terukur.md` | jenis bukti per jenis revisi, contoh sah vs tidak |
| `references/menolak-dengan-alasan.md` | kapan boleh menolak, format argumen, contoh dialog |
| `templates/00_catatan_mentah.md` | kerangka pencatatan mentah |
| `templates/01_revisi.md` | kerangka tabel kerja revisi |
| `templates/lembar-tanggapan.md` | format lembar tanggapan resmi |
| `scripts/parse_revisi.py` | pecah catatan → butir, klasifikasi, verifikasi bukti |
| `tests/run_tests.sh` | uji skrip |
