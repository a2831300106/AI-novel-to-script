# 剧本 YAML Schema 设计文档

## 一、概述

本文档定义了小说转剧本工具使用的 YAML Schema 规范。该 Schema 旨在：
- 让小说作者无需专业知识即可理解和编辑
- 适合 AI 大模型稳定输出
- 覆盖剧本创作的核心要素
- 支持短剧、网剧、电影等多种剧本类型

## 二、为什么选择 YAML 而非 JSON？

| 特性 | YAML | JSON |
|------|------|------|
| **可读性** | 高，支持注释、无需引号 | 中，需要引号、无注释 |
| **编辑门槛** | 低，作者可直接用记事本修改 | 中，需要了解 JSON 语法 |
| **AI 输出稳定性** | 高，格式宽松容错性强 | 中，格式严格易出错 |
| **嵌套结构** | 清晰，缩进直观 | 一般，括号嵌套 |
| **工具支持** | 广泛，主流语言均支持 | 广泛 |

**结论**：YAML 更适合非技术背景的小说作者使用，同时大模型输出 YAML 的稳定性更高。

## 三、完整 Schema 结构

```yaml
# ============================================================
# 剧本元数据
# ============================================================
script:
  version: "1.0"                    # Schema 版本，便于后续升级兼容
  type: "series"                    # 剧本类型: series(网剧), movie(电影), short(短剧)
  title: "剧本标题"                  # 剧本名称
  source: "原著小说名称"             # 原著来源
  author: "改编作者"                 # 改编作者
  created_at: "2024-01-01"          # 创建日期
  synopsis: "故事梗概..."            # 故事简介

# ============================================================
# 人物表
# ============================================================
characters:
  - id: "char_001"                  # 人物唯一标识，用于场景中引用
    name: "张三"                     # 人物名称
    alias: ["小张", "老张"]          # 别名/昵称，小说中可能有多个称呼
    role: "protagonist"              # 角色类型: protagonist(主角), supporting(配角), minor(龙套)
    description: "人物描述..."        # 人物特征描述
    first_appear: "第1章"            # 首次出场章节

  - id: "char_002"
    name: "李四"
    alias: ["老李"]
    role: "supporting"
    description: "张三的好友，性格开朗"
    first_appear: "第1章"

# ============================================================
# 场景表
# ============================================================
locations:
  - id: "loc_001"                   # 场景唯一标识，用于场景引用
    name: "咖啡厅"                   # 场景名称
    type: "interior"                 # 场景类型: interior(内景), exterior(外景)
    time: "day"                      # 默认时间: day(日), night(夜), dawn(晨), dusk(暮)
    description: "温馨的小咖啡厅，墙上挂着油画"  # 场景描述

  - id: "loc_002"
    name: "街道"
    type: "exterior"
    time: "night"
    description: "繁华的商业街，霓虹闪烁"

# ============================================================
# 分集/分章内容
# ============================================================
episodes:
  - episode: 1                       # 集数/章节编号
    title: "第一章 相遇"             # 标题
    synopsis: "本章剧情梗概..."      # 章节简介
    scenes:                          # 场景列表
      - scene_id: "scene_001"        # 场景编号
        location: "loc_001"          # 引用场景表中的场景ID
        time: "day"                  # 可覆盖场景默认时间
        beats:                       # 节拍/镜头列表

          # 动作描述
          - beat_id: "beat_001"
            type: "action"           # 类型: action(动作), dialogue(台词), transition(转场), note(备注)
            content: "张三推门走进咖啡厅，环顾四周"
            characters: ["char_001"] # 涉及人物

          # 台词
          - beat_id: "beat_002"
            type: "dialogue"
            character: "char_001"     # 说话人
            parenthetical: "自言自语" # 括号说明（语气/动作）
            content: "这里人真少啊"
            characters: ["char_001"]

          # 动作描述
          - beat_id: "beat_003"
            type: "action"
            content: "李四从角落站起来，向张三挥手"
            characters: ["char_001", "char_002"]

          # 台词
          - beat_id: "beat_004"
            type: "dialogue"
            character: "char_002"
            content: "张三！这边！"
            characters: ["char_001", "char_002"]

          # 转场
          - beat_id: "beat_005"
            type: "transition"
            content: "切至"           # 转场方式

      - scene_id: "scene_002"
        location: "loc_002"
        time: "night"
        beats:
          - beat_id: "beat_006"
            type: "action"
            content: "夜幕降临，街道上灯火通明"
            characters: []

          - beat_id: "beat_007"
            type: "dialogue"
            character: "char_001"
            content: "今晚的夜景真美"
            characters: ["char_001", "char_002"]

# ============================================================
# 剧情线（可选，用于复杂剧本）
# ============================================================
storylines:
  - id: "line_001"
    name: "主线-张三的成长"
    description: "张三从迷茫到找到人生方向"
    episodes: [1, 2, 3, 4, 5]        # 涉及的章节

  - id: "line_002"
    name: "副线-张三与李四的友情"
    description: "两人从相识到成为挚友"
    episodes: [1, 3, 5]
```

