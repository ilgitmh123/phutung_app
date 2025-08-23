
from flask import Flask, render_template, request
import pandas as pd
import logging
from datetime import datetime

app = Flask(__name__)
# Ghi log lỗi vào logs/error.log
logging.basicConfig(
    filename='logs/error.log',
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ⚡ Load database CSV 1 lần
df = pd.read_csv("data/database_phutung.csv", dtype=str).fillna("")
def format_price(val):
    try:
        num = int(float(val))
        return f"{num:,}"
    except:
        return val


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    code = request.form.get("ma_phutung", "").strip().replace("-", "").upper()

    def normalize(val):
        return str(val).strip().replace("-", "").upper()

    result = df[df["ma_phutung"].apply(normalize) == code]

    def format_price(val):
        try:
            num = int(float(val))
            return f"{num:,}"
        except:
            return val

    if not result.empty:
        record_raw = result.iloc[0].to_dict()
        record = {
            k: format_price(v) if "gia" in k.lower() else v
            for k, v in record_raw.items()
            if k in ["ma_phutung", "ten_san_pham", "gia_si", "gia_le"]
        }
    else:
        record = None

    return render_template("result.html", code=code, record=record)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
