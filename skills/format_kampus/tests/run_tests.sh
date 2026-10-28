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
         periksa_pustaka periksa_sistematika; do
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

# 8. daftar isi — butuh soffice
if command -v soffice >/dev/null 2>&1; then
    cek "buat_daftar_isi berjalan" \
        $PY scripts/buat_daftar_isi.py "$TMP/template.docx" "$PROFIL"
    cek "hasil daftar isi tercipta" test -s "$TMP/template.docx"
else
    # harus gagal dengan pesan jelas, bukan traceback
    cek_tolak "buat_daftar_isi gagal rapi tanpa soffice" \
        $PY scripts/buat_daftar_isi.py "$TMP/template.docx" "$PROFIL"
    cek_isi "pesan soffice hilang menyebut cara pasang" "apt-get install"
    lewatkan "daftar isi nyata" "soffice (LibreOffice) tidak terpasang"
fi

# 7. audit_halaman — butuh poppler
if command -v pdfinfo >/dev/null 2>&1; then
    lewatkan "audit_halaman pada PDF asli" "belum ada render PDF di mesin uji"
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
