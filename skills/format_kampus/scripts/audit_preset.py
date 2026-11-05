#!/usr/bin/env python3
"""Audit provenans dan kelengkapan preset kampus.

Pemakaian:
    python3 audit_preset.py                       # semua preset di ../presets
    python3 audit_preset.py --presets DIR --out AUDIT.md
    python3 audit_preset.py --json audit.json --tahun-acuan 2026

Preset bernama kampus besar sering diturunkan dari pedoman SATU fakultas atau
satu prodi. Pengguna yang memilih "UGM" lalu mendapat angka Fakultas Kedokteran
Hewan tanpa tahu. Skrip ini membuat hal itu terlihat.

Tujuh kriteria (masing-masing 1 poin, tanpa bobot — sengaja sederhana):
  0. provenans  sumber_panduan menunjuk dokumen panduan, BUKAN pengakuan bahwa
                angka berasal dari "konvensi umum" / "belum diverifikasi"
  1. margin     keempat sisi terisi
  2. spasi      spasi isi terisi
  3. sitasi     gaya sitasi terisi
  4. caption    format nomor caption tabel dan gambar diketahui
  5. cakupan    sumber_panduan tidak menunjuk satu fakultas/prodi tertentu
  6. usia       tahun panduan terdeteksi dan tidak lebih tua dari 5 tahun

Skor ini mengukur KELENGKAPAN DAN PROVENANS DATA DI BERKAS, bukan kebenaran angka
terhadap panduan asli. Preset dengan 7/7 tetap harus dicocokkan dengan edisi
panduan terbaru fakultas pengguna.

Kode keluar: 0 selesai; 2 folder preset tidak terbaca.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys

import yaml

LEWATI = {"universitas-contoh.yaml", "custom.yaml", "generic.yaml", "ars-fti-halaman.yaml"}
POLA_UNIT = re.compile(
    r"\b(fakultas|fak\.|FKH|FPIK|FTI|FISIP|FTIP|FEB|FK|FH|prodi|program\s+studi|"
    r"departemen|jurusan|vokasi|DTSL|sekolah)\b", re.I)
POLA_TIDAK_TERVERIFIKASI = re.compile(
    r"belum\s+diverifikasi|kebiasaan\s+umum|konvensi\s+umum", re.I)
POLA_TAHUN = re.compile(r"\b(19[89]\d|20[0-4]\d)\b")


def ambil(d: dict, *kunci, default=None):
    for k in kunci:
        if not isinstance(d, dict):
            return default
        d = d.get(k)
    return default if d is None else d


def tahun_panduan(kampus: dict) -> int | None:
    for field in ("sumber_panduan", "catatan_sumber"):
        ditemukan = [int(t) for t in POLA_TAHUN.findall(str(kampus.get(field) or ""))]
        if ditemukan:
            return max(ditemukan)
    return None


def nilai_kosong(v) -> bool:
    return v is None or (isinstance(v, str) and ("BELUM" in v.upper() or not v.strip()))


def audit_satu(path: str, tahun_acuan: int) -> dict:
    with open(path, encoding="utf-8") as f:
        p = yaml.safe_load(f) or {}
    kampus = p.get("kampus") or {}
    sumber = str(kampus.get("sumber_panduan") or "")
    margin = ambil(p, "dokumen", "margin_cm", default={}) or {}
    sisi_kosong = [s for s in ("kiri", "atas", "kanan", "bawah") if nilai_kosong(margin.get(s))]
    thn = tahun_panduan(kampus)
    tak_terverifikasi = bool(POLA_TIDAK_TERVERIFIKASI.search(sumber))
    # Teks "belum diverifikasi ... fakultas" menyebut kata fakultas tanpa menunjuk
    # satu fakultas; jangan salah dilabeli.
    unit = (not tak_terverifikasi) and bool(POLA_UNIT.search(sumber))
    cap_t = ambil(p, "caption", "tabel", "penomoran")
    cap_g = ambil(p, "caption", "gambar", "penomoran")

    krit = {
        "provenans": bool(sumber) and not tak_terverifikasi,
        "margin": not sisi_kosong,
        "spasi": not nilai_kosong(ambil(p, "spasi", "isi")),
        "sitasi": not nilai_kosong(ambil(p, "sitasi", "gaya")),
        "caption": not (nilai_kosong(cap_t) or nilai_kosong(cap_g)),
        "cakupan": bool(sumber) and not tak_terverifikasi and not unit,
        "usia": thn is not None and (tahun_acuan - thn) <= 5,
    }
    celah = []
    if tak_terverifikasi:
        celah.append("TIDAK TERVERIFIKASI: sumber mengaku konvensi umum, bukan panduan kampus")
    elif not sumber:
        celah.append("sumber_panduan kosong")
    if sisi_kosong:
        celah.append("margin kosong: " + "/".join(sisi_kosong))
    if not krit["spasi"]:
        celah.append("spasi isi kosong")
    if not krit["sitasi"]:
        celah.append("gaya sitasi kosong")
    if not krit["caption"]:
        celah.append("format nomor caption tidak diketahui")
    if unit:
        celah.append("sumber = satu fakultas/prodi")
    if thn is None and not tak_terverifikasi:
        celah.append("tahun panduan tidak terdeteksi")
    elif thn is not None and not krit["usia"]:
        celah.append(f"panduan {thn} (>5 th)")
    if nilai_kosong(ambil(p, "sitasi", "min_jurnal_atau_prosiding")):
        celah.append("minimal jurnal tidak diatur")
    return {
        "berkas": os.path.basename(path),
        "kampus": kampus.get("nama") or "?",
        "sumber_panduan": sumber or "(kosong)",
        "tahun": thn,
        "kriteria": krit,
        "poin": sum(krit.values()),
        "unit": unit,
        "tak_terverifikasi": tak_terverifikasi,
        "celah": celah,
        "manual": bool(re.search(r"(?m)^\s*manual:\s*true\b",
                                 open(path, encoding="utf-8").read(2000))),
    }


def markdown(hasil: list[dict], tahun_acuan: int, tanggal: str) -> str:
    n = len(hasil)
    tak_verif = [h for h in hasil if h["tak_terverifikasi"]]
    satu_unit = sum(1 for h in hasil if h["unit"])
    caption_x = sum(1 for h in hasil if not h["kriteria"]["caption"])
    penuh = [h for h in hasil if h["poin"] == 7]
    baris = [
        "# Audit Preset Kampus",
        "",
        f"Dihasilkan `scripts/audit_preset.py` pada {tanggal} (tahun acuan {tahun_acuan}). "
        "Jangan disunting tangan; jalankan ulang skripnya.",
        "",
        "Poin mengukur **kelengkapan dan provenans data di berkas**, bukan kebenaran "
        "angka terhadap panduan asli. Tujuh kriteria bernilai 1 poin tanpa bobot: "
        "provenans (sumber menunjuk dokumen panduan), margin lengkap, spasi isi, gaya sitasi, format caption, cakupan universitas "
        "(bukan satu fakultas/prodi), dan panduan berusia paling lama 5 tahun.",
        "",
        "## Ringkasan",
        "",
        f"- Preset diaudit: **{n}**",
        f"- **Tidak terverifikasi** (berkas sendiri mengaku angkanya dari konvensi umum): "
        f"**{len(tak_verif)}** — {', '.join(h['berkas'] for h in tak_verif) or '-'}",
        f"- Bersumber dari satu fakultas/prodi: **{satu_unit}**",
        f"- Format nomor caption tidak diketahui: **{caption_x}**",
        f"- Memenuhi 7/7 kriteria: **{len(penuh)}**"
        + (f" ({', '.join(h['berkas'] for h in penuh)})" if penuh else ""),
        "",
        "## Per preset (urut dari yang paling lengkap)",
        "",
        "| Berkas | Kampus | Tahun | Poin | Celah |",
        "|---|---|---|---|---|",
    ]
    for h in sorted(hasil, key=lambda x: (-x["poin"], x["berkas"])):
        baris.append(
            f"| `{h['berkas']}` | {h['kampus']} | {h['tahun'] or '?'} | {h['poin']}/7"
            f"{' (manual)' if h['manual'] else ''} | {'; '.join(h['celah']) or '-'} |")
    baris += [
        "",
        "## Cara memakai laporan ini",
        "",
        "1. Preset bertanda **TIDAK TERVERIFIKASI** jangan pernah disajikan sebagai "
        "ketentuan kampus. Minta panduan resmi pengguna dan ekstrak dari nol.",
        "1b. Saat pengguna menyebut kampus, **tanyakan fakultas dan prodinya**. Bila "
        "preset bertanda *satu fakultas/prodi* dan fakultas pengguna berbeda, perlakukan "
        "angkanya sebagai draf yang belum terkunci.",
        "2. Celah *format nomor caption* dan *minimal jurnal* tidak boleh diisi dengan "
        "dugaan. Tanyakan, atau lihat contoh skripsi terbitan fakultasnya.",
        "3. Menaikkan poin sebuah preset berarti membaca panduan resminya dan mengutip "
        "butirnya, mengikuti cetakan `ars-fti.yaml`.",
        "",
    ]
    return "\n".join(baris)


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="Audit provenans dan kelengkapan preset kampus.")
    ap.add_argument("--presets", default=os.path.join(here, "..", "presets"))
    ap.add_argument("--out", help="tulis laporan Markdown ke berkas ini")
    ap.add_argument("--json", help="tulis hasil mentah JSON ke berkas ini")
    ap.add_argument("--tahun-acuan", type=int, default=datetime.date.today().year)
    ap.add_argument("--tanggal", default=datetime.date.today().isoformat())
    a = ap.parse_args()

    if not os.path.isdir(a.presets):
        print(f"GAGAL: folder preset tidak ada: {a.presets}", file=sys.stderr)
        return 2
    berkas = sorted(f for f in os.listdir(a.presets)
                    if f.endswith(".yaml") and f not in LEWATI)
    hasil = []
    for f in berkas:
        try:
            hasil.append(audit_satu(os.path.join(a.presets, f), a.tahun_acuan))
        except Exception as e:  # noqa: BLE001
            print(f"PERINGATAN: {f} tidak terbaca ({e})", file=sys.stderr)

    md = markdown(hasil, a.tahun_acuan, a.tanggal)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Laporan ditulis: {a.out} ({len(hasil)} preset)")
    else:
        print(md)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(hasil, f, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
