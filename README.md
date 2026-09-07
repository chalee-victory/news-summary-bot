# 뉴스 한 줄 요약봇 (News Summary Bot)

뉴스 기사 URL을 붙여넣으면 AI가 본문을 자동으로 가져와 핵심 내용을 3줄로 요약하고, 핵심 키워드 3개를 뽑아주는 웹 서비스입니다.

**배포 URL**: https://news-summary-bot-gamma.vercel.app

---

## 소개

- 관심 있는 뉴스가 있어도 기사 전문을 읽을 시간이 부족한 사용자를 위한 서비스입니다.
- 기존 요약 도구는 "본문 복사 → 붙여넣기"라는 번거로운 단계를 거쳐야 했지만, 이 서비스는 **URL만 붙여넣으면** 백엔드가 알아서 본문을 크롤링하고 요약까지 완료합니다.
- 타겟 사용자: 매일 여러 뉴스를 소비해야 하는 대학생, 직장인 (아침 뉴스 브리핑, 업무용 이슈 트래킹 등)

## 페이지 구성

| 페이지 | 설명 |
|---|---|
| `index.html` | 홈 — 서비스 소개 및 요약하기로 이동하는 CTA |
| `summarize.html` | 요약하기 — 핵심 기능. URL 입력 → 크롤링 → AI 요약 결과 출력 |
| `guide.html` | 사용법 안내 |
| `about.html` | 서비스 소개 및 제작 배경 |

## 기술 스택

| 구분 | 기술 |
|---|---|
| 프론트엔드 | HTML5, CSS3, Vanilla JavaScript (프레임워크 미사용) |
| 백엔드 | Vercel Serverless Functions (Python) |
| 크롤링 | `requests` (HTML 요청) + `trafilatura` (본문 추출) |
| AI API | Anthropic Claude API (`claude-haiku-4-5`) |
| 배포 | Vercel + GitHub 연동 |

## 프로젝트 구조

```
news-summary-bot/
├── index.html
├── summarize.html
├── guide.html
├── about.html
├── css/
│   └── style.css
├── js/
│   └── main.js           # 프론트-백엔드 연결 (fetch, 결과 렌더링, 에러 처리)
├── api/
│   └── summarize.py      # 크롤링 + AI 요약 백엔드 함수
├── requirements.txt
└── README.md
```

## AI 기능 상세

**입력**: 뉴스 기사 URL (`https://` 또는 `http://`로 시작)

**처리 과정**:
1. 프론트엔드에서 `fetch('/api/summarize', { method: 'POST', body: { url } })`로 백엔드 호출
2. 백엔드가 `requests`로 해당 URL의 HTML을 가져옴
3. `trafilatura`로 광고/메뉴/댓글을 제외한 기사 본문만 추출
4. 추출된 본문을 Claude API에 전달하여 3줄 요약 + 키워드 3개 생성

**출력**: 3줄 요약(불릿 리스트), 핵심 키워드 3개(태그), 원문 보기 링크

**실패 처리**:

| 상황 | 사용자 안내 메시지 |
|---|---|
| 빈 입력 | "뉴스 기사 URL을 입력해주세요." |
| URL 형식 오류 | "올바른 URL 형식이 아니에요. (예: https://로 시작)" |
| 크롤링 실패 (403/404 등) | "해당 페이지에서 기사를 가져올 수 없어요." |
| 본문 추출 실패 | "기사 본문을 인식하지 못했어요." |
| AI API 오류 | "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요." |
| 응답 지연/타임아웃 (20초 초과) | "요약 생성이 너무 오래 걸려요. 잠시 후 다시 시도해주세요." |

## 로컬 실행 방법

> ⚠️ 로컬 정적 서버(Live Server 등)로 프론트엔드만 열면, `api/summarize.py`(Vercel Serverless Function)는 실행되지 않습니다. 백엔드 API까지 포함한 전체 기능은 Vercel에 배포된 환경에서만 정상 동작합니다.

**백엔드 크롤링/요약 로직만 로컬에서 단독 테스트하려면:**

```bash
# 1. 저장소 클론
git clone https://github.com/chalee-victory/news-summary-bot.git
cd news-summary-bot

# 2. 필요한 패키지 설치
pip install -r requirements.txt

# 3. 환경 변수 설정 (아래 "환경 변수 설정" 참고)

# 4. api 폴더의 테스트 스크립트 실행
cd api
python summarize_test.py
```

**프론트엔드 화면만 로컬에서 확인하려면:**

VS Code의 Live Server 확장 프로그램으로 `index.html` 또는 `summarize.html`을 열면 됩니다. (단, AI 요약 기능은 위 이유로 로컬에서는 동작하지 않습니다.)

## 배포 방법 (Vercel)

1. GitHub 저장소를 Vercel과 연동
2. Vercel 프로젝트 설정에서 **Framework Preset을 "Other"**로 지정
   - (Python 파일이 있으면 Vercel이 자동으로 "Python"으로 잡는데, 이 경우 정적 프론트엔드 파일들이 정상적으로 서빙되지 않는 문제가 있어 "Other"로 변경함)
3. 환경 변수에 `ANTHROPIC_API_KEY` 등록 (아래 참고)
4. `main` 브랜치에 push하면 자동으로 빌드 및 배포됨

## 환경 변수 설정

이 프로젝트는 Anthropic Claude API 키를 사용합니다. **API 키는 절대 코드에 직접 작성하거나 GitHub에 커밋하지 않습니다.**

| 변수명 | 설명 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic Console에서 발급받은 API 키 |

**로컬 개발 시**: 프로젝트 루트에 `.env` 파일을 만들고 아래처럼 작성합니다. (`.env`는 `.gitignore`에 등록되어 있어 GitHub에는 올라가지 않습니다.)

```
ANTHROPIC_API_KEY=your_api_key_here
```

**Vercel 배포 시**: Vercel 대시보드 → 프로젝트 → Settings → Environment Variables 메뉴에서 동일한 키/값을 등록합니다.

## 알려진 제약사항

- 일부 언론사 사이트는 크롤링을 차단할 수 있어 본문 추출에 실패할 수 있습니다.
- 자바스크립트 렌더링 기반 사이트는 서버 사이드 요청만으로 본문을 가져오지 못할 수 있습니다.
- 본문 전체가 아닌, AI가 생성한 요약문만 사용자에게 노출하여 저작권 이슈를 최소화했습니다.
