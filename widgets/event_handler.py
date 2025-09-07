"""
事件处理模块
处理鼠标事件、窗口管理和位置更新
"""
from PyQt5.QtCore import Qt, QPoint, QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from config import PetConfig


class EventHandler(QObject):
    """事件处理器"""
    right_click_detected = pyqtSignal()
    position_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.drag_position = QPoint()
        self.is_dragging = False
        self.last_position = QPoint()
        
        # 防抖机制
        self.right_click_timer = QTimer()
        self.right_click_timer.setSingleShot(True)
        self.right_click_timer.timeout.connect(self.right_click_detected.emit)
        self.debounce_delay = 200  # 200ms防抖延迟
        
        # 定时器用于检测位置变化
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self._check_position_change)
        self.move_timer.start(PetConfig.POSITION_CHECK_INTERVAL)
        
    def handle_mouse_press(self, event: QMouseEvent):
        """处理鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent_widget.frameGeometry().topLeft()
            self.is_dragging = True
            event.accept()
        elif event.button() == Qt.RightButton:
            # 使用防抖机制处理右键点击
            self.right_click_timer.start(self.debounce_delay)
            event.accept()
            
    def handle_mouse_move(self, event: QMouseEvent):
        """处理鼠标移动事件（拖拽）"""
        if event.buttons() == Qt.LeftButton and not self.drag_position.isNull():
            self.parent_widget.move(event.globalPos() - self.drag_position)
            # 实时更新跟随窗口位置
            self.position_changed.emit()
            event.accept()
            
    def handle_mouse_release(self, event: QMouseEvent):
        """处理鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.last_position = self.parent_widget.pos()
            event.accept()
            
    def _check_position_change(self):
        """检查位置变化并发出信号"""
        if not self.is_dragging and self.parent_widget:
            current_pos = self.parent_widget.pos()
            if current_pos != self.last_position:
                self.position_changed.emit()
                self.last_position = current_pos
                
    def update_last_position(self):
        """更新最后位置"""
        if self.parent_widget:
            self.last_position = self.parent_widget.pos()
            
    def stop_timers(self):
        """停止所有定时器"""
        if self.move_timer:
            self.move_timer.stop()
        if self.right_click_timer:
            self.right_click_timer.stop()