# WanderChina Map Backend

智能地图 + 多智能体数据生成系统

## 项目概述

本模块为"WANDERCHINA旅行伴侣平台"的核心功能之一，围绕"你在哪里，好东西就在哪里"的理念，构建一个融合实时定位服务、周边推荐系统、人文导览与多智能体数据生成系统的智能地图后端服务体系。

## 核心功能

### 1. 地图基础能力
- 实时定位服务（GPS）
- 周边搜索（餐厅/景点/商场/医院/警局/使馆）
- 距离排序、评分排序
- 多语言搜索（中/英/日/韩）

### 2. 智能推荐系统
- 基于用户位置和偏好的个性化推荐
- 用户画像和历史行为分析
- 协同过滤推荐算法
- 实时热门地点推荐

### 3. 多智能体数据生成系统（核心）
- **游客Agent**：提问、吐槽、分享体验
- **本地人Agent**：推荐、解释文化
- **留学生Agent**：双语翻译、补充说明
- **导览Agent**：输出专业讲解
- **审核Agent**：质量评估与过滤

### 4. 数据标注与评估
- 自动标注（POI标签、情感、类型、语言、角色）
- 多维度质量评估（流畅性、语义、语法、多样性）
- 半自动人工校验
- 数据版本管理

### 5. 数据导出
- JSONL格式
- Chat格式
- Alpaca格式
- 支持质量过滤和多语言筛选

## 技术栈

- **语言**：Python 3.10+
- **框架**：FastAPI
- **数据库**：PostgreSQL + Redis + Elasticsearch
- **异步任务**：Celery + Redis
- **AI模型**：支持 DeepSeek / Qwen / GPT / Claude

## 快速开始

### 1. 环境配置

```bash
# 克隆项目
git clone <repository-url>
cd wanderchina-map-backend

# 安装依赖
poetry install

# 复制环境变量文件
cp .env.example .env
```

### 2. 启动服务

```bash
# 使用 Docker Compose 启动所有服务
docker-compose up -d

# 或手动启动
# 1. 启动 PostgreSQL, Redis, Elasticsearch
# 2. 启动 FastAPI 应用
uvicorn app.main:app --reload

# 3. 启动 Celery Worker
celery -A app.core.celery_app worker --loglevel=info
```

### 3. 访问API文档

启动后访问 http://localhost:8000/docs 查看 Swagger UI 文档。

## API接口

### 地图服务

#### 获取附近地点
```
GET /api/map/nearby?lat={lat}&lng={lng}&type=restaurant
```

#### 获取推荐
```
GET /api/map/recommendations?user_id={id}&lat={lat}&lng={lng}
```

### 数据生成服务

#### 生成单条数据
```
POST /api/map/generate
{
  "location": "Beijing",
  "data_type": "restaurant_recommendation",
  "language": "zh",
  "user_role": "tourist"
}
```

#### 批量生成
```
POST /api/map/generate/batch
{
  "location": "Shanghai",
  "data_type": "review",
  "quantity": 10,
  "agent_types": ["tourist", "local", "student"]
}
```

### 数据标注
```
POST /api/map/annotate/auto/{generated_data_id}
```

### 数据评估
```
POST /api/map/evaluate
{
  "generated_data_ids": ["id1", "id2"],
  "metrics": ["perplexity", "grammar", "sentiment"]
}
```

### 数据导出
```
POST /api/map/export
{
  "format": "jsonl",
  "data_type": "recommendation",
  "quality_threshold": 0.7
}
```

## 项目结构

```
wanderchina-map-backend/
├── app/
│   ├── api/                    # API路由
│   │   ├── map.py             # 地图相关API
│   │   └── data_generation.py # 数据生成API
│   ├── core/                  # 核心配置
│   │   ├── config.py         # 应用配置
│   │   └── celery_app.py     # Celery配置
│   ├── database/              # 数据库
│   │   └── base.py           # 数据库连接
│   ├── models/               # 数据模型
│   │   └── database.py       # SQLAlchemy模型
│   ├── schemas/              # Pydantic模型
│   │   └── map.py            # API数据验证
│   ├── services/             # 业务逻辑
│   │   ├── map_service.py           # 地图服务
│   │   ├── recommendation_service.py # 推荐服务
│   │   ├── data_generation.py       # 数据生成
│   │   ├── annotation_service.py    # 标注服务
│   │   ├── evaluation_service.py    # 评估服务
│   │   ├── export_service.py         # 导出服务
│   │   ├── model_router.py           # 模型路由
│   │   ├── model_clients.py         # 模型客户端
│   │   └── prompt_manager.py        # Prompt管理
│   ├── tasks/                # 异步任务
│   │   └── data_generation_tasks.py
│   ├── utils/               # 工具函数
│   │   ├── helpers.py
│   │   ├── logging.py
│   │   └── cache.py
│   └── main.py              # 应用入口
├── tests/                   # 测试
├── docker-compose.yml       # Docker编排
├── Dockerfile
├── pyproject.toml
└── README.md
```

## 配置说明

### 环境变量

```env
# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/wanderchina

# Redis
REDIS_URL=redis://localhost:6379/0

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# API密钥
DEEPSEEK_API_KEY=your-api-key
QWEN_API_KEY=your-api-key
OPENAI_API_KEY=your-api-key
ANTHROPIC_API_KEY=your-api-key

# 安全
SECRET_KEY=your-secret-key
```

## 数据生成流程

1. **请求接收**：API接收生成请求
2. **Prompt构建**：根据模板和变量构建Prompt
3. **模型选择**：通过Router选择最佳模型
4. **内容生成**：调用AI模型生成内容
5. **质量评估**：审核Agent评估质量
6. **自动标注**：标注POI、情感、类型等
7. **数据存储**：保存到数据库
8. **导出**：支持多种格式导出

## 评估指标

### 文本质量
- **Perplexity**：流畅性评估
- **Grammar Check**：语法检查
- **BERT Score**：语义质量
- **Diversity**：词汇多样性

### 任务质量
- **BLEU/ROUGE**：问答和生成质量
- **Sentiment Analysis**：情感分析

## 扩展能力

- 方言识别与翻译（粤语/四川话）
- AR地图导览
- 实时人流预测
- 多模态数据（图片+文本生成）

## License

MIT License
