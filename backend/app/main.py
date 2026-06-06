"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import upload, convert, export, analyze

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    description="AI 辅助剧本创作工具 - 将小说自动转换为结构化剧本",
    version="1.0.0",
    debug=settings.debug,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(upload.router, prefix="/api", tags=["上传"])
app.include_router(convert.router, prefix="/api", tags=["转换"])
app.include_router(export.router, prefix="/api", tags=["导出"])
app.include_router(analyze.router, prefix="/api", tags=["分析"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI Script Tool API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}