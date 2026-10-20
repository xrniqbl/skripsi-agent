# Data Sources — Klasifikasi, Ekstraksi & Inventarisasi File Lokal

Panduan **STEP 1**. Sumber utama proposal ini adalah **file lokal** yang ditunjuk pengguna, bukan
pencarian internet. Folder bisa berisi campuran literatur, dataset, pedoman kampus, dan berkas
tidak relevan — tugas agent adalah **menginventory semuanya**, lalu memetakan mana yang bisa
dibrugi sebagai bukti.

## 1. Peta Klasifikasi

Jalankan `scripts/ingest_sources.sh <folder> [--out .cache_ekstrak]` untukClasses file + ekstraksi
teks PDF), lalu klasifikasikan tiap file ke satu dari lima kategori:

| Kategori | Ekstensi | Kriteria deteksi (nama file/isi) | Digunakan untuk |
|----------|----------|--------------------------------|-----------------|
| **Literatur** | `.pdf .docx .md .txt .tex` | memuat: judul, penulis, tahun, abstract/"abstrak", jurnal/proceedings | BAB II, latar belakang, argumen gap |
| **Data kuantitatif** | `.csv .tsv .xlsx .xls .json .sav .dta` | memuat header kolom + ≥5 baris data; atau nama file berisi "data","jawaban","responden","skor","survey","hasil" | BAB III: profil & rancangan analisis |
| **Pedoman / template** | `.docx .pdf .md` | nama memuat: "pedoman","skripsi","tesis","disertasi","format","panduan","template","proposal" | Struktur bab, gaya penulisan |
| **Aturan / etika** | `.md .pdf .docx` | memuat "etika","informed consent","persetujuan","pembimbing","sidang" | Persetujuan etik, alurtypename |
| **Lainnya** | `.png .jpg .pptx .zip .py .r .ipynb .json` (non-data) | sisanya | Catat di inventaris, jangan dipaksa |

> File `.json` bersifat ambigu: array of objects → **data**; objek konfigurasi → **lainnya**.
> Periksa 20 baris pertama (`head -20`) sebelum memutuskan.

## 2. Cara Membaca Tiap Jenis File

### 2.1 PDF (literatur)
```bash
# cepat (poppler)
pdftotext -layout "file.pdf" -

# atau via script (membuat .txt sejajar, rekursif)
scripts/ingest_sources.sh <folder>
```
Batas baca (**hemat konteks** — baca bagian yang relevan saja):
1. **Abstrak** (1 paragraf)
2. **Pendahuluan** → cari gap yang diklaim penulis
3. **Metode** → populasi, sampel, teknik analisis
4. **Hasil** → temuan + angka kunci
5. **Kesimpulan/saran** → rekomendasi lanjutan

Hindari membaca seluruh isi PDF; gunakan `pdftotext` + potongan baris (mis. `sed -n '1,60p'`)
untuk bagian-bagian tersebut.

### 2.2 PDF hasil scan / gambar
`pdftotext` menghasilkan teks kosong → tandai `PERLU_OCR` di inventaris.
Tawarkan: (a) user memberi versi digital, (b) OCR (`ocrmypdf`/`tesseract`) bila terpasang,
(c) tetap pakai metadata dari nama file saja. **Jangan mengarang isi dokumen tak terbaca.**

### 2.3 DOCX
Docx adalah zip berisi XML. Ekstraksi tanpa dependensi:
```bash
# macOS: textutil bawaan
textutil -convert txt -stdout "file.docx"

# alternatif python (stdlib)
python3 -c "import zipfile,re,sys;x=zipfile.ZipFile(sys.argv[1]).read('word/document.xml').decode('utf8');print(re.sub('<[^>]+>','',re.sub('</w:p>','\n',x)))" file.docx
```
Bila `textutil` tidak tersedia (Linux), pakai `pandoc file.docx -t plain`.

### 2.4 CSV / TSV / XLSX / JSON (data)
- Ringkas dulu, jangan dump seluruh file: `head -5`, `wc -l`, jumlah kolom.
- Estimasi ukuran file: < 2 MB masih aman dibaca sebagian; lebih besar → wield profilkan dengan
  `scripts/profile_dataset.py` (bukan dibaca mentah).
- For XLSX: `openpyxl` dibutuhkan (`pip3 install openpyxl`); tanpa itu, minta user ekspor ke CSV.
- Semicolon-delimited CSV (umum di Indonesia/Excel lokal) harus ditangani — lihat `profile_dataset.py`
  (deteksi delimiter otomatis).

