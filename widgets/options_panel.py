from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFrame, QLabel, QMessageBox, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint, QTimer
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
        
        self.buttons = []  # 存储按钮引用
        self.animations = []  # 存储动画引用
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 主容器 - 垂直布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 0, 0, 0)  # 左边留出20px空间用于动画
        main_layout.setSpacing(OptionsConfig.BUTTON_SPACING)
        
        # 按钮样式 - 应用配置
        button_style = f"""
            QPushButton {{
                background-color: {OptionsConfig.NORMAL_BUTTON_COLOR};
                border: 1px solid #B0BEC5;
                border-radius: 6px;
                padding: 3px;
                margin: 0px;
                text-align: left;
                font-size: {OptionsConfig.BUTTON_FONT_SIZE}pt;
                color: #333;
                min-height: {OptionsConfig.BUTTON_HEIGHT}px;
                min-width: {OptionsConfig.BUTTON_WIDTH}px;
                max-width: {OptionsConfig.BUTTON_WIDTH}px;
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
        main_layout.addWidget(self.screenshot_button)
        self.buttons.append(self.screenshot_button)
        
        # 隐藏按钮
        self.hide_button = QPushButton(" 隐藏")
        self.hide_button.setStyleSheet(button_style)
        self.hide_button.setToolTip("隐藏到系统托盘")
        self.hide_button.clicked.connect(self.hide_requested.emit)
        main_layout.addWidget(self.hide_button)
        self.buttons.append(self.hide_button)
        
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
        main_layout.addWidget(self.exit_button)
        self.buttons.append(self.exit_button)
        
        # 为每个按钮设置透明度效果
        for button in self.buttons:
            opacity_effect = QGraphicsOpacityEffect(button)
            opacity_effect.setOpacity(0)  # 初始完全透明
            button.setGraphicsEffect(opacity_effect)
        
        # 设置固定宽度，高度自适应按钮和间距
        self.setFixedWidth(OptionsConfig.PANEL_WIDTH + 20)
        # 让布局自动计算高度
        self.adjustSize()
        
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
        """显示事件 - 确保窗口显示时位置正确并播放动画"""
        super().showEvent(event)
        # 立即更新位置
        self.update_position()
        
        # 重新为每个按钮设置透明度效果（确保每次显示都是透明的）
        for button in self.buttons:
            opacity_effect = QGraphicsOpacityEffect(button)
            opacity_effect.setOpacity(0)  # 初始完全透明
            button.setGraphicsEffect(opacity_effect)
        
        # 等待布局完成后再准备动画
        QTimer.singleShot(0, self.prepare_and_play_animation)
    
    def prepare_and_play_animation(self):
        """准备初始状态并播放从左到右的淡入动画"""
        # 清除旧动画
        self.animations.clear()
        
        # 强制更新布局，确保按钮位置已经确定
        self.layout().update()
        self.layout().activate()
        
        # 先保存所有按钮的最终位置并设置初始状态
        button_data = []
        for button in self.buttons:
            # 获取按钮当前位置作为最终位置
            final_pos = button.pos()
            # 计算初始位置（向左偏移15像素）
            initial_pos = final_pos - QPoint(15, 0)
            button_data.append((button, initial_pos, final_pos))
            # 立即设置到初始位置
            button.move(initial_pos)
        
        # 短暂延迟后开始动画，确保位置设置生效
        QTimer.singleShot(20, lambda: self._start_all_animations(button_data))
    
    def _start_all_animations(self, button_data):
        """启动所有按钮的动画"""
        for i, (button, initial_pos, final_pos) in enumerate(button_data):
            # 延迟启动，创建错落效果
            delay = i * 80  # 每个按钮延迟80ms
            
            # 使用定时器延迟启动动画
            QTimer.singleShot(delay, lambda b=button, ip=initial_pos, fp=final_pos: self._start_button_animation(b, ip, fp))
    
    def _start_button_animation(self, button, initial_pos, final_pos):
        """启动按钮动画"""
        # 确保按钮在初始位置
        button.move(initial_pos)
        
        # 获取透明度效果
        opacity_effect = button.graphicsEffect()
        if not opacity_effect:
            # 如果没有透明度效果，重新创建
            opacity_effect = QGraphicsOpacityEffect(button)
            opacity_effect.setOpacity(0)
            button.setGraphicsEffect(opacity_effect)
        
        # 创建透明度动画
        opacity_anim = QPropertyAnimation(opacity_effect, b"opacity", self)
        opacity_anim.setDuration(400)
        opacity_anim.setStartValue(0)
        opacity_anim.setEndValue(1)
        opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # 创建位置动画
        pos_anim = QPropertyAnimation(button, b"pos", self)
        pos_anim.setDuration(400)
        pos_anim.setStartValue(initial_pos)
        pos_anim.setEndValue(final_pos)
        pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # 启动动画
        opacity_anim.start()
        pos_anim.start()
        
        # 保存动画引用防止被垃圾回收
        self.animations.append(opacity_anim)
        self.animations.append(pos_anim)