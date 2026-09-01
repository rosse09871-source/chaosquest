# 🏛️ ChaosQuest 시스템 아키텍처 및 동작 원리 명세서 (ARCHITECTURE.md)

> **ChaosQuest**는 실제 현업 인프라 엔지니어링 장애(Linux, Process, Network, Nginx, Docker, Database, AWS Security)를 재현하고, 독립된 격리 샌드박스 환경에서 실시간으로 조사·복구하는 **인터랙티브 트러블슈팅 플랫폼**입니다.

---

## 📌 1. 전체 시스템 아키텍처 다이어그램

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                    🌐 ACCESS LAYER                                      │
│                                                                                          │
│    [ 사용자 웹 브라우저 ]                           [ 사용자 터미널 (SSH) ]               │
│             │                                                  │                         │
│             ▼                                                  ▼                         │
│      Port 80 (HTTP)                                     Port 22 (SSH)                    │
│    ┌──────────────────┐                               ┌──────────────────┐               │
│    │  Nginx Reverse   │ ──(WebSocket Reverse Proxy)──▶│   ttyd Daemon    │               │
│    │      Proxy       │                               │   (Port 7681)    │               │
│    └──────────────────┘                               └──────────────────┘               │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
                                              ▼ (TTY Session Stream)
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                   🧠 CORE ENGINE LAYER                                   │
│                                                                                          │
│   ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│   │  🖥️ ChaosQuestApp (app/ui/cli.py & app/ui/components.py)                          │   │
│   │   - 3단계 계층 네비게이션: [7대 도메인] ➡️ [18대 트랙] ➡️ [54개 문제 풀]              │   │
│   │   - 실시간 TUI 렌더링: 인시던트 티켓, 3단계 힌트, 스코어링, 포스트모템 회고 리포트     │   │
│   └────────────────────────┬────────────────────────────────────────┬────────────────┘   │
│                            │                                        │                    │
│                            ▼                                        ▼                    │
│   ┌─────────────────────────────────┐      ┌─────────────────────────────────────────┐   │
│   │ 📂 Stage Loader & Discovery     │      │ 🐳 Docker Sandbox Orchestrator          │   │
│   │ (app/engine/stage_loader.py)    │      │ (app/engine/orchestrator.py)            │   │
│   │  - 54개 문제 YAML/스크립트 자동로드│      │  - Docker SDK 기반 격리 컨테이너 라이프사이클 │   │
│   │  - 도메인/트랙 계층 구조 자동 빌드   │      │  - sabotage.sh 고장 주입 & 샌드박스 쉘 연결  │   │
│   └────────────────┬────────────────┘      │  - verify.sh 커널/프로세스 2중 채점     │   │
│                    │                       └────────────────────┬────────────────────┘   │
│                    ▼                                            │                        │
│   ┌─────────────────────────────────┐                           ▼                        │
│   │ 💾 Database & Persistence Layer │              ┌─────────────────────────┐           │
│   │ (app/database/models.py & crud) │              │ 🧹 Session Watchdog     │           │
│   │  - SQLite (data/chaosquest.db)  │              │ (app/engine/watchdog.py)│           │
│   │  - 유저 정보, 풀이 기록, 글로벌 랭킹 │              │  - 30분 초과 유령 세션 청소│           │
│   └─────────────────────────────────┘              └─────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┬────────────────────────┘
                                                                  │
                                                                  ▼ (Docker Socket: /var/run/docker.sock)
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                  🐳 SANDBOX EXECUTION LAYER                              │
│                                                                                          │
│   ┌───────────────────────────────┐              ┌───────────────────────────────┐       │
│   │ 📦 Container: chaos_101-1_sess│              │ 📦 Container: chaos_201-1_sess│  ...  │
│   │  - Ubuntu 22.04 LTS (격리)     │              │  - Ubuntu 22.04 LTS (격리)     │       │
│   │  - CPU: 0.5 Core / Mem: 256MB │              │  - CPU: 0.5 Core / Mem: 256MB │       │
│   │  - 고장 데몬 / 파일시스템 장애 재현│              │  - 80번 포트 선점 좀비 프로세스 재현│       │
│   └───────────────────────────────┘              └───────────────────────────────┘       │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 2. 핵심 모듈별 상세 역할 및 동작 원리

