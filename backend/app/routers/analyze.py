"""剧本分析接口路由"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Tuple, List
from app.services import ScriptAnalyzer
from app.models import Character
from app.utils import tasks

router = APIRouter()


def get_completed_task(task_id: str) -> Dict[str, Any]:
    """获取已完成的任务，带验证"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks[task_id]

    if task.get("status") != "completed":
        raise HTTPException(status_code=400, detail="任务未完成")

    result = task.get("result")
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    return result


def prepare_analysis(task_id: str) -> Tuple[Dict[str, Any], List[Character], ScriptAnalyzer]:
    """公共分析准备逻辑：获取任务、转换角色列表、创建分析器"""
    result = get_completed_task(task_id)
    characters_data = result.get("characters", [])
    characters = [Character(**c) for c in characters_data]
    analyzer = ScriptAnalyzer()
    return result, characters, analyzer


@router.get("/analyze/{task_id}")
async def analyze_script(task_id: str):
    result, characters, analyzer = prepare_analysis(task_id)
    return analyzer.generate_analysis_report(characters, result)


@router.get("/analyze/{task_id}/relationships")
async def analyze_character_relationships(task_id: str):
    result, characters, analyzer = prepare_analysis(task_id)
    return analyzer.analyze_character_relationships(characters, result)


@router.get("/analyze/{task_id}/rhythm")
async def analyze_plot_rhythm(task_id: str):
    result, characters, analyzer = prepare_analysis(task_id)
    return analyzer.analyze_plot_rhythm(result)


@router.get("/analyze/{task_id}/dialogue")
async def analyze_dialogue_style(task_id: str):
    result, characters, analyzer = prepare_analysis(task_id)
    return analyzer.analyze_dialogue_style(characters, result)