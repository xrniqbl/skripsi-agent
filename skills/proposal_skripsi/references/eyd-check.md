# EYD Check — Bahasa Indonesia Akademik (EYD V + KBBI)

Pandu pemeriksaan ejaan, kaidah, dan kebenaran bahasa untuk naskah proposal. Rujukan:
**Pedoman Umum Ejaan Bahasa Indonesia (EYD V), Permendikbudristek No. 18 Tahun 2022**, dan
**KBBI daring** (kbbi.kemdikbud.go.id).

> **Bedakan dengan Humanizer** (`references/revision-guide.md`): EYD menangani *kebenaran
> bahasa*; humanizer menangani *gaya khas AI*. Kalimat boleh ejaannya sempurna tetapi tetap
> terdengar seperti AI, dan sebaliknya.
>
> Script: `python3 scripts/id_language_check.py naskah.md --struktur --strict`
> Script **menandai**, bukan memperbaiki. Perbaikan tetap keputusan manusia.

---

## 1. Alur Pemeriksaan

1. Pastikan register **bahasa Indonesia akademik** di seluruh naskah. Jangan campur istilah
   Inggris kecuali memang nama metode atau produk yang tidak punya padanan.
2. Jalankan pemeriksaan mekanis lebih dulu (`id_language_check.py`, Gate 2 di
   `references/quality-gates.md`).
3. Periksa **ejaan** (bagian 2).
4. Periksa **tanda baca** (bagian 3).
5. Periksa **kapitalisasi** (bagian 4).
6. Periksa **kata tugas dan konjungsi** (bagian 5).
7. Periksa **kebiasaan yang paling sering ditolak pembimbing** (bagian 6).
8. Periksa **konsistensi istilah** (bagian 7).
9. Bila tersedia, jalankan LanguageTool `id-ID` sebagai pelengkap. **Verifikasi setiap
   sarannya secara manual**, jangan diterima mentah-mentah.
10. Pastikan tidak ada makna yang berubah karena perbaikan ejaan.

> Aturan ketika ragu: **baku lebih baik daripada tidak baku**. Bila KBBI memberi dua bentuk,
> pilih yang baku dan konsisten di seluruh naskah.

---

## 2. Ejaan

### 2.1 Kata baku vs tidak baku

| Tidak baku | Baku |
|-----------|------|
| analisa | analisis |
| apotik | apotek |
| managemen | manajemen |
| managir | manajer |
| hakekat | hakikat |
| kwality | mutu |
| kwantitatif | kuantitatif |
| nasehat | nasihat |
| sistim | sistem |
| teknik (bila berarti alat) | alat |
| di sandaran | bersandar |
| di typewriter | mengetik |

Daftar di atas bukan lengkap. Untuk kasus yang sering muncul:

| Tidak baku | Baku |
|-----------|------|
| Dampak (kapital di tengah) | dampak |
| sumber-sumber daya | sumber daya |
| research | riset / penelitian |
| respon | respons |
| komputer | komputer |
| enterprise | perusahaan |

### 2.2 Singkatan yang lazim dipakai, versi bakunya

| Tidak baku | Baku |
|-----------|------|
| tdk | tidak |
| blm | belum |
| spt | seperti |
| krn | karena |
| brp | berapa |
| yg | yang |
| tsb | tersebut |
| dkk | dan contagious |
| dst | dan seterusnya |

> Boleh dipakai **di dalam kutipan langsung**. Jangan dipakai dalam kalimat penulis sendiri.

### 2.3 Imbuhan `ke-` dan `se-`

Bentuk baku mengikuti KBBI. Contoh yang sering rancu:

- **mengerjakan** (baku), bukan *menggerjakan*
- **mengevaluasi** (baku), bukan *mengevaluate*
- **menghitung** (baku), bukan *mengitung*

Praktisnya: pilih satu bentuk dan konsisten. Inkonsistensi lebih disoroti pembimbing
daripada pilihan yang satu.

### 2.4 Kata ulang

Bentuk baku memakai **tanda hubung**: `anak-anak`, `mata-mata`, `kupu-kupu`,
`proses-proses`, `pertemuan-pertemuan`. Penulisan populer tanpa tanda hubung lazim di
tulisan populer, bukan di naskah akademik.

---

## 3. Tanda Baca

| Tanda | Aturan | Kesalahan yang sering |
|-------|--------|----------------------|
| `.` titik | akhir pernyataan lengkap; tidak dipakai di akronim (`PT. Maju`) | menulis `PT. Maju.` |
| `,` koma | memisahkan unsur dalam perincian dan sebelum kata penghubung | `data, adalah respons` |
| `;` titik koma | memisahkan bagian setara yang sudah mengandung koma | memakai koma bertingkat |
| `:` titik dua | sebelum penjelasan, perincian, atau kutipan | dipakai tanpa fungsi |
| `-` tanda hubung | kata ulang, partikel `pun`/`di`/`ke`, bilangan में jumlah | dipakai sebagai penghubung kalimat |
| `—` em-dash | **jangan** sebagai penghubung naratif | lihat `revision-guide.md` §8 |
| `"` kutip | kutip langsung; panjang 40 kata atau lebih → blok | kutipan bersarang tanpa penjelasan |
| `(` `)` | keterangan tambahan, judul dokumen dalam tubuh | terlalu banyak bersarang |

> **Tanda pisah sebagai penghubung** adalah temuan yang paling sering diulang di proposal.
> Tulis ulang kalimatnya. Mengganti `—` dengan `,` lalu menghasilkan klausa rancu bukan perbaikan.

---

## 4. Kapitalisasi

