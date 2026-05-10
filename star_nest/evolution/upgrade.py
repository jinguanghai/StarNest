import shutil
import pathlib
import datetime
import os

def beifen_dangqian_banben(xiangmu_mulu, beifen_mulu):
    xiangmu = pathlib.Path(xiangmu_mulu)
    beifen = pathlib.Path(beifen_mulu)
    beifen.mkdir(parents=True, exist_ok=True)
    shijian = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    mubiao = beifen / f"beifen_{shijian}"
    shutil.copytree(xiangmu, mubiao)
    return mubiao

def tihuan_wei_fuben(xiangmu_mulu, beifen_mulu, beifen_mingcheng=None):
    xiangmu = pathlib.Path(xiangmu_mulu)
    beifen = pathlib.Path(beifen_mulu)
    if beifen_mingcheng is None:
        beifen_liebiao = sorted(beifen.iterdir(), key=os.path.getmtime, reverse=True)
        if not beifen_liebiao:
            raise FileNotFoundError("没有找到备份")
        yuan = beifen_liebiao[0]
    else:
        yuan = beifen / beifen_mingcheng
        if not yuan.exists():
            raise FileNotFoundError(f"备份 {beifen_mingcheng} 不存在")
    if xiangmu.exists():
        shutil.rmtree(xiangmu)
    shutil.copytree(yuan, xiangmu)

def huidao_banben(xiangmu_mulu, beifen_mulu, beifen_mingcheng):
    tihuan_wei_fuben(xiangmu_mulu, beifen_mulu, beifen_mingcheng)

def qingli_jiu_beifen(beifen_mulu, baoliu_geshu=5):
    beifen = pathlib.Path(beifen_mulu)
    if not beifen.exists():
        return
    beifen_liebiao = sorted(beifen.iterdir(), key=os.path.getmtime, reverse=True)
    if len(beifen_liebiao) > baoliu_geshu:
        for wenjian in beifen_liebiao[baoliu_geshu:]:
            if wenjian.is_dir():
                shutil.rmtree(wenjian)
            else:
                wenjian.unlink()