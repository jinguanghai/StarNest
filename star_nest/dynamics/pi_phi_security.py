"""
π-φ安全引擎 PiPhiAnQuan V1.0 [星巢·可计算的第一性原理]
将π-φ折叠思维从隐喻升级为可执行的节律引擎

π(展开): 广扫描——广度优先、发现一切
φ(收敛): 精准杀——深度优先、确认清除

可计算度量:
  pi_shi_neng: 扫描覆盖率 (实际扫描项/应扫描项)
  phi_shou_lian: 清除准确率 (有效清除/总清除)
  bi_huan: 闭环比例 (已归档/已发现)

七律节律驱动: 不同周期→不同π/φ比
  短周期(7s/49s): π小展开 → 快速扫描 → φ轻收敛
  中周期(343s): π中展开 → 全量扫描 → φ部分执行
  长周期(2401s+): π大展开 → LLM深度分析 → φ全量清理+学习
"""
import time
from datetime import datetime
from pathlib import Path


class PiPhiAnQuan:
    """π-φ安全引擎: 七律驱动的扫描节律"""

    def __init__(self, xin, zhaoyaojing, anquansanti=None):
        self.xin = xin
        self.zyj = zhaoyaojing      # 照妖镜(π展开工具)
        self.aq = anquansanti        # 三体安全(φ收敛工具)

        # π-φ 状态
        self.pi_shi_neng = 0.5       # 当前π势能
        self.phi_shou_lian = 0.5     # 当前φ收敛度
        self._zuihou_pi = 0          # 上次π展开时间
        self._zuihou_phi = 0         # 上次φ收敛时间
        self._bi_huan_shu = 0        # 闭环计数
        self._execution_rizhi = []

        # 七律节律映射
        self.JIE_LV = {
            1:    {"pi": 0.1, "phi": 0.0, "ming": "心跳"},
            7:    {"pi": 0.2, "phi": 0.0, "ming": "微周"},
            49:   {"pi": 0.3, "phi": 0.2, "ming": "小周"},
            343:  {"pi": 0.5, "phi": 0.4, "ming": "中周"},
            2401: {"pi": 0.7, "phi": 0.7, "ming": "大周"},
            16807: {"pi": 0.9, "phi": 0.8, "ming": "周天"},
            117649: {"pi": 1.0, "phi": 1.0, "ming": "纪元"},
        }

    # ==================== 周期驱动 ====================

    def zhou_qi(self, zhou_qi_miao: int) -> dict:
        """一个完整的π→φ→闭环安全周期"""
        jl = self.JIE_LV.get(zhou_qi_miao, self.JIE_LV[343])
        self.pi_shi_neng = jl["pi"]
        self.phi_shou_lian = jl["phi"]

        self._jilu(f"[π-φ] {jl['ming']}({zhou_qi_miao}s): π势能={self.pi_shi_neng} φ收敛={self.phi_shou_lian}")

        # 同步到全局状态 S
        try:
            from star_nest.dynamics.global_state import get_global_state
            S = get_global_state(self.xin)
            S.pi_neng = jl["pi"]
            S.phi_neng = jl["phi"]
            S.jielv = jl["ming"]
            S.save()
        except Exception: pass

        # === π 展开: 发现 ===
        scan = self._pi_zhang_kai(zhou_qi_miao)
        self._zuihou_pi = time.time()

        # === φ 收敛: 清除 ===
        clean = self._phi_shou_lian(scan, zhou_qi_miao)
        self._zuihou_phi = time.time()

        # === 闭环 ===
        self._bi_huan_shu += 1
        self._jian_cha_bi_huan(scan, clean)

        return {"pi": {"fa_xian": len(scan) if isinstance(scan, list) else scan.get("fa_xian", 0)},
                "phi": {"qing_chu": clean.get("qing_chu_shu", 0) if isinstance(clean, dict) else 0},
                "jie_lv": jl["ming"], "bi_huan": self._bi_huan_shu}

    def _pi_zhang_kai(self, zhou_qi: int) -> list:
        """π展开: 不同周期→不同扫描深度"""
        if zhou_qi <= 7:
            # 微周期: 仅进程快照
            return self.zyj._sao_ke_yi_jin_cheng() if hasattr(self.zyj, '_sao_ke_yi_jin_cheng') else []

        if zhou_qi <= 49:
            # 小周期: 进程 + 关键目录文件扫描
            threats = self.zyj._sao_ke_yi_jin_cheng() if hasattr(self.zyj, '_sao_ke_yi_jin_cheng') else []
            # 仅扫描用户家目录(快速)
            home = Path.home()
            threats.extend(self.zyj._sao_ke_yi_wen_jian(str(home)))
            return threats[:20]  # 限制数量, 控制展开范围

        if zhou_qi <= 343:
            # 中周期: 全量五维扫描
            return self.zyj.zhao_yao(mulu="C:\\") if hasattr(self.zyj, 'zhao_yao') else []

        # 大周期以上: 全量扫描 + LLM深度分析
        threats = self.zyj.zhao_yao(mulu="C:\\") if hasattr(self.zyj, 'zhao_yao') else []
        if self.xin.llm and threats and zhou_qi >= 2401:
            self._pi_shen_du_fen_xi(threats)
        return threats

    def _pi_shen_du_fen_xi(self, threats: list):
        """π深度分析: LLM复盘漏检和误报(写入经络, 不打印)"""
        if not self.xin.llm or not threats: return
        try:
            from star_nest.protocols.cognition_package import RenzhiBao
            bao = RenzhiBao("反境")
            bao.shu_ju(wei_xie_shu=len(threats),
                       lei_xing=[t.get("leixing","") for t in threats[:10]],
                       yao_qiu="复盘: 这些威胁分类是否合理? 有无漏检类型? 扫描覆盖是否充分?")
            jg = self.xin.llm.chat([{"role":"user","content":bao.to_json()}], wendu=0.2, zuidazifu=300)
            if jg and self.xin.meridian:
                self.xin.meridian.jilu_fansi(f"[π深度复盘] {str(jg)[:300]}")
        except Exception: pass

    # ==================== φ 收敛 ====================

    def _phi_shou_lian(self, threats: list, zhou_qi: int) -> dict:
        """φ收敛: 不同周期→不同清除深度"""
        if not threats:
            return {"qing_chu_shu": 0, "shi_bai_shu": 0, "xiang_qing": []}

        if zhou_qi <= 49:
            # 小周期: 仅自动隔离明显威胁(高严重度 + 有明确路径)
            high_threats = [t for t in threats if t.get("yanzhongdu") == "gao" and t.get("lujing")]
            if high_threats:
                return self.zyj.wu_jing_sha_du(high_threats[:5]) if hasattr(self.zyj, 'wu_jing_sha_du') else self._qing_du_simple(high_threats[:5])
            return {"qing_chu_shu": 0, "shi_bai_shu": 0, "xiang_qing": []}

        # 中周期以上: 五境完整杀毒
        if hasattr(self.zyj, 'wu_jing_sha_du'):
            return self.zyj.wu_jing_sha_du(threats)

        return self._qing_du_simple(threats)

    def _qing_du_simple(self, threats: list) -> dict:
        """简易清除(无LLM时)"""
        cleared = 0
        for t in threats:
            if t.get("lujing") and hasattr(self.zyj, '_ge_li_wen_jian'):
                try:
                    self.zyj._ge_li_wen_jian(t["lujing"])
                    cleared += 1
                except Exception: pass
        return {"qing_chu_shu": cleared, "shi_bai_shu": len(threats) - cleared, "xiang_qing": []}

    # ==================== 闭环检查 ====================

    def _jian_cha_bi_huan(self, scan: list, clean: dict):
        """闭环: π发现的威胁是否已被φ清除?"""
        total = len(scan) if isinstance(scan, list) else 0
        cleared = clean.get("qing_chu_shu", 0) if isinstance(clean, dict) else 0
        if total > 0 and cleared < total * 0.5:
            # 收敛不足: 清除率低于50%
            self.phi_shou_lian = max(0.3, self.phi_shou_lian - 0.1)
            if self.aq and hasattr(self.xin, 'meridian') and self.xin.meridian:
                try:
                    self.xin.meridian.jilu_ganzhi(
                        f"φ收敛不足: {cleared}/{total} 威胁未清除", "gao")
                except Exception: pass
            self._jilu(f"  [闭环] 收敛不足 φ={self.phi_shou_lian:.1f} ({cleared}/{total})")
        elif total > 0 and cleared >= total * 0.5:
            # 健康闭环
            self.phi_shou_lian = min(1.0, self.phi_shou_lian + 0.05)
            self._jilu(f"  [闭环] 健康 φ={self.phi_shou_lian:.1f} ({cleared}/{total})")

    # ==================== 状态查询 ====================

    def qu_zhuang_tai(self) -> dict:
        return {
            "pi": round(self.pi_shi_neng, 2),
            "phi": round(self.phi_shou_lian, 2),
            "bi_huan": self._bi_huan_shu,
            "zuihou_pi": self._zuihou_pi,
            "zuihou_phi": self._zuihou_phi,
        }

    def _jilu(self, msg):
        self._execution_rizhi.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
        # 周期状态写经络静默, 不打印干扰用户
        if self.xin and self.xin.meridian:
            try: self.xin.meridian.jilu_fansi(f"[π-φ] {msg[:200]}")
            except Exception: pass

    def qu_rizhi(self):
        return self._execution_rizhi[-20:]
