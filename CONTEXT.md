# Project Context — Cetak Gambar Massal

> Dokumen checkpoint teknis proyek. Perbarui bagian ini setiap kali alur,
> arsitektur, fitur, packaging, atau batasan proyek berubah.

## 1. Identitas dan tujuan proyek

- **Nama aplikasi:** Cetak Gambar Massal.
- **Jenis:** aplikasi desktop Windows dengan GUI.
- **Tujuan:** memilih banyak file gambar, menyusun gambar dalam grid pada halaman A4, lalu menghasilkan satu file PDF siap cetak.
- **Bahasa antarmuka:** Bahasa Indonesia.
- **Mode halaman saat ini:** A4 portrait.
- **Kualitas output saat ini:** 300 DPI.
- **Status:** prototype/aplikasi fungsional yang sudah dapat dibuild menjadi executable dan installer, tetapi belum sepenuhnya production-ready.

## 2. Teknologi dan dependency

- **Python:** source ditulis untuk Python 3; versi environment belum dikunci.
- **GUI:** `tkinter`, `filedialog`, dan `messagebox`.
- **Pemrosesan gambar/PDF:** Pillow (`PIL.Image`, `PIL.ImageOps`).
- **Packaging executable:** PyInstaller.
- **Installer Windows:** Inno Setup.
- **Test framework:** belum digunakan; self-check memakai `assert` pada `layout.py`.
- **Dependency manifest:** `requirements.txt` tersedia; `tkinterdnd2==0.6.3` digunakan untuk drag & drop.

## 3. Struktur file

```text
IMG_Resizer/
├── cetak_gambar_massal_portrait_margin_fixed.py  # aplikasi utama dan GUI
├── layout.py                                     # kalkulasi layout yang dapat diuji
├── CONTEXT.md                                   # dokumentasi/checkpoint proyek
├── Cetak Gambar Massal.spec                     # konfigurasi PyInstaller
├── installer.iss                                # konfigurasi Inno Setup
├── icon.ico                                     # icon aplikasi dan installer
├── build/                                       # artefak sementara PyInstaller
├── dist/                                        # executable hasil PyInstaller
└── installer/                                   # installer hasil Inno Setup
```

Artefak yang tersedia:

- `dist\\Cetak Gambar Massal.exe` — executable Windows hasil build.
- `installer\\Setup_Cetak_Gambar_Massal.exe` — installer Windows hasil build.
- `build` dan `dist` adalah output build, bukan source utama.

## 4. Alur kerja aplikasi

1. Aplikasi membuat window Tkinter berjudul `Cetak Gambar Massal`.
2. Pengguna menekan **PILIH GAMBAR**.
3. `askopenfilenames()` memilih JPG, JPEG, PNG, BMP, dan WEBP; opsi semua file juga tersedia.
4. Path disimpan pada state global `selected_files` dan nama file ditampilkan pada `Listbox`.
5. Pengguna mengisi lebar, tinggi, dan jarak dalam cm. Default: `3`, `3`, dan `0.2`.
6. Nilai dikonversi ke pixel pada 300 DPI.
7. Layout A4 dihitung dengan margin 10 mm di setiap sisi.
8. Pengguna memilih lokasi PDF; nama default `hasil_cetak_gambar.pdf`.
9. Setiap gambar dibuka, diperbaiki EXIF-nya, landscape diputar ke portrait, lalu di-resize paksa ke ukuran target dan ditempel pada canvas putih.
10. Semua canvas disimpan sebagai PDF multi-halaman menggunakan Pillow.
11. Dialog sukses atau error ditampilkan kepada pengguna.

## 5. Konstanta dan aturan layout

Pada aplikasi utama:

- `A4_WIDTH_MM = 210`
- `A4_HEIGHT_MM = 297`
- `DPI = 300`
- `MARGIN_MM = 10`
- Ukuran A4 pada 300 DPI sekitar `2480 × 3508` pixel.

Rumus konversi:

```text
mm_to_px(mm) = round(mm / 25.4 × DPI)
cm_to_mm(cm) = cm × 10
```

Perhitungan di `layout.py`:

```text
usable_width  = page_width  - 2 × margin
usable_height = page_height - 2 × margin
columns = (usable_width + gap) // (image_width + gap)
rows    = (usable_height + gap) // (image_height + gap)
per_page = columns × rows
total_pages = ceil(image_count / per_page)
```

`calculate_layout()` mengembalikan `columns`, `rows`, `per_page`, dan `total_pages`. `LayoutError` dipakai jika gambar tidak muat atau area halaman invalid.

## 6. Modul dan tanggung jawab

### `cetak_gambar_massal_portrait_margin_fixed.py`

