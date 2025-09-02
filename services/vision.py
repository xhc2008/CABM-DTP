# -*- coding: utf-8 -*-
"""
视觉模型服务
用于处理图片并生成描述
"""

import os
import base64
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QBuffer, QIODevice
from config import ChatConfig

class VisionService:
    """视觉模型服务类"""
    
    def __init__(self):
        # 从环境变量读取配置
        self.base_url = os.getenv('BASE_URL', 'https://api.siliconflow.cn/v1')
        self.api_key = os.getenv('API_KEY')
        self.vision_model = os.getenv('VISION_MODEL', '')
        
        if not self.api_key:
            raise ValueError("API_KEY not found in environment variables")
    
    def pixmap_to_base64(self, pixmap):
        """将QPixmap转换为base64编码的字符串"""
        from PyQt5.QtCore import QBuffer, QIODevice
        
        # 创建QBuffer来保存图片数据
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        
        # 保存pixmap到buffer
        pixmap.save(buffer, "PNG")
        
        # 获取字节数据并转换为base64
        image_data = buffer.data()
        buffer.close()
        
        return base64.b64encode(image_data).decode('utf-8')
    
    def describe_image(self, pixmap, user_input=""):
        """
        使用VLM描述图片
        
        Args:
            pixmap: QPixmap对象
            user_input: 用户输入文本，作为描述的导向
            
        Returns:
            str: 图片描述文本
        """
        try:
            print("开始VLM图片处理...")
            
            # 检查pixmap是否有效
            if not pixmap or pixmap.isNull():
                return "无效的图片"
            
            print(f"图片尺寸: {pixmap.width()}x{pixmap.height()}")
            
            # 将图片转换为base64
            print("转换图片为base64...")
            image_base64 = self.pixmap_to_base64(pixmap)
            print(f"Base64转换完成，长度: {len(image_base64)}")
            
            # 构建请求消息
            messages = [
                {
                    "role": "system",
                    "content": ChatConfig.VISION_SYSTEM_PROMPT
                },
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": user_input if user_input else "请描述这张图片"
                        }
                    ]
                }
            ]
            
            # 发送请求
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.vision_model,
                'messages': messages,
                'max_tokens': 500,
                'temperature': 0.3
            }
            
            print("发送VLM API请求...")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=ChatConfig.API_TIMEOUT
            )
            
            print(f"VLM API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                description = result['choices'][0]['message']['content'].strip()
                print(f"VLM描述: {description}")
                return description
            else:
                error_msg = f"VLM API错误: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                print(error_msg)
                return error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "VLM请求超时"
            print(error_msg)
            return error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"VLM网络错误: {str(e)}"
            print(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"VLM处理出错: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return error_msg