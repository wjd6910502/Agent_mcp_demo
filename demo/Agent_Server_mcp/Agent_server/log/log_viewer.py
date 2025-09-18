#!/usr/bin/env python3
"""
日志查看工具
用于实时监控和分析日志文件
"""

import os
import sys
import time
import argparse
from datetime import datetime, timedelta
import re
from pathlib import Path

class LogViewer:
    """日志查看器"""
    
    def __init__(self, log_dir='logs'):
        self.log_dir = Path(log_dir)
        self.log_files = {
            'main': self.log_dir / 'agent_server.log',
            'error': self.log_dir / 'error.log',
            'chat': self.log_dir / 'chat.log',
            'performance': self.log_dir / 'performance.log'
        }
    
    def list_log_files(self):
        """列出所有日志文件"""
        print("可用的日志文件:")
        for name, path in self.log_files.items():
            if path.exists():
                size = path.stat().st_size
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                print(f"  {name}: {path} ({size} bytes, 修改时间: {mtime})")
            else:
                print(f"  {name}: {path} (文件不存在)")
    
    def tail_log(self, log_type='main', lines=50, follow=False, filter_level=None, filter_session=None):
        """查看日志尾部"""
        log_file = self.log_files.get(log_type)
        if not log_file or not log_file.exists():
            print(f"日志文件不存在: {log_file}")
            return
        
        print(f"正在查看 {log_type} 日志文件: {log_file}")
        print("-" * 80)
        
        # 读取文件内容
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        
        # 过滤和显示
        filtered_lines = self._filter_lines(all_lines, filter_level, filter_session)
        
        # 显示最后N行
        display_lines = filtered_lines[-lines:] if lines > 0 else filtered_lines
        
        for line in display_lines:
            print(line.rstrip())
        
        # 实时跟踪
        if follow:
            print("\n开始实时跟踪日志 (按 Ctrl+C 停止)...")
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    # 移动到文件末尾
                    f.seek(0, 2)
                    
                    while True:
                        line = f.readline()
                        if line:
                            if self._should_display_line(line, filter_level, filter_session):
                                print(line.rstrip())
                        else:
                            time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n停止跟踪")
    
    def _filter_lines(self, lines, filter_level=None, filter_session=None):
        """过滤日志行"""
        filtered = []
        for line in lines:
            if self._should_display_line(line, filter_level, filter_session):
                filtered.append(line)
        return filtered
    
    def _should_display_line(self, line, filter_level=None, filter_session=None):
        """判断是否应该显示该行"""
        if filter_level:
            if not re.search(rf'\b{filter_level.upper()}\b', line):
                return False
        
        if filter_session:
            if not re.search(rf'\b{filter_session}\b', line):
                return False
        
        return True
    
    def search_logs(self, pattern, log_types=None, case_sensitive=False):
        """搜索日志"""
        if log_types is None:
            log_types = ['main', 'error', 'chat', 'performance']
        
        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)
        
        print(f"在日志中搜索模式: {pattern}")
        print("=" * 80)
        
        for log_type in log_types:
            log_file = self.log_files.get(log_type)
            if not log_file or not log_file.exists():
                continue
            
            print(f"\n在 {log_type} 日志中搜索:")
            print("-" * 40)
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if regex.search(line):
                        print(f"  {log_type}:{line_num}: {line.rstrip()}")
    
    def get_stats(self, hours=24):
        """获取日志统计信息"""
        print(f"最近 {hours} 小时的日志统计:")
        print("=" * 50)
        
        since_time = datetime.now() - timedelta(hours=hours)
        
        for log_type, log_file in self.log_files.items():
            if not log_file.exists():
                continue
            
            stats = {
                'total_lines': 0,
                'error_count': 0,
                'warning_count': 0,
                'info_count': 0,
                'debug_count': 0,
                'recent_lines': 0
            }
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    stats['total_lines'] += 1
                    
                    # 检查日志级别
                    if 'ERROR' in line:
                        stats['error_count'] += 1
                    elif 'WARNING' in line:
                        stats['warning_count'] += 1
                    elif 'INFO' in line:
                        stats['info_count'] += 1
                    elif 'DEBUG' in line:
                        stats['debug_count'] += 1
                    
                    # 检查时间戳
                    try:
                        # 尝试解析时间戳
                        timestamp_str = line.split(' - ')[0]
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        if timestamp >= since_time:
                            stats['recent_lines'] += 1
                    except:
                        pass
            
            print(f"\n{log_type} 日志:")
            print(f"  总行数: {stats['total_lines']}")
            print(f"  最近 {hours} 小时: {stats['recent_lines']}")
            print(f"  错误: {stats['error_count']}")
            print(f"  警告: {stats['warning_count']}")
            print(f"  信息: {stats['info_count']}")
            print(f"  调试: {stats['debug_count']}")
    
    def monitor_errors(self, follow=False):
        """监控错误日志"""
        print("监控错误日志...")
        self.tail_log('error', lines=0, follow=follow, filter_level='ERROR')
    
    def monitor_chat(self, follow=False, session_id=None):
        """监控聊天日志"""
        print("监控聊天日志...")
        self.tail_log('chat', lines=0, follow=follow, filter_session=session_id)
    
    def monitor_performance(self, follow=False):
        """监控性能日志"""
        print("监控性能日志...")
        self.tail_log('performance', lines=0, follow=follow)

def main():
    parser = argparse.ArgumentParser(description='日志查看工具')
    parser.add_argument('command', choices=['list', 'tail', 'search', 'stats', 'errors', 'chat', 'perf'],
                       help='要执行的命令')
    parser.add_argument('--log-dir', default='logs', help='日志目录')
    parser.add_argument('--type', choices=['main', 'error', 'chat', 'performance'], default='main',
                       help='日志类型')
    parser.add_argument('--lines', type=int, default=50, help='显示的行数')
    parser.add_argument('--follow', '-f', action='store_true', help='实时跟踪')
    parser.add_argument('--level', help='过滤日志级别')
    parser.add_argument('--session', help='过滤会话ID')
    parser.add_argument('--pattern', help='搜索模式')
    parser.add_argument('--hours', type=int, default=24, help='统计时间范围(小时)')
    parser.add_argument('--case-sensitive', action='store_true', help='区分大小写搜索')
    
    args = parser.parse_args()
    
    viewer = LogViewer(args.log_dir)
    
    if args.command == 'list':
        viewer.list_log_files()
    
    elif args.command == 'tail':
        viewer.tail_log(args.type, args.lines, args.follow, args.level, args.session)
    
    elif args.command == 'search':
        if not args.pattern:
            print("错误: 搜索命令需要 --pattern 参数")
            sys.exit(1)
        viewer.search_logs(args.pattern, [args.type], args.case_sensitive)
    
    elif args.command == 'stats':
        viewer.get_stats(args.hours)
    
    elif args.command == 'errors':
        viewer.monitor_errors(args.follow)
    
    elif args.command == 'chat':
        viewer.monitor_chat(args.follow, args.session)
    
    elif args.command == 'perf':
        viewer.monitor_performance(args.follow)

if __name__ == '__main__':
    main() 