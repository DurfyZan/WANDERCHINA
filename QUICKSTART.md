# 🚀 快速启动指南

## 环境准备

### 1. 检查Node.js版本
```bash
node --version
# 需要 >= 18.0.0
```

### 2. 安装依赖（首次运行）
```bash
cd "e:\AAA熊猫出行\5.20社区前端"
npm install
```

### 3. 启动开发服务器
```bash
npm run dev
```

### 4. 访问应用
打开浏览器访问：http://localhost:5173

---

## 📱 功能预览

### 页面A：社区沙盒 (Community Sandbox)

**访问方式**：点击左侧导航栏"社区沙盒"

**功能亮点**：
- 🌍 自动加载Mock数据（外国游客支付困难场景）
- 💭 观察AI智能体的思考链
- 💬 查看多层嵌套评论树
- ✏️ 悬停卡片查看标注工具栏
- 🏷️ 切换情感标签（正面/焦虑/吐槽）
- 🏷️ 添加自定义标签
- ✏️ 双击文本进行行内编辑
- 📊 查看右侧G-Eval评估面板

**Mock数据场景**：
```
🇺🇸 美国游客 → 抱怨无法使用微信支付
🇨🇳 中国本地人 → 用网络流行语热心解答
🇬🇧 英国华人 → 提供实用建议
🏗️ 嵌套盖楼回复
```

---

### 页面B：控制台 (Dashboard)

**访问方式**：点击左侧导航栏"控制台"

#### Tab 1: 任务配置
- 选择基座模型（DeepSeek-V3/R1, Qwen3-72B/235B）
- 调整Temperature（创造力）
- 调整Top-P（采样范围）
- 设置最大生成轮数
- 选择场景剧本
- 点击"开始生成"触发新的数据生成

#### Tab 2: 数据导出
- 选择导出格式（Alpaca 或 ShareGPT）
- 预览JSONL数据片段
- 点击"复制"按钮复制数据
- 点击"异步导出下载"下载.jsonl文件

---

## 🎨 核心组件速查

| 组件 | 文件位置 | 功能 |
|------|---------|------|
| Sidebar | `components/layout/Sidebar.tsx` | 左侧导航 |
| PostCard | `components/community/PostCard.tsx` | 基础帖子卡片 |
| PostCardWithAnnotation | `components/community/PostCardWithAnnotation.tsx` | 带标注卡片 |
| CommentTree | `components/community/CommentTree.tsx` | 嵌套评论树 |
| EvaluationPanel | `components/evaluation/EvaluationPanel.tsx` | 评估面板 |
| GenerationConfigForm | `components/dashboard/GenerationConfigForm.tsx` | 配置表单 |
| ExportWizard | `components/dashboard/ExportWizard.tsx` | 导出向导 |

---

## 🎯 快捷操作

### 社区页面
- **悬停卡片** → 显示标注工具栏
- **双击文本** → 进入行内编辑模式
- **点击🧠按钮** → 展开/收起思考链
- **点击表情Badge** → 切换情感标签
- **按Enter键** → 添加标签

### 控制台页面
- **拖动滑块** → 调整生成参数
- **点击模型卡片** → 选择基座模型
- **点击导出格式** → 切换Alpaca/ShareGPT
- **点击"复制"** → 复制JSONL数据

---

## 🐛 故障排除

### 问题1：npm命令无法识别
**解决**：确保已安装Node.js，并添加到系统PATH

### 问题2：端口5173被占用
**解决**：修改 `vite.config.ts` 中的端口号

### 问题3：样式显示异常
**解决**：确保已运行 `npm install` 安装Tailwind CSS依赖

---

## 📦 项目依赖清单

```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "lucide-react": "^0.468.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.6.0",
    "@tanstack/react-query": "^5.60.5",
    "axios": "^1.7.9"
  }
}
```

---

## 🎨 自定义主题

修改 `src/index.css` 中的CSS变量：

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    /* ... 更多变量 */
  }
}
```

---

## 📝 开发提示

1. **查看TypeScript类型**：所有接口定义在 `src/types/index.ts`
2. **添加新组件**：在 `src/components/` 下创建新文件夹
3. **修改Mock数据**：编辑 `src/hooks/useCommunityData.ts`
4. **自定义样式**：使用Tailwind CSS原子类或修改 `tailwind.config.js`

---

## 🚀 下一步开发

### 后端对接
1. 实现真实的SSE接口
2. 替换Mock数据为API调用
3. 添加用户认证

### 功能增强
1. 添加更多评估指标
2. 实现批量标注
3. 添加数据统计分析

### 性能优化
1. 添加React.memo优化渲染
2. 实现虚拟列表处理大量数据
3. 优化流式加载性能

---

**祝开发愉快！ 🎉**
