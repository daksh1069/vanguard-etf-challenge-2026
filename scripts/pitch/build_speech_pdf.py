"""Speech script PDF for the finals deck, built from the deck's own speaker notes so the two never diverge.

Reads the slide files (deck order from deck.json), takes each slide's title and <aside> notes, counts spoken words
(skipping the timing line and any line in parentheses, which are stage directions), and lays out a run sheet with
cumulative timings at 140 words a minute, then the full script.

Usage: python scripts/pitch/build_speech_pdf.py [deck folder, default presentation/deck]
"""
import html, json, re, sys
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from pdf_fonts import register_arial

DECK = Path(sys.argv[1] if len(sys.argv) > 1 else "presentation/deck")
OUT = "presentation/WolfPack_Finals_Speech.pdf"
WPM = 140
register_arial()

INK, MUTED, RED, BLUE, LINE, SOFT = (colors.HexColor(c) for c in ("#14202E", "#5C6470", "#B3122B", "#1F5FA8", "#D9D4CA", "#ECE7DD"))
base = ParagraphStyle("b", fontName="A", fontSize=11, leading=15.5, textColor=INK, spaceAfter=6)
title = ParagraphStyle("t", parent=base, fontName="A-B", fontSize=20, leading=24, spaceAfter=4)
sub = ParagraphStyle("s", parent=base, fontSize=10, textColor=MUTED, spaceAfter=10)
h1 = ParagraphStyle("h1", parent=base, fontName="A-B", fontSize=14, leading=18, spaceBefore=10, spaceAfter=6)
h2 = ParagraphStyle("h2", parent=base, fontName="A-B", fontSize=12, leading=16, spaceBefore=10, spaceAfter=3, textColor=INK)
meta = ParagraphStyle("m", parent=base, fontSize=9.5, textColor=BLUE, spaceAfter=6)
direction = ParagraphStyle("d", parent=base, fontName="A-I", fontSize=10, textColor=MUTED)
cell = ParagraphStyle("c", parent=base, fontSize=9.5, leading=12.5, spaceAfter=0)


def text_of(fragment):
    t = re.sub(r"<br\s*/?>", " ", fragment)
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()


def mmss(sec):
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


deck = json.loads((DECK / "deck.json").read_text())
slides = []
for i, sid in enumerate(deck["order"], 1):
    src = (DECK / f"slides/{sid}.html").read_text()
    m = re.search(r"<h[12][^>]*>(.*?)</h[12]>", src, re.S) or re.search(r'<p class="eyebrow">(.*?)</p>', src, re.S)
    note = re.search(r"<aside>(.*?)</aside>", src, re.S)
    paras = [p.strip() for p in html.unescape(note.group(1)).split("\n\n")] if note else []
    cue, body = (paras[0], paras[1:]) if paras else ("", [])
    spoken = [p for p in body if not p.startswith("(")]
    words = sum(len(p.split()) for p in spoken)
    slides.append({"n": i, "id": sid, "title": text_of(m.group(1)) if m else sid, "cue": cue, "body": body,
                   "words": words, "backup": sid.startswith("b-")})

main = [s for s in slides if not s["backup"]]
t = 0.0
for s in main:
    s["start"], s["secs"] = t, s["words"] / WPM * 60
    t += s["secs"]
total_words = sum(s["words"] for s in main)

S = [Paragraph("WolfPack finals pitch: speech script", title),
     Paragraph(f"Vanguard Short-Term International Treasury Index ETF (USD Hedged) · finals on Teams, 13 November 2026 · "
               f"generated from the deck’s speaker notes", sub),
     Paragraph(f"<b>Length.</b> {len(main)} main slides, {total_words:,} spoken words: about <b>{mmss(total_words / 150 * 60)}</b> at a brisk 150 words "
               f"a minute, <b>{mmss(total_words / WPM * 60)}</b> at 140, and <b>{mmss(total_words / 130 * 60)}</b> at a slower 130. Pauses, slide changes and "
               f"handovers usually add 30–60 seconds, so expect 11–13 minutes, with 2 minutes of margin before the 15-minute limit. "
               f"{len(slides) - len(main)} backup slides follow the close for the Q&amp;A.", base)]

