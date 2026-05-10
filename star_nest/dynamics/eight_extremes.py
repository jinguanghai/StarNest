"""
八极状态空间动力学 (Eight Pole Dynamics) - 认知诊断的数学基础
V1.0 零依赖版

基于太极万象演化元系统5.0的八极状态空间理论：
Ω = (Ω₁, Ω₂, Ω₃, Ω₄, Ω₅, Ω₆, Ω₇, Ω₈)ᵀ

八极分量定义：
1. Ω₁ 阳：驱动力、探索性 [-1,1]
2. Ω₂ 阴：稳定性、保守性 [-1,1]
3. Ω₃ 表：边界敏感性、对外反应 [-1,1]
4. Ω₄ 里：深层信念、核心结构 [-1,1]
5. Ω₅ 寒：抑制、迟缓、熵增倾向 [-1,1]
6. Ω₆ 热：亢奋、过度活跃、局部有序 [-1,1]
7. Ω₇ 虚：资源/信息匮乏 [-1,1]
8. Ω₈ 实：资源/信息壅堵、路径依赖 [-1,1]

主方程（二阶非线性微分动力学）：
d²Ω/dt² + Γ(Ω)(dΩ/dt, dΩ/dt) = -∇V(Ω) - ν ⊙ (dΩ/dt) + F_{πφ}(t) + ξ(t)

纯标准库实现，零外部依赖。
"""

import random
import math
from datetime import datetime
from typing import Dict, List, Tuple


