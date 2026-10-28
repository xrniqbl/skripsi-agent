#!/usr/bin/env python3
"""Pecah catatan revisi pembimbing menjadi daftar kerja terlacak, lalu verifikasi.

Pemakaian:
    python3 parse_revisi.py 00_catatan_mentah.md --out 01_revisi.md
    python3 parse_revisi.py 01_revisi.md --verifikasi naskah.md
    python3 parse_revisi.py 01_revisi.md --laporan        # ringkasan status

Mode 1 (pecah):
    Membaca catatan mentah, memecah per baris bernomor/berpoin, mengklasifikasi
    prioritas + jenis dari kata kunci, menulis tabel kerja markdown.

Mode 2 (verifikasi):
    Memeriksa tabel kerja: butir 'selesai' wajib punya bukti; butir 'kritis'
    tidak boleh 'belum'; butir 'klarifikasi' tidak boleh 'selesai' tanpa jawaban.
    Bila --verifikasi NASKAH diberikan, bukti berupa kutipan harus ada di naskah.

Kode keluar:
    0  semua butir lolos
    1  ada butir yang gagal verifikasi
    2  berkas tidak terbaca
"""
from __future__ import annotations

import argparse
import re
import sys

# ---------- klasifikasi ----------
KATA_KRITIS = [
    "beda", "berbeda", "tidak sama", "copy paste", "copy-paste", "plagiat", "plagiasi",
    "sumber", "dari mana", "asal angka", "tidak konsisten", "salah hitung", "keliru",
]
KATA_TINGGI = [
    "rumusan", "tujuan", "metode", "pembahasan", "kurang dalam", "kurang", "tambah",
    "perdalam", "struktur", "logika", "hipotesis", "kesimpulan", "simpulan",
]
KATA_RENDAH = [
    "spasi", "margin", "font", "huruf", "garis", "tabel", "nomor", "penomoran",
    "format", "italic", "miring", "bold", "tegak", "jarak", "indent",
]
KATA_KLARIFIKASI = [
    "kayaknya", "kayak nya", "coba pikir", "pikir lagi", "kurang cocok", "mungkin",
    "sepertinya", "rasanya", "anu", "apa ya",
]
KATA_SARAN = ["sebaiknya", "coba pertimbangkan", "bisa dipertimbangkan", "alangkah"]

# penanda sumber di catatan mentah
RE_SUMBER = re.compile(r"^#{2,4}\s*(.+)$")
RE_BUTIR = re.compile(r"^\s*(?:(\d+)[.)]|[-*•])\s+(.{6,})$")
RE_KUTIP = re.compile(r"[\"'“”‘’]([^\"'“”‘’]{8,120})[\"'“”‘’]")

JENIS_LABEL = {"wajib": "wajib", "saran": "disarankan",
               "klarifikasi": "klarifikasi", "format": "format"}

ROMawi_MAP = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}


def ROMawi(n: int) -> str:
    return ROMawi_MAP.get(n, str(n))


def klasifikasi(teks: str) -> tuple[str, str]:
    """Kembalikan (jenis, prioritas)."""
    r = teks.lower()
    if any(k in r for k in KATA_KLARIFIKASI):
        return "klarifikasi", "tinggi"
    if any(k in r for k in KATA_KRITIS):
        return "wajib", "kritis"
    if any(k in r for k in KATA_RENDAH):
        return "format", "rendah"
    if any(k in r for k in KATA_SARAN):
        return "disarankan", "sedang"
    if any(k in r for k in KATA_TINGGI):
        return "wajib", "tinggi"
    return "wajib", "sedang"


