// placeholderArticles.ts

import { PaginatedResponse, ArticleWithTopic } from "@/models/schema";

export const placeholderArticles: PaginatedResponse<ArticleWithTopic> = {
  items: [
    {
      id: "test-1",
      title: "Loading article...",
      slug: "loading-article",
      content: "",
      summary: "This is placeholder content while data loads.",
      imageUrl: undefined,
      topicId: "test-topic",
      views: 0,
      createdAt: new Date().toISOString(),
      topic: {
        id: "test-topic",
        name: "Loading",
        slug: "loading",
      },
    },
    {
      id: "test-2",
      title: "Another loading article...",
      slug: "loading-article-2",
      content: "",
      summary: "Please wait while we fetch real data.",
      imageUrl: undefined,
      topicId: "test-topic",
      views: 0,
      createdAt: new Date().toISOString(),
      topic: {
        id: "test-topic",
        name: "Loading",
        slug: "loading",
      },
    },
  ],
  total: 2,
  page: 1,
  limit: 10,
  totalPages: 1,
};
