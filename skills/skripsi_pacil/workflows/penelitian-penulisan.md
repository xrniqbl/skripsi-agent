# Alur penelitian dan penulisan

Baca untuk merencanakan pekerjaan atau menghubungkan metode, hasil, dan sistem. POLA adalah susunan kerja yang dapat diadaptasi; PRAKTIK adalah perbaikan proses yang harus dibedakan dari kegiatan yang sudah dilakukan.

## ALUR-01. Tetapkan ruang kerja

**[POLA]** Jalankan skripsi sebagai rangkaian masalah, bukti, metode, hasil, pembahasan, dan luaran. Gunakan tahap yang telah tersedia; jangan memulai kembali seluruh proses hanya karena pengguna meminta satu revisi.

Tentukan tahap saat ini, topik, pertanyaan yang ingin dijawab, hasil yang diminta, dan bagian yang boleh diubah. Ambil informasi yang sudah tersedia terlebih dahulu. Ajukan pertanyaan hanya jika jawabannya dapat mengubah keputusan, data, metode, atau kepatuhan. Jangan meminta profil panjang pada setiap pemanggilan.

Pisahkan tiga jalur keputusan: keputusan yang telah disetujui, keputusan yang sedang diuji, dan perubahan yang baru diusulkan. Jangan mengubah jalur ketiga menjadi jalur pertama hanya karena perubahan tampak lebih baik.

## ALUR-02. Mulai dari masalah, bukan nama algoritma

Bangun alur: gambaran masalah -> rujukan utama -> calon judul -> pemeriksaan kemiripan judul -> draf proposal -> konsultasi -> perbaikan -> persetujuan -> seminar. Jika gambaran masalah belum jelas, lakukan konsultasi sebelum mengunci judul. Jangan melewati persetujuan pembimbing.

Gunakan masalah yang mempunyai objek, data atau bukti keadaan awal, kebutuhan, dan kemungkinan evaluasi. Pilih rujukan utama yang membantu desain skripsi, bukan hanya mempunyai judul mirip. Pisahkan kebutuhan praktis dari pertanyaan akademik; hubungkan keduanya tanpa membesar-besarkan manfaat.

Untuk pekerjaan tim atau pengembangan pekerjaan terdahulu, jelaskan bagian yang dipakai bersama, kontribusi baru, dan batas pekerjaan masing-masing. Jangan mengubah label proyek menjadi skripsi tanpa menjelaskan pengembangan.

## ALUR-03. Peta pertanyaan dan luaran

Gunakan matriks ringkas sebelum memperpanjang narasi.

| Pertanyaan | Bukti yang dibutuhkan | Bagian metode | Hasil | Batas kesimpulan |
|---|---|---|---|---|
| Bagaimana metode diterapkan pada masalah? | Data dan konfigurasi yang benar-benar dipakai | Pengolahan dan pemodelan/perancangan | Artefak atau hasil per tahap | Berlaku pada objek dan kondisi yang diperiksa |
| Bagaimana hasil metode dibandingkan? | Pembanding, protokol, dan metrik yang sebanding | Rancangan evaluasi | Tabel hasil dan analisis | Terbaik hanya dalam kelompok dan ukuran yang diuji |
| Bagaimana hasil digunakan dalam sistem? | Struktur masukan, proses, keluaran, dan bukti fungsi | Implementasi | Artefak dan pengujian sistem | Prototipe atau implementasi terbatas sesuai bukti |

**[POLA]** Tiga pertanyaan tersebut merupakan pola untuk skripsi komparatif dengan implementasi, bukan kewajiban memakai tepat tiga rumusan masalah. Gunakan pertanyaan berbeda untuk UI/UX, testing, proses bisnis, atau topik lain.

## ALUR-04. Jalur data, model, dan sistem

**[POLA]** Untuk pekerjaan berbasis data, gunakan susunan kerja berikut sebagai peta. Penamaan dan pembagian subbab dapat disesuaikan selama urutan operasional serta bukti tetap jelas.

| Tahap | Yang perlu dijelaskan | Bukti yang disiapkan |
|---|---|---|
| Studi literatur | Masalah, alasan metode, protokol evaluasi, gap | Catatan sumber, matriks What-Why-How-Result, sintesis |
| Analisis kebutuhan | Data, perangkat lunak, perangkat keras, pengguna bila ada | Tabel kebutuhan dan alasan pemilihan |
| Pengumpulan data | Sumber, periode, frekuensi, unit, izin, cara memperoleh | Contoh data, jumlah awal, catatan asal |
| Pemrosesan awal | Penyelarasan, duplikasi, nilai kosong, tipe data | Perubahan sebelum/sesudah dan alasan |
| EDA | Struktur, distribusi, tren, hubungan, anomali | Grafik/tabel dengan interpretasi terbatas |
| Pembagian data | Unit pemisahan, urutan, periode latih/validasi/uji | Jumlah dan batas masing-masing bagian |
| Pemodelan | Fitur, normalisasi, bentuk masukan, arsitektur | Tabel konfigurasi, bagan, penjelasan proses |
| Tuning dan pelatihan | Ruang pencarian, validasi, pemilihan, penghentian | Hasil percobaan dan konfigurasi terpilih |
| Pengujian/evaluasi | Metrik, satuan, jumlah sampel efektif, pembanding | Hasil numerik dan grafik sesuai protokol |
| Implementasi | Artefak model, transformasi, metadata, masukan, layanan, tampilan | Alur inferensi, tabel artefak, halaman fitur dan bukti uji |
| Pembahasan | Arti hasil, hubungan literatur, hasil tambahan, batasan | Jawaban pertanyaan dan dasar kesimpulan |

