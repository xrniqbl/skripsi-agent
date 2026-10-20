#!/usr/bin/env python3
"""
generate_campus_presets.py — Bangun preset campus_templates/*.json dari tabel data.

Tabel data di file ini adalah satu-satunya tempat nilai gaya dokumen ditulis.
Preset yang dihasilkan dibaca langsung oleh scripts/apply_campus_template.py.

Aturan main sumber data (anti-hafalan):
  - Every campus carries `sumber.status`:
      "pedoman-resmi"  -> angka diambil dari dokumen resmiCampus (umumnya fakultas/program studi).
      "konvensi-umum"  -> belum ada dokumen resmi yang dipakai sebagai rujukan;
                          angka hanya konvensi umum Indonesia dan WAJIB diverifikasi.
  - `sumber.scope` menjelaskan fakultas/tahun asal angka bila sumber tidak berlaku universal.
  - Tidak ada preset yang mengklaim "semua fakultas" bila sumbernya satu fakultas.

Perintah:
    generate_campus_presets.py              tulis ulang semua preset regenerate=True
    generate_campus_presets.py --check      validasi + deteksi DRIFT (keluar 1 bila tidak sinkron)
    generate_campus_presets.py --only unpad  (bang ulang satu preset)
    generate_campus_presets.py --patch      merge gaya/provenance ke preset LAMA
                                            (ugm/ui/itb) tanpa menimpa `struktur`
                                            hasil tulisan tangan. Idempoten.

Catatan nilai:
  - Angka yang tidak tercantum pada dokumen resmi ditulis apa adanya sebagai
    "perlu konfirmasi (bagian X)", bukan ditebak. `validasi()` tetap lolos karena
    nilai berupa string; yang hilang adalah kepastian, bukan kejujuran.
"""

import argparse
import json
import os
import sys

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_PRESET = os.path.join(AKAR, "campus_templates")

# ── Kerangka struktur bersama ────────────────────────────────────────────────
# Mirrors generic.json: frontmatter -> BAB I -> BAB II -> BAB III -> backmatter.
# Subbab `cek` memakai kunci yang dikenali scripts/apply_campus_template.py (CEK).
STRUKTUR = [
    {
        "id": "frontmatter",
        "judul": "Halaman Depan",
        "wajib": True,
        "wadah": True,
        "subbab": [
            {
                "judul": "Halaman Judul",
                "wajib": True,
                "catatan": "Judul, nama, NIM, pembimbing, program studi, fakultas, tahun",
            },
            {
                "judul": "Lembar Persetujuan",
                "wajib": True,
                "catatan": "Tanda tangan pembimbing, dekan/gubernur fakultas",
            },
            {
                "judul": "Pernyataan Keaslian",
                "wajib": True,
                "catatan": "Pernyataan naskah orisinal dan tidak plagiat",
            },
            {"judul": "Kata Pengantar", "wajib": False},
            {"judul": "Abstrak", "wajib": False},
        ],
    },
    {
        "id": "bab1",
        "judul": "BAB I PENDAHULUAN",
        "wajib": True,
        "subbab": [
            {
                "judul": "Latar Belakang Masalah",
                "wajib": True,
                "cek": ["latar_belakang", "data_empat_lapisan", "celah_penelitian"],
            },
            {"judul": "Rumusan Masalah", "wajib": True, "cek": ["rumusan_masalah"]},
            {"judul": "Tujuan Penelitian", "wajib": True, "cek": ["tujuan"]},
            {"judul": "Manfaat Penelitian", "wajib": True, "cek": ["manfaat"]},
            {"judul": "Batasan Masalah", "wajib": True, "cek": ["batasan"]},
        ],
    },
    {
        "id": "bab2",
        "judul": "BAB II TINJAUAN PUSTAKA",
        "wajib": True,
        "subbab": [
            {"judul": "Landasan Teori", "wajib": True},
            {"judul": "Hubungan Antarvariabel", "wajib": True},
            {
                "judul": "Penelitian Terdahulu yang Relevan",
                "wajib": True,
                "cek": ["tabel_penelitian_terdahulu", "celah_penelitian"],
            },
            {"judul": "Kerangka Berpikir", "wajib": True},
            {
                "judul": "Hipotesis",
                "wajib": False,
                "catatan": "Wajib untuk rancangan kuantitatif hipotesis",
            },
        ],
    },
    {
        "id": "bab3",
        "judul": "BAB III METODE PENELITIAN",
        "wajib": True,
        "subbab": [
            {"judul": "Desain Penelitian", "wajib": True, "cek": ["desain_penelitian"]},
            {
                "judul": "Populasi dan Sampel",
                "wajib": True,
                "cek": ["populasi_sampel", "teknik_sampel", "perhitungan_sampel"],
            },
            {"judul": "Variabel Penelitian", "wajib": True},
            {"judul": "Definisi Operasional Variabel", "wajib": True},
            {"judul": "Skala Pengukuran", "wajib": True, "cek": ["skala_likert"]},
            {
                "judul": "Teknik Pengumpulan Data",
                "wajib": True,
                "cek": ["instrumen_validitas_reliabilitas"],
            },
            {
                "judul": "Teknik Analisis Data",
                "wajib": True,
                "cek": ["uji_statistik_cocok", "hasil_uji_tabel"],
            },
        ],
    },
    {
        "id": "backmatter",
        "judul": "Bagian Akhir",
        "wajib": True,
        "wadah": True,
        "subbab": [
            {
                "judul": "Daftar Pustaka",
                "wajib": True,
                "cek": ["semua_penanda_terdaftar"],
            },
            {"judul": "Lampiran", "wajib": True},
        ],
    },
]

KELENGKAPAN_DASAR = [
    "halaman judul",
    "lembar persetujuan",
    "pernyataan keaslian",
    "kata pengantar",
    "daftar isi",
    "daftar tabel",
    "daftar gambar",
    "daftar singkatan",
    "abstrak (inti sari) bahasa Indonesia",
    "abstrak bahasa Inggris",
    "BAB I Pendahuluan",
    "BAB II Tinjauan Pustaka",
    "BAB III Metode Penelitian",
    "BAB IV Hasil dan Pembahasan",
    "BAB V Kesimpulan dan Saran",
    "daftar pustaka",
    "lampiran (instrumen, data, izin penelitian)",
]

