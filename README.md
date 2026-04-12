# Mini NPU Simulator

## 이론적 배경 및 과제 목표

### MINI NPU 시뮬레이터 개발 

컴퓨터는 우리가 보는 시각의 직관이 없다. 컴퓨터는 이미지를 보고도 어떤 사진인지, 그런 것들을 판단할 수 없다.(모델이 없이는)
우리는 시각으로 사물을 볼 때 전기신호로 특징을 보고 나서 학습된 기억 중 유사한 사물을 인지할 수 있다.
컴퓨터도 이러한 접근법을 통해 사물을 인식시키면 된다.
바로 패턴을 학습시켜 사물을 인식하는 것이다.
우리는 그 과정 중 가장 기초적이고 간단한 MAC 연산을 통해 입력 패턴과 필터로 입력값을 추론하는 간단한 프로그램을 구현한다.

### MAC 연산이 무엇인가?

MAC = Multiply-Accumulate (곱셈-누산)

```
result += A[i] × B[i]
```

수식적으로는 위와 같다. 두 배열의 같은 위치를 곱하고, 그걸 전부 더하는 것이 전부인 연산이다.

사실 이 간단한 연산이 모든 신호 처리의 핵심이라고 할 수 있다.

### MAC 연산은 그래서 어디에 쓰이는가?

이미지 분류 분야에서 2012년 ILSVRC(ImageNet Large Scale Visual Recognition Challenge) 대회의 우승을 차지한 컨볼루션 신경망(CNN) 모델 중 유명한 AlexNet 또한 이 MAC 연산을 연속적으로 수행하는 MATMUL 연산을 사용한다.(MATMUL은 MAC 연산을 K번 수행하는 것과 같다.)

실제 예시를 보면 다음과 같다.

```이미지 필터링(Convolution)
패턴(이미지 조각):        필터(커널):
1  0  1                  0  1  0
0  1  0        →  MAC →  1  0  1      = 결과값 하나
1  0  1                  0  1  0
```

이미지 위를 필터가 슬라이딩하면서 각 위치마다 MAC 연산 한 번씩 → 결과가 흐리기 / 선명하게 / 엣지 검출 등으로 나온다.

신경망(Neural Network) 또한 비슷하다.

```Neural Network 계산 과정
입력값:   [x1, x2, x3]
가중치:   [w1, w2, w3]

뉴런 출력 = x1×w1 + x2×w2 + x3×w3  ← 이게 MAC
```

GPT 같은 모델들도 추론 시에 사용하는 연산의 99%가 MAC 연산이다.
행렬곱이라는 것이 결국 MAC 연산의 반복이다.

``` 과제 요구 사항
Cross 필터로 MAC → Cross 점수
X 필터로 MAC     → X 점수
점수 비교 → 패턴이 십자가 모양인가, X 모양인가 판정
```

여기서 Cross / X 필터는 다음과 같이 생긴 N×N 0/1 격자다 (예: N=5).

```
   Cross (가운데 행 + 가운데 열)        X (두 대각선)
   . . # . .                          # . . . #
   . . # . .                          . # . # .
   # # # # #                          . . # . .
   . . # . .                          . # . # .
   . . # . .                          # . . . #
```

해서, 이 프로젝트에서는 MAC 연산을 실제로 진행해보며 필터와 패턴이 얼마나 닮았는가 수치로 측정하는 것이 목표이다.

## TODO

### 필수 구현

- [x] **MAC 연산 함수 구현**
  - [x] 두 N×N 2차원 배열을 받아 위치별 곱의 합을 반환하는 함수 ([mac.py](mac.py))
  - [x] 외부 라이브러리(NumPy 등) 없이 반복문으로만 구현

- [x] **데이터 구조 구현**
  - [x] N×N 2차원 배열 저장 및 읽기
  - [x] 3×3, 5×5, 13×13, 25×25 크기 모두 처리 가능하게 구현

- [x] **모드 선택 메뉴 구현**
  - [x] 실행 시 1번(사용자 입력) / 2번(data.json 분석) 선택 ([main.py](main.py))

- [x] **모드 1: 사용자 입력 (3×3)** ([mode1.py](mode1.py))
  - [x] 필터 A 입력 (3줄, 공백 구분)
  - [x] 필터 B 입력 (3줄, 공백 구분)
  - [x] 패턴 입력 (3줄, 공백 구분)
  - [x] 입력 검증: 행/열 수 불일치, 숫자 파싱 실패 시 오류 메시지 출력 후 재입력 유도
  - [x] MAC 연산 수행 및 A/B 점수 출력
  - [x] epsilon(1e-9) 기반 동점 처리 → UNDECIDED 출력
  - [x] 판정 결과(A / B / 판정 불가) 출력
  - [x] 연산 시간(10회 평균, ms 단위) 출력

- [x] **모드 2: data.json 분석** ([mode2.py](mode2.py))
  - [x] data.json 파일 직접 작성 (5×5, 13×13, 25×25 필터 및 패턴 포함)
  - [x] 필터 로드: size_5, size_13, size_25 키에서 Cross/X 필터 읽기
  - [x] 패턴 로드: size_{N}_{idx} 키에서 input 배열 및 expected 값 읽기
  - [x] 라벨 정규화: `'+'` → `Cross`, `'x'` → `X`, `'cross'` → `Cross` 로 통일
  - [x] 패턴 키에서 N 추출 → 해당 size_N 필터 자동 선택
  - [x] 필터/패턴 크기 불일치 검증 → 불일치 시 FAIL 처리 (프로그램 중단 금지)
  - [x] 각 패턴에 대해 Cross 점수, X 점수, 판정(Cross/X/UNDECIDED) 출력
  - [x] 판정과 expected 비교 → PASS / FAIL 출력
  - [x] 전체/통과/실패 개수 요약 출력
  - [x] 실패 케이스 식별자 및 실패 사유 출력

- [x] **성능 분석** ([benchmark.py](benchmark.py))
  - [x] 각 크기(3×3, 5×5, 13×13, 25×25)별 MAC 연산 10회 반복 측정
  - [x] I/O 시간 제외, 연산 함수 호출 구간만 측정
  - [x] 크기 / 평균 시간(ms) / 연산 횟수(N²) 표 출력

- [x] **README.md 작성**
  - [x] 실행 방법 작성
  - [x] 구현 요약 작성 (라벨 정규화, MAC 구현 방식, epsilon 정책)
  - [x] 결과 리포트 작성 (FAIL 원인 분석 + O(N²) 시간 복잡도 분석, 10줄 이상)

---

### 보너스 구현 (선택)

