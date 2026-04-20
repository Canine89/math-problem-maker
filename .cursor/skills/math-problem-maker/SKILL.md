---
name: math-problem-maker
description: >-
  수학 문제 YAML 파일을 생성하고 PDF/Word/HTML로 렌더링한다.
  수학 문제, 문제지, 시험지, 수식, LaTeX, 렌더링, PDF 변환을 요청할 때 사용.
---

# 수학 문제지 메이커

## 워크플로우

사용자가 수학 문제 생성을 요청하면 아래 순서를 따른다:

1. `problems/` 디렉토리에 YAML 파일 생성
2. `.venv/bin/python scripts/validate.py <파일>` 실행하여 수식 검증
3. 검증 통과 시 `.venv/bin/python scripts/render.py <파일>` 실행
4. `output/` 에서 결과물 확인 안내

최초 실행 시 `make install`로 venv + 의존성 설치가 필요하다.

## YAML 포맷

```yaml
title: "제목"
subtitle: "학년/과목"
date: "2026-04-20"
time_limit: "50분"
total_points: 100

problems:
  - id: 1
    type: short_answer  # short_answer | multiple_choice | essay
    points: 5
    question: |
      $f(x) = x^2$일 때 $f'(1)$의 값을 구하시오.
    answer: |
      $f'(x) = 2x$이므로 $f'(1) = 2$

  - id: 2
    type: multiple_choice
    points: 3
    question: |
      $\sqrt{9}$의 값은?
    choices:
      - "$1$"
      - "$2$"
      - "$3$"
      - "$4$"
    answer: 3
```

## 수식 깨짐 방지 (필수)

- `question`, `answer`: YAML literal block(`|`) 사용 → 백슬래시 이스케이프 불필요
- `choices` 배열: 따옴표 + `\\` 이스케이프 필수 (`"$\\frac{1}{2}$"`)
- `\frac`, `\sqrt`, 2자리 이상 `^`/`_` 뒤에는 `{}` 필수
- `\sin`, `\cos`, `\lim`, `\log` 등 명령어 형태 사용
- `{`와 `}` 개수 반드시 일치

### 자주 쓰는 수식

```
$\frac{a}{b}$  $\sqrt{x}$  $\int_a^b f(x)\,dx$  $\lim_{x \to a} f(x)$
$\sum_{k=1}^{n} a_k$  $\binom{n}{r}$  $\vec{a}$  $\left(\frac{a}{b}\right)$
```

### 흔한 실수

| 잘못 | 올바름 | 이유 |
|------|--------|------|
| `$\frac12$` | `$\frac{1}{2}$` | 중괄호 필수 |
| `$sin x$` | `$\sin x$` | `\sin` 명령어 |
| `$lim_{x->0}$` | `$\lim_{x \to 0}$` | `\lim`, `\to` 사용 |

## 도형 (figure)

도형 문제는 `figure` 필드에 matplotlib 코드를 literal block으로 작성:

```yaml
figure: |
  from geometry import Figure
  f = Figure(figsize=(5,4))
  f.triangle([(0,0),(8,0),(2,6)], labels=["A","B","C"])
  f.right_angle((0,0), (0,6), (8,0))
  f.save(FIGURE_PATH)
```

`FIGURE_PATH`는 자동 주입. `geometry.py` 주요 함수: triangle, rectangle, circle, arc, segment, dashed, point, label, angle_mark, right_angle, region_label, coordinate_plane, plot_function 등. 상세 API는 AGENTS.md 참조.

## 명령어

```bash
make install                        # venv + 의존성 설치
make validate FILE=<yaml>           # 수식 검증
make render FILE=<yaml>             # PDF/Word/HTML 렌더링
make render-all                     # 전체 렌더링
```
