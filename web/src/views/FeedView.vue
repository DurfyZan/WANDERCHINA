<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "@/api/client";
import type { Post } from "@/api/types";
import PostCard from "@/components/PostCard.vue";

const posts = ref<Post[]>([]);
const loading = ref(true);
const error = ref("");

onMounted(async () => {
  try {
    posts.value = await api.listPosts();
  } catch {
    error.value = "加载失败";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section>
    <header class="page-head">
      <h2>社区动态</h2>
      <router-link class="btn btn-primary" to="/community/post/new">写帖子</router-link>
    </header>
    <p v-if="loading" class="muted">加载中…</p>
    <p v-else-if="error" class="error-msg">{{ error }}</p>
    <p v-else-if="!posts.length" class="muted">还没有帖子，来发第一条吧。</p>
    <PostCard v-for="p in posts" :key="p.id" :post="p" />
  </section>
</template>

<style scoped>
.page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}
.page-head h2 {
  margin: 0;
}
.muted {
  color: var(--muted);
}
</style>
