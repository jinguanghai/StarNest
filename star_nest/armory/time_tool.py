"""
藏剑阁·时间工具 V1.0
提供时间相关操作,纯标准库
"""
import time
from datetime import datetime

def dangqian_shijian(canshu=""):
    """获取当前时间·返回ISO格式字符串"""
    return {"success": True, "output": datetime.now().isoformat(), "data": {"shijianchuo": time.time()}}

def shijianchuo_zhuanhuan(canshu):
    """时间戳转换·参数:时间戳(数字)或ISO字符串"""
    s = str(canshu).strip()
    try:
        if s.replace('.','').replace('-','').replace(':','').replace('T','').isdigit():
            ts = float(s) if '.' in s else int(s)
            dt = datetime.fromtimestamp(ts)
        else:
            dt = datetime.fromisoformat(s)
        return {"success": True, "output": dt.isoformat(), "data": {"shijianchuo": dt.timestamp()}}
    except Exception as e:
        return {"success": False, "error": str(e)}

def jisuan_haoshi(canshu=""):
    """计算耗时·返回当前时间戳"""
    return {"success": True, "output": str(time.time()), "data": {"shijianchuo": time.time()}}

def geshihua_shijian(canshu):
    """格式化时间·参数:格式字符串(如%Y-%m-%d)或时间戳"""
    s = str(canshu).strip()
    try:
        ts = float(s) if s.replace('.','').isdigit() else time.time()
        fmt = "%Y-%m-%d %H:%M:%S" if not s or s.replace('.','').isdigit() else s
        if fmt == s: fmt = "%Y-%m-%d %H:%M:%S"
        result = datetime.fromtimestamp(ts).strftime(fmt)
        return {"success": True, "output": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
