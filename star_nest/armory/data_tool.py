"""
藏剑阁·数据工具 V1.0
JSON读写·文本统计·CSV转换·纯标准库
"""
import json, os
from pathlib import Path

def duqu_json(canshu):
    """读取JSON文件·参数:文件路径"""
    p = Path(str(canshu).strip().strip('"').strip("'"))
    if not p.exists():
        return {"success": False, "error": f"文件不存在: {p}"}
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        return {"success": True, "output": json.dumps(data, ensure_ascii=False)[:2000], "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def xieru_json(canshu):
    """写入JSON文件·参数:JSON字符串{path:,data:}"""
    try:
        d = json.loads(str(canshu)) if canshu.startswith("{") else {"path": "output.json", "data": canshu}
        p = Path(d.get("path", "output.json"))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(d.get("data", {}), ensure_ascii=False, indent=2), encoding='utf-8')
        return {"success": True, "output": f"已写入 {p}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def tongji_zipin(canshu):
    """统计字频·参数:文本字符串"""
    s = str(canshu)
    from collections import Counter
    counts = Counter(s)
    top = counts.most_common(20)
    result = {k: v for k, v in top}
    return {"success": True, "output": json.dumps(result, ensure_ascii=False)[:500], "data": result}

def tongji_cipin(canshu):
    """统计词频·参数:文本字符串(按空格分词)"""
    s = str(canshu)
    from collections import Counter
    words = [w for w in s.split() if len(w) > 1]
    counts = Counter(words).most_common(20)
    result = {k: v for k, v in counts}
    return {"success": True, "output": json.dumps(result, ensure_ascii=False)[:500], "data": result}

def csv_zhuan_list(canshu):
    """CSV转列表·参数:CSV文本"""
    import csv, io
    try:
        reader = csv.reader(io.StringIO(str(canshu)))
        rows = list(reader)
        return {"success": True, "output": f"{len(rows)}行 {len(rows[0]) if rows else 0}列", "data": rows}
    except Exception as e:
        return {"success": False, "error": str(e)}
