#!/usr/bin/env bash
# Uji skill sidang. Jalankan dari folder skill:
#   bash tests/run_tests.sh
set -uo pipefail

PY="${PYTHON:-python3}"
cd "$(dirname "$0")/.." || exit 2
NASKAHDIR="../bab_iv_v/tests"

gagal=0
cek() {
    local nama="$1"; shift
    if "$@" >/tmp/sidang.out 2>&1; then
        echo "LULUS $nama"
    else
        echo "GAGAL $nama"
        sed 's/^/      /' /tmp/sidang.out | head -12
        gagal=$((gagal + 1))
    fi
}
cek_tolak() {
    local nama="$1"; shift
    if "$@" >/tmp/sidang.out 2>&1; then
        echo "GAGAL $nama (harus exit bukan-0)"
        gagal=$((gagal + 1))
    else
        echo "LULUS $nama"
    fi
}
cek_isi() {
    local nama="$1" pola="$2"
    if grep -qi -- "$pola" /tmp/sidang.out; then
        echo "LULUS $nama"
    else
        echo "GAGAL $nama (pola '$pola' tidak muncul)"
        gagal=$((gagal + 1))
    fi
}

echo "== sidang: uji skrip =="

# audit naskah buruk menolak
cek_tolak "audit menolak naskah dengan simpulan kosong" \
    $PY scripts/audit_sidang.py "$NASKAHDIR/naskah_buruk.md"
cek_isi "deteksi simpulan kosong" "simpulan_kosong"
cek_isi "deteksi kata lemah" "kata_lemah"
cek_isi "deteksi bab hilang" "bab_hilang"

# audit naskah baik: peringatan boleh, galat tidak
cek "audit naskah baik tanpa galat" \
    $PY scripts/audit_sidang.py "$NASKAHDIR/naskah_baik.md"
cek_isi "naskah baik: 0 galat" "0 galat"

# pertanyaan dibangkitkan
cek "membangkitkan pertanyaan" \
    $PY scripts/audit_sidang.py "$NASKAHDIR/naskah_baik.md" --pertanyaan
cek_isi "pertanyaan wajib muncul" "Kelompok WAJIB"
cek_isi "pertanyaan angka dari R²" "66%"

# kartu angka
cek "kartu angka tercetak" \
    $PY scripts/audit_sidang.py "$NASKAHDIR/naskah_baik.md" --kartu-angka
cek_isi "kartu memuat β utuh (tidak terpotong)" 'β = 0,412'
cek_isi "kartu memuat R²" 'R² = 0,34'

# json valid
cek "json ditulis" \
    $PY scripts/audit_sidang.py "$NASKAHDIR/naskah_baik.md" --json /tmp/sidang.json
cek "json dapat di-parse" \
    $PY -c "import json;d=json.load(open('/tmp/sidang.json'));assert 'pertanyaan' in d and 'info' in d"

# penolakan argumen salah
cek_tolak "menolak berkas tidak ada" $PY scripts/audit_sidang.py /tmp/nope_xyz.md
cek "help valid" $PY scripts/audit_sidang.py --help

# naskah terlalu pendek
printf 'terlalu pendek\n' > /tmp/pendek.md
cek_tolak "menolak naskah terlalu pendek" $PY scripts/audit_sidang.py /tmp/pendek.md

# naskah bergaya panduan FTI ARS: "Identifikasi Masalah", bukan "Rumusan Masalah"
cek "naskah ARS: rumusan dikenali dari 'Identifikasi Masalah'" \
    $PY scripts/audit_sidang.py tests/naskah_fti_ars.md
$PY scripts/audit_sidang.py tests/naskah_fti_ars.md >/tmp/sd.out 2>&1
if grep -q "rumusan masalah : 2" /tmp/sd.out; then
    echo "LULUS naskah ARS: 2 butir rumusan terbaca"
else
    echo "GAGAL naskah ARS: 2 butir rumusan terbaca"; sed 's/^/      /' /tmp/sd.out | head -8
    gagal=$((gagal + 1))
fi
if grep -q "rumusan_simpulan_beda\|rumusan_tujuan_beda" /tmp/sd.out; then
    echo "GAGAL naskah ARS: tidak boleh ada galat kesejajaran"; gagal=$((gagal + 1))
else
    echo "LULUS naskah ARS: kesejajaran rumusan-tujuan-simpulan utuh"
fi

echo
if [ "$gagal" -eq 0 ]; then
    echo "Ringkasan: SEMUA LULUS"
    exit 0
else
    echo "Ringkasan: GAGAL $gagal"
    exit 1
fi
