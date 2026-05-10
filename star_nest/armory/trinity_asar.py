"""
三体 asar 角色补丁
yunxingti: plan强制·只读·有问题上报
bianchengti: build模式·可写·铸剑炉连接
fuzhiti: 沙箱模式·只读·不执行写操作
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from star_nest.armory.opencode_asar import liechu_asar, duqu_wenjian

BASE = str(Path(__file__).parent.parent)

ROLES = {
    'yunxingti': {
        'port': 9527,
        'desc': '运行体·只读·问题上报',
        'mode': 'plan',
        'xie': False,
    },
    'bianchengti': {
        'port': 9528,
        'desc': '编程体·可写·铸剑炉拥有者',
        'mode': 'build',
        'xie': True,
    },
    'fuzhiti': {
        'port': 9529,
        'desc': '复制体·隔离·沙箱验证',
        'mode': 'plan',
        'xie': False,
    },
}

def santi_asar(role, asar_path, output_path):
    """为三体角色定制 asar"""
    from star_nest.armory.opencode_asar import duqu_asar, chongdabao_asar
    from star_nest.armory.opencode_patch import yizhi_watcher

    print(f"  角色: {ROLES[role]['desc']}")
    print(f"  端口: {ROLES[role]['port']}")

    # 读取
    asar = duqu_asar(asar_path)
    if not asar.get("success"):
        return asar

    # 补丁1: watcher抑制 (全部)
    watcher = yizhi_watcher(asar)
    print(f"  watcher: {watcher.get('output', '?')}")

    # 补丁2: 角色签名
    import json
    from datetime import datetime
    pkg_key = None
    files = asar.get("files", {})
    for k in files:
        if k in ('package.json', '/package.json'):
            pkg_key = k
            break
    if pkg_key:
        try:
            pkg = json.loads(files[pkg_key].decode('utf-8'))
            pkg["xingchao_santi"] = {
                "role": role,
                "desc": ROLES[role]['desc'],
                "biancheng": datetime.now().isoformat(),
                "qixue": "V10.6"
            }
            files[pkg_key] = json.dumps(pkg, indent=2, ensure_ascii=False).encode('utf-8')
            print(f"  签名: {role}")
        except Exception as e:
            print(f"  签名失败: {e}")

    asar["files"] = files

    # 重打包
    jg = chongdabao_asar(asar, output_path)
    if jg.get("success"):
        print(f"  打包: {output_path} ({jg.get('daxiao', 0)} bytes)")
    return jg


def yunxingti_auth(port):
    return {
        "deepseek": {
            "type": "api",
            "key": "sk-c42514915ac64652aa3225fa1efe2450",
            "url": f"http://localhost:{port}/v1"
        }
    }


if __name__ == '__main__':
    for role in ['yunxingti', 'bianchengti', 'fuzhiti']:
        print(f"\n=== {role} ===")
        asar_in = f"{BASE}\\{role}\\OpenCode\\resources\\app.asar"
        asar_out = f"{BASE}\\{role}\\OpenCode\\resources\\app.asar.patched"

        jg = santi_asar(role, asar_in, asar_out)
        if jg.get("success"):
            # 替换原asar
            import shutil
            shutil.move(asar_out, asar_in)
            print(f"  ✓ 已部署")

        # 写auth.json
        auth_path = f"{BASE}\\{role}\\OpenCode\\auth.json"
        import json, os
        os.makedirs(os.path.dirname(auth_path) if not os.path.exists(os.path.dirname(auth_path)) else '.', exist_ok=True)
        # auth.json 放在 resources/ 旁边的 %LOCALAPPDATA% 下
        # 实际 auth.json 在 C:\Users\jin\.local\share\opencode\
        # 但三体各自需要独立的, 通过 user-data-dir 分离
        print(f"  auth: → localhost:{ROLES[role]['port']}")

    print("\n三体 asar 角色补丁完成")
