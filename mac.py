# mac.py
# ─────────────────────────────────────────────────────────────────────────────
# MAC(Multiply-Accumulate) 연산의 핵심 로직을 모아둔 모듈.
#
#   result = Σ A[i][j] * B[i][j]   (i, j ∈ [0, N))
#
# 과제 요구사항: 외부 라이브러리(NumPy 등)를 사용하지 않고,
# 순수 파이썬 반복문만으로 MAC 연산을 구현한다.
# ─────────────────────────────────────────────────────────────────────────────


def mac_2d(A, B):
    """두 N×N 2차원 배열의 MAC(Multiply-Accumulate) 연산을 수행한다.

    Args:
        A: N×N 형태의 2차원 리스트 (필터 또는 패턴)
        B: N×N 형태의 2차원 리스트 (필터 또는 패턴)

    Returns:
        float: 위치별 곱의 총합 (Σ A[i][j] * B[i][j])

    Raises:
        ValueError: 두 배열의 크기가 일치하지 않거나 정사각형이 아닌 경우.
    """
    # 1) 빈 배열 방어 코드 — 입력 검증의 첫 단계
    if not A or not B:
        raise ValueError("입력 배열이 비어 있습니다.")

    # 2) 두 배열의 행 개수가 같은지 확인
    n = len(A)
    if len(B) != n:
        raise ValueError(
            f"행 개수 불일치: len(A)={n}, len(B)={len(B)}"
        )

    # 3) 누산기(accumulator) 초기화 — MAC의 'A'에 해당
    total = 0

    # 4) 모든 위치를 순회하며 곱셈 후 누산
    for i in range(n):
        row_a = A[i]
        row_b = B[i]

        # 정사각형(N×N)인지, 두 행의 길이가 같은지 확인
        if len(row_a) != n or len(row_b) != n:
            raise ValueError(
                f"행 길이 불일치(또는 비정사각): row {i} → "
                f"|A[{i}]|={len(row_a)}, |B[{i}]|={len(row_b)}, N={n}"
            )

        for j in range(n):
            # MAC 핵심 1줄: 곱한 뒤 누산기에 더한다.
            total += row_a[j] * row_b[j]

    return total


def flatten(M):
    """N×N 2차원 배열을 길이 N²의 1차원 리스트로 평탄화한다(보너스 1).

    1차원 배열은 캐시 친화적이며, 인덱스 계산을 단순화하여
    반복문 오버헤드를 약간 줄일 수 있다.

    Args:
        M: N×N 2차원 리스트

    Returns:
        list: 길이 N²의 1차원 리스트 (행 우선 순서)
    """
    # 리스트 컴프리헨션은 일반 for-loop 보다 빠른 편이라 평탄화에 적합하다.
    return [M[i][j] for i in range(len(M)) for j in range(len(M[i]))]


def mac_1d(a, b):
    """1차원 평탄화 배열에 대해 MAC 연산을 수행한다(보너스 1).

    Args:
        a: 길이 L의 1차원 리스트
        b: 길이 L의 1차원 리스트

    Returns:
        float: 위치별 곱의 합

    Raises:
        ValueError: 두 배열의 길이가 다를 경우.
    """
    if len(a) != len(b):
        raise ValueError(
            f"길이 불일치: len(a)={len(a)}, len(b)={len(b)}"
        )

    # 1차원이라 인덱싱이 단순해지고, 캐시 효율도 일반적으로 더 좋다.
    total = 0
    for k in range(len(a)):
        total += a[k] * b[k]
    return total