Masih menggabungkan GUI, state, validasi input, pemrosesan gambar, pembuatan PDF, dan konfigurasi tampilan.

Fungsi utama:

- `resource_path(relative_path)` — mencari resource source/PyInstaller.
- `mm_to_px(mm)` — konversi millimeter ke pixel.
- `cm_to_mm(cm)` — konversi centimeter ke millimeter.
- `pilih_gambar()` — memilih dan menampilkan daftar file.
- `buat_pdf()` — memvalidasi input, menghitung layout, mengolah gambar, dan menyimpan PDF.

GUI dibuat langsung pada level module dan dimulai dengan `root.mainloop()`.

### `layout.py`

Modul tanpa dependensi GUI untuk kalkulasi layout dan validasi dasar. Jalankan self-check dengan:

```text
python layout.py
```

## 7. Validasi dan error handling saat ini

Validasi input GUI:

- Tidak boleh membuat PDF jika belum memilih gambar.
- Lebar dan tinggi harus lebih besar dari nol.
- Jarak tidak boleh negatif.
- Nilai harus dapat dikonversi ke `float`.
- Layout ditolak jika gambar tidak muat pada area A4.

Validasi `layout.py`:

- Semua argumen ukuran dan jumlah gambar harus integer.
- Ukuran gambar dan halaman harus positif.
- Gap dan margin tidak boleh negatif.
- Jumlah gambar harus lebih besar dari nol.
- Margin tidak boleh menghabiskan area halaman.
- Gambar yang tidak muat menghasilkan `LayoutError`.

Error pemrosesan file ditangkap dan ditampilkan melalui `messagebox`. Error internal juga dicetak dengan `print()`, tetapi executable dibuild dengan `console=False`, sehingga output console tidak selalu terlihat.

## 8. Packaging dan distribusi

### PyInstaller — `Cetak Gambar Massal.spec`

- Entry point: `cetak_gambar_massal_portrait_margin_fixed.py`.
- Executable windowed, tanpa console.
- Nama executable: `Cetak Gambar Massal`.
- Icon: `icon.ico`, juga disertakan sebagai data bundle.
- UPX diaktifkan jika tersedia.
- Debug PyInstaller dinonaktifkan.

### Inno Setup — `installer.iss`

- Versi installer: `1.0.0`.
- Default install directory: `{autopf}\\Cetak Gambar Massal`.
- Output: folder `installer`, nama `Setup_Cetak_Gambar_Massal.exe`.
- Shortcut Start Menu dibuat.
- Shortcut Desktop opsional dan tidak dicentang secara default.
- Installer membutuhkan hak administrator (`PrivilegesRequired=admin`).
- Wizard memakai resource English bawaan Inno Setup walaupun aplikasi berbahasa Indonesia.

## 9. Hal yang sudah baik

- Mendukung pemilihan banyak gambar.
- Menggunakan EXIF transpose sebelum pemrosesan gambar.
- Menggunakan resampling `LANCZOS` untuk resize.
- Mendukung PDF multi-halaman.
- Memiliki margin cetak A4.
- Menolak layout jika gambar terlalu besar.
- Perhitungan layout terpisah dari GUI dan dapat diuji tanpa window.
- Executable dan installer sudah tersedia.
- Tidak ditemukan credential, API key, password, atau secret pada source yang dianalisis.

## 10. Kekurangan dan risiko yang diketahui

### Prioritas tinggi

1. **Thread GUI terblokir.** Semua pemrosesan gambar/PDF berjalan pada event loop Tkinter; aplikasi dapat tampak hang pada jumlah file besar.
2. **Memori besar.** Semua canvas halaman disimpan dalam list `pages` sebelum PDF disimpan; banyak halaman dapat menyebabkan RAM tinggi atau `MemoryError`.
3. **Rasio gambar rusak.** `resize()` langsung ke ukuran target sehingga gambar dapat terlihat gepeng/melebar.
4. **Orientasi dipaksa portrait.** Gambar landscape diputar 90 derajat sehingga orientasi asli tidak dipertahankan.
5. **Error terlalu umum.** `except Exception` menyulitkan pembedaan file rusak, permission error, disk penuh, dan error Pillow.
6. **Tanpa progress/pembatalan.** Pengguna tidak mengetahui progres dan tidak dapat membatalkan proses panjang.

### Prioritas menengah

1. Belum ada konfirmasi khusus sebelum menimpa PDF yang sudah ada.
2. File non-gambar masih dapat dipilih melalui `*.*` dan baru gagal saat diproses.
3. `nan`, `inf`, nilai ekstrem, dan batas maksimum belum divalidasi eksplisit.
4. Hanya mendukung A4 portrait; belum mendukung F4, Letter, landscape, custom paper, atau margin custom.
5. Source masih monolitik dan menggunakan state global GUI.
6. Belum tersedia `requirements.txt`; versi dependency belum dikunci.
7. Belum ada test suite formal untuk layout, image processing, dan PDF.
8. Fallback resource menggunakan `except Exception` yang terlalu luas.

