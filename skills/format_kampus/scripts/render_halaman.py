#!/usr/bin/env python3
"""Render isi halaman bagian awal/akhir dari berkas bunyi halaman (YAML).

Pemakaian:
    python3 render_halaman.py halaman.yaml --daftar
    python3 render_halaman.py halaman.yaml --nilai nama="Budi" --nilai nim=123
    python3 render_halaman.py halaman.yaml --cek        # validasi tanpa menulis

Berkas bunyi halaman memisahkan ATURAN FORMAT (ada di presets/<kampus>.yaml)
dari BUNYI HALAMAN (surat pernyataan, lembar pengesahan, dst). Pemisahan ini
penting: format bisa dipakai ulang antar kampus, sedangkan bunyi surat hanya
sah untuk satu kampus.

Semua placeholder {{...}} WAJIB punya nilai. Placeholder yang tidak diganti
akan tampil apa adanya di dokumen mahasiswa, jadi skrip ini menolak render bila
ada yang kosong — kecuali diberi --izinkan-kosong.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

RE_PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")

NILAI_BAWAAN = {
    "institusi": "Universitas Adhirajasa Reswara Sanjaya",
    "kota": "Kota Bandung",
    "fakultas": "Fakultas Teknologi Informasi",
    "gelar": "Sarjana Komputer",
}


def muat(path: str) -> dict:
    try:
        import yaml
    except ImportError:
        sys.exit("GAGAL: butuh PyYAML (pip install pyyaml)")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def kumpulkan_placeholder(hal: dict) -> set[str]:
    """Semua nama placeholder di seluruh berkas (untuk --cek dan pesan galat)."""
    nama: set[str] = set()

    def jelajah(v):
        if isinstance(v, str):
            nama.update(RE_PLACEHOLDER.findall(v))
        elif isinstance(v, dict):
            for x in v.values():
                jelajah(x)
        elif isinstance(v, list):
            for x in v:
                jelajah(x)

    jelajah(hal)
    return nama


def ganti(teks: str, nilai: dict) -> str:
    """Ganti {{kunci}} dengan nilai[kunci]; kunci tak dikenal dibiarkan."""
    if not isinstance(teks, str):
        return teks
    return RE_PLACEHOLDER.sub(
        lambda m: str(nilai.get(m.group(1), m.group(0))), teks)


def kosong_tersisa(hal: dict, nilai: dict) -> list[str]:
    """Placeholder yang masih belum punya nilai (akan tampil mentah)."""
    dipakai = kumpulkan_placeholder(hal)
    return sorted(k for k in dipakai if k not in nilai)


# ---------------------------------------------------------------- render
def render(doc, nama_halaman: str, hal: dict, nilai: dict, gaya: dict) -> None:
    """Gambar satu halaman ke doc sesuai `tipe`-nya."""
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
    from docx.shared import Cm, Pt

    font = gaya["font"]
    # Spasi per halaman: berkas halaman boleh menimpa. Template resmi memakai
    # 1,5 untuk surat pernyataan / lembar pengesahan (terukur dari PDF: jarak
    # antar-baris 21 pt, bukan 27,6 pt) supaya masing-masing tetap SATU halaman.
    # Paragraf isi bab tetap 2 sesuai panduan 4.2 butir 3.
    spasi = hal.get("spasi") or gaya["spasi"]
    contoh = hal.get("contoh") or {}

    def nilai_isi() -> dict:
        """nilai + contoh: kunci yang nilainya kosong diisi teks contoh.

        Tanpa ini, halaman Persembahan/Ringkasan/Abstract tampil kosong total dan
        pengguna tidak tahu apa yang harus ditulis di situ.

        Teks contoh juga memuat placeholder (mis. "... di Program Studi
        {{prodi}}"), jadi contoh WAJIB diganti lebih dulu dengan nilai nyata —
        kalau tidak, hasil render menampilkan "{{prodi}}" mentah di tengah
        paragraf contoh.
        """
        gabung = {k: str(v) for k, v in nilai.items()}
        for k, v in nilai.items():
            if not str(v).strip() and k in contoh:
                gabung[k] = contoh[k]
        # perluas placeholder di dalam teks contoh (bisa berlapis)
        for _ in range(3):
            berubah = False
            for k, v in list(gabung.items()):
                baru = ganti(str(v), gabung)
                if baru != v:
                    gabung[k] = baru
                    berubah = True
            if not berubah:
                break
        return gabung

    def par(teks="", *, pt=None, tebal=False, miring=False, rata="justify",
            indent=1.0, spasi_baris=None, tengah=False, sebelum=0):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = spasi_baris or spasi
        p.paragraph_format.space_after = Pt(0)
        if sebelum:
            p.paragraph_format.space_before = Pt(sebelum)
        # Justify hanya untuk paragraf yang benar-benar mengalir (>= 2 baris).
        # Baris pendek yang di-justify menghasilkan celah antarkata yang aneh,
        # mis. "Telah   dipertahankan   di   depan   Dewan   Penguji".
        teks_final = ganti(teks, nilai_isi())
        rata_efektif = rata
        if rata == "justify" and len(teks_final) < 95:
            rata_efektif = "left"
        p.alignment = (WD_ALIGN_PARAGRAPH.CENTER if tengah or rata == "center"
                       else WD_ALIGN_PARAGRAPH.JUSTIFY if rata_efektif == "justify"
                       else WD_ALIGN_PARAGRAPH.LEFT)
        if indent and rata == "justify":
            p.paragraph_format.first_line_indent = Cm(indent)
        # WAJIB nilai_isi(), bukan nilai: teks paragraf yang memakai placeholder
        # kosong harus jatuh ke `contoh`. Sempat tertinggal `nilai` di sini,
        # sehingga Ringkasan/Abstract/Kata Pengantar tampil kosong walau blok
        # `contoh:` sudah diisi.
        r = p.add_run(teks_final)
        r.font.name = font
        r.font.size = Pt(pt or gaya["isi_pt"])
        r.font.bold = tebal
        r.font.italic = miring
        return p

    def judul(teks, *, sebelum=0, sesudah=12):
        p = doc.add_heading(level=1)
        p.paragraph_format.page_break_before = True
        p.paragraph_format.space_before = Pt(sebelum)
        p.paragraph_format.space_after = Pt(sesudah)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(ganti(teks, nilai_isi()).upper())
        r.font.name = font
        r.font.size = Pt(gaya["judul_pt"])
        r.font.bold = True
        return p

    # Posisi tab untuk SEMUA blok isian di halaman ini, dihitung dari label
    # terpanjang di seluruh halaman. Per blok saja tidak cukup: dua blok di
    # halaman yang sama akan memakai tab berbeda dan titik duanya tidak lurus.
    semua_label: list[str] = []

    def _kumpul_label(v):
        if isinstance(v, dict):
            for k, x in v.items():
                if k in ("isian", "isian_2") and isinstance(x, list):
                    semua_label.extend(str(p_[0]) for p_ in x
                                       if isinstance(p_, list) and p_)
                else:
                    _kumpul_label(x)
        elif isinstance(v, list):
            for x in v:
                _kumpul_label(x)

    _kumpul_label(hal)

    def lebar_label_cm(label: str) -> float:
        """Perkiraan lebar label (cm) pada Times New Roman 12 pt.

        Perkiraan 0,22 cm/huruf terlalu sempit untuk huruf kapital: label
        "Dosen Pembimbing I" melewati tab stop, sehingga titik duanya meleset
        ke kanan dan tidak lurus dengan baris lain. Pakai metrik font bila
        tersedia (Pillow), kalau tidak pakai 0,26 cm/huruf yang lebih aman.
        """
        try:
            from PIL import ImageFont
            # Ukuran font di Pillow adalah PIXEL, bukan point. 12 pt @96 dpi
            # = 16 px. Memakai 12 px (yang setara 9 pt) membuat lebar label
            # dihitung 25% terlalu sempit — tab stop jadi kurang lebar dan
            # label panjang ("Perguruan Tinggi") melewatinya, sehingga kolon
            # meleset ke tab default berikutnya.
            px_untuk_12pt = round(gaya["isi_pt"] / 72 * 96)
            for path in ("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
                         "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf",
                         "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"):
                if os.path.exists(path):
                    f = ImageFont.truetype(path, px_untuk_12pt)
                    px = f.getlength(label)
                    return (px * 72 / 96) / 28.3465      # px -> pt -> cm
        except Exception:
            pass
        return len(label) * 0.30

    # Lebar label terpanjang + ruang 0,3 cm. Posisi tab dihitung di isian()
    # dengan menambahkan indent paragraf, karena w:pos diukur dari margin kiri.
    LEBAR_LABEL = max((lebar_label_cm(x) for x in semua_label),
                      default=lebar_label_cm("Nama")) + 0.3

    def isian(pasangan: list, *, indent_kiri=1.0, jarak_atas=0.0):
        """Blok isian "Label : nilai" dengan titik dua SEJAJAR.

        Tab stop dihitung dari label terpanjang di blok itu, bukan angka tetap.
        Tab 4 cm cukup untuk "Nama" tetapi membuat "Perguruan Tinggi" menabrak
        titik duanya sendiri — titik dua jadi tidak lurus dan blok terlihat
        berantakan. Lebar karakter Times New Roman 12 pt ~0,21 cm, jadi tab
        diberi jarak label_terpanjang * 0,22 cm + 0,5 cm, minimum 3 cm.
        """
        from docx.shared import Cm as _Cm
        posisi_tab = indent_kiri + LEBAR_LABEL
        pertama = True
        for pasangan_satu in pasangan:
            label, isi = pasangan_satu[0], pasangan_satu[1]
            p = doc.add_paragraph()
            if pertama and jarak_atas:
                p.paragraph_format.space_before = Pt(jarak_atas)
            pertama = False
            # Rata KIRI wajib: style Normal memakai JUSTIFY, dan baris isian
            # panjang akan direnggangkan sehingga titik dua tampak melayang.
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = spasi
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.left_indent = _Cm(indent_kiri)
            p.paragraph_format.first_line_indent = _Cm(0)
            # Tab KIRI (dibuktikan dengan uji render): kolon duduk tepat di tab
            # stop. Tab KANAN salah untuk pola "Label\t: nilai" — tab kanan
            # menempelkan UJUNG label di tab stop, lalu ": nilai" menyusul,
            # sehingga kolon ikut bergeser sesuai panjang label.
            tabs = p.paragraph_format.tab_stops
            tabs.add_tab_stop(_Cm(posisi_tab), WD_TAB_ALIGNMENT.LEFT)
            r = p.add_run(ganti(f"{label}\t: {isi}", nilai_isi()))
            r.font.name = font
            r.font.size = Pt(gaya["isi_pt"])

    def tabel(kolom: list, baris: list, lebar_cm=None):
        t = doc.add_table(rows=1, cols=len(kolom))
        t.style = "Table Grid"
        for i, k in enumerate(kolom):
            sel = t.rows[0].cells[i]
            sel.text = ""
            pr = sel.paragraphs[0]
            pr.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = pr.add_run(ganti(str(k), nilai_isi()))
            r.font.name = font
            r.font.size = Pt(gaya["isi_pt"] - 1)
            r.font.bold = True
            pr.paragraph_format.line_spacing = 1.0
        for b in baris:
            kota = t.add_row().cells
            for i, sel_teks in enumerate(b[:len(kolom)]):
                kota[i].text = ""
                pr = kota[i].paragraphs[0]
                pr.paragraph_format.line_spacing = 1.0
                r = pr.add_run(ganti(str(sel_teks), nilai_isi()))
                r.font.name = font
                r.font.size = Pt(gaya["isi_pt"] - 1)
        if lebar_cm:
            for i, w in enumerate(lebar_cm[:len(kolom)]):
                for row in t.rows:
                    row.cells[i].width = Cm(w)
        return t

    tipe = (hal.get("tipe") or "judul").lower()

    # ---- judul halaman ----
    judul(nama_halaman)
    for tambahan in (hal.get("judul_tambahan") or []):
        par(tambahan, tebal=True, rata="center", indent=0, tengah=True)
    for sub in (hal.get("sub_judul") or []):
        par(sub, tebal=True, rata="center", indent=0, tengah=True)

    # ---- badan ----
    if tipe == "kosong":
        pass

    elif tipe == "judul":
        for i_par, s in enumerate(hal.get("paragraf") or []):
            par(s, sebelum=0 if i_par == 0 else 12)
        if hal.get("isian"):
            isian(hal["isian"], jarak_atas=6)
        for s in (hal.get("penutup") or []):
            par(s, indent=0, sebelum=6)

    elif tipe == "surat":
        for s in (hal.get("pembuka") or []):
            par(s, indent=0 if s.rstrip().endswith(":") else 1.0)
        if hal.get("isian"):
            isian(hal["isian"])
        for s in (hal.get("paragraf") or []):
            par(s, sebelum=6)
        if hal.get("tabel_ttd"):
            blok = hal["tabel_ttd"]

            def tabel_ttd(kolom, baris):
                """Tabel tanda tangan: sel pertama boleh memuat dua baris
                (nama + NIDN) lewat pemisah '|' agar tidak menjadi baris tabel
                terpisah yang membuat tabel tampak berantakan."""
                t = doc.add_table(rows=1, cols=len(kolom))
                t.style = "Table Grid"
                for i, k in enumerate(kolom):
                    sel = t.rows[0].cells[i]
                    sel.text = ""
                    pr = sel.paragraphs[0]
                    pr.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    pr.paragraph_format.line_spacing = 1.0
                    r = pr.add_run(str(k))
                    r.font.name = font
                    r.font.size = Pt(gaya["isi_pt"] - 1)
                    r.font.bold = True
                for b in baris:
                    row = t.add_row()
                    for i, sel_teks in enumerate(b[:len(kolom)]):
                        sel = row.cells[i]
                        sel.text = ""
                        for j, bagian in enumerate(str(sel_teks).split("|")):
                            pr = (sel.paragraphs[0] if j == 0
                                  else sel.add_paragraph())
                            pr.alignment = WD_ALIGN_PARAGRAPH.LEFT
                            pr.paragraph_format.line_spacing = 1.0
                            pr.paragraph_format.space_after = Pt(0)
                            r = pr.add_run(ganti(bagian.strip(), nilai_isi()))
                            r.font.name = font
                            r.font.size = Pt(gaya["isi_pt"] - 1)
                return t

            par(blok.get("judul", "Dewan Penguji"), tebal=True, rata="center",
                indent=0, tengah=True)
            tabel_ttd(blok.get("kolom") or ["Nama", "Tanda Tangan"],
                      blok.get("baris") or [])
            if blok.get("judul_2"):
                par(blok["judul_2"], tebal=True, rata="center", indent=0,
                    tengah=True, sebelum=14)
                tabel_ttd(["Nama", "Tanda Tangan"], blok.get("baris_2") or [])
        if hal.get("isian_2"):
            isian(hal["isian_2"], jarak_atas=6)
        for s in (hal.get("paragraf_2") or []):
            par(s, sebelum=6)
        jarak_penutup = 0.0
        for s in (hal.get("penutup") or []):
            if not s:
                jarak_penutup += 1.5 * 14     # ruang tanda tangan
                continue
            par(s, tebal=s.isupper() and len(s) < 60,
                rata="center" if s.isupper() else "justify", tengah=s.isupper(),
                sebelum=6 + jarak_penutup, indent=0)
            jarak_penutup = 0.0
        if hal.get("ttd"):
            # Baris "Dibuat di     : Kota Bandung" / "Pada tanggal  : ..." harus
            # sejajar. Tanpa tab stop, spasinya runtuh jadi satu dan titik dua
            # tidak lurus.
            baris_ttd = [x for x in hal["ttd"] if x]
            berlabel = [x for x in baris_ttd if ":" in x and x.count(":") == 1
                        and x.index(":") < 30]
            pos = 4.0
            if berlabel:
                kiri = max(len(x.split(":")[0].rstrip()) for x in berlabel)
                pos = max(3.5, kiri * 0.22 + 0.6)
            # Baris kosong di blok ttd = ruang tanda tangan. Diwujudkan sebagai
            # space_before, bukan paragraf kosong: paragraf kosong dihitung
            # "spasi manual" oleh audit_rapi dan membuat dokumen sulit dirapikan.
            jarak_tumpuk = 0.0
            for s in hal["ttd"]:
                if not s:
                    jarak_tumpuk += 1.5 * 14        # ~1,5 baris kosong
                    continue
                # Tab KIRI: kolon duduk tepat di tab stop untuk kedua baris
                # ("Dibuat di" / "Pada tanggal") walau panjang label berbeda.
                p = par(s.split(":")[0].rstrip() + "\t: " + s.split(":", 1)[1].strip()
                        if s in berlabel else s,
                        indent=0, rata="left", sebelum=jarak_tumpuk)
                jarak_tumpuk = 0.0
                if s in berlabel:
                    p.paragraph_format.tab_stops.add_tab_stop(
                        Cm(pos), WD_TAB_ALIGNMENT.LEFT)

    elif tipe == "isian":
        for blok in (hal.get("blok") or []):
            par(blok.get("judul", ""), tebal=True, indent=0, rata="left")
            isian(blok.get("isian") or [], indent_kiri=1.0)
        if hal.get("ttd"):
            jarak = 0.0
            for s in hal["ttd"]:
                if s:
                    par(s, indent=0, rata="left", sebelum=jarak)
                    jarak = 0.0
                else:
                    jarak += 1.5 * 14

    elif tipe == "tabel":
        if hal.get("isian"):
            isian(hal["isian"], jarak_atas=6)
        # tabel data: header rata tengah + lebar kolom dari profil. Tanpa lebar,
        # header "Paraf Dosen Pembimbing" pecah jadi 3 baris dan tabel tampak
        # berantakan.
        lebar = hal.get("lebar_kolom_cm")
        t = tabel(hal.get("kolom") or [], hal.get("baris") or [], lebar)
        if lebar:
            # set juga lebar tabel total supaya Word tidak menyesuaikan otomatis
            from docx.shared import Cm as _Cm
            t.autofit = False
            for i, w in enumerate(lebar[:len(hal.get("kolom") or [])]):
                t.columns[i].width = _Cm(w)

    else:
        raise ValueError(f"tipe halaman tidak dikenal: {tipe!r} (halaman {nama_halaman})")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Render isi halaman bagian awal/akhir dari berkas bunyi halaman.")
    ap.add_argument("berkas")
    ap.add_argument("--daftar", action="store_true",
                    help="tampilkan semua halaman dan placeholder-nya")
    ap.add_argument("--cek", action="store_true",
                    help="validasi berkas + placeholder tanpa menulis dokumen")
    ap.add_argument("--nilai", action="append", default=[],
                    metavar="KUNCI=NILAI")
    ap.add_argument("--izinkan-kosong", action="store_true",
                    help="jangan gagal walau ada placeholder tanpa nilai")
    a = ap.parse_args()

    if not os.path.isfile(a.berkas):
        print(f"GAGAL: berkas tidak ada: {a.berkas}", file=sys.stderr)
        return 2
    isi = muat(a.berkas)
    halaman = isi.get("halaman") or {}
    if not halaman:
        print("GAGAL: berkas tidak memuat kunci 'halaman:'.", file=sys.stderr)
        return 2

    nilai = dict(NILAI_BAWAAN)
    for item in a.nilai:
        if "=" not in item:
            print(f"GAGAL: --nilai harus KUNCI=NILAI, dapat: {item}", file=sys.stderr)
            return 2
        k, v = item.split("=", 1)
        nilai[k.strip()] = v

    if a.daftar:
        print(f"{len(halaman)} halaman dari {a.berkas}")
        for nama, hal in halaman.items():
            tipe = hal.get("tipe", "judul")
            wajib = "wajib" if hal.get("wajib") else "opsional"
            ph = sorted(kumpulkan_placeholder(hal))
            print(f"  {nama:52} {tipe:8} {wajib:9} {{{', '.join(ph) if ph else '-'}}}")
        return 0

    kurang = kosong_tersisa(isi, nilai)
    if a.cek:
        print(f"halaman: {len(halaman)}")
        print(f"placeholder dipakai: {len(kumpulkan_placeholder(isi))}")
        if kurang:
            print(f"BELUM ADA NILAI ({len(kurang)}): {', '.join(kurang)}")
            print("  lengkapi dengan --nilai kunci=nilai")
            return 1
        print("semua placeholder punya nilai")
        return 0

    if kurang and not a.izinkan_kosong:
        print(f"GAGAL: {len(kurang)} placeholder belum punya nilai: "
              f"{', '.join(kurang)}", file=sys.stderr)
        print("  Placeholder yang tidak diganti akan tampil mentah di dokumen "
              "mahasiswa. Lengkapi dengan --nilai kunci=nilai, atau pakai "
              "--izinkan-kosong bila memang ingin kerangka kosong.",
              file=sys.stderr)
        return 2
    print(f"berkas valid: {len(halaman)} halaman, {len(kurang)} placeholder kosong")
    return 0


if __name__ == "__main__":
    sys.exit(main())
