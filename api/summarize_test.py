import json
import os
import re
import sys

from dotenv import load_dotenv
import anthropic

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crawl_test import extract_article

load_dotenv()

CODE_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)

SUMMARY_PROMPT = """다음은 뉴스 기사 본문입니다. 언론사의 홍보 문구, 저작권 표시, 구독 유도 문구, '▶'로 시작하는 관련 기사 링크 등은 무시하고, 기사의 핵심 내용만 한국어로 3줄 이내 요약하고 핵심 키워드 3개를 뽑아줘. 결과는 반드시 JSON 형식으로만 응답해: {{"summary": ["...", "...", "..."], "keywords": ["...", "...", "..."]}}

기사 본문:
{article_text}
"""


def summarize_article(article_text):
    """Send extracted article text to Claude and return the parsed summary JSON."""
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


if __name__ == "__main__":
    example_url = "https://n.news.naver.com/mnews/article/001/0012345678"
    article_text = extract_article(example_url)

    if not article_text:
        print("Failed to extract the article body.")
    else:
        try:
            result = summarize_article(article_text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print("Claude did not return valid JSON.")
