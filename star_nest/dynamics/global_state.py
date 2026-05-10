"""
全局状态向量 GlobalState V1.0 [星巢·2cos(π/5)=φ 的工程实现]

整体有序锚点: 所有四脏共享此状态，各自读取、各自更新。
π(LLM无序)·φ(用户无序) -> S迭代 -> 六势态有限吸引子 -> 确定行为

字段:
  肾·八极: baji{阳,阴,表,里,寒,热,虚,实}
  肺·安全: shizhi, anquan_du, weixian_xinhao
  脾·工具: tool_ready, gongju_count
  肝·记忆: memory_hit, jiyi_count
  心·认知: zhishi_midu, execution_yitu, chunk_count
  π-φ:     pi_neng, phi_neng, jielv
  管道:    active, doc_title, processing
"""
import time, json, threading
from pathlib import Path


class GlobalState:
    """
    星巢全局状态向量
    
    使用:
      S = get_global_state(xin)
      S.baji["阳"] = 0.6
      S.shizhi = "阳明"
      S.save()

    铁律: 所有四脏判断前读S, 判断后更新S。
          S是2cos(π/5)=φ中的"cos"——将无序映射到有限区间。
    """

    def __init__(self, xin=None):
        self.xin = xin
        self._lock = threading.Lock()

        # 肾·八极向量
        self.baji = {"阳": 0.5, "阴": 0.5, "表": 0.5, "里": 0.5,
                     "寒": 0.5, "热": 0.5, "虚": 0.5, "实": 0.5}

        # 肺·安全态势
        self.shizhi = "少阳"
        self.anquan_du = 0.5
        self.weixian_xinhao = 0

        # 脾·工具就绪
        self.tool_ready = 0.5
        self.gongju_count = 0

        # 肝·记忆状态
        self.memory_hit = 0.3
        self.jiyi_count = 0

        # 心·认知动态
        self.zhishi_midu = 0.0
        self.execution_yitu = 0.0
        self.chunk_count = 0

        # π-φ 动力
        self.pi_neng = 0.5
        self.phi_neng = 0.5
        self.jielv = "yiweizhou"

        # 管道状态
        self.active = False
        self.doc_title = ""
        self.processing = False

        # 持久化路径
        self._state_file = Path(__file__).parent.parent / "huanjing" / "quanjuzhuangtai.json"
        self._state_file.parent.mkdir(parents=True, exist_ok=True)

    # ==================== 原子读写 ====================

    def save(self):
        """持久化(跨进程)"""
        try:
            data = {
                "baji": self.baji, "shizhi": self.shizhi,
                "anquan_du": self.anquan_du, "weixian_xinhao": self.weixian_xinhao,
                "tool_ready": self.tool_ready, "gongju_count": self.gongju_count,
                "memory_hit": self.memory_hit, "jiyi_count": self.jiyi_count,
                "zhishi_midu": self.zhishi_midu, "execution_yitu": self.execution_yitu,
                "chunk_count": self.chunk_count,
                "pi_neng": self.pi_neng, "phi_neng": self.phi_neng, "jielv": self.jielv,
                "active": self.active, "doc_title": self.doc_title,
                "processing": self.processing,
                "saved_at": time.time()
            }
            self._state_file.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        except Exception:
            pass

    def load(self) -> bool:
        """加载跨进程状态(300s超时)"""
        try:
            if not self._state_file.exists():
                return False
            data = json.loads(self._state_file.read_text(encoding='utf-8'))
            if time.time() - data.get("saved_at", 0) > 300:
                self._state_file.unlink(missing_ok=True)
                return False
            for k in ["baji","shizhi","anquan_du","weixian_xinhao",
                      "tool_ready","gongju_count","memory_hit","jiyi_count",
                      "zhishi_midu","execution_yitu","chunk_count",
                      "pi_neng","phi_neng","jielv",
                      "active","doc_title","processing"]:
                if k in data:
                    setattr(self, k, data[k])
            return True
        except Exception:
            return False

    def reset(self):
        """重置为初始状态"""
        self.baji = {k: 0.5 for k in ["阳","阴","表","里","寒","热","虚","实"]}
        self.shizhi = "少阳"; self.anquan_du = 0.5; self.weixian_xinhao = 0
        self.tool_ready = 0.5; self.zhishi_midu = 0.0; self.execution_yitu = 0.0
        self.chunk_count = 0; self.memory_hit = 0.3
        self.pi_neng = 0.5; self.phi_neng = 0.5
        self.active = False; self.doc_title = ""; self.processing = False
        try:
            self._state_file.unlink(missing_ok=True)
        except Exception:
            pass

    # ==================== 快照 ====================

    def snapshot(self) -> dict:
        """只读快照"""
        return {
            "baji": dict(self.baji), "shizhi": self.shizhi,
            "anquan_du": self.anquan_du, "weixian_xinhao": self.weixian_xinhao,
            "tool_ready": self.tool_ready, "memory_hit": self.memory_hit,
            "pi_neng": self.pi_neng, "phi_neng": self.phi_neng,
            "zhishi_midu": self.zhishi_midu, "execution_yitu": self.execution_yitu,
            "active": self.active, "doc_title": self.doc_title
        }

    def update_from_organs(self, baji=None, shizhi=None, tool_ready=None, memory_hit=None):
        """批量更新(从四脏)"""
        if baji: self.baji = baji
        if shizhi: self.shizhi = shizhi
        if tool_ready is not None: self.tool_ready = tool_ready
        if memory_hit is not None: self.memory_hit = memory_hit


# 单例
_global_state = None


def get_global_state(xin=None):
    global _global_state
    if _global_state is None:
        _global_state = GlobalState(xin)
    return _global_state
