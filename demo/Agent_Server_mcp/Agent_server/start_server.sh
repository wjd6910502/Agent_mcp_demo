#!/bin/bash

# Qwen Agent Web Server 启动脚本
# 使用方法: ./start_server.sh [选项]
# 选项:
#   -p, --port PORT     指定端口号 (默认: 10800)
#   -d, --debug         启用debug模式
#   -h, --host HOST     指定主机地址 (默认: 0.0.0.0)
#   --help              显示帮助信息

# 默认配置
PORT=10800
DEBUG=false
HOST="0.0.0.0"

# 显示帮助信息
show_help() {
    echo "Qwen Agent Web Server 启动脚本"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -p, --port PORT     指定端口号 (默认: 10800)"
    echo "  -d, --debug         启用debug模式"
    echo "  -h, --host HOST     指定主机地址 (默认: 0.0.0.0)"
    echo "  --help              显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                    # 使用默认配置启动"
    echo "  $0 -p 8080           # 在端口8080启动"
    echo "  $0 -d                # 启用debug模式"
    echo "  $0 -p 8080 -d        # 在端口8080启动并启用debug模式"
    echo "  $0 -h localhost      # 在localhost启动"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -d|--debug)
            DEBUG=true
            shift
            ;;
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            echo "使用 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

# 检查脚本是否在正确的目录中运行
if [ ! -f "run.py" ]; then
    echo "❌ 错误: 请在包含 run.py 的目录中运行此脚本"
    exit 1
fi

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

# 构建Python命令
PYTHON_CMD="python3 run.py --port $PORT --host $HOST"

if [ "$DEBUG" = true ]; then
    PYTHON_CMD="$PYTHON_CMD --debug"
fi

echo "🚀 启动 Qwen Agent Web Server..."
echo "📋 配置信息:"
echo "   - 端口: $PORT"
echo "   - 主机: $HOST"
echo "   - Debug模式: $([ "$DEBUG" = true ] && echo "开启" || echo "关闭")"
echo ""

# 执行Python脚本
exec $PYTHON_CMD 