# WANDERCHINA 社区前端

Vue 3 + Pinia + Vue Router + TailwindCSS + vue-i18n（中/英/日/韩）

## 页面

| 路由 | 功能 |
|------|------|
| `/login` `/register` | 登录注册 |
| `/onboarding` | 头像、姓名完善 |
| `/community` | 首页流、分类筛选、推荐、加载更多 |
| `/community/search` | 搜索与标签 |
| `/community/post/new` | 发帖 + AI 生成草稿 |
| `/community/post/:id` | 详情、评论、点赞 |
| `/community/user` | 个人中心、发布与互动记录 |

## 启动

```bash
# 后端
pip install -r requirements.txt
python scripts/init_db.py
python scripts/seed_demo.py
uvicorn app.main:app --reload --port 8000

# 前端（需本机安装 Node.js）
cd web
npm install
npm run dev
```

访问 http://localhost:5173 ，演示账号 `demo` / `demo12345`
