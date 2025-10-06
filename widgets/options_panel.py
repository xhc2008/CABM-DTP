from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFrame, QLabel, QMessageBox, QGraphicsOpacityEffect, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint, QTimer, QSize
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
        self.placeholders = []  # 存储占位符
        
        self.current_page = 0  # 当前页码
        self.buttons_per_page = 3  # 每页显示的按钮数
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 主容器 - 垂直布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
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
        
        # 计算翻页按钮宽度
        button_extra_width = 8
        page_button_spacing = 2
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
        
        # 初始化所有按钮：隐藏并设置为透明
        for button in self.all_buttons:
            button.hide()
            opacity_effect = QGraphicsOpacityEffect(button)
            opacity_effect.setOpacity(0)
            button.setGraphicsEffect(opacity_effect)
        
        # 创建翻页按钮容器
        page_controls = QWidget()
        page_controls.setFixedWidth(OptionsConfig.BUTTON_WIDTH + button_extra_width)
        page_layout = QHBoxLayout(page_controls)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(page_button_spacing)
        
        page_controls_wrapper = QWidget()
        page_controls_wrapper_layout = QHBoxLayout(page_controls_wrapper)
        page_controls_wrapper_layout.setContentsMargins(20, 0, 0, 0)
        page_controls_wrapper_layout.setSpacing(0)
        page_controls_wrapper_layout.addWidget(page_controls)
        
        # 上一页按钮
        self.prev_button = QPushButton("<")
        self.prev_button.setStyleSheet(page_button_style)
        self.prev_button.clicked.connect(self.prev_page)
        page_layout.addWidget(self.prev_button, 0, Qt.AlignLeft)
        
        # 下一页按钮
        self.next_button = QPushButton(">")
        self.next_button.setStyleSheet(page_button_style)
        self.next_button.clicked.connect(self.next_page)
        page_layout.addWidget(self.next_button, 0, Qt.AlignRight)
        
        main_layout.addWidget(page_controls_wrapper)
        
        # 创建按钮容器
        self.buttons_container = QWidget()
        self.buttons_container.setFixedHeight(OptionsConfig.PANEL_HEIGHT)
        self.buttons_layout = QVBoxLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(20, 0, 0, 0)
        self.buttons_layout.setSpacing(OptionsConfig.BUTTON_SPACING)
        self.buttons_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(self.buttons_container)
        
        # 页码标签
        self.page_label = QLabel()
        self.page_label.setFixedWidth(OptionsConfig.BUTTON_WIDTH + button_extra_width)
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet(f"color: #666; font-size: {OptionsConfig.BUTTON_FONT_SIZE}pt;")
        
        page_label_wrapper = QWidget()
        page_label_wrapper_layout = QHBoxLayout(page_label_wrapper)
        page_label_wrapper_layout.setContentsMargins(20, 0, 0, 0)
        page_label_wrapper_layout.setSpacing(0)
        page_label_wrapper_layout.addWidget(self.page_label)
        
        main_layout.addWidget(page_label_wrapper)
        
        # 设置固定宽度
        self.setFixedWidth(OptionsConfig.BUTTON_WIDTH + button_extra_width + 20)
        
        # 初始显示第一页（使用占位符）
        self.update_page()
        
    def update_page(self):
        """更新当前页显示的按钮"""
        # 清空当前显示的按钮和占位符
        for button in self.visible_buttons:
            self.buttons_layout.removeWidget(button)
            button.hide()
        self.visible_buttons.clear()
        
        # 清空占位符
        for placeholder in self.placeholders:
            self.buttons_layout.removeItem(placeholder)
        self.placeholders.clear()
        
        # 计算总页数
        total_pages = (len(self.all_buttons) + self.buttons_per_page - 1) // self.buttons_per_page
        
        # 计算当前页的按钮范围
        start_idx = self.current_page * self.buttons_per_page
        end_idx = min(start_idx + self.buttons_per_page, len(self.all_buttons))
        
        # 添加占位符来保持布局稳定
        for i in range(start_idx, end_idx):
            # 创建占位符，大小与按钮相同
            spacer = QSpacerItem(
                OptionsConfig.BUTTON_WIDTH, 
                OptionsConfig.BUTTON_HEIGHT,
                QSizePolicy.Fixed, 
                QSizePolicy.Fixed
            )
            self.buttons_layout.addItem(spacer)
            self.placeholders.append(spacer)
            
            # 保存对应的按钮引用（但不添加到布局）
            button = self.all_buttons[i]
            self.visible_buttons.append(button)
        
        # 更新翻页按钮状态
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)
        
        # 更新页码标签
        self.page_label.setText(f"{self.current_page + 1}/{total_pages}")
    
    def showEvent(self, event):
        """显示事件 - 替换占位符为真实按钮并播放动画"""
        super().showEvent(event)
        self.update_position()
        
        # 延迟执行，确保布局已经完成
        QTimer.singleShot(10, self.replace_placeholders_with_buttons)
    
    def hideEvent(self, event):
        """隐藏事件 - 用占位符替换真实按钮"""
        super().hideEvent(event)
        self.replace_buttons_with_placeholders()
    
    def replace_placeholders_with_buttons(self):
        """用真实按钮替换占位符并播放动画"""
        if not self.placeholders:
            return
            
        # 移除所有占位符
        for placeholder in self.placeholders:
            self.buttons_layout.removeItem(placeholder)
        self.placeholders.clear()
        
        # 添加真实按钮并设置初始状态
        for i, button in enumerate(self.visible_buttons):
            # 设置初始状态：在左侧外部且透明
            button.move(-200, i * (OptionsConfig.BUTTON_HEIGHT + OptionsConfig.BUTTON_SPACING))
            opacity_effect = button.graphicsEffect()
            if opacity_effect:
                opacity_effect.setOpacity(0)
            
            # 添加到布局
            self.buttons_layout.addWidget(button)
            button.show()
        
        # 强制布局更新
        self.buttons_container.layout().update()
        self.buttons_container.layout().activate()
        
        # 获取最终位置并开始动画
        QTimer.singleShot(20, self.start_enter_animation)
    
    def replace_buttons_with_placeholders(self):
        """用占位符替换真实按钮"""
        # 移除所有按钮
        for button in self.visible_buttons:
            self.buttons_layout.removeWidget(button)
            button.hide()
        
        # 重新添加占位符
        for i in range(len(self.visible_buttons)):
            spacer = QSpacerItem(
                OptionsConfig.BUTTON_WIDTH, 
                OptionsConfig.BUTTON_HEIGHT,
                QSizePolicy.Fixed, 
                QSizePolicy.Fixed
            )
            self.buttons_layout.addItem(spacer)
            self.placeholders.append(spacer)
    
    def start_enter_animation(self):
        """开始进入动画"""
        self.animations.clear()
        
        # 收集按钮的初始和最终位置
        button_data = []
        for button in self.visible_buttons:
            final_pos = button.pos()
            initial_pos = QPoint(-15, final_pos.y())
            button_data.append((button, initial_pos, final_pos))
        
        # 启动错落动画
        for i, (button, initial_pos, final_pos) in enumerate(button_data):
            QTimer.singleShot(
                i * 80, 
                lambda b=button, ip=initial_pos, fp=final_pos: self.animate_single_button(b, ip, fp)
            )
    
    def animate_single_button(self, button, initial_pos, final_pos):
        """动画单个按钮"""
        # 确保在初始位置
        button.move(initial_pos)
        
        # 获取或创建透明度效果
        opacity_effect = button.graphicsEffect()
        if not opacity_effect:
            opacity_effect = QGraphicsOpacityEffect(button)
            opacity_effect.setOpacity(0)
            button.setGraphicsEffect(opacity_effect)
        
        # 创建并行动画
        opacity_anim = QPropertyAnimation(opacity_effect, b"opacity")
        opacity_anim.setDuration(400)
        opacity_anim.setStartValue(0)
        opacity_anim.setEndValue(1)
        opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        pos_anim = QPropertyAnimation(button, b"pos")
        pos_anim.setDuration(400)
        pos_anim.setStartValue(initial_pos)
        pos_anim.setEndValue(final_pos)
        pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        opacity_anim.start()
        pos_anim.start()
        
        self.animations.extend([opacity_anim, pos_anim])
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()
            if self.isVisible():
                QTimer.singleShot(10, self.replace_placeholders_with_buttons)
    
    def next_page(self):
        """下一页"""
        total_pages = (len(self.all_buttons) + self.buttons_per_page - 1) // self.buttons_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_page()
            if self.isVisible():
                QTimer.singleShot(10, self.replace_placeholders_with_buttons)

    # 其他方法保持不变...
    def update_position(self):
        """更新位置（在宠物右侧）"""
        if self.parent_pet and self.isVisible():
            pet_geometry = self.parent_pet.frameGeometry()
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