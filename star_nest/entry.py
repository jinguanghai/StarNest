import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from star_nest.meridian.seven_laws import QiLv
from star_nest.runtime.config import XIANGMU_MULU,XINGCHAOZDD_MULU,jiazai_huanjing
from star_nest.meridian.channel import JingLuo
from star_nest.meridian.memory import JingLuoJiYi
from star_nest.execution.llm import LLMKeHuDuan
from star_nest.execution.forge import ZhuJianLu
from star_nest.shared_memory.manager import JiYiGuanLi
from star_nest.bodies.prog_body.heart import BianChengTi
from star_nest.bodies.runtime_body.heart import YunXingTi
from star_nest.bodies.aux_body.heart import FuZhiTi
from star_nest.runtime.logs.runtime_log import YunXingRiZhi
from star_nest.dynamics.qi_blood import QiXueXunHuan
from star_nest.dynamics.eight_extremes import EightPoleDynamics
import time,threading,os

class SanTiXiTong:
    def __init__(self):
        jiazai_huanjing()
        self.api_key=os.environ.get('DEEPSEEK_API_KEY','');self.houbu_key=os.environ.get('HUOSHAN_API_KEY','')
        self.qilv=QiLv();self.meridian=JingLuo(XINGCHAOZDD_MULU/'shared_memory')
        self.llm=LLMKeHuDuan(self.api_key,"deepseek-v4-pro",huoshan_key=self.houbu_key)
        self.zhujianlu=ZhuJianLu(XIANGMU_MULU, llm=self.llm);self.baji=EightPoleDynamics()
        self.jiyiguanli=JiYiGuanLi(XINGCHAOZDD_MULU/'shared_memory')
        import star_nest.runtime.config as peizhi;peizhi.LV_JI=self.qilv.LV_JI
        self.bianchengti=BianChengTi(self.meridian,self.llm,self.zhujianlu,self.baji,self.jiyiguanli,peizhi)
        self.yunxingti=YunXingTi(self.meridian,self.llm,self.zhujianlu,self.baji,self.jiyiguanli,peizhi)
        self.fuzhiti=FuZhiTi(self.meridian,self.llm,self.zhujianlu,self.baji,self.jiyiguanli,peizhi)
        self.yunxingti.gan.xin=self.yunxingti.xin;self.bianchengti.gan.xin=self.bianchengti.xin
        # 运行日志注入
        self.rizhi = YunXingRiZhi(XINGCHAOZDD_MULU/'rizhi')
        self.meridian.rizhi = self.rizhi
        self.yunxingti.xin.rizhi = self.rizhi
        self.bianchengti.xin.rizhi = self.rizhi
        # 经络记忆注入
        self.meridianjiyi = JingLuoJiYi(XINGCHAOZDD_MULU/'meridian')
        self.meridian.jiyi = self.meridianjiyi
        self.yunxingti.xin.meridian_jiyi = self.meridianjiyi
        self.bianchengti.xin.meridian_jiyi = self.meridianjiyi
        # 气血循环泵注入
        self.qixue = QiXueXunHuan(self.meridian, self.meridianjiyi, xin_can_zhao=self.yunxingti.xin)
        self.qixue._rizhi = self.rizhi
        self.meridian.qixue = self.qixue
        self.yunxingti.xin.qixue = self.qixue
        self.bianchengti.xin.qixue = self.qixue
        # 感知层注入
        try:
            from star_nest.dynamics.perception import GanzhiCeng
            self.ganzhiceng = GanzhiCeng(self.meridian, XINGCHAOZDD_MULU)
            self.yunxingti.xin.ganzhiceng = self.ganzhiceng
            self.bianchengti.xin.ganzhiceng = self.ganzhiceng
        except Exception as e:
            print(f'[!!] ganzhiceng load failed: {e}')
        # 输入层注入
        try:
            from star_nest.dynamics.input_layer import ShuRuCeng
            self.shuruceng = ShuRuCeng(self.yunxingti.xin)
            self.yunxingti.xin.shuruceng = self.shuruceng
            self.bianchengti.xin.shuruceng = ShuRuCeng(self.bianchengti.xin)
        except Exception as e:
            print(f'[!!] shuruceng load failed: {e}')
        # 渐进认知引擎注入
        try:
            from star_nest.dynamics.progressive_cognition import JianJinRenZhi
            self.jianjinrenzhi = JianJinRenZhi(self.yunxingti.xin)
            self.yunxingti.xin.jianjinrenzhi = self.jianjinrenzhi
            self.bianchengti.xin.jianjinrenzhi = JianJinRenZhi(self.bianchengti.xin)
        except Exception as e:
            print(f'[!!] jianjinrenzhi load failed: {e}')
        # 问剑路注入
        try:
            from star_nest.dynamics.inquiry_path import get_wen_jian_lu
            self.wenjianlu = get_wen_jian_lu(self.yunxingti.xin)
            self.yunxingti.xin.wenjianlu = self.wenjianlu
        except Exception as e:
            print(f'[!!] wenjianlu load failed: {e}')
        # 软件操作层注入
        try:
            from star_nest.dynamics.software_layer import RuanJianCeng
            self.ruanjianceng = RuanJianCeng(self.yunxingti.xin)
            self.yunxingti.xin.ruanjianceng = self.ruanjianceng
        except Exception as e:
            print(f'[!!] ruanjianceng load failed: {e}')
        # 软件流水线注入
        try:
            from star_nest.execution.pipeline import LiuShuiXian
            self.liushuixian = LiuShuiXian(self.yunxingti.xin)
            self.yunxingti.xin.liushuixian = self.liushuixian
        except Exception as e:
            print(f'[!!] liushuixian load failed: {e}')
        # 三体安全注入
        try:
            from star_nest.dynamics.security_trinity import AnQuanSanTi
            self.anquan = AnQuanSanTi(meridian=self.meridian, llm=self.llm, xin=self.yunxingti.xin)
            self.yunxingti.xin.anquan = self.anquan
            print(f'[三体安全] Ω监控·π执行·φ验证 就绪')
        except Exception as e:
            print(f'[!!] anquansanti load failed: {e}')
        # 照妖镜注入
        try:
            from star_nest.dynamics.truth_mirror import ZhaoYaoJing
            self.zhaoyaojing = ZhaoYaoJing(self.yunxingti.xin)
            self.yunxingti.xin.zhaoyaojing = self.zhaoyaojing
            print(f'[照妖镜] LLM驱动环境扫描·五境杀毒·铸剑炉执行 就绪')
        except Exception as e:
            print(f'[!!] zhaoyaojing load failed: {e}')
        # π-φ安全引擎注入
        try:
            from star_nest.dynamics.pi_phi_security import PiPhiAnQuan
            self.piphianquan = PiPhiAnQuan(self.yunxingti.xin, self.zhaoyaojing, self.anquan)
            self.yunxingti.xin.piphianquan = self.piphianquan
            print(f'[π-φ] 安全引擎·七律节律·展开→收敛→闭环 就绪')
        except Exception as e:
            print(f'[!!] piphianquan load failed: {e}')
        # π-φ统计总线注入
        try:
            from star_nest.dynamics.pi_phi_stats import PiPhiTongJi
            self.piphi = PiPhiTongJi(meridian=self.meridian)
            self.yunxingti.xin.piphi = self.piphi
            print(f'[π-φ] 全局统计总线就绪')
        except Exception as e:
            print(f'[!!] piphitongji load failed: {e}')
        # 经络自动路由: 运行体问题→写经络日志(不进任务队列)
        def wenti_huizong(tid, wenti):
            try: self.meridian.jilu_fansi(f"[Ω安全|{tid}] {wenti.get('miaoshu','')[:200]}")
            except: pass
            try: self.rizhi.wenti_rizhi(tid, wenti)
            except: pass
        self.meridian.wenti_tongzhi = wenti_huizong
        try:
            from star_nest.dynamics.self_repair import ZiWoXiuFu
            self.yunxingti.gan.xiufu=ZiWoXiuFu(XINGCHAOZDD_MULU)
            self.bianchengti.gan.xiufu=ZiWoXiuFu(XINGCHAOZDD_MULU)
        except Exception as e:
            print(f'[!!] xiufu load failed: {e}')
        self._yunxing=True

    def jiancha_tielu(self):
        print('SanTi V2.0')
        try:
            tj=self.jiyiguanli.zhishi_tongji()
            print(f'[{tj.get("zongshu",0)} entries]')
        except Exception:
            print('[memory OK]')

    def qidong(self):
        self.jiancha_tielu()
        try: self.meridian.jiazai()
        except Exception as e: print(f'[!!] meridian load failed: {e}')
        print('Starting...')
        for ti, name in [(self.bianchengti,'bianchengti'),(self.fuzhiti,'fuzhiti'),(self.yunxingti,'yunxingti')]:
            try:
                ti.start_all()
                print(f'{name} OK')
            except Exception as e:
                print(f'[!!] {name} start failed: {e}')
        # 第五境常驻进化引擎
        try:
            from diprotocols_qidong import DiWuJing
            self.diprotocols = DiWuJing()
            self.diprotocols.qidong()
            print('diprotocols OK')
        except Exception as e:
            print(f'diprotocols skipped: {e}')
        time.sleep(2)
        from star_nest.interface import SanTiJieMian
        SanTiJieMian(self).yunxing()

    def tingzhi(self):
        self._yunxing=False
        self.yunxingti.tingzhi();self.bianchengti.tingzhi();self.fuzhiti.tingzhi()
        self.meridian.baocun();print('Stopped')

def main():
    import sys
    # 下载Python嵌入版
    if "--download-python" in sys.argv:
        from star_nest.dynamics.self_bootstrap import ZiJuCeng
        zj = ZiJuCeng(XINGCHAOZDD_MULU)
        result = zj.xia_zai_python_embed()
        print(f"下载结果: {result}")
        return
    # 自举模式: 环境检测→自我修复→唤醒
    if "--ziju" in sys.argv:
        try:
            from star_nest.dynamics.self_bootstrap import ZiJuCeng
            zj = ZiJuCeng(XINGCHAOZDD_MULU)
            result = zj.zi_ju()
            if not result["success"]:
                print(f"\n自举失败: {result.get('error','')}")
                return
        except Exception as e:
            print(f"[自举] 加载失败: {e}")
            # 继续正常启动
    SanTiXiTong().qidong()

if __name__ == '__main__':
    main()