# Konvensi umum Indonesia yang dipakai bila dokumen resmi belum dipakai sebagai rujukan.
KONVENSI_MARGIN = {"atas": "4 cm", "bawah": "3 cm", "kiri": "4 cm", "kanan": "3 cm"}
KONVENSI_GAYA = {
    "ukuran_halaman": "A4",
    "margin": dict(KONVENSI_MARGIN),
    "font_isi": "Times New Roman 12 pt",
    "font_judul": "Times New Roman 14 pt tebal",
    "spasi": "1.5",
    "rata_kanan_kiri": "justify",
    "penomoran_halaman": "bagian awal angka romawi kecil, bagian inti angka arab, di tengah bawah",
    "nomor_bab": "BAB I, BAB II, BAB III",
}


def konvensi(campus, nama, singkat, sumber_catatan, **gaya):
    """Preset tanpa rujukan dokumen resmi: angka = konvensi umum, wajib diverifikasi."""
    g = dict(KONVENSI_GAYA)
    g.update(gaya)
    return {
        "kampus": nama,
        "singkat": singkat,
        "jenjang": ["skripsi", "thesis", "disertasi"],
        "verifikasi": (
            "Preset ini BELUM diverifikasi ke pedoman resmi. Angka format berasal dari "
            f"konvensi umum penulisan Indonesia, bukan dari dokumen {nama}. "
            "Selalu cocokkan dengan pedoman resmi fakultas/program studi Anda sebelum submit."
        ),
        "sumber": {
            "status": "konvensi-umum",
            "dokumen": None,
            "url": None,
            "scope": "seluruh kampus (perlu konfirmasi)",
            "catatan": sumber_catatan,
        },
        "gaya_dokumen": g,
        "sitasi": "APA 7",
        "daftar_pustaka": 'heading "DAFTAR PUSTAKA" di halaman baru',
        "kelengkapan": list(KELENGKAPAN_DASAR),
        "struktur": STRUKTUR,
    }


def resmi(campus, nama, singkat, dokumen, url, scope, tahun, catatan, gaya, sitasi="APA 7",
          kelengkapan_tambahan=None):
    """Preset dengan angka dari dokumen resmi; scope menjelaskan cakupan fakultas/tahun."""
    kel = list(KELENGKAPAN_DASAR)
    if kelengkapan_tambahan:
        kel.extend(kelengkapan_tambahan)
    return {
        "kampus": nama,
        "singkat": singkat,
        "jenjang": ["skripsi", "thesis", "disertasi"],
        "verifikasi": (
            f"Angka format diambil dari {dokumen} ({scope}). Pedoman ini berlaku untuk "
            f"fakultas/program studi tersebut; fakultas lain di {nama} dapat berbeda. "
            "Cocokkan dengan pedoman unit Anda sebelum submit."
        ),
        "sumber": {
            "status": "pedoman-resmi",
            "dokumen": dokumen,
            "url": url,
            "scope": scope,
            "tahun": tahun,
            "catatan": catatan,
        },
        "gaya_dokumen": gaya,
        "sitasi": sitasi,
        "daftar_pustaka": 'heading "DAFTAR PUSTAKA" di halaman baru',
        "kelengkapan": kel,
        "struktur": STRUKTUR,
    }


# ── Tabel data preset ────────────────────────────────────────────────────────
# Kolom kunci tiap entri: file, preset(dict), regenerate(bool).
# regenerate=True  -> file dibuat/di-timpa oleh generator ini.
# regenerate=False -> file ada di repo (mis. ugm/ui/uny/itb/generic/custom),
#                    tidak ditulis ulang oleh generator.

def gaya(margin=None, font_isi=None, font_judul=None, spasi=None, penomoran=None,
         nomor_bab=None, ukuran_halaman="A4", rata="justify", align=None):
    g = {
        "ukuran_halaman": ukuran_halaman,
        "margin": margin or dict(KONVENSI_MARGIN),
        "font_isi": font_isi or "Times New Roman 12 pt",
        "font_judul": font_judul or "Times New Roman 14 pt tebal",
        "spasi": spasi or "1.5",
        "rata_kanan_kiri": rata,
        "penomoran_halaman": penomoran or "bagian awal angka romawi kecil, bagian inti angka arab, di tengah bawah",
        "nomor_bab": nomor_bab or "BAB I, BAB II, BAB III",
    }
    if align:
        g["catatan_tambahan"] = align
    return g


PRESETS = {}


def daftarkan(nama_file, preset, regenerate=True):
    PRESETS[nama_file] = {"preset": preset, "regenerate": regenerate}


# ── 1. IPB ──────────────────────────────────────────────────────────────────
daftarkan(
    "ipb",
    resmi(
        "ipb",
        "Institut Pertanian Bogor",
        "IPB",
        "Peraturan Rektor IPB No. 27/IT3/PP/2019 tentang Pedoman Penulisan Karya "
        "Ilmiah Tugas Akhir Mahasiswa IPB (PPKI)",
        "https://fapet.ipb.ac.id/~pascafapet/dokumen/pedoman_penulisan_karya_ilmiah.pdf",
        "UNIVERSITAS IPB - peraturan rektor, berlaku lintas fakultas/program studi",
        2019,
        "Menggantikan PERREKTOR No. 9/IT3/LT/2012. Hak cipta karya ilmiah menjadi milik "
        "IPB. Abstrak wajib diterjemahkan ke bahasa Inggris (kecuali laporan akhir D-3). "
        "ANGKA SPASI DAN MARGIN ada di Bab III dan lampiran dokumen, tidak tercantum "
        "pada halaman rujukan - mohon periksa lampiran pedoman asli.",
        gaya(
            margin={"atas": "perlu konfirmasi (Bab III / lampiran PPKI)",
                    "bawah": "perlu konfirmasi", "kiri": "perlu konfirmasi",
                    "kanan": "perlu konfirmasi"},
            spasi="perlu konfirmasi (Bab III / lampiran PPKI)",
            penomoran="ringkasan dan summary memakai angka romawi kecil",
            align="Mengikuti KBBI dan PUEBI edisi terbaru. Ringkasan maksimal 2 halaman, "
                  "1 spasi, kata kunci maksimal 5 kata dengan huruf awal besar. Memuat "
                  "halaman hak cipta, halaman judul dalam, dan halaman tim penguji.",
        ),
        sitasi="Sesuai Bab VII PPKI IPB - periksa lampiran pedoman",
        kelengkapan_tambahan=["halaman hak cipta", "halaman judul dalam",
                              "halaman tim penguji", "ringkasan", "summary"],
    ),
)

