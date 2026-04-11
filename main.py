# main.py
# ─────────────────────────────────────────────────────────────────────────────
# Mini NPU Simulator 의 진입점.
#
# 메뉴:
#   1) 모드 1: 사용자 입력 (3×3)
#   2) 모드 2: data.json 분석
#   3) 성능 분석 (벤치마크)
#   4) MAC 구현 버전 선택   — baseline / sumprod / bitwise 중 골라 사용
#   5) 패턴 생성기 (보너스 2) — 사용자가 N 입력 → Cross/X 자동 생성
#   0) 종료
#
# 버전 선택은 mac.py 의 set_version() 으로 모듈 전역 상태를 바꾼다.
# 이후 mode1/mode2/benchmark 가 호출하는 mac.mac_2d / mac.mac_1d 가
# 자동으로 새 구현을 사용한다.
# ─────────────────────────────────────────────────────────────────────────────

import mac
import mode1
import mode2
import benchmark
import pattern_gen


def _print_menu():
    """대화형 메뉴를 출력한다. 헤더에 현재 선택된 MAC 버전도 함께 보여준다."""
    print()
    print("==============================")
    print("   Mini NPU Simulator (MAC)   ")
    print(f"   * 현재 MAC 버전: {mac.get_version()}")
    print("==============================")
    print("  1) 모드 1: 사용자 입력 (3x3)")
    print("  2) 모드 2: data.json 분석")
    print("  3) 성능 분석 (벤치마크)")
    print("  4) MAC 구현 버전 선택")
    print("  5) 패턴 생성기 (N 입력 → Cross/X 자동)")
    print("  0) 종료")
    print("------------------------------")


def _select_version():
    """사용자에게 MAC 구현 버전을 선택받아 mac.set_version() 으로 적용한다."""
    print("\n--- MAC 구현 버전 선택 ---")
    # mac.VERSIONS 순서대로 번호를 매겨 출력 — 사람이 외울 필요 없이 숫자만 누르면 됨
    for idx, name in enumerate(mac.VERSIONS, start=1):
        marker = " (현재)" if name == mac.get_version() else ""
        desc = mac.VERSION_DESCRIPTIONS.get(name, "")
        print(f"  {idx}) {name}{marker} — {desc}")
    print("  0) 취소")

    try:
        raw = input("선택> ").strip()
    except EOFError:
        print("\n[EOF] 버전 선택을 취소합니다.")
        return

    if raw == "0" or raw == "":
        print("취소되었습니다.")
        return

    # 숫자(1..N)로 들어왔을 수도, 이름('sumprod')으로 들어왔을 수도 있다.
    chosen = None
    if raw.isdigit():
        n = int(raw)
        if 1 <= n <= len(mac.VERSIONS):
            chosen = mac.VERSIONS[n - 1]
    elif raw in mac.VERSIONS:
        chosen = raw

    if chosen is None:
        print(f"[!] 알 수 없는 선택: {raw!r}. 변경하지 않습니다.")
        return

    try:
        mac.set_version(chosen)
        print(f"-> MAC 버전을 '{chosen}' 로 변경했습니다.")
    except ValueError as e:
        # 방어적: VERSIONS 검증을 통과했으니 사실상 도달하지 않음
        print(f"[ERROR] {e}")


def _pattern_generator():
    """메뉴 5번 — 사용자가 N 을 입력해 Cross/X 패턴을 자동 생성하고 후속 액션을 고른다.

    보너스 2 의 진짜 진입점. pattern_gen 모듈을 사용자에게 직접 노출한다.
    """
    print("\n--- 패턴 생성기 (보너스 2) ---")

    # 1) N 을 입력 받는다 — 양의 정수만 허용
    try:
        raw = input("N 입력 (예: 7) > ").strip()
    except EOFError:
        print("\n[EOF] 패턴 생성기를 빠져나갑니다.")
        return

    if not raw.isdigit() or int(raw) < 1:
        print(f"[!] N 은 1 이상의 정수여야 합니다: {raw!r}")
        return
    n = int(raw)

    # 2) Cross / X 패턴 생성
    cross = pattern_gen.make_cross(n)
    x = pattern_gen.make_x(n)

    # 3) 시각화 출력 — 여기서 처음으로 render() 를 사용한다
    print(f"\n[Cross {n}x{n}]")
    print(pattern_gen.render(cross))
    print(f"\n[X {n}x{n}]")
    print(pattern_gen.render(x))

    # 4) 후속 액션 서브메뉴
    print("\n이 패턴들로 무엇을 할까요?")
    print("  1) 모드1 으로 진입 (필터 = Cross/X, 패턴만 입력)")
    print("  2) 이 N 으로 단일 벤치마크 1회")
    print("  3) 그냥 출력만 (돌아가기)")

    try:
        sub = input("선택> ").strip()
    except EOFError:
        print("\n[EOF] 패턴 생성기를 빠져나갑니다.")
        return

    if sub == "1":
        # 자동 생성된 Cross/X 를 필터로 사용 — 사용자는 N×N 패턴만 입력
        try:
            mode1.run_with_filters(cross, x, n, label_a="Cross", label_b="X")
        except EOFError:
            print("\n[EOF] 패턴 입력이 종료되어 모드1을 빠져나갑니다.")
    elif sub == "2":
        benchmark.run_for_size(n)
    elif sub == "3" or sub == "":
        print("패턴 출력만 하고 돌아갑니다.")
    else:
        print(f"[!] 알 수 없는 선택: {sub!r}. 돌아갑니다.")


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
        elif choice == "4":
            _select_version()
        elif choice == "5":
            _pattern_generator()
        elif choice == "0":
            print("종료합니다.")
            return
        else:
            print(f"[!] 알 수 없는 선택: {choice!r}. 0~5 중에서 입력하세요.")


if __name__ == "__main__":
    main()
