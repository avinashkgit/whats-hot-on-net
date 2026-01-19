import { useEffect, useState } from "react";
import { apiClient } from "@/api/apiClient";
import { getFcmToken } from "@/lib/fcm";
import { useToast } from "@/hooks/use-toast";
import { registerFirebaseSW } from "@/lib/registerServiceWorker";

function getDeviceId() {
  let id = localStorage.getItem("device_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("device_id", id);
  }
  return id;
}

export default function EnableNotificationsBanner() {
  const { toast } = useToast();

  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      // only show banner if user hasn't decided yet
      const token = localStorage.getItem("notification_token");

      // Show banner if token missing (even if permission is granted)
      if (!token && Notification.permission !== "denied") {
        setShow(true);
      }
    }, 5000); // 5 seconds

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    registerFirebaseSW();
  }, []);

  const handleEnable = async () => {
    try {
      setLoading(true);

      const token = await getFcmToken();

      await apiClient.saveNotificationToken({
        token,
        platform: "web",
        device_id: getDeviceId(),
        browser: navigator.userAgent,
      });

      toast({
        title: "Notifications enabled ✅",
        description: "You’ll now get alerts for new posts.",
      });

      setShow(false);
    } catch (err: any) {
      toast({
        title: "Could not enable notifications",
        description: err?.message || "Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDismiss = () => {
    setShow(false);
  };

  if (!show) return null;

  return (
    <div className="fixed bottom-4 left-1/2 z-50 w-[92%] max-w-xl -translate-x-1/2">
      <div className="flex items-center justify-between gap-3 rounded-2xl border bg-background p-4 shadow-lg">
        <div className="min-w-0">
          <p className="text-sm font-semibold">Enable Notifications 🔔</p>
          <p className="text-xs text-muted-foreground">
            Get alerts when a new article is posted.
          </p>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <button
            onClick={handleDismiss}
            className="rounded-xl px-3 py-2 text-xs text-muted-foreground hover:bg-muted"
            disabled={loading}
          >
            Not now
          </button>

          <button
            onClick={handleEnable}
            disabled={loading}
            className="rounded-xl bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground hover:opacity-90 disabled:opacity-60"
          >
            {loading ? "Enabling..." : "Enable"}
          </button>
        </div>
      </div>
    </div>
  );
}
