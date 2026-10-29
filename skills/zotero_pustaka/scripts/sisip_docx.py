#!/usr/bin/env python3
"""
sisip_docx.py - Sisipkan Daftar Pustaka hasil render ke dokumen Word.

Yang dilakukan:
    1. Render CSL-JSON -> daftar pustaka bergaya (lewat render_sitasi.py).
    2. Tulis ke DOCX sebagai paragraf biasa dengan hanging indent 1,27 cm,
       spasi 1,15, ukuran mengikuti style Normal dokumen (bukan direct format).
    3. Ganti placeholder {{DAFTAR_PUSTAKA}} bila ada; bila tidak ada, tambah
       bagian "DAFTAR PUSTAKA" di akhir dokumen.
    4. Ganti penanda sitasi {{cite:ID}} dengan sitasi jadi dari mesin yang sama
       sehingga nomor di teks dan nomor di daftar tidak mungkin berbeda.

Pemakaian:
    python3 sisip_docx.py naskah.docx pustaka.csl.json --gaya apa
    python3 sisip_docx.py naskah.docx pustaka.csl.json --gaya ieee \
        --out naskah-berpustaka.docx --judul "DAFTAR PUSTAKA"
    python3 sisip_docx.py naskah.docx pustaka.csl.json --gaya apa --kering  # cek saja

Kode keluar:
    0  berhasil
    1  placeholder sitasi menunjuk id yang tidak ada di pustaka
    2  berkas tidak ditemukan / python-docx tidak terpasang
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

PLACEHOLDER = "{{DAFTAR_PUSTAKA}}"
RE_CITE = re.compile(r"\{\{cite:([^}]+)\}\}")


def _import_docx():
    try:
        from docx import Document
        from docx.shared import Cm, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        return Document, Cm, Pt, WD_ALIGN_PARAGRAPH
    except ImportError:
        sys.exit("GAGAL: butuh python-docx. Jalankan: .venv/bin/pip install python-docx")


def render_pustaka(items_path: str, gaya: str, csl: str | None,
                   naskah: str | None, nama_lengkap: bool,
                   locale: str = "id-ID", format_kampus: str | None = None,
                   locator: dict | None = None) -> tuple[list, dict]:
    import render_sitasi as rs

    items = rs.muat_items(items_path)
    if naskah:
        items = rs.cari_sitasi_di_naskah(naskah, items)
    gaya_path = rs.path_gaya(gaya, csl)
    gaya_pakai = rs.siapkan_gaya(gaya_path, matikan_et_al=nama_lengkap,
                                 format_kampus=format_kampus)
    entri, sitasi, dipakai = rs.render(items, gaya_pakai,
                                       os.path.basename(gaya_path).replace(".csl", ""),
                                       nama_lengkap=nama_lengkap, locale=locale,
                                       locator_map=locator)
    return entri, sitasi


def cari_locator(naskah: str) -> dict:
    """
    Baca {{cite:ID:HAL}} di naskah -> {"ID": ("page", "HAL")}.

    Pedoman kampus memakai (Nama, Tahun:Halaman). Halaman hanya ada di teks,
    bukan di metadata pustaka, jadi satu-satunya tempat asalnya adalah
    penanda sitasi itu sendiri.
    """
    from docx import Document
    out: dict = {}
    doc = Document(naskah)
    teks = [p.text for p in doc.paragraphs]
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                teks.extend(p.text for p in cell.paragraphs)
    for blok in RE_CITE.findall("\n".join(teks)):
        for bagian in blok.split(";"):
            bagian = bagian.strip()
            if not bagian:
                continue
            if ":" in bagian:
                k, v = bagian.split(":", 1)
                out[k.strip()] = ("page", v.strip())
            else:
                out.setdefault(bagian, ("page", ""))
    return {k: v for k, v in out.items() if v[1]}


def _hapus_paragraf(p) -> None:
    el = p._element
    el.getparent().remove(el)


def _rapikan(entri: str) -> str:
    """Spasi setelah penanda nomor gaya: '[1]C.' -> '[1] C.'"""
    entri = re.sub(r"^(\[\d+\])", r"\1 ", entri)
    entri = re.sub(r"^(\d+\.)(?=\S)", r"\1 ", entri)
    return re.sub(r"\s+", " ", entri).strip()


def _set_hanging(p, Cm) -> None:
    pf = p.paragraph_format
    pf.left_indent = Cm(1.27)
    pf.first_line_indent = Cm(-1.27)
    pf.space_after = 0


def sisip(naskah: str, entri: list, keluar: str, judul: str,
          ganti_placeholder: bool = True, kering: bool = False) -> dict:
    Document, Cm, Pt, WD_ALIGN = _import_docx()
    doc = Document(naskah)
    laporan = {"paragraf_pustaka": len(entri), "placeholder": False,
               "ditambahkan_di_akhir": False}

    if kering:
        return laporan

    # --- 1. cari placeholder
    target = None
    for p in doc.paragraphs:
        if PLACEHOLDER in p.text:
            target = p
            break

    if target is not None and ganti_placeholder:
        laporan["placeholder"] = True
        # paragraf pertama memakai posisi placeholder, sisanya disisipkan
        # setelahnya berurutan supaya urutan daftar tidak terbalik
        idx = None
        for i, p in enumerate(doc.paragraphs):
            if p is target:
                idx = i
                break
        for run in list(target.runs):
            run._element.getparent().remove(run._element)
        for i, e in enumerate(entri):
            e = _rapikan(e)
            if i == 0:
                run = target.add_run(e)
                _set_hanging(target, Cm)
            else:
                baru = doc.add_paragraph(e)
                _set_hanging(baru, Cm)
                target._element.addnext(baru._element)
                target = baru
    else:
        # Template kampus punya heading "Daftar Pustaka" tetapi tanpa
        # placeholder. Menambahkan di akhir dokumen menaruh entri SETELAH
        # "Daftar Riwayat Hidup" — bagian yang salah, dan pemeriksa
        # sistematika akan menolaknya. Cari heading-nya dan sisipkan
        # tepat sesudahnya.
        jangkar = None
        for p in doc.paragraphs:
            t = p.text.strip().upper()
            if t in ("DAFTAR PUSTAKA", "DAFTAR PUSTAKA.", "REFERENSI",
                     "REFERENCES") or re.fullmatch(
                         r"(BAB\s+)?DAFTAR\s+PUSTAKA\.?", t):
                jangkar = p
                break
        if jangkar is not None:
            laporan["setelah_heading"] = jangkar.text.strip()
            kursor = jangkar
            for e in entri:
                baru = doc.add_paragraph(_rapikan(e))
                _set_hanging(baru, Cm)
                kursor._element.addnext(baru._element)
                kursor = baru
        else:
            laporan["ditambahkan_di_akhir"] = True
            h = doc.add_paragraph()
            run = h.add_run(judul)
            run.bold = True
            try:
                h.style = doc.styles["Heading 1"]
            except KeyError:
                pass
            for e in entri:
                p = doc.add_paragraph(_rapikan(e))
                _set_hanging(p, Cm)

    doc.save(keluar)
    laporan["berkas"] = keluar
    return laporan


def ganti_sitasi(naskah: str, sitasi: dict, keluar: str) -> dict:
    """Ganti {{cite:ID}} -> sitasi jadi. Dilaporkan per id, tidak diam-diam."""
    Document, _, _, _ = _import_docx()
    doc = Document(naskah)
    dipakai, hilang = [], []

    def proses(p):
        teks = p.text
        if "{{cite:" not in teks:
            return
        def sub(m):
            ids = [x.strip() for x in m.group(1).split(";") if x.strip()]
            bagian = []
            for i in ids:
                # ID:HAL - halaman ikut di penanda, bukan di metadata
                if ":" in i:
                    i = i.split(":", 1)[0].strip()
                if i in sitasi:
                    dipakai.append(i)
                    bagian.append(sitasi[i])
                else:
                    hilang.append(i)
                    bagian.append(f"[?{i}]")
            if len(bagian) == 1:
                return bagian[0]
            # Sitasi ganda. Gaya numerik: [2], [3] — BUKAN (2; 3), karena
            # kurung biasa mengubah nomor gaya IEEE/Vancouver jadi angka
            # telanjang dan pembaca mengira itu tahun terbit.
            if all(re.match(r"^\[\d+\]$", b) for b in bagian):
                return ", ".join(bagian)
            gabung = "; ".join(x.strip("()") for x in bagian)
            return f"({gabung})"
        baru = RE_CITE.sub(sub, teks)
        if baru != teks:
            for r in list(p.runs):
                r._element.getparent().remove(r._element)
            p.add_run(baru)

    for p in doc.paragraphs:
        proses(p)
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    proses(p)

    doc.save(keluar)
    return {"diganti": len(dipakai), "id_hilang": sorted(set(hilang)),
            "berkas": keluar}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Sisipkan Daftar Pustaka ke DOCX")
    ap.add_argument("naskah", help="berkas .docx")
    ap.add_argument("items", help="berkas CSL-JSON")
    ap.add_argument("--gaya", default="apa")
    ap.add_argument("--csl", help="berkas .csl sendiri")
    ap.add_argument("--out", help="berkas keluaran (default: <naskah>-pustaka.docx)")
    ap.add_argument("--judul", default="DAFTAR PUSTAKA")
    ap.add_argument("--nama-lengkap", action="store_true",
                    help="larang et al./dkk (pedoman kampus Indonesia)")
    ap.add_argument("--urut", action="store_true",
                    help="urutkan menurut kemunculan sitasi di naskah")
    ap.add_argument("--ganti-sitasi", action="store_true",
                    help="ganti {{cite:ID}} jadi sitasi jadi")
    ap.add_argument("--locale", default="id-ID", help="locale istilah CSL")
    ap.add_argument("--format-kampus", choices=["nama_tahun_halaman", "nama_tahun",
                                                "naratif"],
                    help="pola sitasi pedoman kampus (mis. nama_tahun_halaman)")
    ap.add_argument("--kering", action="store_true", help="cek tanpa menulis")
    a = ap.parse_args(argv)

    for p in (a.naskah, a.items):
        if not os.path.isfile(p):
            sys.exit(f"GAGAL: berkas tidak ada: {p}")

    out = a.out or os.path.splitext(a.naskah)[0] + "-pustaka.docx"

    locator = cari_locator(a.naskah)
    entri, sitasi = render_pustaka(a.items, a.gaya, a.csl,
                                   a.naskah if a.urut else None,
                                   a.nama_lengkap, a.locale, a.format_kampus,
                                   locator)

    lap = sisip(a.naskah, entri, out, a.judul, kering=a.kering)
    if a.kering:
        print(json.dumps({"kering": True, **lap, "entri": len(entri)},
                         ensure_ascii=False, indent=2))
        return 0

    if a.ganti_sitasi:
        out2 = os.path.splitext(out)[0] + "-sitasi.docx"
        lap2 = ganti_sitasi(out, sitasi, out2)
        lap["sitasi"] = lap2
        os.replace(out2, out)

    print(json.dumps(lap, ensure_ascii=False, indent=2))
    return 0 if not lap.get("sitasi", {}).get("id_hilang") else 1


if __name__ == "__main__":
    sys.exit(main())
