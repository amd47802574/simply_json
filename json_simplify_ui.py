"""
JSON 长文本截断工具 - 图形界面版

基于 simplify_json_result_long_text.py 的核心逻辑，
提供可视化的输入/输出界面。将 JSON 中超过指定长度的字符串截断。
"""

import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Any


# ---------------------------------------------------------------------------
# 核心处理逻辑（与 simplify_json_result_long_text.py 保持一致）
# ---------------------------------------------------------------------------
def simplify_result(json_str: str, max_len: int = 100) -> str:
    """简化 JSON 字符串中的长文本字段，将超过 max_len 字符的文本截断。

    Args:
        json_str: JSON 格式的字符串
        max_len: 字符串截断阈值（默认 100）

    Returns:
        处理后的 JSON 字符串（一行格式）
    """

    def _truncate_text(data: Any) -> Any:
        if isinstance(data, str):
            if len(data) > max_len:
                return data[:max_len]
            return data
        if isinstance(data, dict):
            return {key: _truncate_text(value) for key, value in data.items()}
        if isinstance(data, list):
            if len(data) > 3:
                return [_truncate_text(item) for item in data[:3]]
            return [_truncate_text(item) for item in data]
        return data

    try:
        parsed = json.loads(json_str)
        simplified = _truncate_text(parsed)
        return json.dumps(simplified, ensure_ascii=False, separators=(',', ':'))
    except json.JSONDecodeError:
        raise


