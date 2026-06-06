"""智能剧本分析服务

提供角色关系图谱、剧情节奏分析和对话风格分析功能
"""
import re
from typing import List, Dict, Any, Optional
from collections import defaultdict
from app.models import Character, Storyline


class ScriptAnalyzer:
    """剧本分析器"""

    CLIMAX_KEYWORDS = [
        "冲突", "爆发", "对决", "真相", "揭穿", "质问",
        "决斗", "表白", "决裂", "选择", "牺牲", "死亡",
        "车祸", "火灾", "爆炸", "搏斗", "崩溃",
        "揭露", "暴露", "发现", "恍然大悟",
        "对抗", "对峙", "摊牌", "翻脸", "决一死战"
    ]

    EMOTION_KEYWORDS = {
        "high": ["愤怒", "咆哮", "尖叫", "哭泣", "大笑", "激动", "颤抖", "绝望"],
        "medium": ["叹气", "沉默", "犹豫", "低声", "平静", "微笑"],
        "low": ["点头", "摇头", "轻声", "慢慢", "淡淡"]
    }

    def __init__(self):
        pass

    def analyze_character_relationships(
        self,
        characters: List[Character],
        script_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        relationships = []
        co_occurrence = defaultdict(set)

        for episode in script_data.get("episodes", []):
            for scene in episode.get("scenes", []):
                scene_chars = set()
                for beat in scene.get("beats", []):
                    if beat.get("type") == "dialogue":
                        char_id = beat.get("character")
                        if char_id:
                            scene_chars.add(char_id)
                    for char_id in beat.get("characters", []):
                        scene_chars.add(char_id)

                for char_id in scene_chars:
                    co_occurrence[char_id].update(scene_chars - {char_id})

        char_map = {c.id: c for c in characters}
        for char_id, co_chars in co_occurrence.items():
            for co_char_id in co_chars:
                if char_id < co_char_id:
                    char1 = char_map.get(char_id)
                    char2 = char_map.get(co_char_id)
                    if char1 and char2:
                        relationships.append({
                            "source": char1.name,
                            "target": char2.name,
                            "type": "related",
                            "strength": min(3, len(co_occurrence[char_id]) + len(co_occurrence[co_char_id]))
                        })

        return {
            "nodes": [
                {
                    "id": c.id,
                    "name": c.name,
                    "role": c.role,
                    "description": c.description
                }
                for c in characters
            ],
            "links": relationships
        }

    def analyze_plot_rhythm(
        self,
        script_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        episode_analysis = []
        climax_points = []

        for episode in script_data.get("episodes", []):
            episode_num = episode.get("episode")
            total_beats = 0
            action_count = 0
            dialogue_count = 0
            emotion_intensity = []

            for scene in episode.get("scenes", []):
                for beat in scene.get("beats", []):
                    total_beats += 1
                    content = beat.get("content", "")

                    if beat.get("type") == "action":
                        action_count += 1
                        intensity = self._calculate_emotion_intensity(content)
                        emotion_intensity.append(intensity)

                        if any(kw in content for kw in self.CLIMAX_KEYWORDS):
                            climax_points.append({
                                "episode": episode_num,
                                "scene": scene.get("scene_id"),
                                "beat": beat.get("beat_id"),
                                "content": content[:100],
                                "type": "action_climax"
                            })

                    elif beat.get("type") == "dialogue":
                        dialogue_count += 1
                        intensity = self._calculate_emotion_intensity(content)
                        emotion_intensity.append(intensity)

                        if any(kw in content for kw in self.CLIMAX_KEYWORDS):
                            climax_points.append({
                                "episode": episode_num,
                                "scene": scene.get("scene_id"),
                                "beat": beat.get("beat_id"),
                                "content": content[:100],
                                "type": "dialogue_climax"
                            })

            avg_intensity = sum(emotion_intensity) / len(emotion_intensity) if emotion_intensity else 0

            episode_analysis.append({
                "episode": episode_num,
                "title": episode.get("title"),
                "beat_count": total_beats,
                "action_count": action_count,
                "dialogue_count": dialogue_count,
                "avg_intensity": round(avg_intensity, 2),
                "pace": self._calculate_pace(action_count, dialogue_count)
            })

        return {
            "episodes": episode_analysis,
            "climax_points": climax_points[:10],
            "overall_arc": self._analyze_overall_arc(episode_analysis)
        }

    def _calculate_emotion_intensity(self, content: str) -> float:
        score = 0.0
        for level, keywords in self.EMOTION_KEYWORDS.items():
            if any(kw in content for kw in keywords):
                if level == "high":
                    score = 1.0
                elif level == "medium":
                    score = max(score, 0.6)
                else:
                    score = max(score, 0.3)
        return score

    def _calculate_pace(self, actions: int, dialogues: int) -> str:
        ratio = actions / (dialogues + 1)
        if ratio > 1.5:
            return "fast"
        elif ratio > 0.7:
            return "medium"
        else:
            return "slow"

    def _analyze_overall_arc(self, episode_analysis: List[Dict]) -> Dict[str, Any]:
        if not episode_analysis:
            return {"type": "unknown", "description": "数据不足"}

        intensities = [ep["avg_intensity"] for ep in episode_analysis]
        peak_episode = max(episode_analysis, key=lambda x: x["avg_intensity"])

        if intensities[0] < intensities[-1]:
            arc_type = "rising"
            description = "剧情呈上升趋势，结尾达到高潮"
        elif intensities[0] > intensities[-1]:
            arc_type = "falling"
            description = "剧情呈下降趋势，开头较为激烈"
        else:
            arc_type = "flat"
            description = "剧情节奏平稳"

        if peak_episode["episode"] <= len(episode_analysis) * 0.3:
            arc_type = "delayed_" + arc_type
            description = "高潮提前出现，后期逐渐平缓"

        return {
            "type": arc_type,
            "description": description,
            "peak_episode": peak_episode["episode"],
            "peak_intensity": peak_episode["avg_intensity"]
        }

    def analyze_dialogue_style(
        self,
        characters: List[Character],
        script_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        char_dialogues = defaultdict(lambda: {
            "count": 0, "total_length": 0, "exclamations": 0, "questions": 0
        })

        for episode in script_data.get("episodes", []):
            for scene in episode.get("scenes", []):
                for beat in scene.get("beats", []):
                    if beat.get("type") == "dialogue":
                        char_id = beat.get("character")
                        content = beat.get("content", "")

                        char_dialogues[char_id]["count"] += 1
                        char_dialogues[char_id]["total_length"] += len(content)
                        char_dialogues[char_id]["exclamations"] += content.count("!")
                        char_dialogues[char_id]["questions"] += content.count("?")

        char_map = {c.id: c for c in characters}
        style_analysis = {}

        for char_id, stats in char_dialogues.items():
            char = char_map.get(char_id)
            if not char:
                continue

            avg_length = stats["total_length"] / stats["count"] if stats["count"] > 0 else 0
            exclamation_ratio = stats["exclamations"] / stats["count"] if stats["count"] > 0 else 0
            question_ratio = stats["questions"] / stats["count"] if stats["count"] > 0 else 0

            if exclamation_ratio > 0.15:
                style = "passionate"
            elif question_ratio > 0.2:
                style = "inquisitive"
            elif avg_length > 50:
                style = "verbose"
            elif avg_length < 20:
                style = "concise"
            else:
                style = "balanced"

            style_analysis[char.name] = {
                "dialogue_count": stats["count"],
                "avg_length": round(avg_length, 1),
                "exclamation_ratio": round(exclamation_ratio, 2),
                "question_ratio": round(question_ratio, 2),
                "style": style,
                "description": self._get_style_description(style)
            }

        return style_analysis

    def _get_style_description(self, style: str) -> str:
        descriptions = {
            "passionate": "情绪激烈，富有感染力，常用感叹句",
            "inquisitive": "善于提问，逻辑性强，启发思考",
            "verbose": "善于长篇论述，表达详尽",
            "concise": "言简意赅，直截了当",
            "balanced": "节奏适中，表达稳健"
        }
        return descriptions.get(style, "")

    def generate_analysis_report(
        self,
        characters: List[Character],
        script_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "character_relationships": self.analyze_character_relationships(characters, script_data),
            "plot_rhythm": self.analyze_plot_rhythm(script_data),
            "dialogue_styles": self.analyze_dialogue_style(characters, script_data),
            "summary": self._generate_summary(characters, script_data)
        }

    def _generate_summary(
        self,
        characters: List[Character],
        script_data: Dict[str, Any]
    ) -> Dict[str, str]:
        protagonist_count = len([c for c in characters if c.role == "protagonist"])
        episode_count = len(script_data.get("episodes", []))

        return {
            "total_characters": len(characters),
            "protagonist_count": protagonist_count,
            "total_episodes": episode_count,
            "description": f"本剧本共有 {len(characters)} 个角色（其中 {protagonist_count} 位主角），共 {episode_count} 个章节。"
        }