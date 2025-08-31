import random
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QMouseEvent, QFont
from .input_window import InputWindow
from .message_bubble import MessageBubble
import os
from dotenv import load_dotenv
from services.chat import ChatService
# 在文件顶部添加QThread导入
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal, QThread

# 创建一个工作线程类来处理AI响应
class AIResponseThread(QThread):
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
            import random
            backup_responses = [
                "抱歉，我现在遇到了一点问题，稍后再试吧~",
                "哎呀，网络好像不太稳定，等会儿再聊吧！",
                "我暂时无法处理这个请求，请稍后再试~"
            ]
            self.response_chunk.emit(random.choice(backup_responses))
            print(f"AI回复处理错误: {e}")

class DesktopPet(QWidget):
    """桌面宠物主窗口"""
    ai_response_ready = pyqtSignal(str)  # 添加这个信号
    
    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()
        self.input_window = None
        self.message_bubble = None
        self.current_text = ""
        self.full_text = ""
        self.text_index = 0
        self.is_dragging = False
        self.ai_thread = None
        current_script_dir = os.path.dirname(os.path.abspath(__file__))

        # 向上回退一级，找到项目根目录（即 .env 所在的目录）
        project_root_dir = os.path.dirname(current_script_dir)

        # 构建 .env 文件的完整路径
        env_file_path = os.path.join(project_root_dir, '.env')

        # 加载指定路径的 .env 文件
        load_dotenv(dotenv_path=env_file_path)
        # 初始化AI聊天服务
        api_key = os.getenv("API_KEY", "your_api_key_here")  # 从环境变量获取API密钥
        base_url = os.getenv("BASE_URL", "https://api.example.com")
        model = os.getenv("MODEL", "")
        # print("api_key:", api_key)
        # print("base_url:", base_url)
        # print("model:", model)
        self.chat_service = ChatService(api_key,base_url,model)
        
        # 移除预设回复列表
        # self.responses = [...]
        
        self.init_ui()
        
        # 定时器用于检测位置变化
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.check_position_change)
        self.move_timer.start(50)  # 50ms检查一次
        
        self.last_position = self.pos()
        self.ai_response_ready.connect(self.append_ai_response)
        
    def init_ui(self):
        """初始化界面"""
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建宠物标签
        self.pet_label = QLabel()
        self.pet_label.setAlignment(Qt.AlignCenter)
        
        # 尝试加载宠物图片
        self.load_pet_image()
            
        layout.addWidget(self.pet_label)
        
        # 调整窗口大小
        if hasattr(self, 'pixmap') and not self.pixmap.isNull():
            size = self.pixmap.size()
            self.setFixedSize(size)
        else:
            self.setFixedSize(100, 100)
            
        # 移动到屏幕右下角
        self.move_to_bottom_right()
        
    def load_pet_image(self):
        """加载宠物图片"""
        try:
            self.pixmap = QPixmap("pet.png")
            if not self.pixmap.isNull():
                self.pet_label.setPixmap(self.pixmap)
                return True
            else:
                print("pet.png文件存在但无法加载")
                return False
        except Exception as e:
            print(f"加载图片失败: {e}")
            return False
        
    def move_to_bottom_right(self):
        """将窗口移动到屏幕右下角"""
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry()
        window_size = self.size()
        
        x = screen_rect.width() - window_size.width() - 50
        y = screen_rect.height() - window_size.height() - 50
        
        self.move(x, y)
        self.last_position = QPoint(x, y)
        
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.is_dragging = True
            event.accept()
        elif event.button() == Qt.RightButton:
            self.show_input_window()
            event.accept()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件（拖拽）"""
        if event.buttons() == Qt.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPos() - self.drag_position)
            # 实时更新跟随窗口位置
            self.update_following_windows()
            event.accept()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.last_position = self.pos()
            event.accept()
            
    def check_position_change(self):
        """检查位置变化并更新跟随窗口"""
        if not self.is_dragging:
            current_pos = self.pos()
            if current_pos != self.last_position:
                self.update_following_windows()
                self.last_position = current_pos
                
    def update_following_windows(self):
        """更新所有跟随窗口的位置"""
        if self.input_window and self.input_window.isVisible():
            self.input_window.update_position()
        if self.message_bubble and self.message_bubble.isVisible():
            self.message_bubble.update_position()
            
    def show_input_window(self):
        """显示输入窗口"""
        # 隐藏之前的消息气泡
        if self.message_bubble:
            self.message_bubble.close()
            self.message_bubble = None
            
        # 创建或显示输入窗口
        if not self.input_window:
            self.input_window = InputWindow(self)
            self.input_window.message_sent.connect(self.handle_message)
            
        # 更新并显示位置
        self.input_window.update_position()
        self.input_window.show()
        self.input_window.raise_()
        self.input_window.focus_input()
        
    def handle_message(self, message):
        """处理收到的消息"""
        if message.strip():
            # 立即显示消息气泡准备接收流式内容
            self.prepare_message_bubble()
            
            # 使用QThread处理AI回复，避免界面冻结
            self.process_ai_response_stream(message)
            
    def prepare_message_bubble(self):
        """准备消息气泡用于流式显示"""
        # 创建消息气泡
        if self.message_bubble:
            self.message_bubble.close()
            
        self.message_bubble = MessageBubble(self)
        self.message_bubble.set_text("思考中...")
        
        # 更新并显示位置
        self.message_bubble.update_position()
        self.message_bubble.show()
        self.message_bubble.raise_()

    def append_ai_response(self, text_chunk):
        """追加AI回复文本块"""
        if self.message_bubble:
            current_text = self.message_bubble.get_current_text()
            if current_text == "思考中...":
                current_text = ""
            new_text = current_text + text_chunk
            print(text_chunk,end="")
            self.message_bubble.set_text(new_text)
            self.message_bubble.update_position()

    def show_ai_response(self, response):
        """显示AI回复（保持兼容性）"""
        if self.message_bubble:
            self.message_bubble.set_text(response)
            self.message_bubble.update_position()
            # 3秒后自动隐藏
            QTimer.singleShot(3000, self.hide_message_bubble)
        else:
            # 如果没有气泡，创建一个
            self.prepare_message_bubble()
            self.message_bubble.set_text(response)
            QTimer.singleShot(3000, self.hide_message_bubble)
            
    def hide_message_bubble(self):
        """隐藏消息气泡"""
        if self.message_bubble:
            self.message_bubble.close()
            self.message_bubble = None
    
    def process_ai_response_stream(self, message):
        """处理AI流式回复（使用QThread）"""
        # 如果已有线程在运行，先停止它
        if self.ai_thread and self.ai_thread.isRunning():
            self.ai_thread.terminate()
            self.ai_thread.wait()
        
        # 创建并启动新线程
        self.ai_thread = AIResponseThread(self.chat_service, message)
        self.ai_thread.response_chunk.connect(self.append_ai_response)
        self.ai_thread.finished.connect(self.on_ai_response_finished)
        self.ai_thread.start()

    def on_ai_response_finished(self):
        """AI响应完成后的处理"""
        # 流式响应完成后，设置自动隐藏定时器
        # 注意：这个定时器必须在主线程中创建
        QTimer.singleShot(3000, self.hide_message_bubble)
        
        # 清理线程
        if self.ai_thread:
            self.ai_thread.quit()
            self.ai_thread.wait()
            self.ai_thread = None

    def process_ai_response(self, message):
        """处理AI回复（非流式，保持兼容性）"""
        try:
            response = self.chat_service.process_message(message)
            # 使用信号机制将结果传递回主线程
            self.ai_response_ready.emit(response)
        except Exception as e:
            # 出错时使用备用回复
            import random
            backup_responses = [
                "抱歉，我现在遇到了一点问题，稍后再试吧~",
                "哎呀，网络好像不太稳定，等会儿再聊吧！",
                "我暂时无法处理这个请求，请稍后再试~"
            ]
            self.ai_response_ready.emit(random.choice(backup_responses))
            print(e)

    def closeEvent(self, event):
        """关闭事件"""
        # 停止定时器
        if hasattr(self, 'move_timer'):
            self.move_timer.stop()
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
        
        # 停止AI线程
        if hasattr(self, 'ai_thread') and self.ai_thread and self.ai_thread.isRunning():
            self.ai_thread.terminate()
            self.ai_thread.wait()
        
        # 关闭子窗口
        if self.input_window:
            self.input_window.close()
        if self.message_bubble:
            self.message_bubble.close()
        event.accept()