"""
浑天令 HunTianLing V1.0 [星巢·独立界面]

Linux终端风格暗黑界面 · tkinter标准库 · 零外部依赖

功能:
  - 暗黑终端风格 (背景#0d0d0d 文字#c0c0c0 提示符#00cc66)
  - Shift+Enter 多行输入
  - Enter 单行发送
  - 右键粘贴(不分条)
  - 后台 SanTiXiTong 线程
  - 输出区自动滚动

架构:
  浑天令(界面端) → 问剑路(输入判断) → 心(调度) → 铸剑炉(输出)
"""
import sys, os, threading, time, queue
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import scrolledtext

# ---- 色彩常量 (Linux暗黑终端风格) ----

BG_DARK  = '#0d0d0d'
BG_PANEL = '#1a1a1a'
FG_TEXT  = '#c0c0c0'
FG_PROMPT = '#00cc66'
FG_GOLD  = '#cc9900'
FG_BLUE  = '#6699cc'
FG_RED   = '#cc4444'
FG_GRAY  = '#666666'
FG_GREEN = '#669966'
FONT_NAME = 'Consolas'
FONT_SIZE = 10

TAG_COLORS = {
    "铸剑炉": FG_BLUE,
    "确认":   FG_GOLD,
    "使":     FG_GOLD,
    "安全":    FG_RED,
    "杀毒":    FG_RED,
    "错误":    FG_RED,
    "心":     FG_GRAY,
    "脾":     FG_GRAY,
    "肝":     FG_GRAY,
    "肺":     FG_GRAY,
    "肾":     FG_GRAY,
    "π-φ":    FG_GRAY,
    "三体":   FG_GREEN,
}


# ---- 向后兼容: 旧版 ANSI 终端工具 (仅用于测试) ----

class YanSe:
    """旧版 ANSI 颜色常量 (向后兼容)"""
    MU_LV='\033[32m'; HUO_CHI='\033[31m'; TU_HUANG='\033[33m'
    JIN_BAI='\033[37m'; SHUI_HEI='\033[34m'
    QING='\033[36m'; ZI='\033[35m'; HUI='\033[90m'
    JIACU='\033[1m'; XIAHUA='\033[4m'; SHANSHUO='\033[5m'; FUWEI='\033[0m'
    @classmethod
    def zang_yanse(cls, zangqi_ming):
        m = {"肝":cls.MU_LV,"心":cls.HUO_CHI,"脾":cls.TU_HUANG,"肺":cls.JIN_BAI,"肾":cls.SHUI_HEI}
        return m.get(zangqi_ming, cls.FUWEI)

class ZhongDuan:
    """旧版 终端渲染器 (向后兼容)"""
    def __init__(self): self.kuandu, self.gaodu = 80, 24
    def qingping(self): pass
    def shuchu(self, w, y='', q=''): pass
    def shuchu_wenli(self, w): pass
    def tishifu(self, f='$ '): pass
    def fen_ge_xian(self, k=0): pass
    def biaoti(self, w): pass
    def zangqi_zhuangtai(self, d): pass


