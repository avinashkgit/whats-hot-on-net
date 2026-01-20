import { Link } from "wouter";
import { format } from "date-fns";
import { motion } from "framer-motion";
import { ArticleWithCategory } from "@/models/schema";

interface ArticleCardProps {
  article: ArticleWithCategory;
  featured?: boolean;
}

export function ArticleCard({ article, featured = false }: ArticleCardProps) {
  if (featured) {
    return (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        whileHover={{ y: -4 }}
        className="group relative grid grid-cols-1 md:grid-cols-2 gap-8 items-center p-6 rounded-3xl transition-all duration-300 bg-card shadow-[0_4px_20px_-4px_rgba(0,0,0,0.1)] dark:shadow-[0_10px_30px_-5px_rgba(0,0,0,0.7)] border border-border/50 hover:shadow-[0_20px_40px_-12px_rgba(239,68,68,0.2)] dark:hover:shadow-[0_20px_50px_-12px_rgba(239,68,68,0.3)] hover:border-primary/30"
      >
        <Link href={`/article/${article.slug}`} className="block overflow-hidden rounded-2xl aspect-[4/3] md:aspect-[16/10] shadow-md">
          <div className="w-full h-full bg-muted relative overflow-hidden">
            <img 
              src={article.imageUrl} 
              alt={article.title}
              className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-700 ease-in-out"
            />
            <div className="absolute inset-0 bg-black/10 group-hover:bg-black/0 transition-colors duration-300" />
          </div>
        </Link>
        
        <div className="space-y-4 md:pr-8">
          <div className="flex items-center space-x-2 text-sm font-bold tracking-wider uppercase text-primary">
            <span className="bg-primary/10 px-3 py-1 rounded-full">{article.category.name}</span>
            <span className="text-muted-foreground">•</span>
            <span className="text-muted-foreground font-normal normal-case">
              {article.createdAt && format(new Date(article.createdAt), "MMMM d, yyyy")}
            </span>
          </div>
          
          <Link href={`/article/${article.slug}`} className="block">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold leading-tight group-hover:text-primary transition-colors duration-300">
              {article.title}
            </h2>
          </Link>
          
          <p className="text-lg text-muted-foreground leading-relaxed line-clamp-3">
            {article.summary}
          </p>
          
          <div className="pt-4">
             <Link href={`/article/${article.slug}`}>
              <span className="inline-flex items-center text-foreground font-bold border-b-2 border-primary/20 hover:border-primary transition-all duration-300 pb-1 group-hover:gap-3">
                Read Full Story
              </span>
             </Link>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      whileHover={{ y: -8 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="group flex flex-col h-full bg-card p-5 rounded-2xl border border-border/50 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.1)] dark:shadow-[0_10px_30px_-5px_rgba(0,0,0,0.7)] transition-all duration-300 hover:shadow-[0_20px_40px_-15px_rgba(239,68,68,0.2)] dark:hover:shadow-[0_20px_50px_-15px_rgba(239,68,68,0.3)] hover:border-primary/30"
    >
      <Link href={`/article/${article.slug}`} className="block overflow-hidden rounded-xl aspect-[3/2] mb-5 shadow-sm">
        <div className="w-full h-full bg-muted relative overflow-hidden">
          <img 
            src={article.imageUrl} 
            alt={article.title}
            className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-500 ease-in-out"
          />
        </div>
      </Link>
      
      <div className="flex flex-col flex-grow">
        <div className="flex items-center justify-between text-xs font-bold tracking-wider uppercase mb-3">
          <span className="text-primary bg-primary/10 px-2 py-0.5 rounded-full">{article.category.name}</span>
          <span className="text-muted-foreground font-normal normal-case">
            {article.createdAt && format(new Date(article.createdAt), "MMM d, yyyy")}
          </span>
        </div>
        
        <Link href={`/article/${article.slug}`} className="block mb-2">
          <h3 className="text-xl md:text-2xl font-display font-bold leading-tight group-hover:text-primary transition-colors duration-300">
            {article.title}
          </h3>
        </Link>
        
        <p className="text-muted-foreground line-clamp-3 mb-4 text-sm md:text-base leading-relaxed">
          {article.summary}
        </p>
      </div>
    </motion.div>
  );
}
