"""
软件操作层 RuanJianCeng V1.0 [星巢·软件操作引擎]
任何软件→知识查询→脚本生成→沙箱执行→文件输出
纯Python标准库·零外部依赖
"""
import os, json, tempfile, subprocess, time, re
from pathlib import Path
from datetime import datetime


class RuanJianCeng:
    """软件操作层: 让星巢学会操作任意软件"""

    def __init__(self, xin):
        self.xin = xin
        self.jiao_ben_mulu = Path(__file__).parent.parent / "armory" / "ruanjian"
        self.jiao_ben_mulu.mkdir(parents=True, exist_ok=True)
        self._cao_zuo_lishi = []

    # ==================== Step 1: 知识查询 ====================

    def ruan_jian_zhi_shi(self, xuqiu: str) -> dict:
        """LLM即时查询: 什么软件能做什么? 怎么用Python操作?"""
        if not self.xin.llm:
            return {"ruan_jian": "未知", "fang_fa": "无", "bu_zhou": [], "cuo_wu": "LLM未连接"}

        from star_nest.protocols.cognition_package import RenzhiBao
        bao = RenzhiBao("正境")
        bao.shu_ju(
            xuqiu=xuqiu,
            yao_qiu=(
                "用户想用软件完成任务。返回JSON:"
                '{"ruan_jian":"推荐软件名","fang_fa":"Python API/CLI/无编程接口",'
                '"xia_zai":"下载地址或说明","bu_zhou":["步骤1","步骤2",...],"zhu_yi":"注意事项"}'
                "选软件原则: 免费优先>有Python API优先>命令行优先。如果没有可编程接口, 返回fang_fa=无编程接口"
            )
        )
        try:
            jg = self.xin.llm.chat([{"role": "user", "content": bao.to_json()}], wendu=0.2, zuidazifu=600)
            # 解析JSON
            if "```json" in str(jg):
                start = str(jg).index("```json") + 7
                end = str(jg).index("```", start)
                jg = str(jg)[start:end]
            elif "{" in str(jg):
                start = str(jg).index("{")
                end = str(jg).rindex("}") + 1
                jg = str(jg)[start:end]
            return json.loads(jg)
        except Exception:
            return {"ruan_jian": "未知", "fang_fa": "需要更多信息",
                    "bu_zhou": [], "cuo_wu": f"解析失败:{str(jg)[:100]}"}

    # ==================== Step 2: 生成操作脚本 ====================

    def sheng_cheng_jiao_ben(self, xuqiu: str, zhi_shi: dict = None) -> dict:
        """铸剑炉锻造: 生成操作目标软件的纯Python脚本"""
        if not zhi_shi:
            zhi_shi = self.ruan_jian_zhi_shi(xuqiu)

        ruan_jian = zhi_shi.get("ruan_jian", "未知软件")
        fang_fa = zhi_shi.get("fang_fa", "")
        bu_zhou = zhi_shi.get("bu_zhou", [])
        zhu_yi = zhi_shi.get("zhu_yi", "")

        if fang_fa == "无编程接口":
            return {"success": False,
                    "error": f"{ruan_jian}无编程接口, 无法自动操作。建议: {zhu_yi or '手动操作或寻找替代软件'}"}

        # 构造铸剑炉需求
        duanzao_xuqiu = (
            f"生成一个Python脚本，用于操作{ruan_jian}。\n"
            f"方法: {fang_fa}\n"
            f"步骤: {', '.join(bu_zhou)}\n"
            f"注意事项: {zhu_yi}\n"
            f"要求: 纯Python stdlib + {ruan_jian} API。脚本最后输出文件路径。\n"
            f"原始需求: {xuqiu}"
        )

        if self.xin.zhujianlu:
            jieguo = self.xin.zhujianlu.duanzao(duanzao_xuqiu)
            if jieguo and jieguo.get("success"):
                return {"success": True, "jiao_ben": jieguo.get("output", ""),
                        "gong_ju": jieguo.get("gongju", ""), "zhi_shi": zhi_shi}
            return {"success": False, "error": jieguo.get("error", "锻造失败") if jieguo else "锻造返回空"}

        return {"success": False, "error": "铸剑炉未连接"}

    # ==================== Step 3: 沙箱执行 ====================

    def zhi_xing_jiao_ben(self, jiao_ben_lujing: str, chaoshi: int = 120) -> dict:
        """沙箱执行脚本: subprocess隔离+超时+输出检查"""
        lujing = Path(jiao_ben_lujing)
        if not lujing.exists():
            return {"success": False, "error": f"脚本不存在: {jiao_ben_lujing}"}

        try:
            sandbox = Path(tempfile.mkdtemp(prefix="xingchao_sandbox_"))
            result = subprocess.run(
                ["python", str(lujing)],
                cwd=str(sandbox),
                capture_output=True, text=True,
                timeout=chaoshi,
                env={**os.environ, "PYTHONPATH": str(lujing.parent)}
            )
            output_files = list(sandbox.glob("*"))
            return {
                "success": result.returncode == 0,
                "output": result.stdout[:2000] if result.stdout else result.stderr[:500],
                "return_code": result.returncode,
                "sheng_cheng_wen_jian": [str(f.relative_to(sandbox)) for f in output_files],
                "sha_xiang_mu_lu": str(sandbox),
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"脚本执行超时({chaoshi}s)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== Step 4: 输出交付 ====================

    def jiao_fu(self, zhi_xing_jie_guo: dict, xuqiu: str = "") -> str:
        """验证输出→生成交付信息"""
        if not zhi_xing_jie_guo.get("success"):
            return f"[软件操作] 执行失败: {zhi_xing_jie_guo.get('error', '未知错误')}"

        files = zhi_xing_jie_guo.get("sheng_cheng_wen_jian", [])
        if not files:
            return f"[软件操作] 执行完成但未生成文件。输出: {zhi_xing_jie_guo.get('output', '')[:300]}"

        file_list = "\n".join(f"  - {f}" for f in files)
        sha_xiang = zhi_xing_jie_guo.get("sha_xiang_mu_lu", "")
        return f"[软件操作] ✅ 已生成 {len(files)} 个文件:\n{file_list}\n\n文件路径: {sha_xiang}"

    # ==================== 一站式入口 ====================

    def cao_zuo_ruan_jian(self, xuqiu: str) -> dict:
        """一站式: 知识查询→脚本生成→沙箱执行→交付"""
        kaishi = time.time()
        self._cao_zuo_lishi.append({"xuqiu": xuqiu, "shijian": datetime.now().isoformat()})

        # Step 1: 知识查询
        zhi_shi = self.ruan_jian_zhi_shi(xuqiu)
        if zhi_shi.get("cuo_wu"):
            return {"success": False, "error": f"知识查询失败: {zhi_shi['cuo_wu']}", "zhi_shi": zhi_shi}

        ruan_jian = zhi_shi.get("ruan_jian", "未知")

        # Step 2: 生成脚本
        jiao_ben = self.sheng_cheng_jiao_ben(xuqiu, zhi_shi)
        if not jiao_ben.get("success"):
            return {"success": False, "error": f"脚本生成失败: {jiao_ben.get('error','')}",
                    "zhi_shi": zhi_shi, "jian_yi": f"可尝试手动操作{ruan_jian}或寻找替代方案"}

        # Step 3: 沙箱执行
        script_path = jiao_ben.get("gong_ju", "")
        if not script_path:
            # 尝试从armory/查找
            gong_ju = jiao_ben.get("gong_ju", "")
            if gong_ju:
                script_path = str(self.jiao_ben_mulu / f"{gong_ju}.py")

        if script_path and Path(script_path).exists():
            zhi_xing = self.zhi_xing_jiao_ben(script_path)
        else:
            # 脚本可能被存入藏剑阁, 尝试扫描
            found = list(self.jiao_ben_mulu.rglob("*.py"))
            if found:
                zhi_xing = self.zhi_xing_jiao_ben(str(found[-1]))
            else:
                zhi_xing = {"success": False, "error": "未找到生成的脚本文件"}

        # Step 4: 交付
        jiao_fu = self.jiao_fu(zhi_xing, xuqiu)

        # 记录经络
        if self.xin.meridian and hasattr(self.xin.meridian, 'jilu_fansi'):
            try:
                self.xin.meridian.jilu_fansi(
                    f"[软件操作] {ruan_jian}: {'成功' if zhi_xing.get('success') else '失败'} "
                    f"耗时{round(time.time()-kaishi,1)}s"
                )
            except Exception: pass

        return {
            "success": zhi_xing.get("success", False),
            "ruan_jian": ruan_jian,
            "zhi_shi": zhi_shi,
            "zhi_xing": zhi_xing,
            "jiao_fu": jiao_fu,
            "haoshi": round(time.time() - kaishi, 2),
        }

    def qu_lishi(self):
        return self._cao_zuo_lishi[-10:]
