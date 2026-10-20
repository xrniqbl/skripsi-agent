# Integrasi `paper-review` - Matriks Literatur dan Ekspor Sitasi

Skill `proposal-skripsi` menangani rumusan masalah, metode, dan naskah. Skill
`paper-review` (di `~/.agents/skills/paper-review/`) menangani pengumpulan dan
sintesis literatur. Gunakan keduanya berurutan, jangan menggandakan pekerjaan.

```
paper-review  ->  matriks_referensi.csv  ->  proposal-skripsi  ->  naskah + daftar pustaka
```

---

## 1. Kapan memanggil `paper-review`

Panggil bila salah satu kondisi berikut berlaku:

- Folder sumber lokal berisi banyak PDF/LaTeX yang perlu di sintesis.
- Perlu benchmark penelitian terdahulu untuk tabel Tinjauan Pustaka (BAB II).
- Literatur online masih minim sehingga perlu pencarian terarah.
- Perlu ekspor sitasi (BIB/RIS/CSV) untuk processor seperti Zotero atau Mendeley.

Jangan memanggil bila telaah hanya beberapa, sudah ada matriks, dan bagian BAB II
sudah terisi.

---

## 2. Alih input-output

| Keluaran `paper-review` | Dipakai `proposal-skripsi` di | Peran |
|--------------------------|------------------------------|-------|
| `*.csv` matriks | Tabel Penelitian Terdahulu (BAB II) | sumber baris tabel |
| `*.bib` BibTeX | Daftar Pustaka, `scripts/export_referensi.py` | sumber entri |
| `*.ris` RIS | Impor Zotero/EndNote | sumber entri |
| `*.xml` EndNote | Impor EndNote | sumber entri |
| `*.xlsx` | Working matriks penulis | bukan input naskah |

Semua baris matriks harus diberi penanda `[L-n]` sesuai nomor urut Daftar Pustaka.
Nomor urut harus sama antara teks, tabel, dan Daftar Pustaka.

---

## 3. Format matriks minimum untuk proposal

Kolom yang wajib ada di matriks sebelum masuk ke BAB II:

| Kolom | Dipakai untuk |
|-------|---------------|
| Title & Authors | Tabel penelitian terdahulu, Daftar Pustaka |
| Year | Penyusunan kronologi dan tren penelitian |
| Journal / Publisher | Penentu kredibilitas sumber |
| Purpose | Menentukan relevansi dengan rumusan masalah |
| Method (Variables/Samples) | Menentukan "celah" metode |
| Key Findings | Dasar klaim BAB I dan BAB II |
| Limitations | Dasar argumen celah penelitian |
| Gaps | Dasar rumusan masalah penelitian ini |
| DOI | Penentu untuk menulis DOI dan pelacakan |
| Quality (opsional) | Penentu credibilitas, mis. jumlah sampel |

Bila kolom Gaps kosong, jangan mengarang celah; isi dengan `[menunggu analisis]`
lalu selesaikan pada tahap sintesis.

---

## 4. Konversi ke Daftar Pustaka

Jalankan:

```bash
# validasi dulu: laporkan baris tanpa judul dan field kosong, tanpa menulis berkas
python3 scripts/export_referensi.py matriks_referensi.csv --periksa

# matriks CSV -> BibTeX, RIS, EndNote XML, dan teks APA
python3 scripts/export_referensi.py matriks_referensi.csv --out-dir outputs/ \
    --gaya apa --urutkan penulis
```

Opsi penting: `--gaya apa|vancouver|ieee`, `--urutkan tahun|penulis|judul|input`,
`--nomor L` (awalan penanda `[L-n]`), `--nama` (prefix berkas keluaran).

Keluarannya:

| Berkas | Untuk |
|--------|-------|
| `referensi.bib` | Zotero, Mendeley, LaTeX, Obsidian |
| `referensi.ris` | Zotero, EndNote, Mendeley |
| `referensi.xml` | EndNote (Reference Manager XML) |
| `referensi.txt` | Daftar Pustaka siap tempel (APA/Vancouver/IEEE) |

Semua kolom sumber dipertahankan; kolom kosong tidak diisi dengan tebakan. DOI yang
tidak ada ditandai, bukan ditebak.

---

## 5. Aturan keabsahan daftar pustaka

1. **Sumber tidak boleh fiktif.** Bila DOI tidak ditemukan, cari di Crossref
   (`https://api.crossref.org/works?query.bibliographic=...`) atau Google Scholar
   dan catat URL yang benar-benar dicek.
2. **Penomoran konsisten.** `[L-1]` di teks harus sama dengan entri ke-1 di
   Daftar Pustaka. Jalankan `scripts/proposal_doctor.py` untuk memeriksa.
3. **Sumber primer lebih diutamakan** daripada kutipan sekunder untuk klaim empiris.
4. **Batas waktu.** Umumnya 10 tahun terakhir, kecuali teori dasar atau definisi
   yang masih baku.
5. **Satu kali penulisan.** Jangan menulis `[L-1]` dengan ejaan berbeda di tempat lain.

---

## 6. Alur kerja akhir

```bash
# 1) kumpulkan literatur (skill paper-review)
#    -> matriks_referensi.csv, referensi.bib

# 2) susun proposal (skill proposal-skripsi)
#    bab1, bab2, bab3 memakai penanda [L-n]

# 3) ekspor Daftar Pustaka
python3 scripts/export_referensi.py matriks_referensi.csv --out-dir outputs/

# 4) periksa naskah
python3 scripts/proposal_doctor.py outputs/proposal.md \
    --dataset data/responden.csv --hasil-uji outputs/hasil_uji.json --strict

# 5) bangun DOCX
bash scripts/build_docx.sh outputs/proposal.md --out-dir outputs/ --toc --clean
```

---

## 7. Pilihan tidakdiekspor

Ekspor LaTeX, PPTX, dan PDF berada di luar cakupan skill ini. Bila diperlukan,
gunakan `build_docx.sh` lalu konversi di aplikasi yang sesuai, atau minta pengguna
memilihnya secara eksplisit.

---

## 8. Pemeriksaan silang antar-skrip

Setelah daftar pustaka diekspor, tiga pemeriksa saling menutupi titik gagal:

```bash
# 1) validasi matriks (field kosong, baris tanpa judul)
python3 scripts/export_referensi.py matriks_referensi.csv --periksa

# 2) konsistensi penanda [L-n], placeholder, angka tanpa sumber, sinkronisasi DOCX
python3 scripts/proposal_doctor.py outputs/proposal.md \
    --dataset data/responden.csv --hasil-uji outputs/hasil_uji.json \
    --docx outputs/proposal.docx --strict

# 3) gaya bahasa Indonesia + struktur BAB I
python3 scripts/id_language_check.py outputs/proposal.md --struktur --strict
```

`proposal_doctor.py` memeriksa `[D:kolom]` terhadap header CSV asli dan `[L-n]`
terhadap Daftar Pustaka, sehingga penomoran yang bergeser antara teks, tabel, dan
daftar akan tertangkap sebelum naskah diserahkan ke pembimbing.
