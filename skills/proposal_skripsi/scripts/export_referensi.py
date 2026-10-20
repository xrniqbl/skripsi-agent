#!/usr/bin/env python3
"""
export_referensi.py - Ubah matriks referensi (CSV/JSON) menjadi BibTeX, RIS,
EndNote XML, dan Daftar Pustaka siap tempel.

Input : CSV atau JSON hasil skill `paper-review`, atau daftar manual.
        Kolom yang dikenali (nama kolom tidak case-sensitive, underscore = spasi):
          title, authors/author, year, journal, volume, issue, pages,
          publisher, place, doi, url, isbn, type (journal/book/thesis/
          conference/webpage/report), abstract, keywords, notes
Output: referensi.bib, referensi.ris, referensi.xml, referensi.txt

Usage:
    python3 export_referensi.py matriks.csv --out-dir outputs/ --gaya apa
    python3 export_referensi.py matriks.csv --gaya vancouver --urutkan tahun
    python3 export_referensi.py matriks.csv --periksa           # validasi saja
    python3 export_referensi.py matriks.csv --nomor L           # penanda [L-n]

Aturan keras:
  - Field kosong TIDAK ditebak. DOI tanpa nilai tidak diisi.
  - Hanya baris yang punya judul yang diproses; baris lain dilaporkan.
  - Penomoran [L-n] mengikuti urutan akhir, bukan urutan file.
"""

import argparse
import csv
import glob
import json
import os
import re
import sys
import unicodedata
from datetime import date
from xml.sax.saxutils import escape

ALIAS = {
    "title": "title", "judul": "title", "article title": "title",
    "authors": "authors", "author": "authors", "author(s)": "authors",
    "penulis": "authors", "authors et al": "authors",
    "year": "year", "tahun": "year", "publication year": "year", "date": "year",
    "journal": "journal", "jurnal": "journal", "journal/publisher": "journal",
    "source": "journal", "journal name": "journal", "venue": "journal",
    "volume": "volume", "vol": "volume",
    "issue": "issue", "nomor": "issue", "number": "issue",
    "pages": "pages", "hal": "pages", "page": "pages", "halaman": "pages",
    "publisher": "publisher", "penerbit": "publisher",
    "place": "place", "lokasi": "place", "city": "place",
    "doi": "doi",
    "url": "url", "link": "url",
    "isbn": "isbn",
    "type": "type", "jenis": "type", "tipe": "type", "document type": "type",
    "abstract": "abstract", "ringkasan": "abstract",
    "keywords": "keywords", "kata kunci": "keywords",
    "notes": "notes", "catatan": "notes", "limitations": "notes",
}

JENIS = {
    "journal": "article", "jurnal": "article", "artikel": "article",
    "journal article": "article", "article": "article", "periodical": "article",
    "book": "book", "buku": "book", "monograph": "book",
    "chapter": "incollection", "book chapter": "incollection",
    "bab": "incollection", "in book": "incollection",
    "thesis": "phdthesis", "skripsi": "phdthesis", "thesis/disertasi": "phdthesis",
    "dissertation": "phdthesis", "disertasi": "phdthesis",
    "conference": "inproceedings", "conference paper": "inproceedings",
    "proceedings": "inproceedings", "seminar": "inproceedings",
    "report": "techreport", "laporan": "techreport", "pedoman": "techreport",
    "webpage": "misc", "website": "misc", "blog": "misc", "web": "misc",
}


def normal_kolom(k):
    k = (k or "").strip().lower()
    k = re.sub(r"[_\-]+", " ", k)
    return ALIAS.get(k, k)


def bersihkan_teks(v):
    if v is None:
        return ""
    s = unicodedata.normalize("NFKC", str(v)).strip()
    s = re.sub(r"\s+", " ", s)
    return s


def pecah_penulis(s):
    """'Smith, John; Doe, Jane' -> [('Smith','John'), ('Doe','Jane')]"""
    out = []
    for bagian_teks in re.split(r"\s*;\s*|\s+and\s+", s or ""):
        bagian = bersihkan_teks(bagian_teks)
        if not bagian:
            continue
        if "," in bagian:
            bel, nama = bagian.split(",", 1)
            out.append((bersihkan_teks(bel), bersihkan_teks(nama)))
        else:
            kata = bagian.split()
            if len(kata) == 1:
                out.append((kata[0], ""))
            else:
                out.append((kata[-1], " ".join(kata[:-1])))
    return out


def muat(path):
    if path.lower().endswith(".json"):
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            data = data.get("rows") or data.get("data") or data.get("hasil") or []
        return [{normal_kolom(k): bersihkan_teks(v) for k, v in row.items()}
                for row in data if isinstance(row, dict)]
    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        contoh = fh.readline()
    delim = "\t" if contoh.count("\t") >= max(contoh.count(","), contoh.count(";")) \
        else (";" if contoh.count(";") > contoh.count(",") else ",")
    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        return [{normal_kolom(k): bersihkan_teks(v) for k, v in row.items() if k}
                for row in csv.DictReader(fh, delimiter=delim)]


