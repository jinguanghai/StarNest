"""
记忆管理·JiYiGuanLi 自动化测试
覆盖: 知识检索/技能检索/融合检索/统计/备份
"""
import unittest, sys, os, tempfile, shutil, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestJiYi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from star_nest.entry import SanTiXiTong
        cls.s = SanTiXiTong()
        cls.jm = cls.s.jiyiguanli

    def test_jy_001_tongji(self):
        """统计·zhishi_tongji"""
        tj = self.jm.zhishi_tongji()
        self.assertIn("zongshu", tj)
        self.assertGreater(tj["zongshu"], 200)

    def test_jy_002_ronghe_jiansuo(self):
        """融合检索·返回结构正确"""
        r = self.jm.ronghe_jiansuo("中医 五行", 5)
        self.assertIsInstance(r, dict)
        self.assertIn("zhishi", r)

    def test_jy_003_ronghe_jiansuo_kong(self):
        """融合检索·空查询"""
        r = self.jm.ronghe_jiansuo("", 3)
        self.assertIsInstance(r, dict)

    def test_jy_004_ronghe_jiansuo_chang(self):
        """融合检索·长查询"""
        r = self.jm.ronghe_jiansuo("这是" + "一个"*20 + "非常长的查询", 5)
        self.assertIsInstance(r, dict)

    def test_jy_005_jiansuo_zhishi(self):
        """知识检索·jiansuo_zhishi"""
        r = self.jm.jiansuo_zhishi("数学", 5)
        self.assertIsInstance(r, list)
        if r:
            self.assertIn("biaoti", r[0])
            self.assertIn("yao_dian", r[0])

    def test_jy_006_jiansuo_zhishi_many(self):
        """知识检索·限制数量"""
        r = self.jm.jiansuo_zhishi("学", 20)
        self.assertLessEqual(len(r), 20)

    def test_jy_007_jiansuo_jineng(self):
        """技能检索·返回列表"""
        r = self.jm.jiansuo_jineng("编程")
        self.assertIsInstance(r, list)

    def test_jy_008_cjk_ngram(self):
        """CJK ngram·中文无空格检索"""
        r = self.jm.ronghe_jiansuo("简要介绍五境", 5)
        self.assertIsInstance(r, dict)
        self.assertIn("zhishi", r)

    def test_jy_009_cjk_ngram_short(self):
        """CJK ngram·短中文"""
        r = self.jm.ronghe_jiansuo("心肝脾肺肾", 5)
        self.assertIsInstance(r, dict)

    def test_jy_010_ronghe_jiansuo_teyici(self):
        """融合检索·特异词"""
        r = self.jm.ronghe_jiansuo("铸剑炉 经络 八极", 8)
        self.assertIsInstance(r, dict)

    def test_jy_011_jineng_maodian(self):
        """技能锚点·加载正确"""
        self.assertIsInstance(self.jm.jineng_maodian, list)

    def test_jy_012_beifen_jiyi(self):
        """记忆备份·无异常"""
        tmpd = tempfile.mkdtemp()
        try: self.jm.beifen_jiyi(tmpd)
        except: self.fail("beifen_jiyi raised")
        finally: shutil.rmtree(tmpd, ignore_errors=True)

    def test_jy_013_changqi_db_cunzai(self):
        """长期记忆·db文件存在"""
        self.assertTrue(self.jm.changqi_db.exists())

    def test_jy_014_danshi_jiansuo(self):
        """单字搜索·不崩溃"""
        r = self.jm.ronghe_jiansuo("心", 3)
        self.assertIsInstance(r, dict)

    def test_jy_015_fuhao_jiansuo(self):
        """符号搜索·安全返回"""
        r = self.jm.ronghe_jiansuo("123 !@#$", 3)
        self.assertIsInstance(r, dict)
