#!/usr/bin/env python3
"""
code_interview.py - Koding transkrip wawancara menjadi tabel kode untuk BAB III.

Alur kerja:
  1. codebook   : buat daftar kode (dari CSV atau dari pedoman manual)
  2. apply      : beri kode pada transkrip berdasarkan codebook
  3. report     : tabel kode, frekuensi, dan cuplikan untuk dilampirkan
  4. merge      : gabungkan beberapa hasil pengodean

Format transkrip yang diharapkan (satu berkas per partisipan):
    [P01] Wawancara dengan peserta 1, 2026-03-04
    Partisipan 1
    Petugas: Apa yang Anda rasakan ketika harus menyusun laporan harian?
    Peserta:  Saya sering menunda, karena tidak ada alasan yang jelas.

Format codebook CSV:
    kode;kategori;tema;definisi
    M1;Motivasi ekstrinsik;Motivasi kerja;Pendorong dari imbalan luar

Ayat diberi kode bila mengandung salah satu kata kunci pada kode, atau bila
pola regex pada kolom `pola` cocok. Kata kunci dipisah tanda `|`.

Usage:
    python3 code_interview.py codebook tests/codebook_contoh.csv \\
        --transkrip tests/transkrip_contoh.md --out outputs/hasil_koding
    python3 code_interview.py report outputs/hasil_koding.json
    python3 code_interview.py merge a.json b.json -o gabungan.json

Perhatian:
  - Tool ini membantu pengodean, bukan menggantikan Analisis peneliti.
  - Verifikasi setiap kode sebelum dipakai; jangan dilaporkan sebagai temuan apa adanya.
"""

import argparse
import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

STOP = {
    "ya", "iya", "yaa", "tidak", "bukan", "oke", "baik", "yaudah", "betul",
    "saya", "saya_pun", "kamu", "anda", "di", "ke", "dari", "yang", "dan",
    "dengan", "untuk", "pada", "itu", "ini", "saya", "aja", "sih", "deh",
    "lah", "kok", "gitu", "seperti", "banget", "agak", "lebih", "sudah",
}


def bersihkan(teks):
    teks = teks.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", teks).strip()


def muat_codebook(path):
    kode = []
    with open(path, "r", encoding="utf-8-sig") as fh:
        contoh = fh.readline()
    delim = ";" if contoh.count(";") >= contoh.count(",") else ","
    with open(path, "r", encoding="utf-8-sig") as fh:
        for i, row in enumerate(csv.DictReader(fh, delimiter=delim), 1):
            kolom = { (k or "").strip().lower(): (v or "").strip()
                      for k, v in row.items() if k }
            nk = kolom.get("kode") or kolom.get("code") or kolom.get("id")
            if not nk:
                continue
            kata = kolom.get("kata_kunci") or kolom.get("kata") or kolom.get("keyword") or ""
            kode.append({
                "kode": nk.strip(),
                "kategori": kolom.get("kategori") or kolom.get("category") or "-",
                "tema": kolom.get("tema") or kolom.get("theme") or "-",
                "definisi": kolom.get("definisi") or kolom.get("definition") or "",
                "kata_kunci": [k.strip().lower() for k in kata.split("|") if k.strip()],
                "pola": kolom.get("pola") or kolom.get("regex") or "",
                "baris": i,
            })
    return kode


def muat_transkrip(path):
    """Baca transkrip: kembalikan (peserta,HEADER, [ (id, utc, peran, teks) ])."""
    if os.path.isdir(path):
        berkas = sorted(glob.glob(os.path.join(path, "*.md")) +
                        glob.glob(os.path.join(path, "*.txt")))
    else:
        berkas = [path]
    hasil = []
    for f in berkas:
        if not os.path.isfile(f):
            continue
        with open(f, "r", encoding="utf-8", errors="replace") as fh:
            isi = fh.read()
        header = re.findall(r"^#+\s*(.+)$", isi, re.M)
        peserta = "unknown"
        for h in header:
            m = re.search(r"P(\d+)|partisipan\s+(\d+)", h, re.I)
            if m:
                peserta = m.group(1) or m.group(2)
                break
        if peserta == "unknown":
            peserta = re.sub(r"\W+", "_", os.path.splitext(os.path.basename(f))[0])[:20]
        baris = []
        for no, l in enumerate(isi.split("\n"), 1):
            if not l.strip() or l.strip().startswith("#"):
                continue
            m = re.match(r"^\s*(?:\**)?([^:]{1,24}?)\s*:\s*(.+)$", l)
            if m:
                peran = bersihkan(m.group(1))
                teks = bersihkan(m.group(2))
            else:
                peran = "Peserta"
                teks = bersihkan(l)
            if peran.lower() in STOP:
                continue
            baris.append({"id": f"{peserta}-{no:03d}", "baris": no,
                          "utc": f"baris {no}", "peran": peran, "teks": teks})
        hasil.append({"peserta": peserta, "sumber": os.path.abspath(f),
                      "header": header, "unit": baris})
    return hasil


