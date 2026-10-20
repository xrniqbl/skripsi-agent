# Persyaratan sebelas topik

Baca hanya baris topik yang ditetapkan. Bagian minimum adalah KETENTUAN; cara menghitung fitur, data, atau iterasi adalah PRAKTIK. Jangan menggabungkan seluruh syarat sebelas topik.

## TOP-00. Minimum per topik

**[KETENTUAN]**

| Topik | Proposal: syarat minimum | Hasil akhir: bukti yang diminta |
|---|---|---|
| Pengembangan aplikasi (`TOP-APP`) | Minimal 10 fitur utama di luar login, logout, dan CRUD data master; uraikan *use case*/kebutuhan fungsional; izin jika berbasis mitra atau memakai data/proses instansi eksternal | Minimal pengujian *black-box* oleh calon pengguna pada semua tingkat akses, sebagaimana disebut profil akademik sebagai UAT |
| Mining (`TOP-MIN`) | Data telah dimiliki dan dapat ditampilkan; untuk teks minimal 1.000 data; metodologi jelas | Minimal 1.000 data teks atau minimal 100 data nonteks seperti gambar/rekam medis; minimal lima skenario; model telah diterapkan melalui web atau visualisasi informasi beserta analisisnya |
| UI/UX (`TOP-UX`) | Minimal lima fitur utama di luar login, logout, register; *empathy map* atau sejenisnya; surat izin untuk redesain aplikasi | Proses bisnis dari *empathy map*; filosofi/rationale desain; minimal dua pengujian, masing-masing untuk kegunaan dan estetika; minimal dua iterasi; hasil dari Figma dibuktikan dalam antarmuka aplikasi minimal satu halaman fitur utama |
| Testing (`TOP-TES`) | Minimal lima jenis pengujian; daftar fitur yang diuji; izin perusahaan yang menyatakan kesediaan memberi umpan balik | Dokumentasi setiap tahap metodologi dan dokumentasi penyelesaian *bug* |
| SPK (`TOP-SPK`) | Minimal lima kriteria dan 45 alternatif; untuk implementasi aplikasi minimal satu metode SPK serta tahapan implementasinya | Minimal dua pengujian, misalnya kecocokan perhitungan manual/spreadsheet dengan sistem dan pengujian fitur |
| Forecast (`TOP-FOR`) | Data telah dimiliki dan dapat ditampilkan, minimal 500 baris; metodologi jelas | Minimal dua metode pengukuran kesalahan dan visualisasi grafik |
| Pemodelan dan simulasi (`TOP-SIM`) | *Causal loop* dan surat izin | Model awal sampai CLD yang diperbarui; minimal tiga skenario pada model awal |
| Jaringan (`TOP-NET`) | Surat izin; redesain disertai analisis jaringan saat ini; desain disertai analisis kebutuhan pengguna, aplikasi, dan perangkat minimal 50 node; monitoring/evaluasi disertai metode pemantauan | Implementasi skrip pada router untuk pengelolaan bandwidth atau keamanan; pengujian beserta metrik yang sesuai; untuk monitoring/evaluasi, tunjukkan peningkatan dari sisi pengguna sesuai ketentuan profil akademik |
| IoT (`TOP-IOT`) | Hasil simulasi pada platform yang disebut pedoman, misalnya Tinkercad, ThingSpeak, Wokwi, atau Blynk | Produk perangkat keras IoT, bukan hanya gambar atau simulasi |
| ERP (`TOP-ERP`) | Surat izin; analisis proses bisnis sebelum dan sesudah; untuk pengembangan, gambarkan proses bisnis dari minimal satu modul yang akan dikembangkan; untuk kustomisasi, sebutkan minimal dua modul yang kode programnya akan diubah | Hasil pengujian *black-box* modul yang dikembangkan/dikustomisasi |
| Manajemen proses bisnis (`TOP-BPM`) | Surat izin; mitra minimal UKM dengan omzet tahunan minimal Rp300.000.000 yang dibuktikan wawancara; rencana pemanfaatan teknologi di latar belakang; seluruh proses AS IS; minimal empat aktor/divisi/bagian/departemen; hasil pengukuran kinerja | Proses bisnis usulan; minimal dua skenario simulasi per proses bisnis; perbandingan sebelum/sesudah; validasi pengguna terhadap usulan |

## TOP-01. Cara menerapkan persyaratan

**[PRAKTIK]** Bedakan fitur utama dari halaman, tombol, dan operasi CRUD. Satu proses bisnis tidak menjadi lima fitur hanya karena mempunyai lima layar. Bedakan lima jenis pengujian dari lima kasus uji. Bedakan dua iterasi UI/UX yang mengubah rancangan berdasarkan evaluasi dari dua kali ekspor desain yang sama.

Jumlah minimum adalah syarat administratif topik, bukan pembuktian kecukupan statistik. Jelaskan unit observasi dan jumlah data asli, data setelah pembersihan, data hasil augmentasi, serta sampel efektif. Jangan menyebut 500 baris hasil pengisian ulang sebagai 500 pengamatan independen tanpa penjelasan. Konfirmasikan kecukupan data apabila jumlah asli dan jumlah setelah pengolahan berbeda.

Jangan memaksakan sepuluh fitur aplikasi pada topik *forecast* hanya karena model ditampilkan melalui web. Untuk topik gabungan, minta penetapan kategori dan persyaratan yang berlaku. Jangan menyalin lima skenario *mining* sebagai aturan wajib *forecast* tanpa dasar tambahan.

Persyaratan peningkatan kinerja jaringan tidak boleh dipenuhi dengan merekayasa hasil. Jika peningkatan belum tercapai, laporkan hasil sebenarnya, telusuri penyebab, revisi rancangan, dan konsultasikan status pemenuhan syarat.

Batas omzet pada tabel adalah aturan pemilihan mitra dalam profil akademik, bukan pernyataan tentang definisi hukum UKM yang berlaku saat ini. Ejaan nama platform IoT dinormalisasi untuk keterbacaan; daftar contoh bukan kewajiban memakai semua platform sekaligus.
