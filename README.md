# CABM-DTP

> ## ⚠️ 本项目目前处于**开发阶段**，功能不完整，存在问题，且随缘更新

## 项目简介

CABM-DTP 是一个桌面宠物程序，它不仅可以作为桌面装饰，还能通过集成的大型语言模型和视觉模型与用户进行智能交互。在提供有趣的对话体验的同时，也可以通过MCP在电脑上完成一些简单的任务。

## 功能特点

- 🐾 **桌面宠物** - 可拖拽的桌面宠物形象
- 💬 **智能对话** - 集成 AI 聊天服务，支持连续对话
- 👁️ **视觉识别** - 支持图片上传和内容识别
- 📸 **屏幕截图** - 内置截图功能，可识别截图内容
- 🔧 **工具调用** - 预设多种工具，可以完成一些工作
- 🎯 **简洁界面** - 气泡式消息和浮动输入窗口
- ⚡ **流式响应** - AI 回复实时流式显示


## 安装方法
> 写的比较简单，看不懂可以问AI
### 1. 安装Python

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
去[硅基流动平台](https://cloud.siliconflow.cn/i/mVqMyTZk)申请API密钥

复制 `.env.example` 文件为 `.env`，并填写API配置：
```
API_KEY=【你的API密钥】
BASE_URL=https://api.siliconflow.cn/v1
MODEL=deepseek-ai/DeepSeek-V3
VISION_MODEL=Qwen/Qwen2.5-VL-32B-Instruct
……
```

### 4. 运行应用
双击`start.bat`启动。启动后可能会有几秒的延迟，不要重复启动

使用`start-debug.bat`启动可以不隐藏后台。建议首次启动时使用这个，确认没问题了再使用`start.bat`

## 使用方法

1. **左键拖拽**：移动宠物位置
2. **右键点击**：打开输入窗口和选项栏
3. **发送消息**：在输入窗口中输入文本
4. **截图功能**：进行区域截图并放进输入栏
5. **隐藏**：收进系统托盘栏

## 工具列表
- **read_file**: 读取文本或代码文件的内容
- **modify_file**: 修改文本或代码文件的内容
- **execute_command**: 在cmd中执行一条或多条指令，并等待执行完毕后获取输出
- **execute_command_async**: 在cmd中连续执行一条或多条指令，但不等待执行完成
- **run_python**: 创建一个Python程序并执行，等待执行完毕后获取输出
- **read_notes**: 从记录的笔记中检索相关信息
- **recollect**: 回忆以前的对话和事件
- **自定义工具**：按照相同的格式写好放入tools/即可

## 注意事项

- 需要有效的硅基流动 API 密钥才能使用 AI 功能
- 项目依赖 PyQt5，请确保系统支持 GUI 显示
- 由于AI生成的不确定性，某些工具可能会造成风险（例如删文件）
- 目前仅支持单宠物实例运行
- 本项目仅支持Windows。理论上也支持Windows以外的操作系统，但大概率不行

## 贡献
目前可能不太会接受Pull Requests

## 许可证

[GPL-3.0](LICENSE)

## CABM
> ### Code Afflatus & Beyond Matter

本项目是 CABM 系列的桌面宠物实现，与主 CABM 项目在功能上相互独立但共享相同的设计理念。

本项目的`CABM`也可以解释为：Chat & Assistant & Buddy & Mascot