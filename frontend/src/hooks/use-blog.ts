import {
  useQuery,
  useMutation,
  useQueryClient,
  keepPreviousData,
} from "@tanstack/react-query";

import { apiClient } from "@/api/apiClient";
import type { Article } from "@/models/schema";

/* ======================================================
   TEMP DATA SWITCH
   ------------------------------------------------------
   👉 true  = use placeholder data (backend down)
   👉 false = use real API
====================================================== */

const USE_TEMP_DATA = false;

/* ===========================
   === CATEGORIES ===
=========================== */

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],

    queryFn: async () => {
      if (USE_TEMP_DATA) {
        return [
          {
            id: "temp-category",
            name: "News",
            slug: "news",
          },
        ];
      }

      // backend: GET /categories
      return apiClient.getCategories();
    },

    retry: USE_TEMP_DATA ? false : 3,
    staleTime: 1000 * 60 * 5, // 5 minutes (categories rarely change)
  });
}

/* ===========================
   === ARTICLES (LIST) ===
=========================== */

interface UseArticlesParams {
  category?: string; // category slug
  page?: number;
  limit?: number;
}

export function useArticles({
  category,
  page = 1,
  limit = 10
}: UseArticlesParams) {
  return useQuery({
    // ✅ category must be part of the key
    queryKey: ["articles", category, page, limit],

    queryFn: async () => {
      if (USE_TEMP_DATA) {
        return {
          items: [],
          total: 0,
          page,
          limit,
          totalPages: 0,
        };
      }

      // backend: GET /articles?category=slug&page=&limit=
      return apiClient.getArticles({
        category,
        page,
        limit,
      });
    },

    placeholderData: keepPreviousData,
    retry: USE_TEMP_DATA ? false : 3,
  });
}

/* ===========================
   === SINGLE ARTICLE ===
=========================== */

export function useArticle(slug: string) {
  return useQuery({
    queryKey: ["article", slug],
    enabled: !!slug,

    queryFn: async () => {
      if (USE_TEMP_DATA) return null;

      // backend: GET /articles/:slug
      return apiClient.getArticleBySlug(slug);
    },

    retry: USE_TEMP_DATA ? false : 3,
  });
}

/* ===========================
   === CREATE ARTICLE ===
=========================== */

export function useCreateArticle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (
      data: Omit<Article, "id" | "views" | "createdAt">
    ) => {
      return apiClient.createArticle(data);
    },

    onSuccess: () => {
      // 🔄 refresh all article lists
      queryClient.invalidateQueries({
        queryKey: ["articles"],
      });
    },
  });
}
