import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "@/api/client";
import type { Post, PostCategory } from "@/api/types";

export const useCommunityStore = defineStore("community", () => {
  const category = ref<PostCategory>("all");
  const posts = ref<Post[]>([]);
  const recommendations = ref<Post[]>([]);
  const page = ref(1);
  const hasMore = ref(true);
  const loading = ref(false);

  async function loadRecommendations() {
    recommendations.value = await api.recommendations();
  }

  async function loadFeed(reset = false) {
    if (loading.value) return;
    loading.value = true;
    try {
      if (reset) {
        page.value = 1;
        posts.value = [];
      }
      const res = await api.listPosts(category.value === "all" ? undefined : category.value, page.value);
      posts.value = reset ? res.items : [...posts.value, ...res.items];
      hasMore.value = res.has_more;
      if (res.has_more) page.value += 1;
    } finally {
      loading.value = false;
    }
  }

  function setCategory(c: PostCategory) {
    category.value = c;
    return loadFeed(true);
  }

  return {
    category,
    posts,
    recommendations,
    hasMore,
    loading,
    loadRecommendations,
    loadFeed,
    setCategory,
  };
});
