---
name: zotero_pustaka
description: Menyambungkan Zotero (Web API, Local API, ekspor) dan DOI ke naskah skripsi — metadata jadi CSL-JSON, dedup, render Daftar Pustaka APA/IEEE/Vancouver, sisip ke DOCX. Gunakan saat pengguna menyebut Zotero, Mendeley, metadata referensi, sitasi otomatis, daftar pustaka dari DOI, BibTeX/RIS, atau minta pustaka disisipkan ke Word.
version: 1.0.0
---

# Zotero Pustaka — Referensi dari Zotero/DOI ke Naskah

Sub-skill ini menjawab satu pertanyaan: **bagaimana pustaka yang sudah
dikumpulkan (di Zotero, di berkas BibTeX, atau cuma berupa daftar DOI) berubah
jadi Daftar Pustaka yang patuh pedoman kampus, tanpa satu pun metadata
dikarang dan tanpa nomor sitasi yang berbeda antara teks dan daftar.**

Semua format masuk dinormalkan ke **CSL-JSON** di batas pipeline. Satu bentuk
kanonik ke dalam, satu mesin render ke luar.

## Kapan Dipakai

- Pengguna bertanya "apakah skripsi agent bisa tersambung ke Zotero".
- Ada `zotero.sqlite` / ekspor Zotero JSON / `library.bib` / `.ris` yang harus
  jadi Daftar Pustaka.
- Pengguna memberi daftar DOI dan minta entri pustaka jadi.
- Naskah DOCX punya `{{DAFTAR_PUSTAKA}}` atau `{{cite:ID}}` yang harus diisi.
- Daftar Pustaka hasil tulisan tangan perlu diverifikasi (DOI resolve, urutan,
  et al., usia terbitan) — gerbangnya tetap
  `../format_kampus/scripts/periksa_pustaka.py`, bukan skrip baru.

## Empat Jalur Metadata

| Situasi | Perintah | Catatan |
|---|---|---|
| Zotero desktop jalan di mesin ini | `zotero_client.py user 0 --local` | tanpa auth, port 23119 |
| Punya API key | `zotero_client.py user <id> --key $ZOTERO_KEY` | privat butuh key |
| Grup publik | `zotero_client.py group <id>` | tanpa key |
| Cuma DOI | `zotero_client.py doi 10.xxxx/yyyy` | content negotiation, tanpa akun |
| Cuma judul | `zotero_client.py cari "judul artikel"` | Crossref, kembalikan kandidat DOI |

`python3 scripts/zotero_client.py probe` memeriksa apakah Zotero desktop hidup.
Port mati bukan bug yang bisa diperbaiki dari kode — pindah jalur.

**403 pada `/users/<id>/items` bukan berarti id salah.** Itu jawaban normal
untuk pustaka privat tanpa key. 404 baru berarti grup tidak ada.

## Alur Kerja

```bash
# 0. (sekali) unduh berkas gaya + locale Indonesia
bash scripts/unduh_gaya.sh

# 1. ambil metadata -> CSL-JSON
python3 scripts/zotero_client.py doi --dari-daftar dois.txt --cek \
    --out pustaka.csl.json

# 1b. atau dari ekspor Zotero/BibTeX/RIS (boleh digabung, dedup otomatis)
python3 scripts/konversi_pustaka.py ~/zotero-export.json library.bib \
    --gabung --out pustaka.csl.json

# 2. lihat hasil sebelum menyentuh naskah
python3 scripts/render_sitasi.py pustaka.csl.json --gaya apa

# 3. sisip ke DOCX (mengganti {{DAFTAR_PUSTAKA}} dan {{cite:ID}})
python3 scripts/sisip_docx.py naskah.docx pustaka.csl.json --gaya apa \
    --nama-lengkap --ganti-sitasi --out naskah-final.docx

# 4. gerbang kampus — wajib, jangan lewati
python3 ../format_kampus/scripts/periksa_pustaka.py naskah-final.docx \
    --tahun-acuan 2026
python3 ../proposal_skripsi/scripts/verify_doi.py pustaka.csl.json
```

Gaya tersedia: `apa`, `ieee`, `vancouver`, `chicago-author-date`, `harvard`
(=`harvard-cite-them-right`), `nature`. Gaya kampus sendiri:
`--csl /path/gaya-kampus.csl`.

## Aturan yang Dijaga Skrip Ini

1. **Metadata tidak pernah dikarang.** Field yang tidak ada di sumber tetap
   kosong dan dilaporkan. `--cek` menolak DOI yang tidak resolve di Crossref
   maupun doi.org.
2. **Nomor sitasi = nomor entri.** Sitasi dirender *sesudah* `sort()`, karena
   gaya numerik menomori menurut urutan akhir daftar. Merender sitasi lebih
   dulu memberi `[1]` pada entri yang tercetak sebagai `[3]`.
3. **`et al.`/`dkk` dimatikan dengan `--nama-lengkap`** untuk pedoman yang
   melarangnya (ARS/FTI 4.10 butir 5). Ini mengubah atribut CSL
   `et-al-min`/`et-al-use-first` di salinan sementara, bukan menambal teks
   hasil render.
4. **Dedup dilaporkan, bukan dibuang diam-diam.** Kunci pertama DOI, lalu
   judul ternormalisasi + tahun.
