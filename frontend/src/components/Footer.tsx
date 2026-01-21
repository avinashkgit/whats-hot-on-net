import { useCategories } from "@/hooks/use-blog";
import { Link } from "wouter";

export function Footer() {
  const { data: categories } = useCategories();

  return (
    <footer className="bg-secondary text-foreground py-16 mt-20 border-t border-border">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 border-b border-border pb-12">
          <div className="col-span-1">
            <div className="flex items-baseline space-x-1 mb-6">
              <span className="font-display text-2xl font-black italic text-primary">
                Hot
              </span>
              <span className="font-display text-2xl font-bold">OnNet</span>
            </div>
            <p className="text-muted-foreground text-sm leading-relaxed max-w-xs">
              Curating the most essential stories from around the globe.
              News, science, lifestyle, business, and more delivered with style.
            </p>
          </div>

          <div>
            <h4 className="font-bold mb-4">Sections</h4>
            <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm text-muted-foreground">
              <Link href="/" className="hover:text-primary transition-colors">
                Home
              </Link>

              {categories?.map((category) => (
                <Link
                  key={category.slug}
                  href={`/category/${category.slug}`}
                  className="hover:text-primary transition-colors"
                >
                  {category.name}
                </Link>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-bold mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link
                  href="/about"
                  className="hover:text-primary transition-colors"
                >
                  About Us
                </Link>
              </li>

              <li>
                <Link
                  href="/contact"
                  className="hover:text-primary transition-colors"
                >
                  Contact Us
                </Link>
              </li>

              <li>
                <Link
                  href="/privacy"
                  className="hover:text-primary transition-colors"
                >
                  Privacy Policy
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-8 text-center md:text-left text-xs text-muted-foreground">
          © {new Date().getFullYear()} (hotonnet.com) All rights reserved.
        </div>
      </div>
    </footer>
  );
}