# ── 2. UNAIR (Fakultas Vokasi 2025) ──────────────────────────────────────────
daftarkan(
    "unair",
    resmi(
        "unair",
        "Universitas Airlangga",
        "UNAIR",
        "Buku Panduan Skripsi dan TA Fakultas Vokasi",
        "https://vokasi.unair.ac.id/wp-content/uploads/2025/09/Buku-Panduan-Skripsi-dan-TA-Fakultas-Vokasi-Tahun-2025_opt.pdf",
        "Fakultas Vokasi, Universitas Airlangga (tahun 2025)",
        2025,
        "Fakultas Vokasi; fakultas lain UNAIR dapat punya ketentuan berbeda.",
        gaya(
            margin={"atas": "4 cm", "bawah": "3 cm", "kiri": "4 cm", "kanan": "3 cm"},
            spasi="2",
            penomoran="bagian awal romawi kecil, bagian inti arab, di tengah bawah",
            align="Spasi ganda; abstrak/daftar pustaka dapat 1 spasi. Judul cover 16 pt tebal.",
        ),
    ),
)

# ── 3. UB (Fakultas Teknik 2016) ─────────────────────────────────────────────
daftarkan(
    "ub",
    resmi(
        "ub",
        "Universitas Brawijaya",
        "UB",
        "Panduan Penulisan Skripsi, Tesis dan Disertasi Fakultas Teknik UB",
        "https://industri.ub.ac.id/wp-content/uploads/2023/10/Pedoman-skripsi-FT-UB.pdf",
        "Fakultas Teknik, Universitas Brawijaya (pedoman 2016)",
        2016,
        "Fakultas Teknik; fakultas lain UB dapat punya ketentuan berbeda.",
        gaya(
            margin={"atas": "2,5 cm (4 cm untuk awal bab)", "bawah": "2,5 cm",
                    "kiri": "3 cm (mirror/inside)", "kanan": "2,5 cm (mirror/outside)"},
            spasi="1.5",
            penomoran="bagian awal romawi kecil di tengah bawah; bagian inti/akhir arab di luar atas",
            align="Menggunakan mirror margin: sisi dalam 3 cm, sisi luar 2,5 cm.",
        ),
        kelengkapan_tambahan=["ringkasan (bahasa Indonesia)", "summary (bahasa Inggris)",
                              "lembar orisinalitas", "lembar peruntukan"],
    ),
)

# ── 4. ITS (Fakultas Teknik Industri 2021) ────────────────────────────────────
daftarkan(
    "its",
    resmi(
        "its",
        "Institut Teknologi Sepuluh Nopember",
        "ITS",
        "Pedoman Penyusunan Tugas Akhir Fakultas Teknik Industri ITS",
        "https://www.its.ac.id/tmi/wp-content/uploads/sites/51/2022/02/DRAFT-PEDOMAN-PENYUSUNAN-TUGAS-AKHIR-2021.pdf",
        "Fakultas Teknik Industri, ITS (pedoman 2021)",
        2021,
        "Fakultas Teknik Industri; fakultas/prodi lain ITS dapat punya ketentuan berbeda.",
        gaya(
            margin={"atas": "3,0 cm", "bawah": "2,5 cm", "kiri": "3,0 cm", "kanan": "2,0 cm"},
            spasi="1",
            penomoran="bagian awal romawi kecil, bagian inti/akhir arab, di footer kanan",
            align="Kertas HVS 80 g A4; judul bab huruf besar tebal, nomor bab romawi.",
        ),
    ),
)

# ── 5. UNDIP ────────────────────────────────────────────────────────────────
daftarkan(
    "undip",
    resmi(
        "undip",
        "Universitas Diponegoro",
        "UNDIP",
        "Buku Saku Pedoman Penulisan Skripsi Fakultas Perikanan dan Ilmu Kelautan "
        "(FPIK) UNDIP",
        "https://dpt.undip.ac.id/wp-content/uploads/2022/11/Buku-Saku-Pedoman-Skripsi-FPIK-2021.pdf",
        "FPIK UNDIP (edisi 2021); dikonfirmasi pula oleh FPP UNDIP",
        2021,
        "CATATAN PENTING: FPIK UNDIP memberi NOMOR BAB dengan ANGKA ARAB (1, 2, 3), "
        "berbeda dari UGM, UI, dan UMY yang memakai angka Romawi. Margin atas 3 cm, "
        "bukan 4 cm.",
        gaya(
            margin={"atas": "3 cm", "bawah": "3 cm", "kiri": "4 cm", "kanan": "3 cm"},
            spasi="1.5",
            penomoran="nomor bab memakai ANGKA ARAB; nomor halaman 2 cm dari tepi kanan",
            align="1 spasi untuk abstrak, daftar isi/tabel/gambar/lampiran, isi tabel, "
                  "dan daftar pustaka. Judul bab dan subbab bold kapital. "
                  "Alinea baru 1,25 cm (1 tab).",
        ),
        kelengkapan_tambahan=["pernyataan orisinalitas", "halaman tim penguji"],
    ),
)

# ── 6. UNPAD (FISIP/FTIP/Farmasi) ────────────────────────────────────────────
daftarkan(
    "unpad",
    resmi(
        "unpad",
        "Universitas Padjadjaran",
        "UNPAD",
        "Pedoman Penyusunan dan Penulisan Skripsi (FISIP / FTIP / Fakultas Farmasi)",
        "https://ipol.fisip.unpad.ac.id/wp-content/uploads/2023/03/Pedoman-Skripsi.pdf",
        "Fakultas FISIP, FTIP, dan Farmasi, Universitas Padjadjaran",
        2023,
        "Ketiga fakultas tersebut konsisten: margin 4/4/3/3 cm, TNR 12, spasi 2. "
        "Fakultas lain Unpad dapat berbeda.",
        gaya(
            margin={"atas": "4 cm", "bawah": "3 cm", "kiri": "4 cm", "kanan": "3 cm"},
            spasi="2",
            penomoran="bagian awal romawi kecil di luar atas; bagian inti/akhir arab",
            align="Abstrak, judul tabel/gambar, dan daftar pustaka 1 spasi. Judul bab 14 pt tebal.",
        ),
    ),
)

