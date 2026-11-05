#!/usr/bin/env bash
# Uji pemeriksa integritas AI. Naskah uji SENGAJA cacat: pemeriksa yang tidak
# menangkapnya tidak berguna, dan pemeriksa yang menandai naskah bersih berisik.
set -uo pipefail
PY="${PYTHON:-python3}"
cd "$(dirname "$0")/.." || exit 2
OUT="$(mktemp)"; trap 'rm -f "$OUT"' EXIT
gagal=0
lulus() { echo "LULUS $1"; }
rusak() { echo "GAGAL $1"; sed 's/^/      /' "$OUT" | head -12; gagal=$((gagal+1)); }
ok()    { local n="$1"; shift; if "$@" >"$OUT" 2>&1; then lulus "$n"; else rusak "$n"; fi; }
tolak() { local n="$1"; shift; if "$@" >"$OUT" 2>&1; then rusak "$n (harus exit bukan-0)"; else lulus "$n"; fi; }
ada()   { if grep -qi -- "$2" "$OUT"; then lulus "$1"; else rusak "$1 (pola '$2' tidak muncul)"; fi; }
tidak_ada() { if grep -qi -- "$2" "$OUT"; then rusak "$1 (pola '$2' tidak boleh muncul)"; else lulus "$1"; fi; }
# Baris temuan diawali "  PERINGATAN" (huruf kapital); baris ringkasan memakai
# "peringatan" huruf kecil, jadi pencocokan harus peka huruf dan terjangkar.
tanpa_temuan_peringatan() { if grep -q -- "^  PERINGATAN" "$OUT"; then rusak "$1 (ada baris PERINGATAN)"; else lulus "$1"; fi; }

S=scripts/cek_integritas_ai.py
T=tests
echo "== integritas_akademik: uji pemeriksa =="

ok    "help valid" $PY $S --help
tolak "menolak tanpa argumen" $PY $S
$PY $S /tidak/ada.md >"$OUT" 2>&1; [ $? -eq 2 ] && lulus "berkas tidak ada = kode 2" || rusak "berkas tidak ada harus kode 2"

ok    "naskah dengan pernyataan lengkap lulus bersih" $PY $S $T/naskah_ai_baik.md --ketat
tanpa_temuan_peringatan "naskah baik tanpa peringatan palsu"

ok    "pernyataan 'tidak menggunakan AI' diterima" $PY $S $T/naskah_ai_tidak_pakai.md --ketat
ada   "bentuk tidak-pakai dikenali" "tidak menggunakan AI"

# tanpa pernyataan: peringatan secara bawaan, galat bila profil mewajibkan
ok    "tanpa pernyataan = hanya peringatan" $PY $S $T/naskah_ai_tanpa_pernyataan.md
ada   "peringatan pernyataan hilang" "tidak ada bagian"
tolak "tanpa pernyataan + --ketat gagal" $PY $S $T/naskah_ai_tanpa_pernyataan.md --ketat
tolak "tanpa pernyataan + profil wajib = galat" $PY $S $T/naskah_ai_tanpa_pernyataan.md --profil $T/profil_wajib.yaml
ada   "galat menyebut profil" "mewajibkan"
ok    "profil tidak_diatur = hanya info" $PY $S $T/naskah_ai_tanpa_pernyataan.md --profil $T/profil_tidak_diatur.yaml --ketat
tanpa_temuan_peringatan "tidak_diatur tanpa peringatan"

# naskah buruk: semua kelas cacat harus tertangkap
tolak "naskah buruk ditolak" $PY $S $T/naskah_ai_buruk.md
ada   "menangkap AI sebagai penulis" "kolom penulis"
ada   "menangkap 'tentu, berikut'" "Tentu, berikut"
ada   "menangkap 'sebagai model bahasa'" "sebagai model bahasa"
ada   "menangkap utm_source=chatgpt" "utm_source=chatgpt"
ada   "menangkap 'semoga membantu'" "semoga"
ada   "menangkap penanda belum diisi" "belum diisi"
ada   "menangkap alat tidak disebut/tujuan hilang" "tujuan/bagian"
ada   "menangkap verifikasi hilang" "memverifikasi"

# sikap profil tidak dikenal harus ditolak, bukan diabaikan diam-diam
printf 'integritas:\n  pernyataan_ai: mungkin\n' >"$T/.profil_salah.yaml"
$PY $S $T/naskah_ai_baik.md --profil $T/.profil_salah.yaml >"$OUT" 2>&1; rc=$?
rm -f "$T/.profil_salah.yaml"
[ $rc -eq 2 ] && lulus "sikap profil tidak dikenal = kode 2" || rusak "sikap profil salah harus kode 2 (dapat $rc)"

$PY $S $T/naskah_ai_buruk.md --json "$OUT.json" >/dev/null 2>&1
$PY -c "import json,sys; d=json.load(open(sys.argv[1])); assert d['galat'] and d['peringatan']" "$OUT.json" 2>"$OUT" \
    && lulus "laporan JSON valid" || rusak "laporan JSON tidak valid"
rm -f "$OUT.json"

echo
if [ $gagal -eq 0 ]; then echo "SEMUA LULUS"; exit 0; fi
echo "$gagal PEMERIKSAAN GAGAL"; exit 1
