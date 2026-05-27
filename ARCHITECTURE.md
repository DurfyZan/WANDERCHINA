# WanderChina Map Backend - 技术设计文档

## 1. 系统概述

### 1.1 项目目标

构建一个**"地图 + 多智能体数据工厂 + LLM训练数据引擎"**的综合后端系统，核心竞争力包括：
- 地理场景真实数据生成
- 多角色交互数据
- 可评估、可控的数据质量体系

### 1.2 核心模块

```
┌─────────────────────────────────────────────────────────────┐
│                     WanderChina Map Backend                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Map API    │  │  Data Gen    │  │  Evaluation │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                 │                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Recommendation│  │ Annotation   │  │   Export     │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Multi-Agent Data Generation          │      │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │      │
│  │  │Tourist │ │ Local  │ │Student │ │ Guide  │    │      │
│  │  │ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │    │      │
│  │  └────────┘ └────────┘ └────────┘ └────────┘    │      │
│  │       ┌────────────────────────────────┐       │      │
│  │       │    Model Router & Clients      │       │      │
│  │       │  DeepSeek / Qwen / GPT / Claude│       │      │
│  │       └────────────────────────────────┘       │      │
│  └──────────────────────────────────────────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 2. 架构设计

### 2.1 分层架构

```
┌─────────────────────────────────────────┐
│          Presentation Layer             │
│   (FastAPI Routes + Pydantic Schemas)   │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│           Business Logic Layer          │
│  (Map / Recommendation / Data Gen...)   │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│             Service Layer               │
│  (Model Clients / Prompt Manager)       │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│            Data Access Layer             │
│  (SQLAlchemy + Redis + Elasticsearch)  │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│           Infrastructure                │
│  (PostgreSQL / Redis / ES / Celery)    │
└─────────────────────────────────────────┘
```

### 2.2 异步处理架构

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   FastAPI    │────▶│    Redis     │────▶│  Celery      │
│   Server     │     │   Broker     │     │  Workers     │
└──────────────┘     └──────────────┘     └──────────────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │  Data Gen    │
                                        │  Tasks       │
                                        └──────────────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │ PostgreSQL   │
                                        │ (Results)    │
                                        └──────────────┘
```

## 3. 核心模块设计

### 3.1 多智能体系统

#### Agent类型

```python
class AgentType(Enum):
    TOURIST = "tourist"      # 游客视角
    LOCAL = "local"          # 本地人视角
    STUDENT = "student"      # 留学生视角
    GUIDE = "guide"          # 导游视角
    REVIEWER = "reviewer"    # 审核员视角
```

#### Agent职责矩阵

| Agent | 生成内容类型 | 语言风格 | 特点 |
|-------|------------|---------|------|
| Tourist | 体验分享、推荐 | 口语化、活泼 | 真实感强 |
| Local | 地道推荐、文化解读 | 亲切随和 | 专业地道 |
| Student | 双语内容、跨文化 | 中英混合 | 国际化视角 |
| Guide | 讲解、历史故事 | 专业但有趣 | 知识性强 |
| Reviewer | 质量评估 | 客观专业 | 把控质量 |

#### Prompt模板系统

```python
TEMPLATE_TYPES = {
    "restaurant_recommendation": {
        "template": "请以{role}的身份，推荐{location}附近的好餐厅。",
        "variables": ["role", "location", "style"],
    },
    "attraction_introduction": {
        "template": "介绍一下{location}的{attraction_name}。",
        "variables": ["role", "location", "attraction_name"],
    },
    "cultural_story": {
        "template": "讲一个关于{location}的{topic}的有趣故事。",
        "variables": ["location", "topic"],
    },
}
```

### 3.2 模型路由机制

```python
class ModelRouter:
    def get_best_client(self, task_type: str):
        routing_rules = {
            "code_generation": ["deepseek", "qwen"],
            "creative_writing": ["openai", "anthropic", "qwen"],
            "translation": ["deepseek", "qwen"],
            "reasoning": ["deepseek", "anthropic"],
            "general": ["deepseek", "qwen", "openai"],
        }
```

### 3.3 数据标注系统

#### 自动标注维度

```python
annotation_types = {
    "poi": "地点标签",
    "sentiment": "情感（正/负/中）",
    "data_type": "类型（推荐/吐槽/问答）",
    "language": "语言类型",
    "user_role": "用户角色",
}
```

#### 标注流程

```
生成内容 → 自动标注 → 质量评分 → 人工校验 → 最终确认
    │           │           │           │
    └───────────┴───────────┴───────────┘
                   │
                   ▼
            标注结果存储
```

