const ROLE_LABELS: Record<string, string> = {
  tourist: "外国游客",
  student: "在华留学生",
  local: "本地人",
  admin: "管理员",
};

export function roleLabel(role: string) {
  return ROLE_LABELS[role] ?? role;
}

export function formatTime(iso: string) {
  return new Date(iso).toLocaleString("zh-CN", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
