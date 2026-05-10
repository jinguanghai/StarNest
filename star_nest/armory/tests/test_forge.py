"""
铸剑炉·ZhuJianLu 自动化测试
覆盖: staging/部署/回滚/清理/语法修复/代码生成/白名单
"""
import unittest, sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestZhuJianLu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from star_nest.entry import SanTiXiTong
        cls.s = SanTiXiTong()
        cls.zl = cls.s.zhujianlu
        cls.tmpdir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_zl_001_chushihua(self):
        """初始化·属性完整"""
        for attr in ['gongzuo_mulu','chaoshi','llm','xin']:
            self.assertTrue(hasattr(self.zl, attr), f"Missing: {attr}")

    def test_zl_002_xieru_daima(self):
        """写入代码·staging创建"""
        tf = os.path.join(self.tmpdir, "test_zl.py")
        r = self.zl.xieru_daima(tf, "print('hello')")
        self.assertTrue(r.get("success"), f"xieru failed: {r}")
        staging_path = r.get("staging_lujing", "")
        self.assertTrue(os.path.exists(staging_path), f"staging missing: {staging_path}")

    def test_zl_003_bushu_daima(self):
        """部署代码·staging->target"""
        tf = os.path.join(self.tmpdir, "test_deploy.py")
        self.zl.xieru_daima(tf, "print('deployed')")
        r = self.zl.bushu_daima(tf)
        self.assertTrue(r.get("success"), f"bushu failed: {r}")
        content = open(tf, encoding='utf-8').read()
        self.assertIn("deployed", content)

    def test_zl_004_huigun(self):
        """回滚·有备份还原"""
        tf = os.path.join(self.tmpdir, "test_rollback.py")
        with open(tf, 'w', encoding='utf-8') as f:
            f.write("print('original')")
        self.zl.xieru_daima(tf, "print('new')")
        self.zl.bushu_daima(tf)
        r = self.zl.huigun(tf)
        self.assertTrue(r.get("success"), f"rollback failed: {r}")

    def test_zl_005_huigun_wu_beifen(self):
        """回滚·新文件无备份返回错误"""
        tf = os.path.join(self.tmpdir, "test_no_backup.py")
        self.zl.xieru_daima(tf, "print('new')")
        self.zl.bushu_daima(tf)
        r = self.zl.huigun(tf)
        self.assertFalse(r.get("success"), "Should fail: no backup for new file")

    def test_zl_006_qingli_staging(self):
        """清理staging"""
        tf = os.path.join(self.tmpdir, "test_clean.py")
        self.zl.xieru_daima(tf, "print('x')")
        staging_fp = os.path.join(os.path.dirname(tf), "test_clean.py.staging")
        self.assertTrue(os.path.exists(staging_fp))
        self.zl.qingli_staging(tf)
        self.assertFalse(os.path.exists(staging_fp))

    def test_zl_007_xieru_mulu_bucunzai(self):
        """写入·目标目录不存在"""
        tf = os.path.join(self.tmpdir, "ghost_dir", "test.py")
        r = self.zl.xieru_daima(tf, "print('x')")
        self.assertFalse(r.get("success"))

    def test_zl_008__yinghe_yufa(self):
        """语法修复·方法存在"""
        self.assertTrue(hasattr(self.zl, '_yinghe_yufa_xiufu'))
        self.assertTrue(callable(self.zl._yinghe_yufa_xiufu))

    def test_zl_009__shengcheng_daima(self):
        """代码生成·方法存在"""
        self.assertTrue(hasattr(self.zl, '_shengcheng_daima'))
        self.assertTrue(callable(self.zl._shengcheng_daima))

    def test_zl_010_duanzao_cunzai(self):
        """锻造方法·duanzao存在"""
        self.assertTrue(hasattr(self.zl, 'duanzao'))
        self.assertTrue(callable(self.zl.duanzao))

    def test_zl_011__execution(self):
        """代码执行·_execution"""
        r = self.zl._execution("print('exec ok')")
        self.assertTrue(r.get("success"))
        self.assertIn("exec ok", r.get("output", ""))

    def test_zl_012__execution_cuowu(self):
        """代码执行·语法错误返回失败"""
        r = self.zl._execution("invalid python code @@@")
        self.assertFalse(r.get("success"))

    def test_zl_013__execution_chaoshi(self):
        """代码执行·超时设置正确"""
        self.assertGreater(self.zl.chaoshi, 0)

    def test_zl_014_baimingdan(self):
        """白名单·标准库列表存在"""
        from star_nest.execution import zhujianlu
        self.assertTrue(hasattr(zhujianlu, 'BIAOZHUNKU_BAIMINGDAN'))

    def test_zl_015_jiancha_minxie(self):
        """路径检查·方法存在"""
        self.assertTrue(hasattr(self.zl, '_jiancha_minxie_lujing'))

    def test_zl_016__execution_fanhui_jiegou(self):
        """执行返回·dict结构正确"""
        r = self.zl._execution("x=1")
        self.assertIsInstance(r, dict)
        for k in ['success','output','error']:
            self.assertIn(k, r)

    def test_zl_017_staging_mulu(self):
        """staging·xieru_daima使用临时目录"""
        tf = os.path.join(self.tmpdir, "test_staging.py")
        r = self.zl.xieru_daima(tf, "print('staging_ok')")
        self.assertTrue(r.get("success"), f"xieru failed: {r}")
        staging_lj = r.get("staging_lujing", "")
        self.assertTrue(staging_lj and os.path.exists(staging_lj))
