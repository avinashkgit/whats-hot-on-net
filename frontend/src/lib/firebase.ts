import { initializeApp } from "firebase/app";
import { getMessaging, isSupported } from "firebase/messaging";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// ✅ Debug (remove later)
console.log("Firebase Config:", firebaseConfig);

export const firebaseApp = initializeApp(firebaseConfig);

// ✅ messaging should only be created if supported
export let messaging: any = null;

isSupported().then((supported) => {
  if (supported) {
    messaging = getMessaging(firebaseApp);
  } else {
    console.warn("FCM is not supported in this browser.");
  }
});
