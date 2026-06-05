"""小说解析服务

解析上传的小说文本，识别章节结构
"""
import re
import os
from typing import List, Optional, Tuple
from app.models import Novel, Chapter
from app.config import settings


class NovelParser:
    """小说解析器"""

    # 章节识别正则表达式
    CHAPTER_PATTERNS = [
        r'第[一二三四五六七八九十百千万零\d]+[章节回集]',  # 中文格式
        r'[第\d]+[章节回集]',  # 数字格式
        r'Chapter\s*\d+',  # 英文格式
        r'CHAPTER\s*\d+',  # 英文大写格式
        r'第[一二三四五六七八九十百千万]+部分',  # 部分格式
    ]

    def __init__(self):
        """初始化解析器"""
        self.patterns = [re.compile(p) for p in self.CHAPTER_PATTERNS]

    def parse_file(self, file_path: str) -> Novel:
        """解析文件

        Args:
            file_path: 文件路径

        Returns:
            Novel: 解析后的小说对象
        """
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        return self.parse_text(text)

    def parse_text(self, text: str) -> Novel:
        """解析文本

        Args:
            text: 小说文本

        Returns:
            Novel: 解析后的小说对象
        """
        # 提取元数据
        metadata = self.extract_metadata(text)

        # 识别章节
        chapters = self.detect_chapters(text)

        # 计算总字数
        total_words = sum(ch.word_count for ch in chapters)

        return Novel(
            title=metadata.get('title'),
            author=metadata.get('author'),
            total_chapters=len(chapters),
            total_words=total_words,
            chapters=chapters,
            raw_text=text,
        )

    def extract_metadata(self, text: str) -> dict:
        """提取小说元数据

        Args:
            text: 小说文本

        Returns:
            dict: 元数据字典
        """
        metadata = {}

        # 提取标题（通常在开头）
        lines = text.split('\n')
        for line in lines[:10]:  # 检查前10行
            line = line.strip()
            if line and not self._is_chapter_title(line):
                # 第一行非空且不是章节标题，可能是书名
                if len(line) < 50:  # 标题通常较短
                    metadata['title'] = line
                    break

        # 提取作者（通常在标题后）
        author_patterns = [
            r'作者[:：]\s*(.+)',
            r'著者[:：]\s*(.+)',
            r'作者\s+(.+)',
        ]
        for pattern in author_patterns:
            match = re.search(pattern, text[:500])
            if match:
                metadata['author'] = match.group(1).strip()
                break

        return metadata

    def detect_chapters(self, text: str) -> List[Chapter]:
        """识别章节

        Args:
            text: 小说文本

        Returns:
            List[Chapter]: 章节列表
        """
        # 找到所有章节标题的位置
        chapter_positions = self._find_chapter_positions(text)

        if not chapter_positions:
            # 没有找到章节标题，将全文作为一章
            return [Chapter(
                id=1,
                title="全文",
                content=text.strip(),
                word_count=len(text.strip()),
                start_line=0,
                end_line=len(text.split('\n')),
            )]

        # 根据位置分割章节
        chapters = []
        for i, (title, start_pos) in enumerate(chapter_positions):
            # 确定章节结束位置
            if i < len(chapter_positions) - 1:
                end_pos = chapter_positions[i + 1][1]
            else:
                end_pos = len(text)

            # 提取章节内容
            content = text[start_pos:end_pos].strip()

            # 计算行号
            lines_before = text[:start_pos].split('\n')
            start_line = len(lines_before)
            end_line = start_line + len(content.split('\n'))

            chapters.append(Chapter(
                id=i + 1,
                title=title,
                content=content,
                word_count=len(content),
                start_line=start_line,
                end_line=end_line,
            ))

        return chapters

    def _find_chapter_positions(self, text: str) -> List[Tuple[str, int]]:
        """找到所有章节标题的位置

        Args:
            text: 小说文本

        Returns:
            List[Tuple[str, int]]: (标题, 位置) 列表
        """
        positions = []

        for pattern in self.patterns:
            for match in pattern.finditer(text):
                title = match.group()
                start_pos = match.start()

                # 检查是否是新行开头（避免匹配到正文中的引用）
                line_start = text.rfind('\n', 0, start_pos) + 1
                if start_pos - line_start < 10:  # 章节标题通常在行开头
                    # 避免重复添加同一位置
                    if not any(abs(p[1] - start_pos) < 10 for p in positions):
                        positions.append((title, start_pos))

        # 按位置排序
        positions.sort(key=lambda x: x[1])

        return positions

    def _is_chapter_title(self, line: str) -> bool:
        """检查是否是章节标题

        Args:
            line: 文本行

        Returns:
            bool: 是否是章节标题
        """
        for pattern in self.patterns:
            if pattern.match(line):
                return True
        return False

    def validate_chapters(self, chapters: List[Chapter]) -> Tuple[bool, str]:
        """验证章节数量

        Args:
            chapters: 章节列表

        Returns:
            Tuple[bool, str]: (是否有效, 错误消息)
        """
        if len(chapters) < settings.min_chapters:
            return False, f"章节数量不足，至少需要 {settings.min_chapters} 章"

        return True, ""

    def save_upload(self, task_id: str, text: str) -> str:
        """保存上传的文本

        Args:
            task_id: 任务ID
            text: 文本内容

        Returns:
            str: 文件路径
        """
        # 创建上传目录
        upload_dir = os.path.join(settings.upload_dir, task_id)
        os.makedirs(upload_dir, exist_ok=True)

        # 保存文件
        file_path = os.path.join(upload_dir, "novel.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

        return file_path