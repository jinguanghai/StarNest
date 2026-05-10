"""
反境·软剑（火）：五境流转·反境阶段——因果拆解与安全审查
V10.4 零提示词版：所有LLM调用改用结构化数据包，不再包含任何自然语言提示词。
星巢DMN → 结构化数据 → LLM类DMN → 统计拟合 → 返回结果

【通用问题解决操作系统·完整映射】
- 反境(Measure & Analyze)：fanjing_chaijie——因果拆解，基于功能定义与身份叙事
- 本源境(Sustain)：标准化拆解输出格式
"""

import json


class FanJing:
    """反境：五境流转的反境阶段——因果拆解引擎"""

    def __init__(self, xin):
        self.xin = xin

    def fanjing_chaijie(self, llm, msg: str, gongneng_fenxi: dict, xushi_kuangjia: str = ""):
        """
        反境·软剑：因果拆解。基于肝·正境的功能定义与脾的身份叙事，分析问题因果链。
        V10.4 零提示词：改为发送结构化JSON数据包。
        """
        if not llm:
            return None
        try:
            from star_nest.protocols.cognition_package import RenzhiBao
            bao = RenzhiBao("反境")
            if hasattr(self, 'xin') and self.xin:
                bao.she_zhuangtai(self.xin)
            bao.shu_ju(gongneng=gongneng_fenxi, yuanshi_xiaoxi=msg)
            jieguo = llm.chat([{"role":"user","content":bao.to_json()}], wendu=0.2, zuidazifu=200)
            fenxi = {}
            for bufen in jieguo.split(','):
                if '=' in bufen:
                    jian, zhi = bufen.split('=', 1)
                    fenxi[jian.strip()] = zhi.strip()
            if fenxi:
                return fenxi
        except Exception: pass
        return None