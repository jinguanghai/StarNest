"""
星巢钩子 V1.5 — 智能输入·代码识别·多行自动·管道安全
用法:
   单次:     星巢 检测藏剑阁
   文件:     星巢 -f long_task.txt
   管道:     echo "消息" | 星巢
   交互:     星巢  (代码自动进入多行, Enter空行发送)
   帮助:     星巢 --help
"""
import sys, os, time, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

HELP_TEXT = """星巢 (XingChao) — 通用问题解决操作系统 V2.0

用法:
  星巢 [消息]              单次模式: 发送消息并等待回复
  星巢 -f <文件路径>        文件模式: 读取文件内容作为输入 (默认四层消化)
  星巢 -f <文件路径> --fast 文件模式: 单层快速消化
  星巢 -f <文件路径> --deep 文件模式: 强制四层递进消化
  星巢 --help              显示此帮助
  echo "消息" | 星巢       管道模式: 从管道读取输入
  星巢                      交互模式: 进入REPL对话

交互模式:
  直接输入                 发送消息 (\\行尾续行, 等价Shift+Enter)
  代码(自动识别)            自动进入多行模式 (空行发送)
  exit / 退出               退出交互模式

架构:
  三体: 编程体(π可写) | 运行体(Ω只读) | 复制体(φ沙箱)
  五脏: 心(调度) 肝(记忆) 脾(工具) 肺(审计) 肾(诊断)
  五境: Define→Analyze→Improve→Control→Sustain
  认知包: 三层RenzhiBao — 零提示词与LLM交互
  四层消化: L1粗读→L2精读→L3贯通→L4内化 (长文自动)
"""

# 帮助模式
if len(sys.argv) >= 2 and sys.argv[1] in ("--help", "-h", "/?", "/help"):
    print(HELP_TEXT)
    sys.exit(0)

from star_nest.entry import SanTiXiTong

try:
    s = SanTiXiTong()
    s.bianchengti.start_all()
    s.yunxingti.start_all()
    time.sleep(4)
except Exception as e:
    print(f"[星巢] 启动失败: {e}")
    print("  检查: huanjing/.env 是否配置 DEEPSEEK_API_KEY")
    sys.exit(1)

def chuli(msg, mode=None):
    if mode and hasattr(s.yunxingti.xin.shuruceng, 'chuli'):
        s.yunxingti.xin.shuruceng._shen_du_moshi = (mode != 'fast')
    for q in [s.yunxingti.xin.shuchu_duilie, s.bianchengti.xin.shuchu_duilie]:
        while not q.empty():
            try: q.get_nowait()
            except: pass
    s.yunxingti.xin.add_xuqiu(msg)
    # 七律对时: 执行→一小周(49s), 缓冲→一微周(7s), 轮询→一刹那(1s)
    from star_nest.meridian.seven_laws import QiLv
    ql = QiLv()
    if getattr(s.yunxingti.xin, '_is_exec_cmd', False):
        timeout_s = ql.qu_zhouqi("yixiaozhou")  # 49s
        try: s.yunxingti.xin._is_exec_cmd = False
        except: pass
    else:
        timeout_s = ql.qu_zhouqi("yiweizhou")   # 7s
    step = ql.qu_zhouqi("yixi") or 1              # 1s 轮询间隔
    for _ in range(int(timeout_s / step)):
        time.sleep(step)
        for q in [s.yunxingti.xin.shuchu_duilie, s.bianchengti.xin.shuchu_duilie]:
            try:
                reply = q.get_nowait()
                if reply: return str(reply)[:3000]
            except: pass
    return ""  # 静默

def duqu_duohang(first_line=""):
    """多行输入: 逐行读取直到空行发送, 自动识别代码"""
    lines = []
    if first_line:
        lines.append(first_line)
        print(f"[多行] 检测到代码输入, 继续输入或空行发送:")
    else:
        print("[多行] 粘贴内容后空行发送:")
    try:
        while True:
            line = input()
            if not line.strip():
                break
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass
    return "\n".join(lines)

# 获取消息来源 + 消化模式
msg = ""
digestion_mode = None  # None=自动, 'deep'=四层, 'fast'=单层
args = sys.argv[1:]
if '--fast' in args:
    digestion_mode = 'fast'
    args = [a for a in args if a != '--fast']
if '--deep' in args:
    digestion_mode = 'deep'
    args = [a for a in args if a != '--deep']

if len(args) >= 2 and args[0] == "-f":
    # 文件模式
    fp = args[1]
    if os.path.exists(fp):
        with open(fp, encoding='utf-8') as f:
            msg = f.read().strip()
    else:
        print(f"文件不存在: {fp}")
        sys.exit(1)
elif not sys.stdin.isatty():
    # 管道模式 (安全读取)
    try:
        msg = sys.stdin.buffer.read().decode('utf-8').strip()
    except:
        msg = sys.stdin.read().strip()
else:
    # 命令参数模式
    msg = " ".join(args)
    if len(msg) > 2000:
        tf = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
        tf.write(msg)
        tf.close()
        print(f"[钩子] 长文本({len(msg)}字) 已写入: {tf.name}")
        with open(tf.name, encoding='utf-8') as f:
            msg = f.read().strip()

# 单次模式
if msg:
    result = chuli(msg, mode=digestion_mode)
    if result: print(result)  # 缓冲型 chuli 返回 "" → 不打印
    sys.exit(0)

# 交互模式
print("星巢交互模式 (粘贴自动缓冲 Enter发送, \\行尾续行, exit退出)")
CODEMARK = ['def ','class ','import ','from ','if __name__','@','print(','return ',
            'with ','for ','while ','try:','except ','#!/','```','#include','<html',
            'SELECT ','const ','let ','var ','function ','async ','export ','curl ',
            'git ','pip ','npm ','docker ','ls ','cd ','mkdir ','rm ','cp ','chmod ']
paste_buf = []          # 粘贴缓冲
zuihou_input_time = time.time()

def _duqu_xuhang():
    """读取一行, 行尾 \\=续行(Shift+Enter等效). 返回完整消息"""
    try:
        line = input("星巢> ").rstrip()
    except (EOFError, KeyboardInterrupt):
        return None
    if not line.endswith('\\'):
        return line.strip()
    lines = [line[:-1].rstrip()]
    while True:
        try:
            line = input("  ... ").rstrip()
        except (EOFError, KeyboardInterrupt):
            break
        if line.endswith('\\'):
            lines.append(line[:-1].rstrip())
        else:
            lines.append(line)
            break
    return '\n'.join(lines)

while True:
    line = _duqu_xuhang()
    if line is None:
        break
    line = line.strip()
    
    xianzai = time.time(); jiange = xianzai - zuihou_input_time; zuihou_input_time = xianzai

    if line.lower() in ("exit", "退出"):
        break

    # 代码检测: 自动进入多行
    if any(line.startswith(m) for m in CODEMARK) and not paste_buf:
        msg = duqu_duohang(line)
        if msg: print(chuli(msg)); print()
        continue

    # 粘贴检测: 间隔<0.3s → 缓冲
    if jiange < 0.3:
        paste_buf.append(line)
        continue

    # Enter发送: 有缓冲→发送缓冲; 无缓冲→发送当前行
    if paste_buf:
        if line: paste_buf.append(line)
        msg = "\n".join(paste_buf)
        paste_buf = []
        print(f"[钩子] 长文本({len(msg)}字)→输入层消化")
        print(chuli(msg))
        print()
        continue

    if not line: continue  # 空行跳过
    print(chuli(line))
    print()
