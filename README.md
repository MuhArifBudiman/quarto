# Quarto Report Workspace

Laporan analisis berbasis Quarto (`.qmd` / `.ipynb` / `.py`) dengan Python, dijalankan di VS Code (Windows).

## Prasyarat (sekali per mesin)

| Komponen                                   | Cara                             | Catatan                                      |
| ------------------------------------------ | -------------------------------- | -------------------------------------------- |
| Python 3.11                                | Installer resmi                  | Cek: `python --version`                      |
| Quarto                                     | Installer `.msi` dari quarto.org | Bukan paket pip. Cek: `quarto --version`     |
| VS Code + ekstensi **Quarto** & **Python** | Extensions                       | Ekstensi hanya UI, mesin render tetap Quarto |

Setelah install Quarto, **Reload Window** (`Ctrl+Shift+P` → `Developer: Reload Window`) atau tutup-buka VS Code, supaya PATH terbaca.

## Setup project

```bash
git clone <URL_REPO>
cd <NAMA_REPO>

python -m venv venv
venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Pilih interpreter venv di VS Code: `Ctrl+Shift+P` → `Python: Select Interpreter` → pilih yang di folder `venv`.

### requirements.txt (minimal)

```
pyyaml
nbformat
nbclient
jupyter_client
ipykernel
pandas
matplotlib
```

Jangan hanya `ipykernel`: script internal Quarto butuh `pyyaml`, `nbformat`, `nbclient`, `jupyter_client`.
Perbarui daftar setelah menambah library: `python -m pip freeze > requirements.txt`.

## Verifikasi

```bash
quarto check
```

Pastikan bagian Jupyter menunjuk ke Python di folder `venv`, bukan Python global.

## Render

```bash
quarto render laporan.qmd            # format sesuai YAML
quarto render laporan.ipynb
quarto render laporan.qmd --to html  # override format
quarto preview laporan.qmd           # live preview (HTML)
```

Jalankan dengan **venv aktif** (prompt diawali `(venv)`). Tombol Preview di VS Code membuka terminal sendiri; kalau error, pakai command manual di atas.

## Format output

| Format      | YAML                    | Dependensi tambahan                                    |
| ----------- | ----------------------- | ------------------------------------------------------ |
| HTML        | `format: html`          | Tidak ada                                              |
| PPTX / DOCX | `format: pptx` / `docx` | Tidak ada (Pandoc terbundel)                           |
| PDF (LaTeX) | `format: pdf`           | TinyTeX: `quarto install tinytex` (butuh akses GitHub) |
| PDF (Typst) | `format: typst`         | Bawaan Quarto versi baru (cek `quarto --version`)      |

Contoh header (raw cell paling atas di notebook, atau awal `.qmd`):

```yaml
---
title: "Judul Laporan"
author: "Nama"
format: html
execute:
  echo: false
---
```

## Opsi cell

Taruh di baris **paling atas** code cell:

```python
#| echo: false      # sembunyikan kode, output tetap tampil
#| include: false   # sembunyikan kode dan output
#| warning: false   # sembunyikan warning
```

## Masalah yang pernah muncul

| Gejala                                     | Penyebab                                                | Solusi                                                                  |
| ------------------------------------------ | ------------------------------------------------------- | ----------------------------------------------------------------------- |
| `quarto` tidak dikenali                    | PATH belum terbaca                                      | Reload Window / tutup semua terminal lalu buka baru                     |
| Bisa di cmd, tidak di PowerShell           | Tab PowerShell sesi lama                                | Buka tab PowerShell baru                                                |
| `cannot import name 'TypeAliasType'`       | Memakai Python global yang `typing_extensions`-nya lama | Aktifkan venv, atau `python -m pip install --upgrade typing_extensions` |
| `No module named 'yaml'` / `'nbformat'`    | Venv belum punya dependensi Quarto                      | `python -m pip install -r requirements.txt`                             |
| `No TeX installation was detected`         | Format PDF (LaTeX) tanpa TinyTeX                        | Pakai `format: typst`, atau `quarto install tinytex`                    |
| `504 Gateway Timeout` saat install TinyTeX | Akses ke GitHub tertahan (jaringan/proxy)               | Pakai Typst, atau tanya IT soal akses GitHub                            |

## Catatan lintas mesin (pribadi ↔ kantor)

- TinyTeX dan Quarto **tidak ikut** di Git dan venv. Install ulang di tiap mesin.
- Jangan commit folder `venv/`, hasil render, dan cache. Contoh `.gitignore`:

```
venv/
*_files/
.quarto/
*.html
*.pdf
*.pptx
/.ipynb_checkpoints/
```

- Kalau data mengandung data nasabah/sensitif, **jangan** commit ke repo pribadi. Simpan di luar repo dan baca lewat path lokal atau variabel lingkungan.
- Jaringan kantor bisa membatasi `pip`, GitHub, atau unduhan TinyTeX. Cek lebih dulu sebelum mengandalkan PDF via LaTeX.
