# Agent Server API 文档

## 概述

Agent Server 是一个基于 Flask 的聊天机器人服务，支持流式响应和会话管理。该服务集成了 Qwen 大语言模型和多种 MCP (Model Context Protocol) 工具，包括文件系统访问、内存管理、地图服务和 Blender 集成。

**服务地址**: `http://localhost:10800`

## 基础信息

- **服务名称**: Agent Server
- **版本**: 1.0.0
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

目前该API不需要认证，所有端点都是公开访问的。

## 端点列表

### 1. 服务状态检查

#### GET /
获取服务基本信息和可用端点列表。

**请求**:
```http
GET /
```

**响应**:
```json
{
  "status": "running",
  "service": "Agent Server",
  "version": "1.0.0",
  "endpoints": {
    "chat": "/api/chat",
    "stream": "/api/stream/<session_id>",
    "history": "/api/history/<session_id>",
    "clear": "/api/clear/<session_id>",
    "health": "/api/health"
  }
}
```

### 2. 健康检查

#### GET /api/health
检查服务健康状态。

**请求**:
```http
GET /api/health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "service": "Agent Server"
}
```

### 3. 聊天接口

#### POST /api/chat
发送聊天请求，启动异步处理。

**请求**:
```http
POST /api/chat
Content-Type: application/json
```

**请求参数**:
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| query | string | 是 | 用户输入的消息内容 |
| session_id | string | 否 | 会话ID，默认为 "default" |

**请求示例**:
```json
{
  "query": "你好，请帮我创建一个立方体",
  "session_id": "user_123"
}
```

**响应**:
```json
{
  "status": "processing",
  "session_id": "user_123",
  "message": "Chat request received and processing started"
}
```

**错误响应**:
```json
{
  "error": "Query is required"
}
```

### 4. 流式响应接口

#### GET /api/stream/{session_id}
获取聊天处理的流式响应。

**请求**:
```http
GET /api/stream/user_123
```

**响应格式**: Server-Sent Events (SSE)

**响应类型**:

1. **流式数据** (`type: "stream"`):
```json
{
  "type": "stream",
  "content": "正在处理您的请求...",
  "timestamp": 1703123456.789
}
```

2. **心跳** (`type: "heartbeat"`):
```json
{
  "type": "heartbeat",
  "timestamp": 1703123456.789
}
```

3. **完成信号** (`type: "complete"`):
```json
{
  "type": "complete",
  "content": "处理完成，这是最终结果",
  "timestamp": 1703123456.789
}
```

4. **错误信号** (`type: "error"`):
```json
{
  "type": "error",
  "content": "处理过程中发生错误",
  "timestamp": 1703123456.789
}
```

**客户端示例** (JavaScript):
```javascript
const eventSource = new EventSource('/api/stream/user_123');

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'stream':
      console.log('流式数据:', data.content);
      break;
    case 'complete':
      console.log('处理完成:', data.content);
      eventSource.close();
      break;
    case 'error':
      console.error('错误:', data.content);
      eventSource.close();
      break;
    case 'heartbeat':
      console.log('心跳保持连接');
      break;
  }
};

eventSource.onerror = function(error) {
  console.error('SSE连接错误:', error);
  eventSource.close();
};
```

### 5. 聊天历史

#### GET /api/history/{session_id}
获取指定会话的聊天历史。

**请求**:
```http
GET /api/history/user_123
```

**响应**:
```json
{
  "history": [
    {
      "role": "user",
      "content": "你好，请帮我创建一个立方体"
    },
    {
      "role": "assistant",
      "content": "我正在为您创建一个立方体..."
    }
  ]
}
```

### 6. 清除聊天历史

#### GET /api/clear/{session_id}
清除指定会话的聊天历史。

**请求**:
```http
GET /api/clear/user_123
```

**响应**:
```json
{
  "message": "History cleared"
}
```

## 错误处理

### HTTP 状态码

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式

```json
{
  "error": "错误描述信息"
}
```

## 集成工具

该服务集成了以下 MCP 工具：

1. **文件系统工具** (`filesystem`)
   - 提供对本地文件系统的访问
   - 路径: `/Users/apple/demo_mcp`

2. **内存管理工具** (`memory`)
   - 提供内存存储和管理功能

3. **高德地图工具** (`amap-maps`)
   - 提供地图相关服务
   - 需要 API Key: `63fa842ec9b7775e456f01d7e03fd399`

4. **Blender 工具** (`blender`)
   - 提供 Blender 3D 软件集成功能

## 使用流程

### 完整的聊天流程

1. **发送聊天请求**:
   ```bash
   curl -X POST http://localhost:10800/api/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "你好", "session_id": "test_session"}'
   ```

2. **建立流式连接**:
   ```bash
   curl -N http://localhost:10800/api/stream/test_session
   ```

3. **获取聊天历史** (可选):
   ```bash
   curl http://localhost:10800/api/history/test_session
   ```

4. **清除历史** (可选):
   ```bash
   curl http://localhost:10800/api/clear/test_session
   ```

## 注意事项

1. **会话管理**: 每个 `session_id` 维护独立的聊天历史
2. **流式响应**: 使用 Server-Sent Events 实现实时响应
3. **超时处理**: 流式连接有30秒超时机制
4. **错误恢复**: 服务会自动清理异常会话的队列
5. **并发支持**: 支持多用户同时使用不同会话

## 日志记录

服务提供详细的日志记录，包括：
- 聊天请求和响应
- 性能指标
- 错误信息
- 会话管理

日志文件位置和配置请参考 `log_config.py` 文件。

## 示例客户端

参考 `client/` 目录下的客户端示例代码，了解如何集成该API服务。 