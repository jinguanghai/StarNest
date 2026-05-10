"""
五脏·肾 (shen.py) - 藏志，作强之官，伎巧出焉
V10.3 纯净诊断版（超越境接入·静息思考·补全历史诊断传递）：
肾只负责：八极诊断、静息思考、进化双翼、超越境代理、康复档案、五行信号响应。
八极诊断扩展读取肺巡检报告——从经络图谱感知规矩偏离。
删除全部六势态自愈代码、自审镜调用、xiufu 守护线程引用。

五行信号响应（水属性）：
- 土克水：加速诊断（缩短动态平衡冷却）
- 金生水：正常诊断（恢复冷却周期）

【七律映射】
- run() 静息周期 = 343 (一中周·约6分钟)
- 进化双翼·动态平衡冷却 = 2401 (一大周·约40分钟)
- 进化双翼·突破创新冷却 = 117649 (一纪元·约32.7小时)
"""

import threading, time, json, re
from pathlib import Path
from datetime import datetime
from star_nest.meridian.seven_laws import QiLv
from star_nest.protocols.harm_assist import sheng_ming_hai, sheng_ming_zuo

class ShenZang(threading.Thread):
    """肾线程：意志引擎，作强之官，出超越境之伎巧。进化双翼、八极诊断、经络写入、超越境代理、静息思考"""

    def __init__(self, meridian, llm, baji, peizhi, juese="yunxingti"):
        ziwowangluo = meridian
        xin_yinyong = None
        self.meridian = meridian
        self.baji = baji
        self.peizhi = peizhi
        self.juese = juese
        self._yunxing = True
        super().__init__(daemon=True, name="Shen_Will")
        self.wangluo = ziwowangluo
        self.xin = xin_yinyong
        self.llm = llm or (xin_yinyong.llm if xin_yinyong else None)
        self._zuihou_xintiao = time.time()
        self._jiuchou = None  # 九宫健康矩阵
        self._init_jiuchou()

        self.xiangmu_mulu = Path(__file__).resolve().parent.parent
        self.sikao_rizhi_md = self.xiangmu_mulu / "jiyi" / "sikao_rizhi.md"
        self.kangfu_dangan_md = self.xiangmu_mulu / "jiyi" / "kangfu_dangan.md"
        self.beifen_mulu = self.xiangmu_mulu / "jinhua" / "beifen"
        self.hexin_faze = "正-反-合-超越-本源"
        (self.xiangmu_mulu / "jiyi").mkdir(parents=True, exist_ok=True)

        # 进化双翼参数（保留冷却期，使用七律）
        self._zuihou_pingheng = 0
        self._zuihou_tupo = 0
        self._daiding_zhongzi = []
        self._zhongzi_suo = threading.Lock()

        self._alive = True
        self._last_heartbeat = time.time()
        self._yunxing = True
        self._warmup_complete = False

        self.chaoyuejing = None

        print("[肾] 就绪（V10.3 纯净诊断版·经络感知·五行信号响应）。")

    def _init_jiuchou(self):
        try:
            from star_nest.dynamics.nine_domains import NineDomainsHealth
            self._jiuchou = NineDomainsHealth()
        except Exception:
            pass

    def run(self):
        self._zuozhi_shendu = 0
        while self._yunxing:
            self._last_heartbeat = time.time()
            # 经络信号轮询: 心发信号 → 肾接收(zishen) → 调自审镜
            self._chuli_xinhao()
            time.sleep(QiLv().qu_zhouqi("yiweizhou"))  # 7s
            if time.time() - self._zuihou_xintiao > 120 and self.xin and self.xin.llm:
                self._jingxi_sikao()
                self._zuihou_xintiao = time.time()
            self._xiangying_wuxing_xinhao()
            # 进化停滞检测
            if time.time() - self._zuihou_xintiao > 1800:
                if self.wangluo:
                    try: self.wangluo.jilu_ganzhi("进化停滞（超半小时无心跳）", "zhong")
                    except Exception: pass
            # 佐治: 深度诊断——检查系统性害(问题模式/健康度趋势)
            if self.wangluo and self.wangluo.check_dmn_rest() and time.time() - self._zuozhi_shendu > 2401 \
                    and self.xin and self.xin.llm:
                self._zuozhi_shendu()
                self._zuozhi_shendu = time.time()

    def _chuli_xinhao(self):
        """肾·超越境: 接收心信号 → 调自审镜(进化自审)"""
        try:
            if not self.xin or not self.xin.meridian: return
            for xh in self.xin.meridian.qu_xinhao("shen"):
                if xh.get("leixing") == "zishen":
                    try:
                        from star_nest.introspection import ZiJingShi
                        zjs = ZiJingShi()
                        wenti = zjs.quanjing_jiancha()
                        if wenti and self.xin.meridian:
                            self.xin.meridian.jilu_fansi(f"自审镜: {len(wenti)}个问题")
                    except Exception: pass
        except Exception: pass

    def _zuozhi_shendu(self):
        """佐治·深度诊断: 分析近期问题模式(害), LLM反思演化方向"""
        try:
            zhenduan = self.baji_zhenduan()
            wenti_quyu = zhenduan.get("wenti_quyu", [])
            jl = self.wangluo
            wenti_list = []
            for tid in ["yunxingti", "bianchengti"]:
                wenti_list.extend(jl.qu_wenti_liebiao(tid)[-5:])
            wenti_text = "\n".join([str(w.get("miaoshu",""))[:100] for w in wenti_list[-5:]])
            if not wenti_text and not wenti_quyu:
                return
            # V11.0: 统一认知包
            from star_nest.protocols.cognition_package import RenzhiBao
            bao = RenzhiBao.from_xin(self.xin, "超越境") if self.xin else RenzhiBao("超越境")
            bao.shu_ju(
                zhenduan=f"异常区域:{','.join(wenti_quyu) if wenti_quyu else '无'}",
                zuijin_wenti=wenti_text[:500],
            )
            jg = self.xin.llm.chat([{"role":"user","content":bao.to_json()}], wendu=0.3, zuidazifu=400)
            if jg:
                self.wangluo.jilu_fansi(f"深度反思: {jg[:300]}")
                self._xie_sikao_rizhi(f"DMN深度反思: {jg[:200]}")
        except Exception: pass

    # ========== 五行信号响应 ==========
    def _xiangying_wuxing_xinhao(self):
        """
        五行信号响应（水属性）：
        - 土克水：加速诊断（缩短动态平衡冷却）
        - 金生水：正常诊断（恢复冷却为七律一大周）
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

                if leixing == "wuxing_ke" and "土克水" in biaoqian:
                    self._zuihou_pingheng = max(0, self._zuihou_pingheng - 1200)
                elif leixing == "wuxing_sheng" and "金生水" in biaoqian:
                    self._zuihou_pingheng = time.time()
        except Exception: pass

    def gengxin_xintiao(self):
        self._zuihou_xintiao = time.time()

    def qu_hexin_faze(self) -> str:
        return self.hexin_faze

    # ========== 启动预热 ==========
    def qidong_warmup(self):
        """启动时完整预热：读取历史诊断→执行八极诊断→写入档案。"""
        print("[肾] 静息思考中...")
        lishi_zhenduan = ""
        if self.kangfu_dangan_md.exists():
            try:
                neirong = self.kangfu_dangan_md.read_text(encoding='utf-8')
                zhenduan_list = re.findall(r'## ([\d\-T:]+) 康复诊断\n(.*?)(?=\n##|\Z)', neirong, re.DOTALL)
                zuijin = zhenduan_list[-5:] if len(zhenduan_list) > 5 else zhenduan_list
                if zuijin:
                    lishi_zhenduan = "\n".join([f"{sj}: {zd[:100]}" for sj, zd in zuijin])
                    print(f"[肾]   历史诊断：{len(zuijin)} 条已加载")
            except Exception as e:
                print(f"[肾]   历史诊断读取失败: {e}")
        else:
            print(f"[肾]   首次启动，无历史诊断")

        zhenduan = self.baji_zhenduan()
        wenti_quyu = zhenduan.get("wenti_quyu", [])
        baji_junzhi = zhenduan.get("baji_junzhi", {})

        print(f"[肾]   节点总数：{zhenduan.get('zongshu', 0)}")
        if baji_junzhi:
            print(f"[肾]   八极均值：阳={baji_junzhi.get('yang','?')} 阴={baji_junzhi.get('yin','?')} "
                  f"表={baji_junzhi.get('biao','?')} 里={baji_junzhi.get('li','?')} "
                  f"寒={baji_junzhi.get('han','?')} 热={baji_junzhi.get('re','?')} "
                  f"虚={baji_junzhi.get('xu','?')} 实={baji_junzhi.get('shi','?')}")
        if wenti_quyu:
            print(f"[肾]   发现异常：{', '.join(wenti_quyu)}")
            if self.wangluo:
                try:
                    self.wangluo.jilu_ganzhi(f"八极异常：{', '.join(wenti_quyu)}", "zhong")
                except Exception: pass
        else:
            print(f"[肾]   系统健康，无异常")

        self._xie_sikao_rizhi(f"启动预热诊断：节点={zhenduan.get('zongshu',0)}，异常={', '.join(wenti_quyu) if wenti_quyu else '无'}")
        try:
            shijian = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            wenti_text = ""
            if wenti_quyu:
                for w in wenti_quyu:
                    wenti_text += f"- {w}\n"
            with open(self.kangfu_dangan_md, 'a', encoding='utf-8') as f:
                f.write(f"\n## {shijian} 启动诊断\n{wenti_text or '运行平稳。'}\n")
        except Exception as e:
            print(f"[肾]   康复档案写入失败: {e}")

        self._warmup_complete = True
        print("[肾] 健康基线已建立")

    def _jilu_zhongzi_shengcheng(self, zhongzi):
        try:
            if self.wangluo:
                self.wangluo.jilu_jianyi(
                    leixing="jinhua_zhongzi",
                    neirong=json.dumps(zhongzi, ensure_ascii=False),
                    xinyidu=0.7
                )
        except Exception: pass

    # ========== 五行流转接口 ==========
    def jingsi_shendu(self):
        try:
            zhenduan = self.baji_zhenduan()
            wenti_text = ""
            if zhenduan.get("wenti_quyu"):
                for w in zhenduan["wenti_quyu"]: wenti_text += f"- {w}\n"
            if wenti_text:
                self._xie_sikao_rizhi(f"五行流转·金生水 诊断：{wenti_text[:200]}")
            shijian = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.kangfu_dangan_md, 'a', encoding='utf-8') as f:
                f.write(f"\n## {shijian} 流转诊断\n{wenti_text or '运行平稳。'}\n")
            if wenti_text and self.wangluo:
                self.wangluo.jilu_shijian(
                    leixing="jingsi_shendu",
                    biaoqian="流转诊断",
                    xiangqing=wenti_text[:200]
                )
        except Exception: pass

    # ========== 进化双翼 ==========
    def jiancha_jinhua(self):
        self._hejing_dongtai_pingheng()
        self._chaoyuejing_tupo_chuangxin()

    def _hejing_dongtai_pingheng(self):
        """合境·动态平衡：根据八极诊断结果，写入经络信号，由肝免疫循环响应"""
        if time.time() - self._zuihou_pingheng < QiLv().qu_zhouqi("yidazhou"): return  # 七律一大周
        self._zuihou_pingheng = time.time()
        zhenduan = self.baji_zhenduan()
        wenti_quyu = zhenduan.get("wenti_quyu", [])
        for w in wenti_quyu:
            if self.wangluo:
                try:
                    self.wangluo.jilu_shijian(
                        leixing="baji_tiaozheng",
                        biaoqian="动态平衡",
                        xiangqing=f"八极异常：{w}"
                    )
                except Exception: pass
        # 九宫健康矩阵: 写入健康评分 + 消费
        if self._jiuchou:
            try:
                jk = zhenduan.get("jiankangdu", 0.5)
                self._jiuchou.set_score("fa_shang", 0.8 if jk > 0.6 else 0.4)
                self._jiuchou.set_score("shu_xia", jk)
                self._jiuchou.set_score("qi_xia", 0.7 if len(wenti_quyu) == 0 else 0.3)
                jg_total = self._jiuchou.calculate_total()
                if jg_total < 0.4 and self.wangluo:
                    self.wangluo.jilu_ganzhi(f"九宫健康度临界:{jg_total:.3f}", "gao")
            except Exception: pass

    def _chaoyuejing_tupo_chuangxin(self):
        """超越境·突破创新：生成进化种子"""
        if time.time() - self._zuihou_tupo < 117649: return  # 七律一纪元
        self._zuihou_tupo = time.time()
        if not self.xin or not self.xin.llm: return
        zhenduan = self.baji_zhenduan()
        # V11.0: 统一认知包
        from star_nest.protocols.cognition_package import RenzhiBao
        bao = RenzhiBao.from_xin(self.xin, "超越境") if self.xin else RenzhiBao("超越境")
        bao.shu_ju(zhenduan=str(zhenduan)[:300])
        try:
            jieguo = self.xin.llm.chat([{"role":"user","content":bao.to_json()}], wendu=0.3, zuidazifu=600)
            with self._zhongzi_suo:
                zhongzi = {"id": f"ev_{int(time.time())}", "shijian": datetime.now().isoformat(),
                           "zhaiyao": jieguo[:150], "xiangqing": jieguo[:500],
                           "mubiao_mokuai": [], "ke_huigun": "可回滚" in jieguo,
                           "fengxian": "中", "zhuangtai": "daiding"}
                self._daiding_zhongzi.append(zhongzi)
                if len(self._daiding_zhongzi) > 10: self._daiding_zhongzi = self._daiding_zhongzi[-10:]
            self._jilu_zhongzi_shengcheng(zhongzi)
        except Exception: pass

    # ========== 超越境·属性分析代理 ==========
    def chaoyuejing_shuxing(self, llm, yonghu_xiaoxi: str, gongneng_fenxi: dict,
                            jiupingmu_fenxi: dict, lishi_zhenduan: str = "") -> dict:
        if not self.chaoyuejing:
            return {
                "shuxing_wangluo": ["超越境未接入"],
                "shuxing_pipei": [],
                "chuangxin_fangan": [],
                "wendingxing_baoxian": "信息不足"
            }
        try:
            return self.chaoyuejing.chaoyuejing_shuxing(
                llm, yonghu_xiaoxi, gongneng_fenxi, jiupingmu_fenxi, lishi_zhenduan
            )
        except Exception:
            return {
                "shuxing_wangluo": ["超越境调用异常"],
                "shuxing_pipei": [],
                "chuangxin_fangan": [],
                "wendingxing_baoxian": "信息不足"
            }

    def baji_zhenduan(self):
        baogao = {"zongshu": self.wangluo.tupu.number_of_nodes(), "baji_junzhi": {}, "wenti_quyu": []}
        bajis = []
        for nid in self.wangluo.tupu.nodes():
            baji = self.wangluo.tupu.qu_baji(nid)
            if baji: bajis.append(baji)
        if not bajis: return baogao
        for ji in ["yang","yin","biao","li","han","re","xu","shi"]:
            baogao["baji_junzhi"][ji] = round(sum(b.get(ji,0.5) for b in bajis)/len(bajis), 2)
        if baogao["baji_junzhi"].get("han",0)>0.7: baogao["wenti_quyu"].append("寒高")
        if baogao["baji_junzhi"].get("shi",0)>0.7: baogao["wenti_quyu"].append("实高")
        if baogao["baji_junzhi"].get("xu",0)>0.7: baogao["wenti_quyu"].append("虚高")

        try:
            for node_id in self.wangluo.tupu.nodes():
                shuxing = self.wangluo.tupu._nodes.get(node_id, {})
                leixing = shuxing.get("leixing", "")
                biaoqian = shuxing.get("biaoqian", "")

                # 读取日巡检报告
                if leixing == "shencha_xunjian" and "日巡检" in biaoqian:
                    xiangqing = shuxing.get("xiangqing", "")
                    if "问题" in xiangqing:
                        # 巡检发现问题 → 虚高
                        baogao["baji_junzhi"]["xu"] = min(1.0, baogao["baji_junzhi"].get("xu", 0.5) + 0.1)

                # 读取紧急奏折
                if leixing == "zoushe":
                    baogao["baji_junzhi"]["shi"] = min(1.0, baogao["baji_junzhi"].get("shi", 0.5) + 0.15)
                    if "gao" in str(shuxing.get("xiangqing", "")):
                        baogao["wenti_quyu"].append("奏折高危")
        except Exception: pass

        return baogao

    @sheng_ming_hai([
        ("jiedian_kong", "无网络节点", 0),
        ("shuju_pianxie", "八极数据异常", 1),
    ])
    @sheng_ming_zuo({
        "jiedian_kong": True, "shuju_pianxie": True,
    })
    def shen_zhenduan(self):
        """
        肾·八极深度诊断(基于经络图谱+势能方程)
        
        与 EightPoleDynamics.bajizhenduan(wenti, xiufu) 不同:
        - 肾版基于网络节点状态(八极均值+问题区域)
        - 动力学版基于问题/修复列表计数
        
        实现 π-φ 折叠动力学的核心方程：
        V(Ω) = ½ Ωᵀ·K·Ω + Σ w_i·Ω_i⁴
        识别六势态并计算健康度。
        """
        baji = self.baji_zhenduan()
        if not baji.get("baji_junzhi"):
            return {"shizhi": "未知", "shiliang": None, "jiankangdu": 0.5}
        
        junzhi = baji["baji_junzhi"]
        O = [junzhi.get(k, 0.5) for k in ["yang","yin","biao","li","han","re","xu","shi"]]
        
        # 生克耦合矩阵 K（简化八维）
        K = [
            [ 1,-0.3, 0.2, 0,   0,   0.3, 0,   0  ],  # 阳
            [-0.3, 1,   0,   0.2, 0.3, 0,   0,   0  ],  # 阴
            [ 0.2, 0,   1,  -0.3, 0,   0.3, 0,   0  ],  # 表
            [ 0,   0.2,-0.3, 1,   0,   0,   0.3, 0  ],  # 里
            [ 0,   0.3, 0,   0,   1,  -0.3, 0.2, 0  ],  # 寒
            [ 0.3, 0,   0.3, 0,  -0.3, 1,   0,  -0.2],  # 热
            [ 0,   0,   0,   0.3, 0.2, 0,   1,  -0.3],  # 虚
            [ 0,   0,   0,   0,   0,  -0.2,-0.3, 1  ],  # 实
        ]
        
        # V(Ω) = ½ Ωᵀ·K·Ω + Σ 0.1·Ω_i⁴
        V = 0
        for i in range(8):
            for j in range(8):
                V += 0.5 * O[i] * K[i][j] * O[j]
            V += 0.1 * (O[i] ** 4)
        
        # 六势态识别
        if O[0] > 0.6 and O[2] > 0.5:
            shizhi = "太阳"
        elif O[5] > 0.7 and O[7] > 0.6:
            shizhi = "阳明"
        elif abs(O[2] - O[3]) < 0.2 and max(O[2], O[3]) > 0.4:
            shizhi = "少阳"
        elif O[1] > 0.5 and O[4] > 0.5 and O[6] > 0.5:
            shizhi = "太阴"
        elif O[0] < -0.3 and O[1] < -0.3:
            shizhi = "少阴"
        else:
            shizhi = "厥阴"
        
        # 健康度 = 1/(1+V) 映射到 [0,1]
        jiankangdu = round(1.0 / (1.0 + abs(V)), 3)
        
        return {
            "shizhi": shizhi,
            "shiliang": {k: O[i] for i, k in enumerate(["yang","yin","biao","li","han","re","xu","shi"])},
            "shineng": round(V, 4),
            "jiankangdu": jiankangdu,
            "wenti_quyu": baji.get("wenti_quyu", []),
        }

    def qu_daiding_zhongzi(self):
        with self._zhongzi_suo:
            return [z for z in self._daiding_zhongzi if z.get("zhuangtai")=="daiding"]

    def pizhun_zhongzi(self, zid, tg):
        with self._zhongzi_suo:
            for z in self._daiding_zhongzi:
                if z["id"]==zid: z["zhuangtai"] = "yishenpi" if tg else "yijujue"

    def execution_zhongzi(self, zid):
        with self._zhongzi_suo:
            for z in self._daiding_zhongzi:
                if z["id"]==zid:
                    z["zhuangtai"] = "yiexecution_chenggong"
                    return f"种子 {zid} 执行成功。{z.get('zhaiyao','')[:100]}"
        return f"种子 {zid} 不存在。"

    def chuangjian_beifen(self):
        try:
            from star_nest.dynamics.self_repair import ZiWoXiuFu
            xiufu = ZiWoXiuFu(self.xiangmu_mulu)
            xiufu.chuangjian_beifen()
        except Exception: pass

    def _jingxi_sikao(self):
        zhenduan = self.baji_zhenduan()
        wenti_text = ""
        if zhenduan.get("wenti_quyu"):
            for w in zhenduan["wenti_quyu"]: wenti_text += f"- {w}\n"
        try:
            shijian = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.kangfu_dangan_md, 'a', encoding='utf-8') as f:
                f.write(f"\n## {shijian} 康复诊断\n{wenti_text or '运行平稳。'}\n")
        except Exception as e:
            if self.wangluo and hasattr(self.wangluo, 'rizhi'):
                try: self.wangluo.rizhi.wenti_rizhi(self.juese, {"miaoshu": f"康复档案写入异常:{e}", "leixing": "kangfu_error"})
                except Exception: pass

    def _xie_sikao_rizhi(self, nr):
        try:
            with open(self.sikao_rizhi_md, 'a', encoding='utf-8') as f:
                f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {nr}")
        except Exception as e:
            if self.wangluo and hasattr(self.wangluo, 'rizhi'):
                try: self.wangluo.rizhi.wenti_rizhi(self.juese, {"miaoshu": f"思考日志写入异常:{e}", "leixing": "sikao_error"})
                except Exception: pass

    def qu_zouzhai(self):
        """取走债: 返回肾(诊断)相关的未解决问题"""
        zhai = []
        try:
            if self.wangluo:
                for tid in ["bianchengti","yunxingti"]:
                    for w in self.wangluo.qu_wenti_liebiao(tid):
                        ms = str(w.get("miaoshu",""))[:100]
                        if any(kw in ms for kw in ["健康","诊断","八极","baji","health","崩溃","异常"]):
                            zhai.append(f"[肾-诊断债|{tid}] {ms}")
            zhenduan = self.baji_zhenduan()
            if zhenduan.get("wenti_quyu"):
                zhai.append(f"[肾-诊断债] 当前异常区域: {','.join(zhenduan['wenti_quyu'])}")
        except Exception: pass
        return zhai

    def tingzhi(self):
        self._yunxing = False