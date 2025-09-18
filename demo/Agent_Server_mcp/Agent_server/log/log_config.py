import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class LogConfig:
    """日志配置类"""
    
    def __init__(self, log_dir='logs', app_name='agent_server'):
        self.log_dir = log_dir
        self.app_name = app_name
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def setup_logger(self, name=None, level=logging.DEBUG):
        """设置日志器"""
        logger_name = name or self.app_name
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        
        # 清除已有的处理器
        logger.handlers.clear()
        
        # 添加处理器
        self._add_console_handler(logger)
        self._add_file_handlers(logger)
        
        return logger
    
    def _add_console_handler(self, logger):
        """添加控制台处理器"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 控制台格式化器 - 简洁格式
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    def _add_file_handlers(self, logger):
        """添加文件处理器"""
        # 主日志文件 - 所有级别
        main_handler = RotatingFileHandler(
            os.path.join(self.log_dir, f'{self.app_name}.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setLevel(logging.DEBUG)
        
        # 详细格式化器
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        main_handler.setFormatter(detailed_formatter)
        logger.addHandler(main_handler)
        
        # 错误日志文件 - 仅错误级别
        error_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'error.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
        
        # 聊天日志文件 - 聊天相关日志
        chat_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'chat.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        chat_handler.setLevel(logging.INFO)
        
        # 聊天专用格式化器
        chat_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        chat_handler.setFormatter(chat_formatter)
        logger.addHandler(chat_handler)
        
        # 性能日志文件 - 性能相关日志
        perf_handler = TimedRotatingFileHandler(
            os.path.join(self.log_dir, 'performance.log'),
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.INFO)
        perf_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        perf_handler.setFormatter(perf_formatter)
        logger.addHandler(perf_handler)

class ChatLogger:
    """聊天专用日志器"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def log_chat_start(self, session_id, query):
        """记录聊天开始"""
        self.logger.info(f"[CHAT_START] Session: {session_id} | Query: {query[:100]}{'...' if len(query) > 100 else ''}")
    
    def log_chat_response(self, session_id, response_type, content_length=0):
        """记录聊天响应"""
        self.logger.info(f"[CHAT_RESPONSE] Session: {session_id} | Type: {response_type} | Length: {content_length}")
    
    def log_chat_error(self, session_id, error):
        """记录聊天错误"""
        self.logger.error(f"[CHAT_ERROR] Session: {session_id} | Error: {error}")
    
    def log_chat_complete(self, session_id, duration=None):
        """记录聊天完成"""
        duration_str = f" | Duration: {duration:.2f}s" if duration else ""
        self.logger.info(f"[CHAT_COMPLETE] Session: {session_id}{duration_str}")
    
    def log_user_message(self, session_id, message):
        """记录用户消息"""
        self.logger.info(f"[USER_MSG] Session: {session_id} | Message: {message[:100]}{'...' if len(message) > 100 else ''}")
    
    def log_bot_message(self, session_id, message):
        """记录机器人消息"""
        self.logger.info(f"[BOT_MSG] Session: {session_id} | Message: {message[:100]}{'...' if len(message) > 100 else ''}")

class PerformanceLogger:
    """性能专用日志器"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def log_api_call(self, endpoint, method, duration, status_code=200):
        """记录API调用性能"""
        self.logger.info(f"[API_PERF] {method} {endpoint} | Duration: {duration:.3f}s | Status: {status_code}")
    
    def log_bot_processing(self, session_id, duration):
        """记录机器人处理性能"""
        self.logger.info(f"[BOT_PERF] Session: {session_id} | Processing time: {duration:.3f}s")
    
    def log_memory_usage(self, memory_mb):
        """记录内存使用情况"""
        self.logger.info(f"[MEMORY] Current usage: {memory_mb:.2f} MB")

# 全局日志配置实例
log_config = LogConfig()
logger = log_config.setup_logger()
chat_logger = ChatLogger(logger)
perf_logger = PerformanceLogger(logger)

def get_logger(name=None):
    """获取日志器"""
    return log_config.setup_logger(name)

def get_chat_logger():
    """获取聊天日志器"""
    return chat_logger

def get_perf_logger():
    """获取性能日志器"""
    return perf_logger 