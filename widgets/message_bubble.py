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
        """智能文本换行，支持强制换行长单词"""
        font_metrics = QFontMetrics(self.font)
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # 检查单个单词是否过长
            word_width = font_metrics.horizontalAdvance(word)
            if word_width > max_width:
                # 如果当前行不为空，先添加到结果中
                if current_line:
                    lines.append(current_line.strip())
                    current_line = ""
                
                # 强制拆分长单词
                char_index = 0
                while char_index < len(word):
                    temp_word = ""
                    while char_index < len(word):
                        next_char = word[char_index]
                        test_word = temp_word + next_char
                        if font_metrics.horizontalAdvance(test_word) > max_width and temp_word:
                            break
                        temp_word = test_word
                        char_index += 1
                    
                    if temp_word:
                        lines.append(temp_word)
                continue
            
            # 检查添加这个单词后是否会超出宽度
            test_line = current_line + (" " if current_line else "") + word
            if font_metrics.horizontalAdvance(test_line) > max_width and current_line:
                lines.append(current_line.strip())
                current_line = word
            else:
                current_line = test_line
        
        # 添加最后一行
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
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
            # 使用智能换行计算高度
            max_text_width = self.max_width - self.padding * 2
            wrapped_lines = self._wrap_text(self.text, max_text_width)
            text_height = len(wrapped_lines) * font_metrics.height()
            bubble_width = self.max_width
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
        painter.setBrush(QColor(*BubbleConfig.BACKGROUND_COLOR))
        painter.setPen(QColor(*BubbleConfig.BORDER_COLOR))
        painter.drawRoundedRect(5, 5, width - 10, bubble_height - 10, 10, 10)
        
        # 绘制指向箭头
        painter.setBrush(QColor(*BubbleConfig.BACKGROUND_COLOR))
        painter.setPen(QColor(*BubbleConfig.BORDER_COLOR))
        arrow_center = width // 2
        arrow_points = [
            QPoint(arrow_center - 8, bubble_height - 5),
            QPoint(arrow_center + 8, bubble_height - 5),
            QPoint(arrow_center, height - 5)
        ]
        painter.drawPolygon(arrow_points)
        
        # 绘制文字
        painter.setPen(QColor(*BubbleConfig.TEXT_COLOR))
        painter.setFont(self.font)
        
        # 使用智能换行绘制文本
        max_text_width = width - self.padding
        wrapped_lines = self._wrap_text(self.text, max_text_width)
        
        font_metrics = QFontMetrics(self.font)
        line_height = font_metrics.height()
        y_offset = self.padding // 2
        
        for line in wrapped_lines:
            painter.drawText(
                self.padding // 2, y_offset + line_height,
                line
            )
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