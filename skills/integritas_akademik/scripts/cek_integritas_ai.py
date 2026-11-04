#!/usr/bin/env python3
"""Periksa integritas penggunaan AI pada naskah skripsi.

Pemakaian:
    python3 cek_integritas_ai.py naskah.md
    python3 cek_integritas_ai.py skripsi.docx --profil profil-kampus.yaml --ketat
    python3 cek_integritas_ai.py naskah.md --json laporan.json

Yang diperiksa:
  1. Pernyataan penggunaan AI ada (heading yang memuat istilah AI dan kata
     pernyataan/penggunaan/transparansi/acknowledgment/deklarasi).
  2. Pernyataan memuat tiga unsur: alat, tujuan/bagian, verifikasi oleh penulis.
     Bentuk "tidak menggunakan AI" diterima tanpa pemeriksaan unsur.
  3. Alat AI tidak dicantumkan sebagai penulis/pengarang.
  4. Artefak chatbot yang tertinggal di naskah.

Sikap profil (`integritas.pernyataan_ai`):
    wajib        pernyataan hilang = galat
    dianjurkan   pernyataan hilang = peringatan (juga bila kunci tidak ada)
    tidak_diatur pernyataan hilang = catatan informasi saja

PEMERIKSA POLA, bukan vonis. "Tidak ada temuan" tidak membuktikan naskah bebas
dari AI, dan pemeriksa tidak menilai kejujuran isi pernyataan.

Kode keluar:
    0  lulus (peringatan boleh ada, kecuali --ketat)
    1  ada galat (atau peringatan pada --ketat)
    2  berkas/profil tidak terbaca
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

ISTILAH_AI = (r"(kecerdasan\s+buatan|\bAI\b|\bA\.I\.|generative\s+ai|\bgenai\b|"
              r"\bLLM\b|chatgpt|claude|gemini|copilot|perplexity|deepseek|"
              r"\bgrok\b|llama)")
KATA_PERNYATAAN = r"(pernyataan|deklarasi|transparansi|keterbukaan|acknowledg|penggunaan|pemanfaatan)"

ALAT = (r"(chatgpt|gpt-?\d|openai|claude|anthropic|gemini|bard|copilot|perplexity|"
        r"deepseek|grok|llama|mistral|grammarly|quillbot|notebooklm|deepl|scispace|"
        r"elicit|consensus|scite|undermind|kimi|qwen)")
TUJUAN = (r"(penyuntingan|menyunting|parafras|menerjemah|terjemah|brainstorm|"
          r"gagasan|kerangka|outline|tata\s+bahasa|ejaan|merangkum|ringkas|"
          r"analisis\s+data|pengolahan\s+data|\bkode\b|pemrograman|pencarian\s+literatur|"
          r"bab\s+[ivx\d]+|sub\s?bab|bagian\s+\w+|diterjemahkan|proofread|editing|"
          r"grammar|summar|translat)")
VERIFIKASI = (r"(diverifikasi|verifikasi|diperiksa|memeriksa|dicek|dikonfirmasi|"
              r"ditinjau|disunting\s+ulang|bertanggung\s*jawab|tanggung\s*jawab|"
              r"verified|reviewed|responsib)")
TIDAK_PAKAI = (r"tidak\s+(?:menggunakan|memakai|memanfaatkan)\s+[^.\n]{0,80}?"
               r"(?:kecerdasan\s+buatan|\bAI\b|generative|chatgpt)|"
               r"(?:did\s+not|no)\s+use[d]?\s+[^.\n]{0,60}?(?:\bAI\b|generative)")

PENULIS_AI = (r"^\s*(?:penulis|pengarang|oleh|disusun\s+oleh|diajukan\s+oleh|author|by)"
              r"\s*[:：]\s*[^\n]{0,60}?\b(chatgpt|claude|gemini|copilot|perplexity|"
              r"deepseek|openai|anthropic|\bAI\b)\b")

ARTEFAK = [
    (r"sebagai\s+model\s+bahasa", "frasa chatbot 'sebagai model bahasa'"),
    (r"as\s+an\s+ai(?:\s+language)?\s+model", "frasa chatbot 'as an AI language model'"),
    (r"saya\s+adalah\s+(?:model|asisten)\s+(?:bahasa|ai)", "frasa chatbot 'saya adalah model/asisten'"),
    (r"semoga\s+(?:jawaban|penjelasan)\s+ini\s+membantu", "penutup chatbot 'semoga ... membantu'"),
    (r"tentu[,!]?\s+berikut\s+(?:adalah|ini)", "pembuka chatbot 'Tentu, berikut ...'"),
    (r"i\s+hope\s+this\s+helps", "penutup chatbot 'I hope this helps'"),
    (r"here(?:'s|\s+is)\s+(?:a|the)\s+(?:revised|draft|rewritten)", "pembuka chatbot 'Here is the revised ...'"),
    (r"utm_source=chatgpt", "tautan membawa parameter utm_source=chatgpt.com"),
    (r"oaicite|contentreference\[", "penanda sitasi internal chatbot (oaicite/contentReference)"),
    (r"\[citation\s+needed\]", "penanda '[citation needed]' tertinggal"),
]


def baca(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            sys.exit("GAGAL: butuh python-docx untuk .docx (pip install python-docx)")
        baris = []
        for p in Document(path).paragraphs:
            teks = p.text.strip()
            if not teks:
                continue
            gaya = (p.style.name or "").lower()
            m = re.match(r"heading (\d)", gaya)
            lvl = int(m.group(1)) if m else (1 if gaya in ("title", "judul") else 0)
            baris.append(("#" * lvl + " " + teks) if lvl else teks)
        return "\n".join(baris)
    if ext == ".pdf":
        try:
            return subprocess.run(["pdftotext", "-layout", path, "-"], check=True,
                                  capture_output=True, text=True).stdout
        except (OSError, subprocess.CalledProcessError) as e:
            sys.exit(f"GAGAL: pdftotext tidak bisa membaca PDF ({e})")
    with open(path, encoding="utf-8") as f:
        return f.read()


def muat_sikap(profil_path: str | None) -> str | None:
    if not profil_path:
        return None
    try:
        import yaml
        with open(profil_path, encoding="utf-8") as f:
            p = yaml.safe_load(f) or {}
    except Exception as e:  # noqa: BLE001
        sys.exit(f"GAGAL: profil tidak terbaca: {e}")
    nilai = (p.get("integritas") or {}).get("pernyataan_ai")
    return str(nilai).strip().lower() if nilai else None


def terlihat_heading(baris: str) -> bool:
    s = baris.strip()
    if not s:
        return False
    if s.startswith("#"):
        return True
    return len(s) <= 100 and not s.endswith((".", ",", ";")) and (
        s.isupper() or re.match(r"^(?:\d+(?:\.\d+)*\.?\s+)?[A-Z]", s) is not None)


def cari_pernyataan(teks: str):
    """Kembalikan (nomor_baris, blok) untuk heading pernyataan AI pertama, atau None."""
    baris = teks.splitlines()
    for i, b in enumerate(baris):
        if not terlihat_heading(b):
            continue
        if re.search(ISTILAH_AI, b, re.I) and re.search(KATA_PERNYATAAN, b, re.I):
            blok = []
            for j in range(i + 1, min(i + 41, len(baris))):
                if baris[j].lstrip().startswith("#") and blok:
                    break
                blok.append(baris[j])
            return i + 1, "\n".join(blok)
    return None


def periksa(teks: str, sikap: str | None):
    galat, peringatan, info = [], [], []

    ketemu = cari_pernyataan(teks)
    if ketemu is None:
        pesan = ("tidak ada bagian 'Pernyataan Penggunaan AI'. Bila AI dipakai, "
                 "ungkapkan; bila tidak sama sekali, nyatakan itu "
                 "(templat: skills/integritas_akademik/references/pernyataan-ai.md)")
        if sikap == "wajib":
            galat.append("pernyataan: " + pesan + " — profil kampus mewajibkan")
        elif sikap == "tidak_diatur":
            info.append("pernyataan: tidak ada; profil menyatakan kampus tidak mengatur")
        else:
            peringatan.append("pernyataan: " + pesan)
    else:
        no, blok = ketemu
        info.append(f"pernyataan ditemukan di baris {no}")
        if re.search(TIDAK_PAKAI, blok, re.I):
            info.append("pernyataan berbentuk 'tidak menggunakan AI' — unsur tidak diperiksa")
        else:
            if not re.search(ALAT, blok, re.I):
                peringatan.append(f"pernyataan (baris {no}): nama alat AI tidak disebut")
            if not re.search(TUJUAN, blok, re.I):
                peringatan.append(f"pernyataan (baris {no}): tujuan/bagian naskah yang dibantu tidak disebut")
            if not re.search(VERIFIKASI, blok, re.I):
                peringatan.append(f"pernyataan (baris {no}): tidak ada penegasan bahwa penulis memverifikasi keluaran")
            if re.search(r"\[[^\]\n]{2,80}\]", blok):
                peringatan.append(f"pernyataan (baris {no}): masih ada penanda [..] yang belum diisi")

    for m in re.finditer(PENULIS_AI, teks, re.I | re.M):
        no = teks.count("\n", 0, m.start()) + 1
        galat.append(f"baris {no}: alat AI tercantum di kolom penulis/pengarang — "
                     f"AI tidak boleh menjadi penulis ({m.group(0).strip()[:70]})")

    for pola, label in ARTEFAK:
        for m in re.finditer(pola, teks, re.I):
            no = teks.count("\n", 0, m.start()) + 1
            peringatan.append(f"baris {no}: artefak chatbot — {label}")
    return galat, peringatan, info


def main() -> int:
    ap = argparse.ArgumentParser(description="Periksa integritas penggunaan AI pada naskah.")
    ap.add_argument("naskah")
    ap.add_argument("--profil", help="profil-kampus.yaml (membaca integritas.pernyataan_ai)")
    ap.add_argument("--ketat", action="store_true", help="peringatan dihitung gagal")
    ap.add_argument("--json", help="tulis laporan JSON ke berkas ini")
    a = ap.parse_args()

    if not os.path.isfile(a.naskah):
        print(f"GAGAL: naskah tidak ada: {a.naskah}", file=sys.stderr)
        return 2
    sikap = muat_sikap(a.profil)
    if sikap not in (None, "wajib", "dianjurkan", "tidak_diatur"):
        print(f"GAGAL: integritas.pernyataan_ai tidak dikenal: {sikap!r} "
              "(pakai wajib | dianjurkan | tidak_diatur)", file=sys.stderr)
        return 2

    galat, peringatan, info = periksa(baca(a.naskah), sikap)
    for x in info:
        print(f"  info       {x}")
    for x in peringatan:
        print(f"  PERINGATAN {x}")
    for x in galat:
        print(f"  GALAT      {x}")
    print(f"\nRingkasan: {len(galat)} galat, {len(peringatan)} peringatan")
    print("Catatan: pemeriksa pola; tidak membuktikan ada/tidaknya AI dalam naskah.")

    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"galat": galat, "peringatan": peringatan, "info": info,
                       "sikap_profil": sikap}, f, ensure_ascii=False, indent=2)
    return 1 if galat or (a.ketat and peringatan) else 0


if __name__ == "__main__":
    sys.exit(main())
