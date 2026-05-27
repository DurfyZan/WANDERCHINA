<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { authStore } from "@/stores/auth";

const router = useRouter();
const route = useRoute();
const username = ref("demo");
const password = ref("demo12345");
const error = ref("");
const loading = ref(false);

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    await authStore.login(username.value, password.value);
    const redirect = (route.query.redirect as string) || "";
    if (authStore.state.canEnterCommunity) {
      router.push(redirect || "/community");
    } else {
      router.push("/onboarding");
    }
  } catch (e: unknown) {
    const err = e as { detail?: string };
    error.value = typeof err.detail === "string" ? err.detail : "登录失败";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="card auth-card">
      <h1>WANDERCHINA</h1>
      <p class="subtitle">外国人在华旅行社区</p>
      <form @submit.prevent="submit">
        <div class="field">
          <label>用户名</label>
          <input v-model="username" required autocomplete="username" />
        </div>
        <motion-div class="field">
          <label>密码</label>
          <input v-model="password" type="password" required autocomplete="current-password" />
        </motion-div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button class="btn btn-primary full" type="submit" :disabled="loading">
          {{ loading ? "登录中…" : "登录" }}
        </button>
      </form>
      <p class="foot">
        还没有账号？
        <router-link to="/register">注册</router-link>
      </p>
      <p class="hint">演示账号 demo / demo12345（需先执行 seed_demo）</p>
    </motion-div>
  </motion-div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1rem;
}
.auth-card {
  width: min(400px, 100%);
}
h1 {
  margin: 0;
  font-size: 1.5rem;
}
.subtitle {
  color: var(--muted);
  margin: 0.25rem 0 1.5rem;
}
.full {
  width: 100%;
  margin-top: 0.5rem;
}
.foot {
  text-align: center;
  margin-top: 1.25rem;
  font-size: 0.9rem;
}
.hint {
  font-size: 0.75rem;
  color: var(--muted);
  text-align: center;
  margin-top: 1rem;
}
</style>
