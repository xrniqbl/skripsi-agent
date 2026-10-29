#!/usr/bin/env python3
"""
render_sitasi.py - Render CSL-JSON menjadi Daftar Pustaka + sitasi dalam teks.

Satu daftar item masuk, dua keluaran keluar dari mesin yang sama, supaya nomor
atau nama pengarang tidak mungkin berbeda antara teks dan daftar.

Pemakaian:
    # daftar pustaka APA
    python3 render_sitasi.py pustaka.csl.json --gaya apa

    # IEEE, urut sesuai urutan sitasi di naskah (bukan urutan berkas)
    python3 render_sitasi.py pustaka.csl.json --gaya ieee --urut naskah.md

    # Vancouver, tulis ke berkas + sitasi per item
    python3 render_sitasi.py pustaka.csl.json --gaya vancouver \
        --out daftar_pustaka.md --sitasi-out sitasi.json

    # gaya dari berkas CSL lain (mis. gaya kampus sendiri)
    python3 render_sitasi.py pustaka.csl.json --csl ~/gaya-kampus.csl

    # daftar gaya yang tersedia
    python3 render_sitasi.py --daftar-gaya

Aturan yang dijaga:
    - Gaya numerik (IEEE, Vancouver) menomori menurut URUTAN SITASI. Bila
      --urut diberi naskah, urutan diambil dari kemunculan sitasi di naskah;
      bila tidak, urutan berkas dipakai dan itu dilaporkan.
    - Entri yang tidak punya penulis DAN tidak punya judul dilaporkan sebagai
      cacat, tidak dirender jadi baris kosong.
    - Setiap nama pengarang ditulis lengkap (tidak ada et al./dkk) bila
      --nama-lengkap aktif, sesuai panduan kampus Indonesia.

Kode keluar:
    0  berhasil
    1  ada entri cacat yang tidak bisa dirender
    2  berkas/gaya tidak ditemukan
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE_DIR = os.path.join(SKILL_DIR, "styles")

GAYA_TERSEDIA = {
    "apa": "apa.csl",
    "ieee": "ieee.csl",
    "vancouver": "vancouver.csl",
    "chicago-author-date": "chicago-author-date.csl",
    "harvard": "harvard-cite-them-right.csl",
    "harvard-cite-them-right": "harvard-cite-them-right.csl",
}

GAYA_NUMERIK = {"ieee", "vancouver", "nature", "acm-sig-proceedings"}


# ---------------------------------------------------------------------------
def muat_items(path: str) -> list:
    """Baca CSL-JSON: bisa berbentuk daftar, {items:[...]}, atau {items:{...}}."""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    if isinstance(d, list):
        items = d
    elif isinstance(d, dict):
        items = d.get("items") or d.get("data") or []
        if isinstance(items, dict):
            items = list(items.values())
    else:
        items = []
    bersih = []
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            continue
        it = dict(it)
        it.setdefault("id", f"item{i+1}")
        bersih.append(it)
    return bersih


def path_gaya(nama: str | None, csl: str | None) -> str:
    if csl:
        p = os.path.expanduser(csl)
        if not os.path.isfile(p):
            sys.exit(f"GAGAL: berkas CSL tidak ada: {p}")
        return p
    nama = (nama or "apa").lower()
    if nama not in GAYA_TERSEDIA:
        sys.exit(f"GAGAL: gaya '{nama}' tidak dikenal. "
                 f"Pilihan: {', '.join(sorted(GAYA_TERSEDIA))}")
    p = os.path.join(STYLE_DIR, GAYA_TERSEDIA[nama])
    if not os.path.isfile(p):
        sys.exit(f"GAGAL: berkas gaya hilang: {p}\n"
                 f"Unduh ulang: bash scripts/unduh_gaya.sh")
    # Berkas gaya yang terunduh sebagai halaman 404 punya ukuran sangat kecil
    # dan tidak dimulai dengan deklarasi XML. Cek, jangan asumsikan.
    with open(p, "rb") as f:
        kepala = f.read(80)
    if b"<?xml" not in kepala and b"<style" not in kepala:
        sys.exit(f"GAGAL: berkas gaya rusak (bukan XML): {p} — unduh ulang.")
    return p


def cari_sitasi_di_naskah(naskah: str, items: list) -> list:
    """
    Tentukan urutan item menurut kemunculan sitasinya di naskah.

    Dua bentuk dikenali:
      numerik   [1], [2,3], [4-6]
      penulis   (Harris, 2020) / (Harris & Millman, 2020) / Harris (2020)
    Item yang tidak muncul di naskah ditaruh di belakang, urutan berkas.
    """
    with open(naskah, encoding="utf-8", errors="replace") as f:
        teks = f.read()

    posisi = {}

    # --- numerik: [n] dan variasinya
    for m in re.finditer(r"\[(\d+(?:\s*[,\-–]\s*\d+)*)\]", teks):
        isi = m.group(1)
        nomor = []
        for bagian in re.split(r",", isi):
            bagian = bagian.strip()
            if re.fullmatch(r"\d+\s*[\-–]\s*\d+", bagian):
                a, b = re.split(r"[\-–]", bagian)
                nomor.extend(range(int(a), int(b) + 1))
            elif bagian.isdigit():
                nomor.append(int(bagian))
        for n in nomor:
            posisi.setdefault(n, m.start())

    urut = []
    if posisi:
        for n in sorted(posisi, key=lambda k: posisi[k]):
            if 1 <= n <= len(items):
                it = dict(items[n - 1])
                it["_nomor"] = n
                urut.append(it)
        terpakai = {it["id"] for it in urut}
        for it in items:
            if it["id"] not in terpakai:
                urut.append(dict(it))
        return urut

    # --- penulis-tahun: cocokkan nama belakang + tahun
    def kunci(it):
        nama = ""
        pen = it.get("author") or it.get("editor") or []
        if pen:
            nama = (pen[0].get("family") or pen[0].get("literal") or "").lower()
        thn = ""
        iss = it.get("issued") or {}
        dp = iss.get("date-parts") or [[None]]
        if dp and dp[0] and dp[0][0]:
            thn = str(dp[0][0])
        return nama, thn

    skor = []
    for idx, it in enumerate(items):
        nama, thn = kunci(it)
        p = None
        if nama and thn:
            pola = re.escape(nama) + r"[^()]{0,80}?" + re.escape(thn)
            m = re.search(pola, teks, re.I)
            if m:
                p = m.start()
        skor.append((p is None, p if p is not None else 10**9, idx, it))
    skor.sort(key=lambda t: (t[0], t[1], t[2]))
    return [dict(t[3]) for t in skor]


# ---------------------------------------------------------------------------
def _terapkan_format_sitasi(root, NS: str, pola: str) -> bool:
    """
    Ganti layout <citation> sesuai pola kampus.

    pola yang didukung:
        "nama_tahun_halaman"  -> (Nama, 2020:12)      [ARS/FTI 4.7]
        "nama_tahun"          -> (Nama, 2020)
        "naratif"             -> Nama (2020:12)

    Mengembalikan True bila gaya benar-benar diubah.

    Yang diganti hanya <layout> di dalam <citation>; <sort> dibiarkan supaya
    disambiguasi dan urutan gaya asli tetap berjalan. Rendering halaman
    memakai <text variable="locator"> yang kosong bila sitasi tidak menyebut
    halaman — jadi "(Nama, 2020:12)" hanya muncul saat halaman memang dikutip.
    """
    import xml.etree.ElementTree as ET

    cit = next(root.iter(f"{{{NS}}}citation"), None)
    if cit is None:
        return False

    for lama in list(cit):
        if lama.tag == f"{{{NS}}}layout":
            cit.remove(lama)

    layout = ET.SubElement(cit, f"{{{NS}}}layout")
    layout.set("delimiter", "; ")

    def nama(induk, **atr):
        dasar = {"variable": "author", "delimiter": ", "}
        dasar.update({k.replace("_", "-"): v for k, v in atr.items()})
        nm = ET.SubElement(induk, f"{{{NS}}}names", dasar)
        # form="short" HARUS di <name>, bukan di <names>. Di <names> ia
        # diabaikan dan nama depan ikut tercetak: "(I. Saputra, A. Wijaya)".
        # <name> wajib punya anak (aturan CSL: elemen name harus berisi), jadi
        # <substitute> ganda memberi anak sekaligus cadangan judul.
        ET.SubElement(nm, f"{{{NS}}}name", {"form": "short", "and": "symbol"})
        sub = ET.SubElement(nm, f"{{{NS}}}substitute")
        ET.SubElement(sub, f"{{{NS}}}text",
                      {"variable": "title", "form": "short"})
        return nm

    def tahun_dan_halaman(induk, pakai_halaman: bool):
        dalam = ET.SubElement(induk, f"{{{NS}}}group", {"delimiter": ":"})
        thn = ET.SubElement(dalam, f"{{{NS}}}date", {"variable": "issued"})
        ET.SubElement(thn, f"{{{NS}}}date-part", {"name": "year"})
        if pakai_halaman:
            # locator kosong bila sitasi tidak menyebut halaman, jadi
            # "(Nama, 2020)" tetap keluar untuk sitasi tanpa halaman.
            ET.SubElement(dalam, f"{{{NS}}}text", {"variable": "locator"})
        return dalam

    pakai_halaman = pola in ("nama_tahun_halaman", "naratif")

    if pola == "naratif":
        # Nama (2020:12)
        layout.set("prefix", "")
        layout.set("suffix", "")
        nama(layout, and_="text", suffix=" ")
        kelompok = ET.SubElement(layout, f"{{{NS}}}group",
                                 {"prefix": "(", "suffix": ")"})
        tahun_dan_halaman(kelompok, pakai_halaman)
        return True

    # (Nama, 2020:12) — nama dan tahun di level yang sama, dipisah koma
    layout.set("prefix", "(")
    layout.set("suffix", ")")
    luar = ET.SubElement(layout, f"{{{NS}}}group", {"delimiter": ", "})
    nama(luar, and_="symbol")
    tahun_dan_halaman(luar, pakai_halaman)
    return True


def siapkan_gaya(path: str, matikan_et_al: bool = False,
                 format_kampus: str | None = None) -> str:
    """
    Siapkan berkas gaya untuk citeproc.

    matikan_et_al=True : paksa semua nama pengarang ditulis lengkap. Panduan
    skripsi Indonesia (ARS/FTI 4.10 butir 5) melarang "et al."/"dkk", sedangkan
    CSL baku IEEE/Vancouver/APA memotong pada 3-20 nama. Tanpa ini, naskah yang
    patuh pedoman tidak mungkin dihasilkan dari gaya baku.

    Mengembalikan path gaya (asli, atau salinan sementara bila diubah).
    """
    if not matikan_et_al and not format_kampus:
        return path

    import tempfile
    import xml.etree.ElementTree as ET

    NS = "http://purl.org/net/xbiblio/csl"
    ET.register_namespace("", NS)
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        sys.exit(f"GAGAL: gaya bukan XML valid ({path}): {e}")
    root = tree.getroot()

    BESAR = "999"
    diubah = False

    if matikan_et_al:
        # Elemen <name> yang memotong daftar pengarang biasanya duduk di dalam
        # <macro> di akar dokumen, bukan di dalam <citation>/<bibliography> —
        # keduanya direferensikan lewat <text macro="...">. Jadi jelajahi
        # seluruh dokumen, jangan hanya dua node itu.
        for nm in root.iter(f"{{{NS}}}name"):
            for at in ("et-al-min", "et-al-use-first"):
                if nm.get(at) is not None:
                    nm.set(at, BESAR)
                    diubah = True
            if nm.get("et-al-use-last") is not None:
                nm.set("et-al-use-last", "false")
                diubah = True

        for node in root.iter(f"{{{NS}}}citation"):
            for at in ("et-al-min", "et-al-use-first"):
                if node.get(at) is not None:
                    node.set(at, BESAR)
                    diubah = True
        for node in root.iter(f"{{{NS}}}bibliography"):
            for at in ("et-al-min", "et-al-use-first"):
                if node.get(at) is not None:
                    node.set(at, BESAR)
                    diubah = True

        # buang elemen <et-al> (teks pengganti "et al.") di mana pun berada
        induk_peta = {anak: induk for induk in root.iter() for anak in induk}
        for el in list(root.iter(f"{{{NS}}}et-al")):
            induk = induk_peta.get(el)
            if induk is not None:
                induk.remove(el)
                diubah = True

    if format_kampus:
        # Pedoman kampus Indonesia (ARS/FTI 4.7) menyebut APA tetapi contohnya
        # "(Nama Belakang, Tahun:Halaman)" — titik dua, bukan koma. APA baku
        # tidak punya bentuk itu, jadi layout sitasi diganti, bukan ditambal
        # di teks hasil render.
        if _terapkan_format_sitasi(root, NS, format_kampus):
            diubah = True

    if not diubah:
        return path

    tmp = tempfile.NamedTemporaryFile("wb", suffix=".csl", delete=False)
    tree.write(tmp.name, encoding="utf-8", xml_declaration=True)
    tmp.close()
    return tmp.name


def render(items: list, gaya_path: str, gaya_nama: str,
           nama_lengkap: bool = False, html: bool = False,
           locale: str = "en-US", locator_map: dict | None = None):
    """Render (bibliografi, sitasi-per-item). Melempar ImportError bila citeproc absen."""
    from citeproc import (CitationStylesStyle, CitationStylesBibliography,
                          Citation, CitationItem, formatter)
    from citeproc.source.json import CiteProcJSON

    # citeproc butuh id unik dan bertipe string
    dipakai, seen = [], set()
    for i, it in enumerate(items):
        it = dict(it)
        it.pop("_nomor", None)
        it.pop("_tipe_zotero", None)
        it.pop("_tipe_asli", None)
        it["id"] = str(it.get("id") or f"i{i+1}")
        while it["id"] in seen:
            it["id"] += "_"
        seen.add(it["id"])
        it.setdefault("type", "article-journal")
        dipakai.append(it)

    style = CitationStylesStyle(gaya_path, locale=locale, validate=False)
    fmt = formatter.html if html else formatter.plain
    src = CiteProcJSON(dipakai)

    bib = CitationStylesBibliography(style, src, fmt)
    for it in dipakai:
        bib.register(Citation([CitationItem(it["id"])]))

    # Urutan daftar pustaka adalah milik gaya, bukan milik berkas masukan:
    # APA mengurutkan abjad, IEEE/Vancouver mengurutkan menurut sitasi.
    # Tanpa sort(), citeproc mempertahankan urutan register dan daftar APA
    # keluar tidak berabjad (cacat yang lolos pemeriksaan mata).
    try:
        bib.sort()
    except Exception:
        pass

    # Sitasi HARUS dirender SESUDAH sort(). Gaya numerik menomori menurut
    # urutan akhir daftar; merender sitasi lebih dulu memberi [1] pada entri
    # yang kemudian tercetak sebagai [3] di Daftar Pustaka. Dua sumber nomor
    # untuk satu entri adalah persis kegagalan yang pipeline ini cegah.
    #
    # Setiap Citation harus objek yang SUDAH di-register: register() yang
    # memasang atribut `citation.bibliography`, dan tanpa itu bib.cite()
    # melempar VariableError('bibliography') - bukan sitasi kosong.
    sitasi = {}
    for it in dipakai:
        # locator_map: {"id": ("page", "12")} untuk sitasi yang menyebut
        # halaman. Tanpa Locator, "(Nama, 2020:12)" tidak mungkin keluar;
        # dan locator sebagai string biasa membuat citeproc melempar
        # AttributeError ('str' has no attribute 'identifier').
        kw = {}
        if locator_map and it["id"] in locator_map:
            from citeproc.source import Locator
            label, nomor = locator_map[it["id"]]
            kw["locator"] = Locator(label, str(nomor))
        c = Citation([CitationItem(it["id"], **kw)])
        bib.register(c)
        try:
            sitasi[it["id"]] = bib.cite(c, lambda x: "[%s]" % x)
        except Exception as e:                       # gaya tanpa sitasi teks
            sitasi[it["id"]] = f"[?{type(e).__name__}]"

    entri = [str(e) for e in bib.bibliography()]
    return entri, sitasi, dipakai


def _sudah_bernomor(entri: str) -> bool:
    """True bila gaya sudah menuliskan nomornya sendiri ([1] / 1.)."""
    return bool(re.match(r"^\s*(\[\d+\]|\(\d+\)|\d+\.)", entri))


def _rapikan(entri: str) -> str:
    """Spasi setelah penanda nomor gaya: '[1]C.' -> '[1] C.'"""
    entri = re.sub(r"^(\[\d+\])", r"\1 ", entri)
    entri = re.sub(r"^(\d+\.)(?=\S)", r"\1 ", entri)
    return re.sub(r"\s+", " ", entri).strip()


def _tulis_baris(entri: list, keluar) -> None:
    for i, e in enumerate(entri, 1):
        e = _rapikan(e)
        if _sudah_bernomor(e):
            keluar.write(e + "\n\n")
        else:
            keluar.write(f"{i}. {e}\n\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CSL-JSON -> Daftar Pustaka + sitasi")
    ap.add_argument("items", nargs="?", help="berkas CSL-JSON")
    ap.add_argument("--gaya", default="apa", help="apa|ieee|vancouver|harvard|chicago-author-date")
    ap.add_argument("--csl", help="path berkas .csl sendiri (menimpa --gaya)")
    ap.add_argument("--urut", help="naskah untuk menentukan urutan sitasi numerik")
    ap.add_argument("--out", help="tulis daftar pustaka ke berkas ini")
    ap.add_argument("--sitasi-out", help="tulis peta id->sitasi ke JSON")
    ap.add_argument("--html", action="store_true", help="pertahankan <i> untuk judul")
    ap.add_argument("--nama-lengkap", action="store_true",
                    help="tandai agar pemeriksa menolak et al./dkk")
    ap.add_argument("--locale", default="id-ID",
                    help="locale istilah CSL (default id-ID: 'dan', 'ed.', 'Dalam')")
    ap.add_argument("--format-kampus", choices=["nama_tahun_halaman", "nama_tahun",
                                               "naratif"],
                    help="pola sitasi pedoman kampus; menimpa layout <citation>")
    ap.add_argument("--halaman", action="append", metavar="ID=HAL",
                    help="locator halaman untuk sitasi, boleh berulang")
    ap.add_argument("--jumlah", action="store_true", help="cetak jumlah entri saja")
    ap.add_argument("--daftar-gaya", action="store_true")
    a = ap.parse_args(argv)

    if a.daftar_gaya:
        for k, v in sorted(GAYA_TERSEDIA.items()):
            p = os.path.join(STYLE_DIR, v)
            ada = os.path.isfile(p) and os.path.getsize(p) > 2000
            print(f"{k:24s} {v:32s} {'ok' if ada else 'BELUM DIUNDUH'}")
        return 0

    if not a.items:
        ap.error("beri berkas CSL-JSON, atau pakai --daftar-gaya")

    if not os.path.isfile(a.items):
        sys.exit(f"GAGAL: berkas tidak ada: {a.items}")

    items = muat_items(a.items)
    if not items:
        sys.exit("GAGAL: tidak ada item di berkas")

    gaya_path = path_gaya(a.gaya, a.csl)
    gaya_nama = os.path.basename(gaya_path).replace(".csl", "")
    gaya_pakai = siapkan_gaya(gaya_path, matikan_et_al=a.nama_lengkap,
                              format_kampus=a.format_kampus)

    if a.urut:
        items = cari_sitasi_di_naskah(a.urut, items)
        urut_info = "dari naskah"
    else:
        urut_info = "urutan berkas"

    # locator: baca --halaman "id=12" berulang supaya sitasi bisa
    # "(Nama, 2020:12)" sesuai contoh panduan ARS.
    locator = {}
    for pasangan in (a.halaman or []):
        if "=" in pasangan:
            k, v = pasangan.split("=", 1)
            locator[k.strip()] = ("page", v.strip())

    cacat = [it.get("id") for it in items
             if not (it.get("title") or it.get("author") or it.get("editor"))]

    entri, sitasi, dipakai = render(items, gaya_pakai, gaya_nama,
                                    nama_lengkap=a.nama_lengkap, html=a.html,
                                    locale=a.locale, locator_map=locator)

    if a.jumlah:
        print(json.dumps({"gaya": gaya_nama, "entri": len(entri),
                          "urut": urut_info, "cacat": cacat}, ensure_ascii=False))
        return 0 if not cacat else 1

    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            _tulis_baris(entri, f)
        print(json.dumps({"gaya": gaya_nama, "entri": len(entri),
                          "berkas": a.out, "urut": urut_info, "cacat": cacat},
                         ensure_ascii=False, indent=2))
    else:
        _tulis_baris(entri, sys.stdout)

    if a.sitasi_out:
        with open(a.sitasi_out, "w", encoding="utf-8") as f:
            json.dump({"gaya": gaya_nama, "sitasi": sitasi,
                       "items": [{k: v for k, v in it.items() if not k.startswith("_")}
                                 for it in dipakai]},
                      f, ensure_ascii=False, indent=2)

    return 0 if not cacat else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ImportError as e:
        sys.exit(f"GAGAL: butuh citeproc-py ({e}). Jalankan: "
                 f".venv/bin/pip install citeproc-py")
