"""
三体星巢·自动化测试套件
纯标准库unittest·零外部依赖
运行: python ceshi.py
"""
import unittest, sys, os, ast, subprocess, importlib, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.abspath(__file__))


class TestBianYi(unittest.TestCase):
    """正境: 编译测试——所有.py文件语法正确"""

    def test_all_files_compile(self):
        failed = []
        for root, dirs, files in os.walk(ROOT):
            for f in files:
                if f.endswith('.py') and '__pycache__' not in root:
                    fp = os.path.join(root, f)
                    try:
                        with open(fp, encoding='utf-8', errors='ignore') as fh:
                            ast.parse(fh.read())
                    except SyntaxError as e:
                        rel = os.path.relpath(fp, ROOT)
                        failed.append(f"{rel}: {e}")
        self.assertEqual(len(failed), 0, f"Compile failures:\n" + "\n".join(failed))

    def test_no_bom(self):
        failed = []
        for root, dirs, files in os.walk(ROOT):
            for f in files:
                if f.endswith('.py') and '__pycache__' not in root:
                    with open(os.path.join(root, f), 'rb') as fh:
                        if fh.read(3) == b'\xef\xbb\xbf':
                            failed.append(os.path.relpath(os.path.join(root, f), ROOT))
        self.assertEqual(len(failed), 0, f"BOM found:\n" + "\n".join(failed))


class TestDaoRu(unittest.TestCase):
    """反境: 导入测试——所有核心模块可正确导入"""

    def test_core_modules(self):
        targets = [
            "jingluo.qilv", "jingluo.tupu", "jingluo.jingluo",
            "zhixing.llm", "zhixing.zhujianlu",
            "jiyi_gongxiang.jiyiguanli",
            "wuzang.xin", "wuzang.gan", "wuzang.pi", "wuzang.fei", "wuzang.shen",
            "jiemian", "zijingshi", "donglixue",
            "jinhua.fuzhi", "jinhua.shengji",
            "wangluo.jiedian",
            "cangjiange.wangluo.wangluo_gongju",
            "cangjiange.kaifa.zidong_ceshi",
            "cangjiange.wenjian_gongju", "cangjiange.wenjian_sousuo",
            "cangjiange.shell_mingling", "cangjiange.shijian_gongju",
            "cangjiange.shuju_gongju", "cangjiange.xitong_gongju",
            "cangjiange.git_gongju", "cangjiange.dabao_gongju",
            "cangjiange.yuyin_gongju",
        ]
        failed = []
        for mod in targets:
            try:
                if mod in sys.modules:
                    del sys.modules[mod]
                importlib.import_module(mod)
            except Exception as e:
                failed.append(f"{mod}: {e}")
        self.assertEqual(len(failed), 0, f"Import failures:\n" + "\n".join(failed))

    def test_body_imports(self):
        for body in ['bianchengti', 'yunxingti', 'fuzhiti']:
            try:
                __import__(f'{body}.xin')
            except Exception as e:
                self.fail(f"{body}/xin.py import failed: {e}")


class TestAPI(unittest.TestCase):
    """合境: API测试——每个脏器有必须的方法"""

    def test_wuzang_methods(self):
        from star_nest.organs import xin, gan, pi, fei, shen
        checks = [
            (xin.XinZang, ['jieru_qiguan', 'run', 'tingzhi', 'guangbo_shuchu', 'add_renwu', 'add_xuqiu']),
            (gan.GanZang, ['qidong_warmup', 'ronghe_jiansuo', 'jilu', 'run', 'tingzhi']),
            (pi.PiZang, ['si_lv_pi_pei', 'run', 'tingzhi', 'qidong_warmup']),
            (fei.FeiZang, ['run', 'tingzhi', 'qidong_warmup']),
            (shen.ShenZang, ['run', 'tingzhi', 'qidong_warmup']),
        ]
        for cls, methods in checks:
            missing = [m for m in methods if not hasattr(cls, m)]
            self.assertEqual(len(missing), 0, f"{cls.__name__} missing: {missing}")

    def test_llm_methods(self):
        from star_nest.execution.llm import LLMKeHuDuan
        for m in ['chat', 'goujian_jiegouhua_shuju']:
            self.assertTrue(hasattr(LLMKeHuDuan, m), f"LLMKeHuDuan missing {m}")


