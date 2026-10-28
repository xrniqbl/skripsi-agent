#!/usr/bin/env python3
"""Validasi tabel tangga masalah pada 01_masalah.md.

Pemakaian:
    python3 peta_fenomena.py 01_masalah.md [--min-lulus 3] [--json hasil.json]

Memeriksa setiap blok `## F-xx` dan lima tangga wajibnya:
  1 Fakta        — wajib memuat angka
  2 Kesenjangan  — wajib menyebut pembanding (SOP/target/standar/literatur/persen)
  3 Dampak       — wajib menyebut pihak + besaran
  4 Urgensi      — wajib menyebut alasan waktu (regulasi/audit/peristiwa/eskalasi)
  5 Kelayakan    — wajib menyebut data konkret atau penanda [U]

Kode keluar 1 bila ada fenomena berstatus LULUS padahal tangga 5 kosong/gagal,
karena itu klaim kelayakan palsu.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

TANGGA = {
    1: ("fakta", "Fakta"),
    2: ("kesenjangan", "Kesenjangan"),
    3: ("dampak", "Dampak"),
    4: ("urgensi", "Urgensi"),
    5: ("kelayakan", "Kelayakan"),
}

RE_ANGKA = re.compile(r"\d")
RE_BESARAN = re.compile(
    r"(\d+\s*%|\d+[.,]\d+|\brp\s?[\d.]+|\b\d+\s*(hari|jam|menit|bulan|tahun|berkas|baris|"
    r"responden|partisipan|orang|data|kasus|unit|kali|rb|ribu|juta)\b)", re.I)
RE_PEMBANDING = re.compile(
    r"\b(sop|pedoman|target|renstra|standar|regulasi|perda|uu|pasal|literatur|studi|"
    r"\[L-\d+\]|kapasitas|praktik unit|dibanding)\b", re.I)
RE_URGENSI = re.compile(
    r"\b(audit|bpk|inspektorat|ombudsman|regulasi|uu|perda|tenggat|anggaran|"
    r"eskalasi|berulang|sejak \d{4}|belum pernah|kegagalan|sengketa|temuan)\b", re.I)
RE_KELAYAKAN = re.compile(
    r"(\[U\]|\b\d+\s*(bulan|tahun|berkas|responden|partisipan|orang|dataset|file)\b|"
    r"\b(arsip|tersedia|dipegang|sudah ada|bisa diakses|bersedia)\b)", re.I)
RE_STATUS = re.compile(r"\*\*(?:Verdikt|Status|Verdict)\s*:?\*\*\s*([^\n]*)", re.I)
RE_TANDA = re.compile(r"[✅⚠❌]")
RE_BUTUH = re.compile(r"\[BUTUH[^\]]*\]", re.I)


def pecah_blok(teks: str) -> list[tuple[str, str]]:
    """Bagi markdown jadi blok per fenomena (## F-xx ...)."""
    blok: list[tuple[str, str]] = []
    nama, buf = None, []
    for baris in teks.splitlines():
        if re.match(r"^#{2,3}\s*(F-\d+|FENOMENA)", baris, re.I):
            if nama:
                blok.append((nama, "\n".join(buf)))
            nama, buf = baris.strip("# ").strip(), []
        elif nama:
            buf.append(baris)
    if nama:
        blok.append((nama, "\n".join(buf)))
    return blok


def ambil_tangga(isi: str) -> dict[int, str]:
    """Ambil isi kolom 'Isi' dari tabel tangga, atau baris '- Tangga N: ...'."""
    hasil: dict[int, str] = {}
    for baris in isi.splitlines():
        b = baris.strip()
        if not b.startswith("|"):
            m = re.match(r"^[-*]\s*\**\s*([1-5])\b[^:]*:\s*(.+)$", b)
            if m:
                hasil[int(m.group(1))] = m.group(2).strip()
            continue
        sel = [s.strip() for s in b.strip("|").split("|")]
        if len(sel) < 2:
            continue
        m = re.match(r"^([1-5])\b", sel[0])
        if m:
            # kolom isi = sel[1]; kolom status biasanya sel terakhir
            hasil[int(m.group(1))] = sel[1]
    return hasil


def nilai_tangga(n: int, isi: str) -> tuple[bool, str]:
    """Kembalikan (lulus, alasan)."""
    if not isi or len(isi) < 6:
        return False, "kosong"
    if RE_BUTUH.search(isi) and not RE_KELAYAKAN.search(isi):
        # penanda [BUTUH ...] berarti bukti belum ada
        if n in (1, 2, 3):
            return False, "masih [BUTUH ...]"

    if n == 1:
        return (True, "ada angka") if RE_ANGKA.search(isi) else (False, "tanpa angka terukur")
    if n == 2:
        if not RE_PEMBANDING.search(isi):
            return False, "tanpa pembanding (SOP/target/standar/literatur)"
        return (True, "ada pembanding")
    if n == 3:
        if RE_BESARAN.search(isi):
            return True, "ada besaran"
        return False, "dampak tanpa besaran"
    if n == 4:
        if RE_URGENSI.search(isi):
            return True, "ada alasan waktu"
        return False, "tanpa alasan waktu (regulasi/audit/peristiwa)"
    if n == 5:
        if RE_KELAYAKAN.search(isi):
            return True, "data konkret disebut"
        return False, "tanpa bukti data konkret"
    return False, "tangga tidak dikenal"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("berkas")
    ap.add_argument("--min-lulus", type=int, default=3,
                    help="jumlah tangga minimal untuk disebut layak (default 3)")
    ap.add_argument("--json", help="tulis ringkasan JSON ke berkas ini")
    args = ap.parse_args()

    try:
        teks = open(args.berkas, encoding="utf-8").read()
    except OSError as e:
        print(f"GAGAL membaca {args.berkas}: {e}", file=sys.stderr)
        return 2

    blok = pecah_blok(teks)
    if not blok:
        print("Tidak ada blok fenomena (## F-xx) yang ditemukan.", file=sys.stderr)
        return 2

    ringkas = []
    klaim_palsu = []
    print(f"{'Fenomena':<46} {'Lulus':>6}  {'Status':<10} Catatan")
    print("-" * 100)

    for nama, isi in blok:
        tangga = ambil_tangga(isi)
        lulus, catatan = 0, []
        for n in range(1, 6):
            ok, alasan = nilai_tangga(n, tangga.get(n, ""))
            if ok:
                lulus += 1
            else:
                catatan.append(f"T{n}:{alasan}")

        m = RE_STATUS.search(isi)
        status = m.group(1).strip().upper() if m else ""
        if not status:
            status = "LULUS" if lulus >= args.min_lulus else "RAPUH"

        t5_ok = nilai_tangga(5, tangga.get(5, ""))[0]
        if "LULUS" in status and not t5_ok:
            klaim_palsu.append(nama)

        ringkas.append({"fenomena": nama, "lulus": lulus, "status": status,
                        "kurang": catatan, "tangga5_ok": t5_ok})

        tanda = "OK " if lulus >= args.min_lulus and t5_ok else "-- "
        print(f"{tanda}{nama[:42]:<42} {lulus}/5   {status:<10} {'; '.join(catatan) or 'lengkap'}")

    total = len(ringkas)
    layak = sum(1 for r in ringkas if r["lulus"] >= args.min_lulus and r["tangga5_ok"])
    print("-" * 100)
    print(f"Total: {total} fenomena | layak: {layak} | ambang: {args.min_lulus}/5")

    if klaim_palsu:
        print("\nGALAT: fenomena berikut berstatus LULUS padahal tangga 5 (kelayakan) kosong",
              file=sys.stderr)
        for n in klaim_palsu:
            print(f"  - {n}", file=sys.stderr)
        print("  Perbaiki tangga 5 atau ubah status menjadi RAPUH.", file=sys.stderr)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"total": total, "layak": layak, "min_lulus": args.min_lulus,
                       "klaim_palsu": klaim_palsu, "fenomena": ringkas}, f,
                      ensure_ascii=False, indent=2)
        print(f"JSON: {args.json}")

    return 1 if klaim_palsu else 0


if __name__ == "__main__":
    sys.exit(main())
