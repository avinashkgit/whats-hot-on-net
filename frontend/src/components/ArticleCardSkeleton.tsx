import { motion } from "framer-motion";

interface ArticleCardSkeletonProps {
  featured?: boolean;
}

export function ArticleCardSkeleton({ featured = false }: ArticleCardSkeletonProps) {
  if (featured) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="group relative grid grid-cols-1 md:grid-cols-2 gap-8 items-center mb-16 p-6 rounded-3xl transition-all duration-300 bg-card shadow-[0_4px_20px_-4px_rgba(0,0,0,0.1)] dark:shadow-[0_10px_30px_-5px_rgba(0,0,0,0.7)] border border-border/50"
      >
        {/* Image Skeleton */}
        <div className="block overflow-hidden rounded-2xl aspect-[4/3] md:aspect-[16/10] shadow-md">
          <div className="w-full h-full skeleton" />
        </div>

        {/* Content Skeleton */}
        <div className="space-y-4 md:pr-8">
          {/* Category + Date */}
          <div className="flex items-center space-x-2 text-sm font-bold tracking-wider uppercase">
            <div className="h-7 w-28 rounded-full skeleton" />
            <div className="h-4 w-3 rounded-full skeleton" />
            <div className="h-4 w-32 rounded-full skeleton" />
          </div>

          {/* Title */}
          <div className="space-y-3">
            <div className="h-10 md:h-12 lg:h-14 w-[95%] rounded-2xl skeleton" />
            <div className="h-10 md:h-12 lg:h-14 w-[75%] rounded-2xl skeleton" />
          </div>

          {/* Summary */}
          <div className="space-y-2">
            <div className="h-5 w-full rounded-xl skeleton" />
            <div className="h-5 w-[90%] rounded-xl skeleton" />
            <div className="h-5 w-[80%] rounded-xl skeleton" />
          </div>

          {/* Read Full Story */}
          <div className="pt-4">
            <div className="h-6 w-36 rounded-xl skeleton" />
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className="group flex flex-col h-full bg-card p-5 rounded-2xl border border-border/50 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.1)] dark:shadow-[0_10px_30px_-5px_rgba(0,0,0,0.7)] transition-all duration-300"
    >
      {/* Image Skeleton */}
      <div className="block overflow-hidden rounded-xl aspect-[3/2] mb-5 shadow-sm">
        <div className="w-full h-full skeleton" />
      </div>

      <div className="flex flex-col flex-grow">
        {/* Category + Date */}
        <div className="flex items-center justify-between text-xs font-bold tracking-wider uppercase mb-3">
          <div className="h-5 w-20 rounded-full skeleton" />
          <div className="h-4 w-20 rounded-full skeleton" />
        </div>

        {/* Title */}
        <div className="space-y-2 mb-2">
          <div className="h-7 md:h-8 w-[95%] rounded-xl skeleton" />
          <div className="h-7 md:h-8 w-[75%] rounded-xl skeleton" />
        </div>

        {/* Summary */}
        <div className="space-y-2 mb-4">
          <div className="h-4 md:h-5 w-full rounded-lg skeleton" />
          <div className="h-4 md:h-5 w-[92%] rounded-lg skeleton" />
          <div className="h-4 md:h-5 w-[80%] rounded-lg skeleton" />
        </div>
      </div>
    </motion.div>
  );
}