# ── 7. UNHAS ────────────────────────────────────────────────────────────────
daftarkan(
    "unhas",
    resmi(
        "unhas",
        "Universitas Hasanuddin",
        "UNHAS",
        "Pedoman Penulisan Tugas Akhir Mahasiswa di Lingkup Universitas Hasanuddin, "
        "Keputusan Rektor UNHAS No. 10438/UN4.1/KEP/2023",
        "https://peternakan.unhas.ac.id/wp-content/uploads/2024/09/32-Pedoman-Penulisan_Tugas_Akhir_Skripsi-Tesis-Disertasi-2023.pdf",
        "UNIVERSITAS HASANUDDIN - keputusan rektor, berlaku lintas fakultas",
        2023,
        "BEDA BESAR DARI KAMPUS LAIN: (1) memakai kertas B5 176 x 250 mm (format buku), "
        "BUKAN A4; (2) bab berbasis publikasi (publication-based) sesuai "
        "Permendikbudristek 53/2023, hasil publikasi menjadi unsur utama; (3) struktur "
        "bab Pendahuluan, Metode, Hasil, Pembahasan, dan Kesimpulan. Margin atas dan "
        "bawah 22,5 mm pada halaman judul. Font dan spasi perlu diperiksa di Bab V.",
        gaya(
            ukuran_halaman="B5 (176 x 250 mm) - format buku, bukan A4",
            margin={"atas": "2,25 cm (22,5 mm, halaman judul)", "bawah": "2,25 cm (22,5 mm)",
                    "kiri": "simetris terhadap teks", "kanan": "simetris terhadap teks"},
            spasi="perlu konfirmasi (Bab V.1.6)",
            penomoran="daftar isi otomatis; kata kunci memakai huruf abjad dan italic",
            align="Sampul seragam untuk semua fakultas: skripsi merah, tesis biru langit, "
                  "disertasi putih. Abstrak wajib ada. Daftar istilah, singkatan, dan "
                  "simbol dilampirkan.",
        ),
        kelengkapan_tambahan=["daftar istilah/singkatan/simbol", "abstrak (wajib)"],
    ),
)

# ── 8. Telkom University ─────────────────────────────────────────────────────
daftarkan(
    "telu",
    resmi(
        "telu",
        "Telkom University",
        "TEL-U",
        "Sistematika dan Tata Cara Penulisan Tugas Akhir Fakultas Ekonomi dan Bisnis, "
        "Universitas Telkom",
        "https://mm.telkomuniversity.ac.id/wp-content/uploads/2017/03/Pedoman-Tugas-Akhir-FEB-Februari-2015.pdf",
        "Fakultas Ekonomi dan Bisnis, Telkom University (pedoman Februari 2015)",
        2015,
        "Pedoman spesifik FEB; fakultas lain Telkom University dapat berbeda. Dokumen "
        "menyebut pedoman lengkap akan diperbarui setelah prosedur taskskripsi selesai "
        "disahkan - periksa versi terbaru dari unit Anda.",
        gaya(
            margin={"atas": "3 cm", "bawah": "3 cm",
                    "kiri": "4 cm (termasuk 1 cm penjilidan)", "kanan": "3 cm"},
            spasi="1.5",
            penomoran="nomor bab ditulis lengkap dengan kata BAB dan angka Arab "
                       "(contoh: BAB 1 PENDAHULUAN)",
            align="Rata kiri-kanan (justify). Paragraf baru indent 5 karakter. "
                  "Daftar pustaka 1 spasi dengan hanging indent 5 karakter, urutan "
                  "alphabetis. Setiap bab dimulai pada halaman ganjil.",
        ),
        sitasi="APA (Publication Manual edisi ke-6 atau terbaru) - disebut eksplisit di pedoman",
        kelengkapan_tambahan=["daftar istilah (lampiran)"],
    ),
)

# ── 9. BINUS ─────────────────────────────────────────────────────────────────
daftarkan(
    "binus",
    konvensi(
        "binus",
        "BINUS University",
        "BINUS",
        "BINUS tidak menyediakan satu link PDF publik yang konsisten untuk seluruh "
        "program studi. Preset ini dicatat sebagai konvensi umum (TNR 12, spasi 1.5–2.0, "
        "margin 4/4/3/3) — WAJIB cek pedoman resmi prodi Anda sebelum digunakan.",
    ),
)

# ── 10. UMY ─────────────────────────────────────────────────────────────────
daftarkan(
    "umy",
    resmi(
        "umy",
        "Universitas Muhammadiyah Yogyakarta",
        "UMY",
        "Pedoman Penulisan Usulan Penelitian, Skripsi dan Publikasi Karya Ilmiah, "
        "Fakultas Ekonomi dan Bisnis UMY (berdasar Keputusan Rektor UMY "
        "No. 217/SK-UMY/X/2017)",
        "https://ipief.umy.ac.id/wp-content/uploads/2020/10/PEDOMAN_PENULISAN_USULAN_PENELITIAN.pdf",
        "Fakultas Ekonomi dan Bisnis UMY, mengacu pada SK Rektor UMY 217/SK-UMY/X/2017",
        2017,
        "Buku panduan ini diterbitkan FEB UMY tetapi merujuk peraturan rektor UMY "
        "tingkat universitas. ANGKA MARGIN tidak tercantum pada halaman rujukan - "
        "wajib periksa bagian batas pengetikan pada pedoman asli.",
        gaya(
            margin={"atas": "perlu konfirmasi (pedoman FEB UMY)",
                    "bawah": "perlu konfirmasi",
                    "kiri": "perlu konfirmasi", "kanan": "perlu konfirmasi"},
            spasi="2",
            penomoran="bagian awal angka romawi kecil; bagian isi angka Arab",
            align="1 spasi untuk intisari, kutipan langsung, judul tabel dan gambar lebih "
                  "dari satu baris, serta daftar pustaka. Daftar pustaka memakai hanging "
                  "indent 7 karakter dengan jarak antar sumber 2 spasi. Deteksi plagiasi "
                  "mengikuti bab V SK Rektor UMY.",
        ),
    ),
)

# ── 11. UII ──────────────────────────────────────────────────────────────────
daftarkan(
    "uii",
    resmi(
        "uii",
        "Universitas Islam Indonesia",
        "UII",
        "Panduan Penulisan Tugas Akhir Fakultas Ilmu Farmasi dan Ilmu Gizi, "
        "Universitas Islam Indonesia (TA 2017 Rev 1)",
        "https://science.uii.ac.id/wp-content/uploads/panduan-TA-2017-Rev1-Fix-Farmasi.pdf",
        "Fakultas Ilmu Farmasi dan Ilmu Gizi UII (pedoman 2017 Rev 1)",
        2017,
        "Struktur halaman UII mengikuti pedoman UI 2017. Dokumen aslinya memakai margin "
        "atas 4 cm pada halaman pengesahan, sedangkan naskah badan memakai 3 cm; "
        "perbedaan itu memang ada di dalam pedoman.",
        gaya(
            margin={"atas": "3 cm (naskah badan); 4 cm pada halaman pengesahan",
                    "bawah": "3 cm", "kiri": "4 cm", "kanan": "3 cm"},
            spasi="1.5",
            penomoran="bagian awal angka romawi kecil; bagian isi angka Arab",
            align="Keterangan tabel dan gambar memakai TNR 10. 1 spasi untuk intisari, "
                  "abstract, daftar pustaka, isi tabel, serta judul tabel atau gambar "
                  "lebih dari satu baris. Alinea baru mulai setelah ketukan ke-6 dari tepi "
                  "kiri. Ada panduan khusus penulisan bahasa Arab.",
        ),
    ),
)

