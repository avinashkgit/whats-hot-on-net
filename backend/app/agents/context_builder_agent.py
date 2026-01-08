def build_context(articles, max_chars=12000):
    context = ""

    for a in articles:
        block = f"""
SOURCE: {a['url']}
TITLE: {a['title']}
CONTENT:
{a['text']}
"""
        if len(context) + len(block) > max_chars:
            break

        context += block

    return context.strip()
