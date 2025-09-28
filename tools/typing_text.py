import time
import pyautogui
import pyperclip
from typing import Dict, Any, List, Union
import win32gui
import win32con
import win32api
# 工具定义
tool_definition = {
    "type": "function",
    "function": {
        "name": "typing_text",
        "description": "在用户激活的文本输入框输入文本，常用于发送消息",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "要输入的一段或多段文本内容"
                },
                "press_enter": {
                    "type": "boolean",
                    "description": "全部输入完成后是否按回车键",
                    "default": True
                }
            },
            "required": ["text"]
        }
    }
}

def typing_text(text: Union[List[str], str], press_enter: bool = True) -> Dict[str, Any]:
    """
    模拟键盘输入文本段落
    
    Args:
        text: 要输入的一段或多段文本内容
        press_enter: 最后一段输入完成后是否按回车键，默认为True
        
    Returns:
        包含执行结果和状态的字典，符合MCP工具调用返回格式
    """
    try:
        # 统一处理输入参数
        if isinstance(text, str):
            text = [text]
        
        # 解析文本段，按换行符分割
        paragraphs = []
        for paragraph in text:
            # 按换行符分割，并过滤空行
            lines = [line.strip() for line in paragraph.split('\n') if line.strip()]
            paragraphs.extend(lines)
        
        if not paragraphs:
            return {
                "content": [{
                    "type": "text", 
                    "text": "❌ 没有有效的文本内容可输入"
                }]
            }
        
        # 确保pyautogui安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05  # 设置默认间隔
        
        # 输入前的延迟，确保用户有时间切换到目标窗口
        # time.sleep(0.5)
        
        # 记录开始时间
        start_time = time.time()
        total_chars = 0
        method_used = ""
         # 获取当前焦点窗口
        hwnd = win32gui.GetForegroundWindow()
        # 依次输入每个段落
        for i, paragraph in enumerate(paragraphs):
            total_chars += len(paragraph)
            
            # 判断是否是最后一段
            is_last_paragraph = (i == len(paragraphs) - 1)
            
            # 输入当前段落
            try:
                for char in paragraph:
                    win32api.SendMessage(hwnd, win32con.WM_CHAR, ord(char), 0)
                    time.sleep(0.05)
                if not method_used:
                    method_used = "pyautogui.typewrite"
                    
            except Exception as e:
                # 回退到剪贴板方案
                try:
                    pyperclip.copy(paragraph)
                    pyautogui.hotkey('ctrl', 'v')
                    if not method_used:
                        method_used = "clipboard (ctrl+v)"
                        
                except Exception as e2:
                    # 回退到逐个字符输入
                    try:
                        for char in paragraph:
                            pyautogui.press(char)
                            time.sleep(0.05)
                        if not method_used:
                            method_used = "pyautogui.press (character by character)"
                            
                    except Exception as e3:
                        return {
                            "content": [{
                                "type": "text", 
                                "text": f"❌ 第{i+1}段输入失败:\n- 方法1错误: {str(e)}\n- 方法2错误: {str(e2)}\n- 方法3错误: {str(e3)}"
                            }]
                        }
            
            # 段落间的换行处理
            if not is_last_paragraph:
                # 不是最后一段，总是换行
                pyautogui.press('enter')
                time.sleep(0.1)
            elif press_enter:
                # 是最后一段且要求按回车
                pyautogui.press('enter')
                time.sleep(0.1)
        
        # 计算执行时间
        execution_time = time.time() - start_time
        
        # 构建成功响应
        result_text = f"✅ 文本输入完成\n\n"
        # result_text += f"输入段落数: {len(paragraphs)} 段\n"
        # result_text += f"总字符数: {total_chars} 个字符\n"
        # result_text += f"使用的方法: {method_used}\n"
        # result_text += f"最后一段是否回车: {'是' if press_enter else '否'}\n"
        # result_text += f"执行时间: {execution_time:.2f} 秒\n"
        # result_text += f"输入速度: {total_chars/execution_time:.1f} 字符/秒\n\n"
        
        ## 显示段落预览
        # result_text += "段落预览:\n"
        # for i, paragraph in enumerate(paragraphs):
        #     preview = paragraph[:50] + "..." if len(paragraph) > 50 else paragraph
        #     result_text += f"{i+1}. {preview}\n"
        
        return {
            "content": [{
                "type": "text", 
                "text": result_text
            }]
        }
        
    except Exception as e:
        # 返回MCP标准格式的错误响应
        return {
            "content": [{
                "type": "text", 
                "text": f"❌ 文本输入过程中发生错误: {str(e)}"
            }]
        }

# 标记为工具函数
typing_text.is_tool = True
typing_text.tool_definition = tool_definition