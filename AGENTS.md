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

문제에 도형이 필요하면 `figure` 필드에 **TikZ 코드**를 작성한다.
TikZ는 한국 수능/교재 도형의 실제 제작 도구로, 교재와 동일한 품질이 보장된다.
render.py가 pdflatex으로 컴파일 후 PNG로 변환하여 문제지에 삽입한다.

### 기본 구조

```yaml
- id: 1
  type: short_answer
  question: |
    그림과 같이 ...
  figure: |
    \begin{tikzpicture}[scale=0.5, line width=0.4pt]
      \draw (0,0) -- (4,0) -- (2,3) -- cycle;
      \node[below left] at (0,0) {A};
      \node[below right] at (4,0) {B};
      \node[above] at (2,3) {C};
    \end{tikzpicture}
  answer: |
    ...
```

`\begin{tikzpicture}` ~ `\end{tikzpicture}`만 작성. preamble은 자동 추가.

### 사용 가능한 TikZ 라이브러리

preamble에 자동 포함: `decorations.pathreplacing`, `arrows.meta`, `calc`, `patterns`

### 자주 쓰는 패턴

삼각형 + 직각 표시 + 수선:
```yaml
figure: |
  \begin{tikzpicture}[scale=0.5, line width=0.4pt]
    \coordinate (A) at (0,6);
    \coordinate (B) at (0,0);
    \coordinate (C) at (8,0);
    \coordinate (H) at (2.88,2.16);
    \draw (A) -- (B) -- (C) -- cycle;
    \draw[dashed] (B) -- (H);
    \draw (0,0.4) -- (0.4,0.4) -- (0.4,0);
    \fill (H) circle (1.5pt);
    \node[above left] at (A) {A};
    \node[below left] at (B) {B};
    \node[below right] at (C) {C};
    \node[above right] at (H) {\small H};
    \node[left] at (0,3) {\small $6$};
    \node[below] at (4,0) {\small $8$};
  \end{tikzpicture}
```

중괄호 치수 표시:
```yaml
figure: |
  \begin{tikzpicture}[scale=0.5, line width=0.4pt]
    \draw (0,0) rectangle (8,3);
    \draw[decorate,decoration={brace,mirror,raise=4pt,amplitude=3pt}]
      (0,0) -- node[below=7pt] {\small $a$} (8,0);
  \end{tikzpicture}
```

좌표평면 + 함수 그래프:
```yaml
figure: |
  \begin{tikzpicture}[scale=0.6, line width=0.4pt]
    \draw[->] (-0.5,0) -- (5,0) node[right] {\small $x$};
    \draw[->] (0,-0.5) -- (0,5) node[above] {\small $y$};
    \draw[domain=0:4, smooth, line width=0.6pt] plot (\x, {-\x*\x + 4*\x});
    \fill (2,4) circle (1.5pt);
    \node[above right] at (2,4) {\small $(2,4)$};
    \node[below left] at (0,0) {\small O};
  \end{tikzpicture}
```

원 + 내접 정다각형:
```yaml
figure: |
  \begin{tikzpicture}[scale=0.55, line width=0.4pt]
    \draw (0,0) circle (4);
    \foreach \i in {0,...,5} { \coordinate (P\i) at ({90+60*\i}:4); }
    \draw (P0)--(P1)--(P2)--(P3)--(P4)--(P5)--cycle;
    \fill (0,0) circle (1.5pt);
    \node[below right] at (0,0) {\small O};
    \node[above] at (P0) {\small A};
  \end{tikzpicture}
```

### 스타일 규칙

- `scale=0.4~0.6`: 문제지에 적합한 크기
- `line width=0.4pt`: 교재급 얇은 선
- `\small` 또는 `\footnotesize`: 레이블 크기
- `\fill ... circle (1.5pt)`: 점 표시
- `[dashed]`: 점선, `[dotted]`: 도트선
- `\draw (x,y) rectangle (x2,y2)`: 직사각형
- `\draw (cx,cy) circle (r)`: 원
- `\draw[domain=a:b, smooth] plot (\x, {f(x)})`: 함수 그래프

### 주의사항

- `figure` 필드는 YAML literal block(`|`)이므로 `\`를 그대로 쓰면 됨
- `\begin{tikzpicture}` ~ `\end{tikzpicture}`만 작성 (preamble 자동)
- `\documentclass`, `\usepackage` 등은 작성하지 않는다
- pdflatex + pdftoppm이 필요 (TinyTeX 또는 MacTeX)

## 명령어 요약

| 명령어 | 설명 |
|--------|------|
| `make install` | venv 생성 + 의존성 설치 (최초 1회) |
| `make validate FILE=<yaml>` | 스키마 + 수식 검증 |
| `make render FILE=<yaml>` | PDF/Word/HTML 렌더링 |
| `make render-all` | problems/ 내 전체 렌더링 |
| `make clean` | output/ 비우기 |
