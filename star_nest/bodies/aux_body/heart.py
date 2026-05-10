from star_nest.organs.heart import XinZang
from star_nest.organs.spleen import PiZang
from star_nest.organs.kidneys import ShenZang
import time

class FuZhiTi:
    def __init__(self, meridian, llm, zhujianlu, baji, jiyiguanli, peizhi):
        fzt = 'fuzhiti'
        self.xin = XinZang(meridian, llm, zhujianlu, baji, jiyiguanli, peizhi, juese=fzt)
        self.pi = PiZang(meridian, zhujianlu, llm, jiyiguanli, peizhi, juese=fzt)
        self.shen = ShenZang(meridian, llm, baji, peizhi, juese=fzt)
        self.pi.xin = self.xin
    def start_all(self):
        self.xin.start(); time.sleep(1.5)
        self.pi.start(); time.sleep(0.5)
        self.shen.start()
    def tingzhi(self):
        self.xin.tingzhi(); self.pi.tingzhi(); self.shen.tingzhi()
