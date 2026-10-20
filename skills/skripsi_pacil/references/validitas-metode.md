# Pemeriksaan validitas metode

Baca subbagian yang sesuai: data/ML, forecast, metrik, aplikasi, UI/UX, atau SPK/simulasi/jaringan/IoT. Bedakan hasil audit yang dibuktikan dari saran metode yang belum diterapkan.

**[PRAKTIK]** Terapkan pemeriksaan berikut hanya pada metode yang benar-benar digunakan. Ini adalah pengayaan metodologis, bukan tambahan syarat minimum kampus. Bila naskah atau artefak belum membuktikan suatu risiko, laporkan sebagai pertanyaan pemeriksaan, bukan kesalahan yang telah dipastikan.

## MET-01. Data dan evaluasi pembelajaran mesin

Tetapkan unit observasi dan target sebelum membagi data. Periksa duplikasi, kelompok subjek, perangkat, lokasi, dan waktu. Jika beberapa gambar berasal dari orang atau sesi yang sama, pembagian acak per gambar dapat menempatkan informasi yang sangat berdekatan pada latih dan uji; gunakan pemisahan kelompok yang sesuai dengan klaim generalisasi.

Pisahkan pelatihan, pemilihan model, dan pengujian akhir. Pelajari parameter transformasi hanya dari data latih yang sesuai, termasuk pada setiap fold validasi. Jangan memilih fitur, batas pencilan, penyeimbangan kelas, imputasi, atau normalisasi menggunakan informasi seluruh data sebelum evaluasi [^w17].

Terapkan augmentasi hanya pada bagian yang semestinya. Jangan menyebut hasil augmentasi sebagai responden baru. Simpan jumlah data sebelum/sesudah pembersihan dan alasan perubahan. Nilai 100% pada himpunan uji terbatas memerlukan pemeriksaan kebocoran serta batas konteks, bukan klaim bahwa model sempurna di dunia nyata.

Samakan protokol pembanding: data, target, pemisahan, metrik, anggaran pencarian, serta informasi yang tersedia. Catat seed, versi, konfigurasi, dan artefak yang memungkinkan pengulangan. Laporkan variasi antarulangan jika digunakan; jangan mengarang simpangan baku atau interval kepercayaan dari satu percobaan.

## MET-02. Forecasting dan data berurutan

Pertahankan urutan waktu dan uji pada masa sesudah data latih. Jelaskan rentang tanggal, frekuensi, panjang jendela, horizon, serta cara validasi. Gunakan evaluasi asal bergulir bila sesuai; *TimeSeriesSplit* dan pendekatan sejenis harus disesuaikan dengan jarak waktu serta kebutuhan pemisahan data [^w18] [^w20].

Pastikan seluruh fitur tersedia pada waktu prediksi. Untuk inflasi, suku bunga, atau laporan periodik, bedakan periode yang diukur dari tanggal rilisnya. Mengisi nilai satu bulan ke seluruh hari bulan yang sama dapat menggunakan informasi yang belum diumumkan; pemeriksaan ini tetap diperlukan meskipun fungsi yang digunakan bernama *forward fill*.

Definisikan pemetaan input-target: misalnya histori sampai t untuk memprediksi t+1. Fitur rata-rata bergerak yang memuat target pada waktu yang sedang diprediksi dapat bocor; fitur yang memuat observasi saat t dapat sah bila t memang sudah diketahui ketika memprediksi t+1. Periksa indeks aktual, bukan nama fitur saja.

Perbandingan rasio 70:30 dan 90:10 dapat mengubah periode uji, bukan hanya ukuran data latih. Jangan menyimpulkan penambahan data pasti menyebabkan peningkatan tanpa mengendalikan perbedaan periode. Untuk perbandingan yang lebih kuat, gunakan horizon dan periode evaluasi yang sebanding atau ungkapkan keterbatasannya.

Sertakan pembanding sederhana yang relevan, misalnya nilai terakhir atau pola musiman, bila sesuai lingkup. Jangan menolak metode statistik hanya karena tidak memakai jaringan saraf. Bedakan ARIMA tanpa peubah eksternal dari varian yang memang menerima peubah eksternal; jangan membuat kritik yang salah terhadap seluruh keluarga metode.

Untuk prediksi beberapa langkah, jelaskan strategi rekursif, langsung, atau multi-output. Jika memerlukan peubah eksogen masa depan, nyatakan apakah nilainya diketahui, diproyeksikan, atau diasumsikan. Evaluasi prediksi dengan masukan eksogen aktual tidak sama dengan penggunaan operasional ketika masukan itu belum tersedia.

## MET-03. Metrik dan klaim hasil

Pilih metrik berdasarkan tujuan dan sifat target. Untuk *forecast* profil akademik mewajibkan minimal dua pengukuran kesalahan, tetapi tidak memaksa pasangan tertentu. RMSE memiliki satuan target; MAPE memerlukan perhatian terhadap nilai aktual nol atau mendekati nol [^w19]. Jangan mengganti MAPE menjadi `100 - MAPE` dan menyebutnya akurasi atau probabilitas benar.

