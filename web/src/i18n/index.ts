import { createI18n } from "vue-i18n";

const messages = {
  zh: {
    appName: "WANDERCHINA",
    nav: { feed: "动态", search: "搜索", post: "发帖", me: "我的" },
    category: { all: "全部", scenic: "景点", food: "美食", life: "生活攻略" },
    feed: { title: "社区动态", recommend: "为你推荐", loadMore: "加载更多", empty: "暂无帖子" },
    post: { comment: "评论", like: "点赞", share: "分享", back: "返回" },
    create: { title: "发布内容", ai: "AI 生成", publish: "发布", promptPh: "描述你想生成的内容…" },
    search: { title: "搜索", placeholder: "搜索帖子、问答…", tags: "热门标签" },
    profile: { title: "个人中心", myPosts: "我的发布", history: "互动记录" },
    role: { tourist: "外国游客", student: "留学生", local: "本地人", admin: "管理员" },
    auth: { login: "登录", register: "注册", logout: "退出" },
  },
  en: {
    appName: "WANDERCHINA",
    nav: { feed: "Feed", search: "Search", post: "Post", me: "Me" },
    category: { all: "All", scenic: "Sights", food: "Food", life: "Life tips" },
    feed: { title: "Community", recommend: "For you", loadMore: "Load more", empty: "No posts yet" },
    post: { comment: "Comments", like: "Like", share: "Share", back: "Back" },
    create: { title: "Create post", ai: "AI draft", publish: "Publish", promptPh: "Describe what to generate…" },
    search: { title: "Search", placeholder: "Search posts & Q&A…", tags: "Popular tags" },
    profile: { title: "Profile", myPosts: "My posts", history: "Activity" },
    role: { tourist: "Tourist", student: "Student", local: "Local", admin: "Admin" },
    auth: { login: "Log in", register: "Sign up", logout: "Log out" },
  },
  ja: {
    appName: "WANDERCHINA",
    nav: { feed: "フィード", search: "検索", post: "投稿", me: "マイ" },
    category: { all: "すべて", scenic: "観光", food: "グルメ", life: "生活" },
    feed: { title: "コミュニティ", recommend: "おすすめ", loadMore: "もっと見る", empty: "投稿がありません" },
    post: { comment: "コメント", like: "いいね", share: "共有", back: "戻る" },
    create: { title: "投稿", ai: "AI生成", publish: "公開", promptPh: "生成内容を入力…" },
    search: { title: "検索", placeholder: "投稿を検索…", tags: "人気タグ" },
    profile: { title: "プロフィール", myPosts: "投稿", history: "履歴" },
    role: { tourist: "観光客", student: "留学生", local: "現地", admin: "管理" },
    auth: { login: "ログイン", register: "登録", logout: "ログアウト" },
  },
  ko: {
    appName: "WANDERCHINA",
    nav: { feed: "피드", search: "검색", post: "글쓰기", me: "내 정보" },
    category: { all: "전체", scenic: "명소", food: "맛집", life: "생활팁" },
    feed: { title: "커뮤니티", recommend: "추천", loadMore: "더 보기", empty: "게시물 없음" },
    post: { comment: "댓글", like: "좋아요", share: "공유", back: "뒤로" },
    create: { title: "글 작성", ai: "AI 생성", publish: "게시", promptPh: "생성할 내용을 입력…" },
    search: { title: "검색", placeholder: "게시물 검색…", tags: "인기 태그" },
    profile: { title: "프로필", myPosts: "내 글", history: "활동" },
    role: { tourist: "관광객", student: "유학생", local: "현지인", admin: "관리자" },
    auth: { login: "로그인", register: "가입", logout: "로그아웃" },
  },
};

export const i18n = createI18n({
  legacy: false,
  locale: (localStorage.getItem("wc_locale") as keyof typeof messages) || "zh",
  fallbackLocale: "en",
  messages,
});
