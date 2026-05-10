"""
星巢 自动化测试套件 — 全部 5 层

用法:
  python ceshi_quanbu.py            一键全量
  python ceshi_quanbu.py --cli      仅 CLi 场景
  python ceshi_quanbu.py --tools    仅工具注册
  python ceshi_quanbu.py --fuzhiti  仅复制体检查
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PASS = 0; FAIL = 0; ALL_PASS = 0; ALL_FAIL = 0

def check(name, condition):
    global ALL_PASS, ALL_FAIL
    if condition: ALL_PASS += 1; print(f"  PASS: {name}")
    else: ALL_FAIL += 1; print(f"  FAIL: {name}")

# ==================== L3: 工具注册验证 ====================

def test_gongju():
    print("\n=== L3 工具注册验证 ===")
    try:
        from star_nest.entry import SanTiXiTong
        s = SanTiXiTong()
        s.bianchengti.start_all()
        time.sleep(4)
        pi = s.bianchengti.xin.pi
        tools = dict(pi.gongju_zhuche) if pi else {}
        count = len(tools)
        check(f"工具数量 > 10", count > 10)
        required = ["file_tool", "system_operations", "package_tool"]
        for t in required:
            check(f"关键工具: {t}", t in tools or any(k.endswith("_" + t) for k in tools))
        print(f"  已注册: {count} 件兵器")
        for k in sorted(tools)[:5]:
            print(f"    {k}: {tools[k].get('miaoshu','')[:60]}")
    except Exception as e:
        check(f"工具注册加载", False)
        print(f"  ERROR: {e}")

# ==================== L5: 项目结构验证 ====================

def test_fuzhiti():
    print("\n=== L5 项目结构验证 ===")
    import ast
    xc = ROOT
    check("StarNest 目录存在", os.path.exists(xc))
    
    # AST
    ast_ok = 0; ast_fail = 0
    for dp,_,fs in os.walk(xc):
        if '__pycache__' in dp: continue
        for f in fs:
            if f.endswith('.py'):
                fp = os.path.join(dp,f)
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                        ast.parse(fh.read())
                    ast_ok += 1
                except: ast_fail += 1
    check(f"AST编译 ({ast_ok} OK)", ast_fail == 0)
    
    # .env
    env = os.path.join(xc, 'star_nest', 'runtime', 'environment', '.env')
    has_env = os.path.exists(env)
    check("star_nest/runtime/environment/.env 存在", has_env)
    if has_env:
        key_load = 'DEEPSEEK_API_KEY' in open(env,encoding='utf-8').read()
        check("DEEPSEEK_API_KEY 已配置", key_load)
    
    # 入口文件
    entry = os.path.join(xc, 'star_nest', 'entry.py')
    check("entry.py 存在", os.path.exists(entry))
    readme = os.path.join(xc, 'README.md')
    check("README.md 存在", os.path.exists(readme))

# ==================== L2: CLI 场景测试 ====================

def test_cli():
    print("\n=== L2 CLI 场景测试 ===")
    print("  (此测试需要 LLM API 连接, 每项约 15-40s)")
    try:
        from star_nest.entry import SanTiXiTong
        s = SanTiXiTong()
        s.bianchengti.start_all(); s.yunxingti.start_all()
        time.sleep(3)
        
        scenes = [
            ("对话·你好", "你好", None, None),
            ("执行·文件列表", "列出当前目录的文件", None, None),
            ("执行·读文件", "读 README.md", None, None),
        ]
        for name, msg, expect, not_expect in scenes:
            result = _do_test(s, msg)
            ok = result is not None and "LLM未连接" not in str(result)
            check(name, ok)
            if ok: print(f"    -> {str(result)[:80]}")
    except Exception as e:
        check("CLI测试加载", False)
        print(f"  ERROR: {e}")

def _do_test(s, msg):
    for q in [s.yunxingti.xin.shuchu_duilie, s.bianchengti.xin.shuchu_duilie]:
        while not q.empty():
            try: q.get_nowait()
            except: pass
    s.yunxingti.xin.add_xuqiu(msg)
    for _ in range(120):  # 60s
        time.sleep(0.5)
        for q in [s.yunxingti.xin.shuchu_duilie, s.bianchengti.xin.shuchu_duilie]:
            try:
                r = q.get_nowait()
                if r: return str(r)[:200]
            except: pass
    return None

# ==================== 入口 ====================

if __name__ == '__main__':
    print("=" * 50)
    print("  星巢 V11.0 自动化测试套件")
    print("=" * 50)
    
    args = sys.argv[1:]
    
    if not args or '--tools' in args:
        test_gongju()
    if not args or '--cli' in args:
        test_cli()
    if not args or '--fuzhiti' in args:
        test_fuzhiti()
    
    print("\n" + "=" * 50)
    print(f"  总计: {ALL_PASS} PASS, {ALL_FAIL} FAIL")
    print("=" * 50)
