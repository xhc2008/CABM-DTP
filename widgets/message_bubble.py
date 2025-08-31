from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics

class MessageBubble(QWidget):
    """消息气泡窗口"""
    def __init__(self, parent_pet):
        super().__init__()
        self.parent_pet = parent_pet
        self.text = ""
        self.font = QFont("Arial", 9)
        self.padding = 20  # 内边距
        self.arrow_height = 15  # 箭头高度
        self.min_width = 100  # 最小宽度
        self.max_width = 300  # 最大宽度
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._calculate_size()
        
    def _calculate_size(self):
        """根据文本内容计算窗口大小"""
        if not self.text:
            self.resize(self.min_width, 50)
            return
            
        # 使用字体度量计算文本尺寸
        font_metrics = QFontMetrics(self.font)
        
        # 计算文本在指定宽度范围内的尺寸
        text_width = font_metrics.horizontalAdvance(self.text)
        
        # 如果文本宽度超过最大宽度，需要换行
        if text_width > self.max_width - self.padding * 2:
            # 计算换行后的文本高度
            text_rect = font_metrics.boundingRect(
                0, 0, self.max_width - self.padding * 2, 1000,
                Qt.AlignLeft | Qt.TextWordWrap, self.text
            )
            bubble_width = self.max_width
            text_height = text_rect.height()
        else:
            # 单行文本
            text_height = font_metrics.height()
            bubble_width = max(text_width + self.padding * 2, self.min_width)
        
        # 计算总高度（文本高度 + 内边距 + 箭头高度）
        bubble_height = text_height + self.padding + self.arrow_height
        
        self.resize(bubble_width, bubble_height)
    
    def set_text(self, text):
        """设置文本并重新计算大小"""
        self.text = text
        self._calculate_size()
        self.update()
    
    def get_current_text(self):
        """获取当前显示的文本"""
        return self.text
        
    def paintEvent(self, event):
        """绘制气泡样式"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        bubble_height = height - self.arrow_height
        
        # 绘制气泡背景
        painter.setBrush(QColor(225, 245, 254, 230))  # 浅蓝色半透明
        painter.setPen(QColor(179, 229, 252))
        painter.drawRoundedRect(5, 5, width - 10, bubble_height - 10, 10, 10)
        
        # 绘制指向箭头
        painter.setBrush(QColor(225, 245, 254, 230))
        painter.setPen(QColor(179, 229, 252))
        arrow_center = width // 2
        arrow_points = [
            QPoint(arrow_center - 8, bubble_height - 5),
            QPoint(arrow_center + 8, bubble_height - 5),
            QPoint(arrow_center, height - 5)
        ]
        painter.drawPolygon(arrow_points)
        
        # 绘制文字
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(self.font)
        text_rect = painter.boundingRect(
            self.padding // 2, self.padding // 2,
            width - self.padding, bubble_height - self.padding,
            Qt.AlignLeft | Qt.TextWordWrap, self.text
        )
        painter.drawText(text_rect, Qt.AlignLeft | Qt.TextWordWrap, self.text)
        
    def update_position(self):
        """更新位置（跟随宠物）"""
        if self.parent_pet and self.isVisible():
            # 确保使用正确的几何信息
            pet_geometry = self.parent_pet.frameGeometry()
            bubble_width = self.width()
            bubble_height = self.height()
            
            x = pet_geometry.x() + (pet_geometry.width() - bubble_width) // 2
            y = pet_geometry.y() - bubble_height - 20
            
            self.move(x, y)
            
    def showEvent(self, event):
        """显示事件 - 确保窗口显示时位置正确"""
        super().showEvent(event)
        # 立即更新位置
        self.update_position()