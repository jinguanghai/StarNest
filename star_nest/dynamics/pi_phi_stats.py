"""
π-φ统计总线 PiPhiTongJi V1.0 [星巢·统一度量]
收集所有模块的展开(π)/收敛(φ)度量，计算全局平衡状态

π(展开): 发现、生成、扫描、检索——向外探索
φ(收敛): 归档、执行、清除、优化——向内收敛

每个模块只需加一行统计:
  tjj.pi("gan", hit_count)   # 展开度量
  tjj.phi("gan", 1)          # 收敛度量

全局平衡: 0.8 < π_total / φ_total < 1.2 → 健康
          π/φ > 1.2 → 偏展开(过度发散)
          φ/π > 1.2 → 偏收敛(收缩过紧)
"""
import time
from datetime import datetime


class PiPhiTongJi:
    """π-φ统计总线: 收集→汇总→平衡判断→告警"""

    def __init__(self, meridian=None):
        self.meridian = meridian
        # {模块名: {"pi": 累计值, "phi": 累计值, "pi_n": 次数, "phi_n": 次数}}
        self._quan_ju = {}
        self._lishi = []  # 历史快照
        self._zuihou_kuai_zhao = time.time()

    # ==================== 统计接入 ====================

    def pi(self, module: str, value: float = 1.0):
        """记录一次π展开"""
        if module not in self._quan_ju:
            self._quan_ju[module] = {"pi": 0, "phi": 0, "pi_n": 0, "phi_n": 0}
        self._quan_ju[module]["pi"] += max(0, value)
        self._quan_ju[module]["pi_n"] += 1

    def phi(self, module: str, value: float = 1.0):
        """记录一次φ收敛"""
        if module not in self._quan_ju:
            self._quan_ju[module] = {"pi": 0, "phi": 0, "pi_n": 0, "phi_n": 0}
        self._quan_ju[module]["phi"] += max(0, value)
        self._quan_ju[module]["phi_n"] += 1

    # ==================== 查询 ====================

    def quan_ju_pi_phi(self) -> dict:
        """全局π-φ平衡状态"""
        total_pi = sum(v["pi"] for v in self._quan_ju.values())
        total_phi = sum(v["phi"] for v in self._quan_ju.values())
        ratio = round(total_pi / max(total_phi, 1), 2)

        if total_pi == 0 and total_phi == 0:
            ping_heng_du = "初始"
        elif ratio > 1.5:
            ping_heng_du = "过度展开"
        elif ratio > 1.2:
            ping_heng_du = "偏展开"
        elif ratio < 0.5:
            ping_heng_du = "过度收敛"
        elif ratio < 0.8:
            ping_heng_du = "偏收敛"
        else:
            ping_heng_du = "健康"

        return {
            "pi_total": round(total_pi, 1),
            "phi_total": round(total_phi, 1),
            "pi_phi_ratio": ratio,
            "ping_heng_du": ping_heng_du,
            "mo_kuai_shu": len(self._quan_ju),
        }

    def mo_kuai_xiang_qing(self) -> dict:
        """每个模块的π-φ详情"""
        return {
            mod: {
                "pi": round(v["pi"], 1),
                "phi": round(v["phi"], 1),
                "pi_n": v["pi_n"],
                "phi_n": v["phi_n"],
                "ratio": round(v["pi"] / max(v["phi"], 1), 2),
            }
            for mod, v in self._quan_ju.items()
        }

    def kuai_zhao(self):
        """保存当前快照，计算趋势"""
        state = self.quan_ju_pi_phi()
        state["shijian"] = datetime.now().isoformat()
        self._lishi.append(state)
        self._zuihou_kuai_zhao = time.time()
        if len(self._lishi) > 50:
            self._lishi = self._lishi[-50:]

    def qu_qu_shi(self) -> dict:
        """π-φ趋势: 对比最近两次快照"""
        if len(self._lishi) < 2:
            return {"qu_shi": "数据不足", "pian_cha": 0}
        prev = self._lishi[-2]
        curr = self._lishi[-1]
        drift = round(curr["pi_phi_ratio"] - prev["pi_phi_ratio"], 2)
        if drift > 0.3:
            return {"qu_shi": "向展开偏移", "pian_cha": drift}
        elif drift < -0.3:
            return {"qu_shi": "向收敛偏移", "pian_cha": drift}
        return {"qu_shi": "稳定", "pian_cha": drift}

    def ping_heng_jian_cha(self):
        """平衡检查: 过度偏斜→经络告警"""
        state = self.quan_ju_pi_phi()
        self.kuai_zhao()
        if state["ping_heng_du"] in ("过度展开", "过度收敛"):
            if self.meridian:
                try:
                    self.meridian.jilu_ganzhi(
                        f"π-φ失衡: {state['ping_heng_du']} (ratio={state['pi_phi_ratio']})",
                        "zhong")
                except Exception: pass
        return state