**[PRAKTIK]** Jangan menafsirkan urutan dokumentasi sebagai izin memakai seluruh data untuk keputusan pemodelan. Pisahkan pemeriksaan data awal dari transformasi yang mempelajari parameter. Fit transformasi pada data latih yang sesuai, termasuk di dalam validasi. Jika tahapan nyata berbeda dari bagan, catat perbedaannya dan revisi setelah bukti diperiksa.

## ALUR-05. Ubah keluaran teknis menjadi penjelasan

Untuk setiap tahap, tulis tujuan tahap, masukan, langkah, alasan, keluaran, dan pemeriksaan. Susun pembahasan dari hasil nyata, bukan dari definisi metode saja. Siapkan bukti sebelum menulis paragraf yang mengandung angka.

Gunakan urutan narasi: pengantar kebutuhan pembaca -> tabel/gambar/perhitungan -> pengamatan terukur -> interpretasi terbatas -> hubungan dengan tahap berikutnya. Jangan mengakhiri setiap gambar dengan kalimat manfaat yang sama. Pindahkan rincian berulang ke tabel atau lampiran, tanpa memindahkan temuan penting keluar pembahasan.

Untuk perhitungan manual, nyatakan input, simbol, bobot, asumsi, langkah, dan hasil. Tandai bobot ilustratif secara jelas. Ilustrasi mekanisme tidak menjadi validasi hasil model terlatih dan tidak menggantikan keluaran eksperimen.

## ALUR-06. Pisahkan evaluasi dari implementasi

Catat model atau artefak yang dievaluasi, kriteria pemilihan, transformasi masukan, urutan fitur, dan metadata. Hubungkan artefak tersebut dengan layanan dan tampilan yang benar-benar dibangun. Jangan memilih nama berkas final dari perkiraan.

Jelaskan masukan yang diperlukan sistem, penanganan masukan tidak lengkap, proses, keluaran, dan kondisi gagal. Untuk prediksi masa depan dengan variabel eksogen, nyatakan nilai yang diketahui, diasumsikan, atau diproyeksikan. Bedakan evaluasi historis dari inferensi operasional.

Pisahkan backend dan frontend dalam penjelasan jika implementasi memang demikian. Tidak ada kewajiban universal memakai Flask, React, arsitektur tertentu, panjang jendela tertentu, jumlah fitur tertentu, atau rasio data tertentu. Tetap gunakan nama dan nilai aktual ketika menjelaskan proyek yang bersangkutan.

## ALUR-07. Tulis sesuai kesiapan bukti

**[PRAKTIK]** Urutan bab akhir tetap baku, tetapi urutan menyusun draf dapat mengikuti kesiapan bukti. Bangun kerangka dan peta sumber; mantapkan Bab I-III bersama pembimbing; jalankan pekerjaan; tulis hasil per tahap; susun pembahasan; jawab rumusan masalah; sinkronkan abstrak terakhir. Ini rekomendasi kerja, bukan klaim bahwa setiap skripsi harus ditulis dalam kronologi yang sama.

Jika hasil tambahan berbeda dari dugaan awal, masukkan sebagai analisis tambahan yang jelas. Jangan memaksa variabel atau model tetap dianggap unggul ketika hasil yang tersedia tidak mendukungnya. Jika perubahan dapat mengubah fokus atau luaran yang disetujui, ajukan sebagai keputusan, bukan edit bahasa.

## ALUR-08. Bimbingan dan revisi

Catat masukan pembimbing/penguji, lokasi naskah, tindakan, bukti perubahan, dan bagian terkait. Bedakan masukan yang sudah dipenuhi, belum dipenuhi, dan memerlukan klarifikasi. Jangan menandai selesai hanya karena paragraf sudah diperpanjang.

Untuk revisi metode, periksa pula diagram, tabel konfigurasi, hasil, pembahasan, kesimpulan, dan abstrak. Untuk revisi sumber, periksa nomor sitasi, daftar pustaka, serta komposisi karya unik. Untuk revisi visual, periksa caption, narasi, dan daftar gambar/tabel.

Tutup pekerjaan dengan pemeriksaan sesuai lingkup. Jangan menyatakan seluruh skripsi siap sidang hanya karena satu bab telah diperbaiki.
