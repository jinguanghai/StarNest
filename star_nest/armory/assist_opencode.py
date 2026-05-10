"""
藏剑阁·铸OpenCode工具 V1.1
星巢通过铸剑炉读写OpenCode配置·数据库·设置 + 记忆对齐
纯Python stdlib·零外部依赖
"""
import json, sqlite3, os, shutil, time, hashlib
from pathlib import Path
from datetime import datetime

OPENCODE_DIR = Path(r'C:\Users\jin\.local\share\opencode')
CONFIG_DIR = Path(r'C:\Users\jin\.config\opencode')
AUTH = OPENCODE_DIR / 'auth.json'
DB = OPENCODE_DIR / 'opencode.db'
CONFIG = CONFIG_DIR / 'package.json'

# 记忆对齐状态文件
DUIQI_ZHUANGTAI_FILE = Path(__file__).parent.parent / 'shared_memory' / 'duiqi_zhuangtai.json'

def duqu_auth(canshu=""):
    """读取OpenCode API认证配置"""
    if not AUTH.exists():
        return {"success": False, "error": "auth.json不存在"}
    try:
        data = json.loads(AUTH.read_text(encoding='utf-8'))
        return {"success": True, "output": json.dumps(data, ensure_ascii=False, indent=2), "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def xieru_auth(canshu):
    """修改OpenCode API认证配置·参数:JSON{provider:{key,url,type}}"""
    try:
        d = json.loads(str(canshu)) if canshu.startswith("{") else {"deepseek": {"type": "api", "key": str(canshu)}}
        # 备份
        if AUTH.exists():
            shutil.copy2(AUTH, str(AUTH) + ".backup")
        AUTH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        return {"success": True, "output": f"auth.json已更新"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def duqu_db(canshu=""):
    """查询OpenCode数据库·参数:SQL语句"""
    if not DB.exists():
        return {"success": False, "error": "opencode.db不存在"}
    try:
        query = str(canshu).strip() if canshu else "SELECT name FROM sqlite_master WHERE type='table'"
        conn = sqlite3.connect(str(DB))
        conn.text_factory = str
        rows = conn.execute(query).fetchall()[:20]
        conn.close()
        return {"success": True, "output": json.dumps([list(r) for r in rows], ensure_ascii=False)[:2000], "data": [list(r) for r in rows]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def xieru_db(canshu):
    """执行OpenCode数据库写操作·参数:SQL语句"""
    if not DB.exists():
        return {"success": False, "error": "opencode.db不存在"}
    try:
        query = str(canshu).strip()
        if not query.upper().startswith(("UPDATE", "INSERT", "DELETE", "CREATE", "ALTER")):
            return {"success": False, "error": f"仅允许写操作SQL: {query[:30]}"}
        # 备份
        shutil.copy2(DB, str(DB) + ".backup")
        conn = sqlite3.connect(str(DB))
        conn.execute(query)
        conn.commit()
        conn.close()
        return {"success": True, "output": f"SQL执行成功"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def zhuangtai(canshu=""):
    """OpenCode综合状态·配置摘要"""
    status = {}
    # auth
    if AUTH.exists():
        try:
            auth = json.loads(AUTH.read_text(encoding='utf-8'))
            for provider, info in auth.items():
                key_prefix = info.get("key", "")[:8]
                url = info.get("url", "默认")
                status[f"auth.{provider}"] = f"类型:{info.get('type','?')} key:{key_prefix}... url:{url}"
        except: status["auth"] = "读取失败"
    # db
    if DB.exists():
        status["db"] = f"大小:{DB.stat().st_size}字节, {Path(DB).stat().st_size//1024//1024}MB"
    # config
    if CONFIG.exists():
        try: status["config"] = CONFIG.read_text(encoding='utf-8')[:200]
        except: status["config"] = "读取失败"
    return {"success": True, "output": json.dumps(status, ensure_ascii=False, indent=2), "data": status}

# ===== 记忆对齐 V1.0 =====

def _lianjie_db():
    if not DB.exists():
        return None
    conn = sqlite3.connect(str(DB))
    conn.text_factory = str
    return conn

def _jiequ_wenben(text, zuiduo=200):
    t = (text or "").replace('\n', ' ').replace('\r', '')
    return t[:zuiduo]

def duqu_zuijin_duihua(session_id=None):
    """读取OpenCode会话: 返回{slug, title, wenben, shijian}"""
    conn = _lianjie_db()
    if not conn:
        return {"success": False, "error": "opencode.db不存在"}
    try:
        if session_id:
            sess = conn.execute("SELECT id, slug, title, time_created FROM session WHERE id=?", (session_id,)).fetchone()
        else:
            sess = conn.execute("SELECT id, slug, title, time_created FROM session ORDER BY time_created DESC LIMIT 1").fetchone()
        if not sess:
            conn.close(); return {"success": False, "error": "无会话"}
        sid, slug, title, ts = sess
        # 提取text类型part
        parts = conn.execute(
            "SELECT data FROM part WHERE session_id=? AND json_extract(data, '$.type')='text' ORDER BY time_created LIMIT 20",
            (sid,)).fetchall()
        texts = []
        for p in parts:
            try:
                d = json.loads(p[0])
                t = (d.get("text") or "").strip()
                if t: texts.append(_jiequ_wenben(t, 200))
            except: pass
        conn.close()
        return {"success": True, "slug": slug, "title": title or slug,
                "shijian": ts, "wenben_shu": len(texts), "wenben": texts[:10]}
    except Exception as e:
        try: conn.close()
        except: pass
        return {"success": False, "error": str(e)}

def duqu_suoyou_huihua():
    """读取所有OpenCode会话摘要"""
    conn = _lianjie_db()
    if not conn:
        return {"success": False, "error": "opencode.db不存在"}
    try:
        sessions = conn.execute("SELECT id, slug, title, time_created FROM session ORDER BY time_created DESC").fetchall()
        jieguo = []
        for sid, slug, title, ts in sessions:
            cnt = conn.execute("SELECT COUNT(*) FROM part WHERE session_id=? AND json_extract(data, '$.type')='text'",
                              (sid,)).fetchone()[0]
            jieguo.append({"id": sid[:16], "slug": slug, "title": title or slug, "shijian": ts, "wenben_shu": cnt})
        conn.close()
        return {"success": True, "huihua_shu": len(jieguo), "huihua": jieguo}
    except Exception as e:
        try: conn.close()
        except: pass
        return {"success": False, "error": str(e)}

def _qu_duiqi_zhuangtai():
    if DUIQI_ZHUANGTAI_FILE.exists():
        try: return json.loads(DUIQI_ZHUANGTAI_FILE.read_text(encoding='utf-8'))
        except: pass
    return {"zuihou_duiqi": "", "yidaoru_sessions": [], "zongshu": 0}

def _cun_duiqi_zhuangtai(zhuangtai):
    DUIQI_ZHUANGTAI_FILE.write_text(json.dumps(zhuangtai, ensure_ascii=False, indent=2), encoding='utf-8')

def _shengcheng_qianming_duiqi(biaoti, laiyuan="opencode"):
    bits = ['0'] * 64
    h = hash(biaoti) & 0x3FFFFFF
    for i in range(10, 36):
        if h & (1 << (i - 10)): bits[i] = '1'
    import random; random.seed(biaoti + laiyuan)
    for i in range(36, 64):
        if random.random() > 0.5: bits[i] = '1'
    return ''.join(bits)

def duiqi_jiyi(canshu=""):
    """记忆对齐主函数: OpenCode会话→星巢puxi知识条目"""
    if not DB.exists():
        return {"success": False, "error": "opencode.db不存在"}

    puxi_dir = Path(__file__).parent.parent / 'shared_memory' / 'puxi'
    zhuangtai = _qu_duiqi_zhuangtai()
    yidaoru = set(zhuangtai.get("yidaoru_sessions", []))

    conn = _lianjie_db()
    if not conn:
        return {"success": False, "error": "无法连接OpenCode数据库"}

    try:
        # 获取所有未导入的session
        sessions = conn.execute(
            "SELECT id, slug, title, time_created FROM session ORDER BY time_created").fetchall()
        xin_daoru = 0
        for sid, slug, title, ts in sessions:
            if sid in yidaoru:
                continue
            # 提取该session的text内容
            parts = conn.execute(
                "SELECT data FROM part WHERE session_id=? AND json_extract(data, '$.type')='text' ORDER BY time_created LIMIT 10",
                (sid,)).fetchall()
            texts = []
            for p in parts:
                try:
                    d = json.loads(p[0])
                    t = (d.get("text") or "").strip()
                    if t: texts.append(t)
                except: pass
            if not texts:
                continue

            # 摘要: 前3条文本
            summary = _jiequ_wenben(" | ".join(texts[:3]), 500)
            biaoti = f"OpenCode·{(title or slug)[:50]}"

            # 生成DNA签名
            qianming = _shengcheng_qianming_duiqi(biaoti)

            # 判断位点: 默认写入位点3(三才)和位点5(五行)
            for n in [3, 5]:
                fp = puxi_dir / f"{n}.json"
                if fp.exists():
                    data = json.loads(fp.read_text(encoding='utf-8'))
                    entry = {"biaoti": biaoti, "lingyu": "OpenCode对话",
                             "yao_dian": [summary], "qianming": qianming, "quanzhong": 1.0,
                             "laiyuan": "opencode", "chuangjian_shijian": datetime.now().isoformat()}
                    data.setdefault("zhe_die", []).append(entry)
                    fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

            yidaoru.add(sid)
            xin_daoru += 1

        conn.close()

        # 更新对齐状态
        zhuangtai["zuihou_duiqi"] = datetime.now().isoformat()
        zhuangtai["yidaoru_sessions"] = list(yidaoru)
        zhuangtai["zongshu"] = len(yidaoru)
        _cun_duiqi_zhuangtai(zhuangtai)

        return {"success": True, "xin_daoru": xin_daoru, "yidaoru_zongshu": len(yidaoru),
                "output": f"对齐完成: 新增{xin_daoru}个会话, 累计{len(yidaoru)}个"}
    except Exception as e:
        try: conn.close()
        except: pass
        return {"success": False, "error": str(e)}

def zengliang_duiqi():
    """增量对齐: 导入上次对齐后的新session"""
    duiqi_jiyi("zengliang")

def duiqi_zhuangtai(canshu=""):
    """返回记忆对齐状态"""
    zt = _qu_duiqi_zhuangtai()
    opcode = {"status": "ok"} if DB.exists() else {"status": "缺失"}
    if DB.exists():
        conn = _lianjie_db()
        if conn:
            opcode["xiaoxi_shu"] = conn.execute("SELECT COUNT(*) FROM message").fetchone()[0]
            opcode["huihua_shu"] = conn.execute("SELECT COUNT(*) FROM session").fetchone()[0]
            conn.close()
    puxi_dir = Path(__file__).parent.parent / 'shared_memory' / 'puxi'
    xingchao = {"yidaoru": zt.get("zongshu", 0)}
    if puxi_dir.exists():
        zong = 0
        for n in range(10):
            fp = puxi_dir / f"{n}.json"
            if fp.exists():
                d = json.loads(fp.read_text(encoding='utf-8'))
                zong += len(d.get("zhe_die", []))
        xingchao["zhe_die_zongshu"] = zong
    return {"success": True,
            "opencode": opcode,
            "xingchao": xingchao,
            "zuihou_duiqi": zt.get("zuihou_duiqi", "从未"),
            "output": json.dumps({"opencode": opcode, "xingchao": xingchao,
                                  "zuihou_duiqi": zt.get("zuihou_duiqi", "从未")}, ensure_ascii=False, indent=2)}

# ===== 实时对话对齐 V1.0 =====

DUIQI_DANGQIAN_FILE = Path(__file__).parent.parent / 'shared_memory' / 'duiqi_dangqian.json'

def _qu_dangqian_zhuangtai():
    if DUIQI_DANGQIAN_FILE.exists():
        try: return json.loads(DUIQI_DANGQIAN_FILE.read_text(encoding='utf-8'))
        except: pass
    return {"zuihou_xiaoxi_id": "", "zuihou_duiqi": "", "cishu": 0}

def _cun_dangqian_zhuangtai(zt):
    DUIQI_DANGQIAN_FILE.write_text(json.dumps(zt, ensure_ascii=False, indent=2), encoding='utf-8')

def duqu_dangqian_huihua(zuiduo=10):
    """读取OpenCode当前活动session最新消息"""
    conn = _lianjie_db()
    if not conn:
        return {"success": False, "error": "opencode.db不存在"}
    try:
        sess = conn.execute(
            "SELECT id, slug, title FROM session WHERE time_archived IS NULL ORDER BY time_updated DESC LIMIT 1"
        ).fetchone()
        if not sess:
            conn.close(); return {"success": False, "error": "无活动session"}
        sid, slug, title = sess

        # 读最新消息
        msgs = conn.execute(
            "SELECT id, time_created, data FROM message WHERE session_id=? ORDER BY time_created DESC LIMIT ?",
            (sid, zuiduo)
        ).fetchall()

        jieguo = []
        for mid, ts, data_raw in reversed(msgs):
            try:
                d = json.loads(data_raw)
                role = d.get("role", "?")
                agent = d.get("agent", "")
                # 取text part
                parts = conn.execute(
                    "SELECT data FROM part WHERE message_id=? AND json_extract(data,'$.type')='text' LIMIT 1",
                    (mid,)
                ).fetchall()
                text = ""
                for p in parts:
                    try: text = (json.loads(p[0]).get("text") or "")[:200]
                    except: pass
                if text.strip():
                    jieguo.append({"role": role, "agent": agent, "text": text.replace('\n',' '), "time": ts})
            except: pass

        conn.close()
        return {"success": True, "session_slug": slug, "session_title": title or slug,
                "xiaoxi_shu": len(jieguo), "xiaoxi": jieguo}
    except Exception as e:
        try: conn.close()
        except: pass
        return {"success": False, "error": str(e)}

def duiqi_dangqian_duihua():
    """实时对齐: 读当前session增量→编码→写入puxi位点3"""
    zt = _qu_dangqian_zhuangtai()
    zuihou = zt.get("zuihou_xiaoxi_id", "")

    r = duqu_dangqian_huihua(10)
    if not r.get("success") or not r.get("xiaoxi"):
        return {"success": True, "xin_duan": 0, "cishu": zt.get("cishu", 0)}

    # 提取新消息
    xin_xiaoxi = []
    for x in r["xiaoxi"]:
        xid = x.get("time", "")
        if str(xid) > str(zuihou):
            xin_xiaoxi.append(x)

    if not xin_xiaoxi:
        return {"success": True, "xin_duan": 0, "cishu": zt.get("cishu", 0)}

    # 编码新消息
    puxi_dir = Path(__file__).parent.parent / 'shared_memory' / 'puxi'
    texts = [f"[{x['role']}] {x['text'][:80]}" for x in xin_xiaoxi[:5]]
    summary = " | ".join(texts)

    biaoti = f"当前对话·{datetime.now().strftime('%H%M')}"
    qianming = _shengcheng_qianming_duiqi(biaoti, "dangqian")

    for n in [3]:
        fp = puxi_dir / f"{n}.json"
        if fp.exists():
            data = json.loads(fp.read_text(encoding='utf-8'))
            entry = {"biaoti": biaoti, "lingyu": "实时对话",
                     "yao_dian": [summary], "qianming": qianming, "quanzhong": 1.0,
                     "laiyuan": "dangqian", "chuangjian_shijian": datetime.now().isoformat()}
            data.setdefault("zhe_die", []).append(entry)
            fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    # 更新状态
    zt["zuihou_xiaoxi_id"] = str(xin_xiaoxi[-1].get("time", ""))
    zt["zuihou_duiqi"] = datetime.now().isoformat()
    zt["cishu"] += 1
    _cun_dangqian_zhuangtai(zt)

    return {"success": True, "xin_duan": len(xin_xiaoxi), "cishu": zt["cishu"],
            "output": f"实时对齐: {len(xin_xiaoxi)}新消息 → puxi位点3"}