## 四、字段设计原因详解

### 4.1 script 元数据

| 字段 | 类型 | 必填 | 设计原因 |
|------|------|------|----------|
| `version` | string | 是 | Schema 版本号，便于后续升级兼容。当 Schema 结构变化时，解析器可根据版本号适配 |
| `type` | string | 是 | 区分不同剧本类型（网剧、电影、短剧），不同类型的转换策略和格式要求可能不同 |
| `title` | string | 是 | 剧本名称，用于显示和导出文件名 |
| `source` | string | 否 | 保留原著信息，便于追溯和版权管理 |
| `author` | string | 否 | 改编作者信息 |
| `created_at` | string | 否 | 创建日期，便于版本管理 |
| `synopsis` | string | 否 | 故事梗概，帮助读者快速了解剧情 |

### 4.2 characters 人物表

| 字段 | 类型 | 必填 | 设计原因 |
|------|------|------|----------|
| `id` | string | 是 | 全局唯一标识，用于场景中引用人物。格式建议：`char_XXX` |
| `name` | string | 是 | 人物名称，显示用 |
| `alias` | array | 否 | 别名/昵称列表。小说中人物可能有多个称呼（如"张三"、"小张"、"老张"），便于 AI 识别同一人物 |
| `role` | string | 是 | 角色类型，影响台词分配和剧情权重。可选值：`protagonist`（主角）、`supporting`（配角）、`minor`（龙套） |
| `description` | string | 否 | 人物特征描述，帮助理解人物性格和背景 |
| `first_appear` | string | 否 | 首次出场章节，帮助作者追踪人物出场顺序 |

**设计原因**：
- 独立人物表避免重复定义，便于统一修改
- `id` 引用机制确保人物信息一致性
- `alias` 字段解决小说中人物多称呼问题

### 4.3 locations 场景表

| 字段 | 类型 | 必填 | 设计原因 |
|------|------|------|----------|
| `id` | string | 是 | 场景唯一标识，用于场景引用。格式建议：`loc_XXX` |
| `name` | string | 是 | 场景名称，如"咖啡厅"、"街道" |
| `type` | string | 是 | 场景类型，标准剧本格式要求。可选值：`interior`（内景）、`exterior`（外景） |
| `time` | string | 否 | 默认时间，标准剧本格式要求。可选值：`day`（日）、`night`（夜）、`dawn`（晨）、`dusk`（暮） |
| `description` | string | 否 | 场景描述，帮助理解环境氛围 |

**设计原因**：
- 独立场景表避免重复定义，便于统一修改
- `type` + `time` 是标准剧本格式要求
- 场景可在具体 beat 中覆盖默认时间

### 4.4 episodes 分集内容

采用三层结构：**集 → 场景 → 节拍**

#### 4.4.1 episode 层

| 字段 | 类型 | 必填 | 设计原因 |
|------|------|------|----------|
| `episode` | int | 是 | 集数/章节编号 |
| `title` | string | 是 | 标题 |
| `synopsis` | string | 否 | 章节简介 |
| `scenes` | array | 是 | 场景列表 |

#### 4.4.2 scene 层

