"""
藏剑阁·测试引擎 主运行器
用法: python -m armory.ceshi [模块名]
       python -m armory.ceshi           # 全部
"""
import unittest, sys, os, time, json
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

class CeshiBaoGao:
    def __init__(self):
        self.tongji = {"pass": 0, "fail": 0, "error": 0, "skip": 0, "xiangqing": []}

    def jieguo(self, moshi, ceshi, shifou_chenggong, cuowu=None):
        if shifou_chenggong:
            self.tongji["pass"] += 1
        elif cuowu and "skip" in str(cuowu).lower():
            self.tongji["skip"] += 1
        else:
            self.tongji["fail"] += 1
            self.tongji["xiangqing"].append((moshi, str(ceshi), str(cuowu)[:200] if cuowu else ""))

    def shengcheng(self, kaishi_shijian, moshi_liebiao):
        haoshi = round(time.time() - kaishi_shijian, 2)
        zong = self.tongji["pass"] + self.tongji["fail"] + self.tongji["skip"]
        lv = round(100 * self.tongji["pass"] / max(zong, 1), 1)

        print(f"\n{'='*55}")
        print(f"  星巢三体自迭代 V2.0 · 逐模块测试报告")
        print(f"{'='*55}")
        print(f"  测试模块: {len(moshi_liebiao)}  |  耗时: {haoshi}s")
        print(f"  通过: {self.tongji['pass']}  |  失败: {self.tongji['fail']}  |  跳过: {self.tongji['skip']}")
        print(f"  通过率: {lv}%")
        print(f"{'='*55}")

        if self.tongji["xiangqing"]:
            print(f"\n  失败详情:")
            for m, c, e in self.tongji["xiangqing"][:15]:
                print(f"    [{m}] {c}")
                print(f"      -> {e}")

        print(f"\n  测试覆盖:")
        for moshi in moshi_liebiao:
            print(f"    [+] {moshi}")
        return self.tongji["fail"] == 0

baogao = CeshiBaoGao()

def ceshi_mokuai(moshi, ceshi_lei):
    try:
        suite = unittest.TestLoader().loadTestsFromTestCase(ceshi_lei)
        runner = unittest.TextTestRunner(verbosity=0)
        jieguo = runner.run(suite)
        for _ in range(jieguo.testsRun):
            baogao.jieguo(moshi, moshi, True)
        for _, tb in jieguo.failures + jieguo.errors:
            baogao.tongji["fail"] += 1
            baogao.tongji["xiangqing"].append((moshi, moshi, str(tb)[:200]))
            baogao.tongji["pass"] -= 1
    except Exception as e:
        baogao.tongji["fail"] += 1
        baogao.tongji["xiangqing"].append((moshi, moshi, str(e)[:200]))

if __name__ == "__main__":
    kaishi = time.time()
    moshi_liebiao = []

    ceshi_mokuai = ceshi_mokuai

    from star_nest.armory.tests.ceshi_xin import TestXinZang
    ceshi_mokuai("心", TestXinZang); moshi_liebiao.append("心")

    from star_nest.armory.tests.ceshi_channel import TestJingLuo
    ceshi_mokuai("经络", TestJingLuo); moshi_liebiao.append("经络")

    from star_nest.armory.tests.ceshi_zhujianlu import TestZhuJianLu
    ceshi_mokuai("铸剑炉", TestZhuJianLu); moshi_liebiao.append("铸剑炉")

    from star_nest.armory.tests.ceshi_jiyi import TestJiYi
    ceshi_mokuai("记忆", TestJiYi); moshi_liebiao.append("记忆")

    from star_nest.armory.tests.ceshi_armory import TestCangJianGe
    ceshi_mokuai("藏剑阁", TestCangJianGe); moshi_liebiao.append("藏剑阁")

    from star_nest.armory.tests.ceshi_jiemian import TestJieMian
    ceshi_mokuai("界面", TestJieMian); moshi_liebiao.append("界面")

    from star_nest.armory.tests.ceshi_quanxian import TestQuanXian
    ceshi_mokuai("权限", TestQuanXian); moshi_liebiao.append("权限")

    from star_nest.armory.tests.ceshi_gongju import TestGongJu
    ceshi_mokuai("工具", TestGongJu); moshi_liebiao.append("工具")

    from star_nest.armory.tests.ceshi_protocols import TestWuJing
    ceshi_mokuai("五境", TestWuJing); moshi_liebiao.append("五境")

    from star_nest.armory.tests.ceshi_dynamics import TestDongLiXue
    ceshi_mokuai("动力学", TestDongLiXue); moshi_liebiao.append("动力学")

    from star_nest.armory.tests.ceshi_bianjie import TestBianJie
    ceshi_mokuai("边界", TestBianJie); moshi_liebiao.append("边界")

    ok = baogao.shengcheng(kaishi, sorted(moshi_liebiao))
    sys.exit(0 if ok else 1)
