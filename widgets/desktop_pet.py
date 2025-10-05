"""
桌面宠物主窗口 - 专注于核心功能和UI管理
"""
import random
import os
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QDesktopWidget
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap
from dotenv import load_dotenv

# 导入重构后的模块
from .threads import AIResponseThread, VisionProcessThread
from .system_tray import SystemTrayManager
from .event_handler import EventHandler
from .pet_decorations import PetDecorationManager

# 导入其他组件
from .input_window import InputWindow
from .message_bubble import MessageBubble
from .options_panel import OptionsPanel

# 导入服务
from services.chat import ChatService
from services.vision import VisionService
from services.screenshot_capture import ScreenshotCapture

# 导入配置
from config import PetConfig, BubbleConfig, SystemConfig



class DesktopPet(QWidget):
    """桌面宠物主窗口"""
    ai_response_ready = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # 初始化组件变量
        self.input_window = None
        self.options_panel = None
        self.message_bubble = None
        self.ai_thread = None
        self.vision_thread = None
        self.screenshot_capture = None
        
        # 初始化装饰管理器
        self.decoration_manager = PetDecorationManager(self)
        
        # 初始化管理器
        self.system_tray = SystemTrayManager(self)
        self.event_handler = EventHandler(self)
        
        # 连接信号
        self._connect_signals()
        
        # 加载环境变量
        self._load_environment()
        
        # 初始化服务
        self._init_services()
        
        # 初始化UI
        self.init_ui()
        
        # 连接AI响应信号
        self.ai_response_ready.connect(self.append_ai_response)
        
        # 根据配置决定是否隐藏后台窗口
        self._apply_console_startup_config()
        
    def _connect_signals(self):
        """连接各种信号"""
        # 系统托盘信号
        self.system_tray.show_requested.connect(self.show_from_tray)
        self.system_tray.hide_requested.connect(self.hide_to_tray)
        self.system_tray.toggle_console_requested.connect(self.toggle_console_window)
        self.system_tray.exit_requested.connect(self.close_application)
        
        # 事件处理信号
        self.event_handler.right_click_detected.connect(self._handle_right_click_action)
        self.event_handler.position_changed.connect(self.update_following_windows)
        
    def _load_environment(self):
        """加载环境变量"""
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root_dir = os.path.dirname(current_script_dir)
        env_file_path = os.path.join(project_root_dir, '.env')
        load_dotenv(dotenv_path=env_file_path)
        
    def _init_services(self):
        """初始化各种服务"""
        # 初始化AI聊天服务
        api_key = os.getenv("API_KEY")
        base_url = os.getenv("BASE_URL")
        model = os.getenv("AGENT_MODEL")
        self.chat_service = ChatService(api_key, base_url, model)
        
        # 初始化VLM服务
        try:
            self.vision_service = VisionService()
        except Exception as e:
            print(f"VLM服务初始化失败: {e}")
            self.vision_service = None
            
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
        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry()
        window_size = self.size()
        
        x = screen_rect.width() - window_size.width() - PetConfig.INITIAL_POSITION_OFFSET_X
        y = screen_rect.height() - window_size.height() - PetConfig.INITIAL_POSITION_OFFSET_Y
        
        self.move(x, y)
        self.event_handler.update_last_position()
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        self.event_handler.handle_mouse_press(event)
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件（拖拽）"""
        self.event_handler.handle_mouse_move(event)
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.event_handler.handle_mouse_release(event)
                
    def update_following_windows(self):
        """更新所有跟随窗口的位置"""
        if self.input_window and self.input_window.isVisible():
            self.input_window.update_position()
        if self.options_panel and self.options_panel.isVisible():
            self.options_panel.update_position()
        if self.message_bubble and self.message_bubble.isVisible():
            self.message_bubble.update_position()
        # 更新装饰位置
        self.decoration_manager.update_loading_spinner_position()
            
    def _handle_right_click_action(self):
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
        # 停止思考定时器和加载圈
        self.decoration_manager.stop_thinking_timer()
        
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
            self.options_panel.hide_requested.connect(self.hide_to_tray)
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
            
            # 更新提示为"思考中..."并重新启动思考定时器
            if self.message_bubble:
                self.message_bubble.set_text("思考中...")
                self.message_bubble.update_position()
                # 重新启动思考定时器，因为现在开始真正的AI思考
                self.decoration_manager.start_thinking_timer()
            
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
            
            # 停止思考定时器
            self.decoration_manager.stop_thinking_timer()
            
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
        
        # 启动思考超时定时器（3秒后显示加载圈）
        self.decoration_manager.start_thinking_timer()
        
        # 隐藏输入框，但保持选项栏显示
        if self.input_window:
            self.input_window.close()
            
        # 确保选项栏显示
        if not self.options_panel:
            self.options_panel = OptionsPanel(self)
            self.options_panel.exit_requested.connect(self.close_application)
            self.options_panel.hide_requested.connect(self.hide_to_tray)
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
        # AI开始响应时，停止思考定时器和加载圈
        self.decoration_manager.stop_thinking_timer()
        
        if self.message_bubble:
            current_text = self.message_bubble.get_current_text()
            # 如果当前文本是"思考中..."或者只包含工具调用信息（以">"开头），则清空
            if current_text == "思考中..." or (current_text.strip().startswith(">") and not any(c.isalnum() and not c.isascii() for c in current_text.replace(">", "").replace("工具调用", "").replace("：", ""))):
                current_text = ""
            new_text = current_text + text_chunk
            print(text_chunk, end="")
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
        # 停止思考定时器和加载圈
        self.decoration_manager.stop_thinking_timer()
        
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
        # 停止思考定时器和加载圈
        self.decoration_manager.stop_thinking_timer()
        
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
            self.ai_response_ready.emit(random.choice('\n' + SystemConfig.BACKUP_RESPONSES))
            print(e)

    def close_application(self):
        """关闭应用程序"""
        import os
        import sys
        
        # 执行真正的关闭流程
        self._real_close()
        
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
            
    def hide_to_tray(self):
        """隐藏所有组件"""
        try:
            # 隐藏所有窗口组件
            if self.input_window:
                self.input_window.hide()
            if self.options_panel:
                self.options_panel.hide()
            if self.message_bubble:
                self.message_bubble.hide()
            
            # 隐藏主窗口（桌宠本体）
            self.hide()
            
            # 更新托盘菜单状态
            self.system_tray.update_menu_state(False)
            
            print("已隐藏桌面宠物")
            
        except Exception as e:
            print(f"隐藏失败: {e}")
            
    def show_from_tray(self):
        """恢复显示"""
        try:
            # 显示主窗口（桌宠本体）
            self.show()
            self.raise_()
            self.activateWindow()
            
            # 更新托盘菜单状态
            self.system_tray.update_menu_state(True)
            
            print("已显示桌面宠物")
            
        except Exception as e:
            print(f"显示失败: {e}")
    
    def _apply_console_startup_config(self):
        """应用启动时的后台窗口配置"""
        from config import SystemConfig
        
        if SystemConfig.HIDE_CONSOLE_ON_STARTUP:
            try:
                import ctypes
                
                # 获取控制台窗口句柄
                kernel32 = ctypes.windll.kernel32
                user32 = ctypes.windll.user32
                
                console_window = kernel32.GetConsoleWindow()
                
                if console_window:
                    # 隐藏控制台窗口
                    user32.ShowWindow(console_window, 0)  # SW_HIDE = 0
                    self.system_tray.update_console_menu_state(False)
                    print("启动时已隐藏后台窗口")
                    
            except Exception as e:
                print(f"启动时隐藏后台窗口失败: {e}")
    
    def toggle_console_window(self):
        """切换后台窗口显示/隐藏"""
        try:
            import ctypes
            import sys
            
            # 获取控制台窗口句柄
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32
            
            # 获取当前进程的控制台窗口
            console_window = kernel32.GetConsoleWindow()
            
            if console_window:
                # 检查当前是否可见
                is_visible = user32.IsWindowVisible(console_window)
                
                if is_visible:
                    # 隐藏控制台窗口
                    user32.ShowWindow(console_window, 0)  # SW_HIDE = 0
                    self.system_tray.update_console_menu_state(False)
                    print("后台窗口已隐藏")
                else:
                    # 显示控制台窗口
                    user32.ShowWindow(console_window, 5)  # SW_SHOW = 5
                    self.system_tray.update_console_menu_state(True)
                    print("后台窗口已显示")
            else:
                print("未找到控制台窗口")
                
        except Exception as e:
            print(f"切换后台窗口失败: {e}")

    def closeEvent(self, event):
        """关闭事件 - 隐藏而不是退出"""
        # 隐藏窗口而不是退出
        self.hide_to_tray()
        event.ignore()  # 忽略关闭事件，不真正关闭
            
    def _real_close(self):
        """真正的关闭流程"""
        # 停止事件处理器的定时器
        self.event_handler.stop_timers()
        
        # 清理装饰
        self.decoration_manager.cleanup()
        
        # 停止AI线程和VLM线程
        if self.ai_thread and self.ai_thread.isRunning():
            self.ai_thread.terminate()
            self.ai_thread.wait()
        if self.vision_thread and self.vision_thread.isRunning():
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