def tentukan_jenis(row):
    t = (row.get("type") or "").strip().lower()
    if t in JENIS:
        return JENIS[t]
    if row.get("journal"):
        return "article"
    if row.get("publisher"):
        return "book"
    return "misc"


def kunci_unik(row, dipakai):
    dasar = (row.get("title") or "tanpa-judul")[:40]
    dasar = re.sub(r"[^A-Za-z0-9]+", "", dasar.lower()) or "entri"
    dasar = dasar[:24]
    nama = dasar
    i = ord("a")
    while nama in dipakai:
        nama = f"{dasar}{chr(i)}"
        i += 1
    dipakai.add(nama)
    return nama


def bersihkan_doi(doi):
    doi = bersihkan_teks(doi)
    doi = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", doi, flags=re.I)
    return doi if doi.lower().startswith("10.") else ""


def ke_bibtex(rows):
    dipakai = set()
    out = ["% Dibuat oleh export_referensi.py (skill proposal-skripsi).",
           "% Field kosong tidak diisi tebakan; periksa sebelum submit.", ""]
    for row in rows:
        nama = kunci_unik(row, dipakai)
        jenis = tentukan_jenis(row)
        penulis = pecah_penulis(row.get("authors", ""))
        fields = {
            "author": " and ".join(f"{a}, {b}".strip(", ") for a, b in penulis),
            "title": row.get("title", ""),
            "year": row.get("year", "")[:4],
            "journal": row.get("journal", ""),
            "publisher": row.get("publisher", ""),
            "address": row.get("place", ""),
            "volume": row.get("volume", ""),
            "number": row.get("issue", ""),
            "pages": row.get("pages", "").replace("-", "--"),
            "doi": bersihkan_doi(row.get("doi", "")),
            "url": row.get("url", ""),
            "isbn": row.get("isbn", ""),
            "keywords": row.get("keywords", ""),
            "abstract": row.get("abstract", ""),
            "note": row.get("notes", ""),
        }
        if jenis == "phdthesis":
            _fields = {"school": row.get("publisher") or row.get("journal", "")}
        elif jenis == "inproceedings":
           _fields = {"booktitle": row.get("journal", "")}
        elif jenis == "incollection":
            _fields = {"booktitle": row.get("journal", "")}
        elif jenis == "techreport":
            _fields = {"institution": row.get("publisher", "")}
        else:
            _fields = {}
        fields.update(_fields)
        if not fields.get("title"):
            continue
        out.append(f"@{jenis}{{{nama},")
        for k in ("author", "title", "year", "journal", "booktitle", "publisher",
                  "address", "volume", "number", "pages", "doi", "url", "isbn",
                  "keywords", "abstract", "note", "school", "institution"):
            v = (fields.get(k) or "").replace("{", "").replace("}", "").strip()
            if v:
                out.append(f"  {k:<9} = {{{v}}},")
        out.append("}\n")
    return "\n".join(out)


RIS_TIPE = {"article": "JOUR", "book": "BOOK", "incollection": "CHAP",
            "inproceedings": "CONF", "phdthesis": "THES", "techreport": "RPRT",
            "misc": "GEN"}


def ke_ris(rows):
    dipakai = set()
    out = []
    for row in rows:
        if not row.get("title"):
            continue
        jenis = tentukan_jenis(row)
        nama = kunci_unik(row, dipakai)
        out.append("TY  - " + RIS_TIPE.get(jenis, "GEN"))
        for a, b in pecah_penulis(row.get("authors", "")):
            out.append(f"AU  - {b}, {a}".strip(", "))
        if jenis == "article" and row.get("journal"):
            out += [f"T2  - {row['journal']}", f"JO  - {row['journal']}"]
        elif jenis in ("inproceedings", "incollection") and row.get("journal"):
            out += [f"T2  - {row['journal']}"]
        elif jenis in ("book", "phdthesis", "techreport") and row.get("publisher"):
            out += [f"PB  - {row['publisher']}"]
        if row.get("year"):
            out.append(f"PY  - {row['year'][:4]}")
        if row.get("volume"):
            out.append(f"VL  - {row['volume']}")
        if row.get("issue"):
            out.append(f"IS  - {row['issue']}")
        if row.get("pages"):
            out.append(f"SP  - {row['pages']}")
        if row.get("place"):
            out.append(f"CY  - {row['place']}")
        doi = bersihkan_doi(row.get("doi", ""))
        if doi:
            out += [f"DO  - {doi}", f"UR  - https://doi.org/{doi}"]
        elif row.get("url"):
            out.append(f"UR  - {row['url']}")
        if row.get("abstract"):
            out.append(f"AB  - {row['abstract']}")
        if row.get("keywords"):
            out.append(f"KW  - {row['keywords']}")
        if row.get("notes"):
            out.append(f"N1  - {row['notes']}")
        out.append(f"ID  - {nama}")
        out.append("ER  - \n")
    return "\n".join(out)


