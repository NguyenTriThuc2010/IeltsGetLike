# pronunciation_practice.py - Giao diện luyện tập phát âm

from tkinter import *
from tkinter import messagebox, scrolledtext
import json
import os
import sys
import requests 

# --- Cấu hình Oxford Dictionaries API ---
# Thay thế bằng APP ID và APP KEY THẬT của bạn từ Oxford Dictionaries Developer
APP_ID = "bb0058ed" # <-- ĐẢM BẢO BẠN THAY THẾ ID THẬT CỦA MÌNH VÀO ĐÂY
APP_KEY = "48a80dc6a864ebfcbb4c3c4ae447ec4c" # APP KEY của bạn
LANGUAGE = "en-us" 
BASE_URL = "https://od-api.oxforddictionaries.com/api/v2/entries/"
# ------------------------------------------

class PronunciationPractice:
    def __init__(self, master, file_path):
        self.master = master
        self.master.title(f"Luyện Tập Phát Âm - {os.path.basename(file_path)}")
        self.master.geometry("800x600") 
        self.master.configure(bg="#f0f0f0") 

        self.file_path = file_path
        self.all_vocabulary_data = {} 
        self.current_unit_name = None 
        self.current_flashcards = [] 
        self.current_card_index = 0 

        self.master.update_idletasks()
        x = self.master.winfo_screenwidth() // 2 - self.master.winfo_width() // 2
        y = self.master.winfo_screenheight() // 2 - self.master.winfo_height() // 2
        self.master.geometry(f"+{x}+{y}")

        self.load_all_vocabulary_data()
        self.create_widgets()
        self.display_unit_list() 

    def load_all_vocabulary_data(self):
        """Tải toàn bộ dữ liệu từ vựng từ file JSON."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.all_vocabulary_data = json.load(f)
                    if not isinstance(self.all_vocabulary_data, dict):
                        messagebox.showwarning("Cảnh báo", "File JSON có định dạng không hợp lệ. Khởi tạo lại.")
                        self.all_vocabulary_data = {}
            except json.JSONDecodeError:
                messagebox.showerror("Lỗi", f"Không thể đọc file JSON: {self.file_path}. Dữ liệu có thể bị hỏng.")
                self.all_vocabulary_data = {} 
            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi khi tải dữ liệu: {e}")
                self.all_vocabulary_data = {}
        else:
            messagebox.showwarning("Cảnh báo", f"Không tìm thấy file: {self.file_path}. Vui lòng kiểm tra lại đường dẫn.")
            self.all_vocabulary_data = {}

    def save_all_vocabulary_data(self):
        """Lưu toàn bộ dữ liệu từ vựng (tất cả units) vào file JSON."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.all_vocabulary_data, f, ensure_ascii=False, indent=4)
            # messagebox.showinfo("Thành công", "Đã lưu tất cả thay đổi từ vựng!") # Không cần hiển thị popup khi tự động cập nhật
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu dữ liệu từ vựng: {e}")

    def create_widgets(self):
        """Tạo các thành phần giao diện chính."""
        main_pane = PanedWindow(self.master, orient=HORIZONTAL, sashrelief=RAISED, sashwidth=5, bg="#d0d0d0")
        main_pane.pack(fill=BOTH, expand=True)

        # --- Left Frame: Unit List ---
        self.unit_list_frame = LabelFrame(main_pane, text="Chọn Unit", bg="#e0e0e0", bd=1, relief="solid", padx=10, pady=10)
        main_pane.add(self.unit_list_frame, width=250)

        self.unit_list_canvas = Canvas(self.unit_list_frame, bg="white", bd=0, highlightthickness=0)
        unit_list_scrollbar = Scrollbar(self.unit_list_frame, orient="vertical", command=self.unit_list_canvas.yview)
        self.unit_list_scrollable_frame = Frame(self.unit_list_canvas, bg="white")

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

        # --- Right Frame: Practice Area ---
        self.practice_area_frame = LabelFrame(main_pane, text="Luyện Tập", bg="#f8f8f8", bd=1, relief="solid", padx=10, pady=10)
        main_pane.add(self.practice_area_frame, width=550)

        self.current_unit_label = Label(self.practice_area_frame, text="Chưa chọn Unit nào.", font=("Arial", 14, "bold"), bg="#f8f8f8", pady=10)
        self.current_unit_label.pack(pady=5)

        # Word display area
        self.word_display_frame = Frame(self.practice_area_frame, bg="white", bd=1, relief="solid", padx=20, pady=20)
        self.word_display_frame.pack(pady=20, fill=BOTH, expand=True)

        self.english_word_label = Label(self.word_display_frame, text="Từ tiếng Anh", font=("Arial", 36, "bold"), bg="white", wraplength=400)
        self.english_word_label.pack(pady=(10, 5))

        self.pronunciation_label = Label(self.word_display_frame, text="[Phiên âm]", font=("Arial", 24, "italic"), bg="white", fg="#555555")
        self.pronunciation_label.pack(pady=(5, 10))

        self.vietnamese_word_label = Label(self.word_display_frame, text="Nghĩa tiếng Việt", font=("Arial", 18), bg="white", fg="#777777", wraplength=400)
        self.vietnamese_word_label.pack(pady=(5, 10))

        # Navigation buttons
        nav_buttons_frame = Frame(self.practice_area_frame, bg="#f8f8f8", pady=10)
        nav_buttons_frame.pack(pady=10)

        self.prev_button = Button(nav_buttons_frame, text="⬅️ Từ Trước", command=self.show_previous_card,
                                  font=("Arial", 12, "bold"), bg="#007bff", fg="white", padx=15, pady=8)
        self.prev_button.pack(side=LEFT, padx=10)

        self.next_button = Button(nav_buttons_frame, text="Từ Kế Tiếp ➡️", command=self.show_next_card,
                                  font=("Arial", 12, "bold"), bg="#007bff", fg="white", padx=15, pady=8)
        self.next_button.pack(side=RIGHT, padx=10)

        # Initial state for buttons
        self.prev_button.config(state=DISABLED)
        self.next_button.config(state=DISABLED)
        self.clear_card_display()


    def display_unit_list(self):
        """Hiển thị danh sách các Unit trong khung bên trái."""
        for widget in self.unit_list_scrollable_frame.winfo_children():
            widget.destroy()

        unit_names = sorted(list(self.all_vocabulary_data.keys()))

        if not unit_names:
            Label(self.unit_list_scrollable_frame, text="Chưa có Unit nào để luyện tập.",
                  font=("Arial", 11), fg="gray", bg="white", wraplength=200).pack(pady=10)
            return

        for unit_name in unit_names:
            btn = Button(self.unit_list_scrollable_frame, text=unit_name,
                         command=lambda name=unit_name: self.select_unit(name),
                         font=("Arial", 12), bg="#ffffff", fg="#333", relief="raised", bd=1, padx=10, pady=5, anchor="w")
            btn.pack(fill=X, pady=2, padx=5)

            # Highlight selected unit
            if unit_name == self.current_unit_name:
                btn.config(bg="#aaffaa", relief="sunken") 

        self.unit_list_scrollable_frame.update_idletasks()
        self.unit_list_canvas.config(scrollregion=self.unit_list_canvas.bbox("all"))

    def select_unit(self, unit_name):
        """Chọn một unit và tải các flashcard của nó."""
        if self.current_unit_name == unit_name: 
            return

        self.current_unit_name = unit_name
        # Lọc bỏ các flashcard không có từ tiếng Anh hoặc tiếng Việt
        self.current_flashcards = [
            card for card in self.all_vocabulary_data.get(unit_name, []) 
            if card.get('en') and card.get('vi')
        ]
        self.current_card_index = 0 # Đặt lại chỉ mục về 0 khi chọn unit mới

        self.current_unit_label.config(text=f"Unit: {unit_name} ({len(self.current_flashcards)} từ)")
        self.display_unit_list() # Cập nhật màu sắc nút unit đã chọn

        if self.current_flashcards:
            self.show_current_card()
            self.next_button.config(state=NORMAL)
            self.prev_button.config(state=DISABLED) # Disable prev for the first card
        else:
            self.clear_card_display()
            self.next_button.config(state=DISABLED)
            self.prev_button.config(state=DISABLED)
            messagebox.showinfo("Thông báo", f"Unit '{unit_name}' không có từ vựng hợp lệ để luyện tập.")

    def clear_card_display(self):
        """Xóa nội dung hiển thị của thẻ từ."""
        self.english_word_label.config(text="...")
        self.pronunciation_label.config(text="Chưa có từ để hiển thị.")
        self.vietnamese_word_label.config(text="...")

    def get_oxford_pronunciation(self, word):
        """
        Lấy phiên âm IPA từ Oxford Dictionaries API cho một từ.
        Trả về phiên âm dưới dạng chuỗi hoặc thông báo lỗi.
        """
        # Kiểm tra APP_ID và APP_KEY trước khi thực hiện request
        if not APP_ID or APP_ID == "YOUR_OXFORD_APP_ID" or not APP_KEY:
            return "[Lỗi: Cần cấu hình Oxford API ID/Key chính xác]"

        url = f"{BASE_URL}{word.lower()}" # Sử dụng BASE_URL đã định nghĩa
        headers = {
            "app_id": APP_ID, # Sử dụng biến APP_ID toàn cục
            "app_key": APP_KEY # Sử dụng biến APP_KEY toàn cục
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status() # Báo lỗi nếu phản hồi không thành công (4xx hoặc 5xx)
            data = response.json()
            
            # Phân tích cú pháp JSON để lấy phiên âm
            # Cấu trúc JSON của Oxford API có thể phức tạp.
            # Chúng ta sẽ tìm phiên âm cho tiếng Anh và lấy cái đầu tiên tìm thấy.
            if 'results' in data and data['results']:
                for result in data['results']:
                    if 'lexicalEntries' in result:
                        for lexical_entry in result['lexicalEntries']:
                            if 'pronunciations' in lexical_entry:
                                for pronunciation in lexical_entry['pronunciations']:
                                    # Tìm phoneticSpelling cho ngôn ngữ mong muốn hoặc bất kỳ nếu không tìm thấy
                                    # Thường thì có cả "dialects" (ví dụ: en-us, en-gb) bạn có thể lọc
                                    if 'phoneticSpelling' in pronunciation:
                                        return pronunciation['phoneticSpelling']
            return "[Không tìm thấy phiên âm]"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return "[Không tìm thấy từ trong từ điển]"
            elif e.response.status_code == 403:
                return "[Lỗi API 403: Quyền truy cập bị từ chối. Kiểm tra lại ID/Key]"
            elif e.response.status_code == 429: # Too Many Requests
                return "[Lỗi API 429: Đã vượt quá giới hạn yêu cầu API]"
            else:
                return f"[Lỗi HTTP: {e.response.status_code}]"
        except requests.exceptions.ConnectionError:
            return "[Lỗi kết nối mạng]"
        except Exception as e:
            return f"[Lỗi lấy phiên âm: {e}]"

    def show_current_card(self):
        """Hiển thị thẻ từ hiện tại dựa trên self.current_card_index."""
        if not self.current_flashcards:
            self.clear_card_display()
            self.next_button.config(state=DISABLED)
            self.prev_button.config(state=DISABLED)
            return

        if self.current_card_index < 0:
            self.current_card_index = 0
        elif self.current_card_index >= len(self.current_flashcards):
            self.current_card_index = len(self.current_flashcards) - 1

        card = self.current_flashcards[self.current_card_index]
        english_word = card.get('en', 'N/A')
        vietnamese_word = card.get('vi', 'N/A')
        
        # Lấy phiên âm
        pronunciation_text = card.get('pronunciation', '') 
        
        # Nếu phiên âm chưa có, rỗng, hoặc là một thông báo lỗi cũ, thì gọi API để lấy
        if not pronunciation_text or pronunciation_text.strip() == "" or \
           pronunciation_text.startswith("[Lỗi") or \
           pronunciation_text.startswith("[Không tìm thấy từ") or \
           pronunciation_text == "[Không có phiên âm]": # Bao gồm cả thông báo cũ
            
            self.pronunciation_label.config(text="Đang tải phiên âm...") 
            self.master.update_idletasks() 
            
            fetched_pronunciation = self.get_oxford_pronunciation(english_word)
            
            # Cập nhật phiên âm vào dữ liệu flashcard và lưu lại
            # Chỉ cập nhật nếu API trả về phiên âm hợp lệ (không phải lỗi từ API, lỗi mạng, không tìm thấy từ)
            if not fetched_pronunciation.startswith("[Lỗi") and \
               not fetched_pronunciation.startswith("[Không tìm thấy"):
                card['pronunciation'] = fetched_pronunciation
                # Cập nhật dữ liệu tổng thể và lưu
                # Đảm bảo self.current_unit_name và self.current_card_index còn hợp lệ
                if self.current_unit_name in self.all_vocabulary_data and \
                   self.current_card_index < len(self.all_vocabulary_data[self.current_unit_name]):
                    self.all_vocabulary_data[self.current_unit_name][self.current_card_index]['pronunciation'] = fetched_pronunciation
                    self.save_all_vocabulary_data() 
            else:
                card['pronunciation'] = fetched_pronunciation 
            
            pronunciation_text = card['pronunciation'] 
            
        self.english_word_label.config(text=english_word)
        self.pronunciation_label.config(text=pronunciation_text)
        self.vietnamese_word_label.config(text=vietnamese_word)

        # Cập nhật trạng thái nút điều hướng
        if self.current_card_index == 0:
            self.prev_button.config(state=DISABLED)
        else:
            self.prev_button.config(state=NORMAL)

        if self.current_card_index == len(self.current_flashcards) - 1:
            self.next_button.config(state=DISABLED)
        else:
            self.next_button.config(state=NORMAL)

    def show_next_card(self):
        """Chuyển sang thẻ từ kế tiếp."""
        if self.current_card_index < len(self.current_flashcards) - 1:
            self.current_card_index += 1
            self.show_current_card()

    def show_previous_card(self):
        """Quay lại thẻ từ trước đó."""
        if self.current_card_index > 0:
            self.current_card_index -= 1
            self.show_current_card()


def run_pronunciation_window(file_path):
    """Hàm chạy cửa sổ luyện tập phát âm."""
    root = Tk()
    app = PronunciationPractice(root, file_path)
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        vocabulary_file_path = sys.argv[1]
        run_pronunciation_window(vocabulary_file_path)
    else:
        default_file = "flashcards_data.json"
        if not os.path.exists(default_file):
             with open(default_file, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4) 
        run_pronunciation_window(default_file)