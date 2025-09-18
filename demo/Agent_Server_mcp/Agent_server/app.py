from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pprint
import urllib.parse
import json
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool
from qwen_agent.utils.output_beautify import typewriter_print
import pandas as pd
import threading
import queue
import time
import logging
import os
import tempfile
import time
from datetime import datetime
from log.log_config import logger, chat_logger, perf_logger


app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 全局变量存储聊天历史
chat_history = {}
response_queues = {}

# Step 2: Configure the LLM you are using.
llm_cfg = {
    # Use the model service provided by DashScope:
    # 'model': 'qwen-max-latest',
    # 'model_type': 'qwen_dashscope',
    # 'api_key': 'YOUR_DASHSCOPE_API_KEY',
    # It will use the `DASHSCOPE_API_KEY' environment variable if 'api_key' is not set here.

    # Use a model service compatible with the OpenAI API, such as vLLM or Ollama:
    'model': 'qwen-plus',
    #'model': 'qwq-32b'i,

    #'model':'Qwen3-8B',
    #'model': 'qwen-max',
    'model_server': 'https://dashscope.aliyuncs.com/compatible-mode/v1',  # base_url, also known as api_base
    'api_key': 'sk-xxxxxx',

    #gpu
    #'model': 'unsloth/Qwen3-8B-GGUF',
    #'model':'Qwen3-8B-AWQ',
    #'model_server': 'https://ms-ens-21b18903-a0b0.api-inference.modelscope.cn/v1',  # base_url, also known as api_base
    #'api_key': 'xxxxxxx', 

    # 8b 量化模型
    #'model':'unsloth/Qwen3-8B-GGUF',
    #'model':'Qwen/Qwen3-8B-GGUF',
    #'model_server': 'https://ms-fc-6712b9d2-2667.api-inference.modelscope.cn/v1',  # base_url, also known as api_base
    #'api_key': 'xxxx',
    # (Optional) LLM hyperparameters for generation:
    #'generate_cfg': {
    #    'temperature':0,
    #    'repetition_penalty':0.5
    #}
}

# Step 3: Create an agent. Here we use the `Assistant` agent as an example, which is capable of using tools and reading files.
system_instruction = '''After receiving the user's request, you should:
- first draw an image and obtain the image url,
- then run code `request.get(image_url)` to download the image,
- and finally select an image operation from the given document to process the image.
Please show the image using `plt.show()`.'''

tools = [{  
    "mcpServers": {  
        # 文件系统访问工具  
        "filesystem": {  
            "command": "npx",  
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/kylin"]  
        },  
        # SQLite 数据库工具    
        # 内存管理工具  
        "memory": {  
            "command": "npx",  
            "args": ["-y", "@modelcontextprotocol/server-memory"]  
        },
        "amap-maps": {
            "command": "npx",
            "args": [
                "-y",
                "@amap/amap-maps-mcp-server"
            ],
            "env": {
                "AMAP_MAPS_API_KEY": "63fa842ec9b7775e456f01d7e03fd399"
            }
        },
        "blender": {
            "command": "uv",
            "args": [
                "tool",
                "run",
                "--index-url",
                "https://pypi.tuna.tsinghua.edu.cn/simple",
                "--cache-dir",
                "~/.blender_cache",
                "blender-mcp"
            ]
        },
         # Playwright 浏览器自动化服务
        "playwright": {
            "command": "npx",
            "args": [
                "-y",
                "@playwright/mcp@latest"
            ],
            "env": {
                "PLAYWRIGHT_BROWSERS_PATH": playwright_temp_dir,
                "PLAYWRIGHT_CACHE_DIR": playwright_temp_dir,
                "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "0",
                "TMPDIR": playwright_temp_dir,
                "TEMP": playwright_temp_dir,
                "TMP": playwright_temp_dir,
                "PLAYWRIGHT_ARTIFACTS_DIR": os.path.join(playwright_temp_dir, "artifacts"),
                "PLAYWRIGHT_DOWNLOAD_HOST": "https://playwright.azureedge.net/",
                "PLAYWRIGHT_BROWSERS_PATH_0": playwright_temp_dir
            }
        },


    }  
}]

# 不带工具的机器人
bot_base = Assistant(llm=llm_cfg,
                #system_message=system_instruction,
                #function_list=tools,
                files=[])
# 创建全局bot实例
# bot = Assistant(llm=llm_cfg,
#                 #system_message=system_instruction,
#                 function_list=tools,
#                 files=[])

