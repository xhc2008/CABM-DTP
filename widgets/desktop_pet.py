import random
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QMouseEvent, QFont
from .input_window import InputWindow
from .message_bubble import MessageBubble
from .options_panel import OptionsPanel
import os
from dotenv import load_dotenv
from services.chat import ChatService
from services.vision import VisionService
from services.screenshot_capture import ScreenshotCapture
from config import PetConfig, BubbleConfig, SystemConfig

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
            self.response_chunk.emit('\n' + random.choice(SystemConfig.BACKUP_RESPONSES))
            print(f"AI回复处理错误: {e}")

# 创建一个工作线程类来处理VLM图片描述
class VisionProcessThread(QThread):
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

class DesktopPet(QWidget):
    """桌面宠物主窗口"""
    ai_response_ready = pyqtSignal(str)  # 添加这个信号
    
    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()
        self.input_window = None
        self.options_panel = None
        self.message_bubble = None
        self.current_text = ""
        self.full_text = ""
        self.text_index = 0
        self.is_dragging = False
        self.ai_thread = None
        self.vision_thread = None
        
        # 防抖机制
        self.right_click_timer = QTimer()
        self.right_click_timer.setSingleShot(True)
        self.right_click_timer.timeout.connect(self.handle_right_click_action)
        self.debounce_delay = 200  # 200ms防抖延迟
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
        model = os.getenv("AGENT_MODEL", "")
        # print("api_key:", api_key)
        # print("base_url:", base_url)
        # print("model:", model)
        self.chat_service = ChatService(api_key,base_url,model)
        
        # 初始化VLM服务
        try:
            self.vision_service = VisionService()
        except Exception as e:
            print(f"VLM服务初始化失败: {e}")
            self.vision_service = None
        
        # 截图捕获器
        self.screenshot_capture = None
        
        # 移除预设回复列表
        # self.responses = [...]
        
        self.init_ui()
        
        # 定时器用于检测位置变化
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.check_position_change)
        self.move_timer.start(PetConfig.POSITION_CHECK_INTERVAL)
        
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
            self.setFixedSize(PetConfig.DEFAULT_PET_WIDTH, PetConfig.DEFAULT_PET_HEIGHT)
            
        # 移动到屏幕右下角
        self.move_to_bottom_right()
        
    def load_pet_image(self):
        """加载宠物图片"""
        try:
            self.pixmap = QPixmap(PetConfig.PET_IMAGE_PATH)
            if not self.pixmap.isNull():
                self.pet_label.setPixmap(self.pixmap)
                return True
            else:
                print(f"{PetConfig.PET_IMAGE_PATH}文件存在但无法加载")
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
        
        x = screen_rect.width() - window_size.width() - PetConfig.INITIAL_POSITION_OFFSET_X
        y = screen_rect.height() - window_size.height() - PetConfig.INITIAL_POSITION_OFFSET_Y
        
        self.move(x, y)
        self.last_position = QPoint(x, y)
        
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.is_dragging = True
            event.accept()
        elif event.button() == Qt.RightButton:
            # 使用防抖机制处理右键点击
            self.right_click_timer.start(self.debounce_delay)
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
        if self.options_panel and self.options_panel.isVisible():
            self.options_panel.update_position()
        if self.message_bubble and self.message_bubble.isVisible():
            self.message_bubble.update_position()
            
    def handle_right_click_action(self):
        """处理右键点击的实际逻辑（防抖后执行）"""
        # 检查当前状态并决定相应的行为
        input_visible = self.input_window and self.input_window.isVisible()
        options_visible = self.options_panel and self.options_panel.isVisible()
        bubble_visible = self.message_bubble and self.message_bubble.isVisible()
        
        if bubble_visible:
            # 情况1: 消息气泡显示时
            if options_visible:
                # 如果选项栏也显示，只隐藏选项栏
                self.hide_options_panel()
            else:
                # 打断消息气泡，显示输入框和选项栏
                self.interrupt_message_and_show_input()
        elif input_visible and options_visible:
            # 情况2: 输入框和选项栏都显示时，隐藏它们
            self.hide_panels()
        else:
            # 情况3: 默认情况，显示输入框和选项栏
            self.show_input_window()
            
    def interrupt_message_and_show_input(self):
        """打断消息气泡并显示输入框和选项栏"""
        # 停止AI线程
        if self.ai_thread and self.ai_thread.isRunning():
            self.ai_thread.terminate()
            self.ai_thread.wait()
            self.ai_thread = None
            
        # 隐藏消息气泡
        if self.message_bubble:
            self.message_bubble.close()
            self.message_bubble = None
            
        # 显示输入框和选项栏（不隐藏气泡，因为已经手动隐藏了）
        self.show_input_window(hide_bubble=False)
        
    def hide_options_panel(self):
        """只隐藏选项栏"""
        if self.options_panel:
            self.options_panel.close()
            
    def show_input_window(self, hide_bubble=True):
        """显示输入窗口和选项栏"""
        # 根据参数决定是否隐藏消息气泡
        if hide_bubble and self.message_bubble:
            self.message_bubble.close()
            self.message_bubble = None
            
        # 创建或显示输入窗口
        if not self.input_window:
            self.input_window = InputWindow(self)
            # 确保信号连接正确
            try:
                self.input_window.message_sent.connect(self.handle_message)
                print("输入窗口信号连接成功")
            except Exception as e:
                print(f"输入窗口信号连接失败: {e}")
            
        # 创建或显示选项栏
        if not self.options_panel:
            self.options_panel = OptionsPanel(self)
            self.options_panel.exit_requested.connect(self.close_application)
            self.options_panel.hide_requested.connect(self.hide_panels)
            self.options_panel.screenshot_requested.connect(self.start_screenshot)
            
        # 更新并显示位置
        self.input_window.update_position()
        self.options_panel.update_position()
        
        self.input_window.show()
        self.options_panel.show()
        
        self.input_window.raise_()
        self.options_panel.raise_()
        self.input_window.focus_input()
        
    def handle_message(self, message, image=None):
        """处理收到的消息"""
        if message.strip() or image:
            # 立即显示消息气泡准备接收流式内容
            self.prepare_message_bubble()
            
            # 如果有图片，先用VLM处理
            if image and self.vision_service:
                self.process_image_and_message(message, image)
            else:
                # 使用QThread处理AI回复，避免界面冻结
                self.process_ai_response_stream(message)
                
    def process_image_and_message(self, message, image):
        """处理图片和消息（使用线程避免UI阻塞）"""
        try:
            # 显示"正在看图"提示
            if self.message_bubble:
                self.message_bubble.set_text("查看图片中...")
                self.message_bubble.update_position()
            
            # 如果已有VLM线程在运行，先停止它
            if self.vision_thread and self.vision_thread.isRunning():
                self.vision_thread.terminate()
                self.vision_thread.wait()
            
            # 创建并启动VLM处理线程
            self.vision_thread = VisionProcessThread(self.vision_service, image, message)
            self.vision_thread.vision_completed.connect(self.on_vision_completed)
            self.vision_thread.vision_failed.connect(self.on_vision_failed)
            self.vision_thread.start()
            
        except Exception as e:
            print(f"启动VLM线程失败: {e}")
            self.on_vision_failed(str(e), message)
    
    def on_vision_completed(self, final_message, original_message):
        """VLM处理完成回调"""
        try:
            print(f"VLM处理完成: {final_message[:100]}...")
            
            # 更新提示为"思考中..."
            if self.message_bubble:
                self.message_bubble.set_text("思考中...")
                self.message_bubble.update_position()
            
            # 发送给LLM处理
            self.process_ai_response_stream(final_message)
            
        except Exception as e:
            print(f"VLM完成回调处理失败: {e}")
            self.on_vision_failed(str(e), original_message)
        finally:
            # 清理VLM线程
            if self.vision_thread:
                self.vision_thread.quit()
                self.vision_thread.wait()
                self.vision_thread = None
    
    def on_vision_failed(self, error_message, original_message):
        """VLM处理失败回调"""
        try:
            print(f"VLM处理失败: {error_message}")
            
            # 显示错误信息
            if self.message_bubble:
                self.message_bubble.set_text(f"图片处理失败: {error_message}")
                self.message_bubble.update_position()
                # 3秒后隐藏错误消息
                QTimer.singleShot(3000, self.hide_message_bubble)
            
            # 如果有文本消息，继续处理文本
            if original_message.strip():
                QTimer.singleShot(100, lambda: self._fallback_to_text(original_message))
                
        except Exception as e:
            print(f"VLM失败回调处理失败: {e}")
        finally:
            # 清理VLM线程
            if self.vision_thread:
                self.vision_thread.quit()
                self.vision_thread.wait()
                self.vision_thread = None
                
    def _fallback_to_text(self, message):
        """回退到纯文本处理"""
        try:
            self.prepare_message_bubble()
            self.process_ai_response_stream(message)
        except Exception as e:
            print(f"文本处理也失败: {e}")
            if self.message_bubble:
                self.message_bubble.set_text("处理失败，请重试")
                QTimer.singleShot(3000, self.hide_message_bubble)
                
    def start_screenshot(self):
        """开始截图"""
        try:
            print("开始截图...")
            # 隐藏所有窗口
            self.hide_panels()
            
            # 清理之前的截图捕获器
            if self.screenshot_capture:
                try:
                    self.screenshot_capture.close()
                    self.screenshot_capture.deleteLater()
                except:
                    pass
            
            # 创建截图捕获器，设置父窗口
            self.screenshot_capture = ScreenshotCapture(self)
            self.screenshot_capture.screenshot_captured.connect(self.on_screenshot_captured)
            self.screenshot_capture.show()
            print("截图选择器已显示")
            
        except Exception as e:
            print(f"启动截图失败: {e}")
            # 如果截图失败，重新显示面板
            self.show_input_window()
        
    def on_screenshot_captured(self, pixmap):
        """截图完成回调"""
        try:
            print(f"截图完成，pixmap是否有效: {pixmap and not pixmap.isNull()}")
            
            if pixmap and not pixmap.isNull():
                print(f"截图尺寸: {pixmap.width()}x{pixmap.height()}")
                # 重新显示输入窗口和选项栏
                self.show_input_window()
                
                # 将图片设置到输入窗口
                if self.input_window:
                    self.input_window.set_image(pixmap)
                    print("图片已设置到输入窗口")
            else:
                print("截图无效，重新显示输入窗口")
                # 即使截图无效，也要重新显示输入窗口
                self.show_input_window()
            
        except Exception as e:
            print(f"处理截图时出错: {e}")
            # 出错时也要重新显示输入窗口
            self.show_input_window()
        finally:
            # 延迟清理截图捕获器，确保信号处理完成
            if self.screenshot_capture:
                def cleanup_screenshot():
                    try:
                        if self.screenshot_capture:
                            self.screenshot_capture.hide()
                            self.screenshot_capture.deleteLater()
                            self.screenshot_capture = None
                            print("截图捕获器已清理")
                    except Exception as e:
                        print(f"清理截图捕获器时出错: {e}")
                
                # 延迟500ms清理，确保所有信号处理完成
                QTimer.singleShot(500, cleanup_screenshot)
            
    def prepare_message_bubble(self):
        """准备消息气泡用于流式显示"""
        # 创建消息气泡
        if self.message_bubble:
            self.message_bubble.close()
            
        self.message_bubble = MessageBubble(self)
        self.message_bubble.set_text("思考中...")
        
        # 隐藏输入框，但保持选项栏显示
        if self.input_window:
            self.input_window.close()
            
        # 确保选项栏显示
        if not self.options_panel:
            self.options_panel = OptionsPanel(self)
            self.options_panel.exit_requested.connect(self.close_application)
            self.options_panel.hide_requested.connect(self.hide_panels)
            self.options_panel.screenshot_requested.connect(self.start_screenshot)
            
        # 更新并显示位置
        self.message_bubble.update_position()
        self.options_panel.update_position()
        
        self.message_bubble.show()
        self.options_panel.show()
        
        self.message_bubble.raise_()
        self.options_panel.raise_()

    def append_ai_response(self, text_chunk):
        """追加AI回复文本块"""
        if self.message_bubble:
            current_text = self.message_bubble.get_current_text()
            # 如果当前文本是"思考中..."或者只包含工具调用信息（以">"开头），则清空
            if current_text == "思考中..." or (current_text.strip().startswith(">") and not any(c.isalnum() and not c.isascii() for c in current_text.replace(">", "").replace("工具调用", "").replace("：", ""))):
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
            # 自动隐藏
            QTimer.singleShot(BubbleConfig.AUTO_HIDE_DELAY, self.hide_message_bubble)
        else:
            # 如果没有气泡，创建一个
            self.prepare_message_bubble()
            self.message_bubble.set_text(response)
            QTimer.singleShot(BubbleConfig.AUTO_HIDE_DELAY, self.hide_message_bubble)
            
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
        QTimer.singleShot(BubbleConfig.AUTO_HIDE_DELAY, self.hide_message_bubble)
        
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
            self.ai_response_ready.emit(random.choice('\n'+SystemConfig.BACKUP_RESPONSES))
            print(e)

    def close_application(self):
        """关闭应用程序"""
        import os
        import sys
        
        # 确保所有子窗口都关闭
        if self.input_window:
            self.input_window.close()
        if self.options_panel:
            self.options_panel.close()
        if self.message_bubble:
            self.message_bubble.close()
            
        # 停止所有定时器和线程
        if hasattr(self, 'move_timer') and self.move_timer:
            self.move_timer.stop()
        if hasattr(self, 'right_click_timer') and self.right_click_timer:
            self.right_click_timer.stop()
        if hasattr(self, 'ai_thread') and self.ai_thread and self.ai_thread.isRunning():
            self.ai_thread.terminate()
            self.ai_thread.wait()
        if hasattr(self, 'vision_thread') and self.vision_thread and self.vision_thread.isRunning():
            self.vision_thread.terminate()
            self.vision_thread.wait()
            
        # 关闭主窗口
        self.close()
        
        # 退出整个应用程序
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.quit()
        # 强制退出Python进程（确保后台进程也关闭）
        try:
            os._exit(0)
        except:
            sys.exit(0)
        
    def hide_panels(self):
        """隐藏输入框和选项栏"""
        if self.input_window:
            self.input_window.close()
        if self.options_panel:
            self.options_panel.close()

    def closeEvent(self, event):
        """关闭事件"""
        # 停止定时器
        if hasattr(self, 'move_timer') and self.move_timer:
            self.move_timer.stop()
        if hasattr(self, 'right_click_timer') and self.right_click_timer:
            self.right_click_timer.stop()
        if hasattr(self, 'timer') and hasattr(self, 'timer') and self.timer:
            self.timer.stop()
        
        # 停止AI线程和VLM线程
        if hasattr(self, 'ai_thread') and self.ai_thread and self.ai_thread.isRunning():
            self.ai_thread.terminate()
            self.ai_thread.wait()
        if hasattr(self, 'vision_thread') and self.vision_thread and self.vision_thread.isRunning():
            self.vision_thread.terminate()
            self.vision_thread.wait()
        
        # 关闭子窗口
        if self.input_window:
            self.input_window.close()
        if self.options_panel:
            self.options_panel.close()
        if self.message_bubble:
            self.message_bubble.close()
            
        # 确保应用程序完全退出
        from PyQt5.QtWidgets import QApplication
        QApplication.instance().quit()
        
        event.accept()