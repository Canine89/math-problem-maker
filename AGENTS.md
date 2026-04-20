# 수학 문제지 메이커 - 에이전트 지침

이 프로젝트는 수학 문제를 YAML로 정의하고 PDF/Word/HTML로 렌더링한다.
에이전트의 역할은 **YAML 문제 파일 생성**과 **렌더링 명령 실행**이다.

## 워크플로우

```
1. problems/ 디렉토리에 YAML 파일 생성
2. python scripts/validate.py <파일> 실행 (수식 검증)
3. 검증 통과 시 python scripts/render.py <파일> 실행
4. output/ 에서 결과물(PDF/Word/HTML) 확인
```

## YAML 문제 포맷

```yaml
title: "문제지 제목"
subtitle: "학년/과목"        # 선택
date: "2026-04-20"           # 선택
time_limit: "50분"           # 선택
total_points: 100            # 선택

problems:
  - id: 1                   # 정수, 1부터 시작
    type: short_answer       # short_answer | multiple_choice | essay
    points: 5                # 선택
    question: |
      문제 본문. 수식은 $인라인$ 또는 $$블록$$으로 작성.
    answer: |
      정답/풀이. 수식 동일.

  - id: 2
    type: multiple_choice
    points: 3
    question: |
      객관식 문제 본문.
    choices:                 # multiple_choice일 때 필수
      - "선택지 1"
      - "선택지 2"
      - "선택지 3"
      - "선택지 4"
    answer: 2                # 정답 번호 (1-indexed)
```

## LaTeX 수식 규칙 (수식 깨짐 방지 핵심)

### YAML 안에서의 이스케이프

YAML `|` (literal block) 안에서는 백슬래시가 **그대로 유지**된다.
따라서 `|`를 사용하면 이스케이프 문제가 없다.

```yaml
# 올바름 - literal block 사용
question: |
  $\frac{1}{2}$를 구하시오.

# 올바름 - literal block 사용
answer: |
  $$\int_0^1 x\,dx = \frac{1}{2}$$
```

**주의**: `choices`는 배열이므로 `|`를 쓸 수 없다. 따라서 `\\`로 이스케이프해야 한다:

```yaml
# 올바름 - 따옴표 안에서 \\ 사용
choices:
  - "$\\frac{1}{2}$"
  - "$\\frac{1}{3}$"

# 잘못됨 - 따옴표 안에서 단일 \ 사용 (YAML이 이스케이프 시퀀스로 해석)
choices:
  - "$\frac{1}{2}$"    # YAML이 \f를 form feed로 해석할 수 있음
```

### 인라인 vs 블록 수식

| 용도 | 문법 | 예시 |
|------|------|------|
| 문장 안의 짧은 수식 | `$...$` | `$x^2 + 1$` |
| 독립된 긴 수식 | `$$...$$` | `$$\int_0^1 f(x)\,dx$$` |

### 자주 쓰는 수식 패턴

```
분수:           $\frac{a}{b}$
제곱근:         $\sqrt{x}$, $\sqrt[3]{x}$
적분:           $\int_a^b f(x)\,dx$
극한:           $\lim_{x \to a} f(x)$
합:             $\sum_{k=1}^{n} a_k$
행렬:           $\begin{pmatrix} a & b \\ c & d \end{pmatrix}$
벡터:           $\vec{a}$, $\overrightarrow{AB}$
절댓값:         $|x|$ 또는 $\left|x\right|$
큰 괄호:        $\left(\frac{a}{b}\right)$
조합:           $\binom{n}{r}$ 또는 ${}_{n}\mathrm{C}_{r}$
로그:           $\log_a b$, $\ln x$
삼각함수:       $\sin x$, $\cos\theta$, $\tan^{-1} x$
```

### 흔한 실수와 교정

```
# 잘못                          # 올바름
$\frac12$                       $\frac{1}{2}$       (중괄호 필수)
$sin x$                         $\sin x$            (\sin 명령어 사용)
$lim_{x->0}$                    $\lim_{x \to 0}$    (\lim, \to 사용)
$$x=1,2,3$$                     $$x = 1, 2, 3$$     (쉼표 뒤 공백)
$\displaystyle\frac{1}{2}$      $$\frac{1}{2}$$     (블록 수식 사용)
```

### 중괄호 규칙

- 모든 `\frac`, `\sqrt`, `^`, `_` 뒤에는 **반드시 중괄호** 사용
- `x^2`는 허용되지만, `x^{10}` 처럼 2자리 이상은 반드시 중괄호
- 여는 `{`와 닫는 `}`의 수가 반드시 일치해야 함

## 문제 유형별 가이드

### 단답형 (short_answer)

```yaml
- id: 1
  type: short_answer
  points: 5
  question: |
    $f(x) = x^3 - 3x + 1$일 때, $f'(2)$의 값을 구하시오.
  answer: |
    $f'(x) = 3x^2 - 3$이므로 $f'(2) = 3 \cdot 4 - 3 = 9$
```

### 객관식 (multiple_choice)

```yaml
- id: 2
  type: multiple_choice
  points: 3
  question: |
    $\displaystyle\lim_{n \to \infty} \left(1 + \frac{1}{n}\right)^n$의 값은?
  choices:
    - "$1$"
    - "$e$"
    - "$\\pi$"
    - "$\\infty$"
  answer: 2
```

### 서술형 (essay)

```yaml
- id: 3
  type: essay
  points: 10
  question: |
    다음을 증명하시오.
    $$\sum_{k=1}^{n} k = \frac{n(n+1)}{2}$$
  answer: |
    수학적 귀납법으로 증명한다.
    (i) $n = 1$일 때: $1 = \frac{1 \cdot 2}{2} = 1$ (성립)
    (ii) $n = m$일 때 성립한다고 가정하면 ...
```

## 명령어 요약

| 명령어 | 설명 |
|--------|------|
| `make install` | venv 생성 + 의존성 설치 |
| `.venv/bin/python scripts/validate.py <yaml>` | 스키마 + 수식 검증 |
| `.venv/bin/python scripts/render.py <yaml>` | PDF/Word/HTML 생성 |
| `make validate FILE=<yaml>` | 검증 (make 래퍼) |
| `make render FILE=<yaml>` | 렌더링 (make 래퍼) |
| `make render-all` | 전체 문제 파일 렌더링 |
