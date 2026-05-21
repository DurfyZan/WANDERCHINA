<script setup lang="ts">
import AppHeader from "@/components/AppHeader.vue";
</script>

<template>
  <div class="layout">
    <AppHeader />
    <main class="container main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.main {
  padding: 1.5rem 0 3rem;
}
</style>
