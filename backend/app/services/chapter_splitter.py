"""章节分割服务

按章节分割文本，保留上下文信息
"""
from typing import List, Optional
from app.models import Chapter
from app.config import settings


class ChapterContext:
    """章节上下文"""

    def __init__(
        self,
        chapter: Chapter,
        prev_context: Optional[str] = None,
        next_context: Optional[str] = None,
    ):
        """初始化章节上下文

        Args:
            chapter: 章节对象
            prev_context: 前一章末尾内容
            next_context: 后一章开头内容
        """
        self.chapter = chapter
        self.prev_context = prev_context
        self.next_context = next_context
        self.full_context = self._build_full_context()

    def _build_full_context(self) -> str:
        """构建完整上下文

        Returns:
            str: 包含上下文的完整文本
        """
        parts = []

        # 添加前一章上下文
        if self.prev_context:
            parts.append(f"[前文摘要]\n{self.prev_context}\n\n")

        # 添加当前章节
        parts.append(self.chapter.content)

        # 添加后一章上下文
        if self.next_context:
            parts.append(f"\n\n[后文提示]\n{self.next_context}")

        return "\n".join(parts)


class ChapterSplitter:
    """章节分割器"""

    def __init__(self):
        """初始化分割器"""
        self.context_window = settings.context_window
        self.max_length = settings.max_chapter_length

    def split(self, chapters: List[Chapter]) -> List[ChapterContext]:
        """分割章节并添加上下文

        Args:
            chapters: 章节列表

        Returns:
            List[ChapterContext]: 章节上下文列表
        """
        contexts = []

        for i, chapter in enumerate(chapters):
            # 获取前一章末尾
            prev_context = None
            if i > 0:
                prev_chapter = chapters[i - 1]
                prev_context = self._get_end_context(prev_chapter.content)

            # 获取后一章开头
            next_context = None
            if i < len(chapters) - 1:
                next_chapter = chapters[i + 1]
                next_context = self._get_start_context(next_chapter.content)

            contexts.append(ChapterContext(
                chapter=chapter,
                prev_context=prev_context,
                next_context=next_context,
            ))

        return contexts

    def _get_end_context(self, text: str) -> str:
        """获取文本末尾上下文

        Args:
            text: 文本内容

        Returns:
            str: 末尾上下文
        """
        # 取末尾指定字符数
        if len(text) <= self.context_window:
            return text
        return text[-self.context_window:]

    def _get_start_context(self, text: str) -> str:
        """获取文本开头上下文

        Args:
            text: 文本内容

        Returns:
            str: 开头上下文
        """
        # 取开头指定字符数
        if len(text) <= self.context_window:
            return text
        return text[:self.context_window]

    def truncate_if_needed(self, text: str) -> str:
        """如果文本过长则截断

        Args:
            text: 文本内容

        Returns:
            str: 截断后的文本
        """
        if len(text) <= self.max_length:
            return text

        # 截断并添加提示
        return text[:self.max_length] + "\n\n[文本过长，已截断]"

    def split_long_chapter(self, chapter: Chapter) -> List[Chapter]:
        """分割过长的章节

        Args:
            chapter: 章节对象

        Returns:
            List[Chapter]: 分割后的章节列表
        """
        if len(chapter.content) <= self.max_length:
            return [chapter]

        # 按段落分割
        paragraphs = chapter.content.split('\n\n')
        sub_chapters = []
        current_content = ""
        sub_id = 1

        for para in paragraphs:
            if len(current_content) + len(para) <= self.max_length:
                current_content += para + "\n\n"
            else:
                # 创建子章节
                sub_chapters.append(Chapter(
                    id=chapter.id * 100 + sub_id,
                    title=f"{chapter.title} (第{sub_id}部分)",
                    content=current_content.strip(),
                    word_count=len(current_content.strip()),
                    start_line=chapter.start_line,
                    end_line=chapter.end_line,
                ))
                current_content = para + "\n\n"
                sub_id += 1

        # 添加最后一个子章节
        if current_content:
            sub_chapters.append(Chapter(
                id=chapter.id * 100 + sub_id,
                title=f"{chapter.title} (第{sub_id}部分)",
                content=current_content.strip(),
                word_count=len(current_content.strip()),
                start_line=chapter.start_line,
                end_line=chapter.end_line,
            ))

        return sub_chapters