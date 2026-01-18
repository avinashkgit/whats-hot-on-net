import os
import json
import firebase_admin
from firebase_admin import credentials, messaging


def init_firebase():
    if firebase_admin._apps:
        return

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        raise RuntimeError("Missing env: FIREBASE_SERVICE_ACCOUNT_JSON")

    cred_dict = json.loads(service_account_json)
    cred = credentials.Certificate(cred_dict)

    firebase_admin.initialize_app(cred)


def send_push_to_tokens(tokens: list[str], title: str, body: str, url: str, image_url: str | None = None):
    if not tokens:
        return {"success": 0, "failure": 0}

    init_firebase()

    notif = messaging.Notification(title=title, body=body, image=image_url)

    message = messaging.MulticastMessage(
        tokens=tokens,
        notification=notif,
        data={"url": url},
    )

    resp = messaging.send_each_for_multicast(message)

    return {
        "success": resp.success_count,
        "failure": resp.failure_count,
    }
