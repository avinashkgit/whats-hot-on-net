import { useEffect } from "react";
import { Switch, Route } from "wouter";
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
import AboutUs from "./pages/AboutUs";
import ContactUs from "./pages/ContactUs";
import EnableNotificationsBanner from "@/components/EnableNotificationsBanner";
import { useWouterAnalytics } from "./hooks/useWouterAnalytics";

function Router() {
  return (
    <Switch>
      <Route path="/">{() => <Home />}</Route>

      <Route path="/category/:slug">
        {(params) => <Home category={params.slug} />}
      </Route>

      <Route path="/article/:slug" component={ArticleDetail} />
      <Route path="/privacy" component={PrivacyPolicy} />
      <Route path="/about" component={AboutUs} />
      <Route path="/contact" component={ContactUs} />
      <Route component={NotFound} />
    </Switch>
  );
}

function AppContent() {
  useWouterAnalytics();
  return (
    <>
      <Toaster />
      <ScrollToTop />
      <EnableNotificationsBanner />
      <Router />
    </>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="light">
        <TooltipProvider>
          <AppContent />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
