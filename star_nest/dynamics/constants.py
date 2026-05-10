"""
星巢常量模块 V1.0 — 统一管理所有阈值和魔法数字

七律节律: 7^1=7, 7^2=49, 7^3=343, 7^4=2401, 7^5=16807, 7^6=117649
六势态判定: 安全度/知识密度/执行意图 阈值
八极诊断: 默认值/边界值
认知处理: 超时/温度/分块大小
"""
# ==================== 七律节律 ====================

QI_LV_WEI_ZHOU = 7        # 一微周(心跳)
QI_LV_XIAO_ZHOU = 49      # 一小周(进程扫描)
QI_LV_ZHONG_ZHOU = 343    # 一中周(全量安全)
QI_LV_DA_ZHOU = 2401      # 一大周(深度审计)
QI_LV_ZHOU_TIAN = 16807   # 一周天(全量重检)
QI_LV_QI_ZHOU_TIAN = 117649  # 七周天(自审镜全扫描)

# ==================== 六势态阈值 ====================

# 安全度阈值
AN_QUAN_E_YI = 0.3       # 低于此→厥阴(恶意阻断)
AN_QUAN_KE_YI = 0.5      # 低于此→少阴(安全审查)
AN_QUAN_ZHENG_CHANG = 0.7 # 高于此→信任放行

# 知识密度阈值
ZHI_SHI_TAI_YIN = 0.5    # 高于此→太阴倾向(知识投喂)
ZHI_SHI_TAI_YANG = 0.2   # 低于此+高执行→阳明/太阳

# 执行意图阈值
ZHI_XING_TAI_YANG = 0.5  # 高于此→太阳(强执行意图)
ZHI_XING_YANG_MING = 0.3 # 高于此→阳明(明确指令)

# 危险信号阈值
WEI_XIAN_JUE_YIN = 3     # 危险信号≥此→厥阴(恶意阻断)
WEI_XIAN_SHAO_YIN = 1    # 危险信号≥此→少阴(可疑审查)

# 六势态更新步长
ZHI_SHI_BU_CHANG = 0.1   # 知识密度增量(每块)
AN_QUAN_ZENG_LIANG = 0.02 # 安全度增量(每块安全)
AN_QUAN_JIAN_LIANG = 0.15 # 安全度减量(每块可疑)
ZHI_XING_BU_CHANG = 0.15  # 执行意图增量(每块代码)
WEI_XIAN_E_YI_BU_CHANG = 2  # 危险信号增量(恶意模式)

# ==================== 八极诊断 ====================

BA_JI_DEFAULT = 0.5      # 八极默认值
BA_JI_E_YI_HAN = 0.7     # 寒(恶意)阈值
BA_JI_ZHI_XING_YANG = 0.6 # 阳(执行)阈值
BA_JI_ZHI_SHI_SHI = 0.6   # 实(知识)阈值

# ==================== 认知处理 ====================

# 分块大小
FEN_KUAI_ZHONG_WEN = 800   # 中文本分块(字)
FEN_KUAI_CHANG_WEN = 1200  # 长文本分块(字)
FEN_KUAI_YU_YI = 200      # 语义分块合并上限(字)

# 文本长度阈值
WEN_BEN_DUAN = 500         # 短文本上限(<此走对话)
WEN_BEN_ZHONG = 3000       # 中文本上限(<此分段消化)

# 超时设置(七律对齐·从 QiLv 动态读取, 此处为默认值)
LLM_CHAO_SHI = 49           # LLM调用超时(s, = 一小周)
CHU_LI_CHAO_SHI = 7         # 缓冲型超时(s, = 一微周)
ZHU_JIAN_LU_CHAO_SHI = 49   # 铸剑炉超时(s, = 一小周)
KONG_XIAN_ZHONG_JUE = 7     # 空闲后自动终判(s, = 一微周)
BUFFER_CHAO_SHI = 343        # 跨进程缓冲超时(s, = 一中周)

# LLM 温度
LLM_WEN_DU_DEFAULT = 0.7   # 默认温度(对话用)
LLM_WEN_DU_QUE_DING = 0.1  # 确定型任务(分类/匹配)
LLM_WEN_DU_FEN_XI = 0.2    # 分析型任务(判断/复盘)
LLM_WEN_DU_ZONG_HE = 0.25  # 综合型任务(贯通/总结)

# LLM 输出长度
LLM_ZI_FU_DUAN = 100       # 短输出(匹配/分类)
LLM_ZI_FU_ZHONG = 300      # 中输出(定性分析)
LLM_ZI_FU_CHANG = 500      # 长输出(内容提取)
LLM_ZI_FU_HEN_CHANG = 800  # 超长输出(深度分析)
LLM_ZI_FU_SUMMARY = 1200   # 摘要输出(框架/总结)
LLM_ZI_FU_BATCH = 1500     # 批量输出(安全判断)

# ==================== 安全 ====================

ZHAO_YAO_SCAN_LIMIT = 20    # 每目录扫描上限(文件)
ZHAO_YAO_DLL_LIMIT = 20     # DLL扫描上限
ZHAO_YAO_EXE_LIMIT = 30     # EXE扫描上限
ZHAO_YAO_PROC_LIMIT = 30    # 进程扫描上限
ZHAO_YAO_NET_LIMIT = 50     # 网络连接告警阈值

# ==================== 输入层 ====================

PASTE_JIAN_GE = 0.3         # 粘贴检测间隔(s)
PASTE_BUF_MIN = 3           # 粘贴缓冲最小行数
TOU_WEI_BUFFER_MIN = 3      # 投喂自动触发最小段数
