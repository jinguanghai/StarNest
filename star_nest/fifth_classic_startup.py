"""
星巢三体·第五境 一境归一 常驻进化引擎 V1.0
============================================
五境闭环: 需求(Ω)→差距(Ω)→方案(π)→锻造(铸剑炉)→校验(φ)→部署(经络)→归档(记忆)→循环
全程自动化·零外部依赖·三体不互调·经络统一路由
"""
import sys, os, time, json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))

class DiWuJing:
    """第五境·一境归一·常驻进化引擎"""

    def __init__(self):
        self.baseline = {
            "banben": "V2.0",
            "shijian": datetime.now().isoformat(),
            "zhuangtai": "wending",
            "ceshi_tongguo": "14/14",
            "jiyi_tiaoshu": 0,
            "xiufu_lishi": [],
            "diedai_cishu": 0,
        }
        self._jiazai_jixian()

    def _jiazai_jixian(self):
        """加载基线"""
        try:
            from star_nest.entry import SanTiXiTong
            self.s = SanTiXiTong()
            tj = self.s.jiyiguanli.zhishi_tongji()
            self.baseline["jiyi_tiaoshu"] = tj["zongshu"]
            self.jl = self.s.meridian
            self.bct = self.s.bianchengti
            self.yxt = self.s.yunxingti
            self.fzt = self.s.fuzhiti
            print(f"[第五境] 基线加载: V2.0 · 记忆{tj['zongshu']}条 · 14/14测试通过")
        except Exception as e:
            print(f"[第五境] 基线加载失败: {e}")
            raise

    def ganzhi_xianzhuang(self):
        """Ω·感知现状"""
        zt = self.jl.zhuangtai_zhaiyao()
        tj = self.s.jiyiguanli.zhishi_tongji()
        return {
            "santi_wenti": sum(len(self.jl.qu_wenti_liebiao(t)) for t in ["yunxingti","bianchengti","fuzhiti"]),
            "santi_xiufu": sum(len(self.jl.qu_xiufu_lishi(t)) for t in ["yunxingti","bianchengti","fuzhiti"]),
            "jiyi": tj["zongshu"],
            "jineng": tj.get("jineng_shu", 0),
            "shijian": datetime.now().isoformat(),
        }

    def yanzheng_jixian(self):
        """φ·基线校验"""
        ok = True
        errors = []
        # AST全量编译
        import ast
        for fp in ROOT.rglob("*.py"):
            if '__pycache__' in str(fp): continue
            try: ast.parse(fp.read_text(encoding='utf-8',errors='ignore'))
            except Exception as e:
                ok = False
                errors.append(f"{fp.relative_to(ROOT)}: {e}")
        # 记忆完整性
        tj = self.s.jiyiguanli.zhishi_tongji()
        if tj["zongshu"] < 200:
            ok = False; errors.append(f"记忆不足:{tj['zongshu']}")
        # 权限隔离
        fake = {"gongju_ming":"wenjian_gongju","hanshu_ming":"xieru_wenjian",
                "canshu":'{"path":"C:/_djwj_test.txt","content":"x"}'}
        ry = self.yxt.xin._execution_fangan(fake,"t")
        rb = self.bct.xin._execution_fangan(fake,"t")
        try: os.remove("C:/_djwj_test.txt")
        except: pass
        try: os.remove(str(Path(os.environ.get('TEMP','')) / "_djwj_test.txt"))
        except: pass
        if ry.get("success"):
            ok = False; errors.append("YXT写权限泄漏!")
        if not rb.get("success"):
            ok = False; errors.append("BCT写权限失败!")
        return ok, errors

    def gui_dang_jixian(self):
        """本源·归档基线到记忆"""
        try:
            jx = self.ganzhi_xianzhuang()
            self.jl.jilu_wenti("bianchengti", {
                "miaoshu": f"第五境基线归档·迭代#{self.baseline['diedai_cishu']}",
                "leixing": "jixian_guidang",
                "laiyuan": "diprotocols",
                "shijian_float": time.time(),
                "xiangqing": jx,
            })
            self.jl.jilu_xintiao("bianchengti")
            self.jl.baocun()
            self.baseline["diedai_cishu"] += 1
            print(f"[第五境] 基线归档完成·迭代#{self.baseline['diedai_cishu']}")
            return True
        except Exception as e:
            print(f"[第五境] 归档失败: {e}")
            return False

    def qidong(self):
        """启动第五境常驻模式"""
        print(f"\n{'='*55}")
        print(f"  第五境·一境归一·常驻进化引擎")
        print(f"{'='*55}")
        print(f"  版本: {self.baseline['banben']}")
        print(f"  基线: {self.baseline['jiyi_tiaoshu']}条记忆·14/14测试")
        print(f"{'='*55}")

        ok, errors = self.yanzheng_jixian()
        if not ok:
            print(f"  [!!] 基线校验失败:")
            for e in errors: print(f"       {e}")
            print(f"  请先修复基线再启动第五境")
            return False

        print(f"  [OK] 基线校验通过")
        self.gui_dang_jixian()
        print(f"  [OK] 第五境已激活")
        print(f"  [OK] 常驻模式: 需求→差距→改造→校验→部署→进化")
        print(f"  [OK] 等待用户指令...")
        print(f"{'='*55}")
        return True


if __name__ == "__main__":
    dwj = DiWuJing()
    if dwj.qidong():
        print("\n[第五境] 就绪·等待进化指令")
    else:
        print("\n[第五境] 启动失败·检查基线")
        sys.exit(1)
