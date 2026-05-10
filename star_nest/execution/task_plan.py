"""
任务计划 RenWuJiHua V1.0 [星巢·长任务执行引擎]
DMAIC + 五境嵌入 · 分步执行 · 检查点 · 场景感知 · 流程模板

长任务不是锻造——是"锻造+执行+验证+再锻造"的复合流程。
每个步骤是一个DMAIC循环, Analyze阶段嵌入五境深度分析。
"""
import json, time, re
from pathlib import Path
from datetime import datetime


class BuZhou:
    """DMAIC 步骤: Define→Measure→Analyze(五境嵌入)→Improve→Control"""

    def __init__(self, mingcheng: str, mubiao: str = "", zhibiao: dict = None):
        self.mingcheng = mingcheng          # 步骤名称
        self.mubiao = mubiao                 # 目标描述
        self.zhibiao = zhibiao or {}         # 成功指标 {"wenjian_shu": "<10"}
        self._shiji_before = {}              # 执行前数据
        self._shiji_after = {}               # 执行后数据
        self.dabiao = False                  # 是否达标
        self.piancha = {}                    # 偏差详情
        self.zhuangtai = "pending"           # pending/running/completed/failed/skipped
        self.fenxi_jieguo = ""               # Analyze阶段产出
        self.execution_rizhi = []              # 执行日志
        self.kaishi = 0
        self.jieshu = 0

    def define(self, mubiao: str, zhibiao: dict = None):
        """Define: 设置步骤目标和成功指标"""
        self.mubiao = mubiao
        if zhibiao:
            self.zhibiao.update(zhibiao)
        return self

    def measure(self, xin):
        """Measure: 采集执行前场景数据"""
        try:
            data = {"shijian": datetime.now().isoformat()}
            # 文件统计
            try:
                root = Path(__file__).parent.parent
                data["py_wenjian"] = len(list(root.rglob("*.py")))
            except Exception: pass
            # 磁盘
            try:
                import shutil
                usage = shutil.disk_usage(str(Path(__file__).parent.parent.anchor))
                data["cipan_free_pct"] = round(usage.free / usage.total * 100, 1)
            except Exception: pass
            self._shiji_before = data
            self._jilu(f"Measure: py={data.get('py_wenjian','?')} disk={data.get('cipan_free_pct','?')}%")
        except Exception: pass
        return self

    def execute(self, xin, fangfa: str = "auto", xuqiu: str = ""):
        """执行步骤: 自动调用工具/锻造/对话"""
        self.zhuangtai = "running"
        self.kaishi = time.time()
        self._jilu(f"开始执行: {self.mingcheng}")

        try:
            if fangfa == "duanzao" and xin.zhujianlu:
                jg = xin.zhujianlu.duanzao(xuqiu or self.mubiao)
                if jg and jg.get("success"):
                    self._shiji_after = {"success": True, "output": jg.get("output", "")[:200]}
                else:
                    self._shiji_after = {"success": False, "error": jg.get("error", "") if jg else "未知"}
            elif fangfa == "zhijian" and xin.zhujianlu:
                jg = xin.zhujianlu._execution(xuqiu or self.mubiao)
                self._shiji_after = jg if isinstance(jg, dict) else {"success": True, "output": str(jg)[:200]}
            elif fangfa == "duihua" and xin.llm:
                reply = xin._duihua(xuqiu or self.mubiao)
                self._shiji_after = {"success": True, "output": str(reply)[:200]}
            else:
                # 自动: 走_chuli管道
                result = xin._chuli(xuqiu or self.mubiao)
                self._shiji_after = {"success": result is not None, "output": str(result)[:200] if result else ""}
        except Exception as e:
            self._shiji_after = {"success": False, "error": str(e)}
            self.zhuangtai = "failed"

        self.jieshu = time.time()
        self._jilu(f"执行完成: {round(self.jieshu-self.kaishi,2)}s")
        return self

    def analyze(self, xin) -> str:
        """Analyze: 嵌入五境深度分析(偏差→根因→方案)"""
        if not self._shiji_after:
            self.analyze_status()
            if self.dabiao:
                self.zhuangtai = "completed"
                return "达标，无需分析"

        # 检查是否达标
        self.analyze_status()
        if self.dabiao:
            self.zhuangtai = "completed"
            self._jilu("Analyze: 达标，跳过")
            return "达标"

        # 构造偏差描述, 交给五境深度分析
        shiji = self._shiji_after
        wenti = (
            f"步骤'{self.mingcheng}'未达标。\n"
            f"目标: {self.mubiao}\n"
            f"指标要求: {json.dumps(self.zhibiao, ensure_ascii=False)}\n"
            f"实际结果: {json.dumps(shiji, ensure_ascii=False)[:500]}\n"
            f"执行前环境: {json.dumps(self._shiji_before, ensure_ascii=False)[:200]}"
        )

        self._jilu("Analyze: 嵌入五境深度分析...")
        try:
            self.fenxi_jieguo = xin.fuwu_protocols_fenxi(wenti, shiji.get("error", ""))
        except Exception:
            self.fenxi_jieguo = f"[反境] 偏差: {json.dumps(shiji, ensure_ascii=False)[:200]}"

        self._jilu(f"Analyze产出: {str(self.fenxi_jieguo)[:150]}")
        return self.fenxi_jieguo

    def improve(self, xin, fenxi: str = ""):
        """Improve: 消费Analyze的五境方案→锻造/重规划"""
        if self.dabiao:
            return self

        plan_text = fenxi or self.fenxi_jieguo

        # 场景1: 合境产出了duanzao建议 → 锻造
        if plan_text and any(kw in str(plan_text) for kw in ["锻造", "duanzao", "生成代码"]):
            self._jilu("Improve: 触发锻造")
            try:
                jg = xin.zhujianlu.duanzao(
                    f"修复{self.mingcheng}: {self.mubiao}\n分析: {str(plan_text)[:300]}"
                )
                self._shiji_after = jg if isinstance(jg, dict) else {"success": True, "output": str(jg)[:200]}
                self.zhuangtai = "completed" if jg and jg.get("success") else "failed"
            except Exception as e:
                self.zhuangtai = "failed"
                self._jilu(f"Improve锻造异常: {e}")

        # 场景2: 方案建议替代路径 → 标记跳过
        elif plan_text and any(kw in str(plan_text) for kw in ["跳过", "替代", "无需"]):
            self.zhuangtai = "skipped"
            self._jilu("Improve: 方案建议跳过此步骤")

        # 场景3: 通用 → 重试原始目标
        else:
            self._jilu("Improve: 通用修复→重试")
            self.execute(xin)

        return self

    def control(self, xin):
        """Control: 检查点持久化 + 场景感知"""
        self.analyze_status()
        jiancha = {
            "buzhou": self.mingcheng,
            "zhuangtai": self.zhuangtai,
            "dabiao": self.dabiao,
            "haoshi": round(self.jieshu - self.kaishi, 2) if self.jieshu else 0,
            "shijian": datetime.now().isoformat(),
        }
        # 持久化到经络
        try:
            if xin.meridian and hasattr(xin.meridian, 'jilu_jianchadian'):
                xin.meridian.jilu_jianchadian(jiancha)
        except Exception: pass

        # 场景感知: 对比执行前后文件数变化
        try:
            root = Path(__file__).parent.parent
            current_py = len(list(root.rglob("*.py")))
            before_py = self._shiji_before.get("py_wenjian", current_py)
            if abs(current_py - before_py) > 5:
                self._jilu(f"Control: 场景变化 py:{before_py}→{current_py}")
                if xin.meridian and hasattr(xin.meridian, 'jilu_ganzhi'):
                    xin.meridian.jilu_ganzhi(
                        f"场景变化: py文件{before_py}→{current_py}", "zhong")
        except Exception: pass

        self._jilu(f"Control: 检查点已保存, 状态={self.zhuangtai}")
        return self

    def analyze_status(self):
        """判断步骤是否达标"""
        shiji = self._shiji_after
        if not shiji or not shiji.get("success"):
            self.dabiao = False
            return
        # 检查指标
        for k, v in self.zhibiao.items():
            target_val = v
            actual_val = shiji.get(k, None)
            if actual_val is None:
                continue
            try:
                if isinstance(target_val, str) and target_val.startswith("<"):
                    if actual_val >= float(target_val[1:]):
                        self.dabiao = False
                        self.piancha[k] = actual_val
                        return
            except Exception: pass
        self.dabiao = True

    def _jilu(self, msg):
        self.execution_rizhi.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


