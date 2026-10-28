# Panduan Install — Skripsi Agent

Bundel ini berbentuk kumpulan folder skill. Setiap folder di `skills/` yang memiliki
`SKILL.md` adalah satu skill mandiri. Cara install bergantung pada platform agent yang
Anda pakai: salin folder skill ke tempat platform membaca skill, atau unggah isinya
sebagai pengetahuan/instruksi.

## 0. Unduh

```bash
git clone https://github.com/xrniqbl/skripsi-agent.git
cd skripsi-agent
```

Atau unduh ZIP dari halaman repo (Code → Download ZIP) lalu ekstrak.

## 1. Claude Code (CLI)

Salin semua skill, atau hanya yang dibutuhkan, ke direktori skill personal:

```bash
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
```

Untuk cakupan proyek tertentu, salin ke `.claude/skills/` di root proyek. Folder
`ars_shared_files` dan `shared` harus ikut tersalin — suite ARS memerlukannya.
Mulai ulang sesi Claude Code; skill akan terdeteksi dari nama folder dan frontmatter
`SKILL.md`-nya.

## 2. Claude.ai (web/desktop — Skills)

1. Buka Settings → Capabilities → Skills (atau menu Skills pada versi terbaru).
2. Untuk tiap skill yang diinginkan, buat ZIP berisi folder skill tersebut
   (folder terluar ikut di dalam ZIP, `SKILL.md` berada di dalamnya):

   ```bash
   cd skills && zip -r ../proposal_skripsi.zip proposal_skripsi && cd ..
   ```

3. Unggah ZIP tersebut. Ulangi untuk skill lain yang diperlukan.
   Catatan: skill yang bergantung pada folder bersama (`ars_*`) paling andal dipakai
   lewat Claude Code atau agent berbasis berkas, karena Claude.ai memperlakukan tiap
   skill sebagai paket terpisah.

## 3. ChatGPT / Custom GPT

ChatGPT tidak menjalankan format skill secara native; gunakan dua cara berikut:

- **Custom GPT**: buat GPT baru di chatgpt.com/gpts → Configure → unggah `SKILL.md`
  root repo ini beserta `SKILL.md` sub-skill yang relevan (dan file referensinya) ke
  bagian Knowledge, lalu tempel isi `SKILL.md` root sebagai Instructions.
- **Project / sesi biasa**: unggah file `SKILL.md` root + sub-skill terkait ke dalam
  Project atau lampirkan pada percakapan, lalu minta ChatGPT mengikuti alur di
  dalamnya sebelum mulai bekerja.

Skrip Python pendamping (office_skripsi, proposal_skripsi) dapat dijalankan ChatGPT
hanya pada lingkungan yang menyediakan eksekusi kode; pada sesi tanpa kode, agent
akan mengikuti panduan proseduralnya saja.

## 4. Agent Berbasis Berkas Lain (Cursor, Windsurf, Copilot, Muse, dll.)

1. Clone repo ini ke lokasi yang bisa dibaca agent (mis. di dalam workspace Anda).
2. Arahkan agent ke `SKILL.md` root sebagai instruksi utama (sebagai rules/context
   file sesuai mekanisme platform Anda).
3. Agent akan menelusuri sub-skill di `skills/` sesuai tahap pekerjaan.

## 5. Dependensi Skrip Python

Sebagian skill membawa skrip bantu. Pasang dengan venv, jangan ke Python sistem:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# periksa apakah semua impor tercatat dan terpasang:
.venv/bin/python scripts/cek_dependensi.py
```

`requirements.txt` berisi dependensi wajib (python-docx, lxml, PyYAML, openpyxl, scipy).
Ada dua berkas tambahan:

| Berkas | Untuk apa |
|---|---|
| `requirements.txt` | wajib — dipakai sebagian besar skrip DOCX/YAML/statistik |
| `requirements-office.txt` | opsional — hanya `skills/office_word_files` (server MCP Word) |
| `requirements-dev.txt` | opsional — `pytest` untuk menjalankan tes |

### Alat sistem (bukan paket Python)

Beberapa skrip memanggil program luar. Kalau tidak ada, skrip gagal dengan pesan jelas
(bukan traceback):

| Alat | Dibutuhkan oleh | Pasang |
|---|---|---|
| `soffice` (LibreOffice) | `buat_daftar_isi.py`, konversi PDF | `apt-get install libreoffice` |
| `pdfinfo`, `pdftotext` (poppler-utils) | `audit_halaman.py` | `apt-get install poppler-utils` |
| `pandoc` | ekspor DOCX proposal_skripsi | https://pandoc.org/installing.html |

### Menjalankan tes

```bash
.venv/bin/python tests/tes_bundel.py          # seluruh bundel
bash skills/topik_skripsi/tests/run_tests.sh  # per skill
bash skills/bab_iv_v/tests/run_tests.sh
bash skills/sidang/tests/run_tests.sh
bash skills/revisi_pembimbing/tests/run_tests.sh
bash skills/format_kampus/tests/run_tests.sh
```

Setiap tes keluar kode 1 bila ada yang gagal, jadi bisa dipakai di CI.

Setelah install, jalankan test bawaan masing-masing skill (folder `tests/` bila ada)
untuk memastikan lingkungan lengkap sebelum dipakai pada dokumen penting.

## 6. Memilih Skill Saja (tanpa seluruh bundel)

Setiap folder skill dapat disalin sendiri-sendiri, kecuali:

- Semua `ars_*` membutuhkan `ars_shared_files/` (atau `shared/`) di sampingnya.
- `skripsi_writing`, `office_word_mcp`, `jurnal_writing`, dan `jurnal_submit_pack`
  memanfaatkan skrip di `office_skripsi/` dan/atau server di `office_word_files/` —
  salin bersama bila memakai fungsi DOCX-nya.

## Pembaruan

```bash
cd skripsi-agent && git pull
```

lalu salin ulang folder skill ke direktori platform Anda.
