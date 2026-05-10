"""
五境·WuJing 引擎自动化测试
覆盖: 所有6个引擎可导入+实例化
"""
import unittest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestWuJing(unittest.TestCase):
    def test_wj_001_zhengjing_import(self):
        """正境引擎·可导入"""
        from star_nest.protocols.proper_classic import ZhengJing
        self.assertIsNotNone(ZhengJing)

    def test_wj_002_fanjing_import(self):
        """反境引擎·可导入"""
        from star_nest.protocols.counter_classic import FanJing
        self.assertIsNotNone(FanJing)

    def test_wj_003_hejing_import(self):
        """合境引擎·可导入"""
        from star_nest.protocols.unity_classic import HeJing
        self.assertIsNotNone(HeJing)

    def test_wj_004_chaoyuejing_import(self):
        """超越境引擎·可导入"""
        from star_nest.protocols.transcend_classic import ChaoYueJing
        self.assertIsNotNone(ChaoYueJing)

    def test_wj_005_benyuan_import(self):
        """本源境引擎·可导入"""
        from star_nest.protocols.origin import BenYuan
        self.assertIsNotNone(BenYuan)

    def test_wj_006_zizhi_import(self):
        """自治引擎·可导入"""
        from star_nest.protocols.self_discipline import ZiZhi
        self.assertIsNotNone(ZiZhi)

    def test_wj_007_fanjing_instance(self):
        """反境·实例化(需xin)"""
        from star_nest.entry import SanTiXiTong
        s = SanTiXiTong()
        x = s.bianchengti.xin
        self.assertIsNotNone(x.fanjing)
        self.assertIsNotNone(x.hejing)
        self.assertIsNotNone(x.chaoyuejing)

    def test_wj_008_protocols_methods(self):
        """五境引擎·方法签名检查"""
        from star_nest.entry import SanTiXiTong
        s = SanTiXiTong()
        x = s.bianchengti.xin
        if x.fanjing:
            self.assertTrue(hasattr(x.fanjing, 'fanjing_chaijie'))
        if x.hejing:
            self.assertTrue(hasattr(x.hejing, 'hejing_jiupingmu'))
        if x.chaoyuejing:
            self.assertTrue(hasattr(x.chaoyuejing, 'chaoyuejing_shuxing'))
