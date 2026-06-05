"""工具函数"""
from typing import Dict, Any

# 任务存储（生产环境应使用数据库）
tasks: Dict[str, Dict[str, Any]] = {}


def get_task(task_id: str) -> Dict[str, Any]:
    """获取任务信息

    Args:
        task_id: 任务 ID

    Returns:
        Dict[str, Any]: 任务信息
    """
    return tasks.get(task_id)


def set_task(task_id: str, task_data: Dict[str, Any]):
    """设置任务信息

    Args:
        task_id: 任务 ID
        task_data: 任务数据
    """
    tasks[task_id] = task_data


def delete_task(task_id: str):
    """删除任务

    Args:
        task_id: 任务 ID
    """
    if task_id in tasks:
        del tasks[task_id]