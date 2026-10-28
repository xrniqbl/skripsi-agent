---
name: sidang
description: Persiapan sidang skripsi — menyusun slide presentasi, mengantisipasi pertanyaan penguji dari naskah sendiri, melatih jawaban, dan menyiapkan berkas sidang. Gunakan saat pengguna akan seminar proposal, seminar hasil, atau sidang akhir dan butuh slide, daftar pertanyaan yang kemungkinan muncul, atau latihan menjawab.
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [skripsi, sidang, presentasi, slide, penguji, indonesia]
    related_skills: [bab_iv_v, proposal_skripsi, skripsi_pacil, bahasa_akademik]
---

# Sidang — Slide, Pertanyaan, dan Jawaban

Sidang bukan pembacaan ulang naskah. Penguji sudah membaca. Yang mereka uji dalam 20–40
menit adalah tiga hal:

1. **Apakah lo tahu apa yang lo kerjakan** — bukan hanya hasilnya, tapi kenapa begitu.
2. **Apakah naskah konsisten** — rumusan, metode, hasil, simpulan menyambung.
3. **Apakah lo bisa mempertahankan pilihan** — bukan menyerah pada koreksi pertama.

Slide yang bagus tidak menyelamatkan naskah yang tidak dikuasai. Tapi naskah bagus dengan
slide buruk kehilangan 10–15 menit untuk menjelaskan hal yang seharusnya terlihat dalam
satu gambar.

---

## Alur kerja

```
LANGKAH 1  audit naskah -> daftar titik lemah (scripts/audit_sidang.py)
LANGKAH 2  susun slide (12–18 slide, bukan 40)
LANGKAH 3  bangkitkan daftar pertanyaan penguji dari naskah sendiri
LANGKAH 4  siapkan jawaban + angka pendukung
LANGKAH 5  latihan lisan (ukur waktu, rekam, perbaiki)
LANGKAH 6  berkas & logistik
```

---

## LANGKAH 1 — Audit naskah sebelum bikin slide

Jalankan lebih dulu. Titik lemah yang ditemukan di sini menentukan slide mana yang perlu
dibuat dan pertanyaan mana yang perlu disiapkan.

```bash
python3 scripts/audit_sidang.py naskah.md --json audit.json
```

Yang diperiksa: konsistensi jumlah rumusan/tujuan/simpulan, angka tanpa sumber, klaim
tanpa rujukan, kata berlebihan, dan bagian yang hilang.

---

## LANGKAH 2 — Susun slide

### Aturan jumlah

| Durasi sidang | Jumlah slide | Keterangan |
|---|---|---|
| 10 menit (seminar proposal) | 10–12 | 1 slide ≈ 50–60 detik |
| 15 menit | 12–16 | paling umum untuk seminar hasil |
| 20 menit | 16–20 | sidang akhir dengan demo |

Acuan: **satu slide = satu gagasan = 45–60 detik bicara**. Slide 40 halaman untuk 15 menit
berarti 22 detik per slide — tidak ada yang terbaca, dan penguji akan memotong.

### Kerangka slide

```
1  Judul + identitas              nama, NIM, pembimbing, tanggal
2  Latar belakang (1 gambar/angka)
3  Kesenjangan / masalah          angka + pembanding SOP/target
4  Rumusan masalah                daftar 3–4 butir (sama persis dengan naskah)
5  Tujuan                         daftar sejajar rumusan
6  Batasan / ruang lingkup
7  Landasan teori (1 slide saja)  hanya yang dipakai di pembahasan
8  Penelitian terdahulu           tabel 3–5 studi + posisi penelitian ini
9  Metode — desain & sampel       diagram alur
10 Metode — instrumen & analisis
11 Hasil 1                        jawab rumusan 1
12 Hasil 2                        jawab rumusan 2
13 Hasil 3                        jawab rumusan 3 (uji utama)
14 Pembahasan                     kenapa begitu + bandingkan literatur
15 Simpulan                       1 slide, 3–4 butir
16 Saran + kontribusi
17 Keterbatasan + penelitian lanjut
18 Terima kasih
```

Untuk **seminar proposal**, ganti slide 11–15 dengan: rancangan analisis, jadwal, dan
kontribusi yang diharapkan.

### Aturan isi per slide

| Aturan | Angka |
|---|---|
| Maksimal baris teks | 6 baris |
| Maksimal kata per baris | 10 kata |
| Ukuran font minimum | 20 pt (judul 32–40 pt) |
| Maksimal angka per slide | 4 |
| Maksimal tabel | 5 baris × 4 kolom |
| Warna latar | putih atau gelap konsisten, bukan gradien |

Kalau satu slide butuh lebih dari itu, pecah jadi dua — atau pindahkan ke lampiran.

### Yang harus ada di setiap slide hasil

1. Satu **kalimat kesimpulan slide** di atas (bukan judul topik).
2. Satu **tabel atau grafik** yang mendukungnya.
3. Satu **angka yang diucapkan**, ditandai (bold atau warna).

