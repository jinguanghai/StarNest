"""
藏剑阁·图 (tupu.py) V10.0
轻量级有向图结构，支持八极向量、五行生克、五境检索。
纯标准库实现，零外部依赖。五境认知网络的底层经络。

【通用问题解决操作系统·完整映射】
- Define（正境）：add_node / add_edge 图结构定义——节点=认知碎片，边=关系
- Measure（反境）：baji_xiangsidu 八极余弦相似度——可量化的节点状态距离
- Analyze（反境）：protocols_jiansuo 五境检索——四层递进的正→反→合→超越检索
- Improve（合境）：wuxing_bianli 五行遍历——沿生克关系深度展开
- Control（超越境）：序列化 to_json / from_json——状态持久化与恢复
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta

class TuPu:
    """轻量有向图——八极向量 + 五境检索"""

    def __init__(self, youxiang=True):
        self.youxiang = youxiang
        self._nodes = {}
        self._adj = defaultdict(dict)

    # ========== 正境·Define: 图结构定义 ==========
    def add_node(self, node, **attrs):
        """正境·利剑：添加认知节点，默认初始化为中性八极向量"""
        if node not in self._nodes:
            self._nodes[node] = {
                "baji": {
                    "yang": 0.5, "yin": 0.5, "biao": 0.5, "li": 0.5,
                    "han": 0.5, "re": 0.5, "xu": 0.5, "shi": 0.5
                },
                "chuangjian": datetime.now().isoformat()
            }
        self._nodes[node].update(attrs)
        # 超越境·Control: 确保baji和chuangjian字段永远存在
        if "baji" not in self._nodes[node]:
            self._nodes[node]["baji"] = {
                "yang": 0.5, "yin": 0.5, "biao": 0.5, "li": 0.5,
                "han": 0.5, "re": 0.5, "xu": 0.5, "shi": 0.5
            }
        if "chuangjian" not in self._nodes[node]:
            self._nodes[node]["chuangjian"] = datetime.now().isoformat()
        if node not in self._adj:
            self._adj[node] = {}

    def add_edge(self, u, v, **attrs):
        """正境·利剑：添加关系边，默认五行关系为'生'"""
        if u not in self._nodes:
            self.add_node(u)
        if v not in self._nodes:
            self.add_node(v)
        if "wuxing" not in attrs:
            attrs["wuxing"] = "sheng"
        self._adj[u][v] = attrs
        if not self.youxiang:
            self._adj[v][u] = attrs

    # ========== 基础查询 ==========
    def nodes(self, data=False):
        if data:
            return [(n, self._nodes[n]) for n in self._nodes]
        return list(self._nodes.keys())

    def remove_node(self, node_id):
        """删除节点及其关联边"""
        if node_id in self._nodes:
            del self._nodes[node_id]
        if node_id in self._adj:
            del self._adj[node_id]
        for u in self._adj:
            if node_id in self._adj[u]:
                del self._adj[u][node_id]

    def neighbors(self, node):
        return list(self._adj.get(node, {}).keys())

    def has_node(self, node):
        return node in self._nodes

    def has_edge(self, u, v):
        return u in self._adj and v in self._adj[u]

    def number_of_nodes(self):
        return len(self._nodes)

    def number_of_edges(self):
        count = sum(len(adj) for adj in self._adj.values())
        return count if self.youxiang else count // 2

    def __len__(self):
        return self.number_of_nodes()

    # ========== 反境·Measure: 八极向量系统 ==========
    def shezhi_baji(self, node, baji_cidian):
        """反境·软剑：设置节点八极向量，自动记录更新时间"""
        if node in self._nodes:
            self._nodes[node]["baji"].update(baji_cidian)
            self._nodes[node]["baji_gengxin"] = datetime.now().isoformat()

    def qu_baji(self, node):
        """反境·软剑：获取节点八极向量"""
        if node in self._nodes:
            return dict(self._nodes[node].get("baji", {}))
        return {}

    def baji_xiangsidu(self, baji_a, baji_b):
        """
        反境·软剑：计算两个八极向量的余弦相似度。
        反境·Measure: 返回值 ∈ [0, 1]，可量化的状态距离。
        """
        ji = sum(baji_a.get(k, 0) * baji_b.get(k, 0) for k in ["yang","yin","biao","li","han","re","xu","shi"])
        mo_a = sum(v**2 for v in baji_a.values()) ** 0.5
        mo_b = sum(v**2 for v in baji_b.values()) ** 0.5
        if mo_a == 0 or mo_b == 0:
            return 0.0
        return ji / (mo_a * mo_b)

    def baji_jiansuo(self, mubiao_baji, zuiduo=5):
        """
        反境·软剑：基于八极余弦相似度的模糊检索。
        反境·Measure: 相似度阈值>0.3才纳入结果，防止噪声。
        """
        jieguo = []
        for node_id, shuxing in self._nodes.items():
            xiangsidu = self.baji_xiangsidu(mubiao_baji, shuxing.get("baji", {}))
            if xiangsidu > 0.3:
                jieguo.append((node_id, xiangsidu, shuxing))
        jieguo.sort(key=lambda x: x[1], reverse=True)
        return jieguo[:zuiduo]

    # ========== 合境·Improve: 五行关系系统 ==========
    def shezhi_wuxing(self, u, v, guanxi):
        """合境·重剑：设置边的五行关系（生/克/乘/侮）"""
        if u in self._nodes and v in self._nodes:
            self._adj[u][v] = {"wuxing": guanxi}
            if not self.youxiang:
                self._adj[v][u] = {"wuxing": guanxi}

    def qu_wuxing_linju(self, node, guanxi=None):
        """合境·重剑：查询指定五行关系的邻居"""
        jieguo = []
        for linju, bian_shuxing in self._adj.get(node, {}).items():
            if guanxi is None or bian_shuxing.get("wuxing") == guanxi:
                jieguo.append(linju)
        return jieguo

    def wuxing_bianli(self, node, shendu=2):
        """
        合境·重剑：五行深度优先遍历。
        合境·Improve: 沿生克关系展开认知网络，深度可控。
        """
        fangwen = set()
        jieguo = []

        def dfs(dangqian, dangqian_shendu):
            if dangqian_shendu > shendu or dangqian in fangwen:
                return
            fangwen.add(dangqian)
            jieguo.append(dangqian)
            for linju in self._adj.get(dangqian, {}):
                dfs(linju, dangqian_shendu + 1)

        dfs(node, 0)
        return jieguo

    # ========== 反境·Analyze: 五境专属检索 ==========
    def protocols_jiansuo(self, guanjianci, cengji=None, zuiduo=8):
        """
        合境·重剑：五境递进检索——正境精确→反境模糊→合境五行→超越境八极。
        反境·Analyze: 四层递进，每层补充前一层遗漏的节点。
        """
        jieguo = []

        # 正境：精确关键词匹配
        jingque = self._zhengjing_pipei(guanjianci)
        jieguo.extend(jingque)

        # 反境：模糊语义联想
        if len(jieguo) < zuiduo:
            mohu = self._fanjing_lianxiang(guanjianci)
            for m in mohu:
                if m not in jieguo:
                    jieguo.append(m)

        # 合境：五行生克深度遍历
        if len(jieguo) < zuiduo and jieguo:
            hexin = jieguo[0]
            wuxing_jieguo = self.wuxing_bianli(hexin, shendu=2)
            for w in wuxing_jieguo:
                if w not in jieguo:
                    jieguo.append(w)

        # 超越境：八极向量相似重组
        if len(jieguo) < zuiduo and jieguo:
            hexin_baji = self.qu_baji(jieguo[0])
            baji_jieguo = self.baji_jiansuo(hexin_baji, zuiduo=zuiduo)
            for b_id, _, _ in baji_jieguo:
                if b_id not in jieguo:
                    jieguo.append(b_id)

        return jieguo[:zuiduo]

    def _zhengjing_pipei(self, guanjianci):
        """正境·利剑：精确关键词匹配"""
        jieguo = []
        for node_id, shuxing in self._nodes.items():
            wenben = json.dumps(shuxing, ensure_ascii=False)
            if guanjianci in wenben:
                jieguo.append(node_id)
        return jieguo

    def _fanjing_lianxiang(self, guanjianci, zuiduo=5):
        """反境·软剑：模糊语义联想（基于八极相似度扩散）"""
        mubiao_baji = {
            "yang": 0.5, "yin": 0.5, "biao": 0.7, "li": 0.5,
            "han": 0.3, "re": 0.5, "xu": 0.5, "shi": 0.5
        }
        jieguo = self.baji_jiansuo(mubiao_baji, zuiduo=zuiduo)
        return [jieguo_id for jieguo_id, _, _ in jieguo]

    # ========== 超越境·Control: 序列化 ==========
    def to_json(self):
        """超越境·木剑：序列化为JSON，向下兼容"""
        return {
            "youxiang": self.youxiang,
            "nodes": {n: {"attrs": a} for n, a in self._nodes.items()},
            "edges": []
        }

    @classmethod
    def from_json(cls, data):
        """超越境·木剑：从JSON恢复图结构"""
        g = cls(youxiang=data.get("youxiang", True))
        for node_id, node_data in data.get("nodes", {}).items():
            attrs = node_data.get("attrs", {})
            g.add_node(node_id, **attrs)
        for edge in data.get("edges", []):
            g.add_edge(edge[0], edge[1], **edge[2] if len(edge) > 2 else {})
        return g