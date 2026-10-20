---
name: jurnal-writing
description: Write academic journal articles (IMRAD structure, bilingual abstract, citations) in Indonesian or English as Word documents. Use when the user mentions jurnal, journal article, paper, artikel ilmiah, IMRAD, abstrak/abstract, or submitting to a journal.
license: MIT
compatibility: opencode
metadata:
  audience: researchers
  format: docx
---

# SKILL: Penulisan Artikel Jurnal

Skill menulis artikel jurnal (Indonesia/Inggris) berstruktur **IMRAD** sebagai
dokumen Word, memakai `smart_write.py` (skill `office-word-mcp`) + hardening
`italic-foreign.py` dari repo office-skripsi.

---

## 0. Alur standar

```
1. Tanya target  →  2. Tulis live IMRAD  →  3. Hardening  →  4. Cek kelayakan submit
```

### 1. Tanya target dulu

- Jurnal tujuan (nama, template tersedia? Sinta/Scopus?) — template jurnal
  **selalu menang** atas struktur default di bawah
- Bahasa: Indonesia / Inggris / keduanya (abstrak dua bahasa?)
- Gaya sitasi (APA / IEEE / Vancouver) + minimal jumlah referensi
- Batas halaman/kata + data & hasil yang wajib dimuat (jangan mengarang!)

### 2. Struktur default (kalau tanpa template)

```bash
VENV=/path/ke/repo-office/.venv-mcp/bin/python
F=Artikel.docx

$VENV smart_write.py heading "$F" "JUDUL ARTIKEL MAKSIMAL 14 KATA" --level 1 --watch
$VENV smart_write.py append "$F" "Nama Penulis1, Nama Penulis2" "Afiliasi, email korespondensi"
$VENV smart_write.py heading "$F" "ABSTRAK" --level 1
$VENV smart_write.py append "$F" "Satu paragraf 150–250 kata: masalah, tujuan, metode, hasil utama + angka, simpulan. Diakhiri Kata kunci: 3–5 frasa."
$VENV smart_write.py heading "$F" "ABSTRACT" --level 1
$VENV smart_write.py append "$F" "English version of the abstract, same structure."
$VENV smart_write.py heading "$F" "1. PENDAHULUAN" --level 1
$VENV smart_write.py append "$F" "Gap penelitian → rumusan → tujuan → kontribusi. Setiap klaim penting bersitasi."
$VENV smart_write.py heading "$F" "2. METODE" --level 1
$VENV smart_write.py append "$F" "Desain, data/sampel, instrumen, analisis — cukup detail untuk direplikasi."
$VENV smart_write.py heading "$F" "3. HASIL DAN PEMBAHASAN" --level 1
$VENV smart_write.py append "$F" "Sajikan temuan objektif, lalu bahas makna + bandingkan dengan studi sebelumnya."
$VENV smart_write.py table "$F" 3 3 '[["Metrik","Nilai","Keterangan"],["Akurasi","92,1%","..."],["...","...","..."]]'
$VENV smart_write.py heading "$F" "4. KESIMPULAN" --level 1
$VENV smart_write.py append "$F" "Jawab tujuan, sebut keterbatasan, arah riset lanjut. Tanpa referensi baru."
$VENV smart_write.py heading "$F" "DAFTAR PUSTAKA" --level 1
$VENV smart_write.py append "$F" "Penulis. (Tahun). Judul. Jurnal, volume(halaman)."
```

Kaedah isi:

| Bagian | Aturan praktis |
|--------|----------------|
| Judul | Spesifik, ada variabel + konteks, tanpa singkatan tak umum |
| Abstrak | Tanpa sitasi, tanpa singkatan tanpa kepanjangan, ada angka hasil |
| Pendahuluan | Pola corong: umum → gap → tujuan; sitasi primer >80% |
| Metode | Replikabel: data, alat, parameter, uji statistik |
| Hasil | Fakta dulu, interpretasi di pembahasan; tiap tabel/gambar dirujuk di teks |
| Kesimpulan | Klaim ≤ bukti; sebut limitasi |

### 2b. Preset format siap pakai (teruji Okt 2026, naskah SINTA lolos cek)

Pilih SATU sebelum membangun dokumen (template jurnal tujuan selalu menang):

| Preset | Kertas/margin | Font/body | Kolom | Heading | Sitasi |
|--------|---------------|-----------|-------|---------|--------|
| **JTIIK** (SINTA 2, dua kolom) | A4, 3-3-2-2 (kiri-atas-kanan-bawah) | TNR 10pt spasi 1 | Judul+abstrak 1 kolom; badan 2 kolom @7,5 cm gap 1 cm; gambar/tabel full-width via section break | Judul caps 12pt; bab caps 10pt bold; abstrak EN italic | Harvard-Anglia caps (`NAMA, I., 2024.`) |
| **SINTA-1kol** (generik JURSISTEKNI/JI-UPGRIS) | A4, 3-3-2-2 | TNR 12pt spasi 1 | 1 kolom | Judul 14pt; bab 12pt bold | APA nama-tahun |

Detail bangun 2 kolom + full-width + Harvard: skill `office-word-mcp`
§5.7–§5.8. Setelah naskah final → kemas dengan skill `jurnal-submit-pack`.
Proofread otomatis: `proofread_id.py Naskah.docx` (harus BERSIH).

### 3. Hardening

```bash
# Italic istilah asing saja (terutama artikel Indonesia campur istilah Inggris)
python3 /path/ke/office-skripsi/scripts/italic-foreign.py audit Artikel.docx --strip-other
python3 /path/ke/office-skripsi/scripts/italic-foreign.py apply Artikel.docx --strip-other
# Verifikasi render
soffice --headless --convert-to pdf Artikel.italic.docx && pdftotext -layout Artikel.italic.pdf cek.txt
```

### 4. Cek kelayakan submit

- [ ] Semua sitasi in-text ada di Daftar Pustaka (dan sebaliknya)
- [ ] Tabel/gambar bernomor urut + dirujuk di teks
- [ ] Abstrak ≤ batas kata jurnal, kata kunci 3–5
- [ ] Tidak ada data/angka yang dikarang — tiap angka tertelusur ke sumber
- [ ] Similarity siap cek (parafrasa definisi umum dengan kalimat sendiri)
- [ ] Konversi md→docx: caption 1–N berurutan + semua acuan `(Gambar N)` cocok;
      gambar fit-box proporsional; istilah asing miring (lihat skill
      `office-word-mcp` §5)
- [ ] Kata kunci alfabetis + format ikut template (koma/titik-koma, italic?)
- [ ] Gaya sitasi ikut template (Harvard caps vs APA vs IEEE) — konversi
      menyeluruh badan + pustaka, bukan setengah (lihat `office-word-mcp` §5.8)
- [ ] Layout kolom ikut template (2 kolom = front-matter 1 kolom + gambar/tabel
      full-width via section break, lihat `office-word-mcp` §5.7)
- [ ] Double-blind: hapus nama penulis saat submit review; file <2 MB

---

## Anti-patterns

| ❌ Jangan | ✅ Lakukan |
|-----------|-----------|
| Sitasi dari sumber sekunder/abstrak saja | Baca & sitasi sumber primer |
| Klaim melebihi data | Batasi simpulan pada yang terbukti |
| Satu kalimat penuh miring karena 1 istilah Inggris | `italic-foreign.py --strip-other` |
| Mengarang angka/tabel | Minta data, tandai `[DATA]` bila kosong |
