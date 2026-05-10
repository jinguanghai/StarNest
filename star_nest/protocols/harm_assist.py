"""
害-佐协议 V1.0 [星巢·函数级容错基础设施]

铁律13: 害必有佐 — 任意可调用函数(公开或内部关键)必须声明其害和佐治
支持静态审计(自审镜周期性扫描)与运行时害发现(经络捕获未知害)

害类型统一字典(14种) — 防止碎片化命名
害传播规则 — 调用者必须处理或上浮被调用者的害
"""
import ast, json, inspect
from pathlib import Path

_PY_FILE = Path(__file__)
_HUAN_JING = _PY_FILE.parent.parent / "huanjing"
_HAI_LEIXING_JSON = _HUAN_JING / "hai_leixing.json"

# ========== 已知害类型字典 ==========
HAI_LEIXING = {
    "chen_kong":           ("依赖返回空值",                   0),
    "chen_yichang":        ("依赖返回错误",                   2),
    "quanxian_jujue":      ("权限拒绝/无写权限",              2),
    "chaoshi":             ("执行超时",                       1),
    "yufa_cuowu":          ("语法或代码错误",                 1),
    "execution_shibai":      ("执行失败/返回错误",              2),
    "wangluo_duanlian":    ("网络断开/LLM不可达",             2),
    "cipan_man":           ("磁盘空间不足",                   3),
    "neicun_yichu":        ("内存溢出/进程OOM",               3),
    "wenjian_sunhuai":     ("文件损坏/索引损坏",              2),
    "bingfa_chongtu":      ("并发冲突/锁竞争",                1),
    "LLM_xuanyun":         ("LLM幻觉/返回无效或垃圾数据",     1),
    "shuru_feiqi":         ("输入格式异常/不可解析",          0),
    "zuozhi_yichang":      ("佐治函数自身异常(二次故障)",     2),
}

_EXTRA_HAI_TYPES = {}

def _jia_zai_ewai():
    """加载跨会话持久化的运行时注册害类型"""
    global _EXTRA_HAI_TYPES
    try:
        if _HAI_LEIXING_JSON.exists():
            data = json.loads(_HAI_LEIXING_JSON.read_text(encoding='utf-8'))
            if isinstance(data, dict):
                _EXTRA_HAI_TYPES = data
    except Exception:
        pass

