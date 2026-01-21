import { getToken } from "firebase/messaging";
import { messagingPromise } from "./firebase";

const VAPID_KEY =
  "BJm8t0K2LKC3k6QMQ-AQ8aZO6qcYGIb721l_ggbtW2KcdoxWSaneMrAmdsdvNOkfMCwQVhZ7Uro_qGjXmgJS5o8";

export async function getFcmToken(): Promise<string> {
  const permission = await Notification.requestPermission();

  if (permission !== "granted") {
    throw new Error("Notification permission denied");
  }

  const messaging = await messagingPromise;

  if (!messaging) {
    throw new Error("FCM is not supported in this browser.");
  }

  const token = await getToken(messaging, {
    vapidKey: VAPID_KEY,
  });

  if (!token) throw new Error("FCM token not generated");

  localStorage.setItem("notification_token", token);
  return token;
}
