import sys
from app.ui.cli import ChaosQuestApp


def main():
    try:
        app = ChaosQuestApp()
        app.start()
    except KeyboardInterrupt:
        print("\n\n👋 게임을 종료합니다.")
        sys.exit(0)


if __name__ == "__main__":
    main()