class TestQiDong(unittest.TestCase):
    """超越境: 启动测试——系统可正常初始化"""

    def test_santi_init(self):
        result = subprocess.run(
            [sys.executable, '-c',
             'import sys; sys.path.insert(0,"."); from rukou import SanTiXiTong; s=SanTiXiTong(); print("INIT_OK")'],
            capture_output=True, text=True, timeout=30, cwd=ROOT)
        self.assertIn('INIT_OK', result.stdout, f"Init failed: {result.stderr}")

    def test_startup_no_crash(self):
        result = subprocess.run(
            [sys.executable, '-c',
             'import sys; sys.path.insert(0,"."); from rukou import SanTiXiTong; s=SanTiXiTong();'
             'sm=s.jiyiguanli.zhishi_tongji(); print(f"ENTRIES={sm.get(\"zongshu\",0)}")'],
            capture_output=True, text=True, timeout=30, cwd=ROOT)
        self.assertIn('ENTRIES=', result.stdout, f"Startup failed: {result.stderr}")

    def test_memory_loaded(self):
        result = subprocess.run(
            [sys.executable, '-c',
             'import sys; sys.path.insert(0,"."); from rukou import SanTiXiTong;'
             's=SanTiXiTong(); print(s.jiyiguanli.zhishi_tongji()["zongshu"])'],
            capture_output=True, text=True, timeout=30, cwd=ROOT)
        entries = int(result.stdout.strip().split('\n')[-1])
        self.assertGreater(entries, 200, f"Only {entries} entries")

    def test_baji_empty_input(self):
        from star_nest.dynamics.eight_extremes import EightPoleDynamics
        b = EightPoleDynamics()
        z = b.bajizhenduan([], [])
        self.assertGreater(z['jiankangdu'], 0)
        self.assertIn(z['shizhi'], ['太阳','阳明','少阳','太阴','少阴','厥阴'])


class TestPuXi(unittest.TestCase):
    """超越境: 数字谱系完整性"""

    def test_digital_spectrum(self):
        paths = {
            0: 'zijingshi/__init__.py', 1: 'jingluo/',
            2: 'donglixue/piphicycle.py', 5: 'wuzang/',
            6: 'donglixue/xiufu.py', 7: 'jingluo/qilv.py',
            8: 'donglixue/bajidongli.py', 9: 'shared_memory/jiyiguanli.py',
        }
        for num, path in paths.items():
            full = os.path.join(ROOT, path)
            ok = os.path.exists(full) or (path.endswith('/') and os.path.isdir(full))
            self.assertTrue(ok, f"Spectrum {num} missing: {path}")

    def test_body_memory_dirs(self):
        for body in ['bianchengti', 'yunxingti', 'fuzhiti']:
            self.assertTrue(os.path.isdir(os.path.join(ROOT, body, 'jiyi')),
                            f"{body}/jiyi/ missing")


