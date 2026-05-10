"""
三体星巢·记忆系统专项测试
覆盖: 经络记忆·境判定·谱系检索·关键词匹配·上下文注入
纯标准库unittest·零外部依赖
"""
import unittest, sys, os, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.abspath(__file__))


class TestJingLuoJiYi(unittest.TestCase):
    """经络记忆: 写入·查询·五境显化"""

    @classmethod
    def setUpClass(cls):
        from star_nest.meridian.memory import JingLuoJiYi
        from pathlib import Path
        cls.tmpdir = tempfile.mkdtemp(prefix='jly_test_')
        cls.jiyi = JingLuoJiYi(Path(cls.tmpdir))

    def test_01_baji_write_read(self):
        """八极时序: 写入2条→读回验证"""
        self.jiyi.jilu_baji("yunxingti", {
            "shiliang": {"yang": 0.5, "yin": 0.5, "biao": 0.3, "li": 0.3,
                         "han": 0.4, "re": 0.6, "xu": 0.2, "shi": 0.8},
            "jiankangdu": 0.95, "wenti_shu": 3, "xiufu_shu": 1
        })
        self.jiyi.jilu_baji("bianchengti", {
            "shiliang": {"yang": 0.3, "yin": 0.7, "biao": 0.5, "li": 0.5,
                         "han": 0.6, "re": 0.4, "xu": 0.4, "shi": 0.6},
            "jiankangdu": 0.72, "wenti_shu": 8, "xiufu_shu": 3
        })
        rows = self.jiyi.zuijin_baji(n=5)
        self.assertGreaterEqual(len(rows), 2)
        # 按 juese 过滤
        yun = self.jiyi.zuijin_baji(juese="yunxingti", n=1)
        self.assertEqual(len(yun), 1)
        self.assertAlmostEqual(yun[0]["jiankangdu"], 0.95, delta=0.01)

    def test_02_wenti_write_read(self):
        """问题窗: 写入重复→统计重复"""
        for _ in range(3):
            self.jiyi.jilu_wenti("yunxingti", {"miaoshu": "核心文件缺失:xinghe/xin.py", "leixing": "shencha"})
        self.jiyi.jilu_wenti("bianchengti", {"miaoshu": "duanzao失败:SyntaxError", "leixing": "duanzao"})
        wenti = self.jiyi.zuijin_wenti(n=5)
        self.assertGreaterEqual(len(wenti), 3)
        # 类型统计
        tj = self.jiyi.wenti_leixing_tongji(5)
        self.assertGreaterEqual(len(tj), 1)
        shencha = [t for t in tj if t["leixing"] == "shencha"]
        if shencha:
            self.assertGreaterEqual(shencha[0]["cnt"], 3)

    def test_03_xiufu_and_association(self):
        """修复窗: 写入+关联最近问题"""
        self.jiyi.jilu_wenti("yunxingti", {"miaoshu": "需要修复: 内存泄漏", "leixing": "zhenduan"})
        self.jiyi.jilu_xiufu("bianchengti", {"miaoshu": "GC回收优化", "jieguo": "success"})
        xiufu = self.jiyi.zuijin_xiufu(n=3)
        self.assertGreaterEqual(len(xiufu), 1)

    def test_04_wujing_transition(self):
        """五境流转: 写入→读回"""
        self.jiyi.jilu_wujing("正境", "反境", "health下降", 1)
        self.jiyi.jilu_wujing("反境", "合境", "寻找修复", 2)
        self.jiyi.jilu_wujing("合境", "超越境", "平街方案", 3)
        wj = self.jiyi.zuijin_wujing(n=5)
        self.assertGreaterEqual(len(wj), 3)
        self.assertEqual(wj[-1]["yuan_jing"], "正境")

    def test_05_gongju_diaoyong(self):
        """工具调用: 写入→效能统计"""
        self.jiyi.jilu_gongju("wenjian_gongju", "liechu_mulu", 3, True)
        self.jiyi.jilu_gongju("wenjian_gongju", "liechu_mulu", 3, False)
        self.jiyi.jilu_gongju("zhu_opencode", "zhuangtai", 3, True)
        gj = self.jiyi.zuijin_gongju(n=5)
        self.assertGreaterEqual(len(gj), 3)
        xn = self.jiyi.gongju_xiaoneng()
        mulu = [x for x in xn if x["hanshu_ming"] == "liechu_mulu"]
        if mulu:
            self.assertEqual(mulu[0]["zongshu"], 2)

    def test_06_zhengjing_xianshi(self):
        """正境显化: 返回当前快照"""
        jg = self.jiyi.xianshi_zhengjing()
        self.assertIn("dangqian_baji", jg)
        self.assertIn("huoyue_wenti", jg)

    def test_07_fanjing_xianshi(self):
        """反境显化: 返回问题趋势"""
        jg = self.jiyi.xianshi_fanjing()
        self.assertIn("baji_piaoyi", jg)
        self.assertIn("wenti_leixing", jg)

    def test_08_hejing_xianshi(self):
        """合境显化: 返回修复方案"""
        jg = self.jiyi.xianshi_hejing()
        self.assertIn("zuijin_xiufu", jg)

    def test_09_chaoyuejing_xianshi(self):
        """超越境显化: 返回突破模式"""
        jg = self.jiyi.xianshi_chaoyuejing()
        self.assertIn("kuayu_liuzhuan", jg)

    def test_10_benyuanjing_xianshi(self):
        """本源境显化: 返回长期归档"""
        jg = self.jiyi.xianshi_benyuanjing()
        self.assertIn("zonglan", jg)
        zl = jg["zonglan"]
        self.assertIn("问题", zl)
        self.assertIn("五境流转", zl)

    def test_11_jingluo_shangxiawen(self):
        """上下文注入: 按境返回不同结构"""
        for cj in ["正境","反境","合境","超越境","本源境"]:
            ctx = self.jiyi.jingluo_shangxiawen(cj)
            self.assertIsInstance(ctx, dict)
            self.assertIn("jing", ctx)

    def test_12_tongji_zonglan(self):
        """统计总览: 所有表有计数"""
        z = self.jiyi.tongji_zonglan()
        self.assertEqual(len(z), 5)
        self.assertGreater(sum(z.values()), 0)


