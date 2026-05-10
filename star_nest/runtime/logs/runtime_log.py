"""
运行日志 V2.0  [星巢·经络闭环·级别+轮转]
DEBUG/INFO/WARN/ERROR 四级 · 7天自动清理 · 文本+SQLite双写
纯标准库·零外部依赖
"""
import threading, time, json, sqlite3, re, os
from pathlib import Path
from datetime import datetime, timedelta

LV = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3}

class YunXingRiZhi:
    def __init__(self, cunchu_mulu):
        self.mulu = Path(cunchu_mulu)
        self.mulu.mkdir(parents=True, exist_ok=True)
        self.suo = threading.Lock()
        self.changqi_db = self.mulu.parent / "shared_memory" / "changqi_jiyi.db"
        self.min_level = LV["INFO"]  # 最低记录级别
        self._querenshu_ju_ku()
        self._qingli_jiu_rizhi()

    def _querenshu_ju_ku(self):
        try:
            conn = sqlite3.connect(str(self.changqi_db))
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chengzhang_rizhi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shijian TEXT,
                    leixing TEXT,
                    miaoshu TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception:
            pass

    def _xie_rizhi(self, leixing, miaoshu, level="INFO"):
        if LV.get(level, 1) < self.min_level:
            return
        shijian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.suo:
            try:
                riqi = datetime.now().strftime("%Y%m%d")
                fp = self.mulu / f"yuxing_{riqi}.log"
                import codecs
                with codecs.open(str(fp), 'a', encoding='utf-8') as lf:
                    lf.write(f"[{shijian}] [{level}] [{leixing}] {miaoshu}\n")
            except Exception:
                pass
            try:
                conn = sqlite3.connect(str(self.changqi_db))
                conn.execute(
                    "INSERT INTO chengzhang_rizhi (shijian, leixing, miaoshu) VALUES (?,?,?)",
                    (shijian, f"{level}:{leixing}", miaoshu[:1000])
                )
                conn.commit()
                conn.close()
            except Exception:
                pass

    def _qingli_jiu_rizhi(self):
        """清理7天前的日志文件"""
        try:
            cutoff = datetime.now() - timedelta(days=7)
            for f in self.mulu.glob("yuxing_*.log"):
                try:
                    riqi_str = f.stem.replace("yuxing_", "")
                    if len(riqi_str) == 8:
                        fd = datetime.strptime(riqi_str, "%Y%m%d")
                        if fd < cutoff:
                            f.unlink()
                except: pass
        except: pass

    def huxi_rizhi(self, xiaoxi, xiangying, jiemian=""):
        mx = xiaoxi[:100].replace('\n', ' ')
        xy = (xiangying or "")[:100].replace('\n', ' ')
        jm = jiemian or "CLI"
        miaoshu = f"{jm}|Q:{mx}|A:{xy}"
        self._xie_rizhi("呼吸", miaoshu)

    def wenti_rizhi(self, tid, wenti):
        ms = wenti.get("miaoshu", wenti.get("error", str(wenti)[:80]))
        ms = ms[:200].replace('\n', ' ')
        miaoshu = f"{tid}|{ms}"
        self._xie_rizhi("问题", miaoshu)

    def jiandu_rizhi(self, mingcheng, xiangqing=""):
        miaoshu = f"{mingcheng}|{xiangqing[:150]}"
        self._xie_rizhi("监督", miaoshu)

    def zhoudian_zhenduan(self, bajizhuangtai):
        miaoshu = json.dumps(bajizhuangtai, ensure_ascii=False)[:300]
        self._xie_rizhi("诊断", miaoshu)

    def baocun_meridian(self, wenti_shu, xiufu_shu):
        miaoshu = f"meridian|wenti:{wenti_shu}|xiufu:{xiufu_shu}"
        self._xie_rizhi("经络", miaoshu)

    def jieguo(self, zuiduo=20):
        jieguo = []
        today = datetime.now().strftime("%Y%m%d")
        fp = self.mulu / f"yuxing_{today}.log"
        if fp.exists():
            try:
                lines = fp.read_text(encoding='utf-8').strip().split('\n')
                jieguo = lines[-zuiduo:]
            except Exception:
                pass
        return jieguo

    def rizhi_tongji(self):
        tj = {"wenti": 0, "huxi": 0, "zongshu": 0}
        try:
            conn = sqlite3.connect(str(self.changqi_db))
            for r in conn.execute("SELECT leixing, COUNT(*) FROM chengzhang_rizhi GROUP BY leixing").fetchall():
                lt, cnt = r
                if lt == "问题": tj["wenti"] = cnt
                elif lt == "呼吸": tj["huxi"] = cnt
                tj["zongshu"] += cnt
            conn.close()
        except Exception:
            pass
        return tj

    def saomiao_rizhi(self, riqi=None):
        """扫描指定日期的日志文件"""
        if not riqi:
            riqi = datetime.now().strftime("%Y%m%d")
        fp = self.mulu / f"yuxing_{riqi}.log"
        if not fp.exists():
            return []
        try:
            return [l.rstrip('\n') for l in fp.read_text(encoding='utf-8').split('\n') if l.strip()]
        except Exception:
            return []
