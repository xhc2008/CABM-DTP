import sys
from PyQt5.QtWidgets import QApplication
from widgets.desktop_pet import DesktopPet

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("桌面宠物")
    app.setApplicationVersion("0.1")
    
    pet = DesktopPet()
    pet.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()