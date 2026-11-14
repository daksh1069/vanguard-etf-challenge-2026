"""Final Idea 1 review PDF for the team: docs/pitch/WolfPack_Idea1_Final_Review.pdf
Numbers come from scripts/pitch/real_hedged_full.py, scripts/pitch/validate_etf_test_data.py, docs/pitch/PITCH_FACTS_VERIFIED.md and the
files in data/private/web_sources/. Charts from scripts/pitch/final_review_charts.py.
"""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)

from pdf_fonts import register_arial

OUT = "docs/pitch/WolfPack_Idea1_Final_Review.pdf"
register_arial()

RED, INK, MUTED = colors.HexColor("#CC0000"), colors.HexColor("#1F2328"), colors.HexColor("#5B6470")
LIGHT, RULE = colors.HexColor("#F4F5F6"), colors.HexColor("#D9DCE0")
GOOD, BAD, MID = colors.HexColor("#E8F3EC"), colors.HexColor("#FCEBEB"), colors.HexColor("#FBF3E2")
LINK = "#1F5FA8"
W, H = letter
M = 54
CW = W - 2 * M

body = ParagraphStyle("b", fontName="A", fontSize=9.6, leading=13.4, textColor=INK, spaceAfter=5)
small = ParagraphStyle("s", parent=body, fontSize=8.2, leading=11, textColor=MUTED, spaceAfter=4)
cell = ParagraphStyle("c", parent=body, fontSize=8.4, leading=11, spaceAfter=0)
cellc = ParagraphStyle("cc", parent=cell, alignment=TA_CENTER)
head = ParagraphStyle("h", parent=cell, fontName="A-B", textColor=colors.white)
headc = ParagraphStyle("hc", parent=head, alignment=TA_CENTER)
h1 = ParagraphStyle("h1", parent=body, fontName="A-B", fontSize=13, leading=16, spaceBefore=11, spaceAfter=5, keepWithNext=1)
h2 = ParagraphStyle("h2", parent=body, fontName="A-B", fontSize=10.3, leading=13.5, spaceBefore=7, spaceAfter=3, keepWithNext=1)
title = ParagraphStyle("t", parent=body, fontName="A-B", fontSize=20, leading=24, spaceAfter=3)
sub = ParagraphStyle("st", parent=body, fontSize=9.5, textColor=MUTED, spaceAfter=9)
bullet = ParagraphStyle("bl", parent=body, leftIndent=13, bulletIndent=2, spaceAfter=2.5)
src = ParagraphStyle("src", parent=small, leftIndent=14, firstLineIndent=-14, spaceAfter=2)

P = lambda t, s=body: Paragraph(t, s)
B = lambda t: Paragraph(t, bullet, bulletText="•")
A = lambda url, text: f'<a href="{url}" color="{LINK}">{text}</a>'


def tag(k):
    c = {"Real": "#1B6E3C", "Built": "#1F5FA8", "Model": "#9A6200", "Sourced": "#5B3FA0", "Assumption": "#B00020"}[k]
    lab = {"Built": "Built from real prices"}.get(k, k)
    return f'<font name="A-B" color="{c}">[{lab}]</font>'


def table(rows, widths, header=True, extra=(), center_from=None, fs=None):
    st_c = cell if fs is None else ParagraphStyle("cx", parent=cell, fontSize=fs, leading=fs * 1.3)
    st_cc = ParagraphStyle("ccx", parent=st_c, alignment=TA_CENTER)
    out = []
    for r, row in enumerate(rows):
        line = []
        for c, x in enumerate(row):
            if isinstance(x, str):
                cen = center_from is not None and c >= center_from
                if header and r == 0:
                    line.append(Paragraph(x, headc if cen else head))
                else:
                    line.append(Paragraph(x, st_cc if cen else st_c))
            else:
                line.append(x)
        out.append(line)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.5, RULE),
          ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), INK))
    return Table(out, colWidths=widths, repeatRows=1 if header else 0, style=TableStyle(st + list(extra)))


def box(content, bg=LIGHT, bar=RED):
    t = Table([[content]], colWidths=[CW])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("LINEBEFORE", (0, 0), (0, -1), 3, bar),
                           ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t


def footer(c, doc):
    c.saveState()
    c.setFont("A", 7.8)
    c.setFillColor(MUTED)
    c.drawString(M, 28, "Team WolfPack  |  Idea 1 final review pack  |  12 Nov 2026  |  For internal review")
    c.drawRightString(W - M, 28, f"Page {doc.page}")
    c.setStrokeColor(RED)
    c.setLineWidth(1.5)
    c.line(M, H - 34, M + 36, H - 34)
    c.restoreState()


