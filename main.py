import sys
import signal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from widgets.desktop_pet import DesktopPet

def signal_handler(signum, frame):
    """处理系统信号，确保优雅退出"""
    print(f"接收到信号 {signum}，正在退出...")
    QApplication.instance().quit()

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("桌面宠物")
    app.setApplicationVersion("0.1")
    
    # 设置信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建定时器来处理Python信号（PyQt需要这样做）
    timer = QTimer()
    timer.start(500)  # 每500ms检查一次信号
    timer.timeout.connect(lambda: None)  # 空操作，只是为了让Python信号能被处理
    
    pet = DesktopPet()
    pet.show()
    
    # 确保应用程序完全退出
    try:
        sys.exit(app.exec_())
    except SystemExit:
        pass

if __name__ == "__main__":
    main()