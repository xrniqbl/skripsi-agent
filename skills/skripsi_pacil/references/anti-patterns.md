# Anti-pattern dan pemeriksaan konsistensi

Gunakan sebagai daftar pemeriksaan sesuai masalah yang ditemukan, bukan alasan untuk mengubah semua bagian. Setiap dugaan memerlukan bukti; jangan menyimpulkan niat penulis atau salahnya seluruh skripsi.

**[PRAKTIK]** Gunakan tabel berikut sebagai daftar pemeriksaan lintasbab. Perbaikan harus mengatasi sumber masalah, bukan hanya mengganti kata.

| ID | Anti-pattern | Mengapa bermasalah | Tindakan yang benar |
|---|---|---|---|
| AP-01 | Latar belakang dibuka dengan uraian teknologi sangat umum dan panjang | Masalah objek tidak terlihat | Mulai dari konteks yang relevan lalu bukti masalah |
| AP-02 | Metode dipilih dahulu, masalah dibuat belakangan | Alasan metode menjadi pembenaran setelah keputusan | Uji kebutuhan dan alternatif sebelum menetapkan metode |
| AP-03 | "Belum pernah diteliti" tanpa log pencarian | Klaim cakupan terlalu luas | Batasi pada literatur dan periode penelusuran yang dilakukan |
| AP-04 | Mengganti objek lalu menyebutnya inovasi besar | Kontribusi tidak dijelaskan | Jelaskan perbedaan kebutuhan, data, evaluasi, atau penerapan |
| AP-05 | Bab II hanya daftar definisi | Tidak membangun dasar metode | Hubungkan teori dengan keputusan dan evaluasi skripsi |
| AP-06 | Tabel penelitian terdahulu tanpa sintesis | Hubungan dan gap tidak terlihat | Tambahkan perbandingan dan kesenjangan yang didukung |
| AP-07 | Semua sumber dipaksa lima tahun terakhir | Teori dasar dapat terhapus tanpa alasan | Terapkan ketentuan umur utama secara tepat; gunakan sumber dasar yang relevan |
| AP-08 | Mengutip sumber yang hanya terlihat pada bibliografi karya lain | Sumber belum diperiksa | Buka sumber asli atau ungkapkan kutipan sekunder |
| AP-09 | Merangkum angka dari abstrak/AI ketika tabel aslinya tersedia | Konteks dan satuan dapat hilang | Periksa tabel/figur asli dan kondisi evaluasinya |
| AP-10 | Menganggap logo SINTA/Scopus pada situs cukup | Identitas atau status dapat keliru | Verifikasi melalui pemilik indeks dan keputusan resmi |
| AP-11 | Menyamakan SJR Q2 dengan CiteScore Q2 | Sistem metrik berbeda | Catat sistem, tahun, dan kategori |
| AP-12 | Menyebut SINTA 4 memenuhi rujukan utama nasional | Bertentangan dengan ambang profil akademik | Jadikan pendukung; cari utama yang memenuhi syarat |
| AP-13 | Menganggap DOI menjamin artikel sahih | DOI bukan penilaian metodologi | Periksa identitas, jurnal, pembaruan, dan isi |
| AP-14 | Menganggap semua artikel pada penerbit besar cocok | Mutu dan relevansi tetap perlu dinilai | Nilai desain serta bukti artikel secara individual |
| AP-15 | Memilih kategori kuartil tertinggi yang tidak relevan | Dapat menyesatkan pembaca | Laporkan kategori yang digunakan dan alasannya |
| AP-16 | Memasukkan referensi lokal yang tidak relevan demi 20% | Sitasi menjadi kosmetik | Cari kontribusi FIK yang benar-benar berkaitan |
| AP-17 | Duplikasi satu DOI dalam beberapa nomor | Mengganggu penelusuran dan rasio referensi | Gabungkan rekaman dan perbarui nomor otomatis |
| AP-18 | Menyisipkan sitasi yang tidak mendukung klaim | Menimbulkan kesan ada bukti | Cocokkan setiap klaim dengan bagian sumber |
| AP-19 | Satu kalimat untuk seluruh subbab teori | Melanggar kedalaman pembahasan profil akademik | Kembangkan minimal dua paragraf bermakna pada Bab II |
| AP-20 | Setiap paragraf diawali "Berdasarkan" atau "Selain itu" | Alur terasa mekanis dan hubungan kabur | Pilih pembuka sesuai fungsi, atau mulai langsung dengan subjek |
| AP-21 | Semua "penelitian" diganti menjadi "skripsi" | Judul resmi dan jenis karya lain menjadi salah | Ganti hanya rujukan terhadap karya sendiri |
| AP-22 | Screenshot dijadikan satu-satunya hasil black-box | Respons uji tidak dijelaskan | Isi hasil diharapkan dan aktual sebagai narasi |
| AP-23 | Screenshot antarmuka disebut bukti usability | Belum mengukur pengalaman pengguna | Laporkan tugas, partisipan, instrumen, dan hasil evaluasi |
| AP-24 | Lima kasus uji disebut lima jenis testing | Salah menghitung syarat topik | Bedakan jenis metode pengujian dan kasusnya |
| AP-25 | Lima layar disebut lima fitur utama | Salah menghitung fungsi bisnis | Petakan kebutuhan dan kemampuan pengguna |
| AP-26 | Fit scaler/seleksi fitur pada semua data | Data evaluasi memengaruhi pembentukan model | Fit pada bagian latih yang tepat dan ulangi di setiap fold |
| AP-27 | Pembagian acak untuk prediksi masa depan | Kondisi evaluasi dapat tidak menyerupai penggunaan | Gunakan protokol waktu dan horizon yang sesuai |
| AP-28 | Nilai bulanan dianggap diketahui sejak awal bulan | Berisiko memakai informasi sebelum rilis | Selaraskan dengan waktu ketersediaan sebenarnya |
| AP-29 | Memilih konfigurasi dengan melihat test berulang | Test menjadi alat seleksi | Gunakan validasi untuk seleksi; jaga evaluasi akhir |
| AP-30 | Mengartikan korelasi sebagai sebab-akibat | Desain tidak mengidentifikasi sebab | Laporkan hubungan dan batas inferensi |
| AP-31 | Menyebut selisih signifikan tanpa pengujian | Jenis kepastian tidak jelas | Tampilkan besar selisih; uji statistik bila sesuai |
| AP-32 | Membandingkan metrik dari mata uang/horizon berbeda | Angka tidak setara | Samakan kondisi atau batasi perbandingan secara kualitatif |
| AP-33 | Menyebut model "terbaik" tanpa ruang pembanding | Klaim berlebihan | Sebutkan metrik, skenario, dan kelompok model |
| AP-34 | `100 - MAPE` disebut confidence atau akurasi absolut | Ukurannya tidak memiliki makna probabilistik tersebut | Gunakan metrik asli dan indikator yang terdefinisi |
| AP-35 | Nilai default antarmuka dianggap hasil eksperimen | Angka tidak berasal dari evaluasi | Beri status tidak tersedia atau label contoh/heuristik |
| AP-36 | Menyembunyikan hasil gagal atau ablation yang lebih baik | Kesimpulan menjadi selektif | Laporkan dan jelaskan implikasinya |
| AP-37 | Bab IV mengulang definisi Bab II | Hasil dan analisis tertutup teori | Fokus pada pelaksanaan, bukti, dan interpretasi |
| AP-38 | Kesimpulan menambah fitur atau angka baru | Tidak dapat ditelusuri ke hasil | Jawab rumusan masalah dengan bukti yang sudah dibahas |
| AP-39 | Naskah diklaim siap produksi dari prototipe lokal | Luas validasi tidak mendukung | Nyatakan cakupan implementasi dan pengujian sebenarnya |
| AP-40 | Menambah halaman kosong/definisi demi 90 halaman | Panjang menggantikan substansi | Lengkapi bukti, metode, dan pembahasan yang memang perlu |
| AP-41 | Menyamakan similarity rendah dengan bebas plagiarisme | Atribusi dan izin belum tentu benar | Audit sumber, parafrasa, izin, dan kepemilikan data |

