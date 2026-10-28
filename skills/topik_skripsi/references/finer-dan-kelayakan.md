# FINER dan Kelayakan Topik

## Kenapa FINER, bukan sekadar "bagus atau tidak"

Skripsi bukan lomba ide. Ia proyek terbatas: satu orang, satu semester, satu pembimbing,
biaya sendiri. **Topik yang menarik tapi tidak selesai adalah topik yang gagal**, dan
kegagalan itu tidak terlihat sampai bab IV.

FINER (Hulley, Cummings, Browner, Grady & Newman — *Designing Clinical Research`) memecah
"topik bagus" menjadi lima dimensi yang bisa dinilai terpisah. Di sini bobotnya disesuaikan
untuk konteks skripsi Indonesia: **kelayakan diberi bobot paling besar**, karena itu penyebab
kegagalan nomor satu.

---

## Rubrik penilaian

Setiap dimensi diskor **0–5**. Skor 0 berarti topik mati di dimensi itu.

### F — Feasible (bobot 30)

Bisa dikerjakan dengan sumber daya yang nyata.

| Skor | Kondisi |
|---|---|
| 5 | data sudah di tangan atau akses sudah dijamin tertulis; waktu cukup dengan margin; alat dikuasai; biaya nol |
| 4 | akses hampir pasti; satu hal masih perlu diurus (izin/satu dataset) |
| 3 | akses mungkin; butuh 2–3 hal yang belum ada, tapi jalurnya jelas |
| 2 | salah satu dari waktu/data/alat berisiko gagal |
| 1 | dua atau lebih berisiko gagal |
| 0 | data tidak akan pernah bisa diakses |

Sub-pertanyaan yang harus dijawab sebelum memberi skor:
- Apakah izin lokasi sudah ada, atau baru "katanya boleh"?
- Berapa bulan sisa waktu, dan berapa bulan yang dibutuhkan?
- Apakah lo sudah pernah menjalankan analisis yang dipilih, minimal sekali?
- Ada biaya yang tidak bisa lo tanggung?

### I — Interesting (bobot 15)

Apakah lo akan bertahan enam bulan mengerjakannya.

| Skor | Kondisi |
|---|---|
| 5 | lo sudah penasaran sebelum disuruh; topiknya nyambung dengan kerja/sehari-hari |
| 4 | menarik, ada kaitan pribadi |
| 3 | netral — bisa dikerjakan |
| 2 | dipilih karena gampang, bukan karena ingin tahu |
| 1 | lo sudah bosan sebelum mulai |
| 0 | lo tidak ingin tahu jawabannya |

> Skor 2 bukan bencana, tapi catat: minat rendah + hambatan tinggi = risiko berhenti.

### N — Novel (bobot 20)

Bukan "belum pernah ada", tapi **ada sesuatu yang belum dijelaskan**.

| Skor | Kondisi |
|---|---|
| 5 | ada kontradiksi literatur atau asumsi yang jelas bisa diserang, dibuktikan dengan probe |
| 4 | ada evidence gap nyata (n kecil / satu situs) dengan bukti tabel |
| 3 | ada celah konteks yang beralasan (bukan sekadar ganti kota) |
| 2 | hanya replikasi dengan objek berbeda tanpa alasan mengapa berbeda |
| 1 | sudah ada studi yang hampir identik |
| 0 | topik sudah dijawab tuntas |

Bukti yang wajib disiapkan untuk skor ≥4: hasil `literature_probe.py` + tabel asumsi.

### E — Ethical (bobot 15)

| Skor | Kondisi |
|---|---|
| 5 | tanpa subjek manusia, atau data anonim publik |
| 4 | subjek manusia dewasa, izin jelas, risiko minimal, informed consent siap |
| 3 | ada data sensitif tapi bisa dianonimkan |
| 2 | melibatkan populasi rentan (anak, pasien, narapidana) tanpa jalur etik yang jelas |
| 1 | butuh persetujuan etik yang belum ada dan sulit diperoleh dalam waktu |
| 0 | desainnya tidak mungkin disetujui |

Catatan untuk Indonesia: penelitian di instansi pemerintah biasanya butuh **surat izin
penelitian** (dari kampus + instansi), dan penelitian dengan pasien butuh **kelaikan etik**
dari komite etik. Itu waktu, bukan formalitas — hitung di Feasible.

### R — Relevant (bobot 20)

| Skor | Kondisi |
|---|---|
| 5 | ada pihak konkret yang akan memakai hasilnya, dan sudah menyatakan minat |
| 4 | ada implikasi kebijakan/praktik yang jelas bagi instansi tertentu |
| 3 | relevan secara akademik, pengguna praktis belum jelas |
| 2 | hanya menambah literatur |
| 1 | tidak ada yang akan memakai |
| 0 | bertentangan dengan kebutuhan nyata |

---

## Rumus dan ambang

```
skor_total = Σ (skor_dimensi ÷ 5 × bobot_dimensi)
```

Bobot: F=30, I=15, N=20, E=15, R=20 (total 100).

| Total | Keputusan |
|---|---|
| ≥ 85 | kuat — lanjut, jaga dimensi terlemah |
| 70–84 | layak — lanjut dengan perbaikan pada dimensi terlemah |
| 55–69 | rapuh — perbaiki dulu sebelum menyusun proposal |
| < 55 | ganti topik |
| **ada dimensi 0** | **ganti topik, berapa pun totalnya** |

> Aturan dimensi 0 bersifat mutlak. Topik dengan Feasible 0 tapi Novel 5 adalah topik yang
> tidak akan pernah selesai.

---

## Jalur perbaikan per dimensi

Skor rendah bukan vonis — tapi perbaikannya harus spesifik, bukan "dibuat lebih baik".

| Dimensi lemah | Perbaikan konkret |
|---|---|
| **Feasible 2–3** | kecilkan lingkup (satu unit, bukan satu dinas) · ganti ke data sekunder · turunkan desain (korelasional, bukan eksperimen) · kurangi n dengan uji non-parametrik · minta ekspor anonim alih-alih akses DB |
| **Interesting 2** | pindahkan locus ke tempat lo punya keterikatan · ubah sudut dari "mengukur" ke "menjelaskan mengapa" |
| **Novel 2–3** | jalankan `literature_probe.py` · tambahkan problematisasi satu domain asumsi · cari moderator (variabel yang menjelaskan pertentangan) · pindah dari "apakah berpengaruh" ke "kapan berpengaruh" |
| **Ethical 2–3** | hilangkan identitas sejak pengumpulan · ganti wawancara pasien dengan wawancara petugas · pakai data agregat · siapkan informed consent tertulis |
| **Relevant 2–3** | wawancara 15 menit dengan calon pengguna hasil · kaitkan ke target Renstra/SOP/SPM · tunjukkan keputusan apa yang akan berubah |

---

## Contoh penilaian

**Kandidat A** — "Pengaruh kualitas data rekap terhadap ketepatan pelaporan gizi di
Puskesmas X"

| Dimensi | Skor | Alasan |
|---|---|---|
| Feasible | 4 | arsip 18 bulan tersedia; izin dinas masih diproses |
| Interesting | 4 | lo bekerja di sana, sudah melihat masalahnya |
| Novel | 3 | ada studi serupa di kota lain, tapi belum ada yang mengukur di kabupaten |
| Ethical | 5 | data agregat, tanpa identitas pasien |
| Relevant | 4 | kepala puskesmas menyatakan akan memakai hasilnya |

```
= (4/5×30) + (4/5×15) + (3/5×20) + (5/5×15) + (4/5×20)
= 24 + 12 + 12 + 15 + 16
= 79  → LAYAK, dimensi terlemah: Novel (3)
```

Perbaikan yang disarankan: jalankan probe literatur, lalu tambahkan problematisasi pada
asumsi "ketepatan waktu = kepatuhan" (domain ontologis). Itu menaikkan Novel ke 4 → total 83.

**Kandidat B** — "Pengaruh digitalisasi terhadap kinerja ASN di Indonesia"

| Dimensi | Skor | Alasan |
|---|---|---|
| Feasible | 1 | butuh data nasional, tidak ada akses |
| Interesting | 3 | |
| Novel | 1 | sangat banyak studi serupa |
| Ethical | 5 | |
| Relevant | 2 | tidak ada pengguna konkret |

```
= 6 + 9 + 4 + 15 + 8 = 42  → GANTI
```

Yang membuatnya gagal bukan ambisi, tapi **tidak bisa dikerjakan oleh satu orang dalam satu
semester**. Itu satu-satunya alasan yang dibutuhkan.

---

## Cara memakai skrip

```bash
python3 scripts/skor_topik.py 03_kandidat.json --out 03_skor_topik.md --ambang 70
```

Skrip:
- menghitung total dengan bobot di atas
- mengurutkan kandidat
- menandai dimensi 0 sebagai **DISKUALIFIKASI**
- mencetak dimensi terlemah + saran perbaikan dari tabel di atas
- gagal (exit 1) bila semua kandidat di bawah ambang — supaya tidak lolos diam-diam

Format `03_kandidat.json`:

```json
{
  "kandidat": [
    {
      "id": "K1",
      "judul_kerja": "...",
      "skor": {"feasible": 4, "interesting": 4, "novel": 3, "ethical": 5, "relevant": 4},
      "catatan": "..."
    }
  ]
}
```

Skor harus bilangan bulat 0–5. Skrip menolak nilai di luar rentang itu, bukan
membulatkannya diam-diam.
