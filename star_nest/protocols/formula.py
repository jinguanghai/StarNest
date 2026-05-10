"""
五境流转 · 君臣佐使 V1.0 [星巢·核心认知架构]
重写编程逻辑: 每一个方剂(功能)都有君/臣/害/佐/使五元闭环

君(Jun) : 主要功能目标 — 我要做什么
臣(Chen): 辅助功能 — 谁帮我做、怎么帮我
害(Hai) : 有害副作用 — 可能出什么问题
佐(Zuo) : 佐治功能 — 出问题怎么办、不出问题怎么防
使(Shi) : 反馈功能 — 做完了告诉主功能结果

五元闭环: 君→臣→害→佐→使→君 (下一个决策基于上一个结果)
"""
import time, json


class FangJi:
    """
    方剂: 一个完整的君/臣/害/佐/使认知单元
    
    用法:
        fangji = FangJi("处理用户消息", "回答用户问题")
        fangji.jia_chen("工具匹配", lambda: pi.si_lv_pi_pei(llm, msg))
        fangji.yu_ce_hai("工具不存在", "消息无法匹配任何工具")
        fangji.jia_zuo("五境深度分析", lambda: fuwu_protocols_fenxi(msg))
        fangji.jia_shi("记录结果到日志", lambda r: rizhi.huxi_rizhi(msg, r))
        result = fangji.aozhi()  # 熬制: 按君→臣→害→佐→使顺序执行
    """

    def __init__(self, mingcheng: str, mubiao: str = ""):
        self.mingcheng = mingcheng  # 方剂名称
        self.mubiao = mubiao         # 君: 主要目标
        self.jun = None              # 君: (名称, 函数)
        self.chen_liebiao = []       # 臣: [(名称, 函数), ...]
        self.hai_liebiao = []        # 害: [(类型, 描述, 严重度), ...]  严重度: 0=可忽略 1=注意 2=严重 3=致命
        self.zuo_liebiao = []        # 佐: [(害的类型, 佐治函数), ...]  每个佐对应一种害
        self.shi_liebiao = []        # 使: [(名称, 函数), ...]
        self.execution_rizhi = []      # 执行日志: 记录每一步
        self.jieguo = None           # 最终结果
        self.tongyong_zuozhi = None  # 通用佐治兜底: fn(harm, result, chen_jieguo) → 兜底结果

    # ---- 组方 ----
    def she_jun(self, name: str, fn):
        """设君: 定义主要功能"""
        self.jun = (name, fn)
        return self

    def jia_chen(self, name: str, fn):
        """加臣: 添加辅助功能"""
        self.chen_liebiao.append((name, fn))
        return self

    def yu_ce_hai(self, leixing: str, miaoshu: str, yanzhongdu: int = 1):
        """预测害: 声明可能的副作用"""
        self.hai_liebiao.append({"leixing": leixing, "miaoshu": miaoshu, "yanzhongdu": yanzhongdu})
        return self

    def jia_zuo(self, hai_leixing: str, fn):
        """加佐: 为特定害类型配对佐治函数"""
        self.zuo_liebiao.append((hai_leixing, fn))
        return self

    def jia_shi(self, name: str, fn):
        """加使: 添加反馈函数(回报君)"""
        self.shi_liebiao.append((name, fn))
        return self

    def she_tongyong_zuozhi(self, fn):
        """设通用佐治: 当未知害发生或佐治缺失时调用的兜底函数"""
        self.tongyong_zuozhi = fn
        return self

    # ---- 熬制 ----
    def aozhi(self):
        """
        熬制: 按君→臣→害检测→佐治→使反馈顺序执行
        返回熬制结果
        """
        result = None
        zimiao = f"[方剂·{self.mingcheng}]"

        # === 君: 执行主要功能 ===
        try:
            result = self.jun[1]() if self.jun else None
            self._jilu(f"君·{self.jun[0] if self.jun else '无'}: 执行完毕")
        except Exception as e:
            result = self._cuowu_zhuangtai(f"君执行异常: {e}")
            self._jilu(f"君·异常: {e}")

        # === 臣: 逐个执行辅助功能 ===
        chen_jieguo = {}
        for name, fn in self.chen_liebiao:
            try:
                cj = fn() if callable(fn) else fn
                chen_jieguo[name] = cj
                self._jilu(f"臣·{name}: {str(cj)[:80] if cj else '空'}")
            except Exception as e:
                chen_jieguo[name] = self._cuowu_zhuangtai(str(e))
                self._jilu(f"臣·{name}·异常: {e}")

        # === 害: 检测实际发生的副作用 ===
        actual_harms = self._jiance_hai(result, chen_jieguo)

        # === 佐: 对每个实际发生的害应用佐治 ===
        declared_types = {h["leixing"] for h in self.hai_liebiao}
        for harm in actual_harms:
            # 标记未知害(运行时发现, 未在配方中声明)
            if harm["leixing"] not in declared_types:
                harm["_weizhi"] = True
            zuo_found = False
            for hai_type, zuo_fn in self.zuo_liebiao:
                if hai_type == harm["leixing"] or hai_type == "*":
                    try:
                        zuo_result = zuo_fn(harm, result, chen_jieguo)
                        self._jilu(f"佐·{hai_type}: 佐治完成 → {str(zuo_result)[:80] if zuo_result else '无返回'}")
                        if zuo_result is not None:
                            result = zuo_result
                        zuo_found = True
                        break
                    except Exception as e:
                        self._jilu(f"佐·{hai_type}·佐治异常: {e}")
            if not zuo_found:
                if harm.get("_weizhi") and self.tongyong_zuozhi:
                    self._jilu(f"佐·未知害'{harm['leixing']}': 触发通用佐治")
                    try:
                        tj = self.tongyong_zuozhi(harm, result, chen_jieguo)
                        if tj is not None:
                            result = tj
                    except Exception as e:
                        self._jilu(f"佐·通用佐治异常: {e}")
                else:
                    self._jilu(f"佐·缺失: 害'{harm['leixing']}'无对应佐治(严重度{harm.get('yanzhongdu','?')})")

        # === 使: 反馈给君 ===
        for name, fn in self.shi_liebiao:
            try:
                fn(result, chen_jieguo, actual_harms)
            except Exception as e:
                self._jilu(f"使·{name}·异常: {e}")

        self.jieguo = result
        return result

    # ---- 内部方法 ----
    def _jiance_hai(self, result, chen_jieguo):
        """检测实际发生的害"""
        harms = []
        # 检测臣的返回是否为空
        for name, cj in chen_jieguo.items():
            if cj is None:
                harms.append({"leixing": "chen_kong", "miaoshu": f"臣'{name}'返回空",
                             "yanzhongdu": 1, "laiyuan": name})
            elif isinstance(cj, dict) and cj.get("_error"):
                harms.append({"leixing": "chen_yichang", "miaoshu": f"臣'{name}'返回错误:{cj['_error']}",
                             "yanzhongdu": 2, "laiyuan": name})
        # 检测结果是否包含错误
        if isinstance(result, dict) and not result.get("success", True):
            err = result.get("error", "未知错误")
            # 分类害
            if "权限" in err or "拒绝" in err or "denied" in err.lower():
                harms.append({"leixing": "quanxian_jujue", "miaoshu": err, "yanzhongdu": 2})
            elif "超时" in err or "timeout" in err.lower():
                harms.append({"leixing": "chaoshi", "miaoshu": err, "yanzhongdu": 1})
            elif "语法" in err or "Syntax" in err or "NameError" in err:
                harms.append({"leixing": "yufa_cuowu", "miaoshu": err, "yanzhongdu": 1})
            else:
                harms.append({"leixing": "execution_shibai", "miaoshu": err, "yanzhongdu": 1})
        # 检测臣是否匹配失败
        if not chen_jieguo or all(v is None for v in chen_jieguo.values()):
            harms.append({"leixing": "wu_gongju_pipei", "miaoshu": "无可用工具或臣全为空",
                         "yanzhongdu": 0})
        return harms

    def _cuowu_zhuangtai(self, error: str):
        return {"success": False, "error": str(error)[:200], "_error": str(error)[:200]}

    def _jilu(self, msg):
        self.execution_rizhi.append(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def qu_rizhi(self):
        return self.execution_rizhi

    def qu_jieguo(self):
        return self.jieguo
