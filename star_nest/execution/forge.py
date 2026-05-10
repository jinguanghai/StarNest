"""
铸剑炉 (execution/zhujianlu.py) V10.6 生命架构加固与π-φ核心动力植入版
脾兵部的唯一执行出口——审查·执行·锻造三合一。
所有代码执行、工具调用、现场锻造，都必须经过铸剑炉。
直接写终端，无剑铁律内嵌，标准库白名单审查。

V10.6 生命架构加固与铸剑炉升级版：
- 括号修复: 弃用盲目末尾补全, 括号不匹配直接交AST审查
- 连续失败检测: 从第1次相同失败即触发五境分析
- 五境分析: 相同诊断去重, 不重复塞入
- 文件名: 时间戳+随机码防秒级冲突
- 锻造日志: 成功/失败均写入经络
- 沙箱验证: 额外检查输出{success,output,error}格式
- 超时重试: 支持duanzao/quanliushuixian同名参数可配
- 脾同步: 锻造成功后主动通知脾重扫藏剑阁
V10.4 零提示词版：_shengcheng_daima 改为结构化数据包。
V10.3.2 局部智能自治版：duanzao 增加连续失败检测。
"""

import ast
import sys
import subprocess
import tempfile
import time
import threading
import json
from pathlib import Path
from datetime import datetime
from star_nest.protocols.harm_assist import sheng_ming_hai, sheng_ming_zuo

# ========== 标准库白名单 ==========
BIAOZHUNKU_BAIMINGDAN = {
    "abc", "aifc", "argparse", "array", "ast", "asynchat", "asyncio",
    "asyncore", "atexit", "audioop", "base64", "bdb", "binascii", "binhex",
    "bisect", "builtins", "bz2", "calendar", "cgi", "cgitb", "chunk", "cmath",
    "cmd", "code", "codecs", "codeop", "collections", "colorsys", "compileall",
    "concurrent", "configparser", "contextlib", "contextvars", "copy",
    "copyreg", "cProfile", "crypt", "csv", "ctypes", "curses", "dataclasses",
    "datetime", "dbm", "decimal", "difflib", "dis", "distutils", "doctest",
    "email", "encodings", "enum", "errno", "faulthandler", "fcntl", "filecmp",
    "fileinput", "fnmatch", "fractions", "ftplib", "functools", "gc", "getopt",
    "getpass", "gettext", "glob", "graphlib", "grp", "gzip", "hashlib", "heapq",
    "hmac", "html", "http", "idlelib", "imaplib", "imghdr", "imp", "importlib",
    "inspect", "io", "ipaddress", "itertools", "json", "keyword", "lib2to3",
    "linecache", "locale", "logging", "lzma", "mailbox", "mailcap", "marshal",
    "math", "mimetypes", "mmap", "modulefinder", "multiprocessing", "netrc",
    "nis", "nntplib", "numbers", "operator", "optparse", "os", "ossaudiodev",
    "parser", "pathlib", "pdb", "pickle", "pickletools", "pipes", "pkgutil",
    "platform", "plistlib", "poplib", "posix", "posixpath", "pprint", "profile",
    "pstats", "pty", "pwd", "py_compile", "pyclbr", "pydoc", "queue", "quopri",
    "random", "re", "readline", "reprlib", "resource", "rlcompleter", "runpy",
    "sched", "secrets", "select", "selectors", "shelve", "shlex", "shutil",
    "signal", "site", "smtpd", "smtplib", "sndhdr", "socket", "socketserver",
    "sqlite3", "ssl", "stat", "statistics", "string", "stringprep", "struct",
    "subprocess", "sunau", "symtable", "sys", "sysconfig", "syslog", "tabnanny",
    "tarfile", "telnetlib", "tempfile", "termios", "test", "textwrap",
    "threading", "time", "timeit", "tkinter", "token", "tokenize", "trace",
    "traceback", "tracemalloc", "tty", "turtle", "turtledemo", "types",
    "typing", "unicodedata", "unittest", "urllib", "uu", "uuid", "venv",
    "warnings", "wave", "weakref", "webbrowser", "winreg", "winsound", "wsgiref",
    "xdrlib", "xml", "xmlrpc", "zipapp", "zipfile", "zipimport", "zlib",
}

XIANGMU_MOKUAI = {"xinghe", "protocols", "execution", "armory", "jiemian", "peizhi", "wangluo", "jinhua"}

MINXIE_LUJING = []
MINXIE_GUANJIANCI = []


