<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";

const emit = defineEmits<{ generated: [text: string] }>();
const { t } = useI18n();

const prompt = ref("");
const genType = ref<"post" | "comment" | "qa">("post");
const tags = ref("");
const loading = ref(false);
const error = ref("");

async function generate() {
  if (!prompt.value.trim()) return;
  loading.value = true;
  error.value = "";
  try {
    const tagList = tags.value
      .split(/[,，]/)
      .map((s) => s.trim())
      .filter(Boolean);
    const res = await api.generate(genType.value, prompt.value, tagList);
    emit("generated", res.generated_text);
  } catch {
    error.value = "生成失败，请稍后重试";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <section class="card border-dashed border-brand/30 bg-brand/5">
    <h3 class="mb-3 text-sm font-semibold text-brand">{{ t("create.ai") }}</h3>
    <select v-model="genType" class="input mb-2">
      <option value="post">帖子</option>
      <option value="qa">问答</option>
      <option value="comment">评论</option>
    </select>
    <input v-model="tags" class="input mb-2" placeholder="标签，逗号分隔" />
    <textarea v-model="prompt" class="input mb-2" rows="3" :placeholder="t('create.promptPh')" />
    <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
    <button type="button" class="btn-primary w-full" :disabled="loading" @click="generate">
      {{ loading ? "…" : t("create.ai") }}
    </button>
  </section>
</template>
