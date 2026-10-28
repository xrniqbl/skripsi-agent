#!/usr/bin/env python3
"""Uji kepadatan literatur via OpenAlex + Crossref untuk kandidat topik skripsi.

Pemakaian:
    python3 literature_probe.py "pelaporan gizi puskesmas" \
        --alt "duplicate reporting primary health care" \
        --years 2021-2026 --out 02_probe

Keluaran: tiga hitungan per kueri (longgar / konsep / ketat), sebaran per tahun,
10 judul paling mirip, dan sinyal kepadatan (SEPI / SEDANG / PADAT).

PENTING — kenapa tiga hitungan:

  parameter `search=` di OpenAlex adalah pencarian relevansi longgar. Kueri
  "pelaporan gizi puskesmas" mengembalikan 4.465 karya karena ia mencocokkan
  kata mana pun. Angka itu tidak mengukur kepadatan topik; ia mengukur
  seberapa umum kata-katanya.

  Yang mengukur kepadatan adalah pencarian frasa pada judul+abstrak:
  `title_and_abstract.search:"pelaporan gizi puskesmas"` -> 1 karya.
  Sinyal SEPSI/SEDANG/PADAT dihitung dari angka KETAT, bukan angka longgar.

Ini alat pemetaan medan, bukan bukti orisinalitas. Setiap hitungan harus
dilaporkan bersama kueri persis yang dipakai.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request

UA = "skripsi-agent/1.0 (literature-probe; mailto:noreply@example.org)"
OPENALEX = "https://api.openalex.org/works"
CROSSREF = "https://api.crossref.org/works"
SELECT = "id,title,publication_year,doi,cited_by_count"


def get(url: str, timeout: int = 30) -> dict | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    for percobaan in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:  # noqa: BLE001
            if percobaan == 2:
                print(f"  ! gagal: {type(e).__name__} ({url.split('?')[0]})", file=sys.stderr)
                return None
            time.sleep(1.5 * (percobaan + 1))
    return None


def _oa(filter_str: str, per_page: int = 25, select: str = SELECT) -> tuple[int, list[dict]]:
    params = {"filter": filter_str, "per_page": str(per_page), "select": select}
    data = get(OPENALEX + "?" + urllib.parse.urlencode(params))
    if not data:
        return 0, []
    return data.get("meta", {}).get("count", 0), data.get("results", [])


def rentang_filter(dari: int, sampai: int) -> str:
    return f"from_publication_date:{dari}-01-01,to_publication_date:{sampai}-12-31"


def kueri_openalex(kueri: str, dari: int, sampai: int) -> dict:
    """Tiga level: longgar (search=), konsep (AND semua kata), ketat (frasa persis)."""
    rf = rentang_filter(dari, sampai)
    kata = [k for k in re.split(r"\s+", kueri.strip()) if k]
    frasa = " ".join(kata)

    longgar, _ = _oa(f"default.search:{frasa},{rf}", per_page=1, select="id")
    time.sleep(0.3)

    konsep_f = f"title_and_abstract.search:{' AND '.join(kata)},{rf}"
    konsep, items_konsep = _oa(konsep_f)
    time.sleep(0.3)

    kutip = f'"{frasa}"'
    ketat, items_ketat = _oa(f"title_and_abstract.search:{kutip},{rf}", per_page=25)
    time.sleep(0.3)

    judul_ketat, _ = _oa(f"title.search:{kutip},{rf}", per_page=1, select="id")
    time.sleep(0.3)

    return {"longgar": longgar, "konsep": konsep, "ketat": ketat, "judul_ketat": judul_ketat,
            "items": items_ketat or items_konsep, "frasa": frasa}


def crossref(kueri: str, dari: int, sampai: int) -> dict:
    base = {"filter": f"from-pub-date:{dari}-01-01,until-pub-date:{sampai}-12-31",
            "rows": "0"}
    out = {}
    for label, field in (("judul", "query.title"), ("bibliografis", "query.bibliographic")):
        params = dict(base)
        params[field] = kueri
        data = get(CROSSREF + "?" + urllib.parse.urlencode(params))
        out[label] = (data or {}).get("message", {}).get("total-results", 0)
        time.sleep(0.4)
    return out


def sebaran(items: list[dict]) -> dict[int, int]:
    out: dict[int, int] = {}
    for it in items:
        y = it.get("publication_year")
        if isinstance(y, int):
            out[y] = out.get(y, 0) + 1
    return dict(sorted(out.items()))


def sinyal(ketat: int) -> str:
    if ketat < 5:
        return "SEPI"
    if ketat <= 40:
        return "SEDANG"
    return "PADAT"


def kemiripan(a: str, b: str) -> float:
    na = set(re.findall(r"[a-z0-9]+", (a or "").lower()))
    nb = set(re.findall(r"[a-z0-9]+", (b or "").lower()))
    if not na or not nb:
        return 0.0
    return len(na & nb) / len(na | nb)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kueri", nargs="+", help="satu atau lebih kueri (frasa)")
    ap.add_argument("--alt", action="append", default=[], help="kueri alternatif (boleh berulang)")
    ap.add_argument("--years", default="2021-2026", help="rentang tahun, mis. 2021-2026")
    ap.add_argument("--out", help="prefix keluaran (menulis .md dan .json)")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    m = re.match(r"^(\d{4})-(\d{4})$", args.years)
    if not m:
        print("--years harus berbentuk TAHUN-TAHUN, mis. 2021-2026", file=sys.stderr)
        return 2
    dari, sampai = int(m.group(1)), int(m.group(2))
    if dari > sampai:
        print("tahun awal > tahun akhir", file=sys.stderr)
        return 2
    rentang = sampai - dari + 1

    kueri_semua = args.kueri + args.alt
    laporan: dict = {"rentang": args.years, "rentang_tahun": rentang, "kueri": []}
    semua_item: list[dict] = []

    for k in kueri_semua:
        print(f"\nKueri: {k!r}")
        oa = kueri_openalex(k, dari, sampai)
        cr = crossref(k, dari, sampai)
        seb = sebaran(oa["items"])
        sig = sinyal(oa["ketat"])
        print(f"  longgar (search=)        : {oa['longgar']:>6}   <- JANGAN dipakai untuk sinyal")
        print(f"  konsep (AND semua kata)  : {oa['konsep']:>6}")
        print(f"  ketat  (frasa di judul+abstrak): {oa['ketat']:>6}   <- dipakai untuk sinyal")
        print(f"  frasa di judul saja      : {oa['judul_ketat']:>6}")
        print(f"  Crossref (judul)         : {cr['judul']:>6}")
        print(f"  Crossref (bibliografis)  : {cr['bibliografis']:>6}")
        print(f"  per tahun (sampel)       : "
              + "  ".join(f"{y}:{c}" for y, c in seb.items() if c))
        print(f"  sinyal                   : {sig}")

        laporan["kueri"].append({
            "kueri": k, "frasa": oa["frasa"],
            "openalex": {"longgar": oa["longgar"], "konsep": oa["konsep"],
                         "ketat": oa["ketat"], "judul_ketat": oa["judul_ketat"]},
            "crossref": cr, "per_tahun": seb, "sinyal": sig})
        for it in oa["items"]:
            it["_kueri"] = k
            semua_item.append(it)

    uniq: dict[str, dict] = {}
    for it in semua_item:
        key = (it.get("doi") or it.get("id") or it.get("title") or "").lower()
        if key and key not in uniq:
            uniq[key] = it
    acuan = kueri_semua[0]
    ranked = sorted(uniq.values(), key=lambda it: -kemiripan(acuan, it.get("title", "")))
    top = ranked[: args.top]

    print(f"\n{args.top} judul paling mirip dengan {acuan!r}:")
    if not top:
        print("  (tidak ada hasil pada pencarian ketat — medan sangat sepi)")
    for i, it in enumerate(top, 1):
        skor = kemiripan(acuan, it.get("title", ""))
        print(f"  {i:2}. ({it.get('publication_year','?')}) "
              f"{(it.get('title') or '(tanpa judul)')[:96]}  [relevansi {skor:.2f}]")
        if it.get("doi"):
            print(f"      {it['doi']}")

    laporan["top_mirip"] = [{"judul": it.get("title"), "tahun": it.get("publication_year"),
                             "doi": it.get("doi"),
                             "relevansi": round(kemiripan(acuan, it.get("title", "")), 3)}
                            for it in top]

    if args.out:
        with open(args.out + ".json", "w", encoding="utf-8") as f:
            json.dump(laporan, f, ensure_ascii=False, indent=2)
        baris = [f"# Probe Literatur — {args.years}", "",
                 "| Kueri | longgar | konsep | **ketat** | judul | Crossref | Sinyal |",
                 "|---|---|---|---|---|---|---|"]
        for r in laporan["kueri"]:
            o = r["openalex"]
            baris.append(f"| {r['kueri']} | {o['longgar']} | {o['konsep']} | "
                         f"**{o['ketat']}** | {o['judul_ketat']} | "
                         f"{r['crossref']['judul']} | {r['sinyal']} |")
        baris += ["", f"## {args.top} judul paling mirip", ""]
        if not laporan["top_mirip"]:
            baris.append("_Tidak ada hasil pada pencarian frasa ketat._")
        for i, t in enumerate(laporan["top_mirip"], 1):
            baris.append(f"{i}. ({t['tahun']}) {t['judul']} — relevansi {t['relevansi']}"
                         + (f" — {t['doi']}" if t["doi"] else ""))
        baris += ["",
                  "## Cara membaca",
                  "",
                  "- **longgar** = parameter `search=` OpenAlex (relevansi). Angkanya besar",
                  "  karena mencocokkan kata mana pun. **Jangan pakai untuk menilai kepadatan.**",
                  "- **konsep** = semua kata muncul di judul/abstrak (AND). Batas atas kasar.",
                  "- **ketat** = frasa persis di judul/abstrak. **Ini yang dipakai untuk sinyal.**",
                  "- Sinyal: SEPI <5 · SEDANG 5–40 · PADAT >40 (rentang "
                  f"{rentang} tahun).",
                  "- PADAT bukan larangan — artinya gap-spotting tidak cukup, wajib problematisasi.",
                  "- SEPI bukan pujian — periksa dulu apakah masalahnya nyata dan datanya ada."]
        open(args.out + ".md", "w", encoding="utf-8").write("\n".join(baris) + "\n")
        print(f"\nDitulis: {args.out}.md dan {args.out}.json", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
