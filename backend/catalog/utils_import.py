# backend/catalog/utils_import.py

import os
import re

IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL", "/data/photos/")

def _parse_price(x) -> int:
    if x is None:
        return 0
    s = re.sub(r"[^\d]", "", str(x))
    return int(s) if s else 0

def _parse_percent(x) -> int:
    if x is None:
        return 0
    s = re.sub(r"[^\d.]", "", str(x))
    try:
        v = float(s)
        return int(round(v))
    except Exception:
        return 0

def _norm_image(value: str | None, sku: str) -> str:
    """
    Chuẩn hoá đường dẫn ảnh:
    - Nếu http(s) → giữ nguyên
    - Nếu có backslash → đổi thành '/'
    - Nếu không bắt đầu bằng '/' → thêm '/'
    - Nếu thiếu → IMAGE_BASE_URL + '<SKU>.jpg'
    """
    if not value:
        return f"{IMAGE_BASE_URL.rstrip('/')}/{sku}.jpg"
    v = str(value).strip()
    if v.startswith("http://") or v.startswith("https://"):
        return v
    v = v.replace("\\", "/")
    if not v.startswith("/"):
        v = "/" + v
    return v

def normalize_item(sku: str, raw: dict, default_brand: str = "Honda") -> dict:
    """
    Kỳ vọng raw dạng:
    {
        "Tên Tiếng Việt": "...",       # có thể = "0" => coi như rỗng
        "Model": "K0GA" | "0",
        "Giá bán lẻ": "1,503,360" | "",
        "Ngày cập nhập": "01/09/2025 07:00" | "",
        "Thuế xuất VAT áp dụng\n1/8/2025": "8%" | "",
        "image": "data/photos\\SKU.jpg" | "/data/photos/SKU.jpg" | "http..."
        # (có thể có thêm "Tên tiếng Anh" -> name_en)
        # (không yêu cầu wholesale => mặc định 0)
    }
    """
    from .models import Brand, Category  # tránh vòng lặp import

    # --- Lấy trường theo đúng key bạn dùng ---
    name_vi_raw = str(raw.get("Tên Tiếng Việt", "")).strip()
    name_vi = "" if name_vi_raw == "0" else name_vi_raw

    name_en = str(raw.get("Tên tiếng Anh", "")).strip()  # nếu không có thì rỗng
    model = str(raw.get("Model", "")).strip()
    price_retail = _parse_price(raw.get("Giá bán lẻ"))
    updated_at = str(raw.get("Ngày cập nhập", "")).strip()
    vat = _parse_percent(raw.get("Thuế xuất VAT áp dụng\n1/8/2025"))

    image_url = _norm_image(raw.get("image"), sku)

    # --- Brand & Category mặc định (vì file không có thông tin này) ---
    brand, _ = Brand.objects.get_or_create(name=default_brand, defaults={"slug": default_brand.lower()})
    # luôn đưa vào 'Uncategorized' cho gọn
    category, _ = Category.objects.get_or_create(parent=None, slug="uncategorized", defaults={"name": "Uncategorized"})

    # --- Fallback tên hiển thị ---
    display_name = name_vi or name_en or sku

    # --- attributes CHỈ GIỮ những key bạn yêu cầu ---
    attrs = {
        "name_en": name_en,
        "model": model,
        "vat_rate": vat,
        "wholesale_price": 0,   # bạn muốn có key này; không có trong file thì để 0
        "raw": raw,             # lưu lại raw để đối soát
        "image": image_url,
        "updated_at": updated_at,
    }

    return {
        "name": display_name,
        "oem_code": sku,
        "brand": brand,
        "category": category,
        "retail_price": price_retail,
        "sale_price": None,
        "meta_title": display_name,
        "meta_description": f"{display_name} – phụ tùng chính hãng.",
        "attributes": attrs,
    }