system_instruction = '''在判断 PDF 文件的文件名是否重复时，若两个 PDF 文件的完整文件名（主文件名 + 扩展名）完全相同（不区分大小写），则判定为重复，例如 “会议记>
录.pdf” 与 “会议记录.PDF”“Huiyi.pdf” 与 “huiyi.pdf” 均视为重复，且文件名（包括主
文件名和扩展名）的大小写不影响重复判断，即大小写差异不视为文件名不同，而仅主文件名部分相似但不完全一致的 PDF 文件，即使扩展名均为.pdf，也不判定为重复，例如 “合>
同 1.pdf” 与 “合同 2.pdf”“方案初稿.pdf” 与 “方案终稿.pdf” 均不算重复，同时文件名中包含的空格、标点符号（如 “，”“.”“（）”）、特殊符号（如 “#”“@”“_” 等）均视为有>
效字符，需严格比对，例如 “资料 (副本).pdf” 与 “资料 (副本).pdf”（空格差异）、“资料 (copy).pdf” 与 “资料 (copy).pdf”（空格差异）、“list#1.pdf” 与 “list@1.pdf”（>特殊符号差异）均判定为重复，若文件名存在不可见字符（如全角 / 半角空格差异），例>如 “文件 1.pdf”（半角空格）与 “文件　1.pdf”（全角空格）也判定为重复，辅助判断使>用文件大小来判断，如果大小一致，为重复，尾部标记有copy的也视为重复,尾部标记有副>本的也视为重复,禁止使用filesystem-read,filesystem-read_multiple_files接口'''


bot = Assistant(llm=llm_cfg,
                system_message=system_instruction,
                function_list=tools,
                files=[])
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

logger.info("Agent server initialized successfully")