### 1) 🖥️ TUI & 사용자 상호작용 (`app/ui/cli.py`, `app/ui/components.py`)
* **역할**: 터미널 환경에서 직관적인 그래픽 UI를 제공합니다.
* **3단계 계층 네비게이션**:
  1. `_domain_selection_menu()`: 7대 인프라 도메인 선택 및 도메인별 진척률(%) 표시
  2. `_track_selection_menu(domain_id)`: 해당 도메인의 중분류 트랙(Track 101, 102 등) 선택
  3. `_sub_stage_selection_menu(domain_id, track_id)`: `[Easy]`, `[Medium]`, `[Hard]` 난이도별 세부 문제 선택
* **인시던트 진행 루프 (`_play_stage`)**:
  * 인시던트 티켓 렌더링 (보고자, 심각도, 증상, 목표)
  * `[1] 샌드박스 쉘 접속`: 사용자를 컨테이너 내부 쉘(`/bin/bash`)로 전환
  * `[2] 힌트 요청`: 점수를 차감하고 3단계 점진적 힌트 열람
  * `[3] 복구 검증 및 제출`: `verify.sh` 실행 및 포스트모템 리포트 출력
  * `[4] 인시던트 리셋`: 컨테이너 재생성 및 고장 재주입

### 2) 📂 스테이지 자동 검색 엔진 (`app/engine/stage_loader.py`)
* **역할**: `challenges/` 디렉터리 내의 모든 스테이지 폴더를 자동 스캔하여 메모리 및 DB에 동기화합니다.
* **폴더 규격**:
  * `metadata.yaml`: 메타데이터 (도메인, 트랙, 제목, 난이도, 배점, 3단계 힌트, 포스트모템 회고)
  * `sabotage.sh`: 컨테이너 기동 시 실행되는 고장 주입 스크립트 (POSIX Double-fork 데몬화 지원)
  * `verify.sh`: 문제 복구 여부를 판별하는 채점 스크립트 (0: 성공, 1: 실패)
* **카탈로그 빌더 (`get_domain_catalog()`)**:
  * 로드된 54개 문제를 `Domain ➡️ Track ➡️ Stage` 계층형 딕셔너리로 자동 그룹화

### 3) 🐳 도커 샌드박스 오케스트레이터 (`app/engine/orchestrator.py`)
* **역할**: 호스트 머신의 Docker 데몬(`/var/run/docker.sock`)과 직접 통신하여 사용자 전용 격리 컨테이너의 라이프사이클을 관리합니다.
* **주요 메서드**:
  * `create_sandbox(stage_id, session_id)`:
    * `ubuntu:22.04` 베이스 이미지로 독립 컨테이너 생성 (`chaos_<stage_id>_<session_id>`)
    * CPU 0.5코어, 메모리 256MB 자원 쿼터(Quota) 제한 적용
    * 컨테이너 내부에서 `sabotage.sh`를 실행하여 고장 상황 주입
  * `verify_sandbox(stage_id, session_id)`:
    * 컨테이너 내부에서 `verify.sh`를 `exec_run`으로 실행하고 반환 코드(Exit Code)로 채점
  * `destroy_sandbox(stage_id, session_id)`:
    * 세션 종료 또는 리셋 시 컨테이너를 안전하게 강제 중지 및 삭제

### 4) 🧹 세션 및 리소스 워치독 (`app/engine/watchdog.py`)
* **역할**: 30분(`DEFAULT_SESSION_TTL_SECONDS`) 이상 사용자가 방치한 컨테이너를 탐색하여 자동 삭제하고, DB 상태를 `ABANDONED`로 변경하여 서버 메모리(RAM) 고갈을 방지합니다.
* 앱 기동 시(`ChaosQuestApp.start()`) 및 백그라운드 주기 작업으로 자동 실행됩니다.

