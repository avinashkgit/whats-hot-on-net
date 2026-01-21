import { useEffect, useMemo, useState } from "react";
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
} from "@/components/ui/pagination";
import { AdSense } from "@/components/AdSense";
import { AdPreview } from "@/components/AdPreview";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface HomeProps {
  category?: string;
}

/* ===========================
   WINDOWED PAGINATION HELPER
=========================== */
const getVisiblePages = (current: number, total: number, delta = 2) => {
  const pages: number[] = [];
  const start = Math.max(1, current - delta);
  const end = Math.min(total, current + delta);

  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
};

export default function Home({ category }: HomeProps) {
  const [, setLocation] = useLocation();

  /* ===========================
     ADS CONFIG
  ============================ */
  const SHOW_AD_PREVIEW = false;
  const ADSENSE_CLIENT = "ca-pub-4156721166651159";
  const HOME_AD_AFTER_FEATURE_ARTICLE = "2150862406";
  const HOME_AD_WITHIN_CARDS = "5898535727";

  /* ===========================
     PAGINATION (URL BASED)
  ============================ */
  const search = useSearch();
  const searchParams = new URLSearchParams(search);
  const page = parseInt(searchParams.get("page") || "1", 10);
  const limit = 10;

  const { data, isLoading, error } = useArticles({
    category,
    page,
    limit,
  });

  const articles = data?.items ?? [];
  const totalPages = data?.totalPages ?? 1;

  /* ===========================
     RESPONSIVE GRID
  ============================ */
  const [cardsPerRow, setCardsPerRow] = useState(3);

  useEffect(() => {
    const update = () => {
      const w = window.innerWidth;
      if (w >= 1024) setCardsPerRow(3);
      else if (w >= 768) setCardsPerRow(2);
      else setCardsPerRow(1);
    };

    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  /* ===========================
     FEATURED + LIST
  ============================ */
  const featuredArticle = useMemo(() => {
    return page === 1 ? articles[0] : undefined;
  }, [articles, page]);

  const listToRender = useMemo(() => {
    if (page === 1) return articles.slice(1);
    return articles;
  }, [articles, page]);

  /* ===========================
     ADSENSE SAFETY
  ============================ */
  const allowAdsOnThisPage = !category;
  const shouldShowRowAds = allowAdsOnThisPage && listToRender.length >= 6;
  const MAX_ADS_PER_PAGE = 3;
  const cardsPerAd = cardsPerRow === 1 ? 2 : cardsPerRow;

  const [readyToShowAds, setReadyToShowAds] = useState(false);

  useEffect(() => {
    setReadyToShowAds(false);
    if (!data || isLoading) return;

    const t = window.setTimeout(() => setReadyToShowAds(true), 800);
    return () => window.clearTimeout(t);
  }, [data, isLoading, page, category]);

  const hasEnoughContent =
    page === 1
      ? !!featuredArticle && listToRender.length >= 6
      : listToRender.length >= 6;

  const allowAdsNow = allowAdsOnThisPage && readyToShowAds && hasEnoughContent;

  /* ===========================
     PAGE CHANGE HANDLER
  ============================ */
  const handlePageChange = (newPage: number) => {
    const params = new URLSearchParams(search);
    params.set("page", newPage.toString());

    const basePath = category ? `/category/${category}` : "/";
    setLocation(`${basePath}?${params.toString()}`);

    document.getElementById("page-top")?.scrollIntoView({
      behavior: "smooth",
    });
  };

  /* ===========================
     ERROR STATE
  ============================ */
  if (error) {
    return (
      <div className="min-h-screen flex flex-col overflow-x-hidden">
        <Navigation />
        <main className="container mx-auto px-4 py-24 flex-grow flex flex-col items-center justify-center text-center">
          <h2 className="text-2xl md:text-3xl font-bold mb-4">
            Unable to load articles
          </h2>
          <p className="text-muted-foreground max-w-md mb-8">
            Something went wrong while fetching stories. Please try again.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 rounded-md bg-primary text-primary-foreground font-semibold hover:opacity-90"
          >
            Try again
          </button>
        </main>
        <Footer />
      </div>
    );
  }

  /* ===========================
     LOADING STATE
  ============================ */
  if (isLoading && !data) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navigation />
        <main className="container mx-auto px-4 py-16">
          {!category && <ArticleCardSkeleton featured />}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-16">
            {Array.from({ length: 9 }).map((_, i) => (
              <ArticleCardSkeleton key={i} />
            ))}
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  /* ===========================
     RENDER
  ============================ */
  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden">
      <div id="page-top" />
      <Navigation />

      <main className="container mx-auto px-4 py-16 flex-grow">
        {!category && page === 1 && (
          <div className="mb-12 text-center max-w-2xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-black mb-4">
              Stories that matter, trending across the world.
            </h1>
            <p className="text-muted-foreground">
              Essential news, science, tech, culture, and global insights.
            </p>
          </div>
        )}

        {featuredArticle && page === 1 && (
          <div className="mb-16">
            <ArticleCard article={featuredArticle} featured />
          </div>
        )}

        {allowAdsNow && page === 1 && featuredArticle && (
          <div className="my-10">
            {SHOW_AD_PREVIEW ? (
              <AdPreview label="Ad after Featured" />
            ) : (
              <AdSense
                adClient={ADSENSE_CLIENT}
                adSlot={HOME_AD_AFTER_FEATURE_ARTICLE}
              />
            )}
          </div>
        )}

        {/* GRID — ONLY spacing changed */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-10">
          {(() => {
            const elements: JSX.Element[] = [];
            let adsPlaced = 0;

            listToRender.forEach((article, index) => {
              elements.push(<ArticleCard key={article.id} article={article} />);

              const isEndOfRow = (index + 1) % cardsPerAd === 0;
              const isNotLast = index !== listToRender.length - 1;

              if (
                allowAdsNow &&
                shouldShowRowAds &&
                isEndOfRow &&
                isNotLast &&
                adsPlaced < MAX_ADS_PER_PAGE
              ) {
                adsPlaced++;
                elements.push(
                  <div key={`ad-${index}`} className="col-span-full">
                    {SHOW_AD_PREVIEW ? (
                      <AdPreview label="Ad between rows" />
                    ) : (
                      <AdSense
                        adClient={ADSENSE_CLIENT}
                        adSlot={HOME_AD_WITHIN_CARDS}
                      />
                    )}
                  </div>,
                );
              }
            });

            return elements;
          })()}
        </div>

        {/* PAGINATION — COMPLETELY UNCHANGED */}
        {totalPages > 1 && (
          <div className="mt-20 flex justify-center">
            <div className="w-full max-w-md">
              <Pagination>
                <PaginationContent className="flex justify-center gap-2">
                  <PaginationItem>
                    <button
                      aria-label="Previous page"
                      onClick={() => page > 1 && handlePageChange(page - 1)}
                      className={`h-9 w-9 flex items-center justify-center rounded-md border transition
                        ${
                          page === 1
                            ? "pointer-events-none opacity-40"
                            : "hover:bg-muted"
                        }`}
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </button>
                  </PaginationItem>

                  {page > 3 && (
                    <>
                      <PaginationItem>
                        <PaginationLink
                          href="#"
                          onClick={(e) => {
                            e.preventDefault();
                            handlePageChange(1);
                          }}
                        >
                          1
                        </PaginationLink>
                      </PaginationItem>
                      <span className="px-2 text-muted-foreground">…</span>
                    </>
                  )}

                  {getVisiblePages(page, totalPages).map((p) => (
                    <PaginationItem key={p}>
                      <PaginationLink
                        href="#"
                        isActive={p === page}
                        onClick={(e) => {
                          e.preventDefault();
                          handlePageChange(p);
                        }}
                      >
                        {p}
                      </PaginationLink>
                    </PaginationItem>
                  ))}

                  {page < totalPages - 2 && (
                    <>
                      <span className="px-2 text-muted-foreground">…</span>
                      <PaginationItem>
                        <PaginationLink
                          href="#"
                          onClick={(e) => {
                            e.preventDefault();
                            handlePageChange(totalPages);
                          }}
                        >
                          {totalPages}
                        </PaginationLink>
                      </PaginationItem>
                    </>
                  )}

                  <PaginationItem>
                    <button
                      aria-label="Next page"
                      onClick={() =>
                        page < totalPages && handlePageChange(page + 1)
                      }
                      className={`h-9 w-9 flex items-center justify-center rounded-md border transition
                        ${
                          page === totalPages
                            ? "pointer-events-none opacity-40"
                            : "hover:bg-muted"
                        }`}
                    >
                      <ChevronRight className="h-4 w-4" />
                    </button>
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
