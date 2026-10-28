#!/usr/bin/env python3
"""Buat dokumen usaha PDF (A4) untuk lampiran verifikasi bisnis.

Pemakaian:
    python3 buat_dokumen_usaha.py --nama "Komenin" --out sku.pdf
    python3 buat_dokumen_usaha.py --nama "Komenin" --logo https://situs.id/logo.png --out sku.pdf
    python3 buat_dokumen_usaha.py --nama "Komenin" --jenis kop --out kop.pdf

Jenis:
    sku     Surat Keterangan Usaha — nama usaha, alamat, telepon, bidang usaha,
            kolom tanda tangan, dan cap usaha bulat (digambar otomatis sebagai SVG,
            bisa diganti --cap berkas.png).
    kop     Kop surat resmi usaha (letterhead) — memakai logo bila ada.
    profil  Profil singkat usaha satu halaman.

Logo (--logo) menerima URL http(s) atau berkas lokal; diunduh lalu disematkan
sebagai data URI supaya PDF-nya mandiri (tidak butuh koneksi saat dibuka).

Cap (--cap) menerima berkas gambar. Tanpa itu, cap digambar sebagai SVG bulat
berisi nama usaha + bidang + kota. Cap SVG ini adalah pratinjau tata letak —
cap yang sah tetap dibubuhkan pemilik usaha.

Skrip ini TIDAK membuat dokumen yang mengaku diterbitkan instansi lain.
"""
from __future__ import annotations

import argparse
import base64
import datetime
import html
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

CHROME_KANDIDAT = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "/usr/bin/google-chrome", "/usr/bin/chromium",
]

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")

BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


def cari_chrome() -> str | None:
    for c in CHROME_KANDIDAT:
        p = shutil.which(c)
        if p:
            return p
    return None


# --------------------------------------------------------------------------
# gambar: logo + cap
# --------------------------------------------------------------------------

