# Codex 지침

이 프로젝트의 전체 스펙은 루트의 AGENTS.md에 정의되어 있다. 반드시 참조한다.

## 빠른 시작

```bash
# 환경 셋업
bash .codex/setup.sh

# 문제 생성 후 검증 → 렌더링
.venv/bin/python scripts/validate.py problems/<파일>.yaml
.venv/bin/python scripts/render.py problems/<파일>.yaml
```

## 핵심 규칙

- YAML 문제 파일은 `problems/` 디렉토리에 생성
- `question`, `answer` 필드는 YAML literal block(`|`) 사용
- `choices` 배열 안의 수식은 따옴표 + `\\` 이스케이프 필수
- 반드시 validate 통과 후 render 실행
- 도형이 필요한 문제는 `figure` 필드에 matplotlib 코드 작성 (`from geometry import Figure`)
- 상세 도형 API는 AGENTS.md 참조