### 2.5 MD / TXT
Baca langsung dengan `read` tool. Bila terlalu panjang, baca per bagian heading.

## 3. Inventaris: Format Output

`sumber_inventaris.json` (master data, schema tetap):

```json
{
  "root": "/path/ke/folder",
  "scanned_at": "2026-03-01",
  "counts": {"total": 42, "literatur": 18, "data": 3, "pedoman": 2, "lainnya": 19},
  "files": [
    {
      "path": "literatur/ahmad2021.pdf",
      "kategori": "literatur",
      "ekstensi": ".pdf",
      "bytes": 812345,
      "ekstraksi": "ok",
      "judul": "Pengaruh X terhadap Y",
      "tahun": 2021,
      "penulis": "Ahmad, B.",
      "sumber": "Jurnal Manajemen Indonesia",
      "doi": "10.xxxx/abcd",
      "ringkas": "1–2 kalimat: tujuan, metode, temuan, keterbatasan",
      "marker": "L-1"
    },
    {
      "path": "data/responden.csv",
      "kategori": "data",
      "bytes": 51200,
      "ekstraksi": "ok",
      "rows": 120,
      "cols": 18,
      "delimiter": ";",
      "catatan": "18 butir kuesioner skala 1–5, 4 variabel independen",
      "marker": "D-1"
    }
  ]
}
```

`sumber_inventaris.md` = versi manusia: tabel per kategori (nama file, jenis, tahun, sumber,
status ekstraksi, catatan) + **catatan kelengkapan** (file tak terbaca, file ambigu, duplikat).

## 4. Penandaan Sumber (Wajib)

Setelah inventaris jadi, tiap sumberLiterature diberi **marker** yang dipakai di seluruh proposal:

| Marker | Arti | Contoh pemakaian |
|--------|------|-----------------|
| `[L-1]`, `[L-2]`, … | Literatur ke-1, ke-2, … pada inventaris (urutan tetap) | "…meningkatkan kepatuhan pajak [L-4]." |
| `[D:kolom]` | Berasal dari dataset, sebut nama kolom | "Rata-rata skor fatigue sebesar 3,42 [D:Skor_Fatigue]." |
| `[D]` | Dataset tanpa kolom spesifik (mis. jumlah responden) | "Sebanyak 120 responden [D]." |
| `[U]` | Dinyata user (brief/tanggal/jawaban/konteks) | "Penelitian dilakukan di Toko A [U]." |
| `[P-1]` | Pedoman/aturan Institutional | "Sesuai pedoman [P-1], waktu maksimum …" |
| `(inferensi)` | Penalaran agent, bukan klaim sumber | "Temuan ini mengindikasikan … (inferensi)." |
| `(diringkas)` | Parafrase dari sumber, bukan kutipan verbatim | — |

> Nomor marker **tidak boleh berubah** setelahbab II ditulis. Kalau sumber dihapus/ditambah,
> perbarui seluruh dokumen sekaligus (gunakan `grep` pada marker).

## 5. Deteksi_dataset di Tengah Literatur

Literature sering memuat tabel hasil (nilai mean, SD, jumlah responden) — **boleh** dipakai sebagai
pendukung dengan marker `[L-n]`, tapi **dilarang** diperlakukan sebagai data penelitian ini.
Bedakan tegas dalam naskah:
- Data penelitian ini → `[D:kolom]`
- Angka dari penelitian terdahulu → `[L-n]`

## 6. Aturan Anti-Hallucination Sumber

1. **Judul/tahun/penulis/DOI hanya diisi** jika benar-benar terbaca di file (halaman judul, header,
   atau metadata). Tidak terbaca → kosongkan, tulis `—` (jangan ditebak dari nama file).
2. **JanganARD** mengarang referensi yang tidak ada di folder maupun hasil search terverifikasi.
3. **Jangan** menyatakan "penelitian terdahulu menunjukkan X" tanpa marker.
4. File yang tidak jelas perannya → **tanyakan** user, jangan masukkan diam-diam sebagai landasan.
5. Semua file inventaris **tercatat**, termasuk yang tidak dipakai ("mempertimbangkan alasan tidak
   dipakai" —mis. "duplikat dari [L-3]", "buku teks umum, bukan sumber primer").