# ── 12. UAD ──────────────────────────────────────────────────────────────────
daftarkan(
    "uad",
    resmi(
        "uad",
        "Universitas Ahmad Dahlan",
        "UAD",
        "Pedoman Penyusunan Skripsi Fakultas Hukum UAD (2018), dikonfirmasi Panduan "
        "Penulisan Laporan Tugas Akhir FMIPA UAD (Edisi 2.1)",
        "https://law.uad.ac.id/wp-content/uploads/Pedoman-Penyusunan-Skripsi-new-Copy-review.pdf",
        "Fakultas Hukum UAD (2018) dan Fakultas MIPA UAD (edisi 2.1)",
        2018,
        "Kedua fakultas konsisten: TNR 12 dan spasi 2. ANGKA MARGIN tidak tercantum "
        "pada halaman rujukan - wajib periksa bagian batas tepi pada pedoman asli.",
        gaya(
            margin={"atas": "perlu konfirmasi (bagian batas tepi pedoman UAD)",
                    "bawah": "perlu konfirmasi", "kiri": "perlu konfirmasi",
                    "kanan": "perlu konfirmasi"},
            spasi="2",
            penomoran="bagian awal angka romawi kecil di bawah tengah; nomor bab memakai "
                       "angka Romawi kapital",
            align="FMIPA memberi tabel spasi rinci (judul bab 1 spasi dengan 6 pt setelah; "
                  "baris pertama paragraf 3 spasi). 1 spasi untuk abstrak, kutipan "
                  "langsung, dan daftar pustaka. Isi tabel dan judul gambar memakai 11. "
                  "Kata kunci maksimal 5 kata italic. Judul skripsi TNR 14 kapital.",
        ),
    ),
)

# ── 13. UMS ──────────────────────────────────────────────────────────────────
daftarkan(
    "ums",
    resmi(
        "ums",
        "Universitas Muhammadiyah Surakarta",
        "UMS",
        "Buku Pedoman Penulisan Skripsi Program Studi Manajemen, Fakultas Ekonomi dan "
        "Bisnis UMS",
        "https://manajemen.ums.ac.id/wp-content/uploads/sites/29/2017/12/BUKU-PEDOMAN-SKRIPSI-MANAJEMEN.pdf",
        "Program Studi Manajemen, Fakultas Ekonomi dan Bisnis UMS",
        2017,
        "Pedoman spesifik prodi Manajemen FEB; prodi atau fakultas lain di UMS dapat "
        "berbeda. Margin tepi atas dan tepi kiri 4 cm, tepi bawah dan tepi kanan 3 cm.",
        gaya(
            margin={"atas": "4 cm", "bawah": "3 cm", "kiri": "4 cm", "kanan": "3 cm"},
            spasi="2",
            penomoran="bagian awal angka romawi kecil di bawah tengah; bagian isi dan "
                       "akhir angka Arab 1,5 cm di kanan atas, kecuali halaman awal bab",
            align="Kertas HVS A4 atau kuarto 70-80 gram, cetak satu muka. 1 spasi untuk "
                  "abstrak, kutipan langsung, judul tabel, judul gambar, dan daftar "
                  "pustaka. Rata kanan-kiri (justify). Alinea baru mulai spasi ke-7.",
        ),
    ),
)

# ── 14. UDINUS ───────────────────────────────────────────────────────────────
daftarkan("udinus", konvensi(
    "udinus", "Universitas Dian Nusantara", "UDINUS",
    "Ambil Panduan Penulisan Skripsi resmi Udinus."))

# ── 15. UMM ──────────────────────────────────────────────────────────────────
daftarkan(
    "umm",
    resmi(
        "umm",
        "Universitas Muhammadiyah Malang",
        "UMM",
        "Pedoman Penulisan Tugas Akhir Fakultas Psikologi Universitas Muhammadiyah "
        "Malang (Edisi 2023)",
        "https://tp.umm.ac.id/wp-content/uploads/2024/12/PEDOMAN-Tugas-Akhir-SEP-2023.pdf",
        "Fakultas Psikologi UMM (2023)",
        2023,
        "Pedoman FPP UMM 2023: TNR 12, spasi 1.5 (umum), abstrak/daftar pustaka 1 spasi, "
        "penomoran bab angka Arab (1,2,3), halaman awal romawi kecil di tengah bawah, "
        "bagian inti angka Arab kanan atas (kecuali awal bab tengah bawah). Margin "
        "atas 4 cm, bawah 3 cm, kiri 4 cm, kanan 3 cm.",
        gaya(
            margin={"atas": "4 cm", "bawah": "3 cm", "kiri": "4 cm", "kanan": "3 cm"},
            spasi="1.5",
            penomoran="bagian awal angka romawi kecil; bagian isi angka Arab",
            align="Abstrak, daftar isi/tabel/gambar/lampiran, isi tabel, keterangan tabel/gambar, "
                  "dan daftar pustaka 1 spasi. Paragraf baru 3 spasi (menurut pedoman). "
                  "Hanging indent daftar pustaka, minimal 25 pustaka (80% jurnal).",
        ),
    ),
)

# ── 16. UMB ──────────────────────────────────────────────────────────────────
daftarkan(
    "umb",
    resmi(
        "umb",
        "Universitas Mercu Buana",
        "UMB",
        "Pedoman Penulisan Karya Ilmiah Skripsi Program Studi Manajemen, Fakultas "
        "Ekonomi Universitas Mercu Buana Yogyakarta",
        "https://fe.mercubuana-yogya.ac.id/storage/uploads/2024/05/panduan-skripsi.pdf",
        "Fakultas Ekonomi UMB Yogyakarta (2023/2024)",
        2024,
        "Pedoman dari UMB Yogyakarta (FE Manajemen). Kampus UMB Jakarta berbeda; "
        "preset ini berlaku untuk FE UMB Yogyakarta. Margin kiri dan atas 4 cm, kanan "
        "dan bawah 3 cm. Spasi 2, TNR 12, justify.",
        gaya(
            margin={"atas": "4 cm", "bawah": "3 cm", "kiri": "4 cm", "kanan": "3 cm"},
            spasi="2",
            penomoran="halaman awal angka Romawi (i, ii, iii...) di bawah tengah; "
                       "halaman utama angka Arab (1,2,3...) kanan atas, kecuali halaman bab "
                       "baru di bawah tengah",
            align="Abstrak 1 spasi, daftar pustaka 1 spasi antar baris dengan hanging "
                  "indent 6 ketukan, tabel isi 1 spasi. TNR 12.",
        ),
    ),
)

