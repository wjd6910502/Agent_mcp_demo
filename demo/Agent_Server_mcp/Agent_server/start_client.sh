#!/bin/bash

# Qwen Agent 客户端启动脚本

echo "🚀 Qwen Agent 客户端启动脚本"
echo "================================"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    echo "请先安装 Python3"
    exit 1
fi

# 检查requests库是否安装
if ! python3 -c "import requests" &> /dev/null; then
    echo "⚠️  警告: 未找到 requests 库"
    echo "正在安装 requests..."
    pip3 install requests
    if [ $? -ne 0 ]; then
        echo "❌ 安装 requests 失败"
        exit 1
    fi
fi

# 快速检查服务器是否运行（减少超时时间）
echo "🔍 检查服务器连接..."
if python3 -c "
import requests
try:
    response = requests.get('http://localhost:10800', timeout=1)
    if response.status_code == 200:
        print('✅ 服务器连接正常')
        exit(0)
    else:
        print('❌ 服务器响应异常')
        exit(1)
except:
    print('❌ 无法连接到服务器')
    exit(1)
"; then
    echo "✅ 服务器连接检查通过"
else
    echo "⚠️  警告: 无法连接到服务器"
    echo "请确保服务器正在运行: python run.py"
    echo ""
    read -p "是否继续启动客户端? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "👋 退出"
        exit 1
    fi
fi

# 显示使用选项
echo ""
echo "请选择启动模式:"
echo "1) 交互式聊天模式"
echo "2) 测试连接"
echo "3) 发送单次查询"
echo "4) 查看历史记录"
echo "5) 运行完整测试"
echo "6) 运行示例"
echo ""

read -p "请输入选项 (1-6): " choice

case $choice in
    1)
        echo "启动交互式聊天模式..."
        python3 ./client/client.py
        ;;
    2)
        echo "测试服务器连接..."
        python3 ./client/client.py --test
        ;;
    3)
        read -p "请输入查询内容: " query
        echo "发送查询: $query"
        python3 ./client/client.py --query "$query"
        ;;
    4)
        echo "查看历史记录..."
        python3 ./client/client.py --history
        ;;
    5)
        echo "运行完整测试..."
        python3 ./test/test_client.py
        ;;
    6)
        echo "运行示例..."
        python3 ./test/client_example.py
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "👋 客户端已退出" 