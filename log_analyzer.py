#!/usr/bin/env python3
import argparse
import os
import re
from collections import defaultdict


class LogAnalyzer:
    LOG_PATTERN = re.compile(
        r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (ERROR|WARN|INFO) (.*)$"
    )

    def __init__(self, file_path):
        self.file_path = file_path
        self.logs = []
        self.invalid_lines = 0

    def parse_logs(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"文件不存在: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                match = self.LOG_PATTERN.match(line)
                if match:
                    self.logs.append(
                        {
                            "date": match.group(1),
                            "time": match.group(2),
                            "level": match.group(3),
                            "message": match.group(4),
                            "hour": match.group(2)[:2],
                        }
                    )
                else:
                    self.invalid_lines += 1

    def filter_errors(self):
        return [log for log in self.logs if log["level"] == "ERROR"]

    def count_by_level(self):
        counts = defaultdict(int)
        for log in self.logs:
            counts[log["level"]] += 1
        return dict(counts)

    def count_by_hour(self):
        counts = defaultdict(int)
        for log in self.logs:
            hour_key = f"{log['date']} {log['hour']}:00"
            counts[hour_key] += 1
        return dict(sorted(counts.items()))


def print_bar_chart(counts):
    max_count = max(counts.values()) if counts else 0
    
    if max_count <= 0:
        scale = 1
    elif max_count <= 12:
        scale = 1
    elif max_count <= 24:
        scale = 2
    elif max_count <= 60:
        scale = 5
    else:
        scale = 10
    
    for level in ["ERROR", "WARN", "INFO"]:
        count = counts.get(level, 0)
        if count == 0:
            bars = ""
        else:
            full_bars = count // scale
            remainder = count % scale
            
            bars = "█" * full_bars
            if remainder > 0 and scale > 1:
                bars += "·"
        
        print(f"{level:6} | {bars} ({count}条)")


def main():
    parser = argparse.ArgumentParser(
        description="Python 命令行日志分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python log_analyzer.py errors app.log     显示所有 ERROR 级别日志
  python log_analyzer.py stats app.log      统计各级别日志数量并显示柱状图
  python log_analyzer.py timeline app.log   按小时统计日志数量
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="可用的子命令")

    subparsers.add_parser("errors", help="筛选出所有 ERROR 级别的日志")
    subparsers.add_parser("stats", help="统计各级别日志数量并显示柱状图")
    subparsers.add_parser("timeline", help="按小时统计日志数量")

    args, remaining = parser.parse_known_args()

    if not args.command:
        parser.print_help()
        return

    if len(remaining) != 1:
        print(f"错误: {args.command} 子命令需要一个日志文件路径参数")
        parser.print_help()
        return

    file_path = remaining[0]

    try:
        analyzer = LogAnalyzer(file_path)
        analyzer.parse_logs()

        if analyzer.invalid_lines > 0:
            print(f"警告: 跳过了 {analyzer.invalid_lines} 行格式不匹配的日志")
            print()

        if args.command == "errors":
            errors = analyzer.filter_errors()
            if errors:
                for log in errors:
                    print(f"{log['date']} {log['time']} {log['level']} {log['message']}")
            else:
                print("没有找到 ERROR 级别的日志")

        elif args.command == "stats":
            counts = analyzer.count_by_level()
            print("日志级别统计:")
            print_bar_chart(counts)

        elif args.command == "timeline":
            counts = analyzer.count_by_hour()
            print("按小时统计日志数量:")
            for hour, count in counts.items():
                print(f"{hour} | {count} 条")

    except FileNotFoundError as e:
        print(f"错误: {e}")
    except Exception as e:
        print(f"错误: 处理文件时发生异常 - {e}")


if __name__ == "__main__":
    main()
