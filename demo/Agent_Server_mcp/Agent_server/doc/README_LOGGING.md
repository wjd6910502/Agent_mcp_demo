# 日志系统使用说明

## 概述

Agent Server 现在包含了一个完整的日志系统，支持多种日志级别、文件轮转、性能监控和实时日志查看。

## 日志文件结构

```
logs/
├── agent_server.log    # 主日志文件 (所有级别)
├── error.log          # 错误日志文件 (仅ERROR级别)
├── chat.log           # 聊天日志文件 (聊天相关)
├── performance.log    # 性能日志文件 (性能监控)
└── *.log.1, *.log.2   # 轮转备份文件
```

## 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息

## 日志内容

### 主日志 (agent_server.log)
- 所有级别的日志
- 包含函数名和行号
- 详细的错误堆栈信息

### 错误日志 (error.log)
- 仅包含ERROR级别的日志
- 用于快速定位问题

### 聊天日志 (chat.log)
- 聊天相关的日志
- 用户消息和机器人响应
- 聊天会话状态

### 性能日志 (performance.log)
- API调用性能
- 机器人处理时间
- 内存使用情况

## 日志查看工具

### 基本用法

```bash
# 查看可用的日志文件
python log_viewer.py list

# 查看主日志的最后50行
python log_viewer.py tail --type main --lines 50

# 实时跟踪错误日志
python log_viewer.py errors --follow

# 实时跟踪聊天日志
python log_viewer.py chat --follow

# 实时跟踪性能日志
python log_viewer.py perf --follow
```

### 高级用法

```bash
# 查看特定会话的聊天日志
python log_viewer.py tail --type chat --session session_123

# 搜索包含特定关键词的日志
python log_viewer.py search --pattern "error" --type error

# 查看最近24小时的统计信息
python log_viewer.py stats --hours 24

# 过滤特定日志级别
python log_viewer.py tail --type main --level ERROR

# 实时跟踪并过滤
python log_viewer.py tail --type chat --follow --session session_123
```

### 命令选项

- `list`: 列出所有日志文件
- `tail`: 查看日志尾部
- `search`: 搜索日志内容
- `stats`: 查看统计信息
- `errors`: 监控错误日志
- `chat`: 监控聊天日志
- `perf`: 监控性能日志

### 参数说明

- `--log-dir`: 日志目录 (默认: logs)
- `--type`: 日志类型 (main/error/chat/performance)
- `--lines`: 显示行数 (默认: 50)
- `--follow/-f`: 实时跟踪
- `--level`: 过滤日志级别
- `--session`: 过滤会话ID
- `--pattern`: 搜索模式
- `--hours`: 统计时间范围
- `--case-sensitive`: 区分大小写搜索

## 日志格式

### 主日志格式
```
2024-01-01 12:00:00 - agent_server - INFO - process_chat:123 - Starting chat processing for session session_123
```

### 聊天日志格式
```
2024-01-01 12:00:00 - INFO - [CHAT_START] Session: session_123 | Query: 你好
```

### 性能日志格式
```
2024-01-01 12:00:00 - INFO - [API_PERF] POST /api/chat | Duration: 0.123s | Status: 200
```

## 日志轮转

- 文件大小限制: 10MB
- 备份文件数量: 5个
- 性能日志按天轮转
- 自动清理旧文件

## 性能监控

系统会自动记录以下性能指标：

1. **API响应时间**: 每个API端点的响应时间
2. **机器人处理时间**: 聊天请求的处理时间
3. **内存使用**: 系统内存使用情况

## 故障排查

### 常见问题

1. **日志文件过大**
   - 检查是否有大量重复日志
   - 调整日志级别
   - 清理旧日志文件

2. **性能问题**
   - 查看性能日志
   - 分析API响应时间
   - 检查内存使用情况

3. **错误排查**
   - 查看错误日志
   - 搜索特定错误模式
   - 分析错误堆栈

### 调试技巧

```bash
# 查看最近的错误
python log_viewer.py tail --type error --lines 100

# 搜索特定错误
python log_viewer.py search --pattern "Exception" --type error

# 监控实时错误
python log_viewer.py errors --follow

# 分析性能问题
python log_viewer.py tail --type performance --lines 200
```

## 配置自定义

可以在 `log_config.py` 中修改日志配置：

- 日志文件路径
- 文件大小限制
- 备份文件数量
- 日志格式
- 日志级别

## 最佳实践

1. **定期检查日志**: 每天查看错误日志
2. **监控性能**: 关注API响应时间
3. **清理日志**: 定期清理旧日志文件
4. **设置告警**: 对关键错误设置告警
5. **备份重要日志**: 备份包含重要信息的日志

## 示例脚本

### 监控脚本示例

```bash
#!/bin/bash
# 监控错误日志并发送告警

while true; do
    # 检查是否有新的错误
    if python log_viewer.py tail --type error --lines 1 | grep -q "ERROR"; then
        echo "发现新错误: $(date)"
        # 发送告警邮件或通知
    fi
    sleep 60
done
```

### 日志清理脚本示例

```bash
#!/bin/bash
# 清理30天前的日志文件

find logs/ -name "*.log.*" -mtime +30 -delete
echo "已清理30天前的日志文件"
``` 