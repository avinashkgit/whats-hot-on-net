import React, { useState, useRef } from "react";
import "./App.css";

const articles = [
  {
    id: 1,
    image:
      "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=900&q=80",
    header: "AI Revolution in 2026",
    body: `
Artificial Intelligence has entered a decisive phase in 2026. Large language models,
autonomous agents, and real-time reasoning systems are no longer experimental — they are
embedded into everyday workflows across healthcare, finance, education, and governance.

From AI copilots writing production-grade code to medical diagnostic systems outperforming
human benchmarks, the acceleration is staggering. Experts predict that enterprises failing
to adopt AI-first strategies may struggle to remain competitive.

At the same time, global debates around AI regulation, ethical deployment, and job displacement
have intensified. Governments are racing to balance innovation with accountability, while
citizens grapple with what it means to coexist with increasingly intelligent machines.

Elon Musk reiterated that the goal is not merely a visit, but the foundation of a
self-sustaining Martian colony. The latest Starship prototypes demonstrate enhanced
heat shielding and autonomous landing systems tailored for Mars’ thin atmosphere.

Scientists remain cautiously optimistic, citing radiation exposure and long-term
psychological challenges as key concerns. Still, the mission marks humanity’s boldest
step yet toward becoming a multi-planetary species.
    `,
    published: "2026-01-06T09:30:00",
  },
  {
    id: 2,
    image:
      "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=900&q=80",
    header: "SpaceX Mars Mission Update",
    body: `
SpaceX’s long-anticipated Mars mission has crossed several critical milestones.
With successful deep-space fuel transfer tests and upgraded life-support modules,
the company is edging closer to interplanetary human travel.

Elon Musk reiterated that the goal is not merely a visit, but the foundation of a
self-sustaining Martian colony. The latest Starship prototypes demonstrate enhanced
heat shielding and autonomous landing systems tailored for Mars’ thin atmosphere.

Scientists remain cautiously optimistic, citing radiation exposure and long-term
psychological challenges as key concerns. Still, the mission marks humanity’s boldest
step yet toward becoming a multi-planetary species.
    `,
    published: "2026-01-05T16:45:00",
  },
  {
    id: 3,
    image:
      "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=900&q=80",
    header: "Quantum Computing Breakthrough",
    body: `
A major breakthrough in quantum error correction has brought practical quantum
computing closer than ever. Researchers announced a stable 1,000-qubit system capable
of maintaining coherence far longer than previous generations.

This advancement unlocks new possibilities in cryptography, climate modeling, and
drug discovery. Problems that would take classical supercomputers thousands of years
may now be solved in minutes.

Industry leaders are already preparing for a “post-quantum” era, where existing
encryption standards could become obsolete. Governments and corporations alike are
rushing to upgrade security infrastructure before quantum advantage becomes widespread.
    `,
    published: "2026-01-04T12:10:00",
  },
  {
    id: 4,
    image:
      "https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d?auto=format&fit=crop&w=900&q=80",
    header: "Global Economy Enters AI-Driven Phase",
    body: `
The global economy is undergoing a structural shift as AI-driven automation reshapes
labor markets. Routine cognitive tasks are increasingly handled by intelligent systems,
allowing humans to focus on creativity, strategy, and complex decision-making.

While productivity has surged in developed economies, emerging markets face challenges
adapting to rapid automation. Economists stress the importance of reskilling initiatives
and universal access to AI education.

Despite short-term disruptions, long-term projections remain optimistic, suggesting
AI could add trillions of dollars to global GDP over the next decade.
    `,
    published: "2026-01-03T10:00:00",
  },
  {
    id: 5,
    image:
      "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80",
    header: "Climate Tech Innovations Accelerate",
    body: `
Climate technology saw unprecedented investment in 2025, and the momentum continues
into 2026. Breakthroughs in carbon capture, green hydrogen, and energy storage are
reshaping the clean energy landscape.

AI-powered climate models now provide hyper-local predictions, enabling governments
to respond faster to extreme weather events. Meanwhile, startups are deploying
low-cost solar and battery solutions in remote regions.

Analysts believe that climate tech may soon rival fintech in terms of venture capital
interest, marking a turning point in the global fight against climate change.
    `,
    published: "2026-01-02T08:20:00",
  },
  {
    id: 6,
    image:
      "https://images.unsplash.com/photo-1485217988980-11786ced9454?auto=format&fit=crop&w=900&q=80",
    header: "The Rise of Autonomous AI Agents",
    body: `
Autonomous AI agents capable of planning, executing, and refining tasks without
human intervention are becoming mainstream. These agents manage supply chains,
optimize financial portfolios, and even conduct scientific research.

While productivity gains are undeniable, concerns about transparency and control
remain. Researchers emphasize the need for robust alignment mechanisms to ensure
agents act in accordance with human values.

The era of “set it and forget it” software may be ending, replaced by systems that
continuously evolve and negotiate outcomes in real time.
    `,
    published: "2026-01-01T06:00:00",
  },
  {
    id: 7,
    image:
      "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80",
    header: "Global AI Regulations Take Shape",
    body: `
After years of debate, 2026 is emerging as a defining year for global AI regulation.
Multiple regions have introduced comprehensive frameworks governing transparency,
data usage, and accountability for artificial intelligence systems.

The European Union’s updated AI Act now classifies systems by risk level, while
countries in Asia and North America are pursuing their own regulatory paths.
Tech companies are adjusting rapidly, embedding compliance checks directly
into AI development pipelines.

Critics argue that over-regulation could slow innovation, but supporters insist
that trust and safety are essential if AI is to scale responsibly across society.
  `,
    published: "2025-12-31T22:30:00",
  },
  {
    id: 8,
    image:
      "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=900&q=80",
    header: "The Remote Work Experiment Evolves",
    body: `
Remote work has entered its third major phase. What began as a necessity during
the pandemic has matured into a hybrid-first global norm. Companies are now
optimizing for outcomes rather than hours logged.

AI-driven productivity analytics, virtual offices, and immersive collaboration
tools are redefining what it means to “go to work.” Meanwhile, cities are
rethinking infrastructure as migration patterns shift away from traditional hubs.

Experts suggest that organizations embracing flexibility will attract top talent,
while rigid models may struggle to retain skilled professionals.
  `,
    published: "2025-12-31T18:00:00",
  },
  {
    id: 9,
    image:
      "https://images.unsplash.com/photo-1535223289827-42f1e9919769?auto=format&fit=crop&w=900&q=80",
    header: "Healthcare Enters the Predictive Era",
    body: `
Predictive healthcare powered by AI is transforming how diseases are detected
and treated. Advanced models now analyze genetic data, lifestyle patterns,
and medical history to forecast health risks years in advance.

Hospitals are adopting AI triage systems to prioritize care more effectively,
reducing strain on emergency services. Personalized treatment plans are becoming
the norm rather than the exception.

While privacy concerns remain central, proponents argue that predictive medicine
could significantly extend life expectancy and improve quality of care worldwide.
  `,
    published: "2025-12-31T12:15:00",
  },
  {
    id: 10,
    image:
      "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=900&q=80",
    header: "Education Transformed by AI Tutors",
    body: `
Education systems across the globe are embracing AI tutors that adapt in real time
to individual learning styles. Students now receive personalized explanations,
practice exercises, and feedback tailored to their pace and preferences.

Teachers are shifting roles — from content delivery to mentorship and critical
thinking facilitation. Early studies show improved engagement and reduced dropout
rates in AI-assisted classrooms.

However, education experts stress that human guidance remains essential to foster
creativity, ethics, and emotional intelligence in learners.
  `,
    published: "2025-12-30T20:40:00",
  },
  {
    id: 11,
    image:
      "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=900&q=80",
    header: "New Discoveries Redefine the Universe",
    body: `
Astronomers have identified anomalies in deep-space observations that challenge
existing cosmological models. Data from next-generation telescopes suggests that
dark matter may behave differently than previously assumed.

These findings could lead to a fundamental rethinking of how galaxies form and
evolve. Scientists caution that further validation is needed, but excitement is
growing across the astrophysics community.

As exploration tools become more advanced, humanity continues its timeless quest
to understand the true nature of the universe.
  `,
    published: "2025-12-30T09:10:00",
  },
  {
    id: 12,
    image:
      "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=900&q=80",
    header: "Digital Identity Becomes the New Passport",
    body: `
Digital identity systems are rapidly replacing traditional verification methods.
From airport security to online banking, decentralized identity solutions are
promising faster, safer, and more private authentication.

Governments are piloting blockchain-backed identity platforms that give citizens
greater control over personal data. At the same time, concerns about surveillance
and exclusion persist.

The success of digital identity may ultimately depend on transparency, open
standards, and public trust.
  `,
    published: "2025-12-29T17:55:00",
  },
];

