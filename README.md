# 🚨 ChaosQuest

> **"클라우드 위에서 즐기는 실전 리눅스/인프라 트러블슈팅 아레나 & 학습 플랫폼"**

ChaosQuest는 실제 현업에서 발생하는 리눅스 커널, 프로세스, 네트워크, Nginx, Docker, 데이터베이스, AWS 보안 장애를 재현하고, 독립된 격리 샌드박스에서 직접 해결하는 **인터랙티브 터미널 게임 & 교육 플랫폼**입니다.

---

## 🏛️ 7대 도메인 18대 트랙 (54개 실무 문제 풀)

```text
🏛️ ChaosQuest 54개 실전 인시던트 커리큘럼
├─ 💾 [도메인 1] 파일시스템 & 스토리지 (Track 101 ~ 103 : 9문제)
├─ ⚙️ [도메인 2] 프로세스 & 시스템 자원 (Track 201 ~ 203 : 9문제)
├─ 🌐 [도메인 3] 네트워크 & DNS & 방화벽 (Track 301 ~ 303 : 9문제)
├─ 🚀 [도메인 4] 웹 서버 & 리버스 프록시 (Track 401 ~ 403 : 9문제)
├─ 🐳 [도메인 5] 도커 & 컨테이너 런타임 (Track 501 ~ 502 : 6문제)
├─ 🗄️ [도메인 6] 데이터베이스 & 캐시 연동 (Track 601 ~ 602 : 6문제)
└─ ☁️ [도메인 7] AWS 클라우드 & 인프라 보안 (Track 701 ~ 703 : 9문제)
```

모든 트랙은 **`[Easy]` ➡️ `[Medium]` ➡️ `[Hard]`** 3단계 난이도로 구성되어 있습니다.

---

## 🚀 빠른 시작 (Quickstart)

### 로컬 실행
```bash
# 1. 가상환경 생성 및 의존성 설치
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. 테스트 실행
pytest tests/

# 3. 게임 실행
python -m app.main
```

### AWS EC2 1-클릭 배포
```bash
git clone https://github.com/rosse09871-source/chaosquest.git
cd chaosquest && bash deploy/setup_ec2.sh
bash deploy/launch_web.sh
```

---

## 📖 시스템 아키텍처 및 동작 원리
자세한 시스템 아키텍처, 도커 샌드박스 라이프사이클, 세션 워치독, 데이터베이스 스키마는 **[ARCHITECTURE.md](ARCHITECTURE.md)** 문서를 참조하세요.
