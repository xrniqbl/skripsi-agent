#!/usr/bin/env python3
"""
stats_tests.py — Menjalankan uji statistik nyata untuk proposal (BAB III) dan menghasilkan
tabel hasil siap tempel.

Bawaan: scipy + statsmodels bila terpasang. Tanpa dependensi: perhitungan sendiri berbasis
library standard (t, F, chi-square, korelasi, regresi linear, Cronbach's alpha), memakai
incomplete beta dan incomplete gamma untuk nilai p.

Usage:
    python3 stats_tests.py <file.csv> --out hasil_uji [opsi]

Mode uji (pilih satu atau beberapa):
    --regresi DV=kolom                       regresi linear berganda (DV ~ semua kolom numerik)
    --regresi DV=kolom;X=iv1;iv2             regresi dengan IV yang dipilih
    --ttest-independen DV=kolom --grup=kolom  t-test dua kelompok independen
    --ttest-paired  DV1=kolom --dv2=kolom    paired t-test (pre/post)
    --anova        DV=kolom --grup=kolom      one-way ANOVA
    --chi2         variabel1=kolomA,var2=kolomB  tabel silang + chi-square
    --korelasi     var1=kolomA,var2=kolomB    Pearson atau Spearman
    --cronbach     a=X1_1,X1_2,...            reliabilitas
    --auto         tebak dari nama kolom (butir skala Likert, kolom Y sebagai DV)

Opsi:
    --alpha 0.05   taraf signifikansi (default 0,05)
    --out PREFIX   prefix keluaran (default hasil_uji)
    --json-only    hanya JSON
    --engine auto|scipy|pure  (default: auto)

Output:
    <prefix>.md    tabel hasil + narasi siap tempel ke BAB III
    <prefix>.json  angka machine-readable
"""

import argparse
import csv
import json
import math
import os
import re
import statistics
import sys
from datetime import datetime

# --------------------------------------------------------------- distribusi (pure python)

def _betacf(a, b, x, itmax=200, eps=3e-12):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def betai(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
             + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbeta) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbeta) * _betacf(b, a, 1 - x) / b


def _gammap_series(a, x):
    ap, s, term = a, 1.0 / a, 1.0 / a
    for _ in range(500):
        ap += 1
        term *= x / ap
        s += term
        if abs(term) < abs(s) * 1e-12:
            break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))


def gammainc_upper(a, x):
    """P(a, x) = upper regularized incomplete gamma; untuk chi-square survival."""
    if x <= 0:
        return 1.0
    if x < a + 1:
        return 1.0 - _gammap_series(a, x)
    # continued fraction for Q(a, x)
    tiny = 1e-300
    b = x + 1 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-12:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


# p-values -------------------------------------------------------------

def t_sf_two_sided(t, df):
    if df <= 0:
        return float("nan")
    return betai(df / 2.0, 0.5, df / (df + t * t))


def f_sf(f, df1, df2):
    if f <= 0:
        return 1.0
    return betai(df2 / 2.0, df1 / 2.0, df2 / (df2 + df1 * f))


def chi2_sf(x, df):
    if x <= 0:
        return 1.0
    return gammainc_upper(df / 2.0, x / 2.0)


def norm_sf_two_sided(z):
    # tanpa scipy: gunakan erfc
    return math.erfc(abs(z) / math.sqrt(2.0))


def have_scipy():
    try:
        import scipy  # noqa: F401
        return True
    except ImportError:
        return False


def p_t(t, df, engine="auto"):
    if engine in ("auto", "scipy") and have_scipy():
        from scipy import stats  # type: ignore
        return float(2 * stats.t.sf(abs(t), df))
    return t_sf_two_sided(t, df)


def p_f(f, df1, df2, engine="auto"):
    if engine in ("auto", "scipy") and have_scipy():
        from scipy import stats  # type: ignore
        return float(stats.f.sf(f, df1, df2))
    return f_sf(f, df1, df2)


def p_chi2(x, df, engine="auto"):
    if engine in ("auto", "scipy") and have_scipy():
        from scipy import stats  # type: ignore
        return float(stats.chi2.sf(x, df))
    return chi2_sf(x, df)


# --------------------------------------------------------------- pemuatan data