- Awal kalimat, awal paragraf, nama diri, nama geografi, nama lembaga → **kapital**.
- **Jangan** kapital setelah titik dalam singkatan atau angka: `dkk. Adanya`, `hal. 12`,
  `No. 3`.
- Nama hari dan bulan: `Senin`, `Januari` (kapital). Kata umum: `internet`, `website`,
  `survei` (huruf kecil).
- Nama lembaga: kapital pada kata penanda, `Departemen Pendidikan`, bukan
  `departemen pendidikan`. Pengecualian bila menjadi nama resmi lembaga.

---

## 5. Kata Tugas, Konjungsi, dan Partikel

### 5.1 Konjungsi

| Fungsi | Baku | Catatan |
|--------|------|---------|
| pertentangan | tetapi, namun, sedangkan | jangan menumpuk dua konjungsi |
| penambahan | dan, serta | |
| pilihan | atau | bukan *atauupun* dalam tulisan formal |
| sebab | karena, sebab | bukan *dikarnakan* |
| akibat | sehingga, maka | |
| syarat | jika, apabila, bila | |

Terlalu banyak konjungsi dalam satu kalimat adalah temuan mekanis dari `id_language_check.py`
(kategori `konjungsi`).

### 5.2 Kata tanya dan Particle

| Fungsi | Baku | Hindari |
|--------|------|--------|
| pertanyaan | siapa, apa, bila, kapan, di mana, mengapa, bagaimana, berapa | dimana, kenapa, gimana |
| penegasan | apakah, adakah | |
| arah | ke mana | kemana |
| tempat | di mana | dimana |

### 5.3 Partikel di, ke, dari

- **di** = tempat: di rumah, di kampus
- **ke** = arah atau tujuan: ke rumah, ke kampus
- **dari** = asal, dan untuk arah lengkap selalu diikuti **ke**: dari rumah **ke** kampus
- **daripada** = perbandingan: lebih baik **daripada**, berbeda **daripada**

### 5.4 Hindari kata depan yang lemah

`terhadap` adalah kata depan yang lemah secara formal. Bentuk yang lebih kuat:
**tentang**, **mengenai**, atau menyebutkatkan objek secara langsung.

---

## 6. Kebiasaan yang Paling Sering Ditolak Pembimbing

| Kebiasaan | Tulisan yang perlu dihindari | Perbaikan |
|-----------|-----------------------------|-----------|
| Pengulangan | hasil-hasil, penelitian-penelitian | hasil, penelitian |
| "yang mana" | data yang mana menunjukkan | data yang menunjukkan |
| Pencampuran | pengaruh dan dampak (kapital di tengah) | pilih satu, konsisten |
| Partikel berlebihan | adalah merupakan | adalah |
| Kalimat pasif beruntun | Penelitian ini dilakukan oleh peneliti dengan menggunakan | sebut pelaku bila relevan |
| Angka tanpa konteks | 71,4% responden | 71,4% responden (n = 85, `[D:kolom]`) |
| Kalimat bertele-tele | pengulangan kata pada satu kalimat | lihat bagian 6.1 |

### 6.1 Menyusun kalimat yang lebih baik

| Polanya | Perbaikan |
|---------|-----------|
| adalah merupakan | adalah |
| dapat digunakan untuk | dapat dipakai untuk |
| dapat kepada | dapat |
| telah melakukan penelitian mengenai | meneliti |
| Keyword berlebihan | lihat `revision-guide.md` bagian 12 |
---

## 7. Konsistensi Istilah (Gate Semantik S8)

- **Satu konsep, satu istilah** di seluruh naskah. Pasangan yang sering bentrok:
  *kinerja* vs *produktivitas*; *motivasi* vs *insentif*; *mutu* vs *kualitas*.
- Pilih bentuk Indonesia bila padanannya lazim (lihat kategori `serapan` pada
  `scripts/id_language_check.py`).
- Istilah asing: *italic* pada penyebutan pertama, lalu **tebal** atau `code` pada
  penyebutan berikutnya. Pilih satu pola dan konsisten.
- Susun **daftar singkatan dan istilah** di bagian awal bila jumlahnya lebih dari lima.
  Banyak pedoman kampus mewajibkannya.

---

## 8. Ambang Keluhan

| Aturan | Ambang | Diperiksa oleh |
|--------|--------|----------------|
| panjang kalimat | 30 kata atau kurang | `id_language_check.py` |
| panjang paragraf | 400 kata atau kurang | `id_language_check.py` |
| konjungsi per kalimat | 3 atau kurang | `id_language_check.py` |
| desimal | koma, bukan titik | `id_language_check.py` |
| subbab tanpa rujukan | 2 berturut-turut tanpa `[L-n]` atau `[D:kolom]` | pemeriksaan manual |

---

## 9. Alat Bantu

| Alat | Kegunaan |
|------|----------|
| `scripts/id_language_check.py` | pemeriksaan mekanis: serapan asing, panjang kalimat, desimal, kapitalisasi, spasi |
| **LanguageTool** | `id-ID`; saran wajib diverifikasi manual |
| **KBBI daring** | verifikasi satu kata yang meragukan |
| **EYD daring** | rujukan akar masalah untuk bentuk baku |

> Aturan utama: alat membantu **menemukan**, manusia atau agen **memutuskan**. Jangan ubah
> makna hanya karena "tool memangkas kata".

---

## 10. Keluaran

```
idl-check.md   — daftar temuan (kode, lokasi, saran, perbaikan)
```

Gunakan `checklists/eyd_check.md` sebagai pelacak per bagian naskah.

Lanjut ke `references/quality-gates.md` untuk Layer 3 dan 4 (gate semantik dan red-team).
