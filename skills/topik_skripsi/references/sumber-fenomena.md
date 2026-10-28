# Sumber Fenomena — Delapan Pintu Masuk

Fenomena penelitian tidak lahir dari "cari judul di Google". Ia lahir dari **gesekan antara
apa yang seharusnya dan apa yang terjadi**, dan gesekan itu hanya terlihat kalau lo berada
dekat dengan tempat kejadian atau dekat dengan datanya.

Delapan sumber di bawah diurutkan dari yang paling kuat (paling sulit dibantah pembimbing)
sampai yang paling lemah (paling mudah dianggap opini).

---

## 1. Pengamatan langsung di lokasi

**Kekuatan: tinggi.** Pembimbing sulit membantah apa yang lo lihat sendiri, terutama kalau
ada dokumentasi.

Yang dicari saat berada di lokasi (magang, kerja, KKN, organisasi):

| Yang dilihat | Fenomena yang mungkin |
|---|---|
| Orang mengetik ulang data dari kertas ke Excel | duplikasi entri, risiko salah input, waktu terbuang |
| Dua bagian punya file rekap berbeda untuk periode sama | inkonsistensi sumber kebenaran |
| Antrean panjang di satu loket, loket lain kosong | ketidakseimbangan beban / proses tidak jelas |
| Formulir kertas difotokopi lalu dikirim via WA | kehilangan jejak, tidak ada audit trail |
| Sistem baru tapi orang tetap pakai cara lama | adopsi gagal, resistensi, pelatihan tidak cukup |
| Laporan bulanan selalu telat di tanggal yang sama | bottleneck proses, bukan kelalaian orang |
| Satu orang memegang seluruh proses kunci | *single point of failure* |
| Data yang sama diisi di tiga aplikasi berbeda | integrasi tidak ada, beban ganda |

Cara mengambil bukti:
- **catatan lapangan** bertanggal (tanggal, jam, siapa, apa)
- **foto/Screenshot** (hati-hati data pribadi — samarkan)
- **hitungan**: berapa kali, berapa menit, berapa berkas
- **nama proses** persis seperti disebut pegawai (bukan istilah lo)

> Jangan menulis "sistemnya tidak efisien". Tulis "satu laporan bulanan dikerjakan 3 kali
> oleh 2 orang, total 4 jam per bulan, dengan 2 dari 3 versi berbeda angkanya".

---

## 2. Anomali data sekunder

**Kekuatan: tinggi** — angkanya bisa dicek siapa pun.

Sumber data publik Indonesia yang paling sering menghasilkan fenomena:

| Sumber | Isi | Cara pakai |
|---|---|---|
| BPS (`bps.go.id`) | statistik wilayah, pertanian, industri, kemiskinan | bandingkan antar tahun / antar kabupaten |
| Satu Data Indonesia (`data.go.id`) | dataset lintas kementerian | cari dataset dengan cakupan tidak lengkap |
| BPS daerah / publikasi kabupaten dalam angka | tabel per kecamatan | cari selisih antar tabel |
| Dapodik / Kemdikbud | sekolah, siswa, guru | rasio guru-siswa, sekolah tanpa rombel |
| SIK-NG / Dinkes | fasilitas kesehatan, tenaga | puskesmas tanpa dokter, rasio tenaga |
| SIMPEG/BKN | ASN | formasi vs realisasi |
| LPSE / SPSE | pengadaan | paket gagal lelang berulang |
| SP4N-LAPOR | pengaduan masyarakat | kategori aduan terbanyak vs tindak lanjut |
| Sakip / LKPJ / LPPD | kinerja pemerintah daerah | target vs realisasi berulang tidak tercapai |
| Dashboard instansi (kalau punya akses) | data operasional | tren yang berhenti / kosong |

Pola anomali yang produktif:

- **selisih antar sumber** untuk periode yang sama (contoh: jumlah penduduk BPS vs Dukcapil)
- **target vs realisasi** yang gagal 3 tahun berturut-turut dengan angka hampir sama
- **tren yang berhenti** (data terakhir 2022, padahal seharusnya tahunan)
- **lonjakan tak wajar** (naik 300% dalam satu tahun tanpa perubahan kebijakan)
- **distribusi aneh** (satu kecamatan menyumbang 60% kasus)
- **rasio mustahil** (1 tenaga untuk 12.000 pasien)
- **data kosong sistematis** (kolom yang tidak pernah diisi di semua wilayah)

Cara mengambil bukti: unduh file aslinya (CSV/XLSX/PDF), catat **URL + tanggal akses +
nama tabel + nomor halaman**. Angka tanpa URL akan dibantah.

---

## 3. Keluhan publik

**Kekuatan: sedang** — kuat sebagai pemicu, lemah sebagai bukti tunggal.

| Sumber | Yang dicari | Catatan |
|---|---|---|
| SP4N-LAPOR | kategori aduan terbanyak, aduan berulang, aduan "selesai" tanpa perubahan | data agregat tersedia |
| Ulasan Play Store / App Store | keluhan berulang di aplikasi layanan publik | ambil 50–100 ulasan, kelompokkan |
| Media sosial instansi | komentar keluhan yang sama berulang | screenshot + tanggal |
| Berita lokal | kejadian berulang yang diberitakan berkali-kali | cari 3+ berita untuk pola |
| Kotak saran / buku tamu | keluhan tertulis | foto |