5. **Escape LaTeX di-unescape.** `R\&D` di BibTeX harus tercetak `R&D`.
6. **Locale `id-ID`** dipakai default supaya istilah CSL jadi "dan", "ed.",
   "Dalam" — bukan "and", "eds.", "In".

## Jebakan yang Sudah Memakan Waktu

- **`bibliography()` kosong tanpa galat** bila item belum di-`register()`.
  Dan `bib.cite()` melempar `VariableError('bibliography')` bila objek
  `Citation` yang dipakai bukan objek yang sudah di-register — bukan sitasi
  kosong, tapi exception.
- **`bib.sort()` wajib dipanggil** sebelum membaca bibliografi. Tanpa itu APA
  keluar sesuai urutan berkas dan tidak berabjad — cacat yang lolos
  pemeriksaan mata karena tiap entri tampak benar.
- **Gaya dependent tidak ada di path raw GitHub.** `vancouver.csl` di
  `raw.githubusercontent.com/.../master/vancouver.csl` mengembalikan badan
  `404: Not Found` 14 byte. Unduh dari `https://www.zotero.org/styles/<nama>`
  dan verifikasi isinya XML sebelum dipakai.
- **`et-al-min` duduk di dalam `<macro>`**, bukan di dalam `<citation>` /
  `<bibliography>`. Menjelajahi dua node itu saja tidak mengubah apa pun.
- **`bibtexparser` 2.x tidak punya `bparser`/`loads()`.** Pakai
  `parse_string()` → `Library.entries`, baca `entry.fields_dict[k].value`.
- **`addnext()` berulang pada anchor yang sama membalik urutan.** Geser anchor
  ke paragraf yang baru disisipkan setiap iterasi.
- **`CitationStylesStyle(style, locale=...)`** — parameter kedua bernama
  `locale`, bukan `lang`; `id-ID` sudah dibundel citeproc-py.
- **Pemeriksa kampus menghitung entri jurnal ber-DOI sebagai "sumber web"**
  karena URL-nya cocok pola web, lalu menyalakan galat "web tanpa tanggal
  unduh" pada naskah yang benar. Sudah diperbaiki di `periksa_pustaka.py`:
  entri jurnal dikeluarkan dari daftar web.
- **`periksa_pustaka.py` membaca DOCX dengan `"\n".join()`** sehingga batas
  paragraf hilang dan Daftar Pustaka terbaca **0 entri** pada entri
  banyak-pengarang. Paragraf Word adalah batas entri; harus `"\n\n"`.
- **Template kampus punya heading "Daftar Pustaka" tanpa placeholder.**
  Menambahkan entri di akhir dokumen menaruhnya setelah "Daftar Riwayat
  Hidup" — bagian yang salah, dan `periksa_sistematika.py` menolaknya.
  `sisip_docx.py` mencari heading itu dan menyisipkan tepat sesudahnya.
- **`form="short"` duduk di `<name>`, bukan `<names>`.** Di `<names>` ia
  diabaikan dan keluar `(I. Saputra, A. Wijaya)` alih-alih
  `(Saputra & Wijaya)`.
- **locator berupa string melempar `AttributeError`** — harus
  `citeproc.source.Locator(label, identifier)`. Halaman juga tidak ada di
  metadata pustaka; satu-satunya sumbernya penanda `{{cite:ID:HAL}}` di
  naskah, dibaca `cari_locator()`.
- **`addnext()` berulang pada anchor yang sama membalik urutan** — geser
  anchor ke paragraf yang baru disisipkan setiap iterasi.
- **Jangan menebak "sudah bernomor" dari isi entri.** Judul `1984. (2000)`
  memicu tebakan itu dan menghapus nomornya. Keputusan memberi nomor harus
  bergantung pada gaya (`GAYA_NUMERIK`), bukan pada regex atas teks.
- **Pustaka Zotero nyata punya duplikat** — 163 → 154 entri pada pustaka uji
  240 item. Dedup DOI-dulu lalu judul+tahun, dan laporkan; jangan biarkan
  lolos ke gaya numerik.

## Berkas

```
scripts/zotero_client.py     empat jalur metadata -> CSL-JSON
scripts/konversi_pustaka.py  BibTeX/RIS/Zotero JSON/TSV -> CSL-JSON + dedup
scripts/render_sitasi.py     CSL-JSON -> Daftar Pustaka + sitasi (citeproc)
scripts/sisip_docx.py        sisip ke DOCX, ganti {{cite:ID}}
scripts/unduh_gaya.sh        unduh + verifikasi berkas CSL & locale
styles/                      apa, ieee, vancouver, chicago, harvard, nature
tests/run_tests.sh           uji offline (tanpa jaringan)
references/api-dan-gaya.md   endpoint, kode respons, peta field
```

## Verifikasi

```bash
PYTHON=/root/skripsi-agent/.venv/bin/python bash tests/run_tests.sh
```

37 pemeriksaan offline: konversi tiga format, dedup DOI, urutan abjad APA,
penanda IEEE, penghapusan et al., kecocokan nomor sitasi↔entri, pola sitasi
kampus `(Nama, Tahun:Halaman)` dan naratif, penyisipan DOCX (placeholder,
heading template, hanging indent), dan penolakan id sitasi yang tidak ada.
Hasil terakhir: semua lulus, 0 dilewati.