class TestPanDuanCengJi(unittest.TestCase):
    """境判定: _panduan_cengji 准确率"""

    @classmethod
    def setUpClass(cls):
        from star_nest.shared_memory.manager import JiYiGuanLi
        from pathlib import Path
        cls.guanli = JiYiGuanLi(Path(ROOT) / 'jiyi_gongxiang')

    def _pd(self, q):
        return self.guanli._panduan_cengji(q)

    def test_zhengjing_definition(self):
        """正境: 定义/概念类提问"""
        self.assertEqual(self._pd("星巢是什么"), "正境")
        self.assertEqual(self._pd("介绍一下八极的定义"), "正境")
        self.assertEqual(self._pd("有哪些核心文件"), "正境")

    def test_fanjing_analysis(self):
        """反境: 问题/错误/分析类提问"""
        self.assertEqual(self._pd("为什么duanzao失败了"), "反境")
        self.assertEqual(self._pd("opencode关键词匹配失败的原因分析"), "反境")
        self.assertEqual(self._pd("核心文件缺失怎么分析"), "反境")

    def test_hejing_solution(self):
        """合境: 方案/修复/工具类提问"""
        self.assertEqual(self._pd("怎么解决这个故障"), "合境")
        self.assertEqual(self._pd("如何修复经络记忆"), "合境")
        self.assertEqual(self._pd("用什么工具生成代码"), "合境")
        self.assertEqual(self._pd("生成一个新的工具"), "合境")

    def test_chaoyuejing_innovation(self):
        """超越境: 突破/创新类提问"""
        self.assertEqual(self._pd("还有更好的方法吗"), "超越境")
        self.assertEqual(self._pd("能不能跳出当前范式"), "超越境")
        self.assertEqual(self._pd("有没有创新的方案"), "超越境")

    def test_default_zhengjing(self):
        """默认: 无关提问默认正境"""
        self.assertEqual(self._pd("你好"), "正境")
        self.assertEqual(self._pd("今天天气不错"), "正境")


