#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepare import-ready JSON for parts-store:
- Keeps selected fields
- Adds an "image" URL for each SKU (from --image-base + <SKU> + --image-ext)

Usage:
  python prep_import_json.py input.json output.json --image-base "/data/photos/" --image-ext ".jpg"
  python prep_import_json.py input.json output.json --image-base "https://cdn.example.com/photos/"
"""
import json
import argparse

FIELDS_TO_KEEP = [
    "Tên Tiếng Việt",
    "Model",
    "Giá bán lẻ",
    "Ngày cập nhập",
    "Thuế xuất VAT áp dụng\n1/8/2025",
]

def norm_base(base: str) -> str:
    # ensure base ends with a single slash
    return (base if base.endswith("/") else base + "/")

def main():
    ap = argparse.ArgumentParser(description="Filter product JSON and append image URLs.")
    ap.add_argument("input", help="Input JSON file (object keyed by SKU)")
    ap.add_argument("output", help="Output JSON file")
    ap.add_argument("--image-base", default="/data/photos/", help="Base URL or path prefix for images (default: /data/photos/)")
    ap.add_argument("--image-ext", default=".jpg", help="Image file extension (default: .jpg)")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    out = {}
    count = 0
    base = norm_base(args.image_base)
    for sku, attrs in data.items():
        item = {k: attrs.get(k, "") for k in FIELDS_TO_KEEP}
        item["image"] = f"{base}{sku}{args.image-ext}"
        out[sku] = item
        count += 1

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Done. Wrote {count} items to {args.output}")

if __name__ == "__main__":
    main()
