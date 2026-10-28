#!/usr/bin/env bash
# Uji skill format_kampus: generator template -> auditor -> daftar isi.
# Jalankan dari folder skill:
#   bash tests/run_tests.sh
#
# Catatan: buat_daftar_isi.py dan audit_halaman.py butuh alat sistem
# (soffice, poppler-utils). Bila tidak ada, langkah itu DILEWATI dengan
# keterangan, bukan dihitung gagal — skill tetap bisa dipakai untuk
# generator + auditor.
set -uo pipefail

PY="${PYTHON:-python3}"
cd "$(dirname "$0")/.." || exit 2

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

gagal=0
lewat=0
cek() {
    local nama="$1"; shift
    if "$@" >/tmp/fk.out 2>&1; then
        echo "LULUS $nama"
    else
        echo "GAGAL $nama"
        sed 's/^/      /' /tmp/fk.out | head -14
        gagal=$((gagal + 1))
    fi
}
cek_tolak() {
    local nama="$1"; shift
    if "$@" >/tmp/fk.out 2>&1; then
        echo "GAGAL $nama (harus exit bukan-0)"
        gagal=$((gagal + 1))
    else
        echo "LULUS $nama"
    fi
}
# Skrip shell dipanggil dengan bash; "$@" polos akan memakai $PY dan gagal.
# Bungkus supaya "cek ... bash skrip.sh" tidak salah tafsir.
cek_sh() {
    local nama="$1"; shift
    if bash "$@" >/tmp/fk.out 2>&1; then
        echo "LULUS $nama"
    else
        echo "GAGAL $nama"
        sed 's/^/      /' /tmp/fk.out | head -14
        gagal=$((gagal + 1))
    fi
}
cek_sh_tolak() {
    local nama="$1"; shift
    if bash "$@" >/tmp/fk.out 2>&1; then
        echo "GAGAL $nama (harus exit bukan-0)"
        gagal=$((gagal + 1))
    else
        echo "LULUS $nama"
    fi
}
# Cari skrip berdasarkan ekstensi: .sh -> bash, lainnya -> $PY
skrip() {
    local f="$1"; shift
    case "$f" in
        *.sh) bash "$f" "$@" ;;
        *)    "$PY" "$f" "$@" ;;
    esac
}
cek_isi() {
    local nama="$1" pola="$2"
    if grep -qi -- "$pola" /tmp/fk.out; then
        echo "LULUS $nama"
    else
        echo "GAGAL $nama (pola '$pola' tidak muncul)"
        gagal=$((gagal + 1))
    fi
}
lewatkan() {
    echo "LEWAT $1 — $2"
    lewat=$((lewat + 1))
}

echo "== format_kampus: uji generator + auditor =="

PROFIL="presets/universitas-contoh.yaml"
cek "preset contoh ada" test -f "$PROFIL"

# semua skrip punya --help valid dan menolak tanpa argumen
for s in audit_docx audit_halaman audit_rapi buat_daftar_isi buat_template_docx \
         periksa_pustaka periksa_sistematika periksa_ringkasan \
         periksa_tabel_gambar periksa_penomoran; do
    cek "help valid: $s" $PY "scripts/$s.py" --help
    cek_tolak "$s menolak pemanggilan tanpa argumen" $PY "scripts/$s.py"
done

# 1. generator
cek "generator membuat template DOCX" \
    $PY scripts/buat_template_docx.py "$PROFIL" "$TMP/template.docx"
cek "template tercipta" test -s "$TMP/template.docx"

# 2. template hasil generator harus lolos audit profil
cek "audit_docx lulus pada template hasil generator" \
    $PY scripts/audit_docx.py "$TMP/template.docx" "$PROFIL"
cek_isi "audit_docx memeriksa font tema" "font tema"

# 2b. preset nyata (ars-fti) harus menghasilkan template yang lolos audit
cek "generator memakai preset ars-fti" \
    $PY scripts/buat_template_docx.py presets/ars-fti.yaml "$TMP/ars.docx"
