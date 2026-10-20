---
name: office-word-mcp
description: Create, read, and edit Microsoft Word (.docx) files via the Office-Word MCP server and smart_write helper. Use when the user mentions Word documents, DOCX read/write, live Word editing, reloading Word, tables, headings, or document automation.
license: MIT
compatibility: opencode
metadata:
  audience: developers
  format: docx
---

# SKILL: Office-Word MCP — Baca/Tulis Word Manual & Live

Skill ini mengajarkan agent cara membuat, membaca, dan mengedit dokumen Word (`.docx`)
lewat **Office-Word-MCP-Server** (protocol MCP) dan helper **`smart_write.py`**.

Repo: hasil fork dari `gongrzhe/office-word-mcp-server` + helper live-edit macOS.

---

## 0. Cara kerja (pahami dulu)

| Jalur | Mekanisme | Cocok untuk |
|-------|-----------|-------------|
| **MCP tools** (`word-document-server`) | `python-docx`: tulis langsung ke file di disk | Semua operasi, termasuk tabel & format |
| **Live mode** (`live_write.py` via AppleScript) | Sisip teks ke dokumen yang **sedang terbuka** di Word for Mac | Append paragraf/heading di ujung dokumen, terlihat mengetik |
| **smart_write.py** | Otomatis pilih jalur + jaga sinkronisasi | **Pakai ini sebagai default** |

> Batasan fundamental: `python-docx` tidak berkomunikasi dengan aplikasi Word.
> Word memuat dokumen ke memori — tulisan via file baru terlihat setelah **reload**.
> Live mode menulis ke memori Word langsung — terlihat seketika, tanpa tutup-buka.

---

## 1. Perintah utama — `smart_write.py`

```bash
export PYTHONPATH=/path/ke/repo-office
VENV=/path/ke/repo-office/.venv-mcp/bin/python

# Tulis live (kalau dokumen terbuka) atau via file (kalau tertutup)
$VENV smart_write.py append FILE.docx "teks paragraf" [--style "Heading 2"] [--delay 1.5] [--watch]
$VENV smart_write.py heading FILE.docx "Judul Bab" [--level 1] [--delay 1] [--watch]
$VENV smart_write.py pagebreak FILE.docx [--watch]

# Operasi file (otomatis save → tulis → reload bila dokumen terbuka)
$VENV smart_write.py table FILE.docx ROWS COLS '[["a","b"],["1","2"]]' [--watch] [--no-reload]
$VENV smart_write.py replace FILE.docx "lama" "baru" [--watch] [--no-reload]
$VENV smart_write.py sync FILE.docx [--watch]  # save + satu reload (penutup batch)

# FILE boleh "auto" = dokumen AKTIF di Word (deteksi otomatis, tanpa hardcode)
$VENV smart_write.py info auto
$VENV reload_word.py            # reload dokumen aktif, background
$VENV reload_word.py FILE.docx --watch   # reload + bawa Word ke depan

# Baca (tidak mengubah apa pun)
$VENV smart_write.py read FILE.docx
$VENV smart_write.py info FILE.docx
```

Batch hemat reload (3 operasi file = 1 reload):

```bash
$VENV smart_write.py table F.docx 2 2 '[["a","b"],["1","2"]]' --no-reload
$VENV smart_write.py replace F.docx "lama" "baru" --no-reload
$VENV smart_write.py sync F.docx
```

Reload itu background murni: Word disembunyikan sesaat selama tukar dokumen
(tanpa kedip bila di background), posisi scroll dikembalikan, fokus aplikasi
tidak dicuri. `--watch` hanya untuk demo yang memang ditonton.

Aturan sinkronisasi (jangan dilawan):

1. Habis **live-write** → `save` dulu sebelum operasi file.
2. Habis **operasi file** saat dokumen terbuka → **reload** dulu sebelum live-write.
3. `smart_write.py` sudah melakukan 1–2 otomatis. Jangan campur pemanggilan
   langsung ke MCP tools + AppleScript manual tanpa mengikuti urutan ini.

Kemampuan live mode: **append di ujung dokumen saja**, style per paragraf
(`Normal`, `Heading 1`–`Heading 9`), page break. Tabel, replace tengah,
format per-kata, dan hapus → lewat jalur file.

---

## 2. MCP server langsung (tanpa smart_write)

Berguna untuk operasi batch/skrip, atau saat Word tidak terlibat.

