import os
import glob
import fnmatch
from pathlib import Path

def sousuo_wenjian(moshi, mulu="."):
    """
    使用glob和fnmatch进行文件搜索,返回标准字典。
    
    参数:
        moshi (str): 搜索模式,支持通配符(如 *.txt, **/*.py)
        mulu (str): 搜索目录,默认为当前目录
    
    返回:
        dict: {"status": "success" 或 "error", 
               "info": 描述信息,
               "data": 匹配文件路径列表}
    """
    try:
        # 确保目录存在
        if not os.path.isdir(mulu):
            return {
                "status": "error",
                "info": f"目录不存在: {mulu}",
                "data": []
            }
        
        # 使用glob进行递归搜索
        search_path = os.path.join(mulu, moshi)
        matched_files = glob.glob(search_path, recursive=True)
        
        # 过滤掉目录,只保留文件
        file_list = []
        for f in matched_files:
            if os.path.isfile(f):
                # 转换为相对路径(相对于当前工作目录)
                rel_path = os.path.relpath(f, os.getcwd())
                file_list.append(rel_path)
        
        # 如果glob没有结果,尝试使用fnmatch进行更灵活的匹配
        if not file_list:
            file_list = []
            for root, dirs, files in os.walk(mulu):
                for filename in files:
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, os.getcwd())
                    # 使用fnmatch匹配文件名
                    if fnmatch.fnmatch(filename, os.path.basename(moshi)):
                        # 检查目录模式是否匹配
                        dir_pattern = os.path.dirname(moshi)
                        if dir_pattern:
                            rel_dir = os.path.relpath(root, mulu)
                            if fnmatch.fnmatch(rel_dir, dir_pattern):
                                file_list.append(rel_path)
                        else:
                            file_list.append(rel_path)
        
        # 去重并排序
        file_list = sorted(list(set(file_list)))
        
        return {
            "status": "success",
            "info": f"找到 {len(file_list)} 个文件",
            "data": file_list
        }
        
    except Exception as e:
        return {
            "status": "error",
            "info": f"搜索出错: {str(e)}",
            "data": []
        }


# 示例用法(可删除)
if __name__ == "__main__":
    # 测试搜索
    result = sousuo_wenjian("*.py", ".")
    print(result)