---
name: integritas_akademik
description: Menjaga integritas akademik naskah skripsi/tesis/artikel Indonesia yang dibantu AI — pernyataan penggunaan AI (acknowledgment), larangan AI sebagai penulis, verifikasi referensi, kerahasiaan data responden, dan sisa artefak chatbot di naskah. Gunakan saat naskah dibuat atau disunting dengan bantuan AI, saat pengguna bertanya "boleh pakai AI untuk skripsi?", atau sebelum naskah dinyatakan selesai (jalankan scripts/cek_integritas_ai.py).
---

# Integritas Akademik — Penggunaan AI dalam Skripsi

Bundel ini sendiri adalah alat berbasis AI, jadi pengguna berhak mendapat jawaban
jujur tentang batasnya. Skill ini memegang tiga hal: **apa yang diatur**, **apa yang
harus tertulis di naskah**, dan **apa yang diperiksa sebelum dikumpulkan**.

Dasar aturan dan tingkat verifikasinya ada di `references/regulasi.md`. Untuk penelitian dengan responden manusia, lihat juga `references/kaji-etik.md`. Baca berkas itu
sebelum mengutip pasal kepada pengguna — beberapa rujukan baru terverifikasi sebagian
dan ditandai demikian.

## Aturan yang tidak ditawar

1. **AI bukan penulis.** Nama alat AI tidak pernah masuk kolom penulis/pengarang.
   (Peraturan Rektor UI 16/2025 Pasal 5 huruf a menegaskannya; pola yang sama lazim
   di kampus dan penerbit lain, tetapi periksa aturan kampus pengguna.)
2. **Transparan.** Penggunaan AI diungkapkan dalam naskah. Peraturan Rektor UI 16/2025
   Pasal 4 huruf a mewajibkan *acknowledgment*, tetapi **tidak menetapkan format dan
   letaknya** — itu diserahkan ke fakultas (Pasal 6). Jadi: tanyakan ketentuan
   fakultas pengguna; selama belum ada, pakai templat di `references/pernyataan-ai.md`
   dan sampaikan bahwa letaknya belum terkunci kampus.
3. **Manusia memverifikasi.** Setiap klaim, angka, dan referensi keluaran AI diperiksa
   ke sumber primer. AI dapat menghasilkan referensi yang tidak ada. Jalankan
   `skills/proposal_skripsi/scripts/verify_doi.py` dan `periksa_pustaka.py`.
4. **Data responden tidak masuk ke AI** tanpa izin: nama, kontak, transkrip wawancara
   mentah, data kesehatan. Anonimkan dulu. (Panduan GenAI Kemendikbudristek 2024
   mencantumkan memasukkan data pribadi/sensitif tanpa izin sebagai hal yang dihindari.)
5. **Tidak menyembunyikan.** Menyembunyikan penggunaan AI pada karya dapat dikaitkan
   dengan plagiarisme (Panduan GenAI Kemendikbudristek 2024, Tabel 3.1).
6. **Kemiripan tetap diuji.** Teks AI bisa mirip sumber yang melatihnya; uji kemiripan
   dengan layanan resmi kampus (Peraturan Rektor UI 16/2025 Pasal 4 huruf d).

## Alur

1. **Tanyakan** kampus, fakultas, dan apakah ada pedoman AI tingkat universitas/
   fakultas/prodi, serta apakah pembimbing punya batas sendiri. Pedoman kampus dan
   pembimbing mengalahkan skill ini.
2. **Catat penggunaan AI sejak awal**: alat, versi/tanggal, tujuan, bagian naskah.
   Mencatat belakangan hampir selalu tidak lengkap.
3. **Susun pernyataan** dari `references/pernyataan-ai.md`. Isi hanya fakta yang
   diberikan pengguna — jangan menebak alat atau bagian yang dibantu AI.
4. **Jalankan pemeriksa**:

   ```bash
   python3 skills/integritas_akademik/scripts/cek_integritas_ai.py naskah.docx \
       --profil profil-kampus.yaml
   ```

   Ia memeriksa: pernyataan ada atau tidak, tiga unsurnya (alat, tujuan/bagian,
   verifikasi), AI di kolom penulis, dan artefak chatbot yang tertinggal ("Sebagai
   model bahasa…", `oaicite`, `utm_source=chatgpt.com`).
5. **Verifikasi referensi** satu per satu (lihat aturan 3).

## Kunci profil (opsional)

Tambahkan di `profil-kampus.yaml` hanya bila panduan kampus mengaturnya:

```yaml
integritas:
  pernyataan_ai: wajib        # wajib | dianjurkan | tidak_diatur
  letak_pernyataan: null      # mis. "setelah Kata Pengantar" — isi bila panduan menyebut
  sumber: null                # nama dokumen + pasal
```

- `wajib` → pernyataan yang hilang menjadi **galat**.
- `dianjurkan` atau kunci tidak ada → **peringatan**.
- `tidak_diatur` → hanya catatan informasi.

## Batasan

- Pemeriksa adalah **pemeriksa pola**. Ia tidak bisa membuktikan sebuah naskah bebas
  dari AI maupun menebak apakah AI dipakai. "Tidak ada temuan" bukan "tidak ada AI".
- Pemeriksa tidak menilai kejujuran isi pernyataan; itu tanggung jawab penulis.
- Ini bukan nasihat hukum atau keputusan etik. Sengketa integritas diputus oleh
  kampus melalui mekanismenya sendiri.
