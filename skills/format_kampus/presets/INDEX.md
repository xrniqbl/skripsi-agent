# Registry Preset Kampus

Preset adalah profil format kampus yang sudah jadi (lihat `../SKILL.md`). Sebelum
mengekstrak panduan dari nol, periksa daftar ini: bila kampus pengguna ada, pakai
presetnya sebagai draf awal — tetap konfirmasikan ringkasannya ke pengguna, karena
panduan bisa berubah antar edisi.

| Berkas | Kampus | Sumber panduan | Status |
|---|---|---|---|
| `universitas-contoh.yaml` | Universitas Contoh | — (fiktif, hanya contoh bentuk isian) | FIKSI |

## Menambah preset kampus nyata

1. Ekstrak profil dari buku panduan resmi kampus mengikuti `../SKILL.md` dan
   `../references/ekstraksi-checklist.md`.
2. Simpan sebagai `presets/<slug-kampus>.yaml` (huruf kecil, tanda hubung).
3. Wajib isi `kampus.sumber_panduan` dengan nama dokumen panduan dan edisi/tahunnya,
   agar pembaca bisa menilai kesegarannya.
4. Tambahkan satu baris ke tabel di atas (status: nama kampus persis seperti di
   panduan) dan naikkan versi bundel (lihat CHANGELOG di root repo).
5. Preset hanya berisi KETENTUAN FORMAT dari dokumen publik kampus — jangan pernah
   memasukkan data pribadi, naskah skripsi, atau dokumen milik individu ke folder ini.
