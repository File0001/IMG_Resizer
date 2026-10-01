"""Normalisasi sumber gambar lokal: file, folder, dan ZIP."""
from __future__ import annotations

import hashlib
import os
import posixpath
import tempfile
import zipfile
from pathlib import Path

from PIL import Image

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
MAX_ZIP_ENTRIES = 2000
MAX_MEMBER_SIZE = 100 * 1024 * 1024
MAX_TOTAL_EXTRACTED = 1024 * 1024 * 1024


class InputSourceError(Exception):
    """Kesalahan yang dapat dijelaskan kepada pengguna."""


def _is_image(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS


def _validate_image(path: Path) -> bool:
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except (OSError, ValueError):
        return False


def _safe_member_path(root: Path, member_name: str) -> Path:
    normalized = posixpath.normpath(member_name.replace("\\", "/"))
    if normalized in (".", "") or normalized.startswith("../") or normalized == ".." or normalized.startswith("/"):
        raise InputSourceError(f"ZIP memiliki path berbahaya: {member_name}")
    target = (root / Path(*normalized.split("/"))).resolve()
    if os.path.commonpath((str(root.resolve()), str(target))) != str(root.resolve()):
        raise InputSourceError(f"ZIP memiliki path berbahaya: {member_name}")
    return target


def _identity(path: Path) -> str:
    resolved = str(path.resolve()).casefold()
    try:
        stat = path.stat()
        return f"{resolved}:{stat.st_size}:{stat.st_mtime_ns}"
    except OSError:
        return resolved


def _collect_folder(folder: Path) -> tuple[list[Path], list[str]]:
    valid, invalid = [], []
    for path in sorted(folder.rglob("*")):
        if path.is_file() and _is_image(path):
            (valid if _validate_image(path) else invalid).append(path)
    return valid, invalid


def _extract_zip(archive: Path, root: Path) -> tuple[list[Path], list[str]]:
    try:
        with zipfile.ZipFile(archive) as zf:
            members = [item for item in zf.infolist() if not item.is_dir()]
            if len(members) > MAX_ZIP_ENTRIES:
                raise InputSourceError(f"ZIP melebihi batas {MAX_ZIP_ENTRIES} file.")
            for item in members:
                _safe_member_path(root, item.filename)
            selected = [item for item in members if _is_image(Path(item.filename))]
            total = 0
            valid, invalid = [], []
            for item in selected:
                if item.file_size > MAX_MEMBER_SIZE:
                    invalid.append(item.filename + " (terlalu besar)")
                    continue
                total += item.file_size
                if total > MAX_TOTAL_EXTRACTED:
                    raise InputSourceError("Total isi ZIP melebihi batas 1 GB.")
                target = _safe_member_path(root, item.filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(item) as source, target.open("wb") as destination:
                    destination.write(source.read(MAX_MEMBER_SIZE + 1))
                if target.stat().st_size > MAX_MEMBER_SIZE or not _validate_image(target):
                    invalid.append(item.filename)
                else:
                    valid.append(target)
            return valid, invalid
    except zipfile.BadZipFile as exc:
        raise InputSourceError(f"ZIP rusak: {archive.name}") from exc


def collect_inputs(paths: list[str], workspace: tempfile.TemporaryDirectory) -> tuple[list[str], list[str]]:
    """Kumpulkan gambar valid, deduplikasi, dan kembalikan warning invalid."""
    valid_paths, invalid = [], []
    seen = set()
    extraction_root = Path(workspace.name)
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            candidates, errors = _collect_folder(path)
        elif path.is_file() and path.suffix.lower() == ".zip":
            zip_root = extraction_root / hashlib.sha256(str(path.resolve()).encode()).hexdigest()
            zip_root.mkdir(parents=True, exist_ok=True)
            candidates, errors = _extract_zip(path, zip_root)
        elif path.is_file() and _is_image(path):
            candidates, errors = ([path], []) if _validate_image(path) else ([], [str(path)])
        else:
            candidates, errors = [], [str(path)]
        invalid.extend(errors)
        for candidate in candidates:
            key = _identity(candidate)
            if key not in seen:
                seen.add(key)
                valid_paths.append(str(candidate))
    return valid_paths, invalid


def self_check() -> None:
    """Self-check ringkas untuk path traversal dan deduplikasi."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        safe = _safe_member_path(root, "folder/image.jpg")
        assert str(safe).startswith(str(root.resolve()))
        try:
            _safe_member_path(root, "../../outside.jpg")
        except InputSourceError:
            pass
        else:
            raise AssertionError("path traversal tidak ditolak")
        image = root / "image.jpg"
        Image.new("RGB", (2, 2), "white").save(image)
        workspace = tempfile.TemporaryDirectory()
        paths, invalid = collect_inputs([str(image), str(image)], workspace)
        assert len(paths) == 1 and not invalid
        workspace.cleanup()


if __name__ == "__main__":
    self_check()
    print("input sources self-check: OK")


__all__ = ["InputSourceError", "collect_inputs"]
