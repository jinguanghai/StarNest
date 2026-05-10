"""
经络·三体 OpenCode 路由器 V1.0
运行体(9527) ──问题上报──→ 编程体(9528) ──锻造完成──→ 复制体(9529)
                                                             │
                                                    验证结果回传
纯Python stdlib·零外部依赖
"""
import json, time, threading, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime

JINGLUO_ZHUANGTAI = Path(__file__).parent / 'santi_meridian.json'
SAN_TI = {
    'yunxingti': {'port': 9527, 'url': 'http://localhost:9527/v1/chat/completions'},
    'bianchengti': {'port': 9528, 'url': 'http://localhost:9528/v1/chat/completions'},
    'fuzhiti': {'port': 9529, 'url': 'http://localhost:9529/v1/chat/completions'},
}


class SanTiRouter:
    def __init__(self):
        self.zhuangtai = self._du_zhuangtai()
        self.wenti_duilie = []
        self.xiufu_duilie = []
        self._yunxing = True

    def _du_zhuangtai(self):
        if JINGLUO_ZHUANGTAI.exists():
            try: return json.loads(JINGLUO_ZHUANGTAI.read_text(encoding='utf-8'))
            except: pass
        return {"xin_tiao": {}, "wenti": [], "xiufu": [], "zuihou_lianjie": {}}

    def _cun_zhuangtai(self):
        self.zhuangtai["baocun_shijian"] = datetime.now().isoformat()
        JINGLUO_ZHUANGTAI.write_text(json.dumps(self.zhuangtai, ensure_ascii=False, indent=2), encoding='utf-8')

    def _chaxun_jiankang(self, ti):
        """检查一体是否存活"""
        try:
            req = urllib.request.Request(f"http://localhost:{SAN_TI[ti]['port']}/v1/models")
            resp = urllib.request.urlopen(req, timeout=2)
            data = json.loads(resp.read().decode())
            self.zhuangtai["zuihou_lianjie"][ti] = datetime.now().isoformat()
            return data.get('id', '').startswith('xingchao')
        except:
            return False

    def wenti_shangbao(self, ti, wenti):
        """运行体问题上报到编程体"""
        wenti_xiang = {
            "shijian": datetime.now().isoformat(),
            "laiyuan": ti,
            "miaoshu": str(wenti)[:300],
            "leixing": "santi_wenti"
        }
        self.zhuangtai.setdefault("wenti", []).append(wenti_xiang)
        self._cun_zhuangtai()
        # 发送到编程体
        try:
            self._fasong_xiaoxi('bianchengti', f"[经络路由|{ti}上报] {wenti[:200]}")
        except: pass

    def _fasong_xiaoxi(self, ti, msg):
        """向一体发送消息"""
        data = json.dumps({
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": msg}],
            "max_tokens": 100
        }).encode('utf-8')
        req = urllib.request.Request(
            SAN_TI[ti]['url'],
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=30)

    def jiancha_quanbu(self):
        """三体检康诊断"""
        jieguo = {}
        for ti in SAN_TI:
            jieguo[ti] = self._chaxun_jiankang(ti)
        self.zhuangtai["xin_tiao"] = {ti: datetime.now().isoformat() for ti in SAN_TI}
        self._cun_zhuangtai()
        return jieguo

    def san_ti_zhuang_tai(self):
        return {
            "santi": SAN_TI,
            "jiankang": self.jiancha_quanbu(),
            "wenti_shu": len(self.zhuangtai.get("wenti", [])),
            "tongxin": self.zhuangtai.get("zuihou_lianjie", {}),
        }
