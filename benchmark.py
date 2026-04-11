# benchmark.py
# ─────────────────────────────────────────────────────────────────────────────
# 성능 측정 모듈.
#
# 각 크기(3×3, 5×5, 13×13, 25×25)에 대해 MAC 연산 평균 시간(ms)을 측정한다.
# I/O 시간(패턴 생성/평탄화/패킹)은 측정 구간 밖으로 빼고, 함수 호출 구간만 잰다.
#
# 출력은 두 가지:
#   1) 현재 선택된 MAC 버전으로의 측정 표 (요구사항: 10회 평균)
#   2) 세 버전(baseline / sumprod / bitwise) × (1D / 2D) 의 비교 표
#      - 보너스 1(1D vs 2D)도 여기에 포함된다.
#
# 보다 안정적인 비교를 원하면 BENCHMARK_REPEATS 를 키우면 된다.
# 과제 요구는 10회이므로 기본값은 10으로 둔다.
# ─────────────────────────────────────────────────────────────────────────────

import time

import mac
from mac import flatten, mac_2d_with, mac_1d_with, VERSIONS, pack_grid, mac_packed
from pattern_gen import make_cross, make_x


# 측정에 사용할 격자 크기 — 과제에서 요구하는 4종
SIZES = (3, 5, 13, 25)

# 기본 반복 횟수 (요구사항: 10회). 비교 표는 좀 더 많이 돌려 안정화한다.
REPEATS = 10
COMPARE_REPEATS = 200


def _measure(fn, args, repeats):
    """fn(*args)를 repeats번 호출하고 평균 시간(ms)을 반환한다."""
    start = time.perf_counter()
    for _ in range(repeats):
        fn(*args)
    elapsed = time.perf_counter() - start
    return (elapsed / repeats) * 1000.0


def _print_main_table(results, current_version):
    """과제 요구 형식의 메인 표 출력 (현재 선택된 버전 기준)."""
    print(f"\n=== 성능 분석 (MAC 연산 평균 시간 - 현재 버전: {current_version}) ===")
    print(f"{'크기':>6} | {'평균 시간(ms)':>16} | {'연산 횟수(N²)':>14}")
    print("-" * 46)
    for n in SIZES:
        ms = results[n]
        print(f"{f'{n}x{n}':>6} | {ms:>16.6f} | {n * n:>14}")


def _print_compare_table(rows):
    """버전 비교 표 출력.

    rows: list of (n, baseline, sumprod, bitwise_per_call, bitwise_prepacked)
    각 값은 평균 ms (2D 기준).
    """
    print("\n=== 버전 비교 (2D MAC 평균 ms, 괄호 = baseline 대비 속도배) ===")
    print("(bitwise per-call: 매 호출마다 패킹, bitwise pre-packed: 패킹을 측정 밖에서 1회)")
    header = (
        f"{'크기':>6} | "
        f"{'baseline':>13} | "
        f"{'sumprod':>16} | "
        f"{'bitwise(per-call)':>20} | "
        f"{'bitwise(pre-packed)':>22}"
    )
    print(header)
    print("-" * len(header))

    for row in rows:
        n, base, sp, bw_pc, bw_pp = row

        def fmt(t, base_t):
            # baseline 대비 속도 배수 — 0 보호
            speedup = (base_t / t) if t > 0 else float("inf")
            return f"{t:>10.6f}({speedup:>5.1f}x)"

        print(
            f"{f'{n}x{n}':>6} | "
            f"{base:>13.6f} | "
            f"{fmt(sp, base):>16} | "
            f"{fmt(bw_pc, base):>20} | "
            f"{fmt(bw_pp, base):>22}"
        )


