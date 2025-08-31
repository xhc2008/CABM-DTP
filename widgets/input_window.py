from PyQt5.QtWidgets import (QWidget, QLineEdit, QVBoxLayout, 
                             QHBoxLayout, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class InputWindow(QWidget):
    """输入窗口"""
    message_sent = pyqtSignal(str)  # 发送消息信号
    
    def __init__(self, parent_pet):
        super().__init__()
        self.parent_pet = parent_pet
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(220, 60)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 主容器
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 装饰性外框
        outer_frame = QFrame()
        outer_frame.setStyleSheet("""
            QFrame {
                background-color: lightblue;
                border-radius: 12px;
                border: 2px solid #81D4FA;
            }
        """)
        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(3, 3, 3, 3)
        
        # 内部容器
        inner_frame = QFrame()
        inner_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
            }
        """)
        inner_layout = QHBoxLayout(inner_frame)
        inner_layout.setContentsMargins(10, 8, 10, 8)
        
        # 输入框
        self.input_edit = QLineEdit()
        self.input_edit.setFont(QFont("Arial", 10))
        self.input_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #B0BEC5;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.input_edit.returnPressed.connect(self.send_message)
        
        # 重写按键事件
        self.input_edit.keyPressEvent = self.handle_key_press
        
        inner_layout.addWidget(self.input_edit)
        outer_layout.addWidget(inner_frame)
        main_layout.addWidget(outer_frame)
        
    def handle_key_press(self, event):
        """处理按键事件"""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            QLineEdit.keyPressEvent(self.input_edit, event)
            
    def send_message(self):
        """发送消息"""
        message = self.input_edit.text().strip()
        if message:
            self.message_sent.emit(message)
        self.input_edit.clear()  # 清空输入框内容
        self.close()
        
    def focus_input(self):
        """聚焦到输入框"""
        self.input_edit.setFocus()
        self.input_edit.selectAll()  # 选中所有文本方便重新输入
        
    def update_position(self):
        """更新位置（跟随宠物）"""
        if self.parent_pet and self.isVisible():
            # 确保使用正确的几何信息
            pet_geometry = self.parent_pet.frameGeometry()
            input_width = self.width()
            input_height = self.height()
            
            x = pet_geometry.x() + (pet_geometry.width() - input_width) // 2
            y = pet_geometry.y() - input_height - 10
            
            self.move(x, y)
            
    def showEvent(self, event):
        """显示事件 - 确保窗口显示时位置正确"""
        super().showEvent(event)
        # 立即更新位置
        self.update_position()