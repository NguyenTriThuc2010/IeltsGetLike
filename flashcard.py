from tkinter import *
from tkinter import messagebox
import json
import os
import sys
import subprocess # Để chạy Setting_flashcard.py

# --- Global Variables and Constants ---
DATA_FILE = "flashcards_data.json"
SETTINGS_FILE = "flashcards_settings.json"

flashcards = []
current_index = 0
# text_color này giờ sẽ là màu mặc định nếu thẻ không có màu riêng
global_text_color = "#333" 

current_unit_name = None # Name of the unit currently being studied

# --- Data Loading and Saving Functions ---

def load_flashcards_for_unit(unit_name_to_load):
    """Tải dữ liệu flashcard cho một unit cụ thể."""
    global flashcards, current_index, current_unit_name
    
    current_unit_name = unit_name_to_load # Set the global unit name

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
            messagebox.showerror("Lỗi Dữ Liệu", "Không thể đọc dữ liệu flashcard. Dữ liệu sẽ được khởi tạo lại.")
            all_units_data = {}
    
    # Lấy flashcards cho unit hiện tại
    flashcards = all_units_data.get(current_unit_name, [])

    # Đảm bảo mỗi thẻ có một trường 'color'. Nếu không có, gán màu global_text_color.
    for card in flashcards:
        if "color" not in card:
            card["color"] = global_text_color

    if not flashcards:
        current_index = 0
    elif current_index >= len(flashcards):
        current_index = 0

def load_settings():
    """Tải cài đặt ứng dụng (mode, global_text_color) từ file JSON."""
    global mode, global_text_color
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                if "mode" in settings:
                    mode.set(settings["mode"])
                if "text_color" in settings:
                    global_text_color = settings["text_color"]
                    # label_word.config(fg=global_text_color) will be handled by show_flashcard
        except json.JSONDecodeError:
            print("Không thể tải cài đặt.")
    if not mode.get():
        mode.set("en_first")

def save_settings():
    """Lưu cài đặt hiện tại của ứng dụng (mode, global_text_color) vào SETTINGS_FILE.
       Chỉ lưu các cài đặt chung, không động chạm đến 'units'.
    """
    current_settings = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                current_settings = json.load(f)
        except json.JSONDecodeError:
            pass

    # Cập nhật các giá trị cần thay đổi
    current_settings["mode"] = mode.get()
    current_settings["text_color"] = global_text_color
    
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(current_settings, f, ensure_ascii=False, indent=4)

# --- Core Flashcard Logic Functions ---

def show_flashcard():
    """Hiển thị mặt trước của flashcard dựa vào chế độ và màu riêng của thẻ."""
    if not flashcards:
        label_word.config(text="Unit này chưa có thẻ nào.", fg="gray")
        return
    
    card = flashcards[current_index]
    # Lấy màu của thẻ, nếu không có thì dùng màu global_text_color mặc định
    card_color = card.get("color", global_text_color) 

    if mode.get() == "en_first":
        label_word.config(text=card["en"], fg=card_color)
    else:
        label_word.config(text=card["vi"], fg=card_color)
    label_result.config(text="") # Clear previous result/meaning

def flip_card(event=None):
    """Lật thẻ bài (hiển thị mặt còn lại)."""
    if not flashcards:
        return
    card = flashcards[current_index]
    # Lấy màu của thẻ, nếu không có thì dùng màu global_text_color mặc định
    card_color = card.get("color", global_text_color)

    current_text = label_word.cget("text")

    if mode.get() == "en_first":
        if current_text == card["en"]:
            label_word.config(text=card["vi"], fg=card_color)
        else:
            label_word.config(text=card["en"], fg=card_color) # Lật lại mặt EN
    else: # mode is vi_first
        if current_text == card["vi"]:
            label_word.config(text=card["en"], fg=card_color)
        else:
            label_word.config(text=card["vi"], fg=card_color) # Lật lại mặt VI


def next_card(event=None):
    """Chuyển sang flashcard tiếp theo."""
    global current_index
    if not flashcards:
        return
    current_index = (current_index + 1) % len(flashcards)
    show_flashcard()

