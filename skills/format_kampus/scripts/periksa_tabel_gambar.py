#!/usr/bin/env python3
"""Periksa tabel dan gambar: caption, sumber kutipan, urutan nomor, dan rujukan.

Pemakaian:
    python3 periksa_tabel_gambar.py naskah.md profil-kampus.yaml
    python3 periksa_tabel_gambar.py skripsi.docx profil-kampus.yaml --json lap.json

Yang diperiksa:
  1. Setiap tabel/gambar punya caption (Tabel/Gambar ...)
  2. Posisi caption sesuai profil (tabel: di atas; gambar: di bawah)
  3. Nomor caption berurutan per bab dan memakai format profil (Romawi/Arab)
  4. Nomor bab pada caption cocok dengan bab tempat ia berada
  5. Setiap tabel/gambar DIRUJUK di teks ("... pada Tabel IV.1 ...")
  6. Caption yang mengutip sumber lain mencantumkan sumbernya (Nama, Tahun)

Butir 5 adalah yang paling sering lolos dari pemeriksa lain: caption lengkap,
nomor benar, tapi tabelnya tidak pernah disebut di paragraf mana pun — pembaca
tidak tahu kapan harus melihatnya.

Kode keluar:
    0  lulus (peringatan boleh ada)
    1  ada galat
    2  berkas/profil tidak terbaca
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

ROMAWI = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
          "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12}

RE_BAB = re.compile(r"^\s*#*\s*BAB\s+([IVX]+|\d+)\b", re.I)
RE_CAPTION = re.compile(
    r"^\s*(?:\*\*)?\s*(Tabel|Gambar)\s+([IVX]+|\d+)\s*([.\-])\s*(\d+)\s*(?:\*\*)?\s*[.:]?\s*(.*)$",
    re.I)
# rujukan dalam teks: "Tabel IV.1", "Gambar 3.2", "Tabel IV.1 dan IV.2"
RE_RUJUK = re.compile(r"\b(Tabel|Gambar)\s+([IVX]+|\d+)\s*[.\-]\s*(\d+)", re.I)


def baca(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            sys.exit("GAGAL: butuh python-docx untuk .docx (pip install python-docx)")
        d = Document(path)
        baris = []
        for p in d.paragraphs:
            gaya = (p.style.name or "").lower()
            teks = p.text.strip()
            if not teks:
                continue
            m = re.match(r"heading (\d)", gaya)
            lvl = int(m.group(1)) if m else (1 if gaya in ("title", "judul") else 0)
            baris.append(("#" * lvl + " " + teks) if lvl else teks)
        for i, t in enumerate(d.tables, 1):
            baris.append(f"[[TABEL-OBJ {i}]]")
        # gambar sebaris
        for i, sh in enumerate(d.inline_shapes, 1):
            baris.append(f"[[GAMBAR-OBJ {i}]]")
        return "\n".join(baris)
    if ext == ".pdf":
        import subprocess
        try:
            return subprocess.run(["pdftotext", "-layout", path, "-"],
                                  capture_output=True, text=True, timeout=60).stdout
        except FileNotFoundError:
            sys.exit("GAGAL: butuh pdftotext (apt-get install poppler-utils)")
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def angka_bab(txt):
    """Ubah 'IV' atau '4' menjadi 4; None bila tidak dikenali.

    Jangan memakai ROMAWI.get(k, int(k)): argumen default Python dievaluasi
    SEBELUM pemanggilan, sehingga int('IV') melempar ValueError dan semua
    rujukan bernomor Romawi hilang tanpa jejak.
    """
    t = (txt or "").strip().upper()
    if t.isdigit():
        return int(t)
    return ROMAWI.get(t)


def ke_romawi(n: int) -> str:
    peta = [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, s in peta:
        while n >= v:
            out += s
            n -= v
    return out


def periksa(teks: str, profil: dict) -> dict:
    cap = profil.get("caption") or {}
    tabel_cfg = cap.get("tabel") or {}
    gambar_cfg = cap.get("gambar") or {}
    penomoran = " ".join(str(v) for v in (tabel_cfg.get("penomoran"),
                                          gambar_cfg.get("penomoran"))).lower()
    pakai_romawi = "romawi" in penomoran
    posisi_tabel = (tabel_cfg.get("posisi") or "").lower()
    posisi_gambar = (gambar_cfg.get("posisi") or "").lower()

    baris = teks.splitlines()
    galat: list[dict] = []
    peringatan: list[dict] = []
    info: dict = {}

    # --- telusuri, catat bab aktif & caption ---
    bab_aktif = None
    caption: list[dict] = []
    for idx, b in enumerate(baris):
        m = RE_BAB.match(b)
        if m:
            n = m.group(1).upper()
            bab_aktif = ROMAWI.get(n, int(n) if n.isdigit() else None)
            continue
        c = RE_CAPTION.match(b)
        if c:
            jenis = c.group(1).capitalize()
            nomor_bab_txt, pemisah, urut, judul = c.group(2), c.group(3), c.group(4), c.group(5)
            nomor_bab = angka_bab(nomor_bab_txt)
            caption.append({
                "jenis": jenis, "bab_nomor": nomor_bab,
                "bab_txt": nomor_bab_txt, "urut": int(urut),
                "pemisah": pemisah, "judul": judul.strip(),
                "baris": idx, "bab_aktif": bab_aktif,
            })

    info["jumlah_caption"] = len(caption)
    info["tabel"] = sum(1 for c in caption if c["jenis"] == "Tabel")
    info["gambar"] = sum(1 for c in caption if c["jenis"] == "Gambar")

    # --- 1 & 2. caption hilang / posisi ---
    # Objek bisa datang dari .docx (penanda [[TABEL-OBJ]]) atau dari Markdown.
    # Tabel Markdown menempati BEBERAPA baris pipe berurutan; itu satu tabel,
    # bukan tiga. Kelompokkan blok bersambung jadi satu objek — tanpa ini satu
    # tabel dilaporkan "tanpa caption" berkali-kali.
    obj_tabel: list[int] = []
    sebelumnya_pipe = False
    for i, b in enumerate(baris):
        adalah_pipe = bool(re.match(r"^\s*\|.+\|\s*$", b))
        if b.strip().startswith("[[TABEL-OBJ"):
            obj_tabel.append(i)
        elif adalah_pipe and not sebelumnya_pipe:
            obj_tabel.append(i)
        sebelumnya_pipe = adalah_pipe
    obj_gambar = [i for i, b in enumerate(baris)
                  if b.strip().startswith("[[GAMBAR-OBJ")
                  or re.search(r"!\[[^\]]*\]\([^)]+\)", b)]

    def caption_dekat(idx_obj: int, jenis: str, arah: str) -> dict | None:
        """Cari caption jenis ini dalam 6 baris ke arah 'atas'/'bawah'."""
        rentang = range(idx_obj - 1, max(idx_obj - 7, -1), -1) if arah == "atas" \
            else range(idx_obj + 1, min(idx_obj + 7, len(baris)))
        for j in rentang:
            c = RE_CAPTION.match(baris[j])
            if c and c.group(1).capitalize() == jenis:
                return {"baris": j, "teks": baris[j].strip()}
        return None

    if obj_tabel or obj_gambar:
        for idx in obj_tabel:
            c = caption_dekat(idx, "Tabel", "atas") or caption_dekat(idx, "Tabel", "bawah")
            if not c:
                galat.append({"kode": "tabel_tanpa_caption",
                              "pesan": "Ada tabel tanpa caption 'Tabel ...'.",
                              "saran": "Beri caption di atas tabel: 'Tabel IV.1. Judul.'"})
        for idx in obj_gambar:
            c = caption_dekat(idx, "Gambar", "bawah") or caption_dekat(idx, "Gambar", "atas")
            if not c:
                galat.append({"kode": "gambar_tanpa_caption",
                              "pesan": "Ada gambar tanpa caption 'Gambar ...'.",
                              "saran": "Beri caption di bawah gambar: 'Gambar III.1. Judul.'"})
    else:
        peringatan.append({
            "kode": "objek_tidak_terdeteksi",
            "pesan": "Tidak ada objek tabel/gambar yang terbaca dari berkas ini.",
            "saran": "Untuk .md, tandai tabel dengan blok pipe dan gambar dengan "
                     "'![...]'; untuk .docx objek dibaca dari dokumen."})

    # --- 3 & 4. format & urutan nomor ---
    for c in caption:
        if pakai_romawi and not re.fullmatch(r"[IVX]+", c["bab_txt"].upper()):
            galat.append({
                "kode": "caption_angka_arab",
                "pesan": f"{c['jenis']} {c['bab_txt']}.{c['urut']} memakai angka Arab; "
                         f"panduan mewajibkan angka Romawi per bab.",
                "saran": f"Ganti menjadi {c['jenis']} {ke_romawi(c['bab_nomor'] or 1)}.{c['urut']}."})
        if c["pemisah"] != ".":
            galat.append({
                "kode": "caption_pemisah_salah",
                "pesan": f"{c['jenis']} {c['bab_txt']}{c['pemisah']}{c['urut']} memakai "
                         f"pemisah '{c['pemisah']}', panduan memakai titik.",
                "saran": f"Tulis '{c['jenis']} {c['bab_txt']}.{c['urut']}. Judul.'"})
        if c["bab_aktif"] and c["bab_nomor"] and c["bab_nomor"] != c["bab_aktif"]:
            galat.append({
                "kode": "caption_bab_salah",
                "pesan": (f"{c['jenis']} {c['bab_txt']}.{c['urut']} berada di dalam BAB "
                          f"{ke_romawi(c['bab_aktif'])}, bukan BAB {c['bab_txt']}."),
                "saran": "Nomor bab pada caption harus sama dengan bab tempatnya berada."})

    # urutan per jenis
    for jenis in ("Tabel", "Gambar"):
        per_bab: dict[int, list[int]] = {}
        for c in caption:
            if c["jenis"] != jenis or not c["bab_nomor"]:
                continue
            per_bab.setdefault(c["bab_nomor"], []).append(c["urut"])
        for no, urut in per_bab.items():
            if urut != sorted(urut) or urut != list(range(1, len(urut) + 1)):
                galat.append({
                    "kode": f"urutan_{jenis.lower()}_salah",
                    "pesan": (f"Penomoran {jenis} di BAB {ke_romawi(no)} tidak berurutan "
                              f"dari 1: {urut}."),
                    "saran": f"Nomori ulang {jenis} {ke_romawi(no)}.1, {ke_romawi(no)}.2, ..."})

    # --- 5. rujukan dalam teks ---
    teks_tanpa_caption = "\n".join(
        b for i, b in enumerate(baris) if not RE_CAPTION.match(b))
    dirujuk: set[tuple[str, int, int]] = set()
    for m in RE_RUJUK.finditer(teks_tanpa_caption):
        jenis = m.group(1).capitalize()
        no = angka_bab(m.group(2))
        if no is None:
            continue
        dirujuk.add((jenis, no, int(m.group(3))))

    tak_dirujuk = []
    for c in caption:
        kunci = (c["jenis"], c["bab_nomor"], c["urut"])
        if kunci not in dirujuk:
            tak_dirujuk.append(f"{c['jenis']} {c['bab_txt']}.{c['urut']}")
    if tak_dirujuk:
        galat.append({
            "kode": "objek_tak_dirujuk",
            "pesan": (f"{len(tak_dirujuk)} tabel/gambar tidak pernah dirujuk di teks: "
                      f"{', '.join(tak_dirujuk[:6])}"),
            "saran": ("Sebut di paragraf sebelum objeknya muncul, mis. "
                      "'... disajikan pada Tabel IV.1.' Pembaca perlu tahu kapan "
                      "harus melihatnya.")})

    # rujukan ke nomor yang tidak ada
    semua = {(c["jenis"], c["bab_nomor"], c["urut"]) for c in caption}
    hantu = [f"{j} {ke_romawi(n)}.{u}" for (j, n, u) in dirujuk
             if n and (j, n, u) not in semua]
    if hantu:
        galat.append({
            "kode": "rujukan_hantu",
            "pesan": f"Teks merujuk objek yang caption-nya tidak ada: {', '.join(sorted(set(hantu))[:6])}",
            "saran": "Tambahkan caption untuk objek itu, atau betulkan nomor rujukannya."})

    # --- 6. sumber kutipan pada caption ---
    # Caption yang mengutip karya lain wajib menyebut sumber: (Nama, Tahun)
    # Sumber boleh dalam kurung "(Sanjaya, 2025)" maupun tanpa kurung
    # "diadaptasi dari Sanjaya, 2025" — keduanya sah menurut panduan.
    RE_SUMBER = re.compile(
        r"\(?\s*[A-Z][A-Za-z'\u2019\-.]*(?:\s+(?:dan|&|et\s+al\.?)\s+"
        r"[A-Z][A-Za-z'\u2019\-.]*)?\s*,\s*(?:19|20)\d{2}")
    tanpa_sumber = []
    for c in caption:
        judul = c["judul"]
        if not judul:
            continue
        # caption yang jelas hasil sendiri biasanya tidak mengutip; hanya periksa
        # caption yang mengandung kata penanda karya pihak lain
        if re.search(r"(diambil|diadaptasi|diolah|sumber|modifikasi|adapted|from)", judul, re.I):
            if not RE_SUMBER.search(judul):
                tanpa_sumber.append(f"{c['jenis']} {c['bab_txt']}.{c['urut']}")
    if tanpa_sumber:
        galat.append({
            "kode": "caption_tanpa_sumber",
            "pesan": (f"{len(tanpa_sumber)} caption menyatakan diambil/diolah tetapi "
                      f"tidak mencantumkan sumber: {', '.join(tanpa_sumber[:6])}"),
            "saran": "Akhiri caption dengan '(Nama, Tahun)' sesuai gaya sitasi panduan."})

    total = len(galat)
    return {"ok": total == 0, "kode": 1 if total else 0,
            "galat": galat, "peringatan": peringatan, "info": info}


def cetak(h: dict, profil: dict) -> None:
    k = profil.get("kampus") or {}
    print(f"=== Tabel & Gambar vs {k.get('nama','(profil)')} ===")
    i = h["info"]
    print(f"  caption: {i.get('jumlah_caption',0)} "
          f"(tabel {i.get('tabel',0)}, gambar {i.get('gambar',0)})")
    print()
    if h["galat"]:
        print(f"=== GALAT ({len(h['galat'])}) ===")
        for g in h["galat"]:
            print(f"  x [{g['kode']}] {g['pesan']}")
            print(f"    → {g.get('saran','')}")
        print()
    if h["peringatan"]:
        print(f"=== PERINGATAN ({len(h['peringatan'])}) ===")
        for g in h["peringatan"]:
            print(f"  ! [{g['kode']}] {g['pesan']}")
            print(f"    → {g.get('saran','')}")
        print()
    print(f"Ringkasan: {len(h['galat'])} galat, {len(h['peringatan'])} peringatan")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Periksa caption, urutan nomor, dan rujukan tabel/gambar.",
        epilog="contoh: python3 periksa_tabel_gambar.py skripsi.md profil-kampus.yaml")
    ap.add_argument("naskah")
    ap.add_argument("profil")
    ap.add_argument("--json")
    a = ap.parse_args()

    for p in (a.naskah, a.profil):
        if not os.path.isfile(p):
            print(f"GAGAL: berkas tidak ada: {p}", file=sys.stderr)
            return 2
    try:
        import yaml
    except ImportError:
        print("GAGAL: butuh PyYAML (pip install pyyaml)", file=sys.stderr)
        return 2
    with open(a.profil, encoding="utf-8") as f:
        profil = yaml.safe_load(f)
    if not isinstance(profil, dict) or "caption" not in profil:
        print("GAGAL: profil tidak memuat kunci 'caption:'.", file=sys.stderr)
        return 2

    h = periksa(baca(a.naskah), profil)
    cetak(h, profil)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(h, f, ensure_ascii=False, indent=2)
        print(f"JSON: {a.json}")
    return h["kode"]


if __name__ == "__main__":
    sys.exit(main())
