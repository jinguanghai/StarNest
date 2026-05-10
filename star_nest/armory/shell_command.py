import subprocess
import sys
import os
import signal
import time
import json
import shlex
import threading
from typing import Dict, Any, Optional, Union, List

def execution_mingling(mingling: Union[str, List[str]], chaoshi: Optional[float] = None) -> Dict[str, Any]:
    """
    执行Shell命令并返回标准字典结果。
    
    参数:
        mingling: 命令字符串或命令列表
        chaoshi: 超时时间(秒),None表示无超时
        
    返回:
        字典包含: stdout, stderr, returncode, success, error
    """
    result = {
        "stdout": "",
        "stderr": "",
        "returncode": -1,
        "success": False,
        "error": None
    }
    
    try:
        # 处理命令格式
        if isinstance(mingling, str):
            if sys.platform == "win32":
                cmd_list = mingling
            else:
                cmd_list = shlex.split(mingling)
        elif isinstance(mingling, list):
            cmd_list = mingling
        else:
            result["error"] = "命令必须是字符串或列表"
            return result
        
        # 创建进程
        process = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=(sys.platform == "win32" and isinstance(mingling, str)),
            text=True,
            encoding=sys.getdefaultencoding() or "utf-8",
            errors="replace"
        )
        
        # 处理超时
        if chaoshi is not None and chaoshi > 0:
            try:
                stdout, stderr = process.communicate(timeout=chaoshi)
                result["stdout"] = stdout or ""
                result["stderr"] = stderr or ""
                result["returncode"] = process.returncode
                result["success"] = (process.returncode == 0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                result["error"] = f"命令执行超时({chaoshi}秒)"
                result["stdout"] = ""
                result["stderr"] = "进程已终止"
                result["returncode"] = -2
        else:
            stdout, stderr = process.communicate()
            result["stdout"] = stdout or ""
            result["stderr"] = stderr or ""
            result["returncode"] = process.returncode
            result["success"] = (process.returncode == 0)
            
    except FileNotFoundError as e:
        result["error"] = f"命令未找到: {str(e)}"
    except PermissionError as e:
        result["error"] = f"权限不足: {str(e)}"
    except OSError as e:
        result["error"] = f"系统错误: {str(e)}"
    except Exception as e:
        result["error"] = f"未知错误: {str(e)}"
    
    return result


def execution_mingling_async(mingling: Union[str, List[str]], chaoshi: Optional[float] = None) -> Dict[str, Any]:
    """
    异步执行命令(非阻塞版本),使用线程实现。
    返回结果与execution_mingling相同。
    """
    result_container = {}
    exception_container = []
    
    def target():
        try:
            res = execution_mingling(mingling, chaoshi)
            result_container["result"] = res
        except Exception as e:
            exception_container.append(e)
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout=chaoshi if chaoshi else None)
    
    if exception_container:
        return {
            "stdout": "",
            "stderr": "",
            "returncode": -3,
            "success": False,
            "error": str(exception_container[0])
        }
    
    if "result" in result_container:
        return result_container["result"]
    else:
        return {
            "stdout": "",
            "stderr": "线程未完成",
            "returncode": -4,
            "success": False,
            "error": "执行超时或线程异常"
        }


def anquan_execution(mingling: str, chaoshi: Optional[float] = None, max_output: int = 1048576) -> Dict[str, Any]:
    """
    安全执行命令,限制输出大小防止内存溢出。
    """
    result = execution_mingling(mingling, chaoshi)
    
    if len(result["stdout"]) > max_output:
        result["stdout"] = result["stdout"][:max_output] + "\n... [输出截断]"
        result["error"] = (result["error"] or "") + "输出超过限制"
    
    if len(result["stderr"]) > max_output:
        result["stderr"] = result["stderr"][:max_output] + "\n... [错误截断]"
    
    return result


if __name__ == "__main__":
    # 简单测试
    test_result = execution_mingling("echo Hello World", 5)
    print(json.dumps(test_result, ensure_ascii=False, indent=2))