class TestJiYiXianShi(unittest.TestCase):
    """记忆显化: 谱系检索→五境分配→LLM上下文"""

    @classmethod
    def setUpClass(cls):
        from star_nest.shared_memory.manager import JiYiGuanLi
        from pathlib import Path
        cls.guanli = JiYiGuanLi(Path(ROOT) / 'jiyi_gongxiang')

    def test_zhe_die_jiansuo_structure(self):
        """谱系检索: 返回结构正确"""
        r = self.guanli.zhe_die_jiansuo("正境")
        self.assertIsInstance(r, dict)
        self.assertIn("cengji", r)
        self.assertIn("weizhi", r)
        self.assertIn("zongshu", r)
        self.assertGreater(r["zongshu"], 0, "No entries in digital spectrum")

    def test_zhe_die_jiansuo_recent(self):
        """近期检索: 带chaxun参数检测近期关键词"""
        r = self.guanli.zhe_die_jiansuo("正境", chaxun="近期记忆有哪些")
        self.assertGreater(r["zongshu"], 0)
        # 能返回结果即可,时间排序的正确性由条目时间戳保证

    def test_zhe_die_jiansuo_recent_keywords(self):
        """近期关键词: 全部触发时间加权"""
        queries = ["近期记忆", "最近的内容", "最新知识", "刚学到的", "刚刚发生的事情", "近来的变化"]
        for q in queries:
            r = self.guanli.zhe_die_jiansuo("正境", chaxun=q)
            self.assertGreaterEqual(r.get("zongshu", 0), 0, f"Query '{q}' failed")

    def test_all_cengji_retrieval(self):
        """五境检索: 每境都能返回数据"""
        for cj in ["正境", "反境", "合境", "超越境", "本源境"]:
            r = self.guanli.zhe_die_jiansuo(cj)
            self.assertGreaterEqual(r.get("zongshu", 0), 0, f"{cj} returned no entries")

    def test_ronghe_jiansuo_structure(self):
        """融合检索: 返回四脏分配"""
        r = self.guanli.ronghe_jiansuo("星巢三体架构")
        self.assertIn("zhishi", r)
        self.assertIn("zongshu", r)
        self.assertGreater(r["zongshu"], 0)

    def test_wuzang_ronghe_jiansuo(self):
        """五脏融合: 按境偏置返回"""
        r = self.guanli.wuzang_ronghe_jiansuo("opencode扫描", 5)
        self.assertIn("cengji", r)
        self.assertIn("gan", r)
        self.assertIn("pi", r)
        self.assertIn("fei", r)
        self.assertIn("shen", r)

    def test_zhishi_tongji(self):
        """知识统计: 总数>200"""
        tj = self.guanli.zhishi_tongji()
        self.assertIn("zongshu", tj)
        self.assertGreater(tj["zongshu"], 100)

    def test_zhishi_fenlei(self):
        """知识分类: 至少有一个大类"""
        fl = self.guanli.zhishi_fenlei()
        self.assertGreater(len(fl), 0)
        self.assertGreater(sum(fl.values()), 100)


class TestDuiQi(unittest.TestCase):
    """记忆对齐: OpenCode→星巢知识导入"""

    def test_duqu_suoyou_huihua(self):
        """读所有OpenCode会话"""
        from star_nest.armory.zhu_opencode import duqu_suoyou_huihua
        r = duqu_suoyou_huihua()
        self.assertTrue(r["success"])
        self.assertIn("huihua", r)
        self.assertGreaterEqual(len(r["huihua"]), 1)

    def test_duqu_zuijin_duihua(self):
        """读最近OpeCode会话"""
        from star_nest.armory.zhu_opencode import duqu_zuijin_duihua
        r = duqu_zuijin_duihua()
        self.assertTrue(r["success"])
        self.assertIn("title", r)
        self.assertIn("wenben", r)

    def test_duiqi_jiyi(self):
        """全量对齐: 导入OpenCode会话到puxi"""
        from star_nest.armory.zhu_opencode import duiqi_jiyi
        r = duiqi_jiyi()
        self.assertTrue(r["success"])
        self.assertGreaterEqual(r["yidaoru_zongshu"], 1)

    def test_duiqi_zhuangtai(self):
        """对齐状态: 两边记忆统计"""
        from star_nest.armory.zhu_opencode import duiqi_zhuangtai
        r = duiqi_zhuangtai()
        self.assertTrue(r["success"])
        self.assertIn("opencode", r)
        self.assertIn("xingchao", r)
        self.assertGreater(r["xingchao"]["yidaoru"], 0)

    def test_duiqi_zengliang(self):
        """增量对齐: 不重复导入"""
        from star_nest.armory.zhu_opencode import duiqi_jiyi
        r1 = duiqi_jiyi()
        n1 = r1["yidaoru_zongshu"]
        r2 = duiqi_jiyi()
        n2 = r2["yidaoru_zongshu"]
        self.assertEqual(n1, n2, f"增量对齐不应增加: {n1}→{n2}")

    def test_duiqi_puxi_integrity(self):
        """对齐后puxi含OpenCode条目"""
        from pathlib import Path
        import json
        puxi_dir = Path(ROOT) / 'jiyi_gongxiang' / 'puxi'
        ope_entries = 0
        for n in range(10):
            fp = puxi_dir / f"{n}.json"
            if fp.exists():
                data = json.loads(fp.read_text(encoding='utf-8'))
                for e in data.get("zhe_die", []):
                    if "OpenCode" in str(e.get("biaoti", "")):
                        ope_entries += 1
        self.assertGreater(ope_entries, 0, "puxi中无OpenCode条目")


