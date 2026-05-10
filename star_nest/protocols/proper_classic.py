"""
正境·利剑（木）：任务注册与状态管理
V10.3.2 参数化功能分析版：内化功能分析方法论，剥离预设方案，直指可测量参数改变。

【通用问题解决操作系统·完整映射】
- 正境(Define)：register_task——定义任务类型、参数、优先级
- 反境(Measure)：task_report——任务统计，可计数的状态分布
- 合境(Improve)：update_task——任务状态流转
- 超越境(Control)：任务ID唯一性——uuid保证
- 本源境(Sustain)：标准化任务结构——脏器的共同语言

【V10.3.2 功能分析铁律】
功能定义 ≠ 方案描述。核心逻辑：主体作用于客体，改变了客体的什么可测量参数？
必须剥离用户话语中隐含的预设工具、具体做法和后续因果效应。

经典案例：
× 错误：宇航员需要一支能在太空写字的钢笔（"钢笔"是预设方案）
✓ 正确：改变记录表面的光反射参数（留下可读痕迹）

× 错误：打开deep seek官网（"打开"预设了浏览器）
✓ 正确：改变指定网址内容的访问状态参数——从"未被获取"变为"已被获取"

× 错误：电风扇的功能是吹风/降温（"吹风"是方案，"人觉得凉快"是后续因果效应）
✓ 正确：改变空气的位移参数——电风扇只负责推动空气，凉快是人体的感受，与电风扇功能无关

× 错误：系统信息（没有定义作用）
✓ 正确：改变当前运行环境的探测状态参数——从未知状态变为已知状态

剥离三步法：
1. 找主体：谁/什么系统在操作？
2. 找客体：操作的对象是什么？
3. 问核心：改变了客体的什么可测量参数？
4. 定条件：在什么环境/约束下进行？

反面检验：如果作用描述中出现了工具名、动词包含了方案预设（如"吹风""降温""打开"），说明未剥离干净。
"""

import time
import threading
import uuid
from collections import Counter

class ZhengJing:
    """正境：任务注册与状态管理——五脏共享的任务中枢"""

    TASK_TYPES = {
        'self_replicate': '自我复制',
        'self_repair': '自我修复',
        'code_execution': '代码执行',
        'spontaneous_thinking': '静息思考',
        'user_query': '用户对话',
        'protocols_analysis': '五境分析',
    }

    TASK_COMMANDS = {'task_list', 'task_detail', 'task_report'}

    def __init__(self):
        self.tasks = {}
        self.lock = threading.Lock()

    def register_task(self, task_type, params=None, priority=5):
        """正境·Define：注册新任务，返回唯一ID。
        建议 params 中包含可测量目标字段：metrics: {current: A, target: B, unit: "..."}
        """
        task_id = str(uuid.uuid4())[:8]
        with self.lock:
            self.tasks[task_id] = {
                'id': task_id, 'type': task_type, 'params': params or {},
                'status': 'pending', 'priority': priority,
                'created_at': time.time(), 'started_at': None,
                'completed_at': None, 'result': None, 'error': None
            }
        return task_id

    def update_task(self, task_id, status=None, result=None, error=None):
        """反境·Measure：更新任务状态，自动记录时间戳"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if status:
                    task['status'] = status
                    if status == 'running' and not task['started_at']:
                        task['started_at'] = time.time()
                    elif status in ('completed', 'failed'):
                        task['completed_at'] = time.time()
                if result is not None:
                    task['result'] = result
                if error is not None:
                    task['error'] = error
                return True
        return False

    def is_task_command(self, msg: str) -> bool:
        """判断是否为任务管理命令"""
        cmd = msg.strip().lstrip('/').split()[0] if msg.strip() else ''
        return cmd in self.TASK_COMMANDS

    def handle_task_command(self, cmd: str, task_id: str = None) -> str:
        """命令分发"""
        if cmd == 'task_report':
            return self._cmd_task_report()
        if cmd == 'task_list':
            return self._cmd_task_list()
        if cmd == 'task_detail':
            return self._cmd_task_detail(task_id) if task_id else "请提供任务ID。"
        return "可用: task_list | task_detail <id> | task_report"

    def _cmd_task_report(self):
        """反境·Measure：全局任务统计"""
        tasks = list(self.tasks.values())
        if not tasks:
            return "无注册任务。（提示：五脏尚未通过正境注册任务）"
        type_counts = Counter(t['type'] for t in tasks)
        wancheng = sum(1 for t in tasks if t['status'] == 'completed')
        shibai = sum(1 for t in tasks if t['status'] == 'failed')
        jinxing = sum(1 for t in tasks if t['status'] in ('pending', 'running'))
        recent = sorted(tasks, key=lambda t: t['created_at'], reverse=True)[:10]
        lines = [
            f"【任务中枢报告】总:{len(tasks)} | 完成:{wancheng} | 失败:{shibai} | 进行:{jinxing}",
            f"完成率:{wancheng/len(tasks)*100:.1f}%" if tasks else "完成率:N/A",
            "按类型:"
        ]
        for t, c in type_counts.most_common():
            lines.append(f"  {t}: {c}次")
        lines.append(f"\n最近{len(recent)}条:")
        for t in recent:
            icon = 'O' if t['status']=='completed' else ('~' if t['status'] in ('pending','running') else 'X')
            lines.append(f"  {icon} [{t['type']}] {t['status']} @ {time.ctime(t['created_at'])}")
        return "\n".join(lines)

    def _cmd_task_list(self):
        tasks = list(self.tasks.values())
        if not tasks:
            return "无注册任务。"
        return "任务列表:\n" + "\n".join(
            f"  {'O' if t['status']=='completed' else '~' if t['status'] in ('pending','running') else 'X'} {t['id']}: {t['type']} ({t['status']})"
            for t in tasks
        )

    def _cmd_task_detail(self, task_id: str):
        task = self.tasks.get(task_id)
        if task:
            return (f"任务 {task_id}:\n  类型:{task['type']}\n  状态:{task['status']}\n"
                    f"  创建:{time.ctime(task['created_at'])}\n"
                    f"  完成:{time.ctime(task['completed_at']) if task.get('completed_at') else 'N/A'}\n"
                    f"  结果:{str(task.get('result',''))[:200]}\n  错误:{task.get('error','无')}")
        return f"未找到任务 {task_id}。"