"""
气血循环泵 V1.0  [星巢·经络·五脏·统一模型]
五条经络通道·气转血(认知→数据)·血转气(数据→认知)·阻塞检测
纯Python stdlib·零外部依赖
"""
import json, time, threading
from pathlib import Path
from datetime import datetime


class QiXueXunHuan:
    def __init__(self, meridian, meridianjiyi, xin_can_zhao=None):
        self.meridian = meridian
        self.jiyi = meridianjiyi
        self.xin = xin_can_zhao
        self.suo = threading.Lock()
        self.puxi_dir = Path(__file__).parent.parent / 'shared_memory' / 'puxi'
        self.tongdao = self._chu_jian_tong_dao()
        self._xunhuan_jishu = 0
        self.zuse_liebiao = []
        self._rizhi = None  # 由注入点设, 用于异常日志

    def _log(self, msg):
        try:
            if self._rizhi: self._rizhi.wenti_rizhi("qixue", {"miaoshu": msg, "leixing": "qixue_error"})
        except Exception: pass

    def _chu_jian_tong_dao(self):
        """创建五条经络通道"""
        td = {}
        for ming, px, jieshi in [
            ("任脉", 0, "正境·八极快照入血·知识回养感知"),
            ("督脉", 6, "反境·问题编码入血·漂移触发告警"),
            ("冲脉", 5, "合境·工具结果入血·效能回养推荐"),
            ("带脉", 7, "超越·创新编码入血·跨域回养启发"),
            ("跷脉", -1, "本源·全归档入血·反哺下一轮正境"),
        ]:
            td[ming] = {
                "weizhi": px,
                "jieshi": jieshi,
                "zuihou_xunhuan": None,
                "xunhuan_zongshu": 0,
                "zuse_zhuangtai": "通畅",
                "zuse_yuzhi": 1800 if ming == "跷脉" else 60,
            }
        return td

    # ===== 气→血 (认知写入数据) =====

    def qizhuanxue_renmai(self, cengji, ctx):
        """任脉: 正境感知→puxi位点0 + gan.jilu"""
        td = self.tongdao["任脉"]
        try:
            # 八极快照打包
            baji = self.jiyi.zuijin_baji(n=1)
            kuaizhao = {
                "biaoti": f"正境感知·{datetime.now().strftime('%H%M')}",
                "lingyu": "认知快照",
                "yao_dian": [
                    f"境:{cengji}",
                    f"八极:{baji[0].get('jiankangdu',0) if baji else 'NA'}",
                    f"ctx:{str(ctx)[:80]}"
                ],
                "chuangjian_shijian": datetime.now().isoformat(),
                "quanzhong": 0.7,
                "laiyuan": "renmai"
            }
            self._xie_puxi(0, kuaizhao)
            # 肝·jilu
            if self.xin and hasattr(self.xin, 'gan') and self.xin.gan:
                try: self.xin.gan.jilu("感知快照", {"cengji": cengji, "ctx": str(ctx)[:50]})
                except Exception: pass
            td["xunhuan_zongshu"] += 1
            td["zuihou_xunhuan"] = datetime.now().isoformat()
        except Exception: pass

    def qizhuanxue_dumai(self, cengji, ctx):
        """督脉: 反境问题→puxi位点6 + 严重度升级"""
        td = self.tongdao["督脉"]
        try:
            wenti_tj = self.jiyi.wenti_leixing_tongji(3)
            chongfu = any(t.get("cnt", 0) >= 3 for t in wenti_tj if isinstance(t, dict))
            if chongfu:
                kuaizhao = {
                    "biaoti": f"重复问题模式·{datetime.now().strftime('%H%M')}",
                    "lingyu": "问题模式",
                    "yao_dian": [f"{t.get('leixing','?')}×{t.get('cnt',0)}"
                                 for t in wenti_tj[:3] if isinstance(t, dict)],
                    "chuangjian_shijian": datetime.now().isoformat(),
                    "quanzhong": 0.9,
                    "laiyuan": "dumai"
                }
                self._xie_puxi(6, kuaizhao)
            # 肾·jilu 异常
            baji = self.jiyi.zuijin_baji(n=5)
            if len(baji) >= 2:
                jk0 = baji[-1].get("jiankangdu", 1)
                jk1 = baji[0].get("jiankangdu", 1)
                if jk1 < jk0 - 0.1:
                    if self.xin and hasattr(self.xin, 'shen') and self.xin.shen:
                        try: self.xin.shen.jilu("健康下降", {"from": jk0, "to": jk1})
                        except Exception: pass
            td["xunhuan_zongshu"] += 1
            td["zuihou_xunhuan"] = datetime.now().isoformat()
        except Exception: pass

    def qizhuanxue_chongmai(self, cengji, ctx):
        """冲脉: 合境方案结果→puxi位点5 + 脾·gongju_zhuche更新"""
        td = self.tongdao["冲脉"]
        try:
            xn = self.jiyi.gongju_xiaoneng()
            high_eff = [x for x in xn if x.get("zongshu", 0) >= 2 and
                        x.get("chenggong_shu", 0) / max(x.get("zongshu", 1), 1) >= 0.8]
            if high_eff:
                kuaizhao = {
                    "biaoti": f"高效工具·{datetime.now().strftime('%H%M')}",
                    "lingyu": "工具效能",
                    "yao_dian": [f"{x['gongju_ming']}.{x['hanshu_ming']}: {x['chenggong_shu']}/{x['zongshu']}"
                                 for x in high_eff[:3]],
                    "chuangjian_shijian": datetime.now().isoformat(),
                    "quanzhong": 0.8,
                    "laiyuan": "chongmai"
                }
                self._xie_puxi(5, kuaizhao)
            # 脾·更新效能
            if self.xin and hasattr(self.xin, 'pi') and self.xin.pi:
                for x in high_eff[:3]:
                    gn = x.get("gongju_ming", "")
                    if gn in getattr(self.xin.pi, 'gongju_zhuche', {}):
                        self.xin.pi.gongju_zhuche[gn]["xiaoneng"] = {
                            "lv": f"{x['chenggong_shu']}/{x['zongshu']}"}
            td["xunhuan_zongshu"] += 1
            td["zuihou_xunhuan"] = datetime.now().isoformat()
        except Exception: pass

    def qizhuanxue_daimai(self, cengji, ctx):
        """带脉: 超越创新→puxi位点7 + 肺·审查更新"""
        td = self.tongdao["带脉"]
        try:
            wj = self.jiyi.zuijin_protocols(3)
            kuayu = any(w.get("yuan_jing") != w.get("mubiao_jing") for w in wj)
            if kuayu:
                kuaizhao = {
                    "biaoti": f"跨域流转·{datetime.now().strftime('%H%M')}",
                    "lingyu": "认知突破",
                    "yao_dian": [f"{w['yuan_jing']}→{w['mubiao_jing']}" for w in wj[:3] if w.get('yuan_jing') != w.get('mubiao_jing')],
                    "chuangjian_shijian": datetime.now().isoformat(),
                    "quanzhong": 0.6,
                    "laiyuan": "daimai"
                }
                self._xie_puxi(7, kuaizhao)
            td["xunhuan_zongshu"] += 1
            td["zuihou_xunhuan"] = datetime.now().isoformat()
        except Exception: pass

    def qizhuanxue_qiaomai(self, cengji, ctx):
        """跷脉: 本源归档→puxi位点0-9 + 肾+肝归档"""
        td = self.tongdao["跷脉"]
        try:
            zl = self.jiyi.tongji_zonglan()
            kuaizhao = {
                "biaoti": f"经络归档·{datetime.now().strftime('%m%d_%H%M')}",
                "lingyu": "本源归档",
                "yao_dian": [f"{k}:{v}" for k, v in zl.items()],
                "chuangjian_shijian": datetime.now().isoformat(),
                "quanzhong": 1.0,
                "laiyuan": "qiaomai"
            }
            # 写入位点0和9 (始与终)
            self._xie_puxi(0, kuaizhao)
            self._xie_puxi(9, kuaizhao)
            # 肾·归档
            if self.xin and hasattr(self.xin, 'shen') and self.xin.shen:
                try: self.xin.shen.jilu("本源归档", zl)
                except Exception: pass
            # 肝·归档
            if self.xin and hasattr(self.xin, 'gan') and self.xin.gan:
                try: self.xin.gan.jilu("全流转", {"cengji": cengji, "zonglan": str(zl)[:200]})
                except Exception: pass
            td["xunhuan_zongshu"] += 1
            td["zuihou_xunhuan"] = datetime.now().isoformat()
        except Exception: pass

    def _xie_puxi(self, weizhi, entry):
        """写入puxi位点文件"""
        try:
            fp = self.puxi_dir / f"{weizhi}.json"
            if fp.exists():
                data = json.loads(fp.read_text(encoding='utf-8'))
                data.setdefault("zhe_die", []).append(entry)
                fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception: pass

    # ===== 血→气 (数据回流认知) =====

    def xueyangqi_renmai(self, ctx=None):
        """任脉: 八极快照+近期知识→滋养正境感知"""
        jg = {"tongdao": "任脉"}
        try:
            baji = self.jiyi.zuijin_baji(n=1)
            if baji:
                b = baji[0]
                jg["dangqian_jiankangdu"] = b.get("jiankangdu", 0)
                jg["huoyue_wenti"] = b.get("wenti_shu", 0)
            # 近期位点0的知识
            jg["weizhi0_zuijin"] = self._du_puxi_zuijin(0, 3)
        except Exception: pass
        return jg

    def xueyangqi_dumai(self, ctx=None):
        """督脉: 八极漂移+重复问题→触发反境告警"""
        jg = {"tongdao": "督脉"}
        try:
            baji = self.jiyi.zuijin_baji(n=5)
            if len(baji) >= 2:
                jk0 = baji[-1].get("jiankangdu", 1)
                jk1 = baji[0].get("jiankangdu", 1)
                if jk1 < jk0 - 0.15:
                    jg["jing_bao"] = f"健康下降: {jk0:.2f}→{jk1:.2f}"
            wenti_tj = self.jiyi.wenti_leixing_tongji(5)
            jg["wenti_leixing"] = [(t.get("leixing","?"), t.get("cnt",0))
                                   for t in wenti_tj if isinstance(t, dict)]
            jg["weizhi6_zuijin"] = self._du_puxi_zuijin(6, 2)
        except Exception: pass
        return jg

    def xueyangqi_chongmai(self, ctx=None):
        """冲脉: 高效工具+成功修复→合境推荐"""
        jg = {"tongdao": "冲脉"}
        try:
            xn = self.jiyi.gongju_xiaoneng()
            jg["tuijian_gongju"] = [
                f"{x['gongju_ming']}.{x['hanshu_ming']}({x['chenggong_shu']}/{x['zongshu']})"
                for x in xn if x.get("zongshu", 0) >= 1
            ][:3]
            jg["weizhi5_zuijin"] = self._du_puxi_zuijin(5, 2)
        except Exception: pass
        return jg

    def xueyangqi_daimai(self, ctx=None):
        """带脉: 跨域流转→超越启发"""
        jg = {"tongdao": "带脉"}
        try:
            wj = self.jiyi.zuijin_protocols(5)
            jg["zuijin_liuzhuan"] = [f"{w.get('yuan_jing','?')}→{w.get('mubiao_jing','?')}"
                                     for w in wj]
            jg["weizhi7_zuijin"] = self._du_puxi_zuijin(7, 2)
        except Exception: pass
        return jg

    def xueyangqi_qiaomai(self, ctx=None):
        """跷脉: 全量归档→反哺下一轮检索偏置"""
        jg = {"tongdao": "跷脉"}
        try:
            zl = self.jiyi.tongji_zonglan()
            jg["zonglan"] = zl
        except Exception: pass
        return jg

    def _du_puxi_zuijin(self, weizhi, n=3):
        """读puxi位点最近n条"""
        try:
            fp = self.puxi_dir / f"{weizhi}.json"
            if not fp.exists():
                return []
            data = json.loads(fp.read_text(encoding='utf-8'))
            items = data.get("zhe_die", [])[-n:]
            return [{"biaoti": e.get("biaoti", "")[:30], "shijian": e.get("chuangjian_shijian", "")[:16]}
                    for e in items]
        except Exception:
            return []

    # ===== 一次完整气血循环 =====

    def xunhuan_yici(self, cengji="正境", ctx=None):
        """沿五条经络顺序流转: 气→血 + 血→气 + 阻塞检测"""
        self._xunhuan_jishu += 1
        xueyang = {}
        with self.suo:
            for ming in ["任脉", "督脉", "冲脉", "带脉", "跷脉"]:
                td = self.tongdao[ming]
                try:
                    # 1. 血→气 (上行)
                    xyq_fn = getattr(self, f"xueyangqi_{self._ming_to_pinyin(ming)}", None)
                    if xyq_fn:
                        qi = xyq_fn(ctx)
                        xueyang[ming] = qi

                    # 2. 气→血 (下行)
                    qzx_fn = getattr(self, f"qizhuanxue_{self._ming_to_pinyin(ming)}", None)
                    if qzx_fn:
                        qzx_fn(cengji, ctx)

                    # 3. 阻塞检测
                    self._jiance_danyi(ming)
                except Exception: pass

        # 翘脉每30轮归档一次 (避免频繁写入)
        if self._xunhuan_jishu % 30 == 0:
            try: self.qizhuanxue_qiaomai(cengji, ctx)
            except Exception: pass

        return xueyang

    def _ming_to_pinyin(self, ming):
        mp = {"任脉": "renmai", "督脉": "dumai", "冲脉": "chongmai",
              "带脉": "daimai", "跷脉": "qiaomai"}
        return mp.get(ming, ming)

    def _jiance_danyi(self, ming):
        """单条经络阻塞检测"""
        td = self.tongdao[ming]
        now = datetime.now()
        zuihou = td.get("zuihou_xunhuan")
        if zuihou:
            try:
                # 确保有 datetime 类型
                if isinstance(zuihou, str):
                    zuihou = datetime.fromisoformat(zuihou)
                delta = (now - zuihou).total_seconds()
                if delta > td["zuse_yuzhi"]:
                    td["zuse_zhuangtai"] = "阻塞"
                    if ming not in self.zuse_liebiao:
                        self.zuse_liebiao.append(ming)
                else:
                    td["zuse_zhuangtai"] = "通畅"
                    if ming in self.zuse_liebiao:
                        self.zuse_liebiao.remove(ming)
            except Exception: pass
            finally:
                td["zuihou_xunhuan"] = now.isoformat()
        else:
            td["zuihou_xunhuan"] = now.isoformat()
            td["zuse_zhuangtai"] = "初始化"

    def jiance_zuse(self):
        """全局心包络阻塞诊断"""
        jieguo = {"zuse_shu": len(self.zuse_liebiao), "tongdao": {}}
        for ming, td in self.tongdao.items():
            jieguo["tongdao"][ming] = {
                "zhuangtai": td["zuse_zhuangtai"],
                "xunhuan_shu": td["xunhuan_zongshu"],
                "zuihou_xunhuan": td.get("zuihou_xunhuan", "从未")
            }
        # 经络阻塞→自动路由到编程体
        if self.zuse_liebiao and self.meridian:
            try:
                self.meridian.jilu_wenti("yunxingti", {
                    "miaoshu": f"经络阻塞: {','.join(self.zuse_liebiao)}",
                    "leixing": "qixue_zuse",
                    "yanzhongdu": min(5, len(self.zuse_liebiao) * 2)
                })
            except Exception: pass
        return jieguo

    def xueyangqi_quanju(self, cengji="正境"):
        """血养气全集: 按境返回LLM上下文字段"""
        shangxiawen = {"cengji": cengji}
        try:
            # 正境: 任脉数据
            shangxiawen["renmai"] = self.xueyangqi_renmai()
            # 反境+: 督脉数据
            if cengji in ("反境", "合境", "超越境", "本源境"):
                shangxiawen["dumai"] = self.xueyangqi_dumai()
            # 合境+: 冲脉数据
            if cengji in ("合境", "超越境", "本源境"):
                shangxiawen["chongmai"] = self.xueyangqi_chongmai()
            # 超越+: 带脉数据
            if cengji in ("超越境", "本源境"):
                shangxiawen["daimai"] = self.xueyangqi_daimai()
            # 本源: 跷脉数据
            if cengji == "本源境":
                shangxiawen["qiaomai"] = self.xueyangqi_qiaomai()
        except Exception: pass
        return shangxiawen
