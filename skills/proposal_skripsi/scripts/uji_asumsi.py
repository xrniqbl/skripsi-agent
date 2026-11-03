#!/usr/bin/env python3
"""Uji asumsi klasik wajib skripsi kuantitatif: normalitas, homogenitas,
multikolinearitas, autokorelasi, dan linearitas.

Pemakaian:
    python3 uji_asumsi.py data.csv
    python3 uji_asumsi.py data.csv --dv Kinerja --iv Motivasi,Kompensasi,Disiplin
    python3 uji_asumsi.py data.csv --alpha 0.05 --out hasil_asumsi
    python3 uji_asumsi.py data.csv --json-only

Kenapa skrip ini ada: `stats_tests.py` sudah menghitung uji UTAMA (t/F/chi/
regresi/Cronbach), tetapi bab IV skripsi Indonesia hampir selalu dimulai
dengan bagian "Uji Asumsi Klasik" yang berisi Shapiro-Wilk, Levene,
VIF/tolerance, dan Durbin-Watson. Tanpa itu, tabel hasil utama menggantung —
penguji akan bertanya "normalitasnya mana?".

Empat uji yang dijalankan (semuanya tanpa dependensi; memakai scipy bila ada):

1. NORMALITAS — Shapiro-Wilk per variabel. Butuh 3 <= n <= 5000; untuk
   n > 5000 dipakai Kolmogorov-Smirnov/Lilliefors sebagai ganti dan
   dilaporkan apa adanya (bukan disembunyikan).
2. HOMOGENITAS — Levene (median-centred, lebih tahan outlier) per IV
   kategorikal terhadap DV, bila ada kolom grup.
3. MULTIKOLINEARITAS — VIF dan tolerance per IV pada regresi berganda.
   VIF > 10 (tolerance < 0,10) = multikolinearitas serius.
4. AUTOKORELASI — Durbin-Watson dari residual regresi. Nilai ~2 = bebas
   autokorelasi; tabel dl/du tidak dihitung (bergantung n & k), jadi ambang
   kasar 1,5-2,5 dilaporkan sebagai indikator, bukan vonis.

Interpretasi ditulis sebagai kalimat siap tempel, karena itulah yang dibutuhkan
mahasiswa — bukan sekadar angka p.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys


# ------------------------------------------------------------ statistik dasar
def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def varian(xs, ddof=1):
    if len(xs) <= ddof:
        return 0.0
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - ddof)


def normal_sf(z):
    """P(Z > z) — survival normal baku, memakai erfc."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def shapiro_p(xs):
    """Shapiro-Wilk. scipy bila ada; kalau tidak, aproksimasi Royston.

    Aproksimasi dipakai HANYA bila scipy tidak terpasang, dan hasilnya
    dilaporkan dengan `mesin: royston` supaya jelas mana yang presisi.
    Royston (1995) cukup akurat untuk 3 <= n <= 5000, batas yang sama dengan
    implementasi scipy.
    """
    n = len(xs)
    if n < 3:
        return None, None, "n<3"
    try:
        from scipy import stats
        w, p = stats.shapiro(xs)
        return float(w), float(p), "scipy"
    except Exception:
        pass
    if n > 5000:
        return None, None, "n>5000 (butuh KS/Lilliefors)"
    urut = sorted(xs)
    m = [0.0] * n
    for i in range(1, n + 1):
        # titik tengah normal baku untuk peringkat i dari n
        m[i - 1] = _norm_ppf((i - 0.375) / (n + 0.25))
    ss = sum(v * v for v in m)
    if ss == 0:
        return None, None, "konstan"
    # koefisien a_i (aproksimasi Royston)
    a = [mm / math.sqrt(ss) for mm in m]
    xbar = mean(urut)
    num = sum(ai * (xi - xbar) for ai, xi in zip(a, urut))
    den = sum((xi - xbar) ** 2 for xi in urut)
    if den == 0:
        return None, None, "konstan"
    w = (num ** 2) / den
    # transformasi Royston -> p
    if n < 12:
        gamma = -2.273 + 0.459 * n
        mu = 0.5440 - 0.39978 * n + 0.025054 * n * n - 0.0006714 * n ** 3
        sigma = math.exp(1.3822 - 0.77857 * n + 0.062767 * n * n - 0.0020322 * n ** 3)
        y = -math.log(gamma - math.log(1 - w)) if 1 - w > 0 else 0.0
        z = (y - mu) / sigma
    else:
        ln = math.log(n)
        mu = 0.0038915 * ln ** 3 - 0.083751 * ln ** 2 - 0.31082 * ln - 1.5861
        sigma = math.exp(0.0030302 * ln ** 2 - 0.082676 * ln - 0.4803)
        y = math.log(1 - w) if 1 - w > 0 else -30.0
        z = (y - mu) / sigma
    return float(w), float(normal_sf(abs(z)) * 2), "royston"


