import React, { useState, useRef, useEffect } from "react";
import "./App.css";
import logo from "./assets/favicon.svg";

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
const SWIPE_THRESHOLD = 50;

export default function App() {
  /* =========================
     State
  ========================= */
  const [articles, setArticles] = useState<UiArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [collapsingId, setCollapsingId] = useState<number | null>(null);
  const [topIndex, setTopIndex] = useState(0);
  const [animating, setAnimating] = useState<"up" | "down" | false>(false);
  const [incoming, setIncoming] = useState<number | null>(null);

  const touchStartY = useRef<number | null>(null);
  const touchEndY = useRef<number | null>(null);

  /* =========================
     Fetch Articles
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
     Wheel (Desktop)
  ========================= */
  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    if (expandedId !== null || collapsingId !== null) {
      e.preventDefault();
      return;
    }
    if (animating || loading) return;

    if (e.deltaY > 0 && topIndex < articles.length - 1) {
      setAnimating("up");
      setTimeout(() => {
        setTopIndex((i) => Math.min(i + 1, articles.length - 1));
        setAnimating(false);
      }, 350);
    }

    if (e.deltaY < 0 && topIndex > 0) {
      setAnimating("down");
      setIncoming(topIndex - 1);
      setTimeout(() => {
        setTopIndex((i) => Math.max(i - 1, 0));
        setIncoming(null);
        setAnimating(false);
      }, 350);
    }
  };

  /* =========================
     Touch (Mobile)
  ========================= */
  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartY.current = e.touches[0].clientY;
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    touchEndY.current = e.touches[0].clientY;
  };

  const handleTouchEnd = () => {
    if (
      touchStartY.current === null ||
      touchEndY.current === null ||
      animating ||
      loading ||
      expandedId !== null ||
      collapsingId !== null
    )
      return;

    const delta = touchStartY.current - touchEndY.current;

    if (delta > SWIPE_THRESHOLD && topIndex < articles.length - 1) {
      setAnimating("up");
      setTimeout(() => {
        setTopIndex((i) => Math.min(i + 1, articles.length - 1));
        setAnimating(false);
      }, 350);
    }

    if (delta < -SWIPE_THRESHOLD && topIndex > 0) {
      setAnimating("down");
      setIncoming(topIndex - 1);
      setTimeout(() => {
        setTopIndex((i) => Math.max(i - 1, 0));
        setIncoming(null);
        setAnimating(false);
      }, 350);
    }

    touchStartY.current = null;
    touchEndY.current = null;
  };

  /* =========================
     Scroll Lock
  ========================= */
  useEffect(() => {
    document.body.style.overflow =
      expandedId !== null || collapsingId !== null ? "hidden" : "auto";

    return () => {
      document.body.style.overflow = "auto";
    };
  }, [expandedId, collapsingId]);

  /* =========================
     Render
  ========================= */
  const isExpanded = expandedId !== null || collapsingId !== null;

  return (
    <div className={`app-root ${isExpanded ? "expanded-mode" : ""}`}>
      {/* HEADER */}
      <header className="app-header">
        <img src={logo} alt="Hot on Net Logo" className="app-logo" />
        <h1>Hot on Net</h1>
      </header>

      {/* MAIN */}
      <main className="app-main">
        <div className="article-stack-container">
          <div
            className="article-stack"
            onWheel={handleWheel}
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
          >
            {/* Expanded */}
            {(expandedId !== null || collapsingId !== null) && !loading && (
              <div
                className={`article-card expanded${
                  collapsingId ? " collapsing" : ""
                }`}
                style={{ zIndex: 101 }}
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

            {/* 🔄 Loading placeholders */}
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

            {/* 🔥 Incoming Card */}
            {!loading && incoming !== null && animating === "down" && (
              <div className="article-card incoming" style={{ zIndex: 200 }}>
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

            {/* Stack */}
            {!loading &&
              articles.slice(topIndex, topIndex + 5).map((article, i) => {
                const idx = topIndex + i;
                const offset = i * STACK_GAP;

                return (
                  <div
                    key={article.id}
                    className="article-card"
                    style={{
                      zIndex: articles.length - idx,
                      top: offset,
                      left: `calc(50% + ${offset}px)`,
                      transform: "translate(-50%, 0)",
                      transition: "all 0.35s cubic-bezier(.4,2,.3,1)",
                    }}
                    onClick={() => setExpandedId(article.id)}
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
      </main>

      {/* FOOTER */}
      <footer className="app-footer">© 2026 hotonnet.com</footer>
    </div>
  );
}
