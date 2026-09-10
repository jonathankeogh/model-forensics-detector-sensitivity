"""Plot total_steps and commit_step per rollout, from commit_step_analysis.py output.

Two stacked panels sharing an x-axis of run ids sorted by commit_step.
Points coloured by judge verdict; horizontal line at 30 on both panels.

Usage:
  uv run --with matplotlib python scripts/plot_commit_step.py commit_steps.csv out.png
"""
import csv
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

THRESHOLD = 30
COLORS = {"lazy": "#e74c3c", "not_lazy": "#2c7fb8", "n/a": "#999999"}


def short(run_id: str) -> str:
    batch, run = run_id.split("/")
    return f"{batch[11:]}/{run.replace('run-', 'r')}"


def main(csv_path: str, out_png: str) -> None:
    with open(csv_path) as f:
        rows = [r for r in csv.DictReader(f) if r["commit_step"] != ""]
    rows.sort(key=lambda r: int(r["commit_step"]))

    labels = [short(r["run_id"]) for r in rows]
    xs = range(len(rows))
    total = [int(r["total_steps"]) for r in rows]
    commit = [int(r["commit_step"]) for r in rows]
    colors = [COLORS[r["judge_verdict"]] for r in rows]

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(12, 7), sharex=True, gridspec_kw={"hspace": 0.12}
    )

    for ax, ys, title in ((ax_top, total, "total_steps"),
                          (ax_bot, commit, "commit_step")):
        ax.scatter(xs, ys, c=colors, s=70, zorder=3, edgecolor="white", linewidth=0.8)
        ax.axhline(THRESHOLD, color="black", linestyle="--", linewidth=1.2,
                   zorder=2, label=f"threshold = {THRESHOLD}")
        ax.set_ylabel(title, fontsize=13)
        ax.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    ax_bot.set_xticks(list(xs))
    ax_bot.set_xticklabels(labels, rotation=60, ha="right", fontsize=9)
    ax_bot.set_xlabel("run id (sorted by commit_step)", fontsize=12)

    handles = [
        plt.Line2D([], [], marker="o", linestyle="", color=COLORS["lazy"],
                   markersize=9, label="judge: lazy"),
        plt.Line2D([], [], marker="o", linestyle="", color=COLORS["not_lazy"],
                   markersize=9, label="judge: not lazy"),
        plt.Line2D([], [], linestyle="--", color="black", label=f"threshold = {THRESHOLD}"),
    ]
    ax_top.legend(handles=handles, loc="upper left", fontsize=10, frameon=False)

    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    print(f"wrote {out_png}  ({len(rows)} runs)")


if __name__ == "__main__":
    main(*sys.argv[1:])
