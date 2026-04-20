# 수학 문제지 메이커 - Codex 지침

수학 문제를 YAML로 정의하고 PDF/Word/HTML로 렌더링하는 프로젝트.

## 셋업

```bash
make install
```

## 워크플로우

1. `problems/` 디렉토리에 YAML 파일 생성
2. `.venv/bin/python scripts/validate.py <파일>` 실행 (수식 검증)
3. 검증 통과 시 `.venv/bin/python scripts/render.py <파일>` 실행
4. `output/` 에서 결과물 확인

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

## 수식 깨짐 방지 규칙

- `question`, `answer`: YAML literal block(`|`) 사용 → 백슬래시 이스케이프 불필요
- `choices` 배열: 따옴표 + `\\` 이스케이프 필수 (`"$\\frac{1}{2}$"`)
- `\frac`, `\sqrt`, 2자리 이상 `^`/`_` 뒤에는 `{}` 필수
- `\sin`, `\cos`, `\lim`, `\log` 등 명령어 형태 사용
- `{`와 `}` 개수 반드시 일치

상세 스펙은 루트의 AGENTS.md 참조.
