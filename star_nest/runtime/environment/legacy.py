"""
@legacy 豁免标记 V1.0

标记历史函数为"技术债务": 尚未迁移到害-佐协议
自审镜铁律13扫描时标记为豁免(不告警), 但新代码禁止使用
"""
def legacy(reason: str = ""):
    """
    装饰器: 标记函数为旧代码, 暂时豁免害-佐审计
    
    用法:
        @legacy("V11.0遗留代码, 待迁移")
        def some_old_func(): ...
    
    审计行为:
        - jian_cha_han_shu() 返回 is_legacy=True
        - 自审镜标记为豁免, 不告警
        - 铁律13要求: 新代码(不带@legacy)必须声明害-佐
    """
    def wrapper(fn):
        fn._legacy_ = reason or "未迁移到害-佐协议"
        return fn
    return wrapper
