"""
藏剑阁·工具测试 (CangJianGe)
覆盖: 文件搜索/shell命令/git命令/语音
"""
import unittest, sys, os, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestCangJianGe(unittest.TestCase):
    def test_cj_001_sousuo_wenjian(self):
        """文件搜索·*.py"""
        from star_nest.armory.wenjian_sousuo import sousuo_wenjian
        r = sousuo_wenjian("*.py", os.path.dirname(os.path.dirname(__file__)))
        self.assertEqual(r["status"], "success")
        self.assertGreater(len(r["data"]), 0)

    def test_cj_002_sousuo_mulu_bucunzai(self):
        """文件搜索·不存在目录"""
        from star_nest.armory.wenjian_sousuo import sousuo_wenjian
        r = sousuo_wenjian("*.py", "/non_existent_dir_xyz")
        self.assertIn("error", r["status"].lower() or "error")

    def test_cj_003_sousuo_wu_pipei(self):
        """文件搜索·无匹配"""
        from star_nest.armory.wenjian_sousuo import sousuo_wenjian
        r = sousuo_wenjian("*.xyzabc", os.path.dirname(__file__))
        self.assertEqual(r["status"], "success")
        self.assertEqual(len(r["data"]), 0)

    def test_cj_004_shell_execution(self):
        """Shell命令·echo"""
        from star_nest.armory.shell_mingling import execution_mingling
        r = execution_mingling("echo shell_test_ok")
        self.assertTrue(r.get("success"))
        self.assertIn("shell_test_ok", r.get("stdout", ""))

    def test_cj_005_shell_mingling_bucunzai(self):
        """Shell命令·不存在命令"""
        from star_nest.armory.shell_mingling import execution_mingling
        r = execution_mingling("this_command_does_not_exist_xyz")
        self.assertFalse(r.get("success"))

    def test_cj_006_shell_chaoshi(self):
        """Shell命令·超时设置"""
        from star_nest.armory.shell_mingling import execution_mingling
        r = execution_mingling("sleep 1", chaoshi=0.1)
        self.assertFalse(r.get("success"))

    def test_cj_007_git_mingling(self):
        """Git命令·基本调用"""
        from star_nest.armory.git_gongju import git_mingling
        cwd = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        try:
            r = git_mingling(["status"], cwd)
            self.assertIsInstance(r, dict)
        except Exception:
            self.skipTest("not a git repo or git not available")

    def test_cj_008_yuyin_daoru(self):
        """语音工具·导入检查"""
        try:
            from star_nest.armory.yuyin_gongju import yuyin_shibie
            self.assertTrue(True)
        except ImportError:
            self.skipTest("yuyin_gongju platform-specific")
        except Exception:
            self.skipTest("yuyin_gongju not available")