Jangan membandingkan RMSE rupiah dengan RMSE dolar secara langsung. MAPE yang sama-sama berupa persen pun tidak menjamin evaluasi setara jika horizon, periode, atau karakter target berbeda. Jika metrik memberikan urutan model berbeda, nyatakan komprominya dan gunakan kriteria utama yang ditetapkan, bukan memilih metrik setelah melihat pemenang.

Korelasi bukan bukti kausalitas. Grafik ACF/PACF tidak dengan sendirinya membuktikan semua hubungan nonlinier atau bahwa satu algoritma pasti unggul. Penjelasan tentang penyebab kesalahan harus dibedakan antara hasil diagnosis, penjelasan dari literatur, dan dugaan yang belum diuji.

## MET-04. Pengembangan aplikasi, testing, dan ERP

Turunkan kebutuhan dari proses bisnis atau bukti pengguna. Buat hubungan kebutuhan, fitur, peran akses, kasus uji, hasil, serta revisi. Bedakan pengujian fungsi, penerimaan pengguna, keamanan, kinerja, dan kualitas antarmuka berdasarkan tujuan; jangan mengklaim semua telah diuji hanya dari satu tabel *black-box*.

Uji alur normal, alternatif, input tidak valid, serta batas akses sesuai lingkup. Dokumentasikan kegagalan dan pengujian ulang. Untuk ERP, jelaskan proses sebelum/sesudah, modul yang dikembangkan/dikustomisasi, integrasi, serta hasil pengujiannya. Screenshot halaman login bukan bukti seluruh proses bisnis berjalan.

## MET-05. UI/UX

Hubungkan temuan pengguna dengan *empathy map* atau artefak setara, perumusan masalah, kebutuhan, alternatif desain, prototipe, evaluasi, dan revisi. Jangan membuat persona sebagai hasil wawancara bila sebenarnya asumsi desain. Beri label hipotesis dan validasi melalui bukti yang sesuai.

Penuhi dua jenis evaluasi yang diminta profil akademik: kegunaan dan estetika, serta minimal dua iterasi. Pilih instrumen yang benar-benar mengukur konstruk tersebut dan telusuri cara penghitungan/interpretasinya dari sumber asli. Jangan menganggap setiap instrumen pengalaman pengguna otomatis memenuhi keduanya.

Jelaskan partisipan, kriteria pemilihan, tugas, kondisi sesi, versi prototipe, metrik, serta perubahan setiap iterasi. Skor kepuasan tidak sama dengan keberhasilan menyelesaikan tugas. Bukti satu halaman fitur utama dalam bentuk antarmuka aplikasi tidak boleh disebut implementasi seluruh produk.

## MET-06. SPK, simulasi, jaringan, dan IoT

Untuk SPK, jelaskan sumber kriteria, tipe manfaat/biaya, bobot, alternatif, normalisasi, agregasi, dan validasi keputusan. Cocokkan perhitungan sistem dengan perhitungan independen pada contoh yang dapat ditelusuri. Jangan menyebut kesesuaian rumus sebagai bukti bahwa bobot atau rekomendasi sudah benar bagi pengguna.

Untuk simulasi/proses bisnis, jelaskan asumsi model, hubungan antarvariabel, satuan, kondisi awal, sumber parameter, skenario, dan validasi. Bedakan hasil simulasi dari perbaikan yang benar-benar terjadi pada organisasi. Perbandingan AS IS dan TO BE memerlukan dasar serta kondisi yang sebanding.

Untuk jaringan/IoT, catat lingkungan, perangkat, topologi, beban, konfigurasi, instrumen, metrik, dan pengulangan pengukuran. Uji hanya pada lingkungan yang diizinkan. Simulasi, prototipe laboratorium, dan implementasi lapangan harus diberi label berbeda; jangan mengklaim peningkatan tanpa hasil sebelum/sesudah yang memadai.

## Rujukan teknis tambahan

Gunakan rujukan ini untuk memverifikasi praktik teknis. Rujukan ini bukan tambahan syarat institusi dan bukan daftar pustaka wajib untuk naskah. Periksa versi yang berlaku ketika digunakan.

[^w17]: scikit-learn, [Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html). Kebocoran data, transformasi, dan pemisahan evaluasi.

[^w18]: scikit-learn, [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html). Validasi berurutan dan ketentuan penggunaan pembagi waktu.

[^w19]: R. J. Hyndman dan G. Athanasopoulos, *Forecasting: Principles and Practice*, [Evaluating point forecast accuracy](https://otexts.com/fpp3/accuracy.html). Metrik kesalahan dan batas interpretasinya.

[^w20]: R. J. Hyndman dan G. Athanasopoulos, *Forecasting: Principles and Practice*, [Time series cross-validation](https://otexts.com/fpp3/tscv.html). Evaluasi dengan asal ramalan bergulir.
