import {
  Category,
  PaginatedResponse,
  ArticleWithTopic,
  Article,
} from "@/models/schema";

const API_BASE = "https://whats-hot-on-net.onrender.com";

const routes = {
  topics: {
    list: `${API_BASE}/topics`,
  },
  articles: {
    list: `${API_BASE}/articles`,
    get: (slug: string) => `${API_BASE}/articles/${slug}`,
    create: `${API_BASE}/articles`,
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
  /* ---------- TOPICS ---------- */
  getTopics() {
    return apiFetch<Category[]>(routes.topics.list);
  },

  /* ---------- ARTICLES ---------- */
  getArticles(params?: { topicId?: string; page?: number; limit?: number }) {
    const query = params
      ? `?${new URLSearchParams(
          Object.entries(params)
            .filter(([, v]) => v !== undefined)
            .reduce(
              (acc, [k, v]) => ({ ...acc, [k]: String(v) }),
              {} as Record<string, string>
            )
        ).toString()}`
      : "";

    return apiFetch<PaginatedResponse<ArticleWithTopic>>(
      `${routes.articles.list}${query}`
    );
  },

  getArticleBySlug(slug: string) {
    return apiFetch<ArticleWithTopic>(routes.articles.get(slug));
  },

  createArticle(data: Omit<Article, "id" | "views" | "createdAt">) {
    return apiFetch<Article>(routes.articles.create, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};
