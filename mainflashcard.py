from tkinter import *
from tkinter import messagebox, colorchooser
import json
import os
import subprocess

# --- Global Constants ---
DATA_FILE = "flashcards_data.json"
SETTINGS_FILE = "flashcards_settings.json"

# Global variable to store all units and their data
all_units_data = {} # { "Unit Name": [{"en": "word", "vi": "nghia"}, ...], ... }
unit_settings = {}  # { "Unit Name": {"color": "#hexcode"}, ... }

# --- Data Loading and Saving Functions ---

def load_all_flashcards_data():
    """Loads all flashcards data (for all units) from DATA_FILE."""
    global all_units_data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    all_units_data = loaded
                else:
                    all_units_data = {} # Malformed, start fresh
        except json.JSONDecodeError:
            messagebox.showerror("Lỗi Dữ Liệu", "Không thể đọc dữ liệu flashcard. Dữ liệu sẽ được tạo mới.")
            all_units_data = {}
    else:
        all_units_data = {} # Start empty if no file

def save_all_flashcards_data():
    """Saves all flashcards data (for all units) to DATA_FILE."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_units_data, f, ensure_ascii=False, indent=4)

def load_unit_settings():
    """Loads unit-specific settings (like color) from SETTINGS_FILE."""
    global unit_settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                if "units" in settings and isinstance(settings["units"], dict):
                    unit_settings = settings["units"]
                else:
                    unit_settings = {} # No units settings or malformed
        except json.JSONDecodeError:
            print("Không thể tải cài đặt unit.") # For debugging
            unit_settings = {}
    else:
        unit_settings = {}

def save_unit_settings():
    """Saves unit-specific settings to SETTINGS_FILE."""
    current_app_settings = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                current_app_settings = json.load(f)
        except json.JSONDecodeError:
            pass # Continue with empty dict if file corrupted

    current_app_settings["units"] = unit_settings
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(current_app_settings, f, ensure_ascii=False, indent=4)

# --- Unit Management Functions ---

def refresh_unit_display(list_frame):
    """Refreshes the display of all units."""
    for widget in list_frame.winfo_children():
        widget.destroy() # Clear existing widgets

    if not all_units_data:
        Label(list_frame, text="Chưa có Unit nào. Thêm một Unit mới để bắt đầu!", font=("Arial", 14), fg="gray", bg="white").pack(pady=20)
        return

    for unit_name in sorted(all_units_data.keys()):
        unit_color = unit_settings.get(unit_name, {}).get("color", "#F0F0F0") # Default light gray if no color

        unit_row_frame = Frame(list_frame, bg=unit_color, bd=2, relief="groove", padx=10, pady=10)
        unit_row_frame.pack(fill=X, pady=5)

        # Unit Name Label
        Label(unit_row_frame, text=unit_name, font=("Arial", 16, "bold"), bg=unit_color, fg="#333", wraplength=250).pack(side=LEFT, padx=5, expand=True, anchor="w")

        # Buttons for each unit
        btn_frame = Frame(unit_row_frame, bg=unit_color)
        btn_frame.pack(side=RIGHT, padx=5)

        # Open Unit Button
        Button(btn_frame, text="📖 Mở", command=lambda name=unit_name: open_unit_flashcards(name), **small_button_style).pack(side=LEFT, padx=2)

        # Change Unit Color Button
        Button(btn_frame, text="🎨 Màu", command=lambda name=unit_name: change_unit_color(name, list_frame), **small_button_style).pack(side=LEFT, padx=2)

        # Rename Unit Button
        Button(btn_frame, text="✏️ Đổi Tên", command=lambda name=unit_name: rename_unit(name, list_frame), **small_button_style).pack(side=LEFT, padx=2)

        # Delete Unit Button
        Button(btn_frame, text="🗑️ Xóa", command=lambda name=unit_name: delete_unit(name, list_frame), bg="#CC0000", activebackground="#990000", fg="#ffffff", font=("Arial", 10), bd=0, padx=5, pady=2).pack(side=LEFT, padx=2)


def add_new_unit_dialog(list_frame):
    """Opens a dialog to add a new unit."""
    def save_new_unit():
        unit_name = entry_unit_name.get().strip()
        if unit_name:
            if unit_name in all_units_data:
                messagebox.showwarning("Trùng tên", "Tên Unit này đã tồn tại. Vui lòng chọn tên khác.")
                return

            all_units_data[unit_name] = [] # Initialize as empty list of flashcards
            unit_settings[unit_name] = {"color": "#F0F0F0"} # Default color
            save_all_flashcards_data()
            save_unit_settings()
            add_window.destroy()
            refresh_unit_display(list_frame)
        else:
            messagebox.showwarning("Lỗi nhập liệu", "Vui lòng nhập tên Unit.")

    add_window = Toplevel(root)
    add_window.title("Thêm Unit Mới")
    add_window.transient(root)
    add_window.grab_set()
    add_window.configure(bg="#f5f5f5")

    Label(add_window, text="Tên Unit:", font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_unit_name = Entry(add_window, font=("Arial", 12))
    entry_unit_name.grid(row=0, column=1, padx=10, pady=5)

    Button(add_window, text="Tạo Unit", command=save_new_unit, **button_style).grid(row=1, columnspan=2, pady=10)

def rename_unit(old_name, list_frame):
    """Opens a dialog to rename an existing unit."""
    def save_renamed_unit():
        new_name = entry_new_name.get().strip()
        if new_name and new_name != old_name:
            if new_name in all_units_data:
                messagebox.showwarning("Trùng tên", "Tên Unit này đã tồn tại. Vui lòng chọn tên khác.")
                return

            # Update all_units_data
            all_units_data[new_name] = all_units_data.pop(old_name)
            
            # Update unit_settings
            if old_name in unit_settings:
                unit_settings[new_name] = unit_settings.pop(old_name)
            else: # If old unit had no settings, ensure new one gets default
                unit_settings[new_name] = {"color": "#F0F0F0"}

            save_all_flashcards_data()
            save_unit_settings()
            rename_window.destroy()
            refresh_unit_display(list_frame)
        elif new_name == old_name:
            rename_window.destroy() # No change, just close
        else:
            messagebox.showwarning("Lỗi nhập liệu", "Vui lòng nhập tên Unit mới.")

    rename_window = Toplevel(root)
    rename_window.title(f"Đổi Tên Unit: {old_name}")
    rename_window.transient(root)
    rename_window.grab_set()
    rename_window.configure(bg="#f5f5f5")

    Label(rename_window, text="Tên mới:", font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_new_name = Entry(rename_window, font=("Arial", 12))
    entry_new_name.grid(row=0, column=1, padx=10, pady=5)
    entry_new_name.insert(0, old_name)

    Button(rename_window, text="Lưu Thay Đổi", command=save_renamed_unit, **button_style).grid(row=1, columnspan=2, pady=10)


def delete_unit(unit_name, list_frame):
    """Deletes a unit and its flashcards."""
    confirm = messagebox.askyesno("Xác nhận Xóa Unit", f"Bạn có chắc chắn muốn xóa Unit '{unit_name}' và TẤT CẢ các thẻ bài bên trong không?\nThao tác này không thể hoàn tác!")
    if confirm:
        if unit_name in all_units_data:
            del all_units_data[unit_name]
        if unit_name in unit_settings:
            del unit_settings[unit_name]
        
        save_all_flashcards_data()
        save_unit_settings()
        refresh_unit_display(list_frame)
        messagebox.showinfo("Xóa thành công", f"Unit '{unit_name}' đã được xóa.")

def change_unit_color(unit_name, list_frame):
    """Changes the background color of a specific unit."""
    color_code = colorchooser.askcolor(title=f"Chọn Màu cho Unit: {unit_name}")
    if color_code[1]: # color_code[1] is the hex string
        if unit_name not in unit_settings:
            unit_settings[unit_name] = {}
        unit_settings[unit_name]["color"] = color_code[1]
        save_unit_settings()
        refresh_unit_display(list_frame)

def open_unit_flashcards(unit_name):
    """Opens the flashcard.py window for the selected unit."""
    # Pass the selected unit_name as a command-line argument
    root.withdraw() # Hide main window while flashcard app is open
    try:
        # Pass unit_name as an argument to flashcard.py
        subprocess.run(["python", "flashcard.py", unit_name], check=True)
    except FileNotFoundError:
        messagebox.showerror("Lỗi", "Không tìm thấy file 'flashcard.py'. Vui lòng đảm bảo file nằm cùng thư mục.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi chạy 'flashcard.py': {e}")
    finally:
        root.deiconify() # Show main window again
        # Reload data and settings in case changes were made in flashcard.py that affect unit lists
        load_all_flashcards_data()
        load_unit_settings()
        refresh_unit_display(list_scrollable_frame) # Refresh units display

# --- Application Exit Handler ---

def on_closing():
    """Function called when the Tkinter window is closed."""
    # Save any final changes (though individual functions should save)
    save_all_flashcards_data()
    save_unit_settings()
    root.destroy()

# --- GUI Setup ---

root = Tk()
root.title("Quản lý Flashcard Units")
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

# --- Load Data and Settings at Startup ---
load_all_flashcards_data()
load_unit_settings()

# ==== Main Frame ====
main_frame = Frame(root, bg="#f5f5f5")
main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

# ==== Title ====
Label(main_frame, text="Quản Lý Các Unit Từ Vựng", font=("Arial", 20, "bold"), bg="#f5f5f5", fg="#333").pack(pady=10)

# ==== Unit List Frame with Scrollbar ====
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

# ==== Control Buttons for Units ====
control_frame = Frame(main_frame, bg="#f5f5f5")
control_frame.pack(pady=10)

Button(control_frame, text="➕ Thêm Unit Mới", command=lambda: add_new_unit_dialog(list_scrollable_frame), **button_style).pack(pady=5)
Button(control_frame, text="🔄 Làm Mới Danh Sách Unit", command=lambda: refresh_unit_display(list_scrollable_frame), **button_style).pack(pady=5)

# --- Initial Display ---
refresh_unit_display(list_scrollable_frame)

# --- Set up graceful exit handler ---
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()