| 字段 | 类型 | 必填 | 设计原因 |
|------|------|------|----------|
| `scene_id` | string | 是 | 场景编号，格式建议：`scene_XXX` |
| `location` | string | 是 | 引用场景表中的场景ID |
| `time` | string | 否 | 可覆盖场景默认时间 |
| `beats` | array | 是 | 节拍/镜头列表 |

#### 4.4.3 beat 层

| 字段 | 类型 | 必填 | 设计原因 |
|------|------|------|----------|
| `beat_id` | string | 是 | 节拍编号，格式建议：`beat_XXX` |
| `type` | string | 是 | 类型：`action`（动作）、`dialogue`（台词）、`transition`（转场）、`note`（备注） |
| `content` | string | 是 | 内容 |
| `character` | string | 条件必填 | 说话人ID（仅 `dialogue` 类型需要） |
| `parenthetical` | string | 否 | 台词括号说明，专业剧本必备 |
| `characters` | array | 否 | 涉及的人物ID列表 |

**设计原因**：
- 三层结构符合剧本创作逻辑
- `beat` 是剧本最小单位，包含动作、台词、转场
- `parenthetical` 是专业剧本必备元素，用于标注语气、动作
- `characters` 数组便于追踪人物出场

### 4.5 storylines 剧情线（可选）

| 字段 | 类型 | 必填 | 设计原因 |
|------|------|------|----------|
| `id` | string | 是 | 剧情线唯一标识 |
| `name` | string | 是 | 剧情线名称 |
| `description` | string | 否 | 剧情线描述 |
| `episodes` | array | 否 | 涉及的章节列表 |

**设计原因**：
- 支持复杂剧本的多线叙事
- 帮助作者理清剧情脉络
- 可选字段，简单剧本可省略

## 五、类型枚举值

### 5.1 script.type

| 值 | 说明 |
|------|------|
| `series` | 网剧/电视剧 |
| `movie` | 电影 |
| `short` | 短剧 |

### 5.2 character.role

| 值 | 说明 |
|------|------|
| `protagonist` | 主角 |
| `supporting` | 配角 |
| `minor` | 龙套/群众 |

### 5.3 location.type

| 值 | 说明 |
|------|------|
| `interior` | 内景（室内） |
| `exterior` | 外景（室外） |

### 5.4 location.time

| 值 | 说明 |
|------|------|
| `day` | 日 |
| `night` | 夜 |
| `dawn` | 晨 |
| `dusk` | 暮 |

### 5.5 beat.type

| 值 | 说明 |
|------|------|
| `action` | 动作描述 |
| `dialogue` | 台词 |
| `transition` | 转场 |
| `note` | 备注 |

## 六、使用示例

### 6.1 完整示例

```yaml
script:
  version: "1.0"
  type: "series"
  title: "青春往事"
  source: "小说《青春往事》"
  author: "AI 改编"
  created_at: "2024-01-15"
  synopsis: "讲述了大学生张三和李四的友情故事"

characters:
  - id: "char_001"
    name: "张三"
    alias: ["小张"]
    role: "protagonist"
    description: "大学生，性格内向"
    first_appear: "第1章"

  - id: "char_002"
    name: "李四"
    alias: ["老李"]
    role: "supporting"
    description: "张三的好友，性格开朗"
    first_appear: "第1章"

locations:
  - id: "loc_001"
    name: "大学图书馆"
    type: "interior"
    time: "day"
    description: "安静的大学图书馆，书架林立"

episodes:
  - episode: 1
    title: "第一章 相遇"
    synopsis: "张三在图书馆遇到李四"
    scenes:
      - scene_id: "scene_001"
        location: "loc_001"
        time: "day"
        beats:
          - beat_id: "beat_001"
            type: "action"
            content: "张三走进图书馆，寻找座位"
            characters: ["char_001"]

          - beat_id: "beat_002"
            type: "dialogue"
            character: "char_001"
            parenthetical: "自言自语"
            content: "今天人真多啊"
            characters: ["char_001"]

          - beat_id: "beat_003"
            type: "action"
            content: "李四向张三招手"
            characters: ["char_001", "char_002"]

          - beat_id: "beat_004"
            type: "dialogue"
            character: "char_002"
            content: "张三！这边有空位！"
            characters: ["char_001", "char_002"]

          - beat_id: "beat_005"
            type: "transition"
            content: "淡出"
```