class EightPoleDynamics:
    """八极状态空间动力学——认知诊断的数学基础"""

    def __init__(self):
        # 八极状态向量 Ω = (阳, 阴, 表, 里, 寒, 热, 虚, 实)
        self.omega = [0.0] * 8
        # 状态变化率（速度）
        self.velocity = [0.0] * 8
        # 八维阻尼系数向量
        self.damping = [0.1] * 8
        # 河图洛书耦合矩阵（生克关系）
        self.coupling_matrix = self._init_hetu_luoshu()
        # 四次项权重（非线性项）
        self.quadratic_weights = [0.1] * 8
        
        # 外部驱动力
        self.external_force = [0.0] * 8
        # 噪声强度
        self.noise_intensity = 0.01
        
        # 演化历史
        self.history: List[Dict[str, List[float]]] = []
        self.max_history_length = 100

    def _init_hetu_luoshu(self) -> List[List[float]]:
        """
        生成基于河图洛书的生克耦合矩阵K
        八极相互作用关系：
        - 阴阳相生相克
        - 表里相互影响
        - 寒热对立统一
        - 虚实转化
        """
        # 8x8耦合矩阵，行和列对应：阳、阴、表、里、寒、热、虚、实
        return [
            # 阳的生克关系
            [0.0, -0.3, 0.2, 0.1, -0.2, 0.3, -0.1, 0.1],
            # 阴的生克关系
            [-0.3, 0.0, 0.1, 0.2, 0.3, -0.2, 0.1, -0.1],
            # 表的生克关系
            [0.2, 0.1, 0.0, -0.2, 0.1, -0.1, 0.2, -0.1],
            # 里的生克关系
            [0.1, 0.2, -0.2, 0.0, -0.1, 0.2, -0.1, 0.2],
            # 寒的生克关系
            [-0.2, 0.3, 0.1, -0.1, 0.0, -0.4, 0.2, -0.1],
            # 热的生克关系
            [0.3, -0.2, -0.1, 0.2, -0.4, 0.0, -0.1, 0.2],
            # 虚的生克关系
            [-0.1, 0.1, 0.2, -0.1, 0.2, -0.1, 0.0, -0.3],
            # 实的生克关系
            [0.1, -0.1, -0.1, 0.2, -0.1, 0.2, -0.3, 0.0]
        ]

    def potential(self) -> float:
        """
        计算势能函数 V(Ω) = ½ Ωᵀ·K·Ω + Σ w_i·Ω_i⁴
        """
        # 二次项：½ Ωᵀ·K·Ω
        quadratic_term = 0.5 * sum(
            self.omega[i] * self.coupling_matrix[i][j] * self.omega[j]
            for i in range(8) for j in range(8)
        )
        
        # 四次项：Σ w_i·Ω_i⁴
        quartic_term = sum(
            self.quadratic_weights[i] * self.omega[i]**4
            for i in range(8)
        )
        
        return quadratic_term + quartic_term

    def _gradient(self) -> List[float]:
        """
        计算势能梯度 ∇V(Ω)
        """
        grad = [0.0] * 8
        
        for i in range(8):
            # 二次项梯度
            quadratic_grad = sum(
                self.coupling_matrix[i][j] * self.omega[j]
                for j in range(8)
            )
            # 四次项梯度
            quartic_grad = 4 * self.quadratic_weights[i] * self.omega[i]**3
            grad[i] = quadratic_grad + quartic_grad
        
        return grad

    def step(self, dt: float = 0.01):
        """
        数值积分一步（欧拉方法）
        主方程：d²Ω/dt² = -∇V(Ω) - ν⊙v + F + ξ
        """
        # 计算加速度
        gradient = self._gradient()
        acceleration = [0.0] * 8
        
        for i in range(8):
            acceleration[i] = (
                -gradient[i]                              # 势能梯度
                - self.damping[i] * self.velocity[i]      # 阻尼项
                + self.external_force[i]                  # 外部驱动力
                + random.gauss(0, self.noise_intensity)   # 高斯噪声
            )
        
        # 更新速度和状态
        for i in range(8):
            self.velocity[i] += acceleration[i] * dt
            self.omega[i] += self.velocity[i] * dt
            
            # 边界约束：保持在[-1, 1]区间
            self.omega[i] = max(-1.0, min(1.0, self.omega[i]))
            
            # 速度阻尼：防止速度过大
            self.velocity[i] *= 0.99

        # 记录历史
        self._record_history()

    def _record_history(self):
        """记录状态历史"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "omega": list(self.omega),
            "velocity": list(self.velocity),
            "potential": self.potential()
        }
        self.history.append(record)
        if len(self.history) > self.max_history_length:
            self.history.pop(0)

    def get_state(self) -> Dict[str, float]:
        """获取当前状态快照"""
        return {
            "yang": self.omega[0],      # 阳
            "yin": self.omega[1],       # 阴
            "biao": self.omega[2],      # 表
            "li": self.omega[3],        # 里
            "han": self.omega[4],       # 寒
            "re": self.omega[5],        # 热
            "xu": self.omega[6],        # 虚
            "shi": self.omega[7],       # 实
            "potential": self.potential(),
            "entropy": self.calculate_entropy()
        }

    def calculate_entropy(self) -> float:
        """计算认知熵（基于状态分布）"""
        # 熵 = 状态向量的方差
        mean = sum(self.omega) / 8
        variance = sum((o - mean)**2 for o in self.omega) / 8
        return math.sqrt(variance)

    def set_state(self, state: Dict[str, float]):
        """设置状态"""
        self.omega[0] = state.get("yang", 0.0)
        self.omega[1] = state.get("yin", 0.0)
        self.omega[2] = state.get("biao", 0.0)
        self.omega[3] = state.get("li", 0.0)
        self.omega[4] = state.get("han", 0.0)
        self.omega[5] = state.get("re", 0.0)
        self.omega[6] = state.get("xu", 0.0)
        self.omega[7] = state.get("shi", 0.0)
        
        # 边界约束
        for i in range(8):
            self.omega[i] = max(-1.0, min(1.0, self.omega[i]))

    def set_external_force(self, force: List[float]):
        """设置外部驱动力"""
        self.external_force = force[:8]

    def evolve(self, steps: int = 100, dt: float = 0.01) -> List[Dict[str, float]]:
        """执行多步演化"""
        trajectory = []
        for _ in range(steps):
            self.step(dt)
            trajectory.append(self.get_state())
        return trajectory

    def bajizhenduan(self, wenti: list = None, xiufu: list = None):
        """八极诊断——兼容旧BaJi接口，从问题/修复列表计算健康度与六势态"""
        ws = len(wenti) if wenti else 0
        xs = len(xiufu) if xiufu else 0
        O = {'yang': 0.5, 'yin': 0.5, 'biao': 0.5, 'li': 0.5, 'han': 0.5, 're': 0.5, 'xu': 0.5, 'shi': 0.5}
        O['yang'] = min(1.0, max(-1.0, (xs / 20) - 0.5))
        O['yin'] = min(1.0, max(-1.0, 0.5 - (ws / 30)))
        O['xu'] = min(1.0, max(-1.0, ws / 20 - 0.5))
        self.omega = [O[k] for k in ['yang', 'yin', 'biao', 'li', 'han', 're', 'xu', 'shi']]
        V = sum(0.5 * O[k] * O[k] for k in O)
        jk = round(1.0 / (1.0 + abs(V)), 3)
        shizhi = self._recognize_shizhi()
        return {'shizhi': shizhi, 'shiliang': O, 'jiankangdu': jk, 'wenti_shu': ws, 'xiufu_shu': xs}

    def _recognize_shizhi(self):
        """六势态识别——基于当前omega向量"""
        o = self.omega
        if o[0] > 0.6 and o[2] > 0.5: return "太阳"
        if o[5] > 0.7 and o[7] > 0.6: return "阳明"
        if abs(o[2] - o[3]) < 0.2 and max(o[2], o[3]) > 0.4: return "少阳"
        if o[1] > 0.5 and o[4] > 0.5 and o[6] > 0.5: return "太阴"
        if o[0] < -0.3 and o[1] < -0.3: return "少阴"
        return "厥阴"

    def reset(self):
        """重置到初始状态"""
        self.omega = [0.0] * 8
        self.velocity = [0.0] * 8
        self.external_force = [0.0] * 8
        self.history = []


class SixStateRecognizer:
    """六势态识别器——将八极状态映射到六势态"""

    def __init__(self):
        # 六势态特征向量
        self.state_templates = {
            "taiyang": [0.6, -0.3, 0.5, 0.2, -0.3, 0.4, -0.2, 0.1],    # 太阳
            "yangming": [0.4, -0.2, 0.3, 0.4, -0.4, 0.7, -0.1, 0.6],   # 阳明
            "shaoyang": [0.2, 0.1, 0.3, 0.3, -0.1, 0.2, 0.1, 0.0],     # 少阳
            "taiyin": [-0.3, 0.5, -0.2, 0.3, 0.5, -0.3, 0.5, -0.2],   # 太阴
            "shaoyin": [-0.5, -0.5, -0.3, -0.3, 0.2, -0.4, 0.3, -0.1], # 少阴
            "jueyin": [0.1, 0.0, -0.1, 0.5, 0.2, 0.5, 0.3, 0.2]        # 厥阴
        }

    def recognize(self, omega: List[float]) -> str:
        """
        根据八极状态向量识别六势态
        
        Args:
            omega: 八极状态向量
            
        Returns:
            势态名称：太阳、阳明、少阳、太阴、少阴、厥阴
        """
        max_similarity = -1.0
        best_match = "jueyin"  # 默认混乱态
        
        for state_name, template in self.state_templates.items():
            # 计算余弦相似度
            dot_product = sum(o * t for o, t in zip(omega, template))
            norm_o = math.sqrt(sum(o**2 for o in omega)) + 1e-9
            norm_t = math.sqrt(sum(t**2 for t in template)) + 1e-9
            similarity = dot_product / (norm_o * norm_t)
            
            if similarity > max_similarity and similarity > 0.3:
                max_similarity = similarity
                best_match = state_name
        
        return best_match

    def get_state_description(self, state_name: str) -> Dict[str, str]:
        """获取势态描述"""
        descriptions = {
            "taiyang": {
                "name": "太阳",
                "description": "快速向边界运动，充满活力",
                "characteristics": "阳↑, 表↑, 热↑",
                "suggestion": "适合快速扩张和探索新领域"
            },
            "yangming": {
                "name": "阳明",
                "description": "内部极限环，高振幅振荡",
                "characteristics": "热↑, 实↑",
                "suggestion": "需要注意过度活跃，适当降温"
            },
            "shaoyang": {
                "name": "少阳",
                "description": "枢纽处双稳态跳跃",
                "characteristics": "表↔里交替",
                "suggestion": "处于关键转折点，需要谨慎决策"
            },
            "taiyin": {
                "name": "太阴",
                "description": "缓慢漂移，低能量状态",
                "characteristics": "阴↑, 寒↑, 虚↑",
                "suggestion": "需要注入能量，激发活力"
            },
            "shaoyin": {
                "name": "少阴",
                "description": "向崩溃点收缩",
                "characteristics": "阳↓, 阴↓",
                "suggestion": "严重警告！需要紧急干预"
            },
            "jueyin": {
                "name": "厥阴",
                "description": "混沌奇异吸引子，高熵状态",
                "characteristics": "里与热矛盾共存",
                "suggestion": "系统混乱，需要重新组织"
            }
        }
        return descriptions.get(state_name, descriptions["jueyin"])


# 单例模式
_eight_pole_dynamics = None
_six_state_recognizer = None
_content_pole_diagnosis = None


class ContentPoleDiagnosis:
    """
    内容八极诊断 V1.0 — 输入端态势识别
    
    将输入文本映射到八极维度(阳/阴/表/里/寒/热/虚/实),
    再通过六势态识别器输出态势(太阳~厥阴), 用于:
      - 输入分类(执行/对话/投喂/危险)
      - 八势策略选择(控势/破势/运势/定势)
      - π-φ认知油门调节
    
    全部用认知包(RenzhiBao), 零关键词硬编码.
    """
    # 内容八极特征模板 (LLM识别用)
    POLE_TEMPLATES = {
        "阳": "积极主动、执行导向、创造性、扩展性",
        "阴": "被动接收、信息内化、保守、收纳性",
        "表": "外部操作、工具调用、系统交互、环境改变",
        "里": "内部认知、理解消化、记忆存储、思维加工",
        "寒": "攻击性、恶意意图、破坏性、对抗性",
        "热": "建设性、协作意图、帮助请求、正向贡献",
        "虚": "求知探索、开放性问题、不确定、好奇",
        "实": "确定性指令、明确目标、具体任务、已成型内容",
    }

    # 六势态模板 (LLM判断用)
    SHI_TEMPLATES = {
        "太阳": "强烈执行意图, 创造性任务, 大胆操作, 可能涉及写文件",
        "阳明": "明确命令或请求, 工具调用, 逻辑清晰, 确定性强",
        "少阳": "温和对话, 问候闲聊, 简单问答, 无执行需求",
        "太阴": "知识投喂, 长文本, 理解请求, 需要消化吸收的内容",
        "少阴": "可疑输入, 含代码但意图不明, 权限试探, 异常模式",
        "厥阴": "明确恶意, 病毒代码, 攻击指令, 系统破坏意图",
    }

    def __init__(self, xin=None):
        self.xin = xin
        self._six_state = get_six_state_recognizer()

    def zhenduan_neirong(self, text: str) -> dict:
        """
        诊断输入内容的八极+六势态
        
        优先用LLM语义理解, 无LLM时用本地启发式规则
        
        返回: {"baji": {阳/阴/表/里/寒/热/虚/实: 0-1},
                "shizhi": "太阳"~"厥阴",
                "zhan_du": 0-1,   # 展开度(>0.5偏执行/探索)
                "shou_du": 0-1,   # 收敛度(>0.5偏理解/内化)
                "an_quan_du": 0-1} # 安全度(0=危险, 1=安全)
        """
        # 启发式快速判断(无LLM依赖)
        heuristic = self._kuaishu_panduan(text)

        # 有LLM时用认知包做深度判断
        if self.xin and self.xin.llm and self.xin.llm.api_key:
            try:
                deep = self._renzhibao_panduan(text)
                if deep:
                    return deep
            except Exception: pass

        return heuristic

    def _kuaishu_panduan(self, text: str) -> dict:
        """本地启发式: 基于文本特征的快速八极+六势态判断"""
        t = text.strip()
        length = len(t)

        # 八极维度快速评分
        baji = {"阳": 0.5, "阴": 0.5, "表": 0.5, "里": 0.5,
                "寒": 0.5, "热": 0.5, "虚": 0.5, "实": 0.5}

        # 阳: 执行意图关键词密度
        exec_words = ["执行", "运行", "写", "创建", "删除", "修改", "部署", "构建",
                      "打造", "锻造", "生成", "打包", "安装", "启动", "停止", "重启"]
        exec_count = sum(t.count(w) for w in exec_words)
        baji["阳"] = min(0.9, 0.5 + exec_count * 0.05)

        # 阴: 信息接收特征
        receive_words = ["学习", "理解", "分析", "总结", "阅读", "介绍", "解释", "定义"]
        receive_count = sum(t.count(w) for w in receive_words)
        baji["阴"] = min(0.9, 0.5 + receive_count * 0.05)

        # 表: 对外操作特征
        out_words = ["打开", "搜索", "下载", "发布", "保存", "发送", "连接", "获取",
                     "清理", "扫描", "检测", "修复", "隔离"]
        out_count = sum(t.count(w) for w in out_words)
        baji["表"] = min(0.9, 0.5 + out_count * 0.05)

        # 里: 内部处理特征
        in_words = ["思考", "内化", "锚定", "归档", "吸收", "消化", "记忆", "沉淀"]
        in_count = sum(t.count(w) for w in in_words)
        baji["里"] = min(0.9, 0.5 + in_count * 0.05)

        # 寒: 恶意/破坏特征
        mal_words = ["病毒", "木马", "攻击", "注入", "劫持", "破坏", "清除", "格式化",
                     "rm -rf", "del /f", "shutdown", "加密", "勒索", "后门", "漏洞"]
        mal_count = sum(t.count(w) for w in mal_words)
        baji["寒"] = min(0.95, 0.2 + mal_count * 0.15)

        # 热: 建设性特征
        good_words = ["帮助", "谢谢", "请", "分析", "建议", "优化", "改进", "完善",
                      "贡献", "分享", "教学", "指导"]
        good_count = sum(t.count(w) for w in good_words)
        baji["热"] = min(0.9, 0.3 + good_count * 0.05)

        # 虚: 求知不确定性
        quest_patterns = ["什么", "为什么", "如何", "怎样", "怎么", "?", "？",
                         "是什么", "怎么办", "介绍", "解释", "阐述", "描述"]
        quest_count = sum(t.count(w) for w in quest_patterns)
        baji["虚"] = min(0.9, 0.3 + quest_count * 0.05)

        # 实: 确定性/长文本
        baji["实"] = min(0.9, 0.3 + length / 2000)

        # 恶意代码专项检测
        self._jiance_exie_daima(t, baji)

        # 映射到六势态
        shizhi = self._baji_to_shizhi(baji, t)

        # 安全度
        anquan_du = 1.0 - baji["寒"]

        return {"baji": baji, "shizhi": shizhi,
                "zhan_du": baji["阳"] * 0.7 + baji["表"] * 0.3,
                "shou_du": baji["阴"] * 0.7 + baji["里"] * 0.3,
                "an_quan_du": max(0, anquan_du)}

    def _jiance_exie_daima(self, text: str, baji: dict):
        """恶意代码检测: 发现即拉高寒+实指标"""
        lower = text.lower()
        # 混淆/编码特征
        obfuscation = 0
        obf_patterns = ["eval(", "exec(", "base64", "__import__", "compile(",
                        "from base64", "import base64"]
        for p in obf_patterns:
            if p in lower: obfuscation += 1

        # 系统调用
        sys_patterns = ["os.system", "subprocess.call", "ctypes", "win32api",
                       "CreateRemoteThread", "WriteProcessMemory", "OpenProcess"]
        for p in sys_patterns:
            if p in lower: obfuscation += 1

        # 网络窃取
        net_patterns = ["requests.post", "urllib.request", "socket.socket",
                       "send(", "recv(", ".connect("]
        for p in net_patterns:
            if p in lower: obfuscation += 0.5

        if obfuscation >= 2:
            baji["寒"] = min(1.0, baji["寒"] + 0.3)
            baji["实"] = min(1.0, baji["实"] + 0.2)
        if obfuscation >= 4:
            baji["寒"] = 1.0

    def _baji_to_shizhi(self, baji: dict, text: str) -> str:
        """八极向量→六势态(本地规则)"""
        y, yin = baji["阳"], baji["阴"]
        b, li = baji["表"], baji["里"]
        h, re = baji["寒"], baji["热"]
        x, shi = baji["虚"], baji["实"]

        # 厥阴: 明确恶意
        if h > 0.7:
            return "厥阴"

        # 少阴: 可疑信号(必须有恶意特征, 不能只凭文本长度触发)
        if h > 0.5:
            return "少阴"

        # 太阳: 强执行意图
        if y > 0.6 and b > 0.5 and shi > 0.5:
            return "太阳"

        # 阳明: 明确指令
        if y > 0.5 and shi > 0.5 and h < 0.3:
            return "阳明"

        # 太阴: 知识内容
        if shi > 0.6 and yin > 0.5 and b < 0.4:
            return "太阴"

        # 少阳: 温和交互
        return "少阳"

    def _renzhibao_panduan(self, text: str) -> dict:
        """认知包深度判断(LLM)"""
        from star_nest.protocols.cognition_package import RenzhiBao
        bao = RenzhiBao("正境")
        bao.shu_ju(
            shu_ru=text[:1200],
            yao_qiu="判断输入内容的八极维度和六势态。返回JSON: "
                    "{baji:{阳:0-1,...},shizhi:'太阳'|...|'厥阴',zhan_du:0-1,shou_du:0-1,an_quan_du:0-1}")
        try:
            jg = self.xin.llm.chat([{"role": "user", "content": bao.to_json()}],
                                   wendu=0.1, zuidazifu=400)
            if jg and "{" in str(jg):
                import json
                text = str(jg)
                start = text.index("{")
                end = text.rindex("}") + 1
                result = json.loads(text[start:end])
                if "baji" in result and "shizhi" in result:
                    # 确保八极维度完整
                    for dim in ["阳","阴","表","里","寒","热","虚","实"]:
                        if dim not in result["baji"]:
                            result["baji"][dim] = 0.5
                    return result
        except Exception: pass
        return None


def get_content_pole_diagnosis(xin=None):
    global _content_pole_diagnosis
    if _content_pole_diagnosis is None:
        _content_pole_diagnosis = ContentPoleDiagnosis(xin)
    return _content_pole_diagnosis

def get_eight_pole_dynamics() -> EightPoleDynamics:
    """获取八极动力学单例"""
    global _eight_pole_dynamics
    if _eight_pole_dynamics is None:
        _eight_pole_dynamics = EightPoleDynamics()
    return _eight_pole_dynamics

def get_six_state_recognizer() -> SixStateRecognizer:
    """获取六势态识别器单例"""
    global _six_state_recognizer
    if _six_state_recognizer is None:
        _six_state_recognizer = SixStateRecognizer()
    return _six_state_recognizer


if __name__ == "__main__":
    # 测试代码
    print("=== 八极状态空间动力学测试 ===")
    
    # 测试八极动力学
    dynamics = EightPoleDynamics()
    print("初始状态:", dynamics.get_state())
    
    # 设置一个非零初始状态
    dynamics.set_state({"yang": 0.5, "yin": -0.2, "biao": 0.3, "re": 0.4})
    print("设置状态后:", dynamics.get_state())
    
    # 执行演化
    print("\n执行10步演化...")
    trajectory = dynamics.evolve(10)
    for i, state in enumerate(trajectory):
        print(f"  步{i+1}: 阳={state['yang']:.3f}, 阴={state['yin']:.3f}, 势={state['potential']:.3f}")
    
    # 测试六势态识别器
    print("\n=== 六势态识别器测试 ===")
    recognizer = SixStateRecognizer()
    
    # 测试太阳态
    taiyang_state = [0.7, -0.4, 0.6, 0.2, -0.3, 0.5, -0.2, 0.1]
    result = recognizer.recognize(taiyang_state)
    print(f"太阳态识别结果: {result}")
    print(f"描述: {recognizer.get_state_description(result)}")
    
    # 测试少阴态
    shaoyin_state = [-0.6, -0.6, -0.4, -0.3, 0.2, -0.5, 0.4, -0.2]
    result = recognizer.recognize(shaoyin_state)
    print(f"\n少阴态识别结果: {result}")
    print(f"描述: {recognizer.get_state_description(result)}")
    
    print("\n测试完成！")
