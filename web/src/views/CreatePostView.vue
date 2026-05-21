<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "@/api/client";

const router = useRouter();
const title = ref("");
const body = ref("");
const location = ref("");
const error = ref("");
const loading = ref(false);

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    const post = await api.createPost({
      title: title.value || undefined,
      body: body.value,
      location_name: location.value || undefined,
    });
    router.push(`/community/post/${post.id}`);
  } catch (e: unknown) {
    const err = e as { detail?: unknown };
    error.value = typeof err.detail === "string" ? err.detail : "发布失败";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <section class="card">
    <h2>发布帖子</h2>
    <form @submit.prevent="submit">
      <label class="field">
        <span>标题（选填）</span>
        <input v-model="title" placeholder="一句话概括" />
      </label>
      <label class="field">
        <span>内容</span>
        <textarea v-model="body" rows="6" required placeholder="分享旅行体验或提问…" />
      </label>
      <label class="field">
        <span>地点（选填）</span>
        <input v-model="location" placeholder="例如 成都·宽窄巷子" />
      </label>
      <p v-if="error" class="error-msg">{{ error }}</p>
      <footer class="actions">
        <router-link class="btn btn-ghost" to="/community">取消</router-link>
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? "发布中…" : "发布" }}
        </button>
      </footer>
    </form>
  </section>
</template>

<style scoped>
h2 {
  margin-top: 0;
}
.actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}
</style>
