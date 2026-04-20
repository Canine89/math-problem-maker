# 수학 문제지 메이커

에이전트(Claude Code, Cursor, Codex)가 수학 문제를 생성하고 PDF/Word/HTML로 export하는 파이프라인.

## 요구사항

- Python 3.10+
- [Pandoc](https://pandoc.org/) (`brew install pandoc`)
- LaTeX 엔진 (`brew install --cask mactex-no-gui` 또는 TinyTeX)

## 설치

```bash
make install
```

## 사용법

### 1. 문제 YAML 작성

`problems/` 디렉토리에 YAML 파일을 생성합니다. 예시는 `problems/examples/sample-calculus.yaml`을 참고하세요.

### 2. 수식 검증

```bash
make validate FILE=problems/examples/sample-calculus.yaml
```

### 3. 렌더링 (PDF + Word + HTML)

```bash
make render FILE=problems/examples/sample-calculus.yaml
```

결과물은 `output/` 디렉토리에 생성됩니다:
- `*-문제지.pdf` / `*-문제지.docx` / `*-문제지.html`
- `*-정답지.pdf` / `*-정답지.docx` / `*-정답지.html`

## 프로젝트 구조

```
├── AGENTS.md              # Claude Code / Codex 에이전트 지침
├── .cursor/rules/         # Cursor 에이전트 규칙
├── scripts/
│   ├── render.py          # 렌더링 파이프라인
│   ├── validate.py        # LaTeX 수식 검증
│   └── schema.py          # YAML 스키마
├── templates/             # Jinja2 + LaTeX 템플릿
├── problems/              # 문제 YAML 파일
└── output/                # 생성된 PDF/Word/HTML
```
