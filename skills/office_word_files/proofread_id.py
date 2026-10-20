#!/usr/bin/env python3
"""proofread_id.py — pemeriksa typo & EYD naskah Indonesia dalam .docx.

Cek programatik (deterministik, tanpa AI):
  spasi ganda | spasi sebelum koma/titik | kata ganda (yang yang) |
  pemisahan di-/ke- yang salah (di bayar, di proses, ke hadiran) |
  angka rapat satuan (114,33ms) | format Rp | tanda baca aneh (.. ,, !!) |
  kata non-baku umum (website, digenerate, via, tiap, tak, bila) |
  penanda draft tertinggal ([PERLU, TODO, FIXME, XXX])

Pakai:
  proofread_id.py NASKAH.docx [--strict] [--json]

  --strict : kata non-baku jadi temuan ERROR (default: WARNING)
  --json   : keluaran JSON untuk pipeline

Keluar: daftar temuan bernomor + konteks heading. Exit 1 bila ada ERROR.
Dependensi: python-docx saja.
"""
import json
import re
import sys

try:
    from docx import Document
except ImportError:
    sys.exit("butuh python-docx: pip install python-docx")

# kata kerja/tempat yang umumnya SALAH bila dipisah dari di-/ke-
VERBA = ("bayar|proses|unduh|tolak|verifikasi|hasilkan|tentukan|gunakan|pakai|"
         "tulis|buat|minta|ambil|simpan|hapus|tambah|ubah|kirim|hadir|maksud")
# ...tapi benar terpisah bila diikuti kata ini (tempat/waktu/arah)
KECUALI = {"luar", "dalam", "atas", "bawah", "depan", "belakang", "samping",
           "sini", "situ", "sana", "mana", "sekolah", "kelas", "kantor",
           "rumah", "pasar", "lapangan", "admin"}

NONBAKU = {
    "website": "situs web/web",
    "digenerate": "dibangkitkan/diterbitkan",
    "mengegenerate": "membangkitkan/menerbitkan",
    "sepersekian": "tulis angkanya eksplisit",
    "disubmit": "dikirimkan",
    "diupload": "diunggah",
    "didownload": "diunduh",
    "nggak": "tidak",
    "maren": "kemarin",
}

INFORMAL = ("via", "tiap", "tak ", "tak,", " bila ", "cek ", "dipakai",
            "di sini", "gimana", "kayak", "banget")

DRAFT = ("[PERLU", "[DATA]", "[TODO]", "TODO:", "FIXME", "XXX", "[heter",
         "TBD", "lorem ipsum")


def journal_checks(paras):
    """Cek standar jurnal: panjang abstrak + jumlah kata kunci."""
    out = []
    for i, (text, ctx) in enumerate(paras):
        t = text.strip()
        if t.upper() in ("ABSTRAK", "ABSTRACT"):
            body = paras[i + 1][0] if i + 1 < len(paras) else ""
            # lewati baris kosong
            j = i + 1
            while j < len(paras) and not paras[j][0].strip():
                j += 1
            body = paras[j][0] if j < len(paras) else ""
            n = len(body.split())
            if n and not 150 <= n <= 250:
                out.append(("ERROR", f"abstrak {t} = {n} kata (syarat 150–250)",
                            ctx, body[:100]))
        if re.match(r"(?i)^kata kunci\s*:|^keywords\s*:", t):
            items = [x.strip(" *") for x in re.split(r"[,;]", t.split(":", 1)[1]) if x.strip(" *")]
            if not 3 <= len(items) <= 6:
                out.append(("ERROR", f"kata kunci = {len(items)} (syarat 3–6)",
                            ctx, t[:100]))
    return out


def iter_paras(doc):
    """Yield (teks, heading_terdekat) untuk tiap paragraf + sel tabel."""
    cur = ""
    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        if p.style.name.startswith("Heading"):
            cur = t[:60]
        yield t, cur
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    t = p.text.strip()
                    if t:
                        yield t, cur + " [tabel]"


def check(text):
    out = []
    for m in re.finditer(r"\S  +\S", text):
        out.append(("ERROR", f"spasi ganda di: …{m.group(0)[:40]}…"))
    for m in re.finditer(r"\w [,.]", text):
        out.append(("ERROR", f"spasi sebelum tanda baca: …{m.group(0)}…"))
    for m in re.finditer(r"(?i)\b(\w+) \1\b", text):
        out.append(("ERROR", f"kata ganda: {m.group(0)}"))
    for m in re.finditer(r"\b(di|ke) (\w+)\b", text):
        prep, w = m.group(1), m.group(2).lower()
        if prep == "di" and w in VERBA.split("|") and w not in KECUALI:
            out.append(("ERROR", f"kemungkinan 'di' harus dirangkai: '{m.group(0)}'"))
        if prep == "ke" and w in ("hadir", "maksud") and w not in KECUALI:
            out.append(("ERROR", f"kemungkinan 'ke' harus dirangkai: '{m.group(0)}'"))
    for m in re.finditer(r"\d(?:ms|MB|KB|GB|TB)\b", text):
        out.append(("WARNING", f"angka rapat satuan: {m.group(0)}"))
    for m in re.finditer(r"Rp ?\d", text):
        if not re.match(r"Rp \d", m.group(0)):
            out.append(("WARNING", f"format Rp tanpa spasi: {m.group(0)}…"))
    for m in re.finditer(r"[?!]{2,}|\.{4,}|,,|(?<!\w)::(?!=)|;;", text):
        if "://" not in text[max(0, m.start() - 5):m.end()]:
            out.append(("WARNING", f"tanda baca aneh: {m.group(0)}"))
    low = text.lower()
    for w, saran in NONBAKU.items():
        if re.search(rf"(?i)\b{re.escape(w)}\b", text):
            out.append(("ERROR", f"kata non-baku '{w}' → {saran}"))
    for w in INFORMAL:
        if w in low:
            out.append(("INFO", f"gaya informal/tak-baku: '{w.strip()}' — pertimbangkan bentuk baku"))
    for d in DRAFT:
        if d in text:
            out.append(("ERROR", f"penanda draft tertinggal: {d}"))
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    as_json = "--json" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(2)
    doc = Document(args[0])
    findings = []
    paras = list(iter_paras(doc))
    for text, ctx in paras:
        for level, msg in check(text):
            if level == "INFO" and strict:
                level = "ERROR"
            if level == "INFO" and not strict:
                continue
            findings.append({"level": level, "konteks": ctx,
                             "pesan": msg, "cuplikan": text[:100]})
    for level, msg, ctx, clip in journal_checks(paras):
        findings.append({"level": level, "konteks": ctx,
                         "pesan": msg, "cuplikan": clip})
    if as_json:
        print(json.dumps(findings, indent=2, ensure_ascii=False))
    else:
        if not findings:
            print("BERSIH ✔ tidak ada temuan.")
        for i, f in enumerate(findings, 1):
            print(f"{i}. [{f['level']}] ({f['konteks']}) {f['pesan']}")
            print(f"   …{f['cuplikan'][:90]}…")
    if any(f["level"] == "ERROR" for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
