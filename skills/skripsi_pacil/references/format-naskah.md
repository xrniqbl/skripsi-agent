# Format naskah dan pemeriksaan tampilan

Baca untuk memeriksa tata letak aktual. Jangan menyatakan font, margin, halaman, atau hasil ekspor telah sesuai hanya dari teks Markdown.

## FMT-01. Kertas, huruf, paragraf, dan heading

**[KETENTUAN]**

| Elemen | Ketentuan |
|---|---|
| Kertas | HVS putih 70 gram, A4 21,0 x 29,7 cm |
| Huruf isi | Times New Roman 12 pt |
| Paragraf | Rata kanan-kiri; baris pertama masuk 1,27 cm; sebelum 0 pt dan sesudah 0 pt; minimal tiga kalimat |
| Heading level 1 | Judul bab, Times New Roman 14 pt, tebal, seluruhnya kapital, rata tengah |
| Heading level 2 | Subbab, Times New Roman 13 pt, tebal, kapital awal setiap kata menurut profil akademik, rata kiri; nomor `3.1` |
| Heading level 3 | Sub-subbab, Times New Roman 13 pt, tebal, kapitalisasi kalimat, rata kiri; nomor `3.1.1` |
| Kedalaman | Maksimal tiga level; jangan membuat `3.1.1.1` |
| Margin | Atas 3 cm, bawah 3 cm, kiri 4 cm, kanan 3 cm; profil akademik meminta *mirror margin* |
| Spasi utama | 1,5 untuk isi Bab I-V, kata pengantar, daftar isi, serta daftar tabel/gambar |
| Spasi khusus | Satu untuk abstrak, judul tabel/gambar, dan daftar pustaka |
| Jarak judul bab | Tiga spasi ke teks/subbab pertama sebagaimana profil akademik; jangan menebak konversi pt tanpa memeriksa hasil templat |

**[KONFIRMASI]** Untuk penerapan *mirror margin*, padanan operasional umumnya sisi dalam 4 cm dan sisi luar 3 cm, dengan atas/bawah 3 cm. Periksa hasil halaman ganjil/genap terhadap templat prodi; jangan menerapkan kiri 4 cm pada seluruh halaman lalu mengaku sudah mencerminkan margin cermin.

## FMT-02. Halaman dan bagian baru

**[KETENTUAN]** Cover tidak diberi nomor halaman. Bagian awal memakai angka Romawi kecil, sedangkan Bab I dimulai dengan angka Arab 1 yang berlanjut sampai bagian akhir. Nomor diletakkan di tengah bawah menggunakan Times New Roman 12 pt.

Mulai lembar judul dan bagian berikutnya, bab atau bagian baru harus dimulai pada halaman ganjil. Jika bagian sebelumnya berakhir pada halaman ganjil, sisipkan halaman genap kosong yang tetap dihitung dan tetap bernomor. Letakkan kalimat *Halaman ini sengaja dikosongkan.* di tengah halaman dengan huruf miring.

Gunakan pemisah bagian dan penomoran otomatis dalam pengolah kata. Jangan mengetik nomor halaman atau daftar isi secara manual. Markdown tidak menyimpan margin, nomor halaman, atau ukuran huruf Word; keberadaan aturan di file `.md` bukan bukti bahwa berkas akhir sudah memenuhi tata letak.

## FMT-03. Tabel, gambar, dan persamaan

**[KETENTUAN]** Nomor mengikuti bab dan urutan masing-masing jenis, misalnya `Tabel 4.1`, `Gambar 4.1`, dan `(4.1)` untuk persamaan. Judul tabel berada di atas tabel; judul gambar berada di bawah gambar. Caption Times New Roman 12 pt, normal, rata tengah, satu spasi, tanpa titik penutup.

