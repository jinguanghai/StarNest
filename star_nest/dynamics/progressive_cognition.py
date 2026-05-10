"""
渐进认知引擎 JianJinRenZhi V1.0 [星巢·无阈值认知管道]

核心理念:
  所有输入 -> 缓冲池(不分类) -> 语义分块 -> 渐进五境处理 -> 六势态动态更新 -> 终判+响应

没有:
  - 无字符数阈值 (>500 >50 >15 全部移除)
  - 无入口分类 (不预先判断执行/对话/投喂)
  - 无硬编码白名单 (判断交给 LLM 认知包)

有:
  - 缓冲持久化(跨进程)
  - 六势态动态演化(少阳->太阳/太阴/厥阴)
  - 内容终了检测(自然停顿或明确结束)
  - 恶意模式渐进升级
"""
import time, json, threading
from pathlib import Path
from star_nest.dynamics.constants import (
    AN_QUAN_E_YI, AN_QUAN_KE_YI, ZHI_SHI_TAI_YIN, ZHI_SHI_TAI_YANG,
    ZHI_XING_TAI_YANG, ZHI_XING_YANG_MING, WEI_XIAN_JUE_YIN, WEI_XIAN_SHAO_YIN,
    ZHI_SHI_BU_CHANG, AN_QUAN_ZENG_LIANG, AN_QUAN_JIAN_LIANG, ZHI_XING_BU_CHANG, WEI_XIAN_E_YI_BU_CHANG,
    FEN_KUAI_YU_YI, LLM_WEN_DU_QUE_DING, LLM_ZI_FU_ZHONG,
    KONG_XIAN_ZHONG_JUE, BUFFER_CHAO_SHI,
)


