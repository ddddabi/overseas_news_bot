# overseas_news_bot

**국외뉴스 자동화** 

해외 주요 언론사의 기술/보안 분야 뉴스 중 개인정보 관련 기사를 매일 자동으로 수집하고 구글 시트에 저장하는 자동화 시스템

---

## 📌 프로젝트 개요

### 🎯 목적
- 해외 언론사를 한눈에 모아 볼 수 있도록 함
- 영문 기사 제목을 직역해 볼 수 있음

---

## 📦 사용한 도구 및 라이브러리

| 구분   | 도구/라이브러리           | 설명                                      |
|--------|---------------------------|-------------------------------------------|
| 언어   | Python 3.9                | 프로젝트의 메인 언어                       |
| 수집   | `feedparser`, `requests`  | RSS 피드 파싱 및 HTTP 요청 처리            |
| 번역   | `googletrans`             | 뉴스 제목 자동 번역                        |
| 저장   | `gspread`, `pandas`       | Google Sheets API 연동 및 데이터 저장 처리 |
| 시간   | `python-dateutil`, `pytz` | 다양한 시간 포맷을 KST로 변환               |
| 로깅   | `logging`                 | 실행 로그 기록 및 오류 추적                |
| 통신   | Webhook (KakaoWork)       | 실행 시작/완료 알림 전송                   |

---

## 📁 파일 구조 및 구성

<img width="735" alt="image" src="https://github.com/user-attachments/assets/a1782f78-f6d5-46b1-b917-41aed56da004" />

---

## 🔄 실행 흐름

<img width="1018" alt="image" src="https://github.com/user-attachments/assets/20878c92-71be-4378-b87d-b048c0b73ab3" />

## 필터링
### 날짜 필터링
- 기본 설정
  매일 아침 9시에 자동 실행되며, 스크립트 실행일 기준 '전날 기사'를 대상으로 필터링이 적용됩니다.

- 전체 뉴스 시트
  날짜에 관계없이 수집된 모든 뉴스가 저장되며, 검색일시와 기사일자를 기준으로 조회 및 정렬 가능합니다.

- 필터링 뉴스 시트
  사용자가 지정한 날짜 또는 기간(--date, --from_date, --to_date)에 해당하면서, 지정된 키워드를 포함한 기사만 저장됩니다.

- 특정 날짜 기사만 필터링하고 싶다면 다음과 같이 스크립트를 수동 실행하면 됩니다.

| 명령어 예시                                      | 설명                         |
|--------------------------------------------------|------------------------------|
| `python3 daily_fetch.py`                         | 어제 날짜 기준으로 실행       |
| `python3 daily_fetch.py --date 05-12`            | 5월 12일 기사만 조회          |
| `python3 daily_fetch.py --from_date 05-10 --to_date 05-13` | 5월 10일부터 13일까지 기사 조회 |

### 기사 필터링 조건

필터링된 뉴스는 아래 3가지 조건을 모두 만족해야 합니다


| 조건             | 설명                                                         |
|------------------|--------------------------------------------------------------|
| 날짜 필터 통과   | 오늘 실행 기준으로 어제 날짜의 기사만 수집 (형식: `MM-DD`)      |
| 키워드 필터 통과 | 제목에 `"privacy"`, `"개인정보"`, `"유출"` 등의 키워드 포함 시 통과 |
| 중복 기사 아님   | 기사 내용의 해시값을 기준으로 중복 기사 제외                     |

---

## 📊 결과 예시

- ✅ Google Sheets 기록:  
  [📄 요약 엑셀 보기](https://docs.google.com/spreadsheets/d/1OH-1RTh05dtevPa2xi4tQqaPmv_H_gcP19ZwStd840k/edit?usp=sharing)
  <img width="1080" alt="image" src="https://github.com/user-attachments/assets/caee5457-65dd-40c3-8bad-fe679e5708e0" />
  
---

## 🔧 향후 개선 방향

1. 실시간 반응형 시트 구성 (Google Apps Script) → 뉴스 선정으로 체크한 뉴스 자동 분리 시트로 이동
2. 직역된 영문 제목이 어색하기에 기사 제목처럼 번역하도록 AI(gemini, GPT) 번역 적용(현재는 직역과 의역 동일하게 엑셀에 입력됨.)


---

## 💡 기대 효과

- 수작업 제거 → 매일 아침 최신 국외 뉴스 자동 확보
- 국외 뉴스 수집 시간 최소화
- 영문 제목 번역(직역) 자동화

---

## 기타 설정해야 할 것
### config.yaml
```
webhook:
  url: "WEBHOOK URL"

```

### credentials.json
```
{
  "type": "service_account",
  "project_id": "",
  "private_key_id": "",
  "private_key": "",
  "client_email": "",
  "client_id": "",
  "auth_uri": "",
  "token_uri": "",
  "auth_provider_x509_cert_url": "",
  "client_x509_cert_url": "",
  "universe_domain": "googleapis.com"
}

```
