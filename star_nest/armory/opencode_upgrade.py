"""
藏剑阁·OpenCode 升级编排器 V1.0
三体安全模型: 运行体诊断→编程体锻造→复制体验证→编程体部署→运行体确认
"""
import json, os, shutil, sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

ASAR_PATH = Path(r'C:\Users\jin\AppData\Local\Programs\OpenCode\resources\app.asar')
YML_PATH = Path(r'C:\Users\jin\AppData\Local\Programs\OpenCode\resources\app-update.yml')
SHENGJI_DANGAN = Path(__file__).parent.parent / 'shared_memory' / 'opencode_shengji.json'


def zhenduan():
    """运行体: 诊断当前状态"""
    from star_nest.armory.opencode_asar import liechu_asar, _du_json, duqu_wenjian

    jg = {"shijian": datetime.now().isoformat(), "asar_lujing": str(ASAR_PATH)}

    # 版本
    jg["opencode_banben"] = "1.14.39"
    jg["asar_cunzai"] = ASAR_PATH.exists()
    if ASAR_PATH.exists():
        jg["asar_daxiao"] = os.path.getsize(ASAR_PATH)

    # 文件数
    try:
        r = liechu_asar(str(ASAR_PATH))
        jg["asar_wenjian_shu"] = r.get("shuliang", 0)
    except:
        jg["asar_wenjian_shu"] = None

    # 补丁状态
    jg["yida_buding"] = _jiancha_buding()

    # 备份
    baks = sorted(ASAR_PATH.parent.glob("app.asar.backup.*"), key=lambda p: p.stat().st_mtime, reverse=True)
    jg["beifen_shu"] = len(baks)
    jg["zuijin_beifen"] = str(baks[0]) if baks else "无"

    # 升级历史
    jg["shengji_lishi"] = _du_shengji_dangan()

    _cun_shengji_dangan({"zuihou_zhenduan": jg})
    return jg


def _jiancha_buding():
    """检查补丁是否已应用"""
    try:
        from star_nest.armory.opencode_asar import duqu_wenjian
        js = duqu_wenjian('/out/main/chunks/node-BCdD_j2u.js', str(ASAR_PATH))
        if js:
            return {
                "watcher_yizhi": b'watcher binding suppressed by xingchao' in js,
                "gengxin_jinyong": YML_PATH.exists() and 'disabled' in (YML_PATH.read_text(encoding='utf-8') if YML_PATH.exists() else ''),
            }
    except:
        pass
    return {"watcher_yizhi": False, "gengxin_jinyong": False}


def _du_shengji_dangan():
    if SHENGJI_DANGAN.exists():
        try:
            return json.loads(SHENGJI_DANGAN.read_text(encoding='utf-8'))
        except:
            pass
    return {"cishu": 0, "lishi": []}


def _cun_shengji_dangan(data):
    SHENGJI_DANGAN.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def shengji():
    """编程体: 执行升级"""
    print("[编程体] 开始升级...")

    # 步骤1: 备份
    print("  1. 备份 asar...")
    from star_nest.armory.opencode_asar import beifen_asar
    bak = beifen_asar(str(ASAR_PATH))
    print(f"     备份: {bak}")

    # 步骤2: 应用补丁
    print("  2. 应用补丁...")
    from star_nest.armory.opencode_patch import yingyong_quanbu_buding
    jg = yingyong_quanbu_buding(str(ASAR_PATH))
    if not jg.get("success"):
        print(f"     FAILED: {jg}")
        return {"success": False, "error": "补丁应用失败", "detail": jg}

    patched_path = jg.get("output_path")
    print(f"     新asar: {patched_path}")

    # 步骤3: 复制体验证
    print("  3. 复制体验证...")
    from star_nest.armory.opencode_asar import liechu_asar
    try:
        r = liechu_asar(patched_path)
        new_count = r.get("shuliang", 0)
        print(f"     文件数: {new_count}")
    except Exception as e:
        print(f"     验证失败: {e}")
        return {"success": False, "error": f"复制体验证失败: {e}"}

    # 步骤4: 部署
    print("  4. 部署...")
    try:
        shutil.copy2(patched_path, str(ASAR_PATH))
        print(f"     已替换: {ASAR_PATH}")
    except Exception as e:
        print(f"     部署失败: {e}")
        return {"success": False, "error": f"部署失败: {e}"}

    # 步骤5: 记录
    dangan = _du_shengji_dangan()
    dangan["cishu"] = dangan.get("cishu", 0) + 1
    lishi = dangan.get("lishi", [])
    lishi.append({
        "shijian": datetime.now().isoformat(),
        "beifen": bak,
        "zhuangtai": "wan_cheng"
    })
    dangan["lishi"] = lishi
    _cun_shengji_dangan(dangan)

    print("  [编程体] 升级完成")
    return {"success": True, "output": "OpenCode 升级完成·请重启 OpenCode 以应用更改"}


def huigun():
    """编程体: 回滚到最近备份"""
    print("[编程体] 回滚...")
    from star_nest.armory.opencode_asar import huifu_asar
    restored = huifu_asar(str(ASAR_PATH))
    if restored:
        print(f"  已恢复: {restored}")
        return {"success": True, "output": f"已回滚到: {restored}"}
    return {"success": False, "error": "无可用备份"}


def shengji_zhuangtai():
    """运行体: 返回升级状态"""
    zt = zhenduan()
    return {
        "success": True,
        "banben": zt["opencode_banben"],
        "asar_daxiao": zt["asar_daxiao"],
        "yida_buding": zt["yida_buding"],
        "beifen_shu": zt["beifen_shu"],
        "zuijin_beifen": zt["zuijin_beifen"],
        "shengji_cishu": zt.get("shengji_lishi", {}).get("cishu", 0),
        "output": json.dumps(zt, ensure_ascii=False, indent=2)
    }
