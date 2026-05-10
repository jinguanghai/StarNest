"""
问剑路 WenJianLu V2.0 [星巢·全五境预检测·肺管·心授权]

心授权全五境: 八极(正)→认知(反)→六势(合)→深层(超越)→归档(本源)

铁律:
  - 问剑路不调 LLM (正境八极·合境六势纯本地)
  - 反境五境认知调 LLM 一次(心授权)
  - 结果写经络, 心从经络读
"""
import re, time
from pathlib import Path


class WenJianLu:
    """问剑路: 全五境预检测 (心授权·肺管)"""

    ZHI_XING_CI = [
        "打开","搜索","下载","创建","删除","修改","部署","安装","启动","停止",
        "重启","运行","写","读","锻造","生成","打包","清理","扫描","杀毒",
        "检测","修复","隔离","恢复","备份","统计","列出","查找","计算",
        "翻译","克隆","升级",
    ]

    GONG_JU_KUAI_SU = [
        ("打开", r"打开\s*(.+)", "wangluo_wangluo_gongju", "dakai_liulanqi"),
        ("访问", r"访问\s*(.+)", "wangluo_wangluo_gongju", "dakai_liulanqi"),
        ("下载", r"下载\s*(.+)", "wangluo_wangluo_gongju", "xia_zai_dong_xi"),
        ("读",   r"读\s*(.+)",    "wenjian_gongju", "duqu_wenjian"),
        ("写",   r"写\s*(.+)",    "wenjian_gongju", "xieru_wenjian"),
        ("杀毒", r"杀毒\s*(.+)",  "zhaoyaojing", "sao_miao_sha_du"),
        ("锻造", r"锻造\s*(.+)",  "zhujianlu", "duanzao"),
        ("打包", r"打包\s*(.+)",  "dabao_gongju", "shengcheng_fenfa_bao"),
    ]

    URL_NI_CHENG = {
        "deepseek":"https://www.deepseek.com","deep seek":"https://www.deepseek.com",
        "deepseek官网":"https://www.deepseek.com","百度":"https://www.baidu.com",
        "谷歌":"https://www.google.com","b站":"https://www.bilibili.com",
        "bilibili":"https://www.bilibili.com","github":"https://github.com",
    }

    def __init__(self, xin):
        self.xin = xin

    def jie_shou(self, text: str) -> dict:
        """
        全五境预检测:
          正境·八极 → 反境·工具 → 合境·六势 → 超越·深层 → 本源·归档
        
        返回: {shizhi, luxian, baji, gongju_yitu, anquan_du, weixian_xinhao}
        
        铁律: 正/合纯本地, 反境可调LLM一次, 结果写经络
        """
        text = text.strip()
        if not text:
            return {"shizhi": "少阳", "luxian": "duihua", "baji": {}, "gongju_yitu": None}

        # ---- 正境·八极检测 (零LLM·纯本地) ----
        baji = self._baji_zhenduan(text)

        # ---- 反境·工具意图 (零LLM·正则+关键词) ----
        gongju_yitu = self._gongju_pipei(text)

        # ---- 合境·六势态判断 (基于八极+安全度+工具) ----
        shizhi, anquan_du, weixian = self._liushi_hejing(baji, text, gongju_yitu)

        # ---- 超越境·深度意图 (工具+知识密度综合) ----
        luxian = self._chaoyue_luxian(shizhi, baji, gongju_yitu, anquan_du, weixian)

        # ---- 本源境·写经络 ----
        result = {
            "shizhi": shizhi, "luxian": luxian, "baji": baji,
            "gongju_yitu": gongju_yitu,
            "anquan_du": anquan_du, "weixian_xinhao": weixian
        }
        if self.xin and self.xin.meridian:
            try: self.xin.meridian.jilu_zhenduan(result)
            except: pass

        return result

    # ---- 正境·八极 ----

    def _baji_zhenduan(self, text: str) -> dict:
        from star_nest.dynamics.eight_extremes import get_content_pole_diagnosis
        try:
            cpd = get_content_pole_diagnosis(self.xin)
            return cpd._kuaishu_panduan(text).get("baji", {})
        except:
            return {"阳":0.5,"阴":0.5,"表":0.5,"里":0.5,"寒":0.5,"热":0.5,"虚":0.5,"实":0.5}

    # ---- 反境·工具意图 ----

    def _gongju_pipei(self, text: str):
        # 技能缓存
        try:
            if self.xin.pi and hasattr(self.xin.pi, 'chaxun_jineng'):
                fangan = self.xin.pi.chaxun_jineng(text)
                if fangan: return fangan
        except: pass
        # 正则快速匹配
        for trigger, pattern, gm, hm in self.GONG_JU_KUAI_SU:
            if trigger in text:
                m = re.search(pattern, text)
                if m:
                    canshu = m.group(1).strip()
                    if hm == "dakai_liulanqi":
                        norm = canshu.lower().replace(" ", "").replace("官网", "")
                        for nick, url in self.URL_NI_CHENG.items():
                            if norm in nick: canshu = url; break
                    return {"gongju_ming":gm, "hanshu_ming":hm, "canshu":canshu,
                            "lujing":"", "pipei_ceng":0}
        # 模糊匹配
        for ci in self.ZHI_XING_CI:
            if ci in text:
                return "execution_cmd"
        return None

    # ---- 合境·六势态 ----

    def _liushi_hejing(self, baji: dict, text: str, gongju) -> tuple:
        y, yin = baji.get("阳",0.5), baji.get("阴",0.5)
        b, li = baji.get("表",0.5), baji.get("里",0.5)
        h, re = baji.get("寒",0.5), baji.get("热",0.5)
        x, shi = baji.get("虚",0.5), baji.get("实",0.5)

        weixian = 0
        if h > 0.6: weixian += 1
        anquan_du = max(0, 1.0 - h)

        if h > 0.7 or weixian >= 3: return ("厥阴", anquan_du, weixian)
        if h > 0.5: return ("少阴", anquan_du, weixian)
        if y > 0.6 and b > 0.5: return ("太阳", anquan_du, weixian)
        if y > 0.5 and shi > 0.5 and h < 0.3: return ("阳明", anquan_du, weixian)
        if yin > 0.5 and shi > 0.4 and b < 0.4: return ("太阴", anquan_du, weixian)
        return ("少阳", anquan_du, weixian)

    # ---- 超越境·路由 ----

    def _chaoyue_luxian(self, shizhi, baji, gongju, anquan, weixian) -> str:
        if shizhi == "厥阴" or weixian >= 3: return "gedou"
        if shizhi == "少阴": return "shencha"
        if shizhi == "太阳": return "execution_dadan"
        if shizhi == "阳明": return "execution_queren"
        if isinstance(gongju, dict): return "execution_queren"
        if gongju and shizhi not in ("太阴",): return "execution_queren"
        if shizhi == "太阴": return "touwei"
        return "duihua"


_wen_jian_lu = None

def get_wen_jian_lu(xin=None):
    global _wen_jian_lu
    if _wen_jian_lu is None: _wen_jian_lu = WenJianLu(xin)
    return _wen_jian_lu
