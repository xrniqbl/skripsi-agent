# Panduan Revisi — Humanizer & Penyuntingan Draft (Layer 1)

Pandu menemukan dan memperbaiki **25 pola tulisan khas AI** pada naskah proposal, lalu
menyunting draft secara utuh. Diadaptasi dari [blader/humanizer](https://github.com/blader/humanizer)
(27 pola), [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
(WikiProject AI Cleanup), dan **praktik penyuntingan** yang lazim pada tulisan akademik Indonesia.

> **Bedakan dengan EYD check** (`references/eyd-check.md`): humanizer menangani *gaya
> khas AI*; EYD menangani *kebenaran bahasa* (baku/tidak baku, tanda baca, kapitalisasi).
> Keduanya boleh menemukan hal yang sama, tapi tujuannya berbeda.

## Filosofi

Tulisan AI cenderung memilih frasa berpeluang tertinggi yang cocok untuk **semua** pembaca,
sehingga terdengar generik dan berlapis. Manusia menulis untuk **satu** pembaca dan **satu**
topik. Tiap pola di bawah adalah satu bentuk pilihan generik itu.

**Dua aturan:**
1. Setiap kalimat yang dipertahankan harus menambah sesuatu yang belum dimiliki pembaca.
2. Untuk pola bernomor §1–§5, **satu temuan sudah cukup** untuk mengedit; pola bertanda
   *lemah sendiri* baru acted upon bila beberapa temuan berkumpul di satu bagian.

> **Aturan keselamatan**: jangan mengubah makna, jangan menambah fakta/angka/sitasi.
> Nama, angka, tanggal, kutipan, dan `[L-n]` harus berasal dari naskah & sumber pengguna.

---

## Alur Revisi

1. **Tandai pola.** Baca seluruh teks sekali, tandai semua pola, dari yang terkuat. Perhatikan
   bentuk paragraf, bukan hanya kalimat.
2. **Tulis ulang.** Pertahankan **semua** klaim yang didukung sumber. Boleh diperpendek,
   digabung, atau dipecah. Jangan menambah fakta; bila detail dibutuhkan tapi belum ada → tanya.
3. **Periksa draf.** Baca keras; tanya: apa yang masih terdengar seperti AI? Apakah ada
   klaim/fakta yang bertambah atau hilang? Perhatikan lima pola yang paling sering terlewat:
   bukan-X-melainkan-Y, penutup satu baris, tanda pisah, triada, label tebal.
4. **Tulis versi final.** Sampaikan poin secara natural; **jangan** menambal kata satu per satu.
   Variasikan ritme kalimat pendek-panjang (tulisan manusia berselang-seling).

> Perbedaan dari penulisan paper: proposal adalah **dokumen administratif** yang dibaca
> pembimbing sebagai pembaca pertama. Nada-held, angka, dan `[L-n]` tidak boleh hilang
> demi gaya — yang boleh dirapikan adalah kalimat pembuka, pengulangan, dan pemenggalan.

---

## A. Bertahap alih-alih, bukan menyatakan (§1–§5) — AKTIF pada 1 temuan

### §1 Bukan X melainkan Y
- Pola: "bukan hanya X, tetapi juga Y"; "ini bukan berarti X, melainkan Y"; bentuk terbalik
  "X, bukan Y"; terpecah jadi dua kalimat "Ini bukan X. Ini Y."
- **Masalah**: separuh negatif menyebut sesuatu yang tidak pernah diklaim orang → separuh positif
  terdengar lebih besar tanpa menambah fakta.
- **Perbaikan**: nyatakan langsung; pertahankan kontras hanya bila separuh negatif memang
  mengoreksi keyakinan yang benar-benar dipegang pembaca.
- Contoh: "Penelitian ini bukan sekadar kontribusi teoretis." → "Penelitian ini memperluas
  teori X dengan menambahkan moderator M."

### §2 Penutup satu baris & fragmen dramatis
- Pola: paragraf satu kalimat yang mengulang poin sebelumnya; "Dan itulah inti temuan ini.";
  "Tidak ada garis dasar sebelumnya."; HURUF BESAR.
- **Perbaikan**: hapus penutup yang hanya mengulang; gabungkan fragmen ke kalimat yang
  membawa klaim konkret.
- Catatan proposal: kalimat penutup bab memang lazim ("Bab II telah menyajikan landasan
  teori..."), tetapi **jangan** menutupi subbab dengan mengulang poin di paragraf terakhir.

### §3 Ucapan yang terdengar dalam
- Pola: "Pada intinya, hal terpenting adalah..."; "X adalah bahasa dari Y"; "kunci dari
  segalanya".
- **Perbaikan**: ganti aphorisme dengan klaim konkret (dengan `[L-n]` atau `[D:kolom]`).

### §4 Building-up bertingkat
- Pola: "Mari kita lihat...", "Perlu dicatat bahwa", "Pada bagian ini akan dibahas".
- **Perbaikan**: langsung ke inti. Kecuali penanda struktural yang sah (mis. "Subbab ini
  menguraikan..."), dan itu pun cukup satu kali di awal subbab.

### §5 Berdebat tanpa lawan
- Pola: "Ini bukan tentang X", "Saya tidak mengklaim...", " Sebagian orang mungkin akan
  berkeberatan, tetapi...", "Terlihat menggoda untuk memakai Y, tetapi...".
- **Perbaikan**: hapus sikap defensif; bila memuat klaim nyata, nyatakan langsung. Pertahankan
  pendapat yang memang dibahas lengkap dalam teks.

---

## B. Ritme according to rule (§6–§11) — lemah sendiri

### §6 Triada paksa
- Pola: "inovasi, inspirasi, dan insight"; tiga contoh paralel diikuti kesimpulan.
- **Periksa** apakah tiga butir benar-benar dibutuhkan. Jika tidak → gabung/simpan yang kuat.
- Khas proposal: "sikap, perasaan, dan perilaku" → sering sebenarnya hanya dua.

### §7 Awal kalimat berulang
- Pola: beberapa kalimat berturut-turut diawali subjek/konjungsi yang sama ("Hasil menunjukkan
  bahwa... Hasil menunjukkan bahwa...").
- Gabung atau ganti subjek. (Pengulangan yang disengaja untuk ritme tetap boleh.)

### §8 Tanda pisah sebagai konektor universal
- **Aturan**: versi final tidak boleh memuat em-dash (—) / en-dash (–) sebagai penghubung
  di dalam kalimat naratif. Ganti dengan titik, koma, titik dua, atau tanda kurung.
- Pengecualian: tanda pisah di dalam kode, path, URL, dan kutipan langsung.
- Untuk Bahasa Indonesia, tanda pisah yang lazim adalah **tanda hubung** (`-`) untuk kata
  ulang dan partikel (`memperhatikan-perhatian`), bukan em-dash.
- **Perhatikan skill ini sendiri**: pola ini berlaku untuk naskah user, bukan untuk tabel/
  diagram instruksional di dalam skill.

### §9 Penumpuk kualifier
- Pola: "mungkin-mungkin diharapkan dapat", "kemungkinan besar dapat".
- Simpan hanya kualifier yang didukung sumber. *Lemah sendiri.* (Kebiasaan manusia seperti
  "mungkin", "agaknya" bukan pola.)

### §10 Pasangan berimbuhan di mana-mana
- Pola: "cross-functional", "data-driven", "real-time" di setiap posisi; Bahasa Indonesia:
  "ber-orientasi", "ter-integrasi", "non-formal" berlebihan.
- Gunakan tanda hubung hanya bila tata bahasa menuntutnya (sebelum kata benda): "laporan
  berkualitas tinggi" vs. "mutu laporannya tinggi". *Lemah sendiri.*

### §11 Kalimat pasif & subjek hilang
- "Tidak diperlukan berkas konfigurasi" → "Anda tidak memerlukan berkas konfigurasi."
  Sebut pelaku bila membantu. *Lemah sendiri.* (Baca gate mekanis untuk aturan lebih ketat.)

---

## C. Inflasi & otoritas yang dipinjam (§12–§18)

### §12 Kata AI yang dipakai berlebihan
Kata yang sering dipakai model (dalam tulisan akademik):
*menyoroti, mendalami, multidimensional, transformatif, memperkuat, memperkaya, menavigasi,
pemandangan (kata benda abstrak), krusial, penting,mikan contoh, menegaskan, menyoroti,
pada dasarnya, bermakna.*

Frasa yang perlu diawasi: "mendalam", "tidak sekadar", "sangat penting", "telah terbukti
menunjukkan".

- **Ini satu-satunya daftar kosakata di skill ini.** Ganti dengan kata sehari-hari yang spesifik.
- Pengecualian istilah metode: bila penulisan memang **wajib** memakai istilah asing
  (mis. *grounded theory*, *purposive sampling*), pertahankan — italic pada penyebutan pertama.

### §13 Signifikansi yang digelembungkan
- Pola: "menandai momen penting", "memiliki peran penting", "meletakkan fondasi untuk",
  "masa depan yang cerah"; seksi "Kontribusi dan Tantangan" yang generik.
- Pertahankan faktanya, buang klaimnya; tutup dengan fakta konkret terakhir.

### §14 Keterhubungan yang kabur
- Pola: "berhubungan dengan", "terhubung dengan", "berasosiasi dengan" tanpa menyebut sifat
  hubungan.
- Tulis hubungan seperti sumber menyebutnya; bila tidak ada → biarkan kabur, jangan dikarang.

### §15 Partisip -ing yang dangkal
- Pola: "mencerminkan", "menunjukkan", "memastikan", "melambangkan" yang menempel pada fakta
  sederhana.
- Simpan faktanya; simpan rider hanya bila didukung sumber.

### §16 Bahasa promosi
- Pola: "luar biasa", "sangat kaya", "mendalam", "menyeluruh" (tanpa angka).
- Nyatakan sebagaimana adanya.

### §17 Otoritas yang dipinjam
- Pola: "para ahliosus", "ikut dikutip di Nature, Science, dan NYT" (daftar prestise),
  "aktif di media sosial dengan N pengikut" (di CV/profil).
- Tulis sumber konkret dan apa yang dikatakannya; bila tidak → hapus.

### §18 Menghindari adalah/ada/memiliki
- Pola: "berfungsi sebagai", "menyajikan", "menampilkan", "menawarkan" → "adalah", "memiliki".
- "Tabel 3 berfungsi sebagai ringkasan hasil." → "Tabel 3 merangkum hasil."

---

## D. Formatting menurut aturan (§19–§21)

### §19 Tebal sebagai hiasan
- Pola: label tebal + titik dua; istilah ditebalkan tanpa alasan.
- Hapus tebal hiasan; ubah daftar berlabel menjadi prosa bila labelnya tidak membawa informasi.

### §20 Judul dekoratif & emoji
- Pola: judul Title Case yang berlebihan; emoji, panah di judul; garis pemisah horizontal
  antar-bagian.
- Gunakan **sentence case** untuk subbab; hapus emoji/panah; satu H1 saja.

### §21 Tanda kutip melengkung (lemah sendiri)
- Konversi kutip melengkung ke gaya naskah yang konsisten, atau biarkan mengikuti konvensi
  kampus.

---

## E. Sisa dari chat & draf (§22–§25)

Hapus seluruhnya; tidak perlu ditulis ulang.

### §22 Sisa percakapan dengan bot
- "Semoga membantu!", "Tentu!", "Pertanyaan bagus!", "Apakah Anda ingin...", "Berikut adalah...".
- Buang pembungkusnya, pertahankan isinya.

### §23 Penegakan batas pengetahuan & tebakan
- "Berdasarkan informasi yang tersedia", "tampaknya didirikan pada 1990-an", "informasi
  tentang hidupnya tidak dipublikasikan... mungkin".
- Nyatakan apa yang tidak ditunjukkan sumber, atau hapus kalimatnya. **Jangan pernah**
  menyajikan tebakan sebagai fakta.

### §24 Judul yang diulang di kalimat pertama
- "## Hasil\n\nHasil penelitian menunjukkan..." → hapus kalimat pengulangan.

### §25 Menulis tentang versi sebelumnya
- "Perbaikan ini menggantikan pendekatan lama yang lebih lambat..." → deskripsikan apa yang
  dilation sekarang, bukan versi lama (kecuali di changelog).

---

## Kapan TIDAK Mengedit

- Kutipan langsung, judul, nama diri — biarkan.
- Pola *lemah sendiri* hanya berlaku bila beberapa temuan berkumpul di satu bagian.
- Teks yang ditulis sebelum 30 November 2022 tidak otomatis "ditulis AI" hanya karena gayanya.
- Salam dan penutup resmi.

## Rincian yang Harus DIPERTAHANKAN (ciri suara)

- Detail spesifik & tidak biasa (lokasi, kutipan aneh)
- Ketegangan yang belum selesai, perasaan yang bercampur
- Bahasa yang terikat zaman (slang, lelucon tahun tertentu)
- Pilihan orang pertama yang bisa dijelaskan penulis
- S aside/koreksi diri yang jujur

## Larangan khusus proposal

Berlaku di atas semua aturan gaya:

1. **Jangan** menghapus `[L-n]`, `[D:kolom]`, `[K-n]`, `[U]` saat merapikan kalimat.
2. **Jangan** menghapus angka untuk membuat kalimat lebih ringkas — pindahkan ke klausa
   sebelumnya bila perlu.
3. **Jangan** mengubah rumusan masalah, tujuan, atau hipotesis saat revision gaya; itu isi,
   bukan gaya. Perubahan isi harus lewat gate Step 3/4.
4. **Jangan** menyamakan nada dengan proposal lain. Variasikan ritme, bukan meniru sumber.

## Checklist pemakaian

Gunakan `checklists/humanizer_checklist.md` untuk laporan pola yang ditemukan vs diperbaiki.

## Sumber

Pola berasal dari [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
(WikiProject AI Cleanup) dan adaptasi [blader/humanizer](https://github.com/blader/humanizer).

---

Lanjut ke `quality-gates.md` untuk Layer 2–4 (gate mekanis, semantik, red-team).