def ke_endnote_xml(rows):
    dipakai = set()
    bagian = []
    for row in rows:
        if not row.get("title"):
            continue
        nama = kunci_unik(row, dipakai)
        penulis = "".join(
            f"<contributors><authors><author>{escape(f'{a}, {b}'.strip(', '))}"
            f"<role>author</role></author></authors></contributors>"
            for a, b in pecah_penulis(row.get("authors", "")))
        doi = bersihkan_doi(row.get("doi", ""))
        fields = [
            ("title", row.get("title", "")),
            ("year", row.get("year", "")[:4]),
            ("journal", row.get("journal", "")),
            ("publisher", row.get("publisher", "")),
            ("volume", row.get("volume", "")),
            ("number", row.get("issue", "")),
            ("pages", row.get("pages", "")),
            ("place", row.get("place", "")),
            ("isbn", row.get("isbn", "")),
            ("doi", doi),
            ("abstract", row.get("abstract", "")),
            ("keyword", row.get("keywords", "")),
            ("notes", row.get("notes", "")),
            ("url", row.get("url", "")),
        ]
        isi = "".join(f"<{k}>{escape(v)}</{k}>" for k, v in fields if v)
        bagian.append(
            f"<ref><contributors-count>{len(pecah_penulis(row.get('authors', '')))}"
            f"</contributors-count>{penulis}<titles>{isi}</titles></ref>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            "<xml>\n  <records>\n    " + "\n    ".join(bagian) +
            "\n  </records>\n</xml>\n")


def inisial(bel):
    return "".join(w[0] for w in bel.replace(".", "").split() if w)


def ke_teks(rows, gaya, nomor):
    out = []
    for i, row in enumerate(rows, 1):
        if not row.get("title"):
            continue
        penulis = pecah_penulis(row.get("authors", ""))
        tahun = row.get("year", "")[:4] or "n.d."
        judul = row.get("title", "")
        doi = bersihkan_doi(row.get("doi", ""))
        pref = f"[{nomor}-{i}] " if nomor else ""
        jml = len(penulis)
        if gaya == "vancouver":
            if penulis:
                if jml == 1:
                    nama = f"{penulis[0][1]} {penulis[0][0]}".strip()
                elif jml == 2:
                    nama = (f"{penulis[0][1]} {penulis[0][0]}, dan "
                            f"{penulis[1][1]} {penulis[1][0]}")
                else:
                    nama = f"{penulis[0][1]} {penulis[0][0]}, dkk."
            else:
                nama = "[tanpa penulis]"
            publikasi = (row.get("journal") or row.get("publisher") or "").strip(".")
            inti = f"{pref}{nama}. {judul}."
            if publikasi:
                inti += f" {publikasi}."
            teks = inti + (f" {tahun}." if tahun else "")
            if row.get("volume"):
                teks += f" {row['volume']}"
                if row.get("issue"):
                    teks += f"({row['issue']})"
                teks += ":"
            if row.get("pages"):
                teks += f" {row['pages']}."
            if doi:
                teks += f" doi:{doi}"
        elif gaya == "ieee":
            inisial_s = []
            for bel, depan in penulis:
                kata_depan = [w for w in depan.split() if w]
                if kata_depan:
                    gabungan = " ".join(w[0].upper() + "." for w in kata_depan)
                    inisial_s.append(f"{gabungan} {bel}")
                else:
                    inisial_s.append(bel)
            teks = (f"{pref}" + ("; ".join(inisial_s) + ", " if inisial_s else "") +
                    f'"{judul}," ')
            if row.get("journal"):
                teks += row["journal"] + ", "
            if row.get("volume"):
                teks += f"vol. {row['volume']}, "
            if row.get("issue"):
                teks += f"no. {row['issue']}, "
            if row.get("pages"):
                teks += f"pp. {row['pages']}, "
            if tahun and tahun != "n.d.":
                teks += tahun + ", "
            if doi:
                teks += f"doi: {doi}."
            teks = teks.rstrip(", ") + "."
        else:  # apa
            # penulis berisi (nama_bEL, nama_DEPAN)
            if penulis:
                if jml == 1:
                    nama = f"{penulis[0][0]}, {penulis[0][1]}".strip(", ")
                elif jml <= 20:
                    nama = ", ".join(f"{bel}, {depan}".strip(", ") for bel, depan in penulis[:-1])
                    nama += ", & " + f"{penulis[-1][0]}, {penulis[-1][1]}".strip(", ")
                else:
                    nama = (f"{penulis[0][0]}, {penulis[0][1]}, . . . "
                            f"{penulis[-1][0]}, {penulis[-1][1]}")
            else:
                nama = ""
            tahun_teks = f"({tahun})" if tahun and tahun != "n.d." else "(n.d.)"
            if row.get("journal"):
                sumber = row["journal"].strip(".")
                if row.get("volume"):
                    sumber += f", {row['volume']}"
                    if row.get("issue"):
                        sumber += f"({row['issue']})"
                if row.get("pages"):
                    sumber += f", {row['pages']}"
                if doi:
                    sumber += f". https://doi.org/{doi}"
                teks = f"{pref}{nama} {tahun_teks}. {judul}. {sumber}."
            elif row.get("publisher"):
                tempat = f"{row['place']}: " if row.get("place") else ""
                teks = f"{pref}{nama} {tahun_teks}. {judul} [Buku]. {tempat}{row['publisher']}."
                if doi:
                    teks += f" https://doi.org/{doi}"
            else:
                teks = f"{pref}{nama} {tahun_teks}. {judul}."
                if row.get("url"):
                    teks += f" {row['url']}"
        out.append(re.sub(r"\s+", " ", teks).replace("..", ".").strip())
    return "\n\n".join(out)


