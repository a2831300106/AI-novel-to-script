"""配置管理"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings(BaseSettings):
    """应用配置"""
    # 应用配置
    app_name: str = "AI Script Tool"
    debug: bool = False

    # AI 服务配置
    ai_provider: str = "wenxin"  # wenxin / qwen
    wenxin_api_key: Optional[str] = None
    wenxin_secret_key: Optional[str] = None
    qwen_api_key: Optional[str] = None

    # 文件配置
    upload_dir: str = "uploads"
    output_dir: str = "outputs"
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    # 处理配置
    min_chapters: int = 3  # 最少章节数
    max_chapter_length: int = 8000  # 单章节最大长度（字符）
    context_window: int = 500  # 上下文窗口大小

    class Config:
        """Pydantic 配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()