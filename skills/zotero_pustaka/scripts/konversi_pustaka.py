#!/usr/bin/env python3
"""
konversi_pustaka.py - Semua format masuk -> CSL-JSON, lalu deduplikasi.

Format yang dikenali (deteksi otomatis dari isi berkas, bukan dari ekstensi):
    BibTeX          @article{ ... }
    RIS             TY  - JOUR
    Zotero JSON     [{"itemType": ..., "title": ...}]   (ekspor Zotero 7)
    CSL-JSON        [{"type": ..., "id": ...}]
    Haystack        judul\\tpenulis\\ttahun\\t...          (ekspor pustaka lain)

Pemakaian:
    python3 konversi_pustaka.py pustaka.bib --out pustaka.csl.json
    python3 konversi_pustaka.py *.ris --gabung --out semua.csl.json
    python3 konversi_pustaka.py zotero-export.json --out pustaka.csl.json
    python3 konversi_pustaka.py pustaka.bib --periksa          # laporan saja

Deduplikasi:
    Kunci pertama DOI (huruf kecil, tanpa prefiks URL), lalu judul ternormalisasi
    + tahun. Entri duplikat TIDAK dibuang diam-diam: yang pertama dipertahankan,
    sisanya dilaporkan dengan sumbernya. Nomor ganda pada gaya numerik (IEEE,
    Vancouver) adalah akibat langsung duplikat yang lolos.

Kode keluar:
    0  berhasil
    1  ada berkas gagal dibaca / nol entri
    2  argumen salah
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------------------
# Pemetaan tipe
# ---------------------------------------------------------------------------
BIBTEX_TO_CSL = {
    "article": "article-journal",
    "inproceedings": "paper-conference",
    "conference": "paper-conference",
    "proceedings": "book",
    "book": "book",
    "booklet": "pamphlet",
    "incollection": "chapter",
    "inbook": "chapter",
    "phdthesis": "thesis",
    "mastersthesis": "thesis",
    "bachelorsthesis": "thesis",
    "techreport": "report",
    "manual": "book",
    "misc": "document",
    "online": "webpage",
    "electronic": "webpage",
    "www": "webpage",
    "unpublished": "manuscript",
    "patent": "patent",
    "standard": "standard",
    "dataset": "dataset",
    "software": "software",
}

RIS_TO_CSL = {
    "JOUR": "article-journal",
    "JFULL": "article-journal",
    "EJOUR": "article-journal",
    "MGZN": "article-magazine",
    "NEWS": "article-newspaper",
    "BOOK": "book",
    "EBOOK": "book",
    "CHAP": "chapter",
    "CONF": "paper-conference",
    "CPAPER": "paper-conference",
    "THES": "thesis",
    "RPRT": "report",
    "ELEC": "webpage",
    "WEB": "webpage",
    "BLOG": "post-weblog",
    "GEN": "document",
    "DATA": "dataset",
    "COMP": "software",
    "PAT": "patent",
    "STAND": "standard",
    "UNPB": "manuscript",
    "MANSCPT": "manuscript",
    "MAP": "map",
    "VIDEO": "motion_picture",
    "SOUND": "song",
    "ART": "graphic",
    "PAMP": "pamphlet",
}

# Field BibTeX -> CSL
BIBTEX_FIELDS = {
    "title": "title",
    "journal": "container-title",
    "journaltitle": "container-title",
    "booktitle": "container-title",
    "series": "collection-title",
    "publisher": "publisher",
    "address": "publisher-place",
    "location": "publisher-place",
    "volume": "volume",
    "number": "issue",
    "issue": "issue",
    "pages": "page",
    "doi": "DOI",
    "url": "URL",
    "isbn": "ISBN",
    "issn": "ISSN",
    "abstract": "abstract",
    "keywords": "keyword",
    "language": "language",
    "edition": "edition",
    "note": "note",
    "chapter": "chapter-number",
    "school": "publisher",
    "institution": "publisher",
    "organization": "publisher",
    "howpublished": "medium",
    "type": "genre",
    "eprint": "note",
}

# Field RIS -> CSL
RIS_FIELDS = {
    "TI": "title", "T1": "title",
    "JO": "container-title", "JF": "container-title", "T2": "container-title",
    "JA": "container-title-short",
    "T3": "collection-title",
    "PB": "publisher",
    "CY": "publisher-place", "PP": "publisher-place",
    "VL": "volume",
    "IS": "issue",
    "SP": "page", "EP": None,           # EP digabung ke SP
    "DO": "DOI",
    "UR": "URL",
    "SN": "ISSN", "SN2": "ISBN",
    "AB": "abstract", "N2": "abstract",
    "KW": "keyword",
    "LA": "language",
    "ET": "edition",
    "M3": "genre",
    "DB": "archive",
}


# ---------------------------------------------------------------------------
def _bersih_judul(s: str) -> str:
    """Buang markup BibTeX ({}) dan normalisasi spasi."""
    if not s:
        return ""
    s = re.sub(r"[{}]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _unescape_latex(s: str) -> str:
    """
    BibTeX menyimpan karakter khusus dalam bentuk escape LaTeX. Tanpa ini,
    'R\\&D' tercetak apa adanya di Daftar Pustaka dan terbaca sebagai salah
    ketik, bukan sebagai judul buku.
    """
    if not s:
        return s
    ganti = {
        r"\&": "&", r"\%": "%", r"\$": "$", r"\#": "#", r"\_": "_",
        r"\{": "{", r"\}": "}", r"\textasciitilde": "~",
        r"\textbackslash": "\\", r"~": " ", r"--": "–", r"---": "—",
        r"\textendash": "–", r"\textemdash": "—",
        r"\'{e}": "é", r"\'{a}": "á", r"\'{i}": "í", r"\'{o}": "ó",
        r"\'{u}": "ú", r'\"{o}': "ö", r'\"{u}': "ü", r'\"{a}': "ä",
        r"\c{c}": "ç", r"\~{n}": "ñ",
    }
    for a, b in ganti.items():
        s = s.replace(a, b)
    # akses khusus LaTeX yang tersisa: \textit{x} -> x
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)
    return s


def _tahun_dari(s: str | None) -> dict | None:
    if not s:
        return None
    m = re.search(r"(\d{4})", str(s))
    return {"date-parts": [[int(m.group(1))]]} if m else None


def _pisah_penulis_bibtex(s: str) -> list:
    """'Harris, Charles R. and Millman, K. Jarrod' -> list CSL."""
    out = []
    for bagian in re.split(r"\s+and\s+", s or ""):
        bagian = bagian.strip().strip("{}")
        if not bagian:
            continue
        if "," in bagian:
            fam, _, giv = bagian.partition(",")
            out.append({"family": _bersih_judul(fam), "given": _bersih_judul(giv)})
        else:
            potong = bagian.split()
            if len(potong) == 1:
                out.append({"literal": bagian})
            else:
                out.append({"family": potong[-1], "given": " ".join(potong[:-1])})
    return out


def _pisah_penulis_ris(daftar: list) -> list:
    """RIS: 'Harris, Charles R.' atau 'Harris CR' atau nama organisasi."""
    out = []
    for a in daftar:
        a = a.strip().rstrip(".,")
        if not a:
            continue
        if "," in a:
            fam, _, giv = a.partition(",")
            out.append({"family": fam.strip(), "given": giv.strip()})
        else:
            potong = a.split()
            if len(potong) == 1:
                out.append({"literal": a})
            else:
                out.append({"family": potong[-1], "given": " ".join(potong[:-1])})
    return out


# ---------------------------------------------------------------------------
# Pembaca per format
# ---------------------------------------------------------------------------
def baca_bibtex(teks: str) -> tuple[list, list]:
    """Kembalikan (items, masalah). bibtexparser 2.x; jatuh ke parser mini bila absen."""
    masalah = []
    try:
        import bibtexparser
    except ImportError:
        return _baca_bibtex_mini(teks), masalah

    lib = bibtexparser.parse_string(teks)
    items = []
    for e in lib.entries:
        f = {k.lower(): v.value for k, v in e.fields_dict.items()}
        it = {"id": e.key or f.get("title", "")[:20],
              "type": BIBTEX_TO_CSL.get(e.entry_type, "document"),
              "_sumber": "bibtex"}
        for k, v in f.items():
            dst = BIBTEX_FIELDS.get(k)
            if dst and v:
                bersih = _unescape_latex(_bersih_judul(v)) if dst in (
                    "title", "container-title", "publisher", "publisher-place",
                    "collection-title", "abstract") else v
                it[dst] = bersih
        if f.get("author"):
            it["author"] = _pisah_penulis_bibtex(f["author"])
        elif f.get("editor"):
            it["editor"] = _pisah_penulis_bibtex(f["editor"])
        if f.get("year"):
            d = _tahun_dari(f["year"])
            if d:
                it["issued"] = d
        if it.get("page"):
            it["page"] = it["page"].replace("--", "-").replace("–", "-")
        items.append(it)
    for blok in getattr(lib, "failed_blocks", []):
        masalah.append(f"blok gagal diparse: {str(blok)[:120]}")
    return items, masalah


def _baca_bibtex_mini(teks: str) -> list:
    """Parser BibTeX minimal: cukup untuk entri normal, bukan untuk korpus besar."""
    items = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", teks):
        tipe, key = m.group(1).lower(), m.group(2)
        mulai = m.end()
        kedalaman = 1
        i = mulai
        while i < len(teks) and kedalaman:
            if teks[i] == "{":
                kedalaman += 1
            elif teks[i] == "}":
                kedalaman -= 1
            i += 1
        badan = teks[mulai:i - 1]
        f = {}
        for fm in re.finditer(r"(\w+)\s*=\s*\{", badan):
            nm = fm.group(1).lower()
            j = fm.end()
            d = 1
            while j < len(badan) and d:
                if badan[j] == "{":
                    d += 1
                elif badan[j] == "}":
                    d -= 1
                j += 1
            f[nm] = badan[fm.end():j - 1].strip()
        if tipe in ("comment", "string", "preamble"):
            continue
        it = {"id": key, "type": BIBTEX_TO_CSL.get(tipe, "document"), "_sumber": "bibtex"}
        for k, v in f.items():
            dst = BIBTEX_FIELDS.get(k)
            if dst and v:
                bersih = _unescape_latex(_bersih_judul(v)) if dst in (
                    "title", "container-title", "publisher", "publisher-place",
                    "collection-title", "abstract") else v
                it[dst] = bersih
        if f.get("author"):
            it["author"] = _pisah_penulis_bibtex(f["author"])
        if f.get("year"):
            d = _tahun_dari(f["year"])
            if d:
                it["issued"] = d
        items.append(it)
    return items


def baca_ris(teks: str) -> tuple[list, list]:
    items, masalah = [], []
    sekarang = None
    penulis: list = []

    def tutup():
        nonlocal sekarang, penulis
        if sekarang is None:
            return
        if penulis:
            sekarang["author"] = _pisah_penulis_ris(penulis)
        if sekarang.get("_sp") and sekarang.get("_ep"):
            sekarang["page"] = f"{sekarang['_sp']}-{sekarang['_ep']}"
        elif sekarang.get("_sp"):
            sekarang["page"] = sekarang["_sp"]
        for k in ("_sp", "_ep", "_er", "_da"):
            sekarang.pop(k, None)
        items.append(sekarang)
        sekarang, penulis = None, []

    for baris in teks.splitlines():
        if not baris.strip():
            if sekarang is not None:
                tutup()
            continue
        m = re.match(r"^([A-Z][A-Z0-9])\s{1,2}-\s?(.*)$", baris)
        if not m:
            continue
        tag, isi = m.group(1), m.group(2).strip()
        if tag == "TY":
            tutup()
            sekarang = {"id": f"ris{len(items)+1}",
                        "type": RIS_TO_CSL.get(isi.upper(), "document"),
                        "_sumber": "ris"}
            continue
        if tag == "ER":
            tutup()
            continue
        if sekarang is None:
            continue
        if tag in ("AU", "A1"):
            penulis.append(isi)
            continue
        if tag in ("A2", "ED"):
            sekarang.setdefault("editor", []).extend(_pisah_penulis_ris([isi]))
            continue
        if tag == "PY" or tag == "Y1":
            d = _tahun_dari(isi)
            if d:
                sekarang["issued"] = d
            continue
        if tag == "SP":
            sekarang["_sp"] = isi
            continue
        if tag == "EP":
            sekarang["_ep"] = isi
            continue
        if tag == "ID":
            sekarang["id"] = isi
            continue
        dst = RIS_FIELDS.get(tag)
        if dst:
            if dst == "keyword":
                sekarang["keyword"] = (sekarang.get("keyword", "") + "; " + isi).strip("; ")
            elif dst in ("title", "container-title"):
                sekarang[dst] = _bersih_judul(isi)
            else:
                sekarang.setdefault(dst, isi)
    tutup()
    if not items:
        masalah.append("tidak ada record TY/ER yang terbaca")
    return items, masalah


def baca_zotero_json(data) -> tuple[list, list]:
    items, masalah = [], []
    if isinstance(data, dict) and "items" in data:
        data = data["items"]
    if not isinstance(data, list):
        return [], ["struktur JSON bukan daftar item"]
    for it in data:
        if not isinstance(it, dict):
            continue
        if "itemType" in it or "data" in it:
            d = it.get("data", it)
            csl = zotero_item_ke_csl(d)
            if csl:
                items.append(csl)
            elif d.get("itemType") not in ("attachment", "note", "annotation"):
                masalah.append(f"tipe tak terpetakan: {d.get('itemType')}")
        elif "type" in it:
            it.setdefault("id", f"csl{len(items)+1}")
            items.append(it)
        else:
            masalah.append("entri tanpa itemType/type dilewati")
    return items, masalah


def zotero_item_ke_csl(d: dict) -> dict | None:
    """Salinan ringan dari zotero_client.zotero_ke_csl, tanpa impor silang."""
    tipe_map = {
        "journalArticle": "article-journal", "magazineArticle": "article-magazine",
        "newspaperArticle": "article-newspaper", "book": "book",
        "bookSection": "chapter", "conferencePaper": "paper-conference",
        "thesis": "thesis", "report": "report", "webpage": "webpage",
        "blogPost": "post-weblog", "manuscript": "manuscript",
        "computerProgram": "software", "dataset": "dataset", "patent": "patent",
        "standard": "standard", "document": "document", "preprint": "article",
        "presentation": "speech", "map": "map", "film": "motion_picture",
        "videoRecording": "motion_picture", "audioRecording": "song",
    }
    z = d.get("itemType", "")
    if z in ("attachment", "note", "annotation"):
        return None
    out = {"id": d.get("key") or d.get("itemKey") or f"z{abs(hash(d.get('title','')))%10**6}",
           "type": tipe_map.get(z, "document"), "_sumber": "zotero"}
    peta = {"title": "title", "abstractNote": "abstract", "DOI": "DOI", "url": "URL",
            "volume": "volume", "issue": "issue", "pages": "page",
            "publicationTitle": "container-title", "bookTitle": "container-title",
            "proceedingsTitle": "container-title", "websiteTitle": "container-title",
            "publisher": "publisher", "place": "publisher-place",
            "edition": "edition", "ISSN": "ISSN", "ISBN": "ISBN",
            "language": "language", "reportNumber": "number",
            "university": "publisher", "thesisType": "genre", "series": "collection-title"}
    for src, dst in peta.items():
        v = d.get(src)
        if v not in (None, "", []):
            out[dst] = v
    if d.get("date"):
        t = _tahun_dari(d["date"])
        if t:
            out["issued"] = t
    pen = []
    for c in d.get("creators") or []:
        if c.get("name"):
            pen.append({"literal": c["name"]})
        elif c.get("lastName") or c.get("firstName"):
            pen.append({"family": c.get("lastName", ""), "given": c.get("firstName", "")})
    if pen:
        out["author"] = pen
    return out


def deteksi_format(teks: str) -> str:
    t = teks.lstrip()
    if t.startswith("@") or re.search(r"^\s*@\w+\s*[{(]", teks, re.M):
        return "bibtex"
    if re.search(r"^TY\s{1,2}-", teks, re.M):
        return "ris"
    if t.startswith("[") or t.startswith("{"):
        try:
            data = json.loads(teks)
        except json.JSONDecodeError:
            return "tidak dikenal"
        sample = data if isinstance(data, list) else (data.get("items") or [])
        if isinstance(sample, list) and sample:
            if isinstance(sample[0], dict):
                if "itemType" in sample[0] or "data" in sample[0]:
                    return "zotero-json"
                if "type" in sample[0] or "id" in sample[0]:
                    return "csl-json"
        return "json"
    if "\t" in teks.splitlines()[0] if teks.splitlines() else False:
        return "tsv"
    return "tidak dikenal"


def baca_tsv(teks: str) -> tuple[list, list]:
    """Haystack/paste dari spreadsheet: judul<TAB>penulis<TAB>tahun<TAB>wadah."""
    items, masalah = [], []
    baris = [b for b in teks.splitlines() if b.strip()]
    if not baris:
        return [], ["kosong"]
    mulai = 1 if re.search(r"judul|title|penulis|author", baris[0], re.I) else 0
    for i, b in enumerate(baris[mulai:], 1):
        kol = [x.strip() for x in b.split("\t")]
        it = {"id": f"tsv{i}", "type": "article-journal", "_sumber": "tsv"}
        if len(kol) > 0 and kol[0]:
            it["title"] = kol[0]
        if len(kol) > 1 and kol[1]:
            it["author"] = _pisah_penulis_bibtex(kol[1].replace(";", " and "))
        if len(kol) > 2 and kol[2]:
            t = _tahun_dari(kol[2])
            if t:
                it["issued"] = t
        if len(kol) > 3 and kol[3]:
            it["container-title"] = kol[3]
        if len(kol) > 4 and kol[4]:
            it["DOI"] = kol[4]
        items.append(it)
    return items, masalah


# ---------------------------------------------------------------------------
# Deduplikasi
# ---------------------------------------------------------------------------
def kunci_doi(it: dict) -> str:
    d = str(it.get("DOI") or "").strip().lower()
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d)


def kunci_judul(it: dict) -> str:
    t = it.get("title") or ""
    if isinstance(t, list):
        t = " ".join(str(x) for x in t)
    t = unicodedata.normalize("NFKD", str(t))
    t = re.sub(r"[^a-z0-9 ]", "", t.lower())
    t = re.sub(r"\s+", " ", t).strip()
    thn = ""
    dp = (it.get("issued") or {}).get("date-parts") or [[None]]
    if dp and dp[0] and dp[0][0]:
        thn = str(dp[0][0])
    return f"{t}|{thn}" if t else ""


def dedup(items: list) -> tuple[list, list]:
    """(unik, duplikat). DOI menang; tanpa DOI pakai judul+tahun."""
    unik, dup, terlihat_doi, terlihat_judul = [], [], {}, {}
    for it in items:
        d = kunci_doi(it)
        j = kunci_judul(it)
        if d and d in terlihat_doi:
            dup.append({"id": it.get("id"), "sama_dengan": terlihat_doi[d], "sebab": "DOI"})
            continue
        if not d and j and j in terlihat_judul:
            dup.append({"id": it.get("id"), "sama_dengan": terlihat_judul[j], "sebab": "judul+tahun"})
            continue
        if d:
            terlihat_doi[d] = it.get("id")
        if j:
            terlihat_judul[j] = it.get("id")
        unik.append(it)
    return unik, dup


# ---------------------------------------------------------------------------
def muat(path: str) -> tuple[list, list, str]:
    with open(path, encoding="utf-8", errors="replace") as f:
        teks = f.read()
    fmt = deteksi_format(teks)
    if fmt == "bibtex":
        items, m = baca_bibtex(teks)
    elif fmt == "ris":
        items, m = baca_ris(teks)
    elif fmt in ("zotero-json", "csl-json", "json"):
        try:
            items, m = baca_zotero_json(json.loads(teks))
        except json.JSONDecodeError as e:
            items, m = [], [f"JSON tidak valid: {e}"]
    elif fmt == "tsv":
        items, m = baca_tsv(teks)
    else:
        items, m = [], ["format tidak dikenali"]
    return items, m, fmt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Konversi apa pun -> CSL-JSON + dedup")
    ap.add_argument("berkas", nargs="+", help="satu atau beberapa berkas (glob boleh)")
    ap.add_argument("--out", help="tulis CSL-JSON gabungan ke berkas ini")
    ap.add_argument("--gabung", action="store_true", help="gabung semua berkas jadi satu")
    ap.add_argument("--periksa", action="store_true", help="laporan saja, tak menulis")
    ap.add_argument("--tanpa-dedup", action="store_true")
    a = ap.parse_args(argv)

    daftar = []
    for pola in a.berkas:
        daftar.extend(sorted(glob.glob(pola)) or [pola])

    semua, laporan, gagal = [], [], []
    for p in daftar:
        if not os.path.isfile(p):
            gagal.append({"berkas": p, "sebab": "tidak ada"})
            continue
        items, masalah, fmt = muat(p)
        for it in items:
            it["_berkas"] = os.path.basename(p)
        semua.extend(items)
        laporan.append({"berkas": os.path.basename(p), "format": fmt,
                        "entri": len(items), "masalah": masalah})
        if not items:
            gagal.append({"berkas": p, "sebab": "nol entri terbaca"})

    sebelum = len(semua)
    dup = []
    if not a.tanpa_dedup:
        semua, dup = dedup(semua)

    for it in semua:
        it.pop("_berkas", None)
        it.pop("_sumber", None)

    ringkas = {"berkas": len(daftar), "entri_mentah": sebelum,
               "entri_unik": len(semua), "duplikat": len(dup),
               "gagal": gagal, "per_berkas": laporan}
    if dup:
        ringkas["daftar_duplikat"] = dup[:50]

    if a.periksa:
        print(json.dumps(ringkas, ensure_ascii=False, indent=2))
        return 0 if semua else 1

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump({"versi": "2.6", "items": semua, "laporan": ringkas},
                      f, ensure_ascii=False, indent=2)
        print(json.dumps(ringkas, ensure_ascii=False, indent=2))
        return 0 if semua else 1

    print(json.dumps({"laporan": ringkas, "items": semua}, ensure_ascii=False, indent=2))
    return 0 if semua else 1


if __name__ == "__main__":
    sys.exit(main())
