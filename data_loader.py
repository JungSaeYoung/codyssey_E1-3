# data_loader.py
# ─────────────────────────────────────────────────────────────────────────────
# data.json 파일을 읽어 필터/패턴을 파이썬 객체로 가져오는 모듈.
#
# data.json 스펙(약속):
#   {
#     "size_5":  { "cross": [[..],..], "x": [[..],..] },
#     "size_13": { ... },
#     "size_25": { ... },
#     "size_5_1":  { "input": [[..]], "expected": "+" },
#     "size_13_3": { "input": [[..]], "expected": "x" },
#     ...
#   }
#
# 라벨 정규화 정책:
#   '+', 'cross', 'Cross', 'CROSS' -> 'Cross'
#   'x', 'X', 'XCROSS' 등          -> 'X'
# ─────────────────────────────────────────────────────────────────────────────

import json
import re


# 라벨 정규화에 쓰일 매핑 — 소문자 키를 사용해 대소문자 차이 흡수
_LABEL_MAP = {
    "+": "Cross",
    "cross": "Cross",
    "x": "X",
}


def normalize_label(label):
    """다양한 표기를 'Cross'/'X' 두 카테고리로 통일한다.

    Args:
        label: 사용자가 적은 라벨 문자열 (예: '+', 'x', 'Cross')

    Returns:
        str: 'Cross' 또는 'X'

    Raises:
        ValueError: 알 수 없는 라벨인 경우.
    """
    if label is None:
        raise ValueError("라벨이 None 입니다.")

    # 양 끝 공백 제거 후 소문자로 정규화 (대소문자 무시)
    key = str(label).strip().lower()

    if key in _LABEL_MAP:
        return _LABEL_MAP[key]

    raise ValueError(f"알 수 없는 라벨: {label!r}")


def load_data(path="data.json"):
    """data.json 전체를 dict로 읽어들인다.

    Args:
        path: 파일 경로 (기본: 'data.json')

    Returns:
        dict: JSON 루트 객체

    Raises:
        FileNotFoundError, json.JSONDecodeError 등 표준 예외 그대로 전파
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_filters(data):
    """JSON 데이터에서 size_N 별 (cross, x) 필터 묶음을 추출한다.

    Args:
        data: load_data()의 반환값(dict)

    Returns:
        dict[int, dict]: { N: {'Cross': grid, 'X': grid}, ... }
    """
    filters = {}

    # 'size_5', 'size_13' 처럼 'size_숫자' 형태(아래첨자가 더 없는)만 매칭
    # 패턴 키('size_5_1')와 구분하기 위해 정확히 'size_<digits>'만 허용
    size_re = re.compile(r"^size_(\d+)$")

    for key, value in data.items():
        m = size_re.match(key)
        if not m:
            continue
        n = int(m.group(1))

        # 구조 검증 — cross, x 키가 둘 다 있어야 한다
        if not isinstance(value, dict) or "cross" not in value or "x" not in value:
            raise ValueError(
                f"필터 항목 형식 오류: {key} (cross/x 키가 필요합니다)"
            )

        filters[n] = {
            "Cross": value["cross"],
            "X": value["x"],
        }

    return filters


def load_patterns(data):
    """JSON 데이터에서 검사 대상 패턴들을 (id, n, grid, expected_normalized) 로 추출한다.

    Args:
        data: load_data()의 반환값(dict)

    Returns:
        list[dict]: 각 항목은
            {
                'id':       원본 키 문자열 (예: 'size_5_1'),
                'n':        패턴 크기 (int),
                'input':    N×N 2차원 리스트,
                'expected': 정규화된 라벨 ('Cross' 또는 'X'),
                'expected_raw': 원본 라벨 문자열 (디버그용),
            }
    """
    patterns = []

    # 'size_<digits>_<digits>' 형식만 패턴으로 본다.
    pat_re = re.compile(r"^size_(\d+)_(\d+)$")

    for key, value in data.items():
        m = pat_re.match(key)
        if not m:
            continue

        n = int(m.group(1))

        # 구조 검증
        if not isinstance(value, dict) or "input" not in value or "expected" not in value:
            raise ValueError(
                f"패턴 항목 형식 오류: {key} (input/expected 키가 필요합니다)"
            )

        # 라벨 정규화 — 실패해도 한 항목만 영향받게 ValueError를 그대로 전파
        expected_norm = normalize_label(value["expected"])

        patterns.append({
            "id": key,
            "n": n,
            "input": value["input"],
            "expected": expected_norm,
            "expected_raw": value["expected"],
        })

    # 키 순서가 보장되지 않을 수 있으므로 id 기준으로 정렬해 출력 안정성 확보
    patterns.sort(key=lambda p: (p["n"], p["id"]))
    return patterns
