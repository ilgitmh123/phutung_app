#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_changes_no_git.py
- Edits your Django project **without git** to enable serving /data/photos and
  to auto-populate product image links during JSON import.
- Makes .bak backups next to each edited file.
- Idempotent: safe to run multiple times.

USAGE:
  1) Put this script in the folder that contains the "backend" directory.
  2) Run:  python apply_changes_no_git.py
"""

from pathlib import Path
import re, shutil, os, sys

ROOT = Path.cwd()
BACKEND = ROOT / "backend"
if not BACKEND.exists():
    print("❌ Không tìm thấy thư mục 'backend' trong thư mục hiện tại.")
    print("   Hãy cd vào thư mục parts-store rồi chạy lại:")
    print("   python apply_changes_no_git.py")
    sys.exit(1)

def backup(fp: Path):
    fb = fp.with_suffix(fp.suffix + ".bak")
    if not fb.exists():
        shutil.copy2(fp, fb)
        print(f"→ Backup: {fb.name}")
    else:
        print(f"→ Đã có backup: {fb.name}")

def patch_settings():
    fp = BACKEND / "core" / "settings.py"
    src = fp.read_text(encoding="utf-8")
    if "/data/photos/" in src and "MEDIA_URL" in src and "MEDIA_ROOT" in src:
        print("settings.py: OK (đã có MEDIA_*)")
        return
    backup(fp)
    add = (
        "\n\n# === Added: media settings for serving product photos in dev ===\n"
        "MEDIA_URL = \"/data/photos/\"\n"
        "MEDIA_ROOT = BASE_DIR / \"data\" / \"photos\"\n"
    )
    fp.write_text(src.rstrip() + add, encoding="utf-8")
    print("settings.py: ĐÃ THÊM MEDIA_URL & MEDIA_ROOT")

def patch_urls():
    fp = BACKEND / "core" / "urls.py"
    src = fp.read_text(encoding="utf-8")
    changed = False

    if "from django.conf import settings" not in src:
        src = "from django.conf import settings\n" + src
        changed = True
    if "from django.conf.urls.static import static" not in src:
        src = "from django.conf.urls.static import static\n" + src
        changed = True

    # Ensure urlpatterns has the static() tail
    if "static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)" not in src:
        # Append at the end safely
        src = src.rstrip() + "\n] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\n"
        changed = True

    if changed:
        backup(fp)
        fp.write_text(src, encoding="utf-8")
        print("urls.py: ĐÃ THÊM import + static(...)")
    else:
        print("urls.py: OK (đã có cấu hình static cho MEDIA)")

def patch_utils_import():
    fp = BACKEND / "catalog" / "utils_import.py"
    src = fp.read_text(encoding="utf-8")
    orig = src

    if "import os" not in src:
        # insert after first import line
        src = re.sub(r"(^import\s+[^\n]+\n)", r"\1import os\n", src, count=1, flags=re.M)

    if "IMAGE_BASE_URL" not in src:
        # place near the top after ALIAS or after imports
        # try to insert after the ALIAS mapping; otherwise after imports
        if "ALIAS" in src:
            src = re.sub(r"(ALIAS\s*=\s*\{[\s\S]*?\}\s*)", r"\1\nIMAGE_BASE_URL = os.getenv(\"IMAGE_BASE_URL\", \"/data/photos/\")\n", src, count=1, flags=re.M)
        else:
            src = re.sub(r"(^(\s*import[^\n]+\n)+)", r"\1IMAGE_BASE_URL = os.getenv(\"IMAGE_BASE_URL\", \"/data/photos/\")\n", src, count=1, flags=re.M)

    # Ensure normalize_item injects image
    if "def normalize_item" in src:
        # add two lines before attrs = { ... }
        if "image_in = raw.get(\"image\")" not in src:
            src = re.sub(
                r"(\n\s*attrs\s*=\s*\{)",
                "\n    image_in = raw.get(\"image\")\n    image_url = image_in if image_in else f\"{IMAGE_BASE_URL}{sku}.jpg\"\n\\1",
                src,
                count=1
            )
        # ensure "image": image_url in attrs dict
        # if attrs already contains "image": something, skip
        if re.search(r'attrs\s*=\s*\{[^\}]*"image"\s*:', src, flags=re.S) is None:
            src = re.sub(
                r'(attrs\s*=\s*\{)([^}]*)\}',
                lambda m: m.group(1) + m.group(2).rstrip() + (", " if m.group(2).strip() else "") + '"image": image_url}',
                src,
                count=1,
                flags=re.S
            )

    if src != orig:
        backup(fp)
        fp.write_text(src, encoding="utf-8")
        print("utils_import.py: ĐÃ BỔ SUNG tự tạo link ảnh & biến IMAGE_BASE_URL")
    else:
        print("utils_import.py: OK (đã có logic image)")

def main():
    print("== Bắt đầu vá project (không dùng git) ==")
    patch_settings()
    patch_urls()
    patch_utils_import()
    print("✅ Hoàn tất. Giờ bạn đặt ảnh vào backend/data/photos/ và import JSON.")

if __name__ == "__main__":
    main()
