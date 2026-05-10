"""
藏剑阁 · 模板工具 V1.0
纯Python标准库 · 零外部依赖
生成 Python/批处理/配置文件模板 · 项目脚手架
"""
import os, json
from pathlib import Path
from datetime import datetime


def shengcheng_py(wenjianming, leixing="tool"):
    """生成Python文件模板 leixing=tool/script/test/class"""
    templates = {
        "tool": '''"""
{} · {}
纯Python标准库 · 零外部依赖
"""
import os
from pathlib import Path


def main():
    """主函数"""
    return {{"success": True, "output": "{} 运行完成"}}


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False))
''',
        "script": '''#!/usr/bin/env python
"""{}"""
import sys

def main():
    pass

if __name__ == "__main__":
    main()
''',
        "test": '''"""
{} 测试
"""
import unittest

class Test(unittest.TestCase):
    def test_basic(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
''',
        "class": '''"""{}"""

class {}:
    def __init__(self):
        pass
''',
    }
    name = Path(wenjianming).stem.replace(' ', '_')
    if not wenjianming.endswith('.py'):
        wenjianming = wenjianming + '.py'
    content = templates.get(leixing, templates["tool"]).format(name, datetime.now().strftime("%Y-%m-%d"), name)
    try:
        Path(wenjianming).write_text(content, encoding='utf-8')
        return {"success": True, "output": f"已生成: {wenjianming}", "lujing": str(Path(wenjianming).resolve())}
    except Exception as e:
        return {"success": False, "error": str(e)}


def shengcheng_bat(wenjianming):
    """生成Windows批处理模板"""
    if not wenjianming.endswith('.bat'):
        wenjianming += '.bat'
    content = f"""@echo off
chcp 65001 >nul
echo ================================
echo   {Path(wenjianming).stem}
echo ================================
python {Path(wenjianming).stem}.py %*
pause
"""
    try:
        Path(wenjianming).write_text(content, encoding='utf-8')
        return {"success": True, "output": f"已生成: {wenjianming}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def shengcheng_config(wenjianming):
    """生成JSON配置文件模板"""
    if not wenjianming.endswith('.json'):
        wenjianming += '.json'
    config = {
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "settings": {},
    }
    try:
        Path(wenjianming).write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
        return {"success": True, "output": f"已生成: {wenjianming}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
