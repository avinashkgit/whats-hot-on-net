import { useArticles } from "@/hooks/use-blog";
import { ArticleCard } from "@/components/ArticleCard";
import { ArticleCardSkeleton } from "@/components/ArticleCardSkeleton";
import { Navigation } from "@/components/Navigation";
import { Footer } from "@/components/Footer";
import { useLocation, useSearch } from "wouter";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

interface HomeProps {
  category?: string;
}

export default function Home({ category }: HomeProps) {
  const [, setLocation] = useLocation();

  // Pagination
  const search = useSearch();
  const searchParams = new URLSearchParams(search);
  const page = parseInt(searchParams.get("page") || "1", 10);
  const limit = 10;

  const { data, isLoading, error } = useArticles({
    category,
    page,
    limit,
  });

  /* ===========================
     ERROR STATE
  ============================ */

  if (error) {
    console.error("ARTICLES QUERY ERROR:", error);
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-background p-4">
        <h2 className="text-2xl font-bold mb-4">Unable to load articles</h2>
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-2 bg-primary text-primary-foreground rounded-full font-bold"
        >
          Try Again
        </button>
      </div>
    );
  }

  /* ===========================
     PAGINATION HANDLER
  ============================ */

  const handlePageChange = (newPage: number) => {
    const params = new URLSearchParams(search);
    params.set("page", newPage.toString());

    const basePath = category ? `/category/${category}` : "/";
    setLocation(`${basePath}?${params.toString()}`);

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  /* ===========================
     LOADING STATE (SKELETON UI)
  ============================ */

  if (isLoading && !data) {
    return (
      <div className="min-h-screen bg-background font-sans text-foreground flex flex-col">
        <Navigation />

        <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16 flex-grow">
          {/* HERO HEADER (HOME ONLY) */}
          {!category && page === 1 && (
            <div className="mb-12 text-center max-w-2xl mx-auto">
              <h1 className="text-3xl md:text-5xl font-display font-black tracking-tight mb-4 leading-tight">
                Stories that matter, trending across the world.
              </h1>
              <p className="text-lg text-muted-foreground">
                Essential news, science, tech, culture, and global insights.
              </p>
            </div>
          )}

          {/* FEATURED SKELETON */}
          {!category && page === 1 && <ArticleCardSkeleton featured />}

          {page === 1 && <div className="border-t border-border my-16" />}

          {/* GRID SKELETON */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-12">
            {Array.from({ length: page === 1 ? 9 : 10 }).map((_, i) => (
              <ArticleCardSkeleton key={i} />
            ))}
          </div>
        </main>

        <Footer />
      </div>
    );
  }

  if (!data) return null;

  const { items: articles, totalPages } = data;
  const featuredArticle = articles[0];
  const remainingArticles = articles.slice(1);

  /* ===========================
     RENDER
  ============================ */

  return (
    <div className="min-h-screen bg-background font-sans text-foreground flex flex-col">
      <Navigation />

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16 flex-grow">
        {/* ===========================
            HERO HEADER (HOME ONLY)
        ============================ */}
        {!category && page === 1 && (
          <div className="mb-12 text-center max-w-2xl mx-auto">
            <h1 className="text-3xl md:text-5xl font-display font-black tracking-tight mb-4 leading-tight">
              Stories that matter, trending across the world.
            </h1>
            <p className="text-lg text-muted-foreground">
              Essential news, science, tech, culture, and global insights.
            </p>
          </div>
        )}

        {/* ===========================
            FEATURED ARTICLE
        ============================ */}
        {featuredArticle && page === 1 && (
          <ArticleCard article={featuredArticle} featured />
        )}

        {page === 1 && articles.length > 0 && (
          <div className="border-t border-border my-16" />
        )}

        {/* ===========================
            ARTICLE GRID
        ============================ */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-12">
          {(page === 1 ? remainingArticles : articles).map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>

        {/* ===========================
            EMPTY STATE
        ============================ */}
        {articles.length === 0 && (
          <div className="text-center py-20 bg-muted/30 rounded-3xl">
            <h3 className="text-xl font-bold text-muted-foreground">
              No articles found in this category.
            </h3>
            <button
              onClick={() => setLocation("/")}
              className="mt-4 text-primary font-bold hover:underline"
            >
              Browse all articles
            </button>
          </div>
        )}

        {/* ===========================
            PAGINATION
        ============================ */}
        {totalPages > 1 && (
          <div className="mt-20">
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      if (page > 1) handlePageChange(page - 1);
                    }}
                    className={
                      page <= 1
                        ? "pointer-events-none opacity-50"
                        : "cursor-pointer"
                    }
                  />
                </PaginationItem>

                {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                  (pageNum) => (
                    <PaginationItem key={pageNum}>
                      <PaginationLink
                        href="#"
                        isActive={pageNum === page}
                        onClick={(e) => {
                          e.preventDefault();
                          handlePageChange(pageNum);
                        }}
                        className="cursor-pointer"
                      >
                        {pageNum}
                      </PaginationLink>
                    </PaginationItem>
                  )
                )}

                <PaginationItem>
                  <PaginationNext
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      if (page < totalPages) handlePageChange(page + 1);
                    }}
                    className={
                      page >= totalPages
                        ? "pointer-events-none opacity-50"
                        : "cursor-pointer"
                    }
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
