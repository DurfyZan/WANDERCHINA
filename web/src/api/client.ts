const TOKEN_KEY = "wc_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function mediaUrl(path: string | null | undefined): string {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  return path;
}

type RequestOptions = RequestInit & { auth?: boolean; form?: boolean };

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {};
  if (!options.form) headers["Content-Type"] = "application/json";
  if (options.auth !== false) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(path, { ...options, headers: { ...headers, ...(options.headers as object) } });
  if (!res.ok) {
    let detail: unknown = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? body;
    } catch {
      /* ignore */
    }
    throw { status: res.status, detail };
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  health() {
    return request<{ status: string; service: string }>("/api/v1/health", { auth: false });
  },

  register(body: { email: string; username: string; password: string; role?: string }) {
    return request("/api/v1/auth/register", { method: "POST", body: JSON.stringify(body), auth: false });
  },

  login(username: string, password: string) {
    const form = new URLSearchParams();
    form.set("username", username);
    form.set("password", password);
    return request<import("./types").LoginResponse>("/api/v1/auth/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
      auth: false,
    });
  },

  getProfile() {
    return request<import("./types").UserProfile>("/api/v1/profile/me");
  },

  updateProfile(body: { display_name?: string; bio?: string }) {
    return request<import("./types").UserProfile>("/api/v1/profile/me", {
      method: "PUT",
      body: JSON.stringify(body),
    });
  },

  uploadAvatar(file: File) {
    const form = new FormData();
    form.append("file", file);
    return request<import("./types").UserProfile>("/api/v1/profile/avatar", {
      method: "POST",
      body: form,
      form: true,
    });
  },

  communityAccess() {
    return request<import("./types").CommunityAccess>("/api/v1/community/access");
  },

  listPosts(limit = 20, offset = 0) {
    return request<import("./types").Post[]>(`/api/v1/community/posts?limit=${limit}&offset=${offset}`);
  },

  getPost(id: number) {
    return request<import("./types").PostDetail>(`/api/v1/community/posts/${id}`);
  },

  createPost(body: { title?: string; body: string; location_name?: string }) {
    return request<import("./types").Post>("/api/v1/community/posts", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  addComment(postId: number, body: string) {
    return request<import("./types").Comment>(`/api/v1/community/posts/${postId}/comments`, {
      method: "POST",
      body: JSON.stringify({ body }),
    });
  },

  likePost(postId: number) {
    return request(`/api/v1/community/posts/${postId}/interactions`, {
      method: "POST",
      body: JSON.stringify({ interaction_type: "like" }),
    });
  },

  translateText(text: string, sourceLang: string, targetLang: string) {
    return request<{ translation: string; target_lang: string }>("/api/v1/community/translate", {
      method: "POST",
      body: JSON.stringify({ text, source_lang: sourceLang, target_lang: targetLang }),
    });
  },

  startGeneration(body: { prompt: string; count: number; format: string }) {
    return request<import("./types").GenerationJob>("/api/v1/dataset/generate", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  getJob(jobId: number) {
    return request<import("./types").GenerationJob>(`/api/v1/dataset/jobs/${jobId}`);
  },

  annotate(body: { texts: string[] }) {
    return request<import("./types").AnnotationResult[]>("/api/v1/dataset/annotate", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  evaluateQuality(body: { job_id: number }) {
    return request<import("./types").QualityEvalResult>("/api/v1/dataset/quality", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  exportDataset(body: { job_id: number; format: string }) {
    return request<{ export_id: number; file_path: string; format: string; record_count: number }>("/api/v1/dataset/export", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
};
