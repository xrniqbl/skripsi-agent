# Korpus pembanding kemiripan

`indeks_korpus.json.gz` adalah indeks **hash** shingle (5 kata) dari 18 skripsi
berbahasa Indonesia yang diambil dari repositori institusi terbuka. Berkas ini
**tidak memuat teks naskah** — hanya sidik jari frasa, jumlah kata, dan
metadata sumber. PDF aslinya tidak pernah disimpan di repo.

Dipakai oleh `scripts/cek_kemiripan_korpus.py` dan oleh gerbang
`gate_naskah.sh` (melewati pemeriksaan bila indeks tidak ada).

## Metadata

Lihat `sumber.json` untuk 18 entri: judul, tahun, URL repositori. Semua berasal
dari `repository.uin-suska.ac.id` melalui OAI-PMH (set `type=thesis`).

## Kenapa hanya 18 dokumen

Bukan karena ambisi kecil, tetapi karena repositori institusi Indonesia sebagian
besar memblokir pengambilan otomatis: `repositori.uin-alauddin.ac.id` → 403,
`digilib.unila.ac.id` → tidak merespons, beberapa kampus lain memerlukan
captcha atau login. UIN Suska membuka OAI-PMH secara terbuka, sehingga bisa
diambil utuh dan dapat dipertanggungjawabkan lisensinya.

Angka kemiripan dari korpus ini adalah **indikator**, bukan skor Turnitin.
18 dokumen tidak sebanding dengan miliaran halaman yang dibandingkan Turnitin.
Yang ditangkap kelasnya: frasa yang dipinjam antar-skripsi, bukan dari jurnal.

## Bangun ulang indeks

```bash
# 1. kumpulkan teks korpus ke satu folder (satu .txt per dokumen)
# 2. bangun indeks
python3 scripts/cek_kemiripan_korpus.py --bangun-indeks folder_teks \
        --keluaran indeks_korpus.json --n 5
# 3. padatkan sebelum masuk repo
gzip -9 -f indeks_korpus.json
```

Untuk memakai indeks lain (mis. korpus kampus sendiri):

```bash
INDEKS_KORPUS=/path/indeks.json.gz bash scripts/gate_naskah.sh naskah.docx profil.yaml
```

## Menambah dokumen

Tambah `.txt` ke folder korpus, bangun ulang indeks, perbarui `sumber.json`.
Indeks lama tidak kompatibel bila `--n` berubah: `n` disimpan di dalam berkas
dan dipakai saat pemeriksaan, jadi indeks 5-kata tetap terbaca benar walau
pemanggil lupa menyebutkan `--n`.
