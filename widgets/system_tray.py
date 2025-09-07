"""
系统托盘模块
处理系统托盘图标、菜单和相关功能
"""
import os
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from config import PetConfig


class SystemTrayManager(QObject):
    """系统托盘管理器"""
    show_requested = pyqtSignal()
    exit_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.tray_icon = None
        self.init_system_tray()
        
    def init_system_tray(self):
        """初始化系统托盘"""
        # 检查系统是否支持托盘
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("系统不支持托盘功能")
            return
            
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self.parent_widget)
        
        # 设置托盘图标
        self._set_tray_icon()
        
        # 设置托盘提示
        self.tray_icon.setToolTip("Silver Wolf")
        
        # 创建托盘菜单
        self._create_tray_menu()
        
        # 双击托盘图标显示窗口
        self.tray_icon.activated.connect(self._tray_icon_activated)
        
    def _set_tray_icon(self):
        """设置托盘图标"""
        try:
            if os.path.exists(PetConfig.PET_IMAGE_PATH):
                icon = QIcon(PetConfig.PET_IMAGE_PATH)
            else:
                # 如果宠物图片不存在，创建一个简单的默认图标
                pixmap = QPixmap(32, 32)
                pixmap.fill(Qt.blue)
                icon = QIcon(pixmap)
            self.tray_icon.setIcon(icon)
        except Exception as e:
            print(f"设置托盘图标失败: {e}")
            # 使用系统默认图标
            if self.parent_widget:
                self.tray_icon.setIcon(
                    self.parent_widget.style().standardIcon(
                        self.parent_widget.style().SP_ComputerIcon
                    )
                )
        
    def _create_tray_menu(self):
        """创建托盘菜单"""
        tray_menu = QMenu()
        
        # 显示动作
        show_action = QAction("显示", self.parent_widget)
        show_action.triggered.connect(self.show_requested.emit)
        tray_menu.addAction(show_action)
        
        # 分隔符
        tray_menu.addSeparator()
        
        # 退出动作
        quit_action = QAction("退出", self.parent_widget)
        quit_action.triggered.connect(self.exit_requested.emit)
        tray_menu.addAction(quit_action)
        
        # 设置托盘菜单
        self.tray_icon.setContextMenu(tray_menu)
        
    def _tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_requested.emit()
            
    def show_tray_icon(self):
        """显示托盘图标"""
        if self.tray_icon:
            self.tray_icon.show()
            
    def hide_tray_icon(self):
        """隐藏托盘图标"""
        if self.tray_icon:
            self.tray_icon.hide()
            
    def show_message(self, title, message, icon=QSystemTrayIcon.Information, timeout=3000):
        """显示托盘消息"""
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, icon, timeout)
            
    def is_available(self):
        """检查系统托盘是否可用"""
        return QSystemTrayIcon.isSystemTrayAvailable()