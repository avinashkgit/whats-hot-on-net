import { getToken } from "firebase/messaging";
import { messagingPromise } from "./firebase";
import { trackEvent } from "@/hooks/analytics";

const VAPID_KEY =
  "BJm8t0K2LKC3k6QMQ-AQ8aZO6qcYGIb721l_ggbtW2KcdoxWSaneMrAmdsdvNOkfMCwQVhZ7Uro_qGjXmgJS5o8";

export async function getFcmToken(): Promise<string> {
  const permission = await Notification.requestPermission();

  if (permission !== "granted") {
    trackEvent("notification_enable_failed", { reason: "permission_denied" });
    throw new Error("Notification permission denied");
  }

  const messaging = await messagingPromise;

  if (!messaging) {
    trackEvent("notification_enable_failed", { reason: "not_supported" });
    throw new Error("FCM is not supported in this browser.");
  }

  const token = await getToken(messaging, {
    vapidKey: VAPID_KEY,
  });

  if (!token) {
    trackEvent("notification_enable_failed", { reason: "token_not_generated" });
    throw new Error("FCM token not generated");
  }

  localStorage.setItem("notification_token", token);
  return token;
}
