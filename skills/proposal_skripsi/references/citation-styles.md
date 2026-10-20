# Citation Styles — Daftar Pustaka Proposal (Bahasa Indonesia)

Pandu **STEP 6.1**. Default: **APA 7**. Ganti hanya bila pedoman kampus/user menetapkan gaya
lain. Ironisnya: sitasi Proposal akan dinilai termasuk bagian yang paling sering salah.

## 1. Aturan Umum (Semua Gaya)

1. **Satu sumber = satu entri.** Entri yang tidak dikutip di teks harus dihapus.
2. **Semua kutipan di teks harus punya entri** di daftar pustaka.
3. **Jangan mengarang DOI.** Bila sumber dari file lokal tanpa DOI, tulis
   `(dokumen lokal, namafile.pdf)` — bukan DOI karangan.
4. **Nama penulis**: gunakan nama belakang seperti pada publikasi. Jangan ubah urutan.
5. **Bahasa**: tulis judul dalam bahasa aslinya; bila terjemahan, tambahkan `[terjemahan]`.
6. **Konsistensi**: satu gaya untuk seluruh dokumen. Jangan mencampur APA dengan IEEE.
7. **Tanda baca** dalam daftar pustaka: titik setelah nama, tahun dalam kurung, titik setelah
   judul, dan nama jurnal serta volume dalam *italik*.

## 2. APA 7 (Default)

### Artikel jurnal

```text
Ahmad, J., & Sari, D. (2021). Pengaruh motivasi terhadap kinerja karyawan. Jurnal Manajemen
Indonesia, 22(3), 45-58. https://doi.org/10.1234/jmi.2021.001
```

### Buku

```text
Creswell, J. W., & Creswell, J. D. (2018). Research design: Qualitative, quantitative, and mixed
methods approaches (5th ed.). SAGE Publications.
```

### Bab buku

```text
Field, A. (2018). Discovering statistics using IBM SPSS statistics (5th ed.). SAGE. (Bab 13:
Regresi berganda)
```

### Skripsi/tesis/disertasi

```text
Wijaya, A. (2023). Pengaruh lingkungan kerja terhadap kinerja karyawan pada PT X
(Skripsi, Universitas X). Repository Institusi.
```

Dalam teks: (Wijaya, 2023). Tiga penulis atau lebih: (Santoso et al., 2022).

### Sumber dari internet / laporan

```text
World Health Organization. (2023). Laporan global tuberkulosis 2023. https://www.who.int/...
```

### Dokumen lokal (tanpa DOI)

```text
Kementerian Pendidikan, Kebudayaan, Riset, dan Teknologi. (2024). Panduan proposal skripsi
(dokumen lokal, pedoman_skripsi_2024.pdf).
```

### Kutipan langsung

```text
Menurut Supratman (2020, hlm. 45), "kinerja individu dipengaruhi oleh tiga faktor utama."
```

Kutipan langsung lebih dari 40 kata harus memakai blok kutipan.

## 3. Gaya Lain (Ringkas)

| Gaya | Artikel jurnal | Dalam teks |
|------|----------------|------------|
| **Chicago (author-date)** | Author, First. Year. "Title." *Journal* vol (no): pages. | (Author Year) |
| **Harvard** | Author, A. (Year) 'Title', *Journal*, vol(no), pp. x-y. | (Author, Year) |
| **Vancouver** | Author AB, Author CD. Title. Journal. Year;vol(no):pages. | [1] |
| **IEEE** | A. Author, "Title," *Journal*, vol. no, pp. x-y, Year. | [1] |
| **MLA 9** | Author. "Title." *Journal*, vol. no, Year, pp. x-y. | (Author 45) |

> **Vancouver dan IEEE** memakai nomor urut, sehingga daftar pustaka harus **diurutkan sesuai
> urutan pemakaian pertama**, bukan alfabetis. Tuliskan disclaimer ke user bila memilih gaya ini.

## 4. Menentukan Nomor Urut (untuk Vancouver/IEEE)

Urutan berdasarkan urutan sitasi pertama muncul di BAB I. Cara cepat: baca dokumen dari atas,
catat setiap marker `[L-n]` yang muncul pertama kali, assign nomor 1, 2, 3, dan seterusnya.

## 5. Menutup Daftar Pustaka

Daftar pustaka **tidak** diberi nomor halaman, tidak diberi garis pemisah, dan tidak memuat
sumber yang tidak dikutip. Urutan: alfabetis pada APA/Chicago/Harvard/MLA, nomor pada
Vancouver/IEEE.

## 6. Cek cepat sebelum export

```bash
# Semua marker L-n yang dipakai di teks
grep -o "\[L-[0-9]*\]" proposal_skripsi.md | sort -u

# Bandingkan dengan jumlah entri daftar pustaka
grep -c "^[A-Z][a-zA-Z]*," daftar_pustaka.md
```

Angka keduanya harus sama. Jika tidak, perbaiki sebelum export.
