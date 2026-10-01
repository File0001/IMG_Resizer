import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageOps
import os
import tempfile
from input_sources import InputSourceError, collect_inputs
from layout import calculate_layout, LayoutError

SUPPORTED_INPUT_TYPES = [("Gambar atau ZIP", "*.jpg *.jpeg *.png *.bmp *.webp *.zip"), ("Semua file", "*.*")]
workspace = tempfile.TemporaryDirectory()
last_invalid_files = []


def update_file_list():
    listbox.delete(0, tk.END)
    for file in selected_files:
        listbox.insert(tk.END, os.path.basename(file))
    label_jumlah.config(text=f"{len(selected_files)} gambar siap diproses")
    btn_pdf.config(state=(tk.NORMAL if selected_files else tk.DISABLED))


def add_input_paths(paths):
    global selected_files, last_invalid_files
    try:
        new_files, invalid = collect_inputs(paths, workspace)
    except InputSourceError as error:
        messagebox.showerror("Input tidak valid", str(error))
        return
    if invalid:
        last_invalid_files = invalid
        preview = "\\n".join(f"- {item}" for item in invalid[:8])
        if len(invalid) > 8:
            preview += f"\\n- ... dan {len(invalid) - 8} lainnya"
        if not messagebox.askyesno("File tidak valid", f"Ditemukan {len(invalid)} file yang diabaikan:\\n{preview}\\n\\nLanjutkan dengan {len(new_files)} gambar valid?"):
            return
    existing = set(os.path.normcase(os.path.abspath(item)) for item in selected_files)
    selected_files.extend(item for item in new_files if os.path.normcase(os.path.abspath(item)) not in existing)
    update_file_list()


def on_drop(event):
    add_input_paths(list(root.tk.splitlist(event.data)))


def clear_files():
    selected_files.clear()
    update_file_list()

