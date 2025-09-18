#!/usr/bin/env python3
"""
日志系统测试脚本
用于验证日志配置是否正确工作
"""

import time
import os
from log_config import logger, chat_logger, perf_logger

def test_basic_logging():
    """测试基本日志功能"""
    print("测试基本日志功能...")
    
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    
    print("基本日志测试完成")

def test_chat_logging():
    """测试聊天日志功能"""
    print("测试聊天日志功能...")
    
    session_id = "test_session_123"
    query = "你好，这是一个测试消息"
    response = "你好！我是测试机器人，很高兴为你服务。"
    
    chat_logger.log_chat_start(session_id, query)
    chat_logger.log_user_message(session_id, query)
    chat_logger.log_bot_message(session_id, response)
    chat_logger.log_chat_response(session_id, "stream", len(response))
    chat_logger.log_chat_complete(session_id, 1.5)
    
    print("聊天日志测试完成")

def test_performance_logging():
    """测试性能日志功能"""
    print("测试性能日志功能...")
    
    perf_logger.log_api_call("/api/chat", "POST", 0.123, 200)
    perf_logger.log_bot_processing("test_session_123", 1.456)
    perf_logger.log_memory_usage(128.5)
    
    print("性能日志测试完成")

def test_error_logging():
    """测试错误日志功能"""
    print("测试错误日志功能...")
    
    try:
        # 故意制造一个错误
        result = 1 / 0
    except Exception as e:
        logger.error(f"测试错误: {e}", exc_info=True)
        chat_logger.log_chat_error("test_session_123", str(e))
    
    print("错误日志测试完成")

def check_log_files():
    """检查日志文件是否创建"""
    print("检查日志文件...")
    
    log_files = [
        'logs/agent_server.log',
        'logs/error.log',
        'logs/chat.log',
        'logs/performance.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"✓ {log_file} 存在 ({size} bytes)")
        else:
            print(f"✗ {log_file} 不存在")

def main():
    """主测试函数"""
    print("开始日志系统测试")
    print("=" * 50)
    
    # 确保logs目录存在
    if not os.path.exists('logs'):
        os.makedirs('logs')
        print("创建logs目录")
    
    # 运行各种测试
    test_basic_logging()
    time.sleep(1)
    
    test_chat_logging()
    time.sleep(1)
    
    test_performance_logging()
    time.sleep(1)
    
    test_error_logging()
    time.sleep(1)
    
    # 检查日志文件
    check_log_files()
    
    print("\n" + "=" * 50)
    print("日志系统测试完成！")
    print("\n你可以使用以下命令查看日志:")
    print("python log_viewer.py list")
    print("python log_viewer.py tail --type main --lines 20")
    print("python log_viewer.py tail --type chat --lines 10")
    print("python log_viewer.py tail --type error --lines 5")

if __name__ == '__main__':
    main() 