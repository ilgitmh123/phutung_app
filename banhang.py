import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import json, pandas as pd, unicodedata, os, threading, shutil
import tkinter.font as tkFont

JSON_PATH = "phutung.json"

# ==== Utils xử lý Excel & JSON ====
def normalize_col(col: str) -> str:
    col = str(col).strip().lower()
    col = ''.join(c for c in unicodedata.normalize('NFD', col) if unicodedata.category(c) != 'Mn')
    col = col.replace(" ", "").replace("_", "")
    return col

def has_ma_column(df: pd.DataFrame) -> bool:
    for c in df.columns:
        norm = normalize_col(c)
        if "maphutung" in norm or "masp" in norm or "partnumber" in norm:
            return True
    return False

def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    drop_cols = []
    for col in df.columns:
        norm = normalize_col(col)
        if norm in ["stt"]:   # bỏ cột STT
            drop_cols.append(col)
            continue
        if "maphutung" in norm or "masp" in norm or "partnumber" in norm:
            rename_map[col] = "Mã phụ tùng"
        elif "tentiengviet" in norm:   
            rename_map[col] = "Tên Tiếng Việt"
        elif col.strip().lower().startswith("unnamed: 13"):  # cột Unnamed: 13
            rename_map[col] = "Tên Tiếng Việt"
        elif "giabanle" in norm:
            rename_map[col] = "Giá bán lẻ"
        elif "giabansi" in norm or "giabansy" in norm or "giasi" in norm or "gbs" in norm:
            rename_map[col] = "Giá bán sỉ"
        else:
            rename_map[col] = col
    df = df.rename(columns=rename_map)
    if drop_cols:
        df = df.drop(columns=drop_cols, errors="ignore")
    return df

def read_excel_with_fallback(file_path, sheet_name):
    for header_row in [1, 0, 2, 3, 4, 5]:
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
            df = rename_columns(df)
            if has_ma_column(df):
                return df
        except Exception:
            continue
    return None

def process_excel(file_path):
    try:
        xls = pd.ExcelFile(file_path)
    except Exception:
        return {}

    all_data = []
    for sheet_name in xls.sheet_names:
        df = read_excel_with_fallback(file_path, sheet_name)
        if df is None:
            continue
        all_data.append(df)

    if not all_data:
        return {}

    final_df = pd.concat(all_data, ignore_index=True)

    if "Mã phụ tùng" not in final_df.columns:
        return {}

    if list(final_df.columns).count("Mã phụ tùng") > 1:
        final_df = final_df.loc[:, ~final_df.columns.duplicated()]

    # Format dữ liệu
    for col in final_df.columns:
        if pd.api.types.is_datetime64_any_dtype(final_df[col]):
            final_df[col] = final_df[col].dt.strftime("%d/%m/%Y %H:%M")
        else:
            try:
                final_df[col] = pd.to_numeric(final_df[col])
                final_df[col] = final_df[col].apply(
                    lambda x: f"{x:,.0f}" if pd.notna(x) and abs(x) >= 1
                    else (f"{x*100:.0f}%" if pd.notna(x) and 0 < x < 1 else "")
                )
            except Exception:
                final_df[col] = final_df[col].astype(str).replace("nan", "")

    final_df["Mã phụ tùng"] = final_df["Mã phụ tùng"].astype(str).str.strip()
    final_df = final_df.drop_duplicates(subset=["Mã phụ tùng"], keep="last")

    data_dict = {}
    for _, row in final_df.iterrows():
        key = str(row["Mã phụ tùng"])
        record = {col: str(val) for col, val in row.items()
                  if col != "Mã phụ tùng" and str(val) not in ["", "nan", "None"]}
        data_dict[key] = record
    return data_dict

# ==== JSON Safe I/O ====
def _salvage_json_text(txt: str):
    last = txt.rfind("}")
    if last != -1:
        candidate = txt[:last+1]
        try:
            return json.loads(candidate)
        except Exception:
            return None
    return None

