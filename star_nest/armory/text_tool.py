"""
藏剑阁 · 文本工具 V1.0
纯Python标准库 · 零外部依赖
文本搜索替换 · 格式转换 · 批量处理 · 字数统计 · diff对比
"""
import os, re, json
from pathlib import Path


def sousuo_wenben(mulu, moshi, kuozhan=".py"):
    """在目录中递归搜索正则模式, 返回匹配结果"""
    jieguo = []
    root = Path(mulu)
    if not root.exists():
        return {"success": False, "error": f"目录不存在: {mulu}"}
    try:
        re.compile(moshi)
    except re.error as e:
        return {"success": False, "error": f"正则错误: {e}"}
    for fp in root.rglob(f"*{kuozhan}"):
        try:
            content = fp.read_text(encoding='utf-8', errors='ignore')
            for i, line in enumerate(content.split('\n'), 1):
                if re.search(moshi, line):
                    jieguo.append(f"{fp.relative_to(root)}:{i}: {line.strip()[:120]}")
        except: pass
    return {"success": True, "output": "\n".join(jieguo[:100]) if jieguo else "无匹配",
            "pipei_shu": len(jieguo)}


def tihuan_wenben(mulu, moshi, tihuan, kuozhan=".py"):
    """递归搜索并替换文本(自动备份)"""
    root = Path(mulu)
    if not root.exists():
        return {"success": False, "error": f"目录不存在: {mulu}"}
    count = 0
    for fp in root.rglob(f"*{kuozhan}"):
        try:
            content = fp.read_text(encoding='utf-8', errors='ignore')
            new_content = re.sub(moshi, tihuan, content)
            if new_content != content:
                # 备份
                bak = fp.with_suffix(fp.suffix + '.bak')
                if not bak.exists():
                    fp.rename(bak)
                    fp.write_text(new_content, encoding='utf-8')
                else:
                    fp.write_text(new_content, encoding='utf-8')
                count += 1
        except: pass
    return {"success": True, "output": f"已替换 {count} 个文件"}


def tongji_zifu(mulu, kuozhan=".py"):
    """统计目录中文件的字数/行数/文件数"""
    root = Path(mulu)
    if not root.exists():
        return {"success": False, "error": f"目录不存在: {mulu}"}
    tongji = {"wenjian": 0, "zong_hang": 0, "zong_zi": 0, "leixing": {}}
    for fp in root.rglob(f"*{kuozhan}"):
        try:
            content = fp.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            ext = fp.suffix
            tongji["wenjian"] += 1
            tongji["zong_hang"] += len(lines)
            tongji["zong_zi"] += len(content)
            tongji["leixing"][ext] = tongji["leixing"].get(ext, 0) + 1
        except: pass
    return {"success": True,
            "output": f"{tongji['wenjian']}个文件, {tongji['zong_hang']}行, {tongji['zong_zi']}字符",
            "tongji": tongji}


def geshi_zhuanhuan(shuru, laiyuan="csv", mubiao="json"):
    """格式转换: csv↔json↔markdown_table"""
    if laiyuan == "csv" and mubiao == "json":
        lines = shuru.strip().split('\n')
        if len(lines) < 2:
            return {"success": False, "error": "CSV至少需要标题行+一行数据"}
        headers = [h.strip() for h in lines[0].split(',')]
        rows = []
        for line in lines[1:]:
            vals = [v.strip() for v in line.split(',')]
            rows.append(dict(zip(headers, vals)))
        return {"success": True, "output": json.dumps(rows, ensure_ascii=False, indent=2), "shu_ju": rows}

    if laiyuan == "json" and mubiao == "csv":
        try:
            data = json.loads(shuru)
        except:
            return {"success": False, "error": "JSON解析失败"}
        if not data:
            return {"success": False, "error": "空JSON"}
        headers = list(data[0].keys())
        lines = [','.join(headers)]
        for row in data:
            lines.append(','.join(str(row.get(h, '')) for h in headers))
        return {"success": True, "output": '\n'.join(lines)}

    if laiyuan == "json" and mubiao == "markdown":
        try:
            data = json.loads(shuru)
        except:
            return {"success": False, "error": "JSON解析失败"}
        if not data:
            return {"success": False, "error": "空JSON"}
        headers = list(data[0].keys())
        md = "| " + " | ".join(headers) + " |\n"
        md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        for row in data:
            md += "| " + " | ".join(str(row.get(h, '')) for h in headers) + " |\n"
        return {"success": True, "output": md}

    return {"success": False, "error": f"不支持的转换: {laiyuan}→{mubiao}"}