S = []
# ================================================================== page 1
S += [P("Idea 1, final: a USD-hedged short-term international government bond ETF", title),
      P("Team WolfPack  |  Final review pack for the 13 November finals  |  12 November 2026  |  Check this before we build the slides", sub)]
S.append(box([
    P("<b>What this is</b>"),
    P("This replaces the 7 November Idea 1 PDF as our reference. The idea is the same, but the <b>headline evidence is now real prices</b> instead of "
      "the Model C simulation. It also adds Vanguard's own ten-year record for a similar fund, and corrects several numbers (Section 8). "
      "Every figure is labelled by how we know it, and Sections 5 and 6 list every assumption and limitation. <b>Please try to break it before tomorrow.</b>"),
    P(f"Labels: {tag('Real')} observed data from a real fund or market. {tag('Built')} our calculation using only market prices. "
      f"{tag('Model')} simulation. {tag('Sourced')} from a published page, not re-measured. {tag('Assumption')} a choice we made.", small),
]))
S.append(Spacer(1, 7))
S.append(box([
    P("<b>The pitch in one paragraph</b> <font color='#5B6470'>(draft to read aloud)</font>"),
    P("The <b>Vanguard Short-Term International Treasury Index ETF (USD Hedged)</b> <font color='#5B6470'>(working name)</font> holds about 190 short-term "
      "government bonds from developed markets outside the US and hedges the currency back to dollars every month. Today, US investors can buy short-term "
      "foreign government bonds only with currency risk (ISHG, BWZ), or hedged foreign bonds only with long duration (BNDX, 6.4 years). This fund fills that gap. "
      "Rebuilt from real prices, the exposure returned about 1.9% a year over 2016-2025, against 1.8% for US short Treasuries (VGSH). It lost 2.8% in 2022, "
      "against 3.9% for VGSH and 12.8% for BNDX, and its correlation with VGSH was only about 0.7. Vanguard already runs a close cousin in Ireland: "
      "$7.7 billion, a 0.10% fee and a ten-year record of 2.1% a year."),
], bar=INK))
S.append(Spacer(1, 7))
S.append(P("What the real data supports, and what it doesn't", h2))
S.append(table([
    ["Claim", "Verdict", "Evidence"],
    ["Return the same as VGSH or slightly better", "<b>Supported</b>", f"1.94% vs 1.78% a year, 2016-2025 {tag('Built')}; Vanguard's Irish fund 2.29% {tag('Real')}"],
    ["Smaller 2022 loss than US short bonds", "<b>Supported</b>", f"-2.8% vs VGSH -3.9%, BSV -5.5%, BNDX -12.8% {tag('Built')}"],
    ["Diversifies US short rates", "<b>Supported</b>", f"Correlation with VGSH 0.65-0.69 {tag('Built')}"],
    ["Hedging costs US investors money", "<b>Opposite</b>", f"Real forwards paid 0.06-0.52 points a year more than the rate gap {tag('Real')}"],
    ["Lower risk than VGSH", "Not supported", f"Volatility about 1.7% vs 1.6% {tag('Built')}"],
    ["Beats T-bills", "Not supported", f"1.94% vs 2.17% a year, 2016-2025 {tag('Built')}"],
], [168, 70, CW - 238], extra=[("BACKGROUND", (1, 1), (1, 4), GOOD), ("BACKGROUND", (1, 5), (1, 6), BAD)]))

