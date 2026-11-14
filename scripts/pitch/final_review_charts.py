"""Charts for the final Idea 1 review PDF (static, light mode, printed)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

OUT = "docs/pitch/figures"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"   # validated categorical slots 1-4, fixed order
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})

d = pd.read_csv("data/processed/real_hedged_ishg_monthly.csv", index_col=0)
d.index = pd.PeriodIndex(d.index, freq="M")
d = d[d.index >= pd.Period("2015-02", "M")]
cols = [("Hedged 1-3y non-US government (built from real prices)", "Hedged ISHG, 11 currencies (ex KRW), fee 0.10%", S1),
        ("VGSH (US 1-3y Treasuries)", "VGSH", S2), ("BNDX (hedged, ~6.4y duration)", "BNDX", S3), ("3-month T-bills", "3M T-bills", S4)]
fig, ax = plt.subplots(figsize=(7.0, 3.7), dpi=200)
x = d.index.to_timestamp()
ends = []
for lab, c, col in cols:
    g = 100 * (1 + d[c].fillna(0)).cumprod()
    ax.plot(x, g, color=col, lw=1.6, label=lab, solid_capstyle="round")
    ends.append([g.iloc[-1], g.iloc[-1], col])
ends.sort(key=lambda e: -e[0])                      # spread end labels so they never overlap
for i in range(1, len(ends)):
    if ends[i - 1][1] - ends[i][1] < 1.7:
        ends[i][1] = ends[i - 1][1] - 1.7
for true_y, y, col in ends:
    ax.annotate(f"{true_y:.0f}", (x[-1], true_y), xytext=(x[-1] + pd.Timedelta(days=75), y), textcoords="data", va="center", fontsize=8, color=INK)
ax.set_ylabel("Value of $100 invested")
ax.grid(axis="y", color=GRID, lw=0.6)
ax.set_xlim(x[0], x[-1] + pd.Timedelta(days=230))
ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=2)
ax.tick_params(length=0)
fig.tight_layout()
fig.savefig(f"{OUT}/final_growth.png")
plt.close(fig)

bars = [("3-month T-bills", 1.81), ("Hedged 1-3y non-US govt (real prices)", -2.76), ("VGSH (US 1-3y Treasuries)", -3.86),
        ("Vanguard Irish hedged short-term fund", -5.07), ("BSV (US short-term bonds)", -5.49), ("BNDX (hedged, ~6.4y)", -12.76)]
fig, ax = plt.subplots(figsize=(7.0, 2.6), dpi=200)
labs, vals = [b[0] for b in bars][::-1], [b[1] for b in bars][::-1]
ax.barh(labs, vals, color=S1, height=0.6, edgecolor="white", linewidth=1)
for i, v in enumerate(vals):
    ax.annotate(f"{v:+.1f}%", (v, i), xytext=(4 if v >= 0 else -4, 0), textcoords="offset points", va="center",
                ha="left" if v >= 0 else "right", fontsize=8, color=INK)
ax.axvline(0, color=INK2, lw=0.8)
ax.set_xlim(-15.5, 4)
ax.set_xlabel("Total return in 2022, %")
ax.grid(axis="x", color=GRID, lw=0.6)
ax.tick_params(length=0)
fig.tight_layout()
fig.savefig(f"{OUT}/final_2022.png")
plt.close(fig)
print("charts written")
