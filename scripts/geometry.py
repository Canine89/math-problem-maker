"""수학 문제용 도형을 그리는 matplotlib 헬퍼 모듈.

에이전트가 YAML figure 필드에서 사용하는 고수준 API를 제공한다.
수능/모의고사 스타일의 깔끔한 도형 출력을 목표로 한다.
"""

from __future__ import annotations

import math
from typing import Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
import numpy as np
from matplotlib.patches import FancyArrowPatch

_FONT_CANDIDATES = ["NanumGothic", "AppleGothic", "Malgun Gothic", "sans-serif"]

def _setup_font():
    for font in _FONT_CANDIDATES:
        try:
            matplotlib.font_manager.findfont(font, fallback_to_default=False)
            plt.rcParams["font.family"] = font
            break
        except Exception:
            continue
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["mathtext.fontset"] = "cm"

_setup_font()

Pt = tuple[float, float]


def _mid(p1: Pt, p2: Pt) -> Pt:
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def _offset_from_center(point: Pt, center: Pt, dist: float = 0.35) -> Pt:
    """point를 center로부터 dist만큼 바깥쪽으로 밀어낸 좌표를 반환."""
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return (point[0], point[1] + dist)
    return (point[0] + dx / length * dist, point[1] + dy / length * dist)


def _angle_of(origin: Pt, target: Pt) -> float:
    """origin에서 target 방향의 각도(degree)를 반환."""
    return math.degrees(math.atan2(target[1] - origin[1], target[0] - origin[0]))


def _perp_offset(p1: Pt, p2: Pt, dist: float) -> Pt:
    """p1-p2 선분의 중점에서 수직 방향으로 dist만큼 이동한 좌표."""
    mx, my = _mid(p1, p2)
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return (mx, my + dist)
    nx, ny = -dy / length, dx / length
    return (mx + nx * dist, my + ny * dist)