def ke_data_uri(sumber: str) -> str:
    """URL http(s) atau path lokal -> data URI. String kosong bila gagal."""
    if not sumber:
        return ""
    try:
        if sumber.startswith(("http://", "https://")):
            req = urllib.request.Request(sumber, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                blob = r.read()
                ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
            if not ctype.startswith("image/"):
                ctype = mimetypes.guess_type(sumber)[0] or "image/png"
        else:
            with open(sumber, "rb") as f:
                blob = f.read()
            ctype = mimetypes.guess_type(sumber)[0] or "image/png"
        if len(blob) < 100:
            return ""
        return f"data:{ctype};base64,{base64.b64encode(blob).decode()}"
    except Exception:  # noqa: BLE001
        return ""


def _bidang_cap(bidang: str) -> str:
    """Ambil inti bidang usaha, buang embel-embel setelah tanda pisah."""
    inti = re.split(r"[—–]|\s-\s", bidang)[0].strip().upper()
    kata = inti.split()
    hasil = []
    panjang = 0
    for k in kata:
        if panjang + len(k) + (1 if hasil else 0) > 29:
            break
        hasil.append(k)
        panjang += len(k) + (1 if len(hasil) > 1 else 0)
    return " ".join(hasil) if hasil else inti[:29]


def svg_cap(nama: str, bidang: str, kota: str) -> str:
    """Cap bulat SVG: nama melengkung di atas, bidang + kota di tengah."""
    nama_u = nama.upper()
    bidang_pendek = _bidang_cap(bidang)

    r_busur = 74
    lingkar = 2 * 3.141592653589793 * r_busur
    n = max(len(nama_u), 1)
    # spasi huruf agar nama mengisi busur tanpa meluber
    spasi = max(1.2, min(17.0, (lingkar * 0.58) / n - 8.2))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <defs>
    <path id="atas" d="M 100,100 m -{r_busur},0 a {r_busur},{r_busur} 0 1,1 {2*r_busur},0" fill="none"/>
    <path id="bawah" d="M 100,100 m -{r_busur},0 a {r_busur},{r_busur} 0 1,0 {2*r_busur},0" fill="none"/>
  </defs>
  <g fill="none" stroke="#1e40af" stroke-opacity="0.88">
    <circle cx="100" cy="100" r="94" stroke-width="3.4"/>
    <circle cx="100" cy="100" r="88.5" stroke-width="1.1"/>
    <circle cx="100" cy="100" r="53" stroke-width="1.1"/>
  </g>
  <g fill="#1e40af" fill-opacity="0.9" font-family="DejaVu Sans, Liberation Sans, sans-serif">
    <text font-size="14.5" font-weight="700" letter-spacing="{spasi:.2f}">
      <textPath href="#atas" startOffset="50%" text-anchor="middle">{html.escape(nama_u)}</textPath>
    </text>
    <text x="100" y="94" font-size="6.2" letter-spacing="0.7" text-anchor="middle"
          fill-opacity="0.88">{html.escape(bidang_pendek)}</text>
    <text x="100" y="106" font-size="6.4" letter-spacing="1.6" text-anchor="middle"
          fill-opacity="0.74">{html.escape(kota.upper())}</text>
    <text x="100" y="117" font-size="5.1" letter-spacing="1.2" text-anchor="middle"
          fill-opacity="0.55">INDONESIA</text>
    <text font-size="5.6" letter-spacing="1.3" fill-opacity="0.8">
      <textPath href="#bawah" startOffset="50%" text-anchor="middle">◆ ◆ ◆</textPath>
    </text>
  </g>
</svg>"""


def latar_logo_gelap(uri: str) -> bool:
    """True bila logo punya latar hampir seragam & gelap (butuh sudut membulat)."""
    if not uri.startswith("data:image/"):
        return False
    try:
        import io
        from PIL import Image
        blob = base64.b64decode(uri.split(",", 1)[1])
        im = Image.open(io.BytesIO(blob)).convert("RGB")
        w, h = im.size
        sudut = [im.getpixel(p) for p in
                 ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2))]
        # semua sudut mirip?
        r0, g0, b0 = sudut[0]
        seragam = all(abs(r - r0) + abs(g - g0) + abs(b - b0) < 24
                      for r, g, b in sudut)
        gelap = (r0 + g0 + b0) / 3 < 90
        return bool(seragam and gelap)
    except Exception:  # noqa: BLE001
        return False


def inisial(nama: str) -> str:
    """Huruf awal setiap kata: "Harry's Farm" -> "HF"."""
    bersih = re.sub(r"['’]s\b", "", nama, flags=re.I)
    kata = [k for k in bersih.replace("'", " ").replace("’", " ")
            .replace("-", " ").split() if k]
    if not kata:
        return "US"
    if len(kata) == 1:
        return kata[0][:2].upper()
    return (kata[0][0] + kata[1][0]).upper()


# --------------------------------------------------------------------------
# halaman
# --------------------------------------------------------------------------

def halaman_sku(d: dict) -> str:
    nama = html.escape(d["nama"].upper())
    alamat = html.escape(d["alamat"])
    telepon = html.escape(d["telepon"])
    pemilik = html.escape(d.get("pemilik") or "-")
    bidang = html.escape(d.get("bidang") or "Perdagangan")
    kota = html.escape(d.get("kota") or "Cimahi")
    tanggal = html.escape(d["tanggal"])

    logo = d.get("logo_uri") or ""
    kls = "brand bulat" if d.get("logo_gelap") else "brand"
    logo_html = (f'<img class="{kls}" src="{logo}" alt="">' if logo
                 else f'<div class="brand-txt">{html.escape(inisial(d["nama"]))}</div>')
    cap_html = (f'<img class="cap-img" src="{d["cap_uri"]}" alt="">' if d.get("cap_uri")
                else svg_cap(d["nama"], d.get("bidang") or "", d.get("kota") or "Cimahi"))

    extra = ""
    if d.get("nib"):
        extra += f'<tr><td class="k">NIB</td><td class="s">:</td><td>{html.escape(d["nib"])}</td></tr>'
    if d.get("npwp"):
        extra += f'<tr><td class="k">NPWP</td><td class="s">:</td><td>{html.escape(d["npwp"])}</td></tr>'
    if d.get("situs"):
        extra += f'<tr><td class="k">Situs Web</td><td class="s">:</td><td>{html.escape(d["situs"])}</td></tr>'

    return f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8">
<title>Surat Keterangan Usaha — {nama}</title>
<style>
  @page {{ size: A4; margin: 15mm 19mm 13mm 21mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: "Liberation Serif", "DejaVu Serif", Georgia, serif;
         font-size: 10.5pt; line-height: 1.40; color: #111; margin: 0; }}

  .kop {{ display: flex; align-items: center; gap: 5mm;
          border-bottom: 3px double #111; padding-bottom: 2.4mm; }}
  .brand {{ height: 18mm; width: auto; object-fit: contain; }}
  .brand.bulat {{ border-radius: 2.4mm; }}
  .brand-txt {{ width: 18mm; height: 18mm; border: 1.5pt solid #111; border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                font-family: "Liberation Sans", sans-serif; font-size: 13pt;
                font-weight: 700; letter-spacing: .04em; flex: 0 0 auto; }}
  .kop .nm {{ font-size: 16pt; font-weight: 700; letter-spacing: .05em; line-height: 1.08; }}
  .kop .bd {{ font-size: 7.8pt; color: #333; letter-spacing: .03em; margin-top: 1.1mm;
              text-transform: uppercase; }}
  .kop .al {{ font-size: 8.3pt; color: #333; margin-top: .9mm; }}
  .garis2 {{ border-top: 1px solid #111; margin-top: 1px; margin-bottom: 4.5mm; }}

  h1 {{ font-size: 12pt; text-align: center; text-decoration: underline;
        letter-spacing: .11em; margin: 0 0 1px; font-weight: 700; }}
  .nomor {{ text-align: center; font-size: 9.4pt; margin-bottom: 3.5mm; color: #333; }}

  p {{ margin: 0 0 2.2mm; text-align: justify; }}

  table.data {{ width: 100%; border-collapse: collapse; margin: .8mm 0 2.6mm; }}
  table.data td {{ padding: 1mm .9mm; vertical-align: top; font-size: 10.3pt; }}
  table.data td.k {{ width: 32%; font-weight: 600; }}
  table.data td.s {{ width: 2.4%; }}

  .pernyataan {{ border-left: 2.5px solid #444; padding: 1.3mm 0 1.3mm 3.8mm;
                 margin: 2.6mm 0; font-size: 9.9pt; }}
  .pernyataan ol {{ margin: 0; padding-left: 4.6mm; }}
  .pernyataan li {{ margin-bottom: 1mm; }}

  .tanda {{ margin-top: 20mm; width: 100%; }}
  .tanda td {{ width: 50%; vertical-align: top; font-size: 10.1pt; }}
  .tanda td.kiri {{ position: relative; }}
  .blok-ttd {{ position: relative; height: 50mm; }}
  .cap-wrap {{ position: absolute; left: 0; top: 2mm; width: 39mm; opacity: .8; }}
  .cap-wrap svg, .cap-img {{ width: 39mm; height: 39mm; object-fit: contain; }}
  .ttd {{ height: 14mm; }}
  .nm-ttd {{ font-weight: 700; text-decoration: underline; }}

  .catatan {{ margin-top: 9mm; font-size: 7.5pt; color: #555; line-height: 1.33;
              border-top: 1px solid #ccc; padding-top: 1.8mm; text-align: justify; }}
</style></head>
<body>

<div class="kop">
  {logo_html}
  <div>
    <div class="nm">{nama}</div>
    <div class="bd">{bidang}</div>
    <div class="al">{alamat} &nbsp;·&nbsp; Telp. {telepon}</div>
  </div>
</div>
<div class="garis2"></div>

<h1>SURAT KETERANGAN USAHA</h1>
<div class="nomor">Nomor: {html.escape(d.get('nomor') or '')}</div>

<p>Yang bertanda tangan di bawah ini, selaku pemilik dan penanggung jawab usaha,
dengan ini menerangkan bahwa usaha yang tersebut di bawah ini benar-benar
beroperasi dan beralamat pada lokasi yang tercantum:</p>

<table class="data">
  <tr><td class="k">Nama Usaha</td><td class="s">:</td><td><strong>{nama}</strong></td></tr>
  <tr><td class="k">Nama Pemilik</td><td class="s">:</td><td>{pemilik}</td></tr>
  <tr><td class="k">Bidang Usaha</td><td class="s">:</td><td>{bidang}</td></tr>
  <tr><td class="k">Alamat Usaha</td><td class="s">:</td><td>{alamat}</td></tr>
  <tr><td class="k">Nomor Telepon</td><td class="s">:</td><td>{telepon}</td></tr>
  <tr><td class="k">Status Tempat Usaha</td><td class="s">:</td><td>{html.escape(d.get('status_tempat') or 'Milik sendiri')}</td></tr>
  {extra}
</table>

<p>Usaha tersebut di atas telah berjalan secara aktif dan menjadi sumber penghasilan
utama pemilik. Segala kegiatan operasional, transaksi, dan komunikasi resmi usaha
menggunakan alamat serta nomor telepon sebagaimana tercantum pada tabel di atas.</p>

<div class="pernyataan">
  <ol>
    <li>Seluruh keterangan dalam surat ini adalah benar dan dapat dipertanggungjawabkan.</li>
    <li>Usaha beroperasi pada alamat yang tercantum dan tidak berpindah dalam 12 bulan terakhir.</li>
    <li>Nomor telepon yang tercantum aktif digunakan untuk komunikasi resmi usaha.</li>
  </ol>
</div>

<p>Demikian surat keterangan ini dibuat dengan sebenarnya untuk dapat dipergunakan
sebagaimana mestinya.</p>

<table class="tanda">
  <tr>
    <td class="kiri"><div class="cap-wrap">{cap_html}</div></td>
    <td style="text-align:left;">
      {kota}, {tanggal}<br>
      Pemilik / Penanggung Jawab,
      <div class="blok-ttd">
        <div class="ttd"></div>
        <div class="nm-ttd">{pemilik}</div>
      </div>
    </td>
  </tr>
</table>

<div class="catatan">Dokumen ini dibuat dan ditandatangani sendiri oleh pemilik usaha sebagai
keterangan domisili dan aktivitas usaha, bukan dokumen yang diterbitkan oleh instansi
pemerintah. Cap pada dokumen ini adalah pratinjau tata letak; cap yang sah dibubuhkan oleh
pemilik usaha. Untuk keperluan yang mensyaratkan dokumen resmi, gunakan NIB dari OSS
(oss.go.id) atau Surat Keterangan Domisili Usaha dari kelurahan setempat.</div>

</body></html>"""


def halaman_kop(d: dict) -> str:
    nama = html.escape(d["nama"].upper())
    alamat = html.escape(d["alamat"])
    telepon = html.escape(d["telepon"])
    bidang = html.escape(d.get("bidang") or "Perdagangan")
    logo = d.get("logo_uri") or ""
    kls = "logo-img bulat" if d.get("logo_gelap") else "logo-img"
    logo_html = (f'<img class="{kls}" src="{logo}" alt="">' if logo
                 else f'<div class="logo">{html.escape(inisial(d["nama"]))}</div>')
    return f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8"><title>Kop Surat — {nama}</title>
<style>
  @page {{ size: A4; margin: 20mm; }}
  body {{ font-family: "Liberation Serif", "DejaVu Serif", Georgia, serif;
         font-size: 11pt; color: #111; margin: 0; }}
  .kop {{ display: flex; align-items: center; gap: 5mm;
          border-bottom: 3px double #111; padding-bottom: 3mm; }}
  .logo {{ width: 22mm; height: 22mm; border: 1.8pt solid #111; border-radius: 50%;
           display: flex; align-items: center; justify-content: center;
           font-family: "Liberation Sans", sans-serif; font-size: 15pt;
           font-weight: 700; letter-spacing: .04em; flex: 0 0 auto; }}
  .logo-img {{ height: 22mm; width: auto; object-fit: contain; }}
  .logo-img.bulat {{ border-radius: 3mm; }}
  .txt .nm {{ font-size: 19pt; font-weight: 700; letter-spacing: .06em; line-height: 1.1; }}
  .txt .bd {{ font-size: 8.3pt; color: #333; letter-spacing: .04em;
              text-transform: uppercase; margin-top: 1.4mm; }}
  .txt .al {{ font-size: 9pt; color: #333; margin-top: 1.4mm; }}
  .isi {{ margin-top: 26mm; }}
  p {{ margin: 0 0 12px; text-align: justify; line-height: 1.6; }}
  .garis {{ border-top: 1px solid #111; margin-top: 30mm; padding-top: 6px;
            font-size: 8.5pt; color: #555; text-align: center; }}
</style></head>
<body>
  <div class="kop">
    {logo_html}
    <div class="txt">
      <div class="nm">{nama}</div>
      <div class="bd">{bidang}</div>
      <div class="al">{alamat} &nbsp;|&nbsp; Telp. {telepon}</div>
    </div>
  </div>
  <div class="isi">
    <p><em>Contoh isi surat — ganti dengan teks Anda.</em></p>
    <p>Dengan hormat, sehubungan dengan kegiatan usaha kami, bersama surat ini kami
    sampaikan informasi yang diperlukan. Seluruh komunikasi resmi dapat ditujukan
    ke alamat dan nomor telepon pada kop surat di atas.</p>
  </div>
  <div class="garis">{nama} · {alamat} · {telepon}</div>
</body></html>"""


def halaman_profil(d: dict) -> str:
    nama = html.escape(d["nama"].upper())
    alamat = html.escape(d["alamat"])
    telepon = html.escape(d["telepon"])
    pemilik = html.escape(d.get("pemilik") or "-")
    bidang = html.escape(d.get("bidang") or "Perdagangan")
    logo = d.get("logo_uri") or ""
    logo_html = f'<img class="lg" src="{logo}" alt="">' if logo else ""
    situs_row = (f'<tr><td class="k">Situs Web</td><td>{html.escape(d["situs"])}</td></tr>'
                 if d.get("situs") else "")
    return f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8"><title>Profil Usaha — {nama}</title>
<style>
  @page {{ size: A4; margin: 22mm; }}
  body {{ font-family: "Liberation Sans", "DejaVu Sans", Arial, sans-serif;
         font-size: 10.5pt; color: #111; margin: 0; line-height: 1.6; }}
  .lg {{ height: 20mm; width: auto; margin-bottom: 6mm; }}
  h1 {{ font-size: 22pt; letter-spacing: .04em; margin: 0 0 4px; }}
  .sub {{ color: #555; font-size: 10pt; letter-spacing: .16em; text-transform: uppercase;
          border-bottom: 2px solid #111; padding-bottom: 12px; margin-bottom: 22px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td {{ padding: 8px 6px; border-bottom: 1px solid #e2e2e2; vertical-align: top; }}
  td.k {{ width: 32%; font-weight: 600; color: #333; }}
</style></head>
<body>
  {logo_html}
  <h1>{nama}</h1>
  <div class="sub">Profil Usaha</div>
  <table>
    <tr><td class="k">Nama Usaha</td><td>{nama}</td></tr>
    <tr><td class="k">Pemilik</td><td>{pemilik}</td></tr>
    <tr><td class="k">Bidang Usaha</td><td>{bidang}</td></tr>
    <tr><td class="k">Alamat</td><td>{alamat}</td></tr>
    <tr><td class="k">Telepon</td><td>{telepon}</td></tr>
    {situs_row}
    <tr><td class="k">Jam Operasional</td><td>{html.escape(d.get('jam') or '08.00 – 20.00 WIB')}</td></tr>
  </table>
</body></html>"""


HALAMAN = {"sku": halaman_sku, "kop": halaman_kop, "profil": halaman_profil}


def render(html_str: str, out_pdf: str) -> None:
    chrome = cari_chrome()
    if not chrome:
        print("GAGAL: tidak menemukan Chrome/Chromium untuk render PDF.", file=sys.stderr)
        print("  Pasang: apt-get install chromium   (atau google-chrome)", file=sys.stderr)
        sys.exit(2)
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "dok.html")
    with open(src, "w", encoding="utf-8") as f:
        f.write(html_str)
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer", "--virtual-time-budget=3000",
           f"--print-to-pdf={os.path.abspath(out_pdf)}", "file://" + src]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    shutil.rmtree(tmp, ignore_errors=True)
    if not os.path.isfile(out_pdf) or os.path.getsize(out_pdf) < 800:
        print("GAGAL render PDF.", file=sys.stderr)
        print((r.stderr or "")[-600:], file=sys.stderr)
        sys.exit(2)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Buat dokumen usaha PDF untuk lampiran verifikasi.",
        epilog='contoh: python3 buat_dokumen_usaha.py --nama "Komenin" '
               '--logo https://komenin.id/brand/komenin-robot-256.png --out sku.pdf')
    ap.add_argument("--nama", required=True, help="nama usaha persis seperti didaftarkan")
    ap.add_argument("--alamat",
                    default="Gang Madhayi No. 22, Jalan Kebon Kopi, Cimahi 40535, Jawa Barat")
    ap.add_argument("--telepon", default="+6285846135623")
    ap.add_argument("--pemilik", default="Iqbal Saputra")
    ap.add_argument("--bidang",
                    default="Jasa Teknologi Informasi — Pembuatan dan Pengembangan Website")
    ap.add_argument("--kota", default="Cimahi")
    ap.add_argument("--tanggal", default="", help="mis. '28 Oktober 2026'")
    ap.add_argument("--nib", default="")
    ap.add_argument("--npwp", default="")
    ap.add_argument("--situs", default="", help="situs web usaha")
    ap.add_argument("--status-tempat", default="Milik sendiri")
    ap.add_argument("--nomor", default="")
    ap.add_argument("--logo", default="", help="URL/berkas logo usaha")
    ap.add_argument("--cap", default="", help="berkas gambar cap usaha")
    ap.add_argument("--jenis", default="sku", choices=sorted(HALAMAN))
    ap.add_argument("--out", required=True)
    ap.add_argument("--html", help="simpan juga HTML sumbernya")
    a = ap.parse_args()

    if not a.out.lower().endswith(".pdf"):
        print("PERINGATAN: --out tidak berakhiran .pdf", file=sys.stderr)

    if not a.tanggal:
        t = datetime.date.today()
        a.tanggal = f"{t.day} {BULAN[t.month - 1]} {t.year}"
    if not a.nomor:
        a.nomor = f"001/SKU/{a.tanggal.split()[-1]}"

    d = {"nama": a.nama, "alamat": a.alamat, "telepon": a.telepon,
         "pemilik": a.pemilik, "bidang": a.bidang, "kota": a.kota,
         "tanggal": a.tanggal, "nib": a.nib, "npwp": a.npwp, "situs": a.situs,
         "status_tempat": a.status_tempat, "nomor": a.nomor,
         "logo_uri": ke_data_uri(a.logo), "cap_uri": ke_data_uri(a.cap)}
    d["logo_gelap"] = latar_logo_gelap(d["logo_uri"])

    if a.logo and not d["logo_uri"]:
        print(f"PERINGATAN: logo gagal dimuat ({a.logo}); memakai monogram.", file=sys.stderr)
    if a.cap and not d["cap_uri"]:
        print(f"PERINGATAN: cap gagal dimuat ({a.cap}); memakai cap SVG.", file=sys.stderr)

    doc = HALAMAN[a.jenis](d)
    if a.html:
        with open(a.html, "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"HTML: {a.html}")
    render(doc, a.out)
    print(f"PDF : {a.out}  ({os.path.getsize(a.out):,} B)  jenis={a.jenis}"
          f"  logo={'ya' if d['logo_uri'] else 'monogram'}"
          f"  cap={'gambar' if d['cap_uri'] else 'svg'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
