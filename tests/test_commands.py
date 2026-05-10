"""
星巢 CLI 场景测试 (L2) — 直接调 API 验证六路路由

不启动 SanTiXiTong 多次, 一次启动验证全部场景.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS = 0; FAIL = 0
results = []

def test(name, msg, expect_keywords=None, expect_not=None):
    """执行一个场景测试"""
    global PASS, FAIL
    try:
        from star_nest.entry import SanTiXiTong
        # 使用已有全局实例
        s = SanTiXiTong()
        s.bianchengti.start_all(); s.yunxingti.start_all()
        import time; time.sleep(2)
        
        # 清空输出队列
        for q in [s.yunxingti.xin.shuchu_duilie, s.bianchengti.xin.shuchu_duilie]:
            while not q.empty():
                try: q.get_nowait()
                except: pass
        
        s.yunxingti.xin.add_xuqiu(msg)
        
        # 等待响应 (最多一小周49s)
        for _ in range(98):
            time.sleep(0.5)
            for q in [s.yunxingti.xin.shuchu_duilie, s.bianchengti.xin.shuchu_duilie]:
                try:
                    r = q.get_nowait()
                    if r:
                        r_str = str(r)
                        ok = True
                        if expect_keywords and not any(kw in r_str for kw in expect_keywords):
                            ok = False
                        if expect_not and any(kw in r_str for kw in expect_not):
                            ok = False
                        if ok: PASS += 1; results.append(f"  PASS: {name} ({r_str[:60]}...)")
                        else: FAIL += 1; results.append(f"  FAIL: {name} (unexpected: {r_str[:80]})")
                        return
                except: pass
        FAIL += 1; results.append(f"  FAIL: {name} (timeout)")
    except Exception as e:
        FAIL += 1; results.append(f"  FAIL: {name} ({e})")

print("=" * 50)
print("  星巢 CLI 场景测试 (L2)")
print("=" * 50)

for r in results: print(r)
print("=" * 50)
print(f"  结果: {PASS}/{PASS+FAIL} PASS")
print("=" * 50)
