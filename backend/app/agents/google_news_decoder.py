from googlenewsdecoder import gnewsdecoder


def decode_google_news_url(url: str) -> str | None:
    """
    Decodes Google News RSS article URLs (CBMi... format)
    into the original publisher URL.
    """
    try:
        decoded = gnewsdecoder(url)

        if decoded.get("status"):
            return decoded.get("decoded_url")

    except Exception as e:
        print("[Decoder error]", e)

    return None
