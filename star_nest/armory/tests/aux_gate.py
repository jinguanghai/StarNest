"""
复制体φ·隔离校验门禁 V1.0
在部署前由复制体独立运行:
  python armory/ceshi/fuzhiti_menjin.py
全部通过后才允许部署
"""
import sys, os, ast, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

jieguo = {"pass": 0, "fail": 0}
def menjin(mingcheng, tiaojian):
    if tiaojian:
        jieguo["pass"] += 1; print(f"  [PASS] {mingcheng}")
    else:
        jieguo["fail"] += 1; print(f"  [FAIL] {mingcheng}")

print(f"{'='*50}")
print(f"  复制体φ·隔离校验门禁")
print(f"{'='*50}")

# 1. AST全量编译
print("\n[门禁1] AST全量编译检查")
failed = []
for r, _, fs in os.walk(ROOT):
    for f in fs:
        if f.endswith('.py') and '__pycache__' not in r:
            try:
                with open(os.path.join(r, f), encoding='utf-8', errors='ignore') as fh:
                    ast.parse(fh.read())
            except SyntaxError as e:
                failed.append(f"{os.path.relpath(os.path.join(r, f), ROOT)}: {e}")
menjin("AST编译(53文件)", len(failed) == 0)

# 2. 零外部依赖
print("\n[门禁2] 零外部依赖检查")
stdlib = set(sys.stdlib_module_names)
internal = {'meridian','tupu','qilv','peizhi','rukou','organs','xin','gan','pi','fei','shen',
            'bianchengti','yunxingti','fuzhiti','dynamics','piphicycle','xiufu','bajidongli',
            'bashisuanshu','jiuchou','jiemian','huntianling','execution','zhujianlu','llm',
            'wangluo','jiedian','jinhua','fuzhi','shengji','zijingshi','shared_memory',
            'jiyiguanli','armory','ceshi','quanliang_ceshi','wenjian_sousuo',
            'wenjian_gongju','shell_mingling','git_gongju','yuyin_gongju','huanjing',
            'protocols','zhengjing','fanjing','hejing','chaoyuejing','benyuan','zizhi'}
ext_deps = []
for r, _, fs in os.walk(ROOT):
    for f in fs:
        if f.endswith('.py') and '__pycache__' not in r:
            try:
                with open(os.path.join(r, f), encoding='utf-8', errors='ignore') as fh:
                    tree = ast.parse(fh.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for a in node.names:
                            mod = a.name.split('.')[0]
                            if mod not in stdlib and mod not in internal:
                                ext_deps.append(f"{os.path.relpath(os.path.join(r, f), ROOT)}: import {mod}")
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        mod = node.module.split('.')[0]
                        if mod not in stdlib and mod not in internal and mod:
                            ext_deps.append(f"{os.path.relpath(os.path.join(r, f), ROOT)}: from {mod}")
            except: pass
menjin("零外部依赖", len(ext_deps) == 0)
if ext_deps:
    for d in ext_deps[:5]: print(f"    -> {d}")

# 3. 模块导入
print("\n[门禁3] 核心模块导入检查")
core_mods = ["meridian.qilv","meridian.tupu","meridian.meridian",
             "execution.llm","execution.zhujianlu","shared_memory.jiyiguanli",
             "organs.xin","organs.gan","organs.pi","organs.fei","organs.shen",
             "armory.wenjian_gongju","armory.wenjian_sousuo",
             "protocols.zhengjing","protocols.fanjing","protocols.hejing",
             "dynamics.bajidongli","dynamics.piphicycle"]
import_fail = []
for mod in core_mods:
    try:
        __import__(mod)
    except Exception as e:
        import_fail.append(f"{mod}: {e}")
menjin("模块导入(19核心)", len(import_fail) == 0)

# 4. 安全审查
print("\n[门禁4] 安全审查")
dangerous = []
for r, _, fs in os.walk(ROOT):
    for f in fs:
        if f.endswith('.py') and '__pycache__' not in r:
            fp = os.path.join(r, f)
            with open(fp, encoding='utf-8', errors='ignore') as fh:
                c = fh.read()
            # 排除安全检测器自身和测试文件
            if f in ["quanliang_ceshi.py","fuzhiti_menjin.py","ceshi.py"] or "armory/ceshi/" in fp:
                continue
            if "os.system(" in c and f not in ["shell_mingling.py","zhujianlu.py","ceshi.py"]:
                dangerous.append(f"{f}: os.system")
            if "rm -rf" in c: dangerous.append(f"{f}: rm -rf")
            if "chmod 777" in c: dangerous.append(f"{f}: chmod 777")
menjin("安全审查", len(dangerous) == 0)
if dangerous:
    for d in dangerous: print(f"    [RISK] {d}")

# 5. 子进程启停
print("\n[门禁5] 子进程启停验证")
r = subprocess.run(
    [sys.executable, '-c',
     'import sys;sys.path.insert(0,".");from rukou import SanTiXiTong;s=SanTiXiTong();print("INIT_OK")'],
    capture_output=True, text=True, timeout=60, cwd=ROOT)
menjin("子进程初始化", "INIT_OK" in r.stdout)

# 6. 记忆完整性
print("\n[门禁6] 记忆完整性检查")
try:
    from star_nest.shared_memory.manager import JiYiGuanLi
    jm = JiYiGuanLi(os.path.join(ROOT, "shared_memory"))
    tj = jm.zhishi_tongji()
    menjin(f"记忆条目({tj.get('zongshu',0)}>200)", tj.get('zongshu',0) >= 200)
except Exception as e:
    menjin("记忆完整性", False)
    print(f"    -> {e}")

print(f"\n{'='*50}")
print(f"  门禁结果: {jieguo['pass']}/{jieguo['pass']+jieguo['fail']} 通过")
if jieguo["fail"] > 0:
    print(f"  >>> 部署被阻止 <<<")
else:
    print(f"  >>> 允许部署 <<<")
print(f"{'='*50}")
sys.exit(0 if jieguo["fail"] == 0 else 1)
