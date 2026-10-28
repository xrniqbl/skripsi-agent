# Memecah Catatan Pembimbing

## Bentuk catatan yang umum

| Bentuk | Contoh | Cara menangani |
|---|---|---|
| Tulisan tangan di margin | "poting!" / "dari mana?" | foto → transkrip ke `00_catatan_mentah.md` |
| Komentar Word | balon komentar di naskah | ekstrak ke daftar dengan nomor halaman |
| Pesan WhatsApp | "bab 4 kurang dalam" | satu baris per pesan, jangan digabung |
| Lisan saat bimbingan | ucapan tanpa naskah | catat di ponsel **saat itu**, rapikan malamnya |
| Email | paragraf panjang | pecah per permintaan |
| "Tolong diperbaiki ya" | tanpa keterangan | **klarifikasi**, bukan tebak |

## Aturan pencatatan mentah

1. **Tulis persis.** Jangan dirapikan, jangan ditafsirkan.
   ```
   ❌  "Latar belakang perlu dipersingkat agar lebih fokus pada masalah"
   ✅  "bab 1 latar belakang terlalu panjang, potong"
   ```
   Versi pertama sudah mengandung tafsiran lo — dan tafsiran itu yang nanti salah.

2. **Sertakan sumber + tanggal.** Pembimbing akan bertanya "ini dari bimbingan kapan?".

3. **Jangan gabungkan dua catatan.** Kalau pembimbing bilang "bab 1 dan 2 kurang",
   tulis dua baris.

4. **Catat yang ambigu apa adanya.** "kayaknya metode kurang cocok" → tulis begitu,
   jangan diubah jadi "ganti metode menjadi kuantitatif".

## Pola pemecahan

### Satu catatan → beberapa butir

```
"Bab 1 dan 2 tolong diperbaiki, tabelnya juga"
→ R-01 perbaiki Bab I      (klarifikasi: apa yang diperbaiki?)
→ R-02 perbaiki Bab II     (klarifikasi)
→ R-03 perbaiki tabel      (klarifikasi: tabel mana?)
```

Ini bukan berlebihan — ini memaksa lo bertanya, dan pertanyaan yang tepat menghemat
satu putaran bimbingan.

### Catatan panjang → butir spesifik

```
"Bab 4 pembahasannya kurang dalam, belum ada perbandingan dengan penelitian
 lain, dan kesimpulannya belum menjawab rumusan masalah nomor 3"
→ R-04 perdalam pembahasan Bab IV
→ R-05 tambah perbandingan dengan penelitian lain
→ R-06 perbaiki simpulan agar menjawab rumusan 3
```

## Kata kunci → prioritas

| Kata kunci dalam catatan | Prioritas | Alasan |
|---|---|---|
| "beda", "tidak sama", "tidak konsisten" | **kritis** | inkonsistensi angka = kehilangan kredibilitas |
| "copy paste", "plagiat", "sumbernya?" | **kritis** | risiko akademik |
| "rumusan", "metode", "pembahasan" | tinggi | mengubah struktur/logika |
| "kurang dalam", "tambah", "perdalam" | tinggi | menambah isi |
| "sebaiknya", "coba pertimbangkan" | disarankan | bisa dikerjakan atau ditolak beralasan |
| "kayaknya", "coba pikir lagi", "kurang cocok" | **klarifikasi** | ambigu — tanya dulu |
| "spasi", "margin", "garis", "font", "nomor" | rendah | format, kerjakan terakhir |

Klasifikasi otomatis di skrip memakai daftar ini, tapi **selalu periksa manual**. Contoh
yang sering salah: "coba pikir lagi" bisa berarti wajib (pembimbing tidak mau bilang
langsung bahwa metodenya salah).

## Kapan wajib bertanya

Tanya **sebelum** mengerjakan bila:

1. Catatan memakai kata penilaian tanpa objek: "kurang", "belum pas", "aneh".
2. Catatan menyebut bagian yang tidak ada di naskah ("tabel 3.4" padahal hanya ada 3.1–3.3).
3. Dua catatan bertentangan ("persingkat bab 1" + "latar belakang kurang lengkap").
4. Catatan mengarah ke perubahan metode setelah data terkumpul.

Format bertanya yang efisien — satu pesan, tiga pertanyaan maksimal:

```
Selamat pagi Pak/Bu. Saya ingin memastikan tiga catatan dari bimbingan kemarin:

1. "metode kurang cocok" — apakah yang perlu diubah teknik analisisnya,
   atau cara penarikan sampelnya?
2. "tabel 3.4" — di naskah saya hanya ada Tabel 3.1 sampai 3.3. Apakah
   maksudnya Tabel 3.3?
3. "persingkat bab 1" dan "latar belakang kurang lengkap" — mana yang
   lebih diprioritaskan?

Terima kasih.
```

Jangan mengirim 8 pertanyaan sekaligus. Pembimbing tidak akan menjawab.

## Setelah bimbingan: 30 menit pertama

Ini yang menentukan apakah catatan selamat atau hilang:

```
0–10 menit   transkrip semua catatan ke 00_catatan_mentah.md apa adanya
10–20 menit  pecah jadi butir: python3 scripts/parse_revisi.py
20–30 menit  tandai butir klarifikasi, susun pesan pertanyaan
```

Kalau ditunda dua hari, 30% catatan hilang — terutama yang lisan.

## Tanda daftar kerja lo sudah benar

- Setiap butir bisa dijawab "selesai" dengan satu bukti terukur.
- Butir kritis ≤ 5. Kalau lebih dari 10, kemungkinan lo memecah terlalu halus dan tidak
  akan selesai.
- Tidak ada butir yang isinya "perbaiki bab X" tanpa keterangan apa yang diperbaiki —
  itu masih klarifikasi.
