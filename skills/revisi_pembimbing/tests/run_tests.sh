#!/usr/bin/env bash
# Uji skill revisi_pembimbing. Jalankan dari folder skill:
#   bash tests/run_tests.sh
set -uo pipefail

PY="${PYTHON:-python3}"
cd "$(dirname "$0")/.." || exit 2
NASKAHDIR="../bab_iv_v/tests"

gagal=0
cek() {
    local nama="$1"; shift
    if "$@" >/tmp/revisi.out 2>&1; then
        echo "LULUS $nama"
    else
        echo "GAGAL $nama"
        sed 's/^/      /' /tmp/revisi.out | head -12
        gagal=$((gagal + 1))
    fi
}
cek_tolak() {
    local nama="$1"; shift
    if "$@" >/tmp/revisi.out 2>&1; then
        echo "GAGAL $nama (harus exit bukan-0)"
        gagal=$((gagal + 1))
    else
        echo "LULUS $nama"
    fi
}
cek_isi() {
    local nama="$1" pola="$2"
    if grep -qi -- "$pola" /tmp/revisi.out; then
        echo "LULUS $nama"
    else
        echo "GAGAL $nama (pola '$pola' tidak muncul)"
        gagal=$((gagal + 1))
    fi
}

echo "== revisi_pembimbing: uji skrip =="

# pecah catatan mentah
cek "memecah catatan mentah" \
    $PY scripts/parse_revisi.py tests/catatan_mentah.md --out /tmp/rev_t.md
cek_isi "10 butir terdeteksi" "Terdeteksi 10 butir"
cek "tabel kerja ditulis" test -s /tmp/rev_t.md
if grep -q 'R-01' /tmp/rev_t.md; then
    echo "LULUS tabel memuat R-01"
else
    echo "GAGAL tabel memuat R-01"
    gagal=$((gagal + 1))
fi
if grep -q 'Bukti |' /tmp/rev_t.md; then
    echo "LULUS tabel memuat kolom Bukti"
else
    echo "GAGAL tabel memuat kolom Bukti"
    gagal=$((gagal + 1))
fi

# klasifikasi: "copy paste" harus kritis
if grep -q 'copy paste.*kritis' /tmp/rev_t.md; then
    echo "LULUS 'copy paste' diklasifikasi kritis"
else
    echo "GAGAL 'copy paste' tidak diklasifikasi kritis"
    gagal=$((gagal + 1))
fi

# "kayaknya" harus klarifikasi
if grep -qi 'kayaknya.*klarifikasi' /tmp/rev_t.md; then
    echo "LULUS 'kayaknya' diklasifikasi klarifikasi"
else
    echo "GAGAL 'kayaknya' tidak diklasifikasi klarifikasi"
    gagal=$((gagal + 1))
fi

# "garis vertikal" harus format/rendah
if grep -qi 'garis vertikal.*format.*rendah' /tmp/rev_t.md; then
    echo "LULUS 'garis vertikal' diklasifikasi format/rendah"
else
    echo "GAGAL 'garis vertikal' tidak diklasifikasi format/rendah"
    gagal=$((gagal + 1))
fi

# lokasi: "Tabel 2.1" harus Bab II
if grep -qi 'garis vertikal.*Bab II' /tmp/rev_t.md; then
    echo "LULUS 'Tabel 2.1' memetakan ke Bab II"
else
    echo "GAGAL 'Tabel 2.1' tidak memetakan ke Bab II"
    gagal=$((gagal + 1))
fi

# verifikasi: semua belum -> harus tolak karena ada butir kritis
cek_tolak "verifikasi menolak butir kritis yang belum selesai" \
    $PY scripts/parse_revisi.py /tmp/rev_t.md --verifikasi "$NASKAHDIR/naskah_baik.md"
cek_isi "menyebut butir kritis" "KRITIS"

# verifikasi: tabel terisi -> harus lulus
cek "verifikasi lulus pada tabel terisi" \
    $PY scripts/parse_revisi.py tests/revisi_terisi.md --verifikasi "$NASKAHDIR/naskah_baik.md"
cek_isi "progres 100%" "100%"

# bukti tidak terukur harus ditolak
cat >/tmp/rev_buruk.md <<'EOF'
| ID | Butir | Sumber | Lokasi | Jenis | Prioritas | Status | Bukti |
|---|---|---|---|---|---|---|---|
| R-01 | Perbaiki latar belakang | Bimbingan | Bab I | wajib | kritis | selesai | sudah |
EOF
cek_tolak "bukti 'sudah' ditolak" \
    $PY scripts/parse_revisi.py /tmp/rev_buruk.md --verifikasi "$NASKAHDIR/naskah_baik.md"
cek_isi "pesan bukti tidak terukur" "tidak terukur"

# klarifikasi selesai tanpa jawaban harus ditolak
cat >/tmp/rev_klar.md <<'EOF'
| ID | Butir | Sumber | Lokasi | Jenis | Prioritas | Status | Bukti |
|---|---|---|---|---|---|---|---|
| R-01 | Metode kurang cocok | Bimbingan | Bab III | klarifikasi | tinggi | selesai | sudah diubah metodenya jadi kuantitatif |
EOF
cek_tolak "klarifikasi selesai tanpa jawaban pembimbing ditolak" \
    $PY scripts/parse_revisi.py /tmp/rev_klar.md --verifikasi "$NASKAHDIR/naskah_baik.md"
cek_isi "pesan klarifikasi tanpa jawaban" "klarifikasi"

# penolakan tanpa alasan harus ditolak
cat >/tmp/rev_tolak.md <<'EOF'
| ID | Butir | Sumber | Lokasi | Jenis | Prioritas | Status | Bukti |
|---|---|---|---|---|---|---|---|
| R-01 | Hapus uji beda | Bimbingan | Bab III | wajib | tinggi | ditolak-dengan-alasan | tidak setuju |
EOF
cek_tolak "penolakan tanpa alasan memadai ditolak" \
    $PY scripts/parse_revisi.py /tmp/rev_tolak.md --verifikasi "$NASKAHDIR/naskah_baik.md"

# penolakan dengan alasan memadai harus lulus
cat >/tmp/rev_tolak_ok.md <<'EOF'
| ID | Butir | Sumber | Lokasi | Jenis | Prioritas | Status | Bukti |
|---|---|---|---|---|---|---|---|
| R-01 | Hapus uji beda | Bimbingan | Bab III | wajib | tinggi | ditolak-dengan-alasan | rumusan 3 hal 3 menanyakan perbedaan antar kelompok, uji deskriptif tidak menjawabnya; desain hal 28 |
EOF
cek "penolakan dengan alasan memadai lulus" \
    $PY scripts/parse_revisi.py /tmp/rev_tolak_ok.md --verifikasi "$NASKAHDIR/naskah_baik.md"

# penolakan berkas
cek_tolak "menolak berkas tidak ada" $PY scripts/parse_revisi.py /tmp/nope_xyz.md
cek "help valid" $PY scripts/parse_revisi.py --help

echo
if [ "$gagal" -eq 0 ]; then
    echo "Ringkasan: SEMUA LULUS"
    exit 0
else
    echo "Ringkasan: GAGAL $gagal"
    exit 1
fi
