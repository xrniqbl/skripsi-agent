#!/usr/bin/env bash
# Smoke test skill topik_skripsi. Jalankan dari folder skill ini:
#   bash tests/run_tests.sh
set -uo pipefail

PY="${PYTHON:-python3}"
cd "$(dirname "$0")/.." || exit 2

gagal=0
cek() {
    local nama="$1"; shift
    if "$@" >/tmp/skripsi_test.out 2>&1; then
        echo "LULUS $nama"
    else
        echo "GAGAL $nama"
        sed 's/^/      /' /tmp/skripsi_test.out | head -20
        gagal=$((gagal + 1))
    fi
}

echo "== topik_skripsi: uji skrip =="

# 1) peta_fenomena: contoh punya satu klaim palsu -> harus exit 1
if $PY scripts/peta_fenomena.py tests/contoh_masalah.md --min-lulus 3 >/tmp/pf1.out 2>&1; then
    echo "GAGAL peta_fenomena mendeteksi klaim kelayakan palsu (harus exit 1)"
    gagal=$((gagal + 1))
else
    if grep -q 'GALAT' /tmp/pf1.out; then
        echo "LULUS peta_fenomena mendeteksi klaim kelayakan palsu"
    else
        echo "GAGAL peta_fenomena keluar 1 tanpa pesan GALAT"
        gagal=$((gagal + 1))
    fi
fi

# 2) peta_fenomena pada naskah bersih -> exit 0
cek "peta_fenomena lulus pada naskah tanpa klaim palsu" \
    $PY scripts/peta_fenomena.py tests/contoh_masalah_bersih.md --min-lulus 3

# 3) peta_fenomena JSON (pakai naskah bersih supaya exit 0)
cek "peta_fenomena menulis JSON" \
    $PY scripts/peta_fenomena.py tests/contoh_masalah_bersih.md --json /tmp/pf.json
cek "JSON peta_fenomena terisi" test -s /tmp/pf.json
cek "JSON peta_fenomena dapat di-parse" \
    $PY -c "import json;d=json.load(open('/tmp/pf.json'));assert d['total']==2 and d['layak']==2"

# 4) skor_topik: harus exit 0 (ada yang lolos) dan memuat DISKUALIFIKASI
cek "skor_topik berjalan" \
    $PY scripts/skor_topik.py tests/contoh_kandidat.json --out /tmp/skor.md --ambang 70
if grep -q 'DISKUALIFIKASI' /tmp/skor.md && grep -q 'KUAT' /tmp/skor.md; then
    echo "LULUS skor_topik menandai diskualifikasi + peringkat"
else
    echo "GAGAL skor_topik tidak menandai diskualifikasi/peringkat"
    gagal=$((gagal + 1))
fi

# 5) skor_topik: semua di bawah ambang -> harus exit 1
cat >/tmp/lemah.json <<'EOF'
{"kandidat":[{"id":"X","judul_kerja":"Topik lemah","skor":{"feasible":1,"interesting":1,"novel":1,"ethical":5,"relevant":1}}]}
EOF
if $PY scripts/skor_topik.py /tmp/lemah.json --ambang 70 >/dev/null 2>&1; then
    echo "GAGAL skor_topik tidak exit 1 saat semua di bawah ambang"
    gagal=$((gagal + 1))
else
    echo "LULUS skor_topik exit 1 saat semua di bawah ambang"
fi

# 6) judul_check: contoh punya galat -> exit 1
if $PY scripts/judul_check.py tests/contoh_judul.md --maks-kata 25 --bidang sistem_informasi \
        >/tmp/jc.out 2>&1; then
    echo "GAGAL judul_check tidak mendeteksi galat pada contoh buruk"
    gagal=$((gagal + 1))
else
    echo "LULUS judul_check mendeteksi galat pada contoh buruk"
fi
for pola in 'verba penelitian' 'lokus terlalu luas' 'DUPLIKAT' 'kata klaim hasil'; do
    if grep -qi "$pola" /tmp/jc.out; then
        echo "LULUS judul_check menangkap: $pola"
    else
        echo "GAGAL judul_check tidak menangkap: $pola"
        gagal=$((gagal + 1))
    fi
done

# 7) judul_check pada judul yang benar -> exit 0
cat >/tmp/judul_baik.md <<'EOF'
1. Rancang Bangun Dashboard Rekap Gizi Berbasis Web pada Puskesmas X Kabupaten Y
EOF
cek "judul_check lulus pada judul yang benar" \
    $PY scripts/judul_check.py /tmp/judul_baik.md --bidang sistem_informasi

# 8) skrip tanpa argumen harus menolak, bukan diam
for s in peta_fenomena skor_topik judul_check; do
    if $PY "scripts/$s.py" >/dev/null 2>&1; then
        echo "GAGAL $s menerima pemanggilan tanpa argumen"
        gagal=$((gagal + 1))
    else
        echo "LULUS $s menolak pemanggilan tanpa argumen"
    fi
done

echo
if [ "$gagal" -eq 0 ]; then
    echo "Ringkasan: SEMUA LULUS"
    exit 0
else
    echo "Ringkasan: GAGAL $gagal"
    exit 1
fi