```bash
PYTHONPATH=/path/ke/repo-office $VENV -c "
import asyncio
from word_document_server.tools import document_tools, content_tools, format_tools
async def main():
    print(await document_tools.create_document('lap.docx', title='Judul', author='Nama'))
    print(await content_tools.add_heading('lap.docx', 'Pendahuluan', level=1))
    print(await content_tools.add_paragraph('lap.docx', 'Isi...'))
    print(await content_tools.add_table('lap.docx', 2, 2, [['A','B'],['1','2']]))
    print(await format_tools.highlight_table_header('lap.docx', 0))
    print(await document_tools.get_document_text('lap.docx'))
asyncio.run(main())
"
```

Semua tool MCP bersifat `async` — bungkus dengan `asyncio.run`.

---

## 3. Mendaftarkan MCP ke OpenCode

`install.sh` melakukannya otomatis. Manual:

```json
{
  "mcp": {
    "word-document-server": {
      "type": "local",
      "command": "/path/ke/repo-office/.venv-mcp/bin/python",
      "args": ["/path/ke/repo-office/word_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/ke/repo-office",
        "MCP_TRANSPORT": "stdio"
      },
      "enabled": true
    }
  }
}
```

Restart OpenCode setelah mengubah config.

---

## 4. Anti-patterns

| ❌ Jangan | ✅ Lakukan |
|-----------|-----------|
| Harap tulisan file langsung terlihat di Word yang terbuka | `reload_word.py` / tutup-buka ulang / pakai live mode |
| Mengetik manual di Word saat live-write berjalan | Diam dulu — reload memakai `saving no`, ketikan belum-save hilang |
| Ganti isi tengah dokumen via live mode | `replace` (jalur file) |
| Klaim tabel/format aman tanpa cek | `info` → `table_count`, `read` → verifikasi teks |
| Commit `.venv-mcp/` ke git | Sudah di `.gitignore` — tiap device bikin venv sendiri via `install.sh` |
| Resize gambar asal (distorsi / luber halaman) | Fit-box proporsional (§5.3) |
| Ganti nomor caption tanpa perbaiki acuan di teks | Renumber + ref selalu satu paket (§5.4) |
| Edit XML langsung untuk ganti teks | Replace run-preserving (§5.5) |
| Sisip `teks+break` di ujung (`X` lalu `\r`) | **Break dulu lalu teks** (`\r` lalu `X`) — urutan terbalik menempel ke paragraf lama bila dokumen berakhir tanpa paragraf kosong |
| Percaya `active document` langsung setelah `open` | `ensure_active`: poll nama dokumen aktif hingga cocok (timeout) baru jalan; `verify_saved` setelah save |
| `info auto` gagal padahal dokumen terbuka | `auto` = dokumen AKTIF; bila Word di background tanpa jendela aktif, fallback cek `get name of every document` (`is_open`) |
| Verifikasi warna/link klaim "sudah" | Baca ulang run: `str(r.font.color.rgb)`, `r.underline` — substring bisa false-positive (`lapisan` mengandung `lapis`, gunakan word-boundary) |
| Reload sukses tapi konten Word basi | Cek `count documents` — dokumen mungkin tertutup oleh run gagal sebelumnya; buka ulang biasa (tanpa System Events) |
| Asumsi reload gagal = file rusak | Pisahkan diagnosis: file di disk (baca via python-docx) vs tampilan Word (AppleScript); perbaiki yang terbukti rusak saja |

---

## 5. Membangun dokumen jurnal dari Markdown + gambar (resep terbukti)

Pola yang dipakai untuk `Jurnal_Andy_Pratama.docx` (4000 kata, 6 tabel, 8 gambar).
Prinsip: **satu skrip build → verifikasi → satu reload di akhir.**

### 5.1 Parse Markdown → python-docx

| Sintaks md | Hasil docx |
|------------|-----------|
| `# ` | Judul 16pt bold tengah |
| `## ` / `### ` | Heading 1 (14pt) / Heading 2 (12pt), Times New Roman |
| `**tebal**`, `*miring*`, `` `kode` `` | Run bold / italic / Consolas 10pt (regex `(\*\*.+?\*\*|\*[^*\n]+?\*|`+"`[^`\n]+?`"+`)`) |
| Tabel `\|` + baris pemisah | `Table Grid`, header shading `4472C4` + teks putih bold |
| Blok ```` ```mermaid ```` | Ekstrak isi `[...]` → paragraf style `List Number` |
| Rumus `$...$` | Ganti jadi teks polos (`x̄ = Σxi / n`) |
| `> ` | Catatan italic 11pt |

Daftar Pustaka: deteksi paragraf pola `Nama. (Tahun).` → *hanging indent*
(`left_indent` 1 cm + `first_line_indent` −1 cm).

### 5.2 Gambar: ekstrak, petakan, verifikasi visual

```python
from docx import Document
d = Document("skripsi.docx")
# 1) simpan semua part gambar (try/except: relasi non-image tidak punya .blob)
for rel in d.part.rels.values():
    try:
        blob, ct = rel.target_part.blob, rel.target_part.content_type
    except Exception:
        continue
    if blob and ct.startswith("image/"):
        ext = ct.split("/")[-1]
        open(f"fig/{rel.target_ref.split('/')[-1]}.{ext}", "wb").write(blob)
