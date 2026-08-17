import json
import sys
from typing import Any


def simplify_result(json_str: str) -> str:
    """
    简化JSON字符串中的长文本字段，保留完整结构，将超过100字符的文本截断

    Args:
        json_str: JSON格式的字符串

    Returns:
        处理后的JSON字符串（一行格式）
    """

    def _truncate_text(data: Any) -> Any:
        """
        递归处理数据，截断超过100字符的字符串

        Args:
            data: 待处理的数据

        Returns:
            处理后的数据
        """
        # 处理字符串：超过100字符则截断
        if isinstance(data, str):
            if len(data) > 100:
                return data[:100] + "..."
            return data

        # 处理字典
        if isinstance(data, dict):
            return {key: _truncate_text(value) for key, value in data.items()}

        # 处理列表：长度超过3时，保留前3项，超出部分替换为省略号
        if isinstance(data, list):
            if len(data) > 3:
                kept = [_truncate_text(item) for item in data[:3]]
                kept.append("...")
                return kept
            return [_truncate_text(item) for item in data]

        # 其他类型（数字、布尔、None等）直接返回
        return data

    try:
        parsed = json.loads(json_str)
        simplified = _truncate_text(parsed)
        # 使用默认参数，不添加缩进和空格，输出为一行
        return json.dumps(simplified, ensure_ascii=False, separators=(',', ':'))
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON input"}, ensure_ascii=False, separators=(',', ':'))


if __name__ == "__main__":
    print("JSON文本截断工具 (输入 'exit' 或 'quit' 退出)")
    print("=" * 50)

    while True:
        print("\n请输入JSON数据（多行输入，空行结束）：")

        # 读取多行输入
        lines = []
        try:
            while True:
                line = sys.stdin.readline()
                if not line:  # EOF
                    break
                line = line.strip()
                if line == "":  # 空行表示输入结束
                    break
                if line.lower() in ["exit", "quit"]:  # 退出命令
                    print("程序退出")
                    sys.exit(0)
                lines.append(line)
        except KeyboardInterrupt:
            print("\n程序退出")
            sys.exit(0)

        input_text = "".join(lines)

        if input_text:
            result = simplify_result(input_text)
            print("\n处理结果：")
            print(result)
        else:
            print("未输入任何数据，请重新输入")