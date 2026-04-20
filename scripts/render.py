"""YAML 문제 파일을 PDF, Word, HTML로 렌더링한다.

파이프라인: YAML -> Jinja2 템플릿 -> Markdown -> Pandoc -> PDF/DOCX/HTML
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "output"

CIRCLED_NUMBERS = list("①②③④⑤⑥⑦⑧⑨⑩")


def load_yaml(filepath: Path) -> dict:
    with open(filepath, encoding="utf-8") as f:
        return yaml.safe_load(f)


def render_template(template_name: str, data: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
    )
    tmpl = env.get_template(template_name)
    return tmpl.render(circled_numbers=CIRCLED_NUMBERS, **data)


def _find_pandoc() -> str:
    path = shutil.which("pandoc")
    if not path:
        print("ERROR: pandoc이 설치되어 있지 않습니다.", file=sys.stderr)
        print("  brew install pandoc", file=sys.stderr)
        sys.exit(1)
    return path


def _has_xelatex() -> bool:
    return shutil.which("xelatex") is not None


def pandoc_convert(md_content: str, output_path: Path, fmt: str) -> bool:
    """Markdown 문자열을 pandoc으로 변환한다. 성공 시 True."""
    pandoc = _find_pandoc()

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(md_content)
        tmp_path = tmp.name

    try:
        cmd = [pandoc, tmp_path, "-o", str(output_path), "--standalone"]

        if fmt == "pdf":
            if not _has_xelatex():
                print("  WARN: xelatex 없음, PDF 생성 건너뜀 (brew install --cask mactex-no-gui)", file=sys.stderr)
                return False
            header_tex = TEMPLATES_DIR / "header.tex"
            cmd += [
                "--pdf-engine=xelatex",
                "-V", "mainfont=AppleMyungjo",
                "-V", "documentclass=article",
            ]
            if header_tex.exists():
                cmd += ["-H", str(header_tex)]

        elif fmt == "docx":
            pass  # pandoc handles LaTeX math -> OOXML natively

        elif fmt == "html":
            cmd += ["--katex", "--self-contained"]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ERROR pandoc ({fmt}): {result.stderr.strip()}", file=sys.stderr)
            return False
        return True
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def render_html_preview(data: dict, output_path: Path) -> bool:
    """Jinja2 HTML 템플릿으로 KaTeX 미리보기를 직접 생성한다."""
    try:
        html = render_template("preview.html.j2", {**data, "show_answers": True})
        output_path.write_text(html, encoding="utf-8")
        return True
    except Exception as exc:
        print(f"  ERROR HTML preview: {exc}", file=sys.stderr)
        return False


def render_file(filepath: Path) -> dict[str, bool]:
    """YAML 파일 하나를 모든 포맷으로 렌더링한다."""
    data = load_yaml(filepath)
    stem = filepath.stem
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results: dict[str, bool] = {}

    problem_md = render_template("problem-sheet.md.j2", data)
    answer_md = render_template("answer-sheet.md.j2", data)

    for fmt in ("pdf", "docx"):
        out_problem = OUTPUT_DIR / f"{stem}-문제지.{fmt}"
        out_answer = OUTPUT_DIR / f"{stem}-정답지.{fmt}"
        results[f"문제지.{fmt}"] = pandoc_convert(problem_md, out_problem, fmt)
        results[f"정답지.{fmt}"] = pandoc_convert(answer_md, out_answer, fmt)

    out_html = OUTPUT_DIR / f"{stem}-미리보기.html"
    results["미리보기.html"] = render_html_preview(data, out_html)

    return results


def main() -> int:
    if len(sys.argv) < 2:
        print("사용법: python render.py <yaml_file>", file=sys.stderr)
        return 1

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"파일 없음: {filepath}", file=sys.stderr)
        return 1

    print(f"렌더링 시작: {filepath}", flush=True)
    results = render_file(filepath)

    success = []
    failed = []
    for name, ok in results.items():
        (success if ok else failed).append(name)

    if success:
        print(f"  성공: {', '.join(success)}")
    if failed:
        print(f"  실패: {', '.join(failed)}")
    print(f"  출력 디렉토리: {OUTPUT_DIR}")

    return 1 if failed and not success else 0


if __name__ == "__main__":
    raise SystemExit(main())