class JianJinRenZhi:
    """
    渐进认知引擎
    
    处理循环(后台线程):
      1. 缓冲池: 收集所有输入, 不限长短
      2. 分块器: 按语义单元切分(标题/段落/空行)
      3. 五境处理: 每块走 正->反->合->超越->本源
      4. 六势动态: 处理后更新态势评估
      5. 终判: 内容终了或态势明确->决策+响应
    """

    def __init__(self, xin):
        self.xin = xin
        self._buffer = []           # 原始输入缓冲
        self._protocols_notes = []     # 五境笔记(逐块积累)
        self._liushi = {            # 六势态动态状态
            "shizhi": "少阳",        # 当前态势
            "anquan_du": 0.5,        # 安全度(0=危险, 1=安全)
            "zhishi_midu": 0.0,      # 知识密度(>0.5=太阴倾向)
            "execution_yitu": 0.0,     # 执行意图(>0.5=太阳/阳明倾向)
            "weixian_xinhao": 0,     # 危险信号计数
            "chunk_count": 0,        # 已处理块数
        }
        self._doc_title = ""
        self._start_time = 0
        self._active = False
        self._lock = threading.Lock()
        self._jiange_timer = 0      # 最后输入时间
        self._processing = False    # 后台处理中标志
        self._bg_thread = None      # 后台处理线程
        self._finalized = False     # 已终判标志

        self._state_file = Path(__file__).parent.parent / "huanjing" / "jianjin_state.json"
        self._state_file.parent.mkdir(parents=True, exist_ok=True)

    # ==================== 入口 ====================

    def tian_jia(self, text: str) -> str:
        """
        添加输入到缓冲池。非阻塞立返。
        
        跨进程文件桥接:
          - 缓冲持久化到 jianjin_state.json
          - 终判启动后台线程 -> 结果写 jianjin_result.txt
          - 下次调用发现结果文件 -> 推 shuchu_duilie -> 删文件
        """
        text = text.strip()
        if not text:
            return ""

        # 检查未兑现的终判结果(上次进程启动的线程已完成)
        self._jian_cha_zhongjue_jieguo()

        with self._lock:
            if not self._active:
                self._jia_zai_zhuangtai()

            if text == "结束":
                return self._jie_shu()

            # 自动终判: 旧缓冲超时 -> 启动后台线程(不阻塞), 立返缓冲状态
            if self._active and self._buffer and time.time() - self._jiange_timer >= KONG_XIAN_ZHONG_JUE:
                self._qidong_zhongjue_thread()
                self._jiange_timer = 0

            if not self._active:
                self._active = True
                self._start_time = time.time()
                self._doc_title = text[:80].replace('\n', ' ')

            self._buffer.append(text)
            self._jiange_timer = time.time()
            self._finalized = False
            self._baocun_zhuangtai()
            buf_size = len(self._buffer)

        if buf_size >= 3 and not self._processing:
            self._qidong_houtai_chuli()

        return f"[缓冲] 已收集 {buf_size} 段输入"

    def _jian_cha_zhongjue_jieguo(self):
        """检查文件桥接: 上次进程的终判线程是否已完成"""
        result_file = self._state_file.parent / "jianjin_result.txt"
        try:
            if result_file.exists():
                result = result_file.read_text(encoding='utf-8').strip()
                if result and self.xin:
                    self.xin.shuchu_duilie.put(result)
                result_file.unlink()
        except Exception:
            pass

    def _qidong_zhongjue_thread(self):
        """启动终判线程: 异步LLM处理, 结果写文件桥接(跨进程)"""
        old_buf = list(self._buffer)
        self._buffer = []
        self._active = False
        result_file = self._state_file.parent / "jianjin_result.txt"

        def _worker():
            try:
                while self._processing:
                    time.sleep(0.2)
                self._zhongjue_chuli_from_buf(old_buf)
                verdict = self._zhong_jue_duan()
                result = self._zhi_xing_jue_duan(verdict) or ""
                if result:
                    result_file.write_text(result, encoding='utf-8')
                self._qing_li_lockless()
            except Exception:
                pass

        threading.Thread(target=_worker, daemon=True).start()
        result = ""
        if self._buffer:
            # 解锁后处理(含LLM)
            buf_saved = list(self._buffer)
            self._buffer = []
            self._lock.release()
            try:
                self._zhongjue_chuli_from_buf(buf_saved)
                verdict = self._zhong_jue_duan()
                result = self._zhi_xing_jue_duan(verdict)
            finally:
                self._lock.acquire()
        self._qing_li_lockless()
        if result:
            return result
        return "[完成] 渐进认知结束"

    # ==================== 后台处理线程 ====================

    def _qidong_houtai_chuli(self):
        """启动后台线程处理缓冲(非阻塞)"""
        self._processing = True
        # 拷贝缓冲到线程安全区域
        buf_copy = list(self._buffer)
        self._buffer = []
        
        def _worker():
            try:
                # 语义分块
                full = "\n\n".join(buf_copy)
                chunks = self._yu_yi_fen_kuai(full)
                if not chunks:
                    return
                # 渐进处理每块
                for i, chunk in enumerate(chunks):
                    note = self._chu_li_kuai(chunk, i, len(chunks))
                    with self._lock:
                        self._liushi["chunk_count"] += 1
                        if self._liushi["shizhi"] == "厥阴":
                            # 检测到恶意 -> 中断
                            exie_result = self._chu_li_exie(full)
                            if self.xin:
                                self.xin.shuchu_duilie.put(exie_result)
                            return
                # 处理完成 -> 更新状态
                with self._lock:
                    self._baocun_zhuangtai()
                # 中间摘要写经络, 不打印(静默后台)
                if self.xin and self.xin.meridian:
                    try:
                        summary = self._sheng_cheng_zhongjian_zhaiyao()
                        self.xin.meridian.jilu_fansi(f"渐进·{len(chunks)}块: {summary[:200]}")
                    except Exception: pass
            except Exception as e:
                if self.xin and self.xin.meridian:
                    try:
                        self.xin.meridian.jilu_fansi(f"渐进认知·后台处理异常: {e}")
                    except Exception: pass
            finally:
                self._processing = False
        
        self._bg_thread = threading.Thread(target=_worker, daemon=True)
        self._bg_thread.start()

    def _qing_li_lockless(self):
        """清理状态(锁外调用)"""
        self._buffer = []
        self._protocols_notes = []
        self._liushi = {
            "shizhi": "少阳", "anquan_du": 0.5,
            "zhishi_midu": 0.0, "execution_yitu": 0.0,
            "weixian_xinhao": 0, "chunk_count": 0,
        }
        self._doc_title = ""
        self._active = False
        self._processing = False
        self._finalized = True
        try:
            if self._state_file.exists():
                self._state_file.unlink()
        except Exception: pass

    # ==================== 语义分块 ====================

    def _yu_yi_fen_kuai(self, text: str) -> list:
        """语义分块: 按标题/段落/空行切分, 无固定大小限制"""
        # 按双空行切分(最大语义单元)
        if '\n\n' in text:
            raw = [k.strip() for k in text.split('\n\n') if k.strip()]
            return raw

        # 按单段落切分
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) <= 1:
            return lines

        # 合并短行(相邻短句合并为一块)
        chunks = []
        buf = ""
        for line in lines:
            if len(buf) + len(line) < FEN_KUAI_YU_YI:
                buf = (buf + '\n' + line).strip()
            else:
                if buf: chunks.append(buf)
                buf = line
        if buf: chunks.append(buf)
        return chunks if len(chunks) > 1 else lines

    # ==================== 单块五境处理 ====================

    def _chu_li_kuai(self, chunk: str, index: int, total: int) -> dict:
        """单块走五境: 正->反->合->超越->本源"""
        note = {"kuai_id": index + 1, "yu_wen": chunk[:200]}

        # 正境: 这块说什么
        note["zheng"] = self._zheng_jing(chunk, index, total)
        # 反境: 和前面矛盾吗/有什么新信息
        note["fan"] = self._fan_jing(chunk, note["zheng"])
        # 合境: 整体理解推进到哪里
        note["he"] = self._he_jing(note["zheng"], note["fan"])
        # 超越境: 深层含义
        note["chao"] = self._chao_yue_jing(note)
        # 本源境: 记忆归档
        note["ben"] = self._ben_yuan_jing(chunk, note)

        self._protocols_notes.append(note)
        self._geng_xin_liushizhi(note)
        return note

    def _zheng_jing(self, chunk: str, i: int, total: int) -> dict:
        """正境: 定义这块文本的边界"""
        if self.xin.llm and self.xin.llm.api_key:
            try:
                prompt = (
                    f"你正在阅读一份文档(第{i+1}/{total}块):\n{chunk[:500]}\n"
                    "输出JSON: {\"leixing\":\"标题\"|\"正文\"|\"列表\"|\"引用\"|\"代码\"|\"结束\","
                    "\"he_xin\":\"核心内容(一句)\",\"xin_xi\":\"与前面相比的新信息\","
                    "\"wei_xian\":false}"
                )
                jg = self.xin.llm.chat([{"role":"user","content":prompt}],
                                        wendu=LLM_WEN_DU_QUE_DING, zuidazifu=LLM_ZI_FU_ZHONG)
                if jg and "{" in str(jg):
                    import json
                    return json.loads(jg[jg.index("{"):jg.rindex("}")+1])
            except Exception: pass
        return {"leixing": "正文", "he_xin": chunk[:100], "xin_xi": "", "wei_xian": False}

    def _fan_jing(self, chunk: str, zheng: dict) -> dict:
        """反境: 与已有积累对比, 检测矛盾/缺口"""
        contradictions = []
        gaps = []

        # 与前一块对比
        if len(self._protocols_notes) >= 1:
            prev = self._protocols_notes[-1].get("zheng", {})
            prev_core = prev.get("he_xin", "")
            curr_core = zheng.get("he_xin", "")
            # 简单语义对比(无LLM时)
            if prev_core and curr_core:
                if any(kw in prev_core for kw in ["但是", "然而", "不过", "相反"]):
                    contradictions.append("前块有转折信号")
                if len(curr_core) < 10 and len(prev_core) > 50:
                    gaps.append("当前块信息量骤降")

        return {"mao_dun": contradictions, "que_kou": gaps,
                "xin_xin_xi": zheng.get("xin_xi", "")}

    def _he_jing(self, zheng: dict, fan: dict) -> dict:
        """合境: 整体理解推进"""
        zonghe = "未知"
        if zheng.get("leixing") == "标题":
            zonghe = f"新章节: {zheng.get('he_xin','')}"
        elif zheng.get("wei_xian"):
            zonghe = "危险信号"
        else:
            zonghe = f"知识积累: {zheng.get('he_xin','')[:80]}"
        return {"jin_zhan": zonghe, "zhishi_yue_jin": len(self._protocols_notes) < 3}

    def _chao_yue_jing(self, note: dict) -> dict:
        """超越境: 深层关联和模式"""
        return {"mo_shi": "", "yin_yu": "",
                "guan_lian": f"第{note['kuai_id']}块与全文关系"}

    def _ben_yuan_jing(self, chunk: str, note: dict) -> str:
        """本源境: 记忆归档"""
        try:
            if self.xin.gan and hasattr(self.xin.gan, 'jilu'):
                self.xin.gan.jilu("渐进认知", {
                    "kuai_id": note["kuai_id"],
                    "he_xin": note.get("zheng", {}).get("he_xin", chunk[:100]),
                    "wen_ben": chunk[:300]
                })
        except Exception: pass
        return "已归档"

    # ==================== 六势态动态更新 ====================

    def _geng_xin_liushizhi(self, note: dict):
        """处理后更新六势态评估 + 同步到全局状态S"""
        zheng = note.get("zheng", {})

        if zheng.get("leixing") in ("正文", "列表", "引用"):
            self._liushi["zhishi_midu"] = min(0.9, self._liushi["zhishi_midu"] + ZHI_SHI_BU_CHANG)
        if zheng.get("leixing") == "代码":
            self._liushi["execution_yitu"] = min(0.9, self._liushi["execution_yitu"] + ZHI_XING_BU_CHANG)
        if zheng.get("wei_xian", False):
            self._liushi["weixian_xinhao"] += WEI_XIAN_SHAO_YIN
            self._liushi["anquan_du"] = max(0, self._liushi["anquan_du"] - AN_QUAN_JIAN_LIANG)
        else:
            self._liushi["anquan_du"] = min(1.0, self._liushi["anquan_du"] + AN_QUAN_ZENG_LIANG)

        lower = str(note.get("yu_wen", "")).lower()
        malware_pats = ["eval(", "exec(", "os.system(", "subprocess.call",
                        "rm -rf", "del /f", "format c:", "wscript.shell",
                        "CreateRemoteThread", "WriteProcessMemory", "base64.decode"]
        for pat in malware_pats:
            if pat in lower:
                self._liushi["weixian_xinhao"] += WEI_XIAN_E_YI_BU_CHANG
                self._liushi["anquan_du"] = max(0, self._liushi["anquan_du"] - 0.3)
                break

        self._liushi["shizhi"] = self._jisuan_shizhi()

        # 同步到全局状态 S (四次读: 肾八极·肺安全·脾工具·肝记忆 -> 心综合)
        try:
            from star_nest.dynamics.global_state import get_global_state
            S = get_global_state(self.xin)
            S.zhishi_midu = self._liushi["zhishi_midu"]
            S.execution_yitu = self._liushi["execution_yitu"]
            S.chunk_count = self._liushi["chunk_count"]
            S.anquan_du = self._liushi["anquan_du"]
            S.shizhi = self._liushi["shizhi"]
            S.save()
        except Exception:
            pass

    def _jisuan_shizhi(self) -> str:
        w = self._liushi
        if w["weixian_xinhao"] >= WEI_XIAN_JUE_YIN or w["anquan_du"] < AN_QUAN_E_YI:
            return "厥阴"
        if w["weixian_xinhao"] >= WEI_XIAN_SHAO_YIN or w["anquan_du"] < AN_QUAN_KE_YI:
            return "少阴"
        if w["execution_yitu"] > ZHI_XING_TAI_YANG:
            return "太阳"
        if w["execution_yitu"] > ZHI_XING_YANG_MING and w["zhishi_midu"] < ZHI_SHI_TAI_YIN:
            return "阳明"
        if w["zhishi_midu"] > ZHI_SHI_TAI_YIN and w["execution_yitu"] < ZHI_SHI_TAI_YANG:
            return "太阴"
        return "少阳"

    # ==================== 终判+执行 ====================

    def _zhong_jue_duan(self) -> dict:
        """
        内容终了时的最终判断
        
        输出: {panduan, liyou, xingdong, shizhi, anquan_du}
        panduan: "知识内容" | "执行任务" | "恶意内容" | "混合内容" | "对话交互"
        """
        w = self._liushi
        shizhi = w["shizhi"]

        if shizhi == "厥阴":
            return {"panduan": "恶意内容", "liyou": f"危险信号{w['weixian_xinhao']}个,安全度{w['anquan_du']:.2f}",
                    "xingdong": "隔离+告警+归档", "shizhi": shizhi, "anquan_du": w["anquan_du"]}

        if shizhi == "少阴" and w["zhishi_midu"] > 0.3:
            return {"panduan": "知识内容·含可疑模式", "liyou": "有可疑信号但整体为知识文本",
                    "xingdong": "安全审查后消化", "shizhi": shizhi, "anquan_du": w["anquan_du"]}

        if w["zhishi_midu"] > 0.4 and w["execution_yitu"] < 0.2:
            return {"panduan": "知识内容", "liyou": f"知识密度{w['zhishi_midu']:.2f},共{self._liushi['chunk_count']}块",
                    "xingdong": "四层消化+记忆归档", "shizhi": shizhi, "anquan_du": w["anquan_du"]}

        if w["execution_yitu"] > 0.3 and w["zhishi_midu"] > 0.3:
            return {"panduan": "混合内容", "liyou": "既有知识也有执行意图",
                    "xingdong": "知识消化+执行确认", "shizhi": shizhi, "anquan_du": w["anquan_du"]}

        if w["execution_yitu"] > 0.3:
            return {"panduan": "执行任务", "liyou": f"执行意图{w['execution_yitu']:.2f}",
                    "xingdong": "匹配工具+确认+执行", "shizhi": shizhi, "anquan_du": w["anquan_du"]}

        return {"panduan": "知识内容", "liyou": f"{self._liushi['chunk_count']}块内容,默认消化",
                "xingdong": "四层消化+记忆归档", "shizhi": shizhi, "anquan_du": w["anquan_du"]}

    def _zhi_xing_jue_duan(self, verdict: dict) -> str:
        """
        使·四路反馈: 杀毒/投喂/执行/聊天
        
        基于终判的 panduan 字段选择输出管道:
          - 恶意内容 -> 使·杀毒: 隔离阻断+经络告警
          - 知识内容 -> 使·投喂: 四层消化+记忆归档
          - 执行任务 -> 使·执行: 铸剑炉FangJi
          - 对话交互 -> 使·聊天: LLM自然对话
        """
        pd = verdict["panduan"]
        full = "\n\n".join([n.get("yu_wen", "") for n in self._protocols_notes])

        # 使·杀毒: 恶意->阻断
        if pd == "恶意内容":
            if self.xin.meridian:
                try:
                    self.xin.meridian.jilu_ganzhi(
                        f"使·杀毒: {verdict['liyou']}", "gao")
                except Exception: pass
            return f"[使·杀毒] {verdict['liyou']}\n已隔离, 不执行."

        # 使·投喂: 知识·可疑->审查后消化
        if pd == "知识内容·含可疑模式":
            if self.xin.shuruceng:
                try:
                    result = self.xin.shuruceng._xiaohua_shenceng(full)
                    if result:
                        return f"[使·投喂] 安全审查通过, 内容已消化:\n{result[:2000]}"
                except Exception: pass
            return f"[使·审查] {verdict['liyou']}"

        # 使·投喂: 知识/混合->四层消化
        if pd in ("知识内容", "混合内容"):
            if self.xin.shuruceng and len(full) > 100:
                try:
                    result = self.xin.shuruceng._xiaohua_shenceng(full)
                    if result:
                        return f"[使·投喂] {verdict['liyou']}\n{result[:2000]}"
                except Exception: pass
            return f"[使·投喂] {self._doc_title} — {verdict['liyou']}"

        # 使·执行: 铸剑炉FangJi
        if pd == "执行任务":
            result = self.xin._ao_yao_chuli(full)
            if result:
                return f"[使·执行] {verdict['liyou']}\n{str(result)[:2000]}"
            return f"[使·执行] {verdict['liyou']}"

        # 使·聊天: 默认->LLM对话
        return f"[使·聊天] {self._doc_title}"

    def _chu_li_exie(self, full: str) -> str:
        """使·杀毒: 明确恶意 -> 阻断+归档"""
        if self.xin.meridian:
            try:
                self.xin.meridian.jilu_ganzhi("使·杀毒·恶意阻断", "gao")
                self.xin.meridian.jilu_fansi(f"使·杀毒: {full[:200]}")
            except Exception: pass
        if self.xin.gan and hasattr(self.xin.gan, 'jilu'):
            try:
                self.xin.gan.jilu("恶意输入缓存", {
                    "neirong": full[:1000],
                    "weixian_xinhao": self._liushi["weixian_xinhao"],
                    "shijian": str(time.time())
                })
            except Exception: pass
        self._qing_li()
        return f"[使·杀毒] 检测到恶意内容(危险信号{self._liushi['weixian_xinhao']}), 已隔离."

    # ==================== 中间摘要 ====================

    def _sheng_cheng_zhongjian_zhaiyao(self) -> str:
        """生成中间状态摘要"""
        w = self._liushi
        lines = [f"'{self._doc_title}' — {w['chunk_count']}块已处理"]
        lines.append(f"六势: {w['shizhi']} | 知识密度: {w['zhishi_midu']:.2f} | 安全度: {w['anquan_du']:.2f}")
        if self._protocols_notes:
            last = self._protocols_notes[-1].get("zheng", {})
            if last.get("he_xin"):
                lines.append(f"最近: {last['he_xin'][:100]}")
        return "\n".join(lines)

    # ==================== 持久化 ====================

    def _baocun_zhuangtai(self):
        """保存状态到文件(跨进程)"""
        try:
            state = {
                "active": self._active,
                "doc_title": self._doc_title,
                "buffer": self._buffer,
                "liushi": self._liushi,
                "chunk_count": len(self._protocols_notes),
                "start_time": self._start_time,
            }
            self._state_file.write_text(json.dumps(state, ensure_ascii=False), encoding='utf-8')
        except Exception: pass

    def _jia_zai_zhuangtai(self) -> bool:
        """加载跨进程状态"""
        try:
            if self._state_file.exists():
                state = json.loads(self._state_file.read_text(encoding='utf-8'))
                if state.get("active") and time.time() - state.get("start_time", 0) < BUFFER_CHAO_SHI:
                    self._active = True
                    self._doc_title = state.get("doc_title", "")
                    self._buffer = state.get("buffer", [])
                    self._liushi = state.get("liushi", self._liushi)
                    self._start_time = state.get("start_time", time.time())
                    return True
                else:
                    self._state_file.unlink()
        except Exception: pass
        return False

    def _qing_li(self):
        """清理状态(锁内调用)"""
        self._buffer = []
        self._protocols_notes = []
        self._liushi = {
            "shizhi": "少阳", "anquan_du": 0.5,
            "zhishi_midu": 0.0, "execution_yitu": 0.0,
            "weixian_xinhao": 0, "chunk_count": 0,
        }
        self._doc_title = ""
        self._active = False
        self._processing = False
        self._finalized = True
        try:
            if self._state_file.exists():
                self._state_file.unlink()
        except Exception: pass

    def qu_zhuangtai(self) -> dict:
        return {"active": self._active, "doc_title": self._doc_title,
                "liushi": self._liushi, "buffer_size": len(self._buffer),
                "notes_count": len(self._protocols_notes)}

    # ==================== 五境异常分析 (铁律15基础设施) ====================

    def protocols_yichang_fenxi(self, yichang_type: str, yichang_text: str, laiyuan: str = "") -> dict:
        """
        五境异常认知分析 V1.0
        
        经络发现新异常模式(_new_pattern=True) -> 触发此方法
        使用 RenzhiBao("反境") 让 LLM 分析:
          - 这是 bug 还是预期行为?
          - 应该添加什么 @sheng_ming_hai 声明?
          - 建议的佐治策略?
        
        频率限制: 每种异常类型最多分析 1 次(通过经络节点 count 控制)
        """
        if not self.xin or not self.xin.llm or not self.xin.llm.api_key:
            return {"panduan": "无LLM, 跳过分析"}

        try:
            from star_nest.protocols.cognition_package import RenzhiBao
            bao = RenzhiBao("反境")
            bao.shu_ju(
                yichang_leixing=yichang_type,
                yichang_neirong=yichang_text[:500],
                laiyuan=laiyuan,
                yao_qiu=(
                    "分析这个异常模式, 输出JSON: "
                    '{"panduan":"bug"|"yuqi"|"weizhi", '
                    '"hai_leixing":"建议的害类型名", '
                    '"hai_miaoshu":"害描述", '
                    '"yanzhongdu":0-3, '
                    '"zuozhi_jianyi":"佐治建议"}'
                )
            )
            jg = self.xin.llm.chat([{"role":"user","content":bao.to_json()}],
                                   wendu=0.15, zuidazifu=500)
            if jg and "{" in str(jg):
                import json
                text = str(jg)
                return json.loads(text[text.index("{"):text.rindex("}")+1])
        except Exception:
            pass
        return {"panduan": "weizhi", "hai_miaoshu": str(yichang_text)[:200], "yanzhongdu": 1}