def validasi(rows):
    masalah = []
    for i, row in enumerate(rows, 1):
        if not row.get("title"):
            masalah.append((i, "BARIS", "tidak ada judul"))
            continue
        if not row.get("year"):
            masalah.append((i, "TAHUN", f"tahun kosong pada '{row['title'][:45]}'"))
        if not row.get("authors"):
            masalah.append((i, "PENULIS", f"penulis kosong pada '{row['title'][:45]}'"))
        if row.get("doi") and not bersihkan_doi(row["doi"]):
            masalah.append((i, "DOI", f"DOI tidak valid: '{row['doi']}' pada '{row['title'][:40]}'"))
    return masalah


def main():
    ap = argparse.ArgumentParser(description="Ekspor matriks referensi ke BibTeX/RIS/EndNote/teks")
    ap.add_argument("matriks", nargs="+")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--nama", default="referensi")
    ap.add_argument("--gaya", default="apa", choices=["apa", "vancouver", "ieee"])
    ap.add_argument("--urutkan", default="tahun",
                    choices=["tahun", "penulis", "judul", "input"],
                    help="urutan Daftar Pustaka")
    ap.add_argument("--nomor", default="L", help="awalan penanda, mis. L atau P; kosongkan dengan ''")
    ap.add_argument("--periksa", action="store_true", help="hanya validasi, tanpa menulis berkas")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    rows = []
    for m in args.matriks:
        for f in sorted(glob.glob(m)) or [m]:
            rows += muat(f)
    rows = [r for r in rows if r.get("title")]
    if not rows:
        sys.exit("ERROR: tidak ada baris dengan judul pada berkas Masukan")
    if args.urutkan == "tahun":
        rows.sort(key=lambda r: (r.get("year", "9999") or "9999", r.get("title", "").lower()))
    elif args.urutkan == "penulis":
        rows.sort(key=lambda r: (pecah_penulis(r.get("authors", "")) or [("", "")])[0][0].lower())
    elif args.urutkan == "judul":
        rows.sort(key=lambda r: r.get("title", "").lower())

    masalah = validasi(rows)
    for i, kode, pesan in masalah:
        print(f"[WARN] baris {i} {kode}: {pesan}", file=sys.stderr)
    if args.periksa:
        print(f"\n{len(rows)} entris diperiksa; {len(masalah)} masalah.")
        return 1 if masalah else 0

    os.makedirs(args.out_dir, exist_ok=True)
    keluaran = {
        args.nama + ".bib": ke_bibtex(rows),
        args.nama + ".ris": ke_ris(rows),
        args.nama + ".xml": ke_endnote_xml(rows),
        args.nama + ".txt": "# DAFTAR PUSTAKA\n\n" + ke_teks(rows, args.gaya, args.nomor) + "\n",
    }
    for nama, isi in keluaran.items():
        jalan = os.path.join(args.out_dir, nama)
        with open(jalan, "w", encoding="utf-8") as fh:
            fh.write(isi)
        if not args.quiet:
            print(f"Tulis: {jalan}")
    if not args.quiet:
        print(f"\n{len(rows)} entri, gaya {args.gaya.upper()}, diurutkan {args.urutkan}, "
              f"{len(masalah)} field perlu diperiksa.")
        print("Periksa entri tanpa DOI atau tanpa penulis sebelum submit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
