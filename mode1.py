# mode1.py
# ─────────────────────────────────────────────────────────────────────────────
# 모드 1: 사용자 입력 (3×3) 모드.
#
# 흐름:
#   1. 필터 A(3×3) 입력 받기
#   2. 필터 B(3×3) 입력 받기
#   3. 패턴 (3×3) 입력 받기
#   4. mac_2d 로 두 점수 산출
#   5. epsilon 동점 처리 → A승 / B승 / UNDECIDED 출력
#   6. 10회 평균 연산 시간(ms) 출력
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
    """모드 1의 진입점. main.py 에서 호출된다."""
    print("\n=== 모드 1: 사용자 입력 (3×3) ===")
    n = 3

    # 1) 두 필터와 패턴을 차례로 입력 받는다.
    A = _read_grid("필터 A", n)
    B = _read_grid("필터 B", n)
    P = _read_grid("패턴", n)

    # 2) 각 필터와 패턴의 MAC 점수 — 10회 평균 시간도 함께 측정
    score_a, avg_a_ms = _benchmark_once(A, P, repeats=10)
    score_b, avg_b_ms = _benchmark_once(B, P, repeats=10)

    # 3) 결과 출력
    print("\n--- 결과 ---")
    print(f"필터 A 점수: {score_a}")
    print(f"필터 B 점수: {score_b}")

    # 4) epsilon 기반 동점 처리
    diff = score_a - score_b
    if abs(diff) < EPSILON:
        verdict = "UNDECIDED (판정 불가, 두 점수가 거의 동일)"
    elif diff > 0:
        verdict = "필터 A 와 더 닮음"
    else:
        verdict = "필터 B 와 더 닮음"
    print(f"판정: {verdict}")

    # 5) 평균 연산 시간(10회 평균)
    print(f"평균 연산 시간(10회): A={avg_a_ms:.6f} ms, B={avg_b_ms:.6f} ms")
