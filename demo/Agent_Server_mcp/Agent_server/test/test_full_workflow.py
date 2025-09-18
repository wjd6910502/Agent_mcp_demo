#!/usr/bin/env python3
"""
测试完整工作流程 - 包括Answer解析
"""

import json
import time
from log_config import logger, chat_logger, perf_logger

def parse_answer_content(text):
    """
    解析Answer之后的内容
    从typewriter_print的输出中提取[ANSWER]标记之后的内容
    """
    if not text:
        return ""
    
    # 查找[ANSWER]标记
    answer_marker = '[ANSWER]'
    if answer_marker in text:
        # 分割文本，获取[ANSWER]之后的部分
        parts = text.split(answer_marker)
        if len(parts) > 1:
            # 返回[ANSWER]之后的内容，去除首尾空白
            answer_content = parts[1].strip()
            return answer_content
    
    # 如果没有找到[ANSWER]标记，返回原始文本
    return text

def simulate_bot_response():
    """模拟机器人响应过程"""
    
    # 模拟typewriter_print的输出
    raw_responses = [
        # 第一次响应 - 思考过程
        "[THINK]\n我需要分析用户的问题，这是一个关于天气的询问。",
        
        # 第二次响应 - 工具调用
        "[THINK]\n我需要分析用户的问题，这是一个关于天气的询问。\n[TOOL_CALL] weather_tool\n{\"location\": \"北京\"}",
        
        # 第三次响应 - 工具结果
        "[THINK]\n我需要分析用户的问题，这是一个关于天气的询问。\n[TOOL_CALL] weather_tool\n{\"location\": \"北京\"}\n[TOOL_RESPONSE] weather_tool\n{\"temperature\": \"25°C\", \"condition\": \"晴朗\"}",
        
        # 第四次响应 - 最终答案
        "[THINK]\n我需要分析用户的问题，这是一个关于天气的询问。\n[TOOL_CALL] weather_tool\n{\"location\": \"北京\"}\n[TOOL_RESPONSE] weather_tool\n{\"temperature\": \"25°C\", \"condition\": \"晴朗\"}\n[ANSWER]\n根据天气查询结果，北京今天天气晴朗，温度25°C，非常适合外出活动。",
    ]
    
    session_id = "test_session_123"
    
    print("模拟完整工作流程测试")
    print("=" * 60)
    
    for i, raw_response in enumerate(raw_responses, 1):
        print(f"\n步骤 {i}:")
        print(f"原始响应数据:")
        print(f"Raw response: {repr(raw_response)}")
        
        # 解析Answer内容
        answer_content = parse_answer_content(raw_response)
        
        print(f"解析后的Answer内容:")
        print(f"Parsed answer: {repr(answer_content)}")
        
        # 模拟发送到客户端的数据
        client_data = {
            'type': 'stream',
            'content': answer_content if answer_content else raw_response,
            'timestamp': time.time()
        }
        
        print(f"发送给客户端的数据:")
        print(f"Client data: {json.dumps(client_data, indent=2, ensure_ascii=False)}")
        
        # 记录日志
        logger.info(f"原始响应数据 (session {session_id}):")
        logger.info(f"Raw response_plain_text: {repr(raw_response)}")
        logger.info(f"解析后的Answer内容 (session {session_id}):")
        logger.info(f"Parsed answer_content: {repr(answer_content)}")
        
        print("-" * 40)

def test_complete_signal():
    """测试完成信号"""
    print("\n测试完成信号:")
    print("=" * 60)
    
    # 模拟最终的完整响应
    final_raw_response = "[THINK]\n我需要分析用户的问题，这是一个关于天气的询问。\n[TOOL_CALL] weather_tool\n{\"location\": \"北京\"}\n[TOOL_RESPONSE] weather_tool\n{\"temperature\": \"25°C\", \"condition\": \"晴朗\"}\n[ANSWER]\n根据天气查询结果，北京今天天气晴朗，温度25°C，非常适合外出活动。"
    
    print(f"最终原始响应:")
    print(f"Final raw response: {repr(final_raw_response)}")
    
    # 解析最终Answer内容
    final_answer_content = parse_answer_content(final_raw_response)
    
    print(f"最终解析的Answer内容:")
    print(f"Final parsed answer: {repr(final_answer_content)}")
    
    # 模拟完成信号
    complete_data = {
        'type': 'complete',
        'content': final_answer_content,
        'timestamp': time.time()
    }
    
    print(f"完成信号数据:")
    print(f"Complete signal: {json.dumps(complete_data, indent=2, ensure_ascii=False)}")
    
    # 记录日志
    session_id = "test_session_123"
    logger.info(f"最终原始响应数据 (session {session_id}):")
    logger.info(f"Final raw response_plain_text: {repr(final_raw_response)}")
    logger.info(f"最终解析的Answer内容 (session {session_id}):")
    logger.info(f"Final parsed answer_content: {repr(final_answer_content)}")

def main():
    """主测试函数"""
    print("开始完整工作流程测试")
    print("=" * 60)
    
    simulate_bot_response()
    test_complete_signal()
    
    print("\n" + "=" * 60)
    print("完整工作流程测试完成！")
    print("\n你可以查看日志文件来验证数据记录:")
    print("python log_viewer.py tail --type main --lines 20")

if __name__ == '__main__':
    main() 