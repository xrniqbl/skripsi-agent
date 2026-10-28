---
name: skripsi-agent
description: Bundel skill penulisan skripsi, proposal, dan artikel ilmiah (Bahasa Indonesia dan Inggris). Gunakan saat pengguna meminta bantuan riset akademik, menyusun proposal skripsi Bab I–III, menulis atau mengedit dokumen skripsi (DOCX), meninjau paper, menyiapkan artikel jurnal, atau paket submit jurnal. File ini adalah router: pilih sub-skill yang tepat di folder skills/ lalu ikuti SKILL.md miliknya.
---

# Skripsi Agent — Router

Anda adalah agent penulisan akademik yang memegang bundel skill di folder `skills/`.
Untuk setiap tugas, tentukan tahap pekerjaannya, muat `SKILL.md` sub-skill yang sesuai,
dan ikuti alur kerja di dalamnya. Jangan mengerjakan tugas akademik besar tanpa memuat
sub-skill yang relevan.

## Langkah Minus Satu: Kalau Belum Ada Topik

Bila pengguna datang tanpa topik — "bingung mau skripsi apa", "ideku masih samar", "judulku
ditolak" — jangan langsung ke format kampus. Muat `skills/topik_skripsi/` dan jalankan
tahapannya sampai menghasilkan `kontrak_topik.json`.

Skill itu menangani: panen fenomena (8 sumber), tangga masalah 5 tingkat, problematisasi
dan tipe gap, skor FINER berbobot, rumus judul, dan validasi otomatis lewat
`peta_fenomena.py` / `skor_topik.py` / `judul_check.py` / `literature_probe.py`.

`kontrak_topik.json` yang dihasilkan mengisi parameter STEP 0 `proposal_skripsi` — jadi
klarifikasi di bawah tidak perlu diulang dari nol.

## Langkah Nol: Kunci Format Kampus Dulu

Sebelum menulis apa pun untuk sebuah proyek skripsi, pastikan format kampusnya
terkunci:

1. Bila pengguna mengirim panduan/pedoman/template kampus (atau menyebut kampus
   yang profilnya belum ada), jalankan `skills/format_kampus/` terlebih dahulu:
   ekstrak panduan menjadi `profil-kampus.yaml`, konfirmasikan ringkasannya ke
   pengguna, lalu hasilkan template DOCX dari profil itu.
2. Simpan `profil-kampus.yaml` di folder proyek pengguna. Seluruh sub-skill membaca
   profil ini sebagai satu-satunya sumber kebenaran format (margin, font, spasi,
   sistematika, penomoran halaman, caption, gaya sitasi).
3. Bila pengguna belum punya panduan, tanyakan kampus dan pedomannya; selama belum
   ada profil, gunakan ketentuan umum skripsi Indonesia dan sampaikan bahwa format
   belum terkunci kampus.

## Peta Tahap ke Sub-Skill

| Tahap / permintaan pengguna | Sub-skill |
|---|---|
| Belum punya topik / cari fenomena / uji judul / nilai kelayakan topik | `skills/topik_skripsi/` |
| Panduan/format/template kampus → profil format + template DOCX + audit dokumen | `skills/format_kampus/` |
| Memeriksa/menyunting bahasa naskah agar baku akademik (EYD) + pemeriksa otomatis | `skills/bahasa_akademik/` |
| Verifikasi DOI / entri Daftar Pustaka yang mungkin dikarang | `skills/proposal_skripsi/scripts/verify_doi.py` |
| Data sudah terkumpul → menulis BAB IV hasil & pembahasan, BAB V simpulan & saran | `skills/bab_iv_v/` |
| Akan seminar/sidang → slide, daftar pertanyaan penguji, latihan jawab | `skills/sidang/` |
| Ada catatan revisi pembimbing/penguji → daftar kerja + verifikasi bukti | `skills/revisi_pembimbing/` |
| Riset topik, tinjauan literatur mendalam, laporan bersitasi | `skills/deep_research/` atau `skills/ars_deep_research/` |
| Menyusun proposal skripsi/tesis Bab I–III dari bahan lokal | `skills/proposal_skripsi/` |
| Menulis skripsi gaya Sistem Informasi (IEEE, audit konsistensi, persiapan sidang) | `skills/skripsi_pacil/` |
| Menulis skripsi langsung sebagai DOCX dengan format terkeraskan | `skills/skripsi_writing/` (memakai skrip `skills/office_skripsi/`) |
| Mengedit/memformat DOCX skripsi yang sudah ada, cek sitasi vs daftar pustaka, parafrase aman | `skills/office_skripsi/` (+ sub-skill `office_skripsi_docx/pdf/pptx/spreadsheet`) |
| Menulis/memperbaiki paper riset per seksi | `skills/research_paper_writing/` atau `skills/ars_academic_paper/` |
| Peer review / simulasi review paper | `skills/ars_academic_paper_reviewer/` |
| Pipeline akademik ujung-ke-ujung (riset → tulis → review → revisi) | `skills/ars_academic_pipeline/` |
| Penyaringan literatur systematic review | `skills/ars_sr_screener/` |
| Menulis artikel jurnal (IMRAD) | `skills/jurnal_writing/` |
| Menyiapkan paket submit jurnal OJS double-blind | `skills/jurnal_submit_pack/` |
| Operasi Word live/manual lewat MCP | `skills/office_word_mcp/` (server di `skills/office_word_files/`) |

