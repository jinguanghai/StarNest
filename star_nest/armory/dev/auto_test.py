"""
藏剑阁·全量自测+自愈引擎 V1.0
一键测试全部兵器 → 生成报告 → 失败自动触发duanzao修复
用法: python -m armory.zidong_ceshi
"""
import sys, os, ast, inspect, json, time, tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(ROOT))

CESHI_YONGLI = {
    "wenjian_gongju": [
        ("duqu_wenjian", str(ROOT / "ceshi.py"), True, "读存在的文件"),
        ("duqu_wenjian", "/nonexistent_xyz.abc", False, "读不存在的文件"),
        ("liechu_mulu", str(ROOT), True, "列根目录"),
        ("liechu_mulu", "/nonexistent_path_xyz", False, "列不存在目录"),
        ("chuangjian_mulu", os.path.join(tempfile.gettempdir(), "_zdc_test"), True, "创建目录"),
        ("sousuo_wenjian", "*.py|" + str(ROOT), True, "搜索py文件"),
        ("xieru_wenjian", '{"path":"' + os.path.join(tempfile.gettempdir(), "_zdc_write.txt").replace('\\','/') + '","content":"test"}', True, "写文件JSON"),
    ],
    "wenjian_sousuo": [
        ("sousuo_wenjian", ("*.py", str(ROOT)), True, "glob搜索py"),
        ("sousuo_wenjian", ("*.xyzabc", "/nonexistent_dir"), False, "不存在目录返回错误"),
    ],
    "shell_mingling": [
        ("execution_mingling", "echo test_ok", True, "echo命令"),
        ("execution_mingling", "nonexistent_cmd_xyz_123", False, "不存在命令"),
    ],
    "wangluo_gongju": [
        ("jiancha_lianjie", "deepseek.com", True, "连接deepseek"),
        ("zhuawang_ye", "https://www.baidu.com", True, "抓取百度"),
    ],
    "shijian_gongju": [
        ("dangqian_shijian", "", True, "获取当前时间"),
        ("shijianchuo_zhuanhuan", str(time.time()), True, "时间戳转换"),
        ("geshihua_shijian", str(time.time()), True, "格式化时间"),
    ],
    "shuju_gongju": [
        ("tongji_zipin", "hello world hello", True, "字频统计"),
        ("tongji_cipin", "hello world hello", True, "词频统计"),
    ],
    "xitong_gongju": [
        ("xitong_xinxi", "", True, "系统信息"),
        ("cipan_kongjian", "C:", True, "磁盘空间"),
    ],
    "dabao_gongju": [
        ("shengcheng_fenfa_bao", str(ROOT / "ceshi.py"), True, "打包单文件(小范围)"),
    ],
    "git_gongju": [
        ("git_mingling", (["--version"], str(ROOT)), True, "git版本(需git)"),
    ],
    "yuyin_gongju": [
        ("is_speech_available", "", None, "检查语音(平台相关)"),
    ],
}

jiyu = {"pass": 0, "fail": 0, "skip": 0, "xiangqing": [], "shibai_gongju": set()}

