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
| 환경 변수 관리 | `python-dotenv` (로컬 개발 시 `.env` 파일 로드) |
| 배포 | Vercel + GitHub 연동 |

## 프론트엔드 기술 역할 분리

프레임워크 없이 순수 웹 기술만 사용했기 때문에, 각 기술이 담당하는 역할을 명확히 구분해서 작성했습니다.

| 기술 | 담당 역할 | 이 프로젝트에서의 예 |
|---|---|---|
| **HTML** | 문서의 구조와 의미(semantic) 정의 | `<form>`으로 입력 영역을, `<nav>`로 메뉴를, `aria-label`로 접근성 정보를 명시 |
| **CSS** | 시각적 스타일링과 레이아웃, 반응형 처리 | `:root`의 CSS 변수로 색상 체계 관리, `@media (max-width: 768px)`로 모바일 레이아웃 분기, `[data-theme="dark"]`로 다크모드 색상 전환 |
| **JavaScript** | 사용자 상호작용 처리와 서버 통신 | 폼 제출 이벤트 감지, `fetch`로 백엔드 API 호출, 응답 결과를 DOM에 동적으로 렌더링, 로컬 상태(로딩/에러/완료)를 화면에 반영 |

세 기술은 서로 독립적으로 동작하도록 설계했습니다 — 예를 들어 CSS만 수정해도 JS 로직에 영향이 없고, JS의 `fetch` 로직이 실패해도 HTML 구조 자체는 깨지지 않습니다.

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

**테스트 케이스 재현**:

| 케이스 | 입력 예시 | 실제 응답 |
|---|---|---|
| 정상 입력 | `https://www.hankookilbo.com/news/article/...` (실제 존재하는 뉴스 기사 URL) | `{"summary": [...3줄...], "keywords": [...3개...]}` 형태의 JSON, 화면에 3줄 요약 + 키워드 태그로 렌더링됨 |
| 빈 입력 | (입력창을 비운 채 제출) | 프론트에서 즉시 차단, "뉴스 기사 URL을 입력해주세요." 표시 |
| 잘못된 형식 | `안녕하세요` / `naver.com` (http로 시작하지 않음) | 프론트에서 즉시 차단, "올바른 URL 형식이 아니에요. (예: https://로 시작)" 표시 |
| 존재하지 않는 페이지 | `https://example.com/no-such-article` | 백엔드 400 응답, "해당 페이지에서 기사를 가져올 수 없어요." 표시 |
| 매우 긴 입력(200자 이상 텍스트를 URL 자리에 입력) | 임의의 긴 문자열 | `http`로 시작하지 않으므로 프론트 검증에서 "올바른 URL 형식이 아니에요." 표시 |

> 실제 curl을 이용한 배포 환경 검증 예시:
> ```bash
> curl -X POST https://news-summary-bot-gamma.vercel.app/api/summarize \
>   -H "Content-Type: application/json" \
>   -d '{"url": "https://www.hankookilbo.com/news/article/..."}'
> ```
> 정상 시 `{"summary": [...], "keywords": [...]}` JSON이 반환됨을 확인함. 응답 예시는 `screenshots/` 폴더의 캡처 이미지 참고.

## 성능 및 비용 개선 옵션 (향후 고도화 방향)

현재 구조는 매 요청마다 크롤링 + AI 호출을 처음부터 수행합니다. 트래픽이 늘어나거나 비용을 줄이고 싶을 때 고려할 수 있는 옵션들입니다.

| 옵션 | 효과 | 트레이드오프 |
|---|---|---|
| **결과 캐싱** (같은 URL 재요청 시 저장된 결과 반환) | 같은 기사를 여러 명이 요청해도 AI를 한 번만 호출 → 응답 속도 향상, API 비용 절감 | 캐시 저장소(예: Vercel KV, Redis) 추가 필요, 기사 내용이 갱신되면 캐시가 오래된 정보를 줄 수 있음 |
| **요청 병합(debounce)** | 짧은 시간 내 중복 클릭/요청을 하나로 묶음 | 사용자 체감 반응이 미세하게 늦어질 수 있음 |
| **프롬프트 토큰 절감** (본문을 일정 길이로 잘라서 전달) | AI 호출 비용 감소, 응답 속도 향상 | 너무 짧게 자르면 요약 품질이 떨어질 위험 |
| **더 빠른 모델로 전환** | 응답 속도 개선 | 요약 품질이 다소 낮아질 수 있음 (현재는 `claude-haiku-4-5`로 이미 속도와 품질의 균형을 고려해 선택함) |

