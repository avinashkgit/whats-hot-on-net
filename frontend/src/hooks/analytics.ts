import { logEvent } from "firebase/analytics";
import { analyticsPromise } from "@/lib/firebase";

export async function trackEvent(
  name: string,
  params: Record<string, any> = {},
) {
  const analytics = await analyticsPromise;
  if (!analytics) return;

  logEvent(analytics, name, params);
}
