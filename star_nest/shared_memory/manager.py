import sqlite3, json
from pathlib import Path
from datetime import datetime

class JiYiGuanLi:
    def __init__(self, jiyi_mulu):
        self.jiyi_mulu = Path(jiyi_mulu)
        self.changqi_db = self.jiyi_mulu / "changqi_jiyi.db"
        self.jineng_json = self.jiyi_mulu / "jineng_jiyi.json"
        self.jineng_maodian = []
        if self.jineng_json.exists():
            try:
                self.jineng_maodian = json.loads(self.jineng_json.read_text(encoding='utf-8'))
            except Exception:
                self.jineng_maodian = []

    def jiansuo_zhishi(self, guanjianci, zuiduo=5):
        jieguo, seen = [], set()
        if not self.changqi_db.exists():
            return jieguo
        try:
            conn = sqlite3.connect(str(self.changqi_db))
            conn.text_factory = str
            c = conn.cursor()
            ciku = list(guanjianci.split())
            # CJK ngram fallback
            if len(ciku) == 1 and not any(ci.isascii() and ci.isalpha() for ci in ciku):
                token = ciku[0]
                if len(token) >= 2:
                    for i in range(len(token)-1):
                        ng = token[i:i+2]
                        if any('\u4e00' <= ch <= '\u9fff' for ch in ng):
                            ciku.append(ng)
            for ci in ciku:
                ci = ci.strip()
                if not ci or (len(ci) == 1 and ci.isascii()):
                    continue
                rows = c.execute(
                    "SELECT biaoti, hexinyuanli FROM zhishi_yuanli WHERE biaoti LIKE ? OR hexinyuanli LIKE ?",
                    ("%" + ci + "%", "%" + ci + "%")
                ).fetchall()
                for r in rows:
                    key = r[0]
                    if key not in seen:
                        seen.add(key)
                        he = (r[1] or "")[:300]
                        # 提取要点：按行取前3条非空行
                        points = [l.strip() for l in he.split('\n') if l.strip()][:3]
                        if not points: points = [he[:100]]
                        jieguo.append({"biaoti": r[0], "yao_dian": points})
            conn.close()
            return jieguo[:zuiduo]
        except Exception:
            return jieguo

    def jiansuo_jineng(self, guanjianci):
        jg = []
        for md in self.jineng_maodian:
            if guanjianci in md.get("name", "") or guanjianci in md.get("detail", "") or guanjianci in md.get("compression_key", ""):
                jg.append(md)
        return jg

    def ronghe_jiansuo(self, query, zuiduo=8):
        """返回结构化记忆字典, 与LLM通信格式同构"""
        zhishi = self.jiansuo_zhishi(query, zuiduo)[:5]
        jineng = self.jiansuo_jineng(query)[:3]
        fenlei = self.zhishi_fenlei()
        tongji = self.zhishi_tongji()
        return {
            "zhishi": zhishi,
            "jineng": jineng,
            "fenlei": fenlei,
            "zongshu": tongji.get("zongshu", 0)
        }

    def _panduan_cengji(self, query: str) -> str:
        """从提问推断当前五境(表观遗传信号)"""
        zj = ["什么是","是什么","定义","介绍","概念","框架","结构","架构","有哪些","是谁","叫什么"]
        fj = ["为什么","原因","阻碍","分析","不够","错误","失败","缺失","问题","瓶颈","限制","没找到","崩溃","异常"]
        cy = ["还有","更好","创新","突破","跨","超越","能否","能不能","极限","替代","超越"]
        hj = ["怎么解决","如何做","方案","方法","工具","修复","优化","改进","实现","生成","锻造","怎么","如何"]
        if any(k in query for k in zj): return "正境"
        if any(k in query for k in fj): return "反境"
        if any(k in query for k in cy): return "超越境"
        if any(k in query for k in hj): return "合境"
        return "正境"

    def organs_ronghe_jiansuo(self, query, zuiduo=8):
        """五脏五境表观遗传检索: 按当前境偏置各脏记忆"""
        cengji = self._panduan_cengji(query)
        # 按境的关键词偏置(组蛋白标记)
        pianzhi = {
            "正境": ["定义","概念","框架","体系","结构","模型","原理"],
            "反境": ["阻碍","因果","诊断","错误","失败","缺失","瓶颈","限制"],
            "合境": ["方案","工具","方法","修复","解决","实现","操作"],
            "超越境": ["创新","突破","跨域","极限","边界","超越","属性"],
            "本源境": ["归档","记录","成功","验证","基线","经验","总结"],
        }
        pian_ci = pianzhi.get(cengji, [])
        
        # 检索全量知识
        zhishi = self.jiansuo_zhishi(query, zuiduo)[:5]
        
        # 按境偏置重排(境相关词多的排前面)
        def de_fen(z):
            title = z.get("biaoti","")
            return sum(1 for w in pian_ci if w in title)
        zhishi.sort(key=de_fen, reverse=True)
        
        # 分配到四脏(按标题关键词)
        gan_zhishi = [z for z in zhishi if any(k in z.get("biaoti","") for k in ["概念","定义","知识","理论","中医","哲学","科学","数学","物理"])][:3]
        pi_zhishi = [z for z in zhishi if any(k in z.get("biaoti","") for k in ["工具","兵器","匹配","锻造","藏剑阁","铸剑炉","方法"])][:3]
        fei_zhishi = [z for z in zhishi if any(k in z.get("biaoti","") for k in ["审查","巡检","场景","配置","偏好","审计"])][:3]
        shen_zhishi = [z for z in zhishi if any(k in z.get("biaoti","") for k in ["诊断","健康","进化","八极","修复","平衡","种子"])][:3]
        
        # 未分配的归入肝
        used = set(z["biaoti"] for z in gan_zhishi + pi_zhishi + fei_zhishi + shen_zhishi)
        for z in zhishi:
            if z["biaoti"] not in used and len(gan_zhishi) < 5:
                gan_zhishi.append(z)
        
        jineng = self.jiansuo_jineng(query)[:2]
        fenlei = self.zhishi_fenlei()
        tongji = self.zhishi_tongji()
        return {
            "cengji": cengji,
            "gan": gan_zhishi,
            "pi": pi_zhishi,
            "fei": fei_zhishi,
            "shen": shen_zhishi,
            "jineng": jineng,
            "fenlei": fenlei,
            "zongshu": tongji.get("zongshu", 0)
        }

    def zhe_die_jiansuo(self, cengji="正境", chaxun=""):
        """数字谱系位点检索: 按五境激活对应位点,六十四卦Hamming共振排序
        chaxun: 可选查询文本, 检测"近期"/"最近"→混合时间排序
        """
        jihuo_map = {
            "正境": [1, 2, 3],
            "反境": [5, 6, 8],
            "合境": [4, 5, 9],
            "超越境": [0, 7],
            "本源境": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        }
        weizhi_liebiao = jihuo_map.get(cengji, [1, 2, 3])
        jieguo = {"cengji": cengji, "weizhi": {}, "zongshu": 0}
        zong = 0
        shijian_jiaquan = any(k in chaxun for k in ["近期", "最近", "最新", "刚", "刚刚", "近来"])

        # 当前五境状态向量 (64位)
        zhuangtai = self._shengcheng_zhuangtai(cengji)

        for w in weizhi_liebiao:
            fp = self.jiyi_mulu / "puxi" / f"{w}.json"
            if fp.exists():
                try:
                    data = json.loads(fp.read_text(encoding='utf-8'))
                    items = data.get("zhe_die", [])
                    # 计算Hamming距离,按距离+权重排序
                    for entry in items:
                        qm = entry.get("qianming", "0"*64)
                        qz = entry.get("quanzhong", 1.0)
                        entry["_hamming"] = self._hamming_juli(zhuangtai, qm)
                        entry["_zonghe"] = entry["_hamming"] / max(qz, 0.01)
                        # 时间权重: 近期条目提升排序
                        cjsj = entry.get("chuangjian_shijian", "")
                        if shijian_jiaquan and cjsj:
                            try:
                                from datetime import datetime as _dt
                                age = (_dt.now() - _dt.fromisoformat(cjsj)).total_seconds()
                                if age < 86400: entry["_zonghe"] *= 0.3   # 24h内大幅提升
                                elif age < 604800: entry["_zonghe"] *= 0.6  # 一周内提升
                            except: pass
                    items.sort(key=lambda e: e.get("_zonghe", 32))
                    # 衰减非选中记忆的权重
                    for entry in items[5:]:
                        entry["quanzhong"] = max(0.01, entry.get("quanzhong", 1.0) * 0.995)
                    # 按五脏分组
                    gan_items = []; pi_items = []; fei_items = []; shen_items = []
                    for entry in items[:5]:
                        zang = self._fenlei_organs(entry.get("biaoti",""))
                        if zang == "pi":   pi_items.append(entry)
                        elif zang == "fei": fei_items.append(entry)
                        elif zang == "shen": shen_items.append(entry)
                        else: gan_items.append(entry)
                    jieguo["weizhi"][str(w)] = {
                        "miaoshu": data.get("miaoshu", ""),
                        "shuliang": len(items),
                        "gan": gan_items[:3], "pi": pi_items[:2],
                        "fei": fei_items[:2], "shen": shen_items[:2]
                    }
                    zong += len(items)
                    # 持久化·权重写回位点文件
                    for entry in items:
                        entry.pop("_hamming", None)
                        entry.pop("_zonghe", None)
                    fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
                except: pass
        jieguo["zongshu"] = zong
        return jieguo

    def _shengcheng_zhuangtai(self, cengji):
        """生成当前五境的状态向量(64位)"""
        bits = ['0'] * 64
        # 激活当前境对应的位点标志
        jihuo_map = {"正境": [1,2,3], "反境": [5,6,8], "合境": [4,5,9], "超越境": [0,7], "本源境": [0,1,2,3,4,5,6,7,8,9]}
        for w in jihuo_map.get(cengji, [1,2,3]):
            if 0 <= w <= 9: bits[w] = '1'
        # cengji名称哈希填充
        h = hash(cengji) & 0xFFFFFF
        for i in range(40, 64):
            if h & (1 << (i - 40)): bits[i] = '1'
        return ''.join(bits)

    def _hamming_juli(self, a, b):
        """64位Hamming距离"""
        return sum(1 for i in range(64) if a[i] != b[i])

    def _fenlei_organs(self, title):
        """按标题关键词判定归属脏"""
        title_lower = title.lower()
        pi_kw  = ["工具","兵器","匹配","锻造","铸剑炉","藏剑阁","方法","技能","应用","实现","操作"]
        fei_kw = ["审查","巡检","场景","配置","偏好","审计","感知","环境","气氛","风格"]
        shen_kw = ["诊断","健康","进化","八极","修复","平衡","种子","态势","意志"]
        if any(k in title for k in pi_kw):  return "pi"
        if any(k in title for k in fei_kw): return "fei"
        if any(k in title for k in shen_kw): return "shen"
        return "gan"  # 默认知识归肝

    def zidong_bianma(self, biaoti, neirong=""):
        """新知识自动编码: LLM判定位点→生成签名→写入位点文件"""
        import random
        try:
            from star_nest.protocols.cognition_package import RenzhiBao
            bao = RenzhiBao("本源境")
            bao.shu_ju(puxi_dingyi="0:无极|1:太极|2:阴阳|3:三才|4:四象|5:五行|6:六经|7:七律|8:八纲|9:九畴",
                       biaoti=biaoti[:60], neirong=neirong[:200])
            from star_nest.entry import SanTiXiTong
            llm = SanTiXiTong().llm
            resp = llm.chat([{'role':'user','content':bao.to_json()}], wendu=0.05, zuidazifu=10) if llm and llm.api_key else "5"
            nums = [int(ch) for ch in resp if ch.isdigit()]
            nums = list(set(nums))[:3]
            if not nums: nums = [5]
        except:
            nums = [5]
        
        # 生成64位签名
        bits = ['0'] * 64
        for w in nums:
            if 0 <= w <= 9: bits[w] = '1'
        h = hash(biaoti) & 0x3FFFFFF
        for i in range(10, 36):
            if h & (1 << (i - 10)): bits[i] = '1'
        random.seed(biaoti)
        for i in range(36, 64):
            if random.random() > 0.5: bits[i] = '1'
        qianming = ''.join(bits)
        
        # 构造条目并写入位点
        entry = {"biaoti": biaoti, "lingyu": "", "yao_dian": (neirong or "")[:200].split('\n')[:2],
                 "qianming": qianming, "quanzhong": 1.0, "chuangjian_shijian": datetime.now().isoformat()}
        for n in nums:
            if 0 <= n <= 9:
                fp = self.jiyi_mulu / "puxi" / f"{n}.json"
                if fp.exists():
                    data = json.loads(fp.read_text(encoding='utf-8'))
                    data['zhe_die'].append(entry)
                    fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        return nums

    def touwei(self, msg: str):
        """知识投喂: 从消息中提取标题+内容→自动编码到数字谱系"""
        lines = msg.strip().split('\n')
        biaoti = lines[0].strip()[:80] if lines else ""
        neirong = '\n'.join(lines[1:])[:500] if len(lines) > 1 else ""
        if not biaoti:
            return {"success": False, "error": "标题不能为空"}
        nums = self.zidong_bianma(biaoti, neirong)
        return {"success": True, "output": f"知识已编码到位点:{','.join(str(n) for n in nums)}",
                "biaoti": biaoti, "weizhi": nums}


    def zhishi_fenlei(self):
        """知识分类统计: {领域: 条数}"""
        jieguo = {}
        if not self.changqi_db.exists():
            return jieguo
        try:
            import sqlite3, re
            conn = sqlite3.connect(str(self.changqi_db))
            conn.text_factory = str
            rows = conn.execute("SELECT biaoti FROM zhishi_yuanli").fetchall()
            for r in rows:
                t = r[0]
                # 提取领域前缀（·或：前）
                cat = "其他"
                for sep in ["·", "：", ":"]:
                    if sep in t:
                        cat = t.split(sep)[0].strip()
                        if len(cat) > 10: cat = cat[:8]
                        break
                if cat == "星巢": cat = "星巢"
                # 合并子类到大类 (关键词匹配,不依赖精确前缀)
                zhyl = {"中医":["中医","药","本草","医案","医经","方剂","针灸","药剂","伤寒","金匮","温病","黄帝","神农"],
                        "自然科学":["数学","物理","化学","生物","力学","量子","电磁","有机"],
                        "计算机":["计算机","编程","算法","数据","网络","软件","AI","人工智","机器学","深度学","强化"],
                        "人文社科":["哲学","心理","经济","法律","政治","历史","军事","美学","逻辑","伦理"]}
                for dalei, keys in zhyl.items():
                    if any(k in cat for k in keys):
                        cat = dalei
                        break
                jieguo[cat] = jieguo.get(cat, 0) + 1
            conn.close()
        except: pass
        return jieguo

    def zhishi_tongji(self):
        tj = {"zongshu": 0, "jineng_shu": len(self.jineng_maodian)}
        if self.changqi_db.exists():
            try:
                conn = sqlite3.connect(str(self.changqi_db))
                conn.text_factory = str
                tj["zongshu"] = conn.execute("SELECT COUNT(*) FROM zhishi_yuanli").fetchone()[0]
                conn.close()
            except Exception:
                pass
        return tj

    def beifen_jiyi(self, beifen_mulu):
        Path(beifen_mulu).mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        for src in [self.changqi_db, self.jineng_json]:
            if src.exists():
                dst = Path(beifen_mulu) / (src.stem + "_" + ts + src.suffix)
                dst.write_bytes(src.read_bytes())