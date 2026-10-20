#!/usr/bin/env bash
#
# ingest_sources.sh — Inventarisasi & ekstraksi file lokal untuk skill proposal-skripsi.
#
# Usage:
#   ./ingest_sources.sh <folder> [--out <cache-dir>] [--no-extract] [--json]
#
# Behavior:
#   - Walk folder secara rekursif, klasifikasikan tiap file ke 5 kategori:
#       literatur | data | pedoman | aturan | lainnya
#   - Untuk setiap *.pdf, tulis teks (.txt) ke folder cache via pdftotext (poppler-utils)
#   - Deteksi PDF hasil scan (teks kosong) -> tandai PERLU_OCR
#   - Cetak ringkasan + daftar per kategori
#   - Dengan --json, simpan sumber_inventaris.json ke folder cache
#
# Dependencies:
#   - pdftotext (poppler-utils)   brew install poppler   (macOS)
#     apt install poppler-utils                            (Linux)
#   Tanpa pdftotext, script tetap jalan; PDF ditandai ekstaksi=skip.
#
# Exit codes: 0 sukses, 1 argumen salah, 2 tool wajib (pdftotext) tidak ada dan --extract dipaksa.

set -u

TARGET=""
OUT=""
DO_EXTRACT=1
AS_JSON=0

while [ $# -gt 0 ]; do
  case "$1" in
    --out)      OUT="${2:-}"; shift 2 ;;
    --no-extract) DO_EXTRACT=0; shift ;;
    --json)     AS_JSON=1; shift ;;
    -h|--help)  sed -n '3,20p' "$0"; exit 0 ;;
    -*)         echo "ERROR: opsi tidak dikenal: $1" >&2; exit 1 ;;
    *)          TARGET="$1"; shift ;;
  esac
done

if [ -z "$TARGET" ]; then
  echo "usage: $0 <folder> [--out <cache-dir>] [--no-extract] [--json]" >&2
  exit 1
fi
if [ ! -e "$TARGET" ]; then
  echo "ERROR: path tidak ditemukan: $TARGET" >&2
  exit 1
fi

if [ -z "$OUT" ]; then
  if [ -d "$TARGET" ]; then OUT="$TARGET/.cache_ekstrak"; else OUT="$(dirname "$TARGET")/.cache_ekstrak"; fi
fi
mkdir -p "$OUT"

HAS_PDFTOTEXT=0
if command -v pdftotext >/dev/null 2>&1; then HAS_PDFTOTEXT=1; fi
if [ "$DO_EXTRACT" -eq 1 ] && [ "$HAS_PDFTOTEXT" -eq 0 ]; then
  echo "WARN: pdftotext tidak ditemukan — PDF tidak diekstrak." >&2
  echo "      macOS: brew install poppler | Linux: apt install poppler-utils" >&2
fi

# klasifikasi
classify() {
  local path="$1" base ext name_low
  base="$(basename "$path")"
  ext="${base##*.}"; ext="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"
  name_low="$(printf '%s' "$base" | tr '[:upper:]' '[:lower:]')"

  case "$ext" in
    pdf|docx|md|txt|tex|odt|rtf)
      case "$name_low" in
        *pedoman*|*panduan*|*skripsi*|*tesis*|*disertasi*|*format*|*template*|*proposal*|*pembimbing*|*panduan*)
          echo "pedoman" ;;
        *etika*|*ethic*|*consent*|*persetujuan*|*sidang*|*seminar*)
          echo "aturan" ;;
        *) echo "literatur" ;;
      esac ;;
    csv|tsv|xls|xlsx|json|jsonl|sav|dta)
      if [ "$ext" = "json" ] || [ "$ext" = "jsonl" ]; then
        if head -c 400 "$path" | grep -q '^\s*\[\s*[{]'; then echo "data"; else echo "lainnya"; fi
      else
        echo "data"
      fi ;;
    *) echo "lainnya" ;;
  esac
}

n_total=0; n_lit=0; n_data=0; n_ped=0; n_atr=0; n_lain=0
n_ok=0; n_ocr=0; n_fail=0
JSON_ROWS=""

