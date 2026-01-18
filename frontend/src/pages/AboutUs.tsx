import { Navigation } from "@/components/Navigation";
import { Footer } from "@/components/Footer";
import { motion } from "framer-motion";

export default function AboutUs() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navigation />

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16 flex-grow">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-3xl mx-auto"
        >
          <h1 className="text-4xl font-display font-bold mb-8">About Us</h1>

          <div className="prose prose-slate dark:prose-invert max-w-none space-y-6">
            <section>
              <h2 className="text-2xl font-display font-bold mb-4">
                Welcome to HotOnNet
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                HotOnNet is a modern digital news platform that shares trending
                stories across technology, science, global updates, culture, and
                more — all in a clean and fast reading experience.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-display font-bold mb-4">
                AI-Generated Content
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                Please note that articles, images, and summaries on HotOnNet are
                generated using artificial intelligence. This platform is built
                as an automated content curation and publishing system.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-display font-bold mb-4">
                Our Mission
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                Our mission is to make trending information accessible and easy
                to explore, while showcasing the power of automation in content
                publishing.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-display font-bold mb-4">
                What You’ll Find Here
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                On HotOnNet, you’ll find bite-sized news summaries, full-length
                articles, and curated updates from around the world — designed
                for quick reading and sharing.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-display font-bold mb-4">
                Contact & Feedback
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                We’re always improving. If you have suggestions or want to
                report an issue, feel free to reach out through our Contact page.
              </p>
            </section>

            <section>
              <p className="text-sm text-muted-foreground italic">
                Last updated: January 18, 2026
              </p>
            </section>
          </div>
        </motion.div>
      </main>

      <Footer />
    </div>
  );
}
