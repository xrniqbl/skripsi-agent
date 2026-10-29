#!/usr/bin/env bash
# Uji skill zotero_pustaka tanpa jaringan (jalur offline: konversi + render).
# Jalankan dari folder skill:
#   bash tests/run_tests.sh
#
# Yang diuji offline:
#   - konversi BibTeX/RIS/Zotero-JSON -> CSL-JSON, termasuk dedup DOI
#   - unescape LaTeX (\& -> &) supaya judul tidak tercetak apa adanya
#   - render APA berabjad, IEEE/Vancouver bernomor
#   - nomor sitasi COCOK dengan nomor entri (kegagalan yang paling mahal)
#   - --nama-lengkap benar-benar menghapus et al./dkk
#   - sisip_docx menaruh entri di placeholder, berurutan, dengan hanging indent
#   - pemeriksa pustaka kampus tidak menyalakan galat palsu pada entri ber-DOI
#
# Yang TIDAK diuji di sini (butuh jaringan): zotero_client.py ke api.zotero.org
# dan doi.org. Jalankan manual: python3 scripts/zotero_client.py probe
set -uo pipefail

PY="${PYTHON:-python3}"
cd "$(dirname "$0")/.." || exit 2
S="scripts"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

gagal=0
lewat=0
cek() {
    local nama="$1"; shift
    if "$@" >"$TMP/out" 2>&1; then
        echo "LULUS $nama"
    else
        echo "GAGAL $nama"
        sed 's/^/      /' "$TMP/out" | head -14
        gagal=$((gagal + 1))
    fi
}
cek_tolak() {
    local nama="$1"; shift
    if "$@" >"$TMP/out" 2>&1; then
        echo "GAGAL $nama (harus exit bukan-0)"
        gagal=$((gagal + 1))
    else
        echo "LULUS $nama"
    fi
}
cek_isi() {   # cek_isi "nama" "berkas" "pola"
    local nama="$1" berkas="$2" pola="$3"
    if grep -qF -- "$pola" "$berkas" 2>/dev/null; then
        echo "LULUS $nama"
    else
        echo "GAGAL $nama (tidak menemukan: $pola)"
        head -5 "$berkas" 2>/dev/null | sed 's/^/      /'
        gagal=$((gagal + 1))
    fi
}
cek_tidak_isi() {
    local nama="$1" berkas="$2" pola="$3"
    if grep -qF -- "$pola" "$berkas" 2>/dev/null; then
        echo "GAGAL $nama (masih ada: $pola)"
        grep -n -- "$pola" "$berkas" | head -3 | sed 's/^/      /'
        gagal=$((gagal + 1))
    else
        echo "LULUS $nama"
    fi
}

# --- bahan uji -------------------------------------------------------------
cat > "$TMP/a.bib" <<'BIB'
@article{harris2020,
  title = {Array programming with {NumPy}},
  author = {Harris, Charles R. and Millman, K. Jarrod},
  journal = {Nature}, volume={585}, number={7825}, pages={357--362}, year={2020},
  doi={10.1038/s41586-020-2649-2}
}
@book{sugiyono2019,
  title={Metode Penelitian Kuantitatif, Kualitatif, dan R\&D},
  author={Sugiyono}, publisher={Alfabeta}, address={Bandung}, year={2019}
}
BIB

cat > "$TMP/b.ris" <<'RIS'
TY  - JOUR
TI  - Deteksi Anomali Trafik Jaringan Menggunakan Autoencoder
AU  - Saputra, Iqbal
AU  - Wijaya, Andi
JO  - Jurnal Teknologi Informasi
PY  - 2021
VL  - 5
IS  - 2
SP  - 10
EP  - 20
DO  - 10.1038/s41586-020-2649-2
ER  -
RIS

cat > "$TMP/c.json" <<'JSON'
[{"itemType":"journalArticle","key":"zzz1","title":"Ketiga","creators":[{"lastName":"Zulkarnain","firstName":"Ahmad"}],"date":"2023","publicationTitle":"Jurnal X","volume":"1","pages":"1-9"}]
JSON

# --- 1. konversi -----------------------------------------------------------
cek "konversi BibTeX berjalan" \
    "$PY" "$S/konversi_pustaka.py" "$TMP/a.bib" --periksa
