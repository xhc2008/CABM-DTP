from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFrame, QLabel, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from config import OptionsConfig

class OptionsPanel(QWidget):
    """选项栏面板"""
    exit_requested = pyqtSignal()  # 退出信号
    hide_requested = pyqtSignal()  # 隐藏信号
    screenshot_requested = pyqtSignal()  # 截图信号
    
    def __init__(self, parent_pet):
        super().__init__()
        self.parent_pet = parent_pet
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(OptionsConfig.PANEL_WIDTH, OptionsConfig.PANEL_HEIGHT)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 主容器
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 装饰性外框
        outer_frame = QFrame()
        outer_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {OptionsConfig.BACKGROUND_COLOR};
                border-radius: {OptionsConfig.BORDER_RADIUS}px;
                border: 2px solid {OptionsConfig.BORDER_COLOR};
            }}
        """)
        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(8, 8, 8, 8)
        outer_layout.setSpacing(OptionsConfig.BUTTON_SPACING)
        
        # 标题
        title_label = QLabel("CABM")
        title_label.setFont(QFont("Arial", OptionsConfig.TITLE_FONT_SIZE, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #333;
                padding: 5px;
                border-bottom: 1px solid #ddd;
                margin-bottom: 5px;
            }
        """)
        outer_layout.addWidget(title_label)
        
        # 按钮样式
        button_style = f"""
            QPushButton {{
                background-color: {OptionsConfig.NORMAL_BUTTON_COLOR};
                border: 1px solid #B0BEC5;
                border-radius: 6px;
                padding: 3px;
                text-align: left;
                font-size: {OptionsConfig.BUTTON_FONT_SIZE}pt;
                color: #333;
                min-height: {OptionsConfig.BUTTON_HEIGHT}px;
            }}
            QPushButton:hover {{
                background-color: {OptionsConfig.HOVER_BUTTON_COLOR};
                border-color: #2196F3;
            }}
            QPushButton:pressed {{
                background-color: {OptionsConfig.PRESSED_BUTTON_COLOR};
            }}
        """
        
        # 截图按钮
        self.screenshot_button = QPushButton(" 截图")
        self.screenshot_button.setStyleSheet(button_style)
        self.screenshot_button.clicked.connect(self.screenshot_requested.emit)
        outer_layout.addWidget(self.screenshot_button)
        
        # 隐藏按钮
        self.hide_button = QPushButton(" 隐藏")
        self.hide_button.setStyleSheet(button_style)
        self.hide_button.clicked.connect(self.hide_requested.emit)
        outer_layout.addWidget(self.hide_button)
        
        # 退出按钮
        self.exit_button = QPushButton(" 退出")
        self.exit_button.setStyleSheet(button_style + f"""
            QPushButton {{
                color: {OptionsConfig.EXIT_BUTTON_COLOR};
            }}
            QPushButton:hover {{
                background-color: {OptionsConfig.EXIT_BUTTON_HOVER_BG};
                border-color: #f44336;
            }}
        """)
        self.exit_button.clicked.connect(self.confirm_exit)
        outer_layout.addWidget(self.exit_button)
        
        # 添加弹性空间
        outer_layout.addStretch()
        
        main_layout.addWidget(outer_frame)
        
    def update_position(self):
        """更新位置（在宠物右侧）"""
        if self.parent_pet and self.isVisible():
            # 获取宠物位置
            pet_geometry = self.parent_pet.frameGeometry()
            
            # 计算位置：在宠物右侧
            x = pet_geometry.x() + pet_geometry.width() + OptionsConfig.PANEL_OFFSET_X
            y = pet_geometry.y() - self.height() + OptionsConfig.PANEL_OFFSET_Y
            
            self.move(x, y)
            
    def confirm_exit(self):
        """确认退出对话框"""
        reply = QMessageBox.question(
            self, 
            '确认退出', 
            '真的要关掉吗QwQ',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.exit_requested.emit()
            
    def showEvent(self, event):
        """显示事件 - 确保窗口显示时位置正确"""
        super().showEvent(event)
        # 立即更新位置
        self.update_position()