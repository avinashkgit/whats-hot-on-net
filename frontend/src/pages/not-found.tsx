import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertCircle, ArrowLeft } from "lucide-react";
import { Link } from "wouter";

export default function NotFound() {
  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background px-4">
      <Card className="w-full max-w-lg shadow-lg border-border">
        <CardContent className="py-10 text-center">
          {/* Icon */}
          <div className="flex justify-center mb-6">
            <div className="flex items-center justify-center w-16 h-16 rounded-full bg-destructive/10">
              <AlertCircle className="h-8 w-8 text-destructive" />
            </div>
          </div>

          {/* Heading */}
          <h1 className="text-3xl font-display font-black tracking-tight mb-3">
            Page not found
          </h1>

          {/* Description */}
          <p className="text-muted-foreground max-w-sm mx-auto mb-8 leading-relaxed">
            The page you’re looking for doesn’t exist, was moved, or is no longer
            available. Let’s get you back to what matters.
          </p>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/">
              <Button className="gap-2 font-bold">
                <ArrowLeft className="w-4 h-4" />
                Back to Home
              </Button>
            </Link>

            <Link href="/">
              <Button variant="outline" className="font-semibold">
                Browse Latest Stories
              </Button>
            </Link>
          </div>

          {/* Footer hint */}
          <p className="mt-8 text-xs text-muted-foreground">
            Error code: 404
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