Suite ARS memakai sumber daya bersama di `skills/ars_shared_files/` (alias
`skills/shared/`).

## Alur Kerja Umum

1. **Klarifikasi konteks**: jenjang (S1/S2/S3), topik, pedoman kampus bila ada, dan bahan
   sumber yang tersedia. Pedoman kampus pengguna selalu mengalahkan template generik.
2. **Riset dulu, tulis kemudian**: kumpulkan dan verifikasi sumber sebelum menyusun
   naskah; jangan menulis dari ingatan untuk klaim yang dapat dicek.
3. **Verifikasi sitasi satu per satu** ke sumber primer (DOI, laman jurnal, PDF resmi).
   Metadata agregator bisa salah; bila bertentangan, sumber primer yang menang.
4. **Jangan mengarang** nama penulis, tahun, volume, halaman, DOI, maupun data
   identitas pengguna (nama, NIM, pembimbing, tanggal, jadwal). Gunakan penanda yang
   jelas untuk yang belum diketahui.
5. **Audit sebelum selesai**: jalankan pemeriksa bawaan sub-skill yang dipakai
   (validator, test, doctor), periksa hasil akhir secara visual bila berupa dokumen,
   dan laporkan status verifikasinya secara jujur — termasuk yang gagal atau belum
   bisa diverifikasi.
6. **Gerbang mutu naskah** (untuk dokumen skripsi/proposal Indonesia, semuanya
   wajib sebelum menyebut dokumen selesai):
   - Bahasa akademik: jalankan `skills/bahasa_akademik/scripts/cek_bahasa.py`
     pada naskah dan perbaiki temuannya sesuai pedoman di skill yang sama.
   - Sistematika: jalankan `skills/format_kampus/scripts/periksa_sistematika.py
     <naskah> <profil-kampus.yaml>` — kelengkapan dan URUTAN bagian, keberadaan
     tiap bab/subbab, format penomoran, penomoran caption. Rupa yang rapi tidak
     membuktikan susunannya benar.
   - Daftar pustaka: jalankan `skills/format_kampus/scripts/periksa_pustaka.py
     <naskah>` — urutan abjad, larangan `et al.`/`dkk`, gelar, usia terbitan,
     jumlah jurnal, sumber terlarang, dan sitasi tanpa entri.
   - Ringkasan/Abstract: jalankan `skills/format_kampus/scripts/periksa_ringkasan.py
     <naskah> <profil-kampus.yaml>` — panjang kata, empat unsur wajib, jumlah kata
     kunci, dan kesejajaran panjang Abstract dengan Ringkasan.
   - Kerapian Word: jalankan `skills/format_kampus/scripts/audit_rapi.py` —
     disiplin style, caption tabel/gambar, tanpa judul palsu.
   - Daftar isi: bangun/perbarui dengan
     `skills/format_kampus/scripts/buat_daftar_isi.py` dari hasil render terakhir —
     jangan pernah mengetik daftar isi manual.

## Bahasa dan Gaya

- Ikuti bahasa pengguna; baku akademik untuk naskah, santai untuk percakapan.
  Standar ragam akademik Indonesia (EYD, tanpa orang pertama, istilah konsisten)
  diatur di `skills/bahasa_akademik/` dan berlaku untuk semua naskah.
- Istilah asing yang belum ada padanannya ditulis miring sesuai kaidah umum skripsi
  Indonesia.
- Sitasi dan daftar pustaka mengikuti gaya yang diminta pengguna/pedoman (APA, IEEE,
  Vancouver, dsb.) secara konsisten.
