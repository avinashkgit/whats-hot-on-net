// =======================
// === DOMAIN TYPES ===
// =======================

export interface Topic {
  id: string;
  name: string;
  slug: string;
}

export interface Article {
  id: string;
  title: string;
  slug: string;
  content: string;       // HTML or markdown
  summary: string;
  imageUrl?: string;     // optional (important)
  topicId: string;
  views: number;
  createdAt: string;     // ISO string from API
}

// Article joined with topic
export interface ArticleWithTopic extends Article {
  topic: Topic;
}

// =======================
// === INSERT / CREATE ===
// =======================

// Used when creating a new article
export interface InsertArticle
  extends Omit<Article, "id" | "views" | "createdAt" | "slug"> {
  slug?: string; // optional if backend generates it
}

// =======================
// === API RESPONSES ===
// =======================

export type TopicResponse = Topic;

export type ArticleResponse = ArticleWithTopic;

// Generic paginated response
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}
