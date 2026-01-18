import { Navigation } from "@/components/Navigation";
import { Footer } from "@/components/Footer";
import { motion } from "framer-motion";

export default function ContactUs() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navigation />

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16 flex-grow">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-3xl mx-auto"
        >
          <h1 className="text-4xl font-display font-bold mb-8">Contact Us</h1>

          <div className="prose prose-slate dark:prose-invert max-w-none space-y-6">
            <section>
              <h2 className="text-2xl font-display font-bold mb-4">
                Get in Touch
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                We’d love to hear from you. If you have feedback, suggestions,
                partnership requests, or want to report an issue, you can reach
                out using the details below.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-display font-bold mb-4">
                Email Support
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                📩 Email:{" "}
                <a
                  href="mailto:support@hotonnet.com"
                  className="text-primary font-semibold hover:underline"
                >
                  whatshotonnet@gmail.com"
                </a>
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-display font-bold mb-4">
                Social Media
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                You can also connect with us on X (Twitter):{" "}
                <a
                  href="https://x.com/hotonnet_com"
                  target="_blank"
                  rel="noreferrer"
                  className="text-primary font-semibold hover:underline"
                >
                  @hotonnet_com
                </a>
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-display font-bold mb-4">
                Content Disclaimer
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                HotOnNet is an AI-generated content platform. While we aim to
                share useful and trending updates, information may not always be
                fully accurate. Please verify critical information from official
                sources.
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
