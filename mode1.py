# mode1.py
# ─────────────────────────────────────────────────────────────────────────────
# 모드 1: 사용자 입력 모드.
#
# 두 가지 진입점:
#   run()                — 과제 필수: 3×3 고정. 두 필터와 패턴을 모두 사용자가 입력.
#   run_with_filters()   — 보너스 2 연동: 필터 A/B 가 미리 주어지고(예: pattern_gen
#                          으로 만든 N×N Cross/X), 사용자는 N×N 패턴만 입력.
#
# 두 진입점 모두 내부 _judge_and_print() 으로 통일된 결과 출력을 거친다.
# ─────────────────────────────────────────────────────────────────────────────

import time

from mac import mac_2d


# 동점(거의 같음) 판정 임계값 — 부동소수 오차로 인한 우연 일치를 방지
EPSILON = 1e-9


def _read_grid(label, n):
    """N줄(공백 구분) 입력으로 N×N 격자를 읽는다.

    숫자 파싱 실패, 행/열 수 불일치 시 사용자에게 다시 입력 받는다.

    Args:
        label: 입력 안내 문구에 쓰일 이름 (예: '필터 A')
        n: 격자 크기

    Returns:
        list[list[float]]: N×N 2차원 리스트
    """
    while True:
        print(f"\n[{label}] {n}×{n} 격자를 한 줄에 {n}개 숫자(공백 구분)로 {n}줄 입력하세요.")
        rows = []
        ok = True

        for i in range(n):
            try:
                # 입력 받기 — EOF/Ctrl+C는 그대로 전파해서 main에서 처리
                line = input(f"  {label} row {i + 1}: ")
            except EOFError:
                # 표준입력이 끊기면 더 이상 진행 불가 → 호출자에게 알린다.
                raise

            tokens = line.split()
            if len(tokens) != n:
                print(f"  ! 열 개수가 {n}이 아닙니다 (입력: {len(tokens)}). 다시 입력해주세요.")
                ok = False
                break

            try:
                # int 우선 시도, 실패 시 float — 점수 계산은 어차피 수치만 필요
                row = [float(t) for t in tokens]
            except ValueError as e:
                print(f"  ! 숫자 파싱 실패: {e}. 다시 입력해주세요.")
                ok = False
                break

            rows.append(row)

        if ok and len(rows) == n:
            return rows
        # 실패 시 처음부터 다시 받는다 — 사용자가 어디서 잘못했는지 명확히 보임


def _benchmark_once(A, B, repeats=10):
    """동일한 (A, B) 입력에 대해 mac_2d를 repeats번 실행하고 평균 시간(ms)을 반환한다.

    Args:
        A, B: 같은 크기의 2차원 리스트
        repeats: 반복 횟수 (기본 10)

    Returns:
        tuple[float, float]: (마지막 결과값, 평균 실행 시간 ms)
    """
    # perf_counter는 단조 증가 고해상도 타이머 — 시간 측정에 권장
    start = time.perf_counter()
    result = 0
    for _ in range(repeats):
        result = mac_2d(A, B)
    elapsed = time.perf_counter() - start

    avg_ms = (elapsed / repeats) * 1000.0
    return result, avg_ms


def run():
    """모드 1의 기본 진입점 — 과제 필수 사양인 3×3 고정 입력."""
    print("\n=== 모드 1: 사용자 입력 (3×3) ===")
    n = 3

    # 두 필터와 패턴을 차례로 입력 받는다.
    A = _read_grid("필터 A", n)
    B = _read_grid("필터 B", n)
    P = _read_grid("패턴", n)

    _judge_and_print(A, B, P, "필터 A", "필터 B")


def _judge_and_print(A, B, P, label_a, label_b):
    """공용 결과 출력 헬퍼.

    필터 A/B 와 패턴 P 가 모두 준비된 상태에서 호출된다.
    두 진입점(run / run_with_filters) 모두 이 함수를 거쳐 출력 형식이 통일된다.
    """
    # 1) 각 필터와 패턴의 MAC 점수 — 10회 평균 시간도 함께 측정
    score_a, avg_a_ms = _benchmark_once(A, P, repeats=10)
    score_b, avg_b_ms = _benchmark_once(B, P, repeats=10)

    # 2) 결과 출력
    print("\n--- 결과 ---")
    print(f"{label_a} 점수: {score_a}")
    print(f"{label_b} 점수: {score_b}")

    # 3) epsilon 기반 동점 처리
    diff = score_a - score_b
    if abs(diff) < EPSILON:
        verdict = "UNDECIDED (판정 불가, 두 점수가 거의 동일)"
    elif diff > 0:
        verdict = f"{label_a} 와 더 닮음"
    else:
        verdict = f"{label_b} 와 더 닮음"
    print(f"판정: {verdict}")

    # 4) 평균 연산 시간 (10회 평균)
    print(f"평균 연산 시간(10회): {label_a}={avg_a_ms:.6f} ms, {label_b}={avg_b_ms:.6f} ms")


def run_with_filters(A, B, n, label_a="Cross", label_b="X"):
    """보너스 2 연동: 필터 A/B 가 이미 주어진 상태에서 패턴만 입력 받는다.

    main.py 의 메뉴 5번(패턴 생성기)에서 호출된다. 사용자가 N 을 골라
    pattern_gen 으로 Cross/X 를 만든 뒤, 그것을 필터로 그대로 넘겨주는 흐름.

    Args:
        A: 필터 A (보통 Cross). N×N 2차원 리스트.
        B: 필터 B (보통 X). N×N 2차원 리스트.
        n: 격자 크기. _read_grid 에 그대로 전달된다.
        label_a, label_b: 결과 출력에 사용할 필터 이름.
    """
    print(f"\n=== 모드 1 (필터 사전 제공, N={n}) ===")
    print(f"필터 A = {label_a}, 필터 B = {label_b} (자동 생성된 N×N 패턴)")

    # 사용자는 패턴만 입력하면 된다.
    P = _read_grid("패턴", n)

    _judge_and_print(A, B, P, label_a, label_b)
