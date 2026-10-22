---
name: bahasa_akademik
description: Menjaga naskah skripsi/tesis/artikel berbahasa Indonesia tetap dalam ragam akademik baku sesuai EYD/PUEBI. Gunakan saat menulis, menyunting, atau memeriksa naskah akademik Bahasa Indonesia — sebelum dokumen dinyatakan selesai, jalankan pemeriksa scripts/cek_bahasa.py dan perbaiki temuannya mengikuti references/pedoman-bahasa-akademik.md.
---

# Bahasa Akademik — Ragam Baku untuk Naskah Ilmiah Indonesia

Naskah ilmiah ditulis dalam ragam bahasa Indonesia akademik yang baku, lugas, dan
tidak ambigu. Skill ini adalah lapisan bahasa untuk seluruh bundel: skill penulisan
mana pun yang menghasilkan teks Indonesia wajib tunduk pada pedoman di sini.

## Aturan Inti (ringkasan — rincian di references/pedoman-bahasa-akademik.md)

1. **Baku dan sesuai EYD**: kata baku (analisis, hipotesis, metode, sistem, jadwal),
   imbuhan dan kata depan ditulis benar (`di` pasif disambung, `di` tempat dipisah),
   tanda baca dan huruf kapital mengikuti kaidah.
2. **Tanpa orang pertama/kedua**: jangan memakai *saya, kami, kita, Anda, penulis
   berharap*. Subjek kalimat adalah penelitian, data, atau objeknya: "Penelitian ini
   mengkaji …", "Data menunjukkan …", "Berdasarkan Tabel 3.1, …". Istilah "penulis"
   hanya bila perlu dan tetap orang ketiga.
3. **Kalimat efektif**: satu gagasan utama per kalimat, hindari kalimat majemuk
   bertingkat yang berbelit, hindari pengulangan "yang" berantai dan kata mubazir
   (demi untuk → untuk; agar supaya → agar; sangat … sekali).
4. **Tanpa ragam lisan/gaul**: tidak ada kata seperti *banget, nggak, bikin, kayak,
   jadi* sebagai penghubung longgar, atau *makanya*. Gunakan padanan bakunya.
5. **Istilah konsisten**: satu konsep satu istilah di seluruh naskah; istilah asing
   yang belum ada padanannya ditulis miring; singkatan dijelaskan saat pertama muncul.
6. **Klaim terukur (hedging akademik)**: nyatakan temuan sesuai kekuatan bukti —
   "menunjukkan", "mengindikasikan", "berkaitan dengan" — jangan mengklaim sebab
   mutlak dari data korelasional, dan jangan menjanjikan dampak yang belum dibuktikan.
7. **Objektif dan tanpa emosi**: tidak ada kata evaluatif tanpa dasar ("sangat
   menarik sekali", "luarbiasa"), tidak ada retorika promosi.
8. **Angka dan sitasi tertib**: penulisan bilangan mengikuti kaidah (angka untuk
   nilai ukur dan penomoran; kata untuk awal kalimat), sitasi menyatu dalam kalimat
   secara konsisten dengan gaya yang dipilih (lihat profil format kampus).

## Alur Pemeriksaan (wajib sebelum dokumen dinyatakan selesai)

1. Jalankan pemeriksa mekanis pada naskah (DOCX atau Markdown/teks):

   ```bash
   python3 scripts/cek_bahasa.py naskah.docx
   # atau: python3 scripts/cek_bahasa.py naskah.md
   ```

   Pemeriksa menandai: kata ganti orang pertama/kedua, leksikon tidak baku dan
   ragam lisan, pleonasme umum, spasi ganda, dan pola kalimat bermasalah yang
   terdeteksi pola. Hasilnya daftar temuan per baris/paragraf, bukan vonis —
   nilai konteksnya.
2. Baca ulang temuan satu per satu; perbaiki yang memang menyimpang. Catat yang
   sengaja dipertahankan (mis. kutipan langsung dari responden — kutipan tidak
   diubah bahasanya).
3. Lakukan baca akhir khusus bahasa: satu putaran membaca hanya untuk bahasa
   (bukan isi), dari awal sampai akhir, sebelum audit format dijalankan.

## Batasan

- Pemeriksa bersifat pola (regex) — ia menangkap penyimpangan yang terdaftar,
  bukan menilai mutu argumentasi. Baca akhir oleh agent tetap wajib.
- Pedoman kampus dan dosen pembimbing mengalahkan skill ini bila berbeda
  (mis. kampus yang membolehkan "penulis" secara bebas).