def load_data():
    if not os.path.exists(JSON_PATH):
        return {}
    try:
        with open(JSON_PATH, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            repaired = _salvage_json_text(txt)
            if repaired is not None:
                return repaired
            raise
    except Exception as e:
        messagebox.showerror("Lỗi JSON",
            f"Không đọc được {JSON_PATH}.\nChi tiết: {e}\n"
            f"👉 Hãy xoá file này và cập nhật lại từ Excel.")
        return {}

def update_json(new_data):
    try:
        old_data = load_data()
    except Exception:
        old_data = {}

    added, updated = 0, 0
    for k, v in new_data.items():
        if k in old_data:
            updated += 1
        else:
            added += 1
        old_data[k] = v

    if os.path.exists(JSON_PATH):
        try:
            shutil.copy2(JSON_PATH, JSON_PATH + ".bak")
        except Exception:
            pass

    tmp = JSON_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(old_data, f, ensure_ascii=False, indent=4)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, JSON_PATH)
    return added, updated

# ==== GUI Functions ====
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

def update_data_thread(file_path):
    progress.start(10)
    txt_log.insert(tk.END, f"🔄 Đang xử lý {os.path.basename(file_path)}...\n")
    txt_log.see(tk.END)

    try:
        new_data = process_excel(file_path)
        if not new_data:
            messagebox.showwarning("Không có dữ liệu", "File không chứa dữ liệu hợp lệ")
            return

        added, updated = update_json(new_data)
        txt_log.insert(tk.END, f"✅ Đã cập nhật: {added} mới, {updated} override từ {os.path.basename(file_path)}\n")
        txt_log.see(tk.END)
    finally:
        progress.stop()

def update_data():
    file_path = entry_file.get()
    if not file_path:
        messagebox.showwarning("Thiếu file", "Vui lòng chọn file Excel để cập nhật")
        return
    threading.Thread(target=update_data_thread, args=(file_path,), daemon=True).start()

# ==== BẢNG Ô VUÔNG ====
wholesale_cache = {}
selected_row_widgets = []  # lưu widgets trong hàng đang chọn

def clear_grid():
    for w in grid_frame_inner.winfo_children():
        w.destroy()

def on_row_click(row_index):
    global selected_row_widgets
    for w in selected_row_widgets:
        w.configure(bg="white", fg="black")
    selected_row_widgets = []
    for w in grid_frame_inner.grid_slaves(row=row_index):
        if isinstance(w, tk.Label):
            w.configure(bg="#000000", fg="white")
            selected_row_widgets.append(w)

def make_cell(text, r, c, header=False, width=18):
    bg = "#dce6f1" if header else "white"
    fg = "black"
    lab = tk.Label(grid_frame_inner, text=text, width=width,
                   bg=bg, fg=fg, bd=1, relief="solid",
                   padx=6, pady=6, anchor="center", justify="center")
    lab.grid(row=r, column=c, sticky="nsew")
    grid_frame_inner.grid_columnconfigure(c, weight=1)
    if not header and r == 1:
        lab.bind("<Button-1>", lambda e, row=r: on_row_click(row))
    return lab

def render_record(ma, record: dict):
    clear_grid()
    cols = list(record.keys())

    # sắp xếp đặc biệt
    special_order = []
    if "Tên Tiếng Anh" in cols:
        special_order.append("Tên Tiếng Anh")
    if "Tên Tiếng Việt" in cols:
        special_order.append("Tên Tiếng Việt")
    for sp in special_order:
        if sp in cols:
            cols.remove(sp)

    cols = ["  Mã phụ tùng  "] + special_order + [c for c in cols if c != "Giá bán sỉ"]

    wholesale_cache[ma] = record.get("Giá bán sỉ", None)

    # data để tính width
    vals = [ma] + [record.get(c, "  ") for c in cols[1:]]
    widths = auto_col_width(cols, [vals])

    # Header
    for j, col in enumerate(cols):
        make_cell(col, 0, j, header=True, width=widths[j])

    # Data
    for j, val in enumerate(vals):
        make_cell(val, 1, j, header=False, width=widths[j])

    for j in range(len(cols)):
        grid_frame_inner.grid_columnconfigure(j, weight=2)

