# benchmark.py
# ─────────────────────────────────────────────────────────────────────────────
# 성능 측정 모듈.
#
# 각 크기(3×3, 5×5, 13×13, 25×25)에 대해 MAC 연산을 10회씩 반복하면서
# 평균 시간(ms)을 측정한다. I/O 시간은 측정 구간 밖으로 빼고, 함수 호출 구간만 잰다.
#
# 보너스 1: 1차원 평탄화 MAC(mac_1d)와 2차원 MAC(mac_2d)의 속도 비교도 함께 출력한다.
# ─────────────────────────────────────────────────────────────────────────────

import time

from mac import mac_2d, mac_1d, flatten
from pattern_gen import make_cross, make_x


# 측정에 사용할 격자 크기 — 과제에서 요구하는 4종
SIZES = (3, 5, 13, 25)

# 각 크기마다 반복 측정 횟수 (요구사항: 10회)
REPEATS = 10


def _measure(fn, args, repeats=REPEATS):
    """fn(*args)를 repeats번 호출하고 평균 시간(ms)을 반환한다.

    Args:
        fn: 측정 대상 함수
        args: 함수에 넘길 인자 튜플
        repeats: 반복 횟수

    Returns:
        float: 평균 실행 시간(ms)
    """
    # I/O는 측정 영역 바깥에서 미리 끝내고, 여기서는 순수 호출만 잰다.
    start = time.perf_counter()
    for _ in range(repeats):
        fn(*args)
    elapsed = time.perf_counter() - start
    return (elapsed / repeats) * 1000.0


def run():
    """벤치마크 진입점. main.py 또는 직접 실행 시 호출된다."""
    print("\n=== 성능 분석 (MAC 연산 평균 시간) ===")
    print(f"{'크기':>6} | {'평균 시간(ms)':>16} | {'연산 횟수(N²)':>14}")
    print("-" * 46)

    # 2D 결과를 모아두고, 마지막에 1D와 비교 표를 출력한다.
    results_2d = {}
    results_1d = {}

    for n in SIZES:
        # 1) 측정용 데이터 — 동일 조건이 되도록 Cross/X 패턴을 사용
        cross = make_cross(n)
        x = make_x(n)

        # 2) 2차원 MAC 평균 측정
        avg_ms_2d = _measure(mac_2d, (cross, x))
        results_2d[n] = avg_ms_2d

        # 3) 1차원 MAC 평균 측정 — flatten 시간은 측정 구간 바깥
        cross_flat = flatten(cross)
        x_flat = flatten(x)
        avg_ms_1d = _measure(mac_1d, (cross_flat, x_flat))
        results_1d[n] = avg_ms_1d

        # 4) 표 한 줄 출력 (2D 기준)
        print(f"{f'{n}x{n}':>6} | {avg_ms_2d:>16.6f} | {n * n:>14}")

    # 5) 보너스 1: 1차원 vs 2차원 비교 표
    print("\n--- 보너스 1: 1D vs 2D MAC 비교 ---")
    print(f"{'크기':>6} | {'2D ms':>14} | {'1D ms':>14} | {'속도 향상(배)':>14}")
    print("-" * 60)
    for n in SIZES:
        ms2 = results_2d[n]
        ms1 = results_1d[n]
        # 0으로 나눠지는 일을 방지 — 매우 작은 값일 때를 대비한 안전망
        speedup = (ms2 / ms1) if ms1 > 0 else float("inf")
        print(f"{f'{n}x{n}':>6} | {ms2:>14.6f} | {ms1:>14.6f} | {speedup:>13.2f}x")

    return {"2d": results_2d, "1d": results_1d}


if __name__ == "__main__":
    # 모듈 단독 실행 지원 — 디버깅 시 편리
    run()