# ================================================================== 1. product
S.append(P("1. The product", ParagraphStyle("h1n", parent=h1, keepWithNext=0)))
S.append(table([
    ["Choice", "Proposal", "Basis"],
    ["Index", "FTSE WGBI Developed Markets 1-3 Years Capped Select (non-US), USD-hedged version",
     f"ISHG tracks the unhedged index. FTSE's factsheet shows unhedged returns only, so a hedged series must be confirmed with FTSE {tag('Sourced')}"],
    ["What it holds", "About 192 government bonds, $823B market value, duration 1.89y, yield 3.30% in local currencies. Entry rating A-/A3. Bills excluded. "
                      "Country cap 21%, and countries above 4.6% together capped at 47%", f"FTSE Russell factsheet, 31 Oct 2026 {tag('Sourced')}"],
    ["Currencies (ISHG today)", "EUR 55.5%, JPY 9.1, GBP 7.3, CAD 4.6, AUD 4.5, KRW 4.5 (added Apr-Nov 2026), ILS 4.4, SGD 3.3, NZD 2.1, NOK 1.6, DKK 1.5, SEK 1.3",
     f"ISHG holdings, 5 Nov 2026; FTSE Russell on Korea {tag('Sourced')}"],
    ["Hedge", "100% rolling 1-month currency forwards, reset monthly", f"Standard practice; BNDX and the Irish fund hedge currency {tag('Assumption')}"],
    ["Fee", "0.07-0.10%", f"BNDX 0.07%, Vanguard's Irish fund 0.10%, SCIN 0.06%; ISHG and BWZ 0.35% {tag('Sourced')}"],
    ["Capacity", "A $10B fund would be about 1.2% of the index's market value", f"{tag('Built')} from the FTSE figure"],
], [80, 216, CW - 296]))
S.append(Spacer(1, 5))
S.append(P("<b>Who it's for.</b> Investors with a US short-bond allocation who want a second set of interest-rate curves without currency risk; advisers following "
           "Vanguard's own guidance of about 30% of bonds in hedged international, who want short duration rather than BNDX's 6.4 years; and holders of ISHG or BWZ "
           f"who don't want currency swings. These are our hypotheses: we haven't surveyed investors {tag('Assumption')}."))

# ================================================================== 2. gap
gap_empty = Table([[Paragraph("<font color='#CC0000'><b>None found</b></font><br/>This fund", cellc)]], colWidths=[170])
S.append(KeepTogether([
    P("2. The gap", h1),
    table([
        ["", "Unhedged (currency risk)", "USD-hedged"],
        ["<b>Short-term (1-3y)</b>", "ISHG ($835M, 0.35%), BWZ ($298M, 0.35%)", gap_empty],
        ["<b>All maturities</b>", "BWX ($1.34B), IGOV ($1.04B)", "BNDX (6.4y, 0.07%), GGOV ($4.39B, active, 0.39%), SCIN (0.06%, new), FLIA (0.25%, check hedging)"],
    ], [110, 190, CW - 300], extra=[("BACKGROUND", (2, 1), (2, 1), BAD), ("VALIGN", (0, 1), (-1, -1), "MIDDLE")], center_from=1),
    Spacer(1, 4),
    P(f"etfdb.com lists only six US-listed \"International Government Bonds\" ETFs (12 Nov export) {tag('Sourced')}. The team's Bloomberg screen (Test D) and our searches "
      "found no short-term hedged one either. Vanguard's US short funds (VBIL, VGUS, VGSH) hold only US Treasuries, and its non-US bond fund (BNDX) spans all maturities. "
      "Outside the US, Vanguard already sells a hedged short-term global bond fund (Section 3.3)."),
]))

# ================================================================== 3. evidence
S.append(P("3. The evidence", h1))
S.append(P("3.1 Hedged 1-3 year non-US government bonds, rebuilt from real prices", h2))
S.append(box([
    P(f"<b>How we built it</b> {tag('Built')}, monthly, February 2015 to October 2026:", cell),
    P("1. <b>Bond returns:</b> ISHG's actual total returns (Yahoo). ISHG holds the unhedged index.", cell),
    P("2. <b>Currency moves:</b> month-end spot rates. Bloomberg for EUR, JPY, GBP, CAD and AUD, from the team's file; Yahoo for the rest.", cell),
    P("3. <b>Hedge carry:</b> real 1-month forwards for the five majors (81% of the fund); the 3-month interest-rate gap for the seven small currencies (FRED/OECD); zero for SGD.", cell),
    P("4. <b>Hedged return</b> = ISHG return - sum of (weight x currency move) + sum of (weight x forward premium). ISHG's 0.35% fee swapped for 0.10%.", cell),
    P("Main case leaves out KRW, which only joined the index in 2026. A 12-currency version is shown too. Script: scripts/pitch/real_hedged_full.py.", cell),
], bar=colors.HexColor("#1F5FA8")))
S.append(Spacer(1, 5))
S.append(table([
    ["Feb 2015 to Oct 2026", "Return a year", "Volatility", "Max drawdown", "2022", "Corr. with VGSH", "vs T-bills a year"],
    ["<b>Hedged 1-3y, 11 currencies (main)</b>", "<b>1.80%</b>", "<b>1.73%</b>", "<b>-4.85%</b>", "<b>-2.76%</b>", "<b>0.69</b>", "<b>-0.32%</b>"],
    ["Hedged 1-3y, all 12 currencies", "1.87%", "1.66%", "-4.15%", "-2.56%", "0.65", "-0.25%"],
    ["ISHG, unhedged (0.35% fee)", "-0.14%", "7.02%", "-24.00%", "-10.95%", "0.50", "-2.02%"],
    ["VGSH (US 1-3y Treasuries)", "1.64%", "1.59%", "-5.31%", "-3.86%", "1.00", "-0.49%"],
    ["BSV (US short-term bonds)", "1.86%", "2.22%", "-7.84%", "-5.49%", "0.94", "-0.26%"],
    ["BNDX (hedged, 6.4y)", "1.73%", "4.21%", "-14.89%", "-12.76%", "0.62", "-0.32%"],
    ["3-month T-bills", "2.15%", "0.56%", "0.00%", "+1.79%", "0.33", "0.00%"],
], [160, 54, 52, 58, 50, 60, CW - 434], center_from=1, extra=[("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#EAF1FB"))]))
S.append(Spacer(1, 4))
S.append(Image("docs/pitch/figures/final_growth.png", width=CW, height=CW * 3.7 / 7.0))
S.append(P("Growth of $100, monthly, February 2015 to October 2026. The hedged series ends at 123, VGSH at 121, BNDX at 122 and T-bills at 128.", small))
S.append(Image("docs/pitch/figures/final_2022.png", width=CW, height=CW * 2.6 / 7.0))
S.append(P("Calendar 2022, the year rates rose fastest: short duration, not hedging, is what protected investors. The hedged short series lost less than VGSH.", small))

