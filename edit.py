# edit.py - Giao diện chỉnh sửa và lưu từ vựng (flashcards) theo Unit

from tkinter import *
from tkinter import messagebox, scrolledtext, simpledialog
import json
import os
import sys

class VocabularyEditor:
    def __init__(self, master, file_path):
        self.master = master
        self.master.title(f"Quản Lý Từ Vựng Theo Unit - {os.path.basename(file_path)}")
        self.master.configure(bg="#f8f8f8") # Màu nền mặc định ban đầu

        self.file_path = file_path
        self.all_vocabulary_data = {} 
        self.current_unit_name = None 
        self.current_flashcards = [] 

        # Định nghĩa các chủ đề màu sắc
        self.themes = {
            "Light": {
                "bg": "#f8f8f8",
                "frame_bg": "#e0e0e0",
                "label_bg": "#f8f8f8",
                "unit_list_bg": "white",
                "button_bg": "#007ACC", "button_fg": "white",
                "add_button_bg": "#28a745", "add_button_fg": "white",
                "delete_button_bg": "#dc3545", "delete_button_fg": "white",
                "cancel_button_bg": "#ff7043", "cancel_button_fg": "white",
                "selected_unit_bg": "#aaffaa",
                "flashcard_text_bg": "white",
                "flashcard_text_fg_en": "#0056b3",
                "flashcard_text_fg_vi": "#555555",
                "flashcard_text_fg_index": "#777777",
                "flashcard_selected_bg": "lightblue"
            },
            "Dark": {
                "bg": "#2c2c2c",
                "frame_bg": "#3c3c3c",
                "label_bg": "#2c2c2c",
                "unit_list_bg": "#4c4c4c",
                "button_bg": "#005699", "button_fg": "white",
                "add_button_bg": "#1e7e34", "add_button_fg": "white",
                "delete_button_bg": "#a71d2a", "delete_button_fg": "white",
                "cancel_button_bg": "#cc5200", "cancel_button_fg": "white",
                "selected_unit_bg": "#4CAF50", # Darker green
                "flashcard_text_bg": "#3c3c3c",
                "flashcard_text_fg_en": "#add8e6", # Light blue
                "flashcard_text_fg_vi": "#cccccc", # Light gray
                "flashcard_text_fg_index": "#aaaaaa",
                "flashcard_selected_bg": "#6a5acd" # Medium purple
            },
            "Blue": {
                "bg": "#e0f2f7", # Light Cyan
                "frame_bg": "#b3e5fc", # Light Blue
                "label_bg": "#e0f2f7",
                "unit_list_bg": "#e1f5fe", # Lighter Blue
                "button_bg": "#01579b", "button_fg": "white", # Darker Blue
                "add_button_bg": "#4CAF50", "add_button_fg": "white",
                "delete_button_bg": "#EF5350", "delete_button_fg": "white",
                "cancel_button_bg": "#FF8A65", "cancel_button_fg": "white",
                "selected_unit_bg": "#81C784", # Green
                "flashcard_text_bg": "#e3f2fd", # Pale Blue
                "flashcard_text_fg_en": "#1565c0", # Royal Blue
                "flashcard_text_fg_vi": "#424242",
                "flashcard_text_fg_index": "#616161",
                "flashcard_selected_bg": "#90CAF9" # Lighter Blue
            }
        }
        self.current_theme_name = StringVar(master)
        self.current_theme_name.set("Light") # Chủ đề mặc định
        
        # Căn giữa cửa sổ
        self.master.update_idletasks()
        x = self.master.winfo_screenwidth() // 2 - self.master.winfo_width() // 2
        y = self.master.winfo_screenheight() // 2 - self.master.winfo_height() // 2
        self.master.geometry(f"+{x}+{y}")

        self.load_all_vocabulary_data()
        self.create_widgets()
        self.apply_theme(self.current_theme_name.get()) # Áp dụng chủ đề mặc định
        self.display_unit_list() 

    def load_all_vocabulary_data(self):
        """Tải toàn bộ dữ liệu từ vựng từ file JSON (bao gồm tất cả các units)."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.all_vocabulary_data = json.load(f)
                    if not isinstance(self.all_vocabulary_data, dict):
                        messagebox.showwarning("Cảnh báo", "File JSON có định dạng không hợp lệ (không phải đối tượng gốc). Khởi tạo lại.")
                        self.all_vocabulary_data = {}
            except json.JSONDecodeError:
                messagebox.showerror("Lỗi", f"Không thể đọc file JSON: {self.file_path}. Dữ liệu có thể bị hỏng.")
                self.all_vocabulary_data = {} 
            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi khi tải dữ liệu: {e}")
                self.all_vocabulary_data = {}
        else:
            messagebox.showwarning("Cảnh báo", f"Không tìm thấy file: {self.file_path}. Tạo file mới khi lưu.")
            self.all_vocabulary_data = {}

    def save_all_vocabulary_data(self):
        """Lưu toàn bộ dữ liệu từ vựng (tất cả units) vào file JSON."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.all_vocabulary_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Thành công", "Đã lưu tất cả thay đổi từ vựng!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu dữ liệu từ vựng: {e}")

    def create_widgets(self):
        """Tạo các thành phần giao diện chính."""
        # Main frames: left for unit list, right for flashcard editing
        main_pane = PanedWindow(self.master, orient=HORIZONTAL, sashrelief=RAISED, sashwidth=5) # No initial bg
        main_pane.pack(fill=BOTH, expand=True)

        # --- Left Frame: Unit List ---
        self.unit_list_frame = LabelFrame(main_pane, text="Danh Sách Unit", bd=1, relief="solid", padx=10, pady=10)
        main_pane.add(self.unit_list_frame, width=250)

        self.unit_list_canvas = Canvas(self.unit_list_frame, bd=0, highlightthickness=0)
        unit_list_scrollbar = Scrollbar(self.unit_list_frame, orient="vertical", command=self.unit_list_canvas.yview)
        self.unit_list_scrollable_frame = Frame(self.unit_list_canvas)

        self.unit_list_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.unit_list_canvas.configure(
                scrollregion=self.unit_list_canvas.bbox("all")
            )
        )
        self.unit_list_canvas.create_window((0, 0), window=self.unit_list_scrollable_frame, anchor="nw")
        self.unit_list_canvas.configure(yscrollcommand=unit_list_scrollbar.set)
        self.unit_list_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        unit_list_scrollbar.pack(side=RIGHT, fill="y")

        # Unit management buttons frame
        self.unit_buttons_frame = Frame(self.unit_list_frame, pady=5)
        self.unit_buttons_frame.pack(fill=X)
        self.add_unit_btn = Button(self.unit_buttons_frame, text="➕ Thêm Unit Mới", command=self.add_unit,
               font=("Arial", 10, "bold"), padx=5, pady=2)
        self.add_unit_btn.pack(fill=X, pady=2)
        self.delete_unit_btn = Button(self.unit_buttons_frame, text="🗑️ Xóa Unit Đang Chọn", command=self.delete_selected_unit,
               font=("Arial", 10, "bold"), padx=5, pady=2)
        self.delete_unit_btn.pack(fill=X, pady=2)


        # --- Right Frame: Flashcard Editor ---
        self.flashcard_editor_frame = LabelFrame(main_pane, text="Chỉnh Sửa Từ Vựng", bd=1, relief="solid", padx=10, pady=10)
        main_pane.add(self.flashcard_editor_frame, width=750)

        self.current_unit_label = Label(self.flashcard_editor_frame, text="Chưa chọn Unit nào.", font=("Arial", 14, "bold"), pady=5)
        self.current_unit_label.pack(pady=5)

        # Frame cho các trường nhập liệu từ mới
        self.add_flashcard_frame = LabelFrame(self.flashcard_editor_frame, text="Thêm / Sửa Thẻ Từ", bd=1, relief="solid", padx=10, pady=10)
        self.add_flashcard_frame.pack(pady=10, padx=5, fill=X)

        Label(self.add_flashcard_frame, text="Tiếng Anh:", font=("Arial", 11)).grid(row=0, column=0, sticky=W, pady=2)
        self.en_entry = Entry(self.add_flashcard_frame, width=50, font=("Arial", 11))
        self.en_entry.grid(row=0, column=1, padx=5, pady=2)

        Label(self.add_flashcard_frame, text="Tiếng Việt:", font=("Arial", 11)).grid(row=1, column=0, sticky=W, pady=2)
        self.vi_entry = Entry(self.add_flashcard_frame, width=50, font=("Arial", 11))
        self.vi_entry.grid(row=1, column=1, padx=5, pady=2)

        self.add_edit_button = Button(self.add_flashcard_frame, text="Thêm", command=self.add_or_update_flashcard,
                                       font=("Arial", 11, "bold"), padx=10, pady=3)
        self.add_edit_button.grid(row=0, column=2, rowspan=2, padx=10, pady=5)
        
        self.cancel_edit_button = Button(self.add_flashcard_frame, text="Hủy Sửa", command=self.cancel_flashcard_edit,
                                         font=("Arial", 10), padx=5, pady=2)
        self.cancel_edit_button.grid(row=2, column=1, columnspan=2, pady=5, sticky=E)
        self.cancel_edit_button.grid_remove() 

        # Frame chứa danh sách từ vựng hiện có trong unit
        self.list_flashcard_frame = LabelFrame(self.flashcard_editor_frame, text="Thẻ Từ Trong Unit", bd=1, relief="solid", padx=10, pady=10)
        self.list_flashcard_frame.pack(pady=10, padx=5, fill=BOTH, expand=True)

        self.flashcard_text = scrolledtext.ScrolledText(self.list_flashcard_frame, wrap=WORD, font=("Arial", 11), padx=5, pady=5)
        self.flashcard_text.pack(fill=BOTH, expand=True)
        self.flashcard_text.bind("<ButtonRelease-1>", lambda event: self.select_flashcard_item_by_click(event)) 

        # Footer buttons and Theme selector
        self.footer_buttons_frame = Frame(self.master, pady=10)
        self.footer_buttons_frame.pack(fill=X, side=BOTTOM)
        
        self.save_all_btn = Button(self.footer_buttons_frame, text="Lưu Tất Cả Thay Đổi", command=self.save_all_vocabulary_data,
               font=("Arial", 13, "bold"), padx=15, pady=8)
        self.save_all_btn.pack(side=LEFT, padx=10)
        
        self.delete_card_btn = Button(self.footer_buttons_frame, text="Xóa Thẻ Đã Chọn", command=self.delete_selected_flashcard,
               font=("Arial", 13, "bold"), padx=15, pady=8)
        self.delete_card_btn.pack(side=LEFT, padx=10)

        self.close_btn = Button(self.footer_buttons_frame, text="Đóng Trình Quản Lý", command=self.master.destroy,
               font=("Arial", 13, "bold"), padx=15, pady=8)
        self.close_btn.pack(side=RIGHT, padx=10)

        # Theme selector
        theme_selector_frame = Frame(self.footer_buttons_frame)
        theme_selector_frame.pack(side=RIGHT, padx=10)
        Label(theme_selector_frame, text="Chủ đề:", font=("Arial", 11)).pack(side=LEFT, padx=5)
        
        self.theme_option_menu = OptionMenu(theme_selector_frame, self.current_theme_name, *self.themes.keys(), command=self.apply_theme)
        self.theme_option_menu.config(font=("Arial", 10), width=8)
        self.theme_option_menu.pack(side=RIGHT)


        self.selected_flashcard_index = -1 

    def apply_theme(self, theme_name):
        """Áp dụng chủ đề màu sắc đã chọn cho toàn bộ giao diện."""
        theme = self.themes.get(theme_name, self.themes["Light"]) # Mặc định Light nếu không tìm thấy
        
        # Cập nhật màu cho Master window
        self.master.config(bg=theme["bg"])

        # Cập nhật màu cho LabelFrames
        self.unit_list_frame.config(bg=theme["frame_bg"], fg=theme.get("fg_label_frame", "black"))
        self.flashcard_editor_frame.config(bg=theme["label_bg"], fg=theme.get("fg_label_frame", "black"))
        self.add_flashcard_frame.config(bg=theme["frame_bg"], fg=theme.get("fg_label_frame", "black"))
        self.list_flashcard_frame.config(bg=theme["unit_list_bg"], fg=theme.get("fg_label_frame", "black"))

        # Cập nhật màu cho Labels
        self.current_unit_label.config(bg=theme["label_bg"], fg=theme.get("fg_label", "black"))
        # Cập nhật màu cho các Label trong add_flashcard_frame
        for widget in self.add_flashcard_frame.winfo_children():
            if isinstance(widget, Label):
                widget.config(bg=theme["frame_bg"], fg=theme.get("fg_label", "black"))
        # Cập nhật màu cho Label của theme selector
        for widget in self.footer_buttons_frame.winfo_children():
            if isinstance(widget, Frame): # Find the theme_selector_frame
                for sub_widget in widget.winfo_children():
                    if isinstance(sub_widget, Label):
                        sub_widget.config(bg=theme["bg"], fg=theme.get("fg_label", "black"))


        # Cập nhật màu cho Entries (chỉ nền, màu chữ giữ mặc định)
        self.en_entry.config(bg=theme.get("entry_bg", "white"), fg=theme.get("entry_fg", "black"))
        self.vi_entry.config(bg=theme.get("entry_bg", "white"), fg=theme.get("entry_fg", "black"))

        # Cập nhật màu cho Buttons
        self.add_unit_btn.config(bg=theme["button_bg"], fg=theme["button_fg"])
        self.delete_unit_btn.config(bg=theme["delete_button_bg"], fg=theme["delete_button_fg"])
        self.add_edit_button.config(bg=theme["add_button_bg"], fg=theme["add_button_fg"])
        self.cancel_edit_button.config(bg=theme["cancel_button_bg"], fg=theme["cancel_button_fg"])
        self.save_all_btn.config(bg=theme["button_bg"], fg=theme["button_fg"])
        self.delete_card_btn.config(bg=theme["delete_button_bg"], fg=theme["delete_button_fg"])
        self.close_btn.config(bg=theme["button_bg"], fg=theme["button_fg"])
        self.theme_option_menu.config(bg=theme["button_bg"], fg=theme["button_fg"])

        # Cập nhật màu cho Canvas và Frame bên trong Canvas
        self.unit_list_canvas.config(bg=theme["unit_list_bg"])
        self.unit_list_scrollable_frame.config(bg=theme["unit_list_bg"])
        
        # Cập nhật màu cho footer buttons frame (chỉ bg)
        self.footer_buttons_frame.config(bg=theme["bg"])

        # Cập nhật màu cho các nút Unit trong danh sách (cần refresh)
        self.display_unit_list() # Gọi lại để cập nhật màu cho các nút unit

        # Cập nhật màu cho ScrolledText (flashcard_text)
        self.flashcard_text.config(
            bg=theme["flashcard_text_bg"], 
            fg=theme.get("flashcard_text_default_fg", theme["flashcard_text_fg_en"]) # Default fg if not specified
        )
        self.flashcard_text.tag_config("selected", background=theme["flashcard_selected_bg"])
        self.flashcard_text.tag_config("en_display", foreground=theme["flashcard_text_fg_en"])
        self.flashcard_text.tag_config("vi_display", foreground=theme["flashcard_text_fg_vi"])
        self.flashcard_text.tag_config("index_tag", foreground=theme["flashcard_text_fg_index"])


    def display_unit_list(self):
        """Hiển thị danh sách các Unit trong khung bên trái."""
        # Clear existing buttons
        for widget in self.unit_list_scrollable_frame.winfo_children():
            widget.destroy()

        unit_names = sorted(list(self.all_vocabulary_data.keys()))
        current_theme = self.themes[self.current_theme_name.get()]

        if not unit_names:
            Label(self.unit_list_scrollable_frame, text="Chưa có Unit nào. Thêm mới!",
                  font=("Arial", 11), fg=current_theme.get("fg_label", "gray"), bg=current_theme["unit_list_bg"], wraplength=200).pack(pady=10)
            return

        for unit_name in unit_names:
            btn_bg = current_theme["unit_list_bg"]
            btn_fg = current_theme.get("fg_label", "#333")
            btn_relief = "raised"

            if unit_name == self.current_unit_name:
                btn_bg = current_theme["selected_unit_bg"]
                btn_relief = "sunken"
            
            btn = Button(self.unit_list_scrollable_frame, text=unit_name,
                         command=lambda name=unit_name: self.select_unit(name),
                         font=("Arial", 12), bg=btn_bg, fg=btn_fg, relief=btn_relief, bd=1, padx=10, pady=5, anchor="w")
            btn.pack(fill=X, pady=2, padx=5)

        self.unit_list_scrollable_frame.update_idletasks()
        self.unit_list_canvas.config(scrollregion=self.unit_list_canvas.bbox("all"))

    def select_unit(self, unit_name):
        """Chọn một unit và hiển thị flashcard của nó."""
        if self.current_unit_name == unit_name: 
            return

        self.current_unit_name = unit_name
        self.current_flashcards = self.all_vocabulary_data.get(unit_name, [])
        self.current_unit_label.config(text=f"Đang chỉnh sửa Unit: {unit_name}")
        self.display_flashcards_in_current_unit()
        self.display_unit_list() 
        self.reset_flashcard_edit_mode() 

    def add_unit(self):
        """Thêm một unit mới."""
        new_unit_name = simpledialog.askstring("Thêm Unit Mới", "Nhập tên Unit mới:", parent=self.master)
        if new_unit_name:
            new_unit_name = new_unit_name.strip()
            if not new_unit_name:
                messagebox.showwarning("Cảnh báo", "Tên Unit không được để trống.")
                return
            if new_unit_name in self.all_vocabulary_data:
                messagebox.showwarning("Cảnh báo", f"Unit '{new_unit_name}' đã tồn tại.")
                return
            
            self.all_vocabulary_data[new_unit_name] = [] 
            self.save_all_vocabulary_data()
            self.display_unit_list()
            self.select_unit(new_unit_name) 
            messagebox.showinfo("Thành công", f"Đã thêm Unit '{new_unit_name}'.")

    def delete_selected_unit(self):
        """Xóa unit đang được chọn."""
        if not self.current_unit_name:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một Unit để xóa.")
            return

        confirm = messagebox.askyesno(
            "Xác nhận Xóa Unit",
            f"Bạn có chắc chắn muốn xóa Unit '{self.current_unit_name}' và tất cả thẻ từ bên trong nó không?\n"
            "Hành động này không thể hoàn tác!"
        )
        if confirm:
            if self.current_unit_name in self.all_vocabulary_data:
                del self.all_vocabulary_data[self.current_unit_name]
                self.current_unit_name = None
                self.current_flashcards = []
                self.save_all_vocabulary_data()
                self.display_unit_list()
                self.current_unit_label.config(text="Chưa chọn Unit nào.")
                self.display_flashcards_in_current_unit() 
                messagebox.showinfo("Thành công", "Đã xóa Unit và dữ liệu liên quan.")

    def display_flashcards_in_current_unit(self):
        """Hiển thị tất cả flashcard trong unit đang chọn trong scrolledtext widget."""
        self.flashcard_text.config(state=NORMAL)
        self.flashcard_text.delete(1.0, END)

        if not self.current_flashcards:
            self.flashcard_text.insert(END, "Unit này chưa có từ vựng nào. Hãy thêm từ mới ở trên!")
            self.flashcard_text.config(state=DISABLED)
            return

        # Định nghĩa tags để highlight từ khi chọn và định dạng hiển thị
        # Màu sắc của tags sẽ được cập nhật bởi apply_theme
        current_theme = self.themes[self.current_theme_name.get()]
        self.flashcard_text.tag_config("selected", background=current_theme["flashcard_selected_bg"])
        self.flashcard_text.tag_config("en_display", foreground=current_theme["flashcard_text_fg_en"])
        self.flashcard_text.tag_config("vi_display", foreground=current_theme["flashcard_text_fg_vi"])
        self.flashcard_text.tag_config("index_tag", foreground=current_theme["flashcard_text_fg_index"])


        for i, card in enumerate(self.current_flashcards):
            start_index = self.flashcard_text.index(END) 
            self.flashcard_text.insert(END, f"{i+1}. ", "index_tag")
            self.flashcard_text.insert(END, f"EN: {card.get('en', '')}\n", "en_display")
            self.flashcard_text.insert(END, f"    VI: {card.get('vi', '')}\n\n", "vi_display")
            
            end_index = self.flashcard_text.index(END + "-1c") 
            self.flashcard_text.tag_add(f"flashcard_display_item_{i}", start_index, end_index)

        self.flashcard_text.config(state=DISABLED)
        self.selected_flashcard_index = -1 

    def select_flashcard_item_by_click(self, event):
        """Xác định flashcard được click dựa trên vị trí con trỏ và gọi select_flashcard_item."""
        if not self.current_unit_name:
            return 

        self.flashcard_text.config(state=NORMAL) 
        index_at_click = self.flashcard_text.index(f"@{event.x},{event.y}")
        line_num_clicked = int(index_at_click.split('.')[0])
        self.flashcard_text.config(state=DISABLED)

        start_line_in_text_widget = 1
        current_flashcard_idx = -1
        for i, card in enumerate(self.current_flashcards):
            if line_num_clicked >= start_line_in_text_widget and line_num_clicked < (start_line_in_text_widget + 3):
                current_flashcard_idx = i
                break
            start_line_in_text_widget += 3 
        
        if current_flashcard_idx != -1:
            self.select_flashcard_item(current_flashcard_idx)
        else:
            self.reset_flashcard_edit_mode() 

    def select_flashcard_item(self, index):
        """Chọn một flashcard theo chỉ mục, đưa dữ liệu vào ô nhập liệu để sửa."""
        self.flashcard_text.config(state=NORMAL)
        self.flashcard_text.tag_remove("selected", "1.0", END)
        
        self.flashcard_text.tag_add("selected", f"flashcard_display_item_{index}.first", f"flashcard_display_item_{index}.last")
        
        self.flashcard_text.config(state=DISABLED)
        self.selected_flashcard_index = index 

        if 0 <= index < len(self.current_flashcards):
            card = self.current_flashcards[index]
            self.en_entry.delete(0, END)
            self.en_entry.insert(0, card.get("en", ""))
            self.vi_entry.delete(0, END)
            self.vi_entry.insert(0, card.get("vi", ""))
            self.add_edit_button.config(text="Cập Nhật")
            self.cancel_edit_button.grid() 
            self.en_entry.focus_set() 

    def add_or_update_flashcard(self):
        """Thêm một flashcard mới hoặc cập nhật flashcard hiện có."""
        if not self.current_unit_name:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một Unit trước khi thêm từ.")
            return

        en_word = self.en_entry.get().strip()
        vi_word = self.vi_entry.get().strip()

        if not en_word or not vi_word:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ cả từ tiếng Anh và tiếng Việt.")
            return

        if self.selected_flashcard_index != -1 and self.selected_flashcard_index < len(self.current_flashcards):
            self.current_flashcards[self.selected_flashcard_index]["en"] = en_word
            self.current_flashcards[self.selected_flashcard_index]["vi"] = vi_word
            messagebox.showinfo("Thành công", "Đã cập nhật thẻ từ.")
        else:
            self.current_flashcards.append({"en": en_word, "vi": vi_word})
            messagebox.showinfo("Thành công", "Đã thêm thẻ từ mới.")
        
        self.all_vocabulary_data[self.current_unit_name] = self.current_flashcards
        self.save_all_vocabulary_data()

        self.reset_flashcard_edit_mode() 
        self.display_flashcards_in_current_unit() 

    def reset_flashcard_edit_mode(self):
        """Đặt lại ô nhập liệu và nút về trạng thái 'Thêm mới'."""
        self.en_entry.delete(0, END)
        self.vi_entry.delete(0, END)
        self.add_edit_button.config(text="Thêm")
        self.cancel_edit_button.grid_remove() 
        self.selected_flashcard_index = -1
        self.flashcard_text.config(state=NORMAL)
        self.flashcard_text.tag_remove("selected", "1.0", END) 
        self.flashcard_text.config(state=DISABLED)

    def cancel_flashcard_edit(self):
        """Hủy bỏ chế độ chỉnh sửa thẻ từ."""
        self.reset_flashcard_edit_mode()

    def delete_selected_flashcard(self):
        """Xóa flashcard đã chọn khỏi danh sách của unit hiện tại."""
        if not self.current_unit_name:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một Unit trước.")
            return
        
        if self.selected_flashcard_index == -1:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một thẻ từ để xóa.")
            return

        if self.selected_flashcard_index >= len(self.current_flashcards) or self.selected_flashcard_index < 0:
            messagebox.showerror("Lỗi", "Thẻ từ được chọn không hợp lệ. Vui lòng chọn lại.")
            self.reset_flashcard_edit_mode()
            return

        confirm = messagebox.askyesno(
            "Xác nhận Xóa Thẻ Từ",
            f"Bạn có chắc chắn muốn xóa thẻ từ '{self.current_flashcards[self.selected_flashcard_index]['en']}' không?"
        )
        if confirm:
            del self.current_flashcards[self.selected_flashcard_index]
            self.all_vocabulary_data[self.current_unit_name] = self.current_flashcards 
            self.save_all_vocabulary_data()
            self.reset_flashcard_edit_mode() 
            self.display_flashcards_in_current_unit() 
            messagebox.showinfo("Thành công", "Đã xóa thẻ từ.")


def run_editor_window(file_path):
    """Hàm chạy cửa sổ chỉnh sửa từ vựng."""
    root = Tk()
    app = VocabularyEditor(root, file_path)
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        vocabulary_file_path = sys.argv[1]
        run_editor_window(vocabulary_file_path)
    else:
        default_file = "flashcards_data.json"
        if not os.path.exists(default_file):
             with open(default_file, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4) 
        run_editor_window(default_file)