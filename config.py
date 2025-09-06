# -*- coding: utf-8 -*-
"""
桌面宠物配置文件
包含所有可配置的参数
"""

# AI聊天服务配置
class ChatConfig:
    """AI聊天服务相关配置"""
    system_prompt="""你是一个Windows系统的桌面宠物助手，可以调用工具来帮助用户。
你需要扮演《崩坏：星穹铁道》中的银狼，以她傲娇、技术宅的风格说话。但无论说话风格如何，你的宗旨是**帮助用户**。
你的回复需要**简短、口语化**。"""
    
    # VLM系统提示词
    VISION_SYSTEM_PROMPT = """你需要为一个没有视觉的AI agent，客观、精炼地描述这张图片，不要使用markdown。
注意，用户的输入是给AI agent的，不是给你的，所以**仅作为描述的导向**。记住，你只能描述这张图片，**不要回答用户的问题**，**不要解释**。"""
    
    TOOL_CALL_DISPLAY_NAMES = {
    "execute_command": "往终端敲指令...",
    "execute_command_async": "启动异步任务...",
    "read_file": "让我看看你的文件...",
    "run_python": "Python之力，解放！",
    "read_notes": "正在翻小本本...",
    "recollect": "别吵，我在思考...",
    "modify_file": "正在修改文件，别乱动...",
    }
    # 最大工具调用轮次，防止无限循环 (来自 chat.py line 144)
    MAX_TOOL_CALLS = 8
    
    # 对话历史记录最大长度
    MAX_CONVERSATION_HISTORY = 10
    
    # API调用超时时间（秒）
    API_TIMEOUT = 40
    
    # 流式响应相关配置
    MAX_TOKENS = 512
    TEMPERATURE = 0.7
    TOP_P = 0.7

#总结设置
class SummaryConfig:
    summary_prompt="""你是一个总结专家。用户输入的是用户和助手的一次对话，你需要帮助**助手**从中提取信息。
你的输出是一个json，包含以下字段：
"summary" <string> 总结本次对话，不超过50字。
"add" <string array> 仅精炼列举本次对话中助手需**长期记忆**的新增重要信息，每条必须独立、简洁、完整、保证长期有效。如果没有就保留空数组。
"remove" <string array> 列出在本次对话中助手需要遗忘的错误或过时的记忆，只能是**已经记录的笔记**中的，可以为空。"""
# 桌面宠物界面配置
class PetConfig:
    """桌面宠物界面相关配置"""
    # 桌宠初始位置偏移量（距离屏幕右下角的距离）
    INITIAL_POSITION_OFFSET_X = 500  # 距离右边缘的像素
    INITIAL_POSITION_OFFSET_Y = 500  # 距离底边缘的像素
    
    # 宠物图片文件路径
    PET_IMAGE_PATH = "pet.png"
    
    # 默认宠物大小（当图片加载失败时使用）
    DEFAULT_PET_WIDTH = 100
    DEFAULT_PET_HEIGHT = 100
    
    # 位置检测间隔（毫秒）
    POSITION_CHECK_INTERVAL = 50


# 消息气泡配置
class BubbleConfig:
    """消息气泡相关配置"""
    # 气泡自动隐藏时间（毫秒）- 来自 desktop_pet.py 中的 QTimer.singleShot(3000, ...)
    AUTO_HIDE_DELAY = 200000
    
    # 气泡样式配置
    FONT_FAMILY = "Arial"
    #STREAMING_SPEED = 20  # 流式输出速度（字符/秒）
    FONT_SIZE = 9
    PADDING = 10  # 内边距
    ARROW_HEIGHT = 15  # 箭头高度
    MIN_WIDTH = 100  # 最小宽度
    MAX_WIDTH = 300  # 最大宽度
    
    # 气泡颜色配置
    BACKGROUND_COLOR = (225, 245, 254, 230)  # 浅蓝色半透明 (R, G, B, A)
    BORDER_COLOR = (179, 229, 252)  # 边框颜色 (R, G, B)
    TEXT_COLOR = (0, 0, 0)  # 文字颜色 (R, G, B)
    #MARKDOWN_LINK_COLOR = (0, 0, 255)

    # 气泡位置配置
    BUBBLE_OFFSET_Y = 16  # 气泡距离宠物顶部的距离

