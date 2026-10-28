# 01_revisi.md — Daftar Kerja Revisi

Status: `belum` · `sedang` · `selesai` · `ditolak-dengan-alasan`

| ID | Butir | Sumber | Lokasi | Jenis | Prioritas | Status | Bukti |
|---|---|---|---|---|---|---|---|
| R-01 |  |  |  | wajib | tinggi | belum |  |
| R-02 |  |  |  | wajib | sedang | belum |  |
| R-03 |  |  |  | format | rendah | belum |  |

## Aturan

- **Bukti wajib terukur** — angka, halaman, kutipan. Bukan "sudah"/"ok"/"beres".
- Butir `kritis` tidak boleh tetap `belum` saat verifikasi.
- Butir `klarifikasi` tidak boleh `selesai` tanpa catatan jawaban pembimbing.
- Penolakan (`ditolak-dengan-alasan`) wajib menyebut argumen metodologis + rujukan halaman.

## Verifikasi

```bash
python3 scripts/parse_revisi.py 01_revisi.md --verifikasi naskah.md
```

Kode keluar 1 bila: butir kritis belum selesai, bukti kosong/tidak terukur, klarifikasi
selesai tanpa jawaban, atau penolakan tanpa alasan.

## Catatan pengerjaan

```markdown
### R-01 — <ringkas>

- **Catatan asli**: …
- **Diagnosis**: …
- **Tindakan**: …
- **Bukti**: …
- **Status**: selesai
- **Tanggal**: YYYY-MM-DD
```
