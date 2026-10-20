# Berkontribusi (CONTRIBUTING)

Terima kasih mau berkontribusi! Repo ini fork aktif dari
`GongRzhe/Office-Word-MCP-Server` (upstream diarsipkan) dengan fokus:
live-edit Word, `smart_write.py`, dan skills penulisan akademik.

## Cara cepat mulai

1. Fork repo ini → clone fork-mu.
2. `bash install.sh` (membuat `.venv-mcp`, mendaftar MCP, memasang skills).
3. Buat branch: `git checkout -b fitur/nama-fitur`.

## Standar kontribusi

- **Satu PR = satu perubahan.** Jangan campur fitur + refactor besar.
- **Kode Python**: jelas > pintar. Fungsi baru wajib ada docstring singkat.
- **Skrip yang menyentuh file pengguna**: selalu backup dulu
  (`cp asli.docx asli_backup.docx`) dan jangan pernah menimpa input
  (tulis ke file `.baru` / `.italic` / `.final`).
- **Perubahan perilaku MCP tools**: sebutkan di PR + update tabel di README/skills.
- **Skill baru**: satu folder `skills/<nama>/SKILL.md` dengan frontmatter
  (`name`, `description`, `license`, `compatibility`) + contoh perintah yang
  bisa di-copy-paste + tabel anti-patterns.

## Tes wajib sebelum PR

```bash
# Tes repo office-skripsi (pendamping, kalau menyentuh skripsi/jurnal)
python3 -m unittest discover -s tests   # di folder office-skripsi

# Smoke test MCP (di repo ini)
PYTHONPATH=. .venv-mcp/bin/python -c "
import asyncio
from word_document_server.tools import document_tools, content_tools
async def main():
    print(await document_tools.create_document('/tmp/smoke.docx'))
    print(await content_tools.add_heading('/tmp/smoke.docx', 'Tes', level=1))
    print(await document_tools.get_document_text('/tmp/smoke.docx'))
asyncio.run(main())
"
```

PR yang lolos review akan di-squash-merge. Untuk perubahan besar,
buka **issue dulu** agar tidak bentrok dengan yang lain.

## Melaporkan bug

Sertakan: OS + versi Python + perintah yang dijalankan + pesan error lengkap
+ (kalau bisa) file `.docx` contoh minimal. Tanpa info ini issue akan
ditandai `butuh-info`.
