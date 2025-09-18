#!/usr/bin/env python3
"""
Qwen Agent 客户端使用示例
演示如何使用客户端进行各种操作
"""

from client import QwenAgentClient
import time

def example_basic_chat():
    """基本聊天示例"""
    print("=" * 50)
    print("示例1: 基本聊天")
    print("=" * 50)
    
    client = QwenAgentClient()
    
    # 测试连接
    if not client.test_connection():
        print("❌ 无法连接到服务器")
        return
    
    # 发送聊天请求
    query = "你好，请介绍一下你自己"
    print(f"发送查询: {query}")
    
    response = client.stream_chat(query)
    print(f"\n完整响应:\n{response}")

def example_custom_session():
    """自定义会话示例"""
    print("\n" + "=" * 50)
    print("示例2: 自定义会话")
    print("=" * 50)
    
    client = QwenAgentClient()
    session_id = "example_session_123"
    
    # 发送第一条消息
    query1 = "请帮我写一个Python函数来计算斐波那契数列"
    print(f"会话 {session_id} - 查询1: {query1}")
    response1 = client.stream_chat(query1, session_id)
    
    # 发送第二条消息（会基于第一条的上下文）
    query2 = "请优化这个函数，使其更高效"
    print(f"\n会话 {session_id} - 查询2: {query2}")
    response2 = client.stream_chat(query2, session_id)
    
    # 查看历史记录
    print(f"\n查看会话 {session_id} 的历史记录:")
    history = client.get_history(session_id)
    if "history" in history:
        for i, msg in enumerate(history["history"], 1):
            role = "用户" if msg.get("role") == "user" else "助手"
            content = msg.get("content", "")[:50] + "..." if len(msg.get("content", "")) > 50 else msg.get("content", "")
            print(f"  {i}. {role}: {content}")

def example_callback_usage():
    """回调函数使用示例"""
    print("\n" + "=" * 50)
    print("示例3: 使用回调函数")
    print("=" * 50)
    
    def my_callback(event_type, content):
        """自定义回调函数"""
        if event_type == 'stream':
            # 可以在这里做额外的处理，比如保存到文件
            pass
        elif event_type == 'complete':
            print(f"\n🎉 响应完成，总长度: {len(content)} 字符")
        elif event_type == 'error':
            print(f"\n💥 发生错误: {content}")
    
    client = QwenAgentClient()
    query = "请解释一下什么是机器学习"
    print(f"发送查询: {query}")
    
    response = client.stream_chat(query, callback=my_callback)

def example_history_management():
    """历史记录管理示例"""
    print("\n" + "=" * 50)
    print("示例4: 历史记录管理")
    print("=" * 50)
    
    client = QwenAgentClient()
    session_id = "history_demo"
    
    # 发送几条消息
    queries = [
        "什么是人工智能？",
        "机器学习和深度学习有什么区别？",
        "请推荐一些学习AI的资源"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n发送第{i}条消息: {query}")
        client.stream_chat(query, session_id)
        time.sleep(1)  # 稍微等待一下
    
    # 查看历史记录
    print(f"\n查看会话 {session_id} 的历史记录:")
    history = client.get_history(session_id)
    
    # 清除历史记录
    print(f"\n清除会话 {session_id} 的历史记录:")
    client.clear_history(session_id)
    
    # 再次查看（应该为空）
    print(f"\n清除后再次查看历史记录:")
    history_after_clear = client.get_history(session_id)

def example_error_handling():
    """错误处理示例"""
    print("\n" + "=" * 50)
    print("示例5: 错误处理")
    print("=" * 50)
    
    # 尝试连接到错误的URL
    print("尝试连接到错误的URL:")
    wrong_client = QwenAgentClient("http://localhost:9999")
    wrong_client.test_connection()
    
    # 尝试发送请求到错误的服务器
    print("\n尝试发送请求到错误的服务器:")
    result = wrong_client.chat("测试消息")
    print(f"结果: {result}")

def main():
    """运行所有示例"""
    print("🚀 Qwen Agent 客户端使用示例")
    print("请确保服务器正在运行在 http://localhost:10800")
    print("=" * 50)
    
    try:
        # 运行示例
        example_basic_chat()
        example_custom_session()
        example_callback_usage()
        example_history_management()
        example_error_handling()
        
        print("\n" + "=" * 50)
        print("✅ 所有示例运行完成")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\n👋 示例被用户中断")
    except Exception as e:
        print(f"\n❌ 运行示例时发生错误: {e}")

if __name__ == "__main__":
    main() 