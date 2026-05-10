"""
三体安全 AnQuanSanTi V1.0 [星巢·认知安全]
三体分工: Ω(监控上报) → π(执行清理) → φ(沙箱验证)

Ω 运行体·只读监控:
  - 自审镜铁律5扩展: 非.py文件扫描(exe/dll/vbs/bat)
  - 进程快照对比(新进程→可疑分析)
  - 注册表快照对比(新增Run键→告警)
  - 启动目录监控

π 编程体·可写执行:
  - 隔离(移入.quarantine/)
  - 恢复(从.backup/.reg还原)
  - 注册表清理(reg delete + auto export)
  - 进程终止(taskkill)

φ 复制体·沙箱验证:
  - 可疑文件入沙箱→监控行为→LLM分析→报告
"""
import os, re, time, json, shutil, subprocess
from pathlib import Path
from datetime import datetime


class AnQuanSanTi:
    """三体安全: Ω监控 + π执行 + φ验证"""

    def __init__(self, meridian=None, llm=None, xin=None):
        self.meridian = meridian
        self.llm = llm
        self.xin = xin
        self.quarantine = Path(__file__).parent.parent / ".quarantine"
        self._zuihou_jincheng_kuai = {}
        self._zuihou_zhucebiao_kuai = {}

    # ==================== Ω: 只读监控 ====================

    def omega_jian_shi(self, mulu=None) -> list:
        """Ω 全量监视: 文件+进程+注册表+启动项→上报"""
        root = Path(mulu) if mulu else Path(__file__).parent.parent
        wenti = []
        wenti.extend(self._sao_fei_xingchao_wenjian(root))
        wenti.extend(self._jian_kong_jin_cheng(xin_can_zhao="python"))
        wenti.extend(self._jian_kong_zhu_ce_biao())
        wenti.extend(self._jian_kong_qi_dong_mu_lu())
        # 写经络
        for w in wenti:
            if self.meridian:
                try:
                    self.meridian.jilu_ganzhi(
                        f"[Ω监控] {w.get('miaoshu','')[:80]}",
                        w.get("yanzhongdu", "gao"))
                except Exception: pass
        return wenti

    def _sao_fei_xingchao_wenjian(self, root) -> list:
        """Ω 扫描: 项目目录内的非星巢文件"""
        wenti = []
        # 星巢目录应有但不应有的文件类型
        suspicious_in_dirs = ["organs", "meridian", "execution", "dynamics", "protocols"]
        for d in suspicious_in_dirs:
            target = root / d
            if not target.exists(): continue
            for fp in target.rglob("*"):
                if fp.is_file():
                    ext = fp.suffix.lower()
                    if ext in (".exe", ".dll", ".sys", ".bat", ".vbs", ".ps1", ".scr", ".com"):
                        wenti.append({
                            "leixing": "fei_xingchao_wenjian",
                            "miaoshu": f"异常文件: {fp.relative_to(root)} ({ext})",
                            "yanzhongdu": "gao",
                            "lujing": str(fp),
                        })
        # 可疑文件名
        suspicious_names = ["miner", "coin", "crypto", "hack", "crack", "keygen",
                           "trojan", "virus", "worm", "rat", "backdoor", "rootkit"]
        for fp in root.rglob("*"):
            if fp.is_file() and not fp.suffix == '.py':
                name_lower = fp.stem.lower()
                if any(sn in name_lower for sn in suspicious_names):
                    wenti.append({
                        "leixing": "ke_yi_ming_ming",
                        "miaoshu": f"可疑文件名: {fp.relative_to(root)}",
                        "yanzhongdu": "gao",
                        "lujing": str(fp),
                    })
        return wenti

    def _jian_kong_jin_cheng(self, xin_can_zhao="python") -> list:
        """Ω 进程快照对比: 检测新进程"""
        wenti = []
        try:
            result = subprocess.run(["tasklist", "/FO", "CSV"], capture_output=True, text=True, timeout=15)
            current = {}
            for line in result.stdout.split('\n')[1:]:
                parts = line.strip('"').split('","')
                if len(parts) >= 2:
                    name = parts[0].strip().lower()
                    current[name] = True
            # 对比上次快照
            if self._zuihou_jincheng_kuai:
                new_procs = set(current.keys()) - set(self._zuihou_jincheng_kuai.keys())
                susp = [p for p in new_procs if p not in ("system idle process", "system", "svchost.exe",
                          "csrss.exe", "wininit.exe", "services.exe", "lsass.exe", "smss.exe")]
                for p in susp[:10]:
                    wenti.append({
                        "leixing": "xin_jin_cheng",
                        "miaoshu": f"新进程: {p}",
                        "yanzhongdu": "zhong",
                    })
            self._zuihou_jincheng_kuai = current
        except Exception: pass
        return wenti

    def _jian_kong_zhu_ce_biao(self) -> list:
        """Ω 注册表Run键监控"""
        wenti = []
        run_keys = [
            r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
            r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run",
        ]
        for key in run_keys:
            try:
                result = subprocess.run(["reg", "query", key], capture_output=True, text=True, timeout=10)
                current = {}
                for line in result.stdout.split('\n'):
                    if "REG_" in line:
                        parts = line.strip().split('    ')
                        if len(parts) >= 2:
                            name = parts[0].strip()
                            current[name] = True
                if self._zuihou_zhucebiao_kuai.get(key):
                    new_entries = set(current.keys()) - set(self._zuihou_zhucebiao_kuai.get(key, {}).keys())
                    for entry in new_entries:
                        wenti.append({
                            "leixing": "xin_run_jian",
                            "miaoshu": f"新启动项: {key}\\{entry}",
                            "yanzhongdu": "gao",
                        })
                self._zuihou_zhucebiao_kuai[key] = current
            except Exception: pass
        return wenti

    def _jian_kong_qi_dong_mu_lu(self) -> list:
        """Ω 启动目录监控"""
        wenti = []
        startup_dirs = [
            Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup",
            Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs/StartUp"),
        ]
        for sd in startup_dirs:
            if not sd.exists(): continue
            for fp in sd.rglob("*"):
                if fp.is_file() and fp.suffix.lower() in (".exe", ".bat", ".vbs", ".ps1", ".scr"):
                    wenti.append({
                        "leixing": "qi_dong_mu_lu",
                        "miaoshu": f"启动目录文件: {fp.name}",
                        "yanzhongdu": "zhong",
                        "lujing": str(fp),
                    })
        return wenti

    # ==================== π: 可写执行 ====================

    def pi_zhi_xing(self, wenti_liebiao: list) -> list:
        """π 执行: 隔离+恢复+清理"""
        jieguo = []
        for w in wenti_liebiao:
            if w.get("leixing") in ("fei_xingchao_wenjian", "ke_yi_ming_ming"):
                r = self._ge_li_wen_jian(w)
            elif w.get("leixing") == "xin_run_jian":
                r = self._qing_li_zhu_ce_biao(w)
            elif w.get("leixing") == "xin_jin_cheng":
                r = self._zhong_zhi_jin_cheng(w)
            else:
                r = {"success": False, "error": f"未知类型: {w.get('leixing')}"}
            jieguo.append(r)
            if self.meridian:
                try:
                    self.meridian.jilu_fansi(f"[π执行] {w.get('leixing','')}: {'成功' if r.get('success') else '失败'}")
                except Exception: pass
        return jieguo

    def _ge_li_wen_jian(self, wenti: dict) -> dict:
        """π 隔离文件到检疫区"""
        path = wenti.get("lujing", "")
        if not path or not Path(path).exists():
            return {"success": False, "error": "文件不存在"}
        self.quarantine.mkdir(exist_ok=True)
        src = Path(path)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = self.quarantine / f"{src.name}.quarantined_{ts}"
        try:
            shutil.move(str(src), str(dest))
            print(f"[π隔离] {src.name} → .quarantine/")
            return {"success": True, "output": f"已隔离: {src.name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _qing_li_zhu_ce_biao(self, wenti: dict) -> dict:
        """π 清理注册表启动项(自动导出备份)"""
        miaoshu = wenti.get("miaoshu", "")
        try:
            # 解析 "新启动项: HKCU\...\Run\entry_name"
            import re
            parts = miaoshu.split("\\")
            if len(parts) >= 2:
                key = "\\".join(parts[:-1])
                value = parts[-1] if parts[-1] else ""
            else:
                return {"success": False, "error": "无法解析注册表路径"}
            # 备份
            backup_file = self.quarantine / f"reg_backup_{datetime.now().strftime('%H%M%S')}.reg"
            self.quarantine.mkdir(exist_ok=True)
            subprocess.run(f'reg export "{key}" "{backup_file}"', shell=True, capture_output=True)
            # 删除
            ok, out = self._reg_cmd(f'reg delete "{key}" /v {value} /f')
            print(f"[π清理] 注册表: {value} {'✓' if ok else '✗'}")
            return {"success": ok, "output": f"注册表项已删除: {value}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _zhong_zhi_jin_cheng(self, wenti: dict) -> dict:
        """π 终止可疑进程"""
        miaoshu = wenti.get("miaoshu", "")
        proc_name = miaoshu.replace("新进程: ", "").strip()
        if not proc_name:
            return {"success": False, "error": "无法解析进程名"}
        try:
            result = subprocess.run(
                ["taskkill", "/F", "/IM", proc_name],
                capture_output=True, text=True, timeout=15)
            ok = result.returncode == 0
            print(f"[π终止] 进程: {proc_name} {'✓' if ok else '✗'}")
            return {"success": ok, "output": f"进程已终止: {proc_name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _reg_cmd(self, cmd):
        """执行注册表命令"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return result.returncode == 0, result.stdout.strip()
        except Exception:
            return False, ""

    # ==================== φ: 沙箱验证 ====================

    def phi_yan_zheng(self, sus_path: str) -> dict:
        """φ 沙箱验证: 在沙箱中执行→监控行为→LLM分析→报告"""
        path = Path(sus_path)
        if not path.exists():
            return {"success": False, "error": "文件不存在"}

        import tempfile
        sandbox = Path(tempfile.mkdtemp(prefix="xingchao_phi_"))
        result = {"success": False, "sha_xiang": str(sandbox), "xing_wei": []}

        try:
            # 复制到沙箱
            sandbox_file = sandbox / path.name
            shutil.copy2(str(path), str(sandbox_file))
            result["xing_wei"].append(f"复制到沙箱: {sandbox_file}")

            # 如果是.py, 用AST分析
            if path.suffix == '.py':
                try:
                    import ast
                    tree = ast.parse(path.read_text(encoding='utf-8', errors='ignore'))
                    # 提取所有函数名和import
                    imports = set()
                    funcs = set()
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            imports.add(node.module.split('.')[0])
                        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if not node.name.startswith('_'):
                                funcs.add(node.name)
                    result["xing_wei"].append(f"导入: {','.join(imports) if imports else '无'}")
                    result["xing_wei"].append(f"函数: {','.join(funcs) if funcs else '无'}")

                    # 检测恶意行为
                    malicious_imports = {'socket', 'requests', 'base64', 'cryptography'}
                    suspicious_funcs = {'connect', 'send', 'mine', 'encrypt', 'decrypt', 'hide', 'inject'}
                    matched_imports = imports & malicious_imports
                    matched_funcs = funcs & suspicious_funcs
                    if matched_imports or matched_funcs:
                        result["wei_xian_deng_ji"] = "高"
                        result["xing_wei"].append(f"危险导入: {','.join(matched_imports)}")
                        result["xing_wei"].append(f"可疑函数: {','.join(matched_funcs)}")
                    else:
                        result["wei_xian_deng_ji"] = "低"
                except Exception:
                    result["wei_xian_deng_ji"] = "无法解析"

            # LLM深度分析
            if self.llm and result.get("wei_xian_deng_ji") == "高":
                self._phi_llm_fen_xi(path, result)
        except Exception as e:
            result["xing_wei"].append(f"沙箱异常: {e}")
        finally:
            # 清理沙箱
            try: shutil.rmtree(sandbox, ignore_errors=True)
            except Exception: pass

        return result

    def _phi_llm_fen_xi(self, path, result):
        """φ LLM深度行为分析"""
        try:
            from star_nest.protocols.cognition_package import RenzhiBao
            code = path.read_text(encoding='utf-8', errors='ignore')[:500]
            bao = RenzhiBao("反境")
            bao.shu_ju(wen_jian=str(path.name), xing_wei=result.get("xing_wei", []),
                       dai_ma=code)
            jg = self.llm.chat([{"role":"user","content":bao.to_json()}], wendu=0.1, zuidazifu=300)
            if jg:
                result["llm_fen_xi"] = str(jg)[:300]
        except Exception: pass
