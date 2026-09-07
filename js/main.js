// js/main.js
// summarize.html의 입력 폼을 api/summarize.py 백엔드와 연결하는 스크립트

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('summary-form');
  const urlInput = document.getElementById('article-url');
  const submitButton = form.querySelector('button[type="submit"]');
  const resultPanel = document.getElementById('result-panel');
  const statusBadge = resultPanel.querySelector('.status-badge');
  const summaryList = resultPanel.querySelector('.summary-list');
  const keywordList = resultPanel.querySelector('.keyword-list');
  const originalLinkButton = resultPanel.querySelector('.original-link');
  const errorMessage = document.getElementById('form-error');

  const API_ENDPOINT = '/api/summarize';
  const REQUEST_TIMEOUT_MS = 20000; // 20초: 서버 내부 타임아웃(10초)보다 여유 있게 설정

  form.addEventListener('submit', async function (event) {
    event.preventDefault();

    const url = urlInput.value.trim();

    // --- 1. 클라이언트(프론트엔드) 1차 검증 ---
    // 서버까지 요청을 보내기 전에, 프론트에서 먼저 걸러낼 수 있는 실수는 미리 걸러냅니다.
    // (불필요한 서버 요청을 줄이고, 사용자에게 더 빠른 피드백을 줄 수 있습니다.)
    hideError();

    if (!url) {
      showError('뉴스 기사 URL을 입력해주세요.');
      return;
    }
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      showError('올바른 URL 형식이 아니에요. (예: https://로 시작)');
      return;
    }

    // --- 2. 요청 시작: 로딩 상태로 전환 ---
    setLoadingState(true);

    // 타임아웃 처리를 위한 AbortController
    // fetch 자체에는 timeout 옵션이 없어서, 이런 방식으로 직접 구현해야 합니다.
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // response.ok는 상태 코드가 200~299일 때만 true.
      // 400, 500 같은 에러 상태는 여기서 false로 걸러집니다.
      const data = await response.json();

      if (!response.ok) {
        // 백엔드(summarize.py)가 미리 만들어준 에러 메시지를 그대로 사용
        // (예: "뉴스 기사 URL을 입력해주세요.", "해당 페이지에서 기사를 가져올 수 없어요." 등)
        showError(data.error || '알 수 없는 오류가 발생했습니다.');
        setLoadingState(false);
        return;
      }

      // --- 3. 성공: 결과를 화면에 렌더링 ---
      renderResult(data, url);
      setLoadingState(false);
    } catch (err) {
      clearTimeout(timeoutId);
      setLoadingState(false);

      if (err.name === 'AbortError') {
        showError('요약 생성이 너무 오래 걸려요. 잠시 후 다시 시도해주세요.');
      } else {
        // 네트워크 자체가 끊겼거나 서버에 아예 접속이 안 되는 경우
        showError('네트워크 오류가 발생했습니다. 인터넷 연결을 확인해주세요.');
      }
    }
  });

  function setLoadingState(isLoading) {
    submitButton.disabled = isLoading;
    submitButton.textContent = isLoading ? '요약 생성 중...' : '요약하기';
    statusBadge.textContent = isLoading ? '요약 중' : statusBadge.textContent;
  }

  function renderResult(data, originalUrl) {
    // 요약 3줄 렌더링
    summaryList.innerHTML = '';
    (data.summary || []).forEach(function (line) {
      const li = document.createElement('li');
      li.textContent = line;
      summaryList.appendChild(li);
    });

    // 키워드 렌더링
    keywordList.innerHTML = '';
    (data.keywords || []).forEach(function (keyword) {
      const span = document.createElement('span');
      span.textContent = keyword;
      keywordList.appendChild(span);
    });

    // 원문 보기 버튼 활성화
    originalLinkButton.disabled = false;
    originalLinkButton.onclick = function () {
      window.open(originalUrl, '_blank', 'noopener');
    };

    statusBadge.textContent = '완료';
    resultPanel.classList.add('is-ready');
  }

  function showError(message) {
    errorMessage.textContent = message;
    errorMessage.hidden = false;
  }

  function hideError() {
    errorMessage.hidden = true;
    errorMessage.textContent = '';
  }
});
