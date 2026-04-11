# mac.py
# ─────────────────────────────────────────────────────────────────────────────
# MAC(Multiply-Accumulate) 연산의 핵심 로직 모듈.
#
#   result = Σ A[i][j] * B[i][j]   (i, j ∈ [0, N))
#
# 외부 라이브러리는 사용하지 않는다(stdlib 만 허용).
#
# 이 모듈은 동일한 MAC 결과를 내는 세 가지 "구현 버전"을 제공한다.
# 모드(mode1/mode2)와 벤치마크는 모두 dispatch 함수 mac_2d / mac_1d 를 통해
# 호출하므로, 사용자가 set_version() 으로 버전만 바꿔주면 그 이후의 모든 연산이
# 자동으로 새 구현을 사용한다.
#
#   ┌────────────┬─────────────────────────────┬─────────────────────────────┐
#   │ 버전        │ 알고리즘                     │ 비고                         │
#   ├────────────┼─────────────────────────────┼─────────────────────────────┤
#   │ baseline   │ 순수 파이썬 이중/단일 for문   │ 과제 필수 구현 (참고용 기준) │
#   │ sumprod    │ math.sumprod (C-level)       │ Python 3.12+, 거의 한 줄    │
#   │ bitwise    │ 정수 패킹 + AND + bit_count  │ 0/1 입력 한정, 압도적 속도   │
#   └────────────┴─────────────────────────────┴─────────────────────────────┘
# ─────────────────────────────────────────────────────────────────────────────

import math
from operator import mul


# ───────────────────────────── 공용 검증 헬퍼 ────────────────────────────────
def _validate_2d(A, B):
    """두 2차원 배열이 같은 N×N 형태인지 확인하고, N을 반환한다.

    모든 버전(baseline/sumprod/bitwise)이 호출 전에 공유하는 안전망.

    Raises:
        ValueError: 빈 배열, 행 수 불일치, 비정사각, 열 수 불일치.
    """
    if not A or not B:
        raise ValueError("입력 배열이 비어 있습니다.")

    n = len(A)
    if len(B) != n:
        raise ValueError(f"행 개수 불일치: len(A)={n}, len(B)={len(B)}")

    for i in range(n):
        if len(A[i]) != n or len(B[i]) != n:
            raise ValueError(
                f"행 길이 불일치(또는 비정사각): row {i} → "
                f"|A[{i}]|={len(A[i])}, |B[{i}]|={len(B[i])}, N={n}"
            )
    return n


def _validate_1d(a, b):
    """두 1차원 배열의 길이가 같은지 확인."""
    if len(a) != len(b):
        raise ValueError(f"길이 불일치: len(a)={len(a)}, len(b)={len(b)}")


# ────────────────────────── (1) baseline 구현 ────────────────────────────────
# 과제 필수 요구 — 외부 함수를 일절 쓰지 않고 반복문만으로 누산.
# 비교 기준선이며, 알고리즘의 의미를 가장 직설적으로 보여준다.

def _mac_2d_baseline(A, B):
    """순수 파이썬 이중 for-loop 으로 MAC 을 계산한다(baseline)."""
    n = _validate_2d(A, B)

    # 누산기(accumulator) — MAC 의 'A'(Accumulate)에 해당
    total = 0
    for i in range(n):
        row_a = A[i]
        row_b = B[i]
        for j in range(n):
            # 핵심 1줄: 곱하고 누산
            total += row_a[j] * row_b[j]
    return total


def _mac_1d_baseline(a, b):
    """1차원 평탄화 배열에 대한 baseline 단일 for-loop 구현."""
    _validate_1d(a, b)
    total = 0
    for k in range(len(a)):
        total += a[k] * b[k]
    return total


# ────────────────────────── (2) sumprod 구현 ─────────────────────────────────
# Python 3.12 부터 도입된 math.sumprod 를 사용한다.
# C 레벨 단일 루프이므로 baseline 대비 수 배 빠르다.
# pyproject.toml 의 requires-python = ">=3.12" 가 보장해주므로 안전하다.

