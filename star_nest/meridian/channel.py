"""
经络网络 V2.0 [星巢本体移植版]
三体共享状态图·基于 tupu.py 图引擎·心跳·问题·修复·JSON持久化
纯标准库·零外部依赖
"""
import threading, time, json
from pathlib import Path
from datetime import datetime
from star_nest.meridian.topology import TuPu
from star_nest.meridian.seven_laws import QiLv

class JingLuo:
    def __init__(self, cunchu_lujing):
        self.suo = threading.Lock()
        self.tupu = TuPu(youxiang=True)
        self.qilv = QiLv()
        self.cunchu_lujing = Path(cunchu_lujing)
        self.cunchu_wenjian = self.cunchu_lujing / "meridian_zhuangtai.json"
        self.wenti_liebiao = {"yunxingti": [], "bianchengti": [], "fuzhiti": []}
        self.xiufu_lishi = {"yunxingti": [], "bianchengti": [], "fuzhiti": []}
        self.wenti_tongzhi = None  # 问题通知回调: fn(tid, wenti)
        self.jiyi = None  # 经络记忆注入点
        self.qixue = None  # 气血循环泵注入点
        self.rizhi = None  # 运行日志注入点
        for tid, mc, js in [
            ("yunxingti", "运行体", "execution"),
            ("bianchengti", "编程体", "xiufu"),
            ("fuzhiti", "复制体", "yanzheng"),
        ]:
            self.tupu.add_node(tid, mingcheng=mc, juese=js,
                               chuangjian=datetime.now().isoformat(),
                               zuihou_xintiao=str(time.time()),
                               zhuangtai="jihuo")
        self.tupu.add_edge("bianchengti", "yunxingti", wuxing="sheng", miaoshu="编程体生运行体")
        self.tupu.add_edge("bianchengti", "fuzhiti", wuxing="sheng", miaoshu="编程体生复制体")
        self.tupu.add_edge("fuzhiti", "bianchengti", wuxing="ke", miaoshu="复制体克编程体")
        self.tupu.add_edge("yunxingti", "bianchengti", wuxing="ke", miaoshu="运行体克编程体")

    def jilu_xintiao(self, tid):
        if self.tupu.has_node(tid):
            self.tupu._nodes[tid]["zuihou_xintiao"] = str(time.time())

    def jilu_wenti(self, tid, wenti):
        wenti["shijian"] = datetime.now().isoformat()
        with self.suo:
            self.wenti_liebiao.setdefault(tid, []).append(wenti)
            if len(self.wenti_liebiao[tid]) > 100:
                self.wenti_liebiao[tid] = self.wenti_liebiao[tid][-100:]
            ws = len(self.wenti_liebiao[tid])
        self.tupu.shezhi_baji(tid, {"yang": min(0.8, ws/30), "xu": min(0.9, ws/20)})
        if self.wenti_tongzhi and tid == "yunxingti":
            try: self.wenti_tongzhi(tid, wenti)
            except: pass
        if self.jiyi:
            try: self.jiyi.jilu_wenti(tid, wenti)
            except: pass

    def jilu_xiufu(self, tid, xiufu):
        xiufu["shijian"] = datetime.now().isoformat()
        with self.suo:
            self.xiufu_lishi.setdefault(tid, []).append(xiufu)
            if len(self.xiufu_lishi[tid]) > 100:
                self.xiufu_lishi[tid] = self.xiufu_lishi[tid][-100:]
        self.tupu.shezhi_baji(tid, {"xu": 0.3, "shi": 0.3})
        if self.jiyi:
            try: self.jiyi.jilu_xiufu(tid, xiufu)
            except: pass

    def jilu_ganzhi(self, miaoshu, jibie="zhong"):
        try:
            self.tupu.add_node(f"gz_{int(time.time()*1000)}",
                leixing="ganzhi", biaoqian=str(miaoshu)[:80],
                xiangqing=str(miaoshu)[:200], jibie=jibie,
                shijian=datetime.now().isoformat())
            self._qingli_leixing("ganzhi", 100)
        except: pass

    def jilu_fansi(self, miaoshu):
        try:
            self.tupu.add_node(f"fs_{int(time.time()*1000)}",
                leixing="fansi", biaoqian="静息反思",
                xiangqing=str(miaoshu)[:300], shijian=datetime.now().isoformat())
            self._qingli_leixing("fansi", 100)
        except: pass

    def _qingli_leixing(self, leixing, zuiduo=100):
        """清理超出上限的同类型节点, 防止图引擎无限增长"""
        try:
            nodes_of_type = [(nid, self.tupu._nodes[nid]) for nid in self.tupu.nodes()
                if self.tupu._nodes[nid].get("leixing") == leixing]
            if len(nodes_of_type) > zuiduo:
                nodes_of_type.sort(key=lambda x: str(x[1].get("shijian", "")))
                for nid, _ in nodes_of_type[:len(nodes_of_type) - zuiduo]:
                    try: self.tupu.remove_node(nid)
                    except: pass
        except: pass

    def check_dmn_rest(self):
        """检查经络中是否处于佐治(害检测)模式(供四脏器统一调用)"""
        try:
            for tid in ["bianchengti", "yunxingti", "fuzhiti"]:
                if self.tupu.has_node(tid):
                    if self.tupu._nodes[tid].get("zuozhi_mode") == "active":
                        return True
        except: pass
        return False

    def qu_wenti_liebiao(self, tid):
        with self.suo:
            return list(self.wenti_liebiao.get(tid, []))

    def qu_xiufu_lishi(self, tid):
        with self.suo:
            return list(self.xiufu_lishi.get(tid, []))

    def shezhi_jiedian(self, tid, key, val):
        if self.tupu.has_node(tid):
            self.tupu._nodes[tid][key] = val

    def baocun(self):
        try:
            data = {
                "jiedian": self.tupu._nodes,
                "bian": [(u, v, self.tupu._adj[u][v]) for u in self.tupu._adj for v in self.tupu._adj[u]],
                "wenti_liebiao": self.wenti_liebiao,
                "xiufu_lishi": self.xiufu_lishi,
                "baocun_shijian": datetime.now().isoformat(),
            }
            self.cunchu_wenjian.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception:
            pass

    def jiazai(self):
        if self.cunchu_wenjian.exists():
            try:
                data = json.loads(self.cunchu_wenjian.read_text(encoding='utf-8'))
                for k, v in data.get("jiedian", {}).items():
                    if self.tupu.has_node(k):
                        self.tupu._nodes[k].update(v)
                for u, v_attrs in data.get("bian", []):
                    self.tupu.add_edge(u, v_attrs[0], **(v_attrs[1] if len(v_attrs) > 1 else {}))
                for tid in self.wenti_liebiao:
                    self.wenti_liebiao[tid] = data.get("wenti_liebiao", {}).get(tid, [])
                for tid in self.xiufu_lishi:
                    self.xiufu_lishi[tid] = data.get("xiufu_lishi", {}).get(tid, [])
                return True
            except Exception:
                pass
        return False

    def zhuangtai_zhaiyao(self):
        zy = {}
        for tid in ["yunxingti", "bianchengti", "fuzhiti"]:
            if self.tupu.has_node(tid):
                zy[tid] = {
                    "zhuangtai": self.tupu._nodes[tid].get("zhuangtai", "?"),
                    "wenti_shu": len(self.wenti_liebiao.get(tid, [])),
                    "xiufu_shu": len(self.xiufu_lishi.get(tid, [])),
                }
        return zy

    @property
    def jiedian(self):
        return self.tupu._nodes

    # ---- 穹顶通信: 五脏通过经络消息路由而非直接对象引用 ----
    def zhuce_qiguan(self, tid, qiguan_type, callback):
        """注册器官回调, 实现穹顶自治(铁律6)"""
        if self.tupu.has_node(tid):
            self.tupu._nodes[tid][f"_{qiguan_type}_callback"] = callback
            self.tupu._nodes[tid][f"_{qiguan_type}_zhuche"] = True

    def hujiao_qiguan(self, from_tid, to_qiguan_type, *args, **kwargs):
        """通过经络调用目标器官方法(替代直接对象引用)"""
        for tid in ["bianchengti", "yunxingti", "fuzhiti"]:
            if self.tupu.has_node(tid):
                cb = self.tupu._nodes[tid].get(f"_{to_qiguan_type}_callback")
                if cb:
                    try:
                        result = cb(*args, **kwargs)
                        self.tupu._nodes[tid][f"_{to_qiguan_type}_last_call"] = str(time.time())
                        return result
                    except Exception as e:
                        self.jilu_wenti(tid, {"miaoshu": f"器官调用异常:{to_qiguan_type}:{e}", "leixing": "organ_call_error"})
                        return None

    def jilu_jianchadian(self, data: dict):
        """持久化任务计划检查点(RenWuJiHua使用)"""
        try:
            node_id = f"jcd_{int(time.time()*1000)}"
            self.tupu.add_node(node_id, leixing="jianchadian",
                mingcheng=str(data.get("buzhou",""))[:80],
                zhuangtai=str(data.get("zhuangtai","")),
                dabiao=bool(data.get("dabiao",False)),
                haoshi=float(data.get("haoshi",0)),
                shijian=str(data.get("shijian","")))
            # 清理旧检查点(保留最近50个)
            self._qingli_leixing("jianchadian", 50)
        except Exception: pass
        return None

    def jilu_yichang(self, yichang_text: str, yichang_type: str = "", laiyuan: str = "") -> None:
        """
        异常事件归档 V1.0 — 铁律15基础设施
        
        所有 except 块调用此方法 → 异常入经络 → 事后可追溯
        五境认知引擎监测新异常模式 → 触发 LLM 分析 → 建议害-佐声明
        
        参数:
          yichang_text: 异常描述或 traceback 摘要
          yichang_type: 异常类型名(如 'KeyError', 'ConnectionError')
          laiyuan: 来源(文件名:行号)
        """
        try:
            # 异常类型计数(用于检测新模式)
            key = yichang_type or "Unknown"
            node_id = f"yichang_{key}"
            if self.tupu.has_node(node_id):
                count = self.tupu._nodes[node_id].get("count", 0)
                self.tupu._nodes[node_id]["count"] = count + 1
                self.tupu._nodes[node_id]["last_seen"] = str(time.time())
            else:
                # 新异常模式 — 五境认知引擎可检测此信号
                self.tupu.add_node(node_id, leixing="yichang",
                    yichang_type=key, count=1, first_seen=str(time.time()),
                    sample=yichang_text[:200], laiyuan=laiyuan,
                    _new_pattern=True)
            # 写入反思日志
            self.jilu_fansi(f"异常|{key}|{laiyuan}|{yichang_text[:120]}")
        except Exception:
            pass

    # ==================== 信号中枢 (铁律16·一切信息走经络) ====================

    def fa_xinhao(self, qiguan: str, leixing: str, data: dict = None) -> None:
        """
        心向脏器发信号
        
        qiguan: "脾"/"肝"/"肺"/"肾"
        leixing: "execution"/"jiyi"/"shuchu"/"zhenduan"
        data: 附带数据
        
        信号写入 tupu 节点, 脏器 run() 循环轮询读取
        """
        try:
            xinhao_id = f"xinhao_{qiguan}_{int(time.time()*1000)}"
            self.tupu.add_node(xinhao_id, leixing="xinhao",
                               qiguan=qiguan, xinhao_leixing=leixing,
                               data=json.dumps(data or {}, ensure_ascii=False),
                               shijian=time.time(), processed=False)
            self.jilu_fansi(f"信号|心→{qiguan}|{leixing}")
        except Exception:
            pass

    def qu_xinhao(self, qiguan: str) -> list:
        """
        脏器轮询读取发给自己的信号
        
        返回: [{xinhao_leixing, data, shijian}, ...]
        读取后标记为 processed
        """
        xinhao_list = []
        try:
            for nid, node in list(self.tupu._nodes.items()):
                if (node.get("leixing") == "xinhao" and 
                    node.get("qiguan") == qiguan and
                    not node.get("processed", False)):
                    try:
                        data = json.loads(node.get("data", "{}"))
                    except Exception:
                        data = {}
                    xinhao_list.append({
                        "leixing": node.get("xinhao_leixing", ""),
                        "data": data,
                        "shijian": node.get("shijian", 0)
                    })
                    node["processed"] = True
        except Exception:
            pass
        return xinhao_list

    def jilu_shuru(self, msg: str) -> None:
        """记录输入到经络(肺·问剑路)"""
        self.jilu_fansi(f"输入|{msg[:120]}")
        try:
            self.tupu.add_node(f"shuru_{int(time.time()*1000)}",
                              leixing="shuru", neirong=msg[:200], shijian=time.time(),
                              _cuiliao=True)
        except Exception: pass

    def jilu_zhenduan(self, zhenduan: dict) -> None:
        """记录诊断到经络(心·五境+八极+六势态)"""
        self.jilu_fansi(
            f"诊断|六势={zhenduan.get('shizhi','?')}"
            f"|安全度={zhenduan.get('anquan_du',0):.2f}"
            f"|路由={zhenduan.get('luxian','?')}")
        try:
            self.tupu.add_node(f"zhenduan_{int(time.time()*1000)}",
                              leixing="zhenduan", **zhenduan, shijian=time.time())
        except Exception: pass

    def jilu_jieguo(self, qiguan: str, jieguo: str) -> None:
        """记录执行结果到经络(脏器干活后)"""
        self.jilu_fansi(f"结果|{qiguan}|{jieguo[:150]}")
        try:
            self.tupu.add_node(f"jieguo_{int(time.time()*1000)}",
                              leixing="jieguo", qiguan=qiguan, neirong=jieguo[:300])
        except Exception: pass