S.append(KeepTogether([
    P("3.2 Calendar years, 2016-2025", h2),
    table([
        ["%", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "10y a year", "Std"],
        ["<b>Hedged 1-3y</b>", "1.67", "1.77", "3.12", "2.23", "1.39", "-0.98", "-2.76", "4.37", "3.85", "5.02", "<b>1.94</b>", "2.39"],
        ["Irish fund", "1.93", "1.56", "1.99", "4.45", "3.39", "-0.67", "-5.07", "5.86", "4.42", "5.48", "2.29", "3.28"],
        ["VGSH", "1.10", "0.04", "1.55", "3.52", "3.04", "-0.60", "-3.86", "4.31", "4.01", "5.07", "1.78", "2.74"],
        ["BSV", "1.33", "1.20", "1.34", "4.98", "4.70", "-1.09", "-5.49", "4.89", "3.78", "5.99", "2.11", "3.51"],
        ["BNDX", "4.61", "2.40", "2.81", "7.87", "4.65", "-2.29", "-12.76", "8.78", "3.56", "2.87", "2.08", "6.09"],
        ["T-bills", "0.30", "0.88", "1.90", "2.12", "0.44", "0.04", "1.81", "5.13", "5.12", "4.17", "2.17", "1.96"],
    ], [70] + [33] * 10 + [50, CW - 450], center_from=1, fs=7.6),
    P(f"Hedged 1-3y {tag('Built')}. Irish fund: Vanguard factsheet {tag('Real')}. VGSH, BSV, BNDX: Yahoo total returns {tag('Real')}. T-bills: FRED DTB3. "
      "'Std' is the standard deviation of the ten calendar-year returns. VGSH's 2017 figure from Yahoo looks low and may differ slightly from Vanguard's published return.", small),
]))

S.append(KeepTogether([
    P("3.3 Vanguard already runs a version of this outside the US", h2),
    table([
        ["Vanguard Global Short-Term Bond Index Fund, Institutional Plus USD Hedged Acc (IE00BH65QS77), as of 30 Sep 2026", ""],
        ["Fund size / fee", "$7.72 billion (all share classes) / 0.10% a year"],
        ["Launched", "10 March 2015 (Irish-domiciled UCITS)"],
        ["Returns (net, USD hedged)", "10 years 2.06% a year; 5 years 1.98%; since launch 2.05%; 2022 -5.07%"],
        ["Portfolio", "5,550 bonds; duration 2.7 years; average maturity 2.9 years; average quality AA-; 57.6% government"],
        ["Benchmark", "Bloomberg Global Aggregate ex US MBS 1-5 Year Float Adjusted and Scaled Index, USD hedged"],
    ], [130, CW - 130], extra=[("SPAN", (0, 0), (1, 0))]),
    P(f"Source: {A('https://fund-docs.vanguard.com/Global_Short-Term_Bond_Index_Fund_9376_USD_GE_SW_RETAIL.pdf', 'Vanguard factsheet')} {tag('Real')}. "
      "<b>Why it matters:</b> Vanguard has run hedged short-term global bonds for a decade at a 0.10% fee, at $7.7B. <b>Why it isn't the same product:</b> "
      "it goes out to 5 years and holds US and corporate bonds, so its 2022 loss was bigger and its correlation with VGSH higher (0.86).", small),
]))

