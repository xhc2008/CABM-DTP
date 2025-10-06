from PyQt5.QtWidgets import (QWidget, QTextEdit, QVBoxLayout, 
                             QHBoxLayout, QFrame, QApplication, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap, QTextCursor
from config import InputConfig

class InputWindow(QWidget):
    """输入窗口"""
    message_sent = pyqtSignal(str, object)  # 发送消息信号，包含文本和图片
    
    def __init__(self, parent_pet):
        super().__init__()
        self.parent_pet = parent_pet
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 图片相关
        self.current_image = None  # 当前图片
        self.image_label = None    # 图片显示标签
        
        # 动态调整窗口大小
        self.image_height = InputConfig.IMAGE_THUMBNAIL_HEIGHT  # 图片缩略图高度
        self.min_input_height = 40  # 最小输入框高度（实际可输入区域）
        self.max_input_height = 200  # 最大输入框高度
        self.current_input_height = self.min_input_height
        # 窗口高度 = 输入框高度 + 边框（去掉了之前的多余padding）
        self.base_height = self.min_input_height + 4  # 只保留2px边框 * 2
        self.setFixedSize(InputConfig.WINDOW_WIDTH, self.base_height)
        
        # 安装全局事件过滤器来检测点击其他地方
        QApplication.instance().installEventFilter(self)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 主容器
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 装饰性外框 - 去除多余边距
        self.outer_frame = QFrame()
        self.outer_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 2px solid #B0BEC5;
            }
        """)
        self.outer_layout = QVBoxLayout(self.outer_frame)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)
        
        # 图片显示区域（初始隐藏）
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                border-radius: 0px;
                margin: 0px;
                padding: 5px;
            }
        """)
        self.image_label.setFixedHeight(self.image_height)
        self.image_label.hide()
        self.image_label.mousePressEvent = self.clear_image  # 点击清除图片
        self.outer_layout.addWidget(self.image_label)
        
        # 输入框 - 使用QTextEdit支持多行
        self.input_edit = QTextEdit()
        self.input_edit.setFont(QFont("Arial", 10))
        self.input_edit.setStyleSheet("""
            QTextEdit {
                border: none;
                border-radius: 10px;
                padding: 10px;
                background-color: white;
            }
        """)
        self.input_edit.setPlaceholderText("")
        self.input_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_edit.setFixedHeight(self.min_input_height)
        
        # 连接文本变化信号以动态调整高度
        self.input_edit.textChanged.connect(self.adjust_input_height)
        
        # 重写按键事件
        self.input_edit.keyPressEvent = self.handle_key_press
        
        self.outer_layout.addWidget(self.input_edit)
        self.main_layout.addWidget(self.outer_frame)
        
    def handle_key_press(self, event):
        """处理按键事件"""
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Ctrl+Enter 或 Shift+Enter 换行
            if event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier):
                QTextEdit.keyPressEvent(self.input_edit, event)
            else:
                # 普通Enter发送消息
                self.send_message()
        else:
            QTextEdit.keyPressEvent(self.input_edit, event)
            
    def send_message(self):
        """发送消息"""
        try:
            message = self.input_edit.toPlainText().strip()
            current_image = self.current_image  # 保存当前图片引用
            
            if message or current_image:
                print(f"发送消息: 文本='{message}', 有图片={current_image is not None}")
                self.message_sent.emit(message, current_image)
                
            self.input_edit.clear()  # 清空输入框内容
            self.clear_image()  # 清空图片
            self.close()
            
        except Exception as e:
            print(f"发送消息时出错: {e}")
            import traceback
            traceback.print_exc()
            # 即使出错也要关闭窗口
            self.close()
    
    def adjust_input_height(self):
        """根据内容动态调整输入框高度"""
        # 获取文档内容的实际高度
        doc_height = self.input_edit.document().size().height()
        # 计算需要的高度：文档高度 + padding（上下各10px）
        content_height = int(doc_height) + 20
        
        # 限制在最小和最大高度之间
        new_height = max(self.min_input_height, min(content_height, self.max_input_height))
        
        # 只有当高度变化超过阈值时才调整（避免微小变化导致频繁调整）
        if abs(new_height - self.current_input_height) > 2:
            height_diff = new_height - self.current_input_height
            self.current_input_height = new_height
            
            # 调整输入框高度
            self.input_edit.setFixedHeight(new_height)
            
            # 调整窗口总高度
            current_window_height = self.height()
            new_window_height = current_window_height + height_diff
            
            # 保存当前窗口底部位置
            old_bottom = self.geometry().bottom()
            
            self.setFixedSize(InputConfig.WINDOW_WIDTH, new_window_height)
            
            # 向上调整位置，保持底部不变
            new_y = old_bottom - new_window_height
            self.move(self.x(), new_y)
        
    def set_image(self, pixmap):
        """设置图片"""
        try:
            if pixmap and not pixmap.isNull():
                print(f"设置图片，原始尺寸: {pixmap.width()}x{pixmap.height()}")
                # 覆盖原图片
                self.current_image = pixmap
                
                # 创建缩略图
                thumbnail = pixmap.scaled(
                    self.image_label.width() - 10, 
                    self.image_height - 10, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                print(f"缩略图尺寸: {thumbnail.width()}x{thumbnail.height()}")
                
                self.image_label.setPixmap(thumbnail)
                self.image_label.show()
                
                # 调整窗口大小
                new_height = self.base_height + self.image_height + 10
                self.setFixedSize(InputConfig.WINDOW_WIDTH, new_height)
                print(f"窗口大小调整为: {InputConfig.WINDOW_WIDTH}x{new_height}")
                
                # 更新位置
                self.update_position()
                print("图片设置完成")
            else:
                print("图片无效，无法设置")
        except Exception as e:
            print(f"设置图片时出错: {e}")
            # 出错时清除图片状态
            self.clear_image()
            
    def clear_image(self, event=None):
        """清除图片"""
        self.current_image = None
        self.image_label.clear()
        self.image_label.hide()
        
        # 恢复原始窗口大小
        self.setFixedSize(InputConfig.WINDOW_WIDTH, self.base_height)
        
        # 更新位置
        self.update_position()
        
    def focus_input(self):
        """聚焦到输入框"""
        self.input_edit.setFocus()
        # 添加激活状态的边框高亮效果
        self.outer_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 2px solid #64B5F6;
            }
        """)
        # 选中所有文本
        cursor = self.input_edit.textCursor()
        cursor.select(QTextCursor.Document)
        self.input_edit.setTextCursor(cursor)
        
    def update_position(self):
        """更新位置（跟随宠物）"""
        if self.parent_pet and self.isVisible():
            # 确保使用正确的几何信息
            pet_geometry = self.parent_pet.frameGeometry()
            input_width = self.width()
            input_height = self.height()
            
            x = pet_geometry.x() + (pet_geometry.width() - input_width) // 2 + InputConfig.WINDOW_OFFSET_X
            y = pet_geometry.y() - input_height + InputConfig.WINDOW_OFFSET_Y
            
            self.move(x, y)
            
    def showEvent(self, event):
        """显示事件 - 确保窗口显示时位置正确"""
        super().showEvent(event)
        # 立即更新位置
        self.update_position()
        
    def eventFilter(self, obj, event):
        """全局事件过滤器 - 检测点击其他地方"""
        if event.type() == event.MouseButtonPress:
            # 检查点击是否在输入窗口或选项栏之外
            if self.isVisible():
                click_pos = event.globalPos()
                input_rect = self.geometry()
                
                # 检查是否点击在输入窗口内
                if not input_rect.contains(click_pos):
                    # 检查是否点击在选项栏内（如果存在）
                    options_panel = getattr(self.parent_pet, 'options_panel', None)
                    if options_panel and options_panel.isVisible():
                        options_rect = options_panel.geometry()
                        if not options_rect.contains(click_pos):
                            # 检查是否点击在桌宠本体上（如果是右键，让桌宠处理）
                            pet_rect = self.parent_pet.geometry()
                            if pet_rect.contains(click_pos) and event.button() == Qt.RightButton:
                                # 让桌宠的右键逻辑处理，不在这里关闭
                                pass
                            else:
                                # 点击在其他地方，关闭窗口
                                self.close()
                                if options_panel:
                                    options_panel.close()
                    else:
                        # 检查是否点击在桌宠本体上（如果是右键，让桌宠处理）
                        pet_rect = self.parent_pet.geometry()
                        if pet_rect.contains(click_pos) and event.button() == Qt.RightButton:
                            # 让桌宠的右键逻辑处理，不在这里关闭
                            pass
                        else:
                            # 点击在其他地方，关闭窗口
                            self.close()
        
        return super().eventFilter(obj, event)
        
    def closeEvent(self, event):
        """关闭事件 - 移除事件过滤器，恢复样式"""
        QApplication.instance().removeEventFilter(self)
        # 恢复未激活状态样式
        self.outer_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 2px solid #B0BEC5;
            }
        """)
        # 重置输入框高度
        self.current_input_height = self.min_input_height
        self.input_edit.setFixedHeight(self.min_input_height)
        super().closeEvent(event)