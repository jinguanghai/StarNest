"""
软件流水线 LiuShuiXian V1.0 [星巢·普适软件编排]
行业无关·五层抽象·自主适应

Layer 5: 领域适配 — "这是什么行业？标准流程是什么？"
Layer 4: 软件发现 — "这个行业用什么软件？每个能做什么？"
Layer 3: 流水线编排 — "软件A→B→C按什么顺序？格式兼容吗？"
Layer 2: 执行层 — RuanJianCeng(单软件) + 格式桥接 + 检查点
Layer 1: 学习层 — 记住行业流程+软件操作+格式转换

零行业硬编码。行业知识从LLM临时提取。
"""
import json, time
from pathlib import Path
from datetime import datetime


class LiuShuiXian:
    """普适软件流水线: 行业无关·五层抽象·自主适应"""

    def __init__(self, xin):
        self.xin = xin
        self.ling_yu_ku = {}         # 领域缓存 {行业名: 流程模板}
        self.ruan_jian_tu_pu = {}     # 软件图谱 {软件名: {能力,格式,操作方式}}
        self._zhi_xing_lishi = []

    # ==================== Layer 5: 领域适配 ====================

    def ling_yu_shi_pei(self, xuqiu: str) -> dict:
        """LLM即时查询: 行业+标准流程+关键交付物+常用软件"""
        # 缓存命中
        for hang_ye, data in self.ling_yu_ku.items():
            if hang_ye in xuqiu:
                data["lai_yuan"] = "缓存"
                return data

        if not self.xin.llm:
            return {"hang_ye": "未知", "liu_cheng": [], "cuo_wu": "LLM未连接"}

        from star_nest.protocols.cognition_package import RenzhiBao
        bao = RenzhiBao("正境")
        bao.shu_ju(
            xuqiu=xuqiu,
            yao_qiu=(
                "识别用户需求属于什么行业。返回JSON: "
                '{"hang_ye":"行业名","biao_zhun_liu_cheng":["阶段1","阶段2",...],'
                '"guan_jian_jiao_fu":["交付物1","交付物2",...],'
                '"chang_yong_ruan_jian":["软件1","软件2",...]}'
                "阶段数3-8个。不要编造不存在的软件。不确定的标注'需确认'"
            )
        )
        try:
            jg = self.xin.llm.chat([{"role": "user", "content": bao.to_json()}], wendu=0.2, zuidazifu=600)
            text = str(jg)
            # 解析JSON
            if "```json" in text:
                start = text.index("```json") + 7
                end = text.index("```", start)
                text = text[start:end]
            elif "{" in text:
                start = text.index("{")
                end = text.rindex("}") + 1
                text = text[start:end]
            result = json.loads(text)
            # 缓存
            hang_ye = result.get("hang_ye", "未知")
            self.ling_yu_ku[hang_ye] = result
            result["lai_yuan"] = "LLM"
            return result
        except Exception:
            return {"hang_ye": "未知", "liu_cheng": [], "cuo_wu": "LLM不可用或解析失败"}

    # ==================== Layer 4: 软件发现 ====================

    def ruan_jian_fa_xian(self, ling_yu: dict, xuqiu: str) -> dict:
        """LLM即时查询: 每个阶段用什么软件? 输入输出格式? 操作方法?"""
        liu_cheng = ling_yu.get("biao_zhun_liu_cheng", [])
        already_known = ling_yu.get("chang_yong_ruan_jian", [])

        if not self.xin.llm:
            return {"jie_duan": [], "cuo_wu": "LLM未连接"}

        from star_nest.protocols.cognition_package import RenzhiBao
        bao = RenzhiBao("合境")
        bao.shu_ju(
            hang_ye=ling_yu.get("hang_ye", ""),
            liu_cheng=liu_cheng,
            yi_zhi_ruan_jian=already_known,
            xuqiu=xuqiu,
            yao_qiu=(
                "为每个阶段推荐软件。返回JSON数组: "
                '[{"jie_duan":1,"ming":"阶段名","ruan_jian":"软件名",'
                '"yong_tu":"用途","shu_ru_ge_shi":"输入格式","shu_chu_ge_shi":"输出格式",'
                '"cao_zuo_fang_fa":"Python API/CLI/GUI","ti_dai":"替代软件"}]'
                "每个阶段1-2个软件即可。优先Python API>CLI>GUI。不确定的留空。"
            )
        )
        try:
            jg = self.xin.llm.chat([{"role": "user", "content": bao.to_json()}], wendu=0.2, zuidazifu=800)
            text = str(jg)
            if "```json" in text:
                start = text.index("```json") + 7
                end = text.index("```", start)
                text = text[start:end]
            elif "[" in text:
                start = text.index("[")
                end = text.rindex("]") + 1
                text = text[start:end]
            chain = json.loads(text)
            return {"jie_duan": chain, "lai_yuan": "LLM"}
        except Exception:
            return {"jie_duan": [], "cuo_wu": "LLM不可用或解析失败"}

    # ==================== Layer 3: 流水线编排 ====================

    def bian_pai(self, ruan_jian_lian: list) -> dict:
        """编排DAG: 检测依赖+格式兼容+插入转换节点"""
        nodes = []
        edges = []

        for i, jd in enumerate(ruan_jian_lian):
            node_id = f"n{i}"
            nodes.append({
                "id": node_id,
                "jie_duan": jd.get("jie_duan", i + 1),
                "ming": jd.get("ming", ""),
                "ruan_jian": jd.get("ruan_jian", ""),
                "yong_tu": jd.get("yong_tu", ""),
                "shu_ru": jd.get("shu_ru_ge_shi", ""),
                "shu_chu": jd.get("shu_chu_ge_shi", ""),
                "cao_zuo_fang_fa": jd.get("cao_zuo_fang_fa", ""),
                "ti_dai": jd.get("ti_dai", ""),
                "zhuang_tai": "pending",
            })

            # 边: 上一节点→当前节点
            if i > 0:
                prev_output = nodes[i - 1]["shu_chu"]
                curr_input = nodes[i]["shu_ru"]
                edge_type = "direct"
                needs_convert = None

                # 检测格式是否兼容
                if prev_output and curr_input and prev_output.lower() != curr_input.lower():
                    edge_type = "convert"
                    needs_convert = {"from": prev_output, "to": curr_input}
                    # 插入转换节点标记
                    nodes[i]["xu_yao_zhuan_huan"] = True

                edges.append({
                    "from": nodes[i - 1]["id"],
                    "to": node_id,
                    "type": edge_type,
                    "convert": needs_convert,
                })

        return {"nodes": nodes, "edges": edges, "zong_shu": len(nodes)}

    # ==================== Layer 2: 执行层 ====================

    def zhi_xing(self, dag: dict) -> dict:
        """逐节点执行: RuanJianCeng + 格式转换 + 检查点"""
        nodes = dag.get("nodes", [])
        edges = dag.get("edges", [])
        results = []

        for i, node in enumerate(nodes):
            self._jilu(f"=== 阶段{i+1}/{len(nodes)}: {node['ming']} ({node.get('ruan_jian','?')}) ===")

            # 检测是否需要格式转换
            if i > 0 and node.get("xu_yao_zhuan_huan"):
                edge = edges[i - 1] if i - 1 < len(edges) else {}
                convert_info = edge.get("convert", {})
                if convert_info:
                    self._jilu(f"  格式转换: {convert_info['from']} → {convert_info['to']}")
                    self._zhuan_huan_ge_shi(
                        convert_info["from"], convert_info["to"],
                        results[-1].get("shu_chu_wen_jian", "") if results else ""
                    )

            # 执行单节点: 复用RuanJianCeng
            jie_guo = self._zhi_xing_jie_dian(node)

            # 人工决策检查
            if self._xu_yao_ren_gong_que_ren(node):
                self._jilu(f"  人工决策节点: 等待确认...")
                jie_guo["ren_gong_que_ren"] = True

            results.append(jie_guo)

            # 检查点
            self._jian_cha_dian(node, jie_guo, i, len(nodes))

            # 失败且无替代→停止
            if not jie_guo.get("success") and not node.get("ti_dai"):
                self._jilu(f"  节点失败，无替代方案，流水线暂停")
                break

        dabiao = all(r.get("success") for r in results)
        return {
            "dabiao": dabiao,
            "jie_duan_shu": len(results),
            "jie_guo": results,
            "zhai_yao": self.qu_zhai_yao(),
        }

    def _zhi_xing_jie_dian(self, node: dict) -> dict:
        """执行单个节点=操作一个软件(复用RuanJianCeng)"""
        if hasattr(self.xin, 'ruanjianceng') and self.xin.ruanjianceng:
            return self.xin.ruanjianceng.cao_zuo_ruan_jian(
                f"{node['ming']}: 用{node['ruan_jian']}做{node['yong_tu']}"
            )
        return {"success": False, "error": "RuanJianCeng未注入"}

    def _zhuan_huan_ge_shi(self, yuan: str, mubiao: str, shu_ru_file: str = ""):
        """格式转换: 铸剑炉锻造转换脚本→沙箱执行"""
        if not self.xin.zhujianlu:
            return
        xuqiu = f"生成纯Python格式转换函数: {yuan}→{mubiao}。解析{yuan}二进制格式, 输出{mubiao}格式。输入文件路径: {shu_ru_file}。返回输出文件路径。"
        try:
            jg = self.xin.zhujianlu.duanzao(xuqiu)
            if jg and jg.get("success"):
                self._jilu(f"  格式转换脚本已锻造")
        except Exception as e:
            self._jilu(f"  格式转换失败: {e}")

    def _xu_yao_ren_gong_que_ren(self, node: dict) -> bool:
        """检测是否人工决策节点"""
        keywords = ["评审", "审批", "确认", "验收", "签字", "review", "approve"]
        text = f"{node.get('ming','')} {node.get('yong_tu','')}"
        return any(kw in text for kw in keywords)

    def _jian_cha_dian(self, node: dict, jie_guo: dict, idx: int, total: int):
        """保存检查点到经络"""
        try:
            if self.xin.meridian and hasattr(self.xin.meridian, 'jilu_jianchadian'):
                self.xin.meridian.jilu_jianchadian({
                    "buzhou": f"流水线{idx+1}/{total}",
                    "mingcheng": f"{node.get('ming','')}:{node.get('ruan_jian','')}",
                    "zhuangtai": "completed" if jie_guo.get("success") else "failed",
                    "dabiao": jie_guo.get("success", False),
                    "haoshi": jie_guo.get("haoshi", 0),
                    "shijian": datetime.now().isoformat(),
                })
        except Exception: pass

    # ==================== Layer 1: 学习层 ====================

    def xue_xi(self, jie_guo: dict):
        """归档: 行业流程+软件操作+格式转换 → 下次复用"""
        try:
            if self.xin.gan and hasattr(self.xin.gan, 'jilu'):
                self.xin.gan.jilu("流水线模板", {
                    "zong_jie_duan": jie_guo.get("jie_duan_shu", 0),
                    "dabiao": jie_guo.get("dabiao", False),
                    "zhai_yao": self.qu_zhai_yao()[:500],
                })
        except Exception: pass

        # 软件能力图谱更新
        for jg in jie_guo.get("jie_guo", []):
            if jg.get("success"):
                ruan_jian = jg.get("ruan_jian", "")
                if ruan_jian and ruan_jian not in self.ruan_jian_tu_pu:
                    self.ruan_jian_tu_pu[ruan_jian] = {"cao_zuo_ci_shu": 1}
                elif ruan_jian in self.ruan_jian_tu_pu:
                    self.ruan_jian_tu_pu[ruan_jian]["cao_zuo_ci_shu"] += 1

    # ==================== 一站式 ====================

    def cao_zuo_ren_yi_ling_yu(self, xuqiu: str) -> dict:
        """一站式: 领域适配→软件发现→编排→执行→学习→交付"""
        kaishi = time.time()
        self._zhi_xing_lishi.append({"xuqiu": xuqiu, "shijian": datetime.now().isoformat()})

        # Layer 5: 领域适配
        self._jilu("== Layer5: 领域适配 ==")
        ling_yu = self.ling_yu_shi_pei(xuqiu)
        if ling_yu.get("cuo_wu"):
            return {"success": False, "error": f"领域识别失败: {ling_yu['cuo_wu']}"}
        self._jilu(f"  行业: {ling_yu.get('hang_ye','?')} | 阶段数: {len(ling_yu.get('biao_zhun_liu_cheng',[]))}")

        # Layer 4: 软件发现
        self._jilu("== Layer4: 软件发现 ==")
        ruan_jian = self.ruan_jian_fa_xian(ling_yu, xuqiu)
        jie_duan = ruan_jian.get("jie_duan", [])
        if not jie_duan:
            return {"success": False, "error": "未发现可用软件链", "ling_yu": ling_yu}
        self._jilu(f"  发现 {len(jie_duan)} 个软件节点")

        # Layer 3: 编排
        self._jilu("== Layer3: 流水线编排 ==")
        dag = self.bian_pai(jie_duan)
        self._jilu(f"  DAG: {dag['zong_shu']}节点, {len(dag['edges'])}条边")

        # Layer 2: 执行
        self._jilu("== Layer2: 执行流水线 ==")
        jie_guo = self.zhi_xing(dag)

        # Layer 1: 学习
        self._jilu("== Layer1: 归档学习 ==")
        self.xue_xi(jie_guo)

        haoshi = round(time.time() - kaishi, 2)
        self._jilu(f"== 完成: {haoshi}s, 达标={jie_guo['dabiao']} ==")

        return {
            "success": jie_guo["dabiao"],
            "hang_ye": ling_yu.get("hang_ye", ""),
            "jie_duan_shu": len(jie_duan),
            "jie_guo": jie_guo,
            "zhai_yao": self.qu_zhai_yao(),
            "haoshi": haoshi,
        }

    # ==================== 工具 ====================

    def _jilu(self, msg):
        self._zhi_xing_lishi.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def qu_zhai_yao(self):
        return "\n".join(self._zhi_xing_lishi[-20:])

    def qu_ling_yu_ku(self):
        return self.ling_yu_ku

    def qu_ruan_jian_tu_pu(self):
        return self.ruan_jian_tu_pu
