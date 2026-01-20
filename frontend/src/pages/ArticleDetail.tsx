import { Footer } from "@/components/Footer";
import { Navigation } from "@/components/Navigation";
import { useArticle } from "@/hooks/use-blog";
import { format } from "date-fns";
import { motion } from "framer-motion";
import { Calendar, Clock, Copy, Eye, Share2 } from "lucide-react";
import { Helmet } from "react-helmet-async";
import { useMemo } from "react";
import { useRoute } from "wouter";
import { ArticleDetailSkeleton } from "./ArticleDetailSkeleton";
import { AdSense } from "@/components/AdSense";
import { AdPreview } from "@/components/AdPreview";

export default function ArticleDetail() {
  const [, params] = useRoute("/article/:slug");
  const slug = params?.slug || "";
  const { data: article, isLoading, error } = useArticle(slug);

  // ✅ Toggle this:
  const SHOW_AD_PREVIEW = false;

  // ✅ Replace with your actual AdSense values
  const ADSENSE_CLIENT = "ca-pub-4156721166651159";
  const ARTICLE_DETAIL_PARAGRAPHS = "9646209040";

  // ✅ IMPORTANT: hooks must be ABOVE any return
  const paragraphs = useMemo(() => {
    if (!article?.content) return [];
    return article.content
      .split("\n\n")
      .map((p) => p.trim())
      .filter(Boolean);
  }, [article?.content]);

  // ✅ Ads: show only after selected paragraphs (NOT after every paragraph)
  // After 2nd, 5th, 8th paragraph => idx 1, 4, 7
  const adIndexes = useMemo(() => new Set([1, 4, 7]), []);
  const shouldShowAds = paragraphs.length >= 4;

  /* =========================
     LOADING / ERROR
  ========================== */

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background text-foreground flex flex-col">
        <Navigation />
        <ArticleDetailSkeleton />
        <Footer />
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-background p-6 text-center">
        <h2 className="text-3xl font-display font-bold mb-4">
          Article not found
        </h2>
        <p className="text-muted-foreground mb-8 max-w-md">
          The story you are looking for does not exist or has been moved.
        </p>
        <a
          href="/"
          className="px-8 py-3 bg-primary text-primary-foreground rounded-full font-bold shadow hover:bg-primary/90 transition"
        >
          Back to Home
        </a>
      </div>
    );
  }

  /* =========================
     HELPERS & SEO DATA
  ========================== */

  const readTime = Math.max(1, Math.ceil(article.content.length / 1000));
  const pageUrl = typeof window !== "undefined" ? window.location.href : "";

  const seoTitle = article.title;
  const seoDescription =
    article.summary || article.content.substring(0, 160) + "...";
  const seoImage = article.imageUrl || "";
  const canonicalUrl = pageUrl || `https://hotonnet.com/article/${slug}`;

  const handleShare = async () => {
    try {
      if (navigator.share) {
        await navigator.share({
          title: article.title,
          text: article.summary,
          url: pageUrl,
        });
      } else {
        await navigator.clipboard.writeText(pageUrl);
        alert("Link copied to clipboard");
      }
    } catch (e) {
      console.log("Share failed:", e);
    }
  };

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(pageUrl);
      alert("Link copied!");
    } catch (e) {
      console.log("Copy failed:", e);
      alert("Could not copy link");
    }
  };

  return (
    <>
      <Helmet>
        <title>{seoTitle} | HotOnNet</title>
        <meta name="description" content={seoDescription} />
        <meta property="og:title" content={seoTitle} />
        <meta property="og:description" content={seoDescription} />
        <meta property="og:image" content={seoImage} />
        <meta property="og:url" content={canonicalUrl} />
        <meta property="og:type" content="article" />
        <meta property="og:site_name" content="HotOnNet" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={seoTitle} />
        <meta name="twitter:description" content={seoDescription} />
        <meta name="twitter:image" content={seoImage} />
        <meta name="twitter:creator" content="@avinash2it" />
        <meta name="twitter:site" content="@hotonnet_com" />
        <link rel="canonical" href={canonicalUrl} />
      </Helmet>

      <div className="min-h-screen bg-background text-foreground flex flex-col">
        <Navigation />

        <main className="flex-grow">
          <article className="pb-24">
            {/* HEADER */}
            <div className="bg-secondary/30 pt-16 pb-20">
              <div className="container mx-auto px-4 max-w-4xl text-center">
                <div className="text-sm font-bold tracking-wider uppercase text-primary mb-6">
                  {article.category?.name ?? "General"}
                </div>

                <motion.h1
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-4xl md:text-5xl lg:text-6xl font-display font-bold mb-8 leading-tight"
                >
                  {article.title}
                </motion.h1>

                <p className="text-xl text-muted-foreground italic max-w-2xl mx-auto mb-8">
                  {article.summary}
                </p>

                {/* META + MOBILE SHARE */}
                <div className="flex flex-wrap justify-center gap-6 text-sm text-muted-foreground border-t border-border pt-6">
                  <span className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    {format(new Date(article.createdAt), "MMMM d, yyyy")}
                  </span>

                  <span className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    {readTime} min read
                  </span>

                  <span className="flex items-center gap-2">
                    <Eye className="w-4 h-4" />
                    {(article.views ?? 0).toLocaleString()} views
                  </span>

                  {/* MOBILE SHARE */}
                  <div className="flex items-center gap-3 md:hidden text-primary font-semibold">
                    <button
                      onClick={handleShare}
                      className="flex items-center gap-1 hover:underline"
                    >
                      <Share2 className="w-4 h-4" />
                      Share
                    </button>

                    <span className="opacity-40">•</span>

                    <button
                      onClick={copyLink}
                      className="flex items-center gap-1 hover:underline"
                    >
                      <Copy className="w-4 h-4" />
                      Copy
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* HERO IMAGE */}
            {article.imageUrl ? (
              <div className="container mx-auto px-4 max-w-5xl mt-12 md:mt-16">
                <div className="relative overflow-hidden rounded-2xl shadow-2xl bg-gradient-to-b from-secondary/20 to-transparent">
                  <motion.img
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    src={article.imageUrl}
                    alt={article.title}
                    className="w-full h-auto max-h-[80vh] object-contain mx-auto"
                    loading="eager"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent pointer-events-none" />
                </div>
              </div>
            ) : (
              <div className="container mx-auto px-4 max-w-5xl mt-12 md:mt-16">
                <div className="w-full h-64 md:h-96 bg-gradient-to-br from-secondary/50 to-secondary/30 rounded-2xl flex items-center justify-center">
                  <span className="text-muted-foreground text-lg italic">
                    Featured image coming soon...
                  </span>
                </div>
              </div>
            )}

            {/* CONTENT + DESKTOP SHARE */}
            <div className="container mx-auto px-4 max-w-3xl mt-16 grid md:grid-cols-[1fr_auto] gap-12">
              <div className="prose prose-lg dark:prose-invert max-w-none">
                {paragraphs.map((paragraph, idx) => (
                  <div key={idx} className="space-y-8">
                    {idx === 0 ? (
                      <p className="first-letter:text-7xl first-letter:font-black first-letter:pr-4 first-letter:float-left">
                        {paragraph}
                      </p>
                    ) : (
                      <p>{paragraph}</p>
                    )}

                    {/* ✅ Ad only after selected paragraphs */}
                    {shouldShowAds && adIndexes.has(idx) && (
                      <div className="not-prose">
                        {SHOW_AD_PREVIEW ? (
                          <AdPreview label={`Ad after paragraph ${idx + 1}`} />
                        ) : (
                          <AdSense
                            adClient={ADSENSE_CLIENT}
                            adSlot={ARTICLE_DETAIL_PARAGRAPHS}
                            className="max-w-3xl mx-auto"
                          />
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* DESKTOP SHARE */}
              <aside className="hidden md:block sticky top-32 space-y-4">
                <p className="text-xs uppercase font-bold text-muted-foreground">
                  Share
                </p>

                <button
                  onClick={handleShare}
                  className="p-3 rounded-full bg-secondary hover:bg-primary hover:text-white transition block"
                  title="Share"
                >
                  <Share2 className="w-5 h-5" />
                </button>

                <button
                  onClick={copyLink}
                  className="p-3 rounded-full bg-secondary hover:bg-foreground hover:text-background transition block"
                  title="Copy link"
                >
                  <Copy className="w-5 h-5" />
                </button>
              </aside>
            </div>

            {/* TAG */}
            <div className="container mx-auto px-4 max-w-3xl mt-16 border-t pt-6">
              <span className="inline-block px-4 py-2 bg-secondary rounded-full text-sm font-medium">
                #{article.category?.slug ?? "general"}
              </span>
            </div>
          </article>
        </main>

        <Footer />
      </div>
    </>
  );
}
