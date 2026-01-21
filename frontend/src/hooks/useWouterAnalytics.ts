import { useEffect } from "react";
import { useLocation } from "wouter";
import { logEvent } from "firebase/analytics";
import { analyticsPromise } from "@/lib/firebase";

export function useWouterAnalytics(): void {
  const [location] = useLocation();

  useEffect(() => {
    (async () => {
      const analytics = await analyticsPromise;
      if (!analytics) return;

      logEvent(analytics, "page_view", {
        page_path: location,
      });
    })();
  }, [location]);
}