def _baocun_ewai():
    """保存运行时注册害类型"""
    try:
        _HAI_LEIXING_JSON.parent.mkdir(parents=True, exist_ok=True)
        _HAI_LEIXING_JSON.write_text(json.dumps(_EXTRA_HAI_TYPES, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception:
        pass

def dengji_hai_lei_xing(lei_xing: str, miao_shu: str, yan_zhong_du: int):
    """运行时动态注册新害类型(持久化到 huanjing/hai_leixing.json)"""
    key = f"_dongtai_{lei_xing}"
    _EXTRA_HAI_TYPES[key] = {"leixing": lei_xing, "miaoshu": miao_shu, "yanzhongdu": yan_zhong_du}
    _baocun_ewai()

def qu_hai_miaoshu(lei_xing: str):
    """获取害类型描述(含固定+动态注册)"""
    for d in [HAI_LEIXING, {k: (v["leixing"], v["miaoshu"], v["yanzhongdu"]) for k, v in _EXTRA_HAI_TYPES.items()}]:
        if lei_xing in d:
            return d[lei_xing]
    return None

def qu_quanbu_hai_leixing():
    """返回所有已注册害类型名称"""
    fixed = {k for k in HAI_LEIXING if isinstance(HAI_LEIXING.get(k), tuple)}
    dynamic = set(_EXTRA_HAI_TYPES.keys())
    return fixed | dynamic

# ========== 装饰器：函数级害-佐声明 ==========

def sheng_ming_hai(hai_list):
    """
    装饰器: 为函数声明可能的害列表
    
    hai_list: [("害类型", "描述", 严重度0-3), ...]
                严重度: 0=可忽略 1=注意 2=严重 3=致命
    """
    def wrapper(fn):
        fn._hai_ = hai_list
        return fn
    return wrapper

def sheng_ming_zuo(zuo_map):
    """
    装饰器: 为函数声明佐治映射
    
    zuo_map: {"害类型": 佐治函数(无参数、无副作用), ...}
             值可以是无参函数或True(表示自动兜底佐治)
    
    铁律约束: 佐治函数必须自身不引入新害, 否则违反铁律13的递归安全
    """
    def wrapper(fn):
        fn._zuo_ = zuo_map
        return fn
    return wrapper

# ========== 审计工具 ==========

def jian_cha_han_shu(fn) -> dict:
    """
    检查单个函数的害-佐声明状态
    
    返回: {"covered": bool, "has_hai": bool, "has_zuo": bool, "is_legacy": bool,
           "has_bare_except": bool, "hai_list": [], "zuo_map": {},
           "missing_reason": str}
    """
    hai = getattr(fn, '_hai_', None)
    zuo = getattr(fn, '_zuo_', None)
    legacy = getattr(fn, '_legacy_', None)
    
    has_hai = isinstance(hai, list) and len(hai) > 0
    has_zuo = isinstance(zuo, dict) and len(zuo) > 0
    
    # 检测裸 except Exception: pass (隐式未声明佐治)
    has_bare_except = False
    try:
        src = inspect.getsource(fn)
        has_bare_except = any(
            line.strip() in ('except:', 'except Exception:', 'except Exception: pass', 'except Exception: pass')
            for line in src.split('\n')
        )
    except Exception:
        pass
    
    # 如果函数名以下划线结尾(_ao_yao_chuli等已知FangJi入口函数已在入口覆盖)
    # 不做豁免, 函数自身内部调用的子函数仍需声明
    missing = ""
    if not has_hai:
        missing = "缺少害声明(_hai_)"
    elif not has_zuo:
        missing = "有_hai_但缺少_zuo_"
    
    return {
        "covered": has_hai and has_zuo,
        "has_hai": has_hai,
        "has_zuo": has_zuo,
        "is_legacy": legacy is not None,
        "legacy_reason": legacy,
        "has_bare_except": has_bare_except,
        "hai_list": hai,
        "zuo_map": zuo,
        "missing_reason": missing,
    }

def jian_cha_mo_kuai(module) -> list:
    """
    扫描模块中所有public函数的害-佐声明
    
    返回: [{"name": fn.__name__, "result": jian_cha_han_shu(fn), "file": source_file}, ...]
    """
    result = []
    try:
        src_file = Path(inspect.getfile(module))
    except Exception:
        return result
    
    for name, obj in inspect.getmembers(module):
        if name.startswith('_') or not callable(obj):
            continue
        try:
            fn_file = Path(inspect.getfile(obj))
            if fn_file != src_file:
                continue  # 不是定义在此模块中的函数
        except Exception:
            continue
        
        check = jian_cha_han_shu(obj)
        result.append({"name": name, "result": check, "file": str(src_file)})
    
    return result

def jian_cha_mu_lu(directory: str, file_pattern: str = "*.py") -> list:
    """
    递归扫描目录中所有.py文件的公开函数
    
    返回: 汇总审计报告
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return [{"error": f"目录不存在: {directory}"}]
    
    results = []
    for py_file in dir_path.rglob(file_pattern):
        if py_file.name.startswith('__') or py_file.name.startswith('ceshi_'):
            continue
        try:
            code = py_file.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(code)
        except Exception:
            continue
        
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name.startswith('_') and '__init__' not in str(py_file):
                continue
            
            # 检查装饰器: @sheng_ming_hai / @sheng_ming_zuo / @legacy
            has_hai_deco = False
            has_zuo_deco = False
            has_legacy_deco = False
            hai_list = None
            zuo_map = None
            legacy_reason = None
            
            for deco in node.decorator_list:
                dname = None
                if isinstance(deco, ast.Name):
                    dname = deco.id
                elif isinstance(deco, ast.Call):
                    if isinstance(deco.func, ast.Name):
                        dname = deco.func.id
                    elif isinstance(deco.func, ast.Attribute):
                        dname = deco.func.attr
                
                if dname == 'sheng_ming_hai':
                    has_hai_deco = True
                elif dname == 'sheng_ming_zuo':
                    has_zuo_deco = True
                elif dname == 'legacy':
                    has_legacy_deco = True
                    break
            
            # 检测裸 except Exception: pass
            has_bare = False
            try:
                func_src = ast.get_source_segment(code, node)
                if func_src:
                    has_bare = any(
                        l.strip() in ('except:', 'except Exception:', 'except Exception: pass', 'except Exception: pass')
                        for l in func_src.split('\n')
                    )
            except Exception:
                pass
            
            covered = has_hai_deco and has_zuo_deco
            
            if not covered:
                results.append({
                    "file": str(py_file.relative_to(dir_path)),
                    "function": node.name,
                    "line": node.lineno,
                    "covered": covered,
                    "has_hai": has_hai_deco,
                    "has_zuo": has_zuo_deco,
                    "is_legacy": has_legacy_deco,
                    "has_bare_except": has_bare,
                })
    
    return results

# ========== 害传播检测 ==========

def jian_cha_haixielou(directory: str) -> list:
    """
    检测调用链中的"害泄露": 调用者未处理或未上浮被调用者的害
    
    遍历所有函数, 提取其调用链中其他函数的害声明,
    如果调用者自身未声明这些害且未捕获 → 标记为害泄露
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    
    leaks = []
    # 构建: 函数名 → (文件, 害列表)
    func_hai_map = {}
    for py_file in dir_path.rglob("*.py"):
        if py_file.name.startswith('__') or py_file.name.startswith('ceshi_'):
            continue
        try:
            code = py_file.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(code)
        except Exception:
            continue
        
        mod_name = py_file.stem
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            hai_list = []
            for deco in node.decorator_list:
                dname = None
                if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Name):
                    dname = deco.func.id
                if dname == 'sheng_ming_hai' and deco.args:
                    for arg in deco.args:
                        if isinstance(arg, (ast.List, ast.Tuple)):
                            for elt in arg.elts:
                                if isinstance(elt, (ast.List, ast.Tuple)) and elt.elts:
                                    first = elt.elts[0]
                                    if isinstance(first, ast.Constant):
                                        hai_list.append((first.value, node.lineno))
            func_hai_map[node.name] = (str(py_file.relative_to(dir_path)), hai_list)
    
    # 反向检查: 每个函数的调用者是否处理了被调用者的害
    for py_file in dir_path.rglob("*.py"):
        if py_file.name.startswith('__') or py_file.name.startswith('ceshi_'):
            continue
        try:
            code = py_file.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(code)
        except Exception:
            continue
        
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            # 提取此函数声明的害
            caller_hai = set()
            for deco in node.decorator_list:
                dname = None
                if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Name):
                    dname = deco.func.id
                if dname == 'sheng_ming_hai' and deco.args:
                    for arg in deco.args:
                        if isinstance(arg, (ast.List, ast.Tuple)):
                            for elt in arg.elts:
                                if isinstance(elt, (ast.List, ast.Tuple)) and elt.elts:
                                    first = elt.elts[0]
                                    if isinstance(first, ast.Constant):
                                        caller_hai.add(first.value)
            
            # 提取此函数调用了哪些函数
            called = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Attribute):
                        fn = child.func.attr
                    elif isinstance(child.func, ast.Name):
                        fn = child.func.id
                    else:
                        continue
                    called.add(fn)
            
            # 检查害泄露
            for cfn in called:
                if cfn in func_hai_map:
                    called_file, called_hai_list = func_hai_map[cfn]
                    for htype, hline in called_hai_list:
                        if htype not in caller_hai:
                            leaks.append({
                                "file": str(py_file.relative_to(dir_path)),
                                "function": node.name,
                                "line": node.lineno,
                                "called_func": cfn,
                                "called_file": called_file,
                                "leaked_hai": htype,
                                "called_hai_line": hline,
                            })
    
    return leaks

# 启动时加载动态注册的害类型
_jia_zai_ewai()
