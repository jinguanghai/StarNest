"""
自举层 ZiJuCeng V1.0 [星巢·自我唤醒]
Phase 1: 环境检测 — Python/磁盘/网络/.env/记忆
Phase 2: 自我修复 — 缺少自动补全(下载/生成/恢复)
Phase 3: 唤醒 — 五脏就绪
Phase 4: 反馈 — 提示用户下一步操作

零外部依赖 · 插件到任何Windows机器 · 插入即用
"""
import os, sys, shutil, time, json
from pathlib import Path
from datetime import datetime


class ZiJuCeng:
    """自举层: 环境检测→自我修复→唤醒"""

    def __init__(self, xiangmu_mulu):
        self.mulu = Path(xiangmu_mulu)
        self.jian_ce_jie_guo = {}

    # ==================== Phase 1: 环境检测 ====================

    def jian_ce_huan_jing(self) -> dict:
        """五项检测: Python/磁盘/网络/配置/记忆"""
        jg = {
            "python": self._jian_ce_python(),
            "cipan": self._jian_ce_cipan(),
            "wang_luo": self._jian_ce_wang_luo(),
            "pei_zhi": self._jian_ce_pei_zhi(),
            "ji_yi": self._jian_ce_ji_yi(),
        }
        jg["quan_bu_tong_guo"] = all(
            v.get("tong_guo", False) for v in jg.values()
        )
        self.jian_ce_jie_guo = jg
        return jg

    def _jian_ce_python(self) -> dict:
        # 1. 检查自带Python
        embed = self.mulu.parent / "python" / "python.exe"
        if embed.exists():
            embed_dir = str(embed.parent)
            if embed_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = embed_dir + os.pathsep + os.environ.get("PATH", "")
            return {"tong_guo": True, "ban_ben": "embed 3.12", "lujing": str(embed),
                    "lai_yuan": "自带Python"}
        # 2. 检查系统Python
        try:
            v = sys.version_info
            return {"tong_guo": True, "ban_ben": f"{v.major}.{v.minor}.{v.micro}", "lujing": sys.executable}
        except Exception: pass
        # 3. 尝试查找
        for name in ["python", "python3", "py"]:
            try:
                import subprocess as _sp
                r = _sp.run([name, "--version"], capture_output=True, timeout=5)
                if r.returncode == 0:
                    return {"tong_guo": True, "ban_ben": r.stdout.decode().strip(), "lujing": name}
            except Exception: pass
        return {"tong_guo": False, "cuo_wu": "Python未找到。下载Python嵌入版? (python rukou.py --download-python)"}

    def _jian_ce_cipan(self) -> dict:
        try:
            usage = shutil.disk_usage(str(self.mulu.anchor))
            free_mb = usage.free // (1024 * 1024)
            return {"tong_guo": free_mb > 200, "kong_xian_mb": free_mb,
                    "zong_mb": usage.total // (1024 * 1024)}
        except Exception:
            return {"tong_guo": True, "cuo_wu": "无法检测"}

    def _jian_ce_wang_luo(self) -> dict:
        try:
            import urllib.request
            urllib.request.urlopen("https://www.python.org", timeout=5)
            return {"tong_guo": True, "mu_biao": "python.org"}
        except Exception:
            return {"tong_guo": False, "cuo_wu": "网络不可用, 将使用离线模式"}

    def _jian_ce_pei_zhi(self) -> dict:
        env_path = self.mulu / "huanjing" / ".env"
        if env_path.exists():
            content = env_path.read_text(encoding='utf-8', errors='ignore')
            has_key = "DEEPSEEK_API_KEY" in content and "sk-" in content
            return {"tong_guo": has_key or "HUOSHAN" in content,
                    "wen_jian_cun_zai": True,
                    "api_key_you_xiao": has_key}
        return {"tong_guo": False, "wen_jian_cun_zai": False,
                "cuo_wu": ".env缺失, 需配置API密钥"}

    def _jian_ce_ji_yi(self) -> dict:
        db_paths = [
            self.mulu / "changqi_jiyi.db",
            self.mulu / "shared_memory" / "changqi_jiyi.db",
        ]
        for db in db_paths:
            if db.exists():
                size = db.stat().st_size
                return {"tong_guo": True, "lujing": str(db),
                        "da_xiao_kb": size // 1024}
        # 尝试自动搜索恢复
        recovered = self._sou_suo_ji_yi()
        if recovered:
            return {"tong_guo": True, "lai_yuan": "恢复", "lujing": recovered}
        return {"tong_guo": True, "cuo_wu": "首次启动, 无记忆数据(正常)"}

    def _sou_suo_ji_yi(self):
        """自动搜索备份目录中的记忆文件"""
        search_paths = [
            Path.home() / "backup",
            Path("D:/backup"),
            Path("E:/backup"),
            self.mulu.parent / "backup",
        ]
        for sp in search_paths:
            if not sp.exists():
                continue
            for db in sp.rglob("changqi_jiyi.db"):
                try:
                    target = self.mulu / "changqi_jiyi.db"
                    shutil.copy2(db, target)
                    return str(db)
                except Exception: pass
        return None

    # ==================== Phase 2: 自我修复 ====================

    def zi_wo_xiu_fu(self, jian_ce: dict = None) -> dict:
        """缺什么补什么: 生成配置/恢复记忆"""
        if jian_ce is None:
            jian_ce = self.jian_ce_jie_guo

        xiu_fu_rizhi = []

        # 生成.env模板
        pei_zhi = jian_ce.get("pei_zhi", {})
        if not pei_zhi.get("wen_jian_cun_zai"):
            self._sheng_cheng_env_mo_ban()
            xiu_fu_rizhi.append("已生成.env模板, 请填写API密钥")

        # 记忆恢复
        ji_yi = jian_ce.get("ji_yi", {})
        if ji_yi.get("lai_yuan") == "恢复":
            xiu_fu_rizhi.append(f"记忆已从备份恢复: {ji_yi.get('lujing')}")

        return {"xiu_fu_shu": len(xiu_fu_rizhi), "xiu_fu_xiang": xiu_fu_rizhi}

    def _sheng_cheng_env_mo_ban(self):
        """生成.env和.env.example模板"""
        env_dir = self.mulu / "huanjing"
        env_dir.mkdir(parents=True, exist_ok=True)

        example = env_dir / ".env.example"
        if not example.exists():
            example.write_text(
                "DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n"
                "HUOSHAN_API_KEY=\n"
                "DEFAULT_MODEL=deepseek-chat\n",
                encoding='utf-8'
            )

        env = env_dir / ".env"
        if not env.exists():
            env.write_text(
                "DEEPSEEK_API_KEY=\nHUOSHAN_API_KEY=\nDEFAULT_MODEL=deepseek-chat\n",
                encoding='utf-8'
            )

    # ==================== Python Embeddable 下载 ====================

    def xia_zai_python_embed(self) -> dict:
        """下载Python 3.12嵌入版到项目目录"""
        import urllib.request
        import zipfile

        target_dir = self.mulu.parent / "python"
        target_dir.mkdir(parents=True, exist_ok=True)

        url = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip"
        zip_path = target_dir / "python-embed.zip"

        print(f"[自举] 下载Python嵌入版...")
        print(f"  源: {url}")
        print(f"  目标: {target_dir}")

        try:
            urllib.request.urlretrieve(url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(target_dir)
            zip_path.unlink()  # 删除zip
            python_exe = target_dir / "python.exe"
            if python_exe.exists():
                # 修改 python312._pth 以包含标准库路径
                pth_file = target_dir / "python312._pth"
                if pth_file.exists():
                    content = pth_file.read_text(encoding='utf-8')
                    if "import site" not in content:
                        content += "\nimport site\n"
                        pth_file.write_text(content, encoding='utf-8')
                print(f"[自举] Python嵌入版安装完成: {python_exe}")
                return {"success": True, "lujing": str(python_exe)}
            return {"success": False, "error": "下载完成但python.exe未找到"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== Phase 3: 唤醒 ====================

    def huan_xing(self) -> bool:
        """唤醒五脏: 导入SanTiXiTong → 三体启动"""
        try:
            from star_nest.entry import SanTiXiTong
            self.xitong = SanTiXiTong()
            print(f"[自举] SanTiXiTong 初始化完成")
            return True
        except Exception as e:
            print(f"[自举] 唤醒失败: {e}")
            return False

    # ==================== 一站式 ====================

    def zi_ju(self) -> dict:
        """自举入口: 检测→修复→唤醒"""
        kaishi = time.time()
        bao_gao = []

        # Phase 1
        print("=" * 50)
        print("  星巢自举层 V1.0 · 环境检测")
        print("=" * 50)
        jian_ce = self.jian_ce_huan_jing()
        for k, v in jian_ce.items():
            if k == "quan_bu_tong_guo":
                continue
            zhuang_tai = "✓" if v.get("tong_guo") else "✗"
            xiang_qing = v.get("ban_ben") or v.get("cuo_wu") or ""
            kong_xian = v.get("kong_xian_mb", "")
            info = f"{kong_xian}MB可用" if kong_xian else xiang_qing
            print(f"  [{zhuang_tai}] {k}: {info}")
            if not v.get("tong_guo") and k != "ji_yi":
                bao_gao.append(f"缺{k}: {xiang_qing}")

        # Phase 2
        xiu_fu = self.zi_wo_xiu_fu(jian_ce)
        if xiu_fu["xiu_fu_shu"] > 0:
            print(f"\n  修复: {', '.join(xiu_fu['xiu_fu_xiang'])}")

        # 关键缺失→不启动
        if not jian_ce.get("python", {}).get("tong_guo"):
            print("\n  [✗] Python未找到, 无法启动")
            print("  请安装Python 3.12: https://www.python.org/downloads/")
            return {"success": False, "error": "Python未安装", "jian_ce": jian_ce}

        if not jian_ce.get("pei_zhi", {}).get("tong_guo"):
            print("\n  [!] 请编辑 huanjing/.env 填入 DEEPSEEK_API_KEY 后重新运行")
            if jian_ce.get("wang_luo", {}).get("tong_guo"):
                print("  注册: https://platform.deepseek.com/api_keys")

        # Phase 3
        print(f"\n  唤醒中...")
        ok = self.huan_xing()
        if not ok:
            return {"success": False, "error": "唤醒失败", "jian_ce": jian_ce}

        # Phase 4
        haoshi = round(time.time() - kaishi, 1)
        print(f"\n  自举完成: {haoshi}s")
        print("=" * 50)

        return {
            "success": True,
            "jian_ce": jian_ce,
            "xiu_fu": xiu_fu,
            "haoshi": haoshi,
            "bao_gao": bao_gao,
        }

    def qu_bao_gao(self):
        return self.jian_ce_jie_guo