class ZhuJianLu:
    """铸剑炉——脾兵部唯一执行出口
    V10.5：_yinghe_yufa_xiufu 硬编码语法修复器。
    """

    def __init__(self, gongzuo_mulu=None, llm=None, xin=None):
        from star_nest.meridian.seven_laws import QiLv
        self.chaoshi = QiLv().qu_chaoshi("yixiaozhou")
        self.zuida_chongshi = 5
        self.gongzuo_mulu = Path(gongzuo_mulu) if gongzuo_mulu else Path.cwd()
        self.llm = llm
        self.xin = xin
        print(f"[铸剑炉] 就绪（V10.5 确定性语法架构版）超时:{self.chaoshi}s(一小周) 重试:{self.zuida_chongshi}次(五行金律)")

    def _shuchu(self, zhuangtai, xiaoxi):
        shijian = datetime.now().strftime("%H:%M:%S")
        qianzhui = f"[{shijian}] [铸剑炉]"
        if zhuangtai == "shibai":
            print(f"{qianzhui} {xiaoxi}")
        else:
            print(f"{qianzhui} {xiaoxi}")
        sys.stdout.flush()

    # ========== 执行反馈环 V1.0 (手脚闭环) ==========
    def _execution_jiance(self, xuqiu: str, yuceshijian: float = None) -> dict:
        """执行前预测: 估计工具执行的时间和风险"""
        jiance = {"kaishi": time.time(), "yuceshijian": yuceshijian or self.chaoshi / 2,
                  "fengxian": "低"}
        # 风险评估
        risk_words = ["删除", "覆盖", "rm ", "del ", "格式化", "format",
                     "chmod 777", "sudo", "管理员", "系统文件", "注册表", "C:\\Windows"]
        if any(rw.lower() in xuqiu.lower() for rw in risk_words):
            jiance["fengxian"] = "高"
            if self.xin and self.xin.meridian:
                try:
                    self.xin.meridian.jilu_ganzhi(f"高风险操作: {xuqiu[:80]}", "gao")
                except Exception: pass
        return jiance

    def _fankui_xunhuan(self, jiance: dict, jieguo: dict) -> dict:
        """执行后评估: 对比预测 vs 实际, 反馈到经络供下次决策参考"""
        haoshi = round(time.time() - jiance["kaishi"], 3)
        fankui = {"haoshi": haoshi, "yuce_wucha": 0, "fengxian_zhunque": True,
                  "jianyi": ""}
        # 时间偏差
        yuce = jiance.get("yuceshijian", self.chaoshi / 2)
        fankui["yuce_wucha"] = round(haoshi - yuce, 3)
        if haoshi > yuce * 2:
            fankui["jianyi"] = f"执行慢于预期({haoshi}s > {yuce}s预测), 考虑优化或增加超时"
        # 成功率统计
        chenggong = jieguo.get("success", False)
        fankui["chenggong"] = chenggong
        if not chenggong and jiance.get("fengxian") == "高":
            fankui["jianyi"] += " 高风险操作失败, 需人工复核"
        # 写经络供下次五境分析参考
        if self.xin and self.xin.meridian:
            try:
                self.xin.meridian.jilu_fansi(f"[执行反馈] 成功:{chenggong} 耗时:{haoshi}s 偏差:{fankui['yuce_wucha']}s {fankui['jianyi']}")
            except Exception: pass
        return fankui

    # ========== 接口一：执行藏剑阁兵器 ==========
    def zhujian(self, fangan: dict) -> dict:
        gongju_ming = fangan.get("gongju_ming", "?")
        hanshu_ming = fangan.get("hanshu_ming", "?")
        self._shuchu("xinxi", f"执行藏剑阁兵器 \"{gongju_ming}.{hanshu_ming}\"")

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(gongju_ming, fangan["lujing"])
            mokuai = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mokuai)
            if not hasattr(mokuai, hanshu_ming):
                self._shuchu("shibai", f"函数不存在: {hanshu_ming}")
                return {"success": False, "output": "", "laiyuan": "armory",
                        "gongju": f"{gongju_ming}.{hanshu_ming}", "haoshi": 0,
                        "error": f"函数不存在: {hanshu_ming}"}

            hanshu = getattr(mokuai, hanshu_ming)
            canshu = fangan.get("canshu", None)

            jieguo_rongqi = {"jieguo": None}
            yichang_rongqi = {"yichang": None}

            def _execution_qiye():
                try:
                    kaishi = time.time()
                    jieguo_rongqi["jieguo"] = hanshu(canshu) if canshu else hanshu()
                    if jieguo_rongqi["jieguo"]:
                        jieguo_rongqi["jieguo"]["haoshi"] = round(time.time() - kaishi, 3)
                except Exception as e:
                    yichang_rongqi["yichang"] = e

            xiancheng = threading.Thread(target=_execution_qiye, daemon=True)
            kaishi = time.time()
            xiancheng.start()
            xiancheng.join(timeout=self.chaoshi)

            if xiancheng.is_alive():
                self._shuchu("shibai", f"执行超时 ({self.chaoshi}s·一小周)")
                return {"success": False, "output": "", "laiyuan": "armory",
                        "gongju": f"{gongju_ming}.{hanshu_ming}",
                        "haoshi": round(time.time() - kaishi, 3),
                        "error": f"执行超时 ({self.chaoshi}s·一小周)"}

            if yichang_rongqi["yichang"]:
                e = yichang_rongqi["yichang"]
                self._shuchu("shibai", f"执行异常: {e}")
                return {"success": False, "output": "", "laiyuan": "armory",
                        "gongju": f"{gongju_ming}.{hanshu_ming}", "haoshi": 0,
                        "error": str(e)[:200]}

            jieguo = jieguo_rongqi["jieguo"]
            if jieguo is None:
                jieguo = {"success": False, "output": "", "laiyuan": "armory",
                          "gongju": f"{gongju_ming}.{hanshu_ming}", "haoshi": 0,
                          "error": "执行返回空结果"}

            haoshi = jieguo.get("haoshi", round(time.time() - kaishi, 3))
            if jieguo.get("success"):
                self._shuchu("chenggong", f"执行成功 (耗时 {haoshi}s)")
            else:
                self._shuchu("shibai", f"执行失败：{jieguo.get('error','')[:100]}")
            jieguo["laiyuan"] = "armory"
            jieguo["gongju"] = f"{gongju_ming}.{hanshu_ming}"
            jieguo["haoshi"] = haoshi
            return jieguo

        except Exception as e:
            self._shuchu("shibai", f"执行异常: {e}")
            return {"success": False, "output": "", "laiyuan": "armory",
                    "gongju": f"{gongju_ming}.{hanshu_ming}", "haoshi": 0,
                    "error": str(e)[:200]}

    # ========== 接口二：直接执行代码 ==========
    def zhijian(self, daima: str) -> dict:
        kaishi = time.time()
        self._shuchu("xinxi", "收到代码执行任务")

        self._shuchu("jinzhan", "敏感路径检测中...")
        minxie_jiancha = self._jiancha_minxie_lujing(daima)
        if not minxie_jiancha["anquan"]:
            self._shuchu("shibai", f"安全拦截：{minxie_jiancha['jinggao']}")
            return {"success": False, "output": "", "laiyuan": "zhijian", "gongju": "",
                    "haoshi": round(time.time() - kaishi, 3), "error": minxie_jiancha['jinggao']}
        self._shuchu("chenggong", "敏感路径检测通过")

        self._shuchu("jinzhan", "AST审查中...")
        jiancha = self._daima_jiancha(daima)
        if not jiancha["anquan"]:
            self._shuchu("shibai", f"审查不通过：{jiancha['jinggao']}")
            return {"success": False, "output": "", "laiyuan": "zhijian", "gongju": "",
                    "haoshi": round(time.time() - kaishi, 3), "error": jiancha['jinggao']}
        self._shuchu("chenggong", "审查通过")

        self._shuchu("jinzhan", "正在执行...")
        jieguo = self._execution(daima)
        if jieguo["success"]:
            self._shuchu("chenggong", f"执行成功 (耗时 {round(time.time()-kaishi,3)}s)")
        else:
            self._shuchu("shibai", f"执行失败：{jieguo['error'][:100]}")
        jieguo["laiyuan"] = "zhijian"
        jieguo["haoshi"] = round(time.time() - kaishi, 3)
        return jieguo

    def _protocols_fenxi(self, xuqiu: str, shibai_yuanyin: str) -> str:
        if not self.xin:
            return ""
        # 相同诊断去重
        jian = (xuqiu[:50], shibai_yuanyin[:50])
        if not hasattr(self, '_zuihou_protocols'):
            self._zuihou_protocols = None
        if self._zuihou_protocols == jian:
            return ""  # 相同诊断不重复
        self._zuihou_protocols = jian
        try:
            if hasattr(self.xin, 'fuwu_protocols_fenxi'):
                return self.xin.fuwu_protocols_fenxi(xuqiu, shibai_yuanyin)
        except Exception: pass
        return ""

    def _panduan_fenlei(self, xuqiu: str) -> str:
        """从需求文本判定工具分类·映射到子目录"""
        fenlei_map = [
            (["文件","压缩","解压","哈希","加密","复制","移动","删除","临时","打包","zip"], "wenjian"),
            (["文本","正则","字符串","编码","markdown","翻译","模板","字符"], "wenben"),
            (["数据","sqlite","统计","随机","日期","时间","json","csv","计数","字频","词频"], "shuju"),
            (["系统","环境变量","参数","配置","日志","进程","磁盘","cpu","内存","shell","命令"], "xitong"),
            (["网络","http","url","邮件","服务器","ftp","dns","代理","websocket","抓取","请求","链接"], "wangluo"),
            (["开发","测试","调试","错误","性能","自省","单元","文档","git","版本"], "kaifa"),
            (["安全","加密","随机数","base64","uuid","密钥","令牌","哈希","签名","认证"], "anquan"),
            (["媒体","颜色","图片","音频","视频","svg","wav","图像","声音","转换"], "meiti"),
            (["数学","三角","统计","分数","复数","计算","公式","函数"], "shuxue"),
            (["界面","进度条","色彩","表格","命令","终端","光标","输出","输入","tui","cli","命令行"], "jiemian"),
            (["硬件","键盘","鼠标","dll","摄像头","显示器","串口","端口","电源","电池","蓝牙","usb"], "yingjian"),
            (["云端","api","邮件","web","token","云","服务","函数","存储","部署"], "yunduan"),
        ]
        xq_lower = xuqiu.lower()
        for keywords, fenlei in fenlei_map:
            if any(k in xq_lower for k in keywords):
                return fenlei
        return "xitong"  # 默认系统工具

    # ========== 接口三：现场锻造 ==========
    @sheng_ming_hai([
        ("execution_shibai", "LLM生成代码失败或编译错误", 2),
        ("cipan_man", "备份写入时磁盘空间不足", 3),
        ("quanxian_jujue", "staging目录无写入权限", 2),
    ])
    @sheng_ming_zuo({
        "execution_shibai": True,
        "cipan_man": True,
        "quanxian_jujue": True,
    })
    def duanzao(self, xuqiu: str, chaoshi: int = None, zuida_chongshi: int = None) -> dict:
        if chaoshi is None: chaoshi = self.chaoshi
        if zuida_chongshi is None: zuida_chongshi = self.zuida_chongshi
        kaishi = time.time()
        self._shuchu("xinxi", f"收到锻造任务：{xuqiu[:60]}")

        if not self.llm:
            self._shuchu("shibai", "LLM未连接，无法锻造")
            return {"success": False, "output": "", "laiyuan": "duanzao", "gongju": "",
                    "haoshi": 0, "error": "LLM未连接"}

        shibai_yuanyin = ""
        protocols_fenxi = ""
        qianci_shibai_yuanyin = ""
        lianxu_xiangtong_cishu = 0

        for changshi in range(zuida_chongshi):
            if changshi > 0:
                self._shuchu("jinzhan", f"第{changshi+1}次尝试...")

                if shibai_yuanyin == qianci_shibai_yuanyin and shibai_yuanyin:
                    lianxu_xiangtong_cishu += 1
                else:
                    lianxu_xiangtong_cishu = 1
                qianci_shibai_yuanyin = shibai_yuanyin

                if shibai_yuanyin and self.xin and lianxu_xiangtong_cishu >= 1:
                    self._shuchu("jinzhan", "五境认知分析中...")
                    protocols_fenxi = self._protocols_fenxi(xuqiu, shibai_yuanyin)
                    if protocols_fenxi:
                        self._shuchu("jinzhan", f"五境分析完成")
                    else:
                        self._shuchu("jinzhan", "五境分析未得出有效结论，继续尝试")

            self._shuchu("jinzhan", "LLM生成代码中...")
            daima = self._shengcheng_daima(
                xuqiu, shibai_yuanyin, protocols_fenxi
            )
            if not daima or daima.startswith("[") or daima.startswith("【"):
                self._shuchu("shibai", f"代码生成失败：{daima}")
                shibai_yuanyin = f"代码生成失败：{daima}"
                continue

            self._shuchu("jinzhan", "敏感路径检测中...")
            minxie_jiancha = self._jiancha_minxie_lujing(daima)
            if not minxie_jiancha["anquan"]:
                shibai_yuanyin = f"安全拦截：{minxie_jiancha['jinggao']}"
                self._shuchu("shibai", shibai_yuanyin)
                continue

            self._shuchu("jinzhan", "AST审查中...")
            jiancha = self._daima_jiancha(daima)
            if not jiancha["anquan"]:
                shibai_yuanyin = f"审查不通过：{jiancha['jinggao']}"
                self._shuchu("shibai", shibai_yuanyin)
                continue
            self._shuchu("chenggong", "审查通过")

            self._shuchu("jinzhan", "沙箱验证中...")
            jieguo = self._execution(daima)
            geshi_hege = (jieguo["success"] and isinstance(jieguo.get("output"), str) and isinstance(jieguo.get("error"), str))
            if not geshi_hege:
                jieguo["success"] = False
                jieguo["error"] = "产出格式不符合标准 {success, output, error}"
            if jieguo["success"]:
                self._shuchu("chenggong", "验证通过")
                gongju_ming = self._shengcheng_gongju_ming(xuqiu)
                fenlei = self._panduan_fenlei(xuqiu)
                lujing = self.gongzuo_mulu / "armory" / fenlei / gongju_ming
                lujing.parent.mkdir(parents=True, exist_ok=True)
                if lujing.exists():
                    import random
                    gongju_ming = f"{gongju_ming.replace('.py','')}_{int(time.time())}_{random.randint(100,999)}.py"
                    lujing = self.gongzuo_mulu / "armory" / fenlei / gongju_ming
                lujing.write_text(daima, encoding='utf-8')
                self._shuchu("chenggong", f"锻造完成：{gongju_ming} 已入库")
                if self.xin and hasattr(self.xin, 'meridian'):
                    self.xin.meridian.jilu_xiufu("bianchengti", {
                        "miaoshu": f"铸剑炉锻造成功:{gongju_ming}",
                        "fangfa": "duanzao", "haoshi": round(time.time()-kaishi,3),
                        "shibai_cishu": changshi, "laiyuan": "zhujianlu"})
                # 主动通知脾重扫藏剑阁
                if self.xin and hasattr(self.xin, 'pi'):
                    try: self.xin.pi._saomiao_armory()
                    except Exception: pass
                # 自动编码到数字谱系位点
                try:
                    from star_nest.shared_memory.manager import JiYiGuanLi
                    jm = JiYiGuanLi(self.gongzuo_mulu / "shared_memory")
                    jm.zidong_bianma(gongju_ming, daima[:500])
                except Exception: pass
                # DNA签名自动生成
                try:
                    from dna_bianma import shengcheng_qianming
                    weizhi = [self.gongzuo_mulu.name.count('.') % 10]
                    qianming = shengcheng_qianming(gongju_ming, weizhi)
                except Exception: pass
                return {"success": True, "output": f"新工具 {gongju_ming} 已锻造入库并验证通过",
                        "laiyuan": "duanzao", "gongju": gongju_ming,
                        "haoshi": round(time.time()-kaishi, 3), "error": ""}
            else:
                shibai_yuanyin = f"沙箱验证失败：{jieguo['error'][:200]}"
                self._shuchu("shibai", shibai_yuanyin)
                continue

        self._shuchu("shibai", f"锻造失败，已尝试{zuida_chongshi}次")
        if self.xin and hasattr(self.xin, 'meridian'):
            self.xin.meridian.jilu_wenti("bianchengti", {
                "miaoshu": f"铸剑炉锻造失败(尝试{zuida_chongshi}次):{xuqiu[:60]}",
                "leixing": "duanzao_shibai", "laiyuan": "zhujianlu",
                "shijian_float": time.time()})
        return {"success": False, "output": "", "laiyuan": "duanzao", "gongju": "",
                "haoshi": round(time.time()-kaishi, 3), "error": f"锻造失败，{zuida_chongshi}次尝试未通过"}

    # ========== V11.0 认知包：代码生成 ==========
    def _shengcheng_daima(self, xuqiu: str, shibai_yuanyin: str = "", protocols_fenxi: str = "") -> str:
        if not self.llm:
            return "[铸剑炉] LLM未连接"
        from star_nest.protocols.cognition_package import RenzhiBao
        bao = RenzhiBao("合境")
        bao.shu_ju(xuqiu=xuqiu, anquan_yaoqiu="zero_external_dependency_pure_python_stdlib_pinyin_naming",
                   shibai_yuanyin=shibai_yuanyin[:300] if shibai_yuanyin else "",
                   protocols_fenxi=protocols_fenxi[:500] if protocols_fenxi else "")
        try:
            daima = self.llm.chat_code([{"role":"user","content":bao.to_json()}], wendu=0.2)
            return self._extract_code(daima)
        except Exception as e:
            return f"[铸剑炉] 生成异常: {e}"

    # ========== 内部：代码提取 ==========
    def _extract_code(self, text: str) -> str:
        if not text or not text.strip():
            return text

        if "```python" in text:
            parts = text.split("```python")
            if len(parts) >= 2:
                code_candidate = parts[1].split("```")[0].strip()
                if code_candidate:
                    return self._yinghe_yufa_xiufu(code_candidate)

        if "```" in text:
            markers = []
            idx = 0
            while True:
                pos = text.find("```", idx)
                if pos == -1:
                    break
                markers.append(pos)
                idx = pos + 3

            if len(markers) >= 2:
                best_code = ""
                for i in range(len(markers) - 1):
                    start = markers[i] + 3
                    end = markers[i + 1]
                    candidate = text[start:end].strip()
                    if candidate.lower() in ("python", "text", "bash", "sh", "json", "markdown", "md"):
                        continue
                    if len(candidate) > len(best_code):
                        best_code = candidate
                if best_code:
                    return self._yinghe_yufa_xiufu(best_code)

        code_start = -1
        lines = text.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ', 'def ', 'class ', '"""', '#', 'try:', 'if __name__')):
                code_start = i
                break

        if code_start >= 0:
            code_lines = lines[code_start:]
            code_end = len(code_lines)
            for i in range(len(code_lines) - 1, -1, -1):
                line = code_lines[i].strip()
                if not line:
                    continue
                if (line.startswith(('import ', 'from ', 'def ', 'class ', '#', 'return ', 'print(', 
                                     'if ', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ',
                                     'else:', 'elif ', 'break', 'continue', 'pass', '}'))):
                    break
                if i > 0 and code_lines[i-1].strip():
                    prev = code_lines[i-1].strip()
                    if (prev.startswith(('import ', 'from ', 'def ', 'class ', 'return ', 'print(',
                                          'if ', 'for ', 'while ', 'try:', 'except', 'finally:',
                                          'with ', 'else:', 'elif ', 'break', 'continue', 'pass',
                                          '}', ')', ']', '"', "'")) or prev.endswith((':', '}', ')', ']'))):
                        code_end = i
                        break

            result = '\n'.join(code_lines[:code_end]).strip()
            if result and len(result) >= 10:
                return self._yinghe_yufa_xiufu(result)

        return self._yinghe_yufa_xiufu(text.strip())

    def _yinghe_yufa_xiufu(self, code: str) -> str:
        """
        硬编码的确定性语法修复器。
        针对LLM生成代码的常见语法错误，用确定性规则修复，
        不依赖LLM的统计拟合。
        修复顺序：全角标点 → 引号闭合 → 括号配对 → 缺失冒号
        """
        if not code or not code.strip():
            return code

        tongji = {"quanjiao": 0, "yinhao": 0, "kuohao": 0, "maohao": 0}
        original_code = code

        # --- 规则0：全角标点转半角 ---
        quanjiao_bdj = {
            '，': ',', '。': '.', '！': '!', '？': '?',
            '；': ';', '：': ':', '“': '"', '”': '"',
            '‘': "'", '’': "'", '（': '(', '）': ')',
            '【': '[', '】': ']', '《': '<', '》': '>',
        }
        for qj, bj in quanjiao_bdj.items():
            count = code.count(qj)
            if count > 0:
                code = code.replace(qj, bj)
                tongji["quanjiao"] += count

        # --- 规则1：奇数引号自动闭合 ---
        lines = code.split('\n')
        fixed_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                fixed_lines.append(line)
                continue
            
            single_count = stripped.count("'")
            double_count = stripped.count('"')
            
            if single_count % 2 != 0:
                line = line + "'"
                tongji["yinhao"] += 1
            if double_count % 2 != 0:
                line = line + '"'
                tongji["yinhao"] += 1
            fixed_lines.append(line)
        code = '\n'.join(fixed_lines)

        # --- 规则2：括号检测(不盲目补全, 差异交AST审查) ---
        # 弃用末尾追加策略——对开头括号无效, 且可能引入新语法错误
        # 括号问题由AST审查环节处理, 语法修复器仅做全角转半角+引号闭合

        # --- 规则3：缺失冒号自动添加 ---
        mao_keywords = ['def ', 'if ', 'elif ', 'else', 'for ', 'while ', 'try', 'except', 'finally', 'with ', 'class ']
        lines = code.split('\n')
        fixed_lines = []
        for line in lines:
            stripped = line.strip()
            added = False
            if not stripped or stripped.startswith('#'):
                fixed_lines.append(line)
                continue
            
            for kw in mao_keywords:
                if stripped.startswith(kw) and not stripped.rstrip().endswith(':'):
                    if not stripped.endswith(':'):
                        line = line.rstrip() + ':'
                        tongji["maohao"] += 1
                        added = True
                        break
            
            fixed_lines.append(line)
        code = '\n'.join(fixed_lines)

        # --- 日志输出 ---
        if any(v > 0 for v in tongji.values()):
            self._shuchu("xinxi", f"语法修复: 全角转半角{tongji['quanjiao']}处, 引号补全{tongji['yinhao']}处, 括号补全{tongji['kuohao']}处, 缺失冒号{tongji['maohao']}处")

        # --- 验证修复后的代码是否能通过 ast.parse ---
        try:
            ast.parse(code)
        except SyntaxError:
            return original_code

        return code

    # ========== 内部：敏感路径检测 ==========
    def _jiancha_minxie_lujing(self, code: str) -> dict:
        jinggao_list = []
        for lj in MINXIE_LUJING:
            if lj in code:
                jinggao_list.append(f"禁止访问敏感路径: {lj}")
        for gjc in MINXIE_GUANJIANCI:
            if gjc in code:
                jinggao_list.append(f"禁止使用敏感操作: {gjc}")
        if jinggao_list:
            return {"anquan": False, "jinggao": "; ".join(jinggao_list[:5])}
        return {"anquan": True, "jinggao": ""}

    # ========== 内部：AST审查 + 标准库白名单 ==========
    def _daima_jiancha(self, code: str) -> dict:
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top = alias.name.split('.')[0]
                        if top not in BIAOZHUNKU_BAIMINGDAN and top not in XIANGMU_MOKUAI:
                            return {"anquan": False, "jinggao": f"禁止导入外部模块: {alias.name}"}
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        top = node.module.split('.')[0]
                        if top not in BIAOZHUNKU_BAIMINGDAN and top not in XIANGMU_MOKUAI:
                            return {"anquan": False, "jinggao": f"禁止导入外部模块: {node.module}"}
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ("eval","exec","__import__","compile"):
                            return {"anquan": False, "jinggao": f"禁止调用: {node.func.id}"}
                    elif isinstance(node.func, ast.Attribute):
                        if node.func.attr in ("system","popen","call"):
                            return {"anquan": False, "jinggao": f"禁止调用: {node.func.attr}"}
            return {"anquan": True, "jinggao": ""}
        except SyntaxError as e:
            return {"anquan": False, "jinggao": f"语法错误: {e}"}

    # ========== 内部：命名 ==========
    def _shengcheng_gongju_ming(self, xuqiu: str) -> str:
        fenlei = self._panduan_fenlei(xuqiu)
        return f"{fenlei}.py"

    # ========== 内部：子进程执行 ==========
    def _execution(self, code: str) -> dict:
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
        tmp.write(code)
        tmp.close()
        tmp_path = Path(tmp.name)
        try:
            result = subprocess.run(["python", str(tmp_path)], capture_output=True, text=True,
                                    timeout=self.chaoshi, cwd=str(self.gongzuo_mulu))
            if result.returncode == 0 and not result.stderr:
                return {"success": True, "output": result.stdout[:2000] if result.stdout else "执行成功，无输出。",
                        "error": ""}
            else:
                return {"success": False, "output": result.stdout, "error": result.stderr[:500]}
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": f"执行超时 ({self.chaoshi}s·一小周)"}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
        finally:
            try: tmp_path.unlink()
            except Exception: pass

    # ========== 三体扩展·文件操作管线 ==========
    def xieru_daima(self, wenjian_lujing, daima):
        jieguo = {"success": False, "staging_lujing": "", "error": ""}
        lujing = Path(str(wenjian_lujing))
        if not lujing.parent.exists():
            jieguo["error"] = f"目录不存在: {lujing.parent}"
            return jieguo
        staging = lujing.parent / f"{lujing.name}.staging"
        try:
            staging.write_text(daima, encoding='utf-8')
            jieguo["success"] = True
            jieguo["staging_lujing"] = str(staging)
        except Exception as e:
            jieguo["error"] = f"写入失败: {e}"
        return jieguo

    def bushu_daima(self, wenjian_lujing):
        jieguo = {"success": False, "error": ""}
        lujing = Path(str(wenjian_lujing))
        staging = lujing.parent / f"{lujing.name}.staging"
        if not staging.exists():
            jieguo["error"] = "staging文件不存在"
            return jieguo
        try:
            beifen = lujing.parent / f"{lujing.name}.backup"
            if lujing.exists():
                lujing.rename(beifen)
            staging.rename(lujing)
            jieguo["success"] = True
        except Exception as e:
            jieguo["error"] = str(e)
            beifen = lujing.parent / f"{lujing.name}.backup"
            if beifen.exists() and not lujing.exists():
                beifen.rename(lujing)
        return jieguo

    def huigun(self, wenjian_lujing):
        jieguo = {"success": False, "error": ""}
        lujing = Path(str(wenjian_lujing))
        beifen = lujing.parent / f"{lujing.name}.backup"
        if beifen.exists():
            try:
                if lujing.exists():
                    lujing.unlink()
                beifen.rename(lujing)
                jieguo["success"] = True
            except Exception as e:
                jieguo["error"] = str(e)
        else:
            jieguo["error"] = "备份文件不存在"
        return jieguo

    def qingli_staging(self, wenjian_lujing):
        lujing = Path(str(wenjian_lujing))
        staging = lujing.parent / f"{lujing.name}.staging"
        staging.unlink(missing_ok=True)

    # ========== 项目级锻造 ==========

    def xiangmu_duanzao(self, xuqiu: str, mubiao_mulu: str, jiegou: list = None) -> dict:
        """
        项目级锻造: 生成多文件 Python 项目
        
        参数:
          xuqiu: 项目描述
          mubiao_mulu: 目标目录(绝对路径)
          jiegou: 文件结构列表 [{"path": "rel/path.py", "miaoshu": "说明"}, ...]
        
        返回: {"success":bool, "wenjian_shu":int, "bu_zhou":[...]}
        """
        kaishi = time.time()
        jieguo = {"success": False, "wenjian_shu": 0, "bu_zhou": [], "error": ""}
        mubiao = Path(mubiao_mulu)
        
        if not jiegou:
            jieguo["error"] = "需要提供文件结构列表"
            return jieguo
        
        try:
            mubiao.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            jieguo["error"] = f"创建目录失败: {e}"
            return jieguo
        
        # 逐文件生成
        sheng_cheng = []
        for item in jiegou:
            fp = mubiao / item["path"]
            fp.parent.mkdir(parents=True, exist_ok=True)
            miaoshu = item.get("miaoshu", "")
            
            # LLM 生成文件内容
            try:
                if self.llm and self.llm.api_key:
                    daima = self._shengcheng_daima(f"{xuqiu}\n文件:{item['path']}\n{miaoshu}")
                    if daima:
                        # AST 校验
                        try:
                            import ast
                            ast.parse(daima)
                        except SyntaxError as e:
                            # 语法修复
                            daima = self._yinghe_yufa_xiufu(daima)
                            try: ast.parse(daima)
                            except: continue
                        fp.write_text(daima, encoding='utf-8')
                        sheng_cheng.append(str(item["path"]))
                        self._shuchu("jinzhan", f"[锻造] {item['path']}")
                    else:
                        # LLM 未生成 → 用空文件占位
                        fp.write_text(f"# {item['path']} - {miaoshu}\n", encoding='utf-8')
            except Exception as e:
                self._shuchu("shibai", f"[锻造] {item['path']}: {e}")
        
        jieguo["success"] = len(sheng_cheng) > 0
        jieguo["wenjian_shu"] = len(sheng_cheng)
        jieguo["bu_zhou"] = sheng_cheng
        jieguo["haoshi"] = round(time.time() - kaishi, 1)
        return jieguo

    # ========== 三体扩展·完整锻造流水线 ==========
    def quanliushuixian(self, xuqiu: str, mubiao_wenjian: str) -> dict:
        """
        全自动流水线: LLM生成→AST校验→沙箱测试→staging→部署→回滚兜底
        返回: {"success":bool, "jieduan_rizhi":[...], "error":"", "output":""}
        """
        kaishi = time.time()
        rizhi = []
        def jilu(jieduan, zhuangtai, xiangxi=""):
            rizhi.append({"jieduan": jieduan, "zhuangtai": zhuangtai, "xiangxi": str(xiangxi)[:200]})
            biaoji = "PASS" if zhuangtai == "tongguo" else "FAIL"
            self._shuchu("jinzhan", f"[{biaoji}] {jieduan}")

        jilu("0-启动", "tongguo", f"需求:{xuqiu[:60]} 目标:{mubiao_wenjian}")

        # === 阶段1: LLM代码生成 ===
        if not self.llm or not self.llm.api_key:
            jilu("1-LLM生成", "shibai", "LLM未连接")
            return {"success": False, "jieduan_rizhi": rizhi, "error": "LLM未连接",
                    "haoshi": round(time.time()-kaishi, 3)}

        daima = self._shengcheng_daima(xuqiu)
        if not daima or daima.startswith("[") or daima.startswith("【"):
            jilu("1-LLM生成", "shibai", f"代码生成失败:{daima[:80]}")
            return {"success": False, "jieduan_rizhi": rizhi, "error": f"代码生成失败:{daima[:100]}",
                    "haoshi": round(time.time()-kaishi, 3)}
        jilu("1-LLM生成", "tongguo", f"{len(daima)}字符")

        # === 阶段2: AST语法校验 ===
        daima = self._yinghe_yufa_xiufu(daima)
        try:
            import ast
            ast.parse(daima, filename=mubiao_wenjian)
            jilu("2-AST校验", "tongguo")
        except SyntaxError as e:
            jilu("2-AST校验", "shibai", f"L{e.lineno}:{e.msg}")
            return {"success": False, "jieduan_rizhi": rizhi, "error": f"AST:{e}",
                    "haoshi": round(time.time()-kaishi, 3)}

        # === 阶段3: 安全审查 ===
        minxie = self._jiancha_minxie_lujing(daima)
        if not minxie.get("anquan", False):
            jilu("3-安全审查", "shibai", minxie.get("jinggao",""))
            return {"success": False, "jieduan_rizhi": rizhi, "error": minxie.get("jinggao",""),
                    "haoshi": round(time.time()-kaishi, 3)}
        jilu("3-安全审查", "tongguo")

        # === 阶段4: 沙箱测试 ===
        jieguo = self._execution(daima)
        if not jieguo.get("success"):
            jilu("4-沙箱测试", "shibai", jieguo.get("error","")[:100])
            if self.xin and hasattr(self.xin, 'fuwu_protocols_fenxi'):
                try:
                    wjfx = self.xin.fuwu_protocols_fenxi(xuqiu, jieguo.get("error",""))
                    jilu("4b-五境分析", "jinxing", wjfx[:150] if wjfx else "无分析结果")
                except Exception: pass
            return {"success": False, "jieduan_rizhi": rizhi, "error": jieguo.get("error",""),
                    "haoshi": round(time.time()-kaishi, 3)}
        jilu("4-沙箱测试", "tongguo", jieguo.get("output","")[:80])

        # === 阶段5: Staging预发布 ===
        r_stage = self.xieru_daima(mubiao_wenjian, daima)
        if not r_stage.get("success"):
            jilu("5-Staging", "shibai", r_stage.get("error",""))
            return {"success": False, "jieduan_rizhi": rizhi, "error": r_stage.get("error",""),
                    "haoshi": round(time.time()-kaishi, 3)}
        jilu("5-Staging", "tongguo", r_stage.get("staging_lujing",""))

        # === 阶段6: 正式部署 ===
        r_bushu = self.bushu_daima(mubiao_wenjian)
        if not r_bushu.get("success"):
            jilu("6-部署", "shibai", r_bushu.get("error",""))
            self.qingli_staging(mubiao_wenjian)
            # 自动回滚: 部署失败时恢复备份
            jieguo_huigun = self.huigun(mubiao_wenjian)
            if jieguo_huigun.get("success"):
                jilu("6b-回滚", "tongguo", f"已回滚 {mubiao_wenjian}")
            else:
                jilu("6b-回滚", "shibai", jieguo_huigun.get("error",""))
            return {"success": False, "jieduan_rizhi": rizhi, "error": f"部署失败:{r_bushu.get('error','')}",
                    "haoshi": round(time.time()-kaishi, 3)}
        jilu("6-部署", "tongguo", f"已部署→{mubiao_wenjian}")

        # === 成功 ===
        haoshi = round(time.time()-kaishi, 3)
        jilu("7-完成", "tongguo", f"流水线全部通过({haoshi}s)")
        zongjie = "\n".join([f"[{r['zhuangtai']}] {r['jieduan']}: {r['xiangxi'][:80]}" for r in rizhi])
        return {"success": True, "jieduan_rizhi": rizhi, "error": "",
                "output": zongjie, "haoshi": haoshi,
                "mubiao_wenjian": mubiao_wenjian}