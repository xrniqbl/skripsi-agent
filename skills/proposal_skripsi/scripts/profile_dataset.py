#!/usr/bin/env python3
"""
profile_dataset.py — Profil dataset untuk skill proposal-skripsi.

Menghasilkan profil deskriptif + rekomendasi uji statistik dari file CSV/TSV/XLSX/JSON,
agar angka yang ditulis ke BAB III berasal dari data nyata, bukan karangan.

Usage:
    python3 profile_dataset.py <file.csv> [file2.csv ...] [--out <prefix>] [--sheet NAME] [--alpha]

Options:
    --out <prefix>   prefix untuk keluaran (default: profil_dataset)
    --sheet NAME     nama sheet untuk file .xlsx (default: sheet pertama)
    --json-only      hanya tulis JSON, tanpa markdown
    --min-likert 2   jumlah minimal kolom untuk mendeteksi skala Likert (default 2)

Dependencies:
    stdlib only. XLSX memerlukan openpyxl (pip3 install openpyxl).
    Normalitas dihitung dengan scipy bila terpasang; jika tidak, memakai
    pendekatan skewness-kurtosis dan hasilnya dilabeli "perkiraan".

Output:
    <prefix>.md     laporan markdown (profil, deskriptif, frekuensi, alpha, uji asumsi)
    <prefix>.json   angka machine-readable untuk drafting dan pengecekan
"""

import argparse
import json
import re
import math
import os
import statistics
import sys

# ---------------------------------------------------------------- pemuatan data


