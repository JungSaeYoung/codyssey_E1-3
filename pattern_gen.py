# pattern_gen.py
# ─────────────────────────────────────────────────────────────────────────────
# 보너스 2: 임의 크기(N×N)의 Cross / X 패턴을 자동으로 생성하는 모듈.
#
#   - Cross(+) 패턴: 가운데 행과 가운데 열이 1, 그 외는 0
#   - X        패턴: 두 대각선이 1, 그 외는 0
#
# 짝수 크기에서도 동작하도록 작성했지만, MAC 과제 특성상 보통 홀수 N을 사용한다.
# 모드 1과 benchmark.py에서 재활용한다.
# ─────────────────────────────────────────────────────────────────────────────


def make_cross(n):
    """N×N Cross(+) 패턴을 생성한다.

    Args:
        n: 패턴 크기 (정수, n >= 1)

    Returns:
        list[list[int]]: N×N 십자가 패턴

    Raises:
        ValueError: n이 1 미만인 경우.
    """
    if n < 1:
        raise ValueError(f"패턴 크기는 1 이상이어야 합니다: n={n}")

    # 짝수일 경우 가운데가 두 줄이 되므로, 두 줄 모두를 1로 채운다.
    mid = n // 2

    # 0으로 채워진 N×N 격자를 먼저 만들고, 가운데 행/열만 1로 덮어쓴다.
    grid = [[0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            on_mid_row = (i == mid) or (n % 2 == 0 and i == mid - 1)
            on_mid_col = (j == mid) or (n % 2 == 0 and j == mid - 1)
            if on_mid_row or on_mid_col:
                grid[i][j] = 1

    return grid


def make_x(n):
    """N×N X 패턴을 생성한다.

    Args:
        n: 패턴 크기 (정수, n >= 1)

    Returns:
        list[list[int]]: N×N X 패턴
    """
    if n < 1:
        raise ValueError(f"패턴 크기는 1 이상이어야 합니다: n={n}")

    grid = [[0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        # 주 대각선(↘) 위치 — i == j
        grid[i][i] = 1
        # 반대각선(↙) 위치 — i + j == n - 1
        grid[i][n - 1 - i] = 1

    return grid


def render(grid):
    """디버깅용으로 격자를 사람이 읽기 쉬운 문자열로 변환한다.

    1 -> '#', 0 -> '.' 로 시각화한다(콘솔 호환을 위해 ASCII 사용).

    Args:
        grid: N×N 2차원 리스트

    Returns:
        str: 줄바꿈 포함 시각화 문자열
    """
    lines = []
    for row in grid:
        lines.append(" ".join("#" if v else "." for v in row))
    return "\n".join(lines)
