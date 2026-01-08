import React, { useState, useRef, useEffect } from "react";
import "./App.css";

/* =========================
   Types
========================= */
type ApiArticle = {
  id: number;
  title: string;
  topic: string;
  body: string;
  image_url: string;
  published_at: string;
  created_at: string;
};

type UiArticle = {
  id: number;
  header: string;
  body: string;
  image: string;
  published: string;
};

/* =========================
   Utils
========================= */
function formatDate(dateStr: string) {
  const date = new Date(dateStr);
  return date.toLocaleString("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

const STACK_GAP = 16;

function App() {
  /* =========================
     State
  ========================= */
  const [articles, setArticles] = useState<UiArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [collapsingId, setCollapsingId] = useState<number | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [topIndex, setTopIndex] = useState(0);
  const [animating, setAnimating] = useState<"up" | "down" | false>(false);
  const [incoming, setIncoming] = useState<number | null>(null);
  const animationTimeout = useRef<number | null>(null);

  /* =========================
     Fetch articles
  ========================= */
  useEffect(() => {
    async function fetchArticles() {
      try {
        const res = await fetch(
          "https://whats-hot-on-net.onrender.com/articles"
        );
        const data: ApiArticle[] = await res.json();

        const mapped: UiArticle[] = data.map((a) => ({
          id: a.id,
          header: a.title || a.topic || "Untitled",
          body: a.body || "",
          image: a.image_url || "https://via.placeholder.com/600x400",
          published: a.published_at,
        }));

        setArticles(mapped);
      } catch (err) {
        console.error("Failed to load articles", err);
      } finally {
        setLoading(false);
      }
    }

    fetchArticles();
  }, []);

  /* =========================
     Wheel handler (UNCHANGED)
  ========================= */
  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    if (expandedId !== null || collapsingId !== null) {
      e.preventDefault();
      e.stopPropagation();
      return;
    }

    if (animating || loading) return;

    if (e.deltaY > 0 && topIndex < articles.length - 1) {
      setAnimating("up");
      animationTimeout.current = window.setTimeout(() => {
        setTopIndex((idx) => Math.min(idx + 1, articles.length - 1));
        setAnimating(false);
      }, 350);
    } else if (e.deltaY < 0 && topIndex > 0) {
      setAnimating("down");
      setIncoming(topIndex - 1);
      animationTimeout.current = window.setTimeout(() => {
        setTopIndex((idx) => Math.max(idx - 1, 0));
        setAnimating(false);
        setIncoming(null);
      }, 350);
    }
  };

  /* =========================
     Body scroll lock
  ========================= */
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "hidden";
    };
  }, [expandedId, collapsingId]);

  /* =========================
     Render
  ========================= */
  return (
    <div className="article-stack-container">
      <div className="article-stack" onWheel={handleWheel}>
        {/* Expanded / Collapsing */}
        {(expandedId !== null || collapsingId !== null) && !loading && (
          <div
            className={`article-card expanded${
              collapsingId ? " collapsing" : ""
            }`}
            style={{ zIndex: 101 }}
            onWheel={(e) => e.stopPropagation()}
            onClick={() => {
              setCollapsingId(expandedId);
              setExpandedId(null);
              setTimeout(() => setCollapsingId(null), 600);
            }}
          >
            {(() => {
              const article = articles.find(
                (a) => a.id === (expandedId ?? collapsingId)
              );
              if (!article) return null;

              return (
                <>
                  <img
                    src={article.image}
                    alt={article.header}
                    className="article-image"
                  />
                  <div className="article-content">
                    <h2>{article.header}</h2>
                    <p>{article.body}</p>
                    <span className="article-date">
                      {formatDate(article.published)}
                    </span>
                  </div>
                </>
              );
            })()}
          </div>
        )}

        {/* Loading placeholders */}
        {loading &&
          Array.from({ length: 5 }).map((_, i) => {
            const offset = i * STACK_GAP;
            return (
              <div
                key={`placeholder-${i}`}
                className="article-card placeholder"
                style={{
                  zIndex: 50 - i,
                  top: offset,
                  left: `calc(50% + ${offset}px)`,
                  transform: "translate(-50%, 0)",
                }}
              >
                <div className="image-skeleton" />
                <div className="content-skeleton">
                  <div className="line short" />
                  <div className="line" />
                  <div className="line" />
                </div>
              </div>
            );
          })}

        {/* Incoming (scroll down) */}
        {!loading && incoming !== null && animating === "down" && (
          <div
            className="article-card incoming"
            style={{ zIndex: 200 }}
            onClick={() => setExpandedId(articles[incoming].id)}
          >
            <img
              src={articles[incoming].image}
              alt={articles[incoming].header}
              className="article-image"
            />
            <div className="article-content">
              <h2>{articles[incoming].header}</h2>
              <p>{articles[incoming].body}</p>
              <span className="article-date">
                {formatDate(articles[incoming].published)}
              </span>
            </div>
          </div>
        )}

        {/* Normal stack */}
        {!loading &&
          articles.slice(topIndex, topIndex + 5).map((article, i) => {
            const idx = topIndex + i;
            const offset = i * STACK_GAP;
            const isExpanded = expandedId === article.id;

            const style: React.CSSProperties = {
              zIndex: isExpanded ? 100 : articles.length - idx,
              top: offset,
              left: `calc(50% + ${offset}px)`,
              transform: "translate(-50%, 0)",
              transition: "all 0.35s cubic-bezier(.4,2,.3,1)",
            };

            if (i === 0 && animating === "up" && expandedId === null) {
              style.opacity = 0;
              style.transform = "translate(-50%, -40px) scale(0.96)";
            }

            return (
              <div
                key={article.id}
                className={`article-card${isExpanded ? " expanded" : ""}`}
                style={style}
                onClick={() => setExpandedId(isExpanded ? null : article.id)}
              >
                <img
                  src={article.image}
                  alt={article.header}
                  className="article-image"
                />
                <div className="article-content">
                  <h2>{article.header}</h2>
                  <p>{article.body}</p>
                  <span className="article-date">
                    {formatDate(article.published)}
                  </span>
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
}

export default App;
