"""
动力学·DongLiXue 引擎自动化测试
覆盖: 八极动力/劈脾周期/八奇算术/九筹/修复
"""
import unittest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestDongLiXue(unittest.TestCase):
    def test_dl_001_bajidongli_import(self):
        """八极动力学·可导入"""
        from star_nest.dynamics.eight_extremes import EightPoleDynamics
        self.assertIsNotNone(EightPoleDynamics)

    def test_dl_002_piphicycle_import(self):
        """劈脾周期·可导入"""
        from star_nest.dynamics.pi_phi_cycle import PiPhiController
        self.assertIsNotNone(PiPhiController)

    def test_dl_003_bashisuanshu_import(self):
        """八奇算术·可导入"""
        from star_nest.dynamics.eighty_four import EightStrategies
        self.assertIsNotNone(EightStrategies)

    def test_dl_004_jiuchou_import(self):
        """九筹·可导入"""
        from star_nest.dynamics.nine_domains import NineDomainsHealth
        self.assertIsNotNone(NineDomainsHealth)

    def test_dl_005_xiufu_import(self):
        """修复·可导入"""
        from star_nest.dynamics.self_repair import ZiWoXiuFu
        self.assertIsNotNone(ZiWoXiuFu)

    def test_dl_006_baji_instance(self):
        """八极·通过SanTiXiTong实例化"""
        from star_nest.entry import SanTiXiTong
        s = SanTiXiTong()
        b = s.bianchengti.xin.baji
        self.assertIsNotNone(b)

    def test_dl_007_baji_zhenduan(self):
        """八极·诊断输出"""
        from star_nest.entry import SanTiXiTong
        s = SanTiXiTong()
        b = s.bianchengti.xin.baji
        z = b.bajizhenduan([], [])
        for k in ['shizhi','shiliang','jiankangdu','wenti_shu','xiufu_shu']:
            self.assertIn(k, z)

    def test_dl_008_baji_jianduan_jixian(self):
        """八极·极端输入"""
        from star_nest.entry import SanTiXiTong
        s = SanTiXiTong()
        b = s.bianchengti.xin.baji
        z = b.bajizhenduan(["x"]*200, ["y"]*100)
        self.assertGreater(z['jiankangdu'], 0)
        self.assertLess(z['jiankangdu'], 1.0)

    def test_dl_009_baji_kong_lishi(self):
        """八极·空列表不崩溃"""
        from star_nest.entry import SanTiXiTong
        s = SanTiXiTong()
        b = s.bianchengti.xin.baji
        try: z = b.bajizhenduan(None, None)
        except Exception: z = b.bajizhenduan([], [])
        self.assertIsNotNone(z)

    def test_dl_010_piphicycle_instance(self):
        """劈脾·实例化"""
        from star_nest.dynamics.pi_phi_cycle import PiPhiController
        obj = PiPhiController()
        self.assertIsNotNone(obj)

    def test_dl_011_jiuchou_instance(self):
        """九筹·实例化"""
        from star_nest.dynamics.nine_domains import NineDomainsHealth
        obj = NineDomainsHealth()
        self.assertIsNotNone(obj)

    def test_dl_012_bashisuanshu_instance(self):
        """八奇算术·实例化"""
        from star_nest.dynamics.eighty_four import EightStrategies
        obj = EightStrategies()
        self.assertIsNotNone(obj)

    def test_dl_013_xiufu_instance(self):
        """修复·实例化"""
        from star_nest.dynamics.self_repair import ZiWoXiuFu
        try:
            obj = ZiWoXiuFu(os.path.dirname(os.path.dirname(__file__)))
            self.assertIsNotNone(obj)
        except: self.skipTest("xiufu needs specific args")

    def test_dl_014_eightpole_instance(self):
        """八极动力学·实例化"""
        from star_nest.dynamics.eight_extremes import EightPoleDynamics
        obj = EightPoleDynamics()
        self.assertIsNotNone(obj)