Isi tabel menggunakan ukuran 10 pt dan satu spasi. Header berwarna RGB(217, 217, 217), setara `#D9D9D9`, dan diatur berulang pada halaman lanjutan. Kolom harus memiliki nama dan pemisah yang jelas. Hindari memotong tabel yang sebenarnya masih dapat dimuat utuh pada satu halaman.

Untuk tabel panjang, halaman lanjutan mencantumkan nomor tabel dan kata "lanjutan" tanpa mengulang judul lengkap. Gunakan orientasi lanskap bila perlu, dengan bagian atas tabel/gambar mengarah ke sisi kiri kertas sesuai profil akademik. Jangan mengecilkan teks sampai tidak terbaca hanya untuk memaksakan satu halaman.

Letakkan nomor persamaan dekat margin kanan. Definisikan semua simbol baru, indeks, satuan, dan batas penjumlahan. Gunakan objek persamaan yang dapat disunting, bukan tangkapan layar buram. Periksa bahwa penomoran dan penyebutan dalam paragraf tetap cocok setelah menyisipkan rumus baru.

**[PRAKTIK]** Semua tabel/gambar harus dirujuk dan dibahas, memiliki satuan yang cukup, serta tidak memuat identitas sensitif tanpa izin. Gunakan visual berkualitas baca; grafik harus menunjukkan label sumbu, legenda bila perlu, dan skala yang tidak menyesatkan. Jangan mengganti tabel hasil yang seharusnya berupa teks dengan screenshot notebook.

## FMT-04. Cover dan lembar resmi

**[KETENTUAN]** Cover proposal dicetak pada A4 70 gram dan cover skripsi berupa softcover; cover tidak dicetak bolak-balik. Jangan menafsirkan aturan cover tersebut sebagai izin mengabaikan pengaturan halaman isi.

Anotasi contoh cover memperlihatkan logo 4 x 4 cm, warna oranye `#ff914d`, dan kuning `#f4ff00`. Label SKRIPSI, nama mahasiswa, dan DOSEN PEMBIMBING menggunakan Arial tebal 14 pt; judul Arial tebal 18 pt; NPM dan nama pembimbing Arial 14 pt; blok institusi Arial tebal 12 pt rata kiri. Ikuti templat resmi untuk posisi dan detail grafis, serta periksa konflik kapitalisasi yang dicatat pada catatan konflik di modul aturan akademik.

Isi cover harus mengikuti identitas aktual: judul yang disetujui, nama, NPM, pembimbing, kementerian/institusi, Fakultas Ilmu Komputer, Program Studi Sistem Informasi, Surabaya, dan tahun yang benar. Jangan menyalin nama, gelar, jabatan, prodi Informatika, atau tahun pada contoh. Nama kementerian dan pejabat dapat berubah sehingga perlu diverifikasi untuk dokumen yang akan disahkan.

Lembar pengesahan dan persetujuan mengikuti susunan resmi dan ketentuan cetak timbul profil akademik. Pedoman menyebut latar logo berukuran 13,74 x 14,02 cm. Pernyataan orisinalitas mengikuti formulir resmi dan memerlukan meterai sesuai ketentuan; jangan menambahkan tanda tangan atau stempel digital buatan.

## FMT-05. Jumlah halaman dan pemeriksaan hasil ekspor

**[KETENTUAN]** Bagian inti Bab I-V berkisar 90-150 halaman. Ketentuan ini bukan jumlah seluruh halaman PDF. Bahan rinci yang menyebabkan kelebihan dapat ditempatkan di lampiran atau buku berbeda sesuai profil akademik dan arahan prodi.

**[PRAKTIK]** Jangan memenuhi rentang halaman dengan spasi tambahan, definisi berulang, gambar yang diperbesar tanpa fungsi, atau pemecahan bab yang tidak perlu. Setelah ekspor, periksa halaman ganjil, daftar isi, caption, pemisahan tabel, rumus, halaman kosong, font, dan tautan silang. Jangan menyatakan "format sudah sesuai" jika hanya teks Markdown yang diperiksa.
