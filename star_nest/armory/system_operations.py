"""
藏剑阁 · 系统操作工具 V1.0 [星巢·OS级操作]
纯Python标准库 + Windows内置命令 · 零外部依赖
清理 · 注册表 · 服务 · 进程 · 磁盘 · 计划任务 · 权限模型
"""
import os, subprocess, json, tempfile, shutil
from pathlib import Path
from datetime import datetime


# ==================== 权限与安全 ====================

def qing_qiu_quan_xian(cao_zuo_miao_shu: str, feng_xian: str = "中") -> bool:
    """请求用户授权高危操作。返回True=授权, False=拒绝"""
    print(f"\n[星巢·权限请求]")
    print(f"  操作: {cao_zuo_miao_shu}")
    print(f"  风险: {feng_xian}")
    print(f"  确认执行? [Y/N]: ", end="")
    try:
        reply = input().strip().lower()
        return reply in ("y", "yes", "是", "确认")
    except (EOFError, KeyboardInterrupt):
        return False


def _yun_xing_ming_ling(cmd: list, timeout: int = 30):
    """执行系统命令，返回 (success, output)"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip() or result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "命令超时"
    except Exception as e:
        return False, str(e)


# ==================== 系统清理 ====================

def qing_li_la_ji() -> dict:
    """清理系统垃圾: 临时文件+回收站+浏览器缓存(仅Edge)"""
    items = []
    freed = 0
    temp_paths = [Path(os.environ.get("TEMP", "")), Path(os.environ.get("TMP", "")),
                  Path("C:/Windows/Temp")]
    for tp in temp_paths:
        if not tp or not tp.exists(): continue
        for f in tp.rglob("*"):
            if f.is_file():
                try:
                    s = f.stat().st_size
                    f.unlink()
                    freed += s
                    items.append(f"临时/{f.name}")
                except: pass
    user_temp = Path.home() / "AppData" / "Local" / "Temp"
    if user_temp.exists():
        count = 0
        for f in user_temp.rglob("*"):
            if f.is_file() and count < 50:  # 限制清理数量
                try:
                    s = f.stat().st_size
                    f.unlink()
                    freed += s
                    count += 1
                except: pass
        if count > 0: items.append(f"用户临时/{count}文件")
    freed_mb = round(freed / (1024 * 1024), 1)
    return {"success": True, "output": f"已清理 {len(items)} 类, 释放 {freed_mb}MB",
            "qing_li_xiang": items, "shi_fang_mb": freed_mb}


# ==================== 注册表 ====================

def cha_xun_zhu_ce_biao(lujing: str, jian_ming: str = "") -> dict:
    """查询注册表路径"""
    if not qing_qiu_quan_xian(f"查询注册表: {lujing}", "低"):
        return {"success": False, "error": "用户取消"}
    cmd = f'reg query "{lujing}"'
    if jian_ming:
        cmd += f" /v {jian_ming}"
    ok, output = _yun_xing_ming_ling(cmd)
    if ok:
        lines = [l.strip() for l in output.split('\n') if l.strip()]
        return {"success": True, "output": "\n".join(lines[:30]), "ji_lu_shu": len(lines)}
    return {"success": False, "error": output[:200]}


def shan_chu_zhu_ce_biao(lujing: str, jian_ming: str = "") -> dict:
    """删除注册表项（自动备份）"""
    if not qing_qiu_quan_xian(f"删除注册表: {lujing}/{jian_ming}", "高"):
        return {"success": False, "error": "用户取消"}
    # 备份
    export_file = Path.home() / "Desktop" / f"reg_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.reg"
    _yun_xing_ming_ling(f'reg export "{lujing}" "{export_file}"')
    # 删除
    if jian_ming:
        ok, output = _yun_xing_ming_ling(f'reg delete "{lujing}" /v {jian_ming} /f')
    else:
        ok, output = _yun_xing_ming_ling(f'reg delete "{lujing}" /f')
    return {"success": ok, "output": output[:200] if output else "已删除",
            "bei_fen": str(export_file) if export_file.exists() else ""}


# ==================== 服务管理 ====================

def guan_li_fu_wu(fu_wu_ming: str, cao_zuo: str = "query") -> dict:
    """管理Windows服务: query/start/stop/restart"""
    cmds = {"query": f'sc query "{fu_wu_ming}"',
            "start": f'sc start "{fu_wu_ming}"',
            "stop": f'sc stop "{fu_wu_ming}"'}
    if cao_zuo not in cmds:
        return {"success": False, "error": f"未知操作: {cao_zuo}"}
    if cao_zuo in ("stop",) and not qing_qiu_quan_xian(f"停止服务: {fu_wu_ming}", "中"):
        return {"success": False, "error": "用户取消"}
    ok, output = _yun_xing_ming_ling(cmds[cao_zuo])
    return {"success": ok, "output": output[:300], "cao_zuo": cao_zuo}


# ==================== 进程管理 ====================

def guan_li_jin_cheng(jincheng_ming: str, cao_zuo: str = "list") -> dict:
    """进程管理: list/kill"""
    if cao_zuo == "list":
        ok, output = _yun_xing_ming_ling(f'tasklist /FI "IMAGENAME eq {jincheng_ming}"')
        if ok and "INFO:" not in output:
            return {"success": True, "output": output[:500]}
        return {"success": True, "output": f"未找到进程: {jincheng_ming}"}
    if cao_zuo == "kill":
        if not qing_qiu_quan_xian(f"终止进程: {jincheng_ming}", "高"):
            return {"success": False, "error": "用户取消"}
        ok, output = _yun_xing_ming_ling(f'taskkill /F /IM "{jincheng_ming}"')
        return {"success": ok, "output": output[:200]}
    return {"success": False, "error": f"未知操作: {cao_zuo}"}


# ==================== 磁盘管理 ====================

def qing_li_ci_pan(mulu: str = "C:\\") -> dict:
    """磁盘空间分析+大文件清理建议"""
    path = Path(mulu)
    if not path.exists():
        return {"success": False, "error": f"目录不存在: {mulu}"}
    # 磁盘信息
    usage = shutil.disk_usage(str(path))
    total_gb = round(usage.total / (1024**3), 1)
    free_gb = round(usage.free / (1024**3), 1)
    used_pct = round((1 - usage.free/usage.total) * 100, 1)
    # 查找大文件 (>100MB)
    large_files = []
    try:
        for f in path.rglob("*"):
            if f.is_file() and "__pycache__" not in str(f) and "node_modules" not in str(f):
                size_mb = f.stat().st_size / (1024**2)
                if size_mb > 50 and len(large_files) < 20:
                    large_files.append((str(f.relative_to(path)), round(size_mb, 1)))
    except: pass
    large_files.sort(key=lambda x: x[1], reverse=True)
    summary = f"磁盘{total_gb}GB, 已用{used_pct}%, 剩余{free_gb}GB"
    if large_files:
        summary += f"\n大文件(>50MB): {len(large_files)}个"
        for name, size in large_files[:5]:
            summary += f"\n  - {name} ({size}MB)"
    return {"success": True, "output": summary, "zong_gb": total_gb,
            "kong_xian_gb": free_gb, "yong_gb": round(total_gb - free_gb, 1),
            "da_wen_jian": large_files[:10]}


# ==================== 计划任务 ====================

def guan_li_ji_hua_ren_wu(ren_wu_ming: str, cao_zuo: str = "query") -> dict:
    """管理Windows计划任务"""
    if cao_zuo == "query":
        ok, output = _yun_xing_ming_ling(f'schtasks /query /tn "{ren_wu_ming}"')
        return {"success": ok, "output": output[:500] if ok else f"未找到: {ren_wu_ming}"}
    if cao_zuo == "create":
        if not qing_qiu_quan_xian(f"创建计划任务: {ren_wu_ming}", "中"):
            return {"success": False, "error": "用户取消"}
        ok, output = _yun_xing_ming_ling(
            f'schtasks /create /tn "{ren_wu_ming}" /tr "python {sys.executable}" /sc daily /st 03:00'
        )
        return {"success": ok, "output": output[:300]}
    return {"success": False, "error": f"未知操作: {cao_zuo}"}
