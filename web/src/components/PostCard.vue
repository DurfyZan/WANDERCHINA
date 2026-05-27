<script setup lang="ts">
import { useRouter } from "vue-router";
import type { Post } from "@/api/types";
import { mediaUrl } from "@/api/client";
import { formatTime, roleLabel } from "@/utils/role";

defineProps<{ post: Post }>();
const router = useRouter();

function open(id: number) {
  router.push(`/community/post/${id}`);
}
</script>

<template>
  <article class="card post-card" @click="open(post.id)">
    <header class="post-head">
      <img
        v-if="post.author?.avatar_url"
        :src="mediaUrl(post.author.avatar_url)"
        class="avatar"
        alt=""
      />
      <span v-else class="avatar placeholder" />
      <div>
        <strong class="name">{{ post.author?.display_name || "用户" }}</strong>
        <p class="meta">
          <span class="role">{{ roleLabel(post.author?.role || "") }}</span>
          ·
          <span>{{ formatTime(post.created_at) }}</span>
        </p>
      </div>
    </header>
    <h3 v-if="post.title" class="title">{{ post.title }}</h3>
    <p class="body">{{ post.body }}</p>
    <p v-if="post.location_name" class="loc">📍 {{ post.location_name }}</p>
  </article>
</template>

<style scoped>
.post-card {
  cursor: pointer;
  margin-bottom: 1rem;
  transition: transform 0.15s, box-shadow 0.15s;
}
.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(26, 26, 26, 0.08);
}
.post-head {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}
.placeholder {
  display: inline-block;
}
.name {
  display: block;
  font-weight: 600;
}
.meta {
  margin: 0.15rem 0 0;
  font-size: 0.8rem;
  color: var(--muted);
}
.role {
  color: var(--primary);
}
.title {
  margin: 0 0 0.5rem;
  font-size: 1.05rem;
}
.body {
  margin: 0;
  white-space: pre-wrap;
}
.loc {
  margin: 0.75rem 0 0;
  font-size: 0.875rem;
  color: var(--muted);
}
</style>
