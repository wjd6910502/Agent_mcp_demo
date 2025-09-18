#!/usr/bin/env python3
"""
Qwen Agent Web Server 启动脚本
"""

import sys
import os
import subprocess
import importlib.util
import argparse

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Qwen Agent Web Server 启动脚本')
    parser.add_argument('-p', '--port', type=int, default=10800, 
                       help='指定端口号 (默认: 10800)')
    parser.add_argument('-d', '--debug', action='store_true',
                       help='启用debug模式')
    parser.add_argument('--host', default='0.0.0.0',
                       help='指定主机地址 (默认: 0.0.0.0)')
    return parser.parse_args()

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本检查通过: {sys.version}")
    return True

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'flask',
        'flask_cors', 
        'qwen_agent',
        'json5',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包检查通过")
    return True

def check_nodejs():
    """检查Node.js是否安装"""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Node.js检查通过: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠️  警告: 未检测到Node.js")
    print("某些MCP服务器功能可能无法正常工作")
    print("建议安装Node.js: https://nodejs.org/")
    return False

def check_port_availability(port):
    """检查端口是否可用"""
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            print(f"✅ 端口 {port} 可用")
            return True
    except OSError:
        print(f"❌ 端口 {port} 已被占用")
        print("请关闭占用该端口的程序，或使用其他端口")
        return False

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    print("🚀 Qwen Agent Web Server 启动检查")
    print("=" * 50)
    print(f"📋 配置信息:")
    print(f"   - 端口: {args.port}")
    print(f"   - 主机: {args.host}")
    print(f"   - Debug模式: {'开启' if args.debug else '关闭'}")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查依赖包
    if not check_dependencies():
        sys.exit(1)
    
    # 检查Node.js
    check_nodejs()
    
    # 检查端口
    if not check_port_availability(args.port):
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ 所有检查通过，正在启动服务...")
    print(f"🌐 服务将在 http://{args.host}:{args.port} 启动")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    
    # 启动Flask应用
    try:
        from app import app
        app.run(debug=args.debug, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 