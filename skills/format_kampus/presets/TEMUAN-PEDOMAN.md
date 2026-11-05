# Temuan Pembacaan Pedoman Resmi

Catatan jujur tentang **apa yang benar-benar terbaca** dari pedoman resmi, dibuat
5 November 2026. Dibaca lewat WebFetch (model ringkas), bukan dari berkas utuh di disk:
shell sandbox tidak bisa menjangkau situs kampus. Karena itu semua angka di sini
**perlu dicocokkan** dengan PDF aslinya sebelum dicetak. Tanda `TIDAK DITEMUKAN`
berarti bagian itu tidak ada dalam teks yang terbaca, bukan bahwa pedomannya tidak
mengaturnya.

| Kampus | Dokumen | Terbaca | Tidak terbaca |
|---|---|---|---|
| UNHAS | Keputusan Rektor No. 10438/UN4.1/KEP/2023 (28 Okt 2023), Pedoman Penulisan Tugas Akhir Mahasiswa | kertas **B5 176×250 mm** (4.1.1); APA sistem Harvard (4.2.2 h); **"et al., bukan dkk"** (hlm. 31); penulis > 6: sebut 6 lalu et al. (hlm. 30); wajib reference manager (hlm. 31); abstrak skripsi maks. 250 kata (4.1.7); ucapan terima kasih skripsi maks. 1 halaman (4.1.6); indentasi paragraf "ketukan kelima atau 1,25 mm" (3.4, hlm. 11 — kemungkinan salah ketik untuk cm, **jangan dipakai**) | margin kiri/kanan (5.1.2), font dan spasi isi (5.1.1, 5.1.6), kutipan panjang (5.8), nomor halaman isi (5.7.1), caption (5.4), isi sitasi (5.5.2) — hanya judul subbab yang terbaca |
| IPB | Pedoman Penulisan Karya Ilmiah Tugas Akhir Mahasiswa, Edisi ke-4, IPB Press, Des 2019 (Peraturan Rektor 27/IT3/PP/2019) | abstrak maks. 200 kata, satu halaman untuk dua bahasa (3.1.4 c); tabel dan gambar harus dirujuk di teks (3.2.5.1 butir 4); tinjauan pustaka maks. 10% halaman bagian utama; susunan bagian awal/utama/akhir | **margin, font, spasi, caption, gaya sitasi** — format pengetikan ada di lampiran/bab yang terpotong pada teks yang terbaca |
| UI | Pedoman Penulisan Tugas Akhir | **tidak terbaca**: URL tidak ada di allowlist; pencarian tidak menemukan PDF resmi yang bisa dibuka | semuanya |
| ITB, UGM | — | tidak ditemukan PDF pedoman tingkat universitas yang bisa dibuka | semuanya |

## Dampak pada preset

- `unhas.yaml`: `ukuran_kertas` dikoreksi A4 → **B5**. Sebelumnya konverter membaca
  "B5 (...) bukan A4" sebagai A4 karena mengambil kata kunci pertama di daftarnya,
  bukan yang pertama muncul di teks (diperbaiki di `campus_json2yaml.py`). Margin
  kiri/kanan tetap `null`.
- UNHAS memakai **"et al." dan melarang "dkk"**, kebalikan dari ARS yang melarang
  keduanya di Daftar Pustaka. Aturan *et al* memang berbeda antar kampus; jangan
  menyeragamkan.
- IPB: margin/spasi/sitasi tetap kosong. Preset IPB belum bisa diisi dari sumber
  yang terbaca; butuh PDF utuh dari pengguna.

## Cara menaikkan tingkat verifikasi

Kirim PDF utuh pedoman fakultas Anda ke percakapan. Dengan berkas di disk, teksnya
bisa diekstrak penuh (`pdftotext -layout`) dan tiap angka dikutip dengan nomor butir
seperti pada `ars-fti.yaml`, tanpa perantara model ringkas.