S.append(KeepTogether([
    P("3.4 The hedge itself: does hedging cost a US investor money?", h2),
    table([
        ["2015-2026", "EUR", "JPY", "GBP", "CAD", "AUD"],
        ["Real 1M forward minus rate-gap estimate, points a year", "+0.27", "+0.52", "+0.21", "+0.06", "+0.07"],
        ["Monthly standard deviation", "0.28", "0.36", "0.22", "0.18", "0.17"],
    ], [CW - 250, 50, 50, 50, 50, 50], center_from=1),
    P(f"Real forwards (team's Bloomberg file) paid a dollar investor more than the simple interest-rate gap {tag('Real')}. This is the cross-currency basis working in "
      "a US investor's favour. The comparison uses OECD 3-month interbank rates, so treat the direction as solid and the decimals as approximate.", small),
    P(f"The team's Bloomberg Test A (9 Nov) measured hedged 3-month foreign bills against US T-bills after fees, with the day-count correction applied {tag('Real')}. "
      "Over the last 5 years, five countries were <b>+13.0 bp a year</b> on mid prices and <b>+9.9 bp</b> with a 1-pip cost per roll. The Germany/UK/Canada core was "
      "+3.0 and -0.2 bp. Crossing the full Bloomberg spot spread at every roll turns both negative (about -21 to -38 bp), which is why we assume hedges roll through FX swaps. "
      "Most of the gain comes from the yen.", small),
]))

S.append(KeepTogether([
    P("3.5 The 7 November simulation (Model C) against real prices", h2),
    table([
        ["", "Model C (simulation)", "Rebuilt from real prices", "Verdict"],
        ["Return a year", "1.6-1.7% (2013-2026)", "1.6-1.9% (2013 or 2015 to 2026)", "Matches"],
        ["Volatility", "0.85-1.05%", "1.7-1.8%", "<b>Model understated risk</b>"],
        ["2022", "About -2.8% to -3.0%", "-2.6% to -2.8%", "Matches"],
        ["Max drawdown", "-3.2%", "-4.2% to -4.9%", "Model understated"],
        ["Beats T-bills?", "No", "No", "Same"],
    ], [90, 125, 150, CW - 365], center_from=1, extra=[("BACKGROUND", (3, 2), (3, 2), BAD), ("BACKGROUND", (3, 4), (3, 4), BAD)]),
    P(f"Model C got the return and the 2022 result right, but understated risk by about half. Use the real-price numbers on slides and mention Model C only as a "
      f"cross-check {tag('Model')}.", small),
]))

# ================================================================== 4. why now
S.append(KeepTogether([
    P("4. Why now: rates and the curve-slope point", h1),
    table([
        ["Rate (early Nov 2026)", "Level", "Source"],
        ["Fed funds", "3.75-4.00% (effective 3.88%)", f"FRED, per team docs {tag('Sourced')}"],
        ["Bank of England", "<b>4.00%</b> (raised from 3.75% on 5 Nov)", f"{A('https://www.bankofengland.co.uk/monetary-policy-report/2026/November-2026', 'BoE November 2026 report')} {tag('Sourced')}"],
        ["Bank of Japan", "<b>1.25%</b> (raised June and September, held 30 Oct; next 18 Dec)", f"Trading Economics / BoJ (data/private/web_sources) {tag('Sourced')}"],
        ["ECB deposit", "2.50%", f"Team docs, not re-checked {tag('Sourced')}"],
        ["US 2-year / 3-month bill", "4.46% / about 4.05%", f"FRED (5 Nov), per team docs {tag('Sourced')}"],
    ], [120, 200, CW - 320]),
    Spacer(1, 4),
    P("<b>Hedged foreign 2-year yield</b> is roughly the local 2-year yield plus (US overnight rate minus local overnight rate). Its gap to the US 2-year is therefore "
      "the difference in <b>curve slopes</b>, not the rate gap. Euro (all issuers): 3.13% + (3.88% - 2.44%) = 4.57%, against US 4.46%: a gap of +0.11, "
      "which equals the euro slope (3.13 - 2.44 = 0.69) minus the US slope (4.46 - 3.88 = 0.58). Canada: 3.17% + 1.36% = 4.53%, a gap of +0.07. "
      "A Fed cut lowers the hedge carry and US yields together. With central banks moving apart (Japan hiking, the UK hiking, the ECB lower), "
      f"the case is diversification of rate risk, not a yield pickup {tag('Built')}, from team-docs inputs. It ignores the basis and costs."),
]))

