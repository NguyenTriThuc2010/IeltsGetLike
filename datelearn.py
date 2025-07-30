# datelearn.py - Đã được làm gọn chỉ cho chức năng THÊM MỚI
from tkinter import *
from tkinter import messagebox, colorchooser
import json
import sys
import os # Cần import os để xử lý file tạm

def save_and_close(root, entry_name, text_notes):
    """Lưu dữ liệu lịch trình mới và đóng cửa sổ."""
    name = entry_name.get().strip()
    notes_text = text_notes.get("1.0", END).strip()

    if not name:
        messagebox.showwarning("Lỗi", "Tên lịch trình không được để trống.")
        return

    # Thu thập thông tin về các tag màu (dành cho ghi chú MỚI)
    colored_sections = []
    for tag_name in text_notes.tag_names():
        if tag_name.startswith("color_"):
            tag_config = text_notes.tag_cget(tag_name, "foreground")
            ranges = text_notes.tag_ranges(tag_name)
            for i in range(0, len(ranges), 2):
                start_index = ranges[i]
                end_index = ranges[i+1]
                colored_sections.append({
                    "start": str(start_index),
                    "end": str(end_index),
                    "color": tag_config
                })

    schedule_data = {
        "name": name,
        "notes": notes_text,
        "notes_format": "tkinter_tags",
        "colored_sections": colored_sections
    }
    
    try:
        with open("temp_new_schedule.json", "w", encoding="utf-8") as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=4)
        root.destroy()
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu lịch trình: {e}")

def apply_color_to_selection(text_widget):
    """Áp dụng màu sắc cho văn bản được chọn trong Text widget."""
    try:
        start = text_widget.tag_ranges("sel")[0]
        end = text_widget.tag_ranges("sel")[1]
    except IndexError:
        messagebox.showwarning("Thông báo", "Vui lòng chọn văn bản để tô màu.")
        return

    color_code = colorchooser.askcolor(title="Chọn màu văn bản")[1]
    if color_code:
        # Xóa các tag màu hiện có trong vùng chọn để tránh xung đột
        for tag_name in text_widget.tag_names():
            if tag_name.startswith("color_"):
                text_widget.tag_remove(tag_name, start, end)

        tag_name = f"color_{color_code.replace('#', '')}"
        text_widget.tag_config(tag_name, foreground=color_code)
        text_widget.tag_add(tag_name, start, end)

# Hàm chính tạo cửa sổ datelearn
def create_datelearn_window():
    root = Tk()
    root.title("Tạo Lịch Trình Học Mới")
    root.geometry("650x550")
    root.configure(bg="#f8f8f8")

    root.update_idletasks()
    x = root.winfo_screenwidth() // 2 - root.winfo_width() // 2
    y = root.winfo_screenheight() // 2 - root.winfo_height() // 2
    root.geometry(f"+{x}+{y}")

    Label(root, text="Thiết Lập Lịch Trình Học Mới", 
          font=("Arial", 16, "bold"), bg="#f8f8f8", pady=15).pack()
    
    input_frame = Frame(root, bg="#f8f8f8", padx=20, pady=10)
    input_frame.pack(fill=BOTH, expand=True)

    Label(input_frame, text="Tên Lịch Trình:", font=("Arial", 12), bg="#f8f8f8").grid(row=0, column=0, sticky="w", pady=5)
    entry_name = Entry(input_frame, font=("Arial", 12), width=50, bd=1, relief="solid")
    entry_name.grid(row=0, column=1, sticky="ew", pady=5)

    Label(input_frame, text="Ghi Chú:", font=("Arial", 12), bg="#f8f8f8").grid(row=1, column=0, sticky="nw", pady=5)
    
    text_notes = Text(input_frame, font=("Arial", 11), width=50, height=10, bd=1, relief="solid", wrap=WORD)
    text_notes.grid(row=1, column=1, sticky="nsew", pady=5)

    notes_scrollbar = Scrollbar(input_frame, command=text_notes.yview)
    notes_scrollbar.grid(row=1, column=2, sticky="ns")
    text_notes.config(yscrollcommand=notes_scrollbar.set)

    color_button = Button(input_frame, text="🎨 Tô màu văn bản chọn", 
                          command=lambda: apply_color_to_selection(text_notes),
                          font=("Arial", 10), bg="#add8e6", fg="#333", padx=5, pady=2)
    color_button.grid(row=2, column=1, sticky="w", pady=5, padx=(0, 0))

    input_frame.grid_rowconfigure(1, weight=1)
    input_frame.grid_columnconfigure(1, weight=1)

    Label(input_frame, text="Chọn các khoảng thời gian ôn tập (ví dụ: 1, 3, 7):", 
          font=("Arial", 12), bg="#f8f8f8").grid(row=3, column=0, columnspan=2, sticky="w", pady=10)
    
    Label(input_frame, text="[Các lựa chọn cho khoảng thời gian ôn tập sẽ ở đây]", 
          font=("Arial", 10, "italic"), fg="gray", bg="#f8f8f8").grid(row=4, column=0, columnspan=2, sticky="ew", padx=10)

    button_frame = Frame(root, bg="#f8f8f8", pady=20)
    button_frame.pack()

    Button(button_frame, text="Lưu Lịch Trình", 
           command=lambda: save_and_close(root, entry_name, text_notes),
           font=("Arial", 12, "bold"), bg="#28a745", fg="white", padx=15, pady=8).pack(side=LEFT, padx=10)
    
    Button(button_frame, text="Hủy", 
           command=root.destroy,
           font=("Arial", 12), bg="#dc3545", fg="white", padx=15, pady=8).pack(side=RIGHT, padx=10)

    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()

if __name__ == "__main__":
    create_datelearn_window()