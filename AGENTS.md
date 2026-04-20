# 수학 문제지 메이커

수학 문제를 YAML로 정의하고 PDF/Word/HTML로 렌더링하는 에이전트 기반 프로젝트.
에이전트의 역할은 **YAML 문제 파일 생성** → **검증** → **렌더링 실행**이다.

## 프로젝트 구조

```
├── AGENTS.md                                # 모든 에이전트의 공용 지침 (이 파일)
├── .claude/                                 # Claude Code 전용
│   ├── settings.json                        #   validate/render 명령 자동 허용
│   └── commands/                            #   슬래시 커맨드
│       ├── make-problems.md                 #     /make-problems <학년 과목 개수>
│       ├── validate.md                      #     /validate <yaml_path>
│       └── render.md                        #     /render <yaml_path>
├── .codex/                                  # Codex 전용
│   ├── instructions.md                      #   Codex 지침 (이 파일 요약)
│   └── setup.sh                             #   샌드박스 환경 셋업 스크립트
├── .cursor/                                 # Cursor 전용
│   ├── rules/math-problem.mdc              #   항상 적용되는 수식 규칙
│   └── skills/math-problem-maker/SKILL.md  #   수학 문제 요청 시 자동 활성화
├── scripts/
│   ├── render.py                            # YAML → Markdown → Pandoc → PDF/Word/HTML
│   ├── validate.py                          # 스키마 + LaTeX 수식 검증
│   └── schema.py                            # YAML JSON Schema 정의
├── templates/
│   ├── problem-sheet.md.j2                  # 문제지 Jinja2 템플릿
│   ├── answer-sheet.md.j2                   # 정답지 Jinja2 템플릿
│   ├── header.tex                           # LaTeX 헤더 (한글 폰트, AMS)
│   └── preview.html.j2                      # HTML 미리보기 (KaTeX CDN)
├── problems/                                # 문제 YAML 파일 저장소
├── output/                                  # 렌더링 결과물 (.gitignore)
├── requirements.txt                         # Python 의존성
└── Makefile
```

## 에이전트별 연동 방식

### Claude Code (.claude/)

- `settings.json`: make, validate, render 관련 Bash 명령을 자동 허용하여 매번 승인 불필요
- `commands/make-problems.md`: `/make-problems 중3 이차방정식 10문제` 형태로 호출
- `commands/validate.md`: `/validate problems/파일.yaml` 형태로 호출
- `commands/render.md`: `/render problems/파일.yaml` 형태로 호출
- 이 파일(AGENTS.md)이 프로젝트 전체 지침 역할을 한다

### Codex (.codex/)

- `instructions.md`: 이 파일의 핵심 요약본. Codex가 태스크 수행 시 자동 참조
- `setup.sh`: 샌드박스에서 venv 생성 + 의존성 설치를 자동화
- 루트의 이 파일(AGENTS.md)도 함께 참조된다

### Cursor (.cursor/)

- `rules/math-problem.mdc`: `alwaysApply: true`로 설정되어 항상 적용. 수식 깨짐 방지 핵심 규칙
- `skills/math-problem-maker/SKILL.md`: 수학 문제, 문제지, 시험지, LaTeX 등의 키워드로 자동 활성화

## 워크플로우

```
1. make install                               # 최초 1회: venv + 의존성 설치
2. problems/ 디렉토리에 YAML 파일 생성
3. .venv/bin/python scripts/validate.py <파일>  # 스키마 + 수식 검증
4. .venv/bin/python scripts/render.py <파일>    # PDF/Word/HTML 생성
5. output/ 에서 결과물 확인
```

반드시 **validate → render** 순서. 검증 실패 시 수식을 먼저 수정한다.

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
      정답/풀이.

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

  - id: 3
    type: essay
    points: 10
    question: |
      서술형 문제 본문.
    answer: |
      모범 풀이.
```

## LaTeX 수식 규칙 (수식 깨짐 방지 핵심)

### YAML 이스케이프

YAML `|` (literal block) 안에서는 백슬래시가 그대로 유지된다.
`question`, `answer` 필드는 반드시 `|`를 사용한다.

```yaml
question: |
  $\frac{1}{2}$를 구하시오.       # OK: literal block이므로 \ 그대로

choices:
  - "$\\frac{1}{2}$"              # OK: 따옴표 안에서 \\ 이스케이프 필수
  - "$\frac{1}{2}$"               # WRONG: \f가 form feed로 해석됨
```

### 인라인 vs 블록

| 용도 | 문법 | 예시 |
|------|------|------|
| 문장 안의 짧은 수식 | `$...$` | `$x^2 + 1$` |
| 독립된 긴 수식 | `$$...$$` | `$$\int_0^1 f(x)\,dx$$` |

### 자주 쓰는 수식 패턴

```
분수:       $\frac{a}{b}$
제곱근:     $\sqrt{x}$, $\sqrt[3]{x}$
적분:       $\int_a^b f(x)\,dx$
극한:       $\lim_{x \to a} f(x)$
합:         $\sum_{k=1}^{n} a_k$
행렬:       $\begin{pmatrix} a & b \\ c & d \end{pmatrix}$
벡터:       $\vec{a}$, $\overrightarrow{AB}$
절댓값:     $\left|x\right|$
큰 괄호:    $\left(\frac{a}{b}\right)$
조합:       $\binom{n}{r}$
로그:       $\log_a b$, $\ln x$
삼각함수:   $\sin x$, $\cos\theta$, $\tan^{-1} x$
```

### 흔한 실수와 교정

```
잘못                              올바름
$\frac12$                         $\frac{1}{2}$         중괄호 필수
$sin x$                           $\sin x$              \sin 명령어 사용
$lim_{x->0}$                      $\lim_{x \to 0}$      \lim, \to 사용
$$x=1,2,3$$                       $$x = 1, 2, 3$$       쉼표 뒤 공백
$\displaystyle\frac{1}{2}$        $$\frac{1}{2}$$       블록 수식 사용
```

### 중괄호 규칙

- `\frac`, `\sqrt`, `^`, `_` 뒤에는 반드시 중괄호 사용
- `x^2` 허용, `x^{10}` 처럼 2자리 이상은 반드시 중괄호
- 여는 `{`와 닫는 `}` 개수가 반드시 일치

## 문제 유형별 예시

### 단답형

```yaml
- id: 1
  type: short_answer
  points: 5
  question: |
    $f(x) = x^3 - 3x + 1$일 때, $f'(2)$의 값을 구하시오.
  answer: |
    $f'(x) = 3x^2 - 3$이므로 $f'(2) = 9$
