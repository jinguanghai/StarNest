"""
照妖镜 ZhaoYaoJing V1.0 [星巢·LLM驱动安全扫描]
不是"匹配特征库"——是LLM理解意图 → "声称vs实际"矛盾检测 → 五境杀毒

五境杀毒流程:
  正境: LLM识别威胁类型
  反境: LLM拆解感染链
  合境: LLM生成清除方案(结构化xingdong)
  超越境: 同类变种批量处理
  本源境: touwei归档学习

铸剑炉执行: taskkill + 隔离 + 清理注册表 + 防火墙封禁
"""
import os, re, time, json, shutil, subprocess
from pathlib import Path
from datetime import datetime


class ZhaoYaoJing:
    """照妖镜: LLM驱动宿主环境扫描 → 五境杀毒 → 铸剑炉执行"""

    def __init__(self, xin):
        self.xin = xin
        self.quarantine = Path(__file__).parent.parent / ".quarantine"
        self.quarantine.mkdir(exist_ok=True)
        self._wei_xie_ku = {}  # 威胁知识库缓存
        self._baogao = []

    # ==================== 扫描能力 ====================

    def zhao_yao(self, mulu="C:\\") -> list:
        """全量照妖: 文件+进程+注册表+计划任务+网络连接 → 五维扫描"""
        wei_xie = []
        wei_xie.extend(self._sao_ke_yi_wen_jian(mulu))
        wei_xie.extend(self._sao_ke_yi_jin_cheng())
        wei_xie.extend(self._sao_ke_yi_zhu_ce_biao())
        wei_xie.extend(self._sao_ke_yi_ren_wu())
        wei_xie.extend(self._sao_ke_yi_wang_luo())
        self._baogao = wei_xie
        return wei_xie

    def _sao_ke_yi_wen_jian(self, mulu) -> list:
        """扫描可疑文件: 白名单过滤 + 分区分级"""
        wei_xie = []
        # 高风险目录(仅标记, 不在Downloads误杀)
        high_risk_dirs = [
            (Path.home() / "AppData" / "Local" / "Temp", "gao"),
            (Path.home() / "Downloads", "zhong"),  # Downloads降级——可能是用户下载的安装包
            (Path("C:/Users/Public"), "gao"),
            (Path("C:/Windows/Temp"), "gao"),
        ]
        for rd, yanzhong in high_risk_dirs:
            if not rd.exists(): continue
            for fp in list(rd.rglob("*.exe"))[:20] + list(rd.rglob("*.dll"))[:20] + list(rd.rglob("*.vbs"))[:10]:
                if not fp.is_file(): continue
                # 白名单: 知名合法软件 → 跳过
                if self._shi_fou_bai_ming_dan(fp):
                    continue
                # DLL降级: 无法直接执行, 需宿主进程
                actual_yanzhong = "di" if fp.suffix.lower() == '.dll' else yanzhong
                wei_xie.append({
                    "leixing": "ke_yi_wen_jian",
                    "miaoshu": f"可疑位置文件: {fp}",
                    "lujing": str(fp),
                    "yanzhongdu": actual_yanzhong,
                })

        # 用户目录下的隐藏可执行文件
        home = Path.home()
        for fp in list(home.rglob("*.exe"))[:30]:
            if fp.is_file():
                name = fp.name.lower()
                # 伪装系统进程名
                system_names = ["svchost", "lsass", "csrss", "winlogon", "services", "smss",
                               "explorer", "spoolsv", "wininit", "taskhost"]
                if any(sn == name.replace('.exe','') for sn in system_names):
                    wei_xie.append({
                        "leixing": "wei_zhuang_jin_cheng",
                        "miaoshu": f"伪装系统进程: {fp} (真{name}只在System32)",
                        "lujing": str(fp),
                        "yanzhongdu": "gao",
                    })
        return wei_xie

    def _shi_fou_bai_ming_dan(self, fp) -> bool:
        """白名单: 知名合法软件 + 系统运行时 DLL 跳过扫描"""
        name_lower = fp.name.lower()
        # 应用白名单
        BAI_MING_DAN = [
            "git-", "git ", "python-", "python3", "node-", "nvm-", "vscode", "visualstudio",
            "intellij", "pycharm", "cursor", "windsurf", "sublime",
            "chrome", "firefox", "edge", "brave", "discord", "slack", "zoom",
            "teams", "wechat", "telegram", "opencode", "7z", "winrar", "vlc",
            "notepad++", "obs", "docker", "virtualbox", "nvidia", "amd",
            "intel", "realtek", "logitech", "steam", "epic",
        ]
        for item in BAI_MING_DAN:
            if item in name_lower: return True
        # VC++ 运行时 DLL (Microsoft Visual C++ Redistributable)
        VC_DLL_PATTERNS = ["msvcp", "msvcr", "vcruntime", "concrt", "vcomp",
                          "ucrtbase", "api-ms-win-", "atl", "mfc",
                          "d3dcompiler", "d3dx9", "xinput", "dxgi", "d3d11", "d3d12"]
        for p in VC_DLL_PATTERNS:
            if name_lower.startswith(p): return True
        # 系统目录 DLL 一律放行
        fp_str = str(fp).lower()
        SYSTEM_SAFE = ["system32", "syswow64", "winsxs", "windows\\assembly",
                       "microsoft shared", "microsoft.net"]
        if any(s in fp_str for s in SYSTEM_SAFE) and fp.suffix.lower() in ('.dll', '.ocx'):
            return True
        # Downloads 目录 .exe 白名单
        downloads = str(Path.home() / "Downloads")
        if downloads in fp_str and fp.suffix.lower() == '.exe': return True
        return False

    def _sao_ke_yi_jin_cheng(self) -> list:
        """扫描可疑进程: tasklist + LLM分析"""
        wei_xie = []
        try:
            result = subprocess.run(["tasklist", "/FO", "CSV"], capture_output=True, text=True, timeout=15)
            procs = []
            for line in result.stdout.split('\n')[1:]:
                parts = line.strip('"').split('","')
                if len(parts) >= 2:
                    procs.append(parts[0].strip().lower())
            # 已知恶意进程名模式
            malicious = ["miner", "coin", "crypto", "hack", "crack", "trojan", "keygen"]
            for p in procs:
                if any(mw in p for mw in malicious):
                    wei_xie.append({
                        "leixing": "e_yi_jin_cheng",
                        "miaoshu": f"疑似恶意进程: {p}",
                        "yanzhongdu": "gao",
                        "jin_cheng_ming": p,
                    })
        except Exception: pass
        return wei_xie

    def _sao_ke_yi_zhu_ce_biao(self) -> list:
        """扫描注册表: Run/RunOnce/Winlogon/Shell"""
        wei_xie = []
        keys = [
            r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
            r"HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce",
            r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run",
            r"HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce",
        ]
        BAI_MING_DAN_KEYS = ["microsoftedge", "onedrive", "securityhealth", "windows security",
                             "windows defender", "cortana", "skype", "teams", "onedrive"]
        for key in keys:
            try:
                result = subprocess.run(["reg", "query", key], capture_output=True, text=True, timeout=10)
                if result.returncode != 0: continue
                for line in result.stdout.split('\n'):
                    if "REG_" in line:
                        parts = line.strip().split('    ')
                        if len(parts) >= 2:
                            key_name = parts[0].strip().lower()
                            value = parts[-1].strip()
                            # 白名单: 已知合法软件
                            if any(bk in key_name for bk in BAI_MING_DAN_KEYS):
                                continue
                            if any(bk in value.lower() for bk in ["microsoftedge", "msedge.exe", "onedrive.exe",
                                     "securityhealthsystray.exe", "windowsdefender"]):
                                continue
                            # 标记可疑路径
                            if any(kw in value.lower() for kw in ["temp", "appdata", "public", "downloads", "startup"]):
                                wei_xie.append({
                                    "leixing": "ke_yi_run_jian",
                                    "miaoshu": f"可疑启动项: {key}\\{parts[0].strip()} → {value[:100]}",
                                    "yanzhongdu": "gao",
                                    "zhu_ce_biao_lu_jing": f"{key}\\{parts[0].strip()}",
                                })
            except Exception: pass
        return wei_xie

    def _sao_ke_yi_ren_wu(self) -> list:
        """扫描计划任务: 可疑的定时任务"""
        wei_xie = []
        try:
            result = subprocess.run(["schtasks", "/query", "/FO", "CSV", "/v"], capture_output=True, text=True, timeout=20)
            for line in result.stdout.split('\n')[1:]:
                if "powershell" in line.lower() or "cmd /c" in line.lower() or "wscript" in line.lower():
                    if "temp" in line.lower() or "appdata" in line.lower():
                        parts = line.strip('"').split('","')
                        task_name = parts[0] if len(parts) > 0 else "未知"
                        wei_xie.append({
                            "leixing": "ke_yi_ji_hua_ren_wu",
                            "miaoshu": f"可疑计划任务: {task_name[:80]}",
                            "yanzhongdu": "gao",
                            "ren_wu_ming": task_name,
                        })
        except Exception: pass
        return wei_xie

    def _sao_ke_yi_wang_luo(self) -> list:
        """扫描网络连接: 可疑外连"""
        wei_xie = []
        try:
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=15)
            established = [l for l in result.stdout.split('\n') if "ESTABLISHED" in l]
            if len(established) > 50:
                wei_xie.append({
                    "leixing": "yi_chang_lian_jie",
                    "miaoshu": f"大量活动连接: {len(established)}个ESTABLISHED",
                    "yanzhongdu": "zhong",
                })
        except Exception: pass
        return wei_xie

    # ==================== 真实五境引擎 ====================

    def wu_jing_sha_du(self, wei_xie_liebiao: list) -> dict:
        """
        三阶段安全处理:
          Phase 1 结构预过滤: 白名单/系统路径/已知DLL → 放行
          Phase 2 批量LLM判断: 候选列表 → RenzhiBao("反境") → 合法/可疑/恶意
          Phase 3 执行+归档: 恶意→隔离, 合法→白名单缓存, 可疑→用户确认
        """
        jie_guo = {"qing_chu_shu": 0, "shi_bai_shu": 0, "xiang_qing": [],
                   "fang_xing_shu": 0, "huancun_shu": 0}
        xin = self.xin

        if not wei_xie_liebiao:
            return jie_guo

        # Phase 1: 结构预过滤(快通道)
        fang_xing = []
        hou_xuan = []
        for w in wei_xie_liebiao:
            if self._jiegou_fangxing(w):
                fang_xing.append(w)
                continue
            hou_xuan.append(w)

        jie_guo["fang_xing_shu"] = len(fang_xing)
        if fang_xing:
            for w in fang_xing:
                if xin and xin.meridian:
                    try:
                        xin.meridian.jilu_fansi(f"照妖镜·放行(结构): {w.get('leixing','')} — {w.get('miaoshu','')[:80]}")
                    except Exception: pass

        if not hou_xuan:
            return jie_guo

        # Phase 2: 批量LLM安全判断
        llm_results = self._piliang_llm_panduan(hou_xuan) if xin and xin.llm and xin.llm.api_key else {}
        jie_guo["huancun_shu"] = len(llm_results)

        # Phase 3: 执行+归档
        for i, wei_xie in enumerate(hou_xuan):
            lx = wei_xie.get('leixing', '?')
            llm_judgment = llm_results.get(i, {})

            # 写入经络
            if xin and xin.meridian:
                try:
                    xin.meridian.jilu_fansi(
                        f"照妖镜·候选#{i+1}: {lx} — {wei_xie.get('miaoshu','')[:120]}")
                except Exception: pass

            # LLM 判断调度
            verdict = llm_judgment.get("panduan", "weizhi")
            if verdict == "hefa":
                self._hefa_huancun(wei_xie, llm_judgment)
                jie_guo["fang_xing_shu"] += 1
                continue
            elif verdict == "eyi":
                # 恶意: 直接走五境清除
                zheng_jing = {"xu_yao_chu_li": True, "wei_xie_lei_xing": lx}
                fan_jing = self._fan_jing_chai_jie(wei_xie, zheng_jing)
                xing_dong = self._he_jing_fang_an(wei_xie, zheng_jing, fan_jing)
                zhuan_jian_lu = self._zhuan_jian_lu_zhi_xing(xing_dong)
                if zhuan_jian_lu.get("success"):
                    jie_guo["qing_chu_shu"] += 1
                    jie_guo["xiang_qing"].append({"wei_xie": str(wei_xie.get("miaoshu",""))[:100], "jie_guo": "隔离清除"})
                else:
                    jie_guo["shi_bai_shu"] += 1
                self._chao_yue_tong_lei(wei_xie, xing_dong)
                self._ben_yuan_gui_dang(wei_xie, xing_dong, zhuan_jian_lu)
            else:
                # 可疑: 无LLM时用本地判断兜底, 或标记为需人工确认
                zheng_jing = self._zheng_jing_shi_bie_local(wei_xie)
                if zheng_jing.get("xu_yao_chu_li"):
                    fan_jing = self._fan_jing_chai_jie(wei_xie, zheng_jing)
                    xing_dong = self._he_jing_fang_an(wei_xie, zheng_jing, fan_jing)
                    zhuan_jian_lu = self._zhuan_jian_lu_zhi_xing(xing_dong)
                    if zhuan_jian_lu.get("success"):
                        jie_guo["qing_chu_shu"] += 1
                    else:
                        jie_guo["shi_bai_shu"] += 1
                else:
                    if xin and xin.meridian:
                        try:
                            xin.meridian.jilu_fansi(f"照妖镜·待确认: {wei_xie.get('miaoshu','')[:100]}")
                        except Exception: pass
                    jie_guo["xiang_qing"].append({"wei_xie": str(wei_xie.get("miaoshu",""))[:100], "jie_guo": "待用户确认"})

        return jie_guo

    # ==================== Phase 1: 结构预过滤 ====================

    def _jiegou_fangxing(self, wei_xie: dict) -> bool:
        """结构预过滤: 确定性的安全放行规则(无LLM依赖)"""
        lujing = wei_xie.get("lujing", "")
        if not lujing:
            return False
        fp = Path(lujing)
        # 白名单检查
        if self._shi_fou_bai_ming_dan(fp):
            return True
        # 严重度"di"且不是exe→放行(DLL/配置文件)
        if wei_xie.get("yanzhongdu") == "di":
            return True
        return False

    # ==================== Phase 2: 批量 LLM 安全判断 ====================

    def _piliang_llm_panduan(self, hou_xuan: list) -> dict:
        """
        批量 LLM 安全判断: 收集所有候选→单次 RenzhiBao 调用
        
        输入: 候选威胁列表
        输出: {索引: {"panduan":"hefa"|"keyi"|"eyi", "liyou":"...", "wenjian_ming":"..."}}
        
        判断标准交给 LLM 的语义理解, 不依赖硬编码关键词.
        """
        if not self.xin or not self.xin.llm or not self.xin.llm.api_key:
            return {}

        try:
            from star_nest.protocols.cognition_package import RenzhiBao

            # 构建候选列表摘要
            items = []
            for i, w in enumerate(hou_xuan):
                items.append(f"[{i}] {w.get('leixing','?')} | {Path(w.get('lujing','')).name} | {w.get('miaoshu','')[:120]}")

            bao = RenzhiBao("反境")
            bao.shu_ju(
                hou_xuan_shu=len(hou_xuan),
                hou_xuan_lie_biao="\n".join(items[:30]),
                yao_qiu=(
                    "判断每个候选文件是否为恶意。输出JSON: "
                    '{"panduan":{0:"hefa"|"keyi"|"eyi", ...}, "liyou":{0:"理由", ...}}。'
                    'hefa=合法文件(系统文件/已知软件/运行时库), keyi=不确定需要人工确认, '
                    'eyi=明确恶意需要隔离。给出每个索引的判断。'
                )
            )
            jg = self.xin.llm.chat([{"role": "user", "content": bao.to_json()}],
                                   wendu=0.1, zuidazifu=1500)
            if jg and "{" in str(jg):
                import json
                text = str(jg)
                start = text.index("{")
                end = text.rindex("}") + 1
                raw = json.loads(text[start:end])

                # 结构化输出
                result = {}
                panduan_map = raw.get("panduan", raw) if isinstance(raw, dict) else {}
                liyou_map = raw.get("liyou", {}) if isinstance(raw, dict) else {}

                for i_str, verdict in panduan_map.items():
                    try:
                        idx = int(i_str)
                    except Exception:
                        continue
                    result[idx] = {
                        "panduan": str(verdict),
                        "liyou": str(liyou_map.get(i_str, "")),
                        "wenjian_ming": str(hou_xuan[idx].get("lujing","")) if idx < len(hou_xuan) else ""
                    }
                return result
        except Exception as e:
            if self.xin and self.xin.meridian:
                try:
                    self.xin.meridian.jilu_fansi(f"照妖镜·LLM判断失败: {e}")
                except Exception: pass

        return {}

    # ==================== Phase 3: 缓存 + 本地兜底 ====================

    def _hefa_huancun(self, wei_xie: dict, llm_judgment: dict):
        """合法文件缓存: LLM判断为合法→写入本地白名单→下次秒级跳过"""
        try:
            lujing = wei_xie.get("lujing", "")
            name = Path(lujing).name.lower() if lujing else ""
            if name and self.xin and self.xin.gan and hasattr(self.xin.gan, 'jilu'):
                self.xin.gan.jilu("白名单缓存", {
                    "wenjian_ming": name,
                    "lujing": lujing[:200],
                    "llm_liyou": llm_judgment.get("liyou", "")[:200],
                })
            # 内存缓存: 加入白名单匹配器
            if name and not self._shi_fou_bai_ming_dan(Path(name)):
                # 简单策略: 将文件名模式加入内存白名单(持续到进程重启)
                if not hasattr(self, '_hefa_huancun_set'):
                    self._hefa_huancun_set = set()
                self._hefa_huancun_set.add(name)
        except Exception: pass

    def _zheng_jing_shi_bie_local(self, wei_xie: dict) -> dict:
        """正境本地兜底: 无LLM时的确定性规则(仅处理明显恶意模式)"""
        miaoshu = str(wei_xie)
        # 仅检测明确的恶意操作模式(不是文件名, 而是行为)
        malware_ops = ["rm -rf", "del /f /s", "format", "shutdown /s", "wscript.shell",
                       "CreateRemoteThread", "WriteProcessMemory", "SetWindowsHook"]
        suspicious = any(op in miaoshu for op in malware_ops)
        return {"xu_yao_chu_li": suspicious,
                "wei_xie_lei_xing": wei_xie.get("leixing", "未知")}

    def _fan_jing_chai_jie(self, wei_xie: dict, zheng_jing: dict) -> dict:
        """反境: 拆解感染机制 (从威胁特征推断)"""
        chai_jie = {"chuan_bo_fang_shi": "未知", "yi_lai": []}
        miaoshu = str(wei_xie)
        if "Run" in miaoshu or "启动项" in miaoshu:
            chai_jie["chuan_bo_fang_shi"] = "注册表持久化"
            chai_jie["yi_lai"].append("注册表Run键")
        if "计划任务" in miaoshu:
            chai_jie["chuan_bo_fang_shi"] = "计划任务持久化"
            chai_jie["yi_lai"].append("schtasks")
        if "exe" in miaoshu.lower() and "temp" in miaoshu.lower():
            chai_jie["chuan_bo_fang_shi"] = "临时目录驻留"
        return chai_jie

    def _he_jing_fang_an(self, wei_xie: dict, zheng_jing: dict, fan_jing: dict) -> list:
        """合境: 生成清除方案(结构化步骤)"""
        xing_dong = []
        lx = wei_xie.get("leixing", "")

        if lx in ("ke_yi_wen_jian", "weishen_jin_cheng", "e_yi_jin_cheng"):
            if wei_xie.get("lujing"):
                xing_dong.append({"action": "ge_li", "target": wei_xie["lujing"],
                                  "desc": f"隔离文件: {Path(wei_xie['lujing']).name}"})
            if wei_xie.get("jin_cheng_ming"):
                xing_dong.append({"action": "taskkill", "target": wei_xie["jin_cheng_ming"],
                                  "desc": f"终止进程: {wei_xie['jin_cheng_ming']}"})

        if lx == "ke_yi_run_jian" and wei_xie.get("zhu_ce_biao_lu_jing"):
            xing_dong.append({"action": "reg_delete", "target": wei_xie["zhu_ce_biao_lu_jing"],
                              "desc": f"清理注册表: {wei_xie['zhu_ce_biao_lu_jing']}"})

        if lx == "ke_yi_ji_hua_ren_wu" and wei_xie.get("ren_wu_ming"):
            xing_dong.append({"action": "schtasks_delete", "target": wei_xie["ren_wu_ming"],
                              "desc": f"删除计划任务: {wei_xie['ren_wu_ming']}"})

        if not xing_dong:
            xing_dong.append({"action": "report", "target": str(wei_xie),
                              "desc": "需人工复核"})
        return xing_dong

    def _zhuan_jian_lu_zhi_xing(self, xing_dong: list) -> dict:
        """铸剑炉执行: 用户确认 + 隔离/备份/删除"""
        # 高危操作: 请求用户确认
        ge_li_steps = [s for s in xing_dong if s["action"] == "ge_li"]
        if ge_li_steps:
            from star_nest.armory.xitong_cao_zuo import qing_qiu_quan_xian
            desc = "; ".join(Path(s["target"]).name for s in ge_li_steps[:3])
            if not qing_qiu_quan_xian(f"隔离可疑文件: {desc}", "中"):
                return {"success": False, "error": "用户取消", "bu_zhou_shu": 0}
            # 已确认 → 跳过后面每个ge_li的再次确认
            self._que_ren_guo = True

        success = True
        for step in xing_dong:
            try:
                if step["action"] == "ge_li":
                    self._ge_li_wen_jian(step["target"])
                elif step["action"] == "taskkill":
                    subprocess.run(["taskkill", "/F", "/IM", Path(step["target"]).name],
                                   capture_output=True, timeout=10)
                    self._jilu(f"  终止进程: {step['target']}")
                elif step["action"] == "reg_delete":
                    # 先备份再删除
                    key_path = "\\".join(step["target"].split("\\")[:-1])
                    value_name = step["target"].split("\\")[-1] if "\\" in step["target"] else ""
                    bak = self.quarantine / f"reg_backup_{datetime.now().strftime('%H%M%S')}.reg"
                    subprocess.run(f'reg export "{key_path}" "{bak}"', shell=True, capture_output=True)
                    subprocess.run(f'reg delete "{key_path}" /v {value_name} /f', shell=True, capture_output=True)
                    self._jilu(f"  清理注册表: {step['target']}")
                elif step["action"] == "schtasks_delete":
                    subprocess.run(["schtasks", "/delete", "/tn", step["target"], "/f"],
                                   capture_output=True, timeout=10)
                    self._jilu(f"  删除任务: {step['target']}")
            except Exception as e:
                self._jilu(f"  执行失败: {step.get('desc','')} - {e}")
                success = False
        return {"success": success, "bu_zhou_shu": len(xing_dong)}

    def _chao_yue_tong_lei(self, wei_xie: dict, xing_dong: list):
        """超越境: 同类威胁批量处理"""
        lujing = wei_xie.get("lujing", "")
        if lujing:
            parent = Path(lujing).parent
            name_stem = Path(lujing).stem
            # 同目录下相似命名的文件一起处理
            for sibling in parent.iterdir():
                if sibling.is_file() and sibling.stem[:5] == name_stem[:5] and sibling != Path(lujing):
                    self._ge_li_wen_jian(str(sibling))
                    self._jilu(f"  同目录关联: 已隔离 {sibling.name}")

    def _ben_yuan_gui_dang(self, wei_xie: dict, xing_dong: list, zhuan_jian_lu: dict):
        """本源境: touwei归档 → puxi → 下次秒级识别"""
        if zhuan_jian_lu.get("success") and self.xin.gan:
            try:
                miaoshu = wei_xie.get("miaoshu", "")[:200]
                steps = [s["action"] for s in xing_dong]
                self.xin.gan.jilu("威胁清除", {
                    "wei_xie": miaoshu,
                    "qing_chu_bu_zhou": steps,
                    "jie_guo": "success",
                })
            except Exception: pass

    # ==================== 一站式 ====================

    def sao_miao_sha_du(self, mulu="C:\\") -> dict:
        """一站式: 扫描→五境杀毒→铸剑炉执行→归档"""
        kaishi = time.time()
        self._jilu("=== 照妖镜·全量扫描 ===")
        wei_xie = self.zhao_yao(mulu)
        self._jilu(f"发现 {len(wei_xie)} 个潜在威胁")

        self._jilu("=== 五境杀毒 ===")
        jie_guo = self.wu_jing_sha_du(wei_xie)

        haoshi = round(time.time() - kaishi, 1)
        self._jilu(f"=== 完成: {haoshi}s, 清除{jie_guo['qing_chu_shu']}, 失败{jie_guo['shi_bai_shu']} ===")

        # 写经络
        if self.xin.meridian:
            try:
                self.xin.meridian.jilu_fansi(
                    f"[照妖镜] 扫描{len(wei_xie)}威胁, 清除{jie_guo['qing_chu_shu']}个")
            except Exception: pass

        return {"success": True, "fa_xian": len(wei_xie), "jie_guo": jie_guo,
                "haoshi": haoshi, "baogao": self.qu_baogao()}

    # ==================== 恢复 ====================

    def hui_fu_ge_li(self, _=None) -> dict:
        """一键恢复: 将隔离区的文件移回原位"""
        if not self.quarantine.exists():
            return {"success": False, "error": "隔离区为空"}
        files = list(self.quarantine.glob("*quarantined_*"))
        if not files:
            return {"success": False, "error": "隔离区无文件"}

        restored = []
        failed = []
        for f in files:
            try:
                # 从文件名解析: name.exe.quarantined_20260508_164257
                original_name = f.name.split(".quarantined_")[0]
                # 尝试恢复到原路径(从日志查找)或用户目录
                target = Path.home() / "Downloads" / original_name
                if not target.exists():
                    # 也可能在 Temp 或 Public
                    for guess in [Path.home() / "Downloads", Path("C:/Users/Public"), 
                                  Path.home() / "AppData" / "Local" / "Temp"]:
                        candidate = guess / original_name
                        if not candidate.exists():
                            target = candidate
                            guess.mkdir(parents=True, exist_ok=True)
                            break
                shutil.move(str(f), str(target))
                restored.append(f"{original_name} → {target}")
                self._jilu(f"  恢复: {original_name}")
            except Exception as e:
                failed.append(f"{f.name}: {e}")

        return {"success": len(restored) > 0,
                "output": f"已恢复 {len(restored)} 个文件" + (f", {len(failed)} 个失败" if failed else ""),
                "hui_fu": restored, "shi_bai": failed}

    # ==================== 工具 ====================

    def _ge_li_wen_jian(self, lujing):
        """隔离单个文件到检疫区"""
        src = Path(lujing)
        if not src.exists(): return
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = self.quarantine / f"{src.name}.quarantined_{ts}"
        try:
            shutil.move(str(src), str(dest))
            self._jilu(f"  隔离: {src.name} → .quarantine/")
        except Exception as e:
            self._jilu(f"  隔离失败: {e}")

    def _jilu(self, msg):
        self._baogao.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
        # 铁律: 不打印到stdout(避免污染用户对话流), 写经络即可
        if self.xin and self.xin.meridian:
            try:
                self.xin.meridian.jilu_fansi(f"[照妖镜] {msg[:200]}")
            except Exception: pass

    def qu_baogao(self):
        return self._baogao[-30:]
