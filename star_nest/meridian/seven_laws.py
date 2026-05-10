"""
七律·时间节律感知器 V2.0
穹顶单子统一对时——数字谱系 7=2³-1
阴阳(2)在三维(3)中演化的周期边界
"""
class QiLv:
    LV_JI = {
        "yixi":       {"beishu": 1,      "miaoshu": "一息"},
        "yiweizhou":  {"beishu": 7,      "miaoshu": "一微周"},
        "yixiaozhou": {"beishu": 49,     "miaoshu": "一小周"},
        "yizhongzhou":{"beishu": 343,    "miaoshu": "一中周"},
        "yidazhou":   {"beishu": 2401,   "miaoshu": "一大周"},
        "yizhoutian": {"beishu": 16807,  "miaoshu": "一周天"},
        "yijiyuan":   {"beishu": 117649, "miaoshu": "一纪元"},
    }

    def qu_chaoshi(self, lv_ji: str) -> int:
        return self.LV_JI.get(lv_ji, {}).get("beishu", 30)

    def qu_zhouqi(self, lv_ji: str) -> int:
        return self.LV_JI.get(lv_ji, {}).get("beishu", 60)

    def qu_miaoshu(self, lv_ji: str) -> str:
        return self.LV_JI.get(lv_ji, {}).get("miaoshu", "未知")

    def suoyou_lvji(self):
        return list(self.LV_JI.keys())
