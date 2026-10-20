---
name: jurnal-submit-pack
description: Package a finished journal manuscript for OJS submission (double-blind version, metadata file, originality statement, file checks). Use when the user mentions submit jurnal, OJS, unggah naskah, double-blind, blind review, pernyataan orisinalitas, or artikel sudah jadi siap kirim.
license: MIT
compatibility: opencode
metadata:
  audience: researchers
  format: docx
---

# SKILL: Paket Submit Jurnal (OJS, Double-Blind)

Skill mengemas naskah jurnal yang **sudah final** menjadi paket siap unggah OJS:
versi blind-review + metadata + pernyataan + cek berkas. Memakai
`smart_write.py`/`proofread_id.py` (skill `office-word-mcp`).

---

## 0. Alur standar

```
1. Final-check → 2. Versi blind → 3. Metadata + pernyataan → 4. Cek berkas → 5. Serahkan
```

### 1. Final-check (jangan kemas naskah bermasalah)

```bash
VENV=/path/ke/repo-office/.venv-mcp/bin/python
export PYTHONPATH=/path/ke/repo-office
$VENV proofread_id.py Naskah.docx            # harus BERSIH (exit 0)
$VENV smart_write.py info Naskah.docx        # catat word_count, table_count
```

Bila ERROR → perbaiki dulu (lihat skill `jurnal-writing` §4 + resep
`office-word-mcp` §5). Naskah kotor yang dikemas = kerja dua kali.

### 2. Versi double-blind (`Naskah_SUBMIT.docx`)

Hapus identitas penulis dari salinan (jangan timpa naskah asli!):

```bash
cp Naskah.docx Naskah_SUBMIT.docx
$VENV -c "
import asyncio
from word_document_server.tools import content_tools
async def main():
    # sesuaikan string dengan isi blok judul dokumen target
    for lama in ['Andy Pratama', 'andypratama1211@gmail.com',
                 'Politeknik Pertanian Negeri Samarinda']:
        print(await content_tools.search_and_replace(
            'Naskah_SUBMIT.docx', lama, '[NAMA DIHAPUS UNTUK BLIND REVIEW]'))
asyncio.run(main())
"
$VENV smart_write.py info Naskah_SUBMIT.docx  # pastikan masih utuh
```

Aturan blind: hapus nama penulis, email, afiliasi, ucapan terima kasih yang
menyebut institusi, dan properti dokumen (Title/Author bila berisi nama).
**Jangan** hapus sitasi karya sendiri bila gayanya Harvard/APA naratif —
cukup samarkan afiliasi; penghapusan sitasi diri total justru mencurigakan.

### 3. Metadata OJS (`metadata.txt`) + pernyataan orisinalitas

Ekstrak sekali, pakai untuk form OJS (Judul, Abstrak ID+EN, Kata kunci) +
dokumen tambahan wajib:

```bash
$VENV smart_write.py read Naskah.docx > /tmp/isi.txt
# susun metadata.txt: Judul | Penulis+afiliasi+email | Abstrak ID | Abstract EN |
# Kata kunci | Klasifikasi/JEL bila diminta jurnal
```

Template pernyataan (sesuaikan nama jurnal, tanda tangan bermeterai):

> Yang bertanda tangan di bawah ini, [Nama penulis korespondensi],
> menyatakan bahwa naskah berjudul "[Judul]" adalah karya asli, belum pernah
> dipublikasikan di mana pun dalam bahasa apa pun, tidak sedang dalam proses
> pengajuan ke penerbit lain, dan semua penulis menyetujui pengirimannya ke
> [Nama Jurnal]. Segala pelanggaran etika publikasi menjadi tanggung jawab
> penulis.
>
> [Kota], [Tanggal] — [Tanda tangan + nama terang]

File tambahan OJS yang sering wajib: pernyataan etika + hak cipta (PDF),
instrumen riset/dataset/gambar resolusi asli (opsional tapi memperkuat).

### 4. Cek berkas (gerbang terakhir)

| Syarat umum OJS SINTA | Perintah | Batas |
|------------------------|----------|-------|
| Ukuran file | `ls -lh Naskah_SUBMIT.docx` | ≤ 2 MB |
| Format | `.doc`/`.docx` hasil Word asli (bukan hasil konversi) | — |
| Halaman | buka di Word → status bar | ≤ batas jurnal (umum 8–10) |
| Similarity | Turnitin/iThenticate akun kampus | ≤ 20–25% |
| Referensi | tiap sitasi ada pasangan (cek `jurnal-writing` §4) | 100% |

### 5. Serahkan + catat

Serahkan ke user: `Naskah_SUBMIT.docx`, `metadata.txt`, pernyataan, dan
ringkasan cek (kata, tabel, gambar, similarity). Jangan mengunggah ke OJS
atas nama user — kredensial milik penulis.

---

## Anti-patterns

| ❌ Jangan | ✅ Lakukan |
|-----------|-----------|
| Timpa naskah asli dengan versi blind | Salinan `_SUBMIT` — naskah asli tetap beridentitas |
| Blind setengah (nama hilang, email tertinggal) | Daftar string identitas eksplisit, verifikasi via `read` |
| Metadata diketik ulang manual dari ingatan | Ekstrak dari naskah (`read`), satu sumber kebenaran |
| Kemas sebelum proofread bersih | `proofread_id.py` exit 0 dulu |
| Unggah OJS pakai akun/identitas user | User yang unggah; agent menyiapkan paket |