def sniff_delimiter(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        head = fh.readline()
    counts = {d: head.count(d) for d in [",", ";", "\t", "|"]}
    best = max(counts, key=lambda k: counts[k])
    return best if counts[best] > 0 else ","


def load(path):
    delim = sniff_delimiter(path)
    rows = []
    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        header = [h.strip() for h in fh.readline().replace(delim, "\x1f").split("\x1f")]
        for line in fh:
            if not line.strip():
                continue
            parts = [p.strip() for p in line.rstrip("\n").replace("\x1f", delim).split(delim)]
            if len(parts) < len(header):
                parts += [""] * (len(header) - len(parts))
            rows.append(dict(zip(header, parts[: len(header)])))
    return rows, header


def num(v):
    if v is None:
        return None
    s = str(v).strip().replace(",", ".")
    if s.endswith("%"):
        s = s[:-1]
    try:
        return float(s)
    except ValueError:
        return None


def col_raw(rows, name):
    """Nilai numerik selaras indeks baris (None bila tidak terbaca)."""
    return [num(r.get(name)) for r in rows]


def col(rows, name, numeric=True):
    vals = [num(r.get(name)) for r in rows] if numeric else [
        (str(r.get(name)).strip() if r.get(name) is not None else "") for r in rows]
    return [v for v in vals if v is not None and v != ""]


def fmt(x, nd=3):
    if x is None:
        return "-"
    if isinstance(x, float):
        if math.isnan(x):
            return "-"
        if abs(x) < 1e-4 and x != 0:
            s = f"{x:.3e}"
            return s.replace(".", ",")
        s = f"{x:.{nd}f}"
        return s.replace(".", ",")
    return str(x)


def interpret(p, alpha):
    return "ditolak" if p < alpha else "tidak ditolak"


# --------------------------------------------------------------- uji statistik

def ttest_independent(a, b, alpha, engine):
    na, nb = len(a), len(b)
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    sp2 = ((na - 1) * va + (nb - 1) * vb) / (na + nb - 2)
    se = math.sqrt(sp2 * (1 / na + 1 / nb))
    t = (ma - mb) / se
    df = na + nb - 2
    p = p_t(t, df, engine)
    d = (ma - mb) / math.sqrt(sp2)  # Cohen's d
    return {"test": "Independent t-test", "n1": na, "n2": nb, "mean1": ma, "mean2": mb,
            "sd1": math.sqrt(va), "sd2": math.sqrt(vb), "t": t, "df": df, "p": p,
            "cohens_d": d, "alpha": alpha, "keputusan": interpret(p, alpha)}


def ttest_paired(x, y, alpha, engine):
    diffs = [a - b for a, b in zip(x, y)]
    n = len(diffs)
    md = statistics.fmean(diffs)
    sd = statistics.stdev(diffs)
    se = sd / math.sqrt(n)
    t = md / se
    df = n - 1
    p = p_t(t, df, engine)
    dz = md / sd
    return {"test": "Paired t-test", "n": n, "mean_diff": md, "sd_diff": sd, "t": t,
            "df": df, "p": p, "cohens_dz": dz, "alpha": alpha, "keputusan": interpret(p, alpha)}


def anova_oneway(groups, alpha, engine):
    allv = [v for g in groups for v in g[1]]
    grand = statistics.fmean(allv)
    k = len(groups)
    n = len(allv)
    ssb = sum(len(g[1]) * (statistics.fmean(g[1]) - grand) ** 2 for g in groups)
    ssw = sum((v - statistics.fmean(g[1])) ** 2 for g in groups for v in g[1])
    df1, df2 = k - 1, n - k
    f = (ssb / df1) / (ssw / df2) if ssw > 0 else float("nan")
    p = p_f(f, df1, df2, engine)
    detail = [{"kelompok": name, "n": len(vals), "mean": statistics.fmean(vals),
               "sd": statistics.stdev(vals) if len(vals) > 1 else 0.0} for name, vals in groups]
    return {"test": "One-way ANOVA", "k": k, "n": n, "F": f, "df1": df1, "df2": df2, "p": p,
            "alpha": alpha, "keputusan": interpret(p, alpha), "detail": detail}


def pearson(x, y, alpha, engine):
    n = len(x)
    mx, my = statistics.fmean(x), statistics.fmean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    r = sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else float("nan")
    df = n - 2
    t = r * math.sqrt(df / (1 - r * r)) if abs(r) < 1 else float("inf")
    p = p_t(t, df, engine)
    return {"test": "Pearson correlation", "n": n, "r": r, "t": t, "df": df, "p": p,
            "r2": r * r, "alpha": alpha, "keputusan": interpret(p, alpha)}


def spearman(x, y, alpha, engine):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        ranks = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                ranks[order[k]] = avg
            i = j + 1
        return ranks
    res = pearson(rank(x), rank(y), alpha, engine)
    res["test"] = "Spearman correlation"
    return res


def chi2(rows, va, vb, alpha=0.05):
    cats = sorted({str(r[va]).strip() for r in rows if str(r.get(va, "")).strip()}
                  | {str(r[vb]).strip() for r in rows if str(r.get(vb, "")).strip()})
    cont = {a: {b: 0 for b in cats} for a in cats}
    for r in rows:
        a, b = str(r[va]).strip(), str(r[vb]).strip()
        if a in cont and b in cont[a]:
            cont[a][b] += 1
    n = sum(sum(d.values()) for d in cont.values())
    rowt = {a: sum(cont[a].values()) for a in cats}
    colt = {b: sum(cont[a][b] for a in cats) for b in cats}
    chi = 0.0
    min_exp = float("inf")
    for a in cats:
        for b in cats:
            exp = rowt[a] * colt[b] / n
            min_exp = min(min_exp, exp)
            if exp > 0:
                chi += (cont[a][b] - exp) ** 2 / exp
    # buang kategori tanpa observasi agar df tidak menggelembung
    used_rows = [a for a in cats if sum(cont[a].values()) > 0]
    used_cols = [b for b in cats if sum(cont[a][b] for a in used_rows) > 0]
    cat = ""
    n_cells = len(used_rows) * len(used_cols)
    n_low = sum(1 for a in used_rows for b in used_cols
                if rowt[a] * colt[b] / n < 5)
    if n_cells and n_low / n_cells > 0.2:
        cat = ("Asumsi chi-square dilanggar: lebih dari 20% sel memiliki expected count < 5. "
               "Gabungkan kategori atau gunakan Fisher exact / exact test.")
    df = (len(used_rows) - 1) * (len(used_cols) - 1)
    p = p_chi2(chi, df) if df > 0 else float("nan")
    return {"test": "Chi-square (tabel silang)", "n": n, "chi2": chi, "df": df, "p": p,
            "min_exp": min_exp, "sel_expected_lt5": n_low, "jumlah_sel": n_cells,
            "alpha": alpha, "keputusan": interpret(p, alpha), "catatan": cat,
            "tabel": [{"kategori_1": a, **{f"kategori_2={b}": cont[a][b] for b in used_cols}}
                      for a in used_rows]}


def ols(y, xs, names, alpha, engine):
    """Regresi linear berganda via normal equations + eliminasi Gauss."""
    n = len(y)
    k = len(xs) + 1
    X = [[1.0] + [xs[j][i] for j in range(len(xs))] for i in range(n)]
    XtX = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)] for a in range(k)]
    Xty = [sum(X[i][a] * y[i] for i in range(n)) for a in range(k)]
    # Gaussian elimination dengan pivot parsial
    A = [row[:] + [Xty[i]] for i, row in enumerate(XtX)]
    for col in range(k):
        piv = max(range(col, k), key=lambda r: abs(A[r][col]))
        if abs(A[piv][col]) < 1e-12:
            return None
        A[col], A[piv] = A[piv], A[col]
        for r in range(k):
            if r == col:
                continue
            f = A[r][col] / A[col][col]
            for c in range(col, k + 1):
                A[r][c] -= f * A[col][c]
    beta = [A[i][k] / A[i][i] for i in range(k)]

    ybar = statistics.fmean(y)
    pred = [sum(beta[a] * X[i][a] for a in range(k)) for i in range(n)]
    ssr = sum((pred[i] - ybar) ** 2 for i in range(n))
    sse = sum((y[i] - pred[i]) ** 2 for i in range(n))
    sst = sum((v - ybar) ** 2 for v in y)
    df_model, df_resid = k - 1, n - k
    r2 = ssr / sst if sst > 0 else float("nan")
    adj = 1 - (1 - r2) * (n - 1) / df_resid if df_resid > 0 else float("nan")
    mse = sse / df_resid if df_resid > 0 else float("nan")
    # inverse XtX untuk standard error
    inv = [[0.0] * k for _ in range(k)]
    M = [XtX[i][:] + [1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
    for col in range(k):
        piv = max(range(col, k), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        d = M[col][col]
        M[col] = [v / d for v in M[col]]
        for r in range(k):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [M[r][c] - f * M[col][c] for c in range(2 * k)]
    for i in range(k):
        for j in range(k):
            inv[i][j] = M[i][k + j]

    terms = []
    labels = ["Constant"] + names
    for a in range(k):
        se = math.sqrt(mse * inv[a][a]) if inv[a][a] > 0 else float("nan")
        t = beta[a] / se if se else float("nan")
        p = p_t(t, df_resid, engine)
        if a == 0:
            terms.append({"term": "Constant (Intercept)", "b": beta[a], "se": se, "t": t,
                          "p": p, "keputusan": interpret(p, alpha)})
        else:
            terms.append({"term": names[a - 1], "b": beta[a], "se": se, "t": t, "p": p,
                          "beta_std": beta[a] * math.sqrt(inv[a][a] / (sst / (n - 1)))
                          if sst > 0 else float("nan"),
                          "keputusan": interpret(p, alpha)})
    fmodel = (ssr / df_model) / mse if mse > 0 else float("nan")
    return {"test": "Regresi linear berganda (OLS)", "n": n, "n_pred": len(xs),
            "r2": r2, "adj_r2": adj, "f": fmodel, "df1": df_model, "df2": df_resid,
            "p_model": p_f(fmodel, df_model, df_resid, engine), "terms": terms,
            "alpha": alpha, "engine": engine}


def cronbach(cols, names):
    k = len(cols)
    n = len(cols[0])
    iv = [statistics.variance(c) for c in cols]
    totals = [sum(c[i] for c in cols) for i in range(n)]
    tv = statistics.variance(totals)
    a = (k / (k - 1)) * (1 - sum(iv) / tv)
    return {"test": "Cronbach's alpha", "k": k, "n": n, "alpha": a,
            "kategori": "baik" if a > 0.8 else ("acceptable" if a > 0.7 else "lemah"),
            "items": names}


# ------------------------------------------------------------------ narasi

def narrative(res, alpha):
    t = res["test"]
    if t == "Independent t-test":
        praw = f" pada {res['label']}" if res.get("label") else ""
        return (f"Uji t dua sampel independen{praw} menunjukkan perbedaan rata-rata yang "
                f"{'signifikan' if res['p'] < alpha else 'tidak signifikan'} antara kelompok "
                f"1 (M = {fmt(res['mean1'])}, SD = {fmt(res['sd1'])}, n = {res['n1']}) dan "
                f"kelompok 2 (M = {fmt(res['mean2'])}, SD = {fmt(res['sd2'])}, n = {res['n2']}), "
                f"t({res['df']}) = {fmt(res['t'])}, p = {fmt(res['p'])}, d = {fmt(res['cohens_d'])}. "
                f"H₀ {res['keputusan']} pada α = {fmt(alpha)}.")
    if t == "Paired t-test":
        return (f"Uji t berpasangan menunjukkan perubahan rata-rata yang "
                f"{'signifikan' if res['p'] < alpha else 'tidak signifikan'} "
                f"(M selisih = {fmt(res['mean_diff'])}, SD = {fmt(res['sd_diff'])}), "
                f"t({res['df']}) = {fmt(res['t'])}, p = {fmt(res['p'])}, "
                f"d_z = {fmt(res['cohens_dz'])}. H₀ {res['keputusan']} pada α = {fmt(alpha)}.")
    if t == "One-way ANOVA":
        praw = f" pada {res['label']}" if res.get("label") else ""
        parts = "; ".join(f"{d['kelompok']} (n = {d['n']}, M = {fmt(d['mean'])}, SD = {fmt(d['sd'])})"
                          for d in res["detail"])
        return (f"Analisis varian satu arah{praw} menunjukkan perbedaan rata-rata yang "
                f"{'signifikan' if res['p'] < alpha else 'tidak signifikan'} antar kelompok "
                f"({parts}), F({res['df1']}, {res['df2']}) = {fmt(res['F'])}, p = {fmt(res['p'])}. "
                f"H₀ {res['keputusan']} pada α = {fmt(alpha)}."
                + (" Bila signifikan, lanjutkan dengan uji post hoc (Tukey atau Bonferroni)."
                   if res["p"] < alpha else ""))
    if t in ("Pearson correlation", "Spearman correlation"):
        sig = "signifikan" if res["p"] < alpha else "tidak signifikan"
        pihak = f" {res['label']}" if res.get("label") else ""
        return (f"Uji {t.split()[0].lower()}{pihak} menunjukkan hubungan yang {sig} "
                f"r = {fmt(res['r'])}, t({res['df']}) = {fmt(res['t'])}, p = {fmt(res['p'])}, "
                f"r² = {fmt(res['r2'])} (n = {res['n']}). H₀ {res['keputusan']} pada α = {fmt(alpha)}.")
    if t.startswith("Regresi"):
        sig_iv = [x for x in res["terms"] if x["term"] != "Constant (Intercept)" and x["p"] < alpha]
        return (f"Regresi linear berganda menunjukkan bahwa model secara overall "
                f"{'signifikan' if res['p_model'] < alpha else 'tidak signifikan'}, "
                f"F({res['df1']}, {res['df2']}) = {fmt(res['f'])}, p = {fmt(res['p_model'])}, "
                f"R² = {fmt(res['r2'])}, adjusted R² = {fmt(res['adj_r2'])} (n = {res['n']}). "
                + (f"Variabel yang berpengaruh signifikan: {', '.join(x['term'] for x in sig_iv)}."
                   if sig_iv else "Tidak ada variabel independen yang berpengaruh signifikan."))
    if t == "Chi-square (tabel silang)":
        return (f"Uji chi-square menunjukkan asosiasi yang "
                f"{'signifikan' if res['p'] < res.get('alpha', 0.05) else 'tidak signifikan'} "
                f"antara kedua variabel, χ²({res['df']}) = {fmt(res['chi2'])}, "
                f"p = {fmt(res['p'])} (n = {res['n']}). "
                + (res["catatan"] if res.get("catatan") else ""))
    if t == "Cronbach's alpha":
        return (f"Reliabilitas instrumen diukur dengan Cronbach's alpha sebesar "
                f"{fmt(res['alpha'])} untuk {res['k']} butir, yang termasuk kategori {res['kategori']}.")
    return ""



# ------------------------------------------------------------------ mode --auto

def _levels(rows, name):
    seen = []
    for r in rows:
        v = str(r.get(name, "")).strip()
        if v and v not in seen:
            seen.append(v)
    return seen


def _is_numeric_column(rows, name):
    vals = [num(r.get(name)) for r in rows]
    ok = [v for v in vals if v is not None]
    return len(ok) >= max(3, 0.8 * len(vals))


def _blocks(header):
    """ Kelompokkan kolom bernomor Butir: X1_1, X1_2 -> blok 'X1'. """
    out = {}
    for c in header:
        m = re.match(r"^([A-Za-z]+\d*(?:_[A-Za-z0-9]+)+)_\d+$", c.strip())
        if m:
            out.setdefault(m.group(1), []).append(c)
    return {k: v for k, v in out.items() if len(v) >= 2}


def auto_plan(rows, header, alpha, engine):
    """ Susun rencana uji dari struktur kolom; Returns (results, plan_lines). """
    results, plan = [], []
    blocks = _blocks(header)
    numeric = [c for c in header if _is_numeric_column(rows, c)]

    # 1) variabel dependen: blok berawalan "Y" (mis. Y_Kinerja_1..4)
    dv = next((b for b in blocks if b.split("_")[0] in ("Y", "y", "Y1", "Y2")), None)
    if dv is None:
        cand = [c for c in numeric
                if re.search(r"(kinerja|hasil|performance|skor|prestasi)", c, re.I)]
        if cand:
            dv = cand[0]
            blocks[dv] = [dv]
    dv_items = blocks.get(dv, [])
    if dv_items:
        plan.append(f"- variabel dependen: {dv} (butir: {', '.join(dv_items)})")

    # 2) reliabilitas tiap blok
    for name, items in blocks.items():
        raws = [col_raw(rows, c) for c in items]
        idx = [i for i in range(len(rows)) if all(r[i] is not None for r in raws)]
        if len(idx) < 3:
            continue
        cols = [[r[i] for i in idx] for r in raws]
        res = cronbach(cols, items)
        res["blok"] = name
        results.append(res)
        plan.append(f"- reliabilitas blok {name} ({len(items)} butir, n = {len(idx)})")

    # 3) variabel independen = mean tiap blok
    item_names = {c for items in blocks.values() for c in items}
    ivs = [b for b, items in blocks.items()
           if b != dv and all(_is_numeric_column(rows, c) for c in items)]
    ivs.sort()
    if not ivs:
        ivs = [c for c in numeric if c not in item_names]
    if dv and dv_items and ivs:
        yraw = col_raw(rows, dv_items[0])
        xsraw = []
        for b in ivs:
            raws = [col_raw(rows, c) for c in blocks[b]]
            xsraw.append([statistics.fmean([r[i] for r in raws if r[i] is not None])
                          if all(r[i] is not None for r in raws) else None for i in range(len(rows))])
        keep = [i for i in range(len(rows)) if yraw[i] is not None and all(x[i] is not None for x in xsraw)]
        if len(keep) >= len(xsraw) + 3:
            y2 = [yraw[i] for i in keep]
            xs2 = [[x[i] for i in keep] for x in xsraw]
            names = [f"{b} (mean {len(blocks[b])} butir)" for b in ivs]
            r = ols(y2, xs2, names, alpha, engine)
            if r:
                r["blok_dv"] = dv
                results.append(r)
                plan.append(f"- regresi {dv} ~ {', '.join(names)} (n = {len(keep)})")
        # 4) korelasi tiap IV terhadap DV
        for j, b in enumerate(ivs):
            xraw = xsraw[j]
            pairs = [(xraw[i], yraw[i]) for i in range(len(rows))
                     if xraw[i] is not None and yraw[i] is not None]
            if len(pairs) >= 4:
                r = pearson([p[0] for p in pairs], [p[1] for p in pairs], alpha, engine)
                r["label"] = f"{b} (mean {len(blocks[b])} butir) dengan {dv}"
                results.append(r)
                plan.append(f"- korelasi {b} dengan {dv}")

    # 5) uji kelompok pada kolom kategorikal
    grup_hint = re.compile(r"(divisi|unit|kelompok|jenis|status|jk|gender|tingkat|jenjang|"
                           r"pendidikan|usia|umur|pengalaman|masa_kerja|status_gizi|"
                           r"kelamin|treatment|intervensi|kelompok_uji)", re.I)
    kandidat = [c for c in header if c not in item_names and c != dv]
    kandidat = ([c for c in kandidat if grup_hint.search(c)]
                + [c for c in kandidat if not grup_hint.search(c)])
    for c in kandidat:
        if _is_numeric_column(rows, c) and c not in numeric:
            continue
        lv = _levels(rows, c)
        if not 2 <= len(lv) <= 6 or c == dv:
            continue
        target = dv_items[0] if dv_items else None
        if not target:
            continue
        groups = {}
        for r0 in rows:
            g = str(r0.get(c, "")).strip()
            v = num(r0.get(target))
            if g and v is not None:
                groups.setdefault(g, []).append(v)
        g2 = [(k, v) for k, v in groups.items() if len(v) >= 2]
        if len(g2) == 2:
            res = ttest_independent(g2[0][1], g2[1][1], alpha, engine)
            res["label"] = f"kelompok {c} = {g2[0][0]} vs {g2[1][0]}"
            res["grup"] = c
            results.append(res)
            plan.append(f"- t-test independen {c} pada {target} (2 kelompok: {g2[0][0]}, {g2[1][0]})")
        elif len(g2) > 2:
            res = anova_oneway(g2, alpha, engine)
            res["label"] = f"{c} pada {target} (k = {len(g2)} kelompok)"
            res["grup"] = c
            results.append(res)
            plan.append(f"- ANOVA {c} pada {target} ({len(g2)} kelompok)")
        if results:
            break
    return results, plan


# ------------------------------------------------------------------ keluaran

def render(results, alpha, meta):
    out = ["# Hasil Uji Statistik — Siap Tempel ke BAB III\n"]
    out.append(f"Sumber data: `{meta['file']}` | n = **{meta['n']}** baris, "
               f"{meta['n_cols']} kolom | α = {fmt(alpha)} | engine: **{meta['engine']}**\n")
    out.append("> Angka di bawah ini dihitung dari file dataset. Salin ke naskah proposal dengan")
    out.append("> penanda `[D:nama_kolom]`. Jangan mengarang angka.\n")
    for i, res in enumerate(results, 1):
        judul = res["test"] + (f" — {res['label']}" if res.get("label") else "")
        out.append(f"## {i}. {judul}\n")
        if res["test"] == "Regresi linear berganda (OLS)":
            out.append(f"F model: F({res['df1']}, {res['df2']}) = {fmt(res['f'])}, "
                       f"p = {fmt(res['p_model'])} | R² = {fmt(res['r2'])} | "
                       f"Adj. R² = {fmt(res['adj_r2'])}\n")
            out.append("| Variabel | B | SE | t | p | Keputusan |")
            out.append("|----------|---|---|---|----|------------|")
            for x in res["terms"]:
                out.append(f"| {x['term']} | {fmt(x['b'])} | {fmt(x['se'])} | {fmt(x['t'])} "
                           f"| {fmt(x['p'])} | H₀ {x['keputusan']} |")
            out.append("")
        elif res["test"] == "One-way ANOVA":
            out.append("| Kelompok | n | Mean | SD |")
            out.append("|----------|---|------|----|")
            for d in res["detail"]:
                out.append(f"| {d['kelompok']} | {d['n']} | {fmt(d['mean'])} | {fmt(d['sd'])} |")
            out.append(f"\nF({res['df1']}, {res['df2']}) = {fmt(res['F'])}, p = {fmt(res['p'])}\n")
        elif res["test"] == "Chi-square (tabel silang)":
            out.append("| " + " | ".join(str(c) for c in res["tabel"][0].keys()) + " |")
            out.append("|" + "---|" * len(res["tabel"][0]))
            for row in res["tabel"]:
                out.append("| " + " | ".join(str(v) for v in row.values()) + " |")
            out.append(f"\nχ²({res['df']}) = {fmt(res['chi2'])}, p = {fmt(res['p'])} | "
                       f"expected count terkecil = {fmt(res['min_exp'], 1)} | "
                       f"sel dengan expected < 5: {res.get('sel_expected_lt5', '-')}/"
                       f"{res.get('jumlah_sel', '-')}\n")
            if res.get("catatan"):
                out.append(f"> Catatan: {res['catatan']}\n")
        elif res["test"] == "Independent t-test":
            out.append(f"t({res['df']}) = {fmt(res['t'])}, p = {fmt(res['p'])}, "
                       f"Cohen's d = {fmt(res['cohens_d'])}\n")
        elif res["test"] == "Paired t-test":
            out.append(f"t({res['df']}) = {fmt(res['t'])}, p = {fmt(res['p'])}, "
                       f"Cohen's d_z = {fmt(res['cohens_dz'])}\n")
        elif res["test"] in ("Pearson correlation", "Spearman correlation"):
            out.append(f"r = {fmt(res['r'])}, r² = {fmt(res['r2'])}, t({res['df']}) = "
                       f"{fmt(res['t'])}, p = {fmt(res['p'])}\n")
        elif res["test"] == "Cronbach's alpha":
            out.append(f"α = {fmt(res['alpha'])} dari {res['k']} butir "
                       f"({', '.join(res['items'])}) — kategori {res['kategori']}\n")
        nar = narrative(res, alpha)
        if nar:
            out.append(f"**Narasi siap pakai:** {nar}\n")
        if res.get("blok"):
            out.append(f"Penanda sumber data: `[D:{res['blok']}]`\n")
    return "\n".join(out)


def parse_list(v):
    return [x.strip() for x in v.split(",") if x.strip()]


def parse_pairs(spec, keys, default_first=None):
    """Parse 'v1=kolomA,v2=kolomB' atau 'kolomA,kolomB' (pairs mode)."""
    out = {}
    bare = []
    for part in re.split(r"[,;]", spec or ""):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            k = k.strip().lower()
            v = v.strip()
            if k in keys:
                out[k] = v
            continue
        bare.append(part)
    return out, bare


def main():
    ap = argparse.ArgumentParser(description="Jalankan uji statistik nyata untuk proposal")
    ap.add_argument("file")
    ap.add_argument("--regresi",
                    help="DV=nama_kolom_dependen[,X=iv1;iv2] (tanpa X: semua kolom numerik lain)")
    ap.add_argument("--ttest-independen", help="DV=kolom --grup=kolom (pisah dengan --grup)")
    ap.add_argument("--ttest-paired", help="DV1=kolom --dv2=kolom")
    ap.add_argument("--anova", help="DV=kolom --grup=kolom")
    ap.add_argument("--chi2", help="v1=kolomA,v2=kolomB")
    ap.add_argument("--korelasi", help="v1=kolomA,v2=kolomB --metode pearson|spearman")
    ap.add_argument("--cronbach", help="a=X1_1,X1_2,X1_3")
    ap.add_argument("--auto", action="store_true",
                    help="deteksi otomatis uji yang cocok dari nama & tipe kolom")
    ap.add_argument("--grup")
    ap.add_argument("--metode", default="pearson")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--out", default="hasil_uji")
    ap.add_argument("--json-only", action="store_true")
    ap.add_argument("--engine", default="auto", choices=["auto", "scipy", "pure"])
    ap.add_argument("--alpha-per-test", action="store_true",
                    help="tampilkan alpha per uji pada tabel")
    args = ap.parse_args()

    if not os.path.exists(args.file):
        sys.exit(f"ERROR: file tidak ditemukan: {args.file}")
    rows, header = load(args.file)
    results = []
    eng = args.engine
    if eng == "auto" and not have_scipy():
        print("INFO: scipy tidak terpasang, memakai perhitungan internal (pure).",
              file=sys.stderr)

    def keyed(spec):
        out = {}
        for part in re.split(r"\s*,\s*", spec or ""):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                out[k.strip().lower()] = v.strip()
        return out

    def keyed_ci(spec):
        """ seperti keyed(), tetapi dv1/dv2 dinormalkan dan nilai kolom
        tidak diubah huruf besarnya. """
        out = {}
        for k, v in keyed(spec).items():
            k = {"y": "dv", "dependen": "dv", "iv": "x", "independen": "x"}.get(k, k)
            if k == "dv1":
                k = "dv"
            elif k == "dv1b":
                k = "dv2"
            out[k] = v
        return out

    if args.regresi:
        # format: "DV=nama_kolom" (IV = semua kolom numerik lain)
        #         "DV=nama_kolom,X=iv1;iv2" atau "DV=kolom,iv1;iv2,iv3"
        dv, ivs = None, []
        for part in re.split(r"[,;]", args.regresi):
            part = part.strip()
            if not part:
                continue
            if "=" in part:
                key, val = part.split("=", 1)
                key = key.strip().upper()
                vals = [v.strip() for v in val.split(";") if v.strip()]
                if key in ("DV", "Y", "DEPENDEN"):
                    dv = vals[0]
                elif key in ("X", "IV", "INDEPENDEN"):
                    ivs.extend(vals)
            else:
                ivs.append(part)
        if not dv:
            sys.exit("ERROR: --regresi wajib menyebut DV=nama_kolom")
        if not ivs:
            ivs = [c for c in header if c != dv]
        yraw = col_raw(rows, dv)
        xsraw = [col_raw(rows, c) for c in ivs]
        keep = [i for i in range(len(yraw))
                if yraw[i] is not None and all(x[i] is not None for x in xsraw)]
        if len(keep) < len(ivs) + 3:
            sys.exit("ERROR: kasus lengkap terlalu sedikit untuk regresi berganda")
        y2 = [yraw[i] for i in keep]
        xs2 = [[x[i] for i in keep] for x in xsraw]
        res = ols(y2, xs2, ivs, args.alpha, eng)
        if res:
            results.append(res)

    if args.ttest_independen or args.anova:
        kv = keyed_ci(args.ttest_independen or args.anova)
        dv, grp = kv["dv"], args.grup
        groups = {}
        for r in rows:
            g = str(r.get(grp, "")).strip()
            v = num(r.get(dv))
            if g and v is not None:
                groups.setdefault(g, []).append(v)
        g = [(k, v) for k, v in groups.items() if len(v) >= 2]
        if args.anova:
            results.append(anova_oneway(g, args.alpha, eng))
        elif len(g) == 2:
            results.append(ttest_independent(g[0][1], g[1][1], args.alpha, eng))
        else:
            sys.exit(f"ERROR: t-test butuh tepat 2 kelompok, ditemukan {len(g)}")

    if args.ttest_paired:
        kv = keyed_ci(args.ttest_paired)
        ra, rb = col_raw(rows, kv["dv"]), col_raw(rows, kv.get("dv2") or kv.get("dv1b"))
        pairs = [(a, b) for a, b in zip(ra, rb) if a is not None and b is not None]
        if len(pairs) < 3:
            sys.exit("ERROR: pasangan data untuk paired t-test terlalu sedikit")
        results.append(ttest_paired([p[0] for p in pairs], [p[1] for p in pairs], args.alpha, eng))

    if args.chi2:
        kv, bare = parse_pairs(args.chi2, ("v1", "v2", "a", "b"))
        va = kv.get("v1") or kv.get("a") or (bare[0] if bare else None)
        vb = kv.get("v2") or kv.get("b") or (bare[1] if len(bare) > 1 else None)
        if not va or not vb:
            sys.exit("ERROR: --chi2 butuh dua kolom, mis. v1=Divisi,v2=Jenis_Kelamin")
        results.append(chi2(rows, va, vb, args.alpha))

    if args.korelasi:
        kv, bare = parse_pairs(args.korelasi, ("v1", "v2", "a", "b", "x", "y"))
        va = kv.get("v1") or kv.get("a") or kv.get("x") or (bare[0] if bare else None)
        vb = kv.get("v2") or kv.get("b") or kv.get("y") or (bare[1] if len(bare) > 1 else None)
        if not va or not vb:
            sys.exit("ERROR: --korelasi butuh dua kolom, mis. v1=X1,v2=Y1")
        ra, rb = col_raw(rows, va), col_raw(rows, vb)
        pairs = [(a, b) for a, b in zip(ra, rb) if a is not None and b is not None]
        if len(pairs) < 4:
            sys.exit("ERROR: pasangan data untuk korelasi terlalu sedikit")
        fn = spearman if args.metode.lower() == "spearman" else pearson
        results.append(fn([p[0] for p in pairs], [p[1] for p in pairs], args.alpha, eng))

    if args.cronbach:
        kv, bare = parse_pairs(args.cronbach, ("a", "items", "butir", "k"))
        names = [c.strip() for c in (kv.get("a") or kv.get("items")
                                     or kv.get("butir") or kv.get("k") or "").split(";")
                 if c.strip()]
        names += bare
        if not names:
            sys.exit("ERROR: --cronbach butuh daftar kolom, mis. a=X1_1,X1_2,X1_3")
        raws = [col_raw(rows, c) for c in names]
        idx = [i for i in range(len(rows)) if all(r[i] is not None for r in raws)]
        if len(idx) < 3:
            sys.exit(f"ERROR: hanya {len(idx)} kasus lengkap untuk Cronbach's alpha")
        cols = [[r[i] for i in idx] for r in raws]
        results.append(cronbach(cols, names))

    rencana = []
    if args.auto and not results:
        results, rencana = auto_plan(rows, header, args.alpha, eng)
        if not results:
            sys.exit("ERROR: mode --auto tidak menemukan pola uji pada dataset ini. "
                     "Gunakan --regresi, --ttest-independen, --ttest-paired, --anova, "
                     "--chi2, --korelasi, atau --cronbach secara eksplisit.")
        print("Rencana uji otomatis:\n" + "\n".join(rencana), file=sys.stderr)

    if not results:
        sys.exit("ERROR: tidak ada uji yang diminta. Gunakan --regresi, --ttest-independen, "
                 "--ttest-paired, --anova, --chi2, --korelasi, atau --cronbach.\n"
                 "       Contoh: --regresi DV=Skor_Kinerja")

    meta = {"file": os.path.abspath(args.file), "n": len(rows), "n_cols": len(header),
            "engine": "scipy" if (eng in ("auto", "scipy") and have_scipy()) else "pure",
            "alpha": args.alpha, "waktu": datetime.now().isoformat(timespec="seconds")}
    with open(args.out + ".json", "w", encoding="utf-8") as fh:
        json.dump({"meta": meta, "hasil": results}, fh, ensure_ascii=False, indent=2)
    print(f"Tulis: {args.out}.json", file=sys.stderr)
    if not args.json_only:
        with open(args.out + ".md", "w", encoding="utf-8") as fh:
            fh.write(render(results, args.alpha, meta))
        print(f"Tulis: {args.out}.md", file=sys.stderr)
    print(render(results, args.alpha, meta))


if __name__ == "__main__":
    main()
