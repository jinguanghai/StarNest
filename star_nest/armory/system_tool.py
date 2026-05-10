"""
藏剑阁·系统工具 V1.0
系统信息·资源状态·磁盘空间·纯标准库
"""
import platform, os, sys, shutil, json

def xitong_xinxi(canshu=""):
    """系统信息·返回OS/Python/平台信息"""
    info = {
        "xitong": platform.system(),
        "banben": platform.version(),
        "jiqi": platform.machine(),
        "chuliqi": platform.processor(),
        "python": sys.version,
        "lujing": sys.executable,
        "bianma": sys.getdefaultencoding(),
    }
    return {"success": True, "output": json.dumps(info, ensure_ascii=False, indent=2), "data": info}

def ziyuan_zhuangtai(canshu=""):
    """资源状态·CPU/内存使用(仅stdlib可用信息)"""
    info = {"xitong": platform.system(), "python": sys.version[:30]}
    return {"success": True, "output": json.dumps(info, ensure_ascii=False)[:500], "data": info}

def cipan_kongjian(canshu=""):
    """磁盘空间·参数:盘符(如C:)"""
    path = str(canshu).strip().strip('"').strip("'") or "C:\\"
    try:
        usage = shutil.disk_usage(path)
        info = {
            "lujing": path,
            "zong_GB": round(usage.total / (1024**3), 1),
            "yiyong_GB": round(usage.used / (1024**3), 1),
            "keyong_GB": round(usage.free / (1024**3), 1),
        }
        return {"success": True, "output": f"{info['keyong_GB']}GB可用/{info['zong_GB']}GB总", "data": info}
    except Exception as e:
        return {"success": False, "error": str(e)}

def dangqian_jincheng_xinxi(canshu=""):
    """当前进程信息"""
    info = {
        "pid": os.getpid(),
        "cwd": os.getcwd(),
        "python": sys.version[:20],
    }
    return {"success": True, "output": f"PID:{info['pid']}", "data": info}

import json  # for xitong_xinxi
