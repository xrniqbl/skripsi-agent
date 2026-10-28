# Bukti Terukur

## Prinsip

Bukti adalah sesuatu yang bisa **diperiksa orang lain tanpa bertanya kepada lo**. Kalau
pembimbing harus bertanya "berapa?", itu bukan bukti — itu klaim.

| Revisi | Bukti tidak sah | Bukti sah |
|---|---|---|
| Persingkat latar belakang | "sudah dipersingkat" | "9 → 4 paragraf (hal 1–4)" |
| Perbaiki rumusan | "sudah diperbaiki" | "5 → 4 butir; butir 2 dan 3 digabung (hal 5)" |
| Tambah jurnal | "sudah ditambah" | "10 jurnal dari 32 pustaka (31%), sebelumnya 4 (23%)" |
| Seragamkan angka | "sudah dicek" | "grep '61,5' = 0, grep '62%' = 7 (sebelumnya 6)" |
| Hapus garis tabel | "sudah dirapikan" | "Tabel 2.1: 0 garis vertikal, sebelumnya 6" |
| Perbaiki simpulan | "sudah diubah" | "simpulan 4 butir, sejajar rumusan 1–4 (hal 60)" |
| Tambah pembahasan | "sudah ditambah" | "3 subbab pembahasan, hal 52–58, sebelumnya 2 paragraf" |
| Perbaiki sitasi | "sudah dilengkapi" | "[L-3] ditambah di hal 12; 12 rujukan memakai penanda" |

## Bukti per jenis revisi

### Revisi struktur (rumusan, tujuan, simpulan)

Bukti harus menyebut **jumlah sebelum dan sesudah**.

```
sebelum: rumusan 5 butir (hal 4)
sesudah: rumusan 4 butir — butir 2 & 3 digabung (hal 4)
cek    : 4 butir rumusan = 4 butir tujuan = 4 butir simpulan
```

### Revisi isi (pembahasan, latar belakang)

Bukti harus menyebut **ukuran**, bukan penilaian.

```
✅  latar belakang 9 → 4 paragraf; 1.840 → 780 kata
✅  pembahasan 2 → 4 subbab; hal 52–58 (sebelumnya 52–53)
❌  "lebih dalam" · "lebih fokus" · "sudah bagus"
```

Ukuran kata bisa dihitung:

```bash
# hitung kata bagian tertentu
python3 - <<'EOF'
import re
t = open('skripsi.md').read()
m = re.search(r'1\.1 Latar Belakang(.*?)1\.2', t, re.S)
print('kata:', len(m.group(1).split()) if m else 'tidak ketemu')
EOF
```

### Revisi angka / konsistensi

Bukti harus berupa **hasil grep** — angka lama nol, angka baru konsisten.

```bash
grep -c "61,5" skripsi.md      # harus 0
grep -c "62%" skripsi.md       # harus sama dengan jumlah kemunculan yang benar
grep -n "R²" skripsi.md        # semua harus 0,34
```

```
✅  '61,5' = 0 kemunculan; '62%' = 7 (hal 18, 52, 53, 60, 61)
```

### Revisi sitasi / daftar pustaka

Bukti harus berupa **hitungan**.

```
✅  32 pustaka: 10 jurnal (31%), 18 buku (56%), 4 laporan (13%)
✅  tahun termuda 2025; 12 dari 32 (38%) terbit ≤ 5 tahun
✅  0 penanda [L-n] menggantung (semua ada di Daftar Pustaka)
```

Verifikasi penanda menggantung:

```bash
python3 ../proposal_skripsi/scripts/proposal_doctor.py skripsi.md
```

### Revisi format

Bukti berupa **hitungan objek**, bukan pernyataan.

```
✅  Tabel 2.1: 0 garis vertikal (sebelumnya 6)
✅  12 tabel memakai caption di atas; 0 di bawah
✅  spasi ganda: 0 paragraf (sebelumnya 23)
```

### Revisi plagiarisme / parafrase

Bukti wajib menyebut **hasil pemeriksaan**, bukan janji.

```
✅  paragraf hal 24 diparafrase ulang; similarity 24% (sebelumnya 71%)
✅  3 paragraf di Bab II ditulis ulang dengan sitasi [L-5]
❌  "sudah diparafrase" — tanpa angka, tidak bisa diverifikasi
```

Kalau tidak punya akses Turnitin, sebut alatnya:

```
✅  dicek dengan plagiarisme checker gratis; 3 paragraf mirip, sudah ditulis ulang
```

## Bukti yang harus disimpan

Selain menulis di kolom Bukti, simpan **artefak**-nya:

```
revisi/
  R-01_latar_belakang_sebelum.md
  R-01_latar_belakang_sesudah.md
  R-07_grep_angka.txt
  R-08_similarity_sebelum.png
  R-08_similarity_sesudah.png
```

Berguna saat pembimbing bertanya "coba tunjukkan yang sebelum". Dan berguna saat sidang:
penguji yang meragukan perbaikan bisa langsung dilihatkan.

## Tanda bukti lo lemah

- Bisa ditulis dalam satu kata ("sudah", "ok", "beres").
- Tidak menyebut angka, halaman, atau kutipan.
- Tidak bisa diperiksa orang lain tanpa bertanya ke lo.
- Berisi penilaian ("lebih baik", "cukup", "rapi") bukan ukuran.

Kalau menemukan salah satu tanda ini, revisinya kemungkinan **belum benar-benar selesai** —
hanya sudah dikerjakan setengah.
