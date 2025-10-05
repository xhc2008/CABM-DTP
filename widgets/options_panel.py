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
        
        self.all_buttons = []  # 存储所有功能按钮
        self.visible_buttons = []  # 当前页显示的按钮
        self.animations = []  # 存储动画引用
        
        self.current_page = 0  # 当前页码
        self.buttons_per_page = 3  # 每页显示的按钮数
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 主容器 - 垂直布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 主布局不设置边距
        main_layout.setSpacing(OptionsConfig.BUTTON_SPACING)
        
        # 按钮样式 - 应用配置
        button_style = f"""
            QPushButton {{
                background-color: {OptionsConfig.NORMAL_BUTTON_COLOR};
                border: 1px solid #B0BEC5;
                border-radius: 6px;
                padding: 3px;
                margin: 0px;
                text-align: centre;
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
        
        # 计算翻页按钮宽度：需要考虑边框和padding的额外宽度
        # border: 1px * 2 (左右) = 2px, padding: 3px * 2 (左右) = 6px, 总共8px
        button_extra_width = 8  # 边框和padding的额外宽度
        page_button_spacing = 2  # 按钮间距
        # 总宽度 = BUTTON_WIDTH + button_extra_width，两个按钮平分，减去间距
        page_button_width = (OptionsConfig.BUTTON_WIDTH + button_extra_width - page_button_spacing) // 2 - button_extra_width
        
        # 翻页按钮样式
        page_button_style = f"""
            QPushButton {{
                background-color: {OptionsConfig.NORMAL_BUTTON_COLOR};
                border: 1px solid #B0BEC5;
                border-radius: 6px;
                padding: 3px;
                margin: 0px;
                text-align: center;
                font-size: {OptionsConfig.BUTTON_FONT_SIZE}pt;
                color: #333;
                min-height: {OptionsConfig.BUTTON_HEIGHT}px;
                min-width: {page_button_width}px;
                max-width: {page_button_width}px;
            }}
            QPushButton:hover {{
                background-color: {OptionsConfig.HOVER_BUTTON_COLOR};
                border-color: #2196F3;
            }}
            QPushButton:pressed {{
                background-color: {OptionsConfig.PRESSED_BUTTON_COLOR};
            }}
            QPushButton:disabled {{
                background-color: #E0E0E0;
                color: #999;
                border-color: #CCC;
            }}
        """
        
        # 创建所有功能按钮（但不添加到布局）
        # 截图按钮
        self.screenshot_button = QPushButton("截图")
        self.screenshot_button.setStyleSheet(button_style)
        self.screenshot_button.clicked.connect(self.screenshot_requested.emit)
        self.all_buttons.append(self.screenshot_button)
        
        # 隐藏按钮
        self.hide_button = QPushButton("隐藏")
        self.hide_button.setStyleSheet(button_style)
        self.hide_button.setToolTip("隐藏到系统托盘")
        self.hide_button.clicked.connect(self.hide_requested.emit)
        self.all_buttons.append(self.hide_button)
        
        # 退出按钮
        self.exit_button = QPushButton("退出")
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
        self.all_buttons.append(self.exit_button)
        
        # 临时演示按钮
        demo_button1 = QPushButton("空白")
        demo_button1.setStyleSheet(button_style)
        demo_button1.clicked.connect(lambda: print("功能1被点击"))
        self.all_buttons.append(demo_button1)
        
        demo_button2 = QPushButton("空白")
        demo_button2.setStyleSheet(button_style)
        demo_button2.clicked.connect(lambda: print("功能2被点击"))
        self.all_buttons.append(demo_button2)
        
        demo_button3 = QPushButton("空白")
        demo_button3.setStyleSheet(button_style)
        demo_button3.clicked.connect(lambda: print("功能3被点击"))
        self.all_buttons.append(demo_button3)
        
        demo_button4 = QPushButton("空白")
        demo_button4.setStyleSheet(button_style)
        demo_button4.clicked.connect(lambda: print("功能4被点击"))
        self.all_buttons.append(demo_button4)
        
        # 创建翻页按钮容器（放在最上面）
        page_controls = QWidget()
        page_controls.setFixedWidth(OptionsConfig.BUTTON_WIDTH + button_extra_width)  # 设置固定宽度，考虑边框和padding
        page_layout = QHBoxLayout(page_controls)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(page_button_spacing)
        
        # 添加左边距以与功能按钮对齐
        page_controls_wrapper = QWidget()
        page_controls_wrapper_layout = QHBoxLayout(page_controls_wrapper)
        page_controls_wrapper_layout.setContentsMargins(20, 0, 0, 0)  # 左边距20px
        page_controls_wrapper_layout.setSpacing(0)
        page_controls_wrapper_layout.addWidget(page_controls)
        
        # 上一页按钮
        self.prev_button = QPushButton("<")
        self.prev_button.setStyleSheet(page_button_style)
        self.prev_button.clicked.connect(self.prev_page)
        page_layout.addWidget(self.prev_button, 0, Qt.AlignLeft)  # 左对齐，不拉伸
        
        # 下一页按钮
        self.next_button = QPushButton(">")
        self.next_button.setStyleSheet(page_button_style)
        self.next_button.clicked.connect(self.next_page)
        page_layout.addWidget(self.next_button, 0, Qt.AlignRight)  # 右对齐，不拉伸
        
        main_layout.addWidget(page_controls_wrapper)
        
        # 创建按钮容器（用于显示当前页的按钮）
        self.buttons_container = QWidget()
        self.buttons_layout = QVBoxLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(20, 0, 0, 0)  # 左边留出20px空间用于功能按钮的滑入动画
        self.buttons_layout.setSpacing(OptionsConfig.BUTTON_SPACING)
        main_layout.addWidget(self.buttons_container)
        
        # 页码标签（放在最下面，单独一行）
        self.page_label = QLabel()
        self.page_label.setFixedWidth(OptionsConfig.BUTTON_WIDTH + button_extra_width)  # 设置固定宽度，考虑边框和padding
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet(f"color: #666; font-size: {OptionsConfig.BUTTON_FONT_SIZE}pt;")
        
        # 添加左边距以与功能按钮对齐
        page_label_wrapper = QWidget()
        page_label_wrapper_layout = QHBoxLayout(page_label_wrapper)
        page_label_wrapper_layout.setContentsMargins(20, 0, 0, 0)  # 左边距20px
        page_label_wrapper_layout.setSpacing(0)
        page_label_wrapper_layout.addWidget(self.page_label)
        
        main_layout.addWidget(page_label_wrapper)
        
        # 显示第一页
        self.update_page()
        
        # 设置固定宽度，高度自适应按钮和间距
        # 宽度 = 按钮宽度 + 边框padding + 功能按钮的动画空间
        self.setFixedWidth(OptionsConfig.BUTTON_WIDTH + button_extra_width + 20)
        # 让布局自动计算高度
        self.adjustSize()
    
    def update_page(self):
        """更新当前页显示的按钮"""
        # 清空当前显示的按钮
        for button in self.visible_buttons:
            self.buttons_layout.removeWidget(button)
            button.hide()
        self.visible_buttons.clear()
        
        # 计算总页数
        total_pages = (len(self.all_buttons) + self.buttons_per_page - 1) // self.buttons_per_page
        
        # 计算当前页的按钮范围
        start_idx = self.current_page * self.buttons_per_page
        end_idx = min(start_idx + self.buttons_per_page, len(self.all_buttons))
        
        # 添加当前页的按钮
        for i in range(start_idx, end_idx):
            button = self.all_buttons[i]
            self.buttons_layout.addWidget(button)
            button.show()
            self.visible_buttons.append(button)
            
            # 设置透明度效果
            opacity_effect = QGraphicsOpacityEffect(button)
            opacity_effect.setOpacity(0)  # 初始完全透明
            button.setGraphicsEffect(opacity_effect)
        
        # 更新翻页按钮状态
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)
        
        # 更新页码标签
        self.page_label.setText(f"{self.current_page + 1}/{total_pages}")
        
        # 调整窗口大小
        self.adjustSize()
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()
            # 重新播放动画
            QTimer.singleShot(0, self.prepare_and_play_animation)
    
    def next_page(self):
        """下一页"""
        total_pages = (len(self.all_buttons) + self.buttons_per_page - 1) // self.buttons_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_page()
            # 重新播放动画
            QTimer.singleShot(0, self.prepare_and_play_animation)
        
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
        for button in self.visible_buttons:
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
        for button in self.visible_buttons:
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