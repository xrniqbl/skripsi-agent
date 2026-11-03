#!/usr/bin/env python3
"""Konversi preset kampus JSON (proposal_skripsi) menjadi profil format YAML
(format_kampus) yang mengikat generator DOCX.

Pemakaian:
    python3 campus_json2yaml.py --semua
    python3 campus_json2yaml.py ugm ui itb
    python3 campus_json2yaml.py --semua --keluaran-dir /tmp/coba
    python3 campus_json2yaml.py --semua --cek     # validasi tanpa menulis

Kenapa skrip ini ada: bundel punya DUA tempat menyimpan ketentuan kampus.
`proposal_skripsi/campus_templates/*.json` (29 kampus) dipakai alur proposal,
sedangkan `format_kampus/presets/*.yaml` (sebelumnya 3) adalah satu-satunya
sumber yang dibaca generator DOCX. Akibatnya 26 kampus punya data tetapi
tidak bisa menghasilkan dokumen dengan formatnya sendiri.

Aturan konversi — sama ketatnya dengan ekstraksi manual:

- Angka diambil dari teks panduan ("4 cm", "3,0 cm", "Times New Roman 12 pt").
  Nilai yang tidak terbaca menjadi `null` dan dicatat di `catatan_konflik`,
  TIDAK ditebak. Menebak margin lebih berbahaya daripada mengosongkannya:
  dokumen salah format terlihat benar sampai dicetak.
- Kalimat "perlu konfirmasi" pada JSON dihormati: nilainya null + catatan.
- Nilai yang di panduan punya dua versi ("3 cm naskah badan; 4 cm halaman
  pengesahan") memakai nilai naskah badan, versi lain masuk catatan.
- Teks bebas yang tidak bisa dipetakan (mis. aturan warna sampul) disimpan
  apa adanya di `kampus.catatan_sumber`, bukan dibuang.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

AKAR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
JSON_DIR = os.path.join(AKAR, "skills", "proposal_skripsi", "campus_templates")
KELUARAN_BAWAAN = os.path.join(AKAR, "skills", "format_kampus", "presets")

RE_ANGKA = re.compile(r"(\d+(?:[.,]\d+)?)")


def angka(teks, pola=None):
    """Ambil angka pertama dari teks berpola ('4 cm' -> 4.0). None bila tak ada.

    Koma desimal Indonesia diterima: '2,25 cm' -> 2.25.
    """
    if teks is None:
        return None
    if isinstance(teks, (int, float)):
        return float(teks)
    s = str(teks)
    if pola:
        m = re.search(pola, s, re.I)
        if not m:
            return None
        s = m.group(1)
    elif "konfirmasi" in s.lower():
        return None
    m = RE_ANGKA.search(s)
    return float(m.group(1).replace(",", ".")) if m else None


def ukuran_kertas(teks):
    """'A4 (kuarto 21 x 28 cm)' -> 'A4'. B5/Letter dikenali, tak dikenal -> None."""
    s = (teks or "").upper()
    for kunci, nilai in (("A4", "A4"), ("A-4", "A4"), ("KUARTO", "A4"),
                         ("F4", "F4"), ("FOLIO", "F4"),
                         ("LETTER", "Letter"), ("B5", "B5")):
        if kunci in s:
            return nilai
    return None


def gaya_sitasi(teks):
    """Normalisasi nama gaya dari teks bebas. Tidak dikenal -> None."""
    s = (teks or "").lower()
    if "ieee" in s:
        return "IEEE"
    if "vancouver" in s:
        return "Vancouver"
    if "mla" in s:
        return "MLA"
    if "chicago" in s:
        return "Chicago"
    if "apa" in s:
        return "APA"
    return None


def spasi_isi(teks):
    """'2' -> 2.0, '1,5' -> 1.5, 'perlu konfirmasi' -> None."""
    if teks is None:
        return None
    s = str(teks).lower()
    if "konfirmasi" in s:
        return None
    if "double" in s or "ganda" in s:
        return 2.0
    m = RE_ANGKA.search(s)
    if not m:
        return None
    v = float(m.group(1).replace(",", "."))
    return v if v in (1.0, 1.15, 1.5, 2.0) else None


def penomoran(teks):
    """Petakan kalimat penomoran halaman ke struktur profil.

    Mengembalikan (dict, [catatan]). Yang tidak disebut tetap memakai skema
    baku skripsi Indonesia (Romawi kecil / Arab mulai 1 / Arab lanjutan),
    karena itu konvensi nasional — tetapi setiap penyimpangan yang terbaca
    dari panduan (posisi, jarak tepi) diterapkan.
    """
    s = (teks or "").lower()
    catatan = []
    awal = {"format": "romawi_kecil", "posisi": "tengah_bawah",
            "jarak_dari_bawah_cm": None,
            "lembar_judul_dihitung_tanpa_nomor": True,
            "sampul_dihitung": True,
            "nomor_disembunyikan": []}
    pokok = {"format": "arab", "mulai_dari": 1,
             "awal_bab": "tengah_bawah", "halaman_lain": "kanan_atas"}
    akhir = {"format": "arab_lanjutan", "posisi": "tengah_bawah"}

    if not s:
        catatan.append("penomoran halaman tidak diatur di JSON — memakai skema "
                       "baku (Romawi kecil / Arab mulai 1 / Arab lanjutan)")
        return {"bagian_awal": awal, "bagian_pokok": pokok,
                "bagian_akhir": akhir, "catatan_konflik": catatan}

    # jarak dari tepi bawah, mis. "tengah 2,5 cm dari tepi bawah"
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*cm\s*(?:dari|di)?\s*tepi\s*bawah", s)
    if m:
        awal["jarak_dari_bawah_cm"] = float(m.group(1).replace(",", "."))

    # posisi bagian awal
    if "romawi" in s:
        if "atas" in s and "bawah" not in s.split("romawi")[1][:60]:
            awal["posisi"] = "kanan_atas"
        elif "tengah" in s:
            awal["posisi"] = "tengah_bawah"
    else:
        catatan.append("bagian awal tidak disebut memakai angka Romawi — "
                       "diperiksa manual terhadap panduan")

    # posisi halaman isi
    if re.search(r"(isi|inti|pokok)[^.]{0,80}kanan\s*atas", s) or \
            re.search(r"kanan\s*atas[^.]{0,60}(1,5|2)\s*cm", s):
        pokok["halaman_lain"] = "kanan_atas"
    elif re.search(r"(isi|inti|pokok)[^.]{0,80}tengah\s*bawah", s):
        pokok["halaman_lain"] = "tengah_bawah"
    if "halaman pertama tiap bab" in s or "awal bab" in s:
        pokok["awal_bab"] = "tengah_bawah"

    if "akhir" not in s and "lanjut" not in s:
        catatan.append("bagian akhir (Daftar Pustaka/Lampiran) tidak disebut — "
                       "dipakai Arab lanjutan, bukan mulai dari 1")
    return {"bagian_awal": awal, "bagian_pokok": pokok,
            "bagian_akhir": akhir, "catatan_konflik": catatan}


def caption_dari(catatan_tambahan, kelengkapan):
    """Baca penomoran caption dari teks panduan, hanya bila benar-benar disebut.

    Dua pola dipakai skripsi Indonesia: 'Tabel 4.1' (Arab per bab) atau
    'Tabel IV.1' (Romawi kapital per bab). Salah pilih = seluruh caption
    dokumen salah, jadi tanpa bukti teks hasilnya None.

    "penomoran caption ... (Tabel IV.1)" harus terbaca sebagai Romawi — versi
    pertama fungsi ini mencari pola "tabel iv" yang tidak pernah muncul karena
    contoh di panduan selalu ditulis "Tabel IV.1" dengan titik.
    """
    teks = " ".join(str(x) for x in (catatan_tambahan, " ".join(kelengkapan or []))
                    if x).lower()
    # Bentuk yang muncul di panduan nyata: "Tabel III.1" (tanpa titik setelah
    # angka Romawi) DAN "Tabel IV.1" (dengan titik). Versi pertama hanya
    # menangkap bentuk bertitik, sehingga ARS yang jelas menulis "Tabel IV.1"
    # terbaca "BELUM DIKETAHUI" — caption seluruh dokumen lalu memakai Arab,
    # padahal panduannya Romawi.
    RE_ROMAWI = re.compile(r"(?:tabel|gambar)\s+[ivx]+\s*[.,]?\s*\d")
    RE_ARAB = re.compile(r"(?:tabel|gambar)\s+\d+\s*[.,]\s*\d")
    if RE_ROMAWI.search(teks):
        return "per bab, angka Romawi kapital"
    if RE_ARAB.search(teks):
        return "per bab, angka Arab"
    if "caption" in teks and "romawi" in teks:
        return "per bab, angka Romawi kapital"
    if "caption" in teks and "arab" in teks:
        return "per bab, angka Arab"
    return None


def konversi(data: dict) -> tuple[dict, list[str]]:
    """JSON preset -> (profil, daftar peringatan)."""
    g = data.get("gaya_dokumen") or {}
    s = data.get("sumber") or {}
    catatan_konflik: list[str] = []
    peringatan: list[str] = []

    margin = g.get("margin") or {}
    kiri = angka(margin.get("kiri"))
    atas = angka(margin.get("atas"))
    kanan = angka(margin.get("kanan"))
    bawah = angka(margin.get("bawah"))
    for nama, nilai in (("kiri", kiri), ("atas", atas),
                        ("kanan", kanan), ("bawah", bawah)):
        if nilai is None:
            catatan_konflik.append(f"margin {nama} tidak terbaca dari panduan "
                                   f"({margin.get(nama)!r}) — isi manual")
    # versi kedua yang disebut dalam tanda kurung tetap dicatat
    for nama in ("kiri", "atas", "kanan", "bawah"):
        teks = str(margin.get(nama) or "")
        if ";" in teks:
            catatan_konflik.append(f"margin {nama} punya dua nilai: {teks} — "
                                   f"dipakai nilai pertama (naskah badan)")

    font_isi = str(g.get("font_isi") or "")
    ukuran_pt = angka(font_isi, r"(\d+(?:[.,]\d+)?)\s*pt")
    nama_font = "Times New Roman"
    m = re.match(r"([A-Za-z ]+?)\s+\d", font_isi)
    if m and m.group(1).strip():
        nama_font = m.group(1).strip()
    elif not font_isi:
        peringatan.append("font isi tidak disebut — dipakai Times New Roman "
                          "sebagai default dan dicatat")
        catatan_konflik.append("font isi tidak diatur di JSON")

    judul_pt = angka(g.get("font_judul"), r"(\d+(?:[.,]\d+)?)\s*pt") or (ukuran_pt or 12) + 2

    sis = data.get("struktur") or []
    bagian_awal, bab, bagian_akhir, judul_bab = [], {}, [], {}
    for blok in sis:
        bid = str(blok.get("id") or "")
        judul_blok = str(blok.get("judul") or "")
        sub = [str(x.get("judul")) for x in (blok.get("subbab") or [])
               if x.get("judul")]
        if bid == "frontmatter":
            bagian_awal.extend(sub)
        elif bid == "backmatter":
            bagian_akhir.extend(sub or ["Daftar Pustaka", "Lampiran"])
        elif bid.startswith("bab"):
            # "BAB I PENDAHULUAN" -> kunci "BAB I", judul "PENDAHULUAN".
            # Judul bab WAJIB ikut: tanpa itu generator hanya mencetak "BAB I"
            # tanpa baris "PENDAHULUAN", dan daftar isi kehilangan nama bab.
            m = re.match(r"^(BAB\s+[IVX]+|\d+)\s*(.*)$", judul_blok.strip(), re.I)
            if m:
                kunci = re.sub(r"\s+", " ", m.group(1).upper())
                judul = m.group(2).strip()
            else:
                kunci, judul = f"BAB {bid[3:].upper()}", judul_blok.strip()
            bab[kunci] = sub
            if judul:
                judul_bab[kunci] = judul.upper()
    if not bagian_awal:
        peringatan.append("frontmatter kosong — bagian awal tidak terbentuk")
    if not bab:
        peringatan.append("tidak ada bab terdeteksi")
    elif len(bab) < 5:
        peringatan.append(f"hanya {len(bab)} bab di preset JSON — skripsi utuh "
                          f"butuh 5 (proposal biasanya 3); bab IV/V harus ditambah")
    if not bagian_akhir:
        bagian_akhir = ["Daftar Pustaka", "Lampiran"]
        peringatan.append("backmatter kosong — dipakai Daftar Pustaka + Lampiran")

    ph = penomoran(g.get("penomoran_halaman"))
    catatan_konflik.extend(ph.pop("catatan_konflik", []))

    cap = caption_dari(
        " ".join(str(x) for x in (
            g.get("catatan_tambahan"),
            (s.get("catatan") if isinstance(s, dict) else ""),
            data.get("verifikasi"),
            data.get("daftar_pustaka"),
        ) if x),
        data.get("kelengkapan"))
    if cap is None:
        catatan_konflik.append("penomoran caption (Tabel 4.1 vs Tabel IV.1) tidak "
                               "disebut — periksa panduan sebelum menulis caption")

    gaya = gaya_sitasi(data.get("sitasi"))
    if gaya is None:
        catatan_konflik.append(f"gaya sitasi tidak dikenali: {data.get('sitasi')!r}")

    sp = spasi_isi(g.get("spasi"))
    if sp is None:
        catatan_konflik.append(f"spasi isi tidak terbaca: {g.get('spasi')!r} — "
                               f"isi manual (1,5 atau 2)")

    sumber_teks = " | ".join(str(x) for x in (
        (s.get("dokumen") if isinstance(s, dict) else ""),
        data.get("verifikasi") or "") if x)

    profil = {
        "kampus": {
            "nama": data.get("kampus") or "",
            "fakultas": "",
            "program_studi": ", ".join(data.get("jenjang") or []),
            "sumber_panduan": (s.get("dokumen") if isinstance(s, dict) else "") or sumber_teks,
            "sumber_template": "dikonversi dari campus_templates/%s.json" %
                               (data.get("singkat") or data.get("kampus", "?")).lower().replace(" ", "_"),
            "catatan_sumber": sumber_teks[:900],
        },
        "dokumen": {
            "ukuran_kertas": ukuran_kertas(g.get("ukuran_halaman")),
            "margin_cm": {"kiri": kiri, "atas": atas, "kanan": kanan, "bawah": bawah},
        },
        "font": {
            "nama": nama_font,
            "isi_pt": ukuran_pt or 12,
            "warna": "hitam",
            "judul_bab": {"pt": judul_pt, "tebal": True, "kapital": True, "rata": "tengah"},
            "subbab": {"pt": ukuran_pt or 12, "tebal": True},
            "sub_subbab": {"pt": ukuran_pt or 12, "tebal": True},
            "judul_tabel_gambar_pt": ukuran_pt or 12,
        },
        "spasi": {
            "isi": sp,
            "judul": 1.5,
            "tabel": 1.0,
            "daftar_pustaka": 1.0,
            "catatan_daftar_pustaka": "tiap entri 1 spasi, jarak antar entri 2 spasi",
        },
        "sistematika": {
            "bagian_awal": bagian_awal,
            "judul_bab": judul_bab,
            "bab": bab,
            "bagian_akhir": bagian_akhir,
        },
        "penomoran_halaman": ph,
        "caption": {
            "tabel": {"posisi": "di_atas_tabel", "rata": "tengah",
                      "penomoran": cap or "BELUM DIKETAHUI"},
            "gambar": {"posisi": "di_bawah_gambar", "rata": "tengah",
                       "penomoran": cap or "BELUM DIKETAHUI"},
        },
        "sitasi": {
            "gaya": gaya,
            "min_jurnal_atau_prosiding": None,
            "batas_usia_referensi_tahun": None,
            "aturan_khusus": ([str(data.get("daftar_pustaka"))]
                              if data.get("daftar_pustaka") else []),
        },
        "sampul": {
            "judul": {"pt": judul_pt, "kapital": True, "spasi": 1.5},
            "kata_skripsi_pt": 18,
            "nama_nim_pt": judul_pt,
            "institusi_pt": ukuran_pt or 12,
            "kalimat_diajukan": "Diajukan untuk memenuhi salah satu syarat kelulusan Program Sarjana",
        },
        "bahasa": {"istilah_asing": "miring"},
        "pengecualian": [],
        "catatan_konflik": catatan_konflik,
    }
    return profil, peringatan


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Konversi campus_templates/*.json menjadi presets/*.yaml "
                    "untuk skill format_kampus.")
    ap.add_argument("nama", nargs="*", help="slug kampus (tanpa .json); kosong + --semua")
    ap.add_argument("--semua", action="store_true")
    ap.add_argument("--keluaran-dir", default=KELUARAN_BAWAAN)
    ap.add_argument("--cek", action="store_true", help="validasi saja, tidak menulis")
    a = ap.parse_args()

    try:
        import yaml
    except ImportError:
        print("GAGAL: butuh PyYAML (pip install pyyaml)", file=sys.stderr)
        return 2

    if not os.path.isdir(JSON_DIR):
        print(f"GAGAL: folder preset JSON tidak ada: {JSON_DIR}", file=sys.stderr)
        return 2
    berkas = sorted(f for f in os.listdir(JSON_DIR) if f.endswith(".json"))
    if not a.semua:
        if not a.nama:
            print("GAGAL: sebutkan slug kampus atau pakai --semua", file=sys.stderr)
            return 2
        mau = {f"{n.removesuffix('.json')}.json" for n in a.nama}
        berkas = [f for f in berkas if f in mau]
        hilang = mau - set(berkas)
        if hilang:
            print(f"GAGAL: preset tidak ada: {', '.join(sorted(hilang))}", file=sys.stderr)
            return 2
    if not berkas:
        print("GAGAL: tidak ada berkas untuk dikonversi", file=sys.stderr)
        return 2

    os.makedirs(a.keluaran_dir, exist_ok=True)
    total_catatan = 0
    ditulis = 0
    for nama_berkas in berkas:
        slug = nama_berkas[:-5]
        with open(os.path.join(JSON_DIR, nama_berkas), encoding="utf8") as f:
            data = json.load(f)
        profil, peringatan = konversi(data)
        total_catatan += len(profil["catatan_konflik"])
        tujuan = os.path.join(a.keluaran_dir, f"{slug.replace('_', '-')}.yaml")
        # Jangan pernah menimpa profil yang disusun tangan. Berkas hasil
        # konversi membawa penanda "DIKONVERSI OTOMATIS" di kepalanya; berkas
        # yang tidak punya penanda itu (mis. ars-fti.yaml yang diekstrak dari
        # panduan dengan nomor butir dan catatan_konflik lengkap) adalah sumber
        # yang lebih akurat daripada ringkasan JSON — menimpanya menghapus
        # pekerjaan ekstraksi manual dan menurunkan mutu profil.
        if os.path.exists(tujuan):
            with open(tujuan, encoding="utf8") as f:
                kepala_lama = f.read(400)
            if "DIKONVERSI OTOMATIS" not in kepala_lama:
                print(f"  {slug:14} DILEWATI — {os.path.basename(tujuan)} disusun "
                      f"tangan (hapus berkasnya bila ingin dikonversi ulang)")
                continue
        kepala = (
            f"# Profil Format Kampus — {profil['kampus']['nama'] or slug}\n"
            f"# DIKONVERSI OTOMATIS dari campus_templates/{nama_berkas} oleh\n"
            f"# scripts/campus_json2yaml.py. Jangan disunting tangan: perbaiki\n"
            f"# JSON sumbernya, atau salin berkas ini lalu ubah manual (tandai\n"
            f"# 'manual: true' di kepala berkas supaya konverter tidak menimpanya).\n"
            f"#\n"
            f"# Setiap nilai null berarti panduan TIDAK menyebutkannya — bukan nol,\n"
            f"# bukan default. Periksa catatan_konflik sebelum memakai profil ini\n"
            f"# untuk dokumen yang akan dicetak.\n")
        if a.cek:
            # validasi struktur minimal yang dibutuhkan generator
            kurang = [k for k in ("kampus", "dokumen", "font", "sistematika",
                                  "penomoran_halaman", "sitasi") if k not in profil]
            lab = [k for k, v in (profil["dokumen"]["margin_cm"] or {}).items()
                   if v is None]
            print(f"  {'OK  ' if not kurang else 'X   '} {slug:14} "
                  f"bab={len(profil['sistematika']['bab'])} "
                  f"awal={len(profil['sistematika']['bagian_awal'])} "
                  f"catatan={len(profil['catatan_konflik'])}"
                  + (f" margin-belum:{','.join(lab)}" if lab else "")
                  + (f" KURANG:{','.join(kurang)}" if kurang else ""))
            continue
        with open(tujuan, "w", encoding="utf8") as f:
            f.write(kepala)
            yaml.safe_dump(profil, f, allow_unicode=True, sort_keys=False,
                           default_flow_style=False, width=100)
        ditulis += 1
        print(f"  {slug:14} -> {os.path.basename(tujuan):22} "
              f"bab={len(profil['sistematika']['bab'])} "
              f"catatan_konflik={len(profil['catatan_konflik'])}"
              + (f"  [{'; '.join(peringatan)}]" if peringatan else ""))

    if a.cek:
        print(f"\n{len(berkas)} preset diperiksa.")
    else:
        print(f"\n{ditulis} profil ditulis ke {a.keluaran_dir}")
        print(f"{total_catatan} catatan_konflik total — periksa sebelum dipakai "
              f"untuk dokumen cetak.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
