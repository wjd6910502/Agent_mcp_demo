#!/usr/bin/env python3
"""
Qwen Agent 客户端测试脚本
用于验证客户端的基本功能是否正常
"""

import sys
import time
from client import QwenAgentClient

def test_connection():
    """测试连接功能"""
    print("🔍 测试1: 连接功能")
    print("-" * 30)
    
    client = QwenAgentClient()
    result = client.test_connection()
    
    if result:
        print("✅ 连接测试通过")
        return True
    else:
        print("❌ 连接测试失败")
        return False

def test_basic_chat():
    """测试基本聊天功能"""
    print("\n🔍 测试2: 基本聊天功能")
    print("-" * 30)
    
    client = QwenAgentClient()
    
    # 发送简单查询
    query = "你好"
    print(f"发送查询: {query}")
    
    try:
        response = client.stream_chat(query)
        if response and not response.startswith("错误"):
            print("✅ 基本聊天测试通过")
            return True
        else:
            print(f"❌ 基本聊天测试失败: {response}")
            return False
    except Exception as e:
        print(f"❌ 基本聊天测试异常: {e}")
        return False

def test_session_management():
    """测试会话管理功能"""
    print("\n🔍 测试3: 会话管理功能")
    print("-" * 30)
    
    client = QwenAgentClient()
    session_id = "test_session_123"
    
    try:
        # 发送消息到指定会话
        query = "这是一个测试会话"
        print(f"发送消息到会话 {session_id}: {query}")
        response = client.stream_chat(query, session_id)
        
        # 获取历史记录
        print(f"获取会话 {session_id} 的历史记录")
        history = client.get_history(session_id)
        
        if "history" in history and len(history["history"]) > 0:
            print("✅ 会话管理测试通过")
            return True
        else:
            print("❌ 会话管理测试失败: 历史记录为空")
            return False
            
    except Exception as e:
        print(f"❌ 会话管理测试异常: {e}")
        return False

def test_error_handling():
    """测试错误处理功能"""
    print("\n🔍 测试4: 错误处理功能")
    print("-" * 30)
    
    # 测试连接到错误的URL
    wrong_client = QwenAgentClient("http://localhost:9999")
    result = wrong_client.test_connection()
    
    if not result:
        print("✅ 错误处理测试通过 (正确识别连接失败)")
        return True
    else:
        print("❌ 错误处理测试失败 (应该识别连接失败)")
        return False

def test_stream_response():
    """测试流式响应功能"""
    print("\n🔍 测试5: 流式响应功能")
    print("-" * 30)
    
    client = QwenAgentClient()
    
    # 测试回调函数
    received_chunks = []
    
    def test_callback(event_type, content):
        if event_type == 'stream':
            received_chunks.append(content)
        elif event_type == 'complete':
            print(f"✅ 流式响应完成，收到 {len(received_chunks)} 个数据块")
        elif event_type == 'error':
            print(f"❌ 流式响应错误: {content}")
    
    try:
        query = "请简单介绍一下Python"
        print(f"发送查询: {query}")
        response = client.stream_chat(query, callback=test_callback)
        
        if response and len(received_chunks) > 0:
            print("✅ 流式响应测试通过")
            return True
        else:
            print("❌ 流式响应测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 流式响应测试异常: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行 Qwen Agent 客户端测试")
    print("=" * 50)
    
    tests = [
        ("连接功能", test_connection),
        ("基本聊天", test_basic_chat),
        ("会话管理", test_session_management),
        ("错误处理", test_error_handling),
        ("流式响应", test_stream_response)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            time.sleep(1)  # 测试间隔
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！客户端功能正常")
        return True
    else:
        print("⚠️  部分测试失败，请检查服务器状态和网络连接")
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # 快速测试模式
        print("⚡ 快速测试模式")
        if test_connection() and test_basic_chat():
            print("✅ 快速测试通过")
        else:
            print("❌ 快速测试失败")
    else:
        # 完整测试模式
        run_all_tests()

if __name__ == "__main__":
    main() 