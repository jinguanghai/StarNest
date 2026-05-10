"""
认知包 RenzhiBao V2.0 [星巢·唯一LLM交互协议]
三层结构:
  Layer 1: 认知流(renzhi_liu)   — 五境管道, 告诉LLM按什么认知顺序思考
  Layer 2: 认知状态(renzhi_zhuangtai) — 自指, 系统当前的八极/π-φ/佐治模式
  Layer 3: 结构化数据(renzhi_shuju)   — 按当前认知阶段格式化的任务数据

用法:
    from star_nest.protocols.cognition_package import RenzhiBao
    bao = RenzhiBao.from_xin(xin, "合境")
    bao.shu_ju(gongneng={...}, yinguo={...})
    llm_input = bao.dabao()  # 打成发给LLM的包
"""
import json, time


class RenzhiBao:
    """星巢与LLM交互的唯一协议——三层认知包"""

    def __init__(self, protocols_jieduan: str = "正境"):
        self.jieduan = protocols_jieduan
        self._liu = {}         # Layer1: 认知流
        self._zhuangtai = {}    # Layer2: 认知状态
        self._shuju = {}        # Layer3: 结构化数据

    # ==================== Layer 1: 认知流 ====================

    WUJING_LIU = {
        "正境": {"bu": 1, "zuo": "定义问题边界——主体是谁、客体是什么、作用是什么",
                 "shuchu": "{zhuti, keti, zuoyong, tiaojian}",
                 "shang_you": "无(起点)", "xia_you": "反境"},
        "反境": {"bu": 2, "zuo": "拆解因果关系——阻碍是什么、因果链是什么、关键点在哪",
                 "shuchu": "{zuai_yinsu, yinguo_lian, guanjian_dian, maodun_leixing}",
                 "shang_you": "正境{zhuti,zuoyong}", "xia_you": "合境"},
        "合境": {"bu": 3, "zuo": "生成平衡方案——九屏幕法从时间/空间/动态平衡三个维度寻找可回滚方案",
                 "shuchu": "{pingheng_fangan, ke_huigun, fengxian_pinggu, [xingdong]}",
                 "shang_you": "反境{zuai_yinsu,yinguo_lian}", "xia_you": "超越境/执行"},
        "超越境": {"bu": 4, "zuo": "创新突破——属性分析、资源分析，仅在物理矛盾无法调和时触发",
                 "shuchu": "{chuangxin_fangan, shuxing_fenxi}",
                 "shang_you": "合境{pingheng_fangan}", "xia_you": "本源境"},
        "本源境": {"bu": 5, "zuo": "归档固化——提取认知种子、写入长期记忆、更新基线",
                 "shuchu": "{zhongzi, guan_jian_jiao_xun}",
                 "shang_you": "全部历史", "xia_you": "闭环→新正境"},
    }

    def she_liu(self):
        """Layer1: 设置当前阶段的认知流指令"""
        liu_info = self.WUJING_LIU.get(self.jieduan, self.WUJING_LIU["正境"])
        self._liu = {
            "guan_xian": "五境认知流",
            "shuo_ming": "按正→反→合→超越→本源五步递进思考。当前处于指定阶段，参考上游产出、为下游准备。",
            "dang_qian": {
                "jie_duan": self.jieduan,
                "bu_zhou": liu_info["bu"],
                "ren_wu": liu_info["zuo"],
                "shu_chu_ge_shi": liu_info["shuchu"],
            },
            "shang_you": liu_info.get("shang_you", ""),
            "xia_you": liu_info.get("xia_you", ""),
        }
        return self

    # ==================== Layer 2: 认知状态 ====================

    def she_zhuangtai(self, xin):
        """Layer2: 从xin提取自指认知状态"""
        zt = {}
        # 佐治
        try: zt["zuozhi_mode"] = getattr(xin, '_zuozhi_mode', 'active')
        except Exception: pass
        # 六势态
        try: zt["liushizhi"] = getattr(xin, '_liushizhi', '少阳')
        except Exception: pass
        # 健康度
        try:
            if hasattr(xin, '_zuihou_jiankangdu') and xin._zuihou_jiankangdu:
                zt["jiankangdu"] = round(xin._zuihou_jiankangdu, 3)
        except Exception: pass
        # π-φ
        try:
            if xin._piphicycle:
                ps = xin._piphicycle.get_state()
                zt["pi_phi"] = {"pi": round(ps['pi_energy'], 2), "phi": round(ps['phi_energy'], 2),
                                "entropy": round(ps['entropy'], 2)}
        except Exception: pass
        # 历史参考
        try:
            if xin.gan and hasattr(xin.gan, 'qu_protocols_lishi'):
                lishi = xin.gan.qu_protocols_lishi(self.jieduan, 1)
                if lishi: zt["lishi_cankao"] = lishi[:200]
        except Exception: pass
        self._zhuangtai = zt
        return self

    # ==================== Layer 3: 结构化数据 ====================

    def shu_ju(self, **kw):
        """Layer3: 按当前认知阶段格式化的任务数据"""
        self._shuju = kw
        return self

    # ==================== 打包: 发给LLM ====================

    def dabao(self) -> dict:
        """三层打包——星巢与LLM交互的唯一格式"""
        if not self._liu:
            self.she_liu()
        return {
            "renzhi_liu": self._liu,
            "renzhi_zhuangtai": self._zhuangtai,
            "renzhi_shuju": self._shuju,
        }

    def to_json(self) -> str:
        return json.dumps(self.dabao(), ensure_ascii=False)

    # ==================== 快捷工厂 ====================

    @classmethod
    def from_xin(cls, xin, jieduan: str = "正境"):
        """快捷: 从xin创建完整认知包"""
        bao = cls(jieduan)
        bao.she_liu()
        bao.she_zhuangtai(xin)
        return bao

    @classmethod
    def dui_hua(cls, xin, msg: str, cengji: str = "正境"):
        """快捷: 对话场景的认知包"""
        bao = cls.from_xin(xin, cengji)
        bao.shu_ju(xiaoxi=msg)
        return bao
