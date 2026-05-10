"""
五脏·脾 (pi.py) - 藏意，主运化，五味出焉
V10.3.2 清空技能库版：藏剑阁管理、铸剑炉调度、反境代理、叙事运化、五行信号响应。
技能库初始化为空——所有工具需求走铸剑炉现场锻造。

五行信号响应（土属性）：
- 木克土：工具降级（_gongju_jiangji = True）
- 火生土：解除降级 + 刷新藏剑阁（sili_pihe）

七律映射：
- run() 循环间隔 = 7 (yiweizhou·一微周)

【通用问题解决操作系统·完整映射】
- 正境(Define)：qu_xushi_kuangjia + si_lv_pi_pei——定义身份、意图
- 反境(Measure & Analyze)：fanjing_chaijie（委托反境）+ 匹配日志——可追踪的匹配链路
- 合境(Improve)：任务规划——用藏剑阁已有工具组合解决未直接匹配的任务
- 超越境(Control)：降级兜底 + 铸剑炉锻造新工具 / LLM意图兜底
- 本源境(Sustain)：叙事框架持久化——演化历史归档；技能库持久化——肌肉记忆
"""

import json, threading, time, re, importlib.util, ast
from pathlib import Path
from datetime import datetime
from star_nest.meridian.seven_laws import QiLv
from star_nest.execution.forge import ZhuJianLu
from star_nest.protocols.harm_assist import sheng_ming_hai, sheng_ming_zuo

CANGJIANGE_HANSHU = {
    "wenjian_gongju": {"lujing":"","hanshu":["duqu_wenjian","xieru_wenjian","chuangjian_mulu","liechu_mulu","sousuo_wenjian","wenjian_xinxi","wenben_tongji"]},
    "wangluo_gongju": {"lujing":"","hanshu":["zhuawang_ye","jiancha_lianjie","tiqiu_wenben","diaoyong_api"]},
    "shijian_gongju": {"lujing":"","hanshu":["dangqian_shijian","shijianchuo_zhuanhuan","jisuan_haoshi","geshihua_shijian"]},
    "shuju_gongju": {"lujing":"","hanshu":["duqu_json","xieru_json","shenceng_quzhi","tongji_zipin","tongji_cipin","csv_zhuan_list"]},
    "xitong_gongju": {"lujing":"","hanshu":["xitong_xinxi","ziyuan_zhuangtai","cipan_kongjian","dangqian_jincheng_xinxi","execution_mingling"]},
    "dabao_gongju": {"lujing":"","hanshu":["shengcheng_fenfa_bao"]},
    "wenben_gongju": {"lujing":"","hanshu":["sousuo_wenben","tihuan_wenben","tongji_zifu","geshi_zhuanhuan"]},
    "moban_gongju": {"lujing":"","hanshu":["shengcheng_py","shengcheng_bat","shengcheng_config"]},
    "fenxi_gongju": {"lujing":"","hanshu":["fenxi_fuza_du","fenxi_yilai","chongfu_wenben","duibi_wenjian"]},
    "ruanjianceng": {"lujing":"","hanshu":["cao_zuo_ruan_jian","ruan_jian_zhi_shi","sheng_cheng_jiao_ben","zhi_xing_jiao_ben","jiao_fu"]},
    "liushuixian": {"lujing":"","hanshu":["cao_zuo_ren_yi_ling_yu","ling_yu_shi_pei","ruan_jian_fa_xian","bian_pai","zhi_xing","xue_xi"]},
    "xitong_cao_zuo": {"lujing":"","hanshu":["qing_li_la_ji","cha_xun_zhu_ce_biao","shan_chu_zhu_ce_biao","guan_li_fu_wu","guan_li_jin_cheng","qing_li_ci_pan","guan_li_ji_hua_ren_wu"]},
    "jiyiguanli": {"lujing":"","hanshu":["touwei","zidong_bianma"]},
}


