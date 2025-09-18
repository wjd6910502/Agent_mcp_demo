#!/usr/bin/env python3
"""
Qwen Agent Web Server 客户端
支持聊天、流式响应、历史记录管理等功能
"""

import requests
import json
import time
import threading
import queue
from typing import Optional, Callable, Dict, Any
import sys
import os
import re
import logging

# 导入日志配置
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'log'))
from log_config import get_logger, get_chat_logger

# 获取日志器
logger = get_logger('client')
chat_logger = get_chat_logger()

# 使用标准json库

def setup_linux_compatibility():
    """设置Linux系统兼容性"""
    # 设置默认编码为UTF-8
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding('utf-8')
    
    # 设置环境变量
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    
    # 处理终端编码问题
    try:
        import locale
        # 尝试设置locale为UTF-8
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except (locale.Error, ImportError):
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except locale.Error:
            pass  # 如果都失败，就使用默认设置

# 在模块加载时设置兼容性
setup_linux_compatibility()



class QwenAgentClient:
    """Qwen Agent 客户端类"""
    
    def __init__(self, base_url: str = "http://localhost:10800"):
        """
        初始化客户端
        
        Args:
            base_url: 服务器基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.session_id = f"client_{int(time.time())}"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}
    
    def chat(self, query: str, session_id: Optional[str] = None, options: Optional[list] = None) -> Dict:
        """
        发送聊天请求
        
        Args:
            query: 用户输入的问题
            session_id: 会话ID，如果不提供则使用默认会话
            options: 工具选项列表，格式: [{"name": "string", "enabled": bool}, ...]
            
        Returns:
            响应结果
        """
        if not session_id:
            session_id = self.session_id
            
        data = {
            "query": query,
            "session_id": session_id
        }
        
        # 添加options字段（如果提供）
        if options is not None:
            data["options"] = options
        
        logger.info(f"🤖 发送请求: {query}")
        if options:
            logger.info(f"🔧 工具选项: {options}")
        result = self._make_request('POST', '/api/chat', data)
        
        if "error" not in result:
            logger.info(f"✅ 请求已接收，会话ID: {result.get('session_id')}")
            logger.debug(f"result: {result}")
            return result
        else:
            logger.error(f"❌ 聊天请求失败: {result['error']}")
            return result
    
    def stream_chat(self, query: str, session_id: Optional[str] = None, 
                   callback: Optional[Callable] = None, options: Optional[list] = None) -> str:
        """
        流式聊天，实时获取响应
        
        Args:
            query: 用户输入的问题
            session_id: 会话ID
            callback: 回调函数，用于处理流式响应
            options: 工具选项列表，格式: [{"name": "string", "enabled": bool}, ...]
            
        Returns:
            完整的响应文本
        """
        if not session_id:
            session_id = self.session_id
            
        # 首先发送聊天请求
        chat_result = self.chat(query, session_id, options)
        if "error" in chat_result:
            return f"错误: {chat_result['error']}"
        
        # 然后开始流式接收响应
        return self._stream_response(session_id, callback)
    
    
    def _parse_answer_content(self, content_text: str) -> str:
        """
        解析ANSWER内容
        
        Args:
            content_text: 包含ANSWER标签的文本内容
            
        Returns:
            解析出的ANSWER内容
        """
        logger.debug(f"🔍 正在解析内容: {content_text[:200]}...")
        
        # 处理累积文本问题：找到最后一个[ANSWER]标签
        answer_marker = '[ANSWER]'
        if answer_marker in content_text:
            # 分割文本，获取最后一个[ANSWER]之后的部分
            parts = content_text.split(answer_marker)
            if len(parts) > 1:
                # 返回最后一个[ANSWER]之后的内容，去除首尾空白
                answer_content = parts[-1].strip()
                logger.debug(f"✅ 解析到ANSWER内容: {answer_content[:100]}...")
                return answer_content
        
        # 如果没有找到[ANSWER]标记，返回原始文本
        logger.warning("⚠️  未找到ANSWER标签，返回原始内容")
        return content_text.strip()

    def _stream_response(self, session_id: str, callback: Optional[Callable] = None) -> str:
        """处理流式响应，兼容 type=stream 日志格式"""
        url = f"{self.base_url}/api/stream/{session_id}"
        try:
            logger.info("📡 开始接收流式响应...")
            response = self.session.get(url, stream=True, timeout=30)  # 增加超时时间到30秒
            logger.debug(f"response: {response}")
            response.raise_for_status()

            full_response = ""
            start_time = time.time()
            buffer = ""
            answer_content = ""
            start_time = time.time()
            for line in response.iter_lines():
                if time.time() - start_time > 60:
                    logger.warning("\n⏰ 60秒超时，自动关闭连接")
                    break
                if not line:
                    continue
                try:
                    # 使用更安全的编码处理，兼容不同系统的编码
                    line_str = line.decode('utf-8', errors='replace')
                    print(f"************************************************\n")
                    print(f"result: {line_str}")
                    print(f"************************************************\n")
                except UnicodeDecodeError:
                    # 如果UTF-8解码失败，尝试其他编码
                    try:
                        line_str = line.decode('latin-1', errors='replace')
                    except Exception:
                        logger.warning("⚠️  无法解码响应行，跳过")
                        continue
                logger.debug("1111111111111111111") 
                
                if line_str.startswith('data: '):
                    content = line_str[6:]
                    # 先尝试解析为JSON
                    try:
                        data = json.loads(content)

                        # 兼容 type=complete 的老逻辑
                        s_time = time.time()
                        if data.get('type') == 'complete':
                            s_time = time.time()
                            content_text = data.get('content', '')
                            # 复用原有解析
                            answer_content = self._parse_answer_content(content_text)
                            full_response = answer_content
                            logger.info(f"[complete] ANSWER: {answer_content}")
                            e_time = time.time()
                            logger.info(f"complete 流式响应时间: {e_time - s_time} 秒")
                            break
                        # 新增 type=stream 的处理
                        elif data.get('type') == 'stream':
                            buffer += data.get('content', '')
                            print(f"stream buffer: {buffer}")
                            # 继续累积，直到遇到结尾标记
                            continue
                        else:
                            continue
                    except Exception as e:
                        # 不是JSON，直接累积
                        logger.warning(f"⚠️  JSON解析失败: {e}")
                        buffer += content
                        continue
            end_time = time.time()
            logger.info(f"流式响应时间: {end_time - start_time} 秒")
            
            # 处理累积的 buffer
            #if buffer:
                # 直接使用ANSWER解析逻辑处理累积的buffer
                #answer_content = self._parse_answer_content(buffer)
                #full_response = answer_content
                #print(f"[stream] ANSWER: {answer_content}")
            
            # 返回最终答案
            return full_response if full_response else answer_content if answer_content else "未解析到答案"
        except requests.exceptions.Timeout:
            logger.warning("\n⏰ 请求超时")
            return "请求超时"
        except requests.exceptions.RequestException as e:
            error_msg = f"流式响应失败: {e}"
            logger.error(f"❌ {error_msg}")
            if callback:
                callback('error', error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"流式响应处理异常: {e}"
            logger.error(f"❌ {error_msg}")
            if callback:
                callback('error', error_msg)
            return error_msg
            
    def get_history(self, session_id: Optional[str] = None) -> Dict:
        """
        获取聊天历史
        
        Args:
            session_id: 会话ID
            
        Returns:
            聊天历史记录
        """
        if not session_id:
            session_id = self.session_id
            
        endpoint = f"/api/history/{session_id}"
        result = self._make_request('GET', endpoint)
        
        if "error" not in result:
            history = result.get('history', [])
            logger.info(f"📚 获取到 {len(history)} 条聊天记录")
            return result
        else:
            logger.error(f"❌ 获取历史记录失败: {result['error']}")
            return result
    
    def clear_history(self, session_id: Optional[str] = None) -> Dict:
        """
        清除聊天历史
        
        Args:
            session_id: 会话ID
            
        Returns:
            操作结果
        """
        if not session_id:
            session_id = self.session_id
            
        endpoint = f"/api/clear/{session_id}"
        result = self._make_request('GET', endpoint)
        
        if "error" not in result:
            logger.info(f"🗑️  已清除会话 {session_id} 的历史记录")
            return result
        else:
            logger.error(f"❌ 清除历史记录失败: {result['error']}")
            return result
    
    def test_connection(self) -> bool:
        """
        测试服务器连接
        
        Returns:
            连接是否成功
        """
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)  # 增加超时时间到5秒
            if response.status_code == 200:
                logger.info("✅ 服务器连接正常")
                return True
            else:
                logger.error(f"❌ 服务器响应异常: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 无法连接到服务器: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 连接测试异常: {e}")
            return False


class InteractiveClient:
    """交互式客户端，提供命令行界面"""
    
    def __init__(self, base_url: str = "http://localhost:10800"):
        self.client = QwenAgentClient(base_url)
        self.running = True
        # 默认工具选项
        self.options = [
            {"name": "filesystem", "enabled": True},
            {"name": "memory", "enabled": True},
            {"name": "amap-maps", "enabled": True},
            {"name": "blender", "enabled": True}
        ]
        
    def print_help(self):
        """打印帮助信息"""
        help_text = """
