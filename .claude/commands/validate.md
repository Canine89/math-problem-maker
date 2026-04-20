problems/ 디렉토리의 YAML 파일을 검증한다.

인자로 파일 경로가 주어지면 해당 파일만, 없으면 problems/ 내 모든 YAML 파일을 검증한다.

```bash
.venv/bin/python scripts/validate.py $ARGUMENTS
```

검증 실패 시 오류 내용을 분석하고 YAML 파일의 수식을 수정한 뒤 재검증한다.
