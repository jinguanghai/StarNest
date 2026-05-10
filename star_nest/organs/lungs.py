"""
五脏·肺 (fei.py) - 藏魄，相傅之官，治节出焉
V10.3 相傅治节版（单机模式·P2P已关闭）：场景分析、输出审查、合境九屏幕法代理、
架构巡检（手握自审镜唯一钥匙）、审查档案管理、五行信号响应、
12遍失败后的最终分析报告。

肺是自审镜的唯一调用者——相傅之官，主气，司呼吸，治节出焉。
治节 = 架构巡检 + 规矩监控 + 内化建议，全部写入审查档案和经络图谱。

五行信号响应（金属性）：
- 火克金：肃杀降级（_shaxiang_jiangji = True）
- 土生金：解除降级（_shaxiang_jiangji = False）

P2P状态：已关闭（单机模式）。如需恢复，将 _p2p_yunxing 改为 True 即可。

【七律映射】
- 呼吸周期 = 49 (一小周)
- 日巡检周期 = 16807 (一周天·全量巡检)
- 周巡检周期 = 117649 (七周天·深度自审)

【自审镜调用（唯一入口）】
- _shencha_xunjian() → zijingshi.quanjing_jiancha() → 写入审查档案 + 经络图谱
"""

import json, threading, time, traceback
from pathlib import Path
from datetime import datetime
from star_nest.meridian.seven_laws import QiLv

