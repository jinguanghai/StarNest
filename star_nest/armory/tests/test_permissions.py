"""
权限·QuanXian 隔离自动化测试
覆盖: 写权限隔离/三体权限差异/ke_xieru守卫
"""
import unittest, sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestQuanXian(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from star_nest.entry import SanTiXiTong
        cls.s = SanTiXiTong()
        cls.bct = cls.s.bianchengti
        cls.yxt = cls.s.yunxingti
        cls.fzt = cls.s.fuzhiti

    def test_qx_001_bct_ke_xieru(self):
        """编程体·写权限=True"""
        self.assertTrue(self.bct.pi.ke_xieru)

    def test_qx_002_yxt_ke_xieru(self):
        """运行体·写权限=False"""
        self.assertFalse(self.yxt.pi.ke_xieru)

    def test_qx_003_fzt_ke_xieru(self):
        """复制体·写权限=False"""
        self.assertFalse(self.fzt.pi.ke_xieru)

    def test_qx_004_yxt_write_blocked(self):
        """运行体·写入被拒绝"""
        tf = os.path.join(tempfile.gettempdir(), "_qx_yxt_test.txt")
        fake = {"gongju_ming":"wenjian_gongju","hanshu_ming":"xieru_wenjian",
                "canshu":'{"path":"'+tf.replace('\\','\\\\')+'","content":"test"}'}
        r = self.yxt.xin._execution_fangan(fake, "write")
        try: os.remove(tf)
        except: pass
        self.assertFalse(r.get("success"), f"YXT should be blocked: {r}")

    def test_qx_005_bct_write_allowed(self):
        """编程体·写入通过"""
        tf = os.path.join(tempfile.gettempdir(), "_qx_bct_test.txt")
        fake = {"gongju_ming":"wenjian_gongju","hanshu_ming":"xieru_wenjian",
                "canshu":'{"path":"'+tf.replace('\\','\\\\')+'","content":"test"}'}
        r = self.bct.xin._execution_fangan(fake, "write")
        try: os.remove(tf)
        except: pass
        self.assertTrue(r.get("success"), f"BCT write failed: {r}")

    def test_qx_006_fzt_has_xin(self):
        """复制体·心存在"""
        self.assertIsNotNone(self.fzt.xin)
        self.assertEqual(self.fzt.xin.juese, "fuzhiti")

    def test_qx_007_santi_juese(self):
        """三体·juese正确"""
        self.assertEqual(self.bct.xin.juese, "bianchengti")
        self.assertEqual(self.yxt.xin.juese, "yunxingti")
        self.assertEqual(self.fzt.xin.juese, "fuzhiti")

    def test_qx_008_fzt_minimal_organs(self):
        """复制体·只有心脾肾(最小配置)"""
        self.assertIsNotNone(self.fzt.xin)
        self.assertIsNotNone(self.fzt.pi)
        self.assertIsNotNone(self.fzt.shen)
        # 复制体不应该有肝和肺
        self.assertTrue(not hasattr(self.fzt, 'gan') or self.fzt.gan is None)
        self.assertTrue(not hasattr(self.fzt, 'fei') or self.fzt.fei is None)
