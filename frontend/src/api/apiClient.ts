import {
  Category,
  PaginatedResponse,
  ArticleWithCategory,
  Article,
  NotificationTokenResponse,
  NotificationTokenCreate,
} from "@/models/schema";

export const BASE_URL = `https://api.hotonnet.com`;
export const WEB_URL = `https://hotonnet.com`;
const API_BASE = `${BASE_URL}/api`;
// const API_BASE = "http://127.0.0.1:8000";

const routes = {
  categories: {
    list: `${API_BASE}/categories`,
  },
  articles: {
    list: `${API_BASE}/articles`,
    get: (slug: string) => `${API_BASE}/articles/${slug}`,
    create: `${API_BASE}/articles`,
  },
  notifications: {
    saveToken: `${API_BASE}/notifications/token`,
  },
};

/* ===========================
   === FETCH CORE ===
=========================== */

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({
      message: "Unknown error",
    }));
    throw error;
  }

  return res.json() as Promise<T>;
}

/* ===========================
   === PUBLIC API CLIENT ===
=========================== */

export const apiClient = {
  /* ---------- CATEGORIES ---------- */
  getCategories() {
    return apiFetch<Category[]>(routes.categories.list);
  },

  /* ---------- ARTICLES ---------- */
  getArticles(params?: {
    category?: string; // ✅ slug, not ID
    page?: number;
    limit?: number;
  }) {
    const query = params
      ? `?${new URLSearchParams(
          Object.entries(params)
            .filter(([, v]) => v !== undefined)
            .reduce(
              (acc, [k, v]) => ({ ...acc, [k]: String(v) }),
              {} as Record<string, string>,
            ),
        ).toString()}`
      : "";

    return apiFetch<PaginatedResponse<ArticleWithCategory>>(
      `${routes.articles.list}${query}`,
    );
  },

  getArticleBySlug(slug: string) {
    return apiFetch<ArticleWithCategory>(routes.articles.get(slug));
  },

  createArticle(data: Omit<Article, "id" | "views" | "createdAt">) {
    return apiFetch<Article>(routes.articles.create, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /* ---------- NOTIFICATIONS ---------- */
  saveNotificationToken(payload: NotificationTokenCreate) {
    return apiFetch<NotificationTokenResponse>(routes.notifications.saveToken, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};
