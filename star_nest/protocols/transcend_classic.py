"""
超越境·木剑（金）：系统提示构建、风格格式化与属性创新分析
V10.4 零提示词版：所有LLM调用改用结构化数据包，不再包含任何自然语言提示词。
星巢DMN → 结构化数据 → LLM类DMN → 统计拟合 → 返回结果

【通用问题解决操作系统·完整映射】
- 正境(Define)：build_system_prompt——定义回复时的完整上下文
- 超越境(Innovate & Control)：chaoyuejing_shuxing——属性分析法突破问题
- 本源境(Sustain)：可被肾脏器共享的提示构建接口
"""

import json


class ChaoYueJing:
    """超越境：系统提示构建 + 属性创新分析——肾的伎巧之基"""

    def __init__(self, xin):
        self.xin = xin

    def build_system_prompt(self, user_msg: str, personality: str, scene: str, context: str) -> str:
        anchor = "【回复风格锚定】\n"
        anchor += f"回复风格框架：{personality}"
        if context:
            anchor += f"\n\n【记忆库检索结果】\n{context}"
        return f"""{anchor}
【当前场景】{scene}
【用户问题】{user_msg}
【输出规则 - 必须严格遵守】
1. 简洁、直接、精准，只输出事实和结果。
2. 不要解释思考过程，直接给出最终答案。
"""

    def chaoyuejing_shuxing(self, llm, yonghu_xiaoxi: str, gongneng_fenxi: dict,
                            jiupingmu_fenxi: dict, lishi_zhenduan: str = "") -> dict:
        if not llm:
            return {"shuxing_wangluo": ["未分析"], "shuxing_pipei": [],
                    "chuangxin_fangan": [], "wendingxing_baoxian": "信息不足"}

        from star_nest.protocols.cognition_package import RenzhiBao
        bao = RenzhiBao("超越境")
        if hasattr(self, 'xin') and self.xin:
            bao.she_zhuangtai(self.xin)
        bao.shu_ju(gongneng=gongneng_fenxi, pingheng_fangan=jiupingmu_fenxi.get('pingheng_fangan','')[:200],
                   yuanshi_xiaoxi=yonghu_xiaoxi, lishi_zhenduan=lishi_zhenduan[:800])
        try:
            jg = llm.chat([{"role":"user","content":bao.to_json()}], wendu=0.4, zuidazifu=600)
            fx_result = {"shuxing_wangluo": [], "shuxing_pipei": [],
                         "chuangxin_fangan": [], "wendingxing_baoxian": ""}
            quyu = ""
            for line in jg.strip().split('\n'):
                l = line.strip()
                if "【主体属性网络】" in l:
                    quyu = "shuxing"
                elif "【属性-客体匹配】" in l:
                    quyu = "pipei"
                elif "【创新方案候选】" in l:
                    quyu = "chuangxin"
                elif "【稳定性保险】" in l:
                    quyu = "baoxian"
                elif quyu == "shuxing" and l and not l.startswith("【"):
                    fx_result["shuxing_wangluo"].append(l)
                elif quyu == "pipei" and "→" in l:
                    fx_result["shuxing_pipei"].append(l)
                elif quyu == "chuangxin" and "方案" in l:
                    fx_result["chuangxin_fangan"].append(l)
                elif quyu == "baoxian" and l and not l.startswith("【"):
                    fx_result["wendingxing_baoxian"] += l + "\n"
            return fx_result
        except Exception:
            return {"shuxing_wangluo": ["未分析"], "shuxing_pipei": [],
                    "chuangxin_fangan": [], "wendingxing_baoxian": "信息不足"}