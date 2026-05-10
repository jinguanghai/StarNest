"""
工具·GongJu 自动化测试 (文件/Shell/Git)
覆盖: 文件读写列建搜/Shell执行/Git
"""
import unittest, sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestGongJu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()

    def test_gj_001_duqu_cunzai(self):
        """读文件·存在"""
        from star_nest.armory.wenjian_gongju import duqu_wenjian
        r = duqu_wenjian(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ceshi.py"))
        self.assertTrue(r["success"])

    def test_gj_002_duqu_bucunzai(self):
        """读文件·不存在"""
        from star_nest.armory.wenjian_gongju import duqu_wenjian
        r = duqu_wenjian("/nonexistent_xyz_file.txt")
        self.assertFalse(r["success"])

    def test_gj_003_duqu_kong_path(self):
        """读文件·空路径"""
        from star_nest.armory.wenjian_gongju import duqu_wenjian
        r = duqu_wenjian("")
        self.assertFalse(r["success"])

    def test_gj_004_liechu_mulu(self):
        """列目录·正常"""
        from star_nest.armory.wenjian_gongju import liechu_mulu
        r = liechu_mulu(os.path.dirname(os.path.dirname(__file__)))
        self.assertTrue(r["success"])
        self.assertGreater(len(r.get("data", [])), 0)

    def test_gj_005_liechu_bucunzai(self):
        """列目录·不存在"""
        from star_nest.armory.wenjian_gongju import liechu_mulu
        r = liechu_mulu("/nonexistent_dir_xyz")
        self.assertFalse(r["success"])

    def test_gj_006_liechu_kong(self):
        """列目录·空可转为当前目录"""
        from star_nest.armory.wenjian_gongju import liechu_mulu
        r = liechu_mulu(".")
        self.assertTrue(r["success"])

    def test_gj_007_chuangjian_mulu(self):
        """创建目录·正常"""
        from star_nest.armory.wenjian_gongju import chuangjian_mulu
        d = os.path.join(self.tmpdir, "test_create_dir")
        r = chuangjian_mulu(d)
        self.assertTrue(r["success"])
        self.assertTrue(os.path.isdir(d))

    def test_gj_008_chuangjian_mulu_jiaceng(self):
        """创建目录·嵌套路径"""
        from star_nest.armory.wenjian_gongju import chuangjian_mulu
        d = os.path.join(self.tmpdir, "a", "b", "c")
        r = chuangjian_mulu(d)
        self.assertTrue(r["success"])
        self.assertTrue(os.path.isdir(d))

    def test_gj_009_sousuo_wenjian(self):
        """搜索文件·正常"""
        from star_nest.armory.wenjian_gongju import sousuo_wenjian
        r = sousuo_wenjian("*.py|" + os.path.dirname(os.path.dirname(__file__)))
        self.assertTrue(r["success"])

    def test_gj_010_xieru_wenjian_zhengchang(self):
        """写文件·JSON格式"""
        from star_nest.armory.wenjian_gongju import xieru_wenjian
        tf = os.path.join(self.tmpdir, "write_test.txt")
        r = xieru_wenjian('{"path":"' + tf.replace('\\','\\\\') + '","content":"hello xieru"}')
        self.assertTrue(r["success"])
        self.assertTrue(os.path.exists(tf))
        content = open(tf, encoding='utf-8').read()
        self.assertEqual(content, "hello xieru")

    def test_gj_011_xieru_huaige_json(self):
        """写文件·坏JSON返回失败"""
        from star_nest.armory.wenjian_gongju import xieru_wenjian
        r = xieru_wenjian("not valid json @@@")
        self.assertFalse(r["success"])

    def test_gj_012_xieru_quanxian_jujue(self):
        """写文件·无路径无分隔符返回失败"""
        from star_nest.armory.wenjian_gongju import xieru_wenjian
        r = xieru_wenjian("some_text_without_path")
        self.assertFalse(r["success"])

    def test_gj_013_shell_echo(self):
        """Shell·echo命令"""
        from star_nest.armory.shell_mingling import execution_mingling
        r = execution_mingling("echo test_ok")
        self.assertTrue(r["success"])

    def test_gj_014_shell_bad_command(self):
        """Shell·坏命令返回失败"""
        from star_nest.armory.shell_mingling import execution_mingling
        r = execution_mingling("this_command_does_not_exist_abc123")
        self.assertFalse(r["success"])

    def test_gj_015_shell_duo_mulu(self):
        """Shell·多目录执行"""
        from star_nest.armory.shell_mingling import execution_mingling
        r = execution_mingling("echo hi", chaoshi=5)
        self.assertTrue(r["success"])
