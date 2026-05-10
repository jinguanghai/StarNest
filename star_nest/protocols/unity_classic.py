"""
合境·重剑（土）：记忆上下文聚合与TRIZ九屏幕法系统重组
V10.4 零提示词版：所有LLM调用改用结构化数据包，不再包含任何自然语言提示词。
星巢DMN → 结构化数据 → LLM类DMN → 统计拟合 → 返回结果

【通用问题解决操作系统·完整映射】
- 正境(Define)：retrieve_context——定义记忆检索范围
- 反境(Measure)：检索结果可计数
- 合境(Improve)：hejing_jiupingmu——九屏幕法系统重组，生成可回滚的平衡方案
- 超越境(Control)：_jiupingmufa_moren——安全回退，信息不足时给出保守方案
- 本源境(Sustain)：标准化上下文格式 + 动态平衡方案输出结构
"""

import json


class HeJing:
    """合境：记忆上下文聚合 + 九屏幕法——肺的治节之基"""

    def __init__(self, xin):
        self.xin = xin

    def retrieve_context(self, user_msg: str) -> str:
        parts = []
        if self.xin.gan:
            ctx = self.xin.gan.ronghe_jiansuo(user_msg)
            if ctx:
                parts.append(ctx)
        return "\n\n".join(parts) if parts else ""

    def hejing_jiupingmu(self, llm, yonghu_xiaoxi: str, gongneng_fenxi: dict, yinguo_fenxi: dict,
                         yonghu_pianhao: dict = None) -> dict:
        if not llm:
            return self._jiupingmufa_moren(gongneng_fenxi, yinguo_fenxi, yonghu_pianhao)

        # V11.0: 统一认知包
        from star_nest.protocols.cognition_package import RenzhiBao
        bao = RenzhiBao.from_xin(self.xin, "合境") if self.xin else RenzhiBao("合境")
        bao.shu_ju(
            gongneng=gongneng_fenxi,
            yinguo=yinguo_fenxi,
            yuanshi_xiaoxi=yonghu_xiaoxi,
            jiyi=self.retrieve_context(yonghu_xiaoxi),
            pianhao=yonghu_pianhao or {},
        )
        try:
            jieguo = llm.chat([{"role": "user", "content": bao.to_json()}], wendu=0.3, zuidazifu=1000)
            return self._jiexi_json_jieguo(jieguo)
        except Exception:
            return self._jiupingmufa_moren(gongneng_fenxi, yinguo_fenxi, yonghu_pianhao)

    def _jiexi_json_jieguo(self, wenben: str) -> dict:
        """V11.0: 优先解析JSON, 失败回退到文本解析"""
        try:
            # 提取JSON块(可能在```json...```中)
            if "```json" in wenben:
                start = wenben.index("```json") + 7
                end = wenben.index("```", start)
                wenben = wenben[start:end].strip()
            elif "```" in wenben:
                start = wenben.index("```") + 3
                end = wenben.index("```", start)
                wenben = wenben[start:end].strip()
            # 尝试找到{...}JSON对象
            brace_start = wenben.find('{')
            brace_end = wenben.rfind('}')
            if brace_start >= 0 and brace_end > brace_start:
                wenben = wenben[brace_start:brace_end + 1]
            fenxi = json.loads(wenben)
            # 标准化key名
            result = {
                "shijian_weidu": fenxi.get("shijian_weidu", {}),
                "kongjian_weidu": fenxi.get("kongjian_weidu", {}),
                "pingheng_fangan": fenxi.get("pingheng_fangan", ""),
                "ke_huigun": fenxi.get("ke_huigun", False),
                "fengxian_pinggu": fenxi.get("fengxian_pinggu", "中"),
                "liansuo_yingxiang": fenxi.get("liansuo_yingxiang", ""),
                "youhai_gongneng": fenxi.get("youhai_gongneng", ""),
                "zuozhi_gongneng": fenxi.get("zuozhi_gongneng", ""),
                "xingdong": fenxi.get("xingdong")
            }
            return result
        except (json.JSONDecodeError, ValueError):
            return self._jiexi_jiupingmu_jieguo(wenben)

    def _jiexi_jiupingmu_jieguo(self, wenben: str) -> dict:
        fenxi = {"shijian_weidu": {}, "kongjian_weidu": {}, "pingheng_fangan": "",
                 "ke_huigun": False, "fengxian_pinggu": "中", "liansuo_yingxiang": "",
                 "youhai_gongneng": "", "zuozhi_gongneng": "", "xingdong": None}
        quyu = ""
        xingdong_lines = []
        in_xingdong = False
        for line in wenben.strip().split('\n'):
            line = line.strip()
            if "【执行计划】" in line or "【行动方案】" in line:
                in_xingdong = True
                continue
            if in_xingdong and line.startswith("【"):
                in_xingdong = False
            if in_xingdong and line:
                xingdong_lines.append(line)
            if "【时间维度】" in line:
                quyu = "shijian"
            elif "【空间维度】" in line:
                quyu = "kongjian"
            elif "【动态平衡方案】" in line:
                quyu = "pingheng"
            elif "【有害功能分析】" in line:
                quyu = "youhai"
            elif "【佐制功能候选】" in line:
                quyu = "zuozhi"
            elif quyu == "shijian" and "：" in line and "-" in line:
                jian, zhi = line.split("：", 1)
                fenxi["shijian_weidu"][jian.strip()] = zhi.strip()
            elif quyu == "kongjian" and "：" in line:
                jian, zhi = line.split("：", 1)
                fenxi["kongjian_weidu"][jian.strip()] = zhi.strip()
            elif line.startswith("方案描述："):
                fenxi["pingheng_fangan"] = line.replace("方案描述：", "").strip()
            elif line.startswith("可回滚性："):
                fenxi["ke_huigun"] = "是" in line
            elif line.startswith("风险评估："):
                fenxi["fengxian_pinggu"] = line.replace("风险评估：", "").strip()
            elif line.startswith("连锁影响："):
                fenxi["liansuo_yingxiang"] = line.replace("连锁影响：", "").strip()
            elif quyu == "youhai" and line and not line.startswith("【"):
                fenxi["youhai_gongneng"] += line + "\n"
            elif quyu == "zuozhi" and line and not line.startswith("【"):
                fenxi["zuozhi_gongneng"] += line + "\n"
        fenxi["youhai_gongneng"] = fenxi["youhai_gongneng"].strip()
        fenxi["zuozhi_gongneng"] = fenxi["zuozhi_gongneng"].strip()
        # 提取结构化执行计划
        if xingdong_lines:
            xingdong_text = " ".join(xingdong_lines)
            fenxi["xingdong"] = self._jiexi_xingdong(xingdong_text, fenxi)
        elif fenxi["pingheng_fangan"] and len(fenxi["pingheng_fangan"]) > 10:
            # 没有【执行计划】标记时,从方案描述中提取
            fenxi["xingdong"] = self._jiexi_xingdong(fenxi["pingheng_fangan"], fenxi)
        return fenxi

    def _jiexi_xingdong(self, text: str, fangan: dict) -> dict:
        """从合境输出中提取结构化执行计划"""
        xingdong = {"action": None, "target": None, "params": {}, "rollback": fangan.get("ke_huigun", False)}
        tl = text.lower()
        # 检测工具调用意图
        if any(kw in tl for kw in ["duanzao", "锻造", "生成代码", "写文件", "创建", "修改代码"]):
            xingdong["action"] = "duanzao"
            xingdong["target"] = fangan.get("pingheng_fangan", text)[:200]
        elif any(kw in tl for kw in ["搜索", "查找", "查询", "读取", "读文件"]):
            xingdong["action"] = "sousuo"
            xingdong["params"] = {"query": text[:200]}
        elif any(kw in tl for kw in ["执行命令", "运行", "shell"]):
            xingdong["action"] = "shell"
            xingdong["params"] = {"command": text[:200]}
        elif any(kw in tl for kw in ["写入", "写文件", "保存"]):
            xingdong["action"] = "xieru_wenjian"
            xingdong["params"] = {"content": text[:500]}
        if xingdong["action"]:
            return xingdong
        return None

    def _jiupingmufa_moren(self, gongneng_fenxi=None, yinguo_fenxi=None, yonghu_pianhao=None) -> dict:
        pianhao = yonghu_pianhao or {}
        fengge = pianhao.get("fengge", "balanced")
        deault_fangan = "需进一步分析"
        if fengge == "简洁高效":
            deault_fangan = "建议直接执行基础方案，简化流程"
        elif fengge == "详细全面":
            deault_fangan = "建议从时间与空间维度逐层展开分析"
        return {"shijian_weidu": {"现在-系统": "信息不足"}, "kongjian_weidu": {"系统": "未知"},
                "pingheng_fangan": deault_fangan, "ke_huigun": False, "fengxian_pinggu": "中", "liansuo_yingxiang": "未评估",
                "youhai_gongneng": "", "zuozhi_gongneng": ""}