```
❌  Judul: "Hasil Uji Regresi"
✅  Judul: "Kualitas data menyumbang 34% variasi ketepatan pelaporan"
    + tabel 4 baris: B, SE, β, p, R²
    + satu baris: "p = 0,002 → H0 ditolak pada taraf 5%"
```

Judul slide yang berupa kesimpulan memaksa lo menyimpulkan, dan memudahkan penguji
mengikuti alur.

### Grafik vs tabel

| Gunakan grafik bila | Gunakan tabel bila |
|---|---|
| menunjukkan tren/arah | membandingkan angka presisi |
| membandingkan 2–3 kelompok | penguji butuh nilai p, β, SE |
| menunjukkan proporsi | ada lebih dari 4 variabel |

Grafik tanpa angka sering ditanya "berapa tepatnya?" — siapkan angkanya di catatan lo,
bukan di slide.

### Desain

- Satu jenis font. Satu ukuran judul. Satu palet (2 warna + abu).
- Tanpa animasi. Tanpa transisi. Tanpa suara.
- Nomor slide di kanan bawah.
- Nomor tabel di slide harus sama dengan nomor di naskah — penguji akan mencocokkan.
- Simpan cadangan `.pdf` di flashdisk dan kirim ke email sendiri sebelum berangkat.

---

## LANGKAH 3 — Daftar pertanyaan penguji

Bangkitkan dari naskah lo sendiri, bukan dari daftar generik. Skrip bisa membantu:

```bash
python3 scripts/audit_sidang.py naskah.md --pertanyaan
```

Pertanyaan dikelompokkan per pola. Tiga yang selalu muncul di setiap sidang:

### Kelompok A — Pertanyaan wajib (hampir pasti ditanya)

| Pertanyaan | Kenapa ditanya | Siapkan |
|---|---|---|
| "Apa masalahnya? Kenapa ini penting?" | menguji apakah latar belakang nyambung | satu paragraf + satu angka |
| "Apa bedanya dengan penelitian [X]?" | menguji klaim kebaruan | tabel perbandingan 3 studi |
| "Kenapa pakai metode ini, bukan [Y]?" | menguji penguasaan metode | alasan berbasis karakteristik data |
| "Sampelnya kenapa segitu? Representatif?" | menguji dasar penarikan sampel | rumus/teknik + batas generalisasi |
| "Hasilnya kok tidak signifikan?" | menguji kejujuran + pemahaman | penyebab yang didukung data (`bab_iv_v`) |
| "Apa simpulan utama?" | menguji apakah lo bisa meringkas | 3 butir, satu kalimat masing-masing |
| "Apa kontribusinya?" | menguji nilai tambah | teoretis + praktis, dipisah |
| "Apa kelemahan penelitian ini?" | menguji kesadaran diri | 3 batas, jangan bilang "tidak ada" |

### Kelompok B — Pertanyaan dari angka lo

Dibangkitkan dari naskah. Contoh bentuk:

```
"R² hanya 0,34 — 66% dijelaskan apa?"
"Kenapa n = 4? Apa bisa digeneralisasi?"
"Kenapa p = 0,002 bukan 0,000?"
"Kenapa pakai uji ini padahal data ordinal?"
"Tabel 4.2 dan 4.4 angkanya beda — mana yang benar?"
```

Angka yang tidak konsisten antar tabel adalah pertanyaan paling mematikan karena tidak
ada jawaban benar — hanya pengakuan dan perbaikan.

### Kelompok C — Pertanyaan jebakan

| Pertanyaan | Jebakan | Jawaban aman |
|---|---|---|
| "Menurut Anda, kenapa begitu?" | menguji apakah lo mengarang | "Dari data yang ada, saya hanya bisa menyimpulkan X. Penjelasan Y butuh data tambahan." |
| "Kalau saya bilang metode Anda salah, bagaimana?" | menguji ketahanan | "Yang saya pahami, metode ini dipilih karena [alasan]. Kalau ada pertimbangan lain, saya siap belajar — bagian mana yang perlu saya perbaiki?" |
| "Teori Anda tidak cocok dengan hasil. Bagaimana?" | menguji apakah lo berani berbeda | "Hasil tidak mendukung teori itu pada konteks ini. Perbedaannya karena [mekanisme]." |
| "Coba jelaskan ulang, saya tidak paham." | bisa berarti lo tidak jelas, bisa berarti uji mental | ulangi dengan kalimat lebih pendek + satu contoh konkret |
| "Ini penelitian Anda sendiri atau dibantu AI?" | menguji penguasaan | jawab dengan menjelaskan satu bagian teknis secara detail — penguasaan terbukti dari detail, bukan dari penyangkalan |

---

## LANGKAH 4 — Siapkan jawaban

Format tiap jawaban: **3 kalimat, maksimal 20 detik**.

```
K1  Jawaban langsung (ya/tidak/angkanya)
K2  Alasan atau bukti (angka, tabel, rujukan)
K3  Batas atau tindak lanjut
```

