import pyttsx3
import time
import threading

class Voice:
    def __init__(self):
        self.last_speak_time = 0
        self.is_speaking = False

    def speak_warning(self, text):
        current_time = time.time()

        if self.is_speaking:
            return False

        if current_time - self.last_speak_time < 3:
            return False

        self.last_speak_time = current_time
        self.is_speaking = True

        def run():
            try:
                engine = pyttsx3.init()   # 🔥 tạo mới mỗi lần
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 1.0)

                engine.say(text)
                engine.runAndWait()
                engine.stop()             # 🔥 đảm bảo giải phóng
            except Exception as e:
                print("Voice error:", e)

            self.is_speaking = False

        threading.Thread(target=run, daemon=True).start()
        return True