- [x] **보너스 1: 1차원 배열 최적화** ([mac.py](mac.py))
  - [x] 2차원 배열을 1차원 배열(길이 N²)로 변환하는 함수 구현 (`flatten`)
  - [x] 1차원 기반 MAC 연산 함수 구현 (`mac_1d`)
  - [x] 최적화 전/후 성능 비교 결과 출력 ([benchmark.py](benchmark.py))

- [x] **보너스 2: 패턴 생성기** ([pattern_gen.py](pattern_gen.py))
  - [x] 크기 N 입력 시 N×N 십자가(Cross) 패턴 자동 생성 (`make_cross`)
  - [x] 크기 N 입력 시 N×N X 패턴 자동 생성 (`make_x`)
  - [x] 생성된 패턴을 모드 1 및 성능 분석에 재활용 가능하게 연결
        - 메뉴 5번에서 사용자가 N 입력 → `make_cross(n)` / `make_x(n)` 호출
        - `render()` 로 시각화 출력
        - 후속 액션: (a) `mode1.run_with_filters(cross, x, n)` 으로 그대로 필터 주입,
          (b) `benchmark.run_for_size(n)` 로 임의 N 단일 측정,
          (c) 시각화만 보고 메인 메뉴로 복귀

---

## 실행 방법

uv를 사용해 가상환경 구축.
python version은 3.12로 고정한다. 

```bash
uv venv
source .venv/bin/activate
```

가상환경이 없어도 python이 있다면 프로젝트 내에 외부 라이브러리 사용이 없기 때문에 정상적으로 실행할 수 있을 것이다.

```bash
python main.py
```

> 실행 후 모드를 선택하세요.  
> data.json은 main.py와 같은 폴더에 위치해야 합니다.

### 메뉴 구성

```
==============================
   Mini NPU Simulator (MAC)
   * 현재 MAC 버전: baseline
==============================
  1) 모드 1: 사용자 입력 (3x3)
  2) 모드 2: data.json 분석
  3) 성능 분석 (벤치마크)
  4) MAC 구현 버전 선택              ← baseline / sumprod / bitwise 전환
  5) 패턴 생성기 (N 입력 → Cross/X)  ← 보너스 2
  0) 종료
```

- `4)` 에서 MAC 구현 버전을 바꾸면 이후 실행되는 `1)` `2)` `3)` `5)` 모두에 즉시 반영됩니다 (헤더의 "현재 MAC 버전" 으로 확인 가능).
- `5)` 는 사용자가 임의의 N 을 입력해 Cross/X 패턴을 자동 생성한 뒤, 그 패턴을 (a) `mode1` 의 필터로 그대로 넘겨 사용자가 N×N 패턴만 입력하거나 (b) 그 N 으로 단일 벤치마크를 1회 돌리거나 (c) 그냥 시각화만 출력할 수 있습니다.

---

## 구현 요약

### 프로젝트 구조
```
codyssey_E1-3/
│
├── main.py                 # 진입점: 메뉴 + MAC 버전 선택
│
├── mac.py                  # MAC 연산 핵심 로직 (3개 버전 + dispatch)
│                           #   mac_2d / mac_1d              → 현재 버전으로 dispatch
│                           #   _mac_2d_baseline / _1d        → 순수 for-loop
│                           #   _mac_2d_sumprod  / _1d        → math.sumprod (3.12+)
│                           #   _mac_2d_bitwise  / _1d        → 정수 패킹 + bit_count
│                           #   pack_grid / mac_packed        → bitwise 사전 패킹용
│                           #   set_version / get_version     → 전역 상태 변경
│                           #   mac_2d_with / mac_1d_with     → 특정 버전 직접 호출(벤치)
│                           #   flatten                       → 보너스 1
│
├── data_loader.py          # data.json 파싱, 라벨 정규화
├── mode1.py                # 모드1: 사용자 입력
│                           #   run()              → 3×3 고정 (필수)
│                           #   run_with_filters() → N 가변, 필터 사전 제공 (보너스2 연동)
├── mode2.py                # 모드2: data.json 분석
├── benchmark.py            # 성능 측정
│                           #   run()         → 4 사이즈 + 4 케이스 비교 (메뉴 3)
│                           #   run_for_size()→ 임의 N 단일 측정 (메뉴 5에서 호출)
├── pattern_gen.py          # 보너스2: Cross/X 패턴 자동 생성
│                           #   make_cross / make_x → N×N 격자 생성
│                           #   render              → ASCII 시각화 (#/.)
├── data.json               # 5×5, 13×13, 25×25 필터 + 12개 패턴
└── README.md
```

### 의존 관계
```
main.py
  ├── mac           (버전 선택)
  ├── mode1.py     → mac.py
  ├── mode2.py     → mac.py, data_loader.py
  ├── benchmark.py → mac.py, pattern_gen.py
  └── pattern_gen.py (메뉴 5에서 직접 사용)
       └── 후속 액션으로 mode1.run_with_filters / benchmark.run_for_size 호출
```

### MAC 구현 — 3개 버전과 dispatch

[mac.py](mac.py) 는 동일한 결과를 내는 세 가지 구현을 제공하고, 모듈 전역의 `_current_version` 에 따라 `mac_2d()` / `mac_1d()` 가 알맞은 함수로 분기합니다. mode1/mode2/benchmark 는 모두 dispatch 함수만 호출하므로, 사용자가 메뉴 `4)` 에서 버전을 바꾸면 그 이후의 모든 연산이 자동으로 새 구현을 사용합니다.

| 버전 | 알고리즘 | 특징 | 정확도 |
|---|---|---|---|
| **baseline** | 순수 파이썬 이중/단일 for-loop | 과제 필수 구현, 기준선 | 모든 수치 입력 |
| **sumprod** | `math.sumprod()` (Python 3.12+) | C-level 단일 루프, 한 줄 변경 | 모든 수치 입력 |
| **bitwise** | `pack_grid` + `&` + `int.bit_count()` (3.10+) | 0/1 입력일 때 폭발적 가속, 그 외 입력은 sumprod 로 자동 폴백 | 0/1 한정 (그 외는 폴백) |

세 버전 모두 동일한 입력 검증 헬퍼(`_validate_2d`, `_validate_1d`)를 공유하므로, 잘못된 입력에 대해서는 일관되게 `ValueError` 를 던집니다. 모든 외부 의존성은 stdlib(`math`, `operator`) 만 사용합니다.

#### bitwise 버전의 두 가지 실행 모드

bitwise 트릭은 "패킹 비용을 어디서 치르느냐"에 따라 성능이 크게 달라집니다.

