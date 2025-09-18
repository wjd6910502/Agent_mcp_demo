#!/usr/bin/env python3
"""
测试ANSWER解析功能
"""

import re
import json

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

def test_answer_parsing():
    """测试ANSWER解析功能"""
    
    # 测试用例1：包含ANSWER的文本
    test_text_1 = """
[TOOL_CALL] filesystem
{"path": "/test.txt"}

[TOOL_RESPONSE] filesystem
{"content": "Hello World"}

[ANSWER]
这是一个测试回答，包含了工具调用的结果。

根据文件内容，我可以看到文件包含"Hello World"。
"""
    
    # 测试用例2：不包含ANSWER的文本
    test_text_2 = """
[TOOL_CALL] filesystem
{"path": "/test.txt"}

[TOOL_RESPONSE] filesystem
{"content": "Hello World"}
"""
    
    # 测试用例3：只有ANSWER的文本
    test_text_3 = """
[ANSWER]
这是一个简单的回答，没有工具调用。
"""
    
    print("=== 测试ANSWER解析功能 ===")
    
    # 测试用例1
    print("\n1. 测试包含ANSWER的文本:")
    answer_1 = parse_answer_content(test_text_1)
    print(f"解析结果: {answer_1}")
    
    # 测试用例2
    print("\n2. 测试不包含ANSWER的文本:")
    answer_2 = parse_answer_content(test_text_2)
    print(f"解析结果: {answer_2}")
    
    # 测试用例3
    print("\n3. 测试只有ANSWER的文本:")
    answer_3 = parse_answer_content(test_text_3)
    print(f"解析结果: {answer_3}")
    
    # 测试正则表达式解析
    print("\n=== 测试正则表达式解析 ===")
    
    # 使用正则表达式查找ANSWER
    answer_match_1 = re.search(r'\[ANSWER\]\s*(.*?)(?=\[TOOL_CALL\]|\[TOOL_RESPONSE\]|$)', test_text_1, re.DOTALL)
    if answer_match_1:
        answer_regex_1 = answer_match_1.group(1).strip()
        print(f"正则解析结果1: {answer_regex_1}")
    
    answer_match_2 = re.search(r'\[ANSWER\]\s*(.*?)(?=\[TOOL_CALL\]|\[TOOL_RESPONSE\]|$)', test_text_2, re.DOTALL)
    if answer_match_2:
        answer_regex_2 = answer_match_2.group(1).strip()
        print(f"正则解析结果2: {answer_regex_2}")
    else:
        print("正则解析结果2: 未找到ANSWER")
    
    answer_match_3 = re.search(r'\[ANSWER\]\s*(.*?)(?=\[TOOL_CALL\]|\[TOOL_RESPONSE\]|$)', test_text_3, re.DOTALL)
    if answer_match_3:
        answer_regex_3 = answer_match_3.group(1).strip()
        print(f"正则解析结果3: {answer_regex_3}")

if __name__ == "__main__":
    test_answer_parsing() 