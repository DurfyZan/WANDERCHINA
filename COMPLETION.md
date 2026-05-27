# 子网页智能体数据生成与标注系统 - 完成总结

## 项目概述
基于 Python 的多智能体社交媒体数据生成与标注系统，用于生成真实、多样化的社区互动数据，支持模型微调。

## 核心特性实现

### 1. 多智能体编排 ✅
- **技术实现**: LangGraph 状态机
- **智能体类型**: 外国游客（Tourist）、中国本地人（Local）、外籍留学生（Expat）
- **互动模式**: 发帖 → 多轮嵌套回复（支持 parent_id 盖楼）

### 2. 去 AI 化拟人化 ✅
- **Emoji 注入**: 概率性添加表情符号
- **网络用语**: 中英文网络俚语注入
- **拼写变化**: 概率性字符交换模拟打字错误
- **语气增强**: 感叹号和情绪词添加

### 3. 大模型适配 ✅
- **支持模型**: DeepSeek Chat/V3、Qwen3（推理模式）
- **思考链处理**: 正则提取 <think> 标签，自动剥离
- **重试机制**: 指数退避（5次重试，2-30秒间隔）

### 4. G-Eval 质量评估 ✅
- **评估维度**:
  - 拟人度 (1-5分): 真实感、语言风格、个性化
  - 连贯性 (1-5分): 对话逻辑、上下文衔接
- **通过标准**: 两项均 >= 4 分
- **自动重试**: 未达标最多重试 3 次

### 5. 自动标注 ✅
- **情感分析**: positive/negative/neutral/anxious
- **意图识别**: ask_for_help/complaint/share_experience/recommendation/discussion
- **话题标签**: 自动提取 3-5 个相关标签
- **核心主题**: 2-3 个关键主题

### 6. 数据导出 ✅
- **Alpaca 格式**: instruction + input + output（单轮微调）
- **ShareGPT 格式**: conversations 数组（多轮对话微调）
- **Raw 格式**: 完整 JSON 数据结构
- **文件格式**: .jsonl（按行存储）

## 数据流架构

```
场景输入
  ↓
人设创建（Tourist/Local/Expat）
  ↓
帖子生成（ Tourist Agent）
  ↓
多轮回复（Local + Expat Agents）
  ↓
G-Eval 质量评估
  ↓
未达标 → 自动重试（最多3次） → 达标
  ↓
自动标注（情感/意图/标签）
  ↓
格式导出（Alpaca/ShareGPT/Raw）
  ↓
output/ 目录
```

## 技术栈
- **语言**: Python 3.11+
- **智能体框架**: LangGraph 1.2.0
- **数据验证**: Pydantic v2
- **异步网络**: HTTPX + AsyncIO
- **重试机制**: Tenacity
- **大模型**: DeepSeek / Qwen（通过 OpenAI 兼容接口）

## 项目结构
```
.
├── src/
│   ├── core/                    # 核心模块
│   │   ├── schemas.py          # Pydantic 数据模型
│   │   ├── llm_router.py       # 大模型适配器
│   │   ├── evaluator.py        # G-Eval 评估器
│   │   └── annotator.py        # 自动标注器
│   ├── agents/                 # 智能体模块
│   │   ├── persona_manager.py  # 人设管理 + 去AI化
│   │   └── graph_workflow.py   # 社区互动图
│   └── data/                   # 数据模块
│       └── dataset_exporter.py # 格式导出器
├── output/                     # 导出目录
├── .env.example               # 环境变量模板
├── requirements.txt           # 依赖列表
├── main.py                    # 主入口
├── demo.py                    # 演示脚本
├── README.md                  # 项目文档
├── USAGE_GUIDE.md             # 使用指南
└── COMPLETION.md              # 完成总结
```

## 演示结果

### 示例数据
**场景**: 外国游客在北京地铁使用移动支付遇到困难

**生成内容**:
1. **主帖** (美国游客): 抱怨地铁支付问题，寻求帮助
2. **回复1** (本地人): 建议下载亿通行APP或去服务窗口
3. **回复2** (外籍人士): 推荐购买交通卡
4. **回复3** (本地人): 补充交通卡充值方法

### 导出格式

#### Alpaca 格式
```json
{
  "instruction": "根据以下场景，生成一篇社交媒体帖子...",
  "input": "",
  "output": "刚到北京就被地铁搞懵了！想说用手机支付结果发现要实名认证..."
}
```

#### ShareGPT 格式
```json
{
  "id": "demo_post_001",
  "conversations": [
    {"from": "user", "value": "主帖内容"},
    {"from": "assistant", "value": "回复1"},
    {"from": "user", "value": "回复2"},
    {"from": "assistant", "value": "回复3"}
  ],
  "meta": {
    "location": "北京",
    "annotations": {...}
  }
}
```

## 使用方式

### 1. 配置 API 密钥
```bash
cp .env.example .env
# 编辑 .env 填写密钥
```

### 2. 运行生成
```bash
python main.py
```

### 3. 查看结果
```bash
ls output/
```

## 质量保证

### 代码质量
- ✅ 完整类型提示（Pydantic + TypedDict）
- ✅ 异步非阻塞 I/O
- ✅ 完善的错误处理
- ✅ 重试机制保障稳定性

### 数据质量
- ✅ G-Eval 自动评估
- ✅ 去 AI 化拟人处理
- ✅ 多维度自动标注
- ✅ 标准化导出格式

## 扩展性

### 新增人设
在 `persona_manager.py` 中：
```python
@classmethod
def create_custom_persona(cls, agent_id: str) -> AgentPersona:
    return AgentPersona(
        agent_id=agent_id,
        role_type="Custom",
        nationality="",
        language_style="",
        catchphrases=[],
        age=25,
        personality=""
    )
```

### 新增评估维度
在 `evaluator.py` 中添加新的评估规则：
```python
"safety_score": 评估内容安全性
"emotion_score": 情感丰富度
```

### 新增导出格式
在 `dataset_exporter.py` 中：
```python
def export_to_custom_format(self, payloads):
    # 自定义导出逻辑
    pass
```

## 性能优化建议

1. **并发生成**: 使用 asyncio.gather 并行生成多条数据
2. **缓存机制**: 缓存人设模板减少重复计算
3. **批量评估**: 积累多条数据后批量评估
4. **数据库存储**: 使用 MongoDB 存储中间结果

## 未来规划

- [ ] Web UI 界面
- [ ] 批量数据生成工具
- [ ] 质量监控仪表盘
- [ ] 多语言支持
- [ ] 自定义人设模板
- [ ] 数据集版本管理

## 总结

本系统完整实现了 PRD 中的所有核心功能：
- ✅ 多智能体协作生成真实社交媒体内容
- ✅ 去 AI 化拟人化处理
- ✅ G-Eval 质量评估与自动重试
- ✅ 多维度自动标注
- ✅ 标准微调格式导出

系统已通过演示测试，所有模块功能正常，数据导出格式符合规范。只需配置 API 密钥即可投入使用。

---
**完成时间**: 2026-05-20
**代码行数**: ~1500 行
**模块数量**: 8 个核心模块
**测试状态**: ✅ 演示成功
