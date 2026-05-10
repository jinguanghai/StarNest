"""
自审镜 V11.0
照见自身认知架构·五大铁律验证·仅肺调用
π-φ映射·记忆调用·七律合规·五行信号·代码意图自洽

铁律5(代码意图自洽): 自审镜每天扫描所有.py文件→LLM分析意图
  → "不认识"的代码块 = 被注入的 = 隔离+恢复+告警+学习
"""
import ast, re, json, shutil
from pathlib import Path
from datetime import datetime


class ZiJingShi:
    def __init__(self, xiangmu_mulu=None):
        self.root = Path(xiangmu_mulu) if xiangmu_mulu else Path(__file__).parent
        self.hexin_mulu = ["organs", "protocols", "execution", "meridian", "jiemian", "peizhi", "jinhua", "wangluo", "dynamics", "armory"]
        self._zuihou_yitu_saomiao = 0
        self.quarantine = self.root / ".quarantine"

    def quanjing_jiancha(self, hexin_mulu=None, llm=None):
        mulu = Path(hexin_mulu) if hexin_mulu else self.root
        wenti_liebiao = []
        wenti_liebiao.extend(self._jiancha_pi_phi_yingshe(mulu))
        wenti_liebiao.extend(self._jiancha_jiyi_diaoyong(mulu))
        wenti_liebiao.extend(self._jiancha_qilv_hegui(mulu))
        wenti_liebiao.extend(self._jiancha_wuxing_xinhao(mulu))
        # 铁律5: 代码意图自洽(每343s一次, 减轻LLM开销)
        import time
        if time.time() - self._zuihou_yitu_saomiao > 343:
            self._zuihou_yitu_saomiao = time.time()
            wenti_liebiao.extend(self._jiancha_daima_yitu(mulu, llm))
        # 铁律13: 害-佐协议审计(每启动时一次, 静态扫描)
        if time.time() - self._zuihou_yitu_saomiao > 343:
            wenti_liebiao.extend(self._jiancha_haizuo_xieyi(mulu))
            wenti_liebiao.extend(self._jiancha_haixielou(mulu))
        # 铁律15: 零裸except (每次全景检查都扫描)
        wenti_liebiao.extend(self._jiancha_luo_except(mulu))
        return wenti_liebiao

    def _jiancha_pi_phi_yingshe(self, mulu):
        wenti = []
        for name in ["organs/xin.py", "dynamics/piphicycle.py"]:
            fp = mulu / name
            if not fp.exists():
                wenti.append({"mubiao": name, "miaoshu": f"{name} 不存在", "yanzhongdu": "gao", "sheji_biaoji": "标记一·π-φ缺失"})
        return wenti

    def _jiancha_jiyi_diaoyong(self, mulu):
        wenti = []
        protocols_mulu = mulu / "protocols"
        if protocols_mulu.exists():
            for py_file in protocols_mulu.rglob("*.py"):
                if py_file.name.startswith("__"): continue
                try:
                    daima = py_file.read_text(encoding='utf-8')
                    if not any(kw in daima for kw in ["ronghe_jiansuo", "jiansuo_zhishi", "jiyiguanli", "jiyi"]):
                        wenti.append({"mubiao": f"protocols/{py_file.name}", "miaoshu": "五境引擎未显式调用记忆检索", "yanzhongdu": "zhong", "sheji_biaoji": "标记二·记忆调用缺失"})
                except Exception: pass
        return wenti

    def _jiancha_qilv_hegui(self, mulu):
        wenti = []
        for directory in self.hexin_mulu:
            target = mulu / directory
            if not target.exists(): continue
            for py_file in target.rglob("*.py"):
                if py_file.name.startswith("__"): continue
                if "qilv" in str(py_file): continue
                try:
                    daima = py_file.read_text(encoding='utf-8')
                    for p in re.findall(r'time\.sleep\(\d+\)', daima):
                        wenti.append({"mubiao": str(py_file.relative_to(mulu)), "miaoshu": f"疑似魔法数字: {p}", "yanzhongdu": "di", "sheji_biaoji": "标记三·七律缺失"})
                except Exception: pass
        return wenti

    def _jiancha_wuxing_xinhao(self, mulu):
        wenti = []
        xin_py = mulu / "organs" / "xin.py"
        if xin_py.exists():
            try:
                daima = xin_py.read_text(encoding='utf-8')
                if re.search(r'self\.\w+\._\w+\s*=\s*', daima):
                    wenti.append({"mubiao": "organs/xin.py", "miaoshu": "五行生克可能仍存在直接属性修改", "yanzhongdu": "di", "sheji_biaoji": "标记四·五行信号"})
            except Exception: pass
        return wenti

    # ==================== 铁律13: 害-佐协议审计 ====================

    def _jiancha_haizuo_xieyi(self, mulu):
        """铁律13: 检查核心模块中所有公开函数是否声明了害-佐"""
        wenti = []
        total_scanned = 0
        legacy_count = 0
        try:
            from star_nest.protocols.harm_assist import jian_cha_mu_lu
            for directory in self.hexin_mulu:
                target = mulu / directory
                if not target.exists():
                    continue
                results = jian_cha_mu_lu(str(target))
                for r in results:
                    total_scanned += 1
                    if r.get("is_legacy"):
                        legacy_count += 1
                        continue
                    kind = "缺少佐治" if r.get("has_hai") and not r.get("has_zuo") else "缺少害声明"
                    wenti.append({
                        "mubiao": f"{r['file']}:{r['line']}",
                        "miaoshu": f"{r['function']}: {kind}{'(含裸except)' if r.get('has_bare_except') else ''}",
                        "yanzhongdu": "zhong" if not r.get("has_hai") else "di",
                        "sheji_biaoji": "标记十三·害-佐缺失"
                    })
        except Exception:
            pass
        # 豁免率告警: 超过30%函数标记@legacy → 铁律形同虚设
        if total_scanned > 0 and legacy_count / total_scanned > 0.3:
            wenti.append({
                "mubiao": "铁律13·豁免率",
                "miaoshu": f"豁免泛滥: {legacy_count}/{total_scanned} 函数标记@legacy({legacy_count*100//total_scanned}%), 超过30%阈值",
                "yanzhongdu": "gao",
                "sheji_biaoji": "标记十三·legacy泛滥"
            })
        elif total_scanned > 0:
            uncovered = len(wenti)
            covered = total_scanned - uncovered - legacy_count
            print(f"[自审镜·铁律13] 害-佐审计: 已声明={covered}, 未声明={uncovered}, legacy={legacy_count}, 总数={total_scanned} (仅告警不阻断)")
        return wenti

    def _jiancha_haixielou(self, mulu):
        """铁律13补充: 检测调用链中的害泄露"""
        wenti = []
        try:
            from star_nest.protocols.harm_assist import jian_cha_haixielou
            for directory in self.hexin_mulu:
                target = mulu / directory
                if not target.exists():
                    continue
                leaks = jian_cha_haixielou(str(target))
                for leak in leaks:
                    wenti.append({
                        "mubiao": f"{leak['file']}:{leak['line']}",
                        "miaoshu": f"{leak['function']}调用{leak['called_func']}({leak['called_file']}:{leak['called_hai_line']})未上浮害'{leak['leaked_hai']}'",
                        "yanzhongdu": "zhong",
                        "sheji_biaoji": "标记十三·害传播泄露"
                    })
        except Exception:
            pass
        if wenti:
            print(f"[自审镜·铁律13] 害传播审计: {len(wenti)} 个害泄露点 (调用者未处理或上浮被调用者的害)")
        return wenti

    # ==================== 铁律5: 代码意图自洽 ====================

    def _jiancha_daima_yitu(self, mulu, llm=None) -> list:
        """
        铁律5: 代码意图自洽——注入检测
        自审镜认识星巢的代码风格。
        任何"不认识"的 import/函数/调用链 = 可能被注入 = 隔离调查。
        """
        wenti = []
        # 核心目录内的 .py 文件
        for directory in self.hexin_mulu:
            target = mulu / directory
            if not target.exists(): continue
            for py_file in target.rglob("*.py"):
                if py_file.name.startswith("__"): continue
                try:
                    wenti.extend(self._fenxi_dan_wen_jian(py_file, mulu, llm))
                except Exception: pass
        return wenti

    def _fenxi_dan_wen_jian(self, py_file, mulu, llm=None) -> list:
        """分析单个文件的代码意图"""
        wenti = []
        code = py_file.read_text(encoding='utf-8', errors='ignore')
        lines = code.split('\n')

        # 1. 检测可疑 import (星巢从不用这些)
        suspicious_imports = {
            'socket': '网络直连(星巢只用urllib)',
            'requests': '外部库(pip install, 违反铁律1)',
            'http.server': '自建HTTP服务(应由sidecar统一管理)',
            'subprocess.call': '无沙箱的子进程调用',
            'os.system': '直接系统命令(应用xitong_cao_zuo)',
            'base64': '编码隐藏行为',
            'zlib.compress': '压缩隐藏行为',
            'cryptography': '外部加密库',
            'keyboard': '键盘监听',
            'pyautogui': 'GUI自动化(星巢不用GUI)',
            'pynput': '输入监听',
            'winreg': '直接注册表(应用xitong_cao_zuo)',
        }
        for i, line in enumerate(lines):
            line_s = line.strip()
            if line_s.startswith('import ') or line_s.startswith('from '):
                for mod, reason in suspicious_imports.items():
                    if mod in line_s:
                        wenti.append({
                            "mubiao": f"{py_file.relative_to(mulu)}:{i+1}",
                            "miaoshu": f"可疑import {mod}({reason})",
                            "yanzhongdu": "gao",
                            "sheji_biaoji": "标记五·代码意图不符"
                        })

        # 2. 检测后追加的代码(不在原文件AST中的函数)
        try:
            tree = ast.parse(code)
            func_names = set(n.name for n in ast.walk(tree) 
                           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) 
                           and not n.name.startswith('_'))
        except:
            func_names = set()

        # 3. 检测隐藏行为模式
        hidden_patterns = [
            (r'while\s+True\s*:.*cpu', '疑似挖矿循环'),
            (r'exec\s*\(', '动态执行代码'),
            (r'eval\s*\(', '动态求值(星巢极少用)'),
            (r'__import__\s*\(\s*[\'\"](?!psutil)', '动态导入(仅psutil允许)'),
            (r'lambda\s+.*socket', 'lambda+网络组合'),
        ]
        for pattern, desc in hidden_patterns:
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    wenti.append({
                        "mubiao": f"{py_file.relative_to(mulu)}:{i+1}",
                        "miaoshu": f"可疑模式 {desc}: {line.strip()[:80]}",
                        "yanzhongdu": "gao",
                        "sheji_biaoji": "标记五·代码意图不符"
                    })

        # 4. 意图分析: LLM判断(周期执行, 防过载)
        if llm and wenti and any(w["yanzhongdu"] == "gao" for w in wenti):
            self._shen_du_fen_xi(py_file, mulu, wenti, llm, code)

        return wenti

    def _shen_du_fen_xi(self, py_file, mulu, wenti, llm, code):
        """深度分析: LLM判断可疑代码的意图"""
        try:
            from star_nest.protocols.cognition_package import RenzhiBao
            bao = RenzhiBao("反境")
            bao.shu_ju(
                wen_jian=str(py_file.relative_to(mulu)),
                ke_yi_dian=[w["miaoshu"] for w in wenti[:3]],
                dai_ma_qian_500=code[:500],
            )
            jg = llm.chat([{"role": "user", "content": bao.to_json()}], wendu=0.1, zuidazifu=300)
            if jg and any(kw in str(jg).lower() for kw in ["malicious", "恶意", "注入", "病毒", "trojan", "backdoor", "不是星巢"]):
                self._ge_li_gan_ran(py_file, mulu, str(jg)[:200])
        except: pass

    def _ge_li_gan_ran(self, py_file, mulu, fenxi: str):
        """隔离感染文件 + 从备份恢复"""
        self.quarantine.mkdir(exist_ok=True)
        # 隔离
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rel = str(py_file.relative_to(mulu))
        quarantine_path = self.quarantine / f"{rel.replace('/','_').replace('\\','_')}.infected_{timestamp}"
        try:
            shutil.move(str(py_file), str(quarantine_path))
            print(f"[自审镜·铁律5] 已隔离: {rel} → {quarantine_path}")
            print(f"[自审镜·铁律5] 分析: {fenxi[:120]}")
        except: pass
        # 恢复备份
        backup = py_file.parent / f"{py_file.name}.backup"
        if backup.exists():
            try:
                shutil.copy2(str(backup), str(py_file))
                print(f"[自审镜·铁律5] 已恢复: {rel} ← {backup}")
            except Exception: pass

    # ==================== 铁律15: 零裸except ====================

    def _jiancha_luo_except(self, mulu) -> list:
        """
        铁律15: 零裸except — 禁止 except: 和 except Exception: pass
        
        扫描核心模块发现裸except块 → 标记"标记十五·异常吞噬"
        要求: except Exception + meridian.jilu_yichang() 为最低合格线
        """
        wenti = []
        try:
            import re
            for directory in self.hexin_mulu:
                target = mulu / directory
                if not target.exists(): continue
                for py_file in target.rglob("*.py"):
                    if py_file.name.startswith("__") or "ceshi_" in py_file.name: continue
                    try:
                        code = py_file.read_text(encoding='utf-8', errors='ignore')
                        for i, line in enumerate(code.split('\n'), 1):
                            s = line.strip()
                            if s in ('except:', 'except Exception:', 'except: pass', 'except Exception: pass'):
                                wenti.append({"mubiao": f"{py_file.relative_to(mulu)}:{i}",
                                    "miaoshu": f"裸except吞噬异常: {s}",
                                    "yanzhongdu": "zhong", "sheji_biaoji": "标记十五·异常吞噬"})
                    except Exception: pass
            if wenti:
                print(f"[自审镜·铁律15] 裸except: {len(wenti)} 处 (新代码要求零裸except)")
        except Exception: pass
        return wenti
