"""TikZ 코드를 standalone .tex로 감싸서 컴파일하고 PNG로 변환한다."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

TINYTEX_BIN = Path.home() / "Library" / "TinyTeX" / "bin" / "universal-darwin"

PREAMBLE = r"""\documentclass[border=3pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{decorations.pathreplacing,arrows.meta,calc,patterns}
\usepackage{amsmath,amssymb}
\begin{document}
"""

POSTAMBLE = r"""
\end{document}
"""


def _find_pdflatex() -> str | None:
    path = shutil.which("pdflatex")
    if path:
        return path
    tinytex = TINYTEX_BIN / "pdflatex"
    if tinytex.exists():
        return str(tinytex)
    return None


def _find_pdftoppm() -> str | None:
    return shutil.which("pdftoppm")


def render_tikz(tikz_code: str, output_png: str, dpi: int = 300) -> bool:
    """TikZ 코드를 PNG로 렌더링한다. 성공 시 True."""
    pdflatex = _find_pdflatex()
    pdftoppm = _find_pdftoppm()

    if not pdflatex:
        print("  WARN: pdflatex 없음. TikZ 도형 건너뜀.", flush=True)
        return False
    if not pdftoppm:
        print("  WARN: pdftoppm 없음 (brew install poppler). TikZ 도형 건너뜀.", flush=True)
        return False

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / "figure.tex"
        pdf_path = Path(tmpdir) / "figure.pdf"

        tex_content = PREAMBLE + tikz_code + POSTAMBLE
        tex_path.write_text(tex_content, encoding="utf-8")

        result = subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", tmpdir, str(tex_path)],
            capture_output=True, text=True, timeout=30,
        )

        if not pdf_path.exists():
            log = result.stdout[-500:] if result.stdout else ""
            print(f"  ERROR: TikZ 컴파일 실패:\n{log}", flush=True)
            return False

        png_stem = str(Path(output_png).with_suffix(""))
        result2 = subprocess.run(
            [pdftoppm, "-png", "-r", str(dpi), "-singlefile",
             str(pdf_path), png_stem],
            capture_output=True, text=True, timeout=15,
        )

        actual_png = png_stem + ".png"
        if not Path(actual_png).exists():
            print(f"  ERROR: PNG 변환 실패: {result2.stderr}", flush=True)
            return False

        if actual_png != output_png:
            shutil.move(actual_png, output_png)

    return True
