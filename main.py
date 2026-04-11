# main.py
# ─────────────────────────────────────────────────────────────────────────────
# Mini NPU Simulator 의 진입점.
#
# 메뉴:
#   1) 모드 1: 사용자 입력 (3×3)
#   2) 모드 2: data.json 분석
#   3) 성능 분석 (벤치마크)  - 보너스 1 비교도 함께 출력
#   0) 종료
# ─────────────────────────────────────────────────────────────────────────────

import mode1
import mode2
import benchmark


def _print_menu():
    """대화형 메뉴를 출력한다."""
    print()
    print("==============================")
    print("   Mini NPU Simulator (MAC)   ")
    print("==============================")
    print("  1) 모드 1: 사용자 입력 (3x3)")
    print("  2) 모드 2: data.json 분석")
    print("  3) 성능 분석 (벤치마크)")
    print("  0) 종료")
    print("------------------------------")


def main():
    """대화 루프 — 사용자가 0을 입력할 때까지 메뉴를 반복 표시한다."""
    while True:
        _print_menu()

        try:
            choice = input("선택> ").strip()
        except EOFError:
            # 표준입력이 닫히면 더 이상 진행 불가 → 깔끔히 종료
            print("\n[EOF] 입력이 종료되어 프로그램을 끝냅니다.")
            return
        except KeyboardInterrupt:
            print("\n[Ctrl+C] 프로그램을 종료합니다.")
            return

        if choice == "1":
            # 사용자 입력 모드 — 내부에서 다시 EOFError가 날 수 있으므로 감싸준다.
            try:
                mode1.run()
            except EOFError:
                print("\n[EOF] 입력이 종료되어 모드1을 빠져나갑니다.")
        elif choice == "2":
            mode2.run("data.json")
        elif choice == "3":
            benchmark.run()
        elif choice == "0":
            print("종료합니다.")
            return
        else:
            print(f"[!] 알 수 없는 선택: {choice!r}. 0~3 중에서 입력하세요.")


if __name__ == "__main__":
    main()
