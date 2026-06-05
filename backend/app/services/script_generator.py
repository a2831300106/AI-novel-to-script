"""剧本生成服务

将小说文本转换为 YAML 格式的剧本
"""
import yaml
import re
from typing import List, Dict, Any, Optional
from app.models import (
    Script, ScriptMeta, Character, Location,
    Beat, Scene, Episode, Storyline, Chapter
)
from app.services.ai_provider import AIProvider
from app.config import settings


class ScriptGenerator:
    """剧本生成器"""

    # 剧本生成 Prompt
    SCRIPT_GENERATION_PROMPT = """你是一个专业的剧本编剧。请将以下小说片段转换为 YAML 格式的剧本。

要求：
1. 将叙述转换为动作描述（action）
2. 识别对话并标注说话人
3. 为场景添加时间和地点信息
4. 适当添加转场说明（transition）
5. 每个节拍（beat）都要有明确的类型

人物列表：
{characters}

场景列表：
{locations}

输出 YAML 格式示例：
scenes:
  - scene_id: "scene_001"
    location: "loc_001"
    time: "day"
    beats:
      - beat_id: "beat_001"
        type: "action"
        content: "动作描述"
        characters: ["char_001"]
      - beat_id: "beat_002"
        type: "dialogue"
        character: "char_001"
        parenthetical: "语气说明"
        content: "台词内容"
        characters: ["char_001"]
      - beat_id: "beat_003"
        type: "transition"
        content: "切至"

小说片段：
{text}
"""

    def __init__(self, ai_provider: AIProvider = None):
        """初始化剧本生成器

        Args:
            ai_provider: AI 服务提供商（可选，如果为 None 则使用本地生成）
        """
        self.ai_provider = ai_provider

    async def generate_episode(
        self,
        chapter: Chapter,
        characters: List[Character],
        locations: List[Location],
    ) -> Episode:
        """生成章节剧本

        Args:
            chapter: 章节对象
            characters: 人物列表
            locations: 场景列表

        Returns:
            Episode: 章节剧本
        """
        # 如果有 AI 服务，尝试使用 AI 生成
        if self.ai_provider:
            try:
                # 构建人物列表文本
                characters_text = self._build_characters_text(characters)

                # 构建场景列表文本
                locations_text = self._build_locations_text(locations)

                # 构建 Prompt
                prompt = self.SCRIPT_GENERATION_PROMPT.format(
                    characters=characters_text,
                    locations=locations_text,
                    text=chapter.content[:2000],  # 限制长度
                )

                # 调用 AI 生成剧本
                result = await self.ai_provider.chat_with_yaml(prompt)

                # 解析场景列表
                scenes = []
                for scene_data in result.get("scenes", []):
                    beats = []
                    for beat_data in scene_data.get("beats", []):
                        beats.append(Beat(
                            beat_id=beat_data.get("beat_id", f"beat_{len(beats)+1:03d}"),
                            type=beat_data.get("type", "action"),
                            content=beat_data.get("content", ""),
                            character=beat_data.get("character"),
                            parenthetical=beat_data.get("parenthetical"),
                            characters=beat_data.get("characters", []),
                        ))

                    scenes.append(Scene(
                        scene_id=scene_data.get("scene_id", f"scene_{len(scenes)+1:03d}"),
                        location=scene_data.get("location", locations[0].id if locations else "loc_001"),
                        time=scene_data.get("time"),
                        beats=beats,
                    ))

                if scenes:
                    return Episode(
                        episode=chapter.id,
                        title=chapter.title,
                        synopsis=f"本章共 {chapter.word_count} 字",
                        scenes=scenes,
                    )
            except Exception as e:
                print(f"AI 剧本生成失败: {str(e)}，使用本地生成")

        # 本地生成（演示模式）
        return self._create_local_episode(chapter, characters, locations)

    def _create_local_episode(
        self,
        chapter: Chapter,
        characters: List[Character],
        locations: List[Location],
    ) -> Episode:
        """本地生成剧本（演示模式）

        Args:
            chapter: 章节对象
            characters: 人物列表
            locations: 场景列表

        Returns:
            Episode: 章节剧本
        """
        beats = []
        beat_id = 1
        
        # 获取默认场景
        location_id = locations[0].id if locations else "loc_001"
        
        # 提取对话和动作
        # 匹配中文引号内的对话
        dialogue_pattern = r'"([^"]+)"'
        
        # 分割文本
        paragraphs = chapter.content.split('\n')
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 查找对话
            dialogues = re.findall(dialogue_pattern, para)
            
            if dialogues:
                # 提取对话前的动作描述
                for dialogue in dialogues:
                    # 尝试匹配说话人
                    speaker_pattern = r'([^\s"。，！？]+)[说道问答感叹]'
                    speaker_match = re.search(speaker_pattern, para)
                    
                    # 查找对应的人物
                    character_id = None
                    if speaker_match:
                        speaker_name = speaker_match.group(1)
                        for char in characters:
                            if char.name == speaker_name or speaker_name in char.alias:
                                character_id = char.id
                                break
                    
                    if character_id:
                        beats.append(Beat(
                            beat_id=f"beat_{beat_id:03d}",
                            type="dialogue",
                            character=character_id,
                            content=dialogue,
                            characters=[character_id],
                        ))
                    else:
                        beats.append(Beat(
                            beat_id=f"beat_{beat_id:03d}",
                            type="dialogue",
                            character=characters[0].id if characters else "char_001",
                            content=dialogue,
                            characters=[characters[0].id if characters else "char_001"],
                        ))
                    beat_id += 1
            else:
                # 作为动作描述
                if len(para) > 10:  # 过滤太短的段落
                    beats.append(Beat(
                        beat_id=f"beat_{beat_id:03d}",
                        type="action",
                        content=para[:200],  # 限制长度
                        characters=[],
                    ))
                    beat_id += 1
        
        # 添加转场
        beats.append(Beat(
            beat_id=f"beat_{beat_id:03d}",
            type="transition",
            content="切至",
            characters=[],
        ))
        
        # 如果没有生成任何节拍，添加默认内容
        if not beats:
            beats.append(Beat(
                beat_id="beat_001",
                type="action",
                content=chapter.content[:500] + "...",
                characters=[],
            ))
        
        # 创建场景
        scene = Scene(
            scene_id="scene_001",
            location=location_id,
            time="day",
            beats=beats,
        )

        return Episode(
            episode=chapter.id,
            title=chapter.title,
            synopsis=f"本章共 {chapter.word_count} 字",
            scenes=[scene],
        )

    def _create_basic_episode(self, chapter: Chapter) -> Episode:
        """创建基础剧本结构（当 AI 生成失败时）

        Args:
            chapter: 章节对象

        Returns:
            Episode: 基础剧本
        """
        # 创建一个简单的场景
        scene = Scene(
            scene_id="scene_001",
            location="loc_001",
            time="day",
            beats=[
                Beat(
                    beat_id="beat_001",
                    type="action",
                    content=chapter.content[:500] + "...",
                    characters=[],
                )
            ]
        )

        return Episode(
            episode=chapter.id,
            title=chapter.title,
            synopsis=f"本章共 {chapter.word_count} 字",
            scenes=[scene],
        )

    def _build_characters_text(self, characters: List[Character]) -> str:
        """构建人物列表文本

        Args:
            characters: 人物列表

        Returns:
            str: 人物列表文本
        """
        lines = []
        for char in characters:
            alias_str = ", ".join(char.alias) if char.alias else "无"
            lines.append(
                f"- {char.id}: {char.name}（别名: {alias_str}, 角色: {char.role}, 描述: {char.description or '无'}）"
            )
        return "\n".join(lines)

    def _build_locations_text(self, locations: List[Location]) -> str:
        """构建场景列表文本

        Args:
            locations: 场景列表

        Returns:
            str: 场景列表文本
        """
        lines = []
        for loc in locations:
            lines.append(
                f"- {loc.id}: {loc.name}（类型: {loc.type}, 时间: {loc.time}, 描述: {loc.description or '无'}）"
            )
        return "\n".join(lines)

    def build_script(
        self,
        title: str,
        source: str,
        characters: List[Character],
        locations: List[Location],
        episodes: List[Episode],
        storylines: List[Storyline] = None,
    ) -> Script:
        """构建完整剧本

        Args:
            title: 剧本标题
            source: 原著来源
            characters: 人物列表
            locations: 场景列表
            episodes: 章节列表
            storylines: 剧情线列表

        Returns:
            Script: 完整剧本
        """
        # 创建剧本元数据
        script_meta = ScriptMeta(
            version="1.0",
            type="series",
            title=title,
            source=source,
            author="AI 改编",
            created_at=self._get_current_date(),
            synopsis=f"共 {len(episodes)} 章",
        )

        # 创建完整剧本
        return Script(
            script=script_meta,
            characters=characters,
            locations=locations,
            episodes=episodes,
            storylines=storylines or [],
        )

    def to_yaml(self, script: Script) -> str:
        """将剧本转换为 YAML 格式

        Args:
            script: 剧本对象

        Returns:
            str: YAML 格式文本
        """
        # 使用 Pydantic 的 model_dump 方法转换为字典
        script_dict = script.model_dump()

        # 转换为 YAML
        yaml_text = yaml.dump(
            script_dict,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )

        return yaml_text

    def _get_current_date(self) -> str:
        """获取当前日期

        Returns:
            str: 当前日期字符串
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")