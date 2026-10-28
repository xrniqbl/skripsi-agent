#!/usr/bin/env bash
# Gerbang mutu naskah: jalankan semua pemeriksa isi dalam satu perintah.
#
#   bash skills/format_kampus/scripts/gate_naskah.sh NASKAH PROFIL-KAMPUS.yaml [opsi]
#
# Opsi:
#   --ketat              peringatan dihitung gagal (default: hanya galat)
#   --min-jurnal N       timpa batas minimal jurnal dari profil — berguna untuk
#                        proposal/tahap awal yang memang belum selengkap skripsi
#   --tahun-acuan TAHUN  timpa tahun patokan usia referensi (default: tahun ini)
#
# Pemeriksa yang dijalankan berurutan:
#   1. periksa_sistematika   bagian awal/akhir, bab, subbab, penomoran, caption
#   2. periksa_pustaka       ketentuan daftar pustaka
#   3. periksa_ringkasan     Ringkasan, Abstract, kata kunci
#   4. periksa_tabel_gambar  caption, urutan nomor, rujukan di teks
#   5. periksa_penomoran     nomor subbab dari numbering.xml (khusus .docx)
#   6. cek_bahasa            ragam baku + aturan bahasa panduan
#   7. peta_bab45            pemetaan rumusan -> hasil -> simpulan
#
# Tanpa --ketat, temuan berupa PERINGATAN tidak menggagalkan gerbang; dengan
# --ketat, satu peringatan pun membuat exit 1.
#
# Kode keluar:
#   0  semua gerbang lulus
#   1  ada gerbang gagal
#   2  pemakaian salah / berkas tidak ada
set -uo pipefail

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
fi
if [ $# -lt 2 ]; then
    sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'
    exit 2
fi

NASKAH="$1"
PROFIL="$2"
shift 2
KETAT=""
MIN_JURNAL=""
TAHUN_ACUAN=""
while [ $# -gt 0 ]; do
    case "$1" in
        --ketat)       KETAT="--ketat" ;;
        --min-jurnal)  MIN_JURNAL="${2:-}"; shift ;;
        --tahun-acuan) TAHUN_ACUAN="${2:-}"; shift ;;
        *) echo "GAGAL: opsi tidak dikenal: $1" >&2; exit 2 ;;
    esac
    shift
done

[ -f "$NASKAH" ] || { echo "GAGAL: naskah tidak ada: $NASKAH" >&2; exit 2; }
[ -f "$PROFIL" ] || { echo "GAGAL: profil tidak ada: $PROFIL" >&2; exit 2; }

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
PY="${PYTHON:-python3}"

gagal=0
peringatan=0
laporan="$(mktemp)"
trap 'rm -f "$laporan"' EXIT

jalankan() {
    local nama="$1" skrip="$2"; shift 2
    local out
    out="$("$PY" "$skrip" "$@" 2>&1)"
    local rc=$?
    local ringkas
    ringkas="$(printf '%s\n' "$out" | grep -E '^Ringkasan:|^Preset ' | tail -1)"

    local label
    label="$(printf '%-12s' "$nama")"

    if [ $rc -eq 0 ]; then
        if printf '%s' "$ringkas" | grep -qE '[1-9][0-9]* peringatan'; then
            echo "  ~ $label — $ringkas"
            peringatan=$((peringatan + 1))
            [ "$KETAT" = "--ketat" ] && gagal=$((gagal + 1))
        else
            echo "  OK $label — ${ringkas:-lulus}"
        fi
    elif [ $rc -eq 2 ]; then
        echo "  ? $label — tidak dapat diperiksa (berkas/profil tidak terbaca)"
        gagal=$((gagal + 1))
    else
        echo "  X $label — $ringkas"
        printf '%s\n' "$out" | sed -n '1,400p' >>"$laporan"
        gagal=$((gagal + 1))
    fi
}

echo "=== Gerbang mutu naskah ==="
echo "  naskah : $NASKAH"
echo "  profil : $PROFIL"
[ "$KETAT" = "--ketat" ] && echo "  mode   : KETAT (peringatan = gagal)"
echo

jalankan "sistematika" "$HERE/periksa_sistematika.py" "$NASKAH" "$PROFIL" --abaikan-opsional
# Batas minimal jurnal diambil dari profil (sitasi.min_jurnal_atau_prosiding)
# supaya tidak ada angka yang diulang di dua tempat dan bisa jadi tidak sinkron.
if [ -z "$MIN_JURNAL" ]; then
    MIN_JURNAL="$("$PY" - "$PROFIL" <<'PYEOF'
import sys, yaml
try:
    p = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
    print(int((p.get("sitasi") or {}).get("min_jurnal_atau_prosiding") or 0))
except Exception:
    print(0)
PYEOF
)"
fi
ARG_PUSTAKA=()
[ -n "$MIN_JURNAL" ] && [ "$MIN_JURNAL" != "0" ] && ARG_PUSTAKA+=(--min-jurnal "$MIN_JURNAL")
[ -n "$TAHUN_ACUAN" ] && ARG_PUSTAKA+=(--tahun-acuan "$TAHUN_ACUAN")
jalankan "pustaka" "$HERE/periksa_pustaka.py" "$NASKAH" "${ARG_PUSTAKA[@]+"${ARG_PUSTAKA[@]}"}"
jalankan "ringkasan" "$HERE/periksa_ringkasan.py" "$NASKAH" "$PROFIL"
jalankan "tabel/gambar" "$HERE/periksa_tabel_gambar.py" "$NASKAH" "$PROFIL"
# periksa_penomoran hanya untuk .docx — nomor subbab di .md/.pdf sudah berupa teks
case "$NASKAH" in
    *.docx) jalankan "penomoran" "$HERE/periksa_penomoran.py" "$NASKAH" "$PROFIL" ;;
    *)      echo "  - penomoran    — dilewati (bukan .docx; nomor sudah berupa teks)" ;;
esac
jalankan "bahasa" "$ROOT/skills/bahasa_akademik/scripts/cek_bahasa.py" "$NASKAH"
jalankan "bab IV/V" "$ROOT/skills/bab_iv_v/scripts/peta_bab45.py" "$NASKAH" --periksa

echo
if [ "$gagal" -eq 0 ]; then
    echo "HASIL: semua gerbang lulus ($peringatan dengan peringatan)"
    exit 0
fi
echo "HASIL: $gagal gerbang gagal — rincian:"
sed -n '1,400p' "$laporan"
exit 1
