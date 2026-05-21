<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { api, mediaUrl } from "@/api/client";
import { authStore } from "@/stores/auth";

const router = useRouter();
const displayName = ref("");
const bio = ref("");
const avatarPreview = ref("");
const error = ref("");
const loading = ref(false);

onMounted(async () => {
  await authStore.refresh();
  if (authStore.state.profile) {
    displayName.value = authStore.state.profile.display_name || "";
    bio.value = authStore.state.profile.bio || "";
    avatarPreview.value = mediaUrl(authStore.state.profile.avatar_url);
  }
});

function onFile(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (file) avatarPreview.value = URL.createObjectURL(file);
}

async function submit(e: Event) {
  const form = e.target as HTMLFormElement;
  const fileInput = form.querySelector<HTMLInputElement>('input[type="file"]');
  const file = fileInput?.files?.[0];

  error.value = "";
  if (!displayName.value.trim()) {
    error.value = "请填写姓名或昵称";
    return;
  }
  if (!file && !authStore.state.profile?.avatar_url) {
    error.value = "请上传头像";
    return;
  }

  loading.value = true;
  try {
    await api.updateProfile({ display_name: displayName.value.trim(), bio: bio.value || undefined });
    if (file) await api.uploadAvatar(file);
    await authStore.refresh();
    if (authStore.state.canEnterCommunity) router.push("/community");
    else error.value = "资料仍未完善，请检查头像与姓名";
  } catch (err: unknown) {
    const e = err as { detail?: unknown };
    error.value = typeof e.detail === "string" ? e.detail : "保存失败";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <section class="auth-page">
    <form class="card auth-card" @submit.prevent="submit">
      <h1>完善资料</h1>
      <p class="subtitle">进入社区前请设置头像与姓名</p>

      <label class="avatar-upload">
        <img v-if="avatarPreview" :src="avatarPreview" class="avatar-lg" alt="头像预览" />
        <span v-else class="avatar-lg placeholder">+</span>
        <input type="file" accept="image/*" @change="onFile" />
        <span class="upload-tip">点击上传头像</span>
      </label>

      <label class="field">
        <span>姓名 / 昵称</span>
        <input v-model="displayName" required maxlength="64" placeholder="例如 Alex" />
      </label>
      <label class="field">
        <span>个人简介（选填）</span>
        <textarea v-model="bio" rows="3" placeholder="简单介绍一下自己…" />
      </label>

      <p v-if="error" class="error-msg">{{ error }}</p>
      <button class="btn btn-primary full" type="submit" :disabled="loading">
        {{ loading ? "保存中…" : "进入社区" }}
      </button>
    </form>
  </section>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1rem;
}
.auth-card {
  width: min(420px, 100%);
}
.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  cursor: pointer;
}
.avatar-upload input {
  display: none;
}
.placeholder {
  display: grid;
  place-items: center;
  background: var(--border);
  border-radius: 50%;
  font-size: 2rem;
  color: var(--muted);
}
.upload-tip {
  font-size: 0.85rem;
  color: var(--primary);
}
.full {
  width: 100%;
}
</style>