# ================================================================== 5. assumptions
S.append(P("5. Assumptions", h1))
S.append(table([
    ["#", "Assumption", "Why", "Effect, and how we tested it"],
    ["A1", "ISHG's returns stand in for the index's bond returns", "Only real 1-3y non-US government return series available",
     "Includes ISHG's trading costs. Its 0.35% fee is swapped for 0.10% (+0.25% a year)"],
    ["A2", "Currency weights fixed at ISHG's 5 Nov 2026 mix for all years", "Historical weights unavailable; index rules changed in Sept 2020",
     "Affects only the hedge. Wrong weights leave some currency unhedged, which adds volatility and is a likely reason ours is a little high"],
    ["A3", "KRW left out of the main case", "Korea entered the index Apr-Nov 2026", "12-currency version: +0.07% a year, slightly lower volatility"],
    ["A4", "Majors hedged at real month-end mid 1M forwards, monthly, with no roll cost", "Team's Bloomberg data; forward spreads 0.2-0.6 pips in calm markets (Test B)",
     "A few bp a year at most in calm markets; spreads widened 3-6 times on average in March 2020"],
    ["A5", "Small currencies (19%): carry from 3-month interbank rate gaps; SGD zero", "No free forward data", "Ignores their basis. SGD at zero slightly understates the return"],
    ["A6", "Yahoo spot rates for the small currencies, and for all currencies before 2015", "No free alternative", "End-of-day timing can differ by up to a day, which adds monthly noise"],
    ["A7", "T-bill return = previous month-end 3-month yield / 12", "Standard", "Bloomberg USGG3M from 2015, FRED DTB3 before"],
    ["A8", "Monthly data only", "Matches a monthly hedge reset", "Monthly drawdowns understate daily ones"],
    ["A9", "Fee 0.10% (0.07% possible)", "Irish fund and BNDX precedents", "Each 0.03% of fee is 3 bp a year of return"],
    ["A10", "No taxes, securities lending or tracking error", "Simplicity", "See limitation L7 on taxes"],
], [24, 150, 140, CW - 314]))

# ================================================================== 6. limitations
S.append(P("6. Limitations", h1))
S.append(table([
    ["#", "Limitation", "What it means for the pitch", "Weight"],
    ["L1", "No track record for this exact fund", "Our series is a rebuild; the Irish fund is a cousin. Say so plainly", "High"],
    ["L2", "One sample, 2015-2026", "Zero rates, then the 2022 shock, with US rates mostly above foreign rates. Another decade could differ", "Medium"],
    ["L3", "Constant weights; index changed in 2020; Korea added in 2026", "Historical exposure is approximate", "Medium"],
    ["L4", "Small-currency basis ignored; SGD carry zero", "Minor (19% of weight, small effects)", "Low"],
    ["L5", "Mixed data sources (Bloomberg extract, Yahoo, FRED/OECD monthly averages)", "Small differences from official figures are possible", "Low"],
    ["L6", "The Irish fund isn't the product", "1-5 years, holds US and corporate bonds; use it as precedent, not as performance", "Medium"],
    ["L7", "Taxes", "Treasury interest is exempt from state tax and this fund's isn't. At about 4% yields that's about 0.2-0.4 points a year for "
                     "taxpayers in high-tax states. Withholding and the tax treatment of hedge gains weren't checked. BNDX has the same trade-off and holds $124B", "High for taxable investors"],
    ["L8", "No published hedged index history", "FTSE's factsheet is unhedged only", "Medium"],
    ["L9", "Stress hedging measured only for five currencies at 3 months (Test B)", "Small currencies in stress are untested", "Medium"],
    ["L10", "Demand evidence is indirect", "Irish fund $7.7B, BNDX $124B, GGOV $4.4B in about 17 months; no investor survey", "Medium"],
    ["L11", "Model C understates risk", "Don't headline Model C", "Low"],
    ["L12", "It doesn't beat T-bills", "Position it as a bond-sleeve diversifier, not a cash product", "High"],
], [24, 150, CW - 244, 70], extra=[("BACKGROUND", (3, 1), (3, 1), BAD), ("BACKGROUND", (3, 7), (3, 7), BAD), ("BACKGROUND", (3, 12), (3, 12), BAD)]))