# ---------------------------------------------------------------------------
# UI 界面
# ---------------------------------------------------------------------------
class JsonSimplifyApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("JSON 长文本截断工具")
        self.root.geometry("900x600")
        self.root.minsize(640, 420)

        # 主题色
        self.bg = "#f5f6f8"
        self.accent = "#3b82f6"
        self.root.configure(bg=self.bg)

        self._build_widgets()

    def _build_widgets(self) -> None:
        # 顶部标题栏
        header = tk.Frame(self.root, bg=self.accent, height=48)
        header.pack(fill=tk.X)
        tk.Label(
            header, text="JSON 长文本截断工具",
            fg="white", bg=self.accent, font=("Microsoft YaHei", 14, "bold"),
        ).pack(side=tk.LEFT, padx=16, pady=10)

        # 控制栏
        ctrl = tk.Frame(self.root, bg=self.bg)
        ctrl.pack(fill=tk.X, padx=12, pady=(10, 4))

        tk.Label(ctrl, text="截断长度(字符):", bg=self.bg,
                 font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)
        self.max_len_var = tk.StringVar(value="100")
        spin = ttk.Spinbox(ctrl, from_=10, to=10000, increment=10,
                           width=8, textvariable=self.max_len_var)
        spin.pack(side=tk.LEFT, padx=(4, 16))

        self.pretty_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ctrl, text="美化输出", variable=self.pretty_var,
                        command=self._on_pretty_toggle).pack(side=tk.LEFT)

        # 主体分栏：左输入 / 右输出
        body = tk.PanedWindow(self.root, orient=tk.HORIZONTAL,
                              sashwidth=6, sashrelief=tk.RAISED, bg=self.bg)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 8))

        # 左侧：输入
        left = tk.Frame(body, bg="white")
        tk.Label(left, text="输入 (粘贴 JSON 文本)", bg="white",
                 font=("Microsoft YaHei", 10, "bold"), anchor="w"
                 ).pack(fill=tk.X, padx=8, pady=(6, 2))
        self.input_box = scrolledtext.ScrolledText(
            left, wrap=tk.WORD, font=("Consolas", 11),
            bg="#ffffff", relief=tk.SOLID, bd=1)
        self.input_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        body.add(left, width=430, minsize=200)

        # 右侧：输出
        right = tk.Frame(body, bg="white")
        tk.Label(right, text="输出 (处理后的结果)", bg="white",
                 font=("Microsoft YaHei", 10, "bold"), anchor="w"
                 ).pack(fill=tk.X, padx=8, pady=(6, 2))
        self.output_box = scrolledtext.ScrolledText(
            right, wrap=tk.WORD, font=("Consolas", 11),
            bg="#fafbfc", relief=tk.SOLID, bd=1, state=tk.DISABLED)
        self.output_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        body.add(right, width=430, minsize=200)

        # 底部按钮栏
        footer = tk.Frame(self.root, bg=self.bg)
        footer.pack(fill=tk.X, padx=12, pady=(0, 10))

        self._styled_button(footer, "处理", self._process, primary=True).pack(side=tk.LEFT, padx=4)
        self._styled_button(footer, "清空", self._clear).pack(side=tk.LEFT, padx=4)
        self._styled_button(footer, "复制结果", self._copy).pack(side=tk.LEFT, padx=4)
        self._styled_button(footer, "加载示例", self._load_sample).pack(side=tk.LEFT, padx=4)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        tk.Label(self.root, textvariable=self.status_var, bg=self.bg,
                 fg="#666666", font=("Microsoft YaHei", 9), anchor="w"
                 ).pack(fill=tk.X, padx=14, pady=(0, 6))

    def _styled_button(self, parent, text, cmd, primary=False):
        btn = tk.Button(
            parent, text=text, command=cmd,
            font=("Microsoft YaHei", 10),
            bg=self.accent if primary else "#e5e7eb",
            fg="white" if primary else "#1f2937",
            activebackground="#2563eb" if primary else "#d1d5db",
            activeforeground="white" if primary else "#1f2937",
            relief=tk.FLAT, bd=0, padx=14, pady=6, cursor="hand2",
        )
        return btn

    def _on_pretty_toggle(self) -> None:
        """美化选项切换时，若已有结果则重新渲染。"""
        if self.output_box.get("1.0", tk.END).strip():
            self._process()

    def _process(self) -> None:
        raw = self.input_box.get("1.0", tk.END).strip()
        if not raw:
            messagebox.showinfo("提示", "请先在左侧输入 JSON 文本。")
            return

        try:
            max_len = int(self.max_len_var.get())
            if max_len <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "截断长度必须是正整数。")
            return

        try:
            result = simplify_result(raw, max_len)
        except json.JSONDecodeError:
            messagebox.showerror("错误", "输入的不是合法的 JSON 文本，请检查后重试。")
            self._set_output("")
            self.status_var.set("处理失败：JSON 解析错误")
            return

        if self.pretty_var.get():
            try:
                result = json.dumps(json.loads(result),
                                    ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                pass

        self._set_output(result)
        self.status_var.set(f"处理成功，截断长度 {max_len} 字符")

    def _set_output(self, text: str) -> None:
        self.output_box.config(state=tk.NORMAL)
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, text)
        self.output_box.config(state=tk.DISABLED)

    def _clear(self) -> None:
        self.input_box.delete("1.0", tk.END)
        self._set_output("")
        self.status_var.set("已清空")

    def _copy(self) -> None:
        text = self.output_box.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("提示", "暂无可复制的结果。")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set("结果已复制到剪贴板")

    def _load_sample(self) -> None:
        sample = (
            '{\n'
            '  "name": "示例数据",\n'
            '  "description": "这是一段非常非常长的描述文本，'
            '用于演示JSON长文本截断工具对超过设定长度字符串的处理效果，'
            '它会被自动截断并追加省略号。",\n'
            '  "tags": ["json", "tool", "truncate"],\n'
            '  "items": [\n'
            '    {"id": 1, "content": "短文本"},\n'
            '    {"id": 2, "content": "另一段明显超出截断阈值的超长文本内容，'
            '同样会被工具自动处理以压缩整体输出体积。"}\n'
            '  ]\n'
            '}'
        )
        self.input_box.delete("1.0", tk.END)
        self.input_box.insert(tk.END, sample)
        self.status_var.set("已加载示例，点击「处理」运行")


def main() -> None:
    root = tk.Tk()
    try:
        # 尝试使用更现代的主题
        root.tk.call("source", "azure.tcl")  # 不存在时忽略
    except tk.TclError:
        pass
    JsonSimplifyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
