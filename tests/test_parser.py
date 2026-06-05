"""测试小说解析服务"""
import sys
import os

# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services import NovelParser
from app.models import Novel


def test_novel_parser():
    """测试小说解析"""
    # 读取示例小说
    novel_path = os.path.join(os.path.dirname(__file__), 'sample_novel.txt')

    parser = NovelParser()
    novel = parser.parse_file(novel_path)

    # 打印解析结果
    print("=" * 50)
    print("小说解析测试")
    print("=" * 50)
    print(f"标题: {novel.title}")
    print(f"作者: {novel.author}")
    print(f"总章节数: {novel.total_chapters}")
    print(f"总字数: {novel.total_words}")
    print()

    # 打印章节信息
    print("章节列表:")
    for chapter in novel.chapters:
        print(f"  第 {chapter.id} 章: {chapter.title} ({chapter.word_count} 字)")

    print()

    # 验证章节数量
    is_valid, error_msg = parser.validate_chapters(novel.chapters)
    print(f"章节数量验证: {is_valid}")
    if not is_valid:
        print(f"错误消息: {error_msg}")

    print("=" * 50)

    return novel


if __name__ == "__main__":
    test_novel_parser()