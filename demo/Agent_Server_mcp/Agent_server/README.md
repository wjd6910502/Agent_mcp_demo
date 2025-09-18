# Qwen Agent Web Server

这是一个基于Flask的Web服务，将Qwen Agent的客户端输入改为Web接口输入。

## 功能特性

- 🤖 基于Qwen Agent的智能对话
- 🎨 AI图像生成功能
- 📁 文件系统操作
- 🗺️ 地图查询服务
- 🔧 Blender 3D操作
- 💾 内存管理
- 🌐 实时流式响应
- 📱 响应式Web界面
- 🔄 多会话管理

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

## API接口

### 1. 聊天接口
- **POST** `/api/chat`
- 请求体：
```json
{
    "query": "用户输入的问题",
    "session_id": "会话ID（可选）"
}
```

### 2. 流式响应接口
- **GET** `/api/stream/<session_id>`
- 返回Server-Sent Events格式的流式数据

### 3. 聊天历史接口
- **GET** `/api/history/<session_id>`
- 获取指定会话的聊天历史

### 4. 清除历史接口
- **GET** `/api/clear/<session_id>`
- 清除指定会话的聊天历史

## 配置说明

在 `app.py` 中可以修改以下配置：

### LLM配置
```python
llm_cfg = {
    'model': 'qwen-plus',
    'model_server': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    'api_key': 'your-api-key'
}
```

### MCP服务器配置
支持以下MCP服务器：
- filesystem: 文件系统操作
- memory: 内存管理
- amap-maps: 高德地图服务
- blender: Blender 3D操作

## 使用示例

1. 打开浏览器访问 `http://localhost:5000`
2. 在聊天界面输入问题
3. 系统会实时显示AI的响应
4. 可以使用控制按钮管理会话

## 支持的指令示例

- "画一只可爱的小猫"
- "帮我查看当前目录的文件"
- "查询北京的天气"
- "在Blender中创建一个立方体"

## 注意事项

1. 确保已正确配置API密钥
2. 需要安装Node.js以支持MCP服务器
3. 某些功能可能需要额外的依赖包
4. 建议在生产环境中使用WSGI服务器

## 故障排除

如果遇到问题，请检查：
1. 依赖包是否正确安装
2. API密钥是否有效
3. 网络连接是否正常
4. 端口5000是否被占用 