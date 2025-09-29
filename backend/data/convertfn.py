import json, re, pathlib

with open("output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

out = {}
for sku, item in data.items():
    # fix giá
    gia = re.sub(r"[^\d]", "", item.get("Giá bán lẻ",""))
    gia = int(gia) if gia else 0
    
    # fix vat
    vat = re.sub(r"[^\d]", "", item.get("Thuế xuất VAT áp dụng\n1/8/2025",""))
    vat = int(vat) if vat else 0
    
    # fix image path
    img = item.get("image","").replace("\\","/")  
    if not img.startswith("/"):  
        img = "/" + img

    out[sku] = {
        "Tên Tiếng Việt": item.get("Tên Tiếng Việt","") if item.get("Tên Tiếng Việt")!="0" else "",
        "Model": item.get("Model",""),
        "Giá bán lẻ": gia,
        "Ngày cập nhập": item.get("Ngày cập nhập",""),
        "VAT": vat,
        "image": img,
    }

with open("final.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
