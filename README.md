# AI 辅助剧本创作工具

将小说文本自动转换为结构化剧本（YAML 格式），降低改编门槛，提升创作效率。

## 功能特性

- ✅ 支持上传 TXT 文件或在线输入小说文本
- ✅ 自动识别章节结构（支持多种章节格式）
- ✅ AI 提取人物、场景、剧情线信息
- ✅ 将小说叙述转换为剧本格式（动作/台词/转场）
- ✅ 输出标准 YAML 剧本
- ✅ 在线编辑与预览功能
- ✅ 支持导出 YAML、JSON、TXT 格式

## 技术栈

### 后端
- Python 3.11
- FastAPI
- Pydantic
- PyYAML
- 百度文心一言 / 阿里通义千问 API

### 前端
- Vue 3
- Element Plus
- Axios
- Vite

## 项目结构

```
qiniu/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置管理
│   │   ├── models/            # 数据模型
│   │   │   ├── script.py      # 剧本数据模型
│   │   │   └── novel.py       # 小说数据模型
│   │   ├── services/          # 业务逻辑
│   │   │   ├── novel_parser.py    # 小说解析
│   │   │   ├── chapter_splitter.py # 章节分割
│   │   │   ├── ai_provider.py     # AI 服务
│   │   │   ├── ai_extractor.py    # AI 信息提取
│   │   │   └── script_generator.py # 剧本生成
│   │   ├── routers/           # API 路由
│   │   │   ├── upload.py      # 上传接口
│   │   │   ├── convert.py     # 转换接口
│   │   │   └── export.py      # 导出接口
│   │   └── utils/             # 工具函数
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── views/
│   │   │   ├── Upload.vue     # 上传页面
│   │   │   ├── Editor.vue     # 编辑页面
│   │   │   └── Preview.vue    # 预览页面
│   │   ├── api/               # API 调用
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
│
├── docs/                       # 文档
│   └ yaml_schema.md           # YAML Schema 文档
│
└── README.md
```

## 快速开始

### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 AI 服务 API 密钥

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 3. 访问应用

打开浏览器访问 http://localhost:3000

## API 文档

启动后端后，访问 http://localhost:8000/docs 查看 API 文档。

### 主要接口

- `POST /api/upload` - 上传小说文本
- `POST /api/convert` - 开始转换
- `GET /api/convert/{task_id}/progress` - 查询进度
- `GET /api/export/{task_id}` - 导出剧本

## YAML Schema

剧本输出采用标准 YAML 格式，详见 [docs/yaml_schema.md](docs/yaml_schema.md)。

### Schema 结构

```yaml
script:
  version: "1.0"
  type: "series"
  title: "剧本标题"
  source: "原著小说名称"

characters:
  - id: "char_001"
    name: "张三"
    role: "protagonist"

locations:
  - id: "loc_001"
    name: "咖啡厅"
    type: "interior"

episodes:
  - episode: 1
    title: "第一章"
    scenes:
      - scene_id: "scene_001"
        location: "loc_001"
        beats:
          - beat_id: "beat_001"
            type: "action"
            content: "动作描述"
```

## 配置说明

### AI 服务配置

支持两种 AI 服务：

1. **百度文心一言**
   - 在 `.env` 中设置 `WENXIN_API_KEY` 和 `WENXIN_SECRET_KEY`
   - 设置 `AI_PROVIDER=wenxin`

2. **阿里通义千问**
   - 在 `.env` 中设置 `QWEN_API_KEY`
   - 设置 `AI_PROVIDER=qwen`

### 其他配置

- `MIN_CHAPTERS=3` - 最少章节数（默认 3 章）
- `MAX_FILE_SIZE=10485760` - 最大文件大小（默认 10MB）
- `MAX_CHAPTER_LENGTH=8000` - 单章节最大长度（默认 8000 字符）

## 使用流程

1. **上传小说**
   - 上传 TXT 文件或在线输入文本
   - 系统自动识别章节结构

2. **开始转换**
   - 选择剧本类型（网剧/电影/短剧）
   - 选择 AI 服务
   - 点击"开始转换"

3. **查看结果**
   - 实时查看转换进度
   - 在编辑页面修改剧本
   - 在预览页面查看完整剧本

4. **导出剧本**
   - 导出 YAML 格式（结构化数据）
   - 导出 JSON 格式
   - 导出 TXT 格式（人类可读）

## 设计理念

### 为什么选择 YAML？

1. **人类可读**：作者无需专业知识即可理解和编辑
2. **AI 友好**：适合大模型稳定输出，减少格式错误
3. **格式宽松**：容错性强，不易报错
4. **工具支持**：主流语言均支持 YAML 解析

### Schema 设计原则

1. **结构完整**：覆盖剧本创作的核心要素
2. **引用机制**：人物、场景通过 ID 引用，避免重复定义
3. **可扩展**：支持短剧、网剧、电影等多种剧本类型
4. **低门槛**：作者无需专业剧本知识即可使用

## 后续扩展

- 支持更多输入格式（Word、PDF）
- 支持更多 AI 模型
- 添加剧本模板库
- 支持多人协作编辑
- 用户系统和积分订阅制

## 许可证

MIT License