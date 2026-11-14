"""Shared font setup for the reportlab PDF builders.

Registers Arial as the font family "A" (regular, bold, italic, bold italic). Looks in the usual macOS and Linux
locations; if Arial isn't installed, falls back to reportlab's built-in Helvetica so the builders still run
(a few symbols such as − and ≈ may then render as boxes).
"""
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FACES = {"A": ("Arial.ttf", "Helvetica"), "A-B": ("Arial Bold.ttf", "Helvetica-Bold"),
         "A-I": ("Arial Italic.ttf", "Helvetica-Oblique"), "A-BI": ("Arial Bold Italic.ttf", "Helvetica-BoldOblique")}
SEARCH = [Path("/System/Library/Fonts/Supplemental"), Path("/Library/Fonts"), Path("/usr/share/fonts/truetype/msttcorefonts")]


def register_arial() -> None:
    folder = next((d for d in SEARCH if (d / "Arial.ttf").exists()), None)
    for name, (ttf, builtin) in FACES.items():
        if folder is not None:
            pdfmetrics.registerFont(TTFont(name, str(folder / ttf)))
        else:
            pdfmetrics.registerFont(pdfmetrics.Font(name, builtin, "WinAnsiEncoding"))
    pdfmetrics.registerFontFamily("A", normal="A", bold="A-B", italic="A-I", boldItalic="A-BI")
