import { motion } from "framer-motion";

export function ArticleDetailSkeleton() {
  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Keep Nav visible while loading */}
      <div className="sticky top-0 z-50">
        {/* Navigation will be rendered from ArticleDetail itself */}
      </div>

      <main className="flex-grow">
        <article className="pb-24">
          {/* =========================
              HEADER SKELETON
          ========================== */}
          <div className="bg-secondary/30 pt-16 pb-20">
            <div className="container mx-auto px-4 max-w-4xl text-center">
              {/* Category */}
              <div className="flex justify-center mb-6">
                <div className="h-5 w-28 rounded-full skeleton" />
              </div>

              {/* Title */}
              <motion.div
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4 mb-8"
              >
                <div className="h-10 md:h-12 lg:h-14 w-[95%] mx-auto rounded-2xl skeleton" />
                <div className="h-10 md:h-12 lg:h-14 w-[75%] mx-auto rounded-2xl skeleton" />
              </motion.div>

              {/* Summary */}
              <div className="space-y-3 max-w-2xl mx-auto mb-8">
                <div className="h-6 w-full rounded-xl skeleton" />
                <div className="h-6 w-[90%] mx-auto rounded-xl skeleton" />
              </div>

              {/* Meta row */}
              <div className="flex flex-wrap justify-center gap-6 border-t border-border pt-6">
                <div className="h-4 w-32 rounded-full skeleton" />
                <div className="h-4 w-24 rounded-full skeleton" />
                <div className="h-4 w-28 rounded-full skeleton" />

                {/* Mobile share skeleton (hidden on desktop like original) */}
                <div className="flex items-center gap-3 md:hidden">
                  <div className="h-4 w-16 rounded-full skeleton" />
                  <div className="h-4 w-4 rounded-full skeleton" />
                  <div className="h-4 w-16 rounded-full skeleton" />
                </div>
              </div>
            </div>
          </div>

          {/* =========================
              HERO IMAGE SKELETON
          ========================== */}
          <div className="container mx-auto px-4 max-w-5xl mt-12 md:mt-16">
            <div className="relative overflow-hidden rounded-2xl shadow-2xl bg-gradient-to-b from-secondary/20 to-transparent">
              <div className="w-full h-[260px] md:h-[420px] lg:h-[520px] skeleton" />
            </div>
          </div>

          {/* =========================
              CONTENT + SHARE SKELETON
          ========================== */}
          <div className="container mx-auto px-4 max-w-3xl mt-16 grid md:grid-cols-[1fr_auto] gap-12">
            {/* Content */}
            <div className="prose prose-lg dark:prose-invert max-w-none">
              <div className="space-y-4">
                <div className="h-6 w-full rounded-xl skeleton" />
                <div className="h-6 w-[96%] rounded-xl skeleton" />
                <div className="h-6 w-[90%] rounded-xl skeleton" />
                <div className="h-6 w-[94%] rounded-xl skeleton" />
                <div className="h-6 w-[88%] rounded-xl skeleton" />
                <div className="h-6 w-[92%] rounded-xl skeleton" />
                <div className="h-6 w-[85%] rounded-xl skeleton" />
              </div>
            </div>

            {/* Desktop Share */}
            <aside className="hidden md:block sticky top-32 space-y-4">
              <div className="h-3 w-14 rounded-full skeleton" />
              <div className="h-12 w-12 rounded-full skeleton" />
              <div className="h-12 w-12 rounded-full skeleton" />
            </aside>
          </div>

          {/* =========================
              TAG SKELETON
          ========================== */}
          <div className="container mx-auto px-4 max-w-3xl mt-16 border-t pt-6">
            <div className="h-9 w-40 rounded-full skeleton" />
          </div>
        </article>
      </main>
    </div>
  );
}