### 6.2 最小示例

```yaml
script:
  version: "1.0"
  type: "short"
  title: "简单对话"

characters:
  - id: "char_001"
    name: "小明"
    role: "protagonist"

locations:
  - id: "loc_001"
    name: "房间"
    type: "interior"

episodes:
  - episode: 1
    title: "开场"
    scenes:
      - scene_id: "scene_001"
        location: "loc_001"
        beats:
          - beat_id: "beat_001"
            type: "dialogue"
            character: "char_001"
            content: "你好，世界！"
```

## 七、验证规则

### 7.1 必填字段验证

- `script.version` 必填
- `script.type` 必填，且必须是有效枚举值
- `script.title` 必填
- `characters` 数组至少包含一个元素
- 每个 `character` 必须有 `id`、`name`、`role`
- `locations` 数组至少包含一个元素
- 每个 `location` 必须有 `id`、`name`、`type`
- `episodes` 数组至少包含一个元素
- 每个 `episode` 必须有 `episode`、`title`、`scenes`

### 7.2 引用完整性验证

- `scene.location` 必须引用 `locations` 中存在的 `id`
- `beat.character` 必须引用 `characters` 中存在的 `id`
- `beat.characters` 数组中的每个元素必须引用 `characters` 中存在的 `id`

### 7.3 类型验证

- `script.type` 必须是 `series`、`movie`、`short` 之一
- `character.role` 必须是 `protagonist`、`supporting`、`minor` 之一
- `location.type` 必须是 `interior`、`exterior` 之一
- `location.time` 如果存在，必须是 `day`、`night`、`dawn`、`dusk` 之一
- `beat.type` 必须是 `action`、`dialogue`、`transition`、`note` 之一

## 八、扩展建议

### 8.1 未来可扩展字段

```yaml
# 人物扩展
characters:
  - id: "char_001"
    name: "张三"
    # 未来可扩展
    age: 25
    gender: "male"
    occupation: "大学生"
    relationships:
      - target: "char_002"
        type: "friend"

# 场景扩展
locations:
  - id: "loc_001"
    name: "咖啡厅"
    # 未来可扩展
    address: "北京市朝阳区XXX"
    atmosphere: "温馨"
    props: ["咖啡机", "桌椅"]

# 节拍扩展
beats:
  - beat_id: "beat_001"
    type: "action"
    content: "张三走进咖啡厅"
    # 未来可扩展
    duration: "5s"
    camera_angle: "中景"
    mood: "轻松"
```

### 8.2 版本兼容性

当 Schema 版本升级时：
1. 保持向后兼容，旧版本 YAML 仍可解析
2. 新增字段设为可选
3. 废弃字段标记为 `deprecated`
4. 在 `script.version` 中记录版本号

## 九、工具支持

### 9.1 JSON Schema

可提供等效的 JSON Schema 用于验证：

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["script", "characters", "locations", "episodes"],
  "properties": {
    "script": {
      "type": "object",
      "required": ["version", "type", "title"],
      "properties": {
        "version": { "type": "string" },
        "type": { "enum": ["series", "movie", "short"] },
        "title": { "type": "string" },
        "source": { "type": "string" },
        "author": { "type": "string" },
        "created_at": { "type": "string" },
        "synopsis": { "type": "string" }
      }
    }
    // ... 其他字段
  }
}
```

### 9.2 编辑器支持

可提供 VS Code 扩展，支持：
- YAML 语法高亮
- 字段自动补全
- 引用跳转
- 格式验证

## 十、总结

本 Schema 设计遵循以下原则：
1. **人类可读**：作者无需专业知识即可理解和编辑
2. **AI 友好**：适合大模型稳定输出，减少格式错误
3. **结构完整**：覆盖剧本创作的核心要素
4. **可扩展**：支持短剧、网剧、电影等多种剧本类型

通过合理的字段设计和引用机制，确保剧本数据的一致性和可维护性。