# note.py - Đã cập nhật để hiển thị cả ghi chú và từ vựng, có nút chuyển đổi 2 cột và nút "Edit Từ Vựng"

from tkinter import *
import json
import os
import sys
from tkinter import messagebox

def display_note_window(note_data):
    """Tạo cửa sổ để hiển thị ghi chú chi tiết hoặc danh sách từ vựng."""
    root = Tk()
    root.title(note_data.get("title", "Chi Tiết"))
    root.geometry("1000x600") # Tăng kích thước cửa sổ để chứa 2 cột tốt hơn
    root.configure(bg="#f8f8f8")

    root.update_idletasks()
    x = root.winfo_screenwidth() // 2 - root.winfo_width() // 2
    y = root.winfo_screenheight() // 2 - root.winfo_height() // 2
    root.geometry(f"+{x}+{y}")

    # Tiêu đề
    Label(root, text=note_data.get("title", "Chi Tiết"),
          font=("Arial", 18, "bold"), fg="#333333", bg="#f8f8f8", pady=15).pack()

    # Frame chứa các Text widget và nút điều khiển
    content_frame = Frame(root, bg="#f8f8f8")
    content_frame.pack(fill=BOTH, expand=True, padx=25, pady=10)

    # --- Khởi tạo các Text widget cho chế độ 1 cột và 2 cột ---
    
    # 1 cột (mặc định)
    single_column_frame = Frame(content_frame, bg="white", bd=1, relief="solid")
    single_column_text = Text(single_column_frame, font=("Arial", 12), wrap=WORD,
                              state=DISABLED, bd=0, highlightthickness=0, bg="white",
                              padx=10, pady=10)
    single_column_text.pack(side=LEFT, fill=BOTH, expand=True)
    single_column_scrollbar = Scrollbar(single_column_frame, command=single_column_text.yview)
    single_column_scrollbar.pack(side=RIGHT, fill="y")
    single_column_text.config(yscrollcommand=single_column_scrollbar.set)

    # 2 cột
    two_column_frame = Frame(content_frame, bg="white", bd=1, relief="solid")
    
    left_column_text = Text(two_column_frame, font=("Arial", 12), wrap=WORD,
                            state=DISABLED, bd=0, highlightthickness=0, bg="white",
                            padx=10, pady=10)
    left_column_text.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5)) # Padding phải cho cột trái
    left_column_scrollbar = Scrollbar(two_column_frame, command=left_column_text.yview)
    left_column_scrollbar.pack(side=LEFT, fill="y")
    left_column_text.config(yscrollcommand=left_column_scrollbar.set)

    right_column_text = Text(two_column_frame, font=("Arial", 12), wrap=WORD,
                             state=DISABLED, bd=0, highlightthickness=0, bg="white",
                             padx=10, pady=10)
    right_column_text.pack(side=LEFT, fill=BOTH, expand=True, padx=(5, 0)) # Padding trái cho cột phải
    right_column_scrollbar = Scrollbar(two_column_frame, command=right_column_text.yview)
    right_column_scrollbar.pack(side=RIGHT, fill="y")
    right_column_text.config(yscrollcommand=right_column_scrollbar.set)

    # Biến để theo dõi chế độ hiển thị
    current_display_mode = StringVar(value="single") # "single" hoặc "two"

    def populate_text_widgets():
        # Xóa nội dung cũ
        single_column_text.config(state=NORMAL)
        single_column_text.delete(1.0, END)
        left_column_text.config(state=NORMAL)
        left_column_text.delete(1.0, END)
        right_column_text.config(state=NORMAL)
        right_column_text.delete(1.0, END)

        display_type = note_data.get("display_type", "notes")

        if display_type == "flashcards":
            flashcards = note_data.get("flashcards", [])
            if flashcards:
                # Định nghĩa các tag màu sắc cho từ vựng
                single_column_text.tag_config("english_word", font=("Arial", 13, "bold"), foreground="#0056b3")
                single_column_text.tag_config("vietnamese_word", font=("Arial", 11, "italic"), foreground="#555555")
                single_column_text.tag_config("index_tag", foreground="#888888")

                left_column_text.tag_config("english_word", font=("Arial", 13, "bold"), foreground="#0056b3")
                left_column_text.tag_config("index_tag", foreground="#888888")
                right_column_text.tag_config("vietnamese_word", font=("Arial", 11, "italic"), foreground="#555555")

                for i, card in enumerate(flashcards):
                    english_word = card.get("en", "")
                    vietnamese_word = card.get("vi", "")
                    custom_color = card.get("color", None) # Lấy màu chữ tùy chỉnh

                    # --- Điền vào chế độ 1 cột ---
                    single_column_text.insert(END, f"{i+1}. ", "index_tag")
                    start_en_single = single_column_text.index(INSERT)
                    single_column_text.insert(END, f"{english_word}\n", "english_word")
                    end_en_single = single_column_text.index(INSERT)
                    if custom_color:
                        tag_name_single = f"custom_color_{custom_color.replace('#', '')}"
                        if tag_name_single not in single_column_text.tag_names():
                            single_column_text.tag_config(tag_name_single, foreground=custom_color, font=("Arial", 13, "bold"))
                        single_column_text.tag_add(tag_name_single, start_en_single, end_en_single)
                    single_column_text.insert(END, f"    {vietnamese_word}\n\n", "vietnamese_word")
                    
                    # --- Điền vào chế độ 2 cột ---
                    left_column_text.insert(END, f"{i+1}. ", "index_tag")
                    start_en_left = left_column_text.index(INSERT)
                    left_column_text.insert(END, f"{english_word}\n\n", "english_word") # Thêm khoảng trống để căn bằng
                    end_en_left = left_column_text.index(INSERT)
                    if custom_color:
                        tag_name_left = f"custom_color_{custom_color.replace('#', '')}"
                        if tag_name_left not in left_column_text.tag_names():
                            left_column_text.tag_config(tag_name_left, foreground=custom_color, font=("Arial", 13, "bold"))
                        left_column_text.tag_add(tag_name_left, start_en_left, end_en_left)
                    
                    right_column_text.insert(END, f"\n{vietnamese_word}\n\n", "vietnamese_word") # Thêm dòng mới để căn bằng

            else:
                single_column_text.insert(END, "Không có flashcard nào để hiển thị.", ("Arial", 12, "italic"))
                left_column_text.insert(END, "Không có flashcard nào để hiển thị.", ("Arial", 12, "italic"))
                right_column_text.insert(END, "", ("Arial", 12, "italic")) # Cột phải trống
        else: # display_type == "notes" hoặc không có
            notes_content = note_data.get("notes", "")
            single_column_text.insert(END, notes_content)
            
            # Với chế độ ghi chú, chúng ta chỉ hiển thị ở cột trái và cột phải trống
            left_column_text.insert(END, notes_content)
            right_column_text.insert(END, "\n\n(Nội dung này không được chia thành 2 cột tự động. Vui lòng sử dụng chế độ 1 cột cho ghi chú.)", ("Arial", 10, "italic"))

            # Áp dụng các màu đã lưu (foreground colors)
            colored_sections = note_data.get("colored_sections", [])
            for section in colored_sections:
                start_index = section["start"]
                end_index = section["end"]
                color = section["color"]

                tag_name = f"color_{color.replace('#', '')}"
                if tag_name not in single_column_text.tag_names():
                    single_column_text.tag_config(tag_name, foreground=color)
                if tag_name not in left_column_text.tag_names():
                    left_column_text.tag_config(tag_name, foreground=color)
                
                single_column_text.tag_add(tag_name, start_index, end_index)
                left_column_text.tag_add(tag_name, start_index, end_index)
            
        single_column_text.config(state=DISABLED)
        left_column_text.config(state=DISABLED)
        right_column_text.config(state=DISABLED)

    def switch_layout():
        if current_display_mode.get() == "single":
            single_column_frame.pack_forget()
            two_column_frame.pack(fill=BOTH, expand=True)
            current_display_mode.set("two")
            toggle_button.config(text="1 Cột")
            # Kích hoạt/Vô hiệu hóa nút edit_vocabulary_button
            edit_vocabulary_button.config(state=NORMAL if note_data.get("display_type", "notes") == "flashcards" else DISABLED)
        else:
            two_column_frame.pack_forget()
            single_column_frame.pack(fill=BOTH, expand=True)
            current_display_mode.set("single")
            toggle_button.config(text="2 Cột")
            # Kích hoạt/Vô hiệu hóa nút edit_vocabulary_button
            edit_vocabulary_button.config(state=NORMAL if note_data.get("display_type", "notes") == "flashcards" else DISABLED)

    def edit_vocabulary():
        """Xử lý khi nhấn nút "Edit Từ Vựng"."""
        if note_data.get("display_type", "notes") == "flashcards":
            messagebox.showinfo(
                "Chỉnh Sửa Từ Vựng",
                "Chức năng chỉnh sửa từ vựng cần được thực hiện trong giao diện chính của chương trình (mainsrs.py) hoặc bằng cách chỉnh sửa trực tiếp file JSON của danh sách từ vựng. Cửa sổ này chỉ dùng để xem."
            )
        else:
            # Điều này sẽ không xảy ra nếu nút bị DISABLED đúng cách
            messagebox.showwarning("Thông báo", "Chức năng này chỉ áp dụng cho Danh sách Từ Vựng.")

    # Điền dữ liệu vào các widget ngay khi khởi tạo
    populate_text_widgets()
    
    # Hiển thị mặc định là 1 cột
    single_column_frame.pack(fill=BOTH, expand=True)

    # Frame chứa các nút
    button_frame = Frame(root, bg="#f8f8f8")
    button_frame.pack(pady=10)

    # Nút chuyển đổi layout
    toggle_button = Button(button_frame, text="2 Cột", command=switch_layout,
                           font=("Arial", 13, "bold"), bg="#28a745", fg="white", # Màu xanh lá
                           activebackground="#218838", activeforeground="white",
                           padx=15, pady=8, bd=0, relief="raised")
    toggle_button.pack(side=LEFT, padx=10)

    # Nút Edit Từ Vựng (thay thế Highlighter)
    edit_vocabulary_button = Button(button_frame, text="Edit Từ Vựng", command=edit_vocabulary,
                                    font=("Arial", 13, "bold"), bg="#007bff", fg="white", # Màu xanh dương
                                    activebackground="#0056b3", activeforeground="white",
                                    padx=15, pady=8, bd=0, relief="raised")
    edit_vocabulary_button.pack(side=LEFT, padx=10)
    
    # Vô hiệu hóa nút Edit Từ Vựng nếu đang xem ghi chú ngay từ đầu
    if note_data.get("display_type", "notes") != "flashcards":
        edit_vocabulary_button.config(state=DISABLED)

    # Nút đóng
    Button(button_frame, text="Đóng", command=root.destroy,
           font=("Arial", 13, "bold"), bg="#dc3545", fg="white", # Màu đỏ đậm hơn
           activebackground="#c82333", activeforeground="white",
           padx=15, pady=8, bd=0, relief="raised").pack(side=LEFT, padx=10)

    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        temp_file_path = sys.argv[1]
        if os.path.exists(temp_file_path):
            try:
                with open(temp_file_path, "r", encoding="utf-8") as f:
                    note_data = json.load(f)
                display_note_window(note_data)
            except json.JSONDecodeError:
                messagebox.showerror("Lỗi", "Không thể đọc dữ liệu từ file tạm. Dữ liệu có thể bị hỏng.")
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy file dữ liệu tạm thời.")
    else:
        messagebox.showinfo("Thông báo", "Vui lòng chạy 'mainsrs.py' và sử dụng chức năng 'Xem Ghi Chú' hoặc 'Học' để mở cửa sổ này.")