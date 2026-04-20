"""YAML 문제 파일의 스키마 + LaTeX 수식 유효성을 검증한다."""

import re
import sys
from pathlib import Path

import yaml
from pylatexenc.latexwalker import LatexWalker, LatexWalkerError

from schema import validate_schema

INLINE_MATH = re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", re.DOTALL)
DISPLAY_MATH = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)


def _extract_math(text: str) -> list[tuple[str, str]]:
    """텍스트에서 (모드, 수식) 쌍을 추출한다."""
    results: list[tuple[str, str]] = []
    for m in DISPLAY_MATH.finditer(text):
        results.append(("display", m.group(1).strip()))
    remaining = DISPLAY_MATH.sub("", text)
    for m in INLINE_MATH.finditer(remaining):
        results.append(("inline", m.group(1).strip()))
    return results


def _check_latex(expr: str) -> str | None:
    """LaTeX 수식 문자열을 파싱하여 오류가 있으면 메시지를 반환한다."""
    try:
        walker = LatexWalker(expr)
        walker.get_latex_nodes()
        return None
    except LatexWalkerError as exc:
        return str(exc)


def _check_balanced(expr: str) -> str | None:
    """중괄호/괄호 짝이 맞는지 확인한다."""
    stack: list[str] = []
    pairs = {"{": "}", "(": ")", "[": "]"}
    for ch in expr:
        if ch in pairs:
            stack.append(pairs[ch])
        elif ch in pairs.values():
            if not stack or stack[-1] != ch:
                return f"닫는 '{ch}'에 대응하는 여는 괄호가 없습니다"
            stack.pop()
    if stack:
        return f"닫히지 않은 괄호가 있습니다: {''.join(stack)}"
    return None


def validate_math_in_text(text: str, context: str) -> list[str]:
    """텍스트 내 모든 수식을 검증하고 오류 목록을 반환한다."""
    errors: list[str] = []
    for mode, expr in _extract_math(text):
        label = f"{'$$' if mode == 'display' else '$'}{expr}{'$$' if mode == 'display' else '$'}"
        bal_err = _check_balanced(expr)
        if bal_err:
            errors.append(f"  [{context}] {label}\n    -> 괄호 오류: {bal_err}")
        parse_err = _check_latex(expr)
        if parse_err:
            first_line = parse_err.split("\n")[0]
            errors.append(f"  [{context}] {label}\n    -> 파싱 오류: {first_line}")
    return errors


def validate_file(filepath: Path) -> list[str]:
    """YAML 파일 전체를 검증하고 모든 오류를 반환한다."""
    with open(filepath, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    errors: list[str] = []

    schema_errors = validate_schema(data)
    if schema_errors:
        errors.extend(f"  스키마: {e}" for e in schema_errors)

    for prob in data.get("problems", []):
        pid = prob.get("id", "?")
        if "question" in prob:
            errors.extend(validate_math_in_text(prob["question"], f"문제 {pid} question"))
        if "answer" in prob and isinstance(prob["answer"], str):
            errors.extend(validate_math_in_text(prob["answer"], f"문제 {pid} answer"))
        if "solution" in prob:
            errors.extend(validate_math_in_text(prob["solution"], f"문제 {pid} solution"))
        for i, ch in enumerate(prob.get("choices", []), 1):
            errors.extend(validate_math_in_text(ch, f"문제 {pid} 선택지 {i}"))

    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("사용법: python validate.py <yaml_file>", file=sys.stderr)
        return 1

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"파일 없음: {filepath}", file=sys.stderr)
        return 1

    errors = validate_file(filepath)
    if errors:
        print(f"검증 실패 ({len(errors)}개 오류):")
        for e in errors:
            print(e)
        return 1

    print(f"검증 통과: {filepath}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
