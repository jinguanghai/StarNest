from .celestial_command import ZhongDuan, YanSe
import time

class SanTiJieMian:
    def __init__(self, santizdd):
        self.santizdd = santizdd
        self.zhongduan = ZhongDuan()
        self._qianci_wenti = 0
        self._qianci_xiufu = 0
        self._qianci_tongzhi = 0
        self._moshi = "yunxingti"

    def yunxing(self):
        self.zhongduan.qingping()
        self.zhongduan.fen_ge_xian()
        self.zhongduan.shuchu("星巢·三体自迭代 V2.0", YanSe.QING)
        self.zhongduan.fen_ge_xian()
        self._moshi = "yunxingti"
        self.zhongduan.shuchu("  经络闭环已启动·运行体就绪(编程体后台待命)", YanSe.MU_LV)
        self.zhongduan.fen_ge_xian()
        self._xianshi_zhuangtai()
        self._xunhuan_shuru()

    def _xianshi_zhuangtai(self):
        zt = self.santizdd.meridian.zhuangtai_zhaiyao()
        parts = []
        for tid, label, ys in [("yunxingti","运行体",YanSe.MU_LV), ("bianchengti","编程体",YanSe.HUO_CHI), ("fuzhiti","复制体",YanSe.JIN_BAI)]:
            z = zt.get(tid, {})
            prefix = ">>" if self._moshi == tid else "  "
            parts.append(f"{ys}{prefix}{label}{YanSe.FUWEI}:问题{z.get('wenti_shu',0)} 修复{z.get('xiufu_shu',0)}")
        self.zhongduan.zangqi_zhuangtai({"三体": "O"})
        self.zhongduan.shuchu("  " + " | ".join(parts))
        try:
            tj = self.santizdd.jiyiguanli.zhishi_tongji()
            arms = len(self.santizdd.yunxingti.pi.gongju_zhuche)
            self.zhongduan.shuchu_wenli(f"  记忆{tj.get('zongshu',0)}条 兵器{arms}件")
        except Exception:
            self.zhongduan.shuchu_wenli(f"  记忆: {self._moshi}模式")

    def _xunhuan_shuru(self):
        self.zhongduan.tishifu()
        while True:
            try:
                cmd = input().strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not cmd:
                self._jiancha_bianhua()
                self.zhongduan.tishifu()
                continue
            if cmd.lower() in ("exit", "退出"):
                break
            if cmd in ("status", "状态"):
                self._xianshi_zhuangtai()
                self.zhongduan.tishifu()
                continue
            if cmd in ("jiyi", "记忆"):
                try:
                    tj = self.santizdd.jiyiguanli.zhishi_tongji()
                    self.zhongduan.shuchu(f"长期记忆{tj.get('zongshu',0)}条 技能锚点{tj.get('jineng_shu',0)}条", YanSe.QING)
                except Exception:
                    self.zhongduan.shuchu("记忆系统正常", YanSe.QING)
                self.zhongduan.tishifu()
                continue
            # 需求驱动
            active = self.santizdd.bianchengti if self._moshi == "bianchengti" else self.santizdd.yunxingti
            if cmd.startswith("需求:") or cmd.startswith("需求："):
                xuqiu = cmd[3:].strip()
                active.xin.add_xuqiu(xuqiu)
                self.zhongduan.shuchu(f"[需求] {xuqiu[:60]} -> 已提交", YanSe.QING)
            else:
                active.xin.add_xuqiu(cmd)
                self.zhongduan.shuchu(f"[需求] {cmd[:60]}", YanSe.QING)
                # 等待回复
                self._dengdai_huifu()
            self.zhongduan.tishifu()

    def _dengdai_huifu(self):
        # 优先读当前模式的输出队列，再读另一个
        queues = [
            (self.santizdd.bianchengti.xin.shuchu_duilie, "编程体", YanSe.HUO_CHI),
            (self.santizdd.yunxingti.xin.shuchu_duilie, "运行体", YanSe.MU_LV),
        ] if self._moshi == "bianchengti" else [
            (self.santizdd.yunxingti.xin.shuchu_duilie, "运行体", YanSe.MU_LV),
            (self.santizdd.bianchengti.xin.shuchu_duilie, "编程体", YanSe.HUO_CHI),
        ]
        for _ in range(30):
            for q, label, ys in queues:
                try:
                    msg = q.get_nowait()
                    if msg:
                        self.zhongduan.shuchu(f"[{label}] {str(msg)[:500]}", ys)
                        return
                except Exception:
                    pass
            time.sleep(1)

    def _jiancha_bianhua(self):
        try:
            zt = self.santizdd.meridian.zhuangtai_zhaiyao()
            wt = sum(zt.get(t, {}).get("wenti_shu", 0) for t in zt)
            xf = sum(zt.get(t, {}).get("xiufu_shu", 0) for t in zt)
            now = time.time()
            if wt != self._qianci_wenti and (now - self._qianci_tongzhi > 30):
                self.zhongduan.shuchu_wenli(f"  三体问题{wt} 修复{xf}")
                self._qianci_wenti = wt
                self._qianci_xiufu = xf
                self._qianci_tongzhi = now
        except Exception:
            pass
