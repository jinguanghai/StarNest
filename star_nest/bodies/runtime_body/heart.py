from star_nest.organs.heart import XinZang
from star_nest.organs.liver import GanZang
from star_nest.organs.spleen import PiZang
from star_nest.organs.lungs import FeiZang
from star_nest.organs.kidneys import ShenZang
from star_nest.introspection import ZiJingShi
import time

class YunXingTi:
    def __init__(self, meridian, llm, zhujianlu, baji, jiyiguanli, peizhi):
        yxt = 'yunxingti'
        self.xin = XinZang(meridian, llm, zhujianlu, baji, jiyiguanli, peizhi, juese=yxt)
        self.gan = GanZang(meridian, jiyiguanli, peizhi, juese=yxt)
        self.pi = PiZang(meridian, zhujianlu, llm, jiyiguanli, peizhi, juese=yxt)
        self.fei = FeiZang(meridian, llm, peizhi, juese=yxt)
        self.shen = ShenZang(meridian, llm, baji, peizhi, juese=yxt)
        self.xin.jieru_qiguan(self.gan, self.pi, self.fei, self.shen)
        self.pi.xin = self.xin
        self.zijingshi = ZiJingShi()
    def start_all(self):
        self.xin.start(); time.sleep(1.5)
        self.gan.start(); time.sleep(0.5)
        self.pi.start(); time.sleep(0.5)
        self.fei.start(); time.sleep(0.5)
        self.shen.start()
    def tingzhi(self):
        self.xin.tingzhi(); self.gan.tingzhi(); self.pi.tingzhi(); self.fei.tingzhi(); self.shen.tingzhi()