function formatDate(dateStr: string) {
  const date = new Date(dateStr);
  return date.toLocaleString("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

const STACK_GAP = 16;

function App() {
  const [collapsingId, setCollapsingId] = useState<number | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [topIndex, setTopIndex] = useState(0); // which article is at the top
  const [animating, setAnimating] = useState<"up" | "down" | false>(false);
  const [incoming, setIncoming] = useState<number | null>(null); // index of card animating in
  const animationTimeout = useRef<number | null>(null);

  // Handle wheel scroll for stack effect
  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    if (expandedId !== null || collapsingId !== null) {
      e.preventDefault();
      e.stopPropagation();
      return;
    }

    if (animating) return;
    if (e.deltaY > 0 && topIndex < articles.length - 1) {
      // Scroll up: remove top card
      setAnimating("up");
      animationTimeout.current = window.setTimeout(() => {
        setTopIndex((idx) => Math.min(idx + 1, articles.length - 1));
        setAnimating(false);
      }, 350);
    } else if (e.deltaY < 0 && topIndex > 0) {
      // Scroll down: add card back
      setAnimating("down");
      setIncoming(topIndex - 1);
      animationTimeout.current = window.setTimeout(() => {
        setTopIndex((idx) => Math.max(idx - 1, 0));
        setAnimating(false);
        setIncoming(null);
      }, 350);
    }
  };

  React.useEffect(() => {
    if (expandedId !== null || collapsingId !== null) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "hidden"; // keep hidden since wheel is custom
    }

    return () => {
      document.body.style.overflow = "hidden";
    };
  }, [expandedId, collapsingId]);

  return (
    <div className="article-stack-container">
      <div className="article-stack" onWheel={handleWheel}>
        {/* Overlay expanded card above stack during collapse */}
        {(expandedId !== null || collapsingId !== null) && (
          <div
            className={`article-card expanded${
              collapsingId ? " collapsing" : ""
            }`}
            onWheel={(e) => e.stopPropagation()} 
            style={{ zIndex: 101 }}
            onClick={() => {
              setCollapsingId(expandedId);
              setExpandedId(null);
              setTimeout(() => setCollapsingId(null), 600); // match .expanded transition duration
            }}
          >
            <img
              src={
                articles.find((a) => a.id === (expandedId ?? collapsingId))
                  ?.image
              }
              alt={
                articles.find((a) => a.id === (expandedId ?? collapsingId))
                  ?.header
              }
              className="article-image"
            />
            <div className="article-content">
              <h2>
                {
                  articles.find((a) => a.id === (expandedId ?? collapsingId))
                    ?.header
                }
              </h2>
              <p>
                {
                  articles.find((a) => a.id === (expandedId ?? collapsingId))
                    ?.body
                }
              </p>
              <span className="article-date">
                {formatDate(
                  articles.find((a) => a.id === (expandedId ?? collapsingId))
                    ?.published || ""
                )}
              </span>
            </div>
          </div>
        )}
        {/* Always show stack underneath, even during collapse */}
        {/* Render incoming card for down scroll animation */}
        {incoming !== null && animating === "down" && (
          <div
            key={articles[incoming].id}
            className="article-card incoming"
            style={{
              zIndex: 200,
              top: 0,
              left: `calc(50% + 0px)`,
              transform: "translate(-50%, -40px) scale(0.96)",
              opacity: 0,
              transition: "all 0.35s cubic-bezier(.4,2,.3,1)",
            }}
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
        {articles.slice(topIndex, topIndex + 5).map((article, i) => {
          const idx = topIndex + i;
          const isExpanded = expandedId === article.id;
          const offset = i * STACK_GAP;
          const style: React.CSSProperties = {
            zIndex: isExpanded ? 100 : articles.length - idx,
            top: offset,
            left: `calc(50% + ${offset}px)`,
            transform: "translate(-50%, 0)",
            opacity: 1,
            transition: "all 0.35s cubic-bezier(.4,2,.3,1)",
          };
          // Animate fade out for top card
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
