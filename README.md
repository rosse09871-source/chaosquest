# 🚨 ChaosQuest

> **"클라우드 위에서 즐기는 리눅스/인프라 트러블슈팅 방탈출 게임 & 학습 플랫폼"**

ChaosQuest는 실제 현업에서 발생하는 리눅스, 네트워크, 웹 서버, 데이터베이스, 보안 장애 시나리오를 직접 조사하고 복구하는 인터랙티브 터미널 TUI 게임 & 교육 플랫폼입니다.

---

## 🏗️ 아키텍처 개요
- **Terminal UI**: Python `Textual` & `Rich` 기반 고성능 터미널 그래픽 인터페이스
- **Isolation Sandbox**: Docker 컨테이너를 통한 사용자별/스테이지별 안전 격리 환경
- **Persistence & Scoring**: SQLAlchemy ORM (SQLite / PostgreSQL) 기반 전적 및 타임어택 랭킹 기록
- **Access Portal**: SSH Restricted Shell (`ssh play@...`) 및 Web TTY (`ttyd` + Nginx SSL)

---

## 🚀 빠른 시작 (Local Quickstart)

### 1. 가상환경 생성 및 의존성 설치
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 데이터베이스 초기화 및 테스트 실행
```bash
pytest tests/
```

### 3. 게임 실행
```bash
python -m app.main
```

---

## 📂 프로젝트 구조
```text
chaosquest/
├── app/
│   ├── database/       # DB 모델, 커넥션, CRUD 쿼리
│   ├── engine/         # Docker 컨테이너 및 세션 오케스트레이션
│   └── ui/             # Textual/Rich TUI 컴포넌트
├── challenges/         # 스테이지별 고장 주입 및 채점 스크립트
├── deploy/             # AWS EC2 및 Nginx/SSH 배포 스크립트
└── tests/              # 단위 테스트
```