cek "konversi RIS berjalan" \
    "$PY" "$S/konversi_pustaka.py" "$TMP/b.ris" --periksa
cek "konversi Zotero JSON berjalan" \
    "$PY" "$S/konversi_pustaka.py" "$TMP/c.json" --periksa
cek "gabung tiga format + dedup" \
    "$PY" "$S/konversi_pustaka.py" "$TMP/a.bib" "$TMP/b.ris" "$TMP/c.json" \
    --out "$TMP/gabung.json" --gabung
cek_isi "dedup melaporkan duplikat DOI" "$TMP/gabung.json" '"duplikat": 1'
cek_isi "duplikat menyebut sebab DOI" "$TMP/gabung.json" '"sebab": "DOI"'
cek_tolak "berkas tak ada = gagal" \
    "$PY" "$S/konversi_pustaka.py" "$TMP/tidak-ada.bib" --periksa

# --- 2. render -------------------------------------------------------------
cek "render APA berjalan" \
    "$PY" "$S/render_sitasi.py" "$TMP/gabung.json" --gaya apa --out "$TMP/apa.md"
cek_isi "APA: ampersand APA 7" "$TMP/apa.md" "Harris, C. R., & Millman"
cek_isi "APA: DOI jadi tautan" "$TMP/apa.md" "https://doi.org/10.1038/s41586-020-2649-2"
cek_isi "LaTeX \\& sudah jadi &" "$TMP/apa.md" "R&D"
cek_tidak_isi "tidak ada sisa escape LaTeX" "$TMP/apa.md" 'R\&D'
# urutan abjad: Harris < Saputra < Sugiyono
awk 'NR<=8' "$TMP/apa.md" > "$TMP/apa-kepala.md"
if [ "$(grep -m1 -o 'Harris\|Saputra\|Sugiyono' "$TMP/apa-kepala.md")" = "Harris" ]; then
    echo "LULUS APA mulai dari Harris (berabjad)"
else
    echo "GAGAL APA tidak berabjad"; gagal=$((gagal + 1))
fi

cek "render IEEE berjalan" \
    "$PY" "$S/render_sitasi.py" "$TMP/gabung.json" --gaya ieee \
    --out "$TMP/ieee.md" --sitasi-out "$TMP/ieee-sitasi.json"
cek_isi "IEEE: penanda [1] ada" "$TMP/ieee.md" "[1]"
cek "render Vancouver berjalan" \
    "$PY" "$S/render_sitasi.py" "$TMP/gabung.json" --gaya vancouver --out "$TMP/van.md"

# --- 3. et al dimatikan ----------------------------------------------------
cek "render IEEE nama lengkap" \
    "$PY" "$S/render_sitasi.py" "$TMP/gabung.json" --gaya ieee \
    --nama-lengkap --out "$TMP/ieee-lengkap.md"
cek_tidak_isi "tanpa --nama-lengkap: et al. masih ada" "$TMP/ieee.md" "et al."
# Harris hanya 2 penulis, jadi et-al tak muncul di kedua versi; uji dengan
# entri 3 penulis supaya perbedaan benar-benar terlihat
cat > "$TMP/tiga.bib" <<'BIB'
@article{tiga,
  title={Uji Tiga Penulis},
  author={Satu, A. and Dua, B. and Tiga, C.},
  journal={Jurnal Uji}, year={2024}, volume={1}, pages={1--2}
}
BIB
"$PY" "$S/konversi_pustaka.py" "$TMP/tiga.bib" --out "$TMP/tiga.json" >/dev/null 2>&1
"$PY" "$S/render_sitasi.py" "$TMP/tiga.json" --gaya vancouver --out "$TMP/tiga-biasa.md" >/dev/null 2>&1
"$PY" "$S/render_sitasi.py" "$TMP/tiga.json" --gaya vancouver --nama-lengkap \
    --out "$TMP/tiga-lengkap.md" >/dev/null 2>&1
cek_isi "Vancouver 3 penulis: semua nama tertulis" "$TMP/tiga-lengkap.md" "Tiga C"
cek_tidak_isi "Vancouver 3 penulis lengkap: tanpa et al" "$TMP/tiga-lengkap.md" "et al"

