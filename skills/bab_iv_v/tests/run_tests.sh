#!/usr/bin/env bash
# Uji skill bab_iv_v. Jalankan dari folder skill:
#   bash tests/run_tests.sh
set -uo pipefail

PY="${PYTHON:-python3}"
cd "$(dirname "$0")/.." || exit 2

gagal=0
cek() {
    local nama="$1"; shift
    if "$@" >/tmp/bab45.out 2>&1; then
        echo "LULUS $nama"
    else
        echo "GAGAL $nama"
        sed 's/^/      /' /tmp/bab45.out | head -12
        gagal=$((gagal + 1))
    fi
}
cek_tolak() {
    local nama="$1"; shift
    if "$@" >/tmp/bab45.out 2>&1; then
        echo "GAGAL $nama (harus exit bukan-0)"
        gagal=$((gagal + 1))
    else
        echo "LULUS $nama"
    fi
}
cek_isi() {
    local nama="$1" pola="$2"
    if grep -qi "$pola" /tmp/bab45.out; then
        echo "LULUS $nama"
    else
        echo "GAGAL $nama (pola '$pola' tidak muncul)"
        gagal=$((gagal + 1))
    fi
}

echo "== bab_iv_v: uji skrip =="

# naskah baik harus lulus
cek "naskah baik lulus tanpa temuan" \
    $PY scripts/peta_bab45.py tests/naskah_baik.md --periksa
cek_isi "naskah baik: 0 galat" "Ringkasan: 0 galat"
cek_isi "naskah baik: pemetaan 4 rumusan" "Pemetaan rumusan"

# naskah buruk harus ditolak
cek_tolak "naskah buruk ditolak" \
    $PY scripts/peta_bab45.py tests/naskah_buruk.md --periksa
cek_isi "deteksi tafsir di bagian hasil" "tafsir_di_hasil"
cek_isi "deteksi jumlah simpulan tidak sama" "jumlah_tidak_sama"
cek_isi "deteksi saran tanpa pelaku" "saran_tanpa_pelaku"
cek_isi "deteksi cakupan rumusan rendah" "cakupan_rendah"

# --peta mencetak kerangka
cek "peta mencetak tabel kosong" \
    $PY scripts/peta_bab45.py --peta
cek_isi "peta memuat kolom jawaban" "Jawaban satu kalimat"

# --json valid
cek_tolak "json ditulis walau ada galat" \
    $PY scripts/peta_bab45.py tests/naskah_buruk.md --periksa --json /tmp/bab45.json
cek "json dapat di-parse" \
    $PY -c "import json;d=json.load(open('/tmp/bab45.json'));assert d['galat'] and 'info' in d"

# tanpa argumen harus menolak
cek_tolak "menolak pemanggilan tanpa argumen" $PY scripts/peta_bab45.py

# berkas tidak ada
cek_tolak "menolak berkas tidak ada" \
    $PY scripts/peta_bab45.py /tmp/tidak_ada_xyz.md --periksa

# --help valid
cek "help valid" $PY scripts/peta_bab45.py --help

echo
if [ "$gagal" -eq 0 ]; then
    echo "Ringkasan: SEMUA LULUS"
    exit 0
else
    echo "Ringkasan: GAGAL $gagal"
    exit 1
fi