class ToolManager:
    """藏剑阁·工具管理器 V1.0 [星巢·工具进化系统]
    注册表 + 质量评分 + 语义搜索 + 进化反馈
    """

    def __init__(self):
        self.zhu_ce = {}         # {name: {path, desc, quality, calls, tags}}
        self._zuihou_gengxin = 0

    def zhu_ce_gongju(self, name, path, desc="", tags=None, quality=0.5):
        """注册/更新工具"""
        entry = self.zhu_ce.get(name, {"calls": 0, "success": 0})
        entry.update({
            "name": name, "path": str(path), "desc": desc or name,
            "tags": tags or [],
            "quality": quality,
        })
        self.zhu_ce[name] = entry
        self._zuihou_gengxin = time.time()
        return entry

    def ji_lu_diao_yong(self, name, success=True):
        """记录工具调用(经络已有jilu_gongju, 此为ToolManager本地统计)"""
        entry = self.zhu_ce.get(name)
        if not entry:
            return
        calls = entry.get("calls", 0) + 1
        succ = entry.get("success", 0) + (1 if success else 0)
        # 质量 = 成功率 × 调用频度加权
        quality = round(succ / max(calls, 1) * min(1.0, calls / 10), 3)
        entry["calls"] = calls
        entry["success"] = succ
        entry["quality"] = quality

    def pai_ming(self, query="", top_k=5):
        """按质量排序返回工具列表, 有查询时加语义加权"""
        tools = []
        for name, entry in self.zhu_ce.items():
            score = entry.get("quality", 0.5)
            # 关键词加分
            if query:
                full_text = f"{name} {entry.get('desc','')} {' '.join(entry.get('tags',[]))}"
                matches = sum(1 for w in query.split() if w in full_text)
                score += matches * 0.05
            tools.append((name, score, entry))
        tools.sort(key=lambda x: x[1], reverse=True)
        return tools[:top_k]

    def sou_suo(self, query, top_k=3):
        """语义搜索: 名称+描述+标签 关键词匹配"""
        results = []
        for name, entry in self.zhu_ce.items():
            full = f"{name} {entry.get('desc','')} {' '.join(entry.get('tags',[]))}"
            hits = sum(1 for w in query.split() if w.lower() in full.lower())
            if hits > 0:
                score = hits * 0.3 + entry.get("quality", 0.5) * 0.7
                results.append((name, score, entry))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def qu_tong_ji(self):
        """返回工具统计摘要"""
        return {
            "zong_shu": len(self.zhu_ce),
            "zhi_liang_gao": sum(1 for e in self.zhu_ce.values() if e.get("quality",0) > 0.7),
            "zhi_liang_di": sum(1 for e in self.zhu_ce.values() if e.get("quality",0) < 0.3),
            "zong_diao_yong": sum(e.get("calls",0) for e in self.zhu_ce.values()),
        }


