"""
π-φ循环引擎 (Pi-Phi Cycle Engine) - 认知系统的统一动力核心
V1.0 零依赖版

基于太极万象演化元系统5.0的核心动力学原理：
- 折叠(π)：系统的展开、驱动、创新、消耗能量的过程
- 展开(φ)：系统的收敛、稳定、保存、结构化的过程

公理体系：
1. 守恒公理：I_π + I_φ = I_total = constant
2. 最小势能公理：系统自发向认知势能更低的状态演化
3. 熵界公理：认知熵存在健康区间 [H_low, H_high]

纯标准库实现，零外部依赖。
"""

import random
from datetime import datetime
from typing import Dict, List, Tuple


class PiPhiDynamics:
    """π-φ循环引擎——认知系统的统一动力核心"""

    def __init__(self):
        # 总认知信息量守恒（归一化到[0,1]区间）
        self.total_information = 1.0
        
        # π能量：创新、展开、驱动、消耗（初始值0.5，保持平衡）
        self.pi_energy = 0.5
        # φ能量：收敛、稳定、保存、结构化
        self.phi_energy = 0.5
        
        # 认知熵：衡量系统混乱程度 [0,1]
        self.entropy = 0.5
        # 熵界健康区间
        self.entropy_bounds = (0.2, 0.8)
        
        # 势能函数值
        self.potential = 0.5
        
        # 演化历史记录（用于趋势分析）
        self.history: List[Dict[str, float]] = []
        self.max_history_length = 100
        
        # 状态标志
        self.is_healthy = True
        self.last_health_check = datetime.now()

    def fold(self, delta: float = 0.1) -> Dict[str, float]:
        """
        π折叠：消耗稳定能量，释放创新能量
        驱动系统向更具创新性的状态演化
        
        Args:
            delta: 能量转移量，范围[0,1]
        
        Returns:
            状态变更字典
        """
        delta = max(0.0, min(1.0, delta))  # 约束delta范围
        
        # 执行能量转移：从φ到π
        transfer = min(delta, self.phi_energy)
        self.pi_energy = min(1.0, self.pi_energy + transfer)
        self.phi_energy = max(0.0, self.phi_energy - transfer)
        
        # 更新熵和势能
        self._update_entropy()
        self._update_potential()
        
        # 记录历史
        self._record_history("fold")
        
        return self.get_state()

    def unfold(self, delta: float = 0.1) -> Dict[str, float]:
        """
        φ展开：消耗创新能量，固化为结构
        驱动系统向更稳定的状态演化
        
        Args:
            delta: 能量转移量，范围[0,1]
        
        Returns:
            状态变更字典
        """
        delta = max(0.0, min(1.0, delta))
        
        # 执行能量转移：从π到φ
        transfer = min(delta, self.pi_energy)
        self.phi_energy = min(1.0, self.phi_energy + transfer)
        self.pi_energy = max(0.0, self.pi_energy - transfer)
        
        # 更新熵和势能
        self._update_entropy()
        self._update_potential()
        
        # 记录历史
        self._record_history("unfold")
        
        return self.get_state()

    def _update_entropy(self):
        """根据π-φ平衡更新认知熵"""
        # 熵 = π与φ的不平衡程度
        self.entropy = abs(self.pi_energy - self.phi_energy)
        
        # 熵界约束：自动调节到健康区间
        if self.entropy < self.entropy_bounds[0]:
            # 熵过低：系统过于有序，需要注入扰动
            self.fold(0.03)
        elif self.entropy > self.entropy_bounds[1]:
            # 熵过高：系统过于混乱，需要收敛稳定
            self.unfold(0.03)

    def _update_potential(self):
        """计算认知势能 V(π, φ)"""
        # 势能 = |π - φ|² + π² + φ² - π·φ
        # 当π=φ=0.5时势能最低
        diff = self.pi_energy - self.phi_energy
        self.potential = diff**2 + self.pi_energy**2 + self.phi_energy**2 - self.pi_energy * self.phi_energy
        # 归一化到[0,1]
        self.potential = min(1.0, max(0.0, self.potential))

    def _record_history(self, action: str):
        """记录演化历史"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "pi_energy": self.pi_energy,
            "phi_energy": self.phi_energy,
            "entropy": self.entropy,
            "potential": self.potential
        }
        self.history.append(record)
        if len(self.history) > self.max_history_length:
            self.history.pop(0)

    def get_state(self) -> Dict[str, float]:
        return {
            "pi_energy": self.pi_energy,
            "phi_energy": self.phi_energy,
            "entropy": self.entropy,
            "potential": self.potential,
            "total_information": self.total_information,
            "is_healthy": self.is_healthy
        }

    def auto_evolve(self, steps: int = 1) -> List[Dict[str, float]]:
        trajectory = []
        for _ in range(steps):
            if random.random() < 0.5:
                self.fold(0.05)
            else:
                self.unfold(0.05)
            trajectory.append(self.get_state())
        return trajectory

    def health_check(self) -> Dict[str, object]:
        self.last_health_check = datetime.now()
        self.is_healthy = self.entropy_bounds[0] <= self.entropy <= self.entropy_bounds[1]
        return {"is_healthy": self.is_healthy, "entropy": self.entropy, "potential": self.potential}

    def reset(self):
        self.pi_energy = 0.5
        self.phi_energy = 0.5
        self.entropy = 0.5
        self.potential = 0.5
        self.is_healthy = True
        self.history = []

    def get_trend(self) -> Dict[str, float]:
        if len(self.history) < 2:
            return {"pi_trend": 0.0, "phi_trend": 0.0, "entropy_trend": 0.0}
        prev = self.history[-2]
        curr = self.history[-1]
        return {
            "pi_trend": curr["pi_energy"] - prev["pi_energy"],
            "phi_trend": curr["phi_energy"] - prev["phi_energy"],
            "entropy_trend": curr["entropy"] - prev["entropy"]
        }


class PiPhiController:
    def __init__(self):
        self.engine = PiPhiDynamics()

    def get_state(self) -> Dict[str, float]:
        return self.engine.get_state()

    def adjust(self, target_state: str = "balance") -> Dict[str, float]:
        state = self.engine.get_state()
        if target_state == "balance":
            if state["pi_energy"] > 0.6:
                return self.engine.unfold(0.2)
            elif state["phi_energy"] > 0.6:
                return self.engine.fold(0.2)
        elif target_state == "stable":
            return self.engine.unfold(0.2)
        elif target_state == "explore":
            if random.random() > 0.5:
                return self.engine.fold(0.1)
            else:
                return self.engine.unfold(0.1)
        else:
            return state

    def get_diagnosis(self) -> Dict[str, str]:
        """获取当前状态诊断"""
        state = self.engine.get_state()
        trend = self.engine.get_trend()
        
        diagnosis = []
        
        if state["entropy"] < self.engine.entropy_bounds[0]:
            diagnosis.append("熵值过低：系统过于僵化，需要注入创新")
        elif state["entropy"] > self.engine.entropy_bounds[1]:
            diagnosis.append("熵值过高：系统过于混乱，需要收敛稳定")
        
        if state["pi_energy"] > 0.7:
            diagnosis.append("创新能量充足：适合进行探索和创新")
        elif state["pi_energy"] < 0.3:
            diagnosis.append("创新能量不足：需要激发创造力")
        
        if state["phi_energy"] > 0.7:
            diagnosis.append("稳定能量充足：系统结构良好")
        elif state["phi_energy"] < 0.3:
            diagnosis.append("稳定能量不足：需要巩固成果")
        
        if trend["pi_trend"] > 0.02:
            diagnosis.append("趋势：创新能量正在上升")
        elif trend["pi_trend"] < -0.02:
            diagnosis.append("趋势：创新能量正在下降")
        
        if not state["is_healthy"]:
            diagnosis.append("警告：系统健康检查未通过")
        
        return {"diagnosis": diagnosis, "state": state, "trend": trend}


# 单例模式
_pi_phi_controller = None

def get_pi_phi_controller() -> PiPhiController:
    """获取π-φ控制器单例"""
    global _pi_phi_controller
    if _pi_phi_controller is None:
        _pi_phi_controller = PiPhiController()
    return _pi_phi_controller


if __name__ == "__main__":
    # 测试代码
    print("=== π-φ循环引擎测试 ===")
    
    engine = PiPhiDynamics()
    print("初始状态:", engine.get_state())
    
    # 测试折叠操作
    print("\n执行折叠（增加创新能量）...")
    engine.fold(0.2)
    print("折叠后状态:", engine.get_state())
    
    # 测试展开操作
    print("\n执行展开（增加稳定能量）...")
    engine.unfold(0.3)
    print("展开后状态:", engine.get_state())
    
    # 测试自动演化
    print("\n执行10步自动演化...")
    trajectory = engine.auto_evolve(10)
    for i, step in enumerate(trajectory):
        print(f"  步{i+1}: π={step['pi_energy']:.3f}, φ={step['phi_energy']:.3f}, 熵={step['entropy']:.3f}")
    
    # 测试健康检查
    print("\n健康检查:", engine.health_check())
    
    # 测试控制器
    print("\n=== 控制器测试 ===")
    controller = PiPhiController()
    print("诊断结果:", controller.get_diagnosis())
    
    print("\n测试完成！")