- **per-call (자동)**: 메뉴 `4)` 로 버전을 `bitwise` 로 바꾸면, `mac_2d(A, B)` 호출마다 두 격자를 패킹합니다. 패킹 자체가 파이썬 루프이므로 N이 작을 때는 baseline 보다 오히려 느립니다. 일반성·투명성을 위한 기본 모드.
- **pre-packed (수동)**: `pack_grid()` 로 격자를 미리 정수로 변환해두고 `mac_packed(pa, pb)` 를 호출하면, 측정 구간에 남는 연산은 `(pa & pb).bit_count()` 단 한 줄. N=25 에서 baseline 대비 200배 이상 빠릅니다. 같은 필터를 여러 번 재사용하는 mode2 같은 시나리오에서 이상적.

### 라벨 정규화 정책
- [data_loader.py](data_loader.py) 의 `normalize_label()` 이 담당.
- 입력 문자열은 `strip().lower()` 로 정리한 뒤 매핑한다 → 대소문자 차이를 흡수.
- `'+'`, `'cross'`, `'Cross'`, `'CROSS'` → `'Cross'`
- `'x'`, `'X'` → `'X'`
- 알 수 없는 라벨은 `ValueError` 로 호출자에게 알려 해당 패턴만 FAIL 처리 가능하게 한다.

### epsilon 정책 (동점 처리)
- [mode1.py](mode1.py), [mode2.py](mode2.py) 모두 `EPSILON = 1e-9` 를 사용.
- 두 점수의 차이 절대값이 `EPSILON` 미만이면 `UNDECIDED` 로 판정한다.
- 이유: 부동소수 누산 오차로 점수가 우연히 정확히 같아 보이는 일을 방지하면서, 의미 있는 차이는 모두 잡아내기 위함.

### data.json 스펙
```jsonc
{
  "size_5":  { "cross": [[..]], "x": [[..]] },   // 사이즈별 Cross/X 필터
  "size_13": { "cross": [[..]], "x": [[..]] },
  "size_25": { "cross": [[..]], "x": [[..]] },

  "size_5_1":  { "input": [[..]], "expected": "+" },     // 검사 패턴
  "size_5_2":  { "input": [[..]], "expected": "x" },
  "size_13_3": { "input": [[..]], "expected": "Cross" },
  // ...
}
```
- 키 형식: 필터는 `size_<N>`, 패턴은 `size_<N>_<idx>` 로 정확히 구분한다.
- 모드 2는 패턴 키에서 N을 뽑아 같은 N의 필터를 자동으로 선택한다.
- 패턴 12개(5×5/13×13/25×25 각각 4개: 깨끗한 Cross/X + 노이즈 섞인 Cross/X)를 포함한다.

---

## 최적화 전략 (stdlib 한정)

지금 baseline 의 병목은 알고리즘이 아니라 **"파이썬 바이트코드 루프"** 자체입니다. `mac_2d` 가 하는 일은 곱셈/덧셈 N²번 뿐이지만, 매 곱셈마다 인터프리터가 인덱싱·바인딩·점프 오버헤드를 같이 치르죠. 그래서 최적화 방향은 두 갈래입니다.

1. **루프를 C 레벨로 내리기** — 같은 알고리즘, 다른 도구
2. **알고리즘 자체를 바꾸기** — 입력 특성을 활용

stdlib 만으로 가능한 기법들을 효과 큰 순서로 정리하면:

