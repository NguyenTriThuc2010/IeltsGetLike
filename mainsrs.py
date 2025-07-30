# mainsrs.py - Đã cập nhật để dùng note.py hiển thị cả ghi chú và từ vựng
from tkinter import *
from tkinter import messagebox, simpledialog, colorchooser 
import json
import os
import sys
import subprocess

# --- Constants ---
SRS_SCHEDULE_FILE = "srs_schedules.json"
TEMP_SCHEDULE_DATA_FILE = "temp_new_schedule.json"
NOTE_DISPLAY_FILE = "temp_note_display.json" 

FLASHCARDS_MAIN_FILE = "flashcards_data.json" # File chứa tất cả dữ liệu flashcard

# --- Button Styles ---
setting_button = {
    "font": ("Arial", 14),
    "fg": "#000000",
    "bg": "#ffffff",
    "activebackground": "#000000",
    "activeforeground": "#ffffff",
    "bd": 1,
    "relief": "solid",
    "width": 30,
    "anchor": "w"
}

# --- Data Management Functions ---

def load_srs_schedules():
    """Tải các lịch trình SRS từ file JSON và đảm bảo định dạng đúng."""
    if os.path.exists(SRS_SCHEDULE_FILE):
        try:
            with open(SRS_SCHEDULE_FILE, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                normalized_schedules = []
                for item in loaded_data:
                    if isinstance(item, str):
                        normalized_schedules.append({
                            "name": item, 
                            "notes": "", 
                            "notes_format": "plaintext", 
                            "colored_sections": [],
                            "selected_units": [] 
                        })
                    elif isinstance(item, dict):
                        if "notes" not in item:
                            item["notes"] = ""
                        if "notes_format" not in item:
                            item["notes_format"] = "plaintext"
                        if "colored_sections" not in item:
                            item["colored_sections"] = []
                        if "selected_units" not in item: 
                            item["selected_units"] = []
                        normalized_schedules.append(item)
                return normalized_schedules
        except json.JSONDecodeError:
            messagebox.showwarning("Lỗi dữ liệu", "Không thể đọc lịch trình SRS. Dữ liệu có thể bị hỏng và sẽ được khởi tạo lại.")
            return []
    return []

def save_srs_schedules(schedules):
    """Lưu các lịch trình SRS vào file JSON."""
    with open(SRS_SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=4)

def load_all_flashcards_data():
    """Tải tất cả dữ liệu flashcard từ flashcards_data.json."""
    if os.path.exists(FLASHCARDS_MAIN_FILE):
        try:
            with open(FLASHCARDS_MAIN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict): 
                    return data
                else:
                    messagebox.showwarning("Lỗi dữ liệu", "flashcards_data.json có định dạng không hợp lệ (không phải đối tượng JSON gốc).")
                    return {}
        except json.JSONDecodeError:
            messagebox.showwarning("Lỗi dữ liệu", "Không thể đọc flashcards_data.json. Dữ liệu có thể bị hỏng.")
            return {}
    return {} 

def load_flashcards_from_unit(unit_name):
    """Tải các flashcard cho một unit cụ thể từ flashcards_data.json."""
    all_data = load_all_flashcards_data()
    return all_data.get(unit_name, []) 

def create_new_unit_via_manager(parent_window):
    """Mở flashcard_unit_manager.py để tạo unit mới hoặc chỉnh sửa.
    LƯU Ý: flashcard_unit_manager.py chưa được cung cấp, đây chỉ là placeholder.
    """
    try:
        python_executable = sys.executable
        # Đây là một placeholder, bạn cần file flashcard_unit_manager.py thực tế
        messagebox.showinfo("Thông báo", "Chức năng này cần file 'flashcard_unit_manager.py' để quản lý unit. "
                                        "Hiện tại bạn có thể chỉnh sửa file flashcards_data.json trực tiếp hoặc dùng nút 'Chỉnh Sửa Từ Vựng Gốc' để chỉnh sửa từ.")
        # Ví dụ nếu bạn có file:
        # subprocess.Popen([python_executable, "flashcard_unit_manager.py"]) 
        # messagebox.showinfo("Thông báo", "Vui lòng tạo/chỉnh sửa unit và từ vựng trong cửa sổ quản lý. Sau đó, nhấn 'Làm Mới Danh Sách Unit' tại đây.")
        
    except FileNotFoundError:
        messagebox.showerror("Lỗi", f"Không tìm thấy file 'flashcard_unit_manager.py'. Vui lòng đảm bảo file nằm cùng thư mục.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi mở 'flashcard_unit_manager.py': {e}")


# --- GUI Management for Schedules ---

def apply_color_to_text_widget_selection(text_widget):
    """Áp dụng màu sắc cho văn bản được chọn trong Text widget."""
    try:
        start = text_widget.tag_ranges("sel")[0]
        end = text_widget.tag_ranges("sel")[1]
    except IndexError:
        messagebox.showwarning("Thông báo", "Vui lòng chọn văn bản để tô màu.")
        return

    color_code = colorchooser.askcolor(title="Chọn màu văn bản")[1]
    if color_code:
        for tag_name in text_widget.tag_names():
            if tag_name.startswith("color_"):
                text_widget.tag_remove(tag_name, start, end)

        tag_name = f"color_{color_code.replace('#', '')}"
        text_widget.tag_config(tag_name, foreground=color_code)
        text_widget.tag_add(tag_name, start, end)

def open_edit_notes_window(index, srs_schedules, schedule_list_frame):
    """Mở cửa sổ chỉnh sửa ghi chú riêng biệt."""
    current_data = srs_schedules[index]
    old_notes_text = current_data.get("notes", "")
    old_colored_sections = current_data.get("colored_sections", [])

    edit_notes_win = Toplevel(schedule_list_frame) 
    edit_notes_win.title(f"Sửa Ghi Chú cho '{current_data['name']}'")
    edit_notes_win.geometry("600x450")
    edit_notes_win.transient(schedule_list_frame.winfo_toplevel()) 
    edit_notes_win.grab_set() 

    edit_notes_win.update_idletasks()
    x = edit_notes_win.winfo_screenwidth() // 2 - edit_notes_win.winfo_width() // 2
    y = edit_notes_win.winfo_screenheight() // 2 - edit_notes_win.winfo_height() // 2
    edit_notes_win.geometry(f"+{x}+{y}")

    Label(edit_notes_win, text=f"Ghi chú cho: {current_data['name']}",
          font=("Arial", 14, "bold"), pady=10).pack()

    text_notes = Text(edit_notes_win, font=("Arial", 11), wrap=WORD, bd=1, relief="solid", height=15)
    text_notes.pack(fill=BOTH, expand=True, padx=10, pady=5)

    notes_scrollbar = Scrollbar(edit_notes_win, command=text_notes.yview)
    notes_scrollbar.pack(side=RIGHT, fill="y")
    text_notes.config(yscrollcommand=notes_scrollbar.set)

    text_notes.insert(END, old_notes_text)
    for section in old_colored_sections:
        start_index = section["start"]
        end_index = section["end"]
        color = section["color"]

        tag_name = f"color_{color.replace('#', '')}"
        if tag_name not in text_notes.tag_names():
            text_notes.tag_config(tag_name, foreground=color)
        text_notes.tag_add(tag_name, start_index, end_index)

    color_button = Button(edit_notes_win, text="🎨 Tô màu văn bản chọn",
                          command=lambda: apply_color_to_text_widget_selection(text_notes),
                          font=("Arial", 10), bg="#add8e6", fg="#333", padx=5, pady=2)
    color_button.pack(pady=5)

    def save_notes_changes():
        new_notes_text = text_notes.get("1.0", END).strip()
        new_colored_sections = []
        for tag_name in text_notes.tag_names():
            if tag_name.startswith("color_"):
                tag_config = text_notes.tag_cget(tag_name, "foreground")
                ranges = text_notes.tag_ranges(tag_name)
                for i in range(0, len(ranges), 2):
                    start_index = ranges[i]
                    end_index = ranges[i+1]
                    new_colored_sections.append({
                        "start": str(start_index),
                        "end": str(end_index),
                        "color": tag_config
                    })
        
        srs_schedules[index]["notes"] = new_notes_text
        srs_schedules[index]["colored_sections"] = new_colored_sections
        save_srs_schedules(srs_schedules)
        refresh_schedule_display(schedule_list_frame, srs_schedules)
        messagebox.showinfo("Thành công", "Ghi chú đã được cập nhật!")
        edit_notes_win.destroy()

    def cancel_notes_changes():
        edit_notes_win.destroy()

    button_frame = Frame(edit_notes_win, pady=10)
    button_frame.pack()

    Button(button_frame, text="Lưu Ghi Chú", command=save_notes_changes,
           font=("Arial", 12, "bold"), bg="#28a745", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)
    Button(button_frame, text="Hủy", command=cancel_notes_changes,
           font=("Arial", 12), bg="#dc3545", fg="white", padx=10, pady=5).pack(side=RIGHT, padx=5)

    edit_notes_win.protocol("WM_DELETE_WINDOW", cancel_notes_changes)
    edit_notes_win.focus_set()


def refresh_schedule_display(schedule_list_frame, srs_schedules):
    """Làm mới hiển thị danh sách lịch trình."""
    for widget in schedule_list_frame.winfo_children():
        widget.destroy()

    if not srs_schedules:
        Label(schedule_list_frame, text="Chưa có lịch trình nào. Hãy thêm mới!",
              font=("Arial", 12), fg="gray", bg="white").pack(pady=10)
        return

    for i, schedule_data in enumerate(srs_schedules):
        schedule_row_frame = Frame(schedule_list_frame, bg="#e0e0e0", bd=1, relief="solid", padx=5, pady=5)
        schedule_row_frame.pack(fill=X, pady=3)

        text_frame = Frame(schedule_row_frame, bg="#e0e0e0")
        text_frame.pack(side=LEFT, padx=5, pady=2, expand=True, fill=X)

        Label(text_frame, text=f"Lịch trình: {schedule_data['name']}",
              font=("Arial", 12, "bold"), bg="#e0e0e0", wraplength=400, justify=LEFT).pack(anchor="w")
        
        display_notes = schedule_data["notes"]
        if len(display_notes) > 100:
            display_notes = display_notes[:97] + "..."
        if display_notes:
            Label(text_frame, text=f"Ghi chú: {display_notes}",
                  font=("Arial", 10, "italic"), bg="#e0e0e0", fg="#666", wraplength=400, justify=LEFT).pack(anchor="w")
        else:
            Label(text_frame, text="Chưa có ghi chú.",
                  font=("Arial", 10, "italic"), bg="#e0e0e0", fg="#888", wraplength=400, justify=LEFT).pack(anchor="w")
        
        selected_units_count = len(schedule_data.get("selected_units", []))
        Label(text_frame, text=f"Unit đã chọn: {selected_units_count} unit(s)",
              font=("Arial", 9, "italic"), bg="#e0e0e0", fg="#444", wraplength=400, justify=LEFT).pack(anchor="w")


        button_actions_frame = Frame(schedule_row_frame, bg="#e0e0e0")
        button_actions_frame.pack(side=RIGHT)
        
        Button(button_actions_frame, text="⚙️ Cài đặt Unit",
               command=lambda data=schedule_data, idx=i: open_schedule_unit_settings(data, idx, srs_schedules, schedule_list_frame),
               font=("Arial", 9), bg="#6c757d", fg="white", bd=0, padx=5, pady=2).pack(side=LEFT, padx=2)

        Button(button_actions_frame, text="📖 Xem",
               command=lambda data=schedule_data: view_detailed_notes(data),
               font=("Arial", 9), bg="#4CAF50", fg="white", bd=0, padx=5, pady=2).pack(side=LEFT, padx=2)

        Button(button_actions_frame, text="📝 Sửa Ghi chú",
               command=lambda idx=i: open_edit_notes_window(idx, srs_schedules, schedule_list_frame),
               font=("Arial", 9), bg="#ffc107", fg="#333", bd=0, padx=5, pady=2).pack(side=LEFT, padx=2)

        Button(button_actions_frame, text="✏️ Sửa Tên",
               command=lambda idx=i: edit_srs_schedule(idx, srs_schedules, schedule_list_frame),
               font=("Arial", 9), bg="#007ACC", fg="white", bd=0, padx=5, pady=2).pack(side=LEFT, padx=2)

        Button(button_actions_frame, text="🗑️ Xóa",
               command=lambda idx=i: delete_srs_schedule(idx, srs_schedules, schedule_list_frame),
               font=("Arial", 9), bg="#CC0000", fg="white", bd=0, padx=5, pady=2).pack(side=LEFT, padx=2)
        
        # MODIFIED: Nút Học sẽ gọi start_srs_session như trước
        Button(button_actions_frame, text="🚀 Học",
               command=lambda data=schedule_data: start_srs_session(data),
               font=("Arial", 9), bg="#28a745", fg="white", bd=0, padx=5, pady=2).pack(side=LEFT, padx=2)

def add_srs_schedule(srs_schedules, schedule_list_frame):
    """
    Mở cửa sổ 'datelearn.py' để thêm lịch trình mới.
    Sau khi datelearn.py đóng, kiểm tra file tạm để lấy dữ liệu.
    """
    if os.path.exists(TEMP_SCHEDULE_DATA_FILE):
        os.remove(TEMP_SCHEDULE_DATA_FILE)

    try:
        python_executable = sys.executable
        subprocess.run([python_executable, "datelearn.py"], check=True)

        if os.path.exists(TEMP_SCHEDULE_DATA_FILE):
            with open(TEMP_SCHEDULE_DATA_FILE, "r", encoding="utf-8") as f:
                new_schedule_data = json.load(f)
            
            os.remove(TEMP_SCHEDULE_DATA_FILE)

            new_name = new_schedule_data.get("name", "").strip()
            new_notes = new_schedule_data.get("notes", "").strip()
            new_notes_format = new_schedule_data.get("notes_format", "plaintext")
            new_colored_sections = new_schedule_data.get("colored_sections", [])

            if not new_name:
                messagebox.showwarning("Lỗi", "Tên lịch trình không được để trống.")
                return

            if any(s['name'] == new_name for s in srs_schedules):
                messagebox.showwarning("Trùng tên", "Lịch trình với tên này đã tồn tại.")
                return

            srs_schedules.append({
                "name": new_name, 
                "notes": new_notes,
                "notes_format": new_notes_format,
                "colored_sections": new_colored_sections,
                "selected_units": [] 
            })
            save_srs_schedules(srs_schedules)
            refresh_schedule_display(schedule_list_frame, srs_schedules)
            messagebox.showinfo("Thành công", f"Lịch trình '{new_name}' đã được thêm!")
        else:
            messagebox.showinfo("Thông báo", "Bạn đã hủy việc tạo lịch trình mới.")

    except FileNotFoundError:
        messagebox.showerror("Lỗi", "Không tìm thấy file 'datelearn.py'. Vui lòng đảm bảo file nằm cùng thư mục.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi mở hoặc xử lý 'datelearn.py': {e}")


def edit_srs_schedule(index, srs_schedules, schedule_list_frame):
    """Mở hộp thoại để sửa tên lịch trình."""
    if index < 0 or index >= len(srs_schedules):
        messagebox.showerror("Lỗi", "Chỉ mục lịch trình không hợp lệ.")
        return

    current_data = srs_schedules[index]
    old_name = current_data["name"]

    edited_name = simpledialog.askstring("Sửa Tên Lịch Trình SRS", f"Sửa TÊN lịch trình '{old_name}':",
                                         initialvalue=old_name)
    if not edited_name:
        return

    edited_name = edited_name.strip()
    if not edited_name:
        messagebox.showwarning("Lỗi", "Tên lịch trình không được để trống.")
        return

    if any(s['name'] == edited_name for i, s in enumerate(srs_schedules) if i != index):
        messagebox.showwarning("Trùng tên", "Lịch trình với tên này đã tồn tại.")
        return
    
    if edited_name != old_name:
        srs_schedules[index]["name"] = edited_name
        save_srs_schedules(srs_schedules)
        refresh_schedule_display(schedule_list_frame, srs_schedules)
        messagebox.showinfo("Thành công", "Tên lịch trình đã được sửa!")

def delete_srs_schedule(index, srs_schedules, schedule_list_frame):
    """Xóa một lịch trình khỏi danh sách."""
    if index < 0 or index >= len(srs_schedules):
        messagebox.showerror("Lỗi", "Chỉ mục lịch trình không hợp lệ.")
        return

    confirm = messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc chắn muốn xóa lịch trình '{srs_schedules[index]['name']}' không?")
    if confirm:
        srs_schedules.pop(index)
        save_srs_schedules(srs_schedules)
        refresh_schedule_display(schedule_list_frame, srs_schedules)
        messagebox.showinfo("Xóa thành công", "Lịch trình đã được xóa.")

# --- Functions for Unit Settings and Learning ---

def open_schedule_unit_settings(schedule_data, index, srs_schedules_list, schedule_list_frame):
    """
    Mở cửa sổ cài đặt unit cho một lịch trình cụ thể.
    Người dùng có thể chọn các unit để học cho lịch trình này.
    """
    select_units_win = Toplevel(schedule_list_frame)
    select_units_win.title(f"Cài Đặt Unit cho: {schedule_data['name']}")
    select_units_win.geometry("500x600")
    select_units_win.configure(bg="#f8f8f8")
    select_units_win.transient(schedule_list_frame.winfo_toplevel())
    select_units_win.grab_set()

    select_units_win.update_idletasks()
    x = select_units_win.winfo_screenwidth() // 2 - select_units_win.winfo_width() // 2
    y = select_units_win.winfo_screenheight() // 2 - select_units_win.winfo_height() // 2
    select_units_win.geometry(f"+{x}+{y}")

    Label(select_units_win, text=f"Chọn Các Unit Để Học\ncho lịch trình: {schedule_data['name']}",
              font=("Arial", 16, "bold"), bg="#ff8f8f8", pady=15).pack()

    unit_list_frame = Frame(select_units_win, bg="white", bd=1, relief="solid")
    unit_list_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    canvas = Canvas(unit_list_frame, bg="white")
    scrollbar = Scrollbar(unit_list_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg="white")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    current_selected_units_for_this_schedule = schedule_data.get("selected_units", [])
    selected_unit_vars = {} 

    def refresh_unit_display_internal():
        """Làm mới hiển thị danh sách unit bên trong cửa sổ cài đặt."""
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        selected_unit_vars.clear() 

        all_flashcards_data = load_all_flashcards_data()
        current_units_from_data = list(all_flashcards_data.keys())

        if not current_units_from_data:
            Label(scrollable_frame, text="Chưa có unit nào trong dữ liệu. Hãy tạo unit mới!",
                          font=("Arial", 12), fg="gray", bg="white").pack(pady=20)
            Button(scrollable_frame, text="➕ Tạo Unit Mới",
                           command=lambda: create_new_unit_via_manager(select_units_win), 
                           font=("Arial", 12, "bold"), bg="#007ACC", fg="white", padx=15, pady=8).pack(pady=10)
        else:
            for unit_name in current_units_from_data:
                var = IntVar()
                if unit_name in current_selected_units_for_this_schedule:
                    var.set(1)
                selected_unit_vars[unit_name] = var
                Checkbutton(scrollable_frame, text=unit_name, variable=var,
                                font=("Arial", 12), bg="white", anchor="w", padx=5, pady=2).pack(fill=X)
        
        scrollable_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    refresh_unit_display_internal() # Khởi tạo hiển thị lần đầu

    def on_save_selection():
        newly_selected_units = [unit_name for unit_name, var in selected_unit_vars.items() if var.get() == 1]
        
        schedule_data["selected_units"] = newly_selected_units
        save_srs_schedules(srs_schedules_list)
        
        messagebox.showinfo("Thành công", f"Đã lưu các unit đã chọn cho lịch trình '{schedule_data['name']}'.")
        refresh_schedule_display(schedule_list_frame, srs_schedules_list)
        select_units_win.destroy()

    def on_cancel_selection():
        select_units_win.destroy()

    button_frame = Frame(select_units_win, bg="#f8f8f8", pady=10)
    button_frame.pack(pady=10)

    Button(button_frame, text="✅ Lưu Cài Đặt Unit",
               command=on_save_selection,
               font=("Arial", 12, "bold"), bg="#28a745", fg="white", padx=15, pady=8).pack(side=LEFT, padx=10)
    
    Button(button_frame, text="🔄 Làm Mới Danh Sách Unit",
               command=refresh_unit_display_internal,
               font=("Arial", 10), bg="#007ACC", fg="white", padx=10, pady=5).pack(side=LEFT, padx=10)

    Button(select_units_win, text="Hủy", command=on_cancel_selection,
               font=("Arial", 12), bg="#dc3545", fg="white", padx=10, pady=5).pack(pady=5)

    select_units_win.protocol("WM_DELETE_WINDOW", on_cancel_selection)
    select_units_win.wait_window() 

# MODIFIED: Hàm start_srs_session để chuẩn bị dữ liệu cho note.py
def start_srs_session(schedule_data):
    """
    Hàm này sẽ được gọi khi người dùng nhấn nút 'Học'.
    Nó sẽ tải các flashcard từ các unit đã được cấu hình cho lịch trình này
    và chuẩn bị dữ liệu để hiển thị bằng note.py.
    """
    selected_units = schedule_data.get("selected_units", [])

    if not selected_units:
        messagebox.showwarning("Thông báo", 
                               "Chưa có unit nào được chọn cho lịch trình này.\n"
                               "Vui lòng nhấn '⚙️ Cài đặt Unit' để chọn các unit cần học trước.")
        return

    all_flashcards = []
    missing_units_with_data = [] 
    for unit_name in selected_units:
        flashcards_in_unit = load_flashcards_from_unit(unit_name)
        if flashcards_in_unit:
            all_flashcards.extend(flashcards_in_unit)
        else:
            missing_units_with_data.append(unit_name)

    if not all_flashcards:
        messagebox.showerror("Lỗi", 
                             "Không tìm thấy thẻ nào trong các unit đã chọn hoặc các unit đó không tồn tại trong dữ liệu.\n"
                             "Vui lòng kiểm tra lại 'flashcards_data.json'.")
        if missing_units_with_data:
            messagebox.showwarning("Thiếu dữ liệu Unit", 
                                   f"Các unit sau không có dữ liệu thẻ: {', '.join(missing_units_with_data)}")
        return

    # NEW: Chuẩn bị dữ liệu flashcard để gửi tới note.py
    flashcard_display_data = {
        "display_type": "flashcards", # Loại hiển thị: flashcards
        "title": f"Danh Sách Từ Vựng Cho Lịch Trình: {schedule_data['name']}",
        "flashcards": all_flashcards, # Danh sách flashcard
        "notes": "", # Trường này có thể rỗng nếu chỉ hiển thị flashcard
        "notes_format": "plaintext",
        "colored_sections": []
    }

    try:
        python_executable = sys.executable
        # Ghi dữ liệu flashcard vào file tạm thời
        with open(NOTE_DISPLAY_FILE, "w", encoding="utf-8") as f:
            json.dump(flashcard_display_data, f, ensure_ascii=False, indent=4)
        
        # Gọi note.py để hiển thị flashcard
        subprocess.Popen([python_executable, "note.py", NOTE_DISPLAY_FILE])
        
        messagebox.showinfo("Bắt đầu học SRS", 
                             f"Đã mở cửa sổ học cho lịch trình: '{schedule_data['name']}'\n"
                             f"Tổng số thẻ: {len(all_flashcards)}")

    except FileNotFoundError:
        messagebox.showerror("Lỗi", "Không tìm thấy file 'note.py'. Vui lòng đảm bảo file nằm cùng thư mục.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi mở hoặc xử lý 'note.py': {e}")


def view_detailed_notes(schedule_data):
    """
    Mở cửa sổ note.py để hiển thị chi tiết ghi chú.
    Truyền dữ liệu ghi chú và định dạng qua file tạm.
    """
    if os.path.exists(NOTE_DISPLAY_FILE):
        os.remove(NOTE_DISPLAY_FILE)
    
    notes_to_display = {
        "display_type": "notes", # Loại hiển thị: ghi chú
        "title": f"Ghi chú cho lịch trình: {schedule_data['name']}",
        "notes": schedule_data.get("notes", ""),
        "notes_format": schedule_data.get("notes_format", "plaintext"),
        "colored_sections": schedule_data.get("colored_sections", [])
    }
    
    try:
        python_executable = sys.executable
        with open(NOTE_DISPLAY_FILE, "w", encoding="utf-8") as f:
            json.dump(notes_to_display, f, ensure_ascii=False, indent=4)
        
        subprocess.Popen([python_executable, "note.py", NOTE_DISPLAY_FILE])
    except FileNotFoundError:
        messagebox.showerror("Lỗi", "Không tìm thấy file 'note.py'. Vui lòng đảm bảo file nằm cùng thư mục.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi mở hoặc xử lý 'note.py': {e}")

# NEW FUNCTION: Open the vocabulary editor
def open_vocabulary_editor(parent_window):
    """
    Mở edit.py để chỉnh sửa trực tiếp file flashcards_data.json.
    """
    try:
        python_executable = sys.executable
        edit_script_path = os.path.join(os.path.dirname(__file__), "edit.py")
        
        # Kiểm tra xem file flashcards_data.json có tồn tại không, nếu không thì tạo mới
        if not os.path.exists(FLASHCARDS_MAIN_FILE):
            with open(FLASHCARDS_MAIN_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4) # Tạo một JSON rỗng

        subprocess.Popen([python_executable, edit_script_path, FLASHCARDS_MAIN_FILE])
    except FileNotFoundError:
        messagebox.showerror("Lỗi", "Không tìm thấy file 'edit.py'. Vui lòng đảm bảo file nằm cùng thư mục.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi mở trình chỉnh sửa từ vựng: {e}")


# --- Hàm tạo và hiển thị cửa sổ SRS Method ---
def create_srs_method_window(parent_root):
    window_add_srs = Toplevel(parent_root)
    window_add_srs.title("Quản lý Lịch Trình Ôn Tập SRS")
    window_add_srs.geometry("750x600")
    window_add_srs.configure(bg="#f0f0f0")

    window_add_srs.grab_set() 

    Label(window_add_srs,
          text="Quản lý Lịch Trình Ôn Tập Spaced Repetition",
          font=("Arial", 18, "bold"),
          bg="#f0f0f0",
          fg="#333",
          pady=15, wraplength=700).pack()
    Label(window_add_srs,
          text="Tại đây, bạn sẽ thiết lập và quản lý các lịch học tùy chỉnh của mình để học theo phương pháp lặp lại ngắt quãng.",
          font=("Arial", 8, "italic"),
          bg="#f0f0f0",
          fg="#555",
          pady=5, wraplength=700).pack()
    
    Button(window_add_srs, text="➕ Thêm Lịch Trình Mới", 
           command=lambda: add_srs_schedule(srs_schedules, schedule_list_scrollable_frame), 
           **setting_button).pack(pady=10)

    list_canvas = Canvas(window_add_srs, bg="white", bd=0, highlightthickness=0)
    list_scrollbar = Scrollbar(window_add_srs, orient="vertical", command=list_canvas.yview)
    schedule_list_scrollable_frame = Frame(list_canvas, bg="white")

    schedule_list_scrollable_frame.bind(
        "<Configure>",
        lambda e: list_canvas.configure(
            scrollregion=list_canvas.bbox("all")
        )
    )

    list_canvas.create_window((0, 0), window=schedule_list_scrollable_frame, anchor="nw")
    list_canvas.configure(yscrollcommand=list_scrollbar.set)

    list_canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=20, pady=10)
    list_scrollbar.pack(side=RIGHT, fill="y", padx=(0, 20), pady=10)

    srs_schedules = load_srs_schedules() 
    refresh_schedule_display(schedule_list_scrollable_frame, srs_schedules)

    # NEW: Nút mở trình chỉnh sửa từ vựng gốc
    Button(window_add_srs,
           text="✏️ Chỉnh Sửa Từ Vựng Gốc",
           command=lambda: open_vocabulary_editor(window_add_srs),
           font=("Arial", 12, "bold"),
           bg="#8A2BE2", # Màu tím để dễ phân biệt
           fg="#ffffff",
           bd=0,
           padx=10,
           pady=5).pack(pady=10) # Thêm padding để tách biệt với nút đóng

    Button(window_add_srs,
           text="Đóng",
           command=window_add_srs.destroy,
           font=("Arial", 12),
           bg="#CC0000",
           fg="#ffffff",
           bd=0,
           padx=10,
           pady=5).pack(pady=5) # Giảm padding để nằm gần nút chỉnh sửa

    window_add_srs.protocol("WM_DELETE_WINDOW", window_add_srs.destroy)
    window_add_srs.focus_set()


# --- Main execution block for mainsrs.py ---
if __name__ == "__main__":
    # Đảm bảo file flashcards_data.json tồn tại khi khởi chạy chính
    if not os.path.exists(FLASHCARDS_MAIN_FILE):
        with open(FLASHCARDS_MAIN_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4) 

    srs_root_window = Tk()
    srs_root_window.withdraw() 

    create_srs_method_window(srs_root_window)

    srs_root_window.mainloop()

    srs_root_window.destroy()
    sys.exit()