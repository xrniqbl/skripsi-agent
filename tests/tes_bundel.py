#!/usr/bin/env python3
"""Tes regresi bundel Skripsi Agent.

Pemakaian: python3 tests/tes_bundel.py [root-bundel]
Memeriksa kelengkapan berkas inti, frontmatter semua SKILL.md, keterbacaan YAML
format_kampus, uji asap generator+auditor format_kampus, dan penjaga konten:
bundel tidak boleh memuat data pribadi/proposal pengguna mana pun.
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else
                       os.path.join(os.path.dirname(__file__), '..'))
gagal = []


def cek(nama, ok, detail=''):
    print(('LULUS ' if ok else 'GAGAL ') + nama + (f' — {detail}' if detail else ''))
    if not ok:
        gagal.append(nama)


for f in ('README.md', 'SKILL.md', 'INSTALL.md', 'CREDITS.md', 'VERSION', 'CHANGELOG.md'):
    cek(f'berkas inti {f}', os.path.isfile(os.path.join(ROOT, f)))

skills_dir = os.path.join(ROOT, 'skills')
skill_files = []
for base, _dirs, files in os.walk(skills_dir):
    if 'SKILL.md' in files:
        skill_files.append(os.path.join(base, 'SKILL.md'))
cek('jumlah SKILL.md (termasuk salinan upstream) >= 19', len(skill_files) >= 19,
    f'{len(skill_files)} ditemukan')

# Metadata tiap skill tingkat atas: frontmatter SKILL.md ATAU skill.yaml di sisinya
# (adaptasi Muse memindahkan frontmatter upstream ke skill.yaml).
fm_ok, fm_nama = 0, []
top_dirs = [d for d in sorted(os.listdir(skills_dir))
            if os.path.isfile(os.path.join(skills_dir, d, 'SKILL.md'))]
for d in top_dirs:
    folder = os.path.join(skills_dir, d)
    teks = open(os.path.join(folder, 'SKILL.md'), encoding='utf8').read()
    m = re.match(r'^---\n(.*?)\n---', teks, re.S)
    via_fm = bool(m and re.search(r'^name:', m.group(1), re.M)
                  and re.search(r'^description:', m.group(1), re.M))
    sy = os.path.join(folder, 'skill.yaml')
    via_yaml = False
    if os.path.isfile(sy):
        isi = open(sy, encoding='utf8').read()
        via_yaml = bool(re.search(r'^name:', isi, re.M) and re.search(r'^description:', isi, re.M))
    if via_fm or via_yaml:
        fm_ok += 1
    else:
        fm_nama.append(d)
cek('metadata name+description semua skill tingkat atas', fm_ok == len(top_dirs),
    'bermasalah: ' + ', '.join(fm_nama) if fm_nama else f'{fm_ok} skill')

try:
    import yaml
    for rel in ('skills/format_kampus/format-profile-template.yaml',
                'skills/format_kampus/presets/universitas-contoh.yaml'):
        yaml.safe_load(open(os.path.join(ROOT, rel), encoding='utf8'))
    cek('YAML format_kampus terbaca', True)
except Exception as e:  # noqa: BLE001
    cek('YAML format_kampus terbaca', False, str(e))

fk = os.path.join(ROOT, 'skills', 'format_kampus')
with tempfile.TemporaryDirectory() as tmp:
    tpl = os.path.join(tmp, 'tpl.docx')
    r1 = subprocess.run([sys.executable, os.path.join(fk, 'scripts', 'buat_template_docx.py'),
                         os.path.join(fk, 'presets', 'universitas-contoh.yaml'), tpl],
                        capture_output=True, text=True)
    r2 = subprocess.run([sys.executable, os.path.join(fk, 'scripts', 'audit_docx.py'),
                         tpl, os.path.join(fk, 'presets', 'universitas-contoh.yaml')],
                        capture_output=True, text=True) if r1.returncode == 0 else None
    cek('uji asap format_kampus (generator -> auditor)',
        r1.returncode == 0 and r2 is not None and r2.returncode == 0,
        (r1.stderr or '')[-200:] + ((r2.stderr or '')[-200:] if r2 else ''))

ba = os.path.join(ROOT, 'skills', 'bahasa_akademik')
with tempfile.TemporaryDirectory() as tmp:
    buruk = os.path.join(tmp, 'buruk.md')
    baik = os.path.join(tmp, 'baik.md')
    open(buruk, 'w', encoding='utf8').write(
        'Saya melakukan analisa dengan metoda ini agar supaya hasilnya sangat bagus sekali.\n')
    open(baik, 'w', encoding='utf8').write(
        'Penelitian ini menganalisis data dengan metode yang telah ditentukan.\n')
    rb = subprocess.run([sys.executable, os.path.join(ba, 'scripts', 'cek_bahasa.py'), buruk],
                        capture_output=True, text=True)
    rk = subprocess.run([sys.executable, os.path.join(ba, 'scripts', 'cek_bahasa.py'), baik],
                        capture_output=True, text=True)
    cek('pemeriksa bahasa akademik (buruk gagal, baik lulus)',
        rb.returncode == 1 and rk.returncode == 0,
        f'kode {rb.returncode}/{rk.returncode}')

with tempfile.TemporaryDirectory() as tmp:
    tpl = os.path.join(tmp, 'tpl.docx')
    preset = os.path.join(fk, 'presets', 'universitas-contoh.yaml')
    r1 = subprocess.run([sys.executable, os.path.join(fk, 'scripts', 'buat_template_docx.py'),
                         preset, tpl], capture_output=True, text=True)
    r2 = subprocess.run([sys.executable, os.path.join(fk, 'scripts', 'audit_rapi.py'), tpl],
                        capture_output=True, text=True) if r1.returncode == 0 else None
    cek('audit kerapian lulus pada template', r2 is not None and r2.returncode == 0,
        (r2.stdout or '')[-160:] if r2 else 'generator gagal')
    if r1.returncode == 0:
        from docx import Document
        d = Document(tpl)
        xml = d.styles['TOC 1'].element.xml
        cek('style TOC 1 berdot leader + judul keep-with-next',
            'leader="dot"' in xml and 'keepNext' in d.styles['Heading 1'].element.xml)

    if r1.returncode == 0 and subprocess.run(['which', 'soffice'], capture_output=True).returncode == 0:
        from docx import Document as Doc2
        mini = os.path.join(tmp, 'mini.docx')
        d = Doc2(tpl)
        d.add_heading('DAFTAR ISI', level=1)
        d.add_heading('BAB I PENDAHULUAN', level=1)
        d.add_heading('1.1 Latar Belakang', level=2)
        d.add_paragraph('Isi latar belakang penelitian.')
        d.save(mini)
        r3 = subprocess.run([sys.executable, os.path.join(fk, 'scripts', 'buat_daftar_isi.py'),
                             mini, preset], capture_output=True, text=True)
        isi = ''
        if r3.returncode == 0:
            isi = Doc2(mini).element.xml
        cek('pembuat daftar isi berjalan (field TOC + entri bertab)',
            r3.returncode == 0 and 'TOC' in isi and '<w:tab' in isi,
            (r3.stdout + r3.stderr)[-160:])
    else:
        cek('pembuat daftar isi berjalan (field TOC + entri bertab)', True, 'dilewati: soffice tidak ada')

TERLARANG = ('komenin', 'adhirajasa', 'komenin.id')
temuan = []
for base, _dirs, files in os.walk(ROOT):
    if '.git' in base or os.path.basename(base) == 'tests':
        continue
    for f in files:
        p = os.path.join(base, f)
        try:
            isi = open(p, encoding='utf8', errors='strict').read().lower()
        except (UnicodeDecodeError, ValueError):
            continue
        if any(t in isi for t in TERLARANG):
            temuan.append(os.path.relpath(p, ROOT))
cek('penjaga konten: tanpa data pribadi/proposal pengguna', not temuan,
    'ditemukan di: ' + ', '.join(temuan) if temuan else '')

print(f"\nRingkasan: {'GAGAL ' + str(len(gagal)) if gagal else 'SEMUA LULUS'}")
sys.exit(1 if gagal else 0)
