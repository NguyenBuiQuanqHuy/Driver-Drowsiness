import pyttsx3
import time
import threading

class Voice:
    def __init__(self):
        self.last_speak_time = 0
        self.is_speaking = False
        self.volume = 1.0

    # =====================================
    # SET VOLUME
    # =====================================
    def set_volume(self, value):

        self.volume = value

    def speak_warning(self, text):
        current_time = time.time()

        # Nếu đang nói, hoặc chưa đủ 5 giây giãn cách -> Bỏ qua không nói đè
        if self.is_speaking:
            return False

        if current_time - self.last_speak_time < 5:
            return False

        self.last_speak_time = current_time
        self.is_speaking = True

        def run():
            try:
                engine = pyttsx3.init()   # Khởi tạo cục bộ trong luồng phụ để tránh lỗi COM ẩn
                engine.setProperty('rate', 160) # Tốc độ nói (vừa phải)
                engine.setProperty(
                    'volume',
                    self.volume
                )

                engine.say(text)
                engine.runAndWait()
                engine.stop()             
            except Exception as e:
                print("Voice error:", e)
            finally:
                # 🔥 ĐƯỢC ĐƯA VÀO TRONG ĐÂY: Chỉ khi luồng phụ nói xong hoàn toàn 
                # hoặc gặp lỗi, trạng thái mới chuyển về False
                self.is_speaking = False

        # Chạy luồng phụ ngầm
        threading.Thread(target=run, daemon=True).start()
        return True