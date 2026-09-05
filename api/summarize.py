import json
import os
import re
from http.server import BaseHTTPRequestHandler

import anthropic
import requests
import trafilatura
from dotenv import load_dotenv

load_dotenv()

CODE_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)

SUMMARY_PROMPT = """다음은 뉴스 기사 본문입니다. 언론사의 홍보 문구, 저작권 표시, 구독 유도 문구, '▶'로 시작하는 관련 기사 링크 등은 무시하고, 기사의 핵심 내용만 한국어로 3줄 이내 요약하고 핵심 키워드 3개를 뽑아줘. 결과는 반드시 JSON 형식으로만 응답해: {{"summary": ["...", "...", "..."], "keywords": ["...", "...", "..."]}}

기사 본문:
{article_text}
"""


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


def fetch_html(url):
    """Fetch a URL's HTML, raising requests.RequestException on failure."""
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
    )
    response.raise_for_status()
    return response.text


def extract_body(html):
    """Extract and clean the article body from raw HTML, or None if not found."""
    article_text = trafilatura.extract(html)
    return clean_article_text(article_text) if article_text else None


def summarize_article(article_text):
    """Send article text to Claude and return the parsed summary/keywords dict."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": SUMMARY_PROMPT.format(article_text=article_text),
            }
        ],
    )

    response_text = CODE_FENCE_PATTERN.sub("", message.content[0].text).strip()
    return json.loads(response_text)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            content_length = 0
        raw_body = self.rfile.read(content_length) if content_length else b""

        try:
            payload = json.loads(raw_body or b"{}")
        except json.JSONDecodeError:
            payload = {}

        url = payload.get("url") if isinstance(payload, dict) else None
        url = url.strip() if isinstance(url, str) else ""

        if not url:
            self._respond(400, {"error": "뉴스 기사 URL을 입력해주세요."})
            return

        if not url.startswith("http"):
            self._respond(400, {"error": "올바른 URL 형식이 아니에요."})
            return

        try:
            html = fetch_html(url)
        except requests.RequestException:
            self._respond(400, {"error": "해당 페이지에서 기사를 가져올 수 없어요."})
            return

        article_text = extract_body(html)
        if not article_text:
            self._respond(400, {"error": "기사 본문을 인식하지 못했어요."})
            return

        try:
            result = summarize_article(article_text)
        except Exception:
            self._respond(500, {"error": "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."})
            return

        self._respond(200, result)

    def _respond(self, status_code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
