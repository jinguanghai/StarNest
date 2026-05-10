"""
五脏·肝 (gan.py) - 藏魂，将军之官，谋虑出焉
V10.4 零提示词版：三层记忆 + 免疫系统（六势态统一修复）+ 五行信号响应。
所有LLM调用改用结构化数据包，不再包含任何自然语言提示词。

【通用问题解决操作系统·记忆调用映射】
- 正境(Define)：zhengjing_dingyi——功能分析，作用=改变客体的xx参数
- 反境(Measure & Analyze)：ronghe_jiansuo——融合检索辅助因果拆解
- 合境(Improve)：hejing_jiansuo——检索历史成功方案辅助九屏幕法
- 超越境(Control)：免疫循环——从经络获取诊断（含五行信号），调用自我修复
- 本源境(Sustain)：_baocun_suoyin——索引快照持久化

【V10.4 零提示词】
zhengjing_dingyi 不再发送"你是一个功能分析专家..."提示词，
改为发送结构化JSON数据包：{renwu, shenfen, jiyi, yonghu_xiaoxi, yaoqiu}
星巢DMN → 结构化数据 → LLM类DMN → 统计拟合 → 返回结果
"""

import threading, time, re, sqlite3, json, shutil, traceback
from star_nest.protocols.harm_assist import sheng_ming_hai, sheng_ming_zuo
from collections import deque
from pathlib import Path
from datetime import datetime
from queue import Queue
from star_nest.dynamics.self_repair import ZiWoXiuFu
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class XiangliangSuoyin:
    """V11.1 向量索引: 字符2-gram Jaccard检索, 从xiangliang_suoyin.json加载"""
    def __init__(self, mulu):
        # 多路径鲁棒: mulu可能是项目根或子目录
        base = Path(mulu) if isinstance(mulu, Path) else Path(str(mulu))
        candidates = [base / "xiangliang_suoyin.json"]
        # 尝试向上找 shared_memory/
        p = base
        for _ in range(4):
            p = p.parent
            candidate = p / "shared_memory" / "xiangliang_suoyin.json"
            candidates.append(candidate)
        self.json_path = None
        for c in candidates:
            try:
                if c.exists():
                    self.json_path = c
                    break
            except Exception: pass
        if not self.json_path:
            self.json_path = candidates[1]  # 默认
        self.idf = {}
        self.wendang = {}
        self._yijiazai = False

    def _jiazai(self):
        if self._yijiazai:
            return
        try:
            data = json.loads(self.json_path.read_text(encoding='utf-8'))
            self.idf = data.get('idf', {})
            self.wendang = data.get('wendang', {})
            self._yijiazai = True
        except Exception as e:
            if not hasattr(self, '_rizhi_shibai'):
                self._rizhi_shibai = True
                print(f"[向量索引] 加载失败: {self.json_path} ({e})，检索将降级为关键词匹配")
            self.idf = {}
            self.wendang = {}
            self._yijiazai = True

    def _chouqu_guanjianci(self, wenben):
        ci = re.findall(r'[\u4e00-\u9fa5]{2,}|\w{3,}', str(wenben).lower())
        return list(set([c for c in ci if not c.isdigit()]))

    def _jisuan_tfidf(self, terms):
        """计算查询的TF-IDF向量"""
        tf = {}
        for t in terms:
            tf[t] = tf.get(t, 0) + 1
        vec = {}
        for t, f in tf.items():
            if t in self.idf:
                vec[t] = f * self.idf[t]
        return vec

    def _yuxian_xiangsi(self, q_vec, doc_id):
        """计算查询向量与文档向量的余弦相似度"""
        doc = self.wendang.get(doc_id)
        if not doc:
            return 0.0
        d_tf = doc.get('tf', {})
        dot = 0.0
        q_norm2 = 0.0
        d_norm2 = 0.0
        for t, qv in q_vec.items():
            q_norm2 += qv * qv
            dv = d_tf.get(t, 0)
            dot += qv * dv
            d_norm2 += dv * dv
        for dv in d_tf.values():
            d_norm2 += dv * dv
        if q_norm2 == 0 or d_norm2 == 0:
            return 0.0
        return dot / ((q_norm2 ** 0.5) * (d_norm2 ** 0.5))

    def jiansuo(self, query, top_k=3):
        """字符2-gram Jaccard检索: 返回[(doc_id, score, metadata, yuanwen), ...]"""
        self._jiazai()
        if not self.wendang:
            return []
        q = str(query)
        clean = ''.join(c for c in q if c.isalpha() or c.isdigit()).lower()
        q_ngrams = set()
        for i in range(len(clean) - 1):
            q_ngrams.add(clean[i:i+2])
        if not q_ngrams:
            return []
        # 短查询(<=3个2-gram)用重叠计数, 长查询用Jaccard
        duan_chaxun = len(q_ngrams) <= 3
        scores = []
        seen_ids = set()
        for doc_id in self.wendang:
            doc = self.wendang[doc_id]
            doc_text = ''.join(doc.get('tf', {}).keys())
            doc_ngrams = set()
            for i in range(len(doc_text) - 1):
                doc_ngrams.add(doc_text[i:i+2])
            if not doc_ngrams:
                continue
            intersect = len(q_ngrams & doc_ngrams)
            if duan_chaxun:
                score = intersect  # 原始重叠计数(短查询宽容匹配)
            else:
                union = len(q_ngrams | doc_ngrams)
                score = round(intersect / union, 4) if union > 0 else 0
            threshold = 0.01 if duan_chaxun else 0.02
            if score > threshold:
                meta = doc.get('metadata', {})
                yuanwen = doc.get('yuanwen', '')
                dedup_key = meta.get('biaoti', yuanwen[:30])
                if dedup_key not in seen_ids:
                    seen_ids.add(dedup_key)
                    scores.append((doc_id, score, meta, yuanwen[:150]))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def chaxun(self, doc_id):
        """按ID查询单个文档"""
        self._jiazai()
        doc = self.wendang.get(doc_id)
        if doc:
            return doc.get('metadata', {}), doc.get('yuanwen', '')
        return {}, ''

    def baocun(self):
        pass


