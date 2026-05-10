"""
藏剑阁·打包工具 V1.0
生成分发包·纯标准库
"""
import zipfile, os, shutil
from pathlib import Path
from datetime import datetime

def shengcheng_fenfa_bao(canshu=""):
    """生成ZIP分发包·参数:目标目录路径"""
    s = str(canshu).strip().strip('"').strip("'")
    target = Path(s) if s and Path(s).exists() else Path.cwd()
    output_name = f"xingchao_build_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    output_path = target / output_name if target.is_dir() else Path.cwd() / output_name

    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(target):
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.staging', '.backup']]
                for f in files:
                    if f.endswith(('.pyc', '.pyo', '.db-shm', '.db-wal')):
                        continue
                    fp = os.path.join(root, f)
                    arcname = os.path.relpath(fp, target.parent if target.is_file() else target)
                    zf.write(fp, arcname)
        size_mb = round(os.path.getsize(output_path) / (1024*1024), 2)
        return {"success": True, "output": str(output_path), "data": {"lujing": str(output_path), "daxiao_mb": size_mb}}
    except Exception as e:
        return {"success": False, "error": str(e)}