Aturan: keluhan **bukan** data. Ia adalah **hipotesis** yang harus diuji. "Banyak yang
mengeluh aplikasinya lambat" harus menjadi "dari 80 ulasan 1-bintang, 34 menyebut waktu
muat >10 detik" sebelum layak jadi fenomena.

---

## 4. Mandat vs kenyataan

**Kekuatan: tinggi** — ada dasar hukum, jadi urgensi tidak perlu dibela.

Polanya: **regulasi baru mewajibkan X, tapi belum ada bukti X dijalankan.**

Contoh kerangka:
- UU Perlindungan Data Pribadi (27/2022) mewajibkan pengelolaan data tertentu → bagaimana
  instansi X mengelola data pasien/pegawai?
- Standar Pelayanan Minimal (SPM) menetapkan target → berapa capaian riil?
- Perda tentang keterbukaan informasi → apakah dokumen publik benar-benar tersedia?
- SOP internal yang disahkan tapi tidak dipakai → mengapa?
- Akreditasi/maturitas (SPBE, ISO 27001) → sejauh mana?

Cara mengambil bukti: salin **pasal/kalimat kewajiban** persis, lalu bandingkan dengan
bukti pelaksanaan (dokumen, angka, hasil observasi). Selisihnya adalah fenomena.

---

## 5. Adopsi teknologi yang gagal

**Kekuatan: tinggi** di bidang SI/TI, dan sangat relevan untuk skripsi aplikasi.

Pola yang sering:
- sistem dibangun, tapi pengguna kembali ke Excel
- sistem dibangun ulang setiap ganti pejabat (tiga versi dalam 5 tahun)
- login bulanan < 20% dari pengguna terdaftar
- fitur inti tidak dipakai, fitur sepele dipakai berat
- data di sistem tidak dipercaya, rekap tetap manual

Yang harus dibuktikan: **angka pemakaian** atau **bukti perilaku**, bukan kesan. Kalau tidak
ada akses ke log, gunakan wawancara terstruktur + observasi.

---

## 6. Kontradiksi literatur

**Kekuatan: tinggi** secara akademik — ini gap yang paling dihargai.

Cara menemukan:
1. Ambil satu hubungan yang sering diteliti (mis. kualitas data → kinerja pelaporan).
2. Kumpulkan 8–15 studi.
3. Kelompokkan: berapa positif signifikan, berapa tidak signifikan, berapa negatif.
4. Kalau ada yang bertentangan, cari **perbedaan konteks** yang menjelaskan (populasi,
   alat ukur, sektor, negara, tahun).
5. Pertentangan yang belum dijelaskan = fenomena.

Alat bantu: `scripts/literature_probe.py` untuk memetakan kepadatan; sintesis tetap manual.

---

## 7. Transfer metode

**Kekuatan: sedang–tinggi** — dipakai luas di SI, teknik, kesehatan.

Pola: **metode M terbukti pada domain A; belum pernah dicoba pada domain B yang punya
karakter berbeda.**

Syarat supaya bukan sekadar "ganti objek":
- jelaskan **mengapa** domain B berbeda secara teknis (data lebih sedikit? tidak seimbang?
  musiman? label mahal?)
- jelaskan **mengapa** perbedaan itu membuat M berisiko gagal
- siapkan metrik pembanding (baseline)

Tanpa tiga hal itu, ini bukan penelitian — ini pengulangan dengan nama tempat lain.

---

## 8. Replikasi konteks

**Kekuatan: sedang** — paling lemah kalau berdiri sendiri.

Pola: temuan berlaku di kota besar / perusahaan besar / negara maju; belum diuji di
kabupaten / UMKM / Indonesia.

Supaya kuat, replikasi harus menyatakan **apa yang mungkin berubah** dan **mengapa**:
regulasi, skala, infrastruktur, budaya kerja, ketersediaan data. Kalau jawabannya "tidak
ada yang mungkin berubah", replikasi tidak layak.

---

## Matriks pemilihan sumber

| Situasi lo | Sumber terbaik |
|---|---|
| Sedang/akan magang atau kerja | 1 (pengamatan), 5 (adopsi) |
| Tidak punya akses lokasi | 2 (anomali data), 4 (mandat vs kenyataan) |
| Kuat di statistik | 2, 6 (kontradiksi) |
| Kuat di pemrograman | 5, 7 (transfer metode) |
| Ingin topik kebijakan | 3 (keluhan), 4 (mandat) |
| Ingin topik yang cepat selesai | 2 + 4 (data publik + dokumen hukum) |

---

## Kesalahan yang paling sering terjadi

1. **Mengambil fenomena dari berita tanpa verifikasi.** Berita adalah pemicu, bukan bukti.
2. **Mengarang angka "sekitar 70%"** karena terasa masuk akal. Angka karangan akan
   ketahuan di sidang.
3. **Menganggap teknologi baru = fenomena.** "Belum ada sistem X di tempat Y" adalah
   keadaan, bukan masalah — kecuali ada dampak terukur.
4. **Menyalin fenomena dari skripsi kakak tingkat** di tempat berbeda. Konteksnya beda,
   buktinya tidak ada.
5. **Berhenti di 3 fenomena.** Tiga terlalu sedikit untuk disaring; minimal 8.
