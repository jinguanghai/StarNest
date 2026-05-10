"""
心·XinZang 自动化测试
覆盖: 初始化/器官接入/消息队列/身份/五境/λ调度/duihua
"""
import unittest, sys, os, time, threading, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from pathlib import Path

class TestXinZang(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from star_nest.entry import SanTiXiTong
        cls.s = SanTiXiTong()
        cls.bct = cls.s.bianchengti; cls.yxt = cls.s.yunxingti

    def test_xin_001_chushihua(self):
        """初始化·属性完整性"""
        x = self.bct.xin
        for attr in ['meridian','llm','zhujianlu','baji','jiyiguanli','juese',
                     'shuchu_duilie','renwu_duilie','yonghu_xuqiu_duilie']:
            self.assertIsNotNone(getattr(x, attr, None), f"Missing: {attr}")
        self.assertEqual(x._yunxing, True)

    def test_xin_002_juese(self):
        """身份·三体juese正确"""
        self.assertEqual(self.bct.xin.juese, "bianchengti")
        self.assertEqual(self.yxt.xin.juese, "yunxingti")

    def test_xin_003_jieru_qiguan(self):
        """器官接入·五脏引用正确"""
        x = self.bct.xin
        self.assertIsNotNone(x.gan); self.assertIsNotNone(x.pi)
        self.assertIsNotNone(x.fei); self.assertIsNotNone(x.shen)

    def test_xin_004_protocols_yinqing(self):
        """五境引擎·初始加载"""
        x = self.bct.xin
        self.assertIsNotNone(x.fanjing, "反境缺失")
        self.assertIsNotNone(x.hejing, "合境缺失")
        self.assertIsNotNone(x.chaoyuejing, "超越境缺失")

    def test_xin_005_shenfen_xushi(self):
        """身份叙事·编程体vs运行体"""
        sf_bct = self.bct.xin._shenfen()
        sf_yxt = self.yxt.xin._shenfen()
        self.assertIn("编程", sf_bct)
        self.assertIn("运行", sf_yxt)
        self.assertIn("写权限", sf_bct)
        self.assertIn("不可修改", sf_yxt)

    def test_xin_006_xiaoxi_duilie(self):
        """消息队列·渐进认知引擎缓冲"""
        x = self.bct.xin
        # 关闭渐进引擎→走原始队列
        old_jjr = x.jianjinrenzhi
        x.jianjinrenzhi = None
        x.add_xuqiu("ceshi_xuqiu")
        m = x._xiaoxi_chuandu()
        self.assertIsNotNone(m)
        self.assertIn("ceshi_xuqiu", str(m))
        x.jianjinrenzhi = old_jjr

    def test_xin_007_add_renwu(self):
        """任务添加·renwu_duilie"""
        x = self.bct.xin
        qsize_before = x.renwu_duilie.qsize()
        x.add_renwu("ceshi_renwu")
        self.assertEqual(x.renwu_duilie.qsize(), qsize_before + 1)

    def test_xin_008_guangbo_shuchu(self):
        """广播输出·shuchu_duilie"""
        x = self.bct.xin
        x.guangbo_shuchu("ceshi_shuchu")
        m = x.shuchu_duilie.get_nowait()
        self.assertEqual(m, "ceshi_shuchu")

    def test_xin_009_chuli_kong(self):
        """消息处理·空消息返回None"""
        r = self.bct.xin._chuli("")
        self.assertIsNone(r)

    def test_xin_010_chuli_exit(self):
        """消息处理·exit返回None"""
        r = self.bct.xin._chuli("__EXIT__")
        self.assertIsNone(r)

    def test_xin_011_duihua_jiben(self):
        """对话·基本调用"""
        r = self.bct.xin._duihua("ceshi_duihua")
        self.assertIsInstance(r, str)
        self.assertGreater(len(r), 5)

    def test_xin_012_fuwu_protocols_syntax(self):
        """五境分析·语法错误检测"""
        r = self.bct.xin.fuwu_protocols_fenxi("测试", "SyntaxError: bad token")
        self.assertIsInstance(r, str)

    def test_xin_013_fuwu_protocols_jinzhi(self):
        """五境分析·禁止类错误"""
        r = self.bct.xin.fuwu_protocols_fenxi("测试", "禁止写入系统文件")
        self.assertIsInstance(r, str)
        self.assertGreater(len(r), 0)

    def test_xin_014_execution_duanzao(self):
        """方案执行·duanzao调度"""
        fangan = {"gongju_ming":"zhujianlu","hanshu_ming":"duanzao","canshu":"测试需求"}
        r = self.bct.xin._execution_fangan(fangan, "test")
        self.assertIsNotNone(r)

    def test_xin_015_execution_zhijian(self):
        """方案执行·zhijian执行代码"""
        fangan = {"gongju_ming":"zhujianlu","hanshu_ming":"zhijian","canshu":"print('ok')"}
        r = self.bct.xin._execution_fangan(fangan, "test")
        self.assertIsNotNone(r)

    def test_xin_016_execution_weizhi(self):
        """方案执行·未知handle返回None"""
        fangan = {"gongju_ming":"unknown","hanshu_ming":"unknown","canshu":""}
        r = self.bct.xin._execution_fangan(fangan, "test")
        self.assertIsNone(r)

    def test_xin_017_tiaozheng_yuzhi(self):
        """阈值调整·无异常"""
        try: self.bct.xin.tiaozheng_yuzhi(0.5)
        except: self.fail("tiaozheng_yuzhi raised")

    def test_xin_018_jilu_jiyi(self):
        """记忆记录·jilu_jiyi无异常"""
        try: self.bct.xin._jilu_jiyi("测试输入", "测试回复")
        except: self.fail("_jilu_jiyi raised")

    def test_xin_019_baji_xunhuan(self):
        """八极循环·无异常调用"""
        try: self.bct.xin._baji_xunhuan()
        except: self.fail("_baji_xunhuan raised")

    def test_xin_020_qidong_yure(self):
        """启动预热·无异常"""
        try: self.bct.xin._qidong_yure()
        except: self.fail("_qidong_yure raised")
