#!/usr/bin/env python3
"""Verifikasi DOI dan entri Daftar Pustaka — penegak aturan "DOI wajib resolve".

Pemakaian:
    python3 verify_doi.py daftar_pustaka.md
    python3 verify_doi.py referensi.bib --out laporan_doi.md
    python3 verify_doi.py naskah.md --cache .doi_cache.json
    python3 verify_doi.py --doi 10.1016/j.ijinfomgt.2023.102642

Kenapa alat ini ada:
    Meta memberi DOI yang formatnya benar tapi tidak ada. `10.1016/j.ijinfomgt.2023.102642`
    lolos pemeriksaan mata dan 404 di Crossref. Aturan "DOI wajib resolve" tidak ada artinya
    tanpa alat yang benar-benar memanggil Crossref dan doi.org.

Tiga verdict:
    VALID     — terdaftar di Crossref DAN handle doi.org resolve
    TIDAK ADA — Crossref tidak menemukan, handle gagal resolve (kemungkinan dikarang)
    MENDUGA   — format benar, tetapi Crossref tidak mengenal (bisa DOI lama/registrar lain)
    GAGAL     — jaringan gagal; jangan simpulkan apa pun dari ini

Kode keluar:
    0  semua entri VALID
    1  ada TIDAK ADA atau MENDUGA  (perlu diperbaiki)
    2  berkas tidak terbaca / tidak ada DOI
    3  semua permintaan gagal karena jaringan (bukan salah entri)
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

UA = "skripsi-agent/1.0 (verify-doi; mailto:noreply@example.org)"
CROSSREF = "https://api.crossref.org/works/"
DATACITE = "https://api.datacite.org/dois/"
RESOLVER = "https://doi.org/api/handles/"

# DOI: prefix "10." + 4-9 digit registrar + "/" + suffix
RE_DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>,;)\]}]+)", re.I)
RE_DOI_URL = re.compile(r"https?://(?:dx\.)?doi\.org/(10\.\d{4,9}/\S+)", re.I)


def bersihkan(doi: str) -> str:
    doi = doi.strip().rstrip(".,;:)")
    doi = RE_DOI_URL.sub(r"\1", doi)
    doi = re.sub(r"^(?:doi:\s*)", "", doi, flags=re.I)
    return doi


def get_json(url: str, timeout: int = 20, terima_404: bool = False):
    """Kembalikan (status_http, data). status 0 = gagal jaringan."""
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        if e.code == 404 and terima_404:
            return 404, None
        return e.code, None
    except Exception:  # noqa: BLE001 — jaringan/timeout/DNS
        return 0, None


def cek_crossref(doi: str) -> tuple[str, dict | None]:
    """('VALID' | 'TIDAK ADA' | 'GAGAL', metadata)"""
    url = CROSSREF + urllib.parse.quote(doi, safe="/")
    status, data = get_json(url, terima_404=True)
    if status == 404:
        return "TIDAK ADA", None
    if status != 200 or not isinstance(data, dict):
        return "GAGAL", None
    pesan = data.get("message") or {}
    if not pesan.get("title"):
        return "TIDAK ADA", None
    penulis = []
    for a in (pesan.get("author") or [])[:3]:
        fam = a.get("family") or a.get("name") or ""
        if fam:
            penulis.append(fam)
    tahun = None
    for k in ("published-print", "published-online", "issued", "created"):
        bagian = pesan.get(k) or {}
        dp = bagian.get("date-parts") or []
        if dp and dp[0] and dp[0][0]:
            tahun = dp[0][0]
            break
    return "VALID", {
        "judul": (pesan.get("title") or [""])[0],
        "penulis": penulis,
        "tahun": tahun,
        "wadah": (pesan.get("container-title") or [""])[0],
        "tipe": pesan.get("type"),
        "penerbit": pesan.get("publisher"),
    }


def cek_handle(doi: str) -> str:
    """Resolusi handle doi.org. 'OK' | 'TIDAK ADA' | 'GAGAL'."""
    url = RESOLVER + urllib.parse.quote(doi, safe="")
    status, data = get_json(url, terima_404=True)
    if status == 404:
        return "TIDAK ADA"
    if status != 200 or not isinstance(data, dict):
        return "GAGAL"
    kode = data.get("responseCode")
    return "OK" if kode == 1 else "TIDAK ADA"


def cek_datacite(doi: str) -> str:
    url = DATACITE + urllib.parse.quote(doi, safe="/")
    status, data = get_json(url, terima_404=True)
    if status == 200 and isinstance(data, dict):
        atribut = (data.get("data") or {}).get("attributes") or {}
        if atribut.get("title") or atribut.get("titles"):
            return "OK"
    return "TIDAK ADA"


def verifikasi(doi: str, pakai_datacite: bool = True) -> dict:
    hasil = {"doi": doi, "verdict": "", "metadata": None, "sumber": [], "catatan": []}

    status_cr, meta = cek_crossref(doi)
    time.sleep(0.25)

    if status_cr == "VALID":
        hasil["sumber"].append("crossref")
        hasil["metadata"] = meta
        handle = cek_handle(doi)
        time.sleep(0.2)
        if handle == "OK":
            hasil["sumber"].append("doi.org")
        elif handle == "TIDAK ADA":
            hasil["catatan"].append("Crossref mengenal tetapi handle doi.org gagal resolve")
        hasil["verdict"] = "VALID"
        return hasil

    if status_cr == "GAGAL":
        hasil["verdict"] = "GAGAL"
        hasil["catatan"].append("Crossref tidak dapat dihubungi")
        return hasil

    # Crossref tidak menemukan — mungkin DataCite (dataset, preprint, repositori)
    if pakai_datacite:
        time.sleep(0.2)
        if cek_datacite(doi) == "OK":
            hasil["sumber"].append("datacite")
            hasil["verdict"] = "VALID"
            hasil["catatan"].append("terdaftar di DataCite, bukan Crossref")
            return hasil

    handle = cek_handle(doi)
    time.sleep(0.2)
    if handle == "OK":
        hasil["verdict"] = "MENDUGA"
        hasil["catatan"].append(
            "handle resolve tetapi tidak ada metadata Crossref/DataCite — "
            "verifikasi manual, bisa jadi DOI lama atau registrar lain")
        return hasil
    if handle == "GAGAL":
        hasil["verdict"] = "MENDUGA"
        hasil["catatan"].append("Crossref tidak menemukan; doi.org tidak menjawab")
        return hasil

    hasil["verdict"] = "TIDAK ADA"
    hasil["catatan"].append("tidak ada di Crossref, DataCite, maupun doi.org")
    return hasil


def ambil_doi_dari_teks(teks: str) -> list[tuple[str, str]]:
    """Kembalikan [(doi, baris_asli)] — dedupe, urutan kemunculan."""
    keluar, dilihat = [], set()
    for baris in teks.splitlines():
        for m in RE_DOI.finditer(baris):
            doi = bersihkan(m.group(1))
            kunci = doi.lower()
            if kunci not in dilihat:
                dilihat.add(kunci)
                keluar.append((doi, baris.strip()[:150]))
    return keluar


def muat_cache(path: str | None) -> dict:
    if not path or not os.path.isfile(path):
        return {}
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("berkas", nargs="?", help="naskah / Daftar Pustaka / .bib")
    ap.add_argument("--doi", action="append", default=[], help="periksa DOI tunggal (boleh berulang)")
    ap.add_argument("--out", help="tulis laporan markdown ke berkas ini")
    ap.add_argument("--cache", help="cache JSON (mempercepat pemeriksaan ulang)")
    ap.add_argument("--jeda", type=float, default=0.3, help="jeda antar entri (detik)")
    ap.add_argument("--tanpa-datacite", action="store_true",
                    help="lewati pemeriksaan DataCite (lebih cepat, dataset bisa salah)")
    args = ap.parse_args()

    entri: list[str] = []
    if args.doi:
        entri = [bersihkan(d) for d in args.doi]
    elif args.berkas:
        try:
            teks = open(args.berkas, encoding="utf-8", errors="replace").read()
        except OSError as e:
            print(f"GAGAL membaca {args.berkas}: {e}", file=sys.stderr)
            return 2
        entri = [d for d, _ in ambil_doi_dari_teks(teks)]
    if not entri:
        print("Tidak ada DOI yang ditemukan. "
              "Pastikan Daftar Pustaka memuat DOI, atau pakai --doi.", file=sys.stderr)
        return 2

    cache = muat_cache(args.cache)
    hasil: list[dict] = []
    print(f"Memeriksa {len(entri)} DOI…\n", file=sys.stderr)

    for i, doi in enumerate(entri, 1):
        if doi in cache and cache[doi].get("verdict") in ("VALID", "TIDAK ADA"):
            h = dict(cache[doi])
            h["_cache"] = True
        else:
            h = verifikasi(doi, pakai_datacite=not args.tanpa_datacite)
            h["_cache"] = False
            if h["verdict"] != "GAGAL":
                cache[doi] = h
            time.sleep(args.jeda)
        hasil.append(h)
        tanda = {"VALID": "OK  ", "TIDAK ADA": "GAGAL", "MENDUGA": "DUGA ", "GAGAL": "NET  "}
        judul = ((h["metadata"] or {}).get("judul") or "")[:70]
        print(f"[{i:>3}/{len(entri)}] {tanda[h['verdict']]} {doi}"
              + (f"\n            {judul}" if judul else ""))
        for c in h["catatan"]:
            print(f"            ! {c}")

    if args.cache:
        try:
            json.dump(cache, open(args.cache, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
        except OSError as e:
            print(f"  ! cache tidak tertulis: {e}", file=sys.stderr)

    hitung = {v: sum(1 for h in hasil if h["verdict"] == v)
              for v in ("VALID", "TIDAK ADA", "MENDUGA", "GAGAL")}
    total = len(hasil)
    jaringan_gagal = hitung["GAGAL"] == total

    baris = ["# Verifikasi DOI", "",
             f"Total: **{total}** · VALID **{hitung['VALID']}** · "
             f"TIDAK ADA **{hitung['TIDAK ADA']}** · "
             f"MENDUGA **{hitung['MENDUGA']}** · GAGAL-JARINGAN **{hitung['GAGAL']}**", "",
             "| # | DOI | Verdict | Judul terverifikasi | Sumber |",
             "|---|---|---|---|---|"]
    for i, h in enumerate(hasil, 1):
        judul = ((h["metadata"] or {}).get("judul") or "—")
        judul = judul.replace("|", "\\|")[:80]
        baris.append(f"| {i} | `{h['doi']}` | **{h['verdict']}** | {judul} | "
                     f"{', '.join(h['sumber']) or '—'} |")

    rusak = [h for h in hasil if h["verdict"] in ("TIDAK ADA", "MENDUGA")]
    if rusak:
        baris += ["", "## Entri yang harus diperbaiki", ""]
        for h in rusak:
            baris.append(f"### `{h['doi']}` — {h['verdict']}")
            for c in h["catatan"]:
                baris.append(f"- {c}")
            baris.append("- **Jangan dikarang ulang.** Cari ulang di Google Scholar / "
                         "situs jurnal, atau ganti dengan sumber yang benar-benar dibaca.")
            baris.append("")

    if hitung["TIDAK ADA"]:
        baris += ["", "> DOI berstatus TIDAK ADA adalah indikasi kuat DOI dikarang. "
                  "Hapus entri atau ganti dengan sumber nyata — jangan hanya mengubah digit."]

    teks_laporan = "\n".join(baris)
    print("\n" + teks_laporan)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(teks_laporan + "\n")
        print(f"\nDitulis: {args.out}", file=sys.stderr)

    if jaringan_gagal:
        print("\nSemua permintaan gagal karena jaringan — bukan bukti DOI salah.",
              file=sys.stderr)
        return 3
    return 0 if hitung["VALID"] == total else 1


if __name__ == "__main__":
    sys.exit(main())
