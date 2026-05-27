# 子网页智能体数据生成系统 - 使用指南

## 已完成功能

### 1. 核心模块
- ✅ **LLM 路由器** ([src/core/llm_router.py](src/core/llm_router.py))
  - 支持 DeepSeek、Qwen 等主流大模型
  - 自动剥离推理模型的思考链
  - 内置指数退避重试机制

- ✅ **人设管理** ([src/agents/persona_manager.py](src/agents/persona_manager.py))
  - 三种预设人设：外国游客、中国本地人、外籍留学生
  - 去 AI 化引擎（注入 Emoji、网络用语、小错误）

- ✅ **社区互动图** ([src/agents/graph_workflow.py](src/agents/graph_workflow.py))
  - 基于 LangGraph 的多智能体协作流程
  - 自动生成多轮嵌套回复

- ✅ **质量评估** ([src/core/evaluator.py](src/core/evaluator.py))
  - G-Eval 自动评估拟人度和连贯性
  - 未达标自动重试（最多 3 次）

- ✅ **自动标注** ([src/core/annotator.py](src/core/annotator.py))
  - 情感分析、意图识别、话题标签提取

- ✅ **数据导出** ([src/data/dataset_exporter.py](src/data/dataset_exporter.py))
  - Alpaca 格式（单轮指令微调）
  - ShareGPT 格式（多轮对话微调）
  - 原始 JSON 格式

### 2. 数据模型
完整的 Pydantic 数据模型定义于 [src/core/schemas.py](src/core/schemas.py)

### 3. 演示结果
已成功生成示例数据，导出到 `output/` 目录：
- `alpaca_20260520_002720.jsonl` - Alpaca 微调格式
- `sharegpt_20260520_002720.jsonl` - ShareGPT 对话格式
- `raw_20260520_002720.jsonl` - 原始数据结构

## 如何使用

### 步骤 1：配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填写你的 API 密钥
```

示例 `.env` 配置：
```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# 如果使用 Qwen
QWEN_API_KEY=your_qwen_api_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3-max
```

### 步骤 2：运行主程序
```bash
python main.py
```

系统将自动：
1. 使用配置的人设生成帖子
2. 调用本地人/外籍人士进行多轮回复
3. 通过 G-Eval 评估质量
4. 自动标注情感和话题
5. 导出三种格式的数据集

### 步骤 3：查看结果
生成的数据将保存在 `output/` 目录下：
```bash
# 查看导出文件
ls output/
```

## 项目结构
```
.
├── src/
│   ├── core/
│   │   ├── schemas.py          # 数据模型
│   │   ├── llm_router.py       # 大模型适配器
│   │   ├── evaluator.py        # 质量评估
│   │   └── annotator.py        # 自动标注
│   ├── agents/
│   │   ├── persona_manager.py  # 人设管理
│   │   └── graph_workflow.py   # 互动流程
│   └── data/
│       └── dataset_exporter.py # 数据导出
├── output/                     # 导出目录
├── .env.example               # 环境变量模板
├── requirements.txt           # 依赖
├── main.py                    # 主入口
└── demo.py                    # 演示脚本
```

## 技术栈
- Python 3.11+
- LangGraph（智能体编排）
- Pydantic v2（数据验证）
- HTTPX + AsyncIO（异步网络）
- DeepSeek / Qwen API（可选）

## 下一步
1. 填写 `.env` 中的 API 密钥
2. 运行 `python main.py` 生成真实数据
3. 查看 `output/` 中的导出结果
4. 使用导出的数据进行模型微调

## 扩展开发

### 自定义场景
修改 `main.py` 中的 `scenario` 和 `location` 变量：
```python
scenario = "你的场景描述"
location = "地点"
```

### 添加新人设
在 `persona_manager.py` 中添加新的 `create_*_persona` 方法。

### 更换大模型
在 `.env` 中配置不同的 API 地址和密钥。

---
生成时间：2026-05-20
