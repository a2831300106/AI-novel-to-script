"""导出接口路由"""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from app.config import settings
from app.utils import tasks

router = APIRouter()


@router.get("/export/{task_id}")
async def export_script(task_id: str, format: str = "yaml"):
    """导出剧本

    Args:
        task_id: 任务 ID
        format: 导出格式（yaml, json, txt）

    Returns:
        Response: 剧本文件
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks[task_id]

    if task.get("status") != "completed":
        raise HTTPException(status_code=400, detail="任务未完成")

    # 根据格式导出
    if format == "yaml":
        # 导出 YAML
        yaml_text = task.get("yaml")
        if not yaml_text:
            raise HTTPException(status_code=404, detail="YAML 结果不存在")

        return PlainTextResponse(
            content=yaml_text,
            media_type="application/x-yaml",
            headers={
                "Content-Disposition": f"attachment; filename=script.yaml"
            }
        )

    elif format == "json":
        # 导出 JSON
        import json
        result = task.get("result")
        if not result:
            raise HTTPException(status_code=404, detail="JSON 结果不存在")

        json_text = json.dumps(result, ensure_ascii=False, indent=2)

        return PlainTextResponse(
            content=json_text,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=script.json"
            }
        )

    elif format == "txt":
        # 导出 TXT（格式化剧本）
        result = task.get("result")
        if not result:
            raise HTTPException(status_code=404, detail="结果不存在")

        txt_text = format_script_as_txt(result)

        return PlainTextResponse(
            content=txt_text,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename=script.txt"
            }
        )

    else:
        raise HTTPException(status_code=400, detail="不支持的导出格式")


def format_script_as_txt(script_dict: dict) -> str:
    """将剧本格式化为 TXT 文本

    Args:
        script_dict: 剧本字典

    Returns:
        str: 格式化的文本
    """
    lines = []

    # 添加元数据
    script_meta = script_dict.get("script", {})
    lines.append("=" * 50)
    lines.append(f"剧本标题: {script_meta.get('title', '未命名')}")
    lines.append(f"原著来源: {script_meta.get('source', '未知')}")
    lines.append(f"改编作者: {script_meta.get('author', '未知')}")
    lines.append(f"创建日期: {script_meta.get('created_at', '未知')}")
    lines.append(f"故事梗概: {script_meta.get('synopsis', '无')}")
    lines.append("=" * 50)
    lines.append("\n")

    # 添加人物表
    characters = script_dict.get("characters", [])
    if characters:
        lines.append("【人物表】")
        for char in characters:
            role_map = {
                "protagonist": "主角",
                "supporting": "配角",
                "minor": "龙套",
            }
            role_text = role_map.get(char.get("role"), "未知")
            alias_text = ", ".join(char.get("alias", [])) if char.get("alias") else "无"
            lines.append(
                f"  {char.get('name')} ({role_text}) - 别名: {alias_text} - {char.get('description', '无描述')}"
            )
        lines.append("\n")

    # 添加场景表
    locations = script_dict.get("locations", [])
    if locations:
        lines.append("【场景表】")
        for loc in locations:
            type_map = {
                "interior": "内景",
                "exterior": "外景",
            }
            time_map = {
                "day": "日",
                "night": "夜",
                "dawn": "晨",
                "dusk": "暮",
            }
            type_text = type_map.get(loc.get("type"), "未知")
            time_text = time_map.get(loc.get("time"), "未知")
            lines.append(
                f"  {loc.get('name')} ({type_text}/{time_text}) - {loc.get('description', '无描述')}"
            )
        lines.append("\n")

    # 添加分集内容
    episodes = script_dict.get("episodes", [])
    for episode in episodes:
        lines.append("=" * 50)
        lines.append(f"第 {episode.get('episode')} 章: {episode.get('title')}")
        lines.append(f"简介: {episode.get('synopsis', '无')}")
        lines.append("=" * 50)
        lines.append("\n")

        scenes = episode.get("scenes", [])
        for scene in scenes:
            # 找到场景名称
            location_id = scene.get("location")
            location_name = "未知场景"
            for loc in locations:
                if loc.get("id") == location_id:
                    location_name = loc.get("name")
                    break

            lines.append(f"【场景: {location_name}】")
            lines.append(f"时间: {scene.get('time', '未知')}")
            lines.append("\n")

            beats = scene.get("beats", [])
            for beat in beats:
                beat_type = beat.get("type")

                if beat_type == "action":
                    lines.append(f"  [动作] {beat.get('content')}")

                elif beat_type == "dialogue":
                    # 找到说话人名称
                    character_id = beat.get("character")
                    character_name = "未知人物"
                    for char in characters:
                        if char.get("id") == character_id:
                            character_name = char.get("name")
                            break

                    parenthetical = beat.get("parenthetical")
                    if parenthetical:
                        lines.append(f"  {character_name}（{parenthetical}）: {beat.get('content')}")
                    else:
                        lines.append(f"  {character_name}: {beat.get('content')}")

                elif beat_type == "transition":
                    lines.append(f"  [转场] {beat.get('content')}")

                elif beat_type == "note":
                    lines.append(f"  [备注] {beat.get('content')}")

            lines.append("\n")

    return "\n".join(lines)