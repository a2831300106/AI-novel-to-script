"""转换接口路由"""
import asyncio
import os
from typing import Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.services import (
    NovelParser, ChapterSplitter,
    get_ai_provider, AIExtractor, ScriptGenerator
)
from app.config import settings
from app.utils import tasks

router = APIRouter()


class ConvertRequest(BaseModel):
    """转换请求"""
    task_id: str
    options: Optional[dict] = None


class ConvertProgress(BaseModel):
    """转换进度"""
    task_id: str
    status: str  # processing, completed, failed
    progress: float  # 0.0 - 1.0
    current_step: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None


async def convert_task(task_id: str, options: dict):
    """异步转换任务

    Args:
        task_id: 任务 ID
        options: 转换选项
    """
    try:
        # 获取任务信息
        if task_id not in tasks:
            return

        task = tasks[task_id]
        novel = task["novel"]

        # 更新状态
        task["status"] = "processing"
        task["progress"] = 0.0
        task["current_step"] = "extracting_characters"

        # 获取转换选项
        script_type = options.get("script_type", "series")
        ai_provider_name = options.get("ai_provider", settings.ai_provider)
        chapter_ids = options.get("chapters", None)  # None 表示全部章节

        # 筛选章节
        if chapter_ids:
            chapters = [ch for ch in novel.chapters if ch.id in chapter_ids]
        else:
            chapters = novel.chapters

        # 分割章节
        splitter = ChapterSplitter()
        chapter_contexts = splitter.split(chapters)

        # 合并所有章节文本用于提取信息
        all_text = "\n\n".join([ctx.chapter.content for ctx in chapter_contexts])

        # 尝试获取 AI 服务（如果配置了）
        ai_provider = None
        try:
            ai_provider = await get_ai_provider()
        except Exception as e:
            print(f"AI 服务未配置: {str(e)}，使用演示模式")

        # 提取人物信息
        task["current_step"] = "extracting_characters"
        extractor = AIExtractor(ai_provider)
        characters = await extractor.extract_characters(all_text)
        task["progress"] = 0.2

        # 提取场景信息
        task["current_step"] = "extracting_locations"
        locations = await extractor.extract_locations(all_text)
        task["progress"] = 0.3

        # 提取剧情线
        task["current_step"] = "extracting_storylines"
        storylines = await extractor.extract_storylines(all_text)
        task["progress"] = 0.4

        # 生成剧本
        task["current_step"] = "generating_script"
        generator = ScriptGenerator(ai_provider)

        episodes = []
        total_chapters = len(chapter_contexts)

        for i, ctx in enumerate(chapter_contexts):
            episode = await generator.generate_episode(
                ctx.chapter, characters, locations
            )
            episodes.append(episode)

            # 更新进度
            task["progress"] = 0.4 + (i + 1) / total_chapters * 0.5

        # 构建完整剧本
        script = generator.build_script(
            title=novel.title or "未命名剧本",
            source=novel.title or "未知来源",
            characters=characters,
            locations=locations,
            episodes=episodes,
            storylines=storylines,
        )

        # 转换为 YAML
        yaml_text = generator.to_yaml(script)

        # 保存结果
        task["status"] = "completed"
        task["progress"] = 1.0
        task["current_step"] = "completed"
        task["result"] = script.model_dump()
        task["yaml"] = yaml_text

        # 保存 YAML 文件
        output_dir = os.path.join(settings.output_dir, task_id)
        os.makedirs(output_dir, exist_ok=True)
        yaml_path = os.path.join(output_dir, "script.yaml")
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_text)

    except Exception as e:
        # 处理错误
        if task_id in tasks:
            task = tasks[task_id]
            task["status"] = "failed"
            task["error"] = str(e)


@router.post("/convert")
async def convert_novel(
    request: ConvertRequest,
    background_tasks: BackgroundTasks,
):
    """转换小说为剧本

    Args:
        request: 转换请求
        background_tasks: 后台任务

    Returns:
        dict: 任务状态
    """
    task_id = request.task_id

    # 检查任务是否存在
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 检查任务状态
    task = tasks[task_id]
    if task["status"] not in ["uploaded", "failed"]:
        raise HTTPException(status_code=400, detail="任务正在处理或已完成")

    # 启动后台转换任务
    options = request.options or {}
    background_tasks.add_task(convert_task, task_id, options)

    return {
        "task_id": task_id,
        "status": "processing",
        "progress": 0.0,
    }


@router.get("/convert/{task_id}/progress")
async def get_convert_progress(task_id: str):
    """获取转换进度

    Args:
        task_id: 任务 ID

    Returns:
        ConvertProgress: 转换进度
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks[task_id]

    return ConvertProgress(
        task_id=task_id,
        status=task.get("status", "unknown"),
        progress=task.get("progress", 0.0),
        current_step=task.get("current_step"),
        result=task.get("result"),
        error=task.get("error"),
    )


@router.get("/convert/{task_id}/yaml")
async def get_yaml_result(task_id: str):
    """获取 YAML 结果

    Args:
        task_id: 任务 ID

    Returns:
        dict: YAML 内容
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks[task_id]

    if task.get("status") != "completed":
        raise HTTPException(status_code=400, detail="任务未完成")

    return {
        "task_id": task_id,
        "yaml": task.get("yaml"),
    }