### Prioritas rendah/operasional

1. Belum ada logging file untuk executable GUI.
2. Belum ada dokumentasi pengguna terpisah.
3. Versi installer dan aplikasi belum dikelola dari satu sumber.
4. Folder output build dan installer perlu dijaga agar tidak masuk source control.
5. Installer menggunakan hak administrator meskipun mungkin tidak selalu diperlukan.

## 11. Strategi pengembangan yang disarankan

1. Pertahankan `layout.py` sebagai logika terisolasi dan tambah test layout.
2. Perbaiki validasi numerik dengan `math.isfinite()` dan batas input wajar.
3. Tambahkan mode rasio gambar (`fit` atau `crop`) dan pertahankan orientasi asli.
4. Validasi seluruh file input sebelum membuat halaman.
5. Pindahkan pemrosesan PDF ke worker thread; update GUI hanya melalui mekanisme Tkinter yang aman.
6. Tambahkan status/progress dan pembatalan.
7. Kurangi penggunaan memori dengan strategi temporary/batch page yang aman.
8. Tambahkan pilihan ukuran/orientasi kertas bila kebutuhan bisnis sudah jelas.
9. Tambahkan `requirements.txt`, prosedur build, dan test otomatis.

Prinsip proyek: KISS, YAGNI, perubahan minimum, validasi pada trust boundary, dan jangan menambah abstraksi sebelum kebutuhan nyata.

## 12. Checkpoint perubahan

### 2026-09-30 — Analisis dan ekstraksi layout

- `CONTEXT.md` dibuat sebagai checkpoint proyek.
- Perhitungan grid dipindahkan dari fungsi GUI ke `layout.py`.
- `LayoutError` ditambahkan untuk kondisi gambar tidak muat atau area halaman invalid.
- `calculate_layout()` digunakan kembali oleh aplikasi utama.
- Self-check tanpa framework ditambahkan ke `layout.py`.
- Syntax check source utama dan modul layout berhasil.

### 2026-09-30 — Dokumentasi proyek diperluas

- Tujuan, alur aplikasi, struktur file, aturan layout, packaging, validasi, risiko, dan roadmap pengembangan didokumentasikan di file ini.

### 2026-10-01 — Input gambar, folder, ZIP, dan drag & drop

- `tkinterdnd2==0.6.3` ditambahkan untuk drag & drop pada seluruh widget aplikasi.
- File gambar, folder rekursif, dan ZIP masuk ke pipeline input terpadu.
- ZIP memakai `zipfile` dan temporary directory dengan batas 2.000 entry, 100 MB per file, dan 1 GB total ekstraksi.
- Path traversal ditolak; gambar divalidasi Pillow; input duplikat dihapus.
- File invalid meminta konfirmasi sebelum melanjutkan.
- `requirements.txt` dan hidden import PyInstaller diperbarui.

### 2026-09-30 — Baseline arsitektur sistem

- `ARCHITECTURE.md` ditambahkan.
- Arsitektur ditetapkan sebagai desktop lokal tanpa server, API network, atau database.
- Model data runtime, struktur folder, diagram Mermaid, teknologi yang disetujui, quality gates, serta keputusan yang belum boleh diasumsikan didokumentasikan.

## 13. Perintah verifikasi

Dari root proyek `e:\Master Fix\IMG_Resizer`:

```text
python layout.py
python -m py_compile cetak_gambar_massal_portrait_margin_fixed.py layout.py
```

Hasil self-check yang diharapkan:

```text
layout self-check: OK
```

Uji manual aplikasi:

1. Jalankan source utama pada environment yang memiliki Pillow.
2. Pilih beberapa JPG/PNG.
3. Gunakan default `3 × 3 cm` dan jarak `0.2 cm`.
4. Buat PDF ke lokasi baru.
5. Pastikan jumlah halaman, jumlah gambar per halaman, margin, dan orientasi output sesuai kebutuhan.
6. Uji input kosong, angka negatif, ukuran terlalu besar, file rusak, dan lokasi output yang tidak dapat ditulis.

## 14. Batasan dokumentasi

- `CONTEXT.md` tidak tersedia sebelum checkpoint pertama dibuat.
- Repository Git belum aktif/terdeteksi pada analisis awal; workflow release perlu diverifikasi kembali.
- Versi Python, Pillow, PyInstaller, dan Inno Setup untuk artefak terakhir belum didokumentasikan secara terverifikasi.