process() {
  local f="$1" rel cat ext size status
  rel="${f#"$TARGET"/}"
  cat="$(classify "$f")"
  ext="${f##*.}"; ext="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"
  if [ -f "$f" ]; then size=$(wc -c < "$f" | tr -d ' '); else size=0; fi
  n_total=$((n_total + 1))
  case "$cat" in
    literatur) n_lit=$((n_lit + 1)) ;;
    data)      n_data=$((n_data + 1)) ;;
    pedoman)   n_ped=$((n_ped + 1)) ;;
    aturan)    n_atr=$((n_atr + 1)) ;;
    *)         n_lain=$((n_lain + 1)) ;;
  esac

  status="n/a"
  if [ "$ext" = "pdf" ] && [ "$DO_EXTRACT" -eq 1 ]; then
    local safe="${rel//\//__}"
    local txt="$OUT/${safe%.pdf}.txt"
    if [ -s "$txt" ]; then
      status="ok(cache)"; n_ok=$((n_ok + 1))
    elif [ "$HAS_PDFTOTEXT" -eq 1 ]; then
      if pdftotext -layout "$f" "$txt" 2>/dev/null && [ -s "$txt" ]; then
        status="ok"; n_ok=$((n_ok + 1))
      else
        rm -f "$txt"
        if head -c 2000 "$f" | grep -qiE '/(image|font)'; then status="PERLU_OCR"; n_ocr=$((n_ocr + 1))
        else status="gagal"; n_fail=$((n_fail + 1)); fi
      fi
    else
      status="skip(no-pdftotext)"
    fi
  elif [ "$ext" = "docx" ] || [ "$ext" = "odt" ] || [ "$ext" = "rtf" ]; then
    if command -v textutil >/dev/null 2>&1; then
      local safe="${rel//\//__}"
      textutil -convert txt -stdout "$f" > "$OUT/${safe%.*}.txt" 2>/dev/null
      if [ -s "$OUT/${safe%.*}.txt" ]; then status="ok(textutil)"; else status="gagal(textutil)"; fi
    else
      status="manual(textutil/pandoc)"
    fi
  elif [ "$ext" = "md" ] || [ "$ext" = "txt" ] || [ "$ext" = "tex" ]; then
    status="baca-langsung"
  elif [ "$ext" = "csv" ] || [ "$ext" = "tsv" ] || [ "$ext" = "xlsx" ] || [ "$ext" = "xls" ] || [ "$ext" = "sav" ] || [ "$ext" = "dta" ]; then
    status="profilkan(profile_dataset.py)"
  fi

  printf '  %-11s %-8s %-8s %s\n' "[$cat]" "$ext" "$(printf '%.0fK' $((size / 1024)))" "$rel [$status]"
  if [ "$AS_JSON" -eq 1 ]; then
    JSON_ROWS="${JSON_ROWS}{\"path\":\"${rel//\"/\\\"}\",\"kategori\":\"$cat\",\"ekstensi\":\"$ext\",\"bytes\":$size,\"ekstraksi\":\"$status\"},"
  fi
}

echo "== Inventarisasi: $TARGET"
echo "== Cache       : $OUT"
echo
if [ -d "$TARGET" ]; then
  while IFS= read -r -d '' f; do process "$f"; done < <(find "$TARGET" -type f \
    \( -iname '*.pdf' -o -iname '*.docx' -o -iname '*.md' -o -iname '*.txt' -o -iname '*.tex' \
       -o -iname '*.csv' -o -iname '*.tsv' -o -iname '*.xlsx' -o -iname '*.xls' -o -iname '*.json' \
       -o -iname '*.jsonl' -o -iname '*.odt' -o -iname '*.rtf' -o -iname '*.sav' -o -iname '*.dta' \) \
    -not -path "$OUT/*" -print0)
elif [ -f "$TARGET" ]; then
  process "$TARGET"
fi

echo
echo "-- Ringkasan"
printf '  total file     : %d\n' "$n_total"
printf '  literatur      : %d\n' "$n_lit"
printf '  data           : %d\n' "$n_data"
printf '  pedoman        : %d\n' "$n_ped"
printf '  aturan/etika   : %d\n' "$n_atr"
printf '  lainnya        : %d\n' "$n_lain"
printf '  ekstraksi PDF  : ok=%d PERLU_OCR=%d gagal=%d\n' "$n_ok" "$n_ocr" "$n_fail"

if [ "$n_data" -gt 0 ]; then
  echo
  echo "-- Langkah berikutnya (data)"
  echo "  python3 scripts/profile_dataset.py <file-data> --out profil"
fi
if [ "$n_ocr" -gt 0 ]; then
  echo
  echo "WARNING: $n_ocr PDF perlu OCR. Minta user versi digital atau gunakan ocrmypdf."
fi

if [ "$AS_JSON" -eq 1 ]; then
  json="$OUT/sumber_inventaris.json"
  printf '{\n  "root": "%s",\n  "counts": {"total": %d, "literatur": %d, "data": %d, "pedoman": %d, "aturan": %d, "lainnya": %d},\n  "files": [\n' \
    "$TARGET" "$n_total" "$n_lit" "$n_data" "$n_ped" "$n_atr" "$n_lain" > "$json"
  printf '%s' "$JSON_ROWS" | sed '$ s/,$//' >> "$json"
  printf '\n  ]\n}\n' >> "$json"
  echo
  echo "JSON inventaris: $json"
fi