# ── 17. Gunadarma ────────────────────────────────────────────────────────────
daftarkan("gunadarma", konvensi(
    "gunadarma", "Universitas Gunadarma", "GUNADARMA",
    "Ambil Pedoman Penulisan Skripsi resmi Universitas Gunadarma."))

# ── 18. UPN Veteran Yogyakarta ───────────────────────────────────────────────
daftarkan("upn_veteran", konvensi(
    "upn_veteran", "Universitas Pembangunan Nasional Veteran Yogyakarta", "UPNV",
    "Kampus Bela Negara di Yogyakarta; ambil pedoman penulisan resmi UPNV."))

# ── 19. UPN Veteran Jakarta ──────────────────────────────────────────────────
daftarkan("upnvj", konvensi(
    "upnvj", "Universitas Pembangunan Nasional Veteran Jakarta", "UPNVJ",
    "PTN (kampus Pondok Labu, Jakarta Selatan + Kampus Limo, Depok); "
    "ambil pedoman penulisan resmi UPN Veteran Jakarta."))

# ── 20. UPN Veteran Jawa Timur ───────────────────────────────────────────────
daftarkan("upnv_jatim", konvensi(
    "upnv_jatim", "Universitas Pembangunan Nasional Veteran Jawa Timur", "UPNV JATIM",
    "PTN di Surabaya; ambil pedoman penulisan resmi UPN Veteran Jawa Timur."))

# ── 21. Universitas Budi Luhur ───────────────────────────────────────────────
daftarkan("budi_luhur", konvensi(
    "budi_luhur", "Universitas Budi Luhur", "UBL",
    "Ambil Panduan Penulisan Skripsi resmi Universitas Budi Luhur."))

# ── 22. UMN (Universitas Multimedia Nusantara, Kelapa Dua/Tangerang) ──────────
daftarkan(
    "umn",
    resmi(
        "umn",
        "Universitas Multimedia Nusantara",
        "UMN",
        "Panduan Skripsi Program Studi Kajian (Fakultas Komunikasi dan Penyiaran) UMN",
        "https://www.umn.ac.id/wp-content/uploads/2021/04/Panduan-Skripsi-Kajian-2017_Final.pdf",
        "Program Studi Kajian, FKP UMN (pedoman 2017); dikuatkan Panduan FIKOM & MMT UMN",
        2017,
        "Margin 4/3/4/3 cm + spasi 2 + TNR 12 konsisten di Kajian, FIKOM, dan MMT UMN. "
        "Pengecualian: Program Studi Teknik Elektro UMN "
        "(https://te.umn.ac.id/wp-content/uploads/2020/08/PANDUAN-TEKNIS-SKRIPSI-TE.pdf) "
        "mengatur margin atas 3 cm dan MEWAJIBKAN daftar pustaka gaya IEEE.",
        gaya(
            margin={"atas": "4 cm", "bawah": "3 cm", "kiri": "4 cm", "kanan": "3 cm"},
            spasi="2",
            penomoran="bagian awal romawi kecil di tengah bawah (1,5 cm dari tepi bawah); "
                       "bagian inti/akhir arab di kanan bawah",
            align="Spasi ganda; 1 spasi untuk kutipan panjang, abstrak, tabel, gambar, "
                  "daftar pustaka. Judul bab TNR 12 (Kajian) atau 14-16 (FIKOM/MMT). "
                  "Judul skripsi maksimal 15 kata (TE).",
        ),
        sitasi="IEEE (wajib pada Program Studi Teknik Elektro); fakultas lain dapat berbeda — verifikasi",
        kelengkapan_tambahan=["daftar grafik", "lembar pernyataan (tidak plagiat)"],
    ),
)


# ── CLI & IO ─────────────────────────────────────────────────────────────────

def validasi(path, isi):
    """Pastikan JSON punya kunci wajib + provenance."""
    wajib = ["kampus", "singkat", "jenjang", "verifikasi", "gaya_dokumen",
             "sitasi", "kelengkapan", "struktur"]
    hilang = [k for k in wajib if k not in isi]
    if hilang:
        raise ValueError(f"{path}: kunci hilang {hilang}")
    if "sumber" not in isi:
        raise ValueError(f"{path}: field `sumber` (provenance) wajib ada")
    st = isi["sumber"].get("status")
    if st not in ("pedoman-resmi", "konvensi-umum"):
        raise ValueError(f"{path}: sumber.status tak dikenal: {st!r}")
    if st == "pedoman-resmi" and not isi["sumber"].get("url"):
        raise ValueError(f"{path}: status pedoman-resmi wajib punya url")
    # struktur minimal untuk check
    if not any(b.get("id") == "bab1" for b in isi["struktur"]):
        raise ValueError(f"{path}: struktur tanpa blok bab1")


