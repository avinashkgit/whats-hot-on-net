/* global firebase */
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSyAHzR7ycYphxI8S5-CgHF1E2--X9YxjIcU",
  authDomain: "hotonnet-4a1d1.firebaseapp.com",
  projectId: "hotonnet-4a1d1",
  storageBucket: "hotonnet-4a1d1.firebasestorage.app",
  messagingSenderId: "430818351771",
  appId: "1:430818351771:web:1d5f81b12ae226a7de043e",
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log("FCM BG payload:", payload);

  // ✅ If message already contains notification payload,
  // browser will auto show it → skip manual showNotification()
  if (payload?.notification) {
    return;
  }

  const title = payload?.data?.title || "HotOnNet";
  const body = payload?.data?.body || "New update available";
  const url = payload?.data?.url || "https://hotonnet.com";
  const image = payload?.data?.image || "";

  self.registration.showNotification(title, {
    body,
    icon: "/icons/web-app-manifest-192x192.png",
    image: image || undefined,
    data: { url },
  });
});

// Open site on notification click
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  const url = event.notification?.data?.url || "https://hotonnet.com";

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url === url && "focus" in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow(url);
    })
  );
});