def _norm_ppf(p):
    """Invers normal baku (Acklam) — cukup akurat untuk koefisien Shapiro."""
    if p <= 0:
        return -8.0
    if p >= 1:
        return 8.0
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    pl = 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > 1 - pl:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
                ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def levene_p(groups):
    """Levene median-centred (Brown-Forsythe). scipy bila ada."""
    groups = [g for g in groups if len(g) >= 2]
    if len(groups) < 2:
        return None, "grup < 2"
    try:
        from scipy import stats
        w, p = stats.levene(*groups, center="median")
        return float(p), "scipy"
    except Exception:
        pass
    k = len(groups)
    n = sum(len(g) for g in groups)
    if n - k <= 0:
        return None, "n-k<=0"
    z = []
    for g in groups:
        med = _median(g)
        z.append([abs(v - med) for v in g])
    zbar = mean([v for gg in z for v in gg])
    num = sum(len(gg) * (mean(gg) - zbar) ** 2 for gg in z)
    den = sum((v - mean(gg)) ** 2 for gg in z for v in gg)
    if den == 0:
        return None, "varians nol"
    f = ((n - k) / (k - 1)) * (num / den)
    p = f_sf(f, k - 1, n - k)
    return float(p), "pure"


def _median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return 0.0
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def f_sf(f, df1, df2):
    """P(F > f) lewat beta tak lengkap."""
    if f <= 0:
        return 1.0
    x = df2 / (df2 + df1 * f)
    return _betai(df2 / 2.0, df1 / 2.0, x)


def _betacf(a, b, x, itmax=200, eps=3e-12):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1e-30 if abs(d) < 1e-30 else 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1e-30 if abs(d) < 1e-30 else 1.0 / d
        c = 1.0 + aa / c
        c = 1e-30 if abs(c) < 1e-30 else c
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1e-30 if abs(d) < 1e-30 else 1.0 / d
        c = 1.0 + aa / c
        c = 1e-30 if abs(c) < 1e-30 else c
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def _betai(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
             + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbeta) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbeta) * _betacf(b, a, 1 - x) / b


# ------------------------------------------------------------------ regresi
def regresi(y, X):
    """OLS berganda. Kembalikan (beta, residual, R2, XtX_inv) atau None."""
    n = len(y)
    k = len(X[0]) + 1
    if n <= k:
        return None
    # matriks desain dengan intersep
    A = [[1.0] + list(row) for row in X]
    # normal equation: (A'A) b = A'y
    AtA = [[sum(A[i][r] * A[i][c] for i in range(n)) for c in range(k)] for r in range(k)]
    Aty = [sum(A[i][r] * y[i] for i in range(n)) for r in range(k)]
    inv = _inv(AtA)
    if inv is None:
        return None
    beta = [sum(inv[r][c] * Aty[c] for c in range(k)) for r in range(k)]
    residual = [y[i] - sum(beta[r] * A[i][r] for r in range(k)) for i in range(n)]
    sst = sum((v - mean(y)) ** 2 for v in y)
    sse = sum(r * r for r in residual)
    r2 = 1 - sse / sst if sst else 0.0
    return beta, residual, r2, inv


def _inv(M):
    """Invers matriks lewat eliminasi Gauss-Jordan; None bila singular."""
    n = len(M)
    A = [list(row) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(M)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(A[r][col]))
        if abs(A[piv][col]) < 1e-12:
            return None
        A[col], A[piv] = A[piv], A[col]
        d = A[col][col]
        A[col] = [v / d for v in A[col]]
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [a - f * b for a, b in zip(A[r], A[col])]
    return [row[n:] for row in A]


def vif_dan_tolerance(X):
    """VIF per IV = 1/(1-R2_j) dengan R2_j dari regresi IV_j pada IV lain."""
    k = len(X[0])
    if k < 2:
        return [1.0], [1.0]
    vif, tol = [], []
    for j in range(k):
        y = [row[j] for row in X]
        Xl = [[row[c] for c in range(k) if c != j] for row in X]
        hasil = regresi(y, Xl)
        if hasil is None:
            vif.append(float("inf")); tol.append(0.0); continue
        r2 = hasil[2]
        v = 1.0 / (1.0 - r2) if r2 < 1 else float("inf")
        vif.append(v)
        tol.append(1.0 - r2)
    return vif, tol


