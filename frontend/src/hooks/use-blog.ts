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
   === TOPICS ===
=========================== */

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: async () => {
      if (USE_TEMP_DATA) {
        return [
          {
            id: "temp-topic",
            name: "General",
            slug: "general",
          },
        ];
      }

      return apiClient.getTopics();
    },
    retry: USE_TEMP_DATA ? false : 3,
  });
}

/* ===========================
   === ARTICLES ===
=========================== */

export function useArticles(
  topicId?: string,
  page: number = 1,
  limit: number = 10
) {
  return useQuery({
    queryKey: ["articles", { topicId, page, limit }],

    queryFn: async () => {
      return apiClient.getArticles({
        topicId,
        page,
        limit,
      });
    },

    // ✅ React Query v5 best practice
    placeholderData: keepPreviousData,

    // ❌ do not retry when mocking
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
    mutationFn: async (data: Omit<Article, "id" | "views" | "createdAt">) => {
      return apiClient.createArticle(data);
    },

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["articles"],
      });
    },
  });
}