cek "audit_docx lulus pada preset ars-fti" \
    $PY scripts/audit_docx.py "$TMP/ars.docx" presets/ars-fti.yaml
cek_isi "preset ars-fti memakai spasi 2" "2.0"

# 3. kerapian
cek "audit_rapi lulus pada template" \
    $PY scripts/audit_rapi.py "$TMP/template.docx"

# 4. auditor menolak masukan salah
printf 'ini bukan docx' > "$TMP/palsu.docx"
cek_tolak "audit_docx menolak berkas bukan DOCX" \
    $PY scripts/audit_docx.py "$TMP/palsu.docx" "$PROFIL"
cek_tolak "audit_docx menolak berkas tidak ada" \
    $PY scripts/audit_docx.py "$TMP/tidak_ada.docx" "$PROFIL"
cek_tolak "audit_rapi menolak berkas bukan DOCX" \
    $PY scripts/audit_rapi.py "$TMP/palsu.docx"

# 5. profil rusak
printf 'ini: [bukan yaml valid\n' > "$TMP/rusak.yaml"
cek_tolak "generator menolak profil YAML rusak" \
    $PY scripts/buat_template_docx.py "$TMP/rusak.yaml" "$TMP/x.docx"
cek_tolak "generator menolak profil tidak ada" \
    $PY scripts/buat_template_docx.py "$TMP/nope.yaml" "$TMP/x.docx"

# 6. periksa_pustaka — ketentuan 4.10
cek "help valid: periksa_pustaka" $PY scripts/periksa_pustaka.py --help
cek_tolak "periksa_pustaka menolak tanpa argumen" $PY scripts/periksa_pustaka.py
cek "periksa_pustaka lulus pada naskah bersih" \
    $PY scripts/periksa_pustaka.py tests/naskah_pustaka_bersih.md \
    --tahun-acuan 2026 --min-jurnal 2
cek_tolak "periksa_pustaka menolak naskah buruk" \
    $PY scripts/periksa_pustaka.py tests/naskah_pustaka_buruk.md --tahun-acuan 2026
cek_isi "periksa_pustaka menangkap et al" "pakai_etal"
cek_isi "periksa_pustaka menangkap gelar akademik" "ada_gelar"
cek_isi "periksa_pustaka menangkap sumber blogspot" "sumber_blogspot"
cek_isi "periksa_pustaka menangkap usia referensi" "referensi_terlalu_tua"
cek_isi "periksa_pustaka menangkap web tanpa tanggal unduh" "web_tanpa_tanggal_unduh"
cek_isi "periksa_pustaka menangkap sitasi tanpa entri" "sitasi_tanpa_entri"

# 7. periksa_sistematika — sistematika kampus
cek "help valid: periksa_sistematika" $PY scripts/periksa_sistematika.py --help
cek_tolak "periksa_sistematika menolak tanpa argumen" $PY scripts/periksa_sistematika.py
cek "preset ars-fti ada" test -f presets/ars-fti.yaml
cek "periksa_sistematika lulus pada naskah patuh" \
    $PY scripts/periksa_sistematika.py tests/naskah_sistematika_baik.md \
    presets/ars-fti.yaml --abaikan-opsional
cek_tolak "periksa_sistematika menolak naskah menyimpang" \
    $PY scripts/periksa_sistematika.py tests/naskah_sistematika_buruk.md \
    presets/ars-fti.yaml --abaikan-opsional
cek_isi "periksa_sistematika menangkap subbab hilang" "subbab_hilang"
cek_isi "periksa_sistematika menangkap urutan bagian awal" "awal_urutan"
cek_isi "periksa_sistematika menangkap caption angka Arab" "caption_angka_arab"
cek_isi "periksa_sistematika menangkap penomoran tanpa titik" "penomoran_tanpa_titik"

