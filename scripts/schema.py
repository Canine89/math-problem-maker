"""YAML 문제 파일의 JSON Schema 정의 및 검증."""

import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator, ValidationError

PROBLEM_SCHEMA = {
    "type": "object",
    "required": ["title", "problems"],
    "properties": {
        "title": {"type": "string", "minLength": 1},
        "subtitle": {"type": "string"},
        "date": {"type": "string"},
        "time_limit": {"type": "string"},
        "total_points": {"type": "number", "minimum": 0},
        "problems": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["id", "type", "question"],
                "properties": {
                    "id": {"type": "integer", "minimum": 1},
                    "type": {
                        "type": "string",
                        "enum": ["short_answer", "multiple_choice", "essay"],
                    },
                    "points": {"type": "number", "minimum": 0},
                    "question": {"type": "string", "minLength": 1},
                    "choices": {
                        "type": "array",
                        "minItems": 2,
                        "items": {"type": "string"},
                    },
                    "answer": {},
                    "solution": {"type": "string"},
                },
                "allOf": [
                    {
                        "if": {"properties": {"type": {"const": "multiple_choice"}}},
                        "then": {"required": ["choices"]},
                    }
                ],
            },
        },
    },
}

_validator = Draft7Validator(PROBLEM_SCHEMA)


def validate_schema(data: dict) -> list[str]:
    """YAML 데이터를 스키마에 대해 검증하고 오류 메시지 목록을 반환한다."""
    errors = []
    for err in sorted(_validator.iter_errors(data), key=lambda e: list(e.path)):
        path = " -> ".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"[{path}] {err.message}")
    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("사용법: python schema.py <yaml_file>", file=sys.stderr)
        return 1

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"파일 없음: {filepath}", file=sys.stderr)
        return 1

    with open(filepath, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    errors = validate_schema(data)
    if errors:
        print(f"스키마 검증 실패 ({len(errors)}개 오류):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("스키마 검증 통과")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