def search_part(event=None):
    ma = entry_ma.get().strip()
    if not ma:
        messagebox.showwarning("Thiếu mã", "Vui lòng nhập mã phụ tùng")
        return
    try:
        data = load_data()
    except Exception:
        return

    if ma in data:
        render_record(ma, data[ma])
    else:
        clear_grid()
        make_cell(f"❌ Không tìm thấy mã phụ tùng {ma}", 0, 0, header=True, width=40)
    entry_ma.delete(0, tk.END)

def show_wholesale():
    if not grid_frame_inner.grid_size()[0]:
        return
    for w in grid_frame_inner.grid_slaves(row=1, column=0):
        ma = w.cget("text")
        break
    else:
        return
    gia_si = wholesale_cache.get(ma, None)
    if gia_si:
        messagebox.showinfo("Giá bán sỉ", f"Mã {ma}\nGiá bán sỉ: {gia_si}")
    else:
        messagebox.showinfo("Giá bán sỉ", f"Mã {ma} hiện không có trường 'Giá bán sỉ'.")
def auto_col_width(cols, all_rows):
    font = tkFont.nametofont("TkDefaultFont")
    widths = []
    for j, col in enumerate(cols):
        max_px = font.measure(str(col))
        for row in all_rows:
            if j < len(row):
                max_px = max(max_px, font.measure(str(row[j])))
        char_w = max(60, min(140, int(max_px / font.measure("0") + 2)))
        widths.append(char_w)
    return widths

# ==== GUI ====
root = tk.Tk()
root.title("Quản lý phụ tùng")

# --- Box cập nhật ---
frame_update = tk.LabelFrame(root, text="Cập nhật hàng", padx=10, pady=10)
frame_update.pack(fill="x", padx=10, pady=5)

entry_file = tk.Entry(frame_update, width=50)
entry_file.pack(side="left", padx=5)

btn_browse = tk.Button(frame_update, text="Browse", command=browse_file)
btn_browse.pack(side="left", padx=5)

btn_update = tk.Button(frame_update, text="Cập nhật", command=update_data)
btn_update.pack(side="left", padx=5)

progress = ttk.Progressbar(frame_update, mode="indeterminate")
progress.pack(fill="x", pady=5)

txt_log = scrolledtext.ScrolledText(frame_update, height=8)
txt_log.pack(fill="x", pady=5)

# --- Box tra cứu ---
frame_search = tk.LabelFrame(root, text="Tra cứu phụ tùng", padx=10, pady=10)
frame_search.pack(fill="both", padx=10, pady=5, expand=True)

wrap_top = tk.Frame(frame_search)
wrap_top.pack(fill="x")

entry_ma = tk.Entry(wrap_top, width=30)
entry_ma.pack(side="left", padx=5)
entry_ma.bind("<Return>", search_part)

btn_search = tk.Button(wrap_top, text="Tìm", command=search_part)
btn_search.pack(side="left", padx=5)

btn_wholesale = tk.Button(wrap_top, text="👁 Xem giá sỉ", command=show_wholesale)
btn_wholesale.pack(side="left", padx=5)

# --- Bảng ô vuông ---
grid_container = tk.Frame(frame_search, bd=1, relief="solid")
grid_container.pack(fill="both", expand=True, pady=8)

grid_canvas = tk.Canvas(grid_container, background="#f9f9f9", highlightthickness=0)
grid_canvas.pack(side="left", fill="both", expand=True)

scroll_y = ttk.Scrollbar(grid_container, orient="vertical", command=grid_canvas.yview)
scroll_y.pack(side="right", fill="y")
scroll_x = ttk.Scrollbar(frame_search, orient="horizontal", command=grid_canvas.xview)
scroll_x.pack(fill="x")

grid_canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

grid_frame_inner = tk.Frame(grid_canvas, bg="#f9f9f9")
grid_window = grid_canvas.create_window((0, 0), window=grid_frame_inner, anchor="nw")

def _on_frame_configure(event):
    grid_canvas.configure(scrollregion=grid_canvas.bbox("all"))

def _on_canvas_configure(event):
    grid_canvas.itemconfig(grid_window, width=event.width)

grid_frame_inner.bind("<Configure>", _on_frame_configure)
grid_canvas.bind("<Configure>", _on_canvas_configure)

root.mainloop()