def resource_path(relative_path):
    """Mencari file resource baik saat .py maupun saat menjadi .exe."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# ============================================================
# PENGATURAN A4
# ============================================================

A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297
DPI = 300

# Margin A4
# 1 cm di setiap sisi kertas
MARGIN_MM = 10

# ============================================================
# FUNGSI KONVERSI
# ============================================================

def mm_to_px(mm):
    return int(round(mm / 25.4 * DPI))


def cm_to_mm(cm):
    return float(cm) * 10


# ============================================================
# PILIH GAMBAR
# ============================================================

selected_files = []


def pilih_gambar():
    global selected_files

    files = filedialog.askopenfilenames(title="Pilih gambar atau ZIP", filetypes=SUPPORTED_INPUT_TYPES)
    if files:
        add_input_paths(list(files))


# ============================================================
# BUAT PDF
# ============================================================

def buat_pdf():
    if not selected_files:
        messagebox.showwarning(
            "Belum ada gambar",
            "Silakan pilih gambar terlebih dahulu."
        )
        return

    try:
        lebar_cm = float(entry_lebar.get())
        tinggi_cm = float(entry_tinggi.get())
        jarak_cm = float(entry_jarak.get())

        if lebar_cm <= 0 or tinggi_cm <= 0:
            raise ValueError

        if jarak_cm < 0:
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Input tidak valid",
            "Ukuran gambar dan jarak harus berupa angka yang benar."
        )
        return

    # Ukuran gambar dalam pixel pada 300 DPI
    image_width = mm_to_px(cm_to_mm(lebar_cm))
    image_height = mm_to_px(cm_to_mm(tinggi_cm))
    gap = mm_to_px(cm_to_mm(jarak_cm))

    # Ukuran A4 dalam pixel
    page_width = mm_to_px(A4_WIDTH_MM)
    page_height = mm_to_px(A4_HEIGHT_MM)

    # ============================================================
    # MARGIN A4
    # ============================================================
    # Sisakan margin 1 cm di semua sisi kertas.
    margin = mm_to_px(MARGIN_MM)

    try:
        layout = calculate_layout(
            image_width=image_width,
            image_height=image_height,
            gap=gap,
            page_width=page_width,
            page_height=page_height,
            margin=margin,
            image_count=len(selected_files),
        )
    except (ValueError, LayoutError) as e:
        messagebox.showerror("Ukuran tidak valid", str(e))
        return

    columns = layout["columns"]
    rows = layout["rows"]
    per_page = layout["per_page"]
    total_pages = layout["total_pages"]

    # Pilih lokasi PDF
    output_file = filedialog.asksaveasfilename(
        title="Simpan PDF",
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        initialfile="hasil_cetak_gambar.pdf"
    )

    if not output_file:
        return

    try:
        pages = []

        for page_number in range(total_pages):
            canvas = Image.new(
                "RGB",
                (page_width, page_height),
                "white"
            )

            start = page_number * per_page
            end = min(start + per_page, len(selected_files))

            for index, file in enumerate(selected_files[start:end]):
                try:
                    # Buka gambar dan perbaiki orientasi berdasarkan EXIF
                    # terlebih dahulu, supaya foto dari HP/kamera tidak miring.
                    img = Image.open(file)
                    img = ImageOps.exif_transpose(img).convert("RGB")

                    # ====================================================
                    # TAHAP 1: UBAH ORIENTASI GAMBAR MENJADI PORTRAIT
                    # ====================================================
                    # Jika gambar masih landscape (lebar > tinggi),
                    # putar 90 derajat sehingga menjadi portrait.
                    if img.width > img.height:
                        img = img.rotate(90, expand=True)

                    # ====================================================
                    # TAHAP 2: BARU UBAH UKURAN
                    # ====================================================
                    # Setelah orientasi menjadi portrait, gambar dipaksa
                    # ke ukuran yang diminta. Rasio asli TIDAK dipertahankan.
                    img = img.resize(
                        (image_width, image_height),
                        Image.Resampling.LANCZOS
                    )

                    column = index % columns
                    row = index // columns

                    # Mulai penempatan gambar dari area setelah margin
                    x = margin + column * (image_width + gap)
                    y = margin + row * (image_height + gap)

                    canvas.paste(img, (x, y))

                except Exception as e:
                    print(f"Gagal memproses: {file}")
                    print(e)
                    raise RuntimeError(f"Gagal memproses gambar:\n{file}\n\n{e}") from e

            pages.append(canvas)

        # Simpan semua halaman sebagai PDF
        pages[0].save(
            output_file,
            "PDF",
            resolution=DPI,
            save_all=True,
            append_images=pages[1:]
        )

        messagebox.showinfo(
            "Berhasil",
            f"PDF berhasil dibuat!\n\n"
            f"Jumlah gambar : {len(selected_files)}\n"
            f"Ukuran gambar : {lebar_cm} × {tinggi_cm} cm\n"
            f"Gambar/halaman: {per_page}\n"
            f"Jumlah halaman : {total_pages}\n\n"
            f"File:\n{output_file}"
        )

    except Exception as e:
        messagebox.showerror(
            "Gagal membuat PDF",
            f"Terjadi kesalahan:\n\n{e}"
        )


# ============================================================
# GUI
# ============================================================

root = TkinterDnD.Tk()
root.title("Cetak Gambar Massal")
root.geometry("650x600")

root.iconbitmap(resource_path("icon.ico"))
root.resizable(False, False)

font_normal = ("Segoe UI", 10)
font_title = ("Segoe UI", 16, "bold")

title = tk.Label(
    root,
    text="CETAK GAMBAR MASSAL",
    font=font_title
)
title.pack(pady=(20, 5))

subtitle = tk.Label(
    root,
    text="Pilih banyak gambar → atur ukuran → buat PDF A4",
    font=("Segoe UI", 9)
)
subtitle.pack(pady=(0, 15))

drop_zone = tk.Label(
    root,
    text="SERET GAMBAR, FOLDER, ATAU ZIP KE SINI\\n(JPG, JPEG, PNG, BMP, WEBP, ZIP)",
    relief="groove",
    bd=2,
    padx=20,
    pady=14,
    font=("Segoe UI", 10, "bold")
)
drop_zone.pack(fill="x", padx=30, pady=(0, 10))


# ------------------------------------------------------------
# Tombol pilih gambar
# ------------------------------------------------------------

frame_pilih = tk.Frame(root)
frame_pilih.pack(fill="x", padx=30)

btn_pilih = tk.Button(
    frame_pilih,
    text="PILIH GAMBAR",
    font=("Segoe UI", 10, "bold"),
    command=pilih_gambar,
    width=18,
    height=2
)
btn_pilih.pack(side="left")

btn_clear = tk.Button(
    frame_pilih,
    text="HAPUS SEMUA",
    font=("Segoe UI", 10),
    command=clear_files,
    width=14,
    height=2
)
btn_clear.pack(side="left", padx=(10, 0))

label_jumlah = tk.Label(
    frame_pilih,
    text="Belum ada gambar",
    font=font_normal
)
label_jumlah.pack(side="left", padx=15)


# ------------------------------------------------------------
# List gambar
# ------------------------------------------------------------

listbox = tk.Listbox(
    root,
    height=10,
    font=("Consolas", 9)
)
listbox.pack(
    fill="x",
    padx=30,
    pady=15
)


# ------------------------------------------------------------
# Pengaturan ukuran
# ------------------------------------------------------------

frame_setting = tk.LabelFrame(
    root,
    text=" Pengaturan ",
    font=("Segoe UI", 10, "bold"),
    padx=15,
    pady=10
)
frame_setting.pack(
    fill="x",
    padx=30,
    pady=5
)

tk.Label(
    frame_setting,
    text="Lebar gambar (cm):",
    font=font_normal
).grid(row=0, column=0, sticky="w", pady=5)

entry_lebar = tk.Entry(
    frame_setting,
    width=10,
    font=font_normal
)
entry_lebar.insert(0, "3")
entry_lebar.grid(row=0, column=1, padx=10)

tk.Label(
    frame_setting,
    text="Tinggi gambar (cm):",
    font=font_normal
).grid(row=1, column=0, sticky="w", pady=5)

entry_tinggi = tk.Entry(
    frame_setting,
    width=10,
    font=font_normal
)
entry_tinggi.insert(0, "3")
entry_tinggi.grid(row=1, column=1, padx=10)

tk.Label(
    frame_setting,
    text="Jarak antar gambar (cm):",
    font=font_normal
).grid(row=2, column=0, sticky="w", pady=5)

entry_jarak = tk.Entry(
    frame_setting,
    width=10,
    font=font_normal
)
entry_jarak.insert(0, "0.2")
entry_jarak.grid(row=2, column=1, padx=10)

tk.Label(
    frame_setting,
    text="Kertas:",
    font=font_normal
).grid(row=0, column=2, sticky="w", padx=(50, 10))

tk.Label(
    frame_setting,
    text="A4",
    font=("Segoe UI", 10, "bold")
).grid(row=0, column=3, sticky="w")


# ------------------------------------------------------------
# Tombol buat PDF
# ------------------------------------------------------------

btn_pdf = tk.Button(
    root,
    text="BUAT PDF",
    font=("Segoe UI", 12, "bold"),
    command=buat_pdf,
    width=25,
    height=2
)
btn_pdf.pack(pady=20)
btn_pdf.config(state=tk.DISABLED)


def register_drop_widgets(widget):
    try:
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind("<<Drop>>", on_drop)
    except tk.TclError:
        pass
    for child in widget.winfo_children():
        register_drop_widgets(child)


register_drop_widgets(root)
root.mainloop()
workspace.cleanup()