현재 프로젝트 규모(과제 제출용 단일 사용자 테스트)에서는 위 최적화가 필수는 아니지만, 실제 서비스로 확장할 경우 우선적으로 캐싱 도입을 고려할 계획입니다.

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

### 배포 문제 진단 및 롤백 절차

**배포가 실패했거나 사이트가 정상 동작하지 않을 때:**

1. Vercel 대시보드 → 프로젝트 → **Deployments** 탭에서 실패한 배포(빨간색 "Error") 클릭
2. 배포 상세 화면의 **"Build Logs"**에서 어느 단계(설치/빌드/함수 실행)에서 실패했는지 확인
3. 브라우저에서 실제 동작을 확인할 때는 `F12` 개발자 도구의 **Console**(JS 에러) 및 **Network**(API 응답 상태 코드) 탭을 함께 확인

**흔한 원인과 대응:**

| 증상 | 가능한 원인 | 대응 |
|---|---|---|
| 빌드 자체가 실패함 | `requirements.txt` 누락 패키지, Python 문법 오류 | Build Logs에서 오류 스택 확인 후 코드 수정 → 재커밋 |
| 정적 파일(CSS/이미지 등)이 안 보임 | Framework Preset이 자동으로 "Python"으로 잡힘 | Vercel 프로젝트 Settings → General → Framework Preset을 **"Other"**로 재설정 |
| API 호출 시 500 에러 | 환경 변수(`ANTHROPIC_API_KEY`) 미등록 또는 오타 | Settings → Environment Variables 재확인 후 재배포 |

**이전 배포로 되돌리기(롤백)**: Deployments 탭에서 정상 작동했던 과거 배포 항목을 찾아 우측 `···` 메뉴 → **"Promote to Production"**을 선택하면, 코드를 되돌리지 않고도 즉시 이전 버전으로 복구할 수 있습니다.

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

### API 키 유출 대응 체크리스트

만약 API 키가 실수로 커밋되거나 외부에 노출된 것이 의심되는 경우, 아래 순서로 즉시 조치합니다.

1. **즉시 키 폐기**: Anthropic Console(https://console.anthropic.com) 접속 → 노출된 API 키를 즉시 비활성화/삭제
2. **새 키 발급**: 같은 화면에서 새 API 키 발급
3. **환경 변수 교체**: 로컬 `.env` 파일과 Vercel 대시보드의 Environment Variables 값을 새 키로 교체
4. **재배포**: Vercel에서 재배포하여 새 키가 적용되었는지 확인
5. **영향 범위 확인**: Anthropic Console의 사용량(Usage) 페이지에서 노출 기간 동안 비정상적인 호출이 있었는지 확인
6. **커밋 이력 정리**: 만약 `.env` 파일 자체가 커밋된 적이 있다면, `git log --all --full-history -- .env` 명령으로 이력을 확인하고, 필요 시 `git filter-repo` 또는 BFG Repo-Cleaner 같은 도구로 과거 커밋에서 완전히 제거

> 이 프로젝트는 `git log --all --full-history -- .env` 명령으로 `.env` 파일이 커밋 이력에 존재한 적이 없음을 확인했습니다.

## 알려진 제약사항

- 일부 언론사 사이트는 크롤링을 차단할 수 있어 본문 추출에 실패할 수 있습니다.
- 자바스크립트 렌더링 기반 사이트는 서버 사이드 요청만으로 본문을 가져오지 못할 수 있습니다.
- 본문 전체가 아닌, AI가 생성한 요약문만 사용자에게 노출하여 저작권 이슈를 최소화했습니다.