def process_chat(session_id, query, options=None):
    """处理聊天请求的后台线程"""
    if options is None:
        options = []
    start_time = time.time()
    chat_logger.log_chat_start(session_id, query)
    
    # 记录接收到的选项
    if options:
        logger.info(f"Received options for session {session_id}: {options}")
        for option in options:
            if isinstance(option, dict) and 'name' in option and 'enabled' in option:
                logger.info(f"Option: {option['name']} = {option['enabled']}")
    
    # 定义一个map，key是name，value是enabled
    option_prompt_map = {
        "amap-maps": "可以使用高德地图工具",
        "blender": "可以使用Blender工具",
        "filesystem": "可以使用文件系统工具",
        "memory": "可以使用内存工具"
    }

    #根据option是否打开，拼接出提示词，并且使用bot_base 调用模型，使用当前提示词，都是这个工具可以支持
    option_prompt = ""
    for option in options:
        if option['enabled']:
            option_prompt += option_prompt_map[option['name']] + "\n"
    logger.info(f"Option prompt: {option_prompt}")
    query1 = f"你是一个工具使用专家，目前支持{option_prompt}，如果执行如下命令{query},返回是否可以执行，结果只有yes或者no"
    
    # 获取bot_base的响应结果
    response_result = ""
    for response in bot_base.run(messages=[{'role': 'user', 'content': query1}]):
        if isinstance(response, dict) and 'content' in response:
            response_result += response['content']
        elif isinstance(response, list):
            for item in response:
                if isinstance(item, dict) and 'content' in item:
                    response_result += item['content']
    
    # 解析结果并打印
    response_result = response_result.lower().strip()
    bExec = False
    if 'yes' in response_result:
        print("yes")
        bExec = True
        logger.info("Tool availability check result: yes")
    else:
        print("no")
        logger.info("Tool availability check result: no")
    if 1:
        bExec = True

    if bExec == False:
        response_queues[session_id].put({
            'type': 'complete',
            'content': "工具不可用，请检查工具是否打开",  # 只发送新增内容
            'full_content': "工具不可用，请检查工具是否打开",  # 保留完整内容用于调试
            'timestamp': time.time()
        })
        logger.info(f"Tool availability check result: yes, can execute")
        return

    try:
        # 获取或创建会话历史
        
        if session_id not in chat_history:
            chat_history[session_id] = []
            logger.info(f"Created new chat history for session {session_id}")
        
        #messages = chat_history[session_id]
        
        # 清除上下文 TODO：
        messages = []

        # 添加系统提示词
        pre_prompt = """在判断 PDF 文件的文件名是否重复时，若两个 PDF 文件的完整文件名（主文件名 + 扩展名）完全相同（不区分大小写），则判定为重复，例如 “会议记录.pdf” 与 “会议记录.PDF”“Huiyi.pdf” 与 “huiyi.pdf” 均视为重复，且文件名（包括主文件名和扩展名）的大小写不影响重复判断，即大小写差异不视为文件名不同，而仅主文件名部分相似但不完全一致的 PDF 文件，即使扩展名均为.pdf，也不判定为重复，例如 “合同 1.pdf” 与 “合同 2.pdf”“方案初稿.pdf” 与 “方案终稿.pdf” 均不算重复，同时文件名中包含的空格、标点符号（如 “，”“.”“（）”）、特殊符号（如 “#”“@”“_” 等）均视为有效字符，需严格比对，例如 “资料 (副本).pdf” 与 “资料 (副本).pdf”（空格差异）、“资料 (copy).pdf” 与 “资料 (copy).pdf”（空格差异）、“list#1.pdf” 与 “list@1.pdf”（特殊符号差异）均判定为重复，若文件名存在不可见字符（如全角 / 半角空格差异），例如 “文件 1.pdf”（半角空格）与 “文件　1.pdf”（全角空格）也判定为重复，辅助判断使用文件大小来判断，如果大小一致，为重复，尾部标记有copy的也视为重复,尾部标记有副本的也视为重复,禁止使用filesystem-read,filesystem-read_multiple_files接口,"""

        # 添加系统消息
       # messages.append({'role': 'system', 'content': system_prompt})
        query_new = "" 
        if 'MCP' in query or 'pdf' in query:
            import shutil
            import os
            if os.path.exists("/home/kylin/桌面/临时") and os.path.isdir("/home/kylin/桌面/临时"):
                shutil.rmtree("/home/kylin/桌面/临时")
            query_new = pre_prompt +"/n 删除上一次文件重复操作标记，每次都重新开始标记重复文件" + '#背景# /home/kylin/桌面/MCP 存在一定的重复文件，对这些重复文件进行去重，并且移动到临时文件,如果没有重复的，不做任何操作, "/n" #目的# 将"/home/kylin/桌面/MCP"重复文件移动到"/home/kylin/桌面/临时"文件夹下  "/n" #任务步骤# 1. 创建"/home/kylin/桌面/临时"文件夹 "/n" 2.判断"/home/kylin/桌面/MCP"文件夹下是否有重复文件，并且列出来,如果"/home/kylin/桌面/MCP"下文件存在重复，执行3，否则执行4 "/n" 3.将"/home/kylin/桌面/MCP"重复的文件移至"/home/kylin/桌面/临时"文件夹下 "/n"  4.列出所有不重复文件  '
        elif 'blender' in query and '五角星' in query:
            query_new = '读取/home/kylin目录下"test_mcp_blender"文件夹下的wujiaox.py，读取内部内容，让blender按内容代码执行'
        elif 'blender' in query and '汽车模型' in query:
            query_new = '读取/home/kylin目录下“test_mcp_blender"文件夹下的simple_fbx_import_car_yellow.py，读取内部内容，让blender按内容代码执行'
        else:
            query_new = query 
        messages.append({'role': 'user', 'content': query_new})
        chat_logger.log_user_message(session_id, query)
        
        response_plain_text = ''
        response_messages = []
        last_sent_content = ''  # 记录上次发送的内容长度
        
        logger.info(f"Starting bot.run for session {session_id}")
        
        # 处理响应
        start_time = time.time()
        for response in bot.run(messages=messages):
            try:
                #response_messages = []
                # 检查响应对象的结构
                if isinstance(response, dict):
                    # 如果是字典，直接添加到响应消息列表
                    response_messages.append(response)
                    logger.debug(f"Received dict response: {type(response)}")
                elif isinstance(response, list):
                    # 如果是列表，扩展响应消息列表
                    response_messages.extend(response)
                    logger.debug(f"Received list response with {len(response)} items")
                else:
                    # 其他类型，尝试转换为字典
                    logger.warning(f"Unknown response type: {type(response)}")
                    continue
                
                # 流式输出处理 - 传递消息列表
                if response_messages:
                    response_plain_text = typewriter_print(response_messages, response_plain_text)
                    
                    # 解析Answer之后的数据
                    answer_content = parse_answer_content(response_plain_text)
                    
                    # 判断answer_content是否包含toolcall和tool response
                    has_toolcall = 'toolcall' in answer_content.lower() or 'tool_call' in answer_content.lower()
                    has_tool_response = 'tool response' in answer_content.lower() or 'tool_response' in answer_content.lower()
                    
                    # 根据条件决定返回内容
                    if has_toolcall and has_tool_response:
                        current_content = answer_content
                        logger.info(f"返回answer_content (包含toolcall和tool response)")
                    else:
                        current_content = response_plain_text
                        logger.info(f"返回response_plain_text (不包含toolcall和tool response)")
                    
                    # 流式采样插入：只发送新增的内容
                    if len(current_content) > len(last_sent_content):
                        # 计算新增内容
                        new_content = current_content[len(last_sent_content):]
                        last_sent_content = current_content
                        #print(f"************************************************\n") 
                        #print(f" stream new_contnt = {new_content}\n") 
                        #rint(f"************************************************\n") 
                        # 将新增内容发送到队列
                        if session_id in response_queues:
                            response_queues[session_id].put({
                                'type': 'stream',
                                'content': new_content,  # 只发送新增内容
                                'full_content': '' ,  # 保留完整内容用于调试
                                'timestamp': time.time()
                            })
                            logger.info(f"{session_id}, stream, {new_content}")
                            chat_logger.log_chat_response(session_id, 'stream', len(new_content))
                    
            except Exception as e:
                logger.error(f"Error processing response: {e}", exc_info=True)
                chat_logger.log_chat_error(session_id, str(e))
                # 发送错误信息到队列
                if session_id in response_queues:
                    response_queues[session_id].put({
                        'type': 'error',
                        'content': f"处理响应时出错: {str(e)}",
                        'timestamp': time.time()
                    })
                #print("************************************************break\n") 
                break
        #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@!!!!!!!!!complete_content=", complete_content)
        # 更新聊天历史
        if response_messages:
            messages.extend(response_messages)
            logger.info(f"Updated chat history for session {session_id} with {len(response_messages)} messages")
            chat_logger.log_bot_message(session_id, response_plain_text)
        
        # 发送完成信号
        if session_id in response_queues:
            # 解析最终的Answer内容
            final_answer_content = parse_answer_content(response_plain_text)
            
            # 判断final_answer_content是否包含toolcall和tool response
            has_toolcall = 'toolcall' in final_answer_content.lower() or 'tool_call' in final_answer_content.lower()
            has_tool_response = 'tool response' in final_answer_content.lower() or 'tool_response' in final_answer_content.lower()
            
            # 根据条件决定返回内容
            if has_toolcall and has_tool_response:
                complete_content = final_answer_content
                logger.info(f"完成信号返回answer_content (包含toolcall和tool response)") 
            else:
                complete_content = response_plain_text
                logger.info(f"完成信号返回response_plain_text (不包含toolcall和tool response)")
            #print("************************************************\n") 
            #print("!!!!!!!!!response_plain_text=", response_plain_text) 
            #print("************************************************\n") 
            #response_queues[session_id].put({
            #    'type': 'complete',
            #    'content': response_plain_text,
            #    'timestamp': time.time()
            #})
            if final_answer_content == "":
                response_queues[session_id].put({
                    'type': 'complete',
                    'content': "任务处理已完成。",
                    'timestamp': time.time()
                })
            else:
                response_queues[session_id].put({
                    'type': 'complete',
                    'content': response_plain_text,
                    'timestamp': time.time()
                })
            #print("!!!!!!!!!complete_content=", complete_content) 
        end_time = time.time()
        print(f"总共流式响应时间: {end_time - start_time} 秒")
        # 记录处理时间
        duration = end_time - start_time
        chat_logger.log_chat_complete(session_id, duration)
        perf_logger.log_bot_processing(session_id, duration)
            
    except Exception as e:
        logger.error(f"Error in chat processing for session {session_id}: {e}", exc_info=True)
        chat_logger.log_chat_error(session_id, str(e))
        # 发送错误信号
        if session_id in response_queues:
            response_queues[session_id].put({
                'type': 'error',
                'content': str(e),
                'timestamp': time.time()
            })

