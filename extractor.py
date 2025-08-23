
import pandas as pd
import os

data_dir = "data"
records = []

for file in os.listdir(data_dir):
    if file.endswith(".xlsx") or file.endswith(".xls"):
        path = os.path.join(data_dir, file)
        try:
            df = pd.read_excel(path, dtype=str, header=1)
            for _, row in df.iterrows():
                row_data = row.astype(str).fillna("")
                possible_codes = [col for col in row.index if "mã" in col.lower()]
                possible_names = [col for col in row.index if "tên" in col.lower()]
                possible_prices = [col for col in row.index if "giá" in col.lower()]

                code = next((row_data[c] for c in possible_codes if row_data[c]), "")
                name = next((row_data[c] for c in possible_names if row_data[c]), "")
                prices = [int(float(row_data[c])) for c in possible_prices if row_data[c].isdigit()]

                gia_si = prices[0] if len(prices) >= 1 else ""
                gia_le = prices[1] if len(prices) >= 2 else ""

                if code and name:
                    records.append({
                        "ma_phutung": code,
                        "ten_san_pham": name,
                        "gia_si": gia_si,
                        "gia_le": gia_le
                    })
        except Exception as e:
            print(f"Lỗi đọc file {file}: {e}")

df = pd.DataFrame(records)
df.to_csv("data/database_phutung.csv", index=False)
print("✅ Đã tạo xong database_phutung.csv")