def backfill_sumber():
    """Tambahkan field `sumber` (konvensi-umum) ke preset lama yang belum punya.

    Tidak menyentuh field lain, jadi isi hand-written preset ugm/ui/uny/itb/
    generic/custom tetap utuh. Idempoten.
    """
    berubah = []
    for f in sorted(os.listdir(DIR_PRESET)):
        if not f.endswith(".json"):
            continue
        path = os.path.join(DIR_PRESET, f)
        with open(path, encoding="utf-8") as fh:
            isi = json.load(fh)
        if isi.get("sumber"):
            continue
        isi["sumber"] = {
            "status": "konvensi-umum",
            "dokumen": None,
            "url": None,
            "scope": "seluruh kampus (perlu konfirmasi)",
            "catatan": "Preset lama, disusun dari kebiasaan umum penulisan ilmiah; "
                       "belum diverifikasi ke pedoman resmi fakultas/program studi.",
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(isi, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        berubah.append(f)
    return berubah


def patch_legacy():
    """Perbarui gaya_dokumen/sitasi/sumber pada preset lama TANPA menyentuh `struktur`.

    Preset ugm/ui/itb/uny/generic/custom sebelumnya ditulis tangan dan `struktur`-nya
    sudah dipakai sebagai acuan; generator tidak boleh menimpanya. `--patch` hanya
    merge field gaya + provenance, jadi blok bab tambahan tetap utuh. Idempoten.
    """
    berubah = []
    for nama_file, patch in sorted(PATCH_LEGACY.items()):
        path = os.path.join(DIR_PRESET, f"{nama_file}.json")
        if not os.path.exists(path):
            print(f"  LEWATI  {nama_file}.json tidak ada")
            continue
        with open(path, encoding="utf-8") as fh:
            isi = json.load(fh)
        sebelum = json.dumps(isi, sort_keys=True, ensure_ascii=False)
        isi["gaya_dokumen"] = patch["gaya_dokumen"]
        isi["sitasi"] = patch["sitasi"]
        isi["sumber"] = patch["sumber"]
        isi["verifikasi"] = patch["verifikasi"]
        if patch.get("daftar_pustaka"):
            isi["daftar_pustaka"] = patch["daftar_pustaka"]
        if patch.get("kelengkapan_tambahan"):
            ada = set(isi.get("kelengkapan", []))
            for k in patch["kelengkapan_tambahan"]:
                if k not in ada:
                    isi.setdefault("kelengkapan", []).append(k)
                    ada.add(k)
        validasi(nama_file, isi)
        sesudah = json.dumps(isi, sort_keys=True, ensure_ascii=False)
        if sebelum != sesudah:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(isi, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            berubah.append(nama_file)
        else:
            print(f"  TIDAK BERUBAH  {nama_file}.json")
    return berubah


# ── Patch untuk preset lama (struktur tetap, gaya + provenance di-update) ─────
# Patch dipakai oleh `generate_campus_presets.py --patch`.
# Hanya field gaya_dokumen/sitasi/daftar_pustaka/kelengkapan/sumber/verifikasi
# yang di-merge; `struktur` hasil tulisan tangan tidak pernah ditimpa.
PATCH_LEGACY = {}

# ── UGM ──────────────────────────────────────────────────────────────────────
# Divergent antar fakultas; nilai dasar memakai FKH (2024).
PATCH_LEGACY["ugm"] = {
    "gaya_dokumen": gaya(
        ukuran_halaman="A4 (kuarto 21 x 28 cm)",
        margin={"atas": "4 cm", "bawah": "3 cm", "kiri": "4 cm", "kanan": "3 cm"},
        spasi="2",
        penomoran="bagian awal angka romawi kecil di tengah bawah; bagian inti angka arab "
                   "di tengah bawah (2 cm dari tepi bawah)",
        align="FKH: spasi ganda, abstrak/daftar pustaka 1 spasi, abstrak maks 300 kata, "
              "kata kunci maks 5. TIDAK bolak-balik.",
    ),
    "sitasi": "APA 7 (Fakultas Kedokteran Hewan UGM, 2024)",
    "daftar_pustaka": 'heading "DAFTAR PUSTAKA" di halaman baru',
    "kelengkapan_tambahan": ["kata kunci (maks. 5 kata)"],
    "sumber": {
        "status": "pedoman-resmi",
        "dokumen": "Panduan Penulisan Skripsi Fakultas Kedokteran Hewan UGM",
        "url": "https://fkh.ugm.ac.id/wp-content/uploads/sites/14/2024/08/Panduan-Skripsi-FKH-2024.pdf",
        "scope": "Fakultas Kedokteran Hewan UGM (pedoman 2024)",
        "tahun": 2024,
        "catatan": "PEDOMAN UGM BEDA-BEDA ANTAR FAKULTAS. FKH (2024): spasi 2, kuarto "
                   "21x28, daftar pustaka APA 7. Sebaliknya DTSL Fakultas Teknik (2023, "
                   "https://tsipil.ugm.ac.id/wp-content/uploads/sites/4/2023/02/"
                   "Pedoman-Penulisan-DTSL_2023_v1-Final.pdf) menetapkan spasi 1,15, "
                   "margin atas 2,5 / kiri 2,5 (cetak 3,5) / bawah 3,0 / kanan 2,5 cm. "
                   "Nilai di preset ini mengikuti FKH.",
    },
    "verifikasi": (
        "Angka format diambil dari Panduan Penulisan Skripsi Fakultas Kedokteran Hewan "
        "UGM (2024). UGM TIDAK memiliki satu pedoman tunggal: DTSL Fakultas Teknik (2023) "
        "mengatur spasi 1,15 dan margin berbeda. Wajib cek pedoman fakultas Anda; "
        "preset ini memakai nilai FKH sebagai titik awal."
    ),
}

# ── UI ───────────────────────────────────────────────────────────────────────
# Sumber terbaik sejauh ini: pedoman tingkat UNIVERSITAS (semua fakultas).
PATCH_LEGACY["ui"] = {
    "gaya_dokumen": gaya(
        margin={"atas": "3 cm", "bawah": "3 cm", "kiri": "4 cm", "kanan": "3 cm"},
        spasi="1.5",
        penomoran="bagian awal angka romawi kecil, tengah 2,5 cm dari tepi bawah; "
                   "bagian isi & akhir angka arab di sudut kanan atas "
                   "(1,5 cm tepi atas, 3 cm tepi kanan); halaman pertama tiap bab di tengah bawah",
        align="Rata kiri-kanan (justify). Abstrak maks 500 kata, 1 spasi. "
              "Sampul karton + linen putih (Sarjana) / cokelat (Magister-Doktor). "
              "Logo UI diameter 2,5 cm. Judul sampul 14 pt.",
    ),
    "sitasi": "APA (Fakultas Psikologi & FEB UI merujuk APA Publication Manual) — verifikasi per fakultas",
    "daftar_pustaka": 'heading "DAFTAR PUSTAKA"/"DAFTAR REFERENSI" di halaman baru',
    "kelengkapan_tambahan": ["pernyataan persetujuan publikasi karya ilmiah"],
    "sumber": {
        "status": "pedoman-resmi",
        "dokumen": "Pedoman Penulisan Tugas Akhir Universitas Indonesia (revisi 2017), "
                   "SK Rektor UI No. 2143/SK/R/UI/2017",
        "url": "https://feb.ui.ac.id/uploads/2022/06/SK-Pedoman-Penulisan-Karya-Akhir-2017-UPDATE.pdf",
        "scope": "UNIVERSITAS INDONESIA — berlaku untuk semua fakultas, sekolah, dan vokasi",
        "tahun": 2017,
        "catatan": "Pedoman tingkat universitas (disahkan SK Rektor UI 2143/SK/R/UI/2017), "
                   "jadi yang paling berlaku lintas fakultas. Program Studi boleh menambah "
                   "petunjuk sendiri di atas pedoman ini. Margin atas 3 cm tercantum "
                   "pada butir 3.1.2 (Pengetikan).",
    },
    "verifikasi": (
        "Angka format diambil dari Pedoman Penulisan Tugas Akhir UI 2017 yang "
        "berlaku untuk SELURUH fakultas, sekolah, dan vokasi UI (SK Rektor "
        "2143/SK/R/UI/2017). Program studi boleh menambah ketentuan tersendiri; "
        "verifikasi bila fakultas Anda punya pedoman tambahan."
    ),
}

# ── ITB ──────────────────────────────────────────────────────────────────────
PATCH_LEGACY["itb"] = {
    "gaya_dokumen": gaya(
        margin={"atas": "4 cm", "bawah": "3 cm", "kiri": "4 cm (termasuk 1 cm penjilidan)",
                "kanan": "3 cm"},
        spasi="1.5",
        penomoran="bagian awal angka romawi kecil; bagian isi & akhir angka arab",
        align="1 spasi untuk catatan kaki, keterangan tabel, keterangan gambar, dan daftar "
              "pustaka. Paragraf baru 3 spasi. Dicetak satu muka. Sampul hard cover "
              "biru tua. Standar acuan: Pedoman Format Penulisan Tesis Magister, "
              "Sekolah Pascasarjana ITB.",
    ),
    "sitasi": "IEEE (untuk bidang teknik, sesuai default ITB)",
    "daftar_pustaka": 'heading "DAFTAR PUSTAKA" di halaman baru',
    "sumber": {
        "status": "pedoman-resmi",
        "dokumen": "Tata-cara Penulisan Skripsi Program Studi Teknik Geologi, "
                   "FITB-ITB (mengikuti standar Sekolah Pascasarjana ITB)",
        "url": "https://ditdik.itb.ac.id/wp-content/uploads/sites/90/2015/10/format-penulisan-ta-bentuk-buku-revisi.pdf",
        "scope": "Fakultas Ilmu dan Teknologi Kebumian (FITB) ITB; standar School of "
                 "Graduate Studies (SPS) ITB berlaku lintas fakultas",
        "tahun": 2015,
        "catatan": "Nilai dikonfirmasi juga oleh SITH-Rekayasa Pertanian "
                   "(https://rp.sith.itb.ac.id/wp-content/uploads/sites/168/2016/09/"
                   "Panduan-Penulisan-Skripsi-dan-Draft-Publikasi.pdf): TNR 12, spasi 1,5, "
                   "margin 4/3/4/3 cm. ITB menyatakan tiap prodi punya kekhasan sendiri; "
                   "perbedaan kecil antar prodi wajar.",
    },
    "verifikasi": (
        "Angka format diambil dari pedoman penulisan skripsi FITB-ITB yang "
        "sendirinya mengacu pada standar Sekolah Pascasarjana ITB, dan dikonfirmasi "
        "oleh pedoman SITH-ITB (spasi 1,5; margin 4/3/4/3 cm). ITB menyatakan setiap "
        "program studi punya kekhasan format; cocokkan dengan prodi Anda."
    ),
}


def main():
    ap = argparse.ArgumentParser(description="Generate preset campus_templates")
    ap.add_argument("--check", action="store_true",
                    help="validasi JSON + provenance + deteksi drift (exit 1 bila tidak sinkron)")
    ap.add_argument("--backfill", action="store_true",
                    help="tambahkan sumber.status=konvensi-umum ke preset tanpa provenance")
    ap.add_argument("--patch", action="store_true",
                    help="merge gaya_dokumen/sitasi/sumber ke preset lama, struktur diutmakan")
    ap.add_argument("--only", help="generate satu preset (nama file tanpa .json)")
    args = ap.parse_args()

    if args.backfill:
        berubah = backfill_sumber()
        if berubah:
            print(f"Backfill sumber pada {len(berubah)} preset: {', '.join(berubah)}")
        else:
            print("Semua preset sudah punya provenance; tidak ada perubahan.")
        return 0

    if args.patch:
        berubah = patch_legacy()
        print(f"Di-patch {len(berubah)} preset lama: {', '.join(berubah) if berubah else '(tidak ada)'}")
        print("Catatan: field `struktur` preset lama tidak disentuh.")
        return 0

    targets = PRESETS
    if args.only:
        if args.only not in PRESETS:
            sys.exit(f"ERROR: tidak dikenal: {args.only}")
        targets = {args.only: PRESETS[args.only]}

    dibuat, dilewati, drift = [], [], []
    for nama_file, info in sorted(targets.items()):
        preset = info["preset"]
        path = os.path.join(DIR_PRESET, f"{nama_file}.json")
        validasi(nama_file, preset)

        if args.check:
            # --check = validasi + DETEKSI DRIFT: bandingkan isi di disk dengan
            # hasil generator. Hanya berlaku untuk preset regenerate=True;
            # preset lama (ugm/ui/uny/itb/generic/custom) tidak terdaftar di
            # PRESETS dan tetap diperiksa terpisah oleh tests/run_tests.sh.
            if not os.path.exists(path):
                print(f"  HILANG   {nama_file}.json")
                drift.append(nama_file)
                continue
            with open(path, encoding="utf-8") as fh:
                try:
                    isi_disk = json.load(fh)
                except json.JSONDecodeError as e:
                    print(f"  RUSAK    {nama_file}.json: {e}")
                    drift.append(nama_file)
                    continue
            dibuat.append(nama_file)
            if not info["regenerate"]:
                dilewati.append(nama_file)
                continue
            if isi_disk != preset:
                kunci = sorted(
                    k for k in set(isi_disk) | set(preset)
                    if isi_disk.get(k) != preset.get(k)
                )
                print(f"  DRIFT    {nama_file}.json: field berubah -> {', '.join(kunci)}")
                drift.append(nama_file)
            continue

        if not info["regenerate"]:
            dilewati.append(nama_file)
            continue

        with open(path, "w", encoding="utf-8") as fh:
            json.dump(preset, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        dibuat.append(nama_file)

    if args.check:
        if drift:
            print(f"GAGAL: {len(drift)} preset tidak sinkron dengan generator: "
                  f"{', '.join(drift)}")
            print("Jalankan: python3 scripts/generate_campus_presets.py")
            return 1
        print(f"OK: {len(dibuat)} preset JSON valid, provenance lengkap, "
              f"tanpa drift terhadap generator.")
        return 0
    print(f"Ditulis {len(dibuat)} preset: {', '.join(dibuat)}")
    if dilewati:
        print(f"tidak di-generate: {', '.join(dilewati)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())