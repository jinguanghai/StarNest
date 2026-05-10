import subprocess
import os

def git_mingling(mingling, mulu):
    """
    执行git命令并返回标准字典结果
    :param mingling: list, git命令参数列表,例如 ['status']
    :param mulu: str, 执行命令的工作目录
    :return: dict, 包含 'success', 'output', 'error', 'returncode'
    """
    try:
        result = subprocess.run(
            ['git'] + mingling,
            cwd=mulu,
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'error': result.stderr.strip(),
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': '命令执行超时',
            'returncode': -1
        }
    except FileNotFoundError:
        return {
            'success': False,
            'output': '',
            'error': '未找到git命令或目录不存在',
            'returncode': -2
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'returncode': -3
        }