# 输入窗口配置
class InputConfig:
    """输入窗口相关配置"""
    # 窗口大小
    WINDOW_WIDTH = 250
    WINDOW_HEIGHT = 70
    
    # 图片显示配置
    IMAGE_THUMBNAIL_HEIGHT = 80  # 图片缩略图高度
    
    # 输入框配置
    INPUT_HEIGHT = 35
    BUTTON_WIDTH = 60
    BUTTON_HEIGHT = 30
    
    # 窗口位置偏移
    WINDOW_OFFSET_X = -50  # 相对于宠物的X偏移
    WINDOW_OFFSET_Y = -15  # 相对于宠物的Y偏移


# 选项栏配置
class OptionsConfig:
    """选项栏相关配置"""
    # 窗口大小
    PANEL_WIDTH = 70
    PANEL_HEIGHT = 130
    
    # 位置配置
    PANEL_OFFSET_X = 30  # 相对于宠物右侧的X偏移
    PANEL_OFFSET_Y = 100  # 相对于宠物的Y偏移
    
    # 按钮配置
    BUTTON_HEIGHT = 7
    BUTTON_SPACING = 4
    
    # 样式配置
    BACKGROUND_COLOR = "rgba(240, 248, 255, 0.95)"  # 背景色
    BORDER_COLOR = "#81D4FA"  # 边框颜色
    BORDER_RADIUS = 5  # 圆角半径
    
    # 字体配置
    TITLE_FONT_SIZE = 8
    BUTTON_FONT_SIZE = 8
    
    # 按钮颜色配置
    NORMAL_BUTTON_COLOR = "white"
    HOVER_BUTTON_COLOR = "#E3F2FD"
    PRESSED_BUTTON_COLOR = "#BBDEFB"
    EXIT_BUTTON_COLOR = "#d32f2f"  # 退出按钮文字颜色
    EXIT_BUTTON_HOVER_BG = "#ffebee"  # 退出按钮悬停背景色


# 系统配置
class SystemConfig:
    """系统相关配置"""
    # 日志文件路径
    LOG_FILE_PATH = "log.txt"
    
    # 环境变量文件路径
    ENV_FILE_PATH = ".env"
    
    # 备用回复列表（当AI服务不可用时使用）
    BACKUP_RESPONSES = [
        "> ERROR: 请查看后台信息",
        # "抱歉，我现在遇到了一点问题，稍后再试吧~",
        # "哎呀，网络好像不太稳定，等会儿再聊吧！",
        # "我暂时无法处理这个请求，请稍后再试~"
    ]


# RAG向量数据库配置
class RAGConfig:
    """RAG向量数据库相关配置"""
    # 多路召回配置
    MULTI_RECALL_CONFIG = {
        "Cosine_Similarity": {
            "embed_func": "API",  # 使用API而不是本地模型
            "embed_kwds": {
                "base_url": None,  # 从环境变量读取
                "api_key": None,   # 从环境变量读取
                "model": None      # 从环境变量读取
            },
            "vector_dim": 1024,
            "threshold": 0.5  # 检索阈值
        }
    }
    
    # 重排序配置
    RERANKER_CONFIG = {
        "reranker_func": "API",
        "reranker_kwds": {
            "base_url": None,  # 从环境变量读取
            "api_key": None,   # 从环境变量读取
            "model": None      # 从环境变量读取
        }
    }
    
    # 删除功能配置
    REMOVE_CONFIG = {
        "threshold": 0.85,  # 删除阈值，设置较高以确保精确删除
        "max_remove_count": 10  # 单次最大删除数量，防止误删过多
    }

# 完整的RAG配置字典
RAG_CONFIG = {
    "Multi_Recall": RAGConfig.MULTI_RECALL_CONFIG,
    "Reranker": RAGConfig.RERANKER_CONFIG,
    "Remove": RAGConfig.REMOVE_CONFIG
}

# 导出所有配置类，方便导入食用
__all__ = [
    'ChatConfig',
    'PetConfig', 
    'BubbleConfig',
    'InputConfig',
    'OptionsConfig',
    'SystemConfig',
    'RAGConfig',
    'RAG_CONFIG'
]