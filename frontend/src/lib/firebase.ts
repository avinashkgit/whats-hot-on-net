import { initializeApp } from "firebase/app";
import { getMessaging, isSupported } from "firebase/messaging";

const firebaseConfig = {
  apiKey: "AIzaSyAHzR7ycYphxI8S5-CgHF1E2--X9YxjIcU",
  authDomain: "hotonnet-4a1d1.firebaseapp.com",
  projectId: "hotonnet-4a1d1",
  storageBucket: "hotonnet-4a1d1.firebasestorage.app",
  messagingSenderId: "430818351771",
  appId: "1:430818351771:web:1d5f81b12ae226a7de043e",
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
