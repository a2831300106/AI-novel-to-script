"""小说数据模型

定义小说解析后的数据结构
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class Chapter(BaseModel):
    """章节"""
    id: int = Field(description="章节编号")
    title: str = Field(description="章节标题")
    content: str = Field(description="章节内容")
    word_count: int = Field(description="字数")
    start_line: int = Field(default=0, description="起始行号")
    end_line: int = Field(default=0, description="结束行号")


class Novel(BaseModel):
    """小说"""
    title: Optional[str] = Field(default=None, description="小说标题")
    author: Optional[str] = Field(default=None, description="作者")
    total_chapters: int = Field(description="总章节数")
    total_words: int = Field(description="总字数")
    chapters: List[Chapter] = Field(description="章节列表")
    raw_text: Optional[str] = Field(default=None, description="原始文本")

    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "title": "青春往事",
                "author": "未知",
                "total_chapters": 5,
                "total_words": 15000,
                "chapters": [
                    {
                        "id": 1,
                        "title": "第一章 相遇",
                        "content": "...",
                        "word_count": 3000,
                        "start_line": 1,
                        "end_line": 50
                    }
                ]
            }
        }