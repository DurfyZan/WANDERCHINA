<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { api, mediaUrl } from "@/api/client";
import type { PostDetail } from "@/api/types";
import { formatTime, roleLabel } from "@/utils/role";

const route = useRoute();
const post = ref<PostDetail | null>(null);
const commentText = ref("");
const error = ref("");
const loading = ref(true);

async function load() {
  const id = Number(route.params.id);
  post.value = await api.getPost(id);
}

onMounted(async () => {
  try {
    await load();
  } catch {
    error.value = "帖子不存在或无权访问";
  } finally {
    loading.value = false;
  }
});

async function sendComment() {
  if (!post.value || !commentText.value.trim()) return;
  error.value = "";
  try {
    await api.addComment(post.value.id, commentText.value.trim());
    commentText.value = "";
    await load();
  } catch {
    error.value = "评论失败";
  }
}

async function like() {
  if (!post.value) return;
  try {
    await api.likePost(post.value.id);
  } catch {
    /* ignore duplicate */
  }
}
</script>

<template>
  <section v-if="loading" class="muted">加载中…</section>
  <section v-else-if="error" class="error-msg">{{ error }}</section>
  <section v-else-if="post">
    <router-link class="back" to="/community">← 返回动态</router-link>
    <article class="card">
      <header class="head">
        <img
          v-if="post.author?.avatar_url"
          :src="mediaUrl(post.author.avatar_url)"
          class="avatar"
          alt=""
        />
        <span v-else class="avatar" />
        <motion-div>
          <strong>{{ post.author?.display_name }}</strong>
          <p class="meta">{{ roleLabel(post.author?.role || "") }} · {{ formatTime(post.created_at) }}</p>
        </motion-div>
      </header>
      <h1 v-if="post.title">{{ post.title }}</h1>
      <p class="body">{{ post.body }}</p>
      <p v-if="post.location_name" class="loc">📍 {{ post.location_name }}</p>
      <button class="btn btn-ghost" type="button" @click="like">👍 点赞</button>
    </article>

    <section class="comments card">
      <h3>评论 {{ post.comments.length }}</h3>
      <ul>
        <li v-for="c in post.comments" :key="c.id">
          <strong>{{ c.author?.display_name }}</strong>
          <span class="meta"> · {{ formatTime(c.created_at) }}</span>
          <p>{{ c.body }}</p>
        </li>
      </ul>
      <form class="comment-form" @submit.prevent="sendComment">
        <textarea v-model="commentText" rows="3" placeholder="写下你的评论…" required />
        <button class="btn btn-primary" type="submit">发送</button>
      </form>
    </section>
  </section>
</template>

<style scoped>
.back {
  display: inline-block;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}
.head {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.meta {
  margin: 0;
  font-size: 0.8rem;
  color: var(--muted);
}
.body {
  white-space: pre-wrap;
}
.loc {
  color: var(--muted);
}
.comments {
  margin-top: 1rem;
}
.comments ul {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;
}
.comments li {
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border);
}
.comments li p {
  margin: 0.35rem 0 0;
}
.comment-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.comment-form textarea {
  padding: 0.65rem;
  border: 1px solid var(--border);
  border-radius: 8px;
}
.muted {
  color: var(--muted);
}
</style>