Contoh:

```
P: "Kenapa sampelnya hanya 4 orang?"
J: "Karena penelitian ini studi kasus pada satu puskesmas yang seluruh
    petugas gizinya berjumlah 4 orang, jadi ini sensus, bukan sampel.
    Konsekuensinya, temuan tidak bisa digeneralisasi ke puskesmas lain —
    dan itu saya nyatakan di bagian keterbatasan."
```

Yang harus dihindari saat menjawab:

- Berbicara lebih dari 40 detik tanpa jeda. Penguji akan memotong.
- "Itu dari pembimbing saya." — memindahkan tanggung jawab.
- "Di jurnal X begitu." — tanpa menyebut bagian mana.
- Berdebat. Bedakan: **menjelaskan** pilihan vs **mempertahankan** harga diri.
- Mengarang jawaban. Lebih baik: "Saya belum memeriksa itu; boleh saya jawab setelah saya cek data?"

---

## LANGKAH 5 — Latihan lisan

Latihan bukan membaca slide. Urutannya:

1. **Rekam diri sendiri** menjawab 8 pertanyaan Kelompok A. Dengarkan ulang. Hitung
   berapa kali mengucapkan "ee", "gitu", "kan".
2. **Ukur waktu presentasi** dengan timer. Kalau lewat 10%, potong satu slide.
3. **Latihan dengan orang** yang tidak tahu topik lo. Kalau dia paham slide 3–5, alurnya
   sudah benar.
4. **Latihan tanpa slide.** Tutup laptop, jelaskan penelitian dalam 3 menit. Kalau tidak
   bisa, berarti lo belum menguasai — slide menyembunyikannya.

Target: presentasi selesai 1 menit lebih cepat dari batas waktu. Sisanya untuk napas.

---

## LANGKAH 6 — Berkas dan logistik

### Berkas wajib dibawa

```
[ ] Naskah cetak 3–4 eksemplar (untuk penguji)
[ ] Slide .pptx DAN .pdf di flashdisk
[ ] Slide juga di email sendiri (akses daring)
[ ] Lembar revisi / catatan kosong + pulpen
[ ] Kartu bimbingan / berkas administrasi
[ ] Data mentah + output SPSS/Excel (kalau ditanya)
[ ] Kertas catatan kecil: angka kunci (R², p, n, β)
```

Simpan satu kertas berisi **10 angka kunci** yang paling mungkin ditanya. Jangan
mengandalkan ingatan saat tekanan.

### Sebelum masuk ruang

- Datang 30 menit lebih awal, tes proyektor + remote.
- Air minum.
- Ponsel silent, bukan getar.
- Pakaian sesuai aturan kampus (sudah dicek malam sebelumnya).

### Saat sidang

- Mulai dengan satu kalimat: tujuan penelitian, bukan basa-basi.
- Saat ditanya, **tulis pertanyaannya** dulu. Ini menurunkan panik dan memberi waktu
  berpikir 3 detik.
- Kalau pertanyaan berlapis, ulangi intinya: "Jadi yang ditanyakan tentang A dan B, benar?"
- Kalau tidak tahu: akui, sebut cara mencarinya.
- Akhiri dengan ringkasan 3 butir simpulan, bukan "sekian, terima kasih".

---

## Kesalahan yang paling sering menggugurkan

| Kesalahan | Akibat | Pencegahan |
|---|---|---|
| Slide 40 halaman untuk 15 menit | dipotong di tengah, simpulan tidak tersampaikan | 1 slide = 45–60 detik |
| Angka di slide beda dengan naskah | dianggap tidak teliti | salin dari tabel, jangan dari ingatan |
| Tidak bisa menjelaskan metode sendiri | dianggap tidak mengerjakan sendiri | latihan tanpa slide (LANGKAH 5.4) |
| Menjawab "sesuai pembimbing" | dianggap tidak mandiri | siapkan alasan substantif |
| Berdebat dengan penguji | suasana rusak, revisi diperketat | jelaskan pilihan, terima koreksi |
| Mengarang saat tidak tahu | ketahuan, kredibilitas hilang total | akui + sebut cara mencari |
| Menyembunyikan hasil nonsignifikan | pertanyaan beruntun | laporkan + jelaskan penyebab |

---

## Berkas pendukung

| Berkas | Isi |
|---|---|
| `references/struktur-slide.md` | kerangka slide per jenis sidang + aturan desain |
| `references/bank-pertanyaan.md` | 60+ pertanyaan penguji per kelompok + pola jawaban |
| `references/teknik-menjawab.md` | format 3 kalimat, menangani jebakan, mengelola panik |
| `templates/kerangka-slide.md` | kerangka slide siap salin |
| `templates/kartu-angka.md` | kartu 10 angka kunci untuk dibawa |
| `scripts/audit_sidang.py` | audit naskah + bangkitkan pertanyaan dari naskah |
| `tests/run_tests.sh` | uji skrip |
