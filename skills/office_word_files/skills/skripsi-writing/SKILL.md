---
name: skripsi-writing
description: Write Indonesian thesis/skripsi documents (BAB I–V) with proper academic structure, EYD/PUEBI language, and Word formatting. Use when the user mentions skripsi, thesis, BAB, abstrak, latar belakang, or writing academic final-project documents.
license: MIT
compatibility: opencode
metadata:
  audience: students
  format: docx
---

# SKILL: Penulisan Skripsi (Indonesia)

Skill menulis dokumen skripsi berbahasa Indonesia dari nol sampai siap revisi,
memakai `smart_write.py` (lihat skill `office-word-mcp`) + tooling repo
**office-skripsi** untuk hardening format.

---

## 0. Alur standar

```
1. Tanya struktur  →  2. Tulis live per bab  →  3. Hardening format  →  4. Verifikasi render
```

### 1. Tanya struktur dulu (jangan asal tulis)

Minimal sebelum menulis:

- Judul, nama, NIM, prodi, fakultas, universitas, tahun
- Penomoran bab (`BAB I` / `Bab 1`), sub-bab (`1.1`), judul KAPITAL / Title Case
- Topik tiap bab + data/angka yang harus muncul (jangan mengarang data penelitian!)
- Pedoman kampus (font, spasi, margin) — kalau tidak ada, pakai default dan
  **tandai sebagai asumsi**

### 2. Tulis per bab dengan smart_write

```bash
VENV=/path/ke/repo-office/.venv-mcp/bin/python
F=Skripsi.docx

$VENV smart_write.py heading "$F" "JUDUL SKRIPSI" --level 1 --watch
$VENV smart_write.py append "$F" "SKRIPSI" --style "Heading 2"
$VENV smart_write.py heading "$F" "ABSTRAK" --level 1
$VENV smart_write.py append "$F" "Paragraf abstrak: tujuan, metode, hasil + angka, simpulan. Diakhiri Kata kunci: ..." --delay 1.5
$VENV smart_write.py heading "$F" "BAB I PENDAHULUAN" --level 1
$VENV smart_write.py append "$F" "1.1 Latar Belakang" --style "Heading 2"
$VENV smart_write.py append "$F" "Paragraf 1: konteks umum..." --delay 1.5
# ... dst. per sub-bab: 1.2 Rumusan Masalah, 1.3 Tujuan, 1.4 Manfaat
# BAB II Tinjauan Pustaka, BAB III Metode (+ tabel via smart_write table),
# BAB IV Hasil & Pembahasan, BAB V Penutup, DAFTAR PUSTAKA
```

Struktur isi per bab (ringkas):

| Bab | Wajib ada |
|-----|-----------|
| ABSTRAK | Tujuan, metode + sampel, hasil + angka, simpulan, kata kunci |
| BAB I | Latar belakang (umum→khusus→masalah), rumusan, tujuan, manfaat teoretis+praktis |
| BAB II | Definisi konsep, penelitian terdahulu, kerangka berpikir/hipotesis |
| BAB III | Desain, populasi+sampel, instrumen+uji validitas/reliabilitas, teknik analisis, jadwal (tabel) |
| BAB IV | Gambaran responden, hasil (angka/persamaan), pembahasan vs teori |
| BAB V | Simpulan (jawab rumusan), saran (praktis + peneliti lanjut) |
| DAFTAR PUSTAKA | Hanya yang disitasi di isi |

### 3. Hardening format (repo office-skripsi)

Setelah konten selesai — JANGAN saat masih menulis:

```bash
cd /path/ke/office-skripsi
cp Skripsi.docx Skripsi_backup.docx

# Italic HANYA untuk istilah asing (audit dulu!)
python3 scripts/italic-foreign.py audit Skripsi.docx --strip-other
python3 scripts/italic-foreign.py apply Skripsi.docx --strip-other  # → Skripsi.italic.docx

# Kalau heading diketik manual (1.1, 2.1.2): jadikan numbering asli
unzip -q Skripsi.italic.docx -d work/unpacked/
python3 scripts/merge-runs.py work/unpacked/word/document.xml
python3 scripts/numbering.py work/unpacked/ analyze
python3 scripts/numbering.py work/unpacked/ convert
cd work/unpacked && zip -Xr ../Skripsi_final.docx . && cd ..
python3 scripts/validate-docx.py work/Skripsi_final.docx
```

Aturan italic (PUEBI): istilah asing miring (`machine learning`, `framework`);
**jangan** miringkan nama produk/library (`Laravel`, `MySQL`), akronim (`API`),
heading, caption, Daftar Isi, Daftar Pustaka, potongan kode.

### 4. Verifikasi = render, bukan klaim

```bash
soffice --headless --convert-to pdf Skripsi_final.docx
pdftotext -layout Skripsi_final.pdf Skripsi_final.txt
grep -n "BAB I\|DAFTAR PUSTAKA" Skripsi_final.txt
```

---

## Anti-patterns

| ❌ Jangan | ✅ Lakukan |
|-----------|-----------|
| Mengarang data/angka penelitian | Minta data ke penulis, tandai placeholder `[DATA]` |
| Miringkan seluruh kalimat berisi 1 istilah asing | `italic-foreign.py --strip-other` |
| Italic di heading | Biarkan tegak — bocor ke Daftar Isi |
| Format manual sebelum konten selesai | Konten dulu, hardening belakangan |
| Klaim "sesuai pedoman" tanpa file pedoman | Minta PDF pedoman, catat asumsi |