""" + "="*50 + """
🤖 Qwen Agent 交互式客户端
""" + "="*50 + """
命令列表:
  /help     - 显示此帮助信息
  /history  - 显示聊天历史
  /clear    - 清除聊天历史
  /session  - 显示当前会话ID
  /tools    - 显示当前工具选项
  /enable   - 启用工具 (例如: /enable filesystem)
  /disable  - 禁用工具 (例如: /disable blender)
  /test     - 测试服务器连接
  /quit     - 退出客户端
  /exit     - 退出客户端
  其他输入  - 发送聊天消息
""" + "="*50
        logger.info(help_text)
    
    def run(self):
        """运行交互式客户端"""
        logger.info("🚀 启动 Qwen Agent 交互式客户端")
        
        # 测试连接
        if not self.client.test_connection():
            logger.error("❌ 无法连接到服务器，请确保服务器正在运行")
            return
        
        self.print_help()
        
        while self.running:
            try:
                # 获取用户输入
                user_input = input("\n💬 请输入消息 (输入 /help 查看帮助): ").strip()
                
                if not user_input:
                    continue
                
                # 处理命令
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                else:
                    # 发送聊天消息
                    logger.info(f"\n👤 你: {user_input}")
                    logger.info("🤖 助手: ")
                    
                    # 显示当前启用的工具
                    enabled_tools = [opt['name'] for opt in self.options if opt['enabled']]
                    if enabled_tools:
                        logger.info(f"🔧 启用工具: {', '.join(enabled_tools)}")
                    
                    # 使用流式响应
                    self.client.stream_chat(user_input, options=self.options)
                    
            except KeyboardInterrupt:
                logger.info("\n\n👋 再见!")
                break
            except EOFError:
                logger.info("\n\n👋 再见!")
                break
            except Exception as e:
                logger.error(f"\n❌ 发生错误: {e}")
    
    def _handle_command(self, command: str):
        """处理命令"""
        cmd = command.lower()
        
        if cmd in ['/help', '/h']:
            self.print_help()
            
        elif cmd in ['/history', '/hist']:
            history = self.client.get_history()
            if "history" in history:
                logger.info("\n📚 聊天历史:")
                for i, msg in enumerate(history["history"], 1):
                    role = "👤 用户" if msg.get("role") == "user" else "🤖 助手"
                    content = msg.get("content", "")[:100] + "..." if len(msg.get("content", "")) > 100 else msg.get("content", "")
                    logger.info(f"  {i}. {role}: {content}")
            else:
                logger.info("📚 暂无聊天历史")
                
        elif cmd in ['/clear', '/c']:
            result = self.client.clear_history()
            if "error" not in result:
                logger.info("🗑️  聊天历史已清除")
                
        elif cmd in ['/session', '/s']:
            logger.info(f"🆔 当前会话ID: {self.client.session_id}")
            
        elif cmd in ['/tools']:
            logger.info("🔧 当前工具选项:")
            for opt in self.options:
                status = "✅ 启用" if opt['enabled'] else "❌ 禁用"
                logger.info(f"  {opt['name']}: {status}")
                
        elif cmd.startswith('/enable '):
            tool_name = cmd.split(' ', 1)[1].strip()
            for opt in self.options:
                if opt['name'] == tool_name:
                    opt['enabled'] = True
                    logger.info(f"✅ 已启用工具: {tool_name}")
                    break
            else:
                logger.error(f"❌ 未找到工具: {tool_name}")
                
        elif cmd.startswith('/disable '):
            tool_name = cmd.split(' ', 1)[1].strip()
            for opt in self.options:
                if opt['name'] == tool_name:
                    opt['enabled'] = False
                    logger.error(f"❌ 已禁用工具: {tool_name}")
                    break
            else:
                logger.error(f"❌ 未找到工具: {tool_name}")
            
        elif cmd in ['/test', '/t']:
            self.client.test_connection()
            
        elif cmd in ['/quit', '/exit', '/q']:
            logger.info("👋 再见!")
            self.running = False
            
        else:
            logger.warning(f"❓ 未知命令: {command}")
            logger.info("输入 /help 查看可用命令")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Qwen Agent 客户端")
    parser.add_argument("--url", default="http://localhost:10800", 
                       help="服务器URL (默认: http://localhost:10800)")
    parser.add_argument("--query", help="发送单次查询并退出")
    parser.add_argument("--options", help="工具选项，格式: filesystem,memory,amap-maps,blender (用逗号分隔)")
    parser.add_argument("--history", action="store_true", help="显示聊天历史")
    parser.add_argument("--clear", action="store_true", help="清除聊天历史")
    parser.add_argument("--test", action="store_true", help="测试服务器连接")
    
    args = parser.parse_args()
    
    client = QwenAgentClient(args.url)
    
    if args.test:
        client.test_connection()
    elif args.history:
        client.get_history()
    elif args.clear:
        client.clear_history()
    elif args.query:
        # 处理工具选项
        options = None
        options2 = [
            {"name": "filesystem", "enabled": False},
            {"name": "memory", "enabled": True},
            {"name": "amap-maps", "enabled": False},
            {"name": "blender", "enabled": False}
        ]
        args.options = options2
        if args.options:
            available_tools = ["filesystem", "memory", "amap-maps", "blender"]
            enabled_tools = [tool.strip() for tool in args.options.split(',')]
            options = []
            for tool in available_tools:
                options.append({
                    "name": tool,
                    "enabled": tool in enabled_tools
                })
            logger.info(f"🔧 启用工具: {enabled_tools}")
        
        logger.info(f"🤖 发送查询: {args.query}")
        response = client.stream_chat(args.query, options=options)
        logger.info(f"\n📝 完整响应:\n{response}")
    else:
        # 交互式模式
        interactive_client = InteractiveClient(args.url)
        interactive_client.run()


if __name__ == "__main__":
    main() 