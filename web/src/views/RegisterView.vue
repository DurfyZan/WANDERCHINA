<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "@/api/client";
import { authStore } from "@/stores/auth";

const router = useRouter();
const email = ref("");
const username = ref("");
const password = ref("");
const role = ref("tourist");
const error = ref("");
const loading = ref(false);

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    await api.register({ email: email.value, username: username.value, password: password.value, role: role.value });
    await authStore.login(username.value, password.value);
    router.push("/onboarding");
  } catch (e: unknown) {
    const err = e as { detail?: unknown };
    error.value = typeof err.detail === "string" ? err.detail : "注册失败";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <section class="auth-page">
    <form class="card auth-card" @submit.prevent="submit">
      <h1>注册账号</h1>
      <p class="subtitle">加入 WANDERCHINA 社区</p>
      <label class="field">
        <span>邮箱</span>
        <input v-model="email" type="email" required />
      </label>
      <label class="field">
        <span>用户名</span>
        <input v-model="username" required minlength="2" />
      </label>
      <label class="field">
        <span>密码</span>
        <input v-model="password" type="password" required minlength="8" />
      </label>
      <label class="field">
        <span>身份</span>
        <select v-model="role">
          <option value="tourist">外国游客</option>
          <option value="student">在华留学生</option>
          <option value="local">本地人</option>
        </select>
      </label>
      <p v-if="error" class="error-msg">{{ error }}</p>
      <button class="btn btn-primary full" type="submit" :disabled="loading">注册并完善资料</button>
      <p class="foot">
        已有账号？<router-link to="/login">登录</router-link>
      </p>
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
  width: min(400px, 100%);
}
h1 {
  margin: 0;
}
.subtitle {
  color: var(--muted);
  margin: 0.25rem 0 1.5rem;
}
select {
  padding: 0.65rem 0.85rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  width: 100%;
}
.full {
  width: 100%;
}
.foot {
  text-align: center;
  margin-top: 1rem;
}
</style>
