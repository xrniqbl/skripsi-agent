# Pelaporan pengujian dan artefak

Baca untuk tabel hasil uji, perhitungan manual, catatan eksperimen, atau kesesuaian implementasi. Format dasar pelaporan adalah KETENTUAN; rincian keterlacakan adalah PRAKTIK.

## UJI-01. Pengujian black-box dan penerimaan pengguna

**[KETENTUAN]** Laporkan berdasarkan proses bisnis dan skenario, mencakup alur normal serta alternatif. Hasil yang diharapkan dan hasil sebenarnya ditulis sebagai narasi, bukan diganti screenshot.

| No. | Skenario | Hasil yang diharapkan | Hasil sebenarnya | Status |
|---|---|---|---|---|
| {ID} | {peran, kondisi awal, input/tindakan} | {respons spesifik yang dapat diperiksa} | {respons yang benar-benar diamati} | {Berhasil/Gagal} |

**[PRAKTIK]** Tambahkan identitas versi, tanggal, penguji/peran yang diizinkan, dan lokasi bukti di catatan pendukung. Jangan mengisi "Berhasil" hanya karena tidak ada error yang dilaporkan. Jika belum dijalankan, tulis belum diuji di lembar kerja, bukan memalsukan hasil final.

## UJI-02. Validasi perhitungan

**[KETENTUAN]** Untuk perhitungan seperti SPK, bandingkan hasil manual melalui spreadsheet dengan keluaran sistem, bukan gambar keluaran.

| No. | Nama proses | Hasil perhitungan manual | Hasil sistem | Status |
|---|---|---|---|---|
| {ID} | {langkah atau perhitungan} | {nilai, satuan, presisi} | {nilai, satuan, presisi} | {Berhasil/Gagal} |

**[PRAKTIK]** Tentukan toleransi numerik bila relevan. Simpan contoh input dan langkah perhitungan. Perhitungan ilustratif dengan bobot buatan hanya menjelaskan mekanisme, bukan memvalidasi bobot hasil pelatihan atau performa model sebenarnya.

## UJI-03. Rekaman eksperimen dan kesesuaian implementasi

```text
ID eksperimen dan tujuan:
Data/versi/periode/jumlah observasi:
Pemisahan latih-validasi-uji dan unit pemisahan:
Transformasi dan data yang dipakai untuk fitting:
Model, hiperparameter, seed, dan versi lingkungan:
Kriteria pemilihan konfigurasi:
Metrik, satuan, horizon, dan jumlah sampel efektif:
Hasil aktual dan lokasi artefak:
Kegagalan, penyimpangan protokol, dan batasan:
Keputusan serta bagian naskah yang perlu diperbarui:
```

Cocokkan Bab III, Bab IV, lampiran, kode, metadata, dan artefak implementasi. Model yang diterapkan harus dapat diidentifikasi melalui nama berkas, konfigurasi, struktur fitur, dan versi yang digunakan. Jangan mengklaim telah memeriksa kesesuaian kode apabila kode tidak tersedia.

Pisahkan metrik penelitian dari indikator antarmuka. Nilai default, data contoh, skor heuristik, atau perkiraan tanpa evaluasi harus diberi label yang terlihat. Ketika evaluasi tidak tersedia, tampilkan status tidak tersedia, bukan angka yang menyerupai hasil pengujian.
