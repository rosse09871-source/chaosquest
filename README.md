# ChaosQuest (v2.0)

> **클라우드 실전 리눅스 & SRE 인프라 트러블슈팅 아레나 & 학습 플랫폼**

ChaosQuest는 실제 프로덕션 환경에서 발생하는 리눅스 커널, 파일시스템, 프로세스, 네트워크, Nginx, Docker, 데이터베이스, AWS 보안 장애를 실시간으로 재현하고, 격리된 도커 샌드박스에서 직접 해결하는 **인터랙티브 웹 GUI 기반 인프라 교육 & 게임 플랫폼**입니다.

---

## 🌟 주요 핵심 기능

### 1. 63개 실무 인시던트 시나리오 (8대 도메인 · 21대 트랙)
* **스토리지/파일시스템**: 유령 파일 디스크립터 누수, Inode 고갈, 디스크 권한 손상
* **프로세스 & 자원**: 포트 충돌, 크래시 루프, 은닉형 고부하 프로세스 사냥
* **네트워크 & 방화벽**: DNS 질의 실패, iptables 패킷 드롭, MTU 타임아웃
* **웹서버 & 리버스 프록시**: Nginx 502 Bad Gateway, SSL 인증서 체인 오류, 413 페이로드 제한
* **컨테이너 & 런타임**: Docker 소켓 권한 오류, 데몬 JSON 문법 파괴, 로그 폭주 및 OOMKilled
* **데이터베이스 & 캐시**: SQLite 교착상태(Deadlock), Redis OOM, max_connections 한도 초과 및 좀비 락
* **클라우드 & 보안**: SSH 권한 잠금, AWS 자격증명 포맷 오류, Fail2ban IP 차단 복구
* **CI/CD & 릴리즈 파이프라인**: Git index.lock 잔류 해제, 휠 패키지 캐시 손상, LD_LIBRARY_PATH 복구

### 2. 듀얼 페인 웹 워크스페이스 & 5단계 트러블슈팅 힌트
* **좌측 패널**: 실시간 인시던트 티켓(증상, 심각도, 배점, 목표시간) 및 5단계 점진적 힌트(1~3단계 무료 / 4~5단계 감점)
* **우측 패널**: Xterm.js + WebSocket 기반의 격리된 실제 PTY Bash 터미널 연동

### 3. 1+2 하이브리드 인시던트 타이머 (Hybrid Timer)
* **사전 분석 무료 시간**: 워크스페이스 접속 시 타이머는 `00:00 [대기]` 상태로 유지되어 시간에 쫓기지 않고 인시던트 티켓을 정밀 분석 가능
* **듀얼 트리거 대응 시작**: 상단 `[대응 시작]` 버튼을 누르거나 터미널에 첫 키보드 입력 시 즉시 0초부터 타이머 카운트업 시작

### 4. 0.3초 초고속 컨테이너 프로비저닝 (Fast-Boot Architecture)
* 필수 도구가 사전 탑재된 전용 베이스 이미지(`chaosquest:base`)를 활용하여 기존 30초의 패키지 설치 대기 시간을 **0.3초 즉시 실행**으로 단축

### 5. 엔지니어 커뮤니티 포럼
* 5대 카테고리 (풀이 팁 Write-up, 질문 & 답변 Q&A, 현업 장애 회고, 문제 제안, 일반 토론)
* 키워드 실시간 검색, 최신순/추천순 정렬, 추천(좋아요) 토글, 댓글 스레드
* **내가 쓴 글 모아보기** 필터링 및 **작성자 본인 글/댓글 삭제** 기능

### 6. 관리자(Admin) 권한 및 모더레이션
* `daisy` 최고 관리자 계정 연동 및 보라색 `[ADMIN]` 전용 뱃지 부여
* 커뮤니티 스팸/악성 글 및 댓글 즉시 삭제 모더레이션 권한

---

## 🏛️ 시스템 아키텍처

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                            Web Browser Client                            │
│   (Dashboard / Dedicated Challenges / Workspace / Community Forum)       │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ HTTP REST / WebSocket (PTY)
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend Core Server                         │
│  ├─ Web Routes & Community REST APIs (FastAPI + Jinja2 + Tailwind)       │
│  ├─ WebSocket Terminal PTY Proxy (Asyncio Streams)                       │
│  ├─ AI Senior Mentor Engine (Container Telemetry Diagnostics)            │
│  └─ Session Watchdog & Auto Pruning Service                              │
└──────────────────┬────────────────────────────────────┬──────────────────┘
                   │ SQLAlchemy ORM                     │ Docker SDK
                   ▼                                    ▼
