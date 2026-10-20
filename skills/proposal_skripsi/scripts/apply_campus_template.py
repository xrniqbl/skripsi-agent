#!/usr/bin/env python3
"""
apply_campus_template.py — Terapkan preset template kampus pada proposal.

Perintah:
    list                     tampilkan preset yang tersedia
    show <preset>            tampilkan ringkasan preset
    init <preset> [-o F]     buat kerangka proposal.md dari preset
    check <preset> <naskah>  cek naskah terhadap ketentuan preset [--lengkap]
    new-custom -o F         salin kerangka custom.json untuk diisi manual

Preset dibaca dari campus_templates/*.json. Aturan yang tidak ada di preset
tidak ditebak: script hanya melaporkan, tidak mengubah naskah.
"""

import argparse
import json
import os
import re
import sys

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_PRESET = os.path.join(AKAR, "campus_templates")

CEK = {
    "latar_belakang": r"latar\s+belakang",
    "rumusan_masalah": r"rumusan\s+masalah",
    "tujuan": r"tujuan\s+penelitian",
    "manfaat": r"manfaat\s+penelitian",
    "batasan": r"batasan\s+masalah|ruas\s+lingkup",
    "data_empat_lapisan": None,
    "celah_penelitian": r"(celah|gap|kekosongan|belum diteliti|tidak banyak)",
    "tabel_penelitian_terdahulu": r"tabel\s+\d+\.\d+|penelitian\s+terdahulu",
    "desain_penelitian": r"desain\s+penelitian|ragam\s+penelitian",
    "populasi_sampel": r"populasi",
    "teknik_sampel": r"(teknik\s+sampel|random|sampel\s+(purposive|probabilistik|stratified))",
    "perhitungan_sampel": r"(rumus|sloven|tabel\s+isaac|perhitungan\s+sampel|n\s*=\s*\d+)",
    "skala_likert": r"(skala\s+likert|likert)",
    "instrumen_validitas_reliabilitas": r"(validitas|reliabilitas|cronbach|uji\s+valid)",
    "uji_statistik_cocok": r"(regresi|anova|chi-?square|t-?test|uji\s+\w+|analisis\s+\w+)",
    "hasil_uji_tabel": r"tabel\s+\d+\.\d+|hasil\s+(pengujian|analisis|uji)",
    "semua_penanda_terdaftar": None,
}


def muat_preset(nama):
    jalan = nama if os.path.isabs(nama) else os.path.join(DIR_PRESET, nama + ".json")
    if not jalan.endswith(".json"):
        jalan += ".json"
    if not os.path.exists(jalan):
        sys.exit(f"ERROR: preset tidak ditemukan: {jalan}\n"
                 f"Preset tersedia: {', '.join(daftar_preset())}")
    with open(jalan, "r", encoding="utf-8") as fh:
        return jalan, json.load(fh)


def daftar_preset():
    return sorted(os.path.splitext(f)[0] for f in os.listdir(DIR_PRESET)
                  if f.endswith(".json"))


def format_nilai(v):
    """Rapi nilai preset: dict margin jadi 'atas 4 cm / bawah 3 cm / ...'."""
    if isinstance(v, dict):
        return " / ".join(f"{k} {val}" for k, val in v.items())
    return str(v)


def sumber_preset(preset):
    """Ringkasan provenance; None bila preset lama belum punya field `sumber`."""
    s = preset.get("sumber")
    if not s:
        return "tidak tercatat (preset lama — perlakukan sebagai konvensi umum)"
    st = s.get("status")
    label = {"pedoman-resmi": "PEDOMAN RESMI",
             "konvensi-umum": "KONVENSI UMUM (belum diverifikasi)"}.get(st, st or "?")
    baris = [f"status    : {label}"]
    for kunci, nama in (("dokumen", "dokumen  "), ("scope", "cakupan  "),
                        ("tahun", "tahun    "), ("url", "url      ")):
        if s.get(kunci):
            baris.append(f"{nama}: {s[kunci]}")
    if s.get("catatan"):
        baris.append(f"catatan   : {s['catatan']}")
    return "\n".join("  " + b for b in baris)


