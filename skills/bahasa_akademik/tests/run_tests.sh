#!/usr/bin/env bash
# Uji pemeriksa bahasa akademik (termasuk aturan teknis panduan kampus 4.8/4.9).
set -uo pipefail
PY="${PYTHON:-python3}"
cd "$(dirname "$0")/.." || exit 2
gagal=0
cek() { local n="$1"; shift; if "$@" >/tmp/bh.out 2>&1; then echo "LULUS $n"; else echo "GAGAL $n"; sed 's/^/      /' /tmp/bh.out | head -10; gagal=$((gagal+1)); fi; }
cek_tolak() { local n="$1"; shift; if "$@" >/tmp/bh.out 2>&1; then echo "GAGAL $n (harus exit bukan-0)"; gagal=$((gagal+1)); else echo "LULUS $n"; fi; }
cek_isi() { local n="$1" p="$2"; if grep -qi -- "$p" /tmp/bh.out; then echo "LULUS $n"; else echo "GAGAL $n (pola '$p' tidak muncul)"; sed 's/^/      /' /tmp/bh.out | head -8; gagal=$((gagal+1)); fi; }

echo "== bahasa_akademik: uji pemeriksa =="
cek "help valid" $PY scripts/cek_bahasa.py --help
cek_tolak "menolak tanpa argumen" $PY scripts/cek_bahasa.py
cek "naskah bersih lulus" $PY scripts/cek_bahasa.py tests/naskah_bahasa_bersih.md
cek_tolak "naskah buruk ditolak" $PY scripts/cek_bahasa.py tests/naskah_bahasa_buruk.md

cek_tolak "menangkap singkatan tidak resmi" $PY scripts/cek_bahasa.py tests/naskah_bahasa_buruk.md
cek_isi "menangkap dll" "singkatan tidak resmi"
cek_isi "menangkap kata2" "kata ulang angka"
cek_isi "menangkap PKL/riset" "garis miring"
cek_isi "menangkap daripada" "daripada"
cek_isi "menangkap analisa" "analisa"
cek_isi "menangkap ragam lisan" "ragam lisan"

# naskah bersih tidak boleh memicu aturan garis miring / daripada
$PY scripts/cek_bahasa.py tests/naskah_bahasa_bersih.md >/tmp/bh2.out 2>&1
if grep -qiE "garis miring|daripada|kata ulang" /tmp/bh2.out; then
    echo "GAGAL naskah bersih tidak boleh memicu aturan 4.8/4.9"; gagal=$((gagal+1))
else
    echo "LULUS naskah bersih bebas dari temuan 4.8/4.9"
fi

echo
if [ "$gagal" -eq 0 ]; then echo "Ringkasan: SEMUA LULUS"; exit 0; else echo "Ringkasan: GAGAL $gagal"; exit 1; fi
