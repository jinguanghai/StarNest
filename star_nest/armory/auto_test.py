"""代理·重定向到子目录"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 直接调用实际模块的测试逻辑
from star_nest.armory.dev.zidong_ceshi import CESHI_YONGLI, ceshi_tiaomu, jiyu, shengcheng_baogao

print(f"{'='*55}")
print(f"  藏剑阁·全量自测启动")
print(f"{'='*55}")

for gongju_ming, yongli_liebiao in CESHI_YONGLI.items():
    print(f"\n  [{gongju_ming}]")
    for yongli in yongli_liebiao:
        ceshi_tiaomu(gongju_ming, *yongli)

ok = shengcheng_baogao()
sys.exit(0 if ok else 1)
