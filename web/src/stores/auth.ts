import { reactive } from "vue";
import { api, clearToken, getToken, setToken } from "@/api/client";
import type { UserProfile } from "@/api/types";

export const authState = reactive({
  token: getToken() as string | null,
  profile: null as UserProfile | null,
  canEnterCommunity: false,
});

export const authStore = {
  get state() {
    return authState;
  },

  get isLoggedIn() {
    return !!authState.token;
  },

  async hydrate() {
    const token = getToken();
    if (!token) return;
    authState.token = token;
    await authStore.refresh();
  },

  async login(username: string, password: string) {
    const res = await api.login(username, password);
    setToken(res.access_token);
    authState.token = res.access_token;
    await authStore.refresh();
    return res;
  },

  logout() {
    clearToken();
    authState.token = null;
    authState.profile = null;
    authState.canEnterCommunity = false;
  },

  async refresh() {
    if (!authState.token) return;
    try {
      const access = await api.communityAccess();
      authState.profile = access.user;
      authState.canEnterCommunity = access.can_enter_community;
    } catch {
      authState.profile = await api.getProfile();
      authState.canEnterCommunity = authState.profile.profile_completed;
    }
  },
};