# 2) urutan kemunculan di dokumen = urutan r:embed di document.xml
import re
embeds = re.findall(r'r:embed="(rId\d+)"', d.part.blob.decode("utf-8"))
```

- Gambar kecil (1–8 KB) biasanya ikon/logo — abaikan; yang besar berurutan
  biasanya cocok dengan urutan caption (Gambar 1–N). **Selalu verifikasi visual**
  minimal gambar kunci sebelum dipakai (salah label = fatal).
- Hanya sisipkan gambar yang **dirujuk di teks**; tiap penyisipan wajib ditemani caption.

### 5.3 Ukuran gambar: fit-box proporsional (A4, margin 3 cm)

Baca dimensi PNG dari header (byte 16–24, tanpa dependensi tambahan),
lalu muatkan ke kotak **maks 5,8 inci × 7,5 inci** (tinggi dibatasi agar
caption tetap sehalaman):

- Aspek ≤ 1,2 (screenshot, grafik): kunci **lebar** 5,8 inci.
- Aspek > 1,2 (flowchart tinggi, ERD): kunci **tinggi** 6,8 inci.
- Jangan set lebar+tinggi manual dari tebakan — selalu hitung dari dimensi asli.

### 5.4 Caption + acuan teks = satu paket

- Caption di bawah gambar, tengah, 11pt, label bold (`Gambar N.` + teks biasa).
- Urutan caption di dokumen **harus** 1–N berurutan — cek via
  `get_document_outline` / baca semua paragraf `Gambar \d+\.`.
- Tiap renumber caption, perbaiki **semua** acuan `(Gambar N)` di teks pada
  skrip yang sama. Sumber salah acuan umum: teks masih memakai nomor gambar
  dokumen asal (skripsi) padahal caption sudah dinomori ulang untuk jurnal.

### 5.5 Ganti teks tanpa menghancurkan format

Fungsi `replace_in_para(p, old, new)`: bila string target dalam **satu run**,
ganti di run itu saja. Bila terpecah antar-run, rebuild paragraf via parser
§5.1 (aman bila paragraf hanya berisi markdown inline). Jangan rebuild
paragraf yang berisi *field*, *hyperlink*, atau format manual kompleks.

### 5.6 Hardening layout (satu skrip, sebelum reload final)

- Body rata kanan-kiri, TNR 12, `space_after` 6pt, spasi tunggal, widow control.
- Heading 1/2: `keep_with_next` + `space_before` 12/6pt (heading tak boleh
  yatim di bawah halaman).
- Paragraf gambar: `keep_with_next` (gambar menempel caption);
  caption `space_before` 6pt + `space_after` 12pt.
- Header tabel: `w:tblHeader` = true (berulang tiap halaman).
- Blok kode: `keep_together` + shading `F2F2F2`.
- Blok judul/penulis dipadatkan (afiliasi 11pt).
- Footer: nomor halaman tengah via field `PAGE`.
- Hapus spasi ganda sisa (kecuali blok kode).

### 5.7 Layout dua kolom jurnal (resep JTIIK SINTA 2, teruji Okt 2026)

Template 2 kolom (judul/abstrak 1 kolom, badan 2 kolom @7,5 cm gap 1 cm,
margin 3-3-2-2, TNR 10pt) via `WD_SECTION.CONTINUOUS` + XML `w:cols`:

```python
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

doc.add_section(WD_SECTION.CONTINUOUS)  # front-matter selesai -> badan
sectPr = doc.sections[-1]._sectPr
old = sectPr.find(qn("w:cols"))
if old is not None:
    sectPr.remove(old)
cols = OxmlElement("w:cols")
cols.set(qn("w:num"), "2")
cols.set(qn("w:space"), "567")  # 1 cm; kolom 7,5 cm = 4252 twips
for _ in range(2):
    col = OxmlElement("w:col")
    col.set(qn("w:w"), "4252")
    col.set(qn("w:space"), "567")
    cols.append(col)
