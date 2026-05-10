import shutil
import json
from pathlib import Path
from typing import List, Optional


class ZiWoFuZhi:
    def __init__(self, xiangmu_mulu: str):
        self.xiangmu_mulu = Path(xiangmu_mulu).resolve()
        self.paichu_guize: List[str] = []

    def shezhi_paichu(self, guize_liebiao: List[str]) -> None:
        self.paichu_guize = guize_liebiao

    def _yinggai_paichu(self, lu_jing: Path) -> bool:
        for guize in self.paichu_guize:
            if lu_jing.match(guize) or guize in str(lu_jing):
                return True
        return False

    def fuzhi(self, mubiao_mingcheng: str, mubiao_mulu: str, baohan_env: bool = False) -> Path:
        mubiao_lu = Path(mubiao_mulu).resolve() / mubiao_mingcheng
        if mubiao_lu.exists():
            shutil.rmtree(mubiao_lu)
        shutil.copytree(
            self.xiangmu_mulu,
            mubiao_lu,
            ignore=lambda src, names: [
                n for n in names
                if self._yinggai_paichu(Path(src) / n) or (not baohan_env and n in ('.env', 'venv', '__pycache__'))
            ]
        )
        return mubiao_lu

    def fuzhi_yongyu_fenfa(self, mubiao_mulu: str, baohan_env: bool = False) -> Path:
        mubiao_lu = Path(mubiao_mulu).resolve() / f"{self.xiangmu_mulu.name}_fenfa"
        if mubiao_lu.exists():
            shutil.rmtree(mubiao_lu)
        shutil.copytree(
            self.xiangmu_mulu,
            mubiao_lu,
            ignore=lambda src, names: [
                n for n in names
                if self._yinggai_paichu(Path(src) / n) or n in ('.git', '__pycache__', 'venv', '.env') or (not baohan_env and n in ('.env', 'venv'))
            ]
        )
        return mubiao_lu

    def liechu_fuben(self, mubiao_mulu: str) -> List[Path]:
        mu_lu = Path(mubiao_mulu).resolve()
        if not mu_lu.exists():
            return []
        return [p for p in mu_lu.iterdir() if p.is_dir() and p.name.startswith(self.xiangmu_mulu.name)]

    def shanchu_fuben(self, mubiao_mulu: str, fuben_mingcheng: str) -> bool:
        fuben_lu = Path(mubiao_mulu).resolve() / fuben_mingcheng
        if fuben_lu.exists() and fuben_lu.is_dir():
            shutil.rmtree(fuben_lu)
            return True
        return False

    def baocun_peizhi(self, wenjian_lu: str) -> None:
        peizhi = {
            "xiangmu_mulu": str(self.xiangmu_mulu),
            "paichu_guize": self.paichu_guize
        }
        with open(wenjian_lu, 'w', encoding='utf-8') as f:
            json.dump(peizhi, f, ensure_ascii=False, indent=2)

    def jiazai_peizhi(self, wenjian_lu: str) -> None:
        with open(wenjian_lu, 'r', encoding='utf-8') as f:
            peizhi = json.load(f)
        self.xiangmu_mulu = Path(peizhi["xiangmu_mulu"]).resolve()
        self.paichu_guize = peizhi["paichu_guize"]