# ================================================================== 7. claims
claims = Table([[
    [P("<b>We will say</b>", cell)] + [P("• " + t, cell) for t in [
        "The gap is real in the US-listed market (etfdb, Bloomberg screen, searches)",
        "Rebuilt from real prices, the exposure returned about the same as VGSH or slightly more, 2016-2025",
        "It lost less than US short bonds in 2022 (-2.8% vs -3.9%)",
        "Its correlation with US short Treasuries is about 0.7",
        "Hedging hasn't cost US investors; real forwards paid slightly more",
        "Vanguard already runs a similar fund abroad: $7.7B, 0.10%, ten years"]],
    [P("<b>We won't say</b>", cell)] + [P("• " + t, cell) for t in [
        "That it beats T-bills",
        "That it is lower-risk than VGSH",
        "Any Sharpe ratio",
        "That this fund has a track record",
        "That Model C's 0.85-1.05% volatility is real",
        "That a hedged FTSE index series exists, until FTSE confirms it"]],
]], colWidths=[CW / 2, CW / 2])
claims.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), GOOD), ("BACKGROUND", (1, 0), (1, 0), BAD), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LINEAFTER", (0, 0), (0, 0), 2, colors.white)]))
S.append(KeepTogether([P("7. Claims", h1), claims]))

# ================================================================== 8. corrections
S.append(P("8. Corrections to the 7 November Idea 1 PDF", h1))
for t in ["<b>BNDX duration is 6.4 years</b>, not 6.9 (Vanguard's page). BNDX holds $124.2B in the fund and $84.9B in the ETF share class.",
          "<b>Bank of England 4.00%</b> (5 Nov hike); <b>Bank of Japan 1.25%</b> (not 1.0%).",
          "<b>Euro hedged 2-year 4.57%</b> on the all-issuers curve that Model C uses (4.40% was the AAA curve).",
          "<b>The basis helps a US hedger.</b> In stress it widened in the investor's favour; what worsens is the bid-ask on the roll and the cash needed to settle forward losses.",
          "<b>\"Hedge economics reverse if the Fed cuts\" is wrong.</b> Against the US 2-year, the fund wins or loses by the difference in curve slopes (Section 4).",
          "<b>Volatility is about 1.7%</b> on real prices (same as VGSH), not 0.85-1.05%.",
          "<b>The 0.10% fee has a Vanguard precedent</b> (the Irish fund); 0.07% matches BNDX.",
          "<b>Remove</b> the Sharpe tables (they assume a 0% risk-free rate) and the internal agent names (Alpha-2, Gamma-2, Epsilon)."]:
    S.append(B(t))

# ================================================================== 9. Q&A
S.append(P("9. Questions judges are likely to ask", h1))
S.append(table([
    ["Question", "Answer"],
    ["Why not just buy VGSH?", "About the same return and risk, but a different set of central banks (correlation about 0.7). It's the same diversification logic Vanguard uses for BNDX, at short duration."],
    ["Why not BNDX?", "6.4 years' duration: -12.8% in 2022. This keeps the hedge with 1.9 years' duration (-2.8%)."],
    ["Why not ISHG or BWZ?", "Unhedged: -11% in 2022 and 7% volatility, almost all of it currency, plus a 0.35% fee."],
    ["Does it beat T-bills?", "No, and we don't claim it does. It belongs in a bond allocation, not in cash: 1.9% vs 2.2% a year, 2016-2025."],
    ["Doesn't hedging cost money?", "For a US investor it has paid: real forwards earned 0.06-0.52 points a year more than the rate gap, and in our Bloomberg test hedged foreign bills beat T-bills by about 10-13 bp a year after fees across five countries (about 0-3 bp for Germany/UK/Canada alone)."],
    ["What if the Fed cuts?", "The carry and US yields fall together. The fund's edge against the US 2-year is the curve-slope difference, not the rate gap."],
    ["Is there a track record?", "Not for this fund. We rebuilt it from real prices for 2015-2026, and Vanguard's Irish cousin has ten years at 2.1% a year."],
    ["What about taxes?", "Taxable investors give up the state-tax exemption Treasuries enjoy, so the fund suits IRAs, 401(k)s and tax-exempt investors best. BNDX has the same trade-off."],
    ["Can it be run at scale, and in stress?", "The index is $823B, so a $10B fund is about 1.2%. It holds developed-market government bonds and G10 currency forwards. In March 2020, forward-point spreads widened 3-6 times but stayed small in absolute terms (Test B)."],
    ["Why Vanguard?", "It already runs the Irish fund ($7.7B, 0.10%) and BNDX ($124B), so the hedging scale exists. The US lineup lacks this short hedged option."],
    ["Korea?", "It entered the index Apr-Nov 2026. KRW is hedged with non-deliverable forwards, so we could cap it or leave it out."],
], [125, CW - 125]))