def cek_naskah(teks, preset, lengkap=False):
    """Cek subbab wajib + penanda cek khusus terhadap isi naskah."""
    findings = []
    rendah = teks.lower()
    marker_teks = set(re.findall(r"\[(L-\d+|P-\d+|D:[^\]]+|U)\]", teks))
    pustaka = ""
    m = re.search(r"^#*\s*daftar\s+(pustaka|referensi)", teks, re.I | re.M)
    if m:
        pustaka = teks[m.start():]
    marker_pustaka = set(re.findall(r"\[(L-\d+|P-\d+)\]", pustaka))

    for bagian in preset.get("struktur", []):
        if not bagian.get("wajib", True):
            continue
        judul = bagian["judul"]
        if bagian.get("wadah"):
            # wadah (halaman depan / bagian akhir) tidak punya judul bab sendiri
            pass
        else:
            kunci = judul.replace("BAB I", "bab\\s+i").replace("BAB II", "bab\\s+ii") \
                        .replace("BAB III", "bab\\s+iii")
            if not re.search(kunci, rendah, re.I):
                findings.append(("galat", bagian["id"], f"Bagian wajib '{judul}' tidak ada."))
        for sub in bagian.get("subbab", []):
            if not sub.get("wajib", True):
                continue
            if bagian.get("wadah") and not lengkap:
                # halaman depan dan bagian akhir sering menjadi berkas terpisah;
                #secara default hanya badan naskah proposal (BAB I-III) yang diperiksa
                continue
            if not re.search(sub["judul"], rendah, re.I):
                findings.append(("galat", bagian["id"] + "/" + sub["judul"],
                                 f"Subbab wajib '{sub['judul']}' tidak ada di '{judul}'."))
            for kunci_cek in sub.get("cek", []):
                pola = CEK.get(kunci_cek)
                if pola and not re.search(pola, teks, re.I):
                    findings.append(("peringatan", bagian["id"] + "/" + sub["judul"],
                                     f"Isi '{kunci_cek}' belum terdeteksi pada "
                                     f"'{sub['judul']}'."))
    # penanda sumber
    if pustaka:
        for pen in sorted(marker_teks - marker_pustaka):
            if pen.startswith(("L-", "P-")):
                findings.append(("galat", "pustaka", f"Penanda [{pen}] tidak ada di Daftar Pustaka."))
    elif marker_teks:
        findings.append(("galat", "pustaka", "Penanda sumber dipakai tetapi Daftar Pustaka tidak ada."))
    return findings


