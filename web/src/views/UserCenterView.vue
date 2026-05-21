<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import { api, mediaUrl } from "@/api/client";
import { useAuthStore } from "@/stores/auth";
import type { InteractionItem, Post, UserPublic } from "@/api/types";
import PostCard from "@/components/PostCard.vue";

const route = useRoute();
const { t } = useI18n();
const auth = useAuthStore();
const userId = computed(() => Number(route.params.id) || auth.profile?.id || 0);
const profile = ref<UserPublic | null>(null);
const posts = ref<Post[]>([]);
const interactions = ref<InteractionItem[]>([]);
const tab = ref<"posts" | "history">("posts");

onMounted(async () => {
  if (!userId.value) return;
  profile.value = await api.getUser(userId.value);
  const res = await api.getUserPosts(userId.value);
  posts.value = res.items;
  interactions.value = await api.getUserInteractions(userId.value);
});
</script>

<template>
  <section v-if="profile" class="space-y-4">
    <header class="card flex gap-4">
      <img
        v-if="profile.avatar_url"
        :src="mediaUrl(profile.avatar_url)"
        class="h-16 w-16 rounded-full object-cover"
        alt=""
      />
      <span v-else class="h-16 w-16 rounded-full bg-gray-200" />
      <section>
        <h2 class="text-lg font-bold">{{ profile.display_name || profile.username }}</h2>
        <p class="text-sm text-brand">{{ t(`role.${profile.role}`) }}</p>
        <p v-if="profile.bio" class="mt-1 text-sm text-muted">{{ profile.bio }}</p>
        <p class="mt-1 text-xs text-muted">{{ profile.post_count }} posts</p>
      </section>
    </header>

    <nav class="flex gap-2 border-b border-gray-200">
      <button
        type="button"
        class="px-3 py-2 text-sm"
        :class="tab === 'posts' ? 'border-b-2 border-brand font-semibold text-brand' : 'text-muted'"
        @click="tab = 'posts'"
      >
        {{ t("profile.myPosts") }}
      </button>
      <button
        type="button"
        class="px-3 py-2 text-sm"
        :class="tab === 'history' ? 'border-b-2 border-brand font-semibold text-brand' : 'text-muted'"
        @click="tab = 'history'"
      >
        {{ t("profile.history") }}
      </button>
    </nav>

    <template v-if="tab === 'posts'">
      <PostCard v-for="p in posts" :key="p.id" :post="p" />
    </template>
    <ul v-else class="card divide-y divide-gray-100">
      <li v-for="item in interactions" :key="item.id" class="py-2 text-sm">
        <router-link :to="`/community/post/${item.post_id}`" class="text-brand">
          {{ item.post_title || `#${item.post_id}` }}
        </router-link>
        <span class="text-muted"> — {{ item.interaction_type }}</span>
      </li>
    </ul>
  </section>
</template>
