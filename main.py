import subprocess
from tkinter import *

# --- File Paths Configuration ---
# Centralize your script paths here for easy management
SCRIPT_PATHS = {
    "mainflashcard": "mainflashcard.py",
    "mainsrs": "mainsrs.py",
    # Add other script paths here as you develop more features:
    # "ai_pronunciation": "ai_pronunciation.py",
    # "dictation": "dictation.py",
    # "writing_practice": "writing_practice.py",
    # "vocabulary_export": "vocabulary_export.py",
    # "statistics": "statistics.py",
    # "daily_reminder": "daily_reminder.py",
}

# --- Button Styles ---
setting_button = {
    "font": ("Arial", 14),
    "fg": "#000000",
    "bg": "#ffffff",
    "activebackground": "#000000",
    "activeforeground": "#ffffff",
    "bd": 1,
    "relief": "solid",
    "width": 30,  # Consistent width
    "anchor": "w"  # Left-align text
}

# --- Welcome Screen Function ---
def Start_Welcome_a():
    a = Toplevel(window)
    a.title("Welcome")
    a.configure(bg="White")

    label_a = Label(a, text="Welcome to app IELTS Tool", font=("Arial", 14), bg="White")
    label_a.grid(column=0, row=1, columnspan=2, pady=10)

    btn_clone = Button(a, text="Start now!", command=a.destroy, **setting_button)
    btn_clone.grid(column=0, row=2, columnspan=2, pady=10)

    a.transient(window)
    a.grab_set()

# --- Functions to Run Other Scripts ---
def run_script(script_key):
    """
    Launches a Python script specified by its key in SCRIPT_PATHS.
    Displays an error if the script path is not found.
    """
    script_path = SCRIPT_PATHS.get(script_key)
    if not script_path:
        messagebox.showerror("Lỗi", f"Đường dẫn cho '{script_key}' không được định cấu hình.")
        return

    try:
        subprocess.Popen(["python", script_path])
    except FileNotFoundError:
        messagebox.showerror("Lỗi", f"Không tìm thấy file '{script_path}'. Vui lòng đảm bảo file nằm cùng thư mục.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi chạy '{script_path}': {e}")

# --- Main Window Setup ---
window = Tk()
window.title("IELTS Tool")
window.configure(bg="white")

# Display the welcome screen after a short delay
window.after(100, Start_Welcome_a)

# --- GUI Elements ---

# Menu Label
label_menu = Label(window, text="^Menu^", font=("Arial", 14), fg="blue", bg="yellow", height=2, width=10, bd=1, relief="solid")
label_menu.grid(column=0, row=0, columnspan=2, pady=10)

# Function Buttons
# Use lambda to pass the script key to the general run_script function
flashcard_button = Button(window, text="📘 Flashcard từ vựng", **setting_button, command=lambda: run_script("mainflashcard"))
srs_button = Button(window, text="⏳ Học theo SRS (Spaced Repetition)", **setting_button, command=lambda: run_script("mainsrs"))
voice_button = Button(window, text="🗣️ AI phát âm + luyện nói", **setting_button, command=lambda: messagebox.showinfo("Thông báo", "Tính năng này đang được phát triển.")) # Placeholder
dictation_button = Button(window, text="🎧 Nghe viết (Dictation)", **setting_button, command=lambda: messagebox.showinfo("Thông báo", "Tính năng này đang được phát triển.")) # Placeholder
write_button = Button(window, text="✍️ Viết chính tả / điền từ", **setting_button, command=lambda: messagebox.showinfo("Thông báo", "Tính năng này đang được phát triển.")) # Placeholder
output_vocabulary_button = Button(window, text="📤 Trích xuất từ vựng", **setting_button, command=lambda: messagebox.showinfo("Thông báo", "Tính năng này đang được phát triển.")) # Placeholder
abf_button = Button(window, text="> Thống kê quá trình học <", **setting_button, command=lambda: messagebox.showinfo("Thông báo", "Tính năng này đang được phát triển.")) # Placeholder
notify_button = Button(window, text=">  Nhắc học mỗi ngày <", **setting_button, command=lambda: messagebox.showinfo("Thông báo", "Tính năng này đang được phát triển.")) # Placeholder

# Grid Layout for Buttons
flashcard_button.grid(column=0, row=1, padx=10, pady=5, sticky="w")
srs_button.grid(column=0, row=2, padx=10, pady=5, sticky="w")
voice_button.grid(column=0, row=3, padx=10, pady=5, sticky="w")
dictation_button.grid(column=0, row=4, padx=10, pady=5, sticky="w")
write_button.grid(column=0, row=5, padx=10, pady=5, sticky="w")
output_vocabulary_button.grid(column=0, row=6, padx=10, pady=5, sticky="w")
abf_button.grid(column=0, row=7, padx=10, pady=5, sticky="w")
notify_button.grid(column=0, row=8, padx=10, pady=5, sticky="w")

# --- Run the main application loop ---
window.mainloop()