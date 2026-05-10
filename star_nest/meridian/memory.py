"""
经络记忆 V1.0  [星巢·经络闭环]
八极时序·问题窗·修复窗·五境流转·工具效能
独立SQLite数据库 meridian_jiyi.db
纯标准库·零外部依赖
"""
import sqlite3, time, threading
from pathlib import Path
from datetime import datetime


class JingLuoJiYi:
    def __init__(self, meridian_mulu):
        self.mulu = Path(meridian_mulu)
        self.mulu.mkdir(parents=True, exist_ok=True)
        self.db_lujing = self.mulu / "meridian_jiyi.db"
        self.suo = threading.Lock()
        self._chuangjian_biao()

    def _chuangjian_biao(self):
        with self.suo:
            conn = sqlite3.connect(str(self.db_lujing))
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS baji_shixu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shijian TEXT NOT NULL,
                    juese TEXT,
                    yang REAL, yin REAL, biao REAL, li REAL,
                    han REAL, re REAL, xu REAL, shi REAL,
                    jiankangdu REAL,
                    wenti_shu INTEGER, xiufu_shu INTEGER
                );
                CREATE TABLE IF NOT EXISTS wenti_chuangkou (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shijian TEXT NOT NULL,
                    laiyuan_ti TEXT,
                    miaoshu TEXT,
                    leixing TEXT,
                    yanzhongdu INTEGER DEFAULT 1,
                    guanlian_xiufu_id INTEGER
                );
                CREATE TABLE IF NOT EXISTS xiufu_chuangkou (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shijian TEXT NOT NULL,
                    execution_ti TEXT,
                    guanlian_wenti_id INTEGER,
                    jieguo TEXT,
                    haoshi REAL,
                    miaoshu TEXT
                );
                CREATE TABLE IF NOT EXISTS protocols_guodu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shijian TEXT NOT NULL,
                    yuan_jing TEXT,
                    mubiao_jing TEXT,
                    chufa_yuanyin TEXT,
                    liuzhuan_shendu INTEGER DEFAULT 1,
                    chixu_haomiao INTEGER
                );
                CREATE TABLE IF NOT EXISTS gongju_diaoyong (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shijian TEXT NOT NULL,
                    gongju_ming TEXT,
                    hanshu_ming TEXT,
                    pipei_ceng INTEGER,
                    chenggong INTEGER DEFAULT 0,
                    haoshi REAL
                );
            """)
            conn.commit()
            conn.close()

    # ===== 写入接口 =====

    def jilu_baji(self, juese, bajizhuangtai):
        z = bajizhuangtai
        sl = z.get("shiliang", {})
        with self.suo:
            try:
                conn = sqlite3.connect(str(self.db_lujing))
                conn.execute(
                    "INSERT INTO baji_shixu (shijian,juese,yang,yin,biao,li,han,re,xu,shi,jiankangdu,wenti_shu,xiufu_shu) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (datetime.now().isoformat(), juese,
                     sl.get("yang",0), sl.get("yin",0), sl.get("biao",0), sl.get("li",0),
                     sl.get("han",0), sl.get("re",0), sl.get("xu",0), sl.get("shi",0),
                     z.get("jiankangdu",0), z.get("wenti_shu",0), z.get("xiufu_shu",0))
                )
                conn.commit(); conn.close()
            except: pass

    def jilu_wenti(self, tid, wenti):
        ms = str(wenti.get("miaoshu", str(wenti)[:120]))[:300]
        lt = wenti.get("leixing", wenti.get("laiyuan", "unknown"))
        with self.suo:
            try:
                conn = sqlite3.connect(str(self.db_lujing))
                conn.execute(
                    "INSERT INTO wenti_chuangkou (shijian,laiyuan_ti,miaoshu,leixing,yanzhongdu) VALUES (?,?,?,?,?)",
                    (datetime.now().isoformat(), tid, ms, lt, 1)
                )
                conn.commit(); conn.close()
            except: pass

    def jilu_xiufu(self, tid, xiufu, guanlian_wenti_id=None):
        ms = str(xiufu.get("miaoshu", str(xiufu)[:120]))[:300]
        jg = str(xiufu.get("jieguo", "unknown"))[:20]
        with self.suo:
            try:
                conn = sqlite3.connect(str(self.db_lujing))
                conn.execute(
                    "INSERT INTO xiufu_chuangkou (shijian,execution_ti,guanlian_wenti_id,jieguo,miaoshu) VALUES (?,?,?,?,?)",
                    (datetime.now().isoformat(), tid, guanlian_wenti_id, jg, ms)
                )
                # 关联最近未关联的问题
                if guanlian_wenti_id is None:
                    conn.execute(
                        "UPDATE wenti_chuangkou SET guanlian_xiufu_id=last_insert_rowid() "
                        "WHERE guanlian_xiufu_id IS NULL AND laiyuan_ti=? AND id=(SELECT MAX(id) FROM wenti_chuangkou WHERE laiyuan_ti=?)",
                        (tid, tid)
                    )
                conn.commit(); conn.close()
            except: pass

    def jilu_protocols(self, yuan_jing, mubiao_jing, yuanyin="", liuzhuan_shendu=1):
        with self.suo:
            try:
                conn = sqlite3.connect(str(self.db_lujing))
                conn.execute(
                    "INSERT INTO protocols_guodu (shijian,yuan_jing,mubiao_jing,chufa_yuanyin,liuzhuan_shendu) VALUES (?,?,?,?,?)",
                    (datetime.now().isoformat(), yuan_jing, mubiao_jing, yuanyin[:200], liuzhuan_shendu)
                )
                conn.commit(); conn.close()
            except: pass

    def jilu_gongju(self, gongju_ming, hanshu_ming, pipei_ceng, chenggong=True):
        with self.suo:
            try:
                conn = sqlite3.connect(str(self.db_lujing))
                conn.execute(
                    "INSERT INTO gongju_diaoyong (shijian,gongju_ming,hanshu_ming,pipei_ceng,chenggong) VALUES (?,?,?,?,?)",
                    (datetime.now().isoformat(), gongju_ming, hanshu_ming, pipei_ceng, 1 if chenggong else 0)
                )
                conn.commit(); conn.close()
            except: pass

    # ===== 查询接口 =====

    def _chaxun(self, sql, canshu=(), zuiduo=None):
        try:
            conn = sqlite3.connect(str(self.db_lujing))
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, canshu).fetchall()
            conn.close()
            if zuiduo:
                rows = rows[-zuiduo:]
            return [dict(r) for r in rows]
        except:
            return []

    def zuijin_baji(self, juese=None, n=5):
        if juese:
            return self._chaxun("SELECT * FROM baji_shixu WHERE juese=? ORDER BY id DESC LIMIT ?", (juese, n))
        return self._chaxun("SELECT * FROM baji_shixu ORDER BY id DESC LIMIT ?", (n,))

    def zuijin_wenti(self, n=10):
        return self._chaxun("SELECT * FROM wenti_chuangkou ORDER BY id DESC LIMIT ?", (n,))

    def zuijin_xiufu(self, n=5):
        return self._chaxun("SELECT * FROM xiufu_chuangkou ORDER BY id DESC LIMIT ?", (n,))

    def zuijin_protocols(self, n=5):
        return self._chaxun("SELECT * FROM protocols_guodu ORDER BY id DESC LIMIT ?", (n,))

    def zuijin_gongju(self, n=10):
        return self._chaxun("SELECT * FROM gongju_diaoyong ORDER BY id DESC LIMIT ?", (n,))

    def wenti_leixing_tongji(self, n=5):
        return self._chaxun(
            "SELECT leixing, COUNT(*) as cnt FROM wenti_chuangkou GROUP BY leixing ORDER BY cnt DESC LIMIT ?", (n,))

    def gongju_xiaoneng(self):
        return self._chaxun(
            "SELECT gongju_ming, hanshu_ming, COUNT(*) as zongshu, SUM(chenggong) as chenggong_shu "
            "FROM gongju_diaoyong GROUP BY gongju_ming, hanshu_ming ORDER BY zongshu DESC")

    # ===== 认知流显化 (五境) =====

    def meridian_shangxiawen(self, cengji="正境"):
        """核心: 按境返回LLM上下文字段"""
        shangxiawen = {"cengji": cengji}

        if cengji == "正境":
            return self.xianshi_zhengjing()

        if cengji == "反境":
            return self.xianshi_fanjing()

        if cengji == "合境":
            return self.xianshi_hejing()

        if cengji == "超越境":
            return self.xianshi_chaoyuejing()

        # 本源境及其他
        return self.xianshi_benyuanjing()

    def xianshi_zhengjing(self):
        """正境显化: 当前运行事实快照"""
        jg = {"jing": "正境", "jieshi": "当前运行状态快照"}
        try:
            # 最新八极
            baji = self.zuijin_baji(n=1)
            if baji:
                b = baji[0]
                jg["dangqian_baji"] = {
                    "yang": b.get("yang"), "yin": b.get("yin"),
                    "jiankangdu": b.get("jiankangdu"),
                    "wenti_shu": b.get("wenti_shu"), "xiufu_shu": b.get("xiufu_shu")
                }
            # 活跃问题数
            wenti = self._chaxun("SELECT COUNT(*) as cnt FROM wenti_chuangkou")
            jg["huoyue_wenti"] = wenti[0]["cnt"] if wenti else 0
            # 最近工具调用
            gj = self._chaxun(
                "SELECT COUNT(*) as cnt FROM gongju_diaoyong WHERE shijian > ?",
                (self._zuijin_xiaoshi(1),))
            jg["zuijin_gongju"] = gj[0]["cnt"] if gj else 0
            # 五境流转次数
            wj = self._chaxun("SELECT COUNT(*) as cnt FROM protocols_guodu")
            jg["protocols_liuzhuan"] = wj[0]["cnt"] if wj else 0
        except:
            pass
        return jg

    def xianshi_fanjing(self):
        """反境显化: 问题趋势·重复模式·修复失败率"""
        jg = {"jing": "反境", "jieshi": "问题趋势与阻碍分析"}
        try:
            # 八极漂移
            baji = self.zuijin_baji(n=10)
            if len(baji) >= 2:
                first = baji[-1]
                last = baji[0]
                jg["baji_piaoyi"] = {
                    "jiankangdu": f"{first.get('jiankangdu',0):.2f}→{last.get('jiankangdu',0):.2f}",
                    "yang": f"{first.get('yang',0):.2f}→{last.get('yang',0):.2f}",
                    "xu": f"{first.get('xu',0):.2f}→{last.get('xu',0):.2f}"
                }
            # 问题类型统计
            wenti_tj = self.wenti_leixing_tongji(5)
            if wenti_tj:
                jg["wenti_leixing"] = [(w["leixing"], w["cnt"]) for w in wenti_tj]
            # 重复模式: 相同描述出现>1次
            chongfu = self._chaxun(
                "SELECT miaoshu, COUNT(*) as cnt FROM wenti_chuangkou GROUP BY miaoshu HAVING cnt>1 ORDER BY cnt DESC LIMIT 3")
            if chongfu:
                jg["chongfu_wenti"] = [(c["miaoshu"][:60], c["cnt"]) for c in chongfu]
            # 修复成功率
            zong = self._chaxun("SELECT COUNT(*) as cnt FROM xiufu_chuangkou")
            chenggong = self._chaxun("SELECT COUNT(*) as cnt FROM xiufu_chuangkou WHERE jieguo='success'")
            if zong and zong[0]["cnt"] > 0:
                jg["xiufu_chenggong_lv"] = f"{chenggong[0]['cnt']}/{zong[0]['cnt']} ({100*chenggong[0]['cnt']//zong[0]['cnt']}%)"
            # 未关联修复的活动问题
            weixiufu = self._chaxun(
                "SELECT COUNT(*) as cnt FROM wenti_chuangkou WHERE guanlian_xiufu_id IS NULL")
            jg["weixiufu_wenti"] = weixiufu[0]["cnt"] if weixiufu else 0
        except:
            pass
        return jg

    def xianshi_hejing(self):
        """合境显化: 修复方案·工具推荐·平衡建议"""
        jg = {"jing": "合境", "jieshi": "修复方案与平衡建议"}
        try:
            # 最近修复
            xiufu = self.zuijin_xiufu(5)
            if xiufu:
                jg["zuijin_xiufu"] = [
                    {"shijian": x["shijian"][:16], "jieguo": x["jieguo"], "ti": x["execution_ti"]}
                    for x in xiufu
                ]
            # 最近问题
            wenti = self.zuijin_wenti(5)
            if wenti:
                jg["zuijin_wenti"] = [
                    {"miaoshu": w["miaoshu"][:60], "leixing": w["leixing"]}
                    for w in wenti
                ]
            # 工具效能
            xn = self.gongju_xiaoneng()
            if xn:
                jg["gongju_xiaoneng"] = [
                    {"gongju": x["gongju_ming"], "hanshu": x["hanshu_ming"],
                     "lv": f"{x['chenggong_shu']}/{x['zongshu']}"}
                    for x in xn[:5]
                ]
            # 五境阶段: 最近流转
            wj = self.zuijin_protocols(3)
            if wj:
                jg["zuijin_liuzhuan"] = [
                    f"{w['yuan_jing']}→{w['mubiao_jing']}" for w in wj
                ]
        except:
            pass
        return jg

    def xianshi_chaoyuejing(self):
        """超越境显化: 跨域突破·创新模式"""
        jg = {"jing": "超越境", "jieshi": "跨域突破与创新可能"}
        try:
            # 跨域流转
            kuayu = self._chaxun(
                "SELECT yuan_jing, mubiao_jing, COUNT(*) as cnt FROM protocols_guodu "
                "WHERE yuan_jing != mubiao_jing GROUP BY yuan_jing, mubiao_jing ORDER BY cnt DESC")
            if kuayu:
                jg["kuayu_liuzhuan"] = [
                    f"{k['yuan_jing']}→{k['mubiao_jing']} ({k['cnt']}次)" for k in kuayu[:5]
                ]
            # 工具创新模式: 高成功率
            xn = self._chaxun(
                "SELECT gongju_ming, hanshu_ming, COUNT(*) as zs, SUM(chenggong) as cs "
                "FROM gongju_diaoyong GROUP BY gongju_ming, hanshu_ming "
                "HAVING zs>=2 AND cs*1.0/zs>=0.8 ORDER BY cs DESC LIMIT 3")
            if xn:
                jg["gao_xiao_gongju"] = [
                    f"{x['gongju_ming']}.{x['hanshu_ming']}" for x in xn
                ]
            # 八极极限探测
            baji = self._chaxun(
                "SELECT MAX(yang) as max_yang, MIN(jiankangdu) as min_jk FROM baji_shixu")
            if baji and baji[0].get("min_jk"):
                jg["jixian"] = {
                    "zuidi_jiankangdu": f"{baji[0]['min_jk']:.2f}",
                    "zuigao_yang": f"{baji[0].get('max_yang', 0):.2f}"
                }
        except:
            pass
        return jg

    def xianshi_benyuanjing(self):
        """本源境显化: 长期规律·归档总结"""
        jg = {"jing": "本源境", "jieshi": "长期规律与归档总结"}
        try:
            # 总览
            zong = {}
            for biao, name in [
                ("baji_shixu", "八极记录"), ("wenti_chuangkou", "问题"),
                ("xiufu_chuangkou", "修复"), ("protocols_guodu", "五境流转"),
                ("gongju_diaoyong", "工具调用")
            ]:
                r = self._chaxun(f"SELECT COUNT(*) as cnt FROM {biao}")
                zong[name] = r[0]["cnt"] if r else 0
            jg["zonglan"] = zong
            # 行为规律: 最活跃的问题来源
            laiyuan = self._chaxun(
                "SELECT laiyuan_ti, COUNT(*) as cnt FROM wenti_chuangkou GROUP BY laiyuan_ti ORDER BY cnt DESC")
            if laiyuan:
                jg["huoyue_laiyuan"] = [(l["laiyuan_ti"], l["cnt"]) for l in laiyuan]
            # 长期趋势: 日均八极
            jg["baji_jiyue"] = self._chaxun(
                "SELECT date(shijian) as riqi, AVG(jiankangdu) as avg_jk, COUNT(*) as cnt "
                "FROM baji_shixu GROUP BY date(shijian) ORDER BY riqi DESC LIMIT 7")
        except:
            pass
        return jg

    def _zuijin_xiaoshi(self, n=1):
        from datetime import timedelta
        return (datetime.now() - timedelta(hours=n)).isoformat()

    def tongji_zonglan(self):
        z = {}
        try:
            for biao in ["baji_shixu", "wenti_chuangkou", "xiufu_chuangkou", "protocols_guodu", "gongju_diaoyong"]:
                r = self._chaxun(f"SELECT COUNT(*) as cnt FROM {biao}")
                z[biao] = r[0]["cnt"] if r else 0
        except:
            pass
        return z
