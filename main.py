import sys
import os
import signal
import zipfile
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from widgets.desktop_pet import DesktopPet

# Windows 控制台标题设置
if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleTitleW("CABM-DTP")

def check_if_in_archive():
    """检查程序是否在压缩包中运行"""
    try:
        # 获取当前执行文件的路径
        current_path = os.path.abspath(__file__)
        
        # 检查路径中是否包含压缩包特征
        # Python在压缩包中运行时，路径会包含.zip等
        if '.zip' in current_path.lower() or '.rar' in current_path.lower() or '.7z' in current_path.lower():
            return True
        
        # 检查是否可以正常写入文件（压缩包中通常无法写入）
        test_file = Path('.') / '.write_test'
        try:
            test_file.write_text('test')
            test_file.unlink()
            return False
        except (PermissionError, OSError):
            return True
            
    except Exception:
        return False

def check_and_create_env():
    """检查.env文件是否存在，如果不存在则引导用户创建"""
    env_path = Path('.env')
    
    if env_path.exists():
        return True
    
    print("\n" + "="*60)
    print("未检测到 .env 配置文件")
    print("="*60)
    print("首次运行需要配置 API 密钥")
    print("\n> 如何获取？")
    print("1. 使用浏览器打开https://cloud.siliconflow.cn/i/mVqMyTZk")
    print("2. 注册账号")
    print("3. 左下方有一个“API密钥”，点击它")
    print("4. 上方有一个“新建API密钥”，点击它")
    print("5. 点击“新建密钥”")
    print("6. 点击密钥进行复制，粘贴到这里")
    # 读取示例文件作为参考
    example_path = Path('.env.example')
    defaults = {}
    if example_path.exists():
        with open(example_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    defaults[key.strip()] = value.strip()
    
    # 收集用户输入
    config = {}
    
    # API密钥（必填）
    while True:
        api_key = input("请输入 API 密钥: ").strip()
        if api_key:
            # 检查是否以 sk- 开头
            if not api_key.startswith('sk-'):
                print("⚠️警告：硅基流动的API密钥通常以'sk-'开头")
                confirm = input("是否继续使用此密钥？(Y/N): ").strip().upper()
                if confirm != 'Y':
                    print("请重新输入的 API 密钥")
                    continue
            config['API_KEY'] = api_key
            break
        print("❌ API密钥不能为空，请重新输入")
    
    # 其他配置项直接使用默认值
    config['BASE_URL'] = defaults.get('BASE_URL', 'https://api.siliconflow.cn/v1')
    config['AGENT_MODEL'] = defaults.get('AGENT_MODEL', 'deepseek-ai/DeepSeek-V3')
    config['SUMMURY_MODEL'] = defaults.get('SUMMURY_MODEL', 'Qwen/Qwen3-8B')
    config['VISION_MODEL'] = defaults.get('VISION_MODEL', 'Qwen/Qwen2.5-VL-32B-Instruct')
    config['EMBEDDING_MODEL'] = defaults.get('EMBEDDING_MODEL', 'BAAI/bge-large-zh-v1.5')
    config['RERANKER_MODEL'] = defaults.get('RERANKER_MODEL', 'netease-youdao/bce-reranker-base_v1')
    
    # 写入.env文件
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")
        print("\n✅ .env 文件创建成功！")
        return True
    except Exception as e:
        print(f"\n❌ 创建 .env 文件失败: {e}")
        return False

def signal_handler(signum, frame):
    """处理系统信号，确保优雅退出"""
    print(f"接收到信号 {signum}，正在退出...")
    QApplication.instance().quit()

def initialize_rag_system():
    """初始化RAG系统"""
    try:
        print("正在初始化RAG系统：我知道你很急，但你先别急...")
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
        # 检查是否在压缩包中运行
        if check_if_in_archive():
            print("\n" + "="*60)
            print("❌ 错误：程序正在压缩包中运行")
            print("="*60)
            print("\n请先解压缩到本地文件夹，然后再运行程序。")
            print("压缩包中的程序无法正常创建和修改文件。\n")
            input("按回车键退出...")
            sys.exit(1)
        
        # 检查并创建.env文件
        if not check_and_create_env():
            print("\n配置文件创建失败，程序无法继续运行")
            input("按回车键退出...")
            sys.exit(1)
        
        # 先初始化RAG系统（在创建QApplication之前）
        print("\n开始启动桌面宠物...")
        if not initialize_rag_system():
            print("RAG系统初始化失败，程序退出")
            sys.exit(1)
        
        app = QApplication(sys.argv)
        
        # 设置应用程序属性
        app.setApplicationName("桌面宠物")
        app.setApplicationVersion("1.1")
        
        # 设置应用程序在最后一个窗口关闭时不退出（支持系统托盘）
        app.setQuitOnLastWindowClosed(False)
        
        # 设置信号处理器（仅在非Windows系统上）
        import os
        if os.name != 'nt':  # 非Windows系统
            print("⚠警告：非Windows系统下可能无法正常使用")
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