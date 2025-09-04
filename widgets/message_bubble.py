from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics
from config import BubbleConfig

class MessageBubble(QWidget):
    """消息气泡窗口"""
    def __init__(self, parent_pet):
        super().__init__()
        self.parent_pet = parent_pet
        self.text = ""
        self.font = QFont(BubbleConfig.FONT_FAMILY, BubbleConfig.FONT_SIZE)
        self.padding = BubbleConfig.PADDING  # 内边距
        self.arrow_height = BubbleConfig.ARROW_HEIGHT  # 箭头高度
        self.min_width = BubbleConfig.MIN_WIDTH  # 最小宽度
        self.max_width = BubbleConfig.MAX_WIDTH  # 最大宽度
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._calculate_size()
        
    def _wrap_text(self, text, max_width):
        """改进的文本换行算法，支持中英文混合和长单词"""
        font_metrics = QFontMetrics(self.font)
        lines = []
        current_line = ""
        
        # 按字符处理，更适合中英文混合文本
        for char in text:
            test_line = current_line + char
            test_width = font_metrics.horizontalAdvance(test_line)
            
            # 如果当前字符是换行符，直接换行
            if char == '\n':
                lines.append(current_line)
                current_line = ""
                continue
                
            # 检查添加字符后是否超出宽度
            if test_width <= max_width:
                current_line = test_line
            else:
                # 超出宽度时换行
                if current_line:  # 当前行有内容
                    lines.append(current_line)
                
                # 处理长字符或长单词（如果单个字符就超过宽度，强制显示）
                if font_metrics.horizontalAdvance(char) > max_width:
                    # 单个字符就超过宽度，特殊处理
                    lines.append(char)
                    current_line = ""
                else:
                    current_line = char
        
        # 添加最后一行
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _calculate_size(self):
        """根据文本内容计算窗口大小"""
        if not self.text:
            self.resize(self.min_width, 50)
            return
            
        # 使用字体度量计算文本尺寸
        font_metrics = QFontMetrics(self.font)
        
        # 计算可用文本宽度（减去两倍内边距）
        available_width = self.max_width - 2 * self.padding
        
        # 使用改进的换行算法
        wrapped_lines = self._wrap_text(self.text, available_width)
        
        # 计算最大行宽度
        max_line_width = 0
        for line in wrapped_lines:
            line_width = font_metrics.horizontalAdvance(line)
            max_line_width = max(max_line_width, line_width)
        
        # 计算文本总高度
        text_height = len(wrapped_lines) * font_metrics.height()
        
        # 计算气泡宽度（文本最大宽度 + 两倍内边距，但不超过最大宽度）
        bubble_width = min(max_line_width + 2 * self.padding, self.max_width)
        bubble_width = max(bubble_width, self.min_width)  # 确保不小于最小宽度
        
        # 计算总高度（文本高度 + 两倍内边距 + 箭头高度）
        bubble_height = text_height + 2 * self.padding + self.arrow_height
        
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
        painter.setBrush(QColor(*BubbleConfig.BACKGROUND_COLOR))
        painter.setPen(QColor(*BubbleConfig.BORDER_COLOR))
        painter.drawRoundedRect(0, 0, width, bubble_height, 10, 10)
        
        # 绘制指向箭头
        painter.setBrush(QColor(*BubbleConfig.BACKGROUND_COLOR))
        painter.setPen(QColor(*BubbleConfig.BORDER_COLOR))
        arrow_center = width // 2
        arrow_points = [
            QPoint(arrow_center - 8, bubble_height),
            QPoint(arrow_center + 8, bubble_height),
            QPoint(arrow_center, height)
        ]
        painter.drawPolygon(arrow_points)
        
        # 绘制文字
        painter.setPen(QColor(*BubbleConfig.TEXT_COLOR))
        painter.setFont(self.font)
        
        # 使用改进的换行算法
        available_width = width - 2 * self.padding
        wrapped_lines = self._wrap_text(self.text, available_width)
        
        font_metrics = QFontMetrics(self.font)
        line_height = font_metrics.height()
        y_offset = self.padding + font_metrics.ascent()  # 从顶部内边距开始，加上字体的上升部分
        
        for line in wrapped_lines:
            # 修改：从左到右绘制文本，不再居中
            x_offset = self.padding  # 使用固定的左边距
            
            painter.drawText(x_offset, y_offset, line)
            y_offset += line_height
        
    def update_position(self):
        """更新位置（跟随宠物）"""
        if self.parent_pet and self.isVisible():
            # 确保使用正确的几何信息
            pet_geometry = self.parent_pet.frameGeometry()
            bubble_width = self.width()
            bubble_height = self.height()
            
            x = pet_geometry.x() + (pet_geometry.width() - bubble_width) // 2
            y = pet_geometry.y() - bubble_height - BubbleConfig.BUBBLE_OFFSET_Y
            
            self.move(x, y)
            
    def showEvent(self, event):
        """显示事件 - 确保窗口显示时位置正确"""
        super().showEvent(event)
        # 立即更新位置
        self.update_position()