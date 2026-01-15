import { Switch, Route, useRoute } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "next-themes";
import Home from "@/pages/Home";
import ArticleDetail from "@/pages/ArticleDetail";
import PrivacyPolicy from "@/pages/PrivacyPolicy";
import NotFound from "@/pages/not-found";
import { ScrollToTop } from "./ScrollToTop";

function Router() {
  return (
    <Switch>
      <Route path="/">{() => <Home />}</Route>

      <Route path="/category/:slug">
        {(params) => <Home category={params.slug} />}
      </Route>

      <Route path="/article/:slug" component={ArticleDetail} />
      <Route path="/privacy" component={PrivacyPolicy} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="light">
        <TooltipProvider>
          <Toaster />
          <ScrollToTop />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