### 5) 💾 데이터베이스 레이어 (`app/database/`)
* **역할**: 사용자 정보, 문제 풀이 이력, 스코어링, 실시간 리더보드를 관리합니다.
* **주요 테이블**:
  * `users`: 유저 닉네임, 누적 점수, 가입 일시
  * `stages`: 54개 스테이지 메타데이터 캐시
  * `stage_attempts`: 시도 이력 (시작시간, 종료시간, 소요시간, 사용한 힌트 수, 획득 점수, 세션 ID, 컨테이너 ID)
* **스코어링 공식**:
  * 기본 점수 - (사용한 힌트 수 * 50) + 스피드 보너스

---

## 📚 3. 7대 도메인 18대 트랙 (54개 문제) 카탈로그

| 도메인 ID | 도메인 명칭 | 트랙 ID 및 주제 | 난이도 구성 |
|---|---|---|---|
| **Domain 1** | 💾 파일시스템 & 스토리지 | **Track 101**: 유령 파일 디스크립터 누수<br>**Track 102**: Inode 고갈 및 임시 파일 누적<br>**Track 103**: 권한 & 소유권 지옥 (403) | Easy / Medium / Hard<br>(총 9문제) |
| **Domain 2** | ⚙️ 프로세스 & 시스템 자원 | **Track 201**: 포트 충돌 & 좀비 프로세스<br>**Track 202**: CrashLoop 무한 재시작<br>**Track 203**: CPU 100% 폭주 악성 데몬 | Easy / Medium / Hard<br>(총 9문제) |
| **Domain 3** | 🌐 네트워크 & DNS & 방화벽 | **Track 301**: DNS 이름 풀이 실패<br>**Track 302**: iptables 유령 방화벽 차단<br>**Track 303**: MTU 불일치 & 라우팅 단절 | Easy / Medium / Hard<br>(총 9문제) |
| **Domain 4** | 🚀 웹 서버 & 리버스 프록시 | **Track 401**: Nginx 502 Bad Gateway<br>**Track 402**: SSL/TLS 인증서 & HTTPS 설정<br>**Track 403**: 413 바디 제한 & 504 타임아웃 | Easy / Medium / Hard<br>(총 9문제) |
| **Domain 5** | 🐳 도커 & 컨테이너 런타임 | **Track 501**: 도커 소켓 & 데몬 권한 오류<br>**Track 502**: 컨테이너 환경변수 & 설정 꼬임 | Easy / Medium / Hard<br>(총 6문제) |
| **Domain 6** | 🗄️ 데이터베이스 & 캐시 연동 | **Track 601**: DB 파일 락 & WAL 저널 손상<br>**Track 602**: Redis 바인딩 & OOM Eviction | Easy / Medium / Hard<br>(총 6문제) |
| **Domain 7** | ☁️ AWS 클라우드 & 인프라 보안 | **Track 701**: SSH 키 권한 & StrictModes<br>**Track 702**: AWS CLI 자격증명 & STS 토큰<br>**Track 703**: Fail2ban IP 차단 해제 (Unban) | Easy / Medium / Hard<br>(총 9문제) |

---

## 🌐 4. AWS 클라우드 배포 및 운영 아키텍처

```text
[AWS EC2 Free Tier (t3.micro - 1GB RAM)]
 ├── 💾 2GB Swapfile (/swapfile) ────────── 메모리 부족(OOM) 방지 가상 램
 ├── 🐳 Docker Engine (Host) ─────────────── 샌드박스 컨테이너 온디맨드 스폰
 ├── 📦 ttyd Daemon (Port 7681) ─────────── Web-to-Terminal 스트리밍 게이트웨이
 ├── 🚀 Nginx Reverse Proxy (Port 80) ───── WebSocket 프록시 & 엔드포인트 서빙
 └── ⚙️ Systemd Service ─────────────────── chaosquest-web.service 데몬 자동 복구
```
