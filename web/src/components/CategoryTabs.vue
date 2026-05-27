<script setup lang="ts">
import { useI18n } from "vue-i18n";
import type { PostCategory } from "@/api/types";

const props = defineProps<{ modelValue: PostCategory }>();
const emit = defineEmits<{ "update:modelValue": [PostCategory] }>();
const { t } = useI18n();

const tabs: PostCategory[] = ["all", "scenic", "food", "life"];
</script>

<template>
  <div class="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
    <button
      v-for="tab in tabs"
      :key="tab"
      type="button"
      class="shrink-0 rounded-full px-4 py-1.5 text-sm font-medium transition"
      :class="
        props.modelValue === tab
          ? 'bg-brand text-white'
          : 'bg-white text-muted border border-gray-200 hover:border-brand/40'
      "
      @click="emit('update:modelValue', tab)"
    >
      {{ t(`category.${tab}`) }}
    </button>
  </div>
</template>
