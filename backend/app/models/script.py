"""剧本数据模型

定义剧本 YAML Schema 对应的 Pydantic 数据模型
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date


# ============================================================
# 剧本元数据
# ============================================================

class ScriptMeta(BaseModel):
    """剧本元数据"""
    version: str = Field(default="1.0", description="Schema 版本")
    type: str = Field(description="剧本类型: series(网剧), movie(电影), short(短剧)")
    title: str = Field(description="剧本标题")
    source: Optional[str] = Field(default=None, description="原著小说名称")
    author: Optional[str] = Field(default=None, description="改编作者")
    created_at: Optional[str] = Field(default=None, description="创建日期")
    synopsis: Optional[str] = Field(default=None, description="故事梗概")


# ============================================================
# 人物表
# ============================================================

class Character(BaseModel):
    """人物"""
    id: str = Field(description="人物唯一标识")
    name: str = Field(description="人物名称")
    alias: Optional[List[str]] = Field(default_factory=list, description="别名/昵称")
    role: str = Field(description="角色类型: protagonist(主角), supporting(配角), minor(龙套)")
    description: Optional[str] = Field(default=None, description="人物特征描述")
    first_appear: Optional[str] = Field(default=None, description="首次出场章节")


# ============================================================
# 场景表
# ============================================================

class Location(BaseModel):
    """场景"""
    id: str = Field(description="场景唯一标识")
    name: str = Field(description="场景名称")
    type: str = Field(description="场景类型: interior(内景), exterior(外景)")
    time: Optional[str] = Field(default="day", description="默认时间: day, night, dawn, dusk")
    description: Optional[str] = Field(default=None, description="场景描述")


# ============================================================
# 节拍/镜头
# ============================================================

class Beat(BaseModel):
    """节拍/镜头 - 剧本最小单位"""
    beat_id: str = Field(description="节拍编号")
    type: str = Field(description="类型: action, dialogue, transition, note")
    content: str = Field(description="内容")
    character: Optional[str] = Field(default=None, description="说话人ID（仅 dialogue 类型）")
    parenthetical: Optional[str] = Field(default=None, description="台词括号说明")
    characters: Optional[List[str]] = Field(default_factory=list, description="涉及人物ID列表")


# ============================================================
# 场景
# ============================================================

class Scene(BaseModel):
    """场景"""
    scene_id: str = Field(description="场景编号")
    location: str = Field(description="引用场景表中的场景ID")
    time: Optional[str] = Field(default=None, description="可覆盖场景默认时间")
    beats: List[Beat] = Field(description="节拍/镜头列表")


# ============================================================
# 章节/集
# ============================================================

class Episode(BaseModel):
    """章节/集"""
    episode: int = Field(description="集数/章节编号")
    title: str = Field(description="标题")
    synopsis: Optional[str] = Field(default=None, description="章节简介")
    scenes: List[Scene] = Field(description="场景列表")


# ============================================================
# 剧情线
# ============================================================

class Storyline(BaseModel):
    """剧情线"""
    id: str = Field(description="剧情线唯一标识")
    name: str = Field(description="剧情线名称")
    description: Optional[str] = Field(default=None, description="剧情线描述")
    episodes: Optional[List[int]] = Field(default_factory=list, description="涉及的章节列表")


# ============================================================
# 完整剧本
# ============================================================

class Script(BaseModel):
    """完整剧本"""
    script: ScriptMeta = Field(description="剧本元数据")
    characters: List[Character] = Field(description="人物表")
    locations: List[Location] = Field(description="场景表")
    episodes: List[Episode] = Field(description="分集/分章内容")
    storylines: Optional[List[Storyline]] = Field(default_factory=list, description="剧情线（可选）")

    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "script": {
                    "version": "1.0",
                    "type": "series",
                    "title": "青春往事",
                    "source": "小说《青春往事》",
                    "author": "AI 改编",
                    "created_at": "2024-01-15",
                    "synopsis": "讲述了大学生张三和李四的友情故事"
                },
                "characters": [
                    {
                        "id": "char_001",
                        "name": "张三",
                        "alias": ["小张"],
                        "role": "protagonist",
                        "description": "大学生，性格内向",
                        "first_appear": "第1章"
                    }
                ],
                "locations": [
                    {
                        "id": "loc_001",
                        "name": "大学图书馆",
                        "type": "interior",
                        "time": "day",
                        "description": "安静的大学图书馆"
                    }
                ],
                "episodes": [
                    {
                        "episode": 1,
                        "title": "第一章 相遇",
                        "synopsis": "张三在图书馆遇到李四",
                        "scenes": [
                            {
                                "scene_id": "scene_001",
                                "location": "loc_001",
                                "time": "day",
                                "beats": [
                                    {
                                        "beat_id": "beat_001",
                                        "type": "action",
                                        "content": "张三走进图书馆",
                                        "characters": ["char_001"]
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "storylines": []
            }
        }