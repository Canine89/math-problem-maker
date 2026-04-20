# 수학 문제지 메이커

수학 문제를 YAML로 정의하고 PDF/Word/HTML로 렌더링하는 프로젝트.

## 핵심 워크플로우

```bash
# 1. 의존성 설치 (최초 1회)
make install

# 2. problems/ 에 YAML 문제 파일 생성

# 3. 수식 검증
.venv/bin/python scripts/validate.py <yaml_file>

# 4. 렌더링 (PDF/Word/HTML)
.venv/bin/python scripts/render.py <yaml_file>

# 5. output/ 에서 결과 확인
```

반드시 validate → render 순서로 실행. 검증 실패 시 수식을 먼저 수정한다.

## YAML 문제 포맷

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
    answer: 3  # 1-indexed
```

## 수식 깨짐 방지 규칙 (반드시 준수)

- `question`, `answer` 필드는 YAML literal block(`|`) 사용 → `\frac` 그대로 쓰면 됨
- `choices` 배열 안에서는 따옴표 + 이중 백슬래시 필수: `"$\\frac{1}{2}$"`
- `\frac`, `\sqrt`, 2자리 이상 `^`, `_` 뒤에는 반드시 `{}` 사용
- `\sin`, `\cos`, `\lim`, `\log` 등 반드시 명령어 형태 사용
- `{`와 `}` 개수 일치 필수

### 자주 쓰는 패턴

```
$\frac{a}{b}$  $\sqrt{x}$  $\int_a^b f(x)\,dx$  $\lim_{x \to a} f(x)$
$\sum_{k=1}^{n} a_k$  $\binom{n}{r}$  $\vec{a}$  $\left(\frac{a}{b}\right)$
```

### 흔한 실수

```
$\frac12$     → $\frac{1}{2}$     (중괄호 필수)
$sin x$       → $\sin x$          (\sin 사용)
$lim_{x->0}$  → $\lim_{x \to 0}$  (\lim, \to 사용)
```

## 프로젝트 구조

- `scripts/validate.py` - 스키마 + LaTeX 수식 검증
- `scripts/render.py` - Pandoc 기반 렌더링 (PDF/Word/HTML)
- `scripts/schema.py` - YAML JSON Schema
- `templates/` - Jinja2 템플릿 + LaTeX 헤더
- `problems/` - 문제 YAML 파일
- `output/` - 렌더링 결과물 (.gitignore)