class FeiZang(threading.Thread):
    """肺线程：主气，司呼吸。场景分析、输出审查、架构巡检、五行信号响应、经络写入、报告汇总"""

    def __init__(self, meridian, llm, peizhi, juese="yunxingti"):
        ziwowangluo = meridian
        cunchu_mulu = peizhi.XINGCHAOZDD_MULU
        self.meridian = meridian
        self.peizhi = peizhi
        self.juese = juese
        self._yunxing = True
        super().__init__(daemon=True, name="Fei_Scene")
        self.wangluo = ziwowangluo
        self.llm = llm
        self.mulu = cunchu_mulu or Path(__file__).parent.parent / "jiyi"
        self.mulu.mkdir(exist_ok=True)
        
        self._p2p_yunxing = False
        
        self._alive = True
        self._last_heartbeat = time.time()
        self._heartbeat_interval = 5.0
        self._shaxiang_jiangji = False
        
        self.pianhao_json = self.mulu / "yonghu_pianhao.json"
        self.shencha_json = (self.mulu / "shared_memory" / "shencha_dangan.json") if cunchu_mulu else (self.mulu / "shencha_dangan.json")
        
        self.changjing_ci = {
            "指令执行": ["帮我", "执行", "写一段"],
            "系统调试": ["为什么", "报错", "修复"],
            "复盘总结": ["总结", "回顾", "复盘"],
            "自主迭代": ["升级", "优化", "进化"],
            "日常交互": ["你好", "你是谁", "谈谈"]
        }
        self.fengge_yingshe = {
            "指令执行": "简洁高效", "系统调试": "专业严谨",
            "复盘总结": "详细全面", "自主迭代": "详细全面", "日常交互": "balanced"
        }
        self.pianhao = self._jiazai_pianhao()
        self.shencha_dangan = self._jiazai_shencha()  # V10.3 审查档案
        
        self._zuihou_huxi_xunjian = 0
        self._zuihou_ri_xunjian = 0
        self._zuihou_zhou_xunjian = 0
        
        self.suo = threading.Lock()
        self._yunxing = True
        self._warmup_complete = False

        self.hejing = None

        print(f"[肺] 就绪（V10.3 相傅治节版·单机模式·P2P已关闭）。")

    def run(self):
        """主循环：经络信号轮询(快) + 呼吸节律(慢) + 架构巡检"""
        self._zuozhi_ganzhi = 0
        while self._yunxing:
            # 经络信号轮询: 心发信号给肺 → 肺推 shuchu_duilie (使输出)
            self._chuli_xinhao()
            self._last_heartbeat = time.time()
            time.sleep(QiLv().qu_zhouqi("yiweizhou"))  # 7s
            self._xiangying_wuxing_xinhao()
            self._shencha_xunjian()
            if self.wangluo and self.wangluo.check_dmn_rest() and time.time() - self._zuozhi_ganzhi > 343:
                self._zuozhi_changjing()
                self._zuozhi_ganzhi = time.time()

    def _chuli_xinhao(self):
        """肺·处理经络信号: 心发信号 → 肺推输出(使·浑天令展示)"""
        try:
            if not self.xin or not self.xin.meridian:
                return
            xinhao_list = self.xin.meridian.qu_xinhao("fei")
            for xh in xinhao_list:
                if xh.get("leixing") == "shuchu":
                    text = xh.get("data", {}).get("text", "")
                    if text:
                        self.xin.shuchu_duilie.put(text)
        except Exception:
            pass

    def _zuozhi_changjing(self):
        """佐治·场景感知: 检测硬件层害(文件变化/磁盘不足)"""
        try:
            import os, time as _t
            from pathlib import Path
            root = Path(__file__).parent.parent
            py_count = len(list(root.rglob("*.py")))
            db_count = len(list(root.rglob("*.db")))
            md_count = len(list(root.rglob("*.md")))
            scene = f"环境快照: {py_count}个py文件, {db_count}个数据库, {md_count}个文档"
            if self.wangluo:
                self.wangluo.jilu_ganzhi(f"DMN场景感知: {scene}", "di")
        except Exception: pass

    # ========== 五行信号响应 ==========
    def _xiangying_wuxing_xinhao(self):
        """
        五行信号响应（金属性）：
        - 火克金：肃杀降级，_shaxiang_jiangji = True
        - 土生金：解除降级，_shaxiang_jiangji = False
        """
        if not self.wangluo:
            return
        
        xianzai = time.time()
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
                
                if leixing == "wuxing_ke" and "火克金" in biaoqian:
                    self._shaxiang_jiangji = True
                elif leixing == "wuxing_sheng" and "土生金" in biaoqian:
                    self._shaxiang_jiangji = False
        except Exception as e:
            try:
                if self.wangluo and hasattr(self.wangluo, 'rizhi'):
                    self.wangluo.rizhi.wenti_rizhi(self.juese, {"miaoshu": f"五行信号异常:{e}", "leixing": "wuxing_error"})
            except Exception: pass

    # ========== 架构巡检 ==========
    def _shencha_xunjian(self):
        """
        治节·架构巡检——肺作为自审镜唯一调用者，按七律周期执行三级巡检。
        """
        xianzai = time.time()
        qilv = self.wangluo.qilv if self.wangluo else None
        if not qilv:
            return
        
        # === 呼吸巡检（每yixiaozhou） ===
        if xianzai - self._zuihou_huxi_xunjian >= qilv.qu_zhouqi("yixiaozhou"):
            self._zuihou_huxi_xunjian = xianzai
            self._huxi_xunjian()
        
        # === 日巡检（每yizhoutian） ===
        if xianzai - self._zuihou_ri_xunjian >= qilv.qu_zhouqi("yizhoutian"):
            self._zuihou_ri_xunjian = xianzai
            self._ri_xunjian()
        
        # === 周巡检（每yijiyuan） ===
        if xianzai - self._zuihou_zhou_xunjian >= qilv.qu_zhouqi("yijiyuan"):
            self._zuihou_zhou_xunjian = xianzai
            self._zhou_xunjian()

    def _huxi_xunjian(self):
        """呼吸巡检：快速检查核心文件是否存在"""
        from star_nest.introspection import ZiJingShi
        zijing = ZiJingShi()
        wenti_liebiao = []
        
        hexin_wenjian = [
            "xinghe/xin.py", "xinghe/gan.py", "xinghe/pi.py",
            "xinghe/fei.py", "xinghe/shen.py", "qidong.py"
        ]
        for wj in hexin_wenjian:
            if not (zijing.root / wj).exists():
                wenti_liebiao.append({
                    "mubiao": wj,
                    "miaoshu": f"核心文件缺失: {wj}",
                    "yanzhongdu": "gao",
                    "sheji_biaoji": "核心文件缺失"
                })
        
        if wenti_liebiao:
            self._chuli_xunjian_wenti(wenti_liebiao, "huxi_xunjian")

    def _ri_xunjian(self):
        """日巡检：全量架构合规性检查"""
        try:
            from star_nest.introspection import ZiJingShi
            zijing = ZiJingShi()
            # 铁律5: 传入LLM做深度意图分析
            llm = self.xin.llm if hasattr(self, 'xin') and self.xin and self.xin.llm else None
            jiancha_jieguo = zijing.quanjing_jiancha(llm=llm)
            
            wenti_liebiao = jiancha_jieguo if isinstance(jiancha_jieguo, list) else jiancha_jieguo.get("wenti_liebiao", [])
            guiju_zhuangtai = {}
            if isinstance(jiancha_jieguo, dict):
                guiju_zhuangtai = jiancha_jieguo.get("guiju_zhuangtai", {})
            
            self._gengxin_shencha_dangan(wenti_liebiao, guiju_zhuangtai, "ri_xunjian")
            
            if wenti_liebiao and self.wangluo:
                wenti_zhaiyao = "; ".join([w.get("miaoshu","")[:80] for w in wenti_liebiao[:3]])
                self.wangluo.jilu_shijian(
                    leixing="shencha_xunjian",
                    biaoqian="日巡检",
                    xiangqing=f"发现{len(wenti_liebiao)}个问题: {wenti_zhaiyao}"
                )
                
                gaowei = [w for w in wenti_liebiao if w.get("yanzhongdu") == "gao"]
                for gw in gaowei:
                    self.wangluo.jilu_shijian(
                        leixing="zoushe",
                        biaoqian="紧急奏折",
                        xiangqing=json.dumps(gw, ensure_ascii=False)
                    )
        except Exception as e:
            if self.wangluo:
                try:
                    self.wangluo.jilu_ganzhi(f"架构巡检异常: {str(e)[:100]}", "zhong")
                except Exception:
                    pass

    def _zhou_xunjian(self):
        """周巡检：深度自审——自审镜自指，检查审查逻辑本身"""
        try:
            from star_nest.introspection import ZiJingShi
            zijing = ZiJingShi()
            
            wenti_liebiao = []
            
            zijingshi_path = zijing.root / "xinghe" / "zijingshi.py"
            if zijingshi_path.exists():
                try:
                    zijingshi_code = zijingshi_path.read_text(encoding='utf-8')
                    if "quanjing_jiancha" not in zijingshi_code:
                        wenti_liebiao.append({
                            "mubiao": "zijingshi.py",
                            "miaoshu": "自审镜缺少 quanjing_jiancha 方法",
                            "yanzhongdu": "gao",
                            "sheji_biaoji": "自审镜自指"
                        })
                except Exception: pass
            
            if "xinghe" not in zijing.hexin_mulu:
                wenti_liebiao.append({
                    "mubiao": "zijingshi.py",
                    "miaoshu": "hexin_mulu 不包含自身目录",
                    "yanzhongdu": "zhong",
                    "sheji_biaoji": "自审镜自指"
                })
            
            if wenti_liebiao:
                self._chuli_xunjian_wenti(wenti_liebiao, "zhou_xunjian")
        except Exception as e:
            pass

    # ========== 审查档案管理 ==========
    def _jiazai_shencha(self) -> dict:
        if self.shencha_json.exists():
            try:
                return json.loads(self.shencha_json.read_text(encoding='utf-8'))
            except Exception as e:
                try:
                    if self.wangluo and hasattr(self.wangluo, 'rizhi'):
                        self.wangluo.rizhi.wenti_rizhi(self.juese, {"miaoshu": f"审查档案加载异常:{e}", "leixing": "shencha_error"})
                except Exception: pass
        return {
            "shencha_jilu": [],
            "guiju_jiankong": {
                "pi_phi_xunhuan": {"pianli_cishu": 0, "zuihou_jiancha": ""},
                "protocols_jiyi_tiaoyong": {"pianli_cishu": 0, "zuihou_jiancha": ""},
                "qilv_hegui": {"pianli_cishu": 0, "zuihou_jiancha": ""},
                "wuxing_xinhao": {"pianli_cishu": 0, "zuihou_jiancha": ""}
            }
        }

    def _baocun_shencha(self):
        try:
            self.shencha_json.write_text(
                json.dumps(self.shencha_dangan, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
        except Exception: pass

    def _gengxin_shencha_dangan(self, wenti_liebiao: list, guiju_zhuangtai: dict, zhouqi: str):
        shijian = datetime.now().isoformat()
        
        jilu = {
            "shijian": shijian,
            "zhouqi": zhouqi,
            "wenti_shu": len(wenti_liebiao),
            "wenti_liebiao": wenti_liebiao[:20]
        }
        self.shencha_dangan["shencha_jilu"].append(jilu)
        if len(self.shencha_dangan["shencha_jilu"]) > 100:
            self.shencha_dangan["shencha_jilu"] = self.shencha_dangan["shencha_jilu"][-100:]
        
        for guiju_ming, pianli in guiju_zhuangtai.items():
            if guiju_ming in self.shencha_dangan["guiju_jiankong"]:
                self.shencha_dangan["guiju_jiankong"][guiju_ming]["pianli_cishu"] += pianli
                if pianli > 0:
                    self.shencha_dangan["guiju_jiankong"][guiju_ming]["zuihou_jiancha"] = shijian
        
        self._baocun_shencha()

    def _chuli_xunjian_wenti(self, wenti_liebiao: list, zhouqi: str):
        guiju = {}
        for w in wenti_liebiao:
            biaoji = w.get("sheji_biaoji", "")
            if "π-φ" in biaoji:
                guiju["pi_phi_xunhuan"] = guiju.get("pi_phi_xunhuan", 0) + 1
            elif "记忆" in biaoji:
                guiju["protocols_jiyi_tiaoyong"] = guiju.get("protocols_jiyi_tiaoyong", 0) + 1
            elif "七律" in biaoji:
                guiju["qilv_hegui"] = guiju.get("qilv_hegui", 0) + 1
            elif "五行" in biaoji:
                guiju["wuxing_xinhao"] = guiju.get("wuxing_xinhao", 0) + 1
        
        self._gengxin_shencha_dangan(wenti_liebiao, guiju, zhouqi)

    # ========== 启动预热：场景感知 ==========
    def qidong_warmup(self):
        print("[肺] 场景感知中...")
        print(f"[肺]   风格偏好：{self.pianhao.get('fengge', 'balanced')}")
        print(f"[肺]   技术偏好：{self.pianhao.get('jishu', 0.5)}")
        
        try:
            import shutil
            chicun = shutil.get_terminal_size(fallback=(80, 24))
            print(f"[肺]   终端尺寸：{chicun.columns}x{chicun.lines}")
        except Exception:
            print(f"[肺]   终端尺寸：80x24 (默认)")
        
        try:
            import platform
            print(f"[肺]   操作系统：{platform.system()} {platform.release()}")
        except Exception: pass
        
        jilu_shu = len(self.shencha_dangan.get("shencha_jilu", []))
        print(f"[肺]   审查档案：{jilu_shu} 条历史记录")
        
        try:
            if self.wangluo:
                self.wangluo.jilu_ganzhi(
                    f"启动场景感知：风格={self.pianhao.get('fengge','balanced')}",
                    "di"
                )
        except Exception: pass
        
        self._warmup_complete = True
        print("[肺] 场景基线已建立")

    # ========== 用户偏好 ==========
    def _jiazai_pianhao(self):
        if self.pianhao_json.exists():
            try: return json.loads(self.pianhao_json.read_text(encoding='utf-8'))
            except Exception: pass
        return {"fengge": "balanced", "jishu": 0.5}

    # ========== 合境代理 ==========
    def hejing_jiupingmu(self, llm, yonghu_xiaoxi, gongneng_fenxi, yinguo_fenxi):
        if not self.hejing:
            return {"shijian_weidu":{},"kongjian_weidu":{},"pingheng_fangan":"","ke_huigun":False,"fengxian_pinggu":"中","liansuo_yingxiang":""}
        return self.hejing.hejing_jiupingmu(llm, yonghu_xiaoxi, gongneng_fenxi, yinguo_fenxi)

    # ========== 场景感知与输出审查 ==========
    def qu_changjing_shangxiawen(self, yonghu_xiaoxi):
        changjing = "日常交互"
        for c, ci in self.changjing_ci.items():
            if any(k in yonghu_xiaoxi for k in ci): changjing = c; break
        fengge = self.fengge_yingshe.get(changjing, "balanced")
        if fengge == "balanced": fengge = self.pianhao.get("fengge", "balanced")
        return f"\n【场景】{changjing}，风格：{fengge}，气场：{self._ganzhi_qichang(yonghu_xiaoxi)}\n"

    def _ganzhi_qichang(self, xiaoxi):
        if len(xiaoxi) < 15: return "精炼"
        if "为什么" in xiaoxi and "不" in xiaoxi: return "审慎"
        return "平和"

    def shencha_shuchu(self, shuchu_text):
        if "五境" in shuchu_text and "正-反-合-超越-本源" not in shuchu_text:
            shuchu_text = shuchu_text.replace("五境", "五境（正-反-合-超越-本源）")
        return shuchu_text

    def jilu_shuchu_ganzhi(self, shuchu_text):
        if self.wangluo:
            self.wangluo.jilu_ganzhi(f"输出{len(shuchu_text)}字", "di" if len(shuchu_text)<=800 else "zhong")

    # ========== 汇总报告 ==========
    def xie_baogao(self, liuzhuan_jilu: list, yuanshi_wenti: str) -> str:
        shijian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        baogao = []
        baogao.append("─" * 60)
        baogao.append("  五境认知引擎 · 完整分析报告")
        baogao.append("─" * 60)
        baogao.append(f"  生成时间：{shijian}")
        baogao.append(f"  原始问题：{yuanshi_wenti[:200]}")
        baogao.append(f"  流转遍数：{len(liuzhuan_jilu)}")
        baogao.append("")
        baogao.append("─" * 60)
        baogao.append("  十二遍分析摘要")
        baogao.append("─" * 60)
        for jilu in liuzhuan_jilu:
            bianshu = jilu.get("bianshu", "?")
            gongneng = jilu.get("gongneng", {})
            yinguo = jilu.get("yinguo", {})
            jiupingmu = jilu.get("jiupingmu", {})
            jieguo = jilu.get("jieguo", {})
            baogao.append(f"  第{bianshu}遍：")
            baogao.append(f"    正境：主体={gongneng.get('zhuti','?')}，客体={gongneng.get('keti','?')}，作用={gongneng.get('zuoyong','?')}")
            baogao.append(f"    反境：必要条件={yinguo.get('biyao_tiaojian','?')}，阻碍={yinguo.get('zuai_yinsu','?')}")
            baogao.append(f"    合境：方案={jiupingmu.get('pingheng_fangan','?')[:100]}")
            baogao.append(f"    执行：{'成功' if jieguo.get('success') else '失败'} — {jieguo.get('error','')[:100]}")
            baogao.append("")
        baogao.append("─" * 60)
        baogao.append("  尝试过的方案")
        baogao.append("─" * 60)
        fangan_list = []
        for jilu in liuzhuan_jilu:
            fangan = jilu.get("jiejue_fangan", "")
            if fangan: fangan_list.append(fangan[:200])
        if fangan_list:
            for i, fa in enumerate(fangan_list, 1): baogao.append(f"  方案{i}：{fa}")
        else:
            baogao.append("  （未生成有效方案）")
        baogao.append("")
        zuihou_jilu = liuzhuan_jilu[-1] if liuzhuan_jilu else {}
        zuihou_jieguo = zuihou_jilu.get("jieguo", {})
        baogao.append("─" * 60)
        baogao.append("  最终阻碍")
        baogao.append("─" * 60)
        baogao.append(f"  {zuihou_jieguo.get('error', '未知')[:300]}")
        baogao.append("")
        baogao.append("─" * 60)
        baogao.append("  建议方向")
        baogao.append("─" * 60)
        baogao.append("  1. 检查问题的定义是否准确——是否需要从更根本的层面重新审视")
        baogao.append("  2. 考虑问题是否存在物理矛盾——当前技术条件下可能无解")
        baogao.append("  3. 尝试降低问题的复杂度——将大问题拆分为多个小问题逐个解决")
        baogao.append("  4. 如果涉及外部资源或权限，确认当前环境是否满足条件")
        baogao.append("─" * 60)
        return "\n".join(baogao)

    def qu_zouzhai(self):
        """取走债: 返回肺(巡检)相关的未解决问题"""
        zhai = []
        try:
            if self.wangluo:
                for tid in ["bianchengti","yunxingti"]:
                    for w in self.wangluo.qu_wenti_liebiao(tid):
                        ms = str(w.get("miaoshu",""))[:100]
                        if any(kw in ms for kw in ["巡检","合规","文件","审计","shencha","wenjian"]):
                            zhai.append(f"[肺-巡检债|{tid}] {ms}")
                # 检查审查档案
                gz_nodes = [self.wangluo.tupu._nodes[n] for n in self.wangluo.tupu.nodes()
                    if self.wangluo.tupu._nodes[n].get("leixing") == "ganzhi"]
                if gz_nodes:
                    high = [g for g in gz_nodes if g.get("jibie") == "gao"][-3:]
                    for h in high:
                        zhai.append(f"[肺-感知债] {h.get('xiangqing','')[:80]}")
        except Exception: pass
        return zhai

    def tingzhi(self):
        self._yunxing = False