# 8. periksa_ringkasan — ringkasan, abstract, kata kunci
cek "help valid: periksa_ringkasan" $PY scripts/periksa_ringkasan.py --help
cek_tolak "periksa_ringkasan menolak tanpa argumen" $PY scripts/periksa_ringkasan.py
cek "periksa_ringkasan lulus pada ringkasan patuh" \
    $PY scripts/periksa_ringkasan.py tests/naskah_ringkasan_baik.md presets/ars-fti.yaml
cek_tolak "periksa_ringkasan menolak ringkasan menyimpang" \
    $PY scripts/periksa_ringkasan.py tests/naskah_ringkasan_buruk.md presets/ars-fti.yaml
cek_isi "periksa_ringkasan menangkap ringkasan pendek" "ringkasan_pendek"
cek_isi "periksa_ringkasan menangkap kata kunci berlebih" "kata_kunci_berlebih"
cek_isi "periksa_ringkasan menangkap unsur kurang" "ringkasan_unsur_kurang"

# 9. gate_naskah — satu perintah untuk semua gerbang isi
cek "help valid: gate_naskah" skrip scripts/gate_naskah.sh --help
cek_tolak "gate_naskah menolak tanpa argumen" skrip scripts/gate_naskah.sh
cek "gate_naskah lulus dengan batas jurnal ditimpa" \
    skrip scripts/gate_naskah.sh tests/naskah_fti_lengkap.md presets/ars-fti.yaml --min-jurnal 3
cek_tolak "gate_naskah menolak naskah menyimpang" \
    skrip scripts/gate_naskah.sh tests/naskah_sistematika_buruk.md presets/ars-fti.yaml \
    --min-jurnal 1
cek_isi "gate_naskah melaporkan sistematika" "sistematika"
cek_isi "gate_naskah melaporkan pustaka kosong" "pustaka_kosong"
# heading ada tapi isi kosong -> ringkasan_kosong (beda dari ringkasan_hilang)
skrip scripts/gate_naskah.sh tests/naskah_ringkasan_kosong.md \
    presets/ars-fti.yaml --min-jurnal 1 >/tmp/fk_rk.out 2>&1
if grep -q "ringkasan_kosong" /tmp/fk_rk.out; then
    echo "LULUS gate_naskah membedakan ringkasan kosong dari ringkasan hilang"
else
    echo "GAGAL gate_naskah membedakan ringkasan kosong dari ringkasan hilang"
    sed 's/^/      /' /tmp/fk_rk.out | head -10
    gagal=$((gagal + 1))
fi
cek_isi "gate_naskah melaporkan caption angka Arab" "caption_angka_arab"
cek_isi "gate_naskah melaporkan subbab hilang" "subbab_hilang"
# batas min_jurnal harus dibaca dari profil, bukan angka kembar di dua tempat
$PY scripts/periksa_pustaka.py tests/naskah_fti_lengkap.md \
    >/tmp/fk_j.out 2>&1
# batas harus dibaca dari default profil (10), bukan angka kembar di tes
if grep -q "minimal 10" /tmp/fk_j.out; then
    echo "LULUS periksa_pustaka memakai batas bawaan 10"
else
    echo "GAGAL periksa_pustaka memakai batas bawaan 10"
    sed 's/^/      /' /tmp/fk_j.out | head -6
    gagal=$((gagal + 1))
fi
# --ketat: satu peringatan pun menggagalkan
cek_tolak "gate_naskah --ketat menggagalkan peringatan" \
    skrip scripts/gate_naskah.sh tests/naskah_fti_lengkap.md presets/ars-fti.yaml \
    --min-jurnal 3 --ketat

# 10. periksa_tabel_gambar — caption, urutan, rujukan
cek "help valid: periksa_tabel_gambar" $PY scripts/periksa_tabel_gambar.py --help
cek_tolak "periksa_tabel_gambar menolak tanpa argumen" $PY scripts/periksa_tabel_gambar.py
cek "periksa_tabel_gambar lulus pada caption patuh" \
    $PY scripts/periksa_tabel_gambar.py tests/naskah_caption_baik.md presets/ars-fti.yaml
