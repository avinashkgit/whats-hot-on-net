import { getToken } from "firebase/messaging";
import { messaging } from "./firebase";

export async function getFcmToken(): Promise<string> {
  if (!messaging) {
    throw new Error("FCM not ready / not supported in this browser");
  }

  const permission = await Notification.requestPermission();

  if (permission !== "granted") {
    throw new Error("Notification permission denied");
  }

  const token = await getToken(messaging, {
    vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY,
  });

  if (!token) {
    throw new Error("FCM token not generated");
  }

  localStorage.setItem("notification_token", token);
  return token;
}
