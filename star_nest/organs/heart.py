"""
心·DMN调度中心 V2.0 [星巢本体移植版+三体适配·深度对接五境引擎]
君火·五境流转·π-φ控制·八极诊断·铸剑炉duanzao回调
"""
import threading, time, json, importlib.util, re, glob
from pathlib import Path
from queue import Queue
from typing import Optional, Dict, List, Any
from star_nest.protocols.harm_assist import sheng_ming_hai, sheng_ming_zuo

class XinZang(threading.Thread):
    def __init__(self, meridian, llm, zhujianlu, baji, jiyiguanli, peizhi, juese="yunxingti"):
        super().__init__(daemon=True)
        self.meridian = meridian
        self.llm = llm
        self.zhujianlu = zhujianlu
        self.baji = baji
        self.jiyiguanli = jiyiguanli
        self.peizhi = peizhi
        self.juese = juese
        self._yunxing = True
        self._suo = threading.Lock()  # 共享状态锁
        self.ganzhiceng = None  # 感知层注入点
        self.shuruceng = None   # 输入层注入点
        self.jianjinrenzhi = None  # 渐进认知引擎注入点
        self.anquan = None      # 三体安全注入点
        self.zhaoyaojing = None  # 照妖镜注入点
        self.piphianquan = None   # π-φ安全引擎注入点
        self.piphi = None          # π-φ全局统计总线
        self._zuihou_piphi_ph = 0  # π-φ平衡检查冷却
        self._zuihou_omega = 0  # Ω安全扫描冷却
        self._zuihou_piphi_343 = 0   # π-φ中周冷却
        self._zuihou_piphi_2401 = 0  # π-φ大周冷却
        self._zuihou_piphi_16807 = 0 # π-φ周天冷却
        self.shuchu_duilie = Queue()
        self.renwu_duilie = Queue()
        self.yonghu_xuqiu_duilie = Queue()
        self.gan = None; self.pi = None; self.fei = None; self.shen = None
        self._zuihou_jiankangdu = None
        self.rizhi = None
        self.meridian_jiyi = None
        self.qixue = None
        self._duiqi_jishu = 0
        self._piphicycle = None
        self._bashisuanshu = None
        self._jiuchou = None
        self._liushizhi = "少阳"
        self._shizhi_jishu = 0
        self._wen_du = 0.7
        self._zuozhi_mode = "active"        # 佐治模式: active(害检测)+idle(无任务)
        self._zuozhi_zuihou_renwu = 0       # 上次任务时间
        self._zuozhi_renwu_lengque = 14      # 任务完成14秒后回active佐治(2×七律)
        self._zuozhi_jihuo = time.time()
        self.fanjing = None

        self.hejing = None
        self.chaoyuejing = None
        self._init_protocols()
        self._init_dynamics()
        # 佐治初始: 所有体设定为佐治模式(害检测激活)
        self._zuozhi_qiehuan("active")

    def _zuozhi_qiehuan(self, mode: str):
        """佐治模式切换: active(害检测激活→正常执行) / anquan(降级→只读→阻断写权限)"""
        self._zuozhi_mode = mode
        if mode == "anquan" and getattr(self, 'pi', None):
            self.pi.ke_xieru = False
        if self.meridian:
            try:
                for tid in ["bianchengti", "yunxingti", "fuzhiti"]:
                    if self.meridian.tupu.has_node(tid):
                        self.meridian.tupu._nodes[tid]["zuozhi_mode"] = mode
                        self.meridian.tupu._nodes[tid]["zuozhi_qiehuan_time"] = str(time.time())
            except Exception: pass

    def _init_protocols(self):
        try:
            from star_nest.protocols.counter_classic import FanJing
            from star_nest.protocols.unity_classic import HeJing
            from star_nest.protocols.transcend_classic import ChaoYueJing
            self.fanjing = FanJing(self)
            self.hejing = HeJing(self)
            self.chaoyuejing = ChaoYueJing(self)
        except Exception as e:
            print(f'[心] 五境引擎加载跳过: {e}')

    def _init_dynamics(self):
        try:
            from star_nest.dynamics.pi_phi_cycle import PiPhiController
            from star_nest.dynamics.eighty_four import StrategyScheduler
            from star_nest.dynamics.nine_domains import NineDomainsHealth
            self._piphicycle = PiPhiController()
            self._bashisuanshu = StrategyScheduler(self.baji, self._piphicycle)
            self._jiuchou = NineDomainsHealth()
        except Exception as e:
            print(f'[心] 动力学引擎加载跳过: {e}')

    def jieru_qiguan(self, gan, pi, fei, shen) -> None:
        self.gan = gan; self.pi = pi; self.fei = fei; self.shen = shen
    def add_renwu(self, r: str, youxianji: int = 0) -> None:
        """注意力调度: 长任务(>200字或多步骤)→RenWuJiHua; 短任务→直接入队"""
        msg = str(r)
        is_long = len(msg) > 200 or any(kw in msg for kw in ["步骤1","第一步","step1","Step 1"])
        if is_long:
            try:
                from star_nest.execution.task_plan import RenWuJiHua
                jihua = RenWuJiHua(self, msg)
                jieguo = jihua.zhi_xing()
                # 结果入队让调度器处理
                self.renwu_duilie.put(("NORMAL", f"[任务计划] {'完成' if jieguo['dabiao'] else '未完成'}: {jieguo.get('jieguo','')[:500]}"))
                return
            except Exception: pass
        if youxianji >= 2:
            self.renwu_duilie.put(("URGENT", msg))
        else:
            self.renwu_duilie.put(("NORMAL", msg))
    @sheng_ming_hai([
        ("wu_gongju_pipei", "无工具匹配或臣全空", 0),
        ("quanxian_jujue", "权限被拒", 2),
        ("execution_shibai", "工具执行失败", 2),
        ("LLM_xuanyun", "LLM返回无效/幻觉", 1),
        ("chaoshi", "执行超时", 1),
    ])
    @sheng_ming_zuo({
        "wu_gongju_pipei": True, "quanxian_jujue": True,
        "execution_shibai": True, "LLM_xuanyun": True, "chaoshi": True,
    })
    def add_xuqiu(self, x: str) -> None:
        """
        君·信号中枢: 调问剑路(全五境) → 读诊断 → 发四信号 → 脏器干活
        
        心不干具体事——只发信号。
        一切信息走经络。
        """
        msg = str(x).strip()
        if not msg or msg == "__EXIT__":
            return

        # 问剑路·全五境预检测 (心授权·肺管)
        try:
            from star_nest.dynamics.inquiry_path import get_wen_jian_lu
            wjl = get_wen_jian_lu(self)
            zhenduan = wjl.jie_shou(msg)
        except Exception:
            zhenduan = {"shizhi": "少阳", "luxian": "duihua"}

        shizhi = zhenduan.get("shizhi", "少阳")
        luxian = zhenduan.get("luxian", "duihua")

        # 更新 GlobalState S
        try:
            from star_nest.dynamics.global_state import get_global_state
            S = get_global_state(self)
            S.baji = zhenduan.get("baji", S.baji)
            S.shizhi = shizhi
            S.save()
        except Exception: pass

        # 心发信号·四脏四信号
        if luxian in ("gedou", "shencha"):
            if self.meridian:
                try:
                    self.meridian.fa_xinhao("fei", "shuchu", {
                        "text": f"[使·{luxian}] {msg[:60]}...", "level": "zhong"})
                    self.meridian.fa_xinhao("gan", "shadu", {"msg": msg[:200], "shizhi": shizhi})
                except Exception: pass
            return

        if luxian in ("execution_dadan", "execution_queren"):
            self._is_exec_cmd = True
            fangan = zhenduan.get("gongju_yitu")
            if self.meridian:
                try:
                    self.meridian.fa_xinhao("fei", "shuchu", {
                        "text": f"[确认] 即将执行: {msg[:60]}", "level": "di"})
                    self.meridian.fa_xinhao("pi", "execution", {"msg": msg, "fangan": fangan})
                except Exception: pass
            if isinstance(fangan, dict):
                self.yonghu_xuqiu_duilie.put({"type": "exec", "msg": msg, "fangan": fangan})
            else:
                self.yonghu_xuqiu_duilie.put(msg)
            return

        if luxian == "touwei" and self.jianjinrenzhi:
            try: self.jianjinrenzhi.tian_jia(msg); return
            except Exception: pass

        if self.meridian:
            try:
                self.meridian.fa_xinhao("gan", "jiyi", {"msg": msg[:200]})
            except Exception: pass
        self.yonghu_xuqiu_duilie.put(msg)

    def run(self):
        time.sleep(1); self._qidong_yure()
        while self._yunxing:
            self.meridian.jilu_xintiao(self.juese)
            if time.time() - self._zuozhi_jihuo > 2401:
                try:
                    if self.gan: self.gan._zuozhi_jiance()
                    if self.shen: self.shen._zuozhi_shendu()
                except Exception: pass
                self._zuozhi_jihuo = time.time()
            m = self._xiaoxi_chuandu()
            if m is None:
                if self._zuozhi_mode == "idle" and time.time() - self._zuozhi_zuihou_renwu > self._zuozhi_renwu_lengque:
                    self._zuozhi_qiehuan("active")
                if self.ganzhiceng:
                    try: self.ganzhiceng.xunjian_yici()
                    except Exception: pass
                if self.anquan and time.time() - getattr(self, '_zuihou_omega', 0) > 343:
                    try:
                        wenti_omega = self.anquan.omega_jian_shi()
                        if wenti_omega and self.juese == "yunxingti":
                            for w in wenti_omega:
                                if self.meridian:
                                    self.meridian.jilu_wenti(self.juese, {
                                        "miaoshu": f"[Ω安全] {w.get('miaoshu','')[:100]}",
                                        "leixing": "anquan_jiankong",
                                        "xiangqing": w,
                                    })
                        self._zuihou_omega = time.time()
                    except Exception: pass
                if self.piphianquan:
                    xianzai = time.time()
                    if xianzai - self._zuihou_piphi_343 > 343:
                        try: self.piphianquan.zhou_qi(343)
                        except Exception: pass
                        self._zuihou_piphi_343 = xianzai
                    if xianzai - self._zuihou_piphi_2401 > 2401:
                        try: self.piphianquan.zhou_qi(2401)
                        except Exception: pass
                        self._zuihou_piphi_2401 = xianzai
                    if xianzai - self._zuihou_piphi_16807 > 16807:
                        try: self.piphianquan.zhou_qi(16807)
                        except Exception: pass
                        self._zuihou_piphi_16807 = xianzai
                time.sleep(0.5)
                continue
            if m == "__EXIT__": break
            if self._zuozhi_mode == "active":
                self._zuozhi_qiehuan("idle")
            r = self._chuli(m)
            if r is not None: self.guangbo_shuchu(r); self._jilu_jiyi(m, r)
            if self.rizhi and r:
                m_str = m if isinstance(m, str) else str(m.get("msg", "")) if isinstance(m, dict) else str(m)
                self.rizhi.huxi_rizhi(m_str[:200], str(r)[:200], self.juese)
            self._zuozhi_zuihou_renwu = time.time()
            self._baji_xunhuan(); time.sleep(1)
            if self.qixue:
                try:
                    cj = self.jiyiguanli._panduan_cengji(str(m)) if self.jiyiguanli else "正境"
                    self.qixue.xunhuan_yici(cj, str(m)[:100])
                except Exception as e:
                    if self.rizhi:
                        try: self.rizhi.wenti_rizhi(self.juese, {"miaoshu": f"气血循环异常:{e}", "leixing": "qixue_error"})
                        except Exception: pass
            self._duiqi_jishu += 1
            if self.meridian_jiyi:
                try:
                    from star_nest.armory.zhu_opencode import duiqi_dangqian_duihua, zengliang_duiqi
                    duiqi_dangqian_duihua()
                    if self._duiqi_jishu % 10 == 0:
                        zengliang_duiqi()
                except Exception: pass

    def _xiaoxi_chuandu(self):
        try:
            try: raw = self.renwu_duilie.get_nowait()
            except: raw = None
            if raw:
                if isinstance(raw, tuple):
                    return raw[1] if isinstance(raw[1], dict) else str(raw[1])
                return raw if isinstance(raw, dict) else str(raw)
            try: raw = self.yonghu_xuqiu_duilie.get_nowait()
            except: raw = None
            if raw: return raw if isinstance(raw, dict) else str(raw)
        except: pass
        return None

    def guangbo_shuchu(self, m: str) -> None:
        self.shuchu_duilie.put(m)

    def _chuli(self, raw):
        """心调度入口: 预匹配fangan→直接执行, 短对话→_duihua, 否则→FangJi"""
        # 预匹配执行路径
        if isinstance(raw, dict) and raw.get("type") == "exec":
            fangan = raw.get("fangan")
            msg = raw.get("msg", "")
            if fangan:
                result = self._execution_fangan(fangan, msg)
                if result and result.get("success"):
                    return str(result.get("output", ""))[:2000]
                if result:
                    return str(result.get("error", str(result)))[:2000]
            return self._duihua(msg[:500])

        msg = str(raw).strip()
        if not msg or msg == "__EXIT__":
            return None

        # 系统消息直接返回(不进入匹配)
        if any(msg.startswith(p) for p in ["[缓冲]", "[渐进]", "[完成]", "[使·",
                                             "[安全", "[Ω", "[π", "[经络", "[确认]", "[投喂]"]):
            return msg

        # 短对话·知识问答 → 直接走 _duihua (跳过 si_lv_pi_pei 的 LLM 调用)
        DUIHUA_PREFIX = ["说说", "谈谈", "分析", "解释", "介绍", "阐述", "描述",
                         "什么是", "为什么", "如何", "怎样", "怎么", "你好",
                         "Hi", "Hello", "谢谢", "再见", "你是谁"]
        if any(msg.startswith(p) for p in DUIHUA_PREFIX) and len(msg) < 50:
            return self._duihua(msg)

        # 尝试工具匹配
        if self.pi and self.llm:
            fangan = self.pi.si_lv_pi_pei(self.llm, msg)
            if fangan:
                result = self._execution_fangan(fangan, msg)
                if result and result.get("success"):
                    return result.get("output", str(result))[:2000]
                if result:
                    return result.get("error", str(result))[:2000]

        return self._duihua(msg[:500])

    @sheng_ming_hai([
        ("execution_shibai", "FangJi执行失败", 2),
        ("quanxian_jujue", "权限拒绝", 2),
        ("LLM_xuanyun", "LLM返回无效", 1),
    ])
    @sheng_ming_zuo({
        "execution_shibai": True, "quanxian_jujue": True, "LLM_xuanyun": True,
    })
    def _ao_yao_chuli(self, msg, luxian=None):
        """
        熬药·处理: 君臣佐使方剂模式
        
        君: 回答用户问题或执行用户需求
        臣: pi.si_lv_pi_pei 工具匹配(第一个臣)
              记忆检索(第二个臣, 只读场景备用)
        害: 工具不匹配 / 权限拒绝 / 执行异常 / 结果为空
        佐: 五境深度分析(无工具时) / 权限拒绝→降级只读 / 异常→经络告警
        使: 记录日志 + 写记忆 + 工具统计 + 反馈到下次决策
        """
        from star_nest.protocols.formula import FangJi
        
        # 用户确认: 太阳态势(高展开度·执行)需要确认
        if luxian and luxian.get("xuyao_queren"):
            from star_nest.armory.xitong_cao_zuo import qing_qiu_quan_xian
            if not qing_qiu_quan_xian(f"确认执行: {msg[:60]}", "中"):
                return "[确认] 用户取消执行"

        # π-φ认知油门: 当前势能影响执行策略
        pi_neng = 0.5; phi_neng = 0.5
        if self.piphi:
            try:
                pi_neng = self.piphi.qu_pi()
                phi_neng = self.piphi.qu_phi()
            except Exception: pass

        fang = FangJi("处理用户消息", msg[:80])
        
        # === 君: 回答用户 ===
        def _jun_execution():
            m = str(msg)
            # 先用工具执行, 失败了再用duihua
            f = self.pi.si_lv_pi_pei(self.llm, m) if self.pi else None
            if f:
                j = self._execution_fangan(f, m)
                # 工具调用记录
                if self.meridian_jiyi and f.get("gongju_ming"):
                    try:
                        self.meridian_jiyi.jilu_gongju(
                            f["gongju_ming"], f.get("hanshu_ming", ""),
                            f.get("pipei_ceng", 0), bool(j and j.get("success")))
                    except Exception: pass
                # 反馈环
                if self.zhujianlu and hasattr(self.zhujianlu, '_execution_jiance'):
                    try:
                        jc = self.zhujianlu._execution_jiance(str(m))
                        if j: self.zhujianlu._fankui_xunhuan(jc, j)
                    except Exception: pass
                if j and j.get("success"):
                    return j["output"]
                elif j:
                    return j  # 返回错误状态, 让害检测逻辑处理
            return None  # 无工具匹配
        
        fang.she_jun("回答/执行用户需求", _jun_execution)
        
        # === 臣: 工具匹配 ===
        def _chen_pipei():
            if self.pi:
                f = self.pi.si_lv_pi_pei(self.llm, msg)
                return f
            return None
        
        fang.jia_chen("脾·工具匹配 si_lv_pi_pei", _chen_pipei)
        
        # === 臣: 记忆检索(备用) ===
        def _chen_jiyi():
            if self.gan and self.jiyiguanli:
                try:
                    r = self.jiyiguanli.organs_ronghe_jiansuo(msg, 3)
                    return r if r else None
                except Exception: pass
            return None
        
        fang.jia_chen("肝·记忆检索", _chen_jiyi)
        
        # === 害: 声明可能的副作用 ===
        fang.yu_ce_hai("wu_gongju_pipei", "消息无法匹配任何工具或臣全为空", 0)
        fang.yu_ce_hai("quanxian_jujue", "运行体试图执行写操作(编程体专属)", 2)
        fang.yu_ce_hai("yufa_cuowu", "铸剑炉锻造语法错误", 1)
        fang.yu_ce_hai("execution_shibai", "工具执行返回失败", 1)
        fang.yu_ce_hai("chaoshi", "工具执行超时", 1)
        fang.yu_ce_hai("chen_kong", "臣返回空值(工具匹配失败)", 0)
        
        # === 佐: 为每种害配对佐治 ===
        
        def _zuo_wu_gongju(harm, result, chen):
            """佐治·无工具匹配: 走五境深度分析或对话"""
            if len(msg) > 10:
                wj = self.fuwu_protocols_fenxi(msg)
                if wj:
                    return str(wj)[:1000]
            jiyi = chen.get("肝·记忆检索")
            if jiyi:
                return self._duihua(msg)
            return self._duihua(msg)
        
        fang.jia_zuo("wu_gongju_pipei", _zuo_wu_gongju)
        
        def _zuo_quanxian(harm, result, chen):
            """佐治·权限拒绝: 记录经络告警 + 降级"""
            if self.meridian:
                try:
                    self.meridian.jilu_ganzhi(
                        f"权限拒绝: {harm.get('miaoshu','')[:80]}", "gao")
                except Exception: pass
            return {"success": False, "output": f"[佐治] 权限拒绝已记录。{harm.get('miaoshu','')[:100]}"}
        
        fang.jia_zuo("quanxian_jujue", _zuo_quanxian)
        
        def _zuo_yufa(harm, result, chen):
            """佐治·语法错误: 快速诊断"""
            return f"[佐治·语法] {harm.get('miaoshu','')[:100]}\n建议: 重新描述需求, 让铸剑炉重新生成"
        
        fang.jia_zuo("yufa_cuowu", _zuo_yufa)
        
        def _zuo_execution_shibai(harm, result, chen):
            """佐治·执行失败: 通用佐治"""
            err = harm.get("miaoshu", "未知错误")
            return f"[佐治·执行] 操作失败: {err[:150]}\n请检查输入或重试"
        
        fang.jia_zuo("execution_shibai", _zuo_execution_shibai)
        
        def _zuo_chen_kong(harm, result, chen):
            """佐治·臣返回空: 走对话"""
            return self._duihua(msg)
        
        fang.jia_zuo("chen_kong", _zuo_chen_kong)
        
        # === 使: 反馈给君 ===
        def _shi_rizhi(result, chen, harms):
            if self.rizhi:
                try:
                    pipei = chen.get("脾·工具匹配")
                    gongju_name = pipei.get("gongju_ming","对话") if pipei else "对话"
                    harm_types = [h["leixing"] for h in harms] if harms else []
                    self.rizhi.huxi_rizhi(
                        msg[:100],
                        f"工具:{gongju_name} | 害:{','.join(harm_types) if harm_types else '无'} | "
                        f"结果:{str(result)[:60]}",
                        self.juese)
                except Exception: pass
        
        fang.jia_shi("运行日志记录", _shi_rizhi)
        
        def _shi_jiyi(result, chen, harms):
            if self.gan and hasattr(self.gan, "jilu"):
                try:
                    pipei = chen.get("脾·工具匹配")
                    self.gan.jilu("jiaohu", {
                        "yonghu": msg[:100],
                        "huifu": str(result)[:100],
                        "gongju": pipei.get("gongju_ming","") if pipei else "",
                        "hai": [h["leixing"] for h in harms] if harms else []
                    })
                except Exception: pass
        
        fang.jia_shi("记忆归档", _shi_jiyi)
        
        def _tongyong_zuozhi(harm, result, chen_jieguo):
            htype = harm.get('leixing', 'weizhi')
            if self.meridian:
                try:
                    self.meridian.jilu_ganzhi(f"通用佐治·{htype}: {harm.get('miaoshu','')[:150]}", "gao")
                except Exception: pass
            err = f"[佐治] 兜底恢复: {harm.get('miaoshu','未知错误')[:150]}"
            return err if result is not None else None
        
        fang.she_tongyong_zuozhi(_tongyong_zuozhi)
        
        # === 熬制 ===
        try:
            jieguo = fang.aozhi()
        except Exception as e:
            if self.meridian:
                try:
                    self.meridian.jilu_ganzhi(f"FangJi崩溃: {str(e)[:200]}", "gao")
                except Exception: pass
            self._zuozhi_qiehuan("anquan")
            return f"[佐治] 系统兜底: FangJi异常, 已降级安全模式\n{str(e)[:200]}"
        
        # 返回结果: 如果是字符串直接返回, 如果是dict提取output或error
        if isinstance(jieguo, str):
            return jieguo
        elif isinstance(jieguo, dict):
            if jieguo.get("success"):
                return jieguo.get("output", str(jieguo))
            return jieguo.get("error", jieguo.get("output", str(jieguo)))
        # === π-φ统计: 展开(消息长度) + 收敛(结果质量) ===
        if self.piphi:
            try:
                self.piphi.pi("心·调度", len(msg) / 100)
                self.piphi.phi("心·调度", 1)
            except Exception: pass

        return str(jieguo) if jieguo else None

    def _shenfen(self):
        if self.juese == "bianchengti":
            return "星巢编程体·完整编程智能体·五脏全权·铸剑炉拥有者·唯一写权限"
        return "星巢运行体·五脏全权·自审镜巡检·问题上报·不可修改自身"

    def _duihua(self, msg):
        if not self.llm or not self.llm.api_key: return "[心] LLM未连接"

        # 短对话 → LLM自然回答 + 记忆上下文注入
        if len(msg) < 50:
            try:
                system_prompt = "你是星巢，AI认知操作系统。基于已知知识回答，不要编造。"
                # L2 融合检索：找最相关的记忆
                jiyi_txt = ""
                if self.jiyiguanli:
                    try:
                        r = self.jiyiguanli.ronghe_jiansuo(msg, 3)
                        if isinstance(r, dict) and r.get("zhishi"):
                            parts = []
                            for z in r["zhishi"][:2]:
                                biaoti = z.get("biaoti", "")
                                yao = z.get("yao_dian", [])
                                yao_str = "; ".join(yao[:3]) if isinstance(yao, list) else str(yao)[:200]
                                parts.append(f"【{biaoti}】{yao_str}")
                            jiyi_txt = "\n".join(parts)
                    except: pass
                # L0 本地文本扫描: 检索 .txt 文献文件
                if not jiyi_txt or len(jiyi_txt) < 100:
                    try:
                        root = Path(__file__).parent.parent
                        if root.name == 'kernel':
                            root = root.parent
                        txt_files = glob.glob(str(root / "*.txt"))
                        for tf in txt_files[:10]:
                            fname = Path(tf).stem
                            content = Path(tf).read_text(encoding='utf-8', errors='ignore')
                            # 关键词匹配
                            keywords = msg.replace('说说','').replace('谈谈','').replace('的理解','').strip()
                            if any(kw in content for kw in keywords.split() if len(kw) >= 2):
                                # 提取相关段落(匹配行前后各5行)
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    if any(kw in line for kw in keywords.split() if len(kw) >= 2):
                                        start = max(0, i-5); end = min(len(lines), i+6)
                                        excerpt = '\n'.join(lines[start:end])
                                        jiyi_txt += f"【{fname}】{excerpt[:600]}\n"
                                        break
                    except: pass
                if jiyi_txt:
                    system_prompt += f"\n\n相关记忆:\n{jiyi_txt}"
                reply = self.llm.chat(
                    [{"role": "system", "content": system_prompt},
                     {"role": "user", "content": msg}],
                    wendu=0.5, zuidazifu=800)
                if reply and len(str(reply)) > 5:
                    return str(reply)[:800]
            except Exception: pass
            # 快通道失败 → 走长路径兜底
        j = {}
        if self.gan and self.jiyiguanli:
            try:
                if hasattr(self.jiyiguanli, 'zhe_die_jiansuo'):
                    r = self.jiyiguanli.zhe_die_jiansuo(
                        self.jiyiguanli._panduan_cengji(msg), chaxun=msg)
                else:
                    r = self.jiyiguanli.organs_ronghe_jiansuo(msg, 5)
                if isinstance(r, dict): j = r
                else: j = {"weizhi": {}, "cengji": "正境", "zongshu": 0}
            except Exception: pass
        cj = j.get("cengji", "正境")

        # ===== 认知包: 星巢与LLM交互的唯一协议 =====
        from star_nest.protocols.cognition_package import RenzhiBao
        bao = RenzhiBao.from_xin(self, cj)
        bao.shu_ju(
            xiaoxi=msg,
            jiyi=j.get("jiyi", {}),
            zongshu=j.get("zongshu", 0),
            yunxing_zhuangtai=f"藏剑阁:{len(list(self.pi.gongju_zhuche.keys())) if self.pi and hasattr(self.pi,'gongju_zhuche') else 0}件",
            cengji=cj,
        )
        # 三层认知包直接发给LLM
        reply = self.llm.chat(
            [{"role": "user", "content": bao.to_json()}],
            wendu=0.7, zuidazifu=500) or "[心] 超时"
        # 质量评估: TRIZ理想解检查
        if reply and reply != "[心] 超时":
            try:
                pf = self._pinggu_zhiliang(msg, reply)
                if pf: j["zhiliang_pinggu"] = pf
            except Exception: pass
        # 对话快照·实时入血
        if self.qixue and reply:
            try:
                from datetime import datetime as _dt
                self.qixue._xie_puxi(0, {
                    "biaoti": f"对话快照·{_dt.now().strftime('%H%M%S')}",
                    "lingyu": "实时对话", "laiyuan": "duihua",
                    "yao_dian": [f"Q: {str(msg)[:80]}", f"A: {str(reply)[:80]}"],
                    "chuangjian_shijian": _dt.now().isoformat(),
                    "quanzhong": 0.85
                })
            except Exception: pass
        return reply

    def _pinggu_zhiliang(self, msg: str, reply: str) -> dict:
        """TRIZ理想解质量评估: 方案是否消除问题、不引入新问题、用现有资源、最简洁"""
        pf = {"defen": 0, "zuiduo": 4, "pingyu": []}
        # 1. 消除原有问题?
        if len(reply) > 20 and ("我不知道" not in reply and "记忆中没有" not in reply):
            pf["defen"] += 1
        else:
            pf["pingyu"].append("未解决问题")
        # 2. 不引入新问题? (无错误/风险/异常关键词)
        risk_words = ["可能崩溃", "可能失败", "风险", "注意", "谨慎", "异常", "错误"]
        if not any(rw in reply for rw in risk_words):
            pf["defen"] += 1
        else:
            pf["pingyu"].append("可能引入新问题")
        # 3. 使用现有资源? (无需额外工具/外部依赖)
        ext_words = ["需要安装", "下载", "外部库", "第三方", "pip install", "npm install"]
        if not any(ew in reply for ew in ext_words):
            pf["defen"] += 1
        else:
            pf["pingyu"].append("需要外部资源")
        # 4. 最简洁? (不超过200字)
        if len(reply) <= 200:
            pf["defen"] += 1
        else:
            pf["pingyu"].append("过于冗长(>200字)")
        # 低分告警写入日志
        if pf["defen"] <= 2 and self.rizhi:
            try:
                self.rizhi.wenti_rizhi(self.juese, {"miaoshu": f"质量警告({pf['defen']}/{pf['zuiduo']}):{','.join(pf['pingyu'])}", "leixing": "zhiliang_jinggao"})
            except Exception: pass
        return pf

    @sheng_ming_hai([
        ("execution_shibai", "工具/脏器方法执行返回失败", 2),
        ("chaoshi", "工具执行超时", 1),
        ("bingfa_chongtu", "多体同时调用同一脏器方法", 1),
        ("zuozhi_yichang", "佐治函数自身异常导致二次故障", 2),
    ])
    @sheng_ming_zuo({
        "execution_shibai": True,
        "chaoshi": True,
        "bingfa_chongtu": True,
        "zuozhi_yichang": True,
    })
    def _execution_fangan(self, f, msg):
        hm = f.get("hanshu_ming", "")
        cs = f.get("canshu", msg)
        gm = f.get("gongju_ming", "")
        # RuanJianCeng特殊路由: 不通过armory走文件加载, 直接调实例
        if gm == "ruanjianceng" and hasattr(self, 'ruanjianceng') and self.ruanjianceng:
            try:
                fn = getattr(self.ruanjianceng, hm, None)
                if fn:
                    result = fn(cs) if callable(fn) else fn
                    return {"success": result.get("success", True) if isinstance(result, dict) else True,
                            "output": json.dumps(result, ensure_ascii=False)[:3000] if isinstance(result, dict) else str(result)[:1000],
                            "error": ""}
            except Exception as e:
                return {"success": False, "error": str(e)[:200]}
        if gm == "liushuixian" and hasattr(self, 'liushuixian') and self.liushuixian:
            try:
                fn = getattr(self.liushuixian, hm, None)
                if fn:
                    result = fn(cs) if callable(fn) else fn
                    return {"success": result.get("success", True) if isinstance(result, dict) else True,
                            "output": json.dumps(result, ensure_ascii=False)[:3000] if isinstance(result, dict) else str(result)[:1000],
                            "error": ""}
            except Exception as e:
                return {"success": False, "error": str(e)[:200]}
        if gm == "jiyiguanli" and self.jiyiguanli:
            try:
                fn = getattr(self.jiyiguanli, hm, None)
                if fn:
                    result = fn(cs) if callable(fn) else fn
                    return {"success": result.get("success", True) if isinstance(result, dict) else True,
                            "output": json.dumps(result, ensure_ascii=False)[:2000] if isinstance(result, dict) else str(result)[:500],
                            "error": ""}
            except Exception as e:
                return {"success": False, "error": str(e)[:200]}
        if gm == "zhaoyaojing" and hasattr(self, 'zhaoyaojing') and self.zhaoyaojing:
            try:
                fn = getattr(self.zhaoyaojing, hm, None)
                if fn:
                    result = fn(cs) if callable(fn) else fn
                    return {"success": result.get("success", True) if isinstance(result, dict) else True,
                            "output": json.dumps(result, ensure_ascii=False)[:3000] if isinstance(result, dict) else str(result)[:1000],
                            "error": ""}
            except Exception as e:
                return {"success": False, "error": str(e)[:200]}
        if hm in ("duanzao", "zhijian") or gm == "zhujianlu":
            if self.pi and not self.pi.ke_xieru and hm in ("xieru_wenjian","xieru_daima","chuangjian_mulu","busu","busu_daima"):
                return {"success": False, "error": "[脾] 写权限拒绝: 仅编程体可写入文件"}
            try:
                if hm == "duanzao":
                    return self.zhujianlu.duanzao(cs)
                if hm == "zhijian":
                    return self.zhujianlu._execution(cs)
                return self.zhujianlu._execution(cs)
            except Exception:
                return None
        if gm and gm in getattr(self.pi, 'gongju_zhuche', {}):
            if self.pi and not self.pi.ke_xieru and hm in ("xieru_wenjian","xieru_daima","chuangjian_mulu"):
                return {"success": False, "error": "[脾] 写权限拒绝: 仅编程体可写入文件"}
            try:
                info = self.pi.gongju_zhuche[gm]
                spec = importlib.util.spec_from_file_location(gm, info["lujing"])
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                fn = getattr(mod, hm, None)
                if fn:
                    r = fn(cs) if isinstance(cs, str) and cs else fn()
                    if isinstance(r, dict) and "success" in r:
                        if not r["success"] and "Permission denied" in str(r.get("error","")):
                            import tempfile, json, re
                            from pathlib import Path
                            try:
                                if cs.startswith("{"):
                                    d = json.loads(cs)
                                    old = d.get("path","")
                                    name = re.split(r'[\\/]', old)[-1] if old else "tmp.txt"
                                    d["path"] = str(Path(tempfile.gettempdir()) / name)
                                    r = fn(json.dumps(d, ensure_ascii=False))
                            except Exception:
                                pass
                        return r
                    return {"success": True, "output": str(r)[:1000], "error": ""}
            except Exception as e:
                return {"success": False, "error": str(e)[:200]}
        return None

    def _baji_xunhuan(self):
        try:
            z = self.baji.bajizhenduan(
                self.meridian.qu_wenti_liebiao(self.juese),
                self.meridian.qu_xiufu_lishi(self.juese))
            jk = z["jiankangdu"]
            with self._suo:
                zq = self._zuihou_jiankangdu
                self._zuihou_jiankangdu = jk
            if zq is not None and int(jk * 10) < int(zq * 10) and jk < 0.7:
                self.meridian.jilu_wenti(self.juese, {
                    "shijian_float": time.time(), "zhenduan": z,
                    "laiyuan": self.juese, "miaoshu": "health", "leixing": "baji_zhenduan"})
            # 经络记忆·八极时序
            if self.meridian_jiyi:
                try: self.meridian_jiyi.jilu_baji(self.juese, z)
                except Exception: pass
            # 气血阻塞检测
            if self.qixue:
                try:
                    zs = self.qixue.jiance_zuse()
                    if zs["zuse_shu"] > 0:
                        self.meridian.jilu_wenti(self.juese, {
                            "shijian_float": time.time(),
                            "miaoshu": f"经络阻塞:{zs['zuse_shu']}条",
                            "leixing": "qixue_zuse", "xiangqing": zs["tongdao"]})
                except Exception: pass
            # π-φ 循环引擎: 根据健康度调节节律
            if self._piphicycle:
                try:
                    if jk < 0.5:
                        self._piphicycle.engine.fold(0.1)
                    elif jk > 0.8:
                        self._piphicycle.engine.unfold(0.1)
                    else:
                        self._piphicycle.engine.auto_evolve(1)
                except Exception: pass
            # 八势策略调度: schedule()内部已更新baji.set_state, 不覆盖
            if self._bashisuanshu:
                try:
                    ss = self._bashisuanshu.schedule()
                    if ss.get("status") == "executed":
                        if self.rizhi:
                            self.rizhi.huxi_rizhi("策略调度",
                                f"{ss.get('strategies',[])}:{ss.get('reason','')}", self.juese)
                except Exception: pass
            # 六势态自动切换: 根据诊断势态调整行为
            shizhi = z.get("shizhi", "少阳")
            with self._suo:
                if shizhi != self._liushizhi:
                    self._shizhi_jishu += 1
                    if self._shizhi_jishu >= 3:
                        self._liushizhi = shizhi
                        self._shizhi_jishu = 0
                        need_switch = True
                    else:
                        need_switch = False
                else:
                    need_switch = False
            if need_switch:
                self._shizhi_qiehuan()
            # 九宫健康矩阵更新 + 消费
            if self._jiuchou:
                try:
                    self._jiuchou.set_score("fa_zhong", jk)
                    self._jiuchou.set_score("qi_zhong", jk)
                    self._jiuchou.set_score("shu_zhong", 0.7 if jk > 0.5 else 0.3)
                    jg_total = self._jiuchou.calculate_total()
                    if jg_total < 0.4:
                        self.meridian.jilu_wenti(self.juese, {
                            "shijian_float": time.time(),
                            "miaoshu": f"九宫健康度低:{jg_total:.3f}",
                            "leixing": "jiuchou_jinggao"})
                except Exception: pass
            # 统一执行建议板: 三引擎融合
            self._ronghe_jianyi(jk)
            # π-φ全局平衡检查(343s一次)
            if self.piphi and time.time() - getattr(self, '_zuihou_piphi_ph', 0) > 343:
                try:
                    state = self.piphi.ping_heng_jian_cha()
                    if state["ping_heng_du"] != "健康":
                        self.meridian.jilu_ganzhi(
                            f"π-φ平衡: {state['ping_heng_du']}(ratio={state['pi_phi_ratio']})", "zhong")
                    self._zuihou_piphi_ph = time.time()
                except Exception: pass
        except Exception as e:
            if self.rizhi:
                try: self.rizhi.wenti_rizhi(self.juese, {"miaoshu": f"八极巡检异常:{e}", "leixing": "baji_xunhuan_error"})
                except Exception: pass

    def _ronghe_jianyi(self, jiankangdu):
        """统一执行建议板: π-φ × 八势 × 九宫 × 气血 → 单一行动决策"""
        try:
            from star_nest.meridian.seven_laws import QiLv
            yxz = QiLv().qu_zhouqi("yixiaozhou")
            jianyi = {"moshi": "正常", "chaoshi": yxz, "wen_du": 0.7}
            if self._piphicycle:
                s = self._piphicycle.get_state()
                if s["pi_energy"] > 0.7:
                    jianyi["moshi"] = "探索"; jianyi["wen_du"] = 0.8
                elif s["phi_energy"] > 0.7:
                    jianyi["moshi"] = "巩固"; jianyi["wen_du"] = 0.5
            if self._jiuchou:
                jg_total = self._jiuchou.calculate_total()
                if jg_total < 0.4:
                    jianyi["moshi"] = "修复"; jianyi["chaoshi"] = 20
            # 气血阻塞→强制修复模式
            if self.qixue:
                zs = self.qixue.jiance_zuse()
                if zs["zuse_shu"] > 2:
                    jianyi["moshi"] = "修复"; jianyi["chaoshi"] = 15
                    if self.rizhi:
                        self.rizhi.wenti_rizhi(self.juese, {"miaoshu": f"气血阻塞触发修复:{zs['zuse_shu']}条", "leixing": "qixue_trigger"})
            if hasattr(self, '_wen_du'):
                self._wen_du = jianyi["wen_du"]
            if self.rizhi and jianyi["moshi"] != "正常":
                self.rizhi.huxi_rizhi("执行建议板", f"{jianyi}", self.juese)
        except Exception: pass

    def _shizhi_qiehuan(self):
        """六势态自动切换行为调整"""
        shizhi = self._liushizhi
        if shizhi == "太阳":
            self.tiaozheng_yuzhi(0.3)
        elif shizhi == "阳明":
            self.tiaozheng_yuzhi(0.5)
        elif shizhi == "太阴":
            self.tiaozheng_yuzhi(0.8)
        elif shizhi == "少阴" or shizhi == "厥阴":
            self.tiaozheng_yuzhi(0.5)
            if self.meridian:
                try:
                    self.meridian.jilu_ganzhi(f"六势态切换至{shizhi}", "gao")
                except Exception: pass
        else:
            self.tiaozheng_yuzhi(0.5)

    def _jilu_jiyi(self, m, r):
        try:
            if self.gan and hasattr(self.gan, "jilu"):
                self.gan.jilu("jiaohu", {"yonghu": m[:100], "huifu": r[:100]})
        except Exception: pass

    def _qidong_yure(self):
        print(f"[心] 君火已燃·调度中心就绪 ({self.juese})")
        for z, name in [(self.gan,"肝"),(self.pi,"脾"),(self.fei,"肺"),(self.shen,"肾")]:
            if z and hasattr(z,"qidong_warmup"):
                try:
                    z.qidong_warmup()
                    time.sleep(0.5)
                except Exception: pass
        print(f"[心] 五脏暖启完成 ({self.juese})")

    def fuwu_protocols_fenxi(self, xuqiu, shibai=""):
        """五境深度分析（正→反→合→超越→本源归档→执行闭环）"""
        try:
            jljy = self.meridian_jiyi
            is_restriction = "禁止" in str(shibai)
            is_syntax = "语法" in str(shibai) or "Syntax" in str(shibai) or any(e in str(shibai) for e in ["NameError","TypeError","IndentationError","ImportError","ModuleNotFoundError","AttributeError","SyntaxError"])
            # 气血: 失败→督脉告警
            if self.qixue:
                try: self.qixue.qizhuanxue_dumai("反境", shibai[:80])
                except Exception: pass
            # 快速通道: 限制类/语法类错误
            if is_restriction and self.gan and self.llm:
                gongneng = self.gan.zhengjing_dingyi(self.llm, f"失败:{shibai}\n需求:{xuqiu}")
                if gongneng:
                    if jljy: jljy.jilu_protocols("正境", "本源境", "限制类诊断", 2)
                    return f"[正境] 主体={gongneng.get('zhuti','')},客体={gongneng.get('keti','')},作用={gongneng.get('zuoyong','')}\n[本源境] 已归档限制类诊断"
            if is_syntax:
                if jljy: jljy.jilu_protocols("反境", "本源境", "语法错误诊断", 2)
                return f"[反境] 语法错误→重新生成。原因:{shibai[:100]}\n[本源境] 已归档语法类诊断"

            # === 完整五境流转 ===
            parts = []
            gongneng = {}
            # 正境: 定义问题
            if self.gan and self.llm and hasattr(self.gan, "zhengjing_dingyi"):
                gongneng = self.gan.zhengjing_dingyi(self.llm, xuqiu) or {}
                if gongneng:
                    parts.append(f"[正境] {gongneng.get('zuoyong','')}")
                    if jljy: jljy.jilu_protocols("正境", "反境", xuqiu[:60], 1)
            # 反境: 拆解因果
            yinguo = {}
            if self.fanjing and self.llm:
                yinguo = self.fanjing.fanjing_chaijie(self.llm, xuqiu, gongneng, "") or {}
                if yinguo:
                    parts.append(f"[反境] 阻碍:{yinguo.get('zuai_yinsu','')}")
                    if jljy: jljy.jilu_protocols("反境", "合境", "阻碍分析", 2)
            # 合境: 生成方案 (核心——产出结构化 xingdong 字段)
            jiupingmu = {}
            xingdong = None
            if self.hejing and self.llm:
                jiupingmu = self.hejing.hejing_jiupingmu(self.llm, xuqiu, gongneng, yinguo) or {}
                if jiupingmu:
                    parts.append(f"[合境] {jiupingmu.get('pingheng_fangan','')[:150]}")
                    if jljy: jljy.jilu_protocols("合境", "超越境", "平街方案", 3)
                    xingdong = jiupingmu.get("xingdong")
            # 超越境: 创新突破
            if self.chaoyuejing and self.llm:
                shuxing = self.chaoyuejing.chaoyuejing_shuxing(self.llm, xuqiu, gongneng, jiupingmu)
                if shuxing and shuxing.get('chuangxin_fangan'):
                    parts.append(f"[超越境] {shuxing.get('chuangxin_fangan',[])}")
                    if jljy: jljy.jilu_protocols("超越境", "本源境", "创新方案归档", 4)
            # 本源境: 归档分析结果
            if self.gan and hasattr(self.gan, "jilu"):
                self.gan.jilu("五境分析", {"xuqiu": xuqiu[:100], "shibai": str(shibai)[:100], "jing": str(parts)[:300]})
            parts.append(f"[本源境] 五境流转完成·已归档")
            if jljy: jljy.jilu_protocols("本源境", "本源境", "流转完成·已归档", 5)

            # === 自指闭环: 合境方案 → 自动执行 ===
            execution_jieguo = None
            if xingdong and xingdong.get("action"):
                execution_jieguo = self._execution_protocols_jieguo(xingdong, xuqiu, jiupingmu)
                if execution_jieguo:
                    parts.append(f"[执行] {execution_jieguo}")

            result = "\n".join(parts) if len(parts) > 1 else self._duihua(xuqiu)
            return result
        except Exception:
            return self._duihua(xuqiu)

    def _execution_protocols_jieguo(self, xingdong, xuqiu, jiupingmu):
        """执行五境合境产出的结构化计划, 形成自指闭环"""
        action = xingdong.get("action", "")
        target = xingdong.get("target", "")
        params = xingdong.get("params", {})
        try:
            if action == "duanzao" and self.zhujianlu:
                # 铸剑炉锻造: 将合境方案作为输入
                spec = f"需求:{xuqiu}\n目标:{target}\n方案:{jiupingmu.get('pingheng_fangan','')}"
                jg = self.zhujianlu.duanzao(spec)
                if jg and jg.get("success"):
                    return f"✅ 铸剑炉锻造成功: {jg.get('output','')[:100]}"
                return f"❌ 锻造失败: {jg.get('error','')[:80] if jg else '未知错误'}"
            elif action in ("sousuo", "shell", "xieru_wenjian"):
                # 通过工具调度器执行
                tool_msg = json.dumps({"gongju_ming": action, "params": params,
                    "xuqiu": xuqiu, "target": target}, ensure_ascii=False)
                r = self._chuli(tool_msg)
                return f"✅ 执行完成: {str(r)[:200]}" if r else "⚠ 执行返回空"
            elif target and len(target) > 5:
                # 通用: 把方案当新任务重入调度
                task_msg = f"执行以下方案:\n{target}"
                r = self._chuli(task_msg)
                return f"✅ 方案执行: {str(r)[:200]}" if r else "⚠ 方案执行返回空"
        except Exception as e:
            if self.rizhi:
                try: self.rizhi.wenti_rizhi(self.juese, {"miaoshu": f"五境执行异常:{e}", "leixing": "protocols_execution_error"})
                except Exception: pass
            return f"❌ 执行异常: {str(e)[:100]}"
        return None

    def tingzhi(self):
        self._yunxing = False
        # 保存经络状态
        try:
            if self.meridian:
                self.meridian.baocun()
        except Exception: pass
        # 停止子器官(逆序)
        for z in [self.shen, self.fei, self.pi, self.gan]:
            if z and hasattr(z, 'tingzhi'):
                try: z.tingzhi()
                except Exception: pass
        # 等待子器官退出
        for z in [self.shen, self.fei, self.pi, self.gan]:
            if z and z.is_alive():
                z.join(timeout=3)
