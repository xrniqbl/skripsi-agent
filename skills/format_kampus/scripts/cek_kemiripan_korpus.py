#!/usr/bin/env python3
"""Indeks kemiripan terhadap korpus abstrak skripsi Indonesia.

Pemakaian:
    python3 cek_kemiripan_korpus.py --bangun-indeks korpus/teks --keluaran indeks.json
    python3 cek_kemiripan_korpus.py naskah.md --indeks indeks.json
    python3 cek_kemiripan_korpus.py skripsi.docx --indeks indeks.json --min-kata 8 --md lap.md

Kenapa skrip ini ada: `plagiarism_check.py` hanya membandingkan dengan berkas
sumber yang sudah diunduh. Padahal pola yang paling sering lolos Turnitin
kampus adalah kalimat yang dipinjam antar-repositori skripsi — bukan dari
jurnal, bukan dari internet bebas, tetapi dari skripsi kakak tingkat di kampus
lain. Indeks korpus menangkap kelas itu.

Cara kerja:

- Ekstraksi: setiap dokumen korpus dipotong menjadi shingle N-kata pada
  tingkat kalimat, dinormalkan (huruf kecil, angka dipertahankan, tanda baca
  dibuang).
- Indeks: hash 64-bit setiap shingle -> daftar (dokumen, posisi). Disimpan
  sebagai JSON. Yang disimpan HANYA hash dan DOI/judul sumber, bukan teks
  penuh — PDF aslinya tidak pernah ikut ke repo.
- Pencarian: shingle naskah di-hash dan dicocokkan; kecocokan berurutan
  digabung menjadi kutipan terpanjang, lalu dilaporkan dengan dokumen asal.

Angka kemiripan = persentase shingle naskah yang ditemukan di korpus. Ini
indikator, BUKAN skor Turnitin: korpus lokal hanya 18 dokumen, sementara
Turnitin membandingkan miliaran halaman.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

RE_KATA = re.compile(r"[a-z0-9]+")
KALIMAT = re.compile(r"(?<=[.!?])\s+|\n+")


def normal(teks: str) -> list[str]:
    return RE_KATA.findall(teks.lower())


def shingles(kata: list[str], n: int) -> list[tuple[int, int]]:
    """[(hash, posisi_awal)] untuk setiap jendela n kata."""
    out = []
    for i in range(len(kata) - n + 1):
        jendela = " ".join(kata[i:i + n])
        h = int.from_bytes(hashlib.blake2b(jendela.encode(), digest_size=8).digest(),
                           "big")
        out.append((h, i))
    return out


def baca_teks(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            sys.exit("GAGAL: butuh python-docx untuk .docx")
        d = Document(path)
        return "\n".join(p.text for p in d.paragraphs)
    if ext == ".pdf":
        import subprocess
        return subprocess.run(["pdftotext", "-layout", path, "-"],
                              capture_output=True, text=True).stdout
    with open(path, encoding="utf8", errors="replace") as f:
        return f.read()


def bangun_indeks(folder: str, n: int) -> dict:
    indeks: dict[str, list[list]] = {}
    dokumen = []
    for nama in sorted(os.listdir(folder)):
        path = os.path.join(folder, nama)
        if not os.path.isfile(path):
            continue
        teks = baca_teks(path)
        kata = normal(teks)
        if len(kata) < n * 3:
            continue
        for h, pos in shingles(kata, n):
            indeks.setdefault(str(h), []).append([nama, pos])
        dokumen.append({"id": nama, "kata": len(kata)})
    return {"n": n, "dokumen": dokumen, "shingle": indeks}


def periksa(naskah: str, indeks: dict, n: int, min_kata: int) -> dict:
    kata = normal(naskah)
    sh = shingles(kata, n)
    hash_indeks = indeks["shingle"]
    temuan = []          # (posisi, panjang, dokumen)
    i = 0
    while i < len(sh):
        h, pos = sh[i]
        asal = hash_indeks.get(str(h))
        if not asal:
            i += 1
            continue
        # perluas ke kanan selama shingle berikutnya juga cocok dengan dokumen sama
        panjang = 1
        dok_cocok = {d for d, _ in asal}
        while i + panjang < len(sh):
            h2, _ = sh[i + panjang]
            asal2 = hash_indeks.get(str(h2))
            if not asal2:
                break
            dok2 = {d for d, _ in asal2}
            if not (dok_cocok & dok2):
                break
            panjang += 1
            dok_cocok &= dok2
        total_kata = panjang + n - 1
        if total_kata >= min_kata:
            temuan.append({
                "posisi_kata": pos,
                "kata": total_kata,
                "dokumen": sorted(dok_cocok)[:3],
                "kutipan": " ".join(kata[pos:pos + min(total_kata, 25)]) + " ...",
            })
        i += max(1, panjang)

    cakupan = set()
    for t in temuan:
        cakupan.update(range(t["posisi_kata"], t["posisi_kata"] + t["kata"]))
    persen = (len(cakupan) / len(kata) * 100) if kata else 0.0
    return {"total_kata": len(kata), "shingle_n": n,
            "shingle_naskah": len(sh), "temuan": temuan,
            "persen": round(persen, 2)}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Indeks & pemeriksa kemiripan naskah terhadap korpus lokal.")
    ap.add_argument("naskah", nargs="?", help="naskah yang diperiksa")
    ap.add_argument("--bangun-indeks", metavar="FOLDER",
                    help="bangun indeks dari folder teks korpus")
    ap.add_argument("--keluaran", default="indeks_korpus.json")
    ap.add_argument("--indeks", help="indeks JSON untuk pemeriksaan")
    ap.add_argument("--min-kata", type=int, default=7,
                    help="panjang frasa minimum yang dilaporkan (default 7)")
    ap.add_argument("--n", type=int, default=5, help="ukuran shingle (default 5)")
    ap.add_argument("--md", help="tulis laporan Markdown")
    ap.add_argument("--ketat", action="store_true",
                    help="keluar kode 1 bila ada temuan")
    a = ap.parse_args()

    if a.bangun_indeks:
        if not os.path.isdir(a.bangun_indeks):
            print(f"GAGAL: folder tidak ada: {a.bangun_indeks}", file=sys.stderr)
            return 2
        indeks = bangun_indeks(a.bangun_indeks, a.n)
        with open(a.keluaran, "w", encoding="utf8") as f:
            json.dump(indeks, f, ensure_ascii=False)
        print(f"indeks dibangun: {len(indeks['dokumen'])} dokumen, "
              f"{len(indeks['shingle'])} shingle unik -> {a.keluaran}")
        for d in indeks["dokumen"]:
            print(f"  {d['id']:28} {d['kata']:>7} kata")
        return 0

    if not a.naskah or not a.indeks:
        print("GAGAL: butuh NASKAH dan --indeks (atau pakai --bangun-indeks)",
              file=sys.stderr)
        return 2
    if not os.path.isfile(a.naskah) or not os.path.isfile(a.indeks):
        print("GAGAL: berkas naskah atau indeks tidak ada", file=sys.stderr)
        return 2

    # indeks boleh .json.gz (bentuk yang disimpan di repo supaya tidak 9 MB)
    if a.indeks.endswith(".gz"):
        import gzip
        with gzip.open(a.indeks, "rt", encoding="utf8") as f:
            indeks = json.load(f)
    else:
        with open(a.indeks, encoding="utf8") as f:
            indeks = json.load(f)
    n = int(indeks.get("n") or a.n)
    hasil = periksa(baca_teks(a.naskah), indeks, n, a.min_kata)

    print(f"=== Kemiripan terhadap korpus ===")
    print(f"  naskah   : {os.path.basename(a.naskah)}")
    print(f"  korpus   : {len(indeks['dokumen'])} dokumen, shingle n={n}")
    print(f"  kata     : {hasil['total_kata']}")
    print(f"  kemiripan: {hasil['persen']}% dari kata naskah")
    for t in sorted(hasil["temuan"], key=lambda x: -x["kata"])[:12]:
        print(f"   - {t['kata']:>3} kata @kata-{t['posisi_kata']:>6}  "
              f"{', '.join(t['dokumen'])}")
        print(f"     \"{t['kutipan']}\"")
    if a.md:
        with open(a.md, "w", encoding="utf8") as f:
            f.write(f"# Laporan Kemiripan Korpus\n\n"
                    f"- Naskah: `{os.path.basename(a.naskah)}`\n"
                    f"- Korpus: {len(indeks['dokumen'])} dokumen (shingle n={n})\n"
                    f"- Kemiripan: **{hasil['persen']}%** dari "
                    f"{hasil['total_kata']} kata\n\n## Temuan\n\n")
            for t in sorted(hasil["temuan"], key=lambda x: -x["kata"]):
                f.write(f"- **{t['kata']} kata** (posisi {t['posisi_kata']}) — "
                        f"{', '.join(t['dokumen'])}\n  > {t['kutipan']}\n")
        print(f"\nlaporan: {a.md}")
    if a.ketat and hasil["temuan"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
