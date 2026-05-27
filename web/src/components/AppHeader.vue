<script setup lang="ts">
import { useRouter } from "vue-router";
import { authStore } from "@/stores/auth";
import { mediaUrl } from "@/api/client";

const router = useRouter();

function logout() {
  authStore.logout();
  router.push("/login");
}
</script>

<template>
  <header class="header">
    <div class="container header-inner">
      <router-link to="/community" class="brand">WANDERCHINA</router-link>
      <nav class="nav">
        <router-link to="/community">动态</router-link>
        <router-link to="/community/post/new">发帖</router-link>
      </nav>
      <div class="user" v-if="authStore.state.profile">
        <img
          v-if="authStore.state.profile.avatar_url"
          :src="mediaUrl(authStore.state.profile.avatar_url)"
          class="avatar"
          alt=""
        />
        <span>{{ authStore.state.profile.display_name || authStore.state.profile.username }}</span>
        <button class="btn btn-ghost" type="button" @click="logout">退出</button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 10;
}
.header-inner {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 0;
}
.brand {
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0.02em;
}
.nav {
  display: flex;
  gap: 1rem;
  flex: 1;
}
.nav a.router-link-active {
  color: var(--primary);
  font-weight: 600;
}
.user {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}
</style>
