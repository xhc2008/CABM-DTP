"""
宠物装饰模块
包含加载圈等各种装饰效果
"""
import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QLineF, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen
from config import PetDecorationConfig


class LoadingSpinner(QWidget):
    """小型加载圈组件，显示在宠物头上"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(PetDecorationConfig.LOADING_SPINNER_SIZE, 
                         PetDecorationConfig.LOADING_SPINNER_SIZE)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        
    def start_animation(self):
        """开始动画"""
        self.timer.start(PetDecorationConfig.LOADING_SPINNER_ANIMATION_SPEED)
        self.show()
        
    def stop_animation(self):
        """停止动画"""
        self.timer.stop()
        self.hide()
        
    def update_animation(self):
        """更新动画"""
        self.angle = (self.angle + PetDecorationConfig.LOADING_SPINNER_ROTATION_STEP) % 360
        self.update()
        
    def paintEvent(self, event):
        """绘制加载圈"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = QPointF(self.width() / 2, self.height() / 2)
        radius = min(self.width(), self.height()) / 2 * 0.7
        
        # 绘制多个小点组成的圈
        for i in range(PetDecorationConfig.LOADING_SPINNER_DOTS):
            angle_rad = math.radians(self.angle + i * (360 / PetDecorationConfig.LOADING_SPINNER_DOTS))
            alpha = 255 * (i / PetDecorationConfig.LOADING_SPINNER_DOTS)
            
            color = QColor(*PetDecorationConfig.LOADING_SPINNER_COLOR, int(alpha))
            pen = QPen(color)
            pen.setWidth(PetDecorationConfig.LOADING_SPINNER_LINE_WIDTH)
            painter.setPen(pen)
            
            start_point = QPointF(
                center.x() + (radius - 4) * math.cos(angle_rad),
                center.y() + (radius - 4) * math.sin(angle_rad)
            )
            end_point = QPointF(
                center.x() + radius * math.cos(angle_rad),
                center.y() + radius * math.sin(angle_rad)
            )
            
            painter.drawLine(QLineF(start_point, end_point))


class PetDecorationManager:
    """宠物装饰管理器"""
    def __init__(self, parent_pet):
        self.parent_pet = parent_pet
        self.loading_spinner = None
        self.thinking_timer = None
        
    def start_thinking_timer(self):
        """启动思考超时定时器"""
        # 清理之前的定时器
        self.stop_thinking_timer()
        
        # 创建定时器
        self.thinking_timer = QTimer()
        self.thinking_timer.setSingleShot(True)
        self.thinking_timer.timeout.connect(self.show_loading_spinner)
        self.thinking_timer.start(PetDecorationConfig.THINKING_TIMEOUT)
        
    def stop_thinking_timer(self):
        """停止思考定时器并隐藏加载圈"""
        if self.thinking_timer:
            self.thinking_timer.stop()
            self.thinking_timer = None
            
        if self.loading_spinner:
            self.loading_spinner.stop_animation()
            self.loading_spinner = None
            
    def show_loading_spinner(self):
        """显示加载圈在宠物头上"""
        if not self.loading_spinner:
            self.loading_spinner = LoadingSpinner(self.parent_pet)
            
        # 计算并设置加载圈位置
        self._calculate_and_set_spinner_position()
        self.loading_spinner.start_animation()
        
    def update_loading_spinner_position(self):
        """更新加载圈位置（当宠物移动时）"""
        if self.loading_spinner:
            self._calculate_and_set_spinner_position()
            
    def _calculate_and_set_spinner_position(self):
        """计算并设置加载圈位置"""
        if self.loading_spinner:
            pet_geometry = self.parent_pet.frameGeometry()
            
            # 计算位置：宠物中心 + 偏移
            spinner_x = (pet_geometry.x() + pet_geometry.width() // 2 + 
                        PetDecorationConfig.LOADING_SPINNER_OFFSET_X - 
                        PetDecorationConfig.LOADING_SPINNER_SIZE // 2)
            spinner_y = (pet_geometry.y() + 
                        PetDecorationConfig.LOADING_SPINNER_OFFSET_Y)
            
            self.loading_spinner.move(spinner_x, spinner_y)
            
    def cleanup(self):
        """清理所有装饰"""
        self.stop_thinking_timer()