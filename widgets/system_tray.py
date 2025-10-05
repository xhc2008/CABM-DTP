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
    hide_requested = pyqtSignal()
    toggle_console_requested = pyqtSignal()
    exit_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.tray_icon = None
        self.tray_menu = None
        self.show_hide_action = None
        self.console_action = None
        self.is_pet_visible = True
        self.is_console_visible = True
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
        
        # 双击托盘图标切换显示/隐藏
        self.tray_icon.activated.connect(self._tray_icon_activated)
        
        # 始终显示托盘图标
        self.tray_icon.show()
        
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
        self.tray_menu = QMenu()
        
        # 显示/隐藏动作（根据当前状态动态变化）
        self.show_hide_action = QAction("隐藏", self.parent_widget)
        self.show_hide_action.triggered.connect(self._toggle_show_hide)
        self.tray_menu.addAction(self.show_hide_action)
        
        # 后台窗口显示/隐藏动作
        self.console_action = QAction("隐藏后台", self.parent_widget)
        self.console_action.triggered.connect(self._toggle_console)
        self.tray_menu.addAction(self.console_action)
        
        # 分隔符
        self.tray_menu.addSeparator()
        
        # 退出动作
        quit_action = QAction("退出", self.parent_widget)
        quit_action.triggered.connect(self.exit_requested.emit)
        self.tray_menu.addAction(quit_action)
        
        # 设置托盘菜单
        self.tray_icon.setContextMenu(self.tray_menu)
        
    def _toggle_show_hide(self):
        """切换显示/隐藏"""
        if self.is_pet_visible:
            self.hide_requested.emit()
        else:
            self.show_requested.emit()
    
    def _toggle_console(self):
        """切换后台窗口显示/隐藏"""
        self.toggle_console_requested.emit()
        
    def _tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self._toggle_show_hide()
            
    def update_menu_state(self, is_visible):
        """更新菜单状态"""
        self.is_pet_visible = is_visible
        if self.show_hide_action:
            self.show_hide_action.setText("隐藏" if is_visible else "显示")
    
    def update_console_menu_state(self, is_visible):
        """更新后台窗口菜单状态"""
        self.is_console_visible = is_visible
        if self.console_action:
            self.console_action.setText("隐藏后台" if is_visible else "显示后台")
            
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