# --- External Script Execution ---

def open_setting_flashcard():
    """Mở cửa sổ Setting_flashcard.py để quản lý thẻ."""
    root.withdraw() # Ẩn cửa sổ hiện tại
    try:
        # Pass the current unit name to Setting_flashcard.py
        subprocess.run(["python", "Setting_flashcard.py", current_unit_name], check=True)
    except FileNotFoundError:
        messagebox.showerror("Lỗi", "Không tìm thấy file 'Setting_flashcard.py'. Vui lòng đảm bảo file nằm cùng thư mục.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi chạy 'Setting_flashcard.py': {e}")
    finally:
        root.deiconify() # Hiện lại cửa sổ
        # Tải lại dữ liệu và cài đặt sau khi Setting_flashcard.py đóng
        # để hiển thị các thay đổi (thêm/sửa/xóa thẻ, thay đổi màu thẻ/màu global)
        load_settings() # Tải lại cài đặt (ví dụ: global_text_color nếu đổi)
        load_flashcards_for_unit(current_unit_name) # Tải lại thẻ cho unit hiện tại
        show_flashcard() # Cập nhật hiển thị thẻ

# --- Application Exit Handler ---

def on_closing():
    """Hàm được gọi khi cửa sổ Tkinter đóng."""
    save_settings()
    root.destroy()

# --- GUI Setup ---

root = Tk()

# --- Handle Command Line Arguments for Unit Selection ---
if len(sys.argv) > 1:
    unit_name_from_main = sys.argv[1]
    root.title(f"Flashcard Tiếng Anh - Unit: {unit_name_from_main}")
    # Tải settings trước để có global_text_color cho load_flashcards_for_unit
    mode = StringVar(value="en_first") # Khởi tạo mode trước
    load_settings() 
    load_flashcards_for_unit(unit_name_from_main) 
else:
    messagebox.showerror("Lỗi Khởi Động", "Vui lòng chọn một Unit từ 'mainflashcard.py' để bắt đầu.")
    sys.exit()

root.configure(bg="#f5f5f5")

# ==== KHUNG THẺ BÀI ====
card_frame = Frame(root, bg="white", bd=2, relief="groove", cursor="hand2", width=400, height=300) 
card_frame.pack(pady=30, padx=20)
card_frame.pack_propagate(False)

# Sử dụng global_text_color ban đầu khi tạo label_word
label_word = Label(card_frame, text="", font=("Arial", 28, "bold"), bg="white", fg=global_text_color, wraplength=350)
label_word.pack(padx=50, pady=30, expand=True)

label_result = Label(card_frame, text="", font=("Arial", 18), fg="green", bg="white", wraplength=350) 

# Bindings for flipping and next card
card_frame.bind("<Button-1>", flip_card) 
label_word.bind("<Button-1>", flip_card)

# ==== Các nút chức năng ====
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

# Button "Chuyển thẻ tiếp theo"
Button(root, text="➡️ Thẻ tiếp theo", command=next_card, **button_style).pack(pady=4)

# Button "Quản lý thẻ bài" (mở Setting_flashcard.py)
Button(root, text="⚙️ Quản lý thẻ bài", command=open_setting_flashcard, **button_style).pack(pady=4)

# ==== Chọn chế độ hiển thị trước ====
mode_frame = Frame(root, bg="#f5f5f5")
mode_frame.pack(pady=10)

Label(mode_frame, text="🔁 Xem mặt nào trước?", bg="#f5f5f5", font=("Arial", 12)).pack(side=LEFT, padx=5)
Radiobutton(mode_frame, text="🇬🇧 Tiếng Anh", variable=mode, value="en_first", bg="#f5f5f5", command=show_flashcard).pack(side=LEFT)
Radiobutton(mode_frame, text="🇻🇳 Tiếng Việt", variable=mode, value="vi_first", bg="#f5f5f5", command=show_flashcard).pack(side=LEFT)

# --- Initial Display and Application Loop ---
show_flashcard()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()