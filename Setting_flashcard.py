from tkinter import *
from tkinter import messagebox, colorchooser
import json
import os
import sys

# --- Global Variables and Constants (shared with main app) ---
DATA_FILE = "flashcards_data.json"
SETTINGS_FILE = "flashcards_settings.json"

flashcards = [] # Danh sách flashcards của unit HIỆN TẠI đang được quản lý
# text_color global này giờ sẽ là màu mặc định nếu thẻ không có màu riêng
global_text_color = "#333" 

current_managed_unit_name = None

# --- Data Loading and Saving Functions ---

def load_flashcards_for_unit(unit_name_to_load):
    """Tải dữ liệu flashcard cho một unit cụ thể từ DATA_FILE."""
    global flashcards, current_managed_unit_name

    current_managed_unit_name = unit_name_to_load

    all_units_data = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, dict):
                    all_units_data = loaded_data
                else:
                    all_units_data = {}
        except json.JSONDecodeError:
            messagebox.showerror("Lỗi dữ liệu", "Không thể đọc dữ liệu flashcard. Dữ liệu sẽ được khởi tạo lại.")
            all_units_data = {}

    # Lấy danh sách flashcards của unit được chỉ định
    flashcards = all_units_data.get(current_managed_unit_name, [])
    
    # Đảm bảo mỗi thẻ có một trường 'color'. Nếu không có, gán màu mặc định.
    for card in flashcards:
        if "color" not in card:
            card["color"] = global_text_color # Sử dụng màu global_text_color làm mặc định

def save_flashcards_for_unit():
    """Lưu dữ liệu flashcard của unit hiện tại vào DATA_FILE."""
    global flashcards
    if current_managed_unit_name is None:
        messagebox.showerror("Lỗi Lưu Dữ Liệu", "Không có Unit nào được chọn để lưu.")
        return

    all_units_data = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, dict):
                    all_units_data = loaded_data
        except json.JSONDecodeError:
            pass 

    all_units_data[current_managed_unit_name] = flashcards 

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_units_data, f, ensure_ascii=False, indent=4)

def load_settings():
    """Tải cài đặt ứng dụng (mode, text_color) từ SETTINGS_FILE."""
    global global_text_color
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                if "text_color" in settings:
                    global_text_color = settings["text_color"]
        except json.JSONDecodeError:
            print("Không thể tải cài đặt.")

def save_settings(new_text_color=None, new_mode=None):
    """Lưu cài đặt hiện tại của ứng dụng vào SETTINGS_FILE.
       Chỉ cập nhật text_color và mode (nếu có), bảo toàn các phần khác (ví dụ 'units').
    """
    settings_to_save = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings_to_save = json.load(f)
        except json.JSONDecodeError:
            pass 

    if new_text_color:
        settings_to_save["text_color"] = new_text_color
    if new_mode:
        settings_to_save["mode"] = new_mode

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings_to_save, f, ensure_ascii=False, indent=4)

# --- GUI Management Functions for Each Card ---

def refresh_card_display(list_frame):
    """Làm mới hiển thị danh sách thẻ bài."""
    for widget in list_frame.winfo_children():
        widget.destroy()

    if not flashcards:
        Label(list_frame, text="Unit này chưa có thẻ bài nào.", font=("Arial", 14), fg="gray", bg="white").pack(pady=20)
        return

    for i, card in enumerate(flashcards):
        card_row_frame = Frame(list_frame, bg="#e0e0e0", bd=1, relief="solid", padx=5, pady=5)
        card_row_frame.pack(fill=X, pady=5)

        # Lấy màu riêng của thẻ, nếu không có thì dùng màu global
        card_color = card.get("color", global_text_color)

        Label(card_row_frame, text=f"EN: {card['en']}", font=("Arial", 12, "bold"), bg="#e0e0e0", fg=card_color, wraplength=200).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        Label(card_row_frame, text=f"VI: {card['vi']}", font=("Arial", 12), bg="#e0e0e0", wraplength=200).grid(row=1, column=0, sticky="w", padx=5, pady=2)

        btn_frame = Frame(card_row_frame, bg="#e0e0e0")
        btn_frame.grid(row=0, column=1, rowspan=2, sticky="e", padx=5)

        Button(btn_frame, text="✏️ Sửa", command=lambda idx=i: edit_card_in_list(idx, list_frame), **small_button_style).pack(side=LEFT, padx=2)
        Button(btn_frame, text="🗑️ Xóa", command=lambda idx=i: delete_card_from_list(idx, list_frame), bg="#CC0000", activebackground="#990000", fg="#ffffff", font=("Arial", 10), bd=0, padx=5, pady=2).pack(side=LEFT, padx=2)
        # Thêm nút đổi màu cho từng thẻ
        Button(btn_frame, text="🎨 Màu Thẻ", command=lambda idx=i: change_card_color(idx, list_frame), **small_button_style).pack(side=LEFT, padx=2)
        
