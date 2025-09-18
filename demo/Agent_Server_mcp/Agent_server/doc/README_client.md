# Qwen Agent 客户端使用指南

这是一个用于与 Qwen Agent Web Server 通信的 Python 客户端，支持聊天、流式响应、历史记录管理等功能。

## 功能特性

- 🤖 **智能聊天**: 支持与 Qwen Agent 进行对话
- 📡 **流式响应**: 实时接收 AI 响应，类似 ChatGPT 体验
- 📚 **历史记录**: 管理聊天历史，支持多会话
- 🔧 **会话管理**: 支持自定义会话 ID
- 🛠️ **交互式界面**: 提供命令行交互界面
- ⚡ **错误处理**: 完善的错误处理和重试机制

## 安装依赖

```bash
pip install requests
```

## 快速开始

### 1. 启动服务器

首先确保 Qwen Agent 服务器正在运行：

```bash
cd Agent_server
python run.py
```

### 2. 使用交互式客户端

```bash
python client.py
```

这将启动一个交互式命令行界面，你可以：
- 直接输入消息进行聊天
- 使用 `/help` 查看所有命令
- 使用 `/history` 查看聊天历史
- 使用 `/clear` 清除历史记录

### 3. 使用命令行参数

```bash
# 测试连接
python client.py --test

# 发送单次查询
python client.py --query "你好，请介绍一下你自己"

# 查看历史记录
python client.py --history

# 清除历史记录
python client.py --clear

# 指定服务器URL
python client.py --url http://localhost:10800
```

## 编程接口

### 基本使用

```python
from client import QwenAgentClient

# 创建客户端
client = QwenAgentClient("http://localhost:10800")

# 测试连接
if client.test_connection():
    print("连接成功！")
    
    # 发送聊天请求
    response = client.stream_chat("你好，请介绍一下你自己")
    print(f"AI回复: {response}")
```

### 自定义会话

```python
# 使用自定义会话ID
session_id = "my_session_123"
response = client.stream_chat("请帮我写一个Python函数", session_id)

# 查看会话历史
history = client.get_history(session_id)
print(f"会话历史: {history}")

# 清除会话历史
client.clear_history(session_id)
```

### 使用回调函数

```python
def my_callback(event_type, content):
    if event_type == 'stream':
        # 处理流式内容
        print(content, end='', flush=True)
    elif event_type == 'complete':
        print(f"\n响应完成，总长度: {len(content)} 字符")
    elif event_type == 'error':
        print(f"错误: {content}")

# 使用回调函数
client.stream_chat("请解释机器学习", callback=my_callback)
```

## 命令行界面命令

在交互式模式下，你可以使用以下命令：

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助信息 |
| `/history` | 显示聊天历史 |
| `/clear` | 清除聊天历史 |
| `/session` | 显示当前会话ID |
| `/test` | 测试服务器连接 |
| `/quit` 或 `/exit` | 退出客户端 |

## 运行示例

查看完整的使用示例：

```bash
python client_example.py
```

这个示例展示了：
- 基本聊天功能
- 自定义会话管理
- 回调函数使用
- 历史记录管理
- 错误处理

## API 参考

### QwenAgentClient 类

#### 初始化
```python
QwenAgentClient(base_url="http://localhost:10800")
```

#### 方法

- `test_connection() -> bool`: 测试服务器连接
- `chat(query: str, session_id: str = None) -> dict`: 发送聊天请求
- `stream_chat(query: str, session_id: str = None, callback: callable = None) -> str`: 流式聊天
- `get_history(session_id: str = None) -> dict`: 获取聊天历史
- `clear_history(session_id: str = None) -> dict`: 清除聊天历史

### InteractiveClient 类

提供交互式命令行界面：

```python
from client import InteractiveClient

client = InteractiveClient("http://localhost:10800")
client.run()
```

## 错误处理

客户端包含完善的错误处理机制：

- 网络连接错误
- 服务器响应错误
- JSON 解析错误
- 超时处理

所有错误都会被捕获并显示友好的错误信息。

## 注意事项

1. **服务器状态**: 使用前请确保 Qwen Agent 服务器正在运行
2. **网络连接**: 确保客户端能够访问服务器地址
3. **会话管理**: 不同会话ID的聊天历史是独立的
4. **流式响应**: 流式响应会实时显示，按 Ctrl+C 可以中断
5. **历史记录**: 历史记录存储在服务器端，重启服务器会丢失

## 故障排除

### 连接失败
```
❌ 无法连接到服务器: Connection refused
```
- 检查服务器是否正在运行
- 检查端口号是否正确
- 检查防火墙设置

### 请求失败
```
❌ 聊天请求失败: 500 Internal Server Error
```
- 检查服务器日志
- 确认服务器配置正确
- 检查API密钥是否有效

### 流式响应中断
```
❌ 流式响应失败: timeout
```
- 检查网络连接
- 增加超时时间
- 检查服务器负载

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个客户端！

## 许可证

本项目采用 MIT 许可证。 