## AP-KONSISTENSI. Pemeriksaan yang tidak boleh dilewati

**[PRAKTIK]** Periksa angka utama antara tabel hasil, abstrak, abstract, pembahasan, dan kesimpulan. Jika dua angka berbeda, identifikasi presisi, pembulatan, metrik, dan skenarionya. Jangan memilih angka yang paling bagus atau mengubah hasil tanpa bukti eksperimen.

Bedakan arsitektur sebelum tuning dari arsitektur final. Cocokkan unit, layer, jumlah parameter, urutan fitur, scaler, dan nama artefak dengan versi yang benar-benar dievaluasi. Perbedaan gambar dan tabel belum membuktikan implementasi salah; laporkan kebutuhan verifikasi ketika artefak belum tersedia.

Periksa ulang nomor narasi setiap kali tabel atau gambar disisipkan. Nomor caption yang benar tidak menjamin kalimat sebelumnya masih menunjuk objek yang tepat. Cocokkan juga daftar gambar, daftar tabel, dan lampiran.

Periksa batas setiap kategori metrik, termasuk tanda lebih kecil, lebih besar, dan sama dengan. Interval yang bertumpang tindih harus ditelusuri ke sumber definisinya. Jangan memperbaiki tanda secara diam-diam atau membuat kategori seolah berlaku untuk semua masalah.

Pisahkan skor antarmuka yang bersifat heuristik dari metrik evaluasi. Nilai pengganti, metrik contoh, atau indikator yang belum dikalibrasi tidak boleh menjadi bukti keandalan. Ketika evaluasi tidak tersedia, nyatakan tidak tersedia atau gunakan label contoh yang jelas.

Jangan membuang hasil evaluasi tambahan yang lebih baik atau berbeda dari model utama. Batasi klaim terbaik pada kelompok eksperimen dan kriteria yang dimaksud. Pemilihan artefak operasional harus menjelaskan perbedaan tujuan, bukan menghapus temuan yang tidak sesuai rencana.
