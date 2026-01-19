export async function registerFirebaseSW() {
  if (!("serviceWorker" in navigator)) return;

  try {
    const reg = await navigator.serviceWorker.register(
      "/firebase-messaging-sw.js",
    );
    console.log("✅ Firebase SW registered:", reg);
  } catch (err) {
    console.error("❌ Firebase SW registration failed:", err);
  }
}
