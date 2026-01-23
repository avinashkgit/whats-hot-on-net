import os
import json
import firebase_admin
from firebase_admin import credentials, messaging


def init_firebase():
    """Initialize Firebase Admin only once."""
    if firebase_admin._apps:
        return

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        raise RuntimeError("Missing env: FIREBASE_SERVICE_ACCOUNT_JSON")

    cred_dict = json.loads(service_account_json)
    cred = credentials.Certificate(cred_dict)

    firebase_admin.initialize_app(cred)


def send_push_to_tokens(
    tokens: list[str],
    title: str,
    body: str,
    url: str,
    image_url: str | None = None,
):
    """
    Send DATA-only push notification to web tokens.
    Service Worker will show notification (no duplicates).
    """

    if not tokens:
        return {"success": 0, "failure": 0}

    init_firebase()

    message = messaging.MulticastMessage(
        tokens=tokens,
        data={
            "title": title or "HotOnNet",
            "body": body or "New update available",
            "url": url or "https://hotonnet.com",
            "image": image_url or "",
        },
        webpush=messaging.WebpushConfig(
            headers={
                "Urgency": "high",
            },
            # Optional: browser metadata (does NOT create duplicates)
            notification=messaging.WebpushNotification(
                icon="https://hotonnet.com/icons/web-app-manifest-192x192.png",
                badge="https://hotonnet.com/icons/web-app-manifest-192x192.png",
            ),
        ),
    )

    resp = messaging.send_each_for_multicast(message)

    return {
        "success": resp.success_count,
        "failure": resp.failure_count,
    }