```

### 객관식

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

### 서술형

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

## 도형(figure) 사용법

문제에 도형이 필요하면 `figure` 필드에 matplotlib Python 코드를 작성한다.
`geometry.py` 헬퍼 모듈을 import하여 간결하게 작성할 수 있다.

### 기본 구조

```yaml
- id: 1
  type: short_answer
  question: |
    그림과 같이 ...
  figure: |
    from geometry import Figure
    f = Figure(figsize=(5, 4))
    f.triangle([(0,0), (8,0), (2,6)], labels=["A","B","C"])
    f.save(FIGURE_PATH)
  answer: |
    ...
```

`FIGURE_PATH`는 render.py가 자동으로 주입한다. 직접 정의하지 않는다.

### geometry.py 주요 API

```
# 기본 도형
f.triangle(vertices, labels=["A","B","C"])
f.rectangle(origin, width, height, labels={"A":"sw","B":"se"})
f.circle(center, radius, label="O")
f.polygon(vertices, labels=..., fill=False)

# 선분
f.segment(p1, p2, label="5")
f.dashed(p1, p2)                        # 점선
f.dotted(p1, p2)                        # 도트선

# 표시/주석
f.point(pos, label="P", offset=(0,0.3))
f.label(pos, text, offset=(0,0.3))
f.region_label(pos, "$S_1$")            # 영역 내부 텍스트
f.angle_mark(vertex, p1, p2, label="60°")
f.right_angle(vertex, p1, p2)           # 직각 표시
f.segment_label(p1, p2, "5", offset=0.3)
f.equal_mark(p1, p2, count=1)           # 같은 길이 틱
f.brace(p1, p2, "$a$", direction="below")
f.dimension(p1, p2, "$b$", offset=-0.5)

# 좌표평면
f.coordinate_plane(xlim=(-1,6), ylim=(-1,5))
f.plot_function(lambda x: x**2, xlim=(-2,2))
f.plot_points([(1,1),(2,4)], labels=["A","B"])

# 원/호
f.arc(center, radius, angle_start, angle_end)
f.sector(center, radius, start, end, fill=True)
f.chord(center, radius, angle1, angle2)
f.inscribed_polygon(center, radius, n=6, labels=["A","B",...])

# 영역 채우기
f.fill_polygon(vertices, color="lightblue", alpha=0.3)
f.shade_region(vertices)
f.hatch(vertices, pattern="///")
```

### 자주 쓰는 패턴

삼각형 + 수선 + 직각표시:
```yaml
figure: |
  from geometry import Figure
  f = Figure(figsize=(5,4))
  A, B, C = (0,6), (0,0), (8,0)
  H = (2.88, 2.16)
  f.triangle([A,B,C], labels={"A":A, "B":B, "C":C})
  f.right_angle(B, A, C)
  f.dashed(B, H)
  f.point(H, label="H")
  f.segment_label(A, B, "6", offset=-0.5)
  f.save(FIGURE_PATH)
```

원 + 내접 정다각형:
```yaml
figure: |
  from geometry import Figure
  f = Figure(figsize=(5,5))
  f.circle((0,0), 4)
  f.inscribed_polygon((0,0), 4, 6, rotation=90, labels=["A","B","C","D","E","F"])
  f.point((0,0), label="O")
  f.save(FIGURE_PATH)
```

좌표평면 + 함수 그래프:
```yaml
figure: |
  from geometry import Figure
  f = Figure(figsize=(5,4))
  f.coordinate_plane((-1,6), (-1,5))
  f.plot_function(lambda x: -x**2 + 4*x, (-0.5, 4.5))
  f.plot_points([(2,4)], labels=["(2,4)"])
  f.save(FIGURE_PATH, transparent=False)
```

### 주의사항

- `figure` 필드도 YAML literal block(`|`)이므로 백슬래시 이스케이프 불필요
- matplotlib도 import 가능 (`import matplotlib.pyplot as plt`)
- 복잡한 도형은 좌표를 직접 계산하여 사용
- `f.save(FIGURE_PATH)` 호출을 잊지 않는다

## 명령어 요약

| 명령어 | 설명 |
|--------|------|
| `make install` | venv 생성 + 의존성 설치 (최초 1회) |
| `make validate FILE=<yaml>` | 스키마 + 수식 검증 |
| `make render FILE=<yaml>` | PDF/Word/HTML 렌더링 |
| `make render-all` | problems/ 내 전체 렌더링 |
| `make clean` | output/ 비우기 |
