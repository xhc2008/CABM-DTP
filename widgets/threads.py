"""
线程处理模块
处理AI响应和视觉处理的异步任务
"""
import random
from PyQt5.QtCore import QThread, pyqtSignal
from config import SystemConfig


class AIResponseThread(QThread):
    """AI响应处理线程"""
    response_chunk = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, chat_service, message):
        super().__init__()
        self.chat_service = chat_service
        self.message = message
        
    def run(self):
        try:
            for chunk in self.chat_service.process_message_stream(self.message):
                self.response_chunk.emit(chunk)
            self.finished.emit()
        except Exception as e:
            self.response_chunk.emit('\n' + random.choice(SystemConfig.BACKUP_RESPONSES))
            print(f"AI回复处理错误: {e}")


class VisionProcessThread(QThread):
    """VLM图片描述处理线程"""
    vision_completed = pyqtSignal(str, str)  # 发射(final_message, original_message)
    vision_failed = pyqtSignal(str, str)     # 发射(error_message, original_message)
    
    def __init__(self, vision_service, pixmap, message):
        super().__init__()
        self.vision_service = vision_service
        self.pixmap = pixmap
        self.message = message
        
    def run(self):
        try:
            # 使用VLM描述图片
            image_description = self.vision_service.describe_image(self.pixmap, self.message)
            
            # 构建最终消息格式
            if self.message.strip():
                final_message = f"[图片：{image_description}]{{{self.message}}}"
            else:
                final_message = f"[图片：{image_description}]"
            
            self.vision_completed.emit(final_message, self.message)
            
        except Exception as e:
            print(f"VLM线程处理失败: {e}")
            import traceback
            traceback.print_exc()
            self.vision_failed.emit(str(e), self.message)