def ceshi_tiaomu(gongju_ming, hanshu_ming, canshu, yuji_success, miaoshu):
    """测试单个工具函数·带超时保护"""
    name = f"{gongju_ming}.{hanshu_ming}"
    try:
        import importlib, importlib.util, threading
        
        result = {"value": None, "error": None}
        def _run():
            try:
                # 递归搜索工具文件(适配子目录)
                tool_path = None
                for fp in ROOT.rglob(f"{gongju_ming}.py"):
                    if '__pycache__' not in str(fp):
                        tool_path = str(fp)
                        break
                if not tool_path:
                    result["error"] = ImportError(f"找不到 {gongju_ming}.py")
                    return
                spec = importlib.util.spec_from_file_location(gongju_ming, tool_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                fn = getattr(mod, hanshu_ming)
                if isinstance(canshu, tuple):
                    result["value"] = fn(*canshu)
                elif isinstance(canshu, list):
                    result["value"] = fn(canshu)
                elif canshu == "":
                    result["value"] = fn()
                else:
                    result["value"] = fn(canshu)
            except Exception as e:
                result["error"] = e
        
        t = threading.Thread(target=_run, daemon=True)
        t.start()
        t.join(timeout=10)  # 10秒超时
        
        if t.is_alive():
            if yuji_success is None:
                jiyu["skip"] += 1
                jiyu["xiangqing"].append(f"  SKIP {name}: {miaoshu} (超时)")
                return True
            jiyu["fail"] += 1
            jiyu["shibai_gongju"].add(gongju_ming)
            jiyu["xiangqing"].append(f"  FAIL {name}: {miaoshu} (超时)")
            return False
        
        if result["error"]:
            raise result["error"]
        
        r = result["value"]
        # 兼容两种返回格式: {"success": True} 和 {"status": "success"}
        actual_success = None
        if isinstance(r, dict):
            if "success" in r:
                actual_success = r.get("success")
            elif "status" in r:
                actual_success = r.get("status") == "success"
            else:
                actual_success = bool(r)
        else:
            actual_success = bool(r)
        
        if yuji_success is None:
            jiyu["skip"] += 1
            jiyu["xiangqing"].append(f"  SKIP {name}: {miaoshu}")
            return True
        
        if actual_success == yuji_success:
            jiyu["pass"] += 1
            jiyu["xiangqing"].append(f"  PASS {name}: {miaoshu}")
            return True
        else:
            jiyu["fail"] += 1
            jiyu["shibai_gongju"].add(gongju_ming)
            err = r.get("error", r.get("info", "unknown")) if isinstance(r, dict) else str(r)
            jiyu["xiangqing"].append(f"  FAIL {name}: {miaoshu} (期望{yuji_success}, 实际{actual_success}, {err[:80]})")
            return False
    except Exception as e:
        if yuji_success is None:
            jiyu["skip"] += 1
            jiyu["xiangqing"].append(f"  SKIP {name}: {miaoshu} ({e})")
            return True
        jiyu["fail"] += 1
        jiyu["shibai_gongju"].add(gongju_ming)
        jiyu["xiangqing"].append(f"  FAIL {name}: {miaoshu} (异常: {e})")
        return False
    except Exception as e:
        if yuji_success is None:
            jiyu["skip"] += 1
            jiyu["xiangqing"].append(f"  SKIP {name}: {miaoshu} ({e})")
            return True
        jiyu["fail"] += 1
        jiyu["shibai_gongju"].add(gongju_ming)
        jiyu["xiangqing"].append(f"  FAIL {name}: {miaoshu} (异常: {e})")
        return False

def zidong_xiufu(shibai_gongju_liebiao):
    """对失败工具触发铸剑炉自愈"""
    if not shibai_gongju_liebiao:
        return []
    
    from star_nest.entry import SanTiXiTong
    s = SanTiXiTong()
    zl = s.zhujianlu
    
    xiefu_jieguo = []
    for gm in shibai_gongju_liebiao:
        lujing = str(ROOT / "armory" / f"{gm}.py")
        if not os.path.exists(lujing):
            xiefu_jieguo.append(f"  SKIP {gm}: 文件不存在")
            continue
        
        try:
            xuqiu = f"修复 {gm}.py 中的函数使其通过测试用例"
            jieguo = zl.quanliushuixian(xuqiu, lujing)
            if jieguo.get("success"):
                xiefu_jieguo.append(f"  FIXED {gm}: 铸剑炉已修复")
            else:
                xiefu_jieguo.append(f"  FAIL {gm}: 铸剑炉无法修复 - {jieguo.get('error','')[:100]}")
        except Exception as e:
            xiefu_jieguo.append(f"  ERR {gm}: 铸剑炉异常 - {e}")
    
    return xiefu_jieguo

def shengcheng_baogao():
    zong = jiyu["pass"] + jiyu["fail"] + jiyu["skip"]
    lv = round(100 * jiyu["pass"] / max(zong, 1), 1)
    
    print(f"\n{'='*55}")
    print(f"  藏剑阁·全量自测报告")
    print(f"{'='*55}")
    print(f"  通过: {jiyu['pass']} | 失败: {jiyu['fail']} | 跳过: {jiyu['skip']}")
    print(f"  通过率: {lv}% ({jiyu['pass']}/{zong})")
    print(f"{'='*55}")
    print(f"\n  详细结果:")
    for x in jiyu["xiangqing"]:
        print(x)
    
    if jiyu["shibai_gongju"]:
        print(f"\n  失败兵器: {list(jiyu['shibai_gongju'])}")
        print(f"  正在触发铸剑炉自愈...")
        xiefu = zidong_xiufu(list(jiyu['shibai_gongju']))
        for x in xiefu:
            print(x)
    
    print(f"\n{'='*55}")
    jielun = "全部通过" if jiyu["fail"] == 0 else f"{len(jiyu['shibai_gongju'])}件兵器需修复"
    print(f"  结论: {jielun}")
    print(f"{'='*55}")
    return jiyu["fail"] == 0

if __name__ == "__main__":
    print(f"{'='*55}")
    print(f"  藏剑阁·全量自测启动")
    print(f"{'='*55}")
    
    for gongju_ming, yongli_liebiao in CESHI_YONGLI.items():
        print(f"\n  [{gongju_ming}]")
        for yongli in yongli_liebiao:
            ceshi_tiaomu(gongju_ming, *yongli)
    
    ok = shengcheng_baogao()
    sys.exit(0 if ok else 1)
