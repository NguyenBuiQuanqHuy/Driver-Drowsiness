import pyttsx3


# =========================================
# VOICE MANAGER
# =========================================
# File này quản lý:
# - voice language
# - voice speed
# - enable/disable voice
# =========================================
class VoiceManager:

    def __init__(self):

        # =================================
        # Khởi tạo engine
        # =================================
        self.engine = pyttsx3.init()

        # =================================
        # Lấy danh sách voice
        # =================================
        self.voices = self.engine.getProperty("voices")

        # =================================
        # Mặc định
        # =================================
        self.current_voice = None
        self.voice_speed = 150
        self.enabled = True

    # =====================================
    # GET AVAILABLE VOICES
    # =====================================
    # Trả về danh sách voice
    #
    # Ví dụ:
    # [
    #   "Microsoft David",
    #   "Microsoft Zira"
    # ]
    # =====================================
    def get_voice_names(self):

        names = []

        for voice in self.voices:

            names.append(voice.name)

        return names

    # =====================================
    # SET VOICE
    # =====================================
    # Chọn voice theo tên
    # =====================================
    def set_voice(self, voice_name):

        for voice in self.voices:

            if voice.name == voice_name:

                self.engine.setProperty("voice", voice.id)

                self.current_voice = voice_name

                break

    # =====================================
    # SET SPEED
    # =====================================
    def set_speed(self, speed):

        self.voice_speed = speed

        self.engine.setProperty("rate", speed)

    # =====================================
    # ENABLE / DISABLE
    # =====================================
    def set_enabled(self, enabled):

        self.enabled = enabled

    # =====================================
    # SPEAK
    # =====================================
    def speak(self, text):

        # =================================
        # Nếu voice đang tắt
        # =================================
        if not self.enabled:
            return

        try:

            self.engine.say(text)

            self.engine.runAndWait()

        except Exception as e:

            print("Voice error:", e)