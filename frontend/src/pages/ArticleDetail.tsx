import { Footer } from "@/components/Footer";
import { Navigation } from "@/components/Navigation";
import { useArticle } from "@/hooks/use-blog";
import { format } from "date-fns";
import { motion } from "framer-motion";
import { Calendar, Clock, Copy, Eye, Loader2, Share2 } from "lucide-react";
import { JSXElementConstructor, Key, ReactElement, ReactNode } from "react";
import { useRoute } from "wouter";

export default function ArticleDetail() {
  const [, params] = useRoute("/article/:slug");
  const slug = params?.slug || "";
  const { data: article, isLoading, error } = useArticle(slug);

  /* =========================
     LOADING / ERROR
  ========================== */

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
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
     HELPERS
  ========================== */

  const readTime = Math.ceil(article.content.length / 1000);
  const pageUrl = typeof window !== "undefined" ? window.location.href : "";

  const handleShare = async () => {
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
  };

  const copyLink = async () => {
    await navigator.clipboard.writeText(pageUrl);
  };

  /* =========================
     RENDER
  ========================== */

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Navigation />

      <main className="flex-grow">
        <article className="pb-24">
          {/* =========================
              HEADER
          ========================== */}
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
                  {article.views.toLocaleString()} views
                </span>

                {/* MOBILE SHARE (INLINE, CLEAN) */}
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

          {/* =========================
              HERO IMAGE
          ========================== */}
          {article.imageUrl && (
            <div className="container mx-auto px-4 max-w-5xl -mt-12">
              <motion.img
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                src={article.imageUrl}
                alt={article.title}
                className="rounded-2xl shadow-xl w-full object-cover aspect-[21/9]"
              />
            </div>
          )}

          {/* =========================
              CONTENT + DESKTOP SHARE
          ========================== */}
          <div className="container mx-auto px-4 max-w-3xl mt-16 grid md:grid-cols-[1fr_auto] gap-12">
            <div className="prose prose-lg dark:prose-invert max-w-none">
              {article.content
                .split("\n\n")
                .map(
                  (
                    paragraph:
                      | string
                      | number
                      | boolean
                      | ReactElement<any, string | JSXElementConstructor<any>>
                      | Iterable<ReactNode>
                      | null
                      | undefined,
                    idx: Key
                  ) =>
                    idx === 0 ? (
                      <p
                        key={idx}
                        className="first-letter:text-7xl first-letter:font-black first-letter:pr-4 first-letter:float-left"
                      >
                        {paragraph}
                      </p>
                    ) : (
                      <p key={idx}>{paragraph}</p>
                    )
                )}
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

          {/* =========================
              TAG
          ========================== */}
          <div className="container mx-auto px-4 max-w-3xl mt-16 border-t pt-6">
            <span className="inline-block px-4 py-2 bg-secondary rounded-full text-sm font-medium">
              #{article.category?.slug ?? "general"}
            </span>
          </div>
        </article>
      </main>

      <Footer />
    </div>
  );
}
