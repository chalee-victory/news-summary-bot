import requests
import trafilatura


def clean_article_text(text):
    """Remove promotional, copyright, and source-credit lines."""
    filtered_lines = []
    removable_markers = (
        "저작권자",
        "재판매 및 DB금지",
        "구독 클릭",
        "제보하기",
    )

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("▶") or any(marker in line for marker in removable_markers):
            continue
        if line.startswith("[") and "제공" in line:
            continue
        filtered_lines.append(line)

    return "\n".join(filtered_lines).strip() or None


def extract_article(url):
    """Fetch a news article URL and return its extracted body text."""
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    try:
        article_text = trafilatura.extract(response.text)
        return clean_article_text(article_text) if article_text else None
    except Exception:
        return None


if __name__ == "__main__":
    example_url = "https://n.news.naver.com/mnews/article/001/0012345678"
    article_text = extract_article(example_url)

    if article_text:
        print(article_text)
    else:
        print("Failed to extract the article body.")