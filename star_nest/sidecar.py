"""
星巢侧车 V1.2 — 替换OpenCode Rust侧车·三体多角色·基础防护
用法:
  python xingchao_sidecar.py                          # 默认9527·运行体
  python xingchao_sidecar.py --port 9528 --role bianchengti
  python xingchao_sidecar.py --port 9529 --role fuzhiti
兼容: OpenAI /v1/chat/completions + /v1/models
"""
import http.server, json, sys, os, threading, time, argparse, socket
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=9527, help='端口 (默认9527)')
parser.add_argument('--role', type=str, default='yunxingti', choices=['yunxingti','bianchengti','fuzhiti'])
parser.add_argument('--api-key', type=str, default='', help='API密钥 (可选, 设置后需X-API-Key头)')
args = parser.parse_args()

PORT = args.port
ROLE = args.role
API_KEY = os.environ.get('XINGCHAO_API_KEY', args.api_key)
MAX_BODY = 100_000  # 100KB 请求体上限
REPLY_TIMEOUT = 30  # 等待回复超时(秒)

try:
    from star_nest.entry import SanTiXiTong
    from star_nest.meridian.trinity_router import SanTiRouter
    s = SanTiXiTong()
    santi_router = SanTiRouter()
except Exception as e:
    print(f'[!!] 系统初始化失败: {e}')
    sys.exit(1)

# 按角色启动不同三体组件
_start_failed = []
when = {'yunxingti':[s.bianchengti,s.yunxingti],'bianchengti':[s.bianchengti,s.yunxingti],'fuzhiti':[s.fuzhiti]}
for body in when.get(ROLE, []):
    try: body.start_all()
    except Exception as e:
        _start_failed.append(str(e))
        print(f'[!!] body start failed: {e}')
time.sleep(5)
_healthy = len(_start_failed) == 0

# 角色权限控制
ROLE_XIANZHI = {
    'yunxingti': {'ke_xieru': False, 'moshi': 'plan'},
    'bianchengti': {'ke_xieru': True, 'moshi': 'build'},
    'fuzhiti': {'ke_xieru': False, 'moshi': 'plan'},
}

def xingchao_chuli(msg):
    """走星巢五境认知流处理消息·按角色路由"""
    xz = ROLE_XIANZHI[ROLE]
    
    # 复制体: 沙箱模式, 不执行写操作
    if ROLE == 'fuzhiti':
        return f"[复制体·沙箱] 收到消息长度:{len(msg)}, 仅验证不执行"
    
    # 运行体/编程体: 正常五境认知流
    for q in [s.yunxingti.xin.shuchu_duilie, s.bianchengti.xin.shuchu_duilie]:
        while not q.empty():
            try: q.get_nowait()
            except Exception: pass
    
    if xz['ke_xieru']:
        s.bianchengti.xin.add_xuqiu(msg)
    else:
        s.yunxingti.xin.add_xuqiu(msg)
    
    for _ in range(int(REPLY_TIMEOUT * 2)):
        time.sleep(0.5)
        for q in [s.yunxingti.xin.shuchu_duilie, s.bianchengti.xin.shuchu_duilie]:
            try:
                reply = q.get_nowait()
                if reply: return str(reply)[:3000]
            except Exception: pass
    return f"[{ROLE}] 处理超时"

class SidecarHandler(http.server.BaseHTTPRequestHandler):
    timeout = 30  # socket 超时

    def do_GET(self):
        jk = {}
        try: jk = santi_router.san_ti_zhuang_tai()
        except Exception: pass
        # 穹顶监控数据: 八极/π-φ/记忆/势态
        telemetry = {}
        try:
            xin = s.yunxingti.xin
            bz = xin.baji.bajizhenduan(
                s.meridian.qu_wenti_liebiao('yunxingti'),
                s.meridian.qu_xiufu_lishi('yunxingti'))
            telemetry['jiankangdu'] = bz.get('jiankangdu', 0.5)
            telemetry['shizhi'] = bz.get('shizhi', '少阳')
            telemetry['baji'] = bz.get('shiliang', {})
        except: pass
        try:
            if xin._piphicycle:
                ps = xin._piphicycle.get_state()
                telemetry['piphicycle'] = {'pi_energy': ps.get('pi_energy',0.5), 'phi_energy': ps.get('phi_energy',0.5), 'entropy': ps.get('entropy',0.5)}
        except: pass
        try:
            tj = s.jiyiguanli.zhishi_tongji()
            telemetry['jiyi_tiaoshu'] = tj.get('zongshu', 0)
        except: pass
        resp = {"id": f"xingchao-{ROLE}", "object": "list", "data": [
            {"id": "deepseek-chat", "object": "model", "owned_by": f"xingchao-{ROLE}"}
        ], "santi": jk.get("santi", {}), "jiankang": jk.get("jiankang", {}),
           "wenti_shu": jk.get("wenti_shu", 0), "startup_ok": _healthy, **telemetry}
        self._send(resp)

    def do_POST(self):
        try:
            cl = int(self.headers.get('Content-Length', 0))
            if cl > MAX_BODY:
                self._send_err(413, "Request body too large")
                return
            if API_KEY and self.headers.get('X-API-Key', '') != API_KEY:
                self._send_err(401, "Invalid API key")
                return
            body = json.loads(self.rfile.read(cl))
            msg = body.get('messages', [{}])[-1].get('content', '')
            model = body.get('model', 'deepseek-chat')
            reply = xingchao_chuli(msg)
            resp = {
                "id": f"xingchao-{ROLE}", "object": "chat.completion", "model": model,
                "choices": [{"index": 0, "message": {"role": "assistant", "content": reply}, "finish_reason": "stop"}]
            }
            self._send(resp)
        except json.JSONDecodeError:
            self._send_err(400, "Invalid JSON body")
        except Exception as e:
            self._send_err(500, f"Internal error: {e}")

    def _send_err(self, code, msg):
        try:
            self.send_response(code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"error": msg}).encode('utf-8'))
        except Exception:
            pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-API-Key')
        self.end_headers()

    def _send(self, data):
        try:
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(body)
            self.wfile.flush()
        except Exception as e:
            try:
                self.send_response(500)
                self.end_headers()
            except Exception:
                pass

    def log_message(self, format, *args):
        pass

print(f"星巢侧车·{ROLE}启动 → http://localhost:{PORT}")
httpd = http.server.HTTPServer(('127.0.0.1', PORT), SidecarHandler)
httpd.serve_forever()