┌──────────────────────────────────────┐ ┌─────────────────────────────────┐
│        SQLite3 Database Engine       │ │    Docker Isolated Sandbox      │
│  - users (id, username, is_admin)    │ │   (chaosquest:base Container)   │
│  - stage_attempts (scores, timers)   │ │  ├─ Sabotage Injected Faults    │
│  - posts & comments & likes          │ │  └─ Verify Engine Shell         │
└──────────────────────────────────────┘ └─────────────────────────────────┘
```

---

## 🚀 빠른 시작 가이드 (Quick Start)

### 로컬 환경 실행

```bash
# 1. 저장소 클론 및 가상환경 설정
git clone https://github.com/rosse09871-source/chaosquest.git
cd chaosquest
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. 테스트 스위트 검증 (20종 테스트 100% 통과)
pytest tests/

# 3. 전용 베이스 이미지 빌드 (최초 1회, 0.3초 부팅 최적화)
./scripts/build_base_image.sh

# 4. 웹 서버 실행 (포트 8000)
python3 -m uvicorn app.web.server:app --host 0.0.0.0 --port 8000 --reload
```

브라우저에서 `http://localhost:8000`으로 접속합니다.

---

### AWS EC2 운영 서버 배포

```bash
# 1. 서버 코드 가져오기
cd /path/to/chaosquest
git pull

# 2. 전용 베이스 이미지 1회 빌드
sudo ./scripts/build_base_image.sh

# 3. 서비스 재시작
sudo systemctl restart chaosquest-web
```

---

## 📂 프로젝트 디렉터리 구조

```text
chaosquest/
├── app/
│   ├── config.py                 # 전역 환경변수 및 세션 설정
│   ├── database/
│   │   ├── connection.py         # DB 커넥션 및 자동 마이그레이션
│   │   ├── models.py             # User, Post, Comment, PostLike ORM 모델
│   │   └── crud.py               # 랭킹, 통계, 커뮤니티 CRUD 메서드
│   ├── engine/
│   │   ├── orchestrator.py       # 도커 샌드박스 라이프사이클 및 PTY 소켓
│   │   ├── stage_loader.py       # 54개 메타데이터 로더
│   │   └── ai_mentor.py          # AI 시니어 사수(김수석) 진단 엔진
│   └── web/
│       ├── server.py             # FastAPI 라우터 및 WebSocket 핸들러
│       └── templates/            # 다크 옵시디언 테마 HTML 템플릿
│           ├── dashboard.html    # Bento 메트릭 대시보드
│           ├── challenges.html   # 54개 문제 맵 (아코디언 형태)
│           ├── workspace.html    # 듀얼 페인 웹 워크스페이스
│           ├── community.html    # 커뮤니티 포럼 메인
│           └── post_detail.html  # 게시글 상세, 추천 및 댓글
├── challenges/                   # 54개 실무 시나리오 (sabotage.sh / verify.sh)
├── docker/
│   └── Dockerfile.base           # 사전 패키지 탑재 초고속 베이스 이미지
├── scripts/
│   └── build_base_image.sh       # 베이스 이미지 원클릭 빌드 스크립트
├── tests/                        # Pytest 단위 및 통합 테스트 스위트
└── requirements.txt              # 파이썬 의존성 패키지 목록
```

---

## 🛡️ 보안 및 거버넌스 정책
* **샌드박스 격리**: 모든 문제 해결 작업은 제한된 메모리 및 CPU가 할당된 격리 컨테이너에서 수행됩니다.
* **보안 정보 배제**: 저장소 내 하드코딩된 시크릿 키나 개인 토큰이 없으며 환경변수(`DATABASE_URL`, `SESSION_TTL_SECONDS` 등)를 통해 제어됩니다.
* **모더레이션**: 악성 게시글 및 스팸은 관리자(`daisy`) 권한으로 즉시 제재 가능합니다.
