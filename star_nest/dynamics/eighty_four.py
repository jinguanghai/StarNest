"""
八势策略算子 (Eight Strategies) - 主动干预系统
V1.0 零依赖版

基于太极万象演化元系统5.0的八势策略理论：

八势对应八卦，每个势对应一个动力学算子：

| 八势 | 卦象 | 动力学算子 | 适用条件 |
|------|------|-----------|---------|
| 识势 | ☶ 艮 | 提高观测精度 | 边界信息模糊 |
| 造势 | ☳ 震 | 注入π型随机扰动 | 资源匮乏、动力不足 |
| 运势 | ☱ 兑 | 调整子模块耦合权重 | 内部流通不畅 |
| 控势 | ☲ 离 | 负反馈控制 | 局部过热 |
| 借势 | ☵ 坎 | 引入外部共振频率 | 功能抑制 |
| 乘势 | ☰ 乾 | 放大增益 | 时机成熟 |
| 破势 | ☴ 巽 | 高振幅脉冲 | 结构僵化、壅堵 |
| 定势 | ☷ 坤 | 增大阻尼 | 基础不稳、需沉淀 |

纯标准库实现，零外部依赖。
"""

import random
import math
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class EightStrategies:
    """八势策略算子——主动干预系统"""

    def __init__(self):
        # 八势定义
        self.strategies = {
            "shishi": {"name": "识势", "gua": "艮", "symbol": "☶", "description": "提高观测精度"},
            "zaoshi": {"name": "造势", "gua": "震", "symbol": "☳", "description": "注入创新扰动"},
            "yunshi": {"name": "运势", "gua": "兑", "symbol": "☱", "description": "调整内部耦合"},
            "kongshi": {"name": "控势", "gua": "离", "symbol": "☲", "description": "负反馈控制"},
            "jieshi": {"name": "借势", "gua": "坎", "symbol": "☵", "description": "引入外部共振"},
            "chengshi": {"name": "乘势", "gua": "乾", "symbol": "☰", "description": "放大增益"},
            "poshi": {"name": "破势", "gua": "巽", "symbol": "☴", "description": "高振幅脉冲"},
            "dingshi": {"name": "定势", "gua": "坤", "symbol": "☷", "description": "增大阻尼"}
        }
        
        # 策略执行历史
        self.execution_history: List[Dict[str, str]] = []
        self.max_history_length = 50

    def identify_strategy(self, omega: List[float]) -> List[str]:
        """
        根据当前八极状态识别最优策略
        
        Args:
            omega: 八极状态向量 [阳, 阴, 表, 里, 寒, 热, 虚, 实]
        
        Returns:
            推荐策略列表（按优先级排序）
        """
        strategies = []
        yang, yin, biao, li, han, re, xu, shi = omega
        
        # 识势：边界信息模糊（表维度绝对值小）
        if abs(biao) < 0.2:
            strategies.append(("shishi", "边界信息模糊，需要提高观测精度"))
        
        # 造势：资源匮乏（虚维度负）或动力不足（阳维度低）
        if xu < -0.4 or yang < -0.3:
            strategies.append(("zaoshi", "资源匮乏或动力不足，需要注入创新能量"))
        
        # 运势：内部流通不畅（里维度波动大或实维度高）
        if shi > 0.4:
            strategies.append(("yunshi", "内部壅堵，需要调整耦合权重"))
        
        # 控势：局部过热（热维度高）
        if re > 0.6:
            strategies.append(("kongshi", "系统过热，需要负反馈降温"))
        
        # 借势：功能抑制（寒维度高）
        if han > 0.5:
            strategies.append(("jieshi", "功能受抑制，需要引入外部共振"))
        
        # 乘势：时机成熟（阳维度高且趋势向上）
        if yang > 0.5 and yin < 0.3:
            strategies.append(("chengshi", "时机成熟，可以乘势而上"))
        
        # 破势：结构僵化（实维度极高）
        if shi > 0.7:
            strategies.append(("poshi", "结构僵化严重，需要突破性干预"))
        
        # 定势：基础不稳（阴维度低）
        if yin < -0.4:
            strategies.append(("dingshi", "基础不稳，需要巩固稳定"))
        
        return strategies

    def execute(self, strategy_name: str, omega: List[float]) -> List[float]:
        """
        执行指定策略，返回调整后的状态
        
        Args:
            strategy_name: 策略名称
            omega: 当前八极状态向量
        
        Returns:
            调整后的八极状态向量
        """
        new_omega = list(omega)
        
        if strategy_name == "shishi":
            # 识势·艮：提高观测精度，增强表维度
            new_omega[2] = min(1.0, new_omega[2] * 1.3 + 0.1)
            
        elif strategy_name == "zaoshi":
            # 造势·震：注入π型随机扰动
            perturbation = random.uniform(-0.2, 0.2)
            new_omega[6] += perturbation  # 虚维度扰动
            new_omega[0] = min(1.0, new_omega[0] + 0.1)  # 增加阳驱动力
            
        elif strategy_name == "yunshi":
            # 运势·兑：调整内部耦合，降低实维度
            new_omega[7] = max(-1.0, new_omega[7] * 0.7)
            new_omega[3] = min(1.0, new_omega[3] * 1.1)  # 增强里维度
            
        elif strategy_name == "kongshi":
            # 控势·离：负反馈降温，降低热维度
            new_omega[5] = max(-1.0, new_omega[5] * 0.6)
            
        elif strategy_name == "jieshi":
            # 借势·坎：引入外部共振，降低寒维度
            new_omega[4] = max(-1.0, new_omega[4] * 0.7)
            new_omega[0] = min(1.0, new_omega[0] + 0.05)  # 小幅提升阳
            
        elif strategy_name == "chengshi":
            # 乘势·乾：放大增益
            new_omega[0] = min(1.0, new_omega[0] * 1.2)
            new_omega[2] = min(1.0, new_omega[2] * 1.1)  # 增强边界扩展
            
        elif strategy_name == "poshi":
            # 破势·巽：高振幅脉冲，清空壅堵
            new_omega[7] = 0.0  # 清空实维度
            # 小幅扰动其他维度
            for i in range(8):
                if i != 7:
                    new_omega[i] += random.uniform(-0.1, 0.1)
            
        elif strategy_name == "dingshi":
            # 定势·坤：增大阻尼，增强稳定性
            new_omega[1] = min(1.0, new_omega[1] * 1.2)
            new_omega[0] = max(-1.0, new_omega[0] * 0.9)  # 适度降低阳
            
        # 边界约束
        for i in range(8):
            new_omega[i] = max(-1.0, min(1.0, new_omega[i]))
        
        # 记录执行历史
        self._record_execution(strategy_name)
        
        return new_omega

    def execute_multiple(self, strategies: List[str], omega: List[float]) -> Tuple[List[float], List[str]]:
        """
        执行多个策略（按顺序）
        
        Args:
            strategies: 策略名称列表
            omega: 当前八极状态向量
        
        Returns:
            (调整后的状态, 执行的策略列表)
        """
        new_omega = list(omega)
        executed = []
        
        for strategy_name in strategies:
            if strategy_name in self.strategies:
                new_omega = self.execute(strategy_name, new_omega)
                executed.append(strategy_name)
        
        return new_omega, executed

    def recommend_and_execute(self, omega: List[float], max_strategies: int = 2) -> Tuple[List[float], List[str]]:
        """
        自动识别并执行最优策略
        
        Args:
            omega: 当前八极状态向量
            max_strategies: 最大执行策略数
            
        Returns:
            (调整后的状态, 执行的策略列表)
        """
        # 识别最优策略
        identified = self.identify_strategy(omega)
        
        if not identified:
            return omega, []
        
        # 取优先级最高的策略
        strategy_names = [s[0] for s in identified[:max_strategies]]
        
        # 执行策略
        return self.execute_multiple(strategy_names, omega)

    def _record_execution(self, strategy_name: str):
        """记录策略执行历史"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy_name,
            "name": self.strategies[strategy_name]["name"],
            "gua": self.strategies[strategy_name]["gua"],
            "symbol": self.strategies[strategy_name]["symbol"]
        }
        self.execution_history.append(record)
        if len(self.execution_history) > self.max_history_length:
            self.execution_history.pop(0)

    def get_strategy_info(self, strategy_name: str) -> Optional[Dict[str, str]]:
        """获取策略详细信息"""
        return self.strategies.get(strategy_name)

    def list_strategies(self) -> List[Dict[str, str]]:
        """列出所有策略"""
        return [{"key": k, **v} for k, v in self.strategies.items()]


class StrategyScheduler:
    """策略调度器——根据系统状态自动调度策略"""

    def __init__(self, eight_pole_dynamics, pi_phi_controller):
        self.eight_pole = eight_pole_dynamics
        self.pi_phi = pi_phi_controller
        self.strategies = EightStrategies()
        
    def schedule(self) -> Dict[str, str]:
        """
        根据当前系统状态调度策略
        
        Returns:
            调度结果字典
        """
        # 获取当前状态
        pole_state = self.eight_pole.get_state()
        pi_phi_state = self.pi_phi.get_state()
        
        omega = [
            pole_state["yang"], pole_state["yin"],
            pole_state["biao"], pole_state["li"],
            pole_state["han"], pole_state["re"],
            pole_state["xu"], pole_state["shi"]
        ]
        
        # 根据π-φ状态调整策略选择
        pi_energy = pi_phi_state["pi_energy"]
        phi_energy = pi_phi_state["phi_energy"]
        
        # 如果创新能量不足，优先造势
        if pi_energy < 0.3:
            new_omega, executed = self.strategies.execute_multiple(["zaoshi"], omega)
            self.eight_pole.set_state({
                "yang": new_omega[0], "yin": new_omega[1],
                "biao": new_omega[2], "li": new_omega[3],
                "han": new_omega[4], "re": new_omega[5],
                "xu": new_omega[6], "shi": new_omega[7]
            })
            return {"status": "executed", "strategies": executed, "reason": "创新能量不足，执行造势策略"}
        
        # 如果稳定能量不足，优先定势
        if phi_energy < 0.3:
            new_omega, executed = self.strategies.execute_multiple(["dingshi"], omega)
            self.eight_pole.set_state({
                "yang": new_omega[0], "yin": new_omega[1],
                "biao": new_omega[2], "li": new_omega[3],
                "han": new_omega[4], "re": new_omega[5],
                "xu": new_omega[6], "shi": new_omega[7]
            })
            return {"status": "executed", "strategies": executed, "reason": "稳定能量不足，执行定势策略"}
        
        # 否则自动识别并执行最优策略
        new_omega, executed = self.strategies.recommend_and_execute(omega)
        
        if executed:
            self.eight_pole.set_state({
                "yang": new_omega[0], "yin": new_omega[1],
                "biao": new_omega[2], "li": new_omega[3],
                "han": new_omega[4], "re": new_omega[5],
                "xu": new_omega[6], "shi": new_omega[7]
            })
            return {"status": "executed", "strategies": executed, "reason": "自动识别并执行最优策略"}
        else:
            return {"status": "idle", "strategies": [], "reason": "系统状态良好，无需干预"}


# 单例模式
_eight_strategies = None
_strategy_scheduler = None
_input_router = None


class InputRouter:
    """
    输入端八势路由 V1.0 — 六势态→八势策略→管道分发
    
    不替代原有的EightStrategies(用于系统自身调优),
    而是新建一条面向输入处理的八势策略路由.
    """
    def __init__(self):
        self.strategies = get_eight_strategies()
        self._pipei = {
            # 六势态 → (主策略, 管道类型, 是否需要确认, 是否安全审查)
            "太阳": ("定势", "execution", True,  False),   # 执行·需确认
            "阳明": ("控势", "execution", False, False),   # 执行·直接
            "少阳": ("运势", "duihua",  False, False),   # 对话
            "太阴": ("识势", "touwei",  False, False),   # 投喂消化
            "少阴": ("借势", "shencha", True,  True),    # 审查·沙箱
            "厥阴": ("破势", "gedou",   False, True),    # 隔离·杀毒
        }

    def luxian(self, zhenduan: dict) -> dict:
        """
        输入: 内容八极诊断结果 {baji, shizhi, zhan_du, shou_du, an_quan_du}
        输出: 路由决策 {celve, guandao, xuyao_queren, xuyao_shencha, shuoming}
        """
        shizhi = zhenduan.get("shizhi", "少阳")
        anquan = zhenduan.get("an_quan_du", 0.5)
        zhan = zhenduan.get("zhan_du", 0.5)
        shou = zhenduan.get("shou_du", 0.5)

        celve, guandao, xuyao_queren, xuyao_shencha = self._pipei.get(
            shizhi, ("运势", "duihua", False, False))

        # 安全度修正: 安全度<0.3时强制升级为安全审查
        if anquan < 0.3 and not xuyao_shencha:
            xuyao_shencha = True
            guandao = "shencha"

        # 展开度修正: 高展开度→即使少阳也可能需要执行能力
        if zhan > 0.6 and shou < 0.3 and guandao == "duihua":
            guandao = "hunhe"  # 混合: 对话+执行

        # 收敛度修正: 高收敛度且低安全→可能是伪装的知识投喂
        if shou > 0.7 and anquan < 0.4 and guandao == "touwei":
            xuyao_shencha = True

        shuoming = self._shengcheng_shuoming(shizhi, celve, guandao, xuyao_queren, xuyao_shencha)
        return {
            "celve": celve, "guandao": guandao,
            "xuyao_queren": xuyao_queren, "xuyao_shencha": xuyao_shencha,
            "shuoming": shuoming
        }

    def _shengcheng_shuoming(self, shizhi, celve, guandao, queren, shencha):
        parts = [f"六势:{shizhi}", f"八势:{celve}", f"管道:{guandao}"]
        if queren: parts.append("需确认")
        if shencha: parts.append("安全审查")
        return " | ".join(parts)


def get_input_router() -> InputRouter:
    global _input_router
    if _input_router is None:
        _input_router = InputRouter()
    return _input_router


def get_eight_strategies() -> EightStrategies:
    """获取八势策略算子单例"""
    global _eight_strategies
    if _eight_strategies is None:
        _eight_strategies = EightStrategies()
    return _eight_strategies

def get_strategy_scheduler(eight_pole_dynamics=None, pi_phi_controller=None):
    """获取策略调度器单例"""
    global _strategy_scheduler
    if _strategy_scheduler is None:
        from star_nest.dynamics.pi_phi_cycle import get_pi_phi_controller
        from star_nest.dynamics.eight_extremes import get_eight_pole_dynamics
        
        if eight_pole_dynamics is None:
            eight_pole_dynamics = get_eight_pole_dynamics()
        if pi_phi_controller is None:
            pi_phi_controller = get_pi_phi_controller()
        
        _strategy_scheduler = StrategyScheduler(eight_pole_dynamics, pi_phi_controller)
    return _strategy_scheduler


if __name__ == "__main__":
    # 测试代码
    import sys
    # 设置UTF-8输出
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=== 八势策略算子测试 ===")
    
    strategies = EightStrategies()
    
    # 测试策略识别
    print("\n1. 策略识别测试")
    test_state = [0.1, -0.5, 0.1, 0.3, 0.6, 0.1, -0.5, 0.3]  # 边界模糊、资源匮乏、寒
    identified = strategies.identify_strategy(test_state)
    print(f"测试状态: {test_state}")
    print(f"识别的策略:")
    for strat, reason in identified:
        info = strategies.get_strategy_info(strat)
        print(f"  - {info['name']} ({info['gua']}): {reason}")
    
    # 测试策略执行
    print("\n2. 策略执行测试")
    initial_state = [0.3, -0.2, 0.1, 0.2, 0.4, 0.5, -0.3, 0.2]
    print(f"初始状态: {initial_state}")
    
    # 执行控势策略（降温）
    result = strategies.execute("kongshi", initial_state)
    print(f"执行控势后: {[round(v, 3) for v in result]}")
    
    # 执行造势策略（注入创新）
    result = strategies.execute("zaoshi", result)
    print(f"执行造势后: {[round(v, 3) for v in result]}")
    
    # 测试推荐执行
    print("\n3. 推荐执行测试")
    test_state2 = [-0.2, -0.3, 0.1, 0.1, 0.3, 0.7, -0.2, 0.5]
    result, executed = strategies.recommend_and_execute(test_state2)
    print(f"测试状态: {test_state2}")
    print(f"执行的策略: {[strategies.get_strategy_info(s)['name'] for s in executed]}")
    print(f"执行后状态: {[round(v, 3) for v in result]}")
    
    # 列出所有策略
    print("\n4. 所有策略列表")
    all_strategies = strategies.list_strategies()
    for s in all_strategies:
        print(f"  {s['name']} ({s['gua']}): {s['description']}")
    
    print("\n测试完成！")
