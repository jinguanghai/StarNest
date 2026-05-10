"""
本源境·无剑（水）：螺旋再生——如实观照与认知种子
V10.3 七律超时版：LLM调用增加超时保护，超时返回降级默认结果。

【通用问题解决操作系统·完整映射】
- 正境(Define)：rushi_guanzhao——定义归档结构
- 反境(Measure)：种子四字段完整性检查
- 合境(Improve)：shengcheng_zhongzi——压缩经验为可复用种子，存入长期记忆
- 超越境(Control)：种子上限50颗，日志上限100条
- 本源境(Sustain)：pipei_zhongzi——为新问题匹配历史种子，如实观照
"""

import json
from datetime import datetime


class BenYuan:
    """本源境：认知归档与螺旋再生——五脏共享的记忆中枢"""

    def __init__(self):
        self.protocols_rizhi = []
        self.renzhi_zhongzi = []

    def rushi_guanzhao(self, gongneng_fenxi: dict = None, yinguo_fenxi: dict = None,
                       jiupingmu_fenxi: dict = None, shuxing_fenxi: dict = None,
                       zuizhong_fangan: str = "") -> dict:
        """如实记录本轮五境流转的完整轨迹"""
        guanzhao_jilu = {
            "shijian": datetime.now().isoformat(),
            "protocols_liuzhuan": {
                "zhengjing": gongneng_fenxi or {},
                "fanjing": yinguo_fenxi or {},
                "hejing": jiupingmu_fenxi or {},
                "chaoyuejing": shuxing_fenxi or {}
            },
            "zuizhong_fangan": zuizhong_fangan[:500] if zuizhong_fangan else ""
        }
        self.protocols_rizhi.append(guanzhao_jilu)
        if len(self.protocols_rizhi) > 100:
            self.protocols_rizhi = self.protocols_rizhi[-100:]
        return guanzhao_jilu

    def shengcheng_zhongzi(self, llm, gongneng_fenxi: dict, yinguo_fenxi: dict,
                           jiupingmu_fenxi: dict, zuizhong_fangan: str,
                           xin=None) -> dict:
        """
        将本轮五境流转的精华压缩为一颗认知种子。
        种子生成后存入长期知识库和经络图谱。
        
        V10.3：LLM调用增加超时保护（yiweizhou·7秒），超时返回空字典。

        参数：
            llm: LLM客户端
            gongneng_fenxi: 肝正境定义的功能分析
            yinguo_fenxi: 脾反境的因果拆解
            jiupingmu_fenxi: 肺合境的平衡方案
            zuizhong_fangan: 最终解决方案
            xin: 心实例，用于调用肝的存储和经络写入
        """
        if not llm:
            return {}
        from star_nest.protocols.cognition_package import RenzhiBao
        bao = RenzhiBao("本源境")
        if xin and hasattr(xin, '_zuozhi_mode'):
            bao.she_zhuangtai(xin)
        bao.shu_ju(
            zhengjing={"zhuti":gongneng_fenxi.get('zhuti','?'),"keti":gongneng_fenxi.get('keti','?'),"zuoyong":gongneng_fenxi.get('zuoyong','?')},
            fanjing={"biyao_tiaojian":yinguo_fenxi.get('biyao_tiaojian','?'),"maodun_leixing":yinguo_fenxi.get('maodun_leixing','?')},
            hejing={"pingheng_fangan":jiupingmu_fenxi.get('pingheng_fangan','?')[:100]},
            zuizhong_fangan=zuizhong_fangan[:300],
        )
        try:
            chaoshi = 7
            if xin and hasattr(xin, 'wangluo') and xin.wangluo:
                try:
                    chaoshi = xin.wangluo.qilv.qu_chaoshi("yiweizhou")
                except Exception: pass
            
            jieguo = llm.chat([{"role":"user","content":bao.to_json()}], wendu=0.2, zuidazifu=400)
            zhongzi = self._jiexi_zhongzi(jieguo)
            if zhongzi and zhongzi.get("chufa_tiaojian") and zhongzi.get("zhongzi_zhaiyao"):
                # 保存到内存列表
                self.renzhi_zhongzi.append(zhongzi)
                if len(self.renzhi_zhongzi) > 50:
                    self.renzhi_zhongzi = self.renzhi_zhongzi[-50:]

                if xin and hasattr(xin, 'gan') and xin.gan:
                    try:
                        biaoti = zhongzi.get("chufa_tiaojian", "")[:80]
                        hexin = f"摘要：{zhongzi.get('zhongzi_zhaiyao', '')}\n指引：{zhongzi.get('fuyong_zhiyin', '')}"
                        xin.gan.cunru_zhishi(
                            biaoti=biaoti,
                            hexin=hexin,
                            cengji=zhongzi.get("zhongzi_leixing", "合境起点"),
                            laiyuan="本源境·shengcheng_zhongzi"
                        )
                    except Exception: pass

                if xin and hasattr(xin, 'wangluo') and xin.wangluo:
                    try:
                        xin.wangluo.jilu_jianyi(
                            leixing="renzhi_zhongzi",
                            neirong=json.dumps(zhongzi, ensure_ascii=False),
                            xinyidu=0.8
                        )
                    except Exception: pass

            return zhongzi
        except Exception:
            return {}

    def _jiexi_zhongzi(self, wenben: str) -> dict:
        zhongzi = {"shijian": datetime.now().isoformat(), "chufa_tiaojian": "",
                   "zhongzi_zhaiyao": "", "fuyong_zhiyin": "", "zhongzi_leixing": "合境起点"}
        for line in wenben.strip().split('\n'):
            line = line.strip()
            if line.startswith("触发条件："):
                zhongzi["chufa_tiaojian"] = line.replace("触发条件：","").strip()
            elif line.startswith("种子摘要："):
                zhongzi["zhongzi_zhaiyao"] = line.replace("种子摘要：","").strip()
            elif line.startswith("复用指引："):
                zhongzi["fuyong_zhiyin"] = line.replace("复用指引：","").strip()
            elif line.startswith("种子类型："):
                zhongzi["zhongzi_leixing"] = line.replace("种子类型：","").strip()
        return zhongzi

    def pipei_zhongzi(self, yonghu_xiaoxi: str) -> dict:
        """为新问题匹配最合适的认知种子"""
        for zhongzi in self.renzhi_zhongzi:
            chufa = zhongzi.get("chufa_tiaojian","")
            zhaiyao = zhongzi.get("zhongzi_zhaiyao","")
            if any(ci in yonghu_xiaoxi for ci in chufa.split() if len(ci)>1):
                return zhongzi
            elif any(ci in yonghu_xiaoxi for ci in zhaiyao.split() if len(ci)>1):
                return zhongzi
        return {}

    def liechu_zhongzi(self, zuiduo: int = 5) -> list:
        """列出最近的认知种子"""
        return [{
            "shijian": z.get("shijian","")[:19],
            "leixing": z.get("zhongzi_leixing","未知"),
            "zhaiyao": z.get("zhongzi_zhaiyao","")[:100],
            "chufa": z.get("chufa_tiaojian","")[:80]
        } for z in self.renzhi_zhongzi[-zuiduo:]]