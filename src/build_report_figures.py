"""Builds the chart images referenced in the project README / case study.

Each chart answers one specific business question raised in reports/findings.md.
Run after src/load_db.py.

Usage:
    python src/build_report_figures.py
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

DB_PATH = Path("data/retail.db")
FIG_DIR = Path("reports/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#333333",
        "axes.grid": True,
        "grid.color": "#e6e6e6",
        "grid.linewidth": 0.8,
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)

ACCENT = "#2563eb"
ACCENT_DARK = "#1e3a8a"
NEUTRAL = "#9ca3af"


def monthly_trend(conn: sqlite3.Connection) -> None:
    df = pd.read_sql_query(Path("sql/01_monthly_revenue_trend.sql").read_text(), conn)
    fig, ax1 = plt.subplots(figsize=(10, 4.5))
    ax1.plot(df["month"], df["net_revenue"], color=ACCENT, linewidth=2.2, marker="o", markersize=3, label="Net revenue")
    ax1.set_ylabel("Net revenue ($)")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    ax1.set_xticks(df.index[::3])
    ax1.set_xticklabels(df["month"][::3], rotation=45, ha="right")

    ax2 = ax1.twinx()
    ax2.plot(df["month"], df["profit_margin_pct"], color=ACCENT_DARK, linewidth=1.6, linestyle="--", label="Profit margin %")
    ax2.set_ylabel("Profit margin (%)")
    ax2.grid(False)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False)

    ax1.set_title("Monthly net revenue and profit margin (2023–2024)", loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "01_monthly_trend.png", dpi=160)
    plt.close(fig)


def regional_performance(conn: sqlite3.Connection) -> None:
    df = pd.read_sql_query(Path("sql/02_regional_performance.sql").read_text(), conn).sort_values("net_revenue")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [ACCENT if r == df["region"].iloc[-1] else NEUTRAL for r in df["region"]]
    ax.barh(df["region"], df["net_revenue"], color=colors)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.2f}M"))
    for y, (val, aov) in enumerate(zip(df["net_revenue"], df["avg_order_value"])):
        ax.text(val, y, f"  \\${val/1e6:.2f}M  ·  AOV \\${aov:.0f}", va="center", fontsize=9)
    ax.set_title("Net revenue by region\nNorth leads, but AOV is flat across regions", loc="left", fontweight="bold", fontsize=12)
    ax.set_xlabel("Net revenue")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "02_regional_performance.png", dpi=160)
    plt.close(fig)


def category_profitability(conn: sqlite3.Connection) -> None:
    df = pd.read_sql_query(Path("sql/03_category_profitability.sql").read_text(), conn).sort_values("profit_margin_pct")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [ACCENT if v == df["profit_margin_pct"].max() else NEUTRAL for v in df["profit_margin_pct"]]
    ax.barh(df["category"], df["profit_margin_pct"], color=colors)
    for y, val in enumerate(df["profit_margin_pct"]):
        ax.text(val, y, f"  {val:.1f}%", va="center", fontsize=9)
    ax.set_title("Profit margin by category\nOffice outperforms on margin despite lower revenue", loc="left", fontweight="bold", fontsize=12)
    ax.set_xlabel("Profit margin (%)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "03_category_profitability.png", dpi=160)
    plt.close(fig)


def return_rate_by_channel(conn: sqlite3.Connection) -> None:
    df = pd.read_sql_query(Path("sql/05_channel_return_rate.sql").read_text(), conn)
    agg = df.groupby("channel").apply(
        lambda g: pd.Series(
            {
                "return_rate_pct": (g["returned_orders"].sum() / g["total_orders"].sum()) * 100,
                "avg_discount_pct": g["avg_discount_pct"].mean(),
            }
        )
    ).reset_index()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = range(len(agg))
    ax.bar(x, agg["return_rate_pct"], color=[ACCENT if c == "Marketplace" else NEUTRAL for c in agg["channel"]])
    ax.set_xticks(list(x))
    ax.set_xticklabels(agg["channel"])
    for i, val in enumerate(agg["return_rate_pct"]):
        ax.text(i, val, f"{val:.1f}%", ha="center", va="bottom", fontsize=10)
    ax.set_title("Return rate by channel\nMarketplace returns run highest alongside deepest discounts", loc="left", fontweight="bold", fontsize=12)
    ax.set_ylabel("Return rate (%)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "04_return_rate_by_channel.png", dpi=160)
    plt.close(fig)


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    monthly_trend(conn)
    regional_performance(conn)
    category_profitability(conn)
    return_rate_by_channel(conn)
    conn.close()
    print(f"Saved 4 figures to {FIG_DIR}/")


if __name__ == "__main__":
    main()
