# Registry Preset Kampus

Preset adalah profil format kampus yang sudah jadi (lihat `../SKILL.md`). Sebelum
mengekstrak panduan dari nol, periksa daftar ini: bila kampus pengguna ada, pakai
presetnya sebagai draf awal — tetap konfirmasikan ringkasannya ke pengguna, karena
panduan bisa berubah antar edisi.

> **Peringatan (hasil audit 4 November 2026, lihat [AUDIT.md](AUDIT.md)).**
> "Siap pakai" hanya berarti skrip generator bisa berjalan — **bukan** bahwa angkanya
> ketentuan kampus tersebut.
>
> - **8 preset tidak terverifikasi**: berkasnya sendiri menyatakan angkanya berasal dari
>   "konvensi umum", bukan dari pedoman kampus (BINUS, Budi Luhur, Gunadarma, Udinus,
>   UNY, UPN Veteran Yogyakarta, UPN Veteran Jawa Timur, UPN Veteran Jakarta).
>   Jangan menyajikannya sebagai format kampus; minta panduan resmi pengguna.
> - **16 preset bersumber dari satu fakultas/prodi** (mis. UGM = FKH, ITB = Teknik
>   Geologi, ITS = FTI, UNDIP = FPIK). Tanyakan fakultas pengguna sebelum memakainya.
> - **26 dari 27** preset tidak menyatakan format nomor caption.
> - Nomor SK pada `ui.yaml` (2143/SK/R/UI/2017) **tidak terkonfirmasi** (lihat
>   `skills/integritas_akademik/references/regulasi.md`).
>
> Catatan pembacaan pedoman resmi dan apa yang tidak terbaca: [TEMUAN-PEDOMAN.md](TEMUAN-PEDOMAN.md).
>
> Hasilkan ulang audit: `python3 scripts/audit_preset.py --out presets/AUDIT.md`

Kolom **Siap pakai** adalah hasil percobaan nyata: menjalankan
`buat_template_lengkap.py` terhadap setiap preset. Tanda `perlu isi` berarti
sumber JSON kampusnya tidak menyebut angka tersebut (bukan salah konversi) —
`catatan_konflik:` di berkasnya menjelaskan apa yang harus dicari di panduan.
Skrip akan berhenti dengan daftar kunci yang kosong, bukan diam-diam memakai nol.

| Berkas | Kampus | Kertas | Margin k/r/a/b (cm) | Spasi | Siap pakai |
|---|---|---|---|---|---|
| `ars-fti.yaml` | Univ. Adhirajasa Reswara Sanjaya — FTI | A4 | 4 / 3 / 3 / 3 | 2 | ya |
| `binus.yaml` | BINUS University | A4 | 4 / 4 / 3 / 3 | 1,5 | ya — **TIDAK TERVERIFIKASI** |
| `budi-luhur.yaml` | Universitas Budi Luhur | A4 | 4 / 4 / 3 / 3 | 1,5 | ya — **TIDAK TERVERIFIKASI** |
| `custom.yaml` | (kerangka kosong — isi sendiri) | — | — | — | perlu isi |
| `generic.yaml` | Umum (tanpa kampus) | A4 | 4 / 4 / 3 / 3 | 1,5 | ya |
| `gunadarma.yaml` | Universitas Gunadarma | A4 | 4 / 4 / 3 / 3 | 1,5 | ya — **TIDAK TERVERIFIKASI** |
| `ipb.yaml` | Institut Pertanian Bogor | A4 | — | — | perlu isi |
| `itb.yaml` | Institut Teknologi Bandung | A4 | 4 / 4 / 3 / 3 | 1,5 | ya |
| `its.yaml` | Institut Teknologi Sepuluh Nopember | A4 | 3 / 3 / 2 / 2,5 | 1 | ya |
| `telu.yaml` | Telkom University | A4 | 4 / 3 / 3 / 3 | 1,5 | ya |
| `uad.yaml` | Universitas Ahmad Dahlan | A4 | — | 2 | perlu isi |
| `ub.yaml` | Universitas Brawijaya | A4 | 3 / 2,5 / 2,5 / 2,5 | 1,5 | ya |
| `udinus.yaml` | Universitas Dian Nusantara | A4 | 4 / 4 / 3 / 3 | 1,5 | ya — **TIDAK TERVERIFIKASI** |
| `ugm.yaml` | Universitas Gadjah Mada | A4 | 4 / 4 / 3 / 3 | 2 | ya |
| `ui.yaml` | Universitas Indonesia | A4 | 4 / 3 / 3 / 3 | 1,5 | ya |
| `uii.yaml` | Universitas Islam Indonesia | A4 | 4 / 3 / 3 / 3 | 1,5 | ya |
| `umb.yaml` | Universitas Mercu Buana | A4 | 4 / 4 / 3 / 3 | 2 | ya |
| `umm.yaml` | Universitas Muhammadiyah Malang | A4 | 4 / 4 / 3 / 3 | 1,5 | ya |
| `umn.yaml` | Universitas Multimedia Nusantara | A4 | 4 / 4 / 3 / 3 | 2 | ya |
| `ums.yaml` | Universitas Muhammadiyah Surakarta | A4 | 4 / 4 / 3 / 3 | 2 | ya |
| `umy.yaml` | Universitas Muhammadiyah Yogyakarta | A4 | — | 2 | perlu isi |
| `unair.yaml` | Universitas Airlangga | A4 | 4 / 4 / 3 / 3 | 2 | ya |
| `undip.yaml` | Universitas Diponegoro | A4 | 4 / 3 / 3 / 3 | 1,5 | ya |
| `unhas.yaml` | Universitas Hasanuddin | **B5** | — / 2,25 / — / 2,25 | — | perlu isi |
| `universitas-contoh.yaml` | Universitas Contoh (fiktif) | A4 | 4 / 3 / 3 / 3 | 1,5 | ya |
| `unpad.yaml` | Universitas Padjadjaran | A4 | 4 / 4 / 3 / 3 | 2 | ya |
| `uny.yaml` | Universitas Negeri Yogyakarta | A4 | 4 / 4 / 3 / 3 | 1,5 | ya — **TIDAK TERVERIFIKASI** |
| `upn-veteran.yaml` | UPN Veteran Yogyakarta | A4 | 4 / 4 / 3 / 3 | 1,5 | ya — **TIDAK TERVERIFIKASI** |
| `upnv-jatim.yaml` | UPN Veteran Jawa Timur | A4 | 4 / 4 / 3 / 3 | 1,5 | ya — **TIDAK TERVERIFIKASI** |
| `upnvj.yaml` | UPN Veteran Jakarta | A4 | 4 / 4 / 3 / 3 | 1,5 | ya — **TIDAK TERVERIFIKASI** |

