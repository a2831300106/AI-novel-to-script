"""导出接口路由"""
import os
import json
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
        format: 导出格式（yaml, json, txt, fdx, fountain, storyboard）

    Returns:
        Response: 剧本文件
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks[task_id]

    if task.get("status") != "completed":
        raise HTTPException(status_code=400, detail="任务未完成")

    result = task.get("result")
    yaml_text = task.get("yaml")

    if format == "yaml":
        if not yaml_text:
            raise HTTPException(status_code=404, detail="YAML 结果不存在")
        return PlainTextResponse(
            content=yaml_text,
            media_type="application/x-yaml",
            headers={"Content-Disposition": "attachment; filename=script.yaml"}
        )

    elif format == "json":
        if not result:
            raise HTTPException(status_code=404, detail="JSON 结果不存在")
        json_text = json.dumps(result, ensure_ascii=False, indent=2)
        return PlainTextResponse(
            content=json_text,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=script.json"}
        )

    elif format == "txt":
        if not result:
            raise HTTPException(status_code=404, detail="结果不存在")
        txt_text = format_script_as_txt(result)
        return PlainTextResponse(
            content=txt_text,
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=script.txt"}
        )

    elif format == "fdx":
        if not result:
            raise HTTPException(status_code=404, detail="结果不存在")
        fdx_text = format_script_as_fdx(result)
        return PlainTextResponse(
            content=fdx_text,
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=script.fdx"}
        )

    elif format == "fountain":
        if not result:
            raise HTTPException(status_code=404, detail="结果不存在")
        fountain_text = format_script_as_fountain(result)
        return PlainTextResponse(
            content=fountain_text,
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=script.fountain"}
        )

    elif format == "storyboard":
        if not result:
            raise HTTPException(status_code=404, detail="结果不存在")
        storyboard_text = format_script_as_storyboard(result)
        return PlainTextResponse(
            content=storyboard_text,
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=storyboard.txt"}
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


def format_script_as_fdx(script_dict: dict) -> str:
    """将剧本格式化为 Final Draft XML 格式

    Args:
        script_dict: 剧本字典

    Returns:
        str: Final Draft XML 格式字符串
    """
    from xml.etree.ElementTree import Element, SubElement, tostring
    from xml.dom import minidom

    script_meta = script_dict.get("script", {})
    characters = script_dict.get("characters", [])
    locations = script_dict.get("locations", [])
    episodes = script_dict.get("episodes", [])

    # 创建 XML 文档
    root = Element("FinalDraft", DocumentType="Script", Version="5")
    content = SubElement(root, "Content")

    # 添加标题
    title = SubElement(content, "Paragraph", Type="Scene Heading",)
    SubElement(title, "Text").text = f"{script_meta.get('title', '未命名')} - {script_meta.get('source', '')}"

    # 添加空行
    SubElement(content, "Paragraph", Type="Action")

    # 遍历所有内容
    for episode in episodes:
        # 添加章节标题
        episode_para = SubElement(content, "Paragraph", Type="Act",)
        SubElement(episode_para, "Text").text = f"第 {episode.get('episode')} 章: {episode.get('title', '')}"

        for scene in episode.get("scenes", []):
            location_id = scene.get("location")
            location_name = "未知场景"
            for loc in locations:
                if loc.get("id") == location_id:
                    location_name = loc.get("name")
                    break

            scene_time = scene.get('time', '日')
            scene_heading = SubElement(content, "Paragraph", Type="Scene Heading")
            SubElement(scene_heading, "Text").text = f"{int(scene_time == '夜')} - {location_name} - {scene_time}"

            for beat in scene.get("beats", []):
                beat_type = beat.get("type")

                if beat_type == "action":
                    para = SubElement(content, "Paragraph", Type="Action")
                    SubElement(para, "Text").text = beat.get("content", "")

                elif beat_type == "dialogue":
                    character_id = beat.get("character")
                    character_name = "未知人物"
                    for char in characters:
                        if char.get("id") == character_id:
                            character_name = char.get("name")
                            break

                    char_para = SubElement(content, "Paragraph", Type="Character")
                    SubElement(char_para, "Text").text = character_name.upper()

                    parenthetical = beat.get("parenthetical")
                    if parenthetical:
                        para = SubElement(content, "Paragraph", Type="Parenthetical")
                        SubElement(para, "Text").text = parenthetical

                    dialogue_para = SubElement(content, "Paragraph", Type="Dialogue")
                    SubElement(dialogue_para, "Text").text = beat.get("content", "")

                elif beat_type == "transition":
                    para = SubElement(content, "Paragraph", Type="Transition")
                    SubElement(para, "Text").text = beat.get("content", "")

    # 转换为字符串
    xml_str = tostring(root, encoding="unicode")
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")


def format_script_as_fountain(script_dict: dict) -> str:
    """将剧本格式化为 Fountain 格式

    Fountain 是一种简洁的纯文本剧本格式

    Args:
        script_dict: 剧本字典

    Returns:
        str: Fountain 格式字符串
    """
    lines = []

    script_meta = script_dict.get("script", {})
    characters = script_dict.get("characters", [])
    locations = script_dict.get("locations", [])
    episodes = script_dict.get("episodes", [])

    # 标题块
    lines.append(f"Title: {script_meta.get('title', '未命名')}")
    lines.append(f"Credit: 剧本")
    lines.append(f"Author: {script_meta.get('author', '未知')}")
    lines.append(f"Source: {script_meta.get('source', '')}")
    lines.append("")

    # 人物列表
    lines.append("# 人物表")
    for char in characters:
        role_map = {"protagonist": "主角", "supporting": "配角", "minor": "龙套"}
        role_text = role_map.get(char.get("role"), "")
        lines.append(f"@ {char.get('name')} | {role_text}")
    lines.append("")
    lines.append("===")
    lines.append("")

    for episode in episodes:
        lines.append(f"# 第 {episode.get('episode')} 章: {episode.get('title', '')}")
        lines.append("")

        for scene in episode.get("scenes", []):
            location_id = scene.get("location")
            location_name = "未知场景"
            for loc in locations:
                if loc.get("id") == location_id:
                    location_name = loc.get("name")
                    break

            scene_time = scene.get('time', '日')
            scene_header = f".{location_name}" if scene_time == '夜' else f".{location_name}"
            lines.append(scene_header)
            lines.append(f"@{scene_time}")
            lines.append("")

            for beat in scene.get("beats", []):
                beat_type = beat.get("type")

                if beat_type == "action":
                    lines.append(beat.get("content", ""))
                    lines.append("")

                elif beat_type == "dialogue":
                    character_id = beat.get("character")
                    character_name = "未知人物"
                    for char in characters:
                        if char.get("id") == character_id:
                            character_name = char.get("name")
                            break

                    lines.append(f"^{character_name}")

                    parenthetical = beat.get("parenthetical")
                    if parenthetical:
                        lines.append(f"({parenthetical})")

                    lines.append(beat.get("content", ""))
                    lines.append("")

                elif beat_type == "transition":
                    lines.append(f"> {beat.get('content', '')}")
                    lines.append("")

        lines.append("")

    return "\n".join(lines)


def format_script_as_storyboard(script_dict: dict) -> str:
    """将剧本格式化为分镜脚本格式

    适用于视频创作和剪辑工作流

    Args:
        script_dict: 剧本字典

    Returns:
        str: 分镜脚本格式字符串
    """
    lines = []

    script_meta = script_dict.get("script", {})
    characters = script_dict.get("characters", [])
    locations = script_dict.get("locations", [])
    episodes = script_dict.get("episodes", [])

    char_map = {c.get("id"): c for c in characters}
    loc_map = {l.get("id"): l for l in locations}

    lines.append("=" * 70)
    lines.append(f"分镜脚本 - {script_meta.get('title', '未命名')}")
    lines.append(f"原著: {script_meta.get('source', '未知')}")
    lines.append("=" * 70)
    lines.append("")

    shot_number = 1

    for episode in episodes:
        lines.append("-" * 70)
        lines.append(f"第 {episode.get('episode')} 章: {episode.get('title', '')}")
        if episode.get('synopsis'):
            lines.append(f"简介: {episode.get('synopsis')}")
        lines.append("-" * 70)
        lines.append("")

        for scene in episode.get("scenes", []):
            location_id = scene.get("location")
            location = loc_map.get(location_id, {})
            location_name = location.get("name", "未知场景")
            scene_time = scene.get('time', '日')

            lines.append("[SCENE]")
            lines.append(f"场景: {location_name}")
            lines.append(f"时间: {scene_time}")
            lines.append(f"类型: {'内景' if location.get('type') == 'interior' else '外景'}")
            lines.append("")

            scene_beats = scene.get("beats", [])

            i = 0
            while i < len(scene_beats):
                beat = scene_beats[i]
                beat_type = beat.get("type")

                if beat_type == "action":
                    action_content = beat.get("content", "")

                    if i + 1 < len(scene_beats) and scene_beats[i + 1].get("type") == "dialogue":
                        dialogue_beat = scene_beats[i + 1]
                        char_id = dialogue_beat.get("character")
                        char = char_map.get(char_id, {})

                        lines.append(f"[SHOT {shot_number}]")
                        lines.append(f"画面: {action_content}")
                        lines.append(f"台词: {char.get('name', '未知')}: {dialogue_beat.get('content', '')}")

                        parenthetical = dialogue_beat.get("parenthetical")
                        if parenthetical:
                            lines.append(f"说明: ({parenthetical})")

                        i += 2
                    else:
                        lines.append(f"[SHOT {shot_number}]")
                        lines.append(f"画面: {action_content}")
                        lines.append("台词: -")
                        i += 1

                    lines.append("景别: 中景")
                    lines.append(f"时长: 3-5秒")
                    lines.append("")
                    shot_number += 1

                elif beat_type == "transition":
                    lines.append(f"[TRANSITION]")
                    lines.append(f"转场: {beat.get('content', '')}")
                    lines.append("")
                    i += 1

                elif beat_type == "note":
                    lines.append(f"[NOTE] {beat.get('content', '')}")
                    lines.append("")
                    i += 1

                else:
                    i += 1

        lines.append(f"本章共 {shot_number} 个镜头")
        lines.append("")

    lines.append("=" * 70)
    lines.append(f"总计: {shot_number - 1} 个镜头")
    lines.append("=" * 70)

    return "\n".join(lines)