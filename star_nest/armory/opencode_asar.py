"""
藏剑阁·OpenCode asar 读写器 V1.0
纯Python stdlib实现·解析+提取+重打包·零外部依赖
格式: [preamble 0~16B][JSON header][file data...]
"""
import json, struct, os, shutil, copy, hashlib
from pathlib import Path
from datetime import datetime


def _du_json(path):
    """读取asar文件头JSON·返回 (preamble, header_dict, json_bytes)"""
    with open(path, 'rb') as f:
        data = f.read(4_000_000)
    # 找JSON起始
    start = data.index(b'{"files"')
    preamble = data[:start]
    # 数大括号找JSON结束
    depth = 0; end = start
    for i in range(start, len(data)):
        if data[i] == 0x7b: depth += 1
        elif data[i] == 0x7d: depth -= 1
        if depth == 0: end = i + 1; break
    json_bytes = data[start:end]
    return preamble, json.loads(json_bytes.decode('utf-8')), json_bytes


def duqu_asar(path):
    """读取asar·返回 {files: {path: bytes}, header, preamble, json_bytes, data_start}"""
    path = Path(path)
    if not path.exists():
        return {"success": False, "error": f"文件不存在: {path}"}

    preamble, header, json_bytes = _du_json(str(path))
    data_start = len(preamble) + len(json_bytes)
    
    result = {"success": True, "preamble": preamble, "header": header,
              "json_bytes": json_bytes, "data_start": data_start, "files": {}}
    
    def _flatten(files_dict):
        stack = [("", files_dict)]
        entries = []
        while stack:
            prefix, d = stack.pop()
            for name, info in d.items():
                path = f"{prefix}/{name}"
                if 'files' in info:
                    stack.append((path, info['files']))
                else:
                    entries.append((path, int(info.get('offset', '0')), int(info.get('size', 0))))
        return entries
    
    entries = _flatten(header.get('files', {}))
    with open(str(path), 'rb') as f:
        for filepath, offset, size in entries:
            f.seek(data_start + offset)
            result["files"][filepath] = f.read(size)
    
    return result


def duqu_wenjian(path, asar_path):
    """从asar中读取单个文件·返回 bytes"""
    preamble, header, json_bytes = _du_json(asar_path)
    data_start = len(preamble) + len(json_bytes)
    
    stack = [("", header['files'])]
    while stack:
        prefix, d = stack.pop()
        for name, info in d.items():
            fpath = f"{prefix}/{name}"
            if 'files' in info:
                stack.append((fpath, info['files']))
            elif fpath == path or f"/{path}" == fpath:
                offset = int(info.get('offset', '0'))
                size = int(info.get('size', 0))
                with open(asar_path, 'rb') as f:
                    f.seek(data_start + offset)
                    return f.read(size)
    return None


def chongdabao_asar(asar_data, output_path):
    """重打包asar·输入 duqu_asar 结果·输出新asar文件"""
    header = copy.deepcopy(asar_data.get("header", {}))
    files = asar_data.get("files", {})
    preamble = asar_data.get("preamble", b'\x04\x00\x00\x00\x10>\x1a\x00\x0c>\x1a\x00\x05>\x1a\x00')

    # 按路径排序收集所有文件
    all_entries = []
    stack = [(header['files'], "")]
    while stack:
        d, prefix = stack.pop(0)  # FIFO preserve order
        for name, info in d.items():
            fpath = f"{prefix}/{name}".lstrip("/")
            if 'files' in info:
                stack.append((info['files'], fpath))
            else:
                data = None
                candidates = [fpath, f"/{fpath}", fpath.lstrip("/")]
                if fpath.startswith('/'):
                    candidates.extend([fpath[1:]])
                for c in candidates:
                    if c in files:
                        data = files[c]
                        break
                    if c.lstrip('/') in files:
                        data = files[c.lstrip('/')]
                        break
                if data is not None:
                    all_entries.append((fpath, data, info))
    
    # 按路径排序确保顺序一致
    all_entries.sort(key=lambda x: x[0])
    
    # 重建offset/size
    current_offset = 0
    ordered_data = []
    for fpath, data, info in all_entries:
        info['offset'] = str(current_offset)
        info['size'] = len(data)
        ordered_data.append(data)
        current_offset += len(data)

    # 序列化header JSON
    json_str = json.dumps(header, separators=(',', ':'), ensure_ascii=False)
    json_bytes = json_str.encode('utf-8')

    # 写入文件
    with open(output_path, 'wb') as f:
        f.write(preamble)
        f.write(json_bytes)
        for data in ordered_data:
            f.write(data)

    return {"success": True, "path": str(output_path),
            "daxiao": os.path.getsize(output_path)}


def liechu_asar(path):
    """列出asar内所有文件路径与大小"""
    if not Path(path).exists():
        return {"success": False, "error": f"文件不存在: {path}"}
    
    _, header, _ = _du_json(path)
    result = []
    stack = [("", header['files'])]
    while stack:
        prefix, d = stack.pop()
        for name, info in d.items():
            fpath = f"{prefix}/{name}"
            if 'files' in info:
                stack.append((fpath, info['files']))
            else:
                result.append({"path": fpath, "size": info.get('size', 0),
                               "offset": info.get('offset', '0')})
    return {"success": True, "shuliang": len(result), "wenjian": result}


def beifen_asar(path):
    """备份asar·返回备份路径"""
    path = Path(path)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.parent / f"app.asar.backup.{ts}"
    shutil.copy2(path, backup)
    return str(backup)


def huifu_asar(path, backup_path=None):
    """从备份恢复asar"""
    path = Path(path)
    if backup_path:
        shutil.copy2(backup_path, path)
        return str(backup_path)
    backups = sorted(path.parent.glob("app.asar.backup.*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if backups:
        shutil.copy2(backups[0], path)
        return str(backups[0])
    return None
