<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";
import type { Post } from "@/api/types";
import PostCard from "@/components/PostCard.vue";

const { t } = useI18n();
const query = ref("");
const hotTags = ["美食", "成都", "地铁", "攻略", "翻译"];
const results = ref<Post[]>([]);
const loading = ref(false);

async function search(tag?: string) {
  if (tag) query.value = tag;
  loading.value = true;
  try {
    const res = await api.search(query.value, tag);
    results.value = res.items;
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <section>
    <h2 class="mb-3 text-lg font-bold">{{ t("search.title") }}</h2>
    <form class="mb-4 flex gap-2" @submit.prevent="search()">
      <input v-model="query" class="input flex-1" :placeholder="t('search.placeholder')" />
      <button type="submit" class="btn-primary shrink-0">Go</button>
    </form>
    <p class="mb-2 text-xs text-muted">{{ t("search.tags") }}</p>
    <div class="mb-6 flex flex-wrap gap-2">
      <button
        v-for="tag in hotTags"
        :key="tag"
        type="button"
        class="rounded-full border border-gray-200 bg-white px-3 py-1 text-xs hover:border-brand"
        @click="search(tag)"
      >
        #{{ tag }}
      </button>
    </div>
    <p v-if="loading" class="text-muted">…</p>
    <PostCard v-for="p in results" :key="p.id" :post="p" />
  </section>
</template>
