"""
界面·JieMian/CLI/终端 自动化测试
覆盖: 颜色类/终端渲染/三体界面实例化
"""
import unittest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestJieMian(unittest.TestCase):
    def test_jm_001_yanse_changliang(self):
        """颜色·全部常量存在"""
        from star_nest.interface.celestial_command import YanSe
        for attr in ['MU_LV','HUO_CHI','TU_HUANG','JIN_BAI','SHUI_HEI',
                     'QING','ZI','HUI','JIACU','XIAHUA','SHANSHUO','FUWEI']:
            self.assertIsNotNone(getattr(YanSe, attr, None), f"Missing: {attr}")

    def test_jm_002_yanse_zang(self):
        """颜色·脏器映射"""
        from star_nest.interface.celestial_command import YanSe
        for zang in ["肝","心","脾","肺","肾"]:
            c = YanSe.zang_yanse(zang)
            self.assertIsNotNone(c)

    def test_jm_003_yanse_weizhi(self):
        """颜色·未知脏器返回默认"""
        from star_nest.interface.celestial_command import YanSe
        c = YanSe.zang_yanse("未知")
        self.assertEqual(c, YanSe.FUWEI)

    def test_jm_004_zhongduan_chushihua(self):
        """终端·初始化"""
        from star_nest.interface.celestial_command import ZhongDuan
        z = ZhongDuan()
        self.assertIsNotNone(z)
        self.assertTrue(hasattr(z, 'shuchu'))
        self.assertTrue(hasattr(z, 'fen_ge_xian'))

    def test_jm_005_zhongduan_shuchu(self):
        """终端·输出方法不崩溃"""
        from star_nest.interface.celestial_command import ZhongDuan, YanSe
        z = ZhongDuan()
        try: z.shuchu("test", YanSe.QING)
        except: self.fail("shuchu raised")

    def test_jm_006_zhongduan_fenge(self):
        """终端·分隔线"""
        from star_nest.interface.celestial_command import ZhongDuan
        z = ZhongDuan()
        try: z.fen_ge_xian()
        except: self.fail("fen_ge_xian raised")

    def test_jm_007_zhongduan_qingping(self):
        """终端·清屏"""
        from star_nest.interface.celestial_command import ZhongDuan
        z = ZhongDuan()
        try: z.qingping()
        except: self.fail("qingping raised")

    def test_jm_008_zhongduan_tishifu(self):
        """终端·提示符"""
        from star_nest.interface.celestial_command import ZhongDuan
        z = ZhongDuan()
        try: z.tishifu()
        except: self.fail("tishifu raised")

    def test_jm_009_zhongduan_wenli(self):
        """终端·纹理输出"""
        from star_nest.interface.celestial_command import ZhongDuan
        z = ZhongDuan()
        try: z.shuchu_wenli("test texture")
        except: self.fail("shuchu_wenli raised")

    def test_jm_010_zhongduan_zangqi(self):
        """终端·脏器状态"""
        from star_nest.interface.celestial_command import ZhongDuan
        z = ZhongDuan()
        try: z.zangqi_zhuangtai({"心":"O","肝":"O"})
        except: self.fail("zangqi_zhuangtai raised")

    def test_jm_011_santi_jiemian_instance(self):
        """三体界面·实例化"""
        from star_nest.interface import SanTiJieMian
        from star_nest.entry import SanTiXiTong
        s = SanTiXiTong()
        jm = SanTiJieMian(s)
        self.assertIsNotNone(jm)
        self.assertTrue(hasattr(jm, 'yunxing'))
        self.assertIn(jm._moshi, ['yunxingti', 'bianchengti'])
