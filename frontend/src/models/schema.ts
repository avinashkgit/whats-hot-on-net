// =======================
// === DOMAIN TYPES ===
// =======================

export interface Category {
  id: string;
  name: string;
  slug: string;
}

export interface Article {
  id: string;
  topic: string;
  title: string;
  slug: string;
  content: string;       // HTML or markdown
  summary: string;
  imageUrl?: string;     // optional (important)
  categoryId: string;
  views: number;
  createdAt: string;     // ISO string from API
}

// Article joined with topic
export interface ArticleWithCategory extends Article {
  category: Category;
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

export type CategoryResponse = Category;

export type ArticleResponse = ArticleWithCategory;

// Generic paginated response
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}
