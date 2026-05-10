"""
感知层 GanzhiCeng V1.0 [星巢·感官系统]
文件变化监测 · 系统资源感知 · 门控过滤 · 纯stdlib
将外部世界变化转为结构化感知信号, 注入经络图
"""
import os, time, threading
from pathlib import Path
from datetime import datetime


class GanzhiCeng:
    """感知层: 系统的"感官", 门控过滤后写入经络"""

    def __init__(self, meridian, xiangmu_mulu=None):
        self.meridian = meridian
        self.mulu = Path(xiangmu_mulu) if xiangmu_mulu else Path(__file__).parent.parent
        self._zuihou_saomiao = 0
        self._wenjian_kuaizhao = {}
        self._saomiao_jiange = 49  # 一小周, 与肺巡检对齐
        self._xitong_jinggao_cishu = 0
        # 门控阈值
        self.MENKONG_BIANHUA = 3       # 文件变化≥3个才通知
        self.MENKONG_CIPAN = 10        # 磁盘<10%才告警
        self.MENKONG_CPU = 80          # CPU持续>80% 3次才告警
        self._cpu_gao_cishu = 0

    # ---- 文件感知 ----
    def _saomiao_wenjian(self) -> dict:
        """扫描项目文件变化, 返回变更摘要"""
        bianhua = {"xinzeng": [], "xiugai": [], "shanchu": [], "zongshu": 0}
        try:
            dangqian = {}
            for fp in self.mulu.rglob("*.py"):
                if "__pycache__" in str(fp):
                    continue
                try:
                    mtime = os.path.getmtime(fp)
                    size = os.path.getsize(fp)
                    dangqian[str(fp.relative_to(self.mulu))] = (mtime, size)
                except Exception: pass
            bianhua["zongshu"] = len(dangqian)
            if self._wenjian_kuaizhao:
                old_keys = set(self._wenjian_kuaizhao.keys())
                new_keys = set(dangqian.keys())
                for k in new_keys - old_keys:
                    bianhua["xinzeng"].append(k)
                for k in old_keys - new_keys:
                    bianhua["shanchu"].append(k)
                for k in old_keys & new_keys:
                    if dangqian[k] != self._wenjian_kuaizhao[k]:
                        bianhua["xiugai"].append(k)
            self._wenjian_kuaizhao = dangqian
        except Exception: pass
        return bianhua

    # ---- 系统感知 ----
    def _xitong_zhibiao(self) -> dict:
        """采集CPU/内存/磁盘指标"""
        zhibiao = {"cpu": 0, "neicun": 0, "cipan": 100, "cipan_lujing": str(self.mulu)}
        try:
            import shutil
            usage = shutil.disk_usage(str(self.mulu.anchor))
            zhibiao["cipan"] = round(usage.free / usage.total * 100, 1)
        except Exception: pass
        # CPU/内存(psutil可选, 没有时跳过)
        try:
            _psutil = __import__('psutil')
            zhibiao["cpu"] = round(_psutil.cpu_percent(interval=0.5), 1)
            zhibiao["neicun"] = round(_psutil.virtual_memory().percent, 1)
        except Exception: pass
        return zhibiao

    # ---- 门控 ----
    def ganzhi_menkong(self, bianhua: dict, zhibiao: dict) -> list:
        """门控过滤: 只有超过阈值的变化才产生感知事件"""
        shijian_list = []
        zong = len(bianhua.get("xinzeng", [])) + len(bianhua.get("shanchu", [])) + len(bianhua.get("xiugai", []))
        if zong >= self.MENKONG_BIANHUA:
            shijian_list.append({
                "leixing": "wenjian_bianhua",
                "youxianji": 1,
                "miaoshu": f"文件变更{bianhua.get('zongshu',0)}个文件, 变动{zong}个"
            })
        if zhibiao.get("cipan", 100) < self.MENKONG_CIPAN:
            shijian_list.append({
                "leixing": "cipan_di",
                "youxianji": 2,
                "miaoshu": f"磁盘仅剩{zhibiao['cipan']}% ({zhibiao.get('cipan_lujing','')})"
            })
        if zhibiao.get("cpu", 0) > self.MENKONG_CPU:
            self._cpu_gao_cishu += 1
            if self._cpu_gao_cishu >= 3:
                shijian_list.append({
                    "leixing": "cpu_gao",
                    "youxianji": 1,
                    "miaoshu": f"CPU持续高负载({zhibiao['cpu']}%), 已持续{self._cpu_gao_cishu}次"
                })
        else:
            self._cpu_gao_cishu = 0
        return shijian_list

    # ---- 周期巡检入口 ----
    def xunjian_yici(self):
        """一次完整感知巡检, 吸入外部世界→门控→写经络"""
        if time.time() - self._zuihou_saomiao < self._saomiao_jiange:
            return
        self._zuihou_saomiao = time.time()
        try:
            bianhua = self._saomiao_wenjian()
            zhibiao = self._xitong_zhibiao()
            shijian_list = self.ganzhi_menkong(bianhua, zhibiao)
            for sj in shijian_list:
                self.meridian.jilu_ganzhi(
                    f"感知:{sj['leixing']}:{sj['miaoshu']}",
                    "gao" if sj['youxianji'] >= 2 else "zhong")
        except Exception: pass

    def qu_kuaizhao(self) -> dict:
        """获取当前环境快照(不写经络, 供RenWuJiHua Control阶段使用)"""
        try:
            return {
                "py_wenjian": len(list(self.mulu.rglob("*.py"))),
                "shijian": datetime.now().isoformat(),
            }
        except Exception:
            return {}
