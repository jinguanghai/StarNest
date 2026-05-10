
"""sync: xingchaozdd/*.py -> xingchao_code/*.py (overwrite)"""
import shutil, os, sys

SRC = r"C:\Users\jin\portable\U盘启动\xingchaozdd"
DST = r"C:\Users\jin\portable\U盘启动\xingchao_code"

SKIP = {"StarNest","__pycache__",".git",".venv","venv","ceshi_tmp"}
n = 0
for root, dirs, files in os.walk(SRC, topdown=True):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in files:
        if not f.endswith((".py",".bat",".md",".json",".txt")):
            continue
        src = os.path.join(root, f)
        rel = os.path.relpath(root, SRC)
        dst_dir = os.path.join(DST, rel)
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, os.path.join(dst_dir, f))
        n += 1

# clean pycache
for root, dirs, files in os.walk(DST):
    for d in list(dirs):
        if d == "__pycache__":
            shutil.rmtree(os.path.join(root, d), ignore_errors=True)
print(f"OK: {n} files synced")
