# Plagiarism Check — Deteksi Plagiarisme & Integritas Kutipan (Bahasa Indonesia)

Pandu memeriksa plagiarisme sebelum naskah proposal diserahkan ke pembimbing. Tujuan:
**setiap kalimat berasal dari penulis sendiri, atau dikutip/parafrase dengan atribusi yang benar.**

Berbeda dengan paper jurnal, risiko utama proposal Indonesia bukan hanya *copy-paste*, melainkan:

1. **Rumusan masalah & latar belakang diambil dari proposal/skripsi orang lain** (judul mirip,
   struktur paragraf identik) termasuk dari repository institusi atau mesin pencari,
   sering tanpa atribusi sama sekali.
2. **Definisi operasioal & instrumen disalin** dari paper/proposal lain tanpa-adaptasi.
3. **Bab II menjadi daftar ringkasan** tiap paper, bukan sintesis.

---

## 1. Jenis Plagiarisme

| Jenis | Deskripsi | Tanda |
|-------|-----------|-------|
| **Copy-paste (langsung)** | Menyalin kalimat/paragraf utuh tanpa tanda kutip | Blok kalimat yang gayaunya berbeda dari sekelilingnya |
| **Mosaik / patchwork** | Mengacak kata sumber tanpa parafrase sungguhan | Struktur kalimat masih mengikuti sumber; hanya kata diganti sinonim |
| **Parafrase tanpa atribusi** | Parafrase sahih tetapi sumber tidak disebut | Klaim/angka spesifik tanpa `[L-n]` |
| **Self-plagiarism** | Menyerahkan ulang bagian karyawan sendiri sebelumnya (tanpa izin) | Kalimat identik dengan karya penulis sendiri |
| **Pencucian sitasi / salah kutip** | Mengutip sumber yang tidak pernah dibaca (sitasi sekunder) | Sumber di daftar pustaka tidak cocok dengan klaim |
| **Plagiarisme definisi** *(khas proposal)* | Definisi, rumusan masalah, atau latar belakang proposal lain disalin | Struktur subbab identik dengan proposal lain; frasa kunci sama |
| **Plagiarisme instrumen** *(khas proposal)* | Butir kuesioner/pedoman wawancara disalin tanpa atribusi | Skala, redaksi butir, dan urutan sama persis |

---

## 2. Alur Kerja — Verifikasi Lokal (bisa dilakukan agen)

Tanpa alat berbayar. Kerjakan berurutan:

### 2.1 Overlap terhadap korpus lokal
Bandingkan kalimat naskah dengan **berkas sumber di folder** (hasil `ingest_sources.sh`).

```bash
python3 scripts/plagiarism_check.py naskah.md --sumber .cache_ekstrak/ \
    --md plagiarism_report.md --json plagiarism_report.json
```

- Deteksi: **frasa identik ≥ 7 kata berurutan** (tidak termasuk `[L-n]`) → tandai.
- Kalimat naskah yang memuat rumusan sumber **tanpa tanda kutip dan tanpa `[L-n]`** → merah.
- Perkiraan tingkat: kalimat bertanda / total kalimat.

### 2.2 Deteksi duplikasi internal (WAJIB, tanpa sumber)
Naskah yang menyalin dirinya sendiri (karena drafting berulang) adalah gejala plagiarisme
eksternal yang belum terdeteksi:

```bash
python3 scripts/plagiarism_check.py naskah.md --internal
```

Duplikasi **antar-bab** (BAB I vs BAB II) hampir selalu tanda penulisan ulang yang belum
dibersihkan — perbaiki sebelum pemeriksaan eksternal.

### 2.3 Periksa kutipan langsung
- Setiap kutipan langsung **harus** diapit tanda kutip + `[L-n]` (+ nomor halaman bila gaya
  membutuhkannya).
- **Verifikasi kutipan benar-benar ada di sumber** — jangan mengarang isi kutipan
  (anti-hallucination). `plagiarism_check.py` menandai kutipan yang tidak ditemukan di korpus.
- Kutipan panjang ≥ 40 kata → format blok/indent sesuai gaya.

### 2.4 Uji kualitas parafrase
Parafrase yang baik:
1. Ada `[L-n]` ke sumber aslinya.
2. Struktur kalimat **bukan** salinan berurutan dari sumber (periksa urutan klausa).
3. Bukan sekadar mengganti kata dengan sinonim tanpa mengubah struktur.
4. Makna tetap akurat — parafrase tidak boleh mengubah klaim.