class RenWuJiHua:
    """任务计划: LLM拆解→DMAIC逐步执行→检查点→模板归档"""

    def __init__(self, xin, xuqiu: str):
        self.xin = xin
        self.xuqiu = xuqiu[:2000]
        self.buzhou_list = []
        self.zhuangtai = "pending"
        self._dangqian_buzhou = -1
        self.dabiao = False
        self.execution_rizhi = []
        self.jianchadian = []

    def fen_jie(self) -> list:
        """Define: LLM拆解大需求为步骤列表(每个步骤含目标+指标)"""
        if not self.xin.llm:
            self.buzhou_list = [BuZhou("单步执行", self.xuqiu)]
            return self.buzhou_list

        try:
            prompt = {
                "renwu": "fen_jie_bu_zhou",
                "xuqiu": self.xuqiu,
                "yaoqiu": (
                    "拆解为3-8个步骤。每个步骤格式: 步骤名|目标描述|成功指标。"
                    "示例: 生成清理脚本|生成可清理7天前日志的Python脚本|wenjian_shu<10\n"
                    "如果没有明确的多步骤, 返回单步骤。"
                )
            }
            jg = self.xin.llm.chat(
                [{"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}],
                wendu=0.2, zuidazifu=500)
            if jg:
                for line in jg.strip().split('\n'):
                    line = line.strip()
                    if '|' in line and not line.startswith('#'):
                        parts = line.split('|')
                        if len(parts) >= 2:
                            name = parts[0].strip()
                            target = parts[1].strip()
                            metrics = {}
                            if len(parts) >= 3:
                                for m in parts[2].split(','):
                                    if '<' in m or '>' in m:
                                        k, v = m.split('<') if '<' in m else m.split('>')
                                        metrics[k.strip()] = f"<{v.strip()}" if '<' in m else f">{v.strip()}"
                            self.buzhou_list.append(BuZhou(name, target, metrics))
        except Exception: pass

        if not self.buzhou_list:
            self.buzhou_list = [BuZhou("执行任务", self.xuqiu)]

        self._jilu(f"拆解完成: {len(self.buzhou_list)}个步骤")
        return self.buzhou_list

    def zhi_xing(self) -> dict:
        """DMAIC逐步执行: 每步Define→Measure→Execute→Analyze(五境)→Improve→Control"""
        if not self.buzhou_list:
            self.fen_jie()

        self.zhuangtai = "running"
        results = []

        for i, bz in enumerate(self.buzhou_list):
            self._dangqian_buzhou = i
            self._jilu(f"--- 步骤{i+1}/{len(self.buzhou_list)}: {bz.mingcheng} ---")

            # DMAIC
            bz.define(bz.mubiao, bz.zhibiao)
            bz.measure(self.xin)
            bz.execute(self.xin)

            fenxi = bz.analyze(self.xin)  # 嵌入五境
            bz.improve(self.xin, fenxi)
            bz.control(self.xin)

            # 记录检查点
            self.jianchadian.append({
                "buzhou": i, "mingcheng": bz.mingcheng,
                "zhuangtai": bz.zhuangtai, "dabiao": bz.dabiao,
            })

            results.append(f"[{'✓' if bz.dabiao else '✗'}] {bz.mingcheng}: {bz.zhuangtai}")

            # 致命失败→停止
            if bz.zhuangtai == "failed" and not bz.dabiao:
                self._jilu(f"步骤失败, 停止执行")
                self.zhuangtai = "failed"
                break

        # 全部达标
        if all(bz.dabiao for bz in self.buzhou_list):
            self.dabiao = True
            self.zhuangtai = "completed"
            self._guidang()

        return {"dabiao": self.dabiao, "zhuangtai": self.zhuangtai,
                "buzhou": len(self.buzhou_list), "jieguo": "\n".join(results)}

    def hui_fu(self) -> bool:
        """从最后检查点恢复执行"""
        if not self.jianchadian:
            return False
        last = self.jianchadian[-1]
        start_from = last["buzhou"] + 1 if last["zhuangtai"] == "completed" else last["buzhou"]
        self._jilu(f"恢复: 从步骤{start_from+1}继续")
        # 移除已完成的步骤
        self.buzhou_list = self.buzhou_list[start_from:]
        self.jianchadian = self.jianchadian[:start_from]
        return self.zhi_xing()["dabiao"]

    def _guidang(self):
        """本源境归档: 将完整计划存入记忆(下次相似需求直接复用)"""
        try:
            if self.xin.gan and hasattr(self.xin.gan, 'jilu'):
                self.xin.gan.jilu("流程模板", {
                    "xuqiu": self.xuqiu[:300],
                    "buzhou_shu": len(self.buzhou_list),
                    "buzhou_mulu": [bz.mingcheng for bz in self.buzhou_list],
                    "dabiao": self.dabiao,
                })
        except Exception: pass

    def _jilu(self, msg):
        self.execution_rizhi.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def qu_zhaiyao(self):
        return "\n".join(self.execution_rizhi)
