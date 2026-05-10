"""
LLM客户端 V2.0
双引擎热备容灾·SSL证书降级·结构化JSON(零提示词)
纯标准库·零外部依赖·线程安全
"""
import json, ssl, urllib.request, urllib.error, threading, time

class LLMKeHuDuan:
    def __init__(self, deepseek_key, moxing="deepseek-chat", huoshan_key=None, huoshan_moxing="doubao-pro-32k"):
        self.deepseek_key = deepseek_key
        self.huoshan_key = huoshan_key
        self.deepseek_model = moxing
        self.huoshan_model = huoshan_moxing
        self.suo = threading.Lock()
        self.zhong_engine = True
        self.lianxu_shibai = 0
        self.max_shibai = 5
        self.xintiao_jishi = time.time()
        self.xintiao_jiange = 343
        try:
            self.ssl_ctx = ssl.create_default_context()
        except Exception:
            self.ssl_ctx = None
        # 兼容旧接口
        self.api_key = deepseek_key
        self.moxing = moxing
        self.houbu_key = huoshan_key
        self.houbu_moxing = huoshan_moxing

    def chat(self, xiaoxi_liebiao, wendu=0.7, zuidazifu=2000):
        self.xintiao_jiance()
        if self.lianxu_shibai >= self.max_shibai:
            return ""
        shuju = {"model": self.deepseek_model, "messages": xiaoxi_liebiao,
                 "temperature": wendu, "max_tokens": zuidazifu}
        # deepseek-v4-pro 特有参数: 推理增强 + thinking模式
        if self.deepseek_model == "deepseek-v4-pro":
            shuju["reasoning_effort"] = "high"
            shuju["extra_body"] = {"thinking": {"type": "enabled"}}
        with self.suo:
            try:
                jieguo = self._fasong("https://api.deepseek.com/v1/chat/completions",
                                      shuju, self.deepseek_key)
                if jieguo:
                    self.lianxu_shibai = 0
                    self.zhong_engine = True
                    return jieguo
                self.lianxu_shibai += 1
            except Exception:
                self.lianxu_shibai += 1
            if self.huoshan_key:
                try:
                    shuju["model"] = self.huoshan_model
                    jieguo = self._fasong("https://ark.cn-beijing.volces.com/api/v3/chat/completions",
                                          shuju, self.huoshan_key)
                    if jieguo:
                        self.lianxu_shibai = 0
                        self.zhong_engine = False
                        return jieguo
                    self.lianxu_shibai += 1
                except Exception:
                    self.lianxu_shibai += 1
        return ""

    def _fasong(self, dizhi, shuju, key):
        data = json.dumps(shuju, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(dizhi, data=data, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"}, method="POST")
        try:
            if self.ssl_ctx:
                resp = urllib.request.urlopen(req, timeout=49, context=self.ssl_ctx)
            else:
                resp = urllib.request.urlopen(req, timeout=49)
            result = json.loads(resp.read().decode('utf-8'))
            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"]["content"]
        except (ssl.SSLError, urllib.error.URLError):
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                resp = urllib.request.urlopen(req, timeout=49, context=ctx)
                result = json.loads(resp.read().decode('utf-8'))
                if "choices" in result and result["choices"]:
                    return result["choices"][0]["message"]["content"]
            except Exception:
                pass
        except Exception:
            pass
        return ""

    def chat_code(self, xiaoxi_liebiao, wendu=0.2):
        return self.chat(xiaoxi_liebiao, wendu=wendu, zuidazifu=4000)

    def goujian_jiegouhua_shuju(self, renwu, shenfen, jiyi, yonghu_xiaoxi, yaoqiu):
        # 结构化记忆格式: dict → 紧凑JSON
        if isinstance(jiyi, dict):
            parts = []
            cj = jiyi.get("cengji", "")
            yx = jiyi.get("yunxing_zhuangtai", "")
            zs = jiyi.get("zongshu", 0)
            if cj: parts.append(f"当前:{cj}")
            if yx: parts.append(yx)
            # 位点格式(新·五脏分组) 或 五脏格式 或 旧zhishi格式
            if "weizhi" in jiyi:
                for w_str, info in jiyi.get("weizhi", {}).items():
                    miaoshu = info.get('miaoshu','')
                    # 新格式: 五脏分组
                    has_gan = info.get("gan", [])
                    has_pi  = info.get("pi", [])
                    has_fei = info.get("fei", [])
                    has_shen = info.get("shen", [])
                    if has_gan or has_pi or has_fei or has_shen:
                        for zang_items, label in [(has_gan,"肝"),(has_pi,"脾"),(has_fei,"肺"),(has_shen,"肾")]:
                            if zang_items:
                                pts = [z.get("biaoti","")[:25] for z in zang_items[:1]]
                                parts.append(f"[位点{w_str}:{label}] " + " | ".join(pts))
                    else:
                        zs_list = info.get("zhishi", [])[:2]
                        if zs_list:
                            pts = [z.get("biaoti","")[:30] for z in zs_list]
                            parts.append(f"[位点{w_str}] " + " | ".join(pts))
                parts.append(f"共{zs}条折叠记忆")
            elif "gan" in jiyi:
                for zang, label in [("gan","肝"),("pi","脾"),("fei","肺"),("shen","肾")]:
                    items = jiyi.get(zang, [])[:2]
                    if items:
                        pts = []
                        for z in items:
                            pts.append(z.get("biaoti","")[:30] + ": " + " ".join(z.get("yao_dian",[])[:1])[:80])
                        parts.append(f"[{label}] " + " | ".join(pts))
            elif "zhishi" in jiyi:
                zhishi = jiyi.get("zhishi", [])[:3]
                for z in zhishi:
                    points = z.get("yao_dian", [])[:2]
                    parts.append(f"[{z.get('biaoti','')[:40]}] " + " ".join(points)[:120])
            jiyi_str = " | ".join(parts)[:800]
        else:
            jiyi_str = (str(jiyi or ""))[:800]
        return [{"role": "user", "content": json.dumps({
            "renwu": renwu, "shenfen": shenfen,
            "jiyi": jiyi_str,
            "yonghu_xiaoxi": yonghu_xiaoxi, "yaoqiu": yaoqiu
        }, ensure_ascii=False)}]

    def xintiao_jiance(self):
        if time.time() - self.xintiao_jishi > self.xintiao_jiange:
            self.zhong_engine = True
            self.lianxu_shibai = 0
            self.xintiao_jishi = time.time()
