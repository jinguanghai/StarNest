"""
藏剑阁·文件工具 V1.0
读/写/列/建/搜 — 编程体文件操作完整兵器
"""
import os, json, re
from pathlib import Path

def duqu_wenjian(canshu):
    """读取文件内容·参数:文件路径(字符串)"""
    path = str(canshu).strip().strip('"').strip("'")
    p = Path(path)
    if not p.exists():
        return {"success": False, "error": f"文件不存在: {path}"}
    try:
        content = p.read_text(encoding='utf-8', errors='replace')
        return {"success": True, "output": content[:5000], "data": {"path": str(p), "size": len(content)}}
    except Exception as e:
        return {"success": False, "error": str(e)}

def liechu_mulu(canshu):
    """列出目录内容·参数:目录路径(字符串)"""
    path = str(canshu).strip().strip('"').strip("'")
    if not path or path in ("无参数", ".", "当前"):
        path = "."
    p = Path(path)
    if not p.exists():
        return {"success": False, "error": f"目录不存在: {path}"}
    try:
        items = []
        for item in sorted(p.iterdir()):
            t = "DIR" if item.is_dir() else "FILE"
            sz = item.stat().st_size if item.is_file() else 0
            items.append(f"{t}  {item.name}  ({sz}B)" if sz else f"{t}  {item.name}")
        return {"success": True, "output": "\n".join(items[:60]), "data": [i.name for i in sorted(p.iterdir())]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def chuangjian_mulu(canshu):
    """创建目录·参数:目录路径(字符串)"""
    path = str(canshu).strip().strip('"').strip("'")
    if not path or path in ("无参数",):
        return {"success": False, "error": "请指定目录路径"}
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return {"success": True, "output": f"目录已创建: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def sousuo_wenjian(canshu):
    """搜索文件·参数:模式(字符串,如*.py) 或 模式|目录"""
    s = str(canshu).strip().strip('"').strip("'")
    if "|" in s:
        moshi, mulu = s.split("|", 1)
    else:
        moshi, mulu = s, "."
    try:
        from star_nest.armory.wenjian_sousuo import sousuo_wenjian as _sw
        r = _sw(moshi.strip(), mulu.strip())
        if r.get("status") == "success":
            return {"success": True, "output": "\n".join(r.get("data", [])[:40]), "data": r.get("data", [])}
        return {"success": False, "error": r.get("info", "搜索失败")}
    except Exception as e:
        return {"success": False, "error": f"搜索异常: {e}"}

def xieru_wenjian(canshu):
    """写入文件内容·参数:JSON字符串{"path":"...","content":"..."}"""
    s = str(canshu).strip()
    try:
        if s.startswith("{"):
            d = json.loads(s)
            path = d.get("path", "")
            content = d.get("content", "")
        else:
            parts = s.split("\n", 1)
            path = parts[0].strip().strip('"').strip("'")
            content = parts[1] if len(parts) > 1 else ""
        # 路径校验
        import re
        if not re.search(r'[\\/:]|[A-Za-z]:', path):
            return {"success": False, "error": f"无效路径格式: {path}"}
    except Exception:
        return {"success": False, "error": "参数格式错误"}
    if not path:
        return {"success": False, "error": "未指定文件路径"}
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')
        return {"success": True, "output": f"已写入 {len(content)} 字符 -> {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
