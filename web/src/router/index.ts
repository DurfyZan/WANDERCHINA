import { createRouter, createWebHistory } from "vue-router";
import { authStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/community" },
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
      meta: { guest: true },
    },
    {
      path: "/register",
      name: "register",
      component: () => import("@/views/RegisterView.vue"),
      meta: { guest: true },
    },
    {
      path: "/onboarding",
      name: "onboarding",
      component: () => import("@/views/OnboardingView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/community",
      component: () => import("@/layouts/CommunityLayout.vue"),
      meta: { requiresAuth: true, requiresProfile: true },
      children: [
        { path: "", name: "feed", component: () => import("@/views/FeedView.vue") },
        { path: "search", name: "search", component: () => import("@/views/SearchView.vue") },
        { path: "post/new", name: "post-new", component: () => import("@/views/CreatePostView.vue") },
        { path: "post/:id", name: "post-detail", component: () => import("@/views/PostDetailView.vue") },
        { path: "user", name: "user-center", component: () => import("@/views/UserCenterView.vue") },
      ],
    },
    {
      path: "/chat",
      name: "chat",
      component: () => import("@/views/ChatView.vue"),
      meta: { guest: true },
    },
  ],
});

router.beforeEach(async (to) => {
  if (!authStore.isLoggedIn) {
    await authStore.hydrate();
  }

  if (to.meta.guest && authStore.isLoggedIn) {
    return authStore.state.canEnterCommunity ? "/community" : "/onboarding";
  }

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return { name: "login", query: { redirect: to.fullPath } };
  }

  if (to.meta.requiresProfile && authStore.isLoggedIn && !authStore.state.canEnterCommunity) {
    return "/onboarding";
  }

  if (to.name === "onboarding" && authStore.state.canEnterCommunity) {
    return "/community";
  }
});

export default router;