class PiZang(threading.Thread):
    """脾线程：仓廪之官，运化五味。藏剑阁管理、铸剑炉调度、反境代理、叙事运化、技能库管理、五行信号响应"""

    def __init__(self, meridian, zhujianlu, llm, jiyiguanli, peizhi, juese="yunxingti"):
        ziwowangluo = meridian
        xin = None
        cunchu_mulu = peizhi.XINGCHAOZDD_MULU
        self.meridian = meridian
        self.zhujianlu = zhujianlu
        self.ke_xieru = (juese == "bianchengti")
        self.jiyiguanli = jiyiguanli
        self.peizhi = peizhi
        self.juese = juese
        self._yunxing = True
        super().__init__(daemon=True, name="Pi_Narrative")
        self.wangluo = ziwowangluo
        self.xin = xin
        self.llm = llm or (xin.llm if xin else None)
        self.mulu = cunchu_mulu / "peizhi" if cunchu_mulu else Path(__file__).parent.parent / "jiyi"
        self.mulu.mkdir(parents=True, exist_ok=True)
        self.xiangmu_mulu = Path(__file__).resolve().parent.parent
        # 兼容 xingchao_code: 如果 pi.py 在 kernel/organs/ 下, 根目录是 xingchao_code/
        if self.xiangmu_mulu.name == 'kernel':
            self.xiangmu_mulu = self.xiangmu_mulu.parent
        self.xushi_md = self.mulu / "ziwo_xushi.md"
        self.xushi_yanhua_json = self.mulu / "xushi_yanhua.json"
        self.jineng_json = self.mulu / "jineng_jiyi.json"
        self.suo = threading.Lock()
        self.kuangjia = self._jiazai_kuangjia()
        self.jineng_ku = self._jiazai_jineng()
        self.armory_mulu = self.xiangmu_mulu / "armory"
        self.armory_mulu.mkdir(exist_ok=True)
        self.gongju_zhuche = {}
        self.tool_mgr = ToolManager()  # 工具管理器
        self._saomiao_armory()

        self._pipei_shibai_cishu = 0
        self._zouzhai_liebiao = []
        self._last_heartbeat = time.time()
        self._heartbeat_interval = 5.0
        self._gongju_jiangji = False
        self._yunxing = True
        self._warmup_complete = False

        self.zhujianlu = ZhuJianLu(gongzuo_mulu=self.xiangmu_mulu)
        self.fanjing = None

        print(f"[脾] 就绪（V10.3.2 清空技能库·现场锻造版）。")

    def run(self):
        self._zuozhi_xushi = 0  # 佐治·叙事演化冷却
        while self._yunxing:
            self._last_heartbeat = time.time()
            if self.wangluo:
                time.sleep(self.wangluo.qilv.qu_chaoshi("yiweizhou"))
            else:
                time.sleep(QiLv().qu_chaoshi("yiweizhou"))
            self._xiangying_wuxing_xinhao()
            # 佐治: 身份叙事作为害检测——检查自我定位是否有偏差
            if self.wangluo and self.wangluo.check_dmn_rest() and time.time() - self._zuozhi_xushi > 2401 \
                    and self.xin and self.xin.llm:
                self._zuozhi_xushi_yanhua()
                self._zuozhi_xushi = time.time()

    def _zuozhi_xushi_yanhua(self):
        """佐治·身份审查: 检查自我定位偏差(害), LLM反思是否需要修正"""
        try:
            kj = self.qu_xushi_kuangjia()
            if not kj or not self.xin.llm:
                return
            # V11.0: 统一认知包
            from star_nest.protocols.cognition_package import RenzhiBao
            bao = RenzhiBao.from_xin(self.xin, "本源境")
            bao.shu_ju(
                dangqian_xushi=kj,
                zuijin_shijian=str(list(self.xin.gan.duanqi_jiyi)[-3:])[:300] if self.xin and self.xin.gan else "",
            )
            jg = self.xin.llm.chat([{"role":"user","content":bao.to_json()}], wendu=0.3, zuidazifu=400)
            if jg and "bianhua" in jg:
                self._baocun_xushi_yanhua("dmn_rest_evolution", jg[:300])
                self.wangluo.jilu_fansi(f"身份演化: {jg[:200]}")
        except Exception as e:
            try:
                if self.meridian and hasattr(self.meridian, 'rizhi') and self.meridian.rizhi:
                    self.meridian.rizhi.wenti_rizhi(self.juese, {"miaoshu": f"佐治身份审查异常:{e}", "leixing": "zuozhi_xushi_error"})
            except Exception: pass

    def _xiangying_wuxing_xinhao(self):
        if not self.wangluo:
            return
        xianzai = time.time()
        try:
            for node_id in self.wangluo.tupu.nodes():
                shuxing = self.wangluo.tupu._nodes.get(node_id, {})
                leixing = shuxing.get("leixing", "")
                biaoqian = shuxing.get("biaoqian", "")
                shijian_str = shuxing.get("shijian", "")
                if shijian_str:
                    try:
                        shijian_dt = datetime.fromisoformat(shijian_str)
                        if (xianzai - shijian_dt.timestamp()) > self.wangluo.qilv.qu_zhouqi("yixiaozhou"):
                            continue
                    except Exception:
                        pass
                if leixing == "wuxing_ke" and "木克土" in biaoqian:
                    self._gongju_jiangji = True
                elif leixing == "wuxing_sheng" and "火生土" in biaoqian:
                    self._gongju_jiangji = False
                    self.sili_pihe()
        except Exception:
            pass

    def qidong_warmup(self):
        print("[脾] 叙事运化中...")
        zizhuan_neirong = ""
        zizhuan_path = self.mulu / "zizhuan_jiyi.md"
        if zizhuan_path.exists():
            try:
                quanbu = zizhuan_path.read_text(encoding='utf-8')
                zizhuan_neirong = quanbu[-5000:] if len(quanbu) > 5000 else quanbu
                print(f"[脾]   自传记忆已读取：{len(zizhuan_neirong)} 字符")
            except Exception as e:
                print(f"[脾]   自传记忆读取失败: {e}")

        if zizhuan_neirong and self.llm:
            try:
                xin_xushi = self._yunhua_xushi(zizhuan_neirong)
                if xin_xushi and len(xin_xushi) == 4:
                    jiu_kuangjia = dict(self.kuangjia)
                    self.kuangjia = xin_xushi
                    self._baocun_xushi()
                    print(f"[脾]   身份叙事已更新")
                    self._baocun_xushi_yanhua(jiu_kuangjia, xin_xushi, zizhuan_neirong[:500])
                    print(f"[脾]   叙事演化已记录")
                else:
                    print(f"[脾]   叙事框架保持不变")
            except Exception as e:
                print(f"[脾]   叙事运化异常: {e}")
        else:
            print(f"[脾]   无自传记忆或LLM不可用，叙事框架保持初始状态")

        if not self.jineng_ku:
            self.jineng_ku = []
            self._baocun_jineng()
            print(f"[脾]   技能库已初始化：0 项（现场锻造模式）")

        print(f"[脾]   身份：{self.kuangjia.get('shenfen','?')[:60]}")
        print(f"[脾]   技能：{len(self.jineng_ku)} 项")
        self._warmup_complete = True
        print("[脾] 叙事基线已建立 · 铸剑炉待命")

    def _jiazai_jineng(self) -> list:
        if self.jineng_json.exists():
            try:
                return json.loads(self.jineng_json.read_text(encoding='utf-8'))
            except Exception:
                pass
        return []

    def _baocun_jineng(self):
        try:
            self.jineng_json.write_text(
                json.dumps(self.jineng_ku, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
        except Exception:
            pass

    def chaxun_jineng(self, yonghu_xiaoxi: str) -> dict:
        for jineng in self.jineng_ku:
            if jineng.get("zhuangtai") != "jihuo":
                continue
            for ci in jineng.get("chufa_ci", []):
                if ci in yonghu_xiaoxi:
                    jineng["leiji_diaoyong"] = jineng.get("leiji_diaoyong", 0) + 1
                    jineng["zuihou_shiyong"] = datetime.now().isoformat()
                    self._baocun_jineng()
                    
                    canshu_moban = dict(jineng.get("canshu_moban", {}))
                    canshu = self._tiqu_jineng_canshu(yonghu_xiaoxi, jineng, canshu_moban)
                    
                    return {
                        "gongju_ming": jineng["gongju_ming"],
                        "hanshu_ming": jineng["hanshu_ming"],
                        "lujing": self.gongju_zhuche.get(jineng["gongju_ming"], {}).get("lujing", ""),
                        "canshu": canshu,
                        "laolao_execution": True
                    }
        return None

    def _tiqu_jineng_canshu(self, yonghu_xiaoxi: str, jineng: dict, canshu_moban: dict):
        if "wangzhi" in canshu_moban:
            url_match = re.search(r'(https?://[^\s]+)', yonghu_xiaoxi)
            if url_match:
                canshu_moban["wangzhi"] = url_match.group(1)
            elif canshu_moban.get("wangzhi", "") == "":
                yuming_match = re.search(r'(?:打开|访问|官网|网站|上网)\s*([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)', yonghu_xiaoxi)
                if yuming_match:
                    canshu_moban["wangzhi"] = "https://www." + yuming_match.group(1)
                else:
                    canshu_moban["wangzhi"] = "https://www.deepseek.com"
        
        if "lujing" in canshu_moban and canshu_moban.get("lujing", "") == "":
            lujing_match = re.search(r'(?:读取|读|查看|打开)\s*["\']?([^\s"\']+)["\']?', yonghu_xiaoxi)
            if lujing_match:
                canshu_moban["lujing"] = lujing_match.group(1)
        
        if "neirong" in canshu_moban and canshu_moban.get("neirong", "") == "":
            neirong_match = re.search(r'(?:写入|写)\s*["\']?([^"\']+?)["\']?\s*(?:到|$)', yonghu_xiaoxi)
            if neirong_match:
                canshu_moban["neirong"] = neirong_match.group(1)
        
        if len(canshu_moban) == 1 and "" in canshu_moban.values():
            return list(canshu_moban.values())[0]
        
        if len(canshu_moban) == 1:
            return list(canshu_moban.values())[0]
        
        if not canshu_moban:
            return None
        
        return canshu_moban

    def jineng_ruku(self, gongju_ming: str, hanshu_ming: str, miaoshu: str, chufa_ci: list, canshu_moban: dict):
        for jn in self.jineng_ku:
            if jn["gongju_ming"] == gongju_ming and jn["hanshu_ming"] == hanshu_ming:
                return
        xin_jineng = {
            "gongju_ming": gongju_ming,
            "hanshu_ming": hanshu_ming,
            "miaoshu": miaoshu,
            "chufa_ci": chufa_ci,
            "canshu_moban": canshu_moban,
            "chenggong_lv": 0.95,
            "leiji_diaoyong": 0,
            "neihua_shijian": datetime.now().isoformat(),
            "zuihou_shiyong": None,
            "zhuangtai": "jihuo"
        }
        self.jineng_ku.append(xin_jineng)
        self._baocun_jineng()
        if self.wangluo:
            try:
                self.wangluo.jilu_shijian(
                    "jineng_neihua",
                    "技能内化",
                    f"{gongju_ming}.{hanshu_ming} 从藏剑阁兵器内化为肌肉记忆"
                )
            except Exception:
                pass

    def sili_pihe(self):
        try:
            self._saomiao_armory()
            self._pipei_shibai_cishu = 0
        except Exception: pass

    def fanjing_chaijie(self, llm, msg: str, gongneng_fenxi: dict):
        if not self.fanjing: return None
        try: return self.fanjing.fanjing_chaijie(llm, msg, gongneng_fenxi)
        except Exception: return None

    @sheng_ming_hai([
        ("LLM_xuanyun", "LLM返回无效工具或幻觉匹配", 1),
        ("shuru_feiqi", "用户输入过短或无法解析", 0),
        ("chaoshi", "技能缓存过期或LLM超时", 1),
    ])
    @sheng_ming_zuo({
        "LLM_xuanyun": True,
        "shuru_feiqi": True,
        "chaoshi": True,
    })
    def si_lv_pi_pei(self, llm, yonghu_xiaoxi: str):
        # 对话意图快速通道 (问候/闲聊→直接返回None→走_duihua)
        
        # 第一层: 对话意图快速通道 (问候/闲聊→直接返回None→走_duihua)
        duihua_ci = ["你好", "hello", "hi", "谢谢", "再见", "bye", "拜拜", "你是谁", "介绍一下", "你叫什么",
                     "在吗", "在不在", "好吧", "好的", "好吗", "能不能", "聊聊", "聊天", "说话"]
        if any(ci in yonghu_xiaoxi.lower() for ci in duihua_ci):
            renwu_mix = ["打开","搜索","读 ","查 ","列出","写 ","创建","新建","锻造","打包","执行"]
            if not any(r in yonghu_xiaoxi for r in renwu_mix):
                return None
        
        # 第二层: 技能缓存命中 (最快·肌肉记忆)
        jineng_fangan = self.chaxun_jineng(yonghu_xiaoxi)
        if jineng_fangan:
            return jineng_fangan
        
        # 第三层: 认知包语义匹配 (替代BENDI_GUANJIANCI+自动词表)
        if llm and hasattr(llm, 'chat'):
            fangan = self._renzhibao_pipei(llm, yonghu_xiaoxi)
            if fangan:
                return fangan

        # 第四层: LLM语义理解 + 深度任务规划(兜底)
        if llm and hasattr(llm, 'chat'):
            ranked = self.tool_mgr.pai_ming(yonghu_xiaoxi, top_k=20)
            seen = set()
            gongju_miaoshu = ""
            for name, score, entry in ranked:
                if name.startswith("ceshi_") or name in ("quanliang_ceshi","fuzhiti_menjin"):
                    continue
                seen.add(name)
                gongju_miaoshu += f"- {name}: {entry.get('desc',name)}\n"
            for ming, xinxi in self.gongju_zhuche.items():
                if ming not in seen:
                    if ming.startswith("ceshi_") or ming in ("quanliang_ceshi","fuzhiti_menjin"):
                        continue
                    gongju_miaoshu += f"- {ming}: {xinxi.get('miaoshu',ming)}\n"
            if gongju_miaoshu:
                tishi = f"工具列表：\n{gongju_miaoshu}\n用户请求：\"{yonghu_xiaoxi}\"\n选择: 工具名|函数名。无法匹配: 对话"
                try:
                    jieguo = llm.chat([{"role":"user","content":tishi}], wendu=0.05, zuidazifu=100)
                    if jieguo and "对话" not in jieguo and "|" in jieguo:
                        bufen = jieguo.strip().split('|')
                        if len(bufen) >= 2:
                            gm, hm = bufen[0].strip(), bufen[1].strip()
                            fangan = self._goujian_fangan(gm, hm, llm, yonghu_xiaoxi)
                            if fangan:
                                return fangan
                except Exception: pass
            guihua = self._doubi_renwu_guihua(llm, yonghu_xiaoxi)
            if guihua:
                return guihua
        
        return None

    def _renzhibao_pipei(self, llm, yonghu_xiaoxi: str):
        """
        认知包语义匹配: 替代关键词字典(原BENDI_GUANJIANCI + zidong_ci)
        
        用RenzhiBao让LLM理解用户意图 → 匹配工具注册表 → 返回fangan。
        一次性调用替代逐关键词遍历（150条 → 1条LLM调用）。
        """
        try:
            from star_nest.protocols.cognition_package import RenzhiBao
            # 构建工具描述(只传工具名+描述, 不传关键词)
            tool_descs = []
            for ming, xinxi in list(self.gongju_zhuche.items())[:30]:
                tool_descs.append(f"{ming}: {xinxi.get('miaoshu','')[:80]}")
            # 自动词表中的新工具
            zi = getattr(self, 'zidong_ci', {})
            for ci, (gm, hm) in list(zi.items())[:10]:
                if gm not in [d.split(':')[0] for d in tool_descs]:
                    tool_descs.append(f"{gm}.{hm}: 自动工具({ci})")

            bao = RenzhiBao("合境")
            bao.shu_ju(
                yonghu_qingqiu=yonghu_xiaoxi[:300],
                ke_yong_gongju="; ".join(tool_descs[:20])[:1500],
                yao_qiu="匹配工具: 输出 工具名|函数名。纯对话需求: 输出 对话。"
            )
            jg = llm.chat([{"role":"user","content":bao.to_json()}], wendu=0.1, zuidazifu=80)
            if jg and "|" in str(jg) and "对话" not in str(jg):
                parts = str(jg).strip().split('|')
                if len(parts) >= 2:
                    gm, hm = parts[0].strip(), parts[1].strip()
                    fangan = self._goujian_fangan(gm, hm, llm, yonghu_xiaoxi)
                    if fangan:
                        return fangan
        except Exception: pass
        return None

    def _goujian_fangan(self, gongju_ming, hanshu_ming, llm, yonghu_xiaoxi):
        if gongju_ming == "zhujianlu":
            return {"gongju_ming":gongju_ming,"hanshu_ming":hanshu_ming,"lujing":"","canshu":yonghu_xiaoxi}
        if gongju_ming in self.gongju_zhuche:
            return {"gongju_ming":gongju_ming,"hanshu_ming":hanshu_ming,"lujing":self.gongju_zhuche[gongju_ming]["lujing"],"canshu":self._tiqu_canshu(llm,yonghu_xiaoxi,gongju_ming,hanshu_ming)}
        return None

    def _doubi_renwu_guihua(self, llm, yonghu_xiaoxi: str):
        if not llm: return None
        for ming in CANGJIANGE_HANSHU:
            if ming in self.gongju_zhuche:
                CANGJIANGE_HANSHU[ming]["lujing"] = self.gongju_zhuche[ming]["lujing"]
        from star_nest.protocols.cognition_package import RenzhiBao
        bao = RenzhiBao("合境")
        bao.shu_ju(yonghu_xiaoxi=yonghu_xiaoxi, ke_yong_gongju=CANGJIANGE_HANSHU,
                   zhu_jian_lu="铸剑炉执行/锻造, 函数:duanzao|zhijian")
        try:
            jieguo = llm.chat([{"role":"user","content":bao.to_json()}], wendu=0.2, zuidazifu=300)
            if "无法完成" in jieguo or not jieguo.strip(): return None
            bufen = jieguo.strip().split('|')
            if len(bufen) < 2: return None
            gongju_ming, hanshu_ming = bufen[0].strip(), bufen[1].strip()
            canshu = bufen[2].strip() if len(bufen) > 2 else ""
            if gongju_ming == "zhujianlu":
                return {"gongju_ming":gongju_ming,"hanshu_ming":hanshu_ming,"lujing":"","canshu":canshu or yonghu_xiaoxi}
            if gongju_ming not in self.gongju_zhuche: return None
            lujing = self.gongju_zhuche[gongju_ming]["lujing"]
            try:
                spec = importlib.util.spec_from_file_location(gongju_ming, lujing)
                mokuai = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mokuai)
                if not hasattr(mokuai, hanshu_ming): return None
            except Exception: return None
            return {"gongju_ming":gongju_ming,"hanshu_ming":hanshu_ming,"lujing":lujing,"canshu":canshu}
        except Exception: return None

    def _tiqu_canshu(self, llm, yonghu_xiaoxi, gongju_ming, hanshu_ming):
        if gongju_ming == "zhujianlu": return yonghu_xiaoxi
        # 文件操作: 正则提取文件路径
        if gongju_ming == "wenjian_gongju":
            path_match = re.search(r'["\']?([A-Za-z]:[\\/][^\s"\']+\.\w+)["\']?', yonghu_xiaoxi)
            if path_match:
                return path_match.group(1)
            path_match = re.search(r'([A-Za-z]:[\\/][^\n]{2,80})', yonghu_xiaoxi)
            if path_match:
                return path_match.group(1).strip()
            # liechu_mulu无路径时: 藏剑阁→armory目录, 否则当前目录
            if hanshu_ming == "liechu_mulu":
                if any(w in yonghu_xiaoxi for w in ["藏剑阁","兵器","工具","武器"]):
                    return str(self.armory_mulu)
                return "."
        try:
            tishi = f"""只输出结果本身。用户消息："{yonghu_xiaoxi}"。工具：{gongju_ming}。函数：{hanshu_ming}。提取参数。不需要参数→无参数"""
            canshu_str = llm.chat([{"role":"user","content":tishi}], wendu=0.05, zuidazifu=100)
            if canshu_str and canshu_str.strip() not in ("无参数","无法提取",""):
                canshu_str = canshu_str.strip()
                if not canshu_str.startswith("http") and hanshu_ming in ("zhuawang_ye","dakai_liulanqi","neihua_gongju"):
                    url_match = re.search(r'(https?://[^\s\"]+)', canshu_str)
                    if url_match: canshu_str = url_match.group(1)
                    else:
                        # LLM返回了无协议头的域名，正则从用户消息提取
                        dm = re.search(r'([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)', yonghu_xiaoxi)
                        if dm: canshu_str = dm.group(1)
                # 过滤明显非路径的LLM输出
                if hanshu_ming in ("liechu_mulu","duqu_wenjian") and ("{" in canshu_str or "name" in canshu_str):
                    return "."
                return canshu_str
        except Exception: pass
        if hanshu_ming in ("zhuawang_ye","dakai_liulanqi","neihua_gongju"):
            # 从用户消息中提取域名/URL (去空格去修饰词)
            yx = yonghu_xiaoxi.replace("的","").replace("一下","").replace("帮我","")
            dm = re.search(r'(https?://[^\s\"]+)', yx)
            if dm: return dm.group(1)
            dm = re.search(r'([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)', yx)
            if dm: return dm.group(1).replace(" ","")
            # 无域名 → 从消息提取核心词并自动补.com
            name = yx.replace(" ","").replace("打开","").replace("访问","").replace("浏览","").replace("官网","").replace("网站","").strip()
            if name and "." not in name:
                name = name + ".com"
            return name
        return "." if hanshu_ming == "liechu_mulu" else yonghu_xiaoxi

    def _jilu_pipei_chenggong(self, fangan, yonghu_xiaoxi=""):
        try:
            if self.wangluo:
                self.wangluo.jilu_shijian("gongju_pipei", "工具匹配成功",
                    json.dumps({"gongju":f"{fangan.get('gongju_ming','')}.{fangan.get('hanshu_ming','')}","yonghu":yonghu_xiaoxi[:100]}, ensure_ascii=False))
        except Exception: pass

    def _jilu_pipei_shibai(self, yonghu_xiaoxi="", yuanyin=""):
        try:
            if self.wangluo:
                self.wangluo.jilu_fansi(
                    wenti=f"脾·匹配失败[{datetime.now().strftime('%H:%M:%S')}]：{yuanyin[:80]}",
                    laiyuan_jiedian="xin"
                )
        except Exception: pass

    def _jilu_doubi_guihua(self, fangan, yonghu_xiaoxi=""):
        try:
            if self.wangluo:
                self.wangluo.jilu_shijian("doubi_guihua", "兜底任务规划",
                    json.dumps({"gongju":f"{fangan.get('gongju_ming','')}.{fangan.get('hanshu_ming','')}","yonghu":yonghu_xiaoxi[:100]}, ensure_ascii=False))
                self.wangluo.jilu_fansi(wenti=f"脾·兜底规划[{datetime.now().strftime('%H:%M:%S')}]", laiyuan_jiedian="xin")
        except Exception: pass

    def qu_xushi_kuangjia(self):
        with self.suo:
            return f"【身份】{self.kuangjia.get('shenfen','')}\n【目标】{self.kuangjia.get('mubiao','')}\n【原则】{self.kuangjia.get('yuanze','')}\n【行为】{self.kuangjia.get('xingwei','')}"

    def _yunhua_xushi(self, zizhuan_neirong: str) -> dict:
        if not self.llm:
            return None
        from star_nest.protocols.cognition_package import RenzhiBao
        bao = RenzhiBao("本源境")
        bao.shu_ju(
            jin_qi_jing_li=zizhuan_neirong[:3000],
            dang_qian_kuang_jia=self.kuangjia,
        )
        try:
            jieguo = self.llm.chat([{"role":"user","content":bao.to_json()}], wendu=0.3, zuidazifu=500)
            xin_kuangjia = {}
            for line in jieguo.strip().split('\n'):
                for jian, yingse in [("身份叙事：","shenfen"),("目标叙事：","mubiao"),("原则叙事：","yuanze"),("行为叙事：","xingwei")]:
                    if line.startswith(jian):
                        xin_kuangjia[yingse] = line.replace(jian, "").strip()
            if len(xin_kuangjia) == 4:
                return xin_kuangjia
        except Exception:
            pass
        return None

    def _baocun_xushi(self):
        try:
            neirong = f"""## 身份叙事
{self.kuangjia.get('shenfen','')}

## 目标叙事
{self.kuangjia.get('mubiao','')}

## 原则叙事
{self.kuangjia.get('yuanze','')}

## 行为叙事
{self.kuangjia.get('xingwei','')}
"""
            self.xushi_md.write_text(neirong, encoding='utf-8')
        except Exception as e:
            print(f"[脾] 叙事框架保存失败: {e}")

    def _baocun_xushi_yanhua(self, jiu_kuangjia: dict, xin_kuangjia: dict, zizhuan_zhaiyao: str):
        try:
            lishi = []
            if self.xushi_yanhua_json.exists():
                try:
                    lishi = json.loads(self.xushi_yanhua_json.read_text(encoding='utf-8'))
                except Exception:
                    pass
            lishi.append({
                "shijian": datetime.now().isoformat(),
                "jiu_shenfen": jiu_kuangjia.get('shenfen','')[:100],
                "xin_shenfen": xin_kuangjia.get('shenfen','')[:100],
                "jiu_mubiao": jiu_kuangjia.get('mubiao','')[:100],
                "xin_mubiao": xin_kuangjia.get('mubiao','')[:100],
                "jiu_yuanze": jiu_kuangjia.get('yuanze','')[:100],
                "xin_yuanze": xin_kuangjia.get('yuanze','')[:100],
                "zizhuan_zhaiyao": zizhuan_zhaiyao[:200]
            })
            if len(lishi) > 50:
                lishi = lishi[-50:]
            self.xushi_yanhua_json.write_text(
                json.dumps(lishi, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"[脾] 叙事演化记录失败: {e}")

    def _saomiao_armory(self):
        self.gongju_zhuche = {}
        # 兼容 xingchao_code: 工具可能在 armory/ 或 tools/
        mulu_list = [self.armory_mulu]
        tools_mulu = self.xiangmu_mulu / "tools"
        if tools_mulu.exists() and tools_mulu != self.armory_mulu:
            mulu_list.append(tools_mulu)
        for mulu in mulu_list:
            if not mulu.exists(): continue
            for py in mulu.rglob("*.py"):
                if py.name == "__init__.py": continue
                # 过滤: 跳过测试/开发子目录
                if any(p in py.parts for p in ["ceshi", "kaifa"]): continue
                try:
                    daima = py.read_text(encoding='utf-8')
                    # AST 校验: 跳过非合法 Python (如 JSON 伪装的 .py)
                    try: ast.parse(daima)
                    except: continue
                    doc = ""
                    if '"""' in daima: doc = daima.split('"""')[1].strip().split('\n')[0]
                    # 键名: 子目录文件用 subdir_stem 避免冲突
                    rel = py.relative_to(mulu)
                    if len(rel.parts) > 1:
                        key = rel.parts[0] + "_" + py.stem
                    else:
                        key = py.stem
                    self.gongju_zhuche[key] = {"lujing":str(py),"miaoshu":doc or py.stem}
                    old_quality = self.tool_mgr.zhu_ce.get(key, {}).get("quality", 0.5)
                    self.tool_mgr.zhu_ce_gongju(key, str(py), doc or py.stem, quality=old_quality)
                except Exception: pass
        for ming in CANGJIANGE_HANSHU:
            if ming in self.gongju_zhuche:
                CANGJIANGE_HANSHU[ming]["lujing"] = self.gongju_zhuche[ming]["lujing"]
            else:
                # 子目录工具: 可能用 key="subdir_stem" 而非 "stem"
                for key, info in self.gongju_zhuche.items():
                    if key.endswith("_" + ming):
                        CANGJIANGE_HANSHU[ming]["lujing"] = info["lujing"]
                        break
        self._shengcheng_guanjianci()
        self._gengxin_gongju_zhiliang()

    def _gengxin_gongju_zhiliang(self):
        """从经络记忆读取工具调用统计 → 更新ToolManager质量评分"""
        try:
            if self.meridian and hasattr(self.meridian, 'jiyi') and self.meridian.jiyi:
                for name in self.tool_mgr.zhu_ce:
                    stats = self.meridian.jiyi.gongju_xiaoneng(name)
                    if stats and stats.get("zongshu", 0) > 0:
                        success = stats.get("chenggong", 0)
                        total = stats["zongshu"]
                        quality = round(success / max(total, 1) * min(1.0, total / 10), 3)
                        self.tool_mgr.zhu_ce[name]["quality"] = max(
                            self.tool_mgr.zhu_ce[name].get("quality", 0), quality)
                        self.tool_mgr.zhu_ce[name]["calls"] = total
                        self.tool_mgr.zhu_ce[name]["success"] = success
        except Exception: pass

    def _shengcheng_guanjianci(self):
        """从注册工具的文档字符串自动生成关键词映射"""
        self.zidong_ci = {}  # {关键词: (gongju_ming, hanshu_ming)}
        for gm, info in self.gongju_zhuche.items():
            # 过滤测试文件
            if gm.startswith("ceshi_") or gm in ("quanliang_ceshi","fuzhiti_menjin"):
                continue
            miaoshu = info.get("miaoshu", gm)
            # 工具名拆词
            parts = gm.replace("_"," ").split()
            for p in parts:
                if len(p) >= 2: self.zidong_ci[p] = (gm, None)
            # 描述拆词
            for word in miaoshu.replace("·"," ").replace("："," ").replace("/"," ").split():
                word = word.strip("{}")
                if len(word) >= 2 and word not in self.zidong_ci:
                    self.zidong_ci[word] = (gm, None)
        # 为每个工具找最可能的函数名
        import ast as _ast
        for gm, info in self.gongju_zhuche.items():
            if gm.startswith("ceshi_") or gm in ("quanliang_ceshi","fuzhiti_menjin"):
                continue
            try:
                with open(info["lujing"], encoding='utf-8') as f:
                    code = f.read()
                tree = _ast.parse(code)
                funcs = [n.name for n in _ast.walk(tree) if isinstance(n, _ast.FunctionDef) and not n.name.startswith("_")]
                if funcs:
                    self.zidong_ci[gm] = (gm, funcs[0])  # 工具名 → 第一个公开函数
            except Exception as e:
                try:
                    if self.meridian and hasattr(self.meridian, 'rizhi'):
                        self.meridian.rizhi.wenti_rizhi(self.juese, {"miaoshu": f"工具扫描异常{info.get('lujing','')}:{e}", "leixing": "saomiao_error"})
                except Exception: pass

    def _jiazai_kuangjia(self):
        if self.xushi_md.exists():
            try:
                neirong = self.xushi_md.read_text(encoding='utf-8')
                kj = {}
                for bt, j in {"身份叙事":"shenfen","目标叙事":"mubiao","原则叙事":"yuanze","行为叙事":"xingwei"}.items():
                    p = re.search(rf"##\s*{bt}\s*\n(.*?)(?=\n##|$)", neirong, re.DOTALL)
                    if p: kj[j] = p.group(1).strip()
                if len(kj) == 4: return kj
            except Exception: pass
        return {"shenfen":"五境认知引擎，基于中医认知模型的通用问题解决系统","mubiao":"服务使用者","yuanze":"零外部依赖、可回滚、可追溯、十二遍验证","xingwei":"五境流转结果"}

    def qu_zouzhai(self):
        """取走债: 返回脾(工具)相关的未解决问题"""
        zhai = []
        try:
            if self.wangluo:
                for tid in ["bianchengti","yunxingti"]:
                    for w in self.wangluo.qu_wenti_liebiao(tid):
                        ms = str(w.get("miaoshu",""))[:100]
                        if any(kw in ms for kw in ["工具","匹配","锻造","权限","pipei","duanzao","gongju"]):
                            zhai.append(f"[脾-工具债|{tid}] {ms}")
            if hasattr(self, '_pipei_shibai_cishu') and self._pipei_shibai_cishu > 10:
                zhai.append(f"[脾-匹配债] 连续匹配失败{self._pipei_shibai_cishu}次, 建议扩充技能库")
        except Exception: pass
        return zhai

    def tingzhi(self):
        self._yunxing = False