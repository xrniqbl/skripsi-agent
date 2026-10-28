# Template kerja — salin ke folder proyek pengguna

Empat berkas ini adalah kerangka yang diisi pada FASE 1–6. Salin ke folder kerja proyek
(mis. `~/skripsi/`), bukan dibiarkan di folder skill.

```bash
mkdir -p ~/skripsi
cp templates/00_fenomena.md      ~/skripsi/
cp templates/01_masalah.md       ~/skripsi/
cp templates/02_gap.md           ~/skripsi/
cp templates/kontrak_topik.json  ~/skripsi/
```

| Berkas | Diisi pada | Diperiksa oleh |
|---|---|---|
| `00_fenomena.md` | FASE 1 | manual (minimal 8 fenomena) |
| `01_masalah.md` | FASE 2 | `peta_fenomena.py` |
| `02_gap.md` | FASE 3 | `literature_probe.py` |
| `03_kandidat.json` | FASE 4 | `skor_topik.py` |
| `04_kandidat_judul.md` | FASE 5 | `judul_check.py` |
| `kontrak_topik.json` | FASE 6 | dibaca `proposal_skripsi` STEP 0 |
