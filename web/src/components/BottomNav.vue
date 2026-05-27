<script setup lang="ts">
import { useI18n } from "vue-i18n";
</script>

<template>
  <nav class="fixed bottom-0 left-0 right-0 z-20 border-t border-gray-200 bg-white/95 backdrop-blur">
    <div class="mx-auto flex max-w-lg justify-around py-2">
      <router-link to="/community" class="nav-item" active-class="text-brand font-semibold">
        {{ $t("nav.feed") }}
      </router-link>
      <router-link to="/community/search" class="nav-item" active-class="text-brand font-semibold">
        {{ $t("nav.search") }}
      </router-link>
      <router-link to="/community/post/new" class="nav-item text-brand font-bold text-lg">+</router-link>
      <router-link
        :to="{ name: 'user-center' }"
        class="nav-item"
        active-class="text-brand font-semibold"
      >
        {{ $t("nav.me") }}
      </router-link>
    </div>
  </nav>
</template>

<style scoped>
.nav-item {
  @apply flex flex-col items-center px-3 py-1 text-xs text-muted;
}
</style>
