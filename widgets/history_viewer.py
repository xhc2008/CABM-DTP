# -*- coding: utf-8 -*-
"""
历史记录查看器
支持懒加载和用户友好的显示
"""
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QLabel, 
                             QPushButton, QFrame, QHBoxLayout, QTextEdit, QToolButton)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor


class HistoryViewer(QWidget):
    """历史记录查看器窗口"""
    
    def __init__(self):
        super().__init__()
        self.history_file = "data/history.jsonl"
        self.all_records = []  # 所有历史记录
        self.displayed_count = 0  # 已显示的记录数
        self.batch_size = 20  # 每次加载的记录数
        self.loading = False  # 是否正在加载
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("历史记录")
        self.setWindowFlags(Qt.Window)
        self.resize(600, 700)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题
        title = QLabel("对话历史")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 内容容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)
        
        # 监听滚动事件
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)
        
        # 底部提示
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-size: 10pt;")
        main_layout.addWidget(self.status_label)
        
    def load_initial_records(self):
        """加载初始记录"""
        if not os.path.exists(self.history_file):
            self.status_label.setText("暂无历史记录")
            return
            
        try:
            # 读取所有记录（不倒序，保持原始顺序，最新的在文件末尾）
            with open(self.history_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 倒序读取，让最新的记录在列表开头
                self.all_records = [json.loads(line) for line in reversed(lines) if line.strip()]
            
            # 加载第一批
            self.load_more_records()
            
        except Exception as e:
            self.status_label.setText(f"加载失败: {str(e)}")
    
    def load_more_records(self):
        """加载更多记录"""
        if self.loading:
            return
            
        self.loading = True
        self.status_label.setText("加载中...")
        
        # 计算要加载的记录范围
        start = self.displayed_count
        end = min(start + self.batch_size, len(self.all_records))
        
        if start >= len(self.all_records):
            self.status_label.setText("已加载全部记录")
            self.loading = False
            return
        
        # 添加记录到界面
        for i in range(start, end):
            record = self.all_records[i]
            self.add_record_widget(record)
        
        self.displayed_count = end
        
        # 更新状态
        if self.displayed_count >= len(self.all_records):
            self.status_label.setText(f"已加载全部 {len(self.all_records)} 条记录")
        else:
            self.status_label.setText(f"已加载 {self.displayed_count}/{len(self.all_records)} 条，向下滚动加载更多")
        
        self.loading = False
    
    def add_record_widget(self, record):
        """添加单条记录到界面"""
        # 创建记录容器
        record_frame = QFrame()
        record_frame.setFrameShape(QFrame.StyledPanel)
        record_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        record_layout = QVBoxLayout(record_frame)
        record_layout.setSpacing(8)
        
        # 时间戳
        timestamp = record.get('timestamp', '')
        if timestamp:
            time_label = QLabel(f"🕐 {timestamp}")
            time_label.setStyleSheet("color: #666; font-size: 9pt;")
            record_layout.addWidget(time_label)
        
        # 用户输入
        if 'user_input' in record and record['user_input']:
            user_label = QLabel("你:")
            user_label.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 10pt;")
            record_layout.addWidget(user_label)
            
            user_text = QTextEdit()
            user_text.setPlainText(record['user_input'])
            user_text.setReadOnly(True)
            user_text.setMaximumHeight(100)
            user_text.setStyleSheet("""
                QTextEdit {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 5px;
                    font-size: 9pt;
                }
            """)
            record_layout.addWidget(user_text)
        
        # AI回复
        if 'ai_response' in record and record['ai_response']:
            ai_label = QLabel("银狼:")
            ai_label.setStyleSheet("color: #9c27b0; font-weight: bold; font-size: 10pt;")
            record_layout.addWidget(ai_label)
            
            ai_text = QTextEdit()
            ai_text.setPlainText(record['ai_response'])
            ai_text.setReadOnly(True)
            ai_text.setMaximumHeight(150)
            ai_text.setStyleSheet("""
                QTextEdit {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 5px;
                    font-size: 9pt;
                }
            """)
            record_layout.addWidget(ai_text)
        
        # 工具调用（可折叠）
        if 'tool_calls' in record and record['tool_calls']:
            tool_responses = record.get('tool_responses', [])
            
            # 工具调用标题
            tool_label = QLabel(f"🔧 工具调用 ({len(record['tool_calls'])}次):")
            tool_label.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 9pt;")
            record_layout.addWidget(tool_label)
            
            # 每个工具调用都可以下拉
            for i, tool_call in enumerate(record['tool_calls']):
                tool_collapsible = self.create_collapsible_tool(tool_call, tool_responses, i)
                record_layout.addWidget(tool_collapsible)
        
        # 添加到布局末尾（最新记录在底部，因为我们倒序读取）
        self.content_layout.addWidget(record_frame)
    
    def create_collapsible_tool(self, tool_call, tool_responses, index):
        """创建可折叠的工具调用部件"""
        
        # 容器
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 0, 0, 0)
        container_layout.setSpacing(5)
        
        # 工具名称和折叠按钮（简洁样式，类似列表项）
        tool_name = tool_call.get('function', {}).get('name', '未知')
        toggle_button = QPushButton(f"  ▸  {tool_name}")
        toggle_button.setCheckable(True)
        toggle_button.setChecked(False)
        toggle_button.setFlat(True)
        toggle_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 2px;
                text-align: left;
                font-size: 9pt;
                color: #666;
            }
            QPushButton:hover {
                color: #FF9800;
            }
            QPushButton:checked {
                color: #FF9800;
            }
        """)
        container_layout.addWidget(toggle_button)
        
        # 详细信息容器（默认隐藏）
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(20, 5, 0, 5)
        details_layout.setSpacing(5)
        
        # 输入参数
        tool_args = tool_call.get('function', {}).get('arguments', '')
        if tool_args:
            input_label = QLabel("📥 输入:")
            input_label.setStyleSheet("color: #666; font-size: 9pt; font-weight: bold;")
            details_layout.addWidget(input_label)
            
            input_text = QTextEdit()
            try:
                # 尝试格式化 JSON
                args_dict = json.loads(tool_args) if isinstance(tool_args, str) else tool_args
                formatted_args = json.dumps(args_dict, indent=2, ensure_ascii=False)
                input_text.setPlainText(formatted_args)
            except:
                input_text.setPlainText(str(tool_args))
            
            input_text.setReadOnly(True)
            input_text.setMaximumHeight(100)
            input_text.setStyleSheet("""
                QTextEdit {
                    background-color: #FAFAFA;
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    padding: 5px;
                    font-size: 8pt;
                    font-family: Consolas, monospace;
                }
            """)
            details_layout.addWidget(input_text)
        
        # 输出结果
        tool_call_id = tool_call.get('id', '')
        tool_response = None
        for resp in tool_responses:
            if resp.get('tool_call_id') == tool_call_id:
                tool_response = resp
                break
        
        if tool_response:
            output_label = QLabel("📤 输出:")
            output_label.setStyleSheet("color: #666; font-size: 9pt; font-weight: bold;")
            details_layout.addWidget(output_label)
            
            output_text = QTextEdit()
            content = tool_response.get('content', '')
            try:
                # 尝试格式化 JSON
                content_dict = json.loads(content) if isinstance(content, str) else content
                formatted_content = json.dumps(content_dict, indent=2, ensure_ascii=False)
                output_text.setPlainText(formatted_content)
            except:
                output_text.setPlainText(str(content))
            
            output_text.setReadOnly(True)
            output_text.setMaximumHeight(150)
            output_text.setStyleSheet("""
                QTextEdit {
                    background-color: #FAFAFA;
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    padding: 5px;
                    font-size: 8pt;
                    font-family: Consolas, monospace;
                }
            """)
            details_layout.addWidget(output_text)
        
        details_widget.setVisible(False)
        container_layout.addWidget(details_widget)
        
        # 连接折叠/展开事件
        def toggle_details(checked):
            details_widget.setVisible(checked)
            # 更新箭头方向
            if checked:
                toggle_button.setText(f"  ▾  {tool_name}")
            else:
                toggle_button.setText(f"  ▸  {tool_name}")
        
        toggle_button.toggled.connect(toggle_details)
        
        return container
    
    def on_scroll(self, value):
        """滚动事件处理"""
        # 当滚动到底部时加载更多
        scrollbar = self.scroll_area.verticalScrollBar()
        if value >= scrollbar.maximum() - 10 and not self.loading:
            if self.displayed_count < len(self.all_records):
                self.load_more_records()
    
    def showEvent(self, event):
        """窗口显示时重新加载历史"""
        super().showEvent(event)
        self.reload_history()
    
    def reload_history(self):
        """重新加载历史记录"""
        # 清空现有内容
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 重置状态
        self.all_records = []
        self.displayed_count = 0
        self.loading = False
        
        # 重新加载
        self.load_initial_records()