class GanZang(threading.Thread):
    """肝线程：将军之官，主谋虑，出正境之定义。记忆系统：短期·中期·长期三层存储
    V10.4：zhengjing_dingyi 零提示词——结构化数据直传LLM。
    V10.3：免疫循环集成——从经络接收诊断信号（含五行信号），调用自我修复执行六势态策略。
    """

    def __init__(self, meridian, jiyiguanli, peizhi, juese="yunxingti"):
        ziwowangluo = meridian
        llm = None
        cunchu_mulu = peizhi.XINGCHAOZDD_MULU
        self.meridian = meridian
        self.jiyiguanli = jiyiguanli
        self.peizhi = peizhi
        self.juese = juese
        self.xin = None
        self.xiufu = None
        self._yunxing = True
        super().__init__(daemon=True, name="Gan_Memory")
        self.wangluo = ziwowangluo
        self.llm = llm
        self.mulu = cunchu_mulu or Path(__file__).parent.parent / "jiyi"
        self.mulu.mkdir(exist_ok=True)

        # 三层记忆
        self.duanqi_jiyi = deque(maxlen=20)
        self.zhongqi_md = self.mulu / "zizhuan_jiyi.md"
        self.changqi_db = self.mulu / "changqi_jiyi.db"
        self.suoyin_json = self.mulu / "jiyi_suoyin.json"
        self.suoyin = self._jiazai_suoyin()
        
        self.xiangliang_suoyin = XiangliangSuoyin(self.mulu)

        self._chushihua_md()
        self._chushihua_sqlite()
        
        self.xieru_duilie = Queue(maxsize=100)
        self._xieru_suo = threading.Lock()

        self.xiufu = ZiWoXiuFu(Path(__file__).parent.parent)
        
        self.xin = None
        self.zhengjing = None
        
        self._alive = True
        self._last_heartbeat = time.time()
        self._heartbeat_interval = 5.0
        self._yunxing = True
        self._warmup_complete = False
        
        self._zuihou_mianyi = 0
        
        print(f"[肝] 就绪（V10.4 零提示词·结构化数据版）。")

    def run(self):
        self._zuozhi_zuihou_jiance = 0
        while self._yunxing:
            self._last_heartbeat = time.time()
            # 经络信号轮询: 心发信号 → 肝接收(jiyi/shadu) → 执行
            self._chuli_xinhao()
            # 佐治: 害检测——记忆写队列排空
            try:
                jilu = self.xieru_duilie.get(timeout=1)
                self._xieru_wenjian(jilu)
            except Exception: pass
            if self.wangluo and self.wangluo.check_dmn_rest() and time.time() - self._zuozhi_zuihou_jiance > 120:
                self._zuozhi_jiance()
                self._zuozhi_zuihou_jiance = time.time()
            if self.wangluo and time.time() - self._zuihou_mianyi > self.wangluo.qilv.qu_zhouqi("yixiaozhou"):
                self._mianyi_xunhuan()
                self._zuihou_mianyi = time.time()

    def _chuli_xinhao(self):
        """肝·正境: 接收心信号 → 调照妖镜(杀毒) / 存档记忆"""
        try:
            if not self.xin or not self.xin.meridian: return
            for xh in self.xin.meridian.qu_xinhao("gan"):
                if xh.get("leixing") == "shadu":
                    if self.xin.zhaoyaojing:
                        try:
                            self.xin.zhaoyaojing.sao_miao_sha_du(
                                xh.get("data", {}).get("msg", "C:\\")[:200])
                        except Exception: pass
                elif xh.get("leixing") == "jiyi":
                    try: self.jilu("jiaohu", xh.get("data", {}))
                    except Exception: pass
        except Exception: pass

    def _zuozhi_jiance(self):
        """佐治·害检测: 检查近期记忆是否有模式错配/信息遗漏, 发现害则写经络反思节点"""
        if not self.wangluo or len(self.duanqi_jiyi) < 2:
            return
        try:
            # 随机选一条近期记忆
            import random as _rnd
            recent = list(self.duanqi_jiyi)[-5:]
            sample = _rnd.choice(recent) if recent else None
            if not sample:
                return
            content = str(sample.get("neirong", str(sample)))[:200]
            # 用向量索引找相似历史记忆
            related = self.xiangliang_suoyin.jiansuo(content[:50], 2)
            if related:
                insights = []
                for doc_id, score, meta, text in related:
                    if score > 0.15:
                        insights.append(f"[{score:.2f}] {text[:80]}")
                if insights:
                    self.wangluo.jilu_fansi(
                        f"DMN静息回顾: {content[:60]} → 关联历史: {'; '.join(insights[:2])}")
        except Exception: pass

    def qidong_warmup(self):
        print("[肝] 记忆预热中...")
        try:
            if self.zhongqi_md.exists():
                neirong = self.zhongqi_md.read_text(encoding='utf-8')
                entries = re.findall(r'### (\w+) @ ([\d\-T:]+)\n(.*?)(?=\n---|\Z)', neirong, re.DOTALL)
                zuijin = entries[-20:] if len(entries) > 20 else entries
                for leibie, shijian, neirong_block in zuijin:
                    self.duanqi_jiyi.append({
                        "shijian": shijian,
                        "leibie": leibie,
                        "neirong": neirong_block[:200]
                    })
                print(f"[肝]   近期对话：{len(zuijin)} 条已加载")
        except Exception as e:
            print(f"[肝]   近期对话加载失败: {e}")
        
        # 加载对话精华记忆库
        duihua_jinghua = self.mulu / "duihua_jinghua.md"
        if duihua_jinghua.exists():
            try:
                jinghua_neirong = duihua_jinghua.read_text(encoding='utf-8')
                # 提取核心章节
                zhangjie = re.findall(r'### (.*?)\n(.*?)(?=\n### |\Z)', jinghua_neirong, re.DOTALL)
                for zhang_ming, zhang_neirong in zhangjie[:10]:
                    self.duanqi_jiyi.append({
                        "shijian": "2026-05-01T00:00:00",
                        "leibie": f"精华-{zhang_ming}",
                        "neirong": zhang_neirong[:300]
                    })
                print(f"[肝]   对话精华：{len(zhangjie)} 章节已加载")
            except Exception as e:
                print(f"[肝]   对话精华加载失败: {e}")

        buquan = self._buquan_suoyin()
        if buquan > 0:
            print(f"[肝]   索引补全：{buquan} 个缺失条目")

        zhishi_shu = 0
        try:
            with self._lianjie_db() as lianjie:
                youbiao = lianjie.cursor()
                youbiao.execute("SELECT COUNT(*) FROM zhishi_yuanli")
                zhishi_shu = youbiao.fetchone()[0]
        except Exception as e:
            print(f"[肝] 核心知识计数失败: {e}")
        print(f"[肝]   核心知识：{zhishi_shu} 条")
        print(f"[肝]   索引条目：{len(self.suoyin)} 条")
        self._warmup_complete = True
        print("[肝] 记忆基线已建立")

    def jiansuo_gengxin(self):
        try:
            self._buquan_suoyin()
            if len(self.duanqi_jiyi) > 10:
                self._baocun_suoyin()
        except Exception: pass

    def zhengjing_jiansuo(self, query: str, zuiduo: int = 8) -> str:
        jieguo = set()
        try:
            with self._lianjie_db() as lianjie:
                youbiao = lianjie.cursor()
                youbiao.execute(
                    "SELECT biaoti, hexinyuanli FROM zhishi_yuanli WHERE biaoti LIKE ? OR hexinyuanli LIKE ? LIMIT 5",
                    (f"%{query}%", f"%{query}%")
                )
                for hang in youbiao.fetchall():
                    jieguo.add(f"[核心知识]《{hang[0]}》: {hang[1][:150]}")
        except Exception as e:
            print(f"[肝] 正境检索失败: {e}")
        
        for s in self.suoyin[-20:]:
            guanjianci = " ".join(s.get("guanjianci", []))
            if any(q in guanjianci for q in query.split()):
                jieguo.add(f"[索引命中] {s.get('zhaiyao', '')[:150]}")
            if len(jieguo) >= zuiduo:
                break
        
        for j in reversed(self.duanqi_jiyi):
            if query in str(j):
                jieguo.add(f"[近期对话] {str(j.get('neirong', ''))[:120]}")
            if len(jieguo) >= zuiduo:
                break
        
        return "\n".join(list(jieguo)[:zuiduo]) if jieguo else ""

    def hejing_jiansuo(self, query: str, zuiduo: int = 8) -> str:
        jieguo = set()
        try:
            with sqlite3.connect(str(self.changqi_db)) as lianjie:
                youbiao = lianjie.cursor()
                youbiao.execute(
                    "SELECT biaoti, hexinyuanli FROM zhishi_yuanli WHERE biaoti LIKE ? OR hexinyuanli LIKE ? LIMIT 5",
                    (f"%{query}%", f"%{query}%")
                )
                for hang in youbiao.fetchall():
                    jieguo.add(f"[历史方案]《{hang[0]}》: {hang[1][:150]}")
        except Exception: pass
        
        if self.wangluo:
            try:
                ganzhi_nodes = []
                for node_id in self.wangluo.tupu.nodes():
                    shuxing = self.wangluo.tupu._nodes.get(node_id, {})
                    if shuxing.get("leixing") == "ganzhi":
                        ganzhi_nodes.append(shuxing.get("miaoshu", "")[:150])
                for gn in ganzhi_nodes[-5:]:
                    jieguo.add(f"[执行记录] {gn}")
            except Exception: pass
        
        return "\n".join(list(jieguo)[:zuiduo]) if jieguo else ""

    def zhengjing_dingyi(self, llm, msg: str):
        """
        正境·利剑：功能分析，定义问题。
        V10.4 零提示词：改为发送结构化JSON数据包，不再包含自然语言提示词。
        星巢DMN → 结构化数据 → LLM类DMN → 统计拟合 → 返回结果
        """
        task_id = None
        if self.zhengjing:
            try:
                task_id = self.zhengjing.register_task(
                    'protocols_analysis',
                    params={'method': 'zhengjing_dingyi', 'msg': msg[:80]},
                    priority=5
                )
                self.zhengjing.update_task(task_id, status='running')
            except Exception: pass

        if not llm:
            if task_id and self.zhengjing:
                try: self.zhengjing.update_task(task_id, status='failed', error='LLM不可用')
                except Exception: pass
            return None

        try:
            jiyi_ctx = self.ronghe_jiansuo(msg, zuiduo=3)

            # V11.0: 统一认知包
            from star_nest.protocols.cognition_package import RenzhiBao
            bao = RenzhiBao.from_xin(self.xin, "正境") if self.xin else RenzhiBao("正境")
            bao.shu_ju(
                yonghu_xiaoxi=msg,
                jiyi=jiyi_ctx if jiyi_ctx else "",
            )

            jieguo = llm.chat([{"role":"user","content":bao.to_json()}], wendu=0.2, zuidazifu=200)
            fenxi = {}
            for bufen in jieguo.split(','):
                if '=' in bufen:
                    jian, zhi = bufen.split('=', 1)
                    fenxi[jian.strip()] = zhi.strip()
            if fenxi:
                if task_id and self.zhengjing:
                    try: self.zhengjing.update_task(task_id, status='completed', result=fenxi)
                    except Exception: pass
                return fenxi
            else:
                if task_id and self.zhengjing:
                    try: self.zhengjing.update_task(task_id, status='failed', error='解析结果为空')
                    except Exception: pass
                return None
        except Exception as e:
            if task_id and self.zhengjing:
                try: self.zhengjing.update_task(task_id, status='failed', error=str(e)[:100])
                except Exception: pass
            return None

    def _mianyi_xunhuan(self):
        if not self.wangluo:
            return
        
        xianzai = time.time()
        zhenduan_xinxi = {"laiyuan": "gan", "leixing": "xunhuan", "yanzhongdu": "di", "xiangqing": ""}
        
        muxing_shouke = False
        muxing_shousheng = False
        
        try:
            for node_id in self.wangluo.tupu.nodes():
                shuxing = self.wangluo.tupu._nodes.get(node_id, {})
                leixing = shuxing.get("leixing", "")
                biaoqian = shuxing.get("biaoqian", "")
                
                shijian_str = shuxing.get("shijian", "")
                if shijian_str:
                    try:
                        shijian_dt = datetime.fromisoformat(shijian_str)
                        if (xianzai - shijian_dt.timestamp()) > self.wangluo.qilv.qu_zhouqi("yixiaozhou"):
                            continue
                    except Exception: pass
                
                if leixing == "wuxing_ke" and "金克木" in biaoqian:
                    muxing_shouke = True
                    zhenduan_xinxi.update({"laiyuan": "xin", "leixing": "wuxing", "yanzhongdu": "zhong", "xiangqing": "金克木·肝受克"})
                elif leixing == "wuxing_sheng" and "水生木" in biaoqian:
                    muxing_shousheng = True
                
                if leixing == "ganzhi":
                    zhenduan_xinxi["laiyuan"] = "fei"
                    zhenduan_xinxi["leixing"] = "ganzhi"
                    zhenduan_xinxi["yanzhongdu"] = shuxing.get("fengxian", "di")
                    zhenduan_xinxi["xiangqing"] = shuxing.get("miaoshu", "")
                elif leixing == "fansi":
                    zhenduan_xinxi["laiyuan"] = "pi"
                    zhenduan_xinxi["leixing"] = "fansi"
                    zhenduan_xinxi["xiangqing"] = shuxing.get("wenti", "")
                elif leixing == "jianyi":
                    zhenduan_xinxi["laiyuan"] = "shen"
                    zhenduan_xinxi["leixing"] = "jianyi"
                    zhenduan_xinxi["xiangqing"] = shuxing.get("neirong", "")
                elif leixing == "zoushe":
                    zhenduan_xinxi["laiyuan"] = shuxing.get("laiyuan", "xin")
                    zhenduan_xinxi["leixing"] = "zoushe"
                    zhenduan_xinxi["yanzhongdu"] = "gao"
                    zhenduan_xinxi["xiangqing"] = shuxing.get("xiangqing", "")
                    break
        except Exception: pass
        
        if muxing_shouke and self.xin:
            self.xin._jiansuo_yuzhi = min(0.8, self.xin._jiansuo_yuzhi + 0.05)
        elif muxing_shousheng and self.xin:
            self.xin._jiansuo_yuzhi = max(0.05, self.xin._jiansuo_yuzhi - 0.05)
        
        if not zhenduan_xinxi.get("xiangqing") and not muxing_shouke:
            return
        
        shitai = self.xiufu.panduan_shitai(zhenduan_xinxi)
        
        shangxiawen = {
            "xin": self.xin,
            "gan": self,
            "fei": self.xin.fei if self.xin else None,
            "wangluo": self.wangluo
        }
        jieguo = self.xiufu.execution_xiufu(shitai, shangxiawen)
        
        if self.xin and self.wangluo:
            try:
                self.wangluo.jilu_shijian(
                    leixing="mianyi_xiufu",
                    biaoqian=shitai,
                    xiangqing=json.dumps(jieguo, ensure_ascii=False)
                )
            except Exception: pass
        
        if not jieguo.get("success"):
            print(f"[肝] 免疫修复失败 ({shitai})：{jieguo.get('error','')[:100]}")

    @sheng_ming_hai([
        ("jiyi_kong", "记忆源全空", 0),
        ("suoyin_waixie", "索引损坏", 1),
        ("LLM_xuanyun", "LLM返回无效", 1),
    ])
    @sheng_ming_zuo({
        "jiyi_kong": True, "suoyin_waixie": True, "LLM_xuanyun": True,
    })
    def ronghe_jiansuo(self, query: str, zuiduo: int = 8) -> str:
        jieguo = set()
        for j in reversed(self.duanqi_jiyi):
            if query in str(j):
                neirong = str(j.get('neirong', ''))[:120]
                jieguo.add(f"[近期对话] {neirong}")
            if len(jieguo) >= 2: break
        
        try:
            xiangliang_jieguo = self.xiangliang_suoyin.jiansuo(query, 3)
            for doc_id, xiangsidu, meta, yuanwen in xiangliang_jieguo:
                biaoti = meta.get("biaoti", "未知")
                jieguo.add(f"[向量检索]《{biaoti}》({xiangsidu:.2f}): {yuanwen[:150]}")
        except Exception: pass
        
        if self.wangluo:
            jingque_jieguo = self.wangluo.tupu.protocols_jiansuo(query, zuiduo=zuiduo)
            for node_id in jingque_jieguo:
                if self.wangluo.tupu.has_node(node_id):
                    shuxing = self.wangluo.tupu._nodes.get(node_id, {})
                    neirong = self._tiqu_jiedian_neirong(shuxing.get('leixing', ''), shuxing)
                    if neirong and len(neirong) > 5:
                        jieguo.add(f"[深度记忆] {neirong[:150]}")
                if len(jieguo) >= zuiduo: break
        if len(jieguo) < zuiduo:
            try:
                with self._lianjie_db() as lianjie:
                    youbiao = lianjie.cursor()
                    youbiao.execute("SELECT biaoti, hexinyuanli FROM zhishi_yuanli WHERE biaoti LIKE ? OR hexinyuanli LIKE ? LIMIT 3",
                                    (f"%{query}%", f"%{query}%"))
                    for hang in youbiao.fetchall(): jieguo.add(f"[核心知识]《{hang[0]}》: {hang[1][:150]}")
            except Exception as e:
                print(f"[肝] 融合检索DB回退失败: {e}")
        if len(jieguo) < 3 and self.wangluo:
            baji_jieguo = self.wangluo.tupu.baji_jiansuo(
                {"yang":0.5,"yin":0.5,"biao":0.7,"li":0.5,"han":0.3,"re":0.5,"xu":0.5,"shi":0.5}, zuiduo=3)
            for node_id, _, shuxing in baji_jieguo:
                if node_id not in jieguo:
                    neirong = self._tiqu_jiedian_neirong(shuxing.get('leixing', ''), shuxing)
                    if neirong and len(neirong) > 5: jieguo.add(f"[关联扩散] {neirong[:150]}")
        jieguo_str = "\n".join(list(jieguo)[:zuiduo]) if jieguo else ""
        
        if (not jieguo_str or len(jieguo_str) < 10) and self.wangluo:
            try:
                self.wangluo.jilu_fansi(wenti=f"检索内容稀少[{query[:30]}]", laiyuan_jiedian="xin")
            except Exception: pass
        
        return jieguo_str

    def _tiqu_jiedian_neirong(self, leixing, shuxing):
        if leixing == 'fansi': return f"反思：{shuxing.get('wenti','')}"
        elif leixing == 'ganzhi': return f"感知：{shuxing.get('miaoshu','')}"
        elif leixing == 'jianyi': return f"提案：{shuxing.get('neirong','')}"
        elif leixing == 'shen': return f"身份：{shuxing.get('zhuangtai','')}"
        else: return str(shuxing.get('xiangqing', shuxing.get('biaoqian', str(shuxing)[:100])))

    def jilu(self, leibie, neirong):
        shijian = datetime.now().isoformat()
        jilu = {"shijian": shijian, "leibie": leibie, "neirong": str(neirong)[:200]}
        self.duanqi_jiyi.append(jilu)
        self.wangluo.jilu_shijian(leibie, leibie, str(neirong)[:200])
        try: self.xieru_duilie.put_nowait({"shijian": shijian, "leibie": leibie, "neirong": neirong})
        except Exception:
            try:
                self.xieru_duilie.get_nowait()
                self.xieru_duilie.put_nowait({"shijian": shijian, "leibie": leibie, "neirong": neirong})
            except Exception: pass

    def _xieru_wenjian(self, jilu: dict):
        with self._xieru_suo:
            try:
                shijian = jilu.get("shijian", datetime.now().isoformat())
                leibie = jilu.get("leibie", "通用")
                neirong = jilu.get("neirong", {})
                if not str(neirong).strip(): return
                with open(self.zhongqi_md, 'a', encoding='utf-8') as f:
                    f.write(f"\n---\n### {leibie} @ {shijian[:19]}\n")
                    for k, v in neirong.items(): f.write(f"- **{k}**: {v}\n")
                guanjianci = self._chouqu_guanjianci(str(neirong))
                self.suoyin.append({"shijian": shijian, "leibie": leibie, "guanjianci": guanjianci, "zhaiyao": str(neirong)[:200]})
                if len(self.suoyin) > 500: self.suoyin = self.suoyin[-400:]
                self._baocun_suoyin()
            except Exception as e: print(f"[肝] 写入失败: {e}")

    def cunru_zhishi(self, biaoti, hexin, cengji="zheng", laiyuan=""):
        try:
            with self._lianjie_db() as lianjie:
                lianjie.execute("INSERT INTO zhishi_yuanli (biaoti, hexinyuanli, renzhicengji, laiyuan, ninglian_time) VALUES (?,?,?,?,?)",
                                (biaoti, hexin, cengji, laiyuan, datetime.now().isoformat()))
                lianjie.commit()
        except Exception as e:
            print(f"[肝] 知识写入失败: {e}")

    def _chouqu_guanjianci(self, wenben):
        ci = re.findall(r'[\u4e00-\u9fa5]{2,}|\w{3,}', str(wenben).lower())
        return list(set([c for c in ci if not c.isdigit()]))

    def _jiazai_suoyin(self):
        if self.suoyin_json.exists():
            try: return json.loads(self.suoyin_json.read_text(encoding='utf-8'))
            except Exception: pass
        return []

    def _baocun_suoyin(self):
        try: self.suoyin_json.write_text(json.dumps(self.suoyin, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception: pass

    def _buquan_suoyin(self) -> int:
        count = 0
        try:
            if self.zhongqi_md.exists():
                neirong = self.zhongqi_md.read_text(encoding='utf-8')
                for match in re.finditer(r'### (\w+) @ ([\d\-T:]+)\n(.*?)(?=\n---|\Z)', neirong, re.DOTALL):
                    leibie = match.group(1)
                    neirong_block = match.group(3)
                    guanjianci = self._chouqu_guanjianci(neirong_block)
                    exists = any(s.get('leibie') == leibie for s in self.suoyin[-10:])
                    if not exists:
                        self.suoyin.append({"shijian": match.group(2), "leibie": leibie, "guanjianci": guanjianci, "zhaiyao": neirong_block[:200]})
                        count += 1
        except Exception: pass
        return count

    def _chushihua_md(self):
        if not self.zhongqi_md.exists():
            self.zhongqi_md.write_text("# 五境认知引擎·自传记忆\n\n", encoding='utf-8')

    def _lianjie_db(self):
        lianjie = sqlite3.connect(str(self.changqi_db))
        lianjie.execute("PRAGMA encoding='UTF-8'")
        lianjie.execute("PRAGMA journal_mode=WAL")
        lianjie.text_factory = str
        return lianjie

    def _chushihua_sqlite(self):
        with self._lianjie_db() as lianjie:
            lianjie.execute("""CREATE TABLE IF NOT EXISTS zhishi_yuanli (id INTEGER PRIMARY KEY, biaoti TEXT, hexinyuanli TEXT, guanjianci TEXT, renzhicengji TEXT, guanlian_zhishi TEXT, laiyuan TEXT, ninglian_time TEXT)""")
            lianjie.execute("""CREATE TABLE IF NOT EXISTS chengzhang_rizhi (id INTEGER PRIMARY KEY, shijian TEXT, leixing TEXT, miaoshu TEXT)""")
            lianjie.commit()

    def tongji(self):
        return {"suoyin_shu": len(self.suoyin), "duanqi_shu": len(self.duanqi_jiyi),
                "zhongqi_cunzai": self.zhongqi_md.exists(), "changqi_cunzai": self.changqi_db.exists()}

    def qu_protocols_lishi(self, query: str, zuiduo: int = 3) -> str:
        """检索历史五境分析记录, 语义相似度优先(向量索引) + 关键词回退"""
        jieguo = []
        # 层1: 向量索引语义检索
        try:
            gr = self.xiangliang_suoyin.jiansuo(query, zuiduo * 2)
            for doc_id, xiangsidu, meta, yuanwen in gr:
                if xiangsidu > 0.15:
                    biaoti = meta.get("biaoti", "历史分析")
                    jieguo.append(f"[语义匹配 {xiangsidu:.2f}] {yuanwen[:200] or biaoti}")
        except Exception: pass
        # 层2: SQLite关键词回退
        if len(jieguo) < zuiduo:
            try:
                conn = self._changqi_lianjie()
                cur = conn.execute(
                    "SELECT shijian, miaoshu FROM chengzhang_rizhi WHERE miaoshu LIKE ? OR miaoshu LIKE ? ORDER BY id DESC LIMIT ?",
                    (f"%{query[:10]}%", f"%五境%", zuiduo * 2))
                for row in cur.fetchall():
                    sj, ms = row[0], row[1] if len(row) > 1 else ""
                    jieguo.append(f"[关键词匹配 {sj[:10]}] {ms[:200]}")
                conn.close()
            except Exception: pass
        # 层3: 短期记忆关键词回退
        if len(jieguo) < zuiduo:
            for j in reversed(self.duanqi_jiyi):
                jy = j.get("jiyi", {})
                if jy.get("leixing") == "五境分析":
                    nr = str(j.get("neirong", ""))[:200]
                    if nr:
                        jieguo.append(f"[短期五境] {nr}")
                        if len(jieguo) >= zuiduo: break
        return "\n".join(jieguo[:zuiduo]) if jieguo else ""

    def qu_zouzhai(self):
        """取走债: 返回肝(记忆)相关的未解决问题"""
        zhai = []
        try:
            if self.wangluo:
                for tid in ["bianchengti","yunxingti"]:
                    for w in self.wangluo.qu_wenti_liebiao(tid):
                        ms = str(w.get("miaoshu",""))[:100]
                        if any(kw in ms for kw in ["记忆","检索","jiyi","索引","suoyin","编码"]):
                            zhai.append(f"[肝-记忆债|{tid}] {ms}")
                if len(zhai) == 0 and len(self.duanqi_jiyi) < 3:
                    zhai.append("[肝-记忆债] 短期记忆不足3条, 建议增加交互")
        except Exception: pass
        return zhai

    def tingzhi(self):
        self._yunxing = False
        try:
            if hasattr(self, 'xiangliang_suoyin') and self.xiangliang_suoyin:
                self.xiangliang_suoyin.baocun()
        except Exception: pass