# mode2.py
# ─────────────────────────────────────────────────────────────────────────────
# 모드 2: data.json 에 있는 패턴들을 일괄 분석한다.
#
# 흐름:
#   1. data.json 로드
#   2. size_N 별 (Cross/X) 필터 추출
#   3. 패턴 키('size_N_idx') 들을 순회
#   4. 패턴 크기 N에 해당하는 size_N 필터 자동 선택
#   5. 필터/패턴 크기 불일치 시 FAIL 처리(중단 금지)
#   6. Cross 점수, X 점수, 판정(Cross/X/UNDECIDED) 출력
#   7. 판정과 expected 비교 → PASS/FAIL
#   8. 마지막에 전체/통과/실패 개수와 실패 사유를 요약
# ─────────────────────────────────────────────────────────────────────────────

from data_loader import load_data, load_filters, load_patterns
from mac import mac_2d


# 동점 판정 임계값 — mode1과 동일하게 1e-9 사용
EPSILON = 1e-9


def _verdict(score_cross, score_x):
    """두 점수로부터 'Cross'/'X'/'UNDECIDED' 판정을 만든다."""
    diff = score_cross - score_x
    if abs(diff) < EPSILON:
        return "UNDECIDED"
    return "Cross" if diff > 0 else "X"


def _validate_square(grid, expected_n):
    """grid가 정확히 expected_n × expected_n 형태인지 확인한다.

    Returns:
        (bool, str): (정상 여부, 사유 문자열)
    """
    if not isinstance(grid, list) or len(grid) != expected_n:
        return False, f"행 수 불일치 (필요 {expected_n}, 실제 {len(grid) if isinstance(grid, list) else 'N/A'})"
    for i, row in enumerate(grid):
        if not isinstance(row, list) or len(row) != expected_n:
            return False, f"row {i} 열 수 불일치 (필요 {expected_n}, 실제 {len(row) if isinstance(row, list) else 'N/A'})"
    return True, ""


def run(path="data.json"):
    """모드 2 진입점. main.py 에서 호출된다."""
    print(f"\n=== 모드 2: {path} 분석 ===")

    # 1) JSON 로드 — 파일 자체가 없거나 깨져 있으면 사용자에게 알리고 종료
    try:
        data = load_data(path)
    except FileNotFoundError:
        print(f"[ERROR] '{path}' 파일을 찾을 수 없습니다. main.py와 같은 폴더에 두세요.")
        return
    except Exception as e:
        print(f"[ERROR] '{path}' 로드 실패: {e}")
        return

    # 2) 필터 / 패턴 로드 — 라벨 정규화는 load_patterns 안에서 이뤄진다.
    try:
        filters = load_filters(data)
        patterns = load_patterns(data)
    except Exception as e:
        print(f"[ERROR] 데이터 파싱 실패: {e}")
        return

    print(f"필터 사이즈: {sorted(filters.keys())}")
    print(f"분석할 패턴 수: {len(patterns)}")

    total = 0
    passed = 0
    failed = 0
    fail_records = []  # (id, 사유) 모음

    # 3) 패턴 순회 — 한 패턴이 죽어도 전체가 멈추지 않게 try/except 로 감싼다.
    for p in patterns:
        total += 1
        pid = p["id"]
        n = p["n"]
        grid = p["input"]
        expected = p["expected"]  # 이미 'Cross' / 'X' 로 정규화됨

        print(f"\n[{pid}] (N={n}, expected={expected})")

        # 3-1) 필터 존재 여부 — 없으면 FAIL
        if n not in filters:
            reason = f"size_{n} 필터가 정의되지 않음"
            print(f"  -> FAIL: {reason}")
            failed += 1
            fail_records.append((pid, reason))
            continue

        f_cross = filters[n]["Cross"]
        f_x = filters[n]["X"]

        # 3-2) 필터/패턴 크기 검증 — 셋 모두 N×N 이어야 한다.
        ok, reason = _validate_square(grid, n)
        if not ok:
            print(f"  -> FAIL: 패턴 크기 오류 ({reason})")
            failed += 1
            fail_records.append((pid, f"패턴 크기 오류 ({reason})"))
            continue

        ok, reason = _validate_square(f_cross, n)
        if not ok:
            print(f"  -> FAIL: Cross 필터 크기 오류 ({reason})")
            failed += 1
            fail_records.append((pid, f"Cross 필터 크기 오류 ({reason})"))
            continue

        ok, reason = _validate_square(f_x, n)
        if not ok:
            print(f"  -> FAIL: X 필터 크기 오류 ({reason})")
            failed += 1
            fail_records.append((pid, f"X 필터 크기 오류 ({reason})"))
            continue

        # 3-3) 실제 MAC 연산 — 여기까지 왔다면 안전하다.
        try:
            score_cross = mac_2d(f_cross, grid)
            score_x = mac_2d(f_x, grid)
        except Exception as e:
            # 안전망: 검증을 통과했더라도 산술/형 변환 오류가 날 수 있음
            print(f"  -> FAIL: MAC 연산 오류 ({e})")
            failed += 1
            fail_records.append((pid, f"MAC 연산 오류 ({e})"))
            continue

        verdict = _verdict(score_cross, score_x)

        print(f"  Cross 점수 = {score_cross}")
        print(f"  X     점수 = {score_x}")
        print(f"  판정       = {verdict}")

        # 3-4) PASS/FAIL 판정
        if verdict == expected:
            print(f"  -> PASS")
            passed += 1
        else:
            reason = f"판정({verdict}) != expected({expected})"
            print(f"  -> FAIL: {reason}")
            failed += 1
            fail_records.append((pid, reason))

    # 4) 마지막 요약
    print("\n--- 요약 ---")
    print(f"전체: {total}, 통과: {passed}, 실패: {failed}")
    if fail_records:
        print("실패 케이스:")
        for pid, reason in fail_records:
            print(f"  - {pid}: {reason}")