### 3.4 评估体系

#### 评估指标

```python
metrics = {
    "fluency": ["perplexity", "grammar"],
    "semantic": ["bert_score", "mover_score"],
    "task": ["bleu", "rouge"],
    "quality": ["sentiment", "diversity", "coherence"],
}
```

#### 评估流程

```
生成内容 → 多维度评估 → 综合评分 → 质量筛选 → 输出
    │           │           │           │
    └───────────┴───────────┴───────────┘
                   │
                   ▼
            评估报告生成
```

## 4. 数据库设计

### 4.1 核心表结构

#### POI（地点信息）

```sql
CREATE TABLE pois (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    poi_type POIType NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    city VARCHAR NOT NULL,
    country VARCHAR NOT NULL,
    rating FLOAT DEFAULT 0.0,
    tags JSON,
    metadata JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### GeneratedData（生成数据）

```sql
CREATE TABLE generated_data (
    id VARCHAR PRIMARY KEY,
    agent_type VARCHAR NOT NULL,
    data_type DataType NOT NULL,
    content TEXT NOT NULL,
    language Language DEFAULT 'zh',
    user_role UserRole,
    location_context VARCHAR,
    quality_score FLOAT,
    is_approved BOOLEAN DEFAULT FALSE,
    needs_review BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### Annotation（标注）

```sql
CREATE TABLE annotations (
    id VARCHAR PRIMARY KEY,
    generated_data_id VARCHAR REFERENCES generated_data(id),
    annotation_type VARCHAR NOT NULL,
    label VARCHAR NOT NULL,
    confidence FLOAT,
    is_auto BOOLEAN DEFAULT TRUE,
    annotator VARCHAR,
    created_at TIMESTAMP
);
```

### 4.2 索引策略

```sql
-- 地理位置索引
CREATE INDEX idx_pois_location ON pois (latitude, longitude);
CREATE INDEX idx_pois_city ON pois (city);

-- 时间索引
CREATE INDEX idx_generated_data_created ON generated_data (created_at);

-- 类型索引
CREATE INDEX idx_generated_data_type ON generated_data (data_type);
CREATE INDEX idx_generated_data_quality ON generated_data (quality_score);
```

## 5. API设计

### 5.1 地图服务API

```yaml
/api/map/nearby:
  GET:
    summary: 获取附近地点
    parameters:
      - lat: float
      - lng: float
      - radius: float (default: 1000)
      - poi_type: string
      - language: string (zh/en/ja/ko)

/api/map/recommendations:
  GET:
    summary: 个性化推荐
    parameters:
      - user_id: string
      - lat: float
      - lng: float
```

### 5.2 数据生成API

```yaml
/api/map/generate:
  POST:
    summary: 生成单条数据
    body:
      location: string
      data_type: enum
      language: enum
      user_role: enum
      agent_type: string (optional)

/api/map/generate/batch:
  POST:
    summary: 批量生成
    body:
      location: string
      quantity: int
      agent_types: array (optional)
```

### 5.3 评估导出API

```yaml
/api/map/evaluate:
  POST:
    summary: 批量评估
    body:
      generated_data_ids: array
      metrics: array

/api/map/export:
  POST:
    summary: 导出数据
    body:
      format: enum (jsonl/chat/alpaca)
      data_type: enum
      quality_threshold: float
```

## 6. 数据流架构

### 6.1 完整数据流

```
用户请求
    │
    ▼
┌──────────────┐
│  API Gateway │
└──────────────┘
    │
    ▼
┌──────────────┐     ┌──────────────┐
│  Validation  │────▶│   Routing    │
└──────────────┘     └──────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
  ┌──────────┐       ┌──────────┐       ┌──────────┐
  │  Map     │       │  Data    │       │ Evaluation│
  │ Service  │       │ Generation│       │ Service  │
  └──────────┘       └──────────┘       └──────────┘
        │                   │                   │
        │                   │                   │
        ▼                   ▼                   ▼
  ┌──────────┐       ┌──────────┐       ┌──────────┐
  │PostgreSQL│       │ Model    │       │ Export   │
  │   +ES    │       │ Router   │       │ Service  │
  └──────────┘       └──────────┘       └──────────┘
                            │
                            ▼
                      ┌──────────┐
                      │  LLM API │
                      │(多模型)   │
                      └──────────┘
                            │
                            ▼
                      ┌──────────┐
                      │Celery   │
                      │Tasks    │
                      └──────────┘
```

### 6.2 数据生成流程

```
1. 请求接收
   ↓
2. 参数验证 (Pydantic)
   ↓
3. Prompt构建
   ├─ 选择Agent
   ├─ 加载模板
   └─ 填充变量
   ↓
4. 模型选择
   ├─ 任务类型判断
   ├─ 模型路由
   └─ API调用
   ↓
5. 内容生成
   ↓
6. 质量评估
   ├─ 自动评分
   └─ 审核Agent
   ↓
7. 自动标注
   ├─ POI标签
   ├─ 情感分析
   ├─ 类型识别
   └─ 语言检测
   ↓
8. 数据存储
   └─ PostgreSQL
   ↓
9. 任务完成
```

## 7. 部署架构

### 7.1 Docker Compose 架构

```
┌─────────────────────────────────────────┐
│           Docker Network                │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐│
│  │  FastAPI │  │ Celery  │  │ Celery  ││
│  │  App     │  │ Worker  │  │  Beat   ││
│  │ :8000    │  │         │  │         ││
│  └────┬─────┘  └────┬────┘  └────┬────┘│
│       │             │             │     │
│       └─────────────┼─────────────┘     │
│                     │                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │PostgreSQL│  │  Redis   │  │Elasticsearch││
│  │  :5432   │  │  :6379   │  │   :9200   ││
│  └──────────┘  └──────────┘  └──────────┘│
│                                         │
└─────────────────────────────────────────┘
```

### 7.2 水平扩展策略

```yaml
services:
  app:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
  
  celery_worker:
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## 8. 性能优化

### 8.1 缓存策略

```
┌────────────────┐
│   请求         │
└────────────────┘
       │
       ▼
┌────────────────┐
│  Redis Cache   │──命中──▶ 返回结果
└────────────────┘
       │未命中
       ▼
┌────────────────┐
│  数据库查询     │
└────────────────┘
       │
       ▼
┌────────────────┐
│  写入缓存      │
└────────────────┘
```

### 8.2 数据库优化

- 连接池管理
- 异步查询（asyncpg）
- 批量操作
- 索引优化

### 8.3 API优化

- 限流保护
- 请求压缩
- 响应缓存
- 异步任务

## 9. 安全设计

### 9.1 API安全

- JWT认证
- API密钥验证
- 请求签名
- 限流保护

### 9.2 数据安全

- 敏感数据加密
- 用户位置脱敏
- GDPR合规
- 数据审计日志

## 10. 监控与日志

### 10.1 监控指标

```python
metrics = {
    "api_requests": "API请求量",
    "response_time": "响应时间",
    "error_rate": "错误率",
    "model_calls": "模型调用量",
    "generation_quality": "生成质量",
    "cache_hit_rate": "缓存命中率",
}
```

### 10.2 日志结构

```json
{
  "timestamp": "2024-01-15T12:30:45Z",
  "level": "INFO",
  "service": "data_generation",
  "message": "Generation completed",
  "context": {
    "agent_type": "tourist",
    "data_type": "recommendation",
    "quality_score": 0.85,
    "duration_ms": 1234
  }
}
```

## 11. 扩展能力

### 11.1 未来扩展

- [ ] AR地图导览集成
- [ ] 实时人流预测
- [ ] 多模态数据生成
- [ ] 方言识别与翻译
- [ ] 个性化模型微调

### 11.2 高可用设计

- 服务降级
- 熔断器模式
- 重试机制
- 多区域部署

## 12. 开发规范

### 12.1 代码规范

- 类型注解（Type Hints）
- Pydantic数据验证
- Async/Await异步编程
- 日志记录
- 错误处理

### 12.2 测试策略

- 单元测试
- 集成测试
- 端到端测试
- 性能测试

### 12.3 CI/CD流程

```yaml
# GitHub Actions
- 代码检查 (ruff, mypy)
- 单元测试 (pytest)
- 构建镜像
- 部署测试
- 部署生产
```

## 总结

本系统采用**分层架构**和**微服务设计**，具有以下特点：

✅ **高内聚低耦合**：各服务独立，职责清晰
✅ **异步处理**：Celery异步任务，支持批量处理
✅ **多模型支持**：统一接口，支持DeepSeek/Qwen/GPT等
✅ **质量可控**：完善的评估和标注体系
✅ **易于扩展**：模块化设计，支持功能扩展
✅ **生产级**：包含监控、日志、安全等生产要素

该系统不仅是一个地图服务，更是一个**智能数据工厂**，为LLM训练提供高质量的地理场景社交数据。