# ================================================================== 10. pitch flow + decisions
S.append(KeepTogether([
    P("10. The 15 minutes, and what the team must decide tonight", h1),
    table([
        ["Time", "Slide", "Message"],
        ["0:00", "Hook", "In 2022, hedged international bonds (BNDX) lost 12.8%. Short duration, not hedging, was what protected investors."],
        ["1:30", "The gap", "The two-by-two: short foreign bonds come unhedged, and hedged foreign bonds come long. The short hedged cell is empty in the US."],
        ["4:00", "The product", "What it holds, how the monthly hedge works, fee, capacity."],
        ["6:30", "The evidence", "Rebuilt from real prices: the growth chart and the 2022 bars. About VGSH's return, lower 2022 loss, correlation 0.7."],
        ["9:30", "The hedge", "Hedging didn't cost US investors, and the curve-slope point on rate cuts."],
        ["11:30", "Precedent", "Vanguard's Irish fund: $7.7B, 0.10%, ten years. Bring it home."],
        ["13:00", "Risks", "No track record, taxes, doesn't beat T-bills: we say these ourselves."],
        ["14:30", "Close", "Name, investor, one line."],
    ], [38, 80, CW - 118]),
]))
S.append(Spacer(1, 4))
S.append(box([
    P("<b>Decisions for the team before slides</b>", cell),
    P("1. Fee: 0.07% (matches BNDX) or 0.10% (matches the Irish fund)?  2. KRW: include it or leave it out (NDF hedging)?  3. Working name and ticker.  "
      "4. Who checks which section: Section 3 numbers against the scripts, Section 4 rates against the sources, and the Q&amp;A answers.", cell),
]))

# ================================================================== 11. sources
S.append(P("11. Sources and how to reproduce", h1))
for n, t in enumerate([
    "Built-from-real-prices series: scripts/pitch/real_hedged_full.py writes data/processed/real_hedged_ishg_monthly.csv (Yahoo ISHG/VGSH/BSV/BNDX/BIL, team Bloomberg FX, FRED/OECD rates).",
    "Team's Bloomberg pulls (9 Nov): data/private/bloomberg/etf_test_data.xlsx, independently recomputed in scripts/pitch/validate_etf_test_data.py (formulas matched to 0.00 bp).",
    f"Vanguard Irish fund: {A('https://fund-docs.vanguard.com/Global_Short-Term_Bond_Index_Fund_9376_USD_GE_SW_RETAIL.pdf', 'factsheet, 30 Sep 2026')}; Yahoo NAV 0P00011WU8 (USD Hedged Acc, from 2019).",
    "BNDX page, FTSE WGBI 1-3y factsheet (31 Oct 2026), etfdb category export, and BoJ notes: data/private/web_sources/.",
    f"{A('https://www.bankofengland.co.uk/monetary-policy-report/2026/November-2026', 'Bank of England, November 2026')}; "
    f"{A('https://www.lseg.com/en/media-centre/press-releases/ftse-russell/2025/ftse-russell-country-classification-september-2025', 'FTSE Russell on Korea')}; "
    f"{A('https://advisors.vanguard.com/strategies/fixed-income/bond-funds/international-bond-funds', 'Vanguard on international bonds')}; "
    f"{A('https://vanguard.co.uk/professional/research/going-global-with-bonds', 'Vanguard, Going global with bonds')}.",
    "Model C and its inputs: the team's Idea 1 PDF (7 Nov) and docs/pitch/IDEA1_DATA_SOURCES_AND_CHOICES.md. All figures in one place: docs/pitch/PITCH_FACTS_VERIFIED.md.",
    "Charts: scripts/pitch/final_review_charts.py. This document: scripts/pitch/build_final_review_pdf.py.",
], 1):
    S.append(P(f"[{n}]&nbsp;&nbsp;{t}", src))

doc = BaseDocTemplate(OUT, pagesize=letter, leftMargin=M, rightMargin=M, topMargin=42, bottomMargin=44,
                      title="Idea 1 final review: USD-hedged short-term international government bond ETF", author="Team WolfPack")
doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(M, 44, CW, H - 86, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=footer)])
doc.build(S)
print("wrote", OUT)