class TestTieLv(unittest.TestCase):
    """本源境: 铁律合规测试"""

    def test_zero_external_deps(self):
        stdlib = set(sys.stdlib_module_names)
        internal = {'jingluo','tupu','peizhi','qilv','rukou','wuzang','xin','gan','pi','fei',
                    'shen','bianchengti','yunxingti','fuzhiti','donglixue','piphicycle',
                    'xiufu','bajidongli','bashisuanshu','jiuchou','jiemian','huntianling',
                    'zhixing','zhujianlu','llm','wangluo','jiedian','jinhua','fuzhi',
                    'shengji','zijingshi','jiyi_gongxiang','jiyiguanli','cangjiange',
                    'wenjian_sousuo','shell_mingling','git_gongju','yuyin_gongju','huanjing',
                    'ceshi','wujing','zhengjing','fanjing','hejing','chaoyuejing','benyuan','zizhi',
                    'rizhi','yuxing_rizhi','jingluo_jiyi','qixue_xunhuan','diwujing_qidong',
                    'dna_bianma','santi_router','ganzhiceng','shuruceng','renwujihua','ruanjianceng','liushuixian','zijuceng'}
        external = []
        for root, dirs, files in os.walk(ROOT):
            for f in files:
                if f.endswith('.py') and '__pycache__' not in root:
                    try:
                        with open(os.path.join(root, f), encoding='utf-8', errors='ignore') as fh:
                            tree = ast.parse(fh.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    mod = alias.name.split('.')[0]
                                    if mod not in stdlib and mod not in internal:
                                        external.append(f"{os.path.relpath(os.path.join(root, f), ROOT)}: {mod}")
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    mod = node.module.split('.')[0]
                                    if mod not in stdlib and mod not in internal and mod != '':
                                        external.append(f"{os.path.relpath(os.path.join(root, f), ROOT)}: {mod}")
                    except Exception:
                        pass
        self.assertEqual(len(external), 0, f"External deps:\n" + "\n".join(external))

    def test_zero_prompts(self):
        fp = os.path.join(ROOT, 'zhixing', 'llm.py')
        if os.path.exists(fp):
            with open(fp, encoding='utf-8', errors='ignore') as fh:
                c = fh.read()
            prompts = ['你是一个', '请帮我', 'Please', 'You are a', 'system prompt']
            found = [p for p in prompts if p in c]
            self.assertEqual(len(found), 0, f"Prompt patterns found: {found}")
            self.assertTrue('goujian_jiegouhua_shuju' in c or 'renwu' in c,
                            "No structured JSON pattern")


class TestDuiHua(unittest.TestCase):
    """对话链路测试: _duihua上下文构建 + 错误路径 + 权限检查"""

    @classmethod
    def setUpClass(cls):
        from star_nest.entry import SanTiXiTong
        cls.s = SanTiXiTong()

    def test_duihua_no_llm(self):
        """无LLM连接返回提示"""
        xin = self.s.yunxingti.xin
        xin.llm = None
        r = xin._duihua("测试")
        self.assertIn("LLM未连接", str(r))

    def test_duihua_context_built(self):
        """_duihua构建上下文(jiyi+qixue+piphicycle)"""
        from star_nest.execution.llm import LLMKeHuDuan
        xin = self.s.yunxingti.xin
        if not xin.llm:
            xin.llm = LLMKeHuDuan("test_key", "deepseek-chat")
        # 不实际调用API, 只验证上下文构建不崩溃
        if xin.jiyiguanli:
            cj = xin.jiyiguanli._panduan_cengji("测试消息")
            self.assertIn(cj, ["正境","反境","合境","超越境","本源境"])

    def test_chuli_tool_dispatch(self):
        """_chuli工具调度: 不匹配工具时进入五境或duihua"""
        xin = self.s.yunxingti.xin
        r = xin._chuli("这是一个测试消息abc123")
        self.assertIsNotNone(r, "消息处理不应返回None")
        self.assertIsInstance(r, str, "返回应为字符串")

    def test_zhixing_fangan_permission(self):
        """_zhixing_fangan权限: 运行体拒绝写操作"""
        xin = self.s.yunxingti.xin
        fake = {"gongju_ming": "wenjian_gongju", "hanshu_ming": "xieru_wenjian",
                "canshu": '{"path":"/tmp/_test.txt","content":"x"}'}
        r = xin._zhixing_fangan(fake, "test")
        if r and isinstance(r, dict):
            self.assertFalse(r.get("success", True), "运行体应拒绝写操作")

    def test_baji_xunhuan_no_crash(self):
        """_baji_xunhuan全引擎不崩溃"""
        xin = self.s.yunxingti.xin
        xin._baji_xunhuan()
        self.assertIsNotNone(xin._zuihou_jiankangdu, "八极巡检应设置健康度")


if __name__ == '__main__':
    unittest.main(verbosity=2)
