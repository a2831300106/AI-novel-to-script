"""上传接口路由"""
import uuid
import os
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services import NovelParser
from app.config import settings
from app.utils import tasks

router = APIRouter()


@router.post("/upload")
async def upload_novel(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
):
    """上传小说文本

    Args:
        file: 上传的 TXT 文件
        text: 在线输入的文本

    Returns:
        dict: 任务信息和章节预览
    """
    # 检查输入
    if not file and not text:
        raise HTTPException(status_code=400, detail="请上传文件或输入文本")

    # 获取文本内容
    if file:
        # 检查文件类型
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="只支持 TXT 文件")

        # 检查文件大小
        content = await file.read()
        if len(content) > settings.max_file_size:
            raise HTTPException(status_code=400, detail=f"文件过大，最大支持 {settings.max_file_size / 1024 / 1024}MB")

        # 解码文本
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text_content = content.decode('gbk')
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="无法识别文件编码，请使用 UTF-8 或 GBK 编码")
    else:
        text_content = text

    # 创建任务 ID
    task_id = str(uuid.uuid4())

    # 解析小说
    parser = NovelParser()
    novel = parser.parse_text(text_content)

    # 验证章节数量
    is_valid, error_msg = parser.validate_chapters(novel.chapters)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # 保存任务信息
    tasks[task_id] = {
        "novel": novel,
        "status": "uploaded",
        "created_at": datetime.now().strftime("%Y-%m-%d"),
    }

    # 保存上传文件
    parser.save_upload(task_id, text_content)

    # 返回任务信息
    return {
        "task_id": task_id,
        "title": novel.title,
        "author": novel.author,
        "chapters": [
            {
                "id": ch.id,
                "title": ch.title,
                "word_count": ch.word_count,
            }
            for ch in novel.chapters
        ],
        "total_chapters": novel.total_chapters,
        "total_words": novel.total_words,
    }


@router.get("/upload/{task_id}")
async def get_upload_info(task_id: str):
    """获取上传信息

    Args:
        task_id: 任务 ID

    Returns:
        dict: 任务信息
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks[task_id]
    novel = task["novel"]

    return {
        "task_id": task_id,
        "title": novel.title,
        "author": novel.author,
        "chapters": [
            {
                "id": ch.id,
                "title": ch.title,
                "word_count": ch.word_count,
            }
            for ch in novel.chapters
        ],
        "total_chapters": novel.total_chapters,
        "total_words": novel.total_words,
        "status": task["status"],
    }