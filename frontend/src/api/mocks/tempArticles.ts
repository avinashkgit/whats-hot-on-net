import { PaginatedResponse, ArticleWithTopic } from "@/models/schema";

export const tempArticles: PaginatedResponse<ArticleWithTopic> = {
  items: [
    {
      id: "temp-1",
      title: "Welcome to HotOnNet",
      slug: "welcome-to-hotonnet",
      summary: "This is temporary data while the backend is unavailable.",
      content: "",
      imageUrl: undefined,
      topicId: "general",
      views: 123,
      createdAt: new Date().toISOString(),
      topic: {
        id: "general",
        name: "General",
        slug: "general",
      },
    },
    {
      id: "temp-2",
      title: "Backend Under Maintenance",
      slug: "backend-maintenance",
      summary: "Displaying mock articles until the API is fixed.",
      content: "",
      imageUrl: undefined,
      topicId: "general",
      views: 98,
      createdAt: new Date().toISOString(),
      topic: {
        id: "general",
        name: "General",
        slug: "general",
      },
    },
  ],
  total: 2,
  page: 1,
  limit: 10,
  totalPages: 1,
};