# --- 4. nomor sitasi == nomor entri ---------------------------------------
"$PY" - "$TMP" <<'PYCHK'
import json, re, sys
tmp = sys.argv[1]
d = json.load(open(f"{tmp}/ieee-sitasi.json"))
daftar = open(f"{tmp}/ieee.md", encoding="utf-8").read()
# setiap sitasi "[n]" harus menunjuk entri yang memuat DOI/judul yang sama
peta = {}
for i, blok in enumerate([b for b in daftar.split("\n\n") if b.strip()], 1):
    m = re.match(r"\[(\d+)\]", blok.strip())
    if m:
        peta[int(m.group(1))] = blok
salah = []
for it in d["items"]:
    nomor = d["sitasi"][it["id"]]
    m = re.match(r"\[(\d+)\]", nomor)
    if not m:
        salah.append((it["id"], nomor, "bukan format [n]"))
        continue
    n = int(m.group(1))
    blok = peta.get(n, "")
    judul = (it.get("title") or "")[:25]
    if judul and judul not in blok:
        salah.append((it["id"], nomor, f"[{n}] bukan entri '{judul}'"))
if salah:
    print("nomor sitasi tidak cocok:", salah)
    sys.exit(1)
print(f"ok: {len(d['items'])} sitasi cocok dengan nomor entri")
PYCHK
if [ $? -eq 0 ]; then echo "LULUS nomor sitasi cocok dengan nomor entri"
else echo "GAGAL nomor sitasi tidak cocok"; gagal=$((gagal + 1)); fi

# --- 5. sisip_docx ---------------------------------------------------------
"$PY" - "$TMP" <<'PYDOCX'
import sys
from docx import Document
tmp = sys.argv[1]
d = Document()
d.add_paragraph("BAB I PENDAHULUAN")
d.add_paragraph("Klaim pertama {{cite:harris2020}} dan {{cite:sugiyono2019;zzz1}}.")
d.add_paragraph("{{DAFTAR_PUSTAKA}}")
d.save(f"{tmp}/naskah.docx")
PYDOCX
cek "sisip_docx berjalan" \
    "$PY" "$S/sisip_docx.py" "$TMP/naskah.docx" "$TMP/gabung.json" \
    --gaya apa --out "$TMP/hasil.docx" --ganti-sitasi
"$PY" - "$TMP" <<'PYCHK2'
import sys
from docx import Document
tmp = sys.argv[1]
d = Document(f"{tmp}/hasil.docx")
teks = [p.text for p in d.paragraphs]
gagal = []
# placeholder harus hilang
if any("{{DAFTAR_PUSTAKA}}" in t for t in teks):
    gagal.append("placeholder masih ada")
if any("{{cite:" in t for t in teks):
    gagal.append("penanda sitasi masih ada")
# entri pustaka harus ada sesudah paragraf sitasi, bukan sebelumnya
idx = [i for i, t in enumerate(teks) if "Harris" in t and "(2020)" in t]
if not idx:
    gagal.append("entri Harris tidak ditemukan")
else:
    if idx[0] < 2:
        gagal.append("entri pustaka muncul sebelum badan teks")
# hanging indent
p = d.paragraphs[idx[0]]
if p.paragraph_format.left_indent is None or p.paragraph_format.first_line_indent is None:
    gagal.append("hanging indent tidak diset")
elif p.paragraph_format.first_line_indent >= 0:
    gagal.append("first_line_indent tidak negatif")
# urutan abjad di dokumen
nama = [t.split(",")[0] for t in teks if t and t[0].isupper()][-3:]
if gagal:
    print("; ".join(gagal)); sys.exit(1)
print("ok: placeholder diganti, sitasi jadi, hanging indent benar")
PYCHK2
if [ $? -eq 0 ]; then echo "LULUS DOCX: placeholder + sitasi + indent"
else echo "GAGAL DOCX hasil salah"; gagal=$((gagal + 1)); fi

cek_tolak "sisip_docx menolak id sitasi yang tidak ada" \
    bash -c "'$PY' '$S/sisip_docx.py' '$TMP/naskah.docx' '$TMP/tiga.json' --gaya apa --out '$TMP/x.docx' --ganti-sitasi"

# --- 6. pemeriksa kampus tidak salah tuduh entri ber-DOI -------------------
cat > "$TMP/naskah-dp.md" <<'MD'
# DAFTAR PUSTAKA

