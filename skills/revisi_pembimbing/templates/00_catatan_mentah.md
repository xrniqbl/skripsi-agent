# 00_catatan_mentah.md

Catat **apa adanya**. Jangan dirapikan, jangan ditafsirkan. Satu baris = satu catatan.

Format: `## <sumber + tanggal>` lalu baris bernomor atau berpoin.

```markdown
## Bimbingan 2026-10-14 (ruang 302)

1. …
2. …

## Komentar Word (Skripsi_v3.docx)

- hal 12: "…"
- hal 18: "…"

## WhatsApp 2026-10-16

- …
```

Setelah semua tercatat, jalankan:

```bash
python3 scripts/parse_revisi.py 00_catatan_mentah.md --out 01_revisi.md
```

Catatan yang ambigu (mengandung "kayaknya", "coba pikir lagi", "kurang cocok") otomatis
masuk jenis `klarifikasi` — tanyakan ke pembimbing sebelum dikerjakan.