class HunTianLing:
    """浑天令·星巢独立界面"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("星巢 (XingChao) — 浑天令")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("960x640")
        self.root.minsize(600, 400)

        # ---- 状态栏 (顶部) ----
        self.status_frame = tk.Frame(self.root, bg=BG_PANEL, height=28)
        self.status_frame.pack(fill=tk.X, side=tk.TOP)
        self.status_frame.pack_propagate(False)

        self.status_label = tk.Label(self.status_frame, text="星巢启动中...",
                                      fg=FG_GRAY, bg=BG_PANEL, font=(FONT_NAME, 9),
                                      anchor='w')
        self.status_label.pack(side=tk.LEFT, padx=12, fill=tk.X, expand=True)

        self.exit_btn = tk.Label(self.status_frame, text="✕", fg=FG_GRAY, bg=BG_PANEL,
                                  font=(FONT_NAME, 12), cursor='hand2')
        self.exit_btn.pack(side=tk.RIGHT, padx=12)
        self.exit_btn.bind("<Button-1>", lambda e: self.on_exit())

        # ---- 输出区 ----
        self.output = scrolledtext.ScrolledText(
            self.root, bg=BG_DARK, fg=FG_TEXT, insertbackground=FG_PROMPT,
            font=(FONT_NAME, FONT_SIZE), state='disabled', relief=tk.FLAT,
            bd=0, wrap=tk.WORD, padx=10, pady=5,
            selectbackground='#333333', selectforeground=FG_TEXT
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        # 配置标签颜色
        for tag_name, color in TAG_COLORS.items():
            self.output.tag_config(tag_name, foreground=color)
        self.output.tag_config("提示符", foreground=FG_PROMPT)
        self.output.tag_config("时间戳", foreground=FG_GRAY)

        # 右键菜单
        self.output_menu = tk.Menu(self.root, tearoff=0, bg=BG_PANEL, fg=FG_TEXT)
        self.output_menu.add_command(label="清屏", command=self.clear_output)
        self.output.bind("<Button-3>", lambda e: self.output_menu.tk_popup(e.x_root, e.y_root))

        # ---- 输入区 (底部) ----
        self.input_frame = tk.Frame(self.root, bg=BG_PANEL, height=36)
        self.input_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.input_frame.pack_propagate(False)

        # 提示符
        self.prompt = tk.Label(self.input_frame, text="星巢> ", fg=FG_PROMPT,
                                bg=BG_PANEL, font=(FONT_NAME, FONT_SIZE, 'bold'))
        self.prompt.pack(side=tk.LEFT, padx=(12, 0))

        # 输入框
        self.input_box = tk.Entry(self.input_frame, bg=BG_DARK, fg=FG_TEXT,
                                   insertbackground=FG_PROMPT, relief=tk.FLAT,
                                   bd=0, font=(FONT_NAME, FONT_SIZE))
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 12), pady=6)
        self.input_box.bind("<Return>", self.on_send)
        self.input_box.bind("<Shift-Return>", self.on_newline)
        self.input_box.focus_set()

        # ---- 内部状态 ----
        self._multi_buf = []         # Shift+Enter 多行缓冲
        self._result_queue = []      # 线程安全结果队列
        self._lock = threading.Lock()
        self._running = True
        self._system_started = False
        self._s = None               # SanTiXiTong 实例

        # ---- 启动系统 ----
        self.append_system("星巢启动中...")
        threading.Thread(target=self._start_system, daemon=True).start()

        # ---- 轮询输出 ----
        self._poll_output()

        # ---- 窗口事件 ----
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.root.bind("<Control-l>", lambda e: self.clear_output())
        self.root.bind("<Escape>", lambda e: self.on_exit())

        self.root.mainloop()

    # ==================== 系统启动 ====================

    def _start_system(self):
        """后台线程: 启动SanTiXiTong"""
        try:
            from star_nest.entry import SanTiXiTong
            self._push_result("[浑天令] 初始化三体系统...")
            self._s = SanTiXiTong()
            self._s.bianchengti.start_all()
            self._s.yunxingti.start_all()
            time.sleep(3)
            self._system_started = True
            # 更新状态栏
            jiyi = self._s.jiyiguanli.zhishi_tongji()
            tj = jiyi.get("zongshu", 0)
            gongju = getattr(self._s.yunxingti.xin.pi, 'gongju_zhuche', {})
            self.root.after(0, self._update_status, tj, len(gongju))
            self._push_result("[浑天令] 三体就绪·等待指令")
        except Exception as e:
            self._push_result(f"[错误] 启动失败: {e}")
            self._system_started = False

    def _update_status(self, jiyi_count=285, gongju_count=33):
        self.status_label.config(
            text=f"三体:O  运行体:问题0 修复0 | 编程体:问题0 修复0 | 记忆{jiyi_count}条 兵器{gongju_count}件"
        )

    # ==================== 输入处理 ====================

    def on_send(self, event=None):
        """Enter → 发送"""
        text = self.input_box.get().strip()
        if self._multi_buf:
            self._multi_buf.append(text)
            full_text = '\n'.join(self._multi_buf)
            self._multi_buf = []
            self.input_box.delete(0, tk.END)
            self.echo_input(full_text[:80])
        else:
            self.input_box.delete(0, tk.END)
            if text:
                self.echo_input(text[:80])

        if text:
            self._send_message(text if not self._multi_buf else full_text)

    def on_newline(self, event=None):
        """Shift+Enter → 多行缓冲"""
        text = self.input_box.get()
        if text.strip():
            self._multi_buf.append(text.strip())
        self.input_box.delete(0, tk.END)
        self.prompt.config(text=f"  ... ")  # 续行提示
        return "break"

    def echo_input(self, text):
        """回显用户输入"""
        self.append_output(f"$ {text}", "提示符")

    def _send_message(self, msg):
        """发送消息到星巢"""
        if not self._system_started or not self._s:
            self.append_output("[浑天令] 系统未就绪, 请等待启动完成", "错误")
            return
        try:
            self._s.yunxingti.xin.add_xuqiu(msg)
        except Exception as e:
            self.append_output(f"[错误] 发送失败: {e}", "错误")

    # ==================== 输出处理 ====================

    def _push_result(self, text):
        """线程安全: 推入结果队列"""
        with self._lock:
            self._result_queue.append(text)

    def _poll_output(self):
        """主线程轮询: 检查结果队列 + SanTiXiTong输出队列"""
        if not self._running:
            return

        # 1. 检查内部结果队列
        with self._lock:
            while self._result_queue:
                text = self._result_queue.pop(0)
                self.append_output(text)

        # 2. 检查SanTiXiTong输出队列
        if self._s and self._system_started:
            for xin in [getattr(getattr(self._s, t, None), 'xin', None)
                        for t in ['yunxingti', 'bianchengti']]:
                if xin:
                    try:
                        while not xin.shuchu_duilie.empty():
                            reply = xin.shuchu_duilie.get_nowait()
                            if reply:
                                self.append_output(str(reply))
                    except Exception:
                        pass

        self.root.after(500, self._poll_output)  # 500ms轮询

    def append_output(self, text, tag=None):
        """线程安全: 追加输出文本 (通过after调度到主线程)"""
        def _do():
            self.output.config(state='normal')
            # 添加时间戳
            from datetime import datetime
            ts = datetime.now().strftime("%H:%M:%S")
            self.output.insert(tk.END, f"[{ts}] ", "时间戳")

            # 自动标签着色
            if tag:
                self.output.insert(tk.END, text + '\n', tag)
            else:
                # 自动匹配标签
                matched = None
                for tag_name in TAG_COLORS:
                    if f"[{tag_name}" in text:
                        matched = tag_name
                        break
                self.output.insert(tk.END, text + '\n', matched)
            self.output.see(tk.END)
            self.output.config(state='disabled')
        self.root.after(0, _do)

    def append_system(self, text):
        """追加系统消息(灰色)"""
        def _do():
            self.output.config(state='normal')
            self.output.insert(tk.END, f"  {text}\n", "时间戳")
            self.output.see(tk.END)
            self.output.config(state='disabled')
        self.root.after(0, _do)

    def clear_output(self):
        """清屏"""
        self.output.config(state='normal')
        self.output.delete('1.0', tk.END)
        self.output.config(state='disabled')

    # ==================== 退出 ====================

    def on_exit(self):
        """优雅退出"""
        self._running = False
        if self._s:
            try:
                self._s.bianchengti.xin.tingzhi()
                self._s.yunxingti.xin.tingzhi()
            except Exception:
                pass
        self.root.destroy()


if __name__ == "__main__":
    HunTianLing()
