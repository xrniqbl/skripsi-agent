# Checklist Humanizer (Layer 1)

Pelacak untuk **Layer 1** dari `references/quality-gates.md`. Rujukan pola:
`references/revision-guide.md`.

Humanizer beririsan dengan EYD, tapi bukan hal yang sama. EYD menangkap
kesalahan bahasa; humanizer menangkap **gaya khas mesin**. Kalimat yang ejaannya
sempurna tetap bisa terdeteksi di sini.

> **Aturan mutlak**: humanizer boleh mengubah *gaya*, tidak boleh mengubah *fakta*.
> Angka, kutipan, penanda `[L-n]`/`[D:kolom]`/`[K-n]`, rumusan masalah, tujuan,
> dan hipotesis tidak boleh berubah bentuk, hanya boleh dibuat lebih natural.

## A. Pola struktur (bagian 1-6)

- [ ] Kalimat pembuka bab bukan "Pada zaman yang semakin berkembang..."
- [ ] Frasa penutup bab bukan "Dengan demikian, diharapkan agar penelitian ini..."
- [ ] Tiap subbab punya **kalimat tesis** yang menyatukan isinya
- [ ] Kalimat tesis tidak mengulang judul subbab secara harfiah
- [ ] Tiap paragraf punya satu gagasan utama, bukan tiga
- [ ] Tidak ada daftar bertingkat yang sebenarnya adalah satu kalimat
- [ ] Penomoran manual (`1)`, `a)`, `i)`) tidak bercampur dengan `1.` dan `a.`

## B. Kalimat dan tanda baca (bagian 7-10)

- [ ] Tidak ada tanda pisah (`—`, `–`, `-`) sebagai penghubung
- [ ] Tidak ada "tidak hanya... tetapi juga" berulang
- [ ] Panjang kalimat 15-25 kata; tidak ada yang >30 kata
- [ ] Tidak ada kalimat yang dimulai "Hal ini menunjukkan bahwa..."
- [ ] Kalimat pasif tidak melebihi 1/3 naskah
- [ ] Subjek tidak dihilangkan pada kalimat yang butuh pelaku
- [ ] Kalimat berurutan memakai pola yang beragam (bukan semuanya "X adalah Y")

## C. Kata dan frasa (bagian 11-15)

- [ ] Tidak ada kata kerja generik tanpa objek: menunjukkan, propane, menjamin
- [ ] Penghilangan "sangat", "sangat sekali", "sekali", "amat", "benar-benar"
- [ ] Tidak ada "tidak hanya ... namun juga"
- [ ] Penghilangan "pada hakikatnya", "secara keseluruhan", "dengan demikian"
- [ ] Tidak ada "dapat dikatakan" / "tidak dapat dipungkiri"
- [ ] "-hal ini" / "hal tersebut" diganti objek yang spesifik
- [ ] Tidak ada pengulangan kata yang berlebihan: "sangat ... sekali"
- [ ] Tidak ada "yang mana" sebagai penanda relasi

## D. Tanda tangan AI (bagian 16-21)

- [ ] Tidak ada pengulangan struktur 4-kalimat (claim → acknowledge → explore → conclude)
- [ ] Tidak ada penutup "alhasil" / "hasilnya" yang seragam di tiap bab
- [ ] Tidak ada "mari kita" / "seperti yang telah kita bahas"
- [ ] Tidak ada markdown decoration berlebihan (`**` pada tiap kata, emoji, blok)
- [ ] Kalimat terakhir bab tidak meringkas ulang isi bab secara generik
- [ ] Tidak ada pola "tidak hanya X, tetapi juga Y" yang dipakai >3 kali
- [ ] Kutipan langsung (kutip block) tidak diberi penjelasan penulis sendiri

## E. Kekuatan dan penekanan (bagian 22-25)

- [ ] Kalimat terlalu tinggi kontras, misalnya "sangat signifikan"
- [ ] Penegasan berlebihan: "pasti", "tidak diragukan", "nyata"
- [ ] Frasa "tidak boleh dilupakan" / "perlu diperhatikan"
- [ ] Terlalu banyak "bukan hanya" / "justru"
- [ ] Penutupan subbab dengan pertanyaan retoris yang dijawab sendiri

## F. Pengujian akhir

Jalankan pemeriksaan otomatis, lalu baca ulang dengan mata pembimbing:

```bash
# Lapis 2 adalah partner wajib Lapis 1: pola yang tertinggal biasanya
# juga merupakan kesalahan mekanis.
python3 scripts/id_language_check.py outputs/proposal.md --struktur
python3 scripts/plagiarism_check.py outputs/proposal.md --internal
```

> Pola humanizer **tidak diautomatisasi**. Skrip hanya menangkap sebagian
> (kategori `baku`, `spasi`, `serapan`); sisanya dinilai dengan membaca ulang.

- [ ] Semua temuan `spasi` dan `baku` bersih
- [ ] Tidak ada temuan `serapan` yang belum diputuskan
- [ ] Naskah dibaca ulang keras: apakah ada kalimat yang terasa "ditempel"?
- [ ] Pembaca luar (teman/asisten) bisa menjelaskan isi tiap subbab tanpa membaca
      judulnya?

## G. Yang harus TIDAK diubah

- [ ] Angka hasil analisis tetap sama
- [ ] Kutipan asli sumber tidak diubah kalimatnya
- [ ] Penanda `[L-n]`, `[D:kolom]`, `[K-n]`, `[U]` tetap lengkap
- [ ] Istilah teknis yang sudah disepakati tidak diganti sinonim
- [ ] Rumusan masalah, tujuan, dan hipotesis tetap 1:1

---

Lanjut ke Lapis 2 (mekanis/EYD): `checklists/eyd_check.md`.
