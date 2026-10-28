#!/usr/bin/env python3
"""Hitung dan peringkatkan skor FINER untuk kandidat topik skripsi.

Pemakaian:
    python3 skor_topik.py 03_kandidat.json --out 03_skor_topik.md --ambang 70

Bobot: Feasible 30, Interesting 15, Novel 20, Ethical 15, Relevant 20.
Aturan mutlak: dimensi bernilai 0 = diskualifikasi, berapa pun totalnya.
Kode keluar 1 bila tidak ada kandidat yang lolos ambang.
"""
from __future__ import annotations

import argparse
import json
import sys

BOBOT = {"feasible": 30, "interesting": 15, "novel": 20, "ethical": 15, "relevant": 20}
LABEL = {"feasible": "Feasible", "interesting": "Interesting", "novel": "Novel",
         "ethical": "Ethical", "relevant": "Relevant"}

SARAN = {
    "feasible": [
        "kecilkan lingkup: satu unit kerja, bukan satu dinas",
        "ganti ke data sekunder publik (BPS/Satu Data/LPSE)",
        "turunkan desain: korelasional, bukan eksperimen",
        "kurangi n dan pakai uji non-parametrik",
        "minta ekspor CSV anonim alih-alih akses database",
    ],
    "interesting": [
        "pindahkan lokus ke tempat yang punya keterikatan pribadi",
        "ubah sudut dari 'mengukur besarnya' ke 'menjelaskan mengapa'",
    ],
    "novel": [
        "jalankan literature_probe.py dan laporkan angkanya",
        "tambahkan problematisasi satu domain asumsi (ontologis/epistemologis)",
        "cari moderator: variabel yang menjelaskan pertentangan antar studi",
        "pindah dari 'apakah berpengaruh' ke 'kapan/kapan tidak berpengaruh'",
    ],
    "ethical": [
        "hilangkan identitas sejak pengumpulan data",
        "ganti subjek rentan dengan petugas/agregat",
        "siapkan informed consent tertulis + surat izin penelitian",
    ],
    "relevant": [
        "wawancara 15 menit dengan calon pengguna hasil",
        "kaitkan ke target Renstra/SOP/SPM yang konkret",
        "nyatakan keputusan apa yang akan berubah karena temuan ini",
    ],
}


def skor_kandidat(k: dict) -> tuple[float, dict, list[str]]:
    s = k.get("skor") or {}
    rincian, masalah = {}, []
    for dim in BOBOT:
        v = s.get(dim)
        if v is None:
            masalah.append(f"dimensi '{dim}' tidak ada")
            v = 0
        if not isinstance(v, int) or isinstance(v, bool):
            masalah.append(f"'{dim}' = {v!r} bukan bilangan bulat")
            v = 0
        if not 0 <= v <= 5:
            masalah.append(f"'{dim}' = {v} di luar rentang 0–5")
            v = max(0, min(5, v))
        rincian[dim] = v
    total = sum(rincian[d] / 5 * BOBOT[d] for d in BOBOT)
    return round(total, 1), rincian, masalah


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("berkas")
    ap.add_argument("--out", help="tulis tabel markdown ke berkas ini")
    ap.add_argument("--ambang", type=float, default=70.0)
    args = ap.parse_args()

    try:
        data = json.load(open(args.berkas, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"GAGAL membaca {args.berkas}: {e}", file=sys.stderr)
        return 2

    kandidat = data.get("kandidat") or []
    if not kandidat:
        print("Tidak ada 'kandidat' di JSON.", file=sys.stderr)
        return 2

    hasil = []
    for i, k in enumerate(kandidat, 1):
        total, rincian, masalah = skor_kandidat(k)
        nol = [d for d, v in rincian.items() if v == 0]
        terlemah = min(rincian, key=lambda d: (rincian[d], -BOBOT[d]))
        hasil.append({
            "id": k.get("id") or f"K{i}",
            "judul": k.get("judul_kerja") or k.get("judul") or "(tanpa judul)",
            "total": total,
            "rincian": rincian,
            "diskualifikasi": bool(nol),
            "dimensi_nol": nol,
            "terlemah": terlemah,
            "masalah": masalah,
            "catatan": k.get("catatan", ""),
        })

    hasil.sort(key=lambda h: (h["diskualifikasi"], -h["total"]))
    lolos = [h for h in hasil if not h["diskualifikasi"] and h["total"] >= args.ambang]

    baris = ["# Skor FINER — Peringkat Kandidat Topik", "",
             f"Ambang: **{args.ambang:g}** · bobot F30/I15/N20/E15/R20 · "
             f"dimensi 0 = diskualifikasi", "",
             "| Rank | ID | Judul kerja | Total | F | I | N | E | R | Status |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for rank, h in enumerate(hasil, 1):
        r = h["rincian"]
        if h["diskualifikasi"]:
            status = f"DISKUALIFIKASI ({','.join(h['dimensi_nol'])}=0)"
        elif h["total"] >= 85:
            status = "KUAT"
        elif h["total"] >= args.ambang:
            status = "LAYAK"
        elif h["total"] >= 55:
            status = "RAPUH"
        else:
            status = "GANTI"
        baris.append(
            f"| {rank} | {h['id']} | {h['judul']} | **{h['total']:g}** | "
            f"{r['feasible']} | {r['interesting']} | {r['novel']} | {r['ethical']} | "
            f"{r['relevant']} | {status} |")

    baris += ["", "## Dimensi terlemah dan jalur perbaikan", ""]
    for h in hasil:
        if h["diskualifikasi"]:
            baris.append(f"### {h['id']} — DISKUALIFIKASI")
            baris.append(f"Dimensi bernilai 0: **{', '.join(h['dimensi_nol'])}**. "
                         "Topik tidak bisa dilanjutkan sebelum dimensi ini di atas 0.")
            baris.append("")
            continue
        baris.append(f"### {h['id']} — {h['judul']} ({h['total']:g})")
        baris.append(f"Dimensi terlemah: **{LABEL[h['terlemah']]} "
                     f"({h['rincian'][h['terlemah']]}/5)**")
        for s in SARAN[h["terlemah"]][:3]:
            baris.append(f"- {s}")
        if h["catatan"]:
            baris.append(f"- catatan: {h['catatan']}")
        if h["masalah"]:
            baris.append(f"- **masalah data**: {'; '.join(h['masalah'])}")
        baris.append("")

    teks = "\n".join(baris)
    print(teks)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(teks + "\n")
        print(f"\nDitulis: {args.out}", file=sys.stderr)

    if not lolos:
        print(f"\nTIDAK ADA kandidat yang lolos ambang {args.ambang:g}. "
              "Perbaiki dimensi terlemah atau cari kandidat baru.", file=sys.stderr)
        return 1
    print(f"\nLolos ambang: {len(lolos)} dari {len(hasil)} kandidat.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