sectPr.append(cols)
```

- Gambar/tabel **full-width**: yang tidak perlu terjepit selebar kolom
  dibungkus seksi 1 kolom (`set_layout(1)` → sisip → `set_layout(2)`).
  Pola seksi akhir harus selang-seling `1-2-1-2…` dan berakhir di `2`
  (verifikasi via `doc.sections` + `w:num`).
- Gambar di kolom: lebar maks = lebar kolom (2,9 inci); full-width: 5,8 inci.
  Flowchart tinggi selalu kunci tinggi (maks 9 inci) agar tidak luber halaman.
- Judul tabel **satu sumber saja**: judul `**Tabel N.**` dari Markdown
  dirender menyatu dengan tabelnya di seksi 1 kolom — jangan tambah
  auto-insert judul (duplikat). Deteksi judul memakai regex `^Tabel \d+\.`
  (kalimat badan seperti "Tabel 3 meringkas…" tidak berkoma-titik = bukan judul).

### 5.8 Konversi sitasi ke Harvard-Anglia caps (gaya JTIIK)

- Pustaka: `NAMA, I., NAMA2, J. & NAMA3, K., Tahun. Judul. *Jurnal*, Vol(No), pp.X–Y.`
  Online: `LEMBAGA, Tahun. *Judul*. [online] Tersedia di: <URL>`.
- In-text 3 penulis ditulis lengkap saat mengacu (`(A, B & C, 2024)`,
  bukan `dkk.`); hanging-indent regex ikut berubah ke `^.+,\s*\d{4}\.`.
- URL di dalam run teks harus di-split dulu (`re.split(r"(https?://\S+)")`)
  sebelum diberi warna/garis bawah — URL yang menempel di run tidak kena
  `startswith("http")`.

### 5.9 Otomatisasi rantai build + standar Word (teruji Okt 2026)

Rantai sekali jalan (`build_all.sh`, `set -e`): Markdown → DOCX → format
template → `proofread_id.py` (gerbang, exit ≠ 0 = stop) → `reload_word.py`
background. Jangan reload manual antar langkah.

Standar Word yang diotomatiskan saat build (bukan manual di Word):

- `w:lang` (`id-ID`) di tiap run untuk bahasa proofing.
- Core properties: `keywords` diisi dari baris Kata kunci/Keywords,
  `subject`/`category`/`comments` diisi.
- `w:updateFields=true` di `settings.xml` agar field refresh saat dibuka.
- Normalisasi white space di parser (`re.sub(r"\s+", " ", t)`), bukan di Word.
- Penomoran heading manual ("1.", "2.1") SENGAJA dipertahankan sebagai teks
  (bukan `numbering.xml`): template jurnal menuntut angka statis, dan
  auto-numbering berisiko ganda saat naskah ditempel ke template OJS.

Jebakan blok judul (wajib dihindari):

- Baris MD berurutan TANPA baris kosong digabung parser menjadi satu
  paragraf — penulis/afiliasi/email/korespondensi/catatan WAJIB dipisah
  baris kosong, dan guard build (`seen_heading`: mode header berakhir di
  heading pertama) mencegah abstrak tertelan logika header.
- Format pass WAJIB deteksi isi (bukan indeks `paras[N]`): baris kosong
  spacer menggeser indeks. Baris kosong spesifikasi template (sesudah judul,
  penulis, email, catatan, heading abstrak, 1× sesudah abstrak, 2× sesudah
  kata kunci) dibuat via spacer 10pt eksplisit.

Ketahanan reload (pelajaran insiden hang Okt 2026):

- Gejala: `osascript` System Events menggantung → penyebab: revoke/flakiness
  assistive access (TCC), dialog modal di Word, atau dokumen sudah tertutup.
- Diagnosis: perintah Word murni (`count documents`, close, open) satu per
  satu; bila System Events yang macet, Word-nya sendiri sehat.
- `reload_word.py` dipecah dua fase (SWAP wajib + RESTORE best-effort) plus
  fallback `open` langsung tanpa assistive access bila SWAP gagal.

---

## 6. Pindah session (handoff checklist)

Sebelum menutup sesi kerja dokumen, catat 5 hal ini agar session berikutnya
nyambung tanpa menebak:

1. **Repo & git**: branch + commit terakhir tiap repo yang tersentuh
   (`git log --oneline -2`, `git status -sb` harus bersih/setara remote).
2. **File target**: path dokumen Word + sumber markdown bila ada + statusnya
   (kata, tabel, gambar, penanda terbuka seperti `[PERLU REFERENSI: ...]`).
3. **Fakta terverifikasi**: angka/tanggal/nama yang sudah dicek ke sumber
   (tulis sumbernya, mis. "UAT 4,46 = hitung ulang 803/180 dari Tabel 12 docx").
4. **Skrip sekali-pakai di `/tmp`**: `/tmp` HILANG saat reboot — resepnya sudah
   ada di §5; bila skrip masih dibutuhkan, pindahkan ke `tools/` + commit.
5. **Perintah resume**: `smart_write.py info auto` (cek dokumen aktif) +
   `git log` di tiap repo. Aturan sinkron §0 dan pelajaran §4–§5 tetap berlaku.
