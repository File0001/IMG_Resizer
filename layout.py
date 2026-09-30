"""Perhitungan layout gambar pada halaman cetak."""

import math


class LayoutError(ValueError):
    """Input layout valid, tetapi tidak dapat dimuat pada halaman."""


def calculate_layout(
    image_width: int,
    image_height: int,
    gap: int,
    page_width: int,
    page_height: int,
    margin: int,
    image_count: int,
) -> dict[str, int]:
    """Menghitung grid gambar dan jumlah halaman.

    Semua ukuran menggunakan pixel. Validasi dilakukan di batas fungsi agar
    logika ini dapat digunakan tanpa dependensi Tkinter.
    """
    values = (image_width, image_height, gap, page_width, page_height, margin, image_count)
    if any(not isinstance(value, int) for value in values):
        raise ValueError("Semua ukuran dan jumlah gambar harus berupa integer.")
    if image_width <= 0 or image_height <= 0 or page_width <= 0 or page_height <= 0:
        raise ValueError("Ukuran gambar dan halaman harus lebih besar dari nol.")
    if gap < 0 or margin < 0 or image_count <= 0:
        raise ValueError("Jarak, margin, dan jumlah gambar tidak valid.")

    usable_width = page_width - (2 * margin)
    usable_height = page_height - (2 * margin)
    if usable_width <= 0 or usable_height <= 0:
        raise LayoutError("Margin lebih besar daripada area halaman.")

    columns = (usable_width + gap) // (image_width + gap)
    rows = (usable_height + gap) // (image_height + gap)
    if columns <= 0 or rows <= 0:
        raise LayoutError("Ukuran gambar tidak muat di area halaman.")

    per_page = columns * rows
    return {
        "columns": columns,
        "rows": rows,
        "per_page": per_page,
        "total_pages": math.ceil(image_count / per_page),
    }


if __name__ == "__main__":
    # Self-check sederhana yang dapat dijalankan tanpa framework eksternal.
    assert calculate_layout(354, 354, 24, 2480, 3508, 118, 10)["total_pages"] == 1
    assert calculate_layout(354, 354, 24, 2480, 3508, 118, 100)["total_pages"] > 1
    try:
        calculate_layout(3000, 3000, 0, 2480, 3508, 118, 1)
    except LayoutError:
        pass
    else:
        raise AssertionError("Ukuran yang tidak muat harus menghasilkan LayoutError")
    print("layout self-check: OK")

__all__ = ["LayoutError", "calculate_layout"]