class Figure:
    """수학 도형을 그리는 캔버스."""

    def __init__(self, figsize: tuple[float, float] = (5, 4)):
        self.fig, self.ax = plt.subplots(1, 1, figsize=figsize)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self._default_lw = 1.5
        self._default_color = "black"
        self._label_fontsize = 13

    # ── 기본 도형 ───────────────────────────────────────

    def triangle(
        self,
        vertices: Sequence[Pt],
        labels: dict[str, Pt] | Sequence[str] | None = None,
        fill: bool = False,
        color: str | None = None,
        **kwargs,
    ):
        """삼각형을 그린다.

        labels: dict {"A": (x,y)} 또는 list ["A","B","C"] (vertices 순서).
        """
        self.polygon(vertices, labels=labels, fill=fill, color=color, **kwargs)

    def polygon(
        self,
        vertices: Sequence[Pt],
        labels: dict[str, Pt] | Sequence[str] | None = None,
        fill: bool = False,
        color: str | None = None,
        linestyle: str = "-",
        linewidth: float | None = None,
    ):
        """다각형을 그린다."""
        c = color or self._default_color
        lw = linewidth or self._default_lw
        xs = [v[0] for v in vertices] + [vertices[0][0]]
        ys = [v[1] for v in vertices] + [vertices[0][1]]
        self.ax.plot(xs, ys, linestyle=linestyle, color=c, linewidth=lw)
        if fill:
            poly = plt.Polygon(vertices, alpha=0.15, color=c)
            self.ax.add_patch(poly)
        if labels is not None:
            center = (
                sum(v[0] for v in vertices) / len(vertices),
                sum(v[1] for v in vertices) / len(vertices),
            )
            if isinstance(labels, dict):
                for text, pos in labels.items():
                    lpos = _offset_from_center(pos, center, 0.4)
                    self.ax.text(
                        lpos[0], lpos[1], text,
                        fontsize=self._label_fontsize, ha="center", va="center",
                    )
            else:
                for text, pos in zip(labels, vertices):
                    lpos = _offset_from_center(pos, center, 0.4)
                    self.ax.text(
                        lpos[0], lpos[1], text,
                        fontsize=self._label_fontsize, ha="center", va="center",
                    )

    def rectangle(
        self,
        origin: Pt,
        width: float,
        height: float,
        labels: dict[str, str] | None = None,
        fill: bool = False,
        color: str | None = None,
        linestyle: str = "-",
        linewidth: float | None = None,
    ):
        """직사각형을 그린다.

        labels: {"A": "sw", "B": "se", "C": "ne", "D": "nw"} 형태.
        sw=왼쪽아래, se=오른쪽아래, ne=오른쪽위, nw=왼쪽위.
        """
        c = color or self._default_color
        lw = linewidth or self._default_lw
        corners = {
            "sw": origin,
            "se": (origin[0] + width, origin[1]),
            "ne": (origin[0] + width, origin[1] + height),
            "nw": (origin[0], origin[1] + height),
        }
        verts = [corners["sw"], corners["se"], corners["ne"], corners["nw"]]
        xs = [v[0] for v in verts] + [verts[0][0]]
        ys = [v[1] for v in verts] + [verts[0][1]]
        self.ax.plot(xs, ys, linestyle=linestyle, color=c, linewidth=lw)
        if fill:
            rect = plt.Polygon(verts, alpha=0.15, color=c)
            self.ax.add_patch(rect)
        if labels:
            center = (origin[0] + width / 2, origin[1] + height / 2)
            offset_map = {"sw": (-0.3, -0.3), "se": (0.3, -0.3), "ne": (0.3, 0.3), "nw": (-0.3, 0.3)}
            for text, pos_key in labels.items():
                corner = corners.get(pos_key, origin)
                off = offset_map.get(pos_key, (0, 0))
                self.ax.text(
                    corner[0] + off[0], corner[1] + off[1], text,
                    fontsize=self._label_fontsize, ha="center", va="center",
                )

    def circle(
        self,
        center: Pt,
        radius: float,
        label: str | None = None,
        fill: bool = False,
        color: str | None = None,
        linestyle: str = "-",
        linewidth: float | None = None,
    ):
        """원을 그린다."""
        c = color or self._default_color
        lw = linewidth or self._default_lw
        circ = plt.Circle(center, radius, fill=fill, edgecolor=c, facecolor=c if fill else "none",
                          linewidth=lw, linestyle=linestyle, alpha=0.15 if fill else 1.0)
        self.ax.add_patch(circ)
        if label:
            self.ax.text(center[0], center[1], label,
                         fontsize=self._label_fontsize, ha="center", va="center")

    # ── 선분 / 직선 ──────────────────────────────────────

    def segment(
        self,
        p1: Pt,
        p2: Pt,
        style: str = "-",
        color: str | None = None,
        linewidth: float | None = None,
        label: str | None = None,
    ):
        """선분을 그린다."""
        c = color or self._default_color
        lw = linewidth or self._default_lw
        self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], linestyle=style, color=c, linewidth=lw)
        if label:
            self.segment_label(p1, p2, label)

    def dashed(self, p1: Pt, p2: Pt, label: str | None = None, **kwargs):
        """점선 선분."""
        self.segment(p1, p2, style="--", label=label, **kwargs)

    def dotted(self, p1: Pt, p2: Pt, label: str | None = None, **kwargs):
        """도트선 선분."""
        self.segment(p1, p2, style=":", label=label, **kwargs)

    # ── 표시 / 주석 ──────────────────────────────────────

    def point(
        self,
        pos: Pt,
        label: str | None = None,
        style: str = "ko",
        size: float = 4,
        fontsize: float | None = None,
        offset: Pt = (0, 0.3),
    ):
        """점을 찍고 선택적으로 레이블을 표시한다."""
        self.ax.plot(pos[0], pos[1], style, markersize=size)
        if label:
            fs = fontsize or self._label_fontsize
            self.ax.text(
                pos[0] + offset[0], pos[1] + offset[1], label,
                fontsize=fs, ha="center", va="center",
            )

    def label(
        self,
        pos: Pt,
        text: str,
        offset: Pt = (0, 0.3),
        fontsize: float | None = None,
        ha: str = "center",
        va: str = "center",
    ):
        """임의 위치에 텍스트 레이블을 표시한다."""
        fs = fontsize or self._label_fontsize
        self.ax.text(
            pos[0] + offset[0], pos[1] + offset[1], text,
            fontsize=fs, ha=ha, va=va,
        )

    def region_label(self, pos: Pt, text: str, fontsize: float = 14):
        """도형 내부에 영역 레이블을 표시한다 (S₁ 등)."""
        self.ax.text(
            pos[0], pos[1], text,
            fontsize=fontsize, ha="center", va="center",
            style="italic",
        )

    def segment_label(
        self,
        p1: Pt,
        p2: Pt,
        text: str,
        offset: float = 0.3,
        fontsize: float | None = None,
    ):
        """선분의 중점 근처에 레이블을 표시한다.

        offset > 0: 선분 왼쪽(반시계), offset < 0: 오른쪽(시계).
        """
        pos = _perp_offset(p1, p2, offset)
        fs = fontsize or self._label_fontsize
        self.ax.text(pos[0], pos[1], text, fontsize=fs, ha="center", va="center")

    def angle_mark(
        self,
        vertex: Pt,
        p1: Pt,
        p2: Pt,
        label: str | None = None,
        radius: float = 0.5,
        color: str | None = None,
    ):
        """각도 표시 호를 그린다. vertex에서 p1, p2 방향 사이."""
        c = color or self._default_color
        a1 = _angle_of(vertex, p1)
        a2 = _angle_of(vertex, p2)
        if (a2 - a1) % 360 > 180:
            a1, a2 = a2, a1
        arc = patches.Arc(vertex, 2 * radius, 2 * radius, angle=0,
                          theta1=a1, theta2=a2, color=c, linewidth=1.2)
        self.ax.add_patch(arc)
        if label:
            mid_angle = math.radians((a1 + a2) / 2)
            lx = vertex[0] + (radius + 0.3) * math.cos(mid_angle)
            ly = vertex[1] + (radius + 0.3) * math.sin(mid_angle)
            self.ax.text(lx, ly, label, fontsize=11, ha="center", va="center")

    def right_angle(
        self,
        vertex: Pt,
        p1: Pt,
        p2: Pt,
        size: float = 0.3,
        color: str | None = None,
    ):
        """직각 표시 (ㄱ자 모양)."""
        c = color or self._default_color
        d1 = (p1[0] - vertex[0], p1[1] - vertex[1])
        d2 = (p2[0] - vertex[0], p2[1] - vertex[1])
        len1 = math.hypot(*d1)
        len2 = math.hypot(*d2)
        if len1 < 1e-9 or len2 < 1e-9:
            return
        u1 = (d1[0] / len1 * size, d1[1] / len1 * size)
        u2 = (d2[0] / len2 * size, d2[1] / len2 * size)
        corner1 = (vertex[0] + u1[0], vertex[1] + u1[1])
        corner2 = (vertex[0] + u2[0], vertex[1] + u2[1])
        corner3 = (vertex[0] + u1[0] + u2[0], vertex[1] + u1[1] + u2[1])
        self.ax.plot(
            [corner1[0], corner3[0], corner2[0]],
            [corner1[1], corner3[1], corner2[1]],
            color=c, linewidth=1.0,
        )

    def equal_mark(self, p1: Pt, p2: Pt, count: int = 1, size: float = 0.15):
        """선분 위에 같은 길이 표시 (틱 마크)."""
        mx, my = _mid(p1, p2)
        angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
        perp = angle + math.pi / 2
        dx_seg = math.cos(angle)
        dy_seg = math.sin(angle)
        px = math.cos(perp) * size
        py = math.sin(perp) * size
        spacing = 0.1
        for i in range(count):
            offset = (i - (count - 1) / 2) * spacing
            cx = mx + dx_seg * offset
            cy = my + dy_seg * offset
            self.ax.plot(
                [cx - px, cx + px], [cy - py, cy + py],
                color=self._default_color, linewidth=1.2,
            )

    def parallel_mark(self, p1: Pt, p2: Pt, count: int = 1, size: float = 0.15):
        """선분 위에 평행 표시 (화살표 마크)."""
        mx, my = _mid(p1, p2)
        angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
        dx = math.cos(angle)
        dy = math.sin(angle)
        spacing = 0.12
        for i in range(count):
            offset = (i - (count - 1) / 2) * spacing
            cx = mx + dx * offset
            cy = my + dy * offset
            self.ax.annotate(
                "", xy=(cx + dx * size * 0.5, cy + dy * size * 0.5),
                xytext=(cx - dx * size * 0.5, cy - dy * size * 0.5),
                arrowprops=dict(arrowstyle="->", color=self._default_color, lw=1.2),
            )

    def dimension(
        self,
        p1: Pt,
        p2: Pt,
        text: str,
        offset: float = -0.5,
        fontsize: float | None = None,
    ):
        """치수선 (양쪽 화살표 + 텍스트)."""
        o = _perp_offset(p1, p2, offset)
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length < 1e-9:
            return
        nx, ny = -dy / length * offset, dx / length * offset
        ep1 = (p1[0] + nx, p1[1] + ny)
        ep2 = (p2[0] + nx, p2[1] + ny)
        arrow = FancyArrowPatch(
            ep1, ep2, arrowstyle="<->", color=self._default_color,
            linewidth=1.0, mutation_scale=8,
        )
        self.ax.add_patch(arrow)
        fs = fontsize or 12
        mid = _mid(ep1, ep2)
        self.ax.text(
            mid[0], mid[1], text, fontsize=fs, ha="center", va="center",
            bbox=dict(facecolor="white", edgecolor="none", pad=1),
        )

    def brace(
        self,
        p1: Pt,
        p2: Pt,
        text: str,
        direction: str = "below",
        offset: float = 0.6,
        fontsize: float | None = None,
    ):
        """중괄호 치수 표시."""
        sign = -1 if direction == "below" else 1
        dist = sign * offset
        mid = _perp_offset(p1, p2, dist)
        text_pos = _perp_offset(p1, p2, dist * 1.6)
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length < 1e-9:
            return
        nx, ny = -dy / length * dist, dx / length * dist
        ep1 = (p1[0] + nx, p1[1] + ny)
        ep2 = (p2[0] + nx, p2[1] + ny)
        self.ax.annotate("", xy=ep1, xytext=mid,
                         arrowprops=dict(arrowstyle="-", color=self._default_color, lw=0.8))
        self.ax.annotate("", xy=ep2, xytext=mid,
                         arrowprops=dict(arrowstyle="-", color=self._default_color, lw=0.8))
        self.ax.plot([p1[0], ep1[0]], [p1[1], ep1[1]], color=self._default_color, lw=0.6)
        self.ax.plot([p2[0], ep2[0]], [p2[1], ep2[1]], color=self._default_color, lw=0.6)
        fs = fontsize or 12
        self.ax.text(text_pos[0], text_pos[1], text, fontsize=fs, ha="center", va="center")

    # ── 좌표평면 ──────────────────────────────────────

    def coordinate_plane(
        self,
        xlim: tuple[float, float],
        ylim: tuple[float, float],
        grid: bool = True,
        xlabel: str = "$x$",
        ylabel: str = "$y$",
    ):
        """좌표평면을 그린다. 축과 눈금을 표시한다."""
        self.ax.axis("on")
        self.ax.spines["left"].set_position("zero")
        self.ax.spines["bottom"].set_position("zero")
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["top"].set_visible(False)
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.ax.set_xlabel(xlabel, fontsize=12, loc="right")
        self.ax.set_ylabel(ylabel, fontsize=12, loc="top", rotation=0)
        if grid:
            self.ax.grid(True, alpha=0.3, linestyle="--")

    def plot_function(
        self,
        func,
        xlim: tuple[float, float],
        label: str | None = None,
        color: str = "blue",
        linewidth: float = 1.8,
        n_points: int = 300,
    ):
        """함수 y=func(x)의 그래프를 그린다."""
        xs = np.linspace(xlim[0], xlim[1], n_points)
        ys = np.array([func(x) for x in xs])
        self.ax.plot(xs, ys, color=color, linewidth=linewidth, label=label)
        if label:
            self.ax.legend(fontsize=11)

    def plot_points(
        self,
        points: Sequence[Pt],
        labels: Sequence[str] | None = None,
        style: str = "ko",
        size: float = 5,
    ):
        """좌표평면 위에 점들을 찍는다."""
        for i, p in enumerate(points):
            self.ax.plot(p[0], p[1], style, markersize=size)
            if labels and i < len(labels):
                self.ax.text(p[0] + 0.2, p[1] + 0.3, labels[i],
                             fontsize=self._label_fontsize, ha="left", va="bottom")

    # ── 원 / 호 ──────────────────────────────────────

    def arc(
        self,
        center: Pt,
        radius: float,
        angle_start: float,
        angle_end: float,
        style: str = "-",
        color: str | None = None,
        linewidth: float | None = None,
    ):
        """호를 그린다. 각도는 degree 단위."""
        c = color or self._default_color
        lw = linewidth or self._default_lw
        a = patches.Arc(center, 2 * radius, 2 * radius, angle=0,
                        theta1=angle_start, theta2=angle_end,
                        color=c, linewidth=lw, linestyle=style)
        self.ax.add_patch(a)

    def sector(
        self,
        center: Pt,
        radius: float,
        angle_start: float,
        angle_end: float,
        fill: bool = True,
        color: str = "lightblue",
        alpha: float = 0.3,
    ):
        """부채꼴을 그린다."""
        theta = np.linspace(np.radians(angle_start), np.radians(angle_end), 100)
        xs = [center[0]] + [center[0] + radius * np.cos(t) for t in theta] + [center[0]]
        ys = [center[1]] + [center[1] + radius * np.sin(t) for t in theta] + [center[1]]
        if fill:
            self.ax.fill(xs, ys, color=color, alpha=alpha)
        self.ax.plot(xs, ys, color=self._default_color, linewidth=self._default_lw)

    def chord(
        self,
        circle_center: Pt,
        radius: float,
        angle1: float,
        angle2: float,
        label: str | None = None,
        style: str = "-",
    ):
        """원의 현을 그린다. 각도는 degree."""
        p1 = (
            circle_center[0] + radius * math.cos(math.radians(angle1)),
            circle_center[1] + radius * math.sin(math.radians(angle1)),
        )
        p2 = (
            circle_center[0] + radius * math.cos(math.radians(angle2)),
            circle_center[1] + radius * math.sin(math.radians(angle2)),
        )
        self.segment(p1, p2, style=style, label=label)

    def inscribed_polygon(
        self,
        circle_center: Pt,
        radius: float,
        n: int,
        rotation: float = 0,
        labels: Sequence[str] | None = None,
    ):
        """원에 내접하는 정n각형을 그린다."""
        verts = []
        for i in range(n):
            angle = math.radians(rotation + 360 * i / n)
            verts.append((
                circle_center[0] + radius * math.cos(angle),
                circle_center[1] + radius * math.sin(angle),
            ))
        self.polygon(verts, labels=labels)

    # ── 영역 / 채우기 ────────────────────────────────────

    def fill_polygon(
        self,
        vertices: Sequence[Pt],
        color: str = "lightblue",
        alpha: float = 0.3,
    ):
        """다각형 영역을 색으로 채운다."""
        poly = plt.Polygon(vertices, facecolor=color, edgecolor="none", alpha=alpha)
        self.ax.add_patch(poly)

    def shade_region(
        self,
        vertices: Sequence[Pt],
        color: str = "gray",
        alpha: float = 0.2,
    ):
        """영역을 음영 처리한다."""
        self.fill_polygon(vertices, color=color, alpha=alpha)

    def hatch(
        self,
        vertices: Sequence[Pt],
        pattern: str = "///",
        color: str = "gray",
    ):
        """빗금 채우기."""
        poly = plt.Polygon(vertices, facecolor="none", edgecolor=color,
                           hatch=pattern, linewidth=0.5)
        self.ax.add_patch(poly)

    # ── 출력 ──────────────────────────────────────────

    def save(self, path: str, dpi: int = 150, transparent: bool = True):
        """도형을 PNG 파일로 저장한다."""
        self.ax.autoscale()
        margin = 0.5
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.set_xlim(xlim[0] - margin, xlim[1] + margin)
        self.ax.set_ylim(ylim[0] - margin, ylim[1] + margin)
        self.fig.savefig(path, dpi=dpi, bbox_inches="tight",
                         transparent=transparent, pad_inches=0.1)
        plt.close(self.fig)
