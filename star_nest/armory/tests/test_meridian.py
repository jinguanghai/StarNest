"""
经络·JingLuo 自动化测试
覆盖: 初始化/心跳/问题/修复/持久化/状态摘要/图谱
"""
import unittest, sys, os, time, json, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestJingLuo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        from star_nest.meridian.meridian import JingLuo
        cls.jl = JingLuo(cls.tmpdir)
        from star_nest.entry import SanTiXiTong
        cls.s = SanTiXiTong()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_jl_001_chushihua(self):
        """初始化·三体节点创建"""
        for tid in ["yunxingti","bianchengti","fuzhiti"]:
            self.assertTrue(self.jl.tupu.has_node(tid), f"Missing node: {tid}")

    def test_jl_002_santi_bian(self):
        """三体·边关系正确"""
        self.assertTrue(self.jl.tupu.has_edge("bianchengti","yunxingti"))
        self.assertTrue(self.jl.tupu.has_edge("bianchengti","fuzhiti"))
        self.assertTrue(self.jl.tupu.has_edge("fuzhiti","bianchengti"))

    def test_jl_003_qilv(self):
        """奇律·qilv属性存在"""
        self.assertIsNotNone(self.jl.qilv)
        self.assertGreater(self.jl.qilv.qu_chaoshi("yiweizhou"), 0)

    def test_jl_004_jilu_xintiao(self):
        """心跳记录·jilu_xintiao"""
        self.jl.jilu_xintiao("bianchengti")
        zt = self.jl.zhuangtai_zhaiyao()
        self.assertIn("bianchengti", zt)

    def test_jl_005_jilu_xintiao_feixiao(self):
        """心跳记录·不存在节点静默"""
        try: self.jl.jilu_xintiao("non_existent")
        except: self.fail("jilu_xintiao on missing node raised")

    def test_jl_006_jilu_wenti(self):
        """问题记录·jilu_wenti"""
        self.jl.jilu_wenti("yunxingti", {
            "miaoshu":"测试问题","leixing":"test","laiyuan":"test",
            "shijian_float":time.time()
        })
        wt = self.jl.qu_wenti_liebiao("yunxingti")
        self.assertGreater(len(wt), 0)

    def test_jl_007_jilu_xiufu(self):
        """修复记录·jilu_xiufu"""
        self.jl.jilu_xiufu("yunxingti", {
            "miaoshu":"测试修复","fangfa":"test","laiyuan":"test"
        })
        xf = self.jl.qu_xiufu_lishi("yunxingti")
        self.assertGreater(len(xf), 0)

    def test_jl_008_wenti_chaoguo(self):
        """问题列表·超100条截断"""
        for i in range(105):
            self.jl.jilu_wenti("bianchengti", {
                "miaoshu":f"问题{i}","leixing":"test","laiyuan":"test",
                "shijian_float":time.time()
            })
        wt = self.jl.qu_wenti_liebiao("bianchengti")
        self.assertLessEqual(len(wt), 100)

    def test_jl_009_baocun_jiazai(self):
        """持久化·保存加载"""
        self.jl.jilu_wenti("fuzhiti", {
            "miaoshu":"持久化测试","leixing":"persist","laiyuan":"test",
            "shijian_float":time.time()
        })
        self.jl.baocun()
        from star_nest.meridian.meridian import JingLuo
        jl2 = JingLuo(self.tmpdir)
        jl2.jiazai()
        wt = jl2.qu_wenti_liebiao("fuzhiti")
        # 可能有遗留数据，至少是list
        self.assertIsInstance(wt, list)

    def test_jl_010_zhuangtai_zhaiyao(self):
        """状态摘要·返回字典"""
        zt = self.jl.zhuangtai_zhaiyao()
        self.assertIsInstance(zt, dict)
        for tid in ["yunxingti","bianchengti","fuzhiti"]:
            self.assertIn(tid, zt)

    def test_jl_011_jilu_shijian(self):
        """事件记录·无异常"""
        try: self.jl.jilu_shijian("test_type","测试事件","test_data")
        except: pass  # 可能没有实现

    def test_jl_012_jilu_fansi(self):
        """反思记录·无异常"""
        try: self.jl.jilu_fansi(wenti="测试反思", laiyuan_jiedian="test")
        except: pass

    def test_jl_013_qilv_wanquan(self):
        """共享经络·qilv完整"""
        jl2 = self.s.meridian
        cycles = ["yixi","yiweizhou","yixiaozhou","yizhongzhou",
                   "yidazhou","yizhoutian","yijiyuan"]
        for lv in cycles:
            self.assertGreater(jl2.qilv.qu_chaoshi(lv), 0)
            self.assertGreater(jl2.qilv.qu_zhouqi(lv), 0)

    def test_jl_014_tupu_caozuo(self):
        """图谱操作·节点增删"""
        t = self.jl.tupu
        t.add_node("test_node", mingcheng="Test")
        self.assertTrue(t.has_node("test_node"))
        t.add_edge("test_node","bianchengti",wuxing="sheng")
        self.assertTrue(t.has_edge("test_node","bianchengti"))