Seluruh preset bernilai **A4** (kecuali UNHAS = **B5** 176×250 mm, dikoreksi 5 Nov 2026) dan **Times New Roman**; tidak ada kampus yang
menyebut kertas atau font lain di sumber yang tersedia, jadi tidak ada yang
ditambahkan sebagai tebakan. `ars-fti-halaman.yaml` bukan profil — itu berisi
bunyi halaman bagian awal/akhir untuk `--halaman`.

## Tiga hal yang harus diperiksa sebelum memakai preset otomatis

1. **Preset hasil konversi bukan kutipan panduan.** Kepala berkasnya bertuliskan
   `DIKONVERSI OTOMATIS`; nilai yang berasal dari panduan tercatat di
   `catatan_sumber`, yang tidak ada nilainya `null` + `catatan_konflik`.
2. **Satu kampus sering punya beberapa pedoman.** `ugm.yaml` memakai panduan FKH,
   padahal DTSL Fakultas Teknik memakai spasi 1,15 dan margin berbeda — ini
   tertulis di `catatan_sumber`-nya.
3. **Caption sering tidak disebut panduan.** 28 dari 31 preset tidak menyatakan
   format nomor caption; jangan menebak, tanyakan ke pengguna atau periksa contoh
   skripsi terbitan kampusnya.

## Menambah preset kampus nyata

`ars-fti.yaml` adalah **cetakan** terbaik: setiap angka dikutip dengan nomor butir
panduan, dan memuat `catatan_konflik`, `pengecualian`, serta `ringkasan`. Salin
berkasnya, ganti isinya — jangan mulai dari nol.

Preset boleh dibuat dari `skills/proposal_skripsi/campus_templates/*.json`
memakai `scripts/campus_json2yaml.py --semua`, tetapi hasilnya WAJIB diperiksa
terhadap panduan: konverter hanya membaca apa yang tertulis di JSON, dan JSON itu
sendiri sering tidak memuat margin atau spasi.

1. Ekstrak teks panduan: `pdftotext -layout panduan.pdf panduan.txt`.
2. Isi `dokumen`, `font`, `spasi`, `penomoran_halaman`, `caption`, `sitasi` —
   semuanya angka; kutip nomor butirnya di komentar.
3. Isi `sistematika.bagian_awal`, `bab`, `bagian_akhir` **persis seperti panduan**.
   Jangan menormalkan nama: bila panduan menulis "Identifikasi Masalah", tulis itu,
   bukan "Rumusan Masalah". Nama subbab menentukan apakah pemeriksa bisa bekerja.
4. Catat setiap pertentangan internal panduan di `catatan_konflik` — jangan menebak.
   Contoh nyata: panduan menyebut APA tetapi seluruh contohnya memakai
   `(Nama, Tahun:Halaman)`; panduan mencantumkan subbab BAB IV tetapi template
   resminya tidak.
5. Simpan sebagai `presets/<slug-kampus>.yaml`, isi `kampus.sumber_panduan` dengan
   nama dokumen + edisi/tahun, lalu tambahkan satu baris ke tabel di atas.
6. Uji: `python3 scripts/buat_template_lengkap.py presets/<baru>.yaml /tmp/uji.docx`
   lalu `python3 scripts/periksa_sistematika.py naskah_contoh.md presets/<baru>.yaml`

Perkiraan waktu 20-30 menit per kampus untuk panduan 30-50 halaman yang dibaca
manual. Konversi otomatis 29 preset memerlukan waktu kurang dari satu menit —
itulah sebabnya hasilnya harus diperiksa, bukan dipercaya.

Preset hanya berisi KETENTUAN FORMAT dari dokumen publik kampus — jangan pernah
memasukkan data pribadi, naskah skripsi, atau dokumen milik individu ke folder ini
(penjaga konten `tests/tes_bundel.py` akan menggagalkan build).
