#!/usr/bin/env bash
#
# build_docx.sh — Konversi proposal Markdown ke DOCX (pandoc) + daftar isi.
#
# Usage:
#   ./build_docx.sh <proposal.md> [--out-dir DIR] [--title "..."] [--ref-doc FILE]
#                   [--toc] [--number-sections] [--no-number-sections] [--clean]
#
# Output:
#   <name>.docx          dokumen Word dengan daftar isi otomatis (bila --toc)
#   daftar_isi.md        daftar isi manual (dari --toc) bila diperlukan
#   <name>_ekstrak.md    naskah tanpa blok instruksi/internal
#
# Dependencies:
#   - pandoc   brew install pandoc   (macOS) | apt install pandoc   (Linux)
#   --reference doc (opsional) berisi DOCX dari kampus, mis. pedoman_kampus.docx
#
# Catatan:
#   - Pandoc tidak memproses gaya bahasa Indonesia (mis. "ke-iksa"). Untuk itu,
#     sediakan reference-doc yang sudah disetel di Word/WPS.
#   - Nomor halaman dan tata letak akhir mengikuti reference-doc, bukan script ini.

set -u

SRC=""
OUT_DIR="."
TITLE=""
REF_DOC=""
TOC=0
NUMBER=1
CLEAN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --out-dir)   OUT_DIR="${2:-.}"; shift 2 ;;
    --title)     TITLE="${2:-}"; shift 2 ;;
    --ref-doc)   REF_DOC="${2:-}"; shift 2 ;;
    --toc)       TOC=1; shift ;;
    --number-sections)    NUMBER=1; shift ;;
    --no-number-sections) NUMBER=0; shift ;;
    --clean)     CLEAN=1; shift ;;
    -h|--help)   sed -n '3,22p' "$0"; exit 0 ;;
    -*)          echo "ERROR: opsi tidak dikenal: $1" >&2; exit 1 ;;
    *)           SRC="$1"; shift ;;
  esac
done

if [ -z "$SRC" ]; then
  echo "usage: $0 <proposal.md> [--out-dir DIR] [--title \"...\"] [--ref-doc FILE] [--toc] [--clean]" >&2
  exit 1
fi
if [ ! -f "$SRC" ]; then
  echo "ERROR: file tidak ditemukan: $SRC" >&2
  exit 1
fi
if ! command -v pandoc >/dev/null 2>&1; then
  echo "ERROR: pandoc tidak ditemukan." >&2
  echo "       macOS: brew install pandoc | Linux: apt install pandoc" >&2
  echo "       Alternatif tanpa pandoc: berikan naskah .md ke user, atau tulis LaTeX manual." >&2
  exit 2
fi

mkdir -p "$OUT_DIR"
BASE="$(basename "$SRC" .md)"
DOCX="$OUT_DIR/$BASE.docx"
MD_OUT="$OUT_DIR/$BASE.md"

PANDOC_ARGS=()
[ "$NUMBER" -eq 1 ] && PANDOC_ARGS+=(--number-sections)
[ "$TOC" -eq 1 ] && PANDOC_ARGS+=(--toc --toc-depth=3)
if [ -n "$REF_DOC" ]; then
  if [ ! -f "$REF_DOC" ]; then
    echo "ERROR: reference doc tidak ditemukan: $REF_DOC" >&2
    exit 1
  fi
  PANDOC_ARGS+=(--reference-doc="$REF_DOC")
fi
[ -n "$TITLE" ] && PANDOC_ARGS+=(--metadata "title=$TITLE")

echo "== Konversi: $SRC"
echo "== Keluaran: $DOCX"
echo

# 1) bersihkan blok instruksi internal bila diminta
INPUT="$SRC"
if [ "$CLEAN" -eq 1 ]; then
  CLEAN_MD="$OUT_DIR/${BASE}_ekstrak.md"
  sed -e '/^<!-- *AGENT:/d' -e '/^<!-- *INTERNAL:/d' "$SRC" > "$CLEAN_MD"
  INPUT="$CLEAN_MD"
  echo "Naskah bersih : $CLEAN_MD"
fi

# 2) docx
pandoc "$INPUT" -o "$DOCX" \
  --from=markdown+pipe_tables+raw_html \
  --to=docx \
  "${PANDOC_ARGS[@]}" \
  || { echo "ERROR: konversi DOCX gagal" >&2; exit 3; }
echo "DOCX         : $DOCX"

# 3) daftar isi manual (markdown) bila diminta
if [ "$TOC" -eq 1 ]; then
  TOCC="$OUT_DIR/daftar_isi.md"
  {
    echo "# Daftar Isi"
    echo
    pandoc "$INPUT" --from=markdown+pipe_tables --toc --toc-depth=3 -t plain 2>/dev/null \
      | head -n 60 || true
  } > "$TOCC"
  echo "Daftar isi    : $TOCC"
fi

# 4) ringkasan struktur bab
echo
echo "== Struktur heading"
grep -n "^#\{1,2\} " "$INPUT" | sed 's/^/  /' | head -40

# 5) pemeriksaan cepat marker & placeholder
echo
echo "== Pemeriksaan cepat"
MARK_L=$(grep -o "\[L-[0-9]\+\]" "$INPUT" | sort -u | wc -l | tr -d ' ')
MARK_D=$(grep -o "\[D:[^]]*\]" "$INPUT" | sort -u | wc -l | tr -d ' ')
PLACEHOLDER=$(grep -c "\[isi " "$INPUT" || true)
echo "  marker [L-n] digunakan : $MARK_L"
echo "  marker [D:kolom]      : $MARK_D"
echo "  placeholder [isi ...] : $PLACEHOLDER"
if [ "$PLACEHOLDER" -gt 0 ]; then
  echo "  -> isi atau konfirmasi placeholder ini kepada user sebelum submit"
fi
echo
echo "Selesai."
