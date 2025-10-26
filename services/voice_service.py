import speech_recognition as sr
import threading
import queue
import time

class VoiceService:
    """语音处理服务"""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.listening_thread = None

        # 调整麦克风环境噪音
        print("正在校准麦克风环境噪音...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        print("麦克风校准完成")

    def start_listening(self, callback=None):
        """开始监听语音输入"""
        if self.is_listening:
            print("已经在监听中")
            return

        self.is_listening = True
        self.listening_thread = threading.Thread(
            target=self._listening_worker,
            args=(callback,)
        )
        self.listening_thread.daemon = True
        self.listening_thread.start()
        print("语音监听已启动")

    def stop_listening(self):
        """停止监听语音输入"""
        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join(timeout=1)
        print("语音监听已停止")

    def _listening_worker(self, callback=None):
        """语音监听工作线程"""
        while self.is_listening:
            try:
                # 监听语音输入
                with self.microphone as source:
                    print("请说话...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

                # 识别语音
                print("正在识别语音...")
                text = self.recognizer.recognize_google(audio, language='zh-CN')

                if text:
                    print(f"识别结果: {text}")
                    if callback:
                        callback(text)

            except sr.WaitTimeoutError:
                # 超时，继续监听
                continue
            except sr.UnknownValueError:
                print("无法识别语音")
            except sr.RequestError as e:
                print(f"语音识别服务错误: {e}")
            except Exception as e:
                print(f"语音处理异常: {e}")

            # 短暂暂停避免过度占用CPU
            time.sleep(0.1)

    def record_audio(self, duration: int = 5) -> str:
        """
        录制指定时长的音频并转换为文本

        Args:
            duration: 录制时长（秒）

        Returns:
            str: 识别出的文本
        """
        try:
            with self.microphone as source:
                print(f"请说话，录制{duration}秒...")
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)

            print("正在识别语音...")
            text = self.recognizer.recognize_google(audio, language='zh-CN')
            print(f"识别结果: {text}")
            return text

        except sr.WaitTimeoutError:
            print("录音超时")
            return ""
        except sr.UnknownValueError:
            print("无法识别语音")
            return ""
        except sr.RequestError as e:
            print(f"语音识别服务错误: {e}")
            return ""

    def get_available_microphones(self) -> list:
        """获取可用的麦克风列表"""
        return sr.Microphone.list_microphone_names()

    def set_microphone(self, device_index: int):
        """设置使用的麦克风设备"""
        try:
            self.microphone = sr.Microphone(device_index=device_index)
            # 重新校准环境噪音
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            print(f"已切换到麦克风设备: {device_index}")
        except Exception as e:
            print(f"切换麦克风失败: {e}")

# 语音服务单例
voice_service = VoiceService()