def tebak_lokasi(teks: str) -> str:
    r = teks.lower()
    # urutan penting: yang paling spesifik dulu.
    # "Tabel 2.1" -> Bab II, bukan "—"
    m_tab = re.search(r"\btabel\s*(\d+)\.", r)
    if m_tab:
        return f"Bab {ROMawi(int(m_tab.group(1)))}"
    # "abstrak ... setelah bab 5" -> Abstrak, bukan Bab V
    if re.search(r"\babstrak\b", r):
        return "Abstrak"
    if re.search(r"\blampiran\b", r):
        return "Lampiran"
    if re.search(r"\bpustaka\b|\breferensi\b|\bsitasi\b|\bjurnal\b|\bdaftar pustaka\b", r):
        return "Daftar Pustaka"
    if re.search(r"\bbab\s*(1|i)\b|\blatar\b|\brumusan\b|\btujuan\b|\bmanfaat\b", r):
        return "Bab I"
    if re.search(r"\bbab\s*(2|ii)\b|\btinjauan\b|\bteori\b|\bkerangka\b", r):
        return "Bab II"
    if re.search(r"\bbab\s*(3|iii)\b|\bmetode\b|\bsampel\b|\binstrumen\b|\banalisis\b", r):
        return "Bab III"
    if re.search(r"\bbab\s*(4|iv)\b|\bhasil\b|\bpembahasan\b", r):
        return "Bab IV"
    if re.search(r"\bbab\s*(5|v)\b|\bsimpulan\b|\bkesimpulan\b|\bsaran\b", r):
        return "Bab V"
    m = re.search(r"\bhal(?:aman)?\s*(\d+)", r)
    if m:
        return f"hal {m.group(1)}"
    return "—"


def pecah_catatan(teks: str) -> list[dict]:
    butir: list[dict] = []
    sumber = "(tanpa sumber)"
    for baris in teks.splitlines():
        m_s = RE_SUMBER.match(baris.strip())
        if m_s:
            sumber = m_s.group(1).strip()
            continue
        m = RE_BUTIR.match(baris)
        if not m:
            continue
        isi = re.sub(r"\s+", " ", m.group(2)).strip()
        if len(isi) < 6:
            continue
        # buang penanda status kalau ada ("[selesai]", "(sudah)")
        isi = re.sub(r"^\[[^\]]*\]\s*", "", isi)
        jenis, prioritas = klasifikasi(isi)
        butir.append({
            "isi": isi,
            "sumber": sumber,
            "lokasi": tebak_lokasi(isi),
            "jenis": jenis,
            "prioritas": prioritas,
        })
    return butir