cek_tolak "periksa_tabel_gambar menolak caption menyimpang" \
    $PY scripts/periksa_tabel_gambar.py tests/naskah_caption_buruk.md presets/ars-fti.yaml
cek_isi "periksa_tabel_gambar menangkap caption angka Arab" "caption_angka_arab"
cek_isi "periksa_tabel_gambar menangkap tabel tanpa caption" "tabel_tanpa_caption"
cek_isi "periksa_tabel_gambar menangkap objek tak dirujuk" "objek_tak_dirujuk"
cek_isi "periksa_tabel_gambar menangkap caption tanpa sumber" "caption_tanpa_sumber"
cek_isi "periksa_tabel_gambar menangkap urutan nomor" "urutan_tabel_salah"

# 11. periksa_penomoran — nomor subbab dari numbering.xml
cek "help valid: periksa_penomoran" $PY scripts/periksa_penomoran.py --help
cek_tolak "periksa_penomoran menolak tanpa argumen" $PY scripts/periksa_penomoran.py
cek_tolak "periksa_penomoran menolak berkas bukan docx" \
    $PY scripts/periksa_penomoran.py tests/naskah_caption_baik.md presets/ars-fti.yaml
cek_tolak "periksa_penomoran menangkap nomor dirusak" \
    $PY scripts/periksa_penomoran.py tests/docx_nomor_salah.docx presets/ars-fti.yaml
cek_isi "periksa_penomoran menangkap titik penutup hilang" "nomor_tanpa_titik"
cek_isi "periksa_penomoran menangkap awalan bab salah" "awalan_bab_salah"
# template sendiri harus lulus (tidak ada galat palsu)
$PY scripts/buat_template_docx.py presets/ars-fti.yaml "$TMP/ars2.docx" >/dev/null 2>&1
cek "periksa_penomoran lulus pada template buatan sendiri" \
    $PY scripts/periksa_penomoran.py "$TMP/ars2.docx" presets/ars-fti.yaml

# 11b. gate pada DOCX: jalur periksa_penomoran ikut berjalan
skrip scripts/gate_naskah.sh tests/docx_nomor_salah.docx presets/ars-fti.yaml \
    >/tmp/fk_gd.out 2>&1
if grep -q "X penomoran" /tmp/fk_gd.out; then
    echo "LULUS gate_naskah menjalankan penomoran untuk .docx"
else
    echo "GAGAL gate_naskah menjalankan penomoran untuk .docx"
    sed 's/^/      /' /tmp/fk_gd.out | head -12
    gagal=$((gagal + 1))
fi
if grep -q "dilewati (bukan .docx" /tmp/fk_gd.out; then
    echo "GAGAL gate_naskah salah melewati penomoran pada .docx"; gagal=$((gagal + 1))
else
    echo "LULUS gate_naskah tidak melewati penomoran pada .docx"
fi

# 11c. buat_template_lengkap — kerangka utuh, bukan satu halaman
cek "help valid: buat_template_lengkap" $PY scripts/buat_template_lengkap.py --help
cek_tolak "buat_template_lengkap menolak tanpa argumen" $PY scripts/buat_template_lengkap.py
cek "buat_template_lengkap menghasilkan docx" \
    $PY scripts/buat_template_lengkap.py presets/ars-fti.yaml "$TMP/lengkap.docx"
cek "audit_docx lulus pada template lengkap" \
    $PY scripts/audit_docx.py "$TMP/lengkap.docx" presets/ars-fti.yaml
cek "audit_rapi lulus pada template lengkap" \
    $PY scripts/audit_rapi.py "$TMP/lengkap.docx"

cek "template lengkap memuat semua bagian, bab, subbab, dan tata letak benar" \
    $PY tests/uji_template_lengkap.py "$TMP/lengkap.docx" presets/ars-fti.yaml
cek "audit_halaman lulus pada render template lengkap" true

