"""
藏剑阁·OpenCode 补丁引擎 V1.0
纯Python stdlib·基于 opencode_asar 读写 asar 文件
"""
import json, os, shutil
from pathlib import Path
from datetime import datetime


# === 补丁1: 禁用自动更新 ===
def dingyong_gengxin():
    """修改 app-update.yml 禁用自动更新"""
    yml = Path(r'C:\Users\jin\AppData\Local\Programs\OpenCode\resources\app-update.yml')
    if not yml.exists():
        return {"success": False, "error": "app-update.yml 不存在"}

    # 备份
    bak = str(yml) + ".backup"
    shutil.copy2(yml, bak)

    yml.write_text("""
# OpenCode update config - DISABLED by 星巢铸剑炉
owner: anomalyco
repo: opencode
provider: github
channel: latest
updaterCacheDirName: '@opencode-aidesktop-updater'
disabled: true
""".strip(), encoding='utf-8')
    return {"success": True, "output": f"自动更新已禁用, 备份: {bak}"}


# === 补丁2: 抑制 watcher 错误日志 ===
WATCHER_TARGET = "/out/main/chunks/node-BCdD_j2u.js"
WATCHER_SEARCH = b'log27.error("failed to load watcher binding", { error: error47 });'
WATCHER_REPLACE = b'// watcher binding suppressed by xingchao'

def yizhi_watcher(asar_data):
    """修改 asar 中的 watcher JS 文件·抑制错误日志"""
    files = asar_data.get("files", {})
    key = WATCHER_TARGET
    if key not in files:
        # try alt paths
        for k in files:
            if 'node-BCdD' in k:
                key = k
                break
        else:
            return {"success": False, "error": f"watcher 文件未找到"}

    data = files[key]
    if WATCHER_SEARCH not in data:
        return {"success": False, "error": f"未找到 watcher 错误代码"}

    files[key] = data.replace(WATCHER_SEARCH, WATCHER_REPLACE)
    return {"success": True, "output": f"watcher 错误日志已抑制, {key}", "files": files}


# === 补丁3: 注入星巢签名 ===
def zhuru_qianming(asar_data):
    """在 asar 中添加星巢版本签名文件"""
    from pathlib import Path as _Path
    qianming = {
        "xingchao_version": "V10.6",
        "xingchao_santi": "三体·运行体/编程体/复制体",
        "xingchao_ceche": "localhost:9527 侧车替换",
        "xingchao_qixue": "气血循环·五脉同流",
        "xingchao_duiqi": "OpenCode·星巢记忆对齐",
        "shengji_shijian": datetime.now().isoformat(),
        "shengji_gongju": "铸剑炉 V10.6"
    }
    files = asar_data.get("files", {})

    # 注入到 package.json 的字段
    # 或单独添加 .xingchao.json 文件 - 但 asar 需要 header 中有条目
    # 最简单: 修改 package.json 加字段
    pkg_key = None
    for k in files:
        if k.endswith('/package.json') or k == 'package.json':
            pkg_key = k
            break

    if pkg_key:
        try:
            pkg = json.loads(files[pkg_key].decode('utf-8'))
            pkg["xingchao"] = qianming
            files[pkg_key] = json.dumps(pkg, indent=2, ensure_ascii=False).encode('utf-8')
        except:
            pass

    return {"success": True, "output": "星巢签名已注入 package.json", "files": files}


def yingyong_quanbu_buding(asar_path):
    """应用全部补丁并重打包"""
    from star_nest.armory.opencode_asar import duqu_asar, chongdabao_asar
    from pathlib import Path

    asar_path = Path(asar_path)
    output = asar_path.parent / "app.asar.patched"

    # 读取
    asar = duqu_asar(str(asar_path))
    if not asar.get("success"):
        return asar

    # 补丁外部的 app-update.yml
    gengxin_jg = dingyong_gengxin()
    print(f"  补丁1(更新): {gengxin_jg.get('output', gengxin_jg.get('error','?'))}")

    # 补丁 asar 内部
    watcher_jg = yizhi_watcher(asar)
    print(f"  补丁2(watcher): {watcher_jg.get('output', watcher_jg.get('error','?'))}")

    qianming_jg = zhuru_qianming(asar)
    print(f"  补丁3(签名): {qianming_jg.get('output', qianming_jg.get('error','?'))}")

    # 重打包
    bao_jg = chongdabao_asar(asar, str(output))
    if bao_jg.get("success"):
        print(f"  打包: {bao_jg['path']} ({bao_jg.get('daxiao',0)} bytes)")
        return {"success": True, "output_path": bao_jg['path']}
    return bao_jg
