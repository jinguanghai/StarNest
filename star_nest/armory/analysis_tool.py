"""
藏剑阁 · 分析工具 V1.0
纯Python标准库 · 零外部依赖
代码复杂度 · 依赖分析 · 文件差异 · 重复检测
"""
import os, ast, re, json
from pathlib import Path
from collections import Counter


def fenxi_fuza_du(fp):
    """分析Python文件的圈复杂度/函数长度"""
    path = Path(fp)
    if not path.exists():
        return {"success": False, "error": "文件不存在"}
    code = path.read_text(encoding='utf-8', errors='ignore')
    tree = ast.parse(code)
    jieguo = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
            # 简单圈复杂度: if/for/while/except + 1
            branches = 1
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.And, ast.Or)):
                    branches += 1
            level = "低" if branches <= 5 else ("中" if branches <= 10 else "高")
            jieguo.append(f"{name}: {branches}分支 {lines}行 [{level}]")
    return {"success": True, "output": "\n".join(jieguo) if jieguo else "无函数定义",
            "fu_za_du": [{"name": n.split(':')[0], "branches": int(n.split(':')[1].split('分支')[0].strip())}
                         for n in jieguo]}


def fenxi_yilai(mulu):
    """分析项目Python文件间的import依赖"""
    root = Path(mulu)
    if not root.exists():
        return {"success": False, "error": "目录不存在"}
    yilai = {}
    for fp in root.rglob("*.py"):
        if "__pycache__" in str(fp):
            continue
        try:
            tree = ast.parse(fp.read_text(encoding='utf-8', errors='ignore'))
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split('.')[0])
            # 只保留项目内依赖
            project_imports = [i for i in imports if not i.startswith('_')]
            if project_imports:
                yilai[fp.relative_to(root).as_posix()] = project_imports
        except: pass
    return {"success": True, "output": json.dumps(yilai, ensure_ascii=False, indent=2), "yilai": yilai}


def chongfu_wenben(mulu, zui_xiao=5):
    """检测目录内文件中的重复代码块"""
    root = Path(mulu)
    if not root.exists():
        return {"success": False, "error": "目录不存在"}
    blocks = Counter()
    for fp in root.rglob("*.py"):
        if "__pycache__" in str(fp):
            continue
        try:
            lines = fp.read_text(encoding='utf-8', errors='ignore').split('\n')
            for i in range(len(lines) - zui_xiao):
                block = '\n'.join(l.strip() for l in lines[i:i+zui_xiao] if l.strip())
                if len(block) > 30:
                    blocks[block] += 1
        except: pass
    dups = [(b, c) for b, c in blocks.most_common(20) if c >= 3]
    jieguo = []
    for block, count in dups:
        jieguo.append(f"[重复{count}次] {block[:120]}")
    return {"success": True, "output": "\n".join(jieguo) if jieguo else "未发现重复代码块",
            "chong_fu_shu": len(dups)}


def duibi_wenjian(fp1, fp2):
    """对比两个文件的内容差异"""
    try:
        f1 = Path(fp1).read_text(encoding='utf-8', errors='ignore').split('\n')
        f2 = Path(fp2).read_text(encoding='utf-8', errors='ignore').split('\n')
    except Exception as e:
        return {"success": False, "error": f"读取失败: {e}"}
    diff = []
    max_len = min(max(len(f1), len(f2)), 200)
    for i in range(max_len):
        l1 = f1[i] if i < len(f1) else "<不存在>"
        l2 = f2[i] if i < len(f2) else "<不存在>"
        if l1 != l2:
            sign = "-" if i < len(f1) else " "
            diff.append(f"{sign}L{i+1}: {l1[:100]}")
            if i < len(f2):
                diff.append(f"+L{i+1}: {l2[:100]}")
    return {"success": True, "output": "\n".join(diff[:50]) if diff else "文件完全相同",
            "cha_yi_shu": len(diff) // 2 if diff else 0}