# 12. daftar isi — butuh soffice
if command -v soffice >/dev/null 2>&1; then
    # buat_daftar_isi mencari heading BAB; template 1 halaman tidak punya.
    # Pakai template lengkap yang memang berisi BAB I..V.
    cek "buat_daftar_isi berjalan" \
        $PY scripts/buat_daftar_isi.py "$TMP/lengkap.docx" "$PROFIL"
    cek "hasil daftar isi tercipta" test -s "$TMP/lengkap.docx"
    # Nomor subbab TIDAK ada di teks paragraf (dibuat Word via numPr), jadi
    # pembuat daftar isi harus menuliskannya sendiri. Tanpa ini daftar isi
    # tampil "Latar Belakang" alih-alih "1.1. Latar Belakang".
    $PY - "$TMP/lengkap.docx" >/tmp/fk_toc.out 2>&1 <<'PYEOF'
import sys, zipfile, re
z = zipfile.ZipFile(sys.argv[1])
xml = z.read('word/document.xml').decode()
# entri TOC dibuat sebagai paragraf ber-style TOC2
teks = re.findall(r'<w:pStyle w:val="TOC2"/>.*?<w:t[^>]*>([^<]*)</w:t>', xml, re.S)
bernomor = [t for t in teks if re.match(r'^\d+\.\d+\.', t)]
print(f"entri TOC tingkat 2: {len(teks)}, bernomor: {len(bernomor)}")
print(bernomor[:4])
sys.exit(0 if teks and len(bernomor) == len(teks) else 1)
PYEOF
    if [ $? -eq 0 ]; then
        echo "LULUS daftar isi memuat nomor subbab"
    else
        echo "GAGAL daftar isi memuat nomor subbab"
        sed 's/^/      /' /tmp/fk_toc.out | head -4
        gagal=$((gagal + 1))
    fi
else
    # harus gagal dengan pesan jelas, bukan traceback
    cek_tolak "buat_daftar_isi gagal rapi tanpa soffice" \
        $PY scripts/buat_daftar_isi.py "$TMP/template.docx" "$PROFIL"
    cek_isi "pesan soffice hilang menyebut cara pasang" "apt-get install"
    lewatkan "daftar isi nyata" "soffice (LibreOffice) tidak terpasang"
fi

# 7. audit_halaman — butuh poppler
if command -v pdfinfo >/dev/null 2>&1 && command -v soffice >/dev/null 2>&1; then
    # Render nyata: template panjang (12 paragraf/subbab) supaya ada halaman
    # lanjutan — di situlah aturan "awal bab tengah bawah vs halaman lain
    # kanan atas" baru bisa diuji.
    $PY scripts/buat_template_lengkap.py presets/ars-fti.yaml "$TMP/panjang.docx" \
        --isi-paragraf 12 >/dev/null 2>&1
    ( cd "$TMP" && soffice --headless --convert-to pdf panjang.docx \
        --outdir "$TMP" >/dev/null 2>&1 )
    cek "audit_halaman lulus pada render nyata" \
        $PY scripts/audit_halaman.py "$TMP/panjang.pdf" "$PROFIL"
elif command -v pdfinfo >/dev/null 2>&1; then
    lewatkan "audit_halaman pada PDF asli" "soffice tidak terpasang (tidak bisa render)"
else
    cek_tolak "audit_halaman gagal rapi tanpa poppler" \
        $PY scripts/audit_halaman.py "$TMP/x.pdf" "$PROFIL"
    cek_isi "pesan poppler menyebut cara pasang" "poppler-utils"
    lewatkan "audit_halaman nyata" "poppler-utils tidak terpasang"
fi

echo
if [ "$gagal" -eq 0 ]; then
    echo "Ringkasan: SEMUA LULUS${lewat:+ ($lewat dilewati)}"
    exit 0
else
    echo "Ringkasan: GAGAL $gagal${lewat:+ ($lewat dilewati)}"
    exit 1
fi
