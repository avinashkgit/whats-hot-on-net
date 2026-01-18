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
    measurementId: "G-ENXCW78M27"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  self.registration.showNotification(payload.notification?.title || "HotOnNet", {
    body: payload.notification?.body || "New update available",
    icon: "/icons/web-app-manifest-192x192.png",
  });
});
