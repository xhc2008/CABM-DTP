# -*- coding: utf-8 -*-
"""
截图捕获服务
继承自ScreenshotSelector，用于桌面宠物的截图功能
"""

from PyQt5.QtCore import pyqtSignal, QTimer
from services.ScreenshotSelector import ScreenshotSelector

class ScreenshotCapture(ScreenshotSelector):
    """截图捕获类，继承自ScreenshotSelector"""
    
    # 截图完成信号
    screenshot_captured = pyqtSignal(object)  # 传递QPixmap对象
    
    def __init__(self, parent=None):
        super().__init__()
        self.parent_widget = parent
        
    def on_screenshot_captured(self, pixmap):
        """处理截图完成事件"""
        try:
            print("发射截图完成信号...")
            # 发射信号，传递截图数据
            self.screenshot_captured.emit(pixmap)
            print("信号发射完成")
        except Exception as e:
            print(f"截图信号发射失败: {e}")
        
    def closeEvent(self, event):
        """重写关闭事件，确保不影响主程序"""
        print("截图选择器关闭事件")
        # 断开所有信号连接
        try:
            self.screenshot_captured.disconnect()
        except:
            pass
        event.accept()