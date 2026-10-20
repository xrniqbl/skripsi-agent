# Checklist EYD (Layer 2)

Pelacak untuk **Layer 2** dari `references/quality-gates.md`. Rujukan:
`references/eyd-check.md` (EYD V, Permendikbudristek 18/2022, dan KBBI).

Lapisan ini **mekanis dan dapat diautomasi**. Lulus Layer 2 bukan berarti bahasa
sudah enak dibaca; itu tugas Layer 1 dan Layer 3.

## A. Pemeriksaan otomatis

```bash
python3 scripts/id_language_check.py outputs/proposal.md --struktur \
    --md outputs/idl-check.md
```

- [ ] Semua temuan kategori `baku` diperbaiki atau diputuskan
- [ ] Semua temuan kategori `partikel` diperbaiki
- [ ] Semua temuan kategori `rumus_kabur` diperbaiki
- [ ] Semua temuan kategori `desimal` diperbaiki (koma, bukan titik)
- [ ] Semua temuan kategori `spasi` diperbaiki
- [ ] Semua temuan kategori `non_latin` diperbaiki (harus 0)
- [ ] Semua temuan kategori `serapan` sudah diputuskan, bukan diabaikan diam-diam

## B. Ejaan dan bentuk baku

- [ ] Kata non-baku diganti: `analisa` → `analisis`, `sistim` → `sistem`
- [ ] Imbuhan `ke-` konsisten: `mengerjakan`, `mengevaluasi`, `menghitung`
- [ ] Kata ulang memakai tanda hubung: `anak-anak`, `mata-mata`
- [ ] Kata depan kasar tapi baku: `di`, `ke`, `dari`, `daripada` dipakai tepat
- [ ] `dari ... ke ...` untuk arah lengkap, bukan `dari ... ke` hilang
- [ ] Verifikasi silang ke KBBI untuk kata yang meragukan (bukan dari ingatan)

## C. Tanda baca

- [ ] Tidak ada tanda pisah sebagai penghubung kalimat (`—`, `–`)
- [ ] Titik koma hanya untuk bagian setara yang sudah berkoma
- [ ] Titik dua dipakai sebelum penjelasan dan perincian
- [ ] Kutipan ≥40 kata memakai blok, bukan kutip di dalam kutip
- [ ] Tanda hubung hanya untuk kata ulang, partikel, dan bilangan
- [ ] Tidak ada spasi sebelum tanda baca; tidak ada spasi ganda

## D. Kapitalisasi

- [ ] Awal kalimat, paragraf, nama diri, dan lembaga memakai kapital
- [ ] Tidak ada kapital setelah titik pada singkatan: `dkk. Adanya`, `hal. 12`
- [ ] Hari dan bulan kapital: `Senin`, `Januari`
- [ ] `internet`, `website`, `survei` huruf kecil
- [ ] Nama lembaga konsisten: `Departemen Pendidikan`, bukan `departemen pendidikan`

## E. Konjungsi dan partikel

- [ ] Konjungsi pertentangan tidak ditumpuk: "tapi" dan "namun" dalam satu kalimat
- [ ] `karena` atau `sebab`, bukan `dikarnakan`
- [ ] Kata tanya baku: `mengapa`, `bagaimana`, `di mana`, `ke mana`
- [ ] Tidak ada bentuk 'terhadap' berlebihan di seluruh naskah
- [ ] Jumlah konjungsi per kalimat ≤3

## F. Konsistensi istilah (juga bagian Layer 3)

- [ ] Satu konsep memakai satu istilah di seluruh naskah
- [ ] Tidak ada pasangan yang bertabrakan: kinerja/produktivitas, motivasi/insentif
- [ ] Istilah asing: *italic* pada penyebutan pertama, tebal atau `code` setelahnya
- [ ] Lebih dari lima istilah/singkatan punya daftar di bagian awal
- [ ] Semua singkatan ditulis ulang pada penyebutan pertama

## G. Alarm LanguageTool (opsional)

Bila LanguageTool `id-ID` tersedia:

- [ ] Laporan lengkap dibaca
- [ ] Setiap saran diverifikasi manual sebelum diterima
- [ ] Saran yang salah (kata baku ditolak, istilah metode diubah) **ditolak**
- [ ] Saran EYD yang bertentangan dengan pedoman kampus mengikuti **pedoman kampus**

---

Lanjut ke Layer 3 (gate semantik): `references/quality-gates.md`.
