"""Render HRV / RHR / weekly running mileage charts from the coros-mcp local cache."""
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager

DB = Path.home() / ".config" / "coros-mcp" / "cache.db"
OUT = Path(__file__).parent
END = datetime(2026, 5, 21)
START = END - timedelta(days=183)

for cjk in ("/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc"):
    if Path(cjk).exists():
        font_manager.fontManager.addfont(cjk)
CJK_NAME = next((font_manager.FontProperties(fname=p).get_name()
                 for p in ("/System/Library/Fonts/Hiragino Sans GB.ttc",
                           "/System/Library/Fonts/STHeiti Medium.ttc")
                 if Path(p).exists()), "DejaVu Sans")

plt.rcParams.update({
    "figure.dpi": 140,
    "font.family": [CJK_NAME, "DejaVu Sans"],
    "axes.unicode_minus": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
})


def parse_day(s: str) -> datetime:
    return datetime.strptime(s, "%Y%m%d")


def load_daily():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT date, data FROM daily_records WHERE date BETWEEN ? AND ? ORDER BY date",
        (START.strftime("%Y%m%d"), END.strftime("%Y%m%d")),
    ).fetchall()
    con.close()
    return [(parse_day(d), json.loads(j)) for d, j in rows]


def load_runs():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT start_day, data FROM activities WHERE start_day BETWEEN ? AND ? ORDER BY start_day",
        (START.strftime("%Y%m%d"), END.strftime("%Y%m%d")),
    ).fetchall()
    con.close()
    out = []
    for d, j in rows:
        rec = json.loads(j)
        if rec.get("sport_type") in (100, 102, 103):
            out.append((parse_day(d), (rec.get("distance_meters") or 0) / 1000.0))
    return out


def chart_hrv(daily, path):
    pts = [(d, r.get("avg_sleep_hrv"), r.get("baseline"))
           for d, r in daily if r.get("avg_sleep_hrv") is not None]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    if pts:
        dates = [p[0] for p in pts]
        hrv = [p[1] for p in pts]
        base = [p[2] for p in pts if p[2] is not None]
        ax.plot(dates, hrv, marker="o", ms=5, lw=1.6, color="#2563eb", label="Nightly HRV (RMSSD)")
        if base:
            base_dates = [p[0] for p in pts if p[2] is not None]
            ax.plot(base_dates, base, lw=1.4, ls="--", color="#94a3b8", label="Baseline")
        avg = sum(hrv) / len(hrv)
        ax.axhline(avg, color="#f59e0b", lw=1, alpha=0.6, label=f"6-mo avg {avg:.1f} ms")
    ax.set_title(f"夜间 HRV 趋势  ({START:%Y-%m-%d} → {END:%Y-%m-%d})   n={len(pts)} 夜",
                 fontsize=13, loc="left", pad=12)
    ax.set_ylabel("HRV (ms, RMSSD)")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.set_xlim(START, END)
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def chart_rhr(daily, path):
    pts = [(d, r.get("rhr")) for d, r in daily if r.get("rhr")]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    if pts:
        dates = [p[0] for p in pts]
        rhr = [p[1] for p in pts]
        ax.plot(dates, rhr, marker=".", ms=4, lw=1, color="#0f766e", alpha=0.55, label="Daily RHR")
        if len(rhr) >= 7:
            window = 7
            ma = [sum(rhr[max(0, i - window + 1): i + 1]) / min(window, i + 1)
                  for i in range(len(rhr))]
            ax.plot(dates, ma, lw=2.2, color="#dc2626", label=f"{window}-day moving avg")
        avg = sum(rhr) / len(rhr)
        ax.axhline(avg, color="#94a3b8", lw=1, ls="--", alpha=0.7, label=f"6-mo avg {avg:.1f} bpm")
    ax.set_title(f"静息心率 (RHR) 趋势  ({START:%Y-%m-%d} → {END:%Y-%m-%d})   n={len(pts)} 天",
                 fontsize=13, loc="left", pad=12)
    ax.set_ylabel("RHR (bpm)")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.set_xlim(START, END)
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def chart_weekly_mileage(runs, path):
    weeks: dict[datetime, float] = {}
    for d, km in runs:
        monday = d - timedelta(days=d.weekday())
        weeks[monday] = weeks.get(monday, 0.0) + km
    if weeks:
        cur = START - timedelta(days=START.weekday())
        last = END - timedelta(days=END.weekday())
        while cur <= last:
            weeks.setdefault(cur, 0.0)
            cur += timedelta(days=7)
    items = sorted(weeks.items())
    fig, ax = plt.subplots(figsize=(11, 4.5))
    if items:
        xs = [w for w, _ in items]
        ys = [km for _, km in items]
        ax.bar(xs, ys, width=5.5, color="#7c3aed", alpha=0.85, label="Weekly km")
        if len(ys) >= 4:
            window = 4
            ma = [sum(ys[max(0, i - window + 1): i + 1]) / min(window, i + 1) for i in range(len(ys))]
            ax.plot(xs, ma, color="#f59e0b", lw=2.4, marker="o", ms=4, label=f"{window}-week moving avg")
        total = sum(ys)
        ax.set_title(f"每周跑量  ({START:%Y-%m-%d} → {END:%Y-%m-%d})   合计 {total:.0f} km / {len(runs)} 次",
                     fontsize=13, loc="left", pad=12)
    ax.set_ylabel("距离 (km)")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.set_xlim(START - timedelta(days=4), END + timedelta(days=4))
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main():
    daily = load_daily()
    runs = load_runs()
    chart_hrv(daily, OUT / "trend_hrv.png")
    chart_rhr(daily, OUT / "trend_rhr.png")
    chart_weekly_mileage(runs, OUT / "trend_weekly_km.png")
    print(f"daily rows={len(daily)}  runs={len(runs)}")
    for p in ("trend_hrv.png", "trend_rhr.png", "trend_weekly_km.png"):
        print(f"  wrote {OUT / p}")


if __name__ == "__main__":
    main()