def _mac_2d_sumprod(A, B):
    """행 단위로 math.sumprod 를 호출하고 그 결과를 합산한다."""
    _validate_2d(A, B)
    # zip 으로 인덱싱(row[j])을 제거 → 추가 오버헤드 절감
    return sum(math.sumprod(ra, rb) for ra, rb in zip(A, B))


def _mac_1d_sumprod(a, b):
    """1차원에서는 sumprod 한 번 호출이면 끝."""
    _validate_1d(a, b)
    return math.sumprod(a, b)


# 참고: sumprod 가 없는 환경(<3.12)을 위한 차선책 — sum + map(mul, ...) 패턴.
# 현재 dispatch 에 등록되진 않지만 학습용으로 남겨둔다.
def _mac_2d_mapmul(A, B):
    """sum(map(operator.mul, ...)) 패턴 — sumprod 가 없을 때의 대안."""
    _validate_2d(A, B)
    return sum(sum(map(mul, ra, rb)) for ra, rb in zip(A, B))


# ────────────────────────── (3) bitwise 구현 ─────────────────────────────────
# 입력이 0/1 만으로 구성된 경우(이 과제의 주된 시나리오), MAC 은 단순히
# "두 격자에서 동시에 1인 셀의 개수" 와 같다. 그래서:
#   1) 격자를 단일 정수로 패킹  (행 우선, MSB 부터)
#   2) AND
#   3) bit_count() 로 1의 개수 세기
# 모두 CPython 내부 C 코드이므로 속도가 압도적이다.
#
# 입력에 0/1 외 값이 섞여 있으면 sumprod 로 자동 폴백한다 — 사용자가
# 어떤 모드에서든 안전하게 쓸 수 있도록 하기 위함.

def pack_grid(grid):
    """N×N 0/1 격자를 단일 정수로 패킹한다(행 우선, MSB 부터).

    예) [[1,0],[0,1]] → 0b1001 = 9
    """
    bits = 0
    for row in grid:
        for v in row:
            bits = (bits << 1) | (1 if v else 0)
    return bits


def _is_binary_grid(grid):
    """격자의 모든 원소가 0 또는 1 인지 확인.

    bitwise 경로 적용 가능 여부 판단에만 쓰이므로, True/False 만 빠르게 반환.
    """
    for row in grid:
        for v in row:
            # 정수 0/1 뿐 아니라 0.0/1.0 같은 부동소수 표현도 허용
            if v != 0 and v != 1:
                return False
    return True


def _mac_2d_bitwise(A, B):
    """0/1 입력에 한정해 비트 트릭으로 MAC 을 계산한다.

    0/1 이 아닌 값이 한 셀이라도 있으면 sumprod 로 폴백한다.
    """
    _validate_2d(A, B)

    # 0/1 만 들어 있는지 확인 — 아니라면 sumprod 경로로 자동 위임
    if not (_is_binary_grid(A) and _is_binary_grid(B)):
        return _mac_2d_sumprod(A, B)

    # 두 격자를 정수로 패킹 → AND → 1의 개수 세기
    pa = pack_grid(A)
    pb = pack_grid(B)
    # int.bit_count() 는 Python 3.10+ 의 C 레벨 popcount
    return (pa & pb).bit_count()


def mac_packed(pa, pb):
    """이미 pack_grid() 로 패킹된 두 정수의 MAC.

    bitwise 트릭의 핵심 부분만 떼낸 함수.
    호출자가 필터처럼 재사용되는 격자를 미리 패킹해두면, 매 호출마다
    드는 패킹 비용을 한 번만 치를 수 있다 → 진짜 속도가 나오는 경로.

    Args:
        pa: pack_grid(A) 결과
        pb: pack_grid(B) 결과

    Returns:
        int: 두 격자에서 동시에 1 인 셀의 개수
    """
    # AND 후 popcount — 둘 다 CPython 내부 C 코드라 매우 빠르다.
    return (pa & pb).bit_count()


