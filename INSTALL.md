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

## 5. Dependensi Skrip Python (opsional, untuk skill ber-skrip)

Sebagian skill membawa skrip bantu. Untuk memakai fungsi penuhnya:

```bash
pip install python-docx lxml pyyaml scipy
# ekspor DOCX proposal_skripsi membutuhkan pandoc:
# https://pandoc.org/installing.html
```

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