Harris, C. R., & Millman, K. J. (2024). Array programming with NumPy. Nature, 585(7825), 357-362. https://doi.org/10.1038/s41586-020-2649-2
MD
PP="../format_kampus/scripts/periksa_pustaka.py"
if [ -f "$PP" ]; then
    "$PY" "$PP" "$TMP/naskah-dp.md" --tahun-acuan 2026 --min-jurnal 1 \
        > "$TMP/periksa.out" 2>&1 || true
    if grep -q "web_tanpa_tanggal_unduh" "$TMP/periksa.out"; then
        echo "GAGAL entri jurnal ber-DOI dituduh 'web tanpa tanggal unduh'"
        gagal=$((gagal + 1))
    else
        echo "LULUS entri jurnal ber-DOI tidak dituduh web"
    fi
else
    echo "LEWAT pemeriksa kampus tidak ditemukan di $PP"
    lewat=$((lewat + 1))
fi

# --- 6b. format sitasi kampus (Nama, Tahun:Halaman) ------------------------
cek "render format kampus" \
    "$PY" "$S/render_sitasi.py" "$TMP/gabung.json" --gaya apa \
    --format-kampus nama_tahun_halaman --halaman harris2020=357 \
    --sitasi-out "$TMP/sit-kampus.json" --out "$TMP/kampus.md"
"$PY" - "$TMP" <<'PYCHK3'
import json, sys
d = json.load(open(f"{sys.argv[1]}/sit-kampus.json"))
gagal = []
if d["sitasi"]["harris2020"] != "(Harris & Millman, 2020:357)":
    gagal.append("locator halaman tidak muncul: " + d["sitasi"]["harris2020"])
if d["sitasi"]["sugiyono2019"] != "(Sugiyono, 2019)":
    gagal.append("sitasi tanpa halaman berubah bentuk: " + d["sitasi"]["sugiyono2019"])
if gagal:
    print("; ".join(gagal)); sys.exit(1)
print("ok: (Nama, Tahun:Halaman) dan (Nama, Tahun)")
PYCHK3
if [ $? -eq 0 ]; then echo "LULUS format sitasi kampus"
else echo "GAGAL format sitasi kampus"; gagal=$((gagal + 1)); fi

cek "render format naratif" \
    "$PY" "$S/render_sitasi.py" "$TMP/gabung.json" --gaya apa \
    --format-kampus naratif --sitasi-out "$TMP/sit-naratif.json" --out "$TMP/naratif.md"
cek_isi "naratif: nama di luar kurung" "$TMP/sit-naratif.json" "Sugiyono (2019)"

# --- 6c. template kampus: sisip SETELAH heading yang sudah ada ------------
"$PY" - "$TMP" <<'PYTPL'
import sys
from docx import Document
tmp = sys.argv[1]
d = Document()
d.add_paragraph("BAB V PENUTUP")
d.add_paragraph("Daftar Pustaka")
d.add_paragraph("Daftar Riwayat Hidup")
d.save(f"{tmp}/template.docx")
PYTPL
cek "sisip ke template tanpa placeholder" \
    "$PY" "$S/sisip_docx.py" "$TMP/template.docx" "$TMP/gabung.json" \
    --gaya apa --out "$TMP/template-out.docx"
"$PY" - "$TMP" <<'PYCHK4'
import sys
from docx import Document
d = Document(f"{sys.argv[1]}/template-out.docx")
teks = [p.text for p in d.paragraphs]
gagal = []
try:
    i_head = next(i for i, t in enumerate(teks) if t.strip().lower() == "daftar pustaka")
    i_riwayat = next(i for i, t in enumerate(teks) if "riwayat hidup" in t.lower())
except StopIteration:
    print("heading tidak ditemukan"); sys.exit(1)
entri = [i for i, t in enumerate(teks) if "(2020)" in t or "(2022)" in t or "(2019)" in t]
if not entri:
    gagal.append("entri tidak disisipkan")
elif not all(i_head < i < i_riwayat for i in entri):
    gagal.append("entri tidak berada di antara heading dan bagian akhir")
if gagal:
    print("; ".join(gagal)); sys.exit(1)
print("ok: entri masuk setelah heading, sebelum bagian akhir")
PYCHK4
if [ $? -eq 0 ]; then echo "LULUS DOCX: sisip setelah heading template"
else echo "GAGAL DOCX: posisi entri salah"; gagal=$((gagal + 1)); fi

