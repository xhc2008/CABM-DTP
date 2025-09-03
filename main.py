import sys
import signal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from widgets.desktop_pet import DesktopPet

def signal_handler(signum, frame):
    """处理系统信号，确保优雅退出"""
    print(f"接收到信号 {signum}，正在退出...")
    QApplication.instance().quit()

def initialize_rag_system():
    """初始化RAG系统"""
    try:
        print("正在初始化RAG系统：这会有点慢，不要着急...")
        from services.context_builder import get_context_builder
        context_builder = get_context_builder()
        print("RAG系统初始化完成")
        return True
    except Exception as e:
        print(f"RAG系统初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    try:
        # 先初始化RAG系统（在创建QApplication之前）
        print("开始启动桌面宠物...")
        if not initialize_rag_system():
            print("RAG系统初始化失败，程序退出")
            sys.exit(1)
        
        app = QApplication(sys.argv)
        
        # 设置应用程序属性
        app.setApplicationName("桌面宠物")
        app.setApplicationVersion("0.1")
        
        # 设置信号处理器（仅在非Windows系统上）
        import os
        if os.name != 'nt':  # 非Windows系统
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        
        # 创建定时器来处理Python信号（PyQt需要这样做）
        timer = QTimer()
        timer.start(500)  # 每500ms检查一次信号
        timer.timeout.connect(lambda: None)  # 空操作，只是为了让Python信号能被处理
        
        print("正在创建桌面宠物...")
        pet = DesktopPet()
        pet.show()
        
        print("桌面宠物启动成功")
        
        # 确保应用程序完全退出
        try:
            sys.exit(app.exec_())
        except SystemExit:
            pass
            
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()