rows = [["#", "Slide", "Words", "Target", f"Starts at ({WPM} wpm)"]]
for s in main:
    rows.append([str(s["n"]), Paragraph(s["title"], cell), str(s["words"]), mmss(s["secs"]), mmss(s["start"])])
rows.append(["", Paragraph("<b>Total</b>", cell), f"{total_words:,}", mmss(t), ""])
tb = Table(rows, colWidths=[0.35 * inch, 3.9 * inch, 0.65 * inch, 0.7 * inch, 1.3 * inch], repeatRows=1)
tb.setStyle(TableStyle([("FONT", (0, 0), (-1, -1), "A", 9.5), ("FONT", (0, 0), (-1, 0), "A-B", 9.5),
                        ("BACKGROUND", (0, 0), (-1, 0), SOFT), ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
                        ("ALIGN", (2, 0), (-1, -1), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
S += [Spacer(1, 6), tb, Spacer(1, 10)]

# suggested three-way split at section boundaries (team can change it)
groups = [("Speaker 1: problem, product, investor", ["cover", "hook", "gap", "product", "how", "who"]),
          ("Speaker 2: the evidence", ["method", "growth", "stress", "hedge"]),
          ("Speaker 3: why now, scale, precedent, risks, close", ["now", "liquidity", "precedent", "risks", "close"])]
split = []
for name, ids in groups:
    w = sum(s["words"] for s in main if s["id"] in ids)
    nums = [s["n"] for s in main if s["id"] in ids]
    split.append(f"<b>{name}</b>: slides {nums[0]}–{nums[-1]}, about {mmss(w / WPM * 60)}")
S.append(Paragraph("<b>A suggested three-way split</b> (change it to fit the team): " + "; ".join(split) + ". "
                   "Hand over with one short line, for example “Now, does it hold up on real prices?”", base))
S.append(Paragraph("<b>Delivery.</b> Say the numbers slowly and round them as the notes do. Pause after the empty cell on slide 3 and after "
                   "the 2022 chart. Lines in grey italics are stage directions, not part of the speech. Rehearse once with a timer: "
                   "if you run long, cut from the liquidity and why-now slides first; the stress, gap and risks slides are the ones judges remember.", base))

S += [PageBreak(), Paragraph("The script", h1)]
for s in main:
    block = [Paragraph(f"Slide {s['n']} · {s['title']}", h2),
             Paragraph(f"{s['cue']} Starts at {mmss(s['start'])} · {s['words']} words", meta)]
    for p in s["body"]:
        block.append(Paragraph(html.escape(p).replace("\n", "<br/>"), direction if p.startswith("(") else base))
    S.append(KeepTogether(block))

S.append(Paragraph("Backup slides (for the Q&amp;A only)", h1))
for s in slides:
    if s["backup"]:
        block = [Paragraph(f"Slide {s['n']} · {s['title']}", h2), Paragraph(html.escape(s["cue"]), meta)]
        block += [Paragraph(html.escape(p), direction if p.startswith("(") else base) for p in s["body"]]
        S.append(KeepTogether(block))


def footer(c, doc):
    c.saveState()
    c.setFont("A", 8.5)
    c.setFillColor(MUTED)
    c.drawString(0.8 * inch, 0.5 * inch, "Team WolfPack · speech script for the 13 November 2026 finals")
    c.drawRightString(letter[0] - 0.8 * inch, 0.5 * inch, str(doc.page))
    c.restoreState()


doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.75 * inch, bottomMargin=0.8 * inch,
                        title="WolfPack finals speech script", author="Team WolfPack")
doc.build(S, onFirstPage=footer, onLaterPages=footer)
print(f"wrote {OUT}: {len(main)} main slides, {total_words} words, {mmss(t)} at {WPM} wpm")
for s in main:
    print(f"  {s['n']:>2} {s['id']:<10} {s['words']:>4} words  {mmss(s['secs'])}  starts {mmss(s['start'])}")
