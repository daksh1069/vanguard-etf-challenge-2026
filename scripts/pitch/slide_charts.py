"""Charts for the finals deck (16:9 slides). Sized so that, shown at half their pixel size on a 1920x1080 slide,
text is at least 24px. Transparent background so they sit on the slide's paper colour.
Data: data/processed/real_hedged_ishg_monthly.csv (scripts/pitch/real_hedged_full.py)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

OUT = "presentation/figures"
INK, INK2, GRID, NEUTRAL = "#14202E", "#46505C", "#D9D4CA", "#B3ACA0"
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"   # validated categorical slots 1-4, fixed order
FS = 18                                                          # 18pt at dpi 200 shown at 50% = 25px on the slide
plt.rcParams.update({"font.family": "Arial", "font.size": FS, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.spines.left": False, "savefig.transparent": True})

d = pd.read_csv("data/processed/real_hedged_ishg_monthly.csv", index_col=0)
d.index = pd.PeriodIndex(d.index, freq="M")
d = d[d.index >= pd.Period("2015-02", "M")]

# ---- growth of $100 (slide: 1080 x 600 px)
cols = [("Hedged 1-3y non-US govt (our fund, rebuilt)", "Hedged ISHG, 11 currencies (ex KRW), fee 0.10%", S1, 3.0),
        ("VGSH (US 1-3y Treasuries)", "VGSH", S2, 2.2), ("BNDX (hedged, 6.4y duration)", "BNDX", S3, 2.2),
        ("3-month T-bills", "3M T-bills", S4, 2.2)]
fig, ax = plt.subplots(figsize=(10.8, 6.0), dpi=200)
x = d.index.to_timestamp()
ends = []
for lab, c, col, lw in cols:
    g = 100 * (1 + d[c].fillna(0)).cumprod()
    ax.plot(x, g, color=col, lw=lw, label=lab, solid_capstyle="round")
    ends.append([g.iloc[-1], g.iloc[-1], col])
ends.sort(key=lambda e: -e[0])
for i in range(1, len(ends)):                     # keep end labels apart
    if ends[i - 1][1] - ends[i][1] < 2.4:
        ends[i][1] = ends[i - 1][1] - 2.4
for true_y, y, col in ends:
    ax.annotate(f"{true_y:.0f}", (x[-1], true_y), xytext=(x[-1] + pd.Timedelta(days=90), y), textcoords="data",
                va="center", fontsize=FS, color=INK, fontweight="bold")
ax.set_ylabel("Value of $100, Feb 2015 start")
ax.grid(axis="y", color=GRID, lw=1)
ax.set_xlim(x[0], x[-1] + pd.Timedelta(days=330))
ax.set_ylim(94, 138)
ax.legend(frameon=False, fontsize=FS - 1, loc="upper left", ncol=1, handlelength=1.4, borderaxespad=0.2)
ax.tick_params(length=0)
fig.tight_layout()
fig.savefig(f"{OUT}/slide_growth.png")
plt.close(fig)

# ---- 2022 total returns (slide: 960 x 560 px)
bars = [("3-month T-bills", 1.81, NEUTRAL), ("Our fund (hedged 1-3y, rebuilt)", -2.76, S1), ("VGSH, US 1-3y Treasuries", -3.86, NEUTRAL),
        ("Vanguard Irish hedged 1-5y fund", -5.07, NEUTRAL), ("BSV, US short-term bonds", -5.49, NEUTRAL), ("BNDX, hedged, 6.4y", -12.76, NEUTRAL)]
fig, ax = plt.subplots(figsize=(9.6, 5.6), dpi=200)
labs, vals, cs = [b[0] for b in bars][::-1], [b[1] for b in bars][::-1], [b[2] for b in bars][::-1]
ax.barh(labs, vals, color=cs, height=0.62, edgecolor="none")
for i, v in enumerate(vals):
    ax.annotate(f"{v:+.1f}%", (v, i), xytext=(8 if v >= 0 else -8, 0), textcoords="offset points", va="center",
                ha="left" if v >= 0 else "right", fontsize=FS, color=INK, fontweight="bold")
ax.axvline(0, color=INK2, lw=1.2)
ax.set_xlim(-17, 4.5)
ax.set_xlabel("Total return in calendar 2022, %")
ax.grid(axis="x", color=GRID, lw=1)
ax.set_axisbelow(True)
ax.tick_params(length=0)
ax.spines["bottom"].set_visible(False)
for t in ax.get_yticklabels():
    if t.get_text().startswith("Our fund"):
        t.set_color(INK); t.set_fontweight("bold")
fig.tight_layout()
fig.savefig(f"{OUT}/slide_2022.png")
plt.close(fig)
print("slide charts written")
