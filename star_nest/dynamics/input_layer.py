"""
输入层 ShuRuCeng V2.1 [星巢·纯文本消化管道]
四层递进认知消化 + 代码检测

分类/路由/投喂模式迁移至渐进认知引擎(jianjinrenzhi).
ShuRuCeng 只保留: 代码检测 / 分块 / 中文本消化 / 四层消化.
"""
import re, time, json
from pathlib import Path
from datetime import datetime


class ShuRuCeng:
    """认知输入层: 文本分块→消化→锚定记忆"""

    def __init__(self, xin):
        self.xin = xin
        self._zuihou_xiaohua = 0
        self._shen_du_moshi = True

    # ==================== 入口 ====================

    def chuli(self, msg: str, mode: str = None) -> str:
        """文本处理: 代码检测→消化管道"""
        if not msg or not msg.strip():
            return None
        if mode == 'fast':
            self._shen_du_moshi = False
        elif mode == 'deep':
            self._shen_du_moshi = True
        if self._shifou_daima(msg):
            return None
        length = len(msg)
        if length <= 500:
            return None
        if length <= 3000:
            return self._xiaohua_zhongwen(msg)
        return self._xiaohua_shenceng(msg)

    # ==================== 四层递进消化 ====================

    def _xiaohua_shenceng(self, msg: str) -> str:
        """
        长文本四层递进消化:
          L1 正境粗读 → L2 反境精读 → L3 合境贯通 → L4 超越本源
        
        无LLM时降级为原单层模式
        """
        if not self._shen_du_moshi or not self.xin.llm or not self.xin.llm.api_key:
            return self._xiaohua_changwen_old(msg)

        llm = self.xin.llm
        doc_title = msg.strip()[:60].replace('\n', ' ')
        kuai_list = self._fenkuai(msg, 800)
        if len(kuai_list) <= 1:
            return self._xiaohua_changwen_old(msg)

        start_time = time.time()
        print(f"[输入层·四层消化] 开始: {doc_title}... ({len(kuai_list)}块, {len(msg)}字)")

        # ── Layer 1: 正境粗读 ──
        print(f"[L1·正境] 逐块粗读 {len(kuai_list)} 块...")
        l1_notes = self._layer1_zhengjing(llm, kuai_list, doc_title)
        self._cun_l1_notes(l1_notes, doc_title)
        print(f"[L1·正境] 完成, {len(l1_notes)}条笔记")
        if len(kuai_list) > 4:
            time.sleep(1)

        # ── Layer 2: 反境精读 ──
        print(f"[L2·反境] 跨块聚类分析...")
        l2_notes = self._layer2_fanjing(llm, l1_notes, doc_title)
        self._cun_l2_notes(l2_notes, doc_title)
        print(f"[L2·反境] 完成, {len(l2_notes)}条深层笔记")
        time.sleep(1)

        # ── Layer 3: 合境贯通 ──
        print(f"[L3·合境] 构建统一框架...")
        l3_framework = self._layer3_hejing(llm, l1_notes, l2_notes, doc_title)
        self._cun_l3_framework(l3_framework, doc_title)
        print(f"[L3·合境] 完成, 核心模型={l3_framework.get('hexin_moxing','?')[:60]}")
        time.sleep(1)

        # ── Layer 4: 超越→本源 ──
        print(f"[L4·超越] 意图判断 + 价值内化...")
        l4_intent = self._layer4_chaoyue(llm, l3_framework, doc_title)
        self._cun_l4_intent(l4_intent, doc_title)
        print(f"[L4·超越] 完成, 意图={l4_intent.get('zuozhe_yitu','?')[:60]}")

        haoshi = round(time.time() - start_time, 1)
        summary = self._build_summary(l1_notes, l2_notes, l3_framework, l4_intent, haoshi)
        print(f"[输入层·四层消化] 完成, 耗时{haoshi}s")
        return summary

    def _xiaohua_changwen_old(self, msg: str) -> str:
        """原单层消化(兜底)"""
        kuai_list = self._fenkuai(msg, 1200)
        results = []
        digested_count = 0
        for i, kuai in enumerate(kuai_list):
            if not kuai.strip(): continue
            digested_count += 1
            try:
                if self.xin.gan and hasattr(self.xin.gan, 'zhengjing_dingyi') and self.xin.llm:
                    dingyi = self.xin.gan.zhengjing_dingyi(
                        self.xin.llm, f"[文档消化 {i+1}/{len(kuai_list)}] {kuai[:600]}")
                    zhaiyao = dingyi.get('zuoyong', kuai[:100]) if dingyi else kuai[:100]
                else:
                    zhaiyao = kuai[:100]
            except Exception:
                zhaiyao = kuai[:100]
            results.append(f"§{i+1}: {zhaiyao}")
            self._maoding(kuai, i, len(kuai_list))
            if i > 0 and i % 5 == 0: time.sleep(2)
        summary = f"[输入层·单层消化] {len(kuai_list)}段→{digested_count}段: " + "; ".join(results[:10])
        return f"{summary}\n\n以上内容已分段消化并存入记忆。你可以直接提问。"


    # ==================== 代码检测 ====================

    def _shifou_daima(self, msg: str) -> bool:
        """检测输入是否为代码/代码指令"""
        text = msg.strip()
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if not lines:
            return False
        first = lines[0]

        # Python 代码标记
        py_markers = ['def ', 'class ', 'import ', 'from ', 'if __name__', '@',
                      'print(', 'return ', 'with ', 'for ', 'while ', 'try:',
                      'except ', 'elif ', 'else:', '#!']
        if any(first.startswith(m) for m in py_markers):
            return True

        # 其他代码标记
        if any(first.startswith(m) for m in ['#!/', '#include', '<html', '<!DOCTYPE',
                'SELECT ', 'INSERT ', 'package ', 'const ', 'let ', 'var ',
                'function ', 'async ', 'export ', 'require(']):
            return True

        # 代码块标记
        if text.startswith('```'):
            return True

        # 特征统计: 含代码特有符号密度高
        code_chars = '{}()[]=;:.'
        code_density = sum(text.count(c) for c in code_chars)
        total = max(len(text), 1)
        # 中文为主→不判代码
        cn_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        if cn_count > total * 0.3:
            return False
        if code_density / total > 0.08:
            return True

        # shell 命令
        shell_cmds = ['ls ', 'cd ', 'mkdir ', 'rm ', 'cp ', 'mv ', 'chmod ', 'grep ',
                      'pip ', 'npm ', 'git ', 'docker ', 'python ', 'echo ',
                      'cat ', 'find ', 'wget ', 'curl ', 'ps ']
        if any(text.lower().startswith(c) for c in shell_cmds):
            return True

        return False

    # ==================== 分块 ====================

    def _fenkuai(self, msg: str, max_chars: int = 800) -> list:
        """语义分块: 优先按空行→段落→句号切分"""
        # 层1: 空行分隔
        if '\n\n' in msg:
            kuai_list = [k.strip() for k in msg.split('\n\n') if k.strip()]
            # 合并过短的块
            merged = []
            buf = ""
            for k in kuai_list:
                if len(buf) + len(k) < max_chars:
                    buf = (buf + '\n\n' + k).strip()
                else:
                    if buf: merged.append(buf)
                    buf = k
            if buf: merged.append(buf)
            return merged

        # 层2: 段落分隔
        if '\n' in msg:
            kuai_list = [k.strip() for k in msg.split('\n') if k.strip()]
            merged = []
            buf = ""
            for k in kuai_list:
                if len(buf) + len(k) < max_chars:
                    buf = (buf + '\n' + k).strip()
                else:
                    if buf: merged.append(buf)
                    buf = k
            if buf: merged.append(buf)
            return merged if len(merged) > 1 else [msg[:max_chars]]

        # 层3: 强行按长度切分
        return [msg[i:i+max_chars] for i in range(0, len(msg), max_chars)]

    # ==================== 消化管道 ====================

    def _xiaohua_zhongwen(self, msg: str) -> str:
        """中文本(500-3000字): 分块→每块走五境正境分析→合并摘要"""
        kuai_list = self._fenkuai(msg, 800)
        if len(kuai_list) == 1:
            # 只有一个块, 走正常管道
            return None

        results = []
        for i, kuai in enumerate(kuai_list):
            if not kuai.strip():
                continue
            # 每块走正境定义: 提取主体/客体/作用
            try:
                if self.xin.gan and hasattr(self.xin.gan, 'zhengjing_dingyi') and self.xin.llm:
                    dingyi = self.xin.gan.zhengjing_dingyi(
                        self.xin.llm,
                        f"[文本块{i+1}/{len(kuai_list)}] {kuai[:500]}"
                    )
                    if dingyi:
                        results.append(f"块{i+1}: {dingyi.get('zuoyong', kuai[:80])}")
                    else:
                        results.append(f"块{i+1}: {kuai[:100]}")
                else:
                    results.append(f"块{i+1}: {kuai[:100]}")
            except Exception:
                results.append(f"块{i+1}: {kuai[:100]}")

            # 锚定记忆
            self._maoding(kuai, i, len(kuai_list))

        # 返回合并摘要
        summary = "\n".join(results)
        if self.xin.gan and hasattr(self.xin.gan, 'jilu'):
            try:
                self.xin.gan.jilu("文档消化", {
                    "leixing": "zhongwen_xiaohua",
                    "kuai_shu": len(kuai_list),
                    "zhaiyao": summary[:300],
                    "neirong": msg[:2000]
                })
            except Exception: pass
        return f"[输入层·中文本消化] {len(kuai_list)}块:\n{summary}"

    # ==================== 记忆锚定 ====================

    def _maoding(self, kuai, index, total):
        """将消化块的摘要锚定到记忆中(可检索)"""
        try:
            if self.xin.gan and hasattr(self.xin.gan, 'jilu'):
                self.xin.gan.jilu("文档块", {
                    "kuai_index": f"{index+1}/{total}",
                    "neirong": kuai[:500],
                })
            # 写入经络反思: 文档块消化记录
            if self.xin.meridian and hasattr(self.xin.meridian, 'jilu_fansi'):
                self.xin.meridian.jilu_fansi(
                    f"doc_chunk:{index+1}/{total}:{kuai[:80]}"
                )
        except Exception: pass