def run_for_size(n, repeats=REPEATS):
    """단일 크기 N 에 대해 현재 버전 MAC 평균 시간(ms)을 측정·출력한다.

    main.py 의 메뉴 5번(패턴 생성기)에서 "이 N 으로 한 번 측정해보기" 옵션으로
    호출된다. SIZES 고정 표가 아니라 사용자가 입력한 임의의 N 을 지원한다.

    Args:
        n: 격자 크기 (양의 정수)
        repeats: 반복 횟수 (기본 REPEATS)
    """
    if n < 1:
        print(f"[!] N 은 1 이상이어야 합니다: n={n}")
        return

    current = mac.get_version()
    cross = make_cross(n)
    x = make_x(n)

    # 측정 — 메인 표와 동일한 _measure 호출
    avg_ms = _measure(mac_2d_with, (current, cross, x), repeats=repeats)

    print(f"\n=== 단일 N 벤치마크 (N={n}, 버전={current}, {repeats}회 평균) ===")
    print(f"  평균 시간(ms) : {avg_ms:.6f}")
    print(f"  연산 횟수(N²): {n * n}")


def run():
    """벤치마크 진입점. main.py 또는 직접 실행 시 호출된다."""
    current = mac.get_version()

    # ───────── (A) 과제 요구 형식: 현재 선택 버전으로 10회 평균 측정 ──────────
    main_results = {}
    for n in SIZES:
        cross = make_cross(n)
        x = make_x(n)
        # 현재 버전에 해당하는 함수를 직접 호출 — set_version 부수효과 없음
        main_results[n] = _measure(
            mac_2d_with, (current, cross, x), repeats=REPEATS
        )
    _print_main_table(main_results, current)

    # ───────── (B) 4가지 케이스 비교 (2D 기준) ─────────────────────────────
    # baseline / sumprod / bitwise(per-call) / bitwise(pre-packed) 를 비교한다.
    # 보너스 1(1D vs 2D)은 별도 작은 표로 따로 출력한다.
    rows = []
    for n in SIZES:
        cross = make_cross(n)
        x = make_x(n)

        # baseline / sumprod / bitwise(per-call) — 매 호출이 격자를 새로 처리
        base = _measure(mac_2d_with, ("baseline", cross, x), COMPARE_REPEATS)
        sp   = _measure(mac_2d_with, ("sumprod",  cross, x), COMPARE_REPEATS)
        bw_pc = _measure(mac_2d_with, ("bitwise", cross, x), COMPARE_REPEATS)

        # bitwise(pre-packed) — 패킹은 측정 구간 밖에서 1번만
        cross_pk = pack_grid(cross)
        x_pk = pack_grid(x)
        bw_pp = _measure(mac_packed, (cross_pk, x_pk), COMPARE_REPEATS)

        rows.append((n, base, sp, bw_pc, bw_pp))

    _print_compare_table(rows)

    # ───────── (C) 보너스 1: 같은 버전에서 1D vs 2D ─────────────────────────
    print("\n--- 보너스 1: 1D vs 2D (sumprod 버전 기준) ---")
    print(f"{'크기':>6} | {'2D ms':>12} | {'1D ms':>12} | {'1D 속도배':>10}")
    print("-" * 50)
    for n in SIZES:
        cross = make_cross(n)
        x = make_x(n)
        cross_flat = flatten(cross)
        x_flat = flatten(x)
        ms2 = _measure(mac_2d_with, ("sumprod", cross, x), COMPARE_REPEATS)
        ms1 = _measure(mac_1d_with, ("sumprod", cross_flat, x_flat), COMPARE_REPEATS)
        speedup = (ms2 / ms1) if ms1 > 0 else float("inf")
        print(f"{f'{n}x{n}':>6} | {ms2:>12.6f} | {ms1:>12.6f} | {speedup:>9.2f}x")

    # 결과 정합성 sanity check — 모든 버전이 같은 값을 내야 한다.
    print("\n--- 결과 정합성 (한 케이스 샘플) ---")
    n = 13
    cross = make_cross(n)
    x = make_x(n)
    for v in VERSIONS:
        val = mac_2d_with(v, cross, x)
        print(f"  {v:>9} : mac_2d({n}x{n}, Cross, X) = {val}")

    return {"main": main_results, "compare": rows}


if __name__ == "__main__":
    # 모듈 단독 실행 지원 — 디버깅 시 편리
    run()
