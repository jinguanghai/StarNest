from star_nest.organs.heart import XinZang
from star_nest.organs.liver import GanZang
from star_nest.organs.spleen import PiZang
from star_nest.organs.lungs import FeiZang
from star_nest.organs.kidneys import ShenZang
import time

class BianChengTi:
    def __init__(self, meridian, llm, zhujianlu, baji, jiyiguanli, peizhi):
        bct = 'bianchengti'
        self.xin = XinZang(meridian, llm, zhujianlu, baji, jiyiguanli, peizhi, juese=bct)
        self.gan = GanZang(meridian, jiyiguanli, peizhi, juese=bct)
        self.pi = PiZang(meridian, zhujianlu, llm, jiyiguanli, peizhi, juese=bct)
        self.fei = FeiZang(meridian, llm, peizhi, juese=bct)
        self.shen = ShenZang(meridian, llm, baji, peizhi, juese=bct)
        self.xin.jieru_qiguan(self.gan, self.pi, self.fei, self.shen)
        self.pi.xin = self.xin

    def start_all(self):
        self.xin.start(); time.sleep(1.5)
        self.gan.start(); time.sleep(0.5)
        self.pi.start(); time.sleep(0.5)
        self.fei.start(); time.sleep(0.5)
        self.shen.start()
    def tingzhi(self):
        self.xin.tingzhi(); self.gan.tingzhi(); self.pi.tingzhi(); self.fei.tingzhi(); self.shen.tingzhi()