def buat_kerangka(preset, judul, nama, nim, pembimbing, tahun):
    out = [f"# PROPOSAL PENELITIAN — {preset['kampus']} ({preset['singkat']})", ""]
    out += ["<!--", "  Kerangka awal. Hapus blok instruksi ini setelah naskah selesai (build_docx.sh --clean).",
            f"  Preset: {preset['kampus']} | Gaya: {preset.get('sitasi') or 'belum ditentukan'}",
            f"  {preset.get('verifikasi', '')}", "-->", ""]
    out += ["---", "", f"**Judul:** {judul}", "",
            f"**Nama:** {nama}  ", f"**NIM:** {nim}  ",
            f"**Pembimbing:** {pembimbing}  ",
            f"**Program Studi:** Tulis program studi  ", f"**Fakultas:** Tulis fakultas  ",
            f"**Tahun:** {tahun}", "", "---", ""]
    g = preset.get("gaya_dokumen", {})
    if g:
        out += ["> **Ketentuan dokumen dari preset**", ">"]
        for k, v in g.items():
            out.append(f"> - {k.replace('_', ' ')}: {format_nilai(v)}")
        out.append(">")
        out.append("> Sumber angka: " + preset.get("verifikasi", "belum dicatat."))
        out.append("")
    for bagian in preset.get("struktur", []):
        if not bagian.get("wajib", True):
            continue
        out += [f"# {bagian['judul']}", ""]
        if bagian.get("catatan"):
            out += [f"<!-- {bagian['catatan']} -->", ""]
        for sub in bagian.get("subbab", []):
            out.append(f"## {sub['judul']}")
            if sub.get("catatan"):
                out.append(f"<!-- {sub['catatan']} -->")
            if sub.get("cek"):
                out.append(f"<!-- wajib ada: {', '.join(sub['cek'])} -->")
            out += ["", "[Tulis di sini.]", ""]
    out += ["---", "",
            "<!-- Penanda sumber: [L-n] literatur lokal, [P-n] publikasi online, "
            "[U] data umum, [D:kolom] kolom dataset, (inferensi) kesimpulan penulis -->", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Terapkan preset template kampus")
    sub = ap.add_subparsers(dest="perintah", required=True)

    sub.add_parser("list", help="tampilkan preset yang tersedia")

    p_show = sub.add_parser("show", help="tampilkan ringkasan preset")
    p_show.add_argument("preset")

    p_init = sub.add_parser("init", help="buat kerangka proposal dari preset")
    p_init.add_argument("preset")
    p_init.add_argument("-o", "--out", default="proposal.md")
    p_init.add_argument("--judul", default="[Judul penelitian]")
    p_init.add_argument("--nama", default="[Nama lengkap]")
    p_init.add_argument("--nim", default="[NIM]")
    p_init.add_argument("--pembimbing", default="[Nama pembimbing]")
    p_init.add_argument("--tahun", default="[Tahun]")

    p_check = sub.add_parser("check", help="cek naskah terhadap preset")
    p_check.add_argument("preset")
    p_check.add_argument("naskah")
    p_check.add_argument("--json")
    p_check.add_argument("--lengkap", action="store_true",
                         help="periksa juga halaman depan dan bagian akhir")

    p_new = sub.add_parser("new-custom", help="salin kerangka custom.json")
    p_new.add_argument("-o", "--out", default="campus_templates/institusi_saya.json")

    args = ap.parse_args()

    if args.perintah == "list":
        for nama in daftar_preset():
            _, isi = muat_preset(nama)
            st = (isi.get("sumber") or {}).get("status")
            tanda = {"pedoman-resmi": " [resmi]", "konvensi-umum": " [konvensi]"}.get(st, "")
            print(f"{nama:<14} {isi['kampus']}  (sitasi: {isi.get('sitasi') or '-'}){tanda}")
        print("\n[resmi]    = angka format dari dokumen resmi (lihat `show <preset>` untuk sumber)")
        print("[konvensi] = BELUM diverifikasi ke pedoman resmi; wajib dicocokkan manual")
        return 0

    if args.perintah == "new-custom":
        sumber = os.path.join(DIR_PRESET, "custom.json")
        with open(sumber, "r", encoding="utf-8") as fh:
            isi = json.load(fh)
        if os.path.exists(args.out):
            sys.exit(f"ERROR: {args.out} sudah ada; hapus atau pilih nama lain.")
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(isi, fh, ensure_ascii=False, indent=2)
        print(f"Tulis: {args.out}\nIsi seluruh field kosong dari pedoman resmi kampus Anda.")
        return 0

    _, preset = muat_preset(args.preset)

    if args.perintah == "show":
        print(f"{preset['kampus']} ({preset['singkat']})")
        print(f"Sitasi   : {preset.get('sitasi') or 'belum ditentukan'}")
        print("Sumber   :")
        print(sumber_preset(preset))
        print(f"Verifikasi: {preset.get('verifikasi', '-')}")
        g = preset.get("gaya_dokumen", {})
        for k, v in g.items():
            print(f"  {k.replace('_', ' '):<18}: {format_nilai(v)}")
        print("\nKelengkapan wajib:")
        for item in preset.get("kelengkapan", []):
            print(f"  - {item}")
        print("\nStruktur:")
        for b in preset.get("struktur", []):
            flag = "wajib" if b.get("wajib", True) else "opsional"
            print(f"  [{flag}] {b['judul']}")
            for s in b.get("subbab", []):
                print(f"      - {s['judul']}"
                      + (f"  (cek: {', '.join(s['cek'])})" if s.get("cek") else ""))
        return 0

    if args.perintah == "init":
        isi = buat_kerangka(preset, args.judul, args.nama, args.nim,
                            args.pembimbing, args.tahun)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(isi)
        print(f"Tulis: {args.out}")
        print(f"Lanjutkan: isi subbab, jalankan scripts/proposal_doctor.py, "
              f"lalu scripts/build_docx.sh {args.out} --toc --clean")
        return 0

    if args.perintah == "check":
        if not os.path.exists(args.naskah):
            sys.exit(f"ERROR: naskah tidak ditemukan: {args.naskah}")
        with open(args.naskah, "r", encoding="utf-8", errors="replace") as fh:
            teks = fh.read()
        findings = cek_naskah(teks, preset, args.lengkap)
        for level, kode, pesan in findings:
            print(f"[{'GALAT' if level == 'galat' else 'WARN'}] {kode}: {pesan}")
        galat = sum(1 for f in findings if f[0] == "galat")
        print(f"\nPreset {args.preset}: {galat} galat, {len(findings) - galat} peringatan.")
        if args.json:
            with open(args.json, "w", encoding="utf-8") as fh:
                json.dump({"preset": args.preset, "naskah": args.naskah,
                           "galat": galat, "findings":
                           [{"level": a, "kode": b, "pesan": c} for a, b, c in findings]},
                          fh, ensure_ascii=False, indent=2)
            print(f"Tulis: {args.json}", file=sys.stderr)
        return 1 if galat else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