def token(teks):
    return set(re.findall(r"[a-z]+", teks.lower()))


def cocok(unit, k):
    t = token(unit["teks"])
    if k["pola"]:
        try:
            if re.search(k["pola"], unit["teks"], re.I):
                return True
        except re.error:
            print(f"PERINGATAN: pola tidak valid pada kode {k['kode']}: {k['pola']}",
                  file=sys.stderr)
    for kata in k["kata_kunci"]:
        kata = kata.lower()
        if " " in kata:
            if kata in unit["teks"].lower():
                return True
        elif kata in t:
            return True
    return False


def koding(transkrip, codebook, min_kata=4):
    for tr in transkrip:
        tr["unit_kode"] = []
        for unit in tr["unit"]:
            unit["kode"] = [k for k in codebook if cocok(unit, k)]
            tr["unit_kode"].append(unit)
    return transkrip


def ringkas(transkrip, codebook):
    freq = Counter()
    per_kategori = defaultdict(Counter)
    per_tema = defaultdict(Counter)
    peta = {}
    for tr in transkrip:
        for unit in tr.get("unit_kode", []):
            if not unit["kode"]:
                continue
            for k in unit["kode"]:
                freq[k["kode"]] += 1
                per_kategori[k["kategori"]][k["kode"]] += 1
                per_tema[k["tema"]][k["kode"]] += 1
                peta.setdefault(k["kode"], []).append({
                    "peserta": tr["peserta"], "unit": unit["id"],
                    "waktu": unit["utc"], "cuplikan": unit["teks"],
                })
    tabel = []
    for k in codebook:
        n = freq.get(k["kode"], 0)
        tabel.append({"kode": k["kode"], "kategori": k["kategori"], "tema": k["tema"],
                      "definisi": k["definisi"], "jumlah_unit": n,
                      "cuplikan": peta.get(k["kode"], [])})
    return tabel, dict(per_kategori), dict(per_tema), freq