Nilai tiap paragraf: `kutipan tepat` / `parafrase baik` / `parafrase tipis (berisiko)` / `salin`.

### 2.5 Self-plagiarism
- Bandingkan dengan karya penulis sendiri sebelumnya bila tersedia.
- Konteks Indonesia: proposal terdahulu yang disalin **dengan izin** masih harus dilaporkan
  sebagai catatan integritas, bukan diam-diam.

### 2.6 Verifikasi sumber jaringan (opsional)
- Cari frasa verbatim (8–10 kata) di mesin pencari untuk menemukan sumber tak dikenal.
- **Jangan** memakai hasil pencarian sebagai bukti final; gunakan sebagai sinyal.

---

## 3. Skor Kemiripan

Bila memakai Turnitin/iThenticate/PlagiarismCheck atau estimasi lokal:

| Pita | Interpretasi |
|------|--------------|
| 0–10% | Wajar bila berasal dari kutipan singkat dan daftar pustaka; tetap periksa kalimat sumber (bukan templat). |
| 10–20% | Cari sumber berulang; parafrase ulang bagian yang tumpang tindih tanpa kutip. |
| >20% | **Wajib direvisi**: kutip/parafrase/sitasi seluruh bagian yang tumpang tindih sebelum diserahkan. |

> Alat kemiripan **bukan** penilai bahasa dan **bukan** pengganti verifikasi salah kutip.
> Skor rendah ≠ bebas plagiarisme. Banyak plagiarisme berupa parafrase yang lolos deteksi
> mesin tetapi gagal uji parafrase §2.4.

**Jangan** memarafrase tanpa atribusi.

## 4. Aturan Anti-Plagiarisme (selalu berlaku)

1. **Jangan** menyalin kalimat sumber tanpa tanda kutip + `[L-n]`.
2. **Jangan** memarafrase tanpa atribusi.
3. **Jangan** mengarang atau mempercantik isi kutipan.
4. **Jangan** mengirim teks hasil AI yang menyalin sumber; integritas akademik tetap berlaku.
5. Setiap data/angka/klaim spesifik punya sumber — bila tidak → tandai `UNVERIFIED`.
6. **Struktur ≠ ciptaan.** Mengambil *kerangka* subbab umum ("1.1 Latar Belakang") bukan
   plagiarisme; menyalin *isi paragrafnya* adalah plagiarisme.

---

## 5. Integritas & Etika

- Parafrase sahih = menuliskan gagasan dengan kalimat sendiri **sambil** menyitasi; bukan
  mengganti kata.
- Laporkan temuan tumpang tindih yang signifikan kepada user; **jangan** diperbaiki diam-diam
  lalu dianggap selesai.
- Bila sumber berbahasa Inggris dipakai untuk naskah Indonesia, parafrase ke dalam bahasa
  sendiri tetap wajib — terjemahan harfiah bukan parafrase.

---

## 6. Pemeriksaan khusus proposal

| Letak | Yang diperiksa |
|-------|----------------|
| **Judul & rumusan masalah** | Apakah judul terlalu mirip proposal lain? Uji dengan pencarian judul. |
| **Latar belakang** | Apakah kalimat pertama subbab identik dengan sumber mana pun? |
| **Definisi & instrumen** | Butir kuesioner/pedoman harus dinyatakan **asal** (`[L-n]`) atau "dikembangkan sendiri". |
| **Bab II** | Bukan daftar ringkasan per paper. Wajib ada **sintesis** antar sumber (§ Step 2.1). |
| **Tabel penelitian terdahulu** | Data tiap baris harus dapat dilacak ke sumbernya. |

> **Saran praktis**: bila rumusan masalah terasa "terlalu mudah", biasanya karena diambil dari
> proposal lain tanpa digali. Kembalilah ke data lokal (`[D:kolom]`) untuk membangunnya.

---

## 7. Keluaran

```
plagiarism_report.md   — area tumpang tindih (lokasi, sumber, jenis, keputusan: kutip/parafrase/sitasi/hapus)
plagiarism_report.json — angka machine-readable untuk pemeriksaan lanjutan
```

Gunakan `checklists/plagiarism_check.md` untuk pelacakan per bagian.