def tulis_tabel(butir: list[dict], keluar: str) -> None:
    baris = [
        "# Daftar Kerja Revisi",
        "",
        "Isi kolom **Bukti** dengan sesuatu yang bisa diverifikasi orang lain — angka, "
        "nomor halaman, kutipan. Bukan \"sudah\".",
        "",
        "Status: `belum` · `sedang` · `selesai` · `ditolak-dengan-alasan`",
        "",
        "| ID | Butir | Sumber | Lokasi | Jenis | Prioritas | Status | Bukti |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, b in enumerate(butir, 1):
        isi = b["isi"].replace("|", "\\|")
        baris.append(
            f"| R-{i:02d} | {isi} | {b['sumber']} | {b['lokasi']} | {b['jenis']} | "
            f"{b['prioritas']} | belum |  |")
    baris += [
        "",
        "## Catatan pengerjaan",
        "",
        "Tempel detail per butir di bawah ini (satu subbab per R-xx):",
        "",
        "```markdown",
        "### R-01 — <ringkas>",
        "- **Catatan asli**: …",
        "- **Diagnosis**: …",
        "- **Tindakan**: …",
        "- **Bukti**: …",
        "- **Status**: selesai",
        "- **Tanggal**: YYYY-MM-DD",
        "```",
    ]
    open(keluar, "w", encoding="utf-8").write("\n".join(baris) + "\n")


def baca_tabel(path: str) -> list[dict]:
    """Baca tabel kerja revisi dari markdown."""
    teks = open(path, encoding="utf-8").read()
    butir: list[dict] = []
    for baris in teks.splitlines():
        if not baris.strip().startswith("|"):
            continue
        sel = [s.strip() for s in baris.strip().strip("|").split("|")]
        if len(sel) < 8 or not re.match(r"^R-\d+$", sel[0]):
            continue
        # kolom terakhir = bukti (bisa mengandung | yang sudah di-escape)
        if len(sel) > 8:
            sel = sel[:7] + ["|".join(sel[7:])]
        butir.append({
            "id": sel[0], "isi": sel[1].replace("\\|", "|"), "sumber": sel[2],
            "lokasi": sel[3], "jenis": sel[4], "prioritas": sel[5],
            "status": sel[6].strip().lower(), "bukti": sel[7].strip(),
        })
    return butir


BUKTI_TIDAK_SAH = {"", "-", "sudah", "ok", "oke", "beres", "done", "selesai",
                   "sudah dicek", "sudah diperbaiki", "fix", "v", "✓", "ya"}


def verifikasi(butir: list[dict], naskah: str | None) -> tuple[list[dict], list[dict]]:
    galat, peringatan = [], []
    isi_naskah = ""
    if naskah:
        try:
            isi_naskah = open(naskah, encoding="utf-8", errors="replace").read()
        except OSError as e:
            galat.append({"id": "-", "pesan": f"naskah tidak terbaca: {e}"})
            return galat, peringatan

    for b in butir:
        if b["status"] not in ("belum", "sedang", "selesai", "ditolak-dengan-alasan"):
            peringatan.append({"id": b["id"],
                               "pesan": f"status '{b['status']}' tidak dikenal "
                                        f"(pakai: belum/sedang/selesai/ditolak-dengan-alasan)"})
        if b["prioritas"] == "kritis" and b["status"] != "selesai":
            galat.append({"id": b["id"],
                          "pesan": f"butir KRITIS masih '{b['status']}' — kerjakan lebih dulu"})
        if b["status"] == "selesai":
            if b["bukti"].lower() in BUKTI_TIDAK_SAH:
                galat.append({"id": b["id"],
                              "pesan": "status selesai tetapi bukti kosong/tidak terukur "
                                       "(isi dengan angka, halaman, atau kutipan)"})
            elif naskah:
                # bukti berupa kutipan: cek keberadaannya di naskah
                kutipan = RE_KUTIP.findall(b["bukti"])
                for k in kutipan:
                    if k.strip() and k.strip() not in isi_naskah:
                        peringatan.append({
                            "id": b["id"],
                            "pesan": f"kutipan bukti tidak ditemukan di naskah: '{k[:60]}'"})
                # bukti berupa angka: hanya angka berpola data (desimal/persen) yang dicek.
                # tanggal, nomor halaman, dan hitungan pustaka bukan nilai naskah.
                # Bukti hasil pemeriksaan eksternal (similarity, jumlah kata) juga dilewati.
                eksternal = re.search(r"similar|plagia|turnitin|kata|jurnal|pustaka|"
                                      r"paragraf|garis|presen", b["bukti"], re.I)
                angka = re.findall(r"\d+[.,]\d+\s*%?|\d+\s*%", b["bukti"])
                if angka and not eksternal and not any(
                        a.replace(" ", "") in isi_naskah.replace(" ", "") for a in angka):
                    peringatan.append({
                        "id": b["id"],
                        "pesan": f"angka data pada bukti ({', '.join(angka[:3])}) tidak "
                                 f"ditemukan di naskah — periksa apakah revisi diterapkan"})
        if b["jenis"] == "klarifikasi" and b["status"] == "selesai":
            if not re.search(r"(jawab|dijawab|klarifikasi|menurut pembimbing|disetujui)",
                             b["bukti"], re.I):
                galat.append({"id": b["id"],
                              "pesan": "butir klarifikasi ditandai selesai tanpa catatan "
                                       "jawaban pembimbing — tanyakan dulu, jangan menebak"})
        if b["status"] == "ditolak-dengan-alasan" and len(b["bukti"]) < 20:
            galat.append({"id": b["id"],
                          "pesan": "penolakan tanpa alasan memadai — tulis argumen "
                                   "metodologis + rujukan halaman"})
    return galat, peringatan


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("berkas")
    ap.add_argument("--out", help="tulis tabel kerja ke berkas ini (mode pecah)")
    ap.add_argument("--verifikasi", metavar="NASKAH",
                    help="verifikasi tabel kerja terhadap naskah")
    ap.add_argument("--laporan", action="store_true", help="cetak ringkasan status")
    ap.add_argument("--ketat", action="store_true", help="peringatan dihitung sebagai galat")
    args = ap.parse_args()

    try:
        teks = open(args.berkas, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print(f"GAGAL membaca {args.berkas}: {e}", file=sys.stderr)
        return 2

    # mode pecah: berkas belum berupa tabel kerja
    if not re.search(r"^\|\s*R-\d+", teks, re.M) and not args.verifikasi and not args.laporan:
        butir = pecah_catatan(teks)
        if not butir:
            print("Tidak ada butir catatan yang terdeteksi. "
                  "Format: baris bernomor '1. ...' atau berpoin '- ...'.", file=sys.stderr)
            return 2
        keluar = args.out or "01_revisi.md"
        tulis_tabel(butir, keluar)
        print(f"Terdeteksi {len(butir)} butir.\n")
        print(f"{'ID':<6} {'Prioritas':<10} {'Jenis':<12} Lokasi")
        print("-" * 78)
        urut = {"kritis": 0, "tinggi": 1, "sedang": 2, "rendah": 3}
        for i, b in enumerate(sorted(butir, key=lambda x: urut[x["prioritas"]]), 1):
            print(f"R-{b.get('_n', i):02d}  {b['prioritas']:<10} {b['jenis']:<12} "
                  f"{b['lokasi']}")
            print(f"       {b['isi'][:88]}")
        hitung = {}
        for b in butir:
            hitung[b["prioritas"]] = hitung.get(b["prioritas"], 0) + 1
        print("\n" + " · ".join(f"{k}: {v}" for k, v in
                                sorted(hitung.items(), key=lambda x: urut[x[0]])))
        print(f"\nDitulis: {keluar}")
        print("Langkah berikutnya: isi kolom Bukti, lalu jalankan --verifikasi NASKAH.",
              file=sys.stderr)
        return 0

    # mode verifikasi / laporan
    butir = baca_tabel(args.berkas)
    if not butir:
        print("Tabel kerja revisi tidak ditemukan (butuh baris '| R-01 | ... |').",
              file=sys.stderr)
        return 2

    galat, peringatan = verifikasi(butir, args.verifikasi or None)
    hitung = {}
    for b in butir:
        hitung[b["status"]] = hitung.get(b["status"], 0) + 1

    print(f"Total butir: {len(butir)}")
    for s in ("belum", "sedang", "selesai", "ditolak-dengan-alasan"):
        if hitung.get(s):
            print(f"  {s:<24} {hitung[s]}")
    selesai = hitung.get("selesai", 0) + hitung.get("ditolak-dengan-alasan", 0)
    print(f"  progres                  {selesai}/{len(butir)} "
          f"({selesai / len(butir) * 100:.0f}%)")

    kritis = [b for b in butir if b["prioritas"] == "kritis"]
    if kritis:
        print(f"\nButir kritis ({len(kritis)}):")
        for b in kritis:
            tanda = "OK  " if b["status"] == "selesai" else "!!  "
            print(f"  {tanda}{b['id']} [{b['status']}] {b['isi'][:70]}")

    if galat:
        print(f"\n=== GALAT ({len(galat)}) ===")
        for g in galat:
            print(f"  ✗ {g['id']}: {g['pesan']}")
    if peringatan:
        print(f"\n=== PERINGATAN ({len(peringatan)}) ===")
        for p in peringatan:
            print(f"  ! {p['id']}: {p['pesan']}")
    if not galat and not peringatan:
        print("\nSemua butir lolos verifikasi.")

    gagal = bool(galat) or (args.ketat and bool(peringatan))
    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main())
