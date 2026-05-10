from pathlib import Path
import os

# 自动适配: 如果在 kernel/ 子目录下，往上多退一层
_peizhi_dir = Path(__file__).parent
_root = _peizhi_dir.parent
if _root.name == 'kernel':
    _root = _root.parent

XIANGMU_MULU = _root
XINGCHAOZDD_MULU = _root

LLM_ZHU = "DeepSeek"
LLM_BEI = "火山"

ZUDA_SHIBAI = 5
YANZHENG_CHAOSHI = 10
ZUDA_ZHONGCHI = 5
LIANXU_SHIBAI_MAX = 3

BIANCHENGTI_SHENFEN = "星巢编程体:专注于代码生成与系统架构,逻辑严谨,风格简洁。"
YUNXINGTI_SHENFEN = "星巢运行体:负责任务调度与流程控制,高效稳定。"
FUZHITI_SHENFEN = "星巢复制体:用于数据同步与备份,确保一致性。"

XIUGAI_BAIMINGDAN = ["config", "settings", "env"]
XIUGAI_HEIMINGDAN = ["password", "secret", "token", "key"]

ANQUAN_BAOHU = [
    "禁止执行外部命令",
    "禁止访问系统目录",
    "禁止修改环境变量",
    "禁止网络请求",
    "禁止文件删除操作",
    "禁止覆盖系统文件",
    "禁止读取敏感文件",
    "禁止注入代码",
    "禁止修改权限",
    "禁止递归删除"
]

def jiazai_huanjing():
    env_path = XIANGMU_MULU / "huanjing" / ".env"
    if not env_path.exists():
        env_path = XINGCHAOZDD_MULU / "huanjing" / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip("\"'")
                    if key and value:
                        os.environ[key] = value