import { initializeApp } from "firebase/app";
import { getAnalytics, isSupported as analyticsSupported, type Analytics } from "firebase/analytics";
import { getMessaging, isSupported as messagingSupported, type Messaging } from "firebase/messaging";

const firebaseConfig = {
  apiKey: "AIzaSyAHzR7ycYphxI8S5-CgHF1E2--X9YxjIcU",
  authDomain: "hotonnet-4a1d1.firebaseapp.com",
  projectId: "hotonnet-4a1d1",
  storageBucket: "hotonnet-4a1d1.firebasestorage.app",
  messagingSenderId: "430818351771",
  appId: "1:430818351771:web:1d5f81b12ae226a7de043e",
  measurementId: "G-ENXCW78M27"
};

export const firebaseApp = initializeApp(firebaseConfig);

// --------------------
// ✅ Analytics
// --------------------
export const analyticsPromise: Promise<Analytics | null> = analyticsSupported().then(
  (supported) => {
    if (!supported) return null;
    return getAnalytics(firebaseApp);
  }
);

// --------------------
// ✅ Messaging (FCM)
// --------------------
export const messagingPromise: Promise<Messaging | null> = messagingSupported().then(
  (supported) => {
    if (!supported) {
      console.warn("FCM is not supported in this browser.");
      return null;
    }
    return getMessaging(firebaseApp);
  }
);
