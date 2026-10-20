# Analisis Data Kualitatif - Panduan Referensi

Berkas ini berlaku ketika desain penelitian bukan survei kuantitatif. Jangan campur:
bila ada variabel yang diukur dengan skala angka, gunakan `references/dataset-analysis.md`
dan `scripts/stats_tests.py`.

---

## 1. Menentukan desain kualitatif

| Desain | Tanyakan | Contoh topik |
|--------|----------|--------------|
| Studi kasus | Bagaimana konteks X menjelaskan hasil Y? | Efektivitas program pelatihan pada satu unit kerja |
| Fenomenologi | Apa pengalaman yang dialami peserta? | Pengalaman Novel yang berhasil |
| Grounded theory | Kategori apa yang muncul dari data? | Proses terbentuknya budaya kerja di tim baru |
| Analisis tematik | Pola tema apa yang berulang? | Persepsi mahasiswa terhadap kelas daring |
| Deskriptif kualitatif | Gambaran apa yang sedang terjadi? | Gambaran pelaksanaan RKAS di sekolah |

Aturan praktis:
1. Gunakan satu desain utama. Bila dua dipakai, jelaskan batasannya.
2. Desain harus konsisten dengan rumusan masalah dan teknik pengumpulan data.
3. Studi kasus menuntut batas waktu, tempat, dan kasus yang jelas.
4. Fenomenologi menuntut deskripsi pengalaman dari dalam, bukan penilaian baik atau buruk.

---

## 2. Teknik pengumpulan data

| Teknik | Kekuatan | Catatan etika |
|--------|----------|---------------|
| Wawancara mendalam | Mendalam pada makna | Perlu persetujuan, durasi 30-90 menit |
| Wawancara semi-terstruktur | Fleksibel tetapi terarah | Pedoman berisi pertanyaan inti dan pertanyaan pendalam |
| Observasi-partisipan | Perilaku nyata | Jangan merusak privasi subjek |
| Focus Group Discussion | Perspektif bersama | Kelompok kecil 6-10 orang; hindari dominasi vokal |
| Dokumentasi | Jejak spontan | Arsip, notulen, foto, laporan |
| Catatan lapangan | Konteks situasional | Tulis segera setelah observasi |

Setiap teknik yang dipakai wajib:
- dijelaskan mengapa sesuai dengan tujuan penelitian;
- punya prosedur etika: persetujuan informed, anonimisasi, hak mundur, penyimpanan data;
- punya panduan instrumen di Lampiran (`templates/pedoman_wawancara.md`).

---

## 3. Tahapan analisis

1. **Transkripsi** - verbum atau semi-verbum, konsisten dengan pedoman transkripsi
   yang ditetapkan sejak awal. Simpan rekaman asli.
2. **Kutipan verbatim** untuk kutipan langsung; sertakan penanda waktu bila relevan.
3. **Koding terbuka** - beri kode pada setiap potongan bermakna. Kode sebaiknya
   satu sampai tiga kata, berupa frasa yang dekat dengan data, bukan label yang menghakimi.
4. **Koding kategorikal** - kelompokkan kode yang serupa secara logis.
5. **Koding tematik** - susun tema besar dari kategori, hubungkan dengan rumusan masalah.
6. **Validasi** - member checking, triangulasi sumber, dan pemeriksaan ulang kode oleh
   rekan sejawat atau pembimbing.
7. **Pelaporan** - tabel kode, narasi tema, kutipan peserta dengan penanda
   `[K-n]`, misalnya `[K-3: peserta 3, wawancara 2]`.

### Kelengkapan data
- Gunakan saturasi data. Nyatakan alasan penghentian pengumpulan data: kode baru tidak
  lagi memunculkan tema baru setelah beberapa peserta terakhir.
- Bila data belum jenuh, proposal harus menyebut rencana perpanjangan sampling.

### Mutu penelitian

| Aspek | Praktik |
|-------|---------|
| Kredibilitas | Member checking, triangulasi, deskripsi tebal (thick description) |
| Transferabilitas | Deskripsi tebal konteks, purposive sampling yang jelas |
| Dependabilitas | Audit trail: menyimpan setiap versi kode dan alasan perubahan |
| Confirmability | Refleksi peneliti, datasheet auditing, tidak menggeser kesimpulan |

---

## 4. Bentuk keluaran untuk BAB III

Subbab metode untuk penelitian kualitatif memuat:

1. **Desain penelitian kualitatif** - jenis dan justifikasinya.
2. **Lokasi dan waktu penelitian** - batas konteks.
3. **Informan atau peserta** - kriteria inklusi, eksklusi, jumlah.
4. **Teknik pengumpulan data** - merujuk pedoman wawancara di Lampiran.
5. **Teknik analisis data** - tahapan Magnucki atau Miles dan Huberman.
6. **Uji validitas data** - triangulasi, member checking, uji kredibilitas.
7. **Etika penelitian** - persetujuan, anonimisasi, hak mundur, penyimpanan.

Tabel yang perlu disiapkan:

```markdown
| Kode | Kategori | Tema | Jumlah Kutipan | Sumber |
|------|----------|------|----------------|--------|
| M1 | Motivasi ekstrinsik | Motivasi kerja | 12 | [K-1], [K-3] |
```

---

## 5. Batasan yang harus disebut jujur

- Tidak ada generalisasi statistik; kesimpulan bersifat transferabel, bukan
  generalizable.
- Kutipan dapat dipilih secara selektif; sebutkan prosedur pemilihan kutipan.
- Hasil pengodean bersifat interpretif; sertakan contoh pengodean yang saling
  berbeda agar pembaca dapat menilai.
- Jangan menyebut angka persentase dari "sebagian besar peserta" tanpa menghitung
  penyebutnya lebih dahulu.

---

## 6. Larangan keras

- Membuat kutipan yang tidak ada di transkrip.
- Mengubah arti kutipan saat menyunting.
- Menyebut nama peserta tanpa persetujuan tertulis.
- Mengarang tema, kode, atau jumlah peserta.
- Menghapus jawaban yang tidak mendukung hipotesis tanpa mencatat alasannya.
- Mengganti kata "sebagian besar" dengan angka spesifik yang tidak dihitung.

---

## 7. Alat bantu

Alat kualitatif bersifat opsional; pekerjaan bisa dilakukan manual dengan
`scripts/code_interview.py` untuk membuat tabel kode dari transkrip.

| Alat | Kegunaan |
|------|----------|
| NVivo atau Atlas.ti | Kode bertingkat, pencarian, matriks kasus |
| Taguette (gratis) | Koding terbuka sederhana |
| MAXQDA | Analisis campuran (mixed methods) |

Bila memakai perangkat lunak, tulis nama perangkat, versinya, dan proses pengodean
di BAB III agar dapat diaudit.
