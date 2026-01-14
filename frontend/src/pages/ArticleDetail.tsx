import { useArticle } from "@/hooks/use-blog";
import { Navigation } from "@/components/Navigation";
import { Footer } from "@/components/Footer";
import { Loader2, Calendar, Clock, Share2, Facebook, Twitter, Linkedin, Eye } from "lucide-react";
import { useRoute } from "wouter";
import { format } from "date-fns";
import { motion } from "framer-motion";
import { ReactElement, JSXElementConstructor, ReactNode, Key } from "react";

export default function ArticleDetail() {
  const [match, params] = useRoute("/article/:slug");
  const slug = params?.slug || "";
  const { data: article, isLoading, error } = useArticle(slug);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-background p-4">
        <h2 className="text-3xl font-display font-bold mb-4">Article not found</h2>
        <p className="text-muted-foreground mb-8">The story you are looking for does not exist or has been moved.</p>
        <a href="/" className="px-8 py-3 bg-primary text-primary-foreground rounded-full font-bold shadow-lg hover:shadow-xl hover:bg-primary/90 transition-all">
          Back to Home
        </a>
      </div>
    );
  }

  // Calculate read time roughly
  const readTime = Math.ceil(article.content.length / 1000);

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Navigation />
      
      <main className="flex-grow">
        <article className="pb-20">
          {/* Header Section */}
          <div className="bg-secondary/30 pt-16 pb-20">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl text-center">
              <div className="flex items-center justify-center space-x-2 text-sm font-bold tracking-wider uppercase text-primary mb-6">
                <span>{article.topic.name}</span>
              </div>
              
              <motion.h1 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-4xl md:text-5xl lg:text-6xl font-display font-bold leading-tight mb-8 text-balance"
              >
                {article.title}
              </motion.h1>

              <motion.p 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="text-xl md:text-2xl text-muted-foreground mb-8 font-serif italic max-w-2xl mx-auto leading-relaxed"
              >
                {article.summary}
              </motion.p>
              
              <div className="flex flex-col md:flex-row items-center justify-center gap-6 text-sm text-muted-foreground border-t border-border/50 pt-8 w-max mx-auto px-8">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  <span>{article.createdAt && format(new Date(article.createdAt), "MMMM d, yyyy")}</span>
                </div>
                <div className="hidden md:block w-1 h-1 bg-muted-foreground/30 rounded-full" />
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  <span>{readTime} min read</span>
                </div>
                <div className="hidden md:block w-1 h-1 bg-muted-foreground/30 rounded-full" />
                <div className="flex items-center gap-2">
                  <Eye className="w-4 h-4" />
                  <span>{article.views.toLocaleString()} views</span>
                </div>
              </div>
            </div>
          </div>

          {/* Hero Image */}
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-5xl -mt-12">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="rounded-2xl overflow-hidden shadow-2xl shadow-black/5 aspect-[21/9]"
            >
              <img 
                src={article.imageUrl} 
                alt={article.title}
                className="w-full h-full object-cover"
              />
            </motion.div>
          </div>

          {/* Content Body */}
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-3xl mt-16">
            <div className="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-12">
              <div className="prose prose-lg prose-slate md:prose-xl max-w-none 
                dark:prose-invert
                prose-headings:font-display prose-headings:font-bold prose-h1:text-4xl prose-h2:text-3xl
                prose-p:leading-relaxed prose-p:text-muted-foreground prose-p:mb-6
                prose-a:text-primary prose-a:no-underline hover:prose-a:underline
                prose-blockquote:border-l-4 prose-blockquote:border-primary prose-blockquote:pl-6 prose-blockquote:italic prose-blockquote:font-serif
                prose-img:rounded-xl prose-img:shadow-lg">
                
                {article.content.split('\n\n').map((paragraph: string | number | boolean | ReactElement<any, string | JSXElementConstructor<any>> | Iterable<ReactNode> | null | undefined, idx: Key | null | undefined) => {
                  // First paragraph is a drop cap
                  if (idx === 0) {
                    return (
                      <p key={idx} className="first-letter:float-left first-letter:text-7xl first-letter:pr-4 first-letter:font-black first-letter:font-display first-letter:text-foreground">
                        {paragraph}
                      </p>
                    );
                  }
                  return <p key={idx}>{paragraph}</p>;
                })}
              </div>

              {/* Sidebar / Share (Desktop) */}
              <div className="hidden md:block">
                <div className="sticky top-32 space-y-6">
                  <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-4">Share</div>
                  <button className="p-3 rounded-full bg-secondary hover:bg-primary hover:text-white transition-colors block" title="Share on Twitter">
                    <Twitter className="w-5 h-5" />
                  </button>
                  <button className="p-3 rounded-full bg-secondary hover:bg-[#1877F2] hover:text-white transition-colors block" title="Share on Facebook">
                    <Facebook className="w-5 h-5" />
                  </button>
                  <button className="p-3 rounded-full bg-secondary hover:bg-[#0A66C2] hover:text-white transition-colors block" title="Share on LinkedIn">
                    <Linkedin className="w-5 h-5" />
                  </button>
                  <button className="p-3 rounded-full bg-secondary hover:bg-foreground hover:text-background transition-colors block" title="Copy Link">
                    <Share2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
            
            {/* Tags */}
            <div className="mt-16 pt-8 border-t border-border">
              <div className="flex flex-wrap gap-2">
                <span className="px-4 py-2 bg-secondary rounded-full text-sm font-medium text-foreground">
                  #{article.topic.slug}
                </span>
                <span className="px-4 py-2 bg-secondary rounded-full text-sm font-medium text-foreground">
                  #trending
                </span>
                <span className="px-4 py-2 bg-secondary rounded-full text-sm font-medium text-foreground">
                  #news
                </span>
              </div>
            </div>
          </div>
        </article>
      </main>

      <Footer />
    </div>
  );
}