def _mac_1d_bitwise(a, b):
    """1차원 0/1 리스트에 대한 비트 트릭 MAC. 비-0/1 값이면 sumprod 로 폴백."""
    _validate_1d(a, b)

    # 1차원 빠른 검증
    for v in a:
        if v != 0 and v != 1:
            return _mac_1d_sumprod(a, b)
    for v in b:
        if v != 0 and v != 1:
            return _mac_1d_sumprod(a, b)

    # 패킹 후 동일한 트릭
    pa = 0
    for v in a:
        pa = (pa << 1) | (1 if v else 0)
    pb = 0
    for v in b:
        pb = (pb << 1) | (1 if v else 0)
    return (pa & pb).bit_count()


# ────────────────────────── 공용 유틸리티 ────────────────────────────────────
def flatten(M):
    """N×N 2차원 배열을 길이 N²의 1차원 리스트로 평탄화한다(보너스 1).

    리스트 컴프리헨션은 일반 for-loop 보다 빠른 편이라 평탄화에 적합하다.
    """
    return [M[i][j] for i in range(len(M)) for j in range(len(M[i]))]


# ────────────────────────── 버전 dispatch ────────────────────────────────────
# 사용 가능한 버전 목록 (UI/검증에 사용)
VERSIONS = ("baseline", "sumprod", "bitwise")

# 사용자 대상 짧은 설명 — main.py 메뉴에서 그대로 보여준다.
VERSION_DESCRIPTIONS = {
    "baseline": "순수 파이썬 for-loop (과제 필수 구현, 기준선)",
    "sumprod":  "math.sumprod 사용 (C-level 루프, 3~4배 빠름)",
    "bitwise":  "정수 패킹 + bit_count (0/1 한정, 매우 빠름·아니면 sumprod 폴백)",
}

# 2D / 1D 각각의 dispatch 표
_DISPATCH_2D = {
    "baseline": _mac_2d_baseline,
    "sumprod":  _mac_2d_sumprod,
    "bitwise":  _mac_2d_bitwise,
}
_DISPATCH_1D = {
    "baseline": _mac_1d_baseline,
    "sumprod":  _mac_1d_sumprod,
    "bitwise":  _mac_1d_bitwise,
}

# 현재 선택된 버전 — 모듈 전역 상태. 기본값은 과제 필수 구현인 baseline.
_current_version = "baseline"


def set_version(name):
    """현재 사용 중인 MAC 구현 버전을 변경한다.

    Args:
        name: 'baseline', 'sumprod', 'bitwise' 중 하나

    Raises:
        ValueError: 알 수 없는 버전 이름.
    """
    global _current_version
    if name not in VERSIONS:
        raise ValueError(
            f"알 수 없는 MAC 버전: {name!r} (가능: {', '.join(VERSIONS)})"
        )
    _current_version = name


def get_version():
    """현재 선택된 MAC 구현 버전 이름을 반환한다."""
    return _current_version


def mac_2d(A, B):
    """현재 선택된 버전으로 2차원 MAC 을 계산한다.

    mode1/mode2/benchmark 모두 이 함수를 호출하므로, 버전을 바꾸면
    이후의 모든 호출이 자동으로 새 구현을 사용한다.
    """
    return _DISPATCH_2D[_current_version](A, B)


def mac_1d(a, b):
    """현재 선택된 버전으로 1차원 MAC 을 계산한다."""
    return _DISPATCH_1D[_current_version](a, b)


# ───────── 벤치마크 등에서 특정 버전을 직접 호출하기 위한 공개 API ──────────
# (set_version 으로 전역 상태를 바꾸지 않고도 특정 버전을 골라 호출할 수 있게)

def mac_2d_with(version, A, B):
    """version 이름으로 2D MAC 함수를 골라 직접 호출."""
    if version not in _DISPATCH_2D:
        raise ValueError(f"알 수 없는 MAC 버전: {version!r}")
    return _DISPATCH_2D[version](A, B)


def mac_1d_with(version, a, b):
    """version 이름으로 1D MAC 함수를 골라 직접 호출."""
    if version not in _DISPATCH_1D:
        raise ValueError(f"알 수 없는 MAC 버전: {version!r}")
    return _DISPATCH_1D[version](a, b)