def sniff_delimiter(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        head = fh.readline()
    counts = {d: head.count(d) for d in [",", ";", "\t", "|"]}
    best = max(counts, key=lambda k: counts[k])
    return best if counts[best] > 0 else ","


def load_delimited(path):
    delim = sniff_delimiter(path)
    rows = []
    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        first = fh.readline()
        if not first.strip():
            return [], delim
        header = [h.strip() for h in first.replace(delim, "\x1f").split("\x1f")]
        for line in fh:
            if not line.strip():
                continue
            parts = [p.strip() for p in line.replace("\x1f", delim).split(delim)]
            if len(parts) < len(header):
                parts += [""] * (len(header) - len(parts))
            rows.append(dict(zip(header, parts[: len(header)])))
    return rows, delim


def load_xlsx(path, sheet=None):
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        sys.exit(
            "ERROR: file .xlsx memerlukan openpyxl. Jalankan: pip3 install openpyxl\n"
            "       Alternatif: ekspor sheet ke CSV lalu jalankan ulang script ini."
        )
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb[sheet] if sheet else wb.worksheets[0]
    it = ws.iter_rows(values_only=True)
    header_row = next(it, None)
    if header_row is None:
        return [], ","
    header = [str(h).strip() if h is not None else f"col{i+1}" for i, h in enumerate(header_row)]
    rows = []
    for r in it:
        if r is None or all(v is None for v in r):
            continue
        rows.append({header[i]: ("" if i >= len(r) or r[i] is None else str(r[i]))
                     for i in range(len(header))})
    wb.close()
    return rows, ","


def load_json_array(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        for key in ("data", "rows", "records", "items"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
        else:
            data = [data]
    rows = []
    for obj in data:
        if isinstance(obj, dict):
            rows.append({k: ("" if v is None else str(v)) for k, v in obj.items()})
    return rows, ","


def load_file(path, sheet=None):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv", ".tsv", ".txt"):
        return load_delimited(path)
    if ext in (".xlsx", ".xlsm"):
        return load_xlsx(path, sheet)
    if ext in (".json", ".jsonl"):
        return load_json_array(path)
    sys.exit(f"ERROR: format tidak didukung: {path} (gunakan csv, tsv, xlsx, atau json)")


# ------------------------------------------------------------------ utilitas


def to_number(v):
    if v is None:
        return None
    s = str(v).strip().replace(",", ".")
    if s == "" or s in {"na", "n/a", "null", "none", "-", "nan"}:
        return None
    pct = False
    if s.endswith("%"):
        pct = True
        s = s[:-1]
    try:
        f = float(s)
    except ValueError:
        return None
    if pct:
        f /= 100.0
    return f


def is_likert(values):
    vals = [v for v in values if v is not None]
    if len(vals) < 5:
        return None
    lo, hi = min(vals), max(vals)
    if lo < 1 or hi > 10:
        return None
    span = hi - lo
    if span in (3, 4, 6) and all(float(v).is_integer() for v in vals):
        return int(span + 1)
    return None


def cronbach_alpha(columns):
    """columns: list of list (setiap kolom = list nilai numerik, panjang sama)."""
    if len(columns) < 2:
        return None
    n = len(columns[0])
    if n < 3:
        return None
    k = len(columns)
    item_vars = []
    for col in columns:
        try:
            item_vars.append(statistics.variance(col))
        except statistics.StatisticsError:
            return None
    if sum(item_vars) == 0:
        return None
    try:
        totals = [sum(col[i] for col in columns) for i in range(n)]
        tot_var = statistics.variance(totals)
    except statistics.StatisticsError:
        return None
    if tot_var == 0:
        return None
    return (k / (k - 1)) * (1 - sum(item_vars) / tot_var)


def shapiro(values):
    try:
        from scipy import stats  # type: ignore
        if 3 <= len(values) <= 5000:
            stat, p = stats.shapiro(values)
            return float(stat), float(p), "shapiro-wilk"
    except Exception:
        pass
    return None, None, "perkiraan (skewness-kurtosis)"


def normality_skew(values):
    """Pendekatan berbasis skewness: rules of thumb skew -2..+2 dianggap normal."""
    try:
        sk = statistics.mean([(x - statistics.fmean(values)) ** 3
                              for x in values]) / (statistics.stdev(values) ** 3)
    except (statistics.StatisticsError, ZeroDivisionError):
        return None
    verdict = "normal" if -2 <= sk <= 2 else "tidak normal"
    return sk, verdict


# ------------------------------------------------------------------- profil


def profile(path, sheet=None, min_likert=2):
    rows, delim = load_file(path, sheet)
    cols = []
    if rows:
        cols = list(rows[0].keys())
    out_cols = []
    numeric = {}
    for c in cols:
        raw = [r.get(c, "") for r in rows]
        nums = [to_number(v) for v in raw]
        nums_clean = [n for n in nums if n is not None]
        n_missing = len(nums) - len(nums_clean)
        is_num = len(nums_clean) >= max(3, 0.5 * len(raw))
        filled = [str(v).strip() for v in raw if str(v).strip() != ""]
        entry = {
            "nama": c,
            "tipe": "numerik" if is_num else "kategorikal",
            "n_valid": len(nums_clean) if is_num else len(filled),
            "n_missing": n_missing if is_num else len(raw) - len(filled),
            "pct_lengkap": round(
                100.0 * (len(nums_clean) if is_num else len(filled)) / len(raw), 1
            ) if raw else 0.0,
            "n_unik": len(set(filled)),
        }
        if is_num and nums_clean:
            values = nums_clean
            mean = statistics.fmean(values)
            sd = statistics.stdev(values) if len(values) > 1 else 0.0
            sv = sorted(values)
            def quantile(p):
                if len(sv) == 1:
                    return sv[0]
                k = (len(sv) - 1) * p
                f = math.floor(k)
                c = min(f + 1, len(sv) - 1)
                return sv[f] + (sv[c] - sv[f]) * (k - f)
            norm = normality_skew(values)
            sh_stat, sh_p, sh_method = shapiro(values)
            likert = is_likert(values)
            entry.update({
                "mean": round(mean, 3), "median": round(statistics.median(values), 3),
                "std": round(sd, 3), "min": round(min(values), 3), "max": round(max(values), 3),
                "q1": round(quantile(0.25), 3), "q3": round(quantile(0.75), 3),
                "skewness": round(norm[0], 3) if norm[0] is not None else None,
                "normalitas_skew": norm[1] if norm else None,
                "shapiro_stat": round(sh_stat, 4) if sh_stat is not None else None,
                "shapiro_p": round(sh_p, 4) if sh_p is not None else None,
                "normalitas_metode": sh_method,
                "skala_likert": likert,
            })
            numeric[c] = values
        elif not is_num:
            freq = {}
            for v in raw:
                s = str(v).strip()
                if s == "":
                    continue
                freq[s] = freq.get(s, 0) + 1
            top = sorted(freq.items(), key=lambda kv: -kv[1])[:5]
            entry["frekuensi_top"] = [
                {"nilai": k, "freq": v, "pct": round(100.0 * v / max(1, sum(freq.values())), 1)}
                for k, v in top
            ]
        out_cols.append(entry)

    # pengelompokan skala Likert -> alpha
    likert_cols = [c for c, e in zip(cols, out_cols) if e.get("skala_likert")]
    alphas = {}
    for e in out_cols:
        if not e.get("skala_likert"):
            continue
        base = "".join(ch for ch in e["nama"] if not ch.isdigit()) or e["nama"]
        alphas.setdefault(base, []).append(e["nama"])
    alpha_results = {}
    for base, group in alphas.items():
        if len(group) < min_likert:
            continue
        a = cronbach_alpha([numeric[c] for c in group])
        if a is not None:
            alpha_results[base] = {"kolom": group, "alpha": round(a, 3),
                                   "kategori": "baik" if a > 0.8 else ("acceptable" if a > 0.7 else "lemah")}

    return {
        "file": os.path.abspath(path),
        "delimiter": delim,
        "n_rows": len(rows),
        "n_cols": len(cols),
        "kolom": out_cols,
        "alpha": alpha_results,
        "n_likert_cols": len(likert_cols),
    }


DV_PATTERN = re.compile(
    r"(^|[^a-z])(y\d*|dv|dependen|performa\w*|kinerja|hasil|prestas\w*|produk\w*|"
    r"satisfaction|puas\w*|komitmen|loyal\w*|kepuasan|adopsi\w*|kualitas)",
    re.IGNORECASE,
)
ID_PATTERN = re.compile(r"(^|_)(id| kode| code| Responden| no|nomor| nama)$", re.IGNORECASE)


def is_id_like(col):
    if col["tipe"] != "kategorikal":
        return False
    if ID_PATTERN.search(col["nama"]):
        return True
    filled = col["n_valid"] or 1
    return col["n_unik"] / filled > 0.9 and col["n_unik"] > 10


def recommend(prof):
    """Rekomendasi teknik analisis berdasarkan karakter data nyata."""
    recs = []
    num_cols = [c for c in prof["kolom"] if c["tipe"] == "numerik"]
    cat_cols = [c for c in prof["kolom"] if c["tipe"] == "kategorikal" and not is_id_like(c)]
    n = prof["n_rows"]

    # kelompokkan kolom numerik yang terdeteksi skala Likert
    likert_groups = {}
    for c in num_cols:
        if not c.get("skala_likert"):
            continue
        base = ("".join(ch for ch in c["nama"] if not ch.isdigit()) or c["nama"]).strip("_")
        likert_groups.setdefault(base, []).append(c)

    dv_groups = {b: g for b, g in likert_groups.items() if DV_PATTERN.search(b)}
    iv_groups = {b: g for b, g in likert_groups.items() if b not in dv_groups}

    if len(dv_groups) == 1 and iv_groups:
        dv_base, dv = next(iter(dv_groups.items()))
        iv_cols = [c for name in iv_groups for c in iv_groups[name]]
        non_normal_iv = [c for c in iv_cols if c.get("normalitas_skew") == "tidak normal"]
        rekom = "regresi linear berganda"
        if prof.get("alpha") and any(len(g) > 3 for g in iv_groups.values()):
            rekom = "PLS-SEM (apabila jumlah indikator banyak) atau regresi berganda"
        if non_normal_iv:
            rekom += "; periksa asumsi normalitas residual"
        recs.append({
            "tipe": "regresi",
            "untuk": f"{dv_base} sebagai variabel dependen, dipengaruhi oleh {', '.join(c['nama'] for c in iv_cols)}",
            "alasan": ("butir skala Likert membentuk variabel laten sehingga skor variabel "
                        "dihitung dari rata-rata butirnya; " + rekom),
            "data": f"{dv[0]['nama']} vs {', '.join(c['nama'] for c in iv_cols)}",
        })
    elif len(likert_groups) > 1 and not dv_groups:
        names = ", ".join(likert_groups.keys())
        recs.append({
            "tipe": "korelasi / uji beda",
            "untuk": names,
            "alasan": ("beberapa variabel skala Likert terdeteksi tanpa variabel dependen yang jelas; "
                       "tentukan DV secara teoretis, lalu gunakan regresi; bila hanya ingin "
                       "keterhubungan, gunakan Pearson r atau Spearman rho"),
            "data": ", ".join(g[0]["nama"] for g in likert_groups.values()),
        })

    non_normal = [c for c in num_cols if c.get("normalitas_skew") == "tidak normal"]
    if non_normal and not likert_groups:
        recs.append({
            "tipe": "uji non-parametrik",
            "untuk": ", ".join(c["nama"] for c in non_normal[:5]),
            "alasan": ("skewness di luar rentang -2 sampai +2 sehingga asumsi normalitas tidak "
                       "terpenuhi; gunakan Mann-Whitney U, Kruskal-Wallis, atau Spearman"),
            "data": ", ".join(c["nama"] for c in non_normal[:5]),
        })

    if cat_cols and (likert_groups or num_cols):
        group_col = cat_cols[0]
        target = next((g[0]["nama"] for g in (dv_groups or likert_groups).values()), num_cols[0]["nama"])
        skew = next((c for c in num_cols if c["nama"] == target), {}).get("normalitas_skew")
        test = "one-way ANOVA atau independent t-test"
        if skew == "tidak normal":
            test = "Kruskal-Wallis atau Mann-Whitney U"
        recs.append({
            "tipe": "perbandingan antar kelompok",
            "untuk": f"{target} menurut kelompok {group_col['nama']}",
            "alasan": (f"kolom {group_col['nama']} berperan sebagai kelompok pembanding "
                       f"({group_col['n_unik']} kategori); gunakan {test}"),
            "data": f"{target} x {group_col['nama']}",
        })

    if len(num_cols) >= 2 and not likert_groups:
        recs.append({
            "tipe": "korelasi",
            "untuk": f"{num_cols[0]['nama']} dan {num_cols[1]['nama']}",
            "alasan": "dua variabel numerik tanpa pola butir kuesioner; gunakan Pearson r bila normal, Spearman rho bila ordinal",
            "data": f"{num_cols[0]['nama']}, {num_cols[1]['nama']}",
        })

    if n and n < 30:
        recs.append({
            "tipe": "perhatian ukuran sampel",
            "untuk": f"n = {n}",
            "alasan": "sampel kecil; utamakan uji non-parametrik dan hindari regresi dengan prediktor terlalu banyak",
            "data": "-",
        })
    return recs


# ------------------------------------------------------------------ keluaran


def fmt(x, nd=2):
    if x is None:
        return "-"
    if isinstance(x, float):
        s = f"{x:.{nd}f}"
        return s.replace(".", ",")
    return str(x)


def render_markdown(profiles):
    out = []
    out.append("# Profil Dataset — Dasar Rancangan Analisis Bab III\n")
    out.append("Dihasilkan oleh `scripts/profile_dataset.py`. **Semua angka dalam naskah proposal harus")
    out.append("mengambil dari berkas ini atau dihitung ulang darinya.**\n")
    for prof in profiles:
        name = os.path.basename(prof["file"])
        out.append(f"## {name}\n")
        out.append(f"- Baris: **{prof['n_rows']}** | Kolom: **{prof['n_cols']}** | Delimiter: `{prof['delimiter']}`")
        out.append(f"- Lokasi: `{prof['file']}`")
        out.append(f"- Kolom terdeteksi skala Likert: **{prof['n_likert_cols']}**\n")

        out.append("### Deskriptif per kolom\n")
        out.append("| Kolom | Tipe | Valid | Missing | Lengkap % | Unik | Min | Max | Mean | Median | SD | Skew | Normalitas |")
        out.append("|-------|------|-------|---------|-----------|------|-----|-----|------|--------|-----|------|-----------|")
        for c in prof["kolom"]:
            if c["tipe"] == "numerik":
                out.append(
                    f"| {c['nama']} | num | {c['n_valid']} | {c['n_missing']} | {c['pct_lengkap']} | {c['n_unik']} "
                    f"| {fmt(c['min'])} | {fmt(c['max'])} | {fmt(c['mean'])} | {fmt(c['median'])} | {fmt(c['std'])} "
                    f"| {fmt(c['skewness'])} | {c.get('normalitas_skew') or '-'} |")
            else:
                out.append(
                    f"| {c['nama']} | kat | {c['n_valid']} | {c['n_missing']} | {c['pct_lengkap']} | {c['n_unik']} "
                    f"| - | - | - | - | - | - | - |")
        out.append("")

        cat_cols = [c for c in prof["kolom"] if c["tipe"] == "kategorikal"]
        if cat_cols:
            out.append("### Frekuensi kategori\n")
            for c in cat_cols:
                out.append(f"**{c['nama']}**\n")
                out.append("| Nilai | Frekuensi | Persentase |")
                out.append("|-------|-----------|-------------|")
                for f in c.get("frekuensi_top", []):
                    out.append(f"| {f['nilai']} | {f['freq']} | {fmt(f['pct'], 1)} |")
                out.append("")

        norm_cols = [c for c in prof["kolom"] if c["tipe"] == "numerik" and c.get("shapiro_p") is not None]
        if norm_cols:
            out.append("### Uji normalitas\n")
            out.append("| Kolom | Metode | Statistik | p-value | Keputusan (alpha 0,05) |")
            out.append("|-------|--------|-----------|---------|--------------------------|")
            for c in norm_cols:
                verdict = "normal" if c["shapiro_p"] > 0.05 else "tidak normal"
                out.append(f"| {c['nama']} | {c['normalitas_metode']} | {fmt(c['shapiro_stat'], 4)} | "
                           f"{fmt(c['shapiro_p'], 4)} | {verdict} |")
            out.append("")
        elif prof["kolom"]:
            out.append("### Uji normalitas\n")
            out.append("Tidak tersedia uji parametrik (scipy tidak terpasang). Gunakan kolom skewness di atas:")
            out.append("skewness di luar -2 sampai +2 menunjukkan distribusi tidak normal.\n")

        if prof["alpha"]:
            out.append("### Reliabilitas (Cronbach's alpha)\n")
            out.append("| Kelompok kolom | Jumlah butir | Alpha | Kategori |")
            out.append("|-----------------|--------------|-------|-----------|")
            for base, info in prof["alpha"].items():
                out.append(f"| {base} | {len(info['kolom'])} | {fmt(info['alpha'], 3)} | {info['kategori']} |")
            out.append("\nKategori: alpha > 0,80 baik; 0,70-0,80 acceptable; < 0,70 lemah.\n")

        recs = recommend(prof)
        out.append("### Rekomendasi teknik analisis\n")
        if not recs:
            out.append("Tidak ada rekomendasi otomatis. Periksa manual jenis kolom pada tabel di atas.\n")
        else:
            out.append("| Tipe uji | Untuk | Alasan | Data |")
            out.append("|----------|-------|--------|------|")
            for r in recs:
                out.append(f"| {r['tipe']} | {r['untuk']} | {r['alasan']} | `{r['data']}` |")
            out.append("")
        out.append("---\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Profil dataset untuk rancangan analisis Bab III")
    ap.add_argument("files", nargs="+", help="file csv/tsv/xlsx/json")
    ap.add_argument("--out", default="profil_dataset", help="prefix keluaran")
    ap.add_argument("--sheet", default=None, help="nama sheet untuk xlsx")
    ap.add_argument("--json-only", action="store_true")
    ap.add_argument("--min-likert", type=int, default=2)
    args = ap.parse_args()

    profiles = []
    for f in args.files:
        if not os.path.exists(f):
            sys.exit(f"ERROR: file tidak ditemukan: {f}")
        p = profile(f, args.sheet, args.min_likert)
        p["rekomendasi"] = recommend(p)
        profiles.append(p)
        print(f"OK  {f}: {p['n_rows']} baris x {p['n_cols']} kolom, "
              f"{p['n_likert_cols']} kolom skala Likert", file=sys.stderr)

    jpath = args.out + ".json"
    with open(jpath, "w", encoding="utf-8") as fh:
        json.dump({"files": profiles}, fh, ensure_ascii=False, indent=2)
    print(f"Tulis: {jpath}", file=sys.stderr)

    if not args.json_only:
        mpath = args.out + ".md"
        with open(mpath, "w", encoding="utf-8") as fh:
            fh.write(render_markdown(profiles))
        print(f"Tulis: {mpath}", file=sys.stderr)

    for p in profiles:
        print(f"\n== {os.path.basename(p['file'])}", file=sys.stderr)
        for r in p["rekomendasi"]:
            print(f"   - {r['tipe']}: {r['untuk']}", file=sys.stderr)


if __name__ == "__main__":
    main()