# --- 6d. judul berawalan angka tidak menghilangkan nomor -------------------
cat > "$TMP/angka.json" <<'JSON'
[{"id":"x1","type":"motion_picture","title":"1984","issued":{"date-parts":[[2000]]}},
 {"id":"x2","type":"book","title":"Zaman Baru","author":[{"family":"Saputra","given":"Iqbal"}],"issued":{"date-parts":[[2022]]}}]
JSON
cek "render judul berawalan angka" \
    "$PY" "$S/render_sitasi.py" "$TMP/angka.json" --gaya apa --out "$TMP/angka.md"
"$PY" - "$TMP" <<'PYCHK5'
import re, sys
t = open(f"{sys.argv[1]}/angka.md", encoding="utf-8").read()
n = [int(m.group(1)) for m in re.finditer(r"^(\d+)\. ", t, re.M)]
if n != list(range(1, len(n) + 1)):
    print("nomor tidak berurutan:", n); sys.exit(1)
if len(n) != 2:
    print("jumlah entri salah:", n); sys.exit(1)
print("ok: dua entri, nomor 1 dan 2 utuh")
PYCHK5
if [ $? -eq 0 ]; then echo "LULUS nomor utuh meski judul mulai angka"
else echo "GAGAL nomor bolong pada judul berangka"; gagal=$((gagal + 1)); fi

# --- 6e. dedup pustaka Zotero nyata (tanpa jaringan) -----------------------
"$PY" - "$TMP" <<'PYDUP'
import json, sys
tmp = sys.argv[1]
items = [
    {"id": "a", "type": "article-journal", "title": "Sama", "DOI": "10.1/x",
     "issued": {"date-parts": [[2020]]}},
    {"id": "b", "type": "article-journal", "title": "Sama sekali lain",
     "DOI": "https://doi.org/10.1/X", "issued": {"date-parts": [[2020]]}},
    {"id": "c", "type": "book", "title": "Buku Kembar",
     "issued": {"date-parts": [[2021]]}},
    {"id": "d", "type": "book", "title": "buku  kembar",
     "issued": {"date-parts": [[2021]]}},
    {"id": "e", "type": "book", "title": "Buku Beda Tahun",
     "issued": {"date-parts": [[2022]]}},
]
json.dump({"items": items}, open(f"{tmp}/dup.json", "w"))
PYDUP
"$PY" - "$TMP" <<'PYCHK6'
import sys, importlib.util
spec = importlib.util.spec_from_file_location("zc", "scripts/zotero_client.py")
zc = importlib.util.module_from_spec(spec); spec.loader.exec_module(zc)
import json
items = json.load(open(f"{sys.argv[1]}/dup.json"))["items"]
unik, dup = zc.dedup(items)
gagal = []
if len(unik) != 3:
    gagal.append(f"unik={len(unik)} (harus 3)")
if len(dup) != 2:
    gagal.append(f"dup={len(dup)} (harus 2)")
if not any(d["sebab"] == "DOI" for d in dup):
    gagal.append("DOI case-sensitive / prefiks URL tidak dinormalkan")
if not any(d["sebab"] == "judul+tahun" for d in dup):
    gagal.append("duplikat judul+tahun tidak terdeteksi")
if gagal:
    print("; ".join(gagal)); sys.exit(1)
print("ok: 5 -> 3 unik, 2 duplikat dilaporkan")
PYCHK6
if [ $? -eq 0 ]; then echo "LULUS dedup pustaka Zotero"
else echo "GAGAL dedup pustaka Zotero"; gagal=$((gagal + 1)); fi

# --- 7. ketahanan argumen --------------------------------------------------
cek_tolak "render menolak gaya tak dikenal" \
    "$PY" "$S/render_sitasi.py" "$TMP/gabung.json" --gaya tidak-ada
cek "daftar gaya berjalan" "$PY" "$S/render_sitasi.py" --daftar-gaya
cek_tolak "sisip_docx menolak berkas hilang" \
    "$PY" "$S/sisip_docx.py" "$TMP/tidak.docx" "$TMP/gabung.json"

echo
if [ "$gagal" -eq 0 ]; then
    echo "Ringkasan: SEMUA LULUS (${lewat} dilewati)"
    exit 0
else
    echo "Ringkasan: $gagal GAGAL (${lewat} dilewati)"
    exit 1
fi