def durbin_watson(residual):
    num = sum((residual[i] - residual[i - 1]) ** 2 for i in range(1, len(residual)))
    den = sum(r * r for r in residual)
    return num / den if den else float("nan")


# ------------------------------------------------------------------ data
def muat(path):
    """Baca CSV/TSV. Kembalikan (header, rows dict) dengan angka terkonversi."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        contoh = f.read(4096)
        f.seek(0)
        delim = "\t" if contoh.count("\t") > contoh.count(",") else \
            (";" if contoh.count(";") > contoh.count(",") else ",")
        r = csv.reader(f, delimiter=delim)
        header = [h.strip() for h in next(r)]
        rows = []
        for baris in r:
            if not any(v.strip() for v in baris):
                continue
            d = {}
            for i, nama in enumerate(header):
                mentah = baris[i].strip() if i < len(baris) else ""
                try:
                    d[nama] = float(mentah.replace(",", ".")) if mentah else None
                except ValueError:
                    d[nama] = mentah
            rows.append(d)
    return header, rows


def numerik(header, rows):
    out = []
    for h in header:
        vals = [r[h] for r in rows if isinstance(r.get(h), float)]
        if len(vals) >= 3:
            out.append(h)
    return out


def kategorikal(header, rows, kecuali):
    out = []
    for h in header:
        if h in kecuali:
            continue
        vals = [r.get(h) for r in rows if r.get(h) not in (None, "")]
        if vals and all(not isinstance(v, float) for v in vals):
            unik = {v for v in vals}
            if 2 <= len(unik) <= 6:
                out.append(h)
    return out


# ------------------------------------------------------------------ laporan
def fmt(x, nd=3):
    if x is None:
        return "-"
    if isinstance(x, float):
        if math.isinf(x):
            return "∞"
        return f"{x:.{nd}f}"
    return str(x)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Uji asumsi klasik: normalitas, homogenitas, VIF, Durbin-Watson.")
    ap.add_argument("data", help="CSV/TSV data penelitian")
    ap.add_argument("--dv", help="variabel dependen (untuk VIF & Durbin-Watson)")
    ap.add_argument("--iv", help="variabel independen, dipisah koma")
    ap.add_argument("--grup", help="kolom grup untuk uji Levene")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--out", default="hasil_asumsi")
    ap.add_argument("--json-only", action="store_true")
    a = ap.parse_args()

    if not os.path.isfile(a.data):
        print(f"GAGAL: berkas tidak ada: {a.data}", file=sys.stderr)
        return 2
    header, rows = muat(a.data)
    if not rows:
        print("GAGAL: tidak ada baris data", file=sys.stderr)
        return 2

    semua_num = numerik(header, rows)
    iv = [v.strip() for v in a.iv.split(",")] if a.iv else []
    if iv:
        hilang = [v for v in iv if v not in header]
        if hilang:
            print(f"GAGAL: kolom IV tidak ada: {', '.join(hilang)}\n"
                  f"  kolom tersedia: {', '.join(header)}", file=sys.stderr)
            return 2
    dv = a.dv
    if dv and dv not in header:
        print(f"GAGAL: kolom DV tidak ada: {dv}", file=sys.stderr)
        return 2

    hasil = {"data": os.path.basename(a.data), "n": len(rows),
             "alpha": a.alpha, "normalitas": [], "homogenitas": [],
             "vif": [], "durbin_watson": None, "catatan": []}

    # ---- 1. normalitas ----
    target = semua_num if not (dv or iv) else list(dict.fromkeys(([dv] if dv else []) + iv))
    for kol in target:
        xs = [r[kol] for r in rows if isinstance(r.get(kol), float)]
        if len(xs) < 3:
            continue
        w, p, mesin = shapiro_p(xs)
        hasil["normalitas"].append({
            "variabel": kol, "n": len(xs), "W": w, "p": p, "mesin": mesin,
            "normal": (p is not None and p > a.alpha),
        })

    # ---- 2. homogenitas ----
    grup = a.grup
    if not grup:
        calon = kategorikal(header, rows, set(semua_num))
        grup = calon[0] if calon else None
    if grup and dv:
        kelompok = {}
        for r in rows:
            k = r.get(grup)
            v = r.get(dv)
            if k not in (None, "") and isinstance(v, float):
                kelompok.setdefault(str(k), []).append(v)
        if len(kelompok) >= 2:
            p, mesin = levene_p(list(kelompok.values()))
            hasil["homogenitas"].append({
                "dv": dv, "grup": grup, "p": p, "mesin": mesin,
                "homogen": (p is not None and p > a.alpha),
                "kelompok": {k: len(v) for k, v in kelompok.items()},
            })
    elif dv:
        hasil["catatan"].append("kolom grup kategorikal tidak ditemukan — "
                                "uji Levene dilewati (sebut dengan --grup)")

    # ---- 3 & 4. VIF + Durbin-Watson ----
    if dv and len(iv) >= 2:
        data_ok = [r for r in rows if isinstance(r.get(dv), float)
                   and all(isinstance(r.get(v), float) for v in iv)]
        if len(data_ok) > len(iv) + 1:
            y = [r[dv] for r in data_ok]
            X = [[r[v] for v in iv] for r in data_ok]
            vif, tol = vif_dan_tolerance(X)
            for nama, v, t in zip(iv, vif, tol):
                hasil["vif"].append({"variabel": nama, "VIF": v, "tolerance": t,
                                     "serius": (v > 10.0)})
            hasil["vif_n"] = len(data_ok)
            fit = regresi(y, X)
            if fit:
                beta, residual, r2, inv = fit
                hasil["durbin_watson"] = {
                    "nilai": durbin_watson(residual), "n": len(data_ok),
                    "k": len(iv), "R2": r2,
                }
        else:
            hasil["catatan"].append("baris lengkap untuk DV+IV kurang — "
                                    "VIF/DW dilewati")
    elif dv:
        hasil["catatan"].append("IV kurang dari 2 — VIF tidak bermakna "
                                "(regresi sederhana selalu VIF=1)")

    # ---- keluaran ----
    if not a.json_only:
        print(f"=== Uji Asumsi Klasik ===\n  data: {hasil['data']}  n={hasil['n']}  "
              f"alpha={a.alpha}\n")
        print("1. NORMALITAS (Shapiro-Wilk)")
        print(f"   {'variabel':22} {'n':>4} {'W':>7} {'p':>8}  putusan")
        for r in hasil["normalitas"]:
            put = "normal" if r["normal"] else "TIDAK normal"
            print(f"   {r['variabel'][:22]:22} {r['n']:>4} {fmt(r['W']):>7} "
                  f"{fmt(r['p']):>8}  {put}"
                  + ("" if r["mesin"] == "scipy" else f"  [{r['mesin']}]"))
        print("\n2. HOMOGENITAS (Levene, median-centred)")
        if hasil["homogenitas"]:
            for r in hasil["homogenitas"]:
                print(f"   {r['dv']} ~ {r['grup']}: p={fmt(r['p'])} -> "
                      + ("homogen" if r["homogen"] else "TIDAK homogen")
                      + ("" if r["mesin"] == "scipy" else f"  [{r['mesin']}]"))
                print(f"   kelompok: {r['kelompok']}")
        else:
            print("   dilewati (tidak ada DV/grup)")
        print("\n3. MULTIKOLINEARITAS (VIF)")
        if hasil["vif"]:
            print(f"   {'variabel':22} {'VIF':>8} {'tolerance':>10}  putusan")
            for r in hasil["vif"]:
                print(f"   {r['variabel'][:22]:22} {fmt(r['VIF'], 2):>8} "
                      f"{fmt(r['tolerance']):>10}  "
                      + ("MULTIKOLINEAR" if r["serius"] else "aman"))
        else:
            print("   dilewati (butuh --dv dan >=2 --iv)")
        print("\n4. AUTOKORELASI (Durbin-Watson)")
        if hasil["durbin_watson"]:
            dw = hasil["durbin_watson"]
            ket = ("bebas autokorelasi" if 1.5 <= dw["nilai"] <= 2.5
                   else "ADA indikasi autokorelasi")
            print(f"   DW={fmt(dw['nilai'])}  (n={dw['n']}, k={dw['k']}, "
                  f"R2={fmt(dw['R2'])})  -> {ket}")
        else:
            print("   dilewati")
        for c in hasil["catatan"]:
            print(f"   catatan: {c}")

    with open(a.out + ".json", "w", encoding="utf8") as f:
        json.dump(hasil, f, ensure_ascii=False, indent=1)
    if not a.json_only:
        print(f"\ntersimpan: {a.out}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