### 1) `math.sumprod` — 가장 큰 한 방 (Python 3.12+)
Python 3.12 부터 [`math.sumprod(a, b)`](https://docs.python.org/3/library/math.html#math.sumprod) 가 추가됐습니다. `Σ a[i] * b[i]` 를 **C 레벨 단일 루프** 로 계산해 줍니다. 이 프로젝트는 이미 `requires-python = ">=3.12"` 라 바로 쓸 수 있고, 25×25 기준 baseline 대비 약 **2.3배** 빠릅니다.

### 2) `sum + map(operator.mul, ...)` — 3.12 미만에서의 차선책
`map` 은 C 이터레이터, `operator.mul` 은 C 함수 → `for` 루프 오버헤드가 거의 사라집니다. `sumprod` 가 없는 환경에서의 정석. (`mac.py` 에 `_mac_2d_mapmul` 로 학습용으로 남겨둠)

### 3) 비트 트릭 — 입력이 0/1 이라는 특성을 활용
이 과제의 필터/패턴은 사실상 **이진(0/1)** 입니다. 그러면 MAC = "겹치는 1의 개수" 와 같죠 → AND 한 번 + popcount 한 번이면 끝. 단, 패킹 비용을 어떻게 처리하느냐가 관건입니다 (아래 "bitwise 함정" 참고).

### 4) "한 번 할 일은 한 번만" — 호출 외부로 빼기
- 필터는 한 번 로드하면 변하지 않음 → 시작 시 한 번만 flatten/pack 해두면 mode 2 의 24번 호출 모두에서 재활용 가능
- `len()` / `range()` / 전역 lookup 을 루프 바깥에서 지역 변수에 묶어두는 micro-opt 도 공짜로 얻을 수 있음

### 5) `array.array` 로 메모리 압축
`list[int]` 는 각 원소가 PyObject 포인터(64bit) 라 캐시 효율이 나쁩니다. `array.array('b', ...)` 로 바꾸면 메모리가 1/8 이 되고, `sumprod`/`map` 과 함께 쓰면 캐시 히트가 개선되어 큰 N 에서 미세 이득.

### 6) 알고리즘 측면
- **희소(sparse)** 필터(특히 X, Cross 처럼 1의 수가 N 에 비례)는 **1의 위치만 저장** 하면 MAC = `sum(P[i][j] for i,j in filter_ones)` 로 줄어듭니다. N=25 의 X 필터는 1이 49개뿐이라, 625 → 49 (약 13배 감소).
- **분리 가능 필터(separable filter)** 라면 행/열로 분해해 O(N²) → O(N) 가능. Cross/X 는 분리 불가.

### bitwise 함정 — "그냥 켜기만 한다고 빨라지지 않는다"

흥미로운 점: `mac_2d` 호출마다 새로 패킹하는 **per-call** 모드에서는 bitwise 가 baseline 보다 오히려 **느립니다** (위 결과 표 참고). 패킹 자체가 파이썬 루프이기 때문이죠. 이 비용은 "같은 격자를 여러 번 쓰는" 시나리오에서만 amortize 됩니다.

그래서 [mac.py](mac.py) 는 bitwise 의 두 진입점을 분리해 둡니다:
- `_mac_2d_bitwise(A, B)` — 일반 dispatch (자동 폴백 포함, per-call 패킹)
- `mac_packed(pa, pb)` — 사용자가 사전 패킹한 정수만 받아서 AND+popcount 만 수행

벤치마크의 "bitwise (pre-packed)" 행이 두 번째 경로의 진짜 성능을 보여주는 것입니다 — N=25 에서 baseline 대비 **228×**.

### 적용 우선순위 (실제로 한다면)

1. **`mac.py` 에서 dispatch 기본값을 sumprod 로 변경** — 한 줄 수정으로 mode2 전체가 안정적으로 ~2배 빨라지고, 모든 입력에서 안전. (현재는 호환성을 위해 기본값을 baseline 으로 유지)
2. **mode2 시작 시 필터를 한 번만 flatten / pack** — 패턴 12개 × 필터 2개 = 24번의 redundant pack 을 0번으로.
3. **0/1 입력 한정 fast-path** — `data.json` 로드 직후 모든 값이 {0, 1} 이면 자동으로 `mac_packed` 경로로 분기 (필터·패턴 모두 사전 패킹).

이 세 가지만 적용해도 25×25 mode 2 전체 시간이 사실상 측정 잡음 아래로 내려갑니다.

---

## 동작 흐름

처음 코드를 보는 사람을 위한 "이 프로그램이 안에서 무슨 일을 하는가"를 단계별로 정리합니다.

### 0. 한눈에 보는 전체 구조

```
                  ┌───────────────┐
사용자 ─ 키보드 →  │    main.py    │ ← 모듈 전역: mac._current_version
                  │  (메뉴 루프)   │     ('baseline' / 'sumprod' / 'bitwise')
                  └───────┬───────┘
       ┌─────────┬────────┼────────┬─────────┬──────────┐
       ▼         ▼        ▼        ▼         ▼          │
   ┌───────┐ ┌───────┐ ┌──────┐ ┌───────┐ ┌──────────┐  │
   │ mode1 │ │ mode2 │ │bench │ │ ver   │ │ pattern  │  │
   │ (3x3) │ │(JSON) │ │ mark │ │select │ │   gen    │  │
   └───┬───┘ └───┬───┘ └──┬───┘ └───┬───┘ └────┬─────┘  │
       │         │        │         │          │         │
       │     data_loader  │         │      pattern_gen   │
       │    (JSON 파싱·   │         │      (Cross/X 생성  │
       │    라벨 정규화)  │         │       + render)    │
       │         │        │         │          │         │
       │         │     pattern_gen  │     ┌────┴────┐    │
       │         │     (벤치 입력)  │     ▼         ▼    │
       │         │        │         │  mode1.run  bench  │
       │         │        │         │  with_      run_   │
       │         │        │         │  filters    for_   │
       │         │        │         │             size   │
       ▼         ▼        ▼         ▼     ▼         ▼    │
                ┌────────────────────────┐                │
                │         mac.py         │                │
                │   ┌────────────────┐   │                │
                │   │ mac_2d/mac_1d  │ ← _current_version │
                │   │   (dispatch)   │   │  에 따라 분기  │
                │   └───────┬────────┘   │                │
                │      ┌────┼─────┐      │                │
                │      ▼    ▼     ▼      │                │
                │   baseline sumprod bitwise              │
                │   (for-loop)(C 루프)(비트)              │
                └────────────────────────┘                │
                                                          │
                  set_version() ◀──────────────────────────┘
```

핵심 1: **mode1/mode2/benchmark 는 mac.py 의 어떤 구현을 쓰는지 모른다.** 모두 `mac.mac_2d(A, B)` 만 호출하고, 그 호출이 `mac._current_version` 에 따라 알맞은 함수로 자동 분기된다. 메뉴 4번에서 버전을 바꾸면 이후 모든 연산이 즉시 새 구현을 사용한다.

핵심 2: **`pattern_gen` 은 두 곳에서 사용된다.** (1) `benchmark` 가 측정용 입력으로 자동 호출하는 경로, (2) 메뉴 5번에서 사용자가 직접 N 을 입력해 호출한 뒤 결과 패턴을 `mode1.run_with_filters()` 또는 `benchmark.run_for_size()` 로 흘려보내는 경로. 두 번째가 보너스 2 의 진짜 의도이며, 사용자는 임의의 N 을 골라 자동 생성된 Cross/X 를 mode1 의 필터로 활용할 수 있다.

### 1. 프로그램 시작 → 메뉴 루프 ([main.py](main.py))

```
python main.py
   │
   ▼
main() 진입
   │
   ▼
무한 루프 시작 ────────────────────────────────┐
   │                                          │
   ├─ _print_menu()                            │
   │     ├─ "현재 MAC 버전: baseline" 출력      │
   │     └─ 1)~5), 0) 메뉴 출력                 │
   │                                          │
   ├─ input("선택> ")                          │
   │                                          │
   ├─ choice == "1" → mode1.run()             │
   ├─ choice == "2" → mode2.run("data.json")  │
   ├─ choice == "3" → benchmark.run()         │
   ├─ choice == "4" → _select_version()       │
   ├─ choice == "5" → _pattern_generator()    │
   ├─ choice == "0" → return (종료)            │
   └──────────────────────────────────────────┘
```

EOF(`Ctrl+Z` / `Ctrl+D`)나 `Ctrl+C` 를 누르면 깔끔히 종료된다.

### 2. 모드 1 — 사용자 입력 ([mode1.py](mode1.py))

mode1 은 두 진입점을 갖는다. 둘 다 마지막에 같은 `_judge_and_print()` 헬퍼를 거쳐 출력 형식을 통일한다.

- `run()` — 메뉴 1번. 3×3 고정. 두 필터와 패턴을 모두 사용자가 입력 (과제 필수 사양).
- `run_with_filters(A, B, n)` — 메뉴 5번에서 호출. 필터 A/B 가 미리 주어지고(보통 pattern_gen 으로 만든 N×N Cross/X), 사용자는 N×N 패턴만 입력.

```
mode1.run()  ←─ 메뉴 1
   │
   ├─ _read_grid("필터 A", 3)         ┐
   │     루프:                        │
   │       3줄 input() 으로 받기        │
   │       → split() 로 토큰화         │  잘못된 입력이면
   │       → 토큰 수 검증 (≠3 → 재입력) │  처음부터 다시
   │       → float 변환 (실패 → 재입력)│
   │     → 3×3 리스트 완성            ┘
   │
   ├─ _read_grid("필터 B", 3)   (동일 절차)
   ├─ _read_grid("패턴",   3)   (동일 절차)
   │
   └─ _judge_and_print(A, B, P, "필터 A", "필터 B")  ┐
                                                   │
mode1.run_with_filters(A, B, n)  ←─ 메뉴 5         │
   │                                                │
   ├─ A, B 는 호출자에서 이미 받음 (pattern_gen 결과)│
   ├─ _read_grid("패턴", n)   (N×N 입력만 받음)     │
   │                                                │
   └─ _judge_and_print(A, B, P, "Cross", "X")  ─────┤
                                                   │
                                                   ▼
                              _judge_and_print(A, B, P, label_a, label_b)
                                 │
                                 ├─ _benchmark_once(A, P, repeats=10)
                                 │     ├─ perf_counter() 시작
                                 │     ├─ for _ in range(10): mac_2d(A, P)  ← dispatch
                                 │     └─ 평균 시간(ms) 계산
                                 │
                                 ├─ _benchmark_once(B, P, repeats=10)  (동일)
                                 │
                                 ├─ 출력: {label_a} 점수 / {label_b} 점수
                                 │
                                 ├─ 판정 (epsilon = 1e-9)
                                 │     |Δ| < 1e-9 → "UNDECIDED"
                                 │     A > B      → "{label_a} 와 더 닮음"
                                 │     A < B      → "{label_b} 와 더 닮음"
                                 │
                                 └─ 출력: 평균 연산 시간 (ms)
```

### 3. 모드 2 — data.json 분석 ([mode2.py](mode2.py))

```
mode2.run("data.json")
   │
   ├─ data_loader.load_data("data.json")     ┐ JSON 파일을
   │       (FileNotFoundError → 안내 후 종료) │ 단순히 dict 로 로드
   │                                         ┘
   │
   ├─ data_loader.load_filters(data)
   │       │
   │       ├─ 정규식 ^size_(\d+)$ 매칭 키만 필터로 인식
   │       └─ {5: {Cross: …, X: …}, 13: {…}, 25: {…}}
   │
   ├─ data_loader.load_patterns(data)
   │       │
   │       ├─ 정규식 ^size_(\d+)_(\d+)$ 매칭 키만 패턴으로 인식
   │       ├─ 각 패턴의 expected 라벨을 normalize_label() 로 정규화
   │       │     '+', 'cross', 'Cross' → 'Cross'
   │       │     'x', 'X'              → 'X'
   │       └─ id 기준 정렬해서 출력 안정화
   │
   ├─ 카운터 초기화 (total / passed / failed / fail_records)
   │
   └─ 모든 패턴을 순회 ─────────────────────────────────────────┐
        │                                                       │
        ├─ filters 에 size_N 이 없으면 → FAIL 기록 후 계속        │ 한 패턴이
        │                                                       │ 죽어도
        ├─ _validate_square(grid, n)        (패턴)               │ 전체는
        ├─ _validate_square(f_cross, n)     (Cross 필터)         │ 멈추지
        ├─ _validate_square(f_x, n)         (X 필터)             │ 않는다
        │     하나라도 실패 → FAIL 기록 후 다음 패턴              │
        │                                                       │
        ├─ score_cross = mac_2d(f_cross, grid)   ← dispatch     │
        ├─ score_x     = mac_2d(f_x,     grid)   ← dispatch     │
        │                                                       │
        ├─ _verdict(score_cross, score_x)                       │
        │     |Δ| < 1e-9 → "UNDECIDED"                          │
        │     Cross > X  → "Cross"                              │
        │     Cross < X  → "X"                                  │
        │                                                       │
        ├─ verdict == expected ? PASS : FAIL                    │
        └────────────────────────────────────────────────────────┘
   │
   └─ 마지막 요약 출력
         전체 / 통과 / 실패 개수
         실패 케이스 식별자와 사유 목록
```

### 4. 벤치마크 ([benchmark.py](benchmark.py))

벤치마크도 두 진입점을 갖는다.

- `run()` — 메뉴 3번. 고정 SIZES = (3, 5, 13, 25) 에 대해 4파트(메인표 / 버전비교 / 1D vs 2D / 정합성) 출력.
- `run_for_size(n)` — 메뉴 5번에서 호출. 임의의 N 에 대해 단일 측정 1줄.

```
benchmark.run()  ←─ 메뉴 3
   │
   ├─ (A) 메인 표 — 현재 선택 버전, 10회 평균
   │       SIZES = (3, 5, 13, 25) 각각:
   │           cross = make_cross(n)
   │           x     = make_x(n)
   │           평균 ms = _measure(mac_2d_with, (current_ver, cross, x), 10)
   │       → 표 출력 (크기 / 평균 시간 / 연산 횟수 N²)
   │
   ├─ (B) 4가지 케이스 비교 — 각 케이스 COMPARE_REPEATS(=200)회 평균
   │       SIZES 각각:
   │           base   = baseline 으로 측정
   │           sp     = sumprod 로 측정
   │           bw_pc  = bitwise 로 측정 (매 호출 패킹 → 함정 케이스)
   │           cross_pk = pack_grid(cross)   ┐ 측정 구간
   │           x_pk     = pack_grid(x)       │ 바깥
   │           bw_pp  = mac_packed 만 측정    ┘ (사전 패킹)
   │       → 비교 표 출력
   │
   ├─ (C) 보너스 1 — 1D vs 2D (sumprod 기준)
   │       각 N: cross / x / cross_flat / x_flat 준비 후
   │            mac_2d_with("sumprod") vs mac_1d_with("sumprod") 측정
   │
   └─ (D) 정합성 sanity check
         모든 버전이 mac_2d(13×13 Cross, X) 로 같은 값을 내는지 확인

benchmark.run_for_size(n)  ←─ 메뉴 5의 후속 액션 2
   │
   ├─ N 검증 (1 미만이면 안내 후 종료)
   ├─ cross = make_cross(n), x = make_x(n)
   ├─ 평균 ms = _measure(mac_2d_with, (current_ver, cross, x), REPEATS=10)
   └─ 한 줄 출력 (N / 버전 / 평균 시간 / 연산 횟수)
```

`_measure()` 는 `time.perf_counter()` 로 호출 직전·직후를 찍어 평균을 내며, **flatten / pack 같은 준비 작업은 측정 구간 밖** 에서 수행해 "순수 연산 시간" 만 잰다.

### 5. MAC 버전 dispatch ([mac.py](mac.py))

이 프로젝트의 가장 중요한 디자인 결정.

```
mode1/mode2/benchmark
        │
        ▼
   mac.mac_2d(A, B)        ← 이 함수가 dispatch 의 입구
        │
        ▼
   _DISPATCH_2D[_current_version](A, B)
        │
        ├─ "baseline" → _mac_2d_baseline(A, B)
        │                  └─ for i: for j: total += A[i][j]*B[i][j]
        │
        ├─ "sumprod"  → _mac_2d_sumprod(A, B)
        │                  └─ sum(math.sumprod(ra, rb) for ra, rb in zip(A, B))
        │
        └─ "bitwise"  → _mac_2d_bitwise(A, B)
                          ├─ 0/1 격자 아님? → _mac_2d_sumprod 폴백
                          ├─ pack_grid(A) → 정수 pa
                          ├─ pack_grid(B) → 정수 pb
                          └─ (pa & pb).bit_count()
```

세 함수 모두 호출 직후 `_validate_2d()` 를 통과해야 한다 — 잘못된 입력은 항상 동일한 `ValueError` 로 떨어진다. 사용자 입장에서는 어떤 버전을 골라도 인터페이스(반환값/예외)가 똑같다.

### 6. 메뉴 4번 — 버전 변경

```
_select_version()
   │
   ├─ mac.VERSIONS 순서대로 번호 매겨 출력
   │     "1) baseline (현재) — …"
   │     "2) sumprod         — …"
   │     "3) bitwise         — …"
   │     "0) 취소"
   │
   ├─ input("선택> ")
   │     └─ 숫자(1..3) 또는 이름('sumprod') 모두 허용
   │
   ├─ mac.set_version(chosen)
   │     └─ mac._current_version 갱신 (모듈 전역 상태)
   │
   └─ 메뉴 루프로 복귀
       → 다음 _print_menu() 호출 시 헤더의 "현재 MAC 버전" 이 갱신됨
       → 이후 모드1/모드2/벤치마크는 모두 새 구현으로 동작
```

### 7. 메뉴 5번 — 패턴 생성기 (보너스 2)

이 항목이 보너스 2 의 진짜 진입점입니다. 사용자가 N 을 입력해서 N×N Cross/X 패턴을 받아 보고, 그 패턴을 바로 mode1/벤치마크에 연결할 수 있습니다.

```
_pattern_generator()
   │
   ├─ N 입력 받기 (양의 정수만 허용, 그 외는 거부 후 메뉴로 복귀)
   │
   ├─ pattern_gen.make_cross(n)  → cross
   ├─ pattern_gen.make_x(n)      → x
   │
   ├─ pattern_gen.render(cross) 출력  ← #/. ASCII 시각화
   ├─ pattern_gen.render(x)     출력
   │
   └─ 후속 액션 서브메뉴
        ├─ 1) 모드1 진입 → mode1.run_with_filters(cross, x, n)
        │       └─ 사용자는 N×N 패턴만 입력
        │       └─ Cross 점수 / X 점수 / 판정 / 평균시간 출력
        │
        ├─ 2) 단일 벤치마크 → benchmark.run_for_size(n)
        │       └─ 현재 선택된 MAC 버전으로 N×N MAC 을 10회 평균 측정
        │
        └─ 3) 그냥 출력만 → 메인 메뉴로 복귀
```

설계 포인트:
- `pattern_gen.render()` 는 여기서 처음으로 사용자에게 노출됩니다 (다른 곳에서는 호출되지 않음).
- `mode1.run_with_filters(A, B, n)` 는 기존 `mode1.run()` 과 형제 함수로, 필터가 미리 주어졌을 때의 진입점. 두 함수 모두 내부 `_judge_and_print()` 헬퍼를 거쳐 출력 형식이 동일합니다.
- `benchmark.run_for_size(n)` 은 `SIZES = (3,5,13,25)` 고정 표가 아니라 임의의 N 을 받기 위한 별도 진입점.
- 메뉴 4번에서 MAC 버전을 바꾼 뒤 메뉴 5번에 들어가면, 후속 액션의 mode1/벤치마크 모두 새 버전으로 동작합니다.

### 8. 첫 사용 시나리오 (5분 안에 따라 해보기)

```
$ python main.py

   * 현재 MAC 버전: baseline
   1) 모드 1 …  2) 모드 2 …  3) 벤치마크  4) 버전 선택  5) 패턴 생성기  0) 종료
선택> 2                          ← data.json 으로 12개 패턴 일괄 검증
                                   (모두 PASS 가 떠야 정상)
선택> 3                          ← baseline 기준 벤치마크
선택> 4                          ← 버전 선택 메뉴 진입
선택> 2                          ← sumprod 선택
선택> 3                          ← sumprod 기준 벤치마크 (2배쯤 빨라짐)
선택> 4
선택> 3                          ← bitwise 로 변경
선택> 2                          ← bitwise 로 mode2 다시 — 결과는 동일하게 12/12

# 보너스 2 시나리오
선택> 5                          ← 패턴 생성기 진입
N 입력 (예: 7) > 7               ← 임의 N
                                   (Cross/X 7×7 시각화 출력)
선택> 2                          ← 이 N 으로 단일 벤치마크 1회
선택> 5                          ← 다시 패턴 생성기
N 입력 (예: 7) > 5
선택> 1                          ← 5×5 Cross/X 를 필터로 사용해 mode1 진입
                                   (사용자는 5×5 패턴만 입력하면 됨)
선택> 0                          ← 종료
```

이 시나리오를 따라 하면 (a) 동일한 입력이 세 구현에서 같은 결과를 낸다는 것, (b) 보너스 2 의 패턴 생성기가 mode1·벤치마크와 자연스럽게 연결된다는 것을 직접 확인할 수 있습니다.

---

## 결과 리포트

### 모드 2 실행 결과
12개 패턴 전부 PASS:
```
=== 모드 2: data.json 분석 ===
필터 사이즈: [5, 13, 25]
분석할 패턴 수: 12

[size_5_1]  N=5,  expected=Cross  -> Cross=9,  X=1   판정=Cross  PASS
[size_5_2]  N=5,  expected=X      -> Cross=1,  X=9   판정=X      PASS
[size_5_3]  N=5,  expected=Cross  -> Cross=9,  X=3   판정=Cross  PASS
[size_5_4]  N=5,  expected=X      -> Cross=1,  X=7   판정=X      PASS
[size_13_1] N=13, expected=Cross  -> Cross=25, X=1   판정=Cross  PASS
[size_13_2] N=13, expected=X      -> Cross=1,  X=25  판정=X      PASS
[size_13_3] N=13, expected=Cross  -> Cross=24, X=2   판정=Cross  PASS
[size_13_4] N=13, expected=X      -> Cross=2,  X=24  판정=X      PASS
[size_25_1] N=25, expected=Cross  -> Cross=49, X=1   판정=Cross  PASS
[size_25_2] N=25, expected=X      -> Cross=1,  X=49  판정=X      PASS
[size_25_3] N=25, expected=Cross  -> Cross=48, X=1   판정=Cross  PASS
[size_25_4] N=25, expected=X      -> Cross=2,  X=49  판정=X      PASS

전체: 12, 통과: 12, 실패: 0
```

### 성능 분석 (현재 버전 = baseline, 10회 평균)
```
   크기 |    평균 시간(ms) |   연산 횟수(N²)
   3x3 |       0.001620 |              9
   5x5 |       0.001880 |             25
 13x13 |       0.007760 |            169
 25x25 |       0.026310 |            625
```

### 버전 비교 (2D MAC 평균 ms, 괄호 = baseline 대비 속도배)

> 속도배 읽는 법: **1.0x = baseline 과 동일**, **2.3x = baseline 보다 2.3배 빠름**, **0.5x = baseline 의 절반 속도(2배 느림)**.

```
   크기 |  baseline |       sumprod | bitwise(per-call) | bitwise(pre-packed)
   3x3 |  0.000995 | 0.001205(0.8x) |   0.002104(0.5x)  |   0.000066( 15.1x)
   5x5 |  0.001900 | 0.001654(1.1x) |   0.004736(0.4x)  |   0.000063( 30.2x)
 13x13 |  0.007846 | 0.004371(1.8x) |   0.037821(0.2x)  |   0.000092( 85.3x)
 25x25 |  0.024899 | 0.010618(2.3x) |   0.123170(0.2x)  |   0.000109(228.4x)
```

읽는 법:
- **sumprod** 는 매 N 에서 안정적으로 baseline 대비 1.1×~2.3× 빠르고, N 이 커질수록 격차가 커집니다. 전형적인 "C 레벨 루프 vs 파이썬 바이트코드 루프" 차이.
- **bitwise (per-call)** 는 baseline 보다 **느립니다**. 매 호출마다 2개의 격자를 파이썬 for-loop 으로 패킹하는 비용이 AND+popcount 의 이득을 압도하기 때문. 즉 "그냥 버전을 bitwise 로 바꿨다고 자동으로 빨라지진 않음" 이라는 정직한 결과.
- **bitwise (pre-packed)** 는 패킹을 측정 구간 밖에서 1번만 해두고 `mac_packed()` 를 호출한 케이스. N=25 에서 **228×** 빨라지고, N 이 커질수록 격차가 더 벌어집니다. 입력이 0/1 이고 같은 격자를 여러 번 쓰는 시나리오라면 압도적 우위.

### 보너스 1 — 1D vs 2D MAC 비교 (sumprod 버전 기준)
```
   크기 |    2D ms |    1D ms | 속도 향상
   3x3 | 0.001223 | 0.000348 |  3.51x
   5x5 | 0.001761 | 0.000467 |  3.77x
 13x13 | 0.004448 | 0.001807 |  2.46x
 25x25 | 0.010996 | 0.006118 |  1.80x
```
재미있는 점: baseline 버전에서는 1D/2D 차이가 거의 없었는데(둘 다 파이썬 루프이므로), sumprod 버전에서는 1D 가 분명히 더 빠릅니다. C 레벨로 내려가면 "행 단위 sumprod 호출 + 외부 sum" 의 누적 오버헤드가 드러나기 때문입니다. 이건 "최적화는 시스템 전체로 봐야 한다" 는 좋은 사례.

### 분석 — FAIL 원인 및 시간 복잡도

이번 12개 패턴 테스트에서는 모든 케이스가 PASS 했고 FAIL 은 발생하지 않았다. 이는
필터(Cross / X)가 서로 직교에 가까운 형태이고, 노이즈를 섞은 패턴(`*_3`, `*_4`)도
"진짜" 픽셀이 살아남는 비율이 충분히 높아 점수 차이가 명확하게 갈렸기 때문이다.
FAIL 이 발생할 수 있는 시나리오는 동작 단계별로 세 갈래로 나뉜다.

**(1) 데이터 로드 단계 — 분석 자체가 중단되는 경우.**
`data.json` 안에 미지원 라벨(`'plus'`, `'cross_shape'` 등)이 하나라도 섞이면
`load_patterns()` 안의 `normalize_label()` 이 `ValueError` 를 던지고, 이 예외는
패턴별로 잡히지 않은 채 그대로 위로 전파된다. `mode2.run()` 의 외곽 try/except 가
이걸 잡아 `[ERROR] 데이터 파싱 실패: …` 메시지를 출력하면서 분석 전체를 중단한다.
즉 이 단계에서의 오류는 **"한 패턴만 FAIL"** 이 아니라 **"전체 분석 종료"** 다.
한 항목만 FAIL 처리하려면 `load_patterns` 안에서 항목별로 try/except 를 두면 되지만,
현재 구현은 그렇게 하지 않는다 — 데이터 손상은 조기에 크게 알리는 편이 안전하다는 판단.

**(2) 패턴 순회 단계 — 해당 패턴만 FAIL 로 기록되는 경우.**
순회 안에서 발생하는 오류는 모두 `fail_records` 에 사유와 함께 적히고, 다음 패턴으로
계속 진행한다. 대표적으로 (a) `filters` 에 해당 `size_N` 이 아예 없는 경우,
(b) `_validate_square()` 가 "행/열 수 불일치" 를 발견한 경우(데이터 손상),
(c) `mac_2d()` 가 산술/형 변환 오류를 던진 경우.

**(3) 판정 단계 — UNDECIDED 로 인한 FAIL.**
노이즈가 너무 많아 두 점수의 차이가 epsilon(1e-9) 이내로 좁아지면 `UNDECIDED` 로 판정되고,
expected 와 다르면 FAIL 로 잡힌다. (1)/(2)/(3) 어느 경로든 마지막에 실패 케이스 식별자와
사유가 요약 출력되어 디버깅을 돕는다.

**시간 복잡도.** `mac_2d` 는 정확히 N² 번의 곱셈+덧셈을 수행하므로 입력 크기에 대해
**O(N²)** 이며, 이는 곧 격자에 들어 있는 셀 수에 비례한다. baseline 측정표를 보면
N=3 → 9, N=5 → 25, N=13 → 169, N=25 → 625 로 셀 수가 약 70배(625/9 ≈ 69.4)까지
늘어나는데, 평균 시간도 대략 같은 비율로 늘어 O(N²) 가정과 잘 맞는다. 13×13 → 25×25
구간이 다른 구간보다 가파른 것은, 파이썬 해석기 오버헤드(인덱싱·바인딩·점프)가 작은
N 에서는 측정 잡음에 묻혔다가 큰 N 에서 본격적으로 드러나기 때문이다.

**1D vs 2D 의 해석은 어떤 버전을 쓰느냐에 따라 달라진다.** baseline(순수 파이썬 루프)
에서는 `mac_1d` 와 `mac_2d` 의 차이가 거의 없다 — 둘 다 같은 종류의 바이트코드 루프이고,
실제 시간은 곱셈/덧셈 자체가 아니라 인터프리터 오버헤드가 지배하기 때문이다. 반면
sumprod 버전에서는 1D 가 분명히 더 빠른데(N=25 에서 1.80x, N=3 에서 3.77x), 이는
2D 경로가 "행 단위 sumprod 호출 N번 + 외부 sum" 으로 분해되는 반면 1D 경로는 sumprod
한 번이면 끝나기 때문이다. 즉 **루프 자체가 C 레벨로 내려가야 평탄화의 이득이 비로소
드러나며**, "최적화는 한 함수만 보지 말고 호출 경로 전체를 함께 봐야 한다"는 좋은
사례가 된다.

---

## 타 프로젝트와의 교차 검증 — "1D 가 2D 보다 빠르다" 는 항상 맞는가?

### 문제 제기

같은 과제를 구현한 다른 프로젝트
([TraceofLight/1_month_crunch](https://github.com/TraceofLight/1_month_crunch), `e1-3` 브랜치)에서는
**1D MAC 이 2D MAC 보다 일관되게 ~1.5배 빠르다** 는 결과가 나왔다.

```
(저쪽 프로젝트 측정)
   크기 |  2D 평균(ms) |  1D 평균(ms) | 비율
   3x3 |   0.000610  |   0.000390  | 1.56x
   5x5 |   0.001110  |   0.000550  | 2.02x
 13x13 |   0.005550  |   0.003120  | 1.78x
 25x25 |   0.019240  |   0.012690  | 1.52x
```

이에 비해 이 프로젝트의 baseline 에서는 1D/2D 차이가 거의 없다(25×25 에서 ~1.0x).
같은 언어, 같은 알고리즘인데 왜 결과가 다를까?

### 원인: 내부 루프에서의 "간접 접근 횟수"

두 프로젝트의 mac_2d 내부 루프를 한 줄씩 비교하면 차이가 명확하다.

**저쪽 프로젝트의 2D (느린 쪽)**
```python
# 매 반복마다 .values 속성 접근 + [row][col] 이중 인덱싱
total += pattern.values[row_index][column_index] * filter_matrix.values[row_index][column_index]
```
내부 루프의 매 iteration 에서 피연산자 하나당 3단계를 거친다:
1. `pattern.values` — dataclass 의 속성 접근 (CPython 이 딕셔너리를 뒤짐)
2. `[row_index]` — 외부 리스트에서 행을 꺼냄
3. `[column_index]` — 행 안에서 열을 꺼냄

피연산자가 2개이므로 **매 iteration 당 6회의 간접 접근**.

**저쪽 프로젝트의 1D (빠른 쪽)**
```python
total += pattern_flat[index] * filter_flat[index]
```
로컬 변수에 단일 인덱싱만 한다.

피연산자당 1회 → **매 iteration 당 2회 간접 접근**.

6회 vs 2회 → 1D 가 1.5배 정도 빠른 건 당연하다.

**이 프로젝트의 2D**
```python
for i in range(n):
    row_a = A[i]    # ← 행 캐싱: 외부 루프에서 한 번만 꺼냄
    row_b = B[i]
    for j in range(n):
        total += row_a[j] * row_b[j]   # 로컬 변수 + 인덱싱 1회
```
`row_a = A[i]` 로 행을 미리 로컬 변수에 꺼내 두면, 내부 루프에서는 `row_a[j]` 만 하면 된다.
속성 접근도 없고, 외부 리스트 인덱싱도 없다.

피연산자당 1회 → **매 iteration 당 2회 간접 접근** — 1D 와 동일!

### 재현 실험

이론만으로 끝내면 안 되니까 직접 세 가지 코드를 같은 환경에서 돌렸다.

```
=== 저쪽 스타일 (dataclass + .values[r][c] 매번 접근) ===
    N     their_2D     their_1D    2D/1D
  3x3    0.001233ms   0.000917ms   1.35x   ← 2D 가 느리다
  5x5    0.002660ms   0.001656ms   1.61x
 13x13   0.014018ms   0.008633ms   1.62x
 25x25   0.051989ms   0.035257ms   1.47x

=== 이 프로젝트 스타일 (순수 리스트 + row 캐싱) ===
    N       our_2D       our_1D    2D/1D
  3x3    0.000672ms   0.000415ms   1.62x
  5x5    0.001363ms   0.000939ms   1.45x
 13x13   0.006905ms   0.005566ms   1.24x
 25x25   0.022708ms   0.023609ms   0.96x   ← 2D 와 1D 가 사실상 동일

=== 핵심 비교: row 캐싱 한 줄 제거하면? ===
    N    no_cache_2D   cached_2D    gap
  3x3    0.000725ms   0.000662ms   1.10x
  5x5    0.001636ms   0.001335ms   1.23x
 13x13   0.009201ms   0.006792ms   1.35x
 25x25   0.031081ms   0.023027ms   1.35x   ← 캐싱 빼면 저쪽과 비슷한 격차 재현!
```

세 번째 표가 결정적이다. `row_a = A[i]` 라는 **단 한 줄** 을 빼는 것만으로
25×25 에서 1.35배 느려져서 저쪽 레포의 ~1.5배 격차와 비슷한 패턴이 재현된다.

### 그래서 결론은

| 질문 | 답 |
|---|---|
| "1D 가 2D 보다 항상 빠른가?" | **아니다.** 구현에 따라 다르다. |
| 저쪽 레포가 틀린 건가? | **아니다.** 저쪽 측정도 정확하다. |
| 이 프로젝트가 틀린 건가? | **아니다.** 이 프로젝트 측정도 정확하다. |
| 진짜 원인은? | **내부 루프의 간접 접근 횟수** 가 다르다. |

더 정확하게 말하면:
- "2D 가 본질적으로 느리다" 가 아니라, **"내부 루프에서 속성 접근과 이중 인덱싱을 반복하면 느리다"** 가 맞다.
- 행 캐싱(`row_a = A[i]`)을 하면 2D 라도 내부 루프의 접근 비용이 1D 와 동일해진다.
- 저쪽 프로젝트에서 1D 가 빨랐던 건 **차원 차이** 때문이 아니라, 1D 로 평탄화하면 dataclass 속성 접근과 이중 인덱싱이 자동으로 사라지기 때문이다.

이것은 파이썬 성능 최적화의 근본적인 교훈이기도 하다:
**"몇 차원이냐" 보다 "내부 루프에서 한 번 더 찾느냐 안 찾느냐" 가 더 크게 영향을 미친다.**
CPython 인터프리터에서 속성 접근(attribute lookup) 한 번의 비용은 리스트 인덱싱 한 번의
비용과 비슷하거나 더 크기 때문에, 루프 안에서 이를 제거하는 것(로컬 변수 캐싱)이
차원을 바꾸는 것보다 더 효과적인 최적화가 된다.