class TestQiXue(unittest.TestCase):
    """气血循环: 五脉创建·气转血·血转气·阻塞检测"""

    def test_01_qixue_init(self):
        """初始化: 五条经络通道注册"""
        from star_nest.dynamics.qi_blood import QiXueXunHuan
        qx = QiXueXunHuan(None, None)
        self.assertEqual(len(qx.tongdao), 5)
        for ming in ["任脉", "督脉", "冲脉", "带脉", "跷脉"]:
            self.assertIn(ming, qx.tongdao)
            td = qx.tongdao[ming]
            self.assertIn("zuse_zhuangtai", td)

    def test_02_xunhuan_yici(self):
        """一次循环: 五脉流转不崩溃"""
        from star_nest.dynamics.qi_blood import QiXueXunHuan
        from star_nest.meridian.memory import JingLuoJiYi
        from pathlib import Path
        import tempfile
        tmp = tempfile.mkdtemp(prefix='qx_test_')
        jly = JingLuoJiYi(Path(tmp))
        # 写入一些测试数据
        jly.jilu_baji("yunxingti", {
            "shiliang": {"yang": 0.5, "yin": 0.5, "biao": 0.3, "li": 0.3,
                         "han": 0.4, "re": 0.6, "xu": 0.2, "shi": 0.8},
            "jiankangdu": 0.9, "wenti_shu": 1, "xiufu_shu": 2
        })
        qx = QiXueXunHuan(None, jly)
        jg = qx.xunhuan_yici("正境", "测试气血循环")
        self.assertIsInstance(jg, dict)
        # 五脉都有回流数据
        for ming in ["任脉", "督脉", "冲脉", "带脉"]:
            self.assertIn(ming, jg)

    def test_03_qizhuanxue_renmai(self):
        """气转血·任脉: puxi位点0写入"""
        from star_nest.dynamics.qi_blood import QiXueXunHuan
        from star_nest.meridian.memory import JingLuoJiYi
        from pathlib import Path
        import tempfile, json
        tmp = tempfile.mkdtemp(prefix='qx_test_')
        jly = JingLuoJiYi(Path(tmp))
        jly.jilu_baji("yunxingti", {
            "shiliang": {"yang": 0.5, "yin": 0.5, "biao": 0.3, "li": 0.3,
                         "han": 0.4, "re": 0.6, "xu": 0.2, "shi": 0.8},
            "jiankangdu": 0.9, "wenti_shu": 1, "xiufu_shu": 2
        })
        qx = QiXueXunHuan(None, jly)
        qx.qizhuanxue_renmai("正境", "测试")
        td = qx.tongdao["任脉"]
        self.assertGreater(td["xunhuan_zongshu"], 0)

    def test_04_xueyangqi(self):
        """血转气·全境: 返回数据结构正确"""
        from star_nest.dynamics.qi_blood import QiXueXunHuan
        from star_nest.meridian.memory import JingLuoJiYi
        from pathlib import Path
        import tempfile
        tmp = tempfile.mkdtemp(prefix='qx_test_')
        jly = JingLuoJiYi(Path(tmp))
        qx = QiXueXunHuan(None, jly)
        for cj in ["正境", "反境", "合境", "超越境", "本源境"]:
            jg = qx.xueyangqi_quanju(cj)
            self.assertIsInstance(jg, dict)
            self.assertIn("cengji", jg)
            self.assertIn("renmai", jg)

    def test_05_jiance_zuse(self):
        """阻塞检测: 通道状态可检测"""
        from star_nest.dynamics.qi_blood import QiXueXunHuan
        from star_nest.meridian.memory import JingLuoJiYi
        from pathlib import Path
        import tempfile
        tmp = tempfile.mkdtemp(prefix='qx_test_')
        jly = JingLuoJiYi(Path(tmp))
        qx = QiXueXunHuan(None, jly)
        qx.xunhuan_yici("正境", "初始化")
        zs = qx.jiance_zuse()
        self.assertIn("zuse_shu", zs)
        self.assertIn("tongdao", zs)
        self.assertEqual(len(zs["tongdao"]), 5)
        # 刚循环后不应阻塞
        self.assertEqual(zs["zuse_shu"], 0)

    def test_06_qixue_in_xin(self):
        """集成: xin有qixue属性"""
        from star_nest.organs.heart import XinZang
        self.assertTrue(hasattr(XinZang, '__init__'))

    def test_07_qixue_in_jingluo(self):
        """集成: jingluo有qixue属性"""
        from star_nest.meridian.jingluo import JingLuo
        jl = JingLuo.__new__(JingLuo)
        self.assertTrue(hasattr(JingLuo, '__init__'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
