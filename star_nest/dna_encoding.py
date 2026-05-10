"""六十四卦DNA编码: 为每条知识生成64位签名 + 状态共振检索"""
import sys, json, os, time
from pathlib import Path

# 自动定位项目根目录
ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))
puxi_dir = ROOT / 'shared_memory' / 'puxi'

def shengcheng_qianming(biaoti, weizhi_liebiao):
    """生成64位六十四卦签名:
    bits 0-9:   谱系位点(属于哪些位点)
    bits 10-19: 标题哈希(领域特征)
    bits 20-35: 更多标题信息
    bits 36-45: 权重扩大区(振动空间)
    bits 46-63: 随机种子(唯一性)
    """
    bits = ['0'] * 64
    # 0-9: locus
    for w in weizhi_liebiao:
        if 0 <= w <= 9:
            bits[w] = '1'
    # 10-35: title hash
    h = hash(biaoti) & 0x3FFFFFF
    for i in range(10, 36):
        if h & (1 << (i - 10)):
            bits[i] = '1'
    # 36-63: 随机振动(模拟不同状态敏感性)
    import random
    random.seed(biaoti)
    for i in range(36, 64):
        if random.random() > 0.5:
            bits[i] = '1'
    return ''.join(bits)

def hamming_distance(a, b):
    """Hamming距离: 不同位数"""
    return sum(1 for i in range(64) if a[i] != b[i])

def shengcheng_zhuangtai(cengji="正境"):
    """生成当前系统状态向量(64位),用于共振检索"""
    cengji_map = {
        "正境":  [1,2,3], "反境": [5,6,8],
        "合境":  [4,5,9], "超越境": [0,7],
        "本源境": [0,1,2,3,4,5,6,7,8,9]
    }
    jihuo = cengji_map.get(cengji, [1,2,3])
    bits = ['0'] * 64
    for w in jihuo:
        if 0 <= w <= 9:
            bits[w] = '1'
    # 振动区: 当前cengji的hash
    h = hash(cengji) & 0xFFFFFF
    for i in range(40, 64):
        if h & (1 << (i - 40)):
            bits[i] = '1'
    return ''.join(bits)

# 生成所有签名并写入位点文件
total = 0
for i in range(10):
    fp = os.path.join(puxi_dir, f'{i}.json')
    if not os.path.exists(fp): continue
    with open(fp, encoding='utf-8') as f:
        data = json.loads(f.read())
    for entry in data.get('zhe_die', []):
        title = entry.get('biaoti', '')
        # 从父位点找到所有位点(去重)
        entry['qianming'] = shengcheng_qianming(title, [i])  # 本位点签名
        entry['quanzhong'] = 1.0
        total += 1
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))

print(f'Generated signatures for {total} entries across 10 loci')

# 测试: 状态共振检索
state = shengcheng_zhuangtai("反境")
print(f'State vector (反境): {state[:20]}...')

# 检索位点5中的记忆, 按Hamming距离排序
fp5 = os.path.join(puxi_dir, '5.json')
with open(fp5, encoding='utf-8') as f:
    data5 = json.loads(f.read())
entries = data5.get('zhe_die', [])[:5]
for e in entries:
    dist = hamming_distance(state, e.get('qianming', '0'*64))
    print(f'  {e["biaoti"][:40]}: Hamming={dist}')
print('DNA encoding complete')