@app.route('/')
def index():
    """主页"""
    logger.info("Homepage accessed")
    return jsonify({
        'status': 'running',
        'service': 'Agent Server',
        'version': '1.0.0',
        'endpoints': {
            'chat': '/api/chat',
            'stream': '/api/stream/<session_id>?incremental=true',  # 支持增量更新模式
            'history': '/api/history/<session_id>',
            'clear': '/api/clear/<session_id>',
            'health': '/api/health'
        },
        'features': {
            'incremental_streaming': '支持增量流式更新，减少数据传输量',
            'streaming_modes': {
                'incremental': '?incremental=true (默认) - 只发送新增内容',
                'full': '?incremental=false - 发送完整内容'
            }
        }
    })

@app.route('/api/health')
def health_check():
    """健康检查端点"""
    logger.info("Health check requested")
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'Agent Server'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天API接口"""
    start_time = time.time()
    logger.info("Chat API endpoint called")
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        session_id = data.get('session_id', 'default')
        # 接收一组字典，每个字典包含一个字符串和一个布尔值
        options = data.get('options', [])  # 格式: [{"name": "string", "enabled": bool}, ...]

        logger.info(f"Chat request - Session: {session_id}, Query length: {len(query)}, Options count: {len(options)}")
        
        if not query:
            logger.warning("Empty query received")
            duration = time.time() - start_time
            perf_logger.log_api_call('/api/chat', 'POST', duration, 400)
            return jsonify({'error': 'Query is required'}), 400
        
        # 创建响应队列
        if session_id not in response_queues:
            response_queues[session_id] = queue.Queue()
            logger.info(f"Created response queue for session {session_id}")
        
        # 启动后台处理线程
        thread = threading.Thread(target=process_chat, args=(session_id, query, options))
        thread.daemon = True
        thread.start()
        
        logger.info(f"Started processing thread for session {session_id}")
        
        duration = time.time() - start_time
        perf_logger.log_api_call('/api/chat', 'POST', duration, 200)
        
        return jsonify({
            'status': 'processing',
            'session_id': session_id,
            'message': 'Chat request received and processing started'
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        duration = time.time() - start_time
        perf_logger.log_api_call('/api/chat', 'POST', duration, 500)
        return jsonify({'error': str(e)}), 500

@app.route('/api/stream/<session_id>')
def stream(session_id):
    """流式响应接口"""
    # 获取查询参数，支持增量更新模式
    incremental = request.args.get('incremental', 'true').lower() == 'true'
    logger.info(f"Stream endpoint accessed for session {session_id}, incremental mode: {incremental}")
    
    def generate():
        if session_id not in response_queues:
            logger.warning(f"Session {session_id} not found in response queues")
            yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
            return
        
        accumulated_content = ''  # 累积内容，用于增量模式
        
        try:
            while True:
                try:
                    # 从队列获取响应，设置超时 - 减少超时时间从30秒到10秒
                    response = response_queues[session_id].get(timeout=10)
                    
                    # 处理增量更新
                    if incremental and response['type'] == 'stream':
                        # 增量模式：只发送新增内容
                        accumulated_content += response['content']
                        stream_response = {
                            'type': 'stream',
                            'content': response['content'],  # 新增内容
                            'accumulated_content': "streaming",  # 累积的完整内容
                            'timestamp': response['timestamp']
                        }
                    else:
                        # 非增量模式：发送完整内容
                        stream_response = response
                    
                    yield f"data: {json.dumps(stream_response)}\n\n"
                    
                    # 如果是完成或错误，结束流
                    if response['type'] in ['complete', 'error']:
                        logger.info(f"Stream ended for session {session_id} with type: {response['type']}")
                        break
                        
                except queue.Empty:
                    # 发送心跳保持连接
                    logger.debug(f"Sending heartbeat for session {session_id}")
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"
                    
        except Exception as e:
            logger.error(f"Error in stream generation for session {session_id}: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        finally:
            # 清理队列
            if session_id in response_queues:
                del response_queues[session_id]
                logger.info(f"Cleaned up response queue for session {session_id}")
    
    return app.response_class(generate(), mimetype='text/plain')

@app.route('/api/history/<session_id>')
def get_history(session_id):
    """获取聊天历史"""
    logger.info(f"History requested for session {session_id}")
    if session_id in chat_history:
        history_count = len(chat_history[session_id])
        logger.info(f"Returning {history_count} messages for session {session_id}")
        return jsonify({'history': chat_history[session_id]})
    else:
        logger.info(f"No history found for session {session_id}")
        return jsonify({'history': []})

@app.route('/api/clear/<session_id>')
def clear_history(session_id):
    """清除聊天历史"""
    logger.info(f"Clearing history for session {session_id}")
    if session_id in chat_history:
        del chat_history[session_id]
        logger.info(f"History cleared for session {session_id}")
    return jsonify({'message': 'History cleared'})

# 添加错误处理器
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.url}")
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Agent Server on port 10800")
    app.run(debug=False, host='0.0.0.0', port=10800)
