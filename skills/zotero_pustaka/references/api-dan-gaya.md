# Endpoint, Kode Respons, dan Peta Field

Catatan hasil probe langsung, bukan kutipan dokumentasi. Kode respons adalah
kontrak: jangan diterjemahkan longgar.

## Zotero Web API v3

Basis: `https://api.zotero.org`. Selalu kirim `Zotero-API-Version: 3`.

| Panggilan | Path | Catatan |
|---|---|---|
| Item pengguna | `/users/<id>/items?limit=100&start=0` | privat butuh key |
| Koleksi pengguna | `/users/<id>/collections` | aturan auth sama |
| Item grup | `/groups/<id>/items` | grup publik tanpa key |
| Item tunggal | `/users/<id>/items/<itemKey>` | |
| Anak/lampiran | `/items/<key>/children` | |

Paging: `limit` (maks 100) + `start`. Ukuran sebenarnya ada di header
`Total-Results` — badan respons tidak memberi tahu apakah itu satu halaman
atau seluruh pustaka.

### Kode respons

| Kode | Arti sebenarnya |
|---|---|
| 200 | data ada (publik, atau key sah) |
| 403 | pustaka ada tapi privat / key tidak ada / scope kurang |
| 404 | id grup tidak ada |
| 429 | rate limit; `Retry-After` di header |

Probe: `users/1`, `users/22000`, `groups/22000` → 403. `groups/9` → 404.
`users/475425` → 200. Jadi 403 memang dipakai untuk "privat", bukan "tidak ada".

### Auth

`Authorization: Bearer <API_KEY>`. Key dibuat per akun dengan scope
baca/tulis dan grup; key tanpa scope `library` read berperilaku persis seperti
tanpa key.

## Local API (Zotero 7 desktop)

`http://127.0.0.1:23119/`

| Path | Guna |
|---|---|
| `/connector/ping` | probe hidup/mati |
| `/api/users/0/items?limit=N` | pustaka pengguna lokal |
| `/api/users/0/collections` | koleksi |

Tanpa auth karena terikat pengguna desktop. Probe gagal = aplikasi tidak
jalan; tidak ada yang bisa diperbaiki dari sisi kode, pindah jalur.

## DOI content negotiation

```bash
curl -sLH 'Accept: application/vnd.citationstyles.csl+json' \
  https://doi.org/10.1038/s41586-020-2649-2
```

Mengembalikan CSL-JSON — bentuk yang langsung dimakan citeproc. `title` dan
`container-title` sering datang sebagai **list**, dan `author[]` membawa
`affiliation`, `sequence`, `role`, `ORCID` yang bukan metadata bibliografis.
`rapikan_csl()` di `zotero_client.py` membuang keduanya.

Nama field dari Crossref memakai gaya sendiri: `journal-article` bukan
`article-journal`. Tanpa pemetaan, setiap artikel jurnal jatuh ke `document`
dan gaya APA mencetaknya tanpa nama jurnal.

## Crossref

`https://api.crossref.org/works/<doi>` — envelope `message.*`.
`/works?query.bibliographic=<judul>` — cari DOI dari judul.

Catatan hasil probe: pencarian judul "array programming with numpy"
mengembalikan **review** artikel itu di urutan pertama, bukan artikelnya.
Jangan ambil hasil pertama buta; periksa `type` dan `title`.

## Zotero translate service

`POST https://translate.zotero.org/web/translate` dengan `{"url":...}` atau
`{"identifier":...}`. Di probe: **badan kosong** untuk pemanggil tanpa sesi,
bahkan dengan UA Zotero 7. Bangun pipeline di jalur DOI, perlakukan translate
sebagai bonus oportunistik: deteksi badan kosong lalu lanjut, jangan parse
string kosong jadi record.

## Peta field

### Zotero → CSL

| Zotero itemType | CSL type |
|---|---|
| journalArticle | article-journal |
| conferencePaper | paper-conference |
| bookSection | chapter |
| thesis | thesis |
| report | report |
| webpage | webpage |
| preprint | article |
| dataset | dataset |
| computerProgram | software |
| attachment / note / annotation | dilewati |

| Field Zotero | Field CSL |
|---|---|
| publicationTitle / bookTitle / proceedingsTitle | container-title |
| pages | page |
| place | publisher-place |
| date | issued.date-parts |
| creators[] | author[] (name → literal) |
| abstractNote | abstract |

### BibTeX → CSL

`article`→`article-journal`, `inproceedings`→`paper-conference`,
`book`→`book`, `incollection`→`chapter`, `phdthesis`/`mastersthesis`→`thesis`,
`techreport`→`report`, `misc`/`online`→`document`/`webpage`.

Field: `journal`→`container-title`, `pages`→`page`, `address`→`publisher-place`,
`school`→`publisher` (tesis).

### RIS → CSL

`TY  - JOUR`→`article-journal`, `BOOK`→`book`, `CHAP`→`chapter`,
`CONF`/`CPAPER`→`paper-conference`, `THES`→`thesis`, `RPRT`→`report`,
`ELEC`/`WEB`→`webpage`. `SP`+`EP` digabung jadi `page`.

## Gaya dan locale

Unduh dari `https://www.zotero.org/styles/<nama>` — server ini mengikuti
redirect ke induk gaya dependent. Jangan dari path raw repo: `vancouver` dan
kawan-kawan dependent tidak disimpan dengan namanya sendiri, dan permintaan ke
sana menulis `404: Not Found` (14 byte) menimpa gaya valid.

Ukuran wajar setelah unduh: apa ≈ 86 KB, chicago-author-date ≈ 168 KB,
ieee ≈ 18 KB, vancouver ≈ 18 KB, harvard-cite-them-right ≈ 11 KB.

Locale Indonesia: `locales-id-ID.xml` dari repo `citation-style-language/locales`.
Sudah dibundel citeproc-py, jadi cukup `CitationStylesStyle(path, locale="id-ID")`.
Tanpa itu, "editor" tetap "ed." (Inggris) bukan "ed. oleh" / "Dalam" (Indonesia).