def render(hasil, kode_aktif=None):
    tabel, per_kategori, per_tema, freq = hasil["tabel"]
    out = ["# Tabel Kode Analisis Kualitatif - Siap Tempel ke BAB III\n",
           f"Partisipan: **{len(hasil['transkrip'])}** | Unit ter kode: "
           f"**{sum(freq.values())}** | Kode aktif: **{sum(1 for t in tabel if t['jumlah_unit'])}** "
           f"dari {len(tabel)} | dibuat {hasil['meta']['waktu']}\n",
           "> Angka di bawah dihitung dari transkrip yang diinput. Kode bercuplikan 0 berarti "
           "kata kunci tidak muncul; periksa manual sebelum melaporkan.\n",
           "## Tabel Kode\n",
           "| Kode | Kategori | Tema | Jumlah unit | Cuplikan |",
           "|------|----------|------|--------------|----------|"]
    for t in tabel:
        if kode_aktif and t["kode"] not in kode_aktif:
            continue
        contoh = t["cuplikan"][0]["cuplikan"][:90] if t["cuplikan"] else "-"
        out.append(f"| {t['kode']} | {t['kategori']} | {t['tema']} | {t['jumlah_unit']} "
                   f"| {contoh} |")
    out.append("\n## Ringkasan per Tema\n")
    for tema, kode_tema in sorted(per_tema.items()):
        total = sum(kode_tema.values())
        detail = ", ".join(f"{k}={v}" for k, v in kode_tema.most_common())
        out.append(f"- **{tema}** (total unit {total}): {detail}")
    out.append("\n## Ringkasan per Kategori\n")
    for kat, kode_kat in sorted(per_kategori.items()):
        total = sum(kode_kat.values())
        out.append(f"- **{kat}** (total unit {total})")
    out.append("\n## Cuplikan per Kode\n")
    for t in tabel:
        if not t["cuplikan"]:
            continue
        out.append(f"\n### {t['kode']} - {t['kategori']} ({t['jumlah_unit']} unit)\n")
        if t["definisi"]:
            out.append(f"Definisi: {t['definisi']}\n")
        for c in t["cuplikan"][:5]:
            out.append(f"- `[K-{c['peserta']}: {c['waktu']}]` \"{c['cuplikan']}\"")
    out.append("\n> Penanda sumber kualitatif memakai format `[K-peserta:waktu]`. "
               "Nama asli peserta tidak boleh ditulis di naskah.\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Koding transkrip wawancara")
    sub = ap.add_subparsers(dest="perintah", required=True)

    p1 = sub.add_parser("apply", help="koding transkrip dengan codebook")
    p1.add_argument("codebook")
    p1.add_argument("--transkrip", required=True, help="berkas atau folder transkrip")
    p1.add_argument("--out", default="hasil_koding")
    p1.add_argument("--kode", help="batasi hanya kode tertentu, pisahkan koma")
    p1.add_argument("--tanpa-md", action="store_true")

    p2 = sub.add_parser("report", help="tulis ulang laporan dari JSON")
    p2.add_argument("json")
    p2.add_argument("--out")
    p2.add_argument("--kode")

    p3 = sub.add_parser("merge", help="gabungkan beberapa JSON pengodean")
    p3.add_argument("json", nargs="+")
    p3.add_argument("-o", "--out", required=True)

    args = ap.parse_args()

    if args.perintah == "merge":
        gabung = []
        for f in args.json:
            with open(f, "r", encoding="utf-8") as fh:
                gabung += json.load(fh)["transkrip"]
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"transkrip": gabung}, fh, ensure_ascii=False, indent=2)
        print(f"Tulis: {args.out} ({len(gabung)} transkrip)", file=sys.stderr)
        return 0

    if args.perintah == "apply":
        if not os.path.exists(args.codebook):
            sys.exit(f"ERROR: codebook tidak ditemukan: {args.codebook}")
        codebook = muat_codebook(args.codebook)
        if not codebook:
            sys.exit("ERROR: codebook kosong atau kolom 'kode' tidak terbaca")
        transkrip = muat_transkrip(args.transkrip)
        if not transkrip:
            sys.exit(f"ERROR: tidak ada transkrip di {args.transkrip}")
        hasil_koding = koding(transkrip, codebook)
        tabel, per_kategori, per_tema, freq = ringkas(hasil_koding, codebook)
        meta = {"codebook": os.path.abspath(args.codebook), "kode_input": len(codebook),
                "transkrip_input": [t["sumber"] for t in hasil_koding],
                "waktu": datetime.now().isoformat(timespec="seconds")}
        data = {"meta": meta, "transkrip": hasil_koding, "tabel": tabel}
        with open(args.out + ".json", "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        print(f"Tulis: {args.out}.json", file=sys.stderr)
        if not args.tanpa_md:
            with open(args.out + ".md", "w", encoding="utf-8") as fh:
                fh.write(render({"meta": meta, "transkrip": hasil_koding,
                                 "tabel": (tabel, per_kategori, per_tema, freq)},
                                args.kode))
            print(f"Tulis: {args.out}.md", file=sys.stderr)
        kode_aktif = args.kode.split(",") if args.kode else None
        print(render({"meta": meta, "transkrip": hasil_koding,
                      "tabel": (tabel, per_kategori, per_tema, freq)}, kode_aktif))
        return 0

    if args.perintah == "report":
        with open(args.json, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        freq = Counter()
        per_kategori, per_tema = defaultdict(Counter), defaultdict(Counter)
        for t in data["tabel"]:
            freq[t["kode"]] = t["jumlah_unit"]
            per_kategori[t["kategori"]][t["kode"]] = t["jumlah_unit"]
            per_tema[t["tema"]][t["kode"]] = t["jumlah_unit"]
        isi = render({"meta": data["meta"], "transkrip": data["transkrip"],
                      "tabel": (data["tabel"], dict(per_kategori), dict(per_tema), freq)},
                     args.kode.split(",") if args.kode else None)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(isi)
            print(f"Tulis: {args.out}", file=sys.stderr)
        print(isi)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
