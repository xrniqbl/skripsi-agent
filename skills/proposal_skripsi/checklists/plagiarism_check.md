# Checklist Plagiarisme (Layer 2 + Layer 3)

Pelacak untuk pemeriksaan plagiarisme dalam alur QC. Rujukan:
`references/plagiarism-check.md`.

Pemeriksaan ini punya dua sifat yang harus diingat:

1. **Temuan adalah sinyal, bukan bukti.** Kata yang sama muncul karena istilah
   baku, bukan karena plagiarisme.
2. **Skor nol bukan berarti bersih.** Parafrase dan cuplikan yang disisipkan
   tidak terdeteksi pola kata berurutan. Skrip ini tidak menggantikan Turnitin.

## A. Pemeriksaan otomatis

```bash
# duplikasi dalam naskah sendiri
python3 scripts/plagiarism_check.py outputs/proposal.md --internal

# perbandingan dengan folder sumber
python3 scripts/plagiarism_check.py outputs/proposal.md --sumber .cache_ekstrak/ \
    --md outputs/plagiarism_report.md --json outputs/plagiarism_report.json
```

- [ ] Kedua perintah dijalankan
- [ ] Laporan MD dan JSON dibuat
- [ ] Setiap temuan dibaca satu per satu, bukan hanya jumlah
- [ ] Temuan yang merupakan false positive ditandai dan dicatat alasannya

## B. Verifikasi manual setiap temuan

Untuk tiap temuan, putuskan salah satu:

- [ ] **Kutipan sah** — ada penanda `[L-n]` dan rujukan di daftar
- [ ] Parafrase sah — kalimat ditulis ulang, analisis dan rujukan tetap ada
- [ ] Perlu diperbaiki — kutipan tidak diberi tanda
- [ ] Plagiarisme — disalin utuh tanpa tanda dan tanpa rujukan

Temuan yang diputuskan "false positive" tetap dicatat di
`outputs/plagiarism_report.md` pada bagian catatan.

## C. Lima tipe yang wajib diperiksa manual (bagian 6)

| Tipe | Pemeriksaan | Status |
|------|-------------|--------|
| 1. Copy-paste utuh | Ada kalimat ≥7 kata identik tanpa tanda? | |
| 2. Mosaik | Paragraf dirakit dari beberapa sumber, tanda hilang di antaranya? | |
| 3. Parafrase dangkal | Hanya ganti kata, analisis dan interpretasi tidak berubah? | |
| 4. Mengutip diri sendiri | Teks proposal sebelumnya dipakai lagi tanpa kutipan? | |
| 5. "Laundering" | Kutipan diberi tanda, tapi sumber yang disebut bukan yang mengutip? | |

## D. Pemeriksaan khusus proposal

- [ ] **Definisi dan Landasan Teori** — tiap definisi diberi rujukan
- [ ] **BAB II** — tidak ada paragraf tanpa sitasi
- [ ] **BAB III** — nama instrumen, validator, dan rumus kutip dengan rujukan
- [ ] **BAB I Latar Belakang** — setiap klaim empiris punya `[L-n]` atau `[D:kolom]`
- [ ] **Hasil Analisis** — angka berasal dari data, bukan dari artikel
- [ ] **Kutipan langsung** — blok kutip >40 kata, menggunakan tanda hubung saat dipotong
- [ ] **Kutipan tidak langsung** — bukan bentuk "menurut [L-1], X adalah Y" secara harfiah

## E. Tumpang tindih internal

- [ ] Tidak ada kalimat identik di BAB I dan BAB III
- [ ] Rumusan masalah tidak disalin langsung dari judul artikel
- [ ] Tabel hasil tidak menyalin tabel dari artikel tanpa `[D:kolom]`
- [ ] Abstract dan abstrak Indonesia bukan terjemahan harfiah satu-satu

## F. Ambang similarity (bila Turningitin tersedia)

| Skor | Tindakan |
|------|----------|
| <15% | Tidak ada tindakan |
| 15-30% | Baca laporan, periksa tiap sumber |
| 30-50% | Wajib parafrase atau kutip ulang bagian yang ditandai |
| >50% | Perbaiki extensif, hubungi pembimbing bila perlu |

Sumber, definisi wajib, dan kutipan sah biasanya menyumbang sebagian besar
persentase. **Jangan panik pada angka tunggal.**

## G. Tindakan sebelum submit

- [ ] Semua temuan "perlu diperbaiki" sudah diperbaiki
- [ ] Daftar rujukan memuat semua sumber yang dikutip di naskah
- [ ] Tidak ada sumber di daftar rujukan yang tidak dikutip di naskah
- [ ] Laporan final tersimpan sebagai bukti proses

---

Lanjut ke Layer 4 (red-team / baca sebagai pembimbing):
`references/quality-gates.md`.
