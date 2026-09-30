# Project Context

## Current state

- Aplikasi desktop Windows berbasis Python, Tkinter, dan Pillow.
- Fungsi utama: memilih banyak gambar, menyusun gambar pada halaman A4 portrait dengan margin 10 mm, lalu membuat PDF 300 DPI.
- Packaging menggunakan PyInstaller melalui `Cetak Gambar Massal.spec`.
- Installer menggunakan Inno Setup melalui `installer.iss`.

## Checkpoint 2026-09-30

- Perhitungan grid gambar dipindahkan ke `layout.py` agar dapat diuji tanpa GUI.
- Validasi layout mencakup ukuran tidak valid, margin tidak valid, dan gambar yang tidak muat.
- Self-check dapat dijalankan dengan `python layout.py`.

## Known limitations

- Pemrosesan PDF masih berjalan pada thread GUI.
- Semua halaman PDF masih disimpan dalam memori sebelum disimpan.
- Orientasi landscape diputar paksa ke portrait dan rasio gambar belum dipertahankan.
- Belum tersedia test suite formal, progress bar, pembatalan, dan pilihan ukuran kertas.

## Build/check commands

```text
python layout.py
python -m py_compile cetak_gambar_massal_portrait_margin_fixed.py layout.py
```
