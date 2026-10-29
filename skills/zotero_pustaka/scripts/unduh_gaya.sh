#!/usr/bin/env bash
# unduh_gaya.sh - Unduh berkas CSL ke styles/ dengan verifikasi.
#
# Kenapa verifikasi: gaya dependent (vancouver, harvard, dsb) TIDAK ada di
# path raw GitHub dengan namanya sendiri. Permintaan ke sana mengembalikan
# badan "404: Not Found" sepanjang 14 byte yang, kalau ditulis apa adanya,
# menimpa gaya valid dan baru meledak jauh di dalam citeproc dengan galat
# parsing yang tidak menyebut berkas mana pun.
#
# Pakai: bash scripts/unduh_gaya.sh [nama-gaya ...]
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/styles"
mkdir -p "$DIR"

GAYA=("$@")
if [ ${#GAYA[@]} -eq 0 ]; then
  GAYA=(apa ieee vancouver chicago-author-date harvard-cite-them-right nature)
fi

gagal=0
for st in "${GAYA[@]}"; do
  keluar="$DIR/$st.csl"
  kode=$(curl -sL -m 30 -o "$keluar.tmp" -w "%{http_code}" "https://www.zotero.org/styles/$st")
  ukuran=$(wc -c < "$keluar.tmp" 2>/dev/null || echo 0)
  if [ "$kode" = "200" ] && [ "$ukuran" -gt 2000 ] && head -c 200 "$keluar.tmp" | grep -q "<style"; then
    mv "$keluar.tmp" "$keluar"
    printf '  %-28s ok   %6s byte\n' "$st" "$ukuran"
  else
    rm -f "$keluar.tmp"
    printf '  %-28s GAGAL (http=%s, %s byte) - gaya lama dipertahankan\n' "$st" "$kode" "$ukuran"
    gagal=$((gagal+1))
  fi
done

# Lokal Indonesia: tanpa ini istilah "and"/"ed." tetap Inggris walau
# entri sudah benar.
LOC="$DIR/locales-id-ID.xml"
kode=$(curl -sL -m 30 -o "$LOC.tmp" -w "%{http_code}" \
  "https://raw.githubusercontent.com/citation-style-language/locales/master/locales-id-ID.xml")
if [ "$kode" = "200" ] && head -c 200 "$LOC.tmp" | grep -q "<locale"; then
  mv "$LOC.tmp" "$LOC"
  printf '  %-28s ok   %6s byte\n' "locales-id-ID.xml" "$(wc -c < "$LOC")"
else
  rm -f "$LOC.tmp"
  printf '  %-28s GAGAL (http=%s)\n' "locales-id-ID.xml" "$kode"
  gagal=$((gagal+1))
fi

echo
if [ "$gagal" -eq 0 ]; then
  echo "Semua gaya siap di $DIR"
else
  echo "$gagal berkas gagal diunduh"
fi
exit $(( gagal > 0 ))