def add_new_card_dialog(list_frame):
    """Mở hộp thoại để thêm một thẻ bài mới vào unit hiện tại."""
    def save_new_card():
        en_word = entry_en.get().strip()
        vi_word = entry_vi.get().strip()

        if en_word and vi_word:
            # Thêm thẻ mới với màu mặc định là global_text_color
            flashcards.append({"en": en_word, "vi": vi_word, "color": global_text_color})
            save_flashcards_for_unit()
            add_window.destroy()
            refresh_card_display(list_frame)
        else:
            messagebox.showwarning("Lỗi nhập liệu", "Vui lòng nhập cả từ tiếng Anh và tiếng Việt.")

    add_window = Toplevel(root)
    add_window.title("Thêm Thẻ Bài Mới")
    add_window.transient(root)
    add_window.grab_set()
    add_window.configure(bg="#f5f5f5")

    Label(add_window, text="Tiếng Anh:", font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_en = Entry(add_window, font=("Arial", 12))
    entry_en.grid(row=0, column=1, padx=10, pady=5)

    Label(add_window, text="Tiếng Việt:", font=("Arial", 12), bg="#f5f5f5").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    entry_vi = Entry(add_window, font=("Arial", 12))
    entry_vi.grid(row=1, column=1, padx=10, pady=5)

    Button(add_window, text="Lưu Thẻ", command=save_new_card, **button_style).grid(row=2, columnspan=2, pady=10)

def edit_card_in_list(index, list_frame):
    """Mở hộp thoại để chỉnh sửa một thẻ bài cụ thể trong danh sách."""
    if index < 0 or index >= len(flashcards):
        messagebox.showerror("Lỗi", "Chỉ mục thẻ bài không hợp lệ.")
        return

    card_to_edit = flashcards[index]

    def save_edited_card():
        en_word = entry_en.get().strip()
        vi_word = entry_vi.get().strip()

        if en_word and vi_word:
            card_to_edit["en"] = en_word
            card_to_edit["vi"] = vi_word
            # Màu của thẻ không bị thay đổi khi chỉnh sửa nội dung
            save_flashcards_for_unit()
            edit_window.destroy()
            refresh_card_display(list_frame)
        else:
            messagebox.showwarning("Lỗi nhập liệu", "Vui lòng nhập cả từ tiếng Anh và tiếng Việt.")

    edit_window = Toplevel(root)
    edit_window.title("Chỉnh Sửa Thẻ Bài")
    edit_window.transient(root)
    edit_window.grab_set()
    edit_window.configure(bg="#f5f5f5")

    Label(edit_window, text="Tiếng Anh:", font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_en = Entry(edit_window, font=("Arial", 12))
    entry_en.grid(row=0, column=1, padx=10, pady=5)
    entry_en.insert(0, card_to_edit["en"])

    Label(edit_window, text="Tiếng Việt:", font=("Arial", 12), bg="#f5f5f5").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    entry_vi = Entry(edit_window, font=("Arial", 12))
    entry_vi.grid(row=1, column=1, padx=10, pady=5)
    entry_vi.insert(0, card_to_edit["vi"])

    Button(edit_window, text="Lưu Thay Đổi", command=save_edited_card, **button_style).grid(row=2, columnspan=2, pady=10)

def delete_card_from_list(index, list_frame):
    """Xóa một thẻ bài cụ thể khỏi danh sách."""
    if index < 0 or index >= len(flashcards):
        messagebox.showerror("Lỗi", "Chỉ mục thẻ bài không hợp lệ.")
        return

    confirm = messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc chắn muốn xóa thẻ bài '{flashcards[index]['en']}' không?")
    if confirm:
        flashcards.pop(index)
        save_flashcards_for_unit()
        refresh_card_display(list_frame)
        messagebox.showinfo("Xóa thành công", "Thẻ bài đã được xóa.")

def change_card_color(index, list_frame):
    """Mở hộp thoại chọn màu để thay đổi màu chữ của một thẻ bài cụ thể."""
    if index < 0 or index >= len(flashcards):
        messagebox.showerror("Lỗi", "Chỉ mục thẻ bài không hợp lệ.")
        return

    current_card = flashcards[index]
    initial_color = current_card.get("color", global_text_color) # Lấy màu hiện tại hoặc mặc định

    color_code = colorchooser.askcolor(title=f"Chọn Màu Chữ cho Thẻ: {current_card['en']}", initialcolor=initial_color)
    if color_code[1]: # color_code[1] là chuỗi hex
        current_card["color"] = color_code[1] # Cập nhật màu cho thẻ đó
        save_flashcards_for_unit() # Lưu lại thay đổi màu của thẻ
        refresh_card_display(list_frame) # Làm mới hiển thị để thấy màu mới

def change_global_text_color(list_frame):
    """Mở hộp thoại chọn màu để thay đổi màu chữ GLOBAL cho tất cả flashcard."""
    global global_text_color
    color_code = colorchooser.askcolor(title="Chọn Màu Chữ Toàn Cục", initialcolor=global_text_color)
    if color_code[1]:
        global_text_color = color_code[1]
        save_settings(new_text_color=global_text_color) # Lưu màu mới vào cài đặt

        # Cập nhật màu cho các thẻ chưa có màu riêng về màu global mới
        for card in flashcards:
            if "color" not in card: # Chỉ cập nhật nếu thẻ chưa có màu riêng
                 card["color"] = global_text_color
        save_flashcards_for_unit() # Lưu lại thay đổi nếu có thẻ được cập nhật màu mặc định
        
        refresh_card_display(list_frame) # Làm mới để áp dụng màu mới


# --- Application Exit Handler ---

def on_closing():
    """Hàm được gọi khi cửa sổ Tkinter đóng."""
    root.destroy()

# --- GUI Setup ---

root = Tk()

# --- Xử lý đối số dòng lệnh để xác định Unit ---
if len(sys.argv) > 1:
    unit_name_from_args = sys.argv[1]
    root.title(f"Quản lý Thẻ Bài - Unit: {unit_name_from_args}")
    load_settings() # Tải màu chữ global trước khi tải thẻ
    load_flashcards_for_unit(unit_name_from_args) # Tải dữ liệu cho unit được chỉ định
else:
    messagebox.showerror("Lỗi Khởi Động", "Không có Unit nào được chọn. Vui lòng mở từ 'flashcard.py'.")
    sys.exit() 

root.configure(bg="#f5f5f5")

# Button Styles
button_style = {
    "font": ("Arial", 13),
    "fg": "#ffffff",
    "bg": "#007ACC",
    "activebackground": "#005F99",
    "activeforeground": "#ffffff",
    "bd": 0,
    "width": 25,
    "height": 1,
    "cursor": "hand2"
}

small_button_style = {
    "font": ("Arial", 10),
    "fg": "#ffffff",
    "bg": "#007ACC",
    "activebackground": "#005F99",
    "activeforeground": "#ffffff",
    "bd": 0,
    "padx": 5,
    "pady": 2,
    "cursor": "hand2"
}

# ==== Main Management Frame ====
main_frame = Frame(root, bg="#f5f5f5")
main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

# ==== Title ====
Label(main_frame, text=f"Quản lý thẻ bài của Unit: {current_managed_unit_name}", font=("Arial", 18, "bold"), bg="#f5f5f5", fg="#333", wraplength=400).pack(pady=10)

# ==== List Frame with Scrollbar ====
list_canvas = Canvas(main_frame, bg="white", bd=0, highlightthickness=0)
list_scrollbar = Scrollbar(main_frame, orient="vertical", command=list_canvas.yview)
list_scrollable_frame = Frame(list_canvas, bg="white")

list_scrollable_frame.bind(
    "<Configure>",
    lambda e: list_canvas.configure(
        scrollregion=list_canvas.bbox("all")
    )
)

list_canvas.create_window((0, 0), window=list_scrollable_frame, anchor="nw")
list_canvas.configure(yscrollcommand=list_scrollbar.set)

list_canvas.pack(side=LEFT, fill=BOTH, expand=True)
list_scrollbar.pack(side=RIGHT, fill="y")

# ==== Control Buttons ====
control_frame = Frame(main_frame, bg="#f5f5f5")
control_frame.pack(pady=10)

Button(control_frame, text="➕ Thêm Thẻ Bài Mới", command=lambda: add_new_card_dialog(list_scrollable_frame), **button_style).pack(pady=5)
Button(control_frame, text="🎨 Đổi Màu Chữ Toàn Cục", command=lambda: change_global_text_color(list_scrollable_frame), **button_style).pack(pady=5)


# --- Initial Display ---
refresh_card_display(list_scrollable_frame)

# --- Set up graceful exit handler ---
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()