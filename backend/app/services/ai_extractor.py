"""AI 信息提取服务

使用 AI 提取小说中的人物、场景、剧情线等信息
"""
import json
import re
from typing import List, Dict, Any
from app.models import Character, Location, Storyline
from app.services.ai_provider import AIProvider, get_ai_provider


class AIExtractor:
    """AI 信息提取器"""

    # 人物提取 Prompt
    CHARACTER_EXTRACTION_PROMPT = """你是一个专业的剧本分析助手。请从以下小说文本中提取人物信息。

要求：
1. 识别所有出场人物
2. 判断角色类型：protagonist（主角）、supporting（配角）、minor（龙套）
3. 提取人物别名和昵称
4. 简要描述人物特征
5. 记录首次出场章节

输出 JSON 格式：
{
  "characters": [
    {
      "id": "char_001",
      "name": "人物名称",
      "alias": ["别名1", "别名2"],
      "role": "protagonist/supporting/minor",
      "description": "人物描述",
      "first_appear": "首次出场章节"
    }
  ]
}

小说文本：
{text}
"""

    # 场景提取 Prompt
    LOCATION_EXTRACTION_PROMPT = """你是一个专业的剧本分析助手。请从以下小说文本中提取场景信息。

要求：
1. 识别所有场景地点
2. 判断场景类型：interior（内景/室内）、exterior（外景/室外）
3. 判断默认时间：day（日）、night（夜）、dawn（晨）、dusk（暮）
4. 简要描述场景特征

输出 JSON 格式：
{
  "locations": [
    {
      "id": "loc_001",
      "name": "场景名称",
      "type": "interior/exterior",
      "time": "day/night/dawn/dusk",
      "description": "场景描述"
    }
  ]
}

小说文本：
{text}
"""

    # 剧情线提取 Prompt
    STORYLINE_EXTRACTION_PROMPT = """你是一个专业的剧本分析助手。请从以下小说文本中提取剧情线信息。

要求：
1. 识别主要剧情线（主线和副线）
2. 描述剧情线内容
3. 标注涉及章节

输出 JSON 格式：
{
  "storylines": [
    {
      "id": "line_001",
      "name": "剧情线名称",
      "description": "剧情线描述",
      "episodes": [1, 2, 3]
    }
  ]
}

小说文本：
{text}
"""

    def __init__(self, ai_provider: AIProvider = None):
        """初始化 AI 信息提取器

        Args:
            ai_provider: AI 服务提供商（可选，如果为 None 则使用本地提取）
        """
        self.ai_provider = ai_provider

    async def extract_characters(self, chapters_text: str) -> List[Character]:
        """提取人物信息

        Args:
            chapters_text: 章节文本

        Returns:
            List[Character]: 人物列表
        """
        # 如果有 AI 服务，尝试使用 AI 提取
        if self.ai_provider:
            try:
                prompt = self.CHARACTER_EXTRACTION_PROMPT.format(text=chapters_text[:3000])
                result = await self.ai_provider.chat_with_json(prompt)

                characters = []
                for char_data in result.get("characters", []):
                    characters.append(Character(
                        id=char_data.get("id", f"char_{len(characters)+1:03d}"),
                        name=char_data.get("name", ""),
                        alias=char_data.get("alias", []),
                        role=char_data.get("role", "supporting"),
                        description=char_data.get("description"),
                        first_appear=char_data.get("first_appear"),
                    ))

                if characters:
                    return characters
            except Exception as e:
                print(f"AI 人物提取失败: {str(e)}，使用本地提取")

        # 本地提取（演示模式）
        return self._extract_characters_local(chapters_text)

    def _extract_characters_local(self, text: str) -> List[Character]:
        """本地提取人物信息（演示模式）

        Args:
            text: 文本内容

        Returns:
            List[Character]: 人物列表
        """
        characters = []
        
        # 使用正则提取对话中的人物名称
        # 匹配格式："XXX说"、"XXX道"、"XXX问" 等
        dialogue_pattern = r'"([^"]+)"[，。]?\s*([^\s"。，！？]+)[说道问答感叹]'
        matches = re.findall(dialogue_pattern, text)
        
        # 统计人物出现频率
        name_count = {}
        for match in matches:
            name = match[1] if len(match) > 1 else None
            if name and len(name) >= 2 and len(name) <= 4:
                name_count[name] = name_count.get(name, 0) + 1
        
        # 按出现频率排序
        sorted_names = sorted(name_count.items(), key=lambda x: x[1], reverse=True)
        
        # 创建人物列表
        for i, (name, count) in enumerate(sorted_names[:10]):  # 最多10个人物
            role = "protagonist" if i == 0 else ("supporting" if i < 3 else "minor")
            characters.append(Character(
                id=f"char_{i+1:03d}",
                name=name,
                alias=[],
                role=role,
                description=f"小说中的人物，出现约{count}次",
                first_appear="第1章",
            ))
        
        # 如果没有提取到人物，添加默认人物
        if not characters:
            characters.append(Character(
                id="char_001",
                name="主角",
                alias=[],
                role="protagonist",
                description="小说主角",
                first_appear="第1章",
            ))
        
        return characters

    async def extract_locations(self, chapters_text: str) -> List[Location]:
        """提取场景信息

        Args:
            chapters_text: 章节文本

        Returns:
            List[Location]: 场景列表
        """
        # 如果有 AI 服务，尝试使用 AI 提取
        if self.ai_provider:
            try:
                prompt = self.LOCATION_EXTRACTION_PROMPT.format(text=chapters_text[:3000])
                result = await self.ai_provider.chat_with_json(prompt)

                locations = []
                for loc_data in result.get("locations", []):
                    locations.append(Location(
                        id=loc_data.get("id", f"loc_{len(locations)+1:03d}"),
                        name=loc_data.get("name", ""),
                        type=loc_data.get("type", "interior"),
                        time=loc_data.get("time", "day"),
                        description=loc_data.get("description"),
                    ))

                if locations:
                    return locations
            except Exception as e:
                print(f"AI 场景提取失败: {str(e)}，使用本地提取")

        # 本地提取（演示模式）
        return self._extract_locations_local(chapters_text)

    def _extract_locations_local(self, text: str) -> List[Location]:
        """本地提取场景信息（演示模式）

        Args:
            text: 文本内容

        Returns:
            List[Location]: 场景列表
        """
        locations = []
        
        # 常见场景关键词
        location_keywords = [
            "图书馆", "咖啡厅", "餐厅", "宿舍", "教室", "办公室",
            "街道", "公园", "医院", "车站", "机场", "商场",
            "家", "房间", "客厅", "卧室", "厨房",
        ]
        
        # 查找场景关键词
        found_locations = set()
        for keyword in location_keywords:
            if keyword in text:
                found_locations.add(keyword)
        
        # 创建场景列表
        for i, loc_name in enumerate(list(found_locations)[:5]):  # 最多5个场景
            # 判断是内景还是外景
            interior_keywords = ["图书馆", "咖啡厅", "餐厅", "宿舍", "教室", "办公室", "家", "房间", "客厅", "卧室", "厨房"]
            loc_type = "interior" if loc_name in interior_keywords else "exterior"
            
            locations.append(Location(
                id=f"loc_{i+1:03d}",
                name=loc_name,
                type=loc_type,
                time="day",
                description=f"小说中的场景：{loc_name}",
            ))
        
        # 如果没有提取到场景，添加默认场景
        if not locations:
            locations.append(Location(
                id="loc_001",
                name="默认场景",
                type="interior",
                time="day",
                description="小说场景",
            ))
        
        return locations

    async def extract_storylines(self, chapters_text: str) -> List[Storyline]:
        """提取剧情线信息

        Args:
            chapters_text: 章节文本

        Returns:
            List[Storyline]: 剧情线列表
        """
        # 如果有 AI 服务，尝试使用 AI 提取
        if self.ai_provider:
            try:
                prompt = self.STORYLINE_EXTRACTION_PROMPT.format(text=chapters_text[:3000])
                result = await self.ai_provider.chat_with_json(prompt)

                storylines = []
                for line_data in result.get("storylines", []):
                    storylines.append(Storyline(
                        id=line_data.get("id", f"line_{len(storylines)+1:03d}"),
                        name=line_data.get("name", ""),
                        description=line_data.get("description"),
                        episodes=line_data.get("episodes", []),
                    ))

                if storylines:
                    return storylines
            except Exception as e:
                print(f"AI 剧情线提取失败: {str(e)}，使用默认剧情线")

        # 默认剧情线
        return [Storyline(
            id="line_001",
            name="主线",
            description="小说主要剧情",
            episodes=[1],
        )]

    async def extract_all(self, chapters_text: str) -> Dict[str, Any]:
        """提取所有信息

        Args:
            chapters_text: 章节文本

        Returns:
            Dict[str, Any]: 包含人物、场景、剧情线的字典
        """
        characters = await self.extract_characters(chapters_text)
        locations = await self.extract_locations(chapters_text)
        storylines = await self.extract_storylines(chapters_text)

        return {
            "characters": characters,
            "locations": locations,
            "storylines": storylines,
        }