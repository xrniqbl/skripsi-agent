#!/usr/bin/env python3
"""
zotero_client.py - Klien multi-jalur untuk mengambil metadata pustaka.

Empat jalur, dipilih otomatis atau eksplisit:
  1. Web API v3         https://api.zotero.org  (butuh API key untuk pustaka privat)
  2. Local API          http://127.0.0.1:23119  (Zotero 7 desktop jalan, tanpa auth)
  3. DOI content neg.   https://doi.org/<doi>   (CSL-JSON langsung, tanpa akun)
  4. Crossref           https://api.crossref.org (cari DOI dari judul, cek keberadaan)

Keluaran selalu CSL-JSON (bentuk kanonik seluruh pipeline), ditulis ke berkas
`*.csl.json` lewat subperintah `simpan`, atau dicetak ke stdout.

Pemakaian:
    # apakah Zotero desktop hidup?
    python3 zotero_client.py probe

    # pustaka pengguna (butuh key kalau privat)
    python3 zotero_client.py user 475425 --key "$ZOTERO_KEY" --out pustaka.csl.json

    # grup publik, tanpa key
    python3 zotero_client.py group 22000 --out grup.csl.json

    # satu DOI jadi entri CSL
    python3 zotero_client.py doi 10.1038/s41586-020-2649-2

    # beberapa DOI sekaligus dari berkas teks
    python3 zotero_client.py doi --dari-daftar dois.txt --out hasil.csl.json

    # cari DOI dari judul (Crossref)
    python3 zotero_client.py cari "array programming with numpy"

Kode keluar:
    0  berhasil
    1  tidak ada data / semua entri gagal
    2  argumen salah
    3  jaringan gagal total (jangan simpulkan entri salah)

Aturan keras:
    Field kosong TIDAK ditebak. Bila sumber tidak menyediakan volume, volume
    tetap kosong dan dilaporkan di `--laporan`. Metadata karangan adalah cacat
    yang justru ingin dicegah pipeline ini.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "skripsi-agent/2.6 (zotero_pustaka; +https://github.com/)"
API_VER = "3"
LOCAL_BASE = os.environ.get("ZOTERO_LOCAL", "http://127.0.0.1:23119")
WEB_BASE = "https://api.zotero.org"
DOI_BASE = "https://doi.org/"
CROSSREF = "https://api.crossref.org/works"

# Zotero itemType -> CSL type. Tipe tanpa pemetaan dicatat, tidak dipaksa
# jadi article-journal (lihat references/zotero-api.md).
ZOTERO_TO_CSL = {
    "journalArticle": "article-journal",
    "magazineArticle": "article-magazine",
    "newspaperArticle": "article-newspaper",
    "book": "book",
    "bookSection": "chapter",
    "conferencePaper": "paper-conference",
    "thesis": "thesis",
    "report": "report",
    "webpage": "webpage",
    "blogPost": "post-weblog",
    "manuscript": "manuscript",
    "letter": "personal_communication",
    "interview": "interview",
    "film": "motion_picture",
    "artwork": "graphic",
    "computerProgram": "software",
    "dataset": "dataset",
    "patent": "patent",
    "standard": "standard",
    "document": "document",
    "preprint": "article",
    "encyclopediaArticle": "entry-encyclopedia",
    "dictionaryEntry": "entry-dictionary",
    "presentation": "speech",
    "map": "map",
    "audioRecording": "song",
    "videoRecording": "motion_picture",
    "podcast": "broadcast",
    "forumPost": "post",
    "email": "personal_communication",
    "instantMessage": "personal_communication",
    "attachment": None,     # dilewati
    "note": None,           # dilewati
    "annotation": None,     # dilewati
}


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
def _req(url: str, headers: dict | None = None, timeout: int = 25,
         method: str = "GET", data: bytes | None = None):
    h = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h, method=method, data=data)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", "replace")
        return r.status, dict(r.headers), body


def get_json(url: str, headers: dict | None = None, timeout: int = 25):
    """Kembalikan (status, headers, objek-json-atau-None). Tidak melempar."""
    try:
        status, hdrs, body = _req(url, headers=headers, timeout=timeout)
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), None
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, {}, None
    if not body.strip():
        return status, hdrs, None
    try:
        return status, hdrs, json.loads(body)
    except json.JSONDecodeError:
        return status, hdrs, None


# ---------------------------------------------------------------------------
# 1 & 2: Zotero (Web API / Local API)
# ---------------------------------------------------------------------------
def probe_local(timeout: int = 3) -> bool:
    """True bila Zotero desktop menjawab di port lokal."""
    try:
        status, _, body = _req(LOCAL_BASE + "/connector/ping", timeout=timeout)
        return status == 200
    except Exception:
        return False


def _zotero_headers(key: str | None) -> dict:
    h = {"Zotero-API-Version": API_VER}
    if key:
        h["Authorization"] = "Bearer " + key
    return h


def zotero_items(target: str, ident: str, key: str | None = None,
                 limit: int = 100, collection: str | None = None,
                 local: bool = False, jeda: float = 0.25) -> tuple[list, dict]:
    """
    Ambil semua item satu pustaka, dipage sampai habis.

    target : 'user' | 'group'
    ident  : id numerik pustaka
    local  : pakai Local API (ident diabaikan, selalu users/0)

    Mengembalikan (daftar-item-mentah, laporan) - laporan memuat total
    sebenarnya dari header Total-Results, jumlah terambil, dan status HTTP
    sehingga pemanggil bisa membedakan 'kosong' dari 'ditolak'.
    """
    if local:
        base = f"{LOCAL_BASE}/api/users/0"
        headers = {}
        total_hdr = None
    else:
        base = f"{WEB_BASE}/{target}s/{ident}"
        headers = _zotero_headers(key)

    q = f"/items?limit={min(limit, 100)}&format=json"
    if collection:
        q = f"/collections/{collection}/items?limit={min(limit, 100)}&format=json"

    items: list = []
    start = 0
    total = None
    last_status = 0

    while True:
        url = f"{base}{q}&start={start}"
        status, hdrs, data = get_json(url, headers=headers)
        last_status = status
        if status != 200 or not isinstance(data, list):
            break
        if total is None:
            total_hdr = hdrs.get("Total-Results") or hdrs.get("total-results")
            total = int(total_hdr) if total_hdr and str(total_hdr).isdigit() else None
        if not data:
            break
        items.extend(data)
        start += len(data)
        if total is not None and start >= total:
            break
        if len(data) < min(limit, 100):
            break
        time.sleep(jeda)  # hormati rate limit (429 membawa Retry-After)

    laporan = {
        "sumber": "local" if local else f"zotero-{target}",
        "id": str(ident),
        "http": last_status,
        "total_dilaporkan": total,
        "terambil": len(items),
        "lengkap": (total is None) or (len(items) >= total),
    }
    if last_status == 403 and not local:
        laporan["catatan"] = ("403 = pustaka privat / key tidak ada atau kurang scope. "
                              "Bukan berarti id tidak valid.")
    return items, laporan


# ---------------------------------------------------------------------------
# Konversi Zotero item -> CSL-JSON
# ---------------------------------------------------------------------------
def _tahun(dari: str | None) -> dict | None:
    if not dari:
        return None
    m = re.search(r"(\d{4})", dari)
    if not m:
        return None
    return {"date-parts": [[int(m.group(1))]]}


def _penulis(creators: list) -> list:
    out = []
    for c in creators or []:
        if c.get("creatorType", "author") not in ("author", "editor", "translator",
                                                  "bookAuthor", "director"):
            continue
        if c.get("name"):
            out.append({"literal": c["name"]})
        else:
            fam = (c.get("lastName") or "").strip()
            giv = (c.get("firstName") or "").strip()
            if fam or giv:
                out.append({"family": fam, "given": giv})
    return out


def zotero_ke_csl(item: dict) -> dict | None:
    """Satu item Zotero -> satu entri CSL-JSON. None untuk tipe yang dilewati."""
    it = item.get("data", item)
    ztype = it.get("itemType", "")
    if ztype in ZOTERO_TO_CSL and ZOTERO_TO_CSL[ztype] is None:
        return None
    csl_type = ZOTERO_TO_CSL.get(ztype)
    if csl_type is None:
        csl_type = "document"          # dicatat pemanggil lewat _tipe_asli

    key = it.get("key") or it.get("itemKey") or ""
    out = {
        "id": key or re.sub(r"\W+", "", it.get("title", ""))[:24] or "item",
        "type": csl_type,
        "_tipe_zotero": ztype,
    }
    peta = {
        "title": "title",
        "abstractNote": "abstract",
        "DOI": "DOI",
        "url": "URL",
        "volume": "volume",
        "issue": "issue",
        "pages": "page",
        "publicationTitle": "container-title",
        "bookTitle": "container-title",
        "proceedingsTitle": "container-title",
        "websiteTitle": "container-title",
        "publisher": "publisher",
        "place": "publisher-place",
        "edition": "edition",
        "ISSN": "ISSN",
        "ISBN": "ISBN",
        "language": "language",
        "extra": None,
        "series": "collection-title",
        "conferenceName": "event",
        "journalAbbreviation": "container-title-short",
        "reportNumber": "number",
        "university": "publisher",
        "thesisType": "genre",
        "numberOfVolumes": "number-of-volumes",
    }
    for src, dst in peta.items():
        if not dst:
            continue
        v = it.get(src)
        if v not in (None, "", []):
            out[dst] = v if not isinstance(v, str) else v.strip()

    if it.get("date"):
        d = _tahun(it["date"])
        if d:
            out["issued"] = d
    pen = _penulis(it.get("creators"))
    if pen:
        out["author"] = pen
    tags = [t.get("tag") for t in it.get("tags", []) if t.get("tag")]
    if tags:
        out["keyword"] = "; ".join(tags)
    return out


# ---------------------------------------------------------------------------
# 3 & 4: DOI / Crossref
# ---------------------------------------------------------------------------
RE_DOI = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/)?(10\.\d{4,9}/\S+)$", re.I)

# Field CSL-JSON yang dipertahankan. Crossref/DataCite mengirim puluhan field
# administratif (license, reference-count, indexed, deposited) yang bukan
# metadata bibliografis dan hanya membuat berkas kanonik jadi gemuk.
CSL_FIELDS = {
    "id", "type", "title", "title-short", "author", "editor", "translator",
    "container-title", "container-title-short", "collection-title",
    "collection-number", "publisher", "publisher-place", "event",
    "event-place", "page", "page-first", "volume", "issue", "number",
    "number-of-pages", "number-of-volumes", "edition", "chapter-number",
    "DOI", "URL", "ISBN", "ISSN", "PMID", "PMCID", "abstract", "keyword",
    "note", "language", "issued", "accessed", "submitted", "genre",
    "medium", "status", "version", "archive", "archive-place",
    "archive_location", "call-number", "dimensions", "scale", "source",
    "shortTitle", "short-title", "original-title", "original-publisher",
    "original-publisher-place", "original-date", "references",
    "reviewed-title", "section", "citation-number", "citation-label",
    "first-reference-note-number", "year-suffix", "categories",
    "part", "supplement", "volume-title", "volume-title-short",
}

# Crossref/DataCite memakai tipe bergaya sendiri, bukan tipe CSL.
CROSSREF_TO_CSL = {
    "journal-article": "article-journal",
    "proceedings-article": "paper-conference",
    "book-chapter": "chapter",
    "book-section": "chapter",
    "book-part": "chapter",
    "book": "book",
    "monograph": "book",
    "edited-book": "book",
    "reference-book": "book",
    "report": "report",
    "report-series": "report",
    "dissertation": "thesis",
    "posted-content": "article",
    "dataset": "dataset",
    "peer-review": "review",
    "standard": "standard",
    "component": "document",
    "other": "document",
    "journal-issue": "document",
    "journal-volume": "document",
    "proceedings": "book",
    "reference-entry": "entry-encyclopedia",
    "book-set": "book",
}


def _unescape_html(s: str) -> str:
    """
    Crossref mengirim entitas HTML di judul: "Knowledge Discovery &amp; Data
    Mining". Tanpa di-decode, "&amp;" tercetak apa adanya di Daftar Pustaka
    dan terbaca sebagai salah ketik.
    """
    import html as _html
    if not isinstance(s, str) or "&" not in s:
        return s
    return _html.unescape(s)


def rapikan_csl(rec: dict) -> dict:
    """Buang field non-CSL dan normalisasi bentuk list -> skalar."""
    out = {}
    for k, v in rec.items():
        if k not in CSL_FIELDS:
            continue
        if v in (None, "", [], {}):
            continue
        if isinstance(v, list) and k in ("title", "container-title",
                                         "collection-title", "abstract"):
            v = v[0] if v and isinstance(v[0], str) else v
        out[k] = v
    # judul sebagai list-of-dict (DataCite) -> string
    for k in ("title", "container-title"):
        if isinstance(out.get(k), list):
            bagian = []
            for el in out[k]:
                if isinstance(el, dict):
                    bagian.append(el.get("title") or el.get("value") or "")
                elif isinstance(el, str):
                    bagian.append(el)
            out[k] = "; ".join(b for b in bagian if b)
    # DOI selalu tanpa prefiks URL
    if out.get("DOI"):
        out["DOI"] = re.sub(r"^https?://(dx\.)?doi\.org/", "", str(out["DOI"]).strip())
    # halaman: en-dash kalau masih tanda hubung tunggal
    pg = out.get("page")
    if isinstance(pg, str) and re.fullmatch(r"\s*\d+\s*-\s*\d+\s*", pg):
        a, b = [x.strip() for x in pg.split("-")]
        out["page"] = f"{a}-{b}"
    # ISSN/ISBN dikirim sebagai list -> ambil yang pertama, sisanya ke catatan
    for k in ("ISSN", "ISBN"):
        if isinstance(out.get(k), list):
            nilai = [str(x) for x in out[k] if x]
            if nilai:
                out[k] = nilai[0]
                if len(nilai) > 1:
                    out.setdefault("note", "")
                    out["note"] = (out["note"] + f" {k}: " + ", ".join(nilai)).strip()
    # tipe Crossref -> tipe CSL
    t = out.get("type")
    if isinstance(t, str):
        if t in CROSSREF_TO_CSL:
            out["type"] = CROSSREF_TO_CSL[t]
        elif "-" in t and t not in ZOTERO_TO_CSL.values():
            out["_tipe_asli"] = t
            out["type"] = "document"
    # abstrak: buang markup JATS/HTML
    if isinstance(out.get("abstract"), str):
        s = re.sub(r"<[^>]+>", " ", out["abstract"])
        s = re.sub(r"\s+", " ", s).strip()
        out["abstract"] = s
    # nama: buang affiliation/role/sequence/ORCID - sisakan family/given/literal
    for k in ("author", "editor", "translator"):
        if isinstance(out.get(k), list):
            bersih = []
            for nm in out[k]:
                if not isinstance(nm, dict):
                    if isinstance(nm, str) and nm.strip():
                        bersih.append({"literal": nm.strip()})
                    continue
                sat = {}
                if nm.get("literal"):
                    sat["literal"] = str(nm["literal"]).strip()
                else:
                    if nm.get("family"):
                        sat["family"] = str(nm["family"]).strip()
                    if nm.get("given"):
                        sat["given"] = str(nm["given"]).strip()
                if sat:
                    bersih.append(sat)
            if bersih:
                out[k] = bersih
            else:
                out.pop(k, None)
    # judul/wadah/abstrak: decode entitas HTML lalu rapikan spasi
    for k in ("title", "container-title", "publisher", "publisher-place",
              "abstract", "note", "keyword"):
        if isinstance(out.get(k), str):
            out[k] = re.sub(r"\s+", " ", _unescape_html(out[k])).strip()
    return out


def bersih_doi(s: str) -> str:
    s = s.strip().rstrip(".,;)")
    m = RE_DOI.match(s)
    return m.group(1) if m else s


def doi_ke_csl(doi: str) -> tuple[dict | None, str]:
    """Content negotiation doi.org -> CSL-JSON. (entri, status-teks)."""
    doi = bersih_doi(doi)
    url = DOI_BASE + urllib.parse.quote(doi, safe="/")
    h = {"Accept": "application/vnd.citationstyles.csl+json"}
    try:
        status, _, body = _req(url, headers=h, timeout=30)
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, f"jaringan: {type(e).__name__}"
    if not body.strip():
        return None, "badan kosong"
    try:
        rec = json.loads(body)
    except json.JSONDecodeError:
        return None, "bukan JSON"
    rec.pop("indexed", None)
    rec.setdefault("id", doi)
    rec["DOI"] = rec.get("DOI") or doi
    rec = rapikan_csl(rec)
    if not rec.get("type"):
        rec["type"] = "article-journal"
    return rec, "ok"


def cari_doi(judul: str, baris: int = 3) -> list:
    q = urllib.parse.urlencode({"query.bibliographic": judul, "rows": baris,
                                "select": "DOI,title,author,issued,container-title,type"})
    status, _, data = get_json(f"{CROSSREF}?{q}")
    if status != 200 or not isinstance(data, dict):
        return []
    out = []
    for it in data.get("message", {}).get("items", []):
        judul_it = (it.get("title") or [""])[0]
        out.append({
            "doi": it.get("DOI", ""),
            "judul": judul_it,
            "tahun": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "wadah": (it.get("container-title") or [""])[0],
            "tipe": it.get("type", ""),
        })
    return out


def cek_doi(doi: str) -> dict:
    """Verifikasi keberadaan DOI di Crossref + resolusi handle doi.org."""
    doi = bersih_doi(doi)
    st_cr, _, cr = get_json(f"{CROSSREF}/{urllib.parse.quote(doi, safe='/')}")
    st_h, _, hd = get_json("https://doi.org/api/handles/" + urllib.parse.quote(doi, safe="/"))
    ada_cr = st_cr == 200 and isinstance(cr, dict)
    ada_h = st_h == 200 and isinstance(hd, dict) and hd.get("responseCode") == 1
    if ada_cr and ada_h:
        verdict = "VALID"
    elif ada_cr or ada_h:
        verdict = "MENDUGA"
    elif st_cr == 0 and st_h == 0:
        verdict = "GAGAL"
    else:
        verdict = "TIDAK ADA"
    return {"doi": doi, "verdict": verdict, "crossref": st_cr, "handle": st_h}


# ---------------------------------------------------------------------------
# Deduplikasi
# ---------------------------------------------------------------------------
def _kunci_doi(it: dict) -> str:
    d = str(it.get("DOI") or "").strip().lower()
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d)


def _kunci_judul(it: dict) -> str:
    import unicodedata
    t = it.get("title") or ""
    if isinstance(t, list):
        t = " ".join(str(x) for x in t)
    t = unicodedata.normalize("NFKD", str(t))
    t = re.sub(r"[^a-z0-9 ]", "", t.lower())
    t = re.sub(r"\s+", " ", t).strip()
    dp = (it.get("issued") or {}).get("date-parts") or [[None]]
    thn = str(dp[0][0]) if dp and dp[0] and dp[0][0] else ""
    return f"{t}|{thn}" if t else ""


def dedup(items: list) -> tuple[list, list]:
    """
    Buang entri kembar: DOI dulu, lalu judul ternormalisasi + tahun.

    Pustaka Zotero nyata memang mengandung duplikat (entri yang diimpor dua
    kali, atau dua item tanpa judul sama sekali). Pada gaya numerik
    (IEEE/Vancouver) duplikat langsung merusak penomoran, dan pada gaya
    abjad ia mencetak baris yang sama dua kali di Daftar Pustaka.
    Duplikat DILAPORKAN, tidak dibuang diam-diam.
    """
    unik, dup, doi_ada, judul_ada = [], [], {}, {}
    for it in items:
        d, j = _kunci_doi(it), _kunci_judul(it)
        if d and d in doi_ada:
            dup.append({"id": it.get("id"), "sama_dengan": doi_ada[d],
                        "sebab": "DOI"})
            continue
        if j and j in judul_ada:
            dup.append({"id": it.get("id"), "sama_dengan": judul_ada[j],
                        "sebab": "judul+tahun"})
            continue
        if d:
            doi_ada[d] = it.get("id")
        if j:
            judul_ada[j] = it.get("id")
        unik.append(it)
    return unik, dup


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------
def baca_doi_daftar(path: str) -> list[str]:
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                out.append(bersih_doi(line))
    return out


def simpan(items: list, path: str, laporan: dict | None = None) -> None:
    paket = {"versi": "2.6", "dibuat": time.strftime("%Y-%m-%dT%H:%M:%S"),
             "items": items}
    if laporan:
        paket["laporan"] = laporan
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(paket, f, ensure_ascii=False, indent=2)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Ambil metadata pustaka -> CSL-JSON")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("probe", help="cek apakah Zotero desktop lokal hidup")

    p = sub.add_parser("user", help="pustaka pengguna Zotero")
    p.add_argument("id")
    p.add_argument("--tanpa-dedup", action="store_true",
                   help="pertahankan entri kembar (default: dibuang + dilaporkan)")
    p.add_argument("--key", default=os.environ.get("ZOTERO_KEY"))
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--collection")
    p.add_argument("--local", action="store_true", help="pakai Local API")
    p.add_argument("--out")

    p = sub.add_parser("group", help="pustaka grup Zotero")
    p.add_argument("id")
    p.add_argument("--tanpa-dedup", action="store_true")
    p.add_argument("--key", default=os.environ.get("ZOTERO_KEY"))
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--collection")
    p.add_argument("--out")

    p = sub.add_parser("doi", help="DOI -> entri CSL")
    p.add_argument("doi", nargs="?")
    p.add_argument("--dari-daftar", help="berkas teks berisi satu DOI per baris")
    p.add_argument("--cek", action="store_true", help="verifikasi dulu di Crossref")
    p.add_argument("--jeda", type=float, default=0.3)
    p.add_argument("--out")

    p = sub.add_parser("cari", help="cari DOI dari judul via Crossref")
    p.add_argument("judul")
    p.add_argument("--baris", type=int, default=3)

    a = ap.parse_args(argv)

    if a.cmd == "probe":
        hidup = probe_local()
        print(json.dumps({"local_api": LOCAL_BASE, "hidup": hidup,
                          "saran": ("pakai --local" if hidup else
                                    "Zotero desktop tidak jalan; pakai --key atau jalur DOI")},
                         ensure_ascii=False, indent=2))
        return 0 if hidup else 1

    if a.cmd in ("user", "group"):
        items_raw, lap = zotero_items(a.cmd, a.id, key=a.key, limit=a.limit,
                                      collection=a.collection,
                                      local=getattr(a, "local", False))
        if not items_raw:
            print(json.dumps(lap, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        csl, dilewati = [], []
        for it in items_raw:
            c = zotero_ke_csl(it)
            if c is None:
                dilewati.append((it.get("data", it).get("itemType")))
            else:
                csl.append(c)
        lap["dilewati"] = sorted({d for d in dilewati if d})
        if not getattr(a, "tanpa_dedup", False):
            sebelum = len(csl)
            csl, dup = dedup(csl)
            lap["duplikat"] = len(dup)
            if dup:
                lap["daftar_duplikat"] = dup[:30]
            lap["entri_sebelum_dedup"] = sebelum
        lap["entri"] = len(csl)
        if a.out:
            simpan(csl, a.out, lap)
            print(json.dumps(lap, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"laporan": lap, "items": csl}, ensure_ascii=False, indent=2))
        return 0

    if a.cmd == "doi":
        daftar = (baca_doi_daftar(a.dari_daftar) if a.dari_daftar
                  else ([bersih_doi(a.doi)] if a.doi else []))
        if not daftar:
            ap.error("beri DOI atau --dari-daftar")
        items, gagal, jaringan = [], [], 0
        for d in daftar:
            if a.cek:
                v = cek_doi(d)
                if v["verdict"] == "TIDAK ADA":
                    gagal.append(v)
                    continue
                if v["verdict"] == "GAGAL":
                    jaringan += 1
            entri, st = doi_ke_csl(d)
            if entri:
                items.append(entri)
            else:
                gagal.append({"doi": d, "sebab": st})
            time.sleep(a.jeda)
        lap = {"diminta": len(daftar), "berhasil": len(items),
               "gagal": gagal, "jaringan_gagal": jaringan}
        if a.out:
            simpan(items, a.out, lap)
            print(json.dumps(lap, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"laporan": lap, "items": items},
                             ensure_ascii=False, indent=2))
        if not items and jaringan == len(daftar):
            return 3
        return 0 if items else 1

    if a.cmd == "cari":
        hasil = cari_doi(a.judul, a.baris)
        print(json.dumps(hasil, ensure_ascii=False, indent=2))
        return 0 if hasil else 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
