"""Flag rollouts that crashed rather than finished.

The paper's grader (reproduce/scripts/grade_precommit_rollouts.py) counts step-*
folders and checks for a git commit. It cannot tell a run that ended because the
agent stopped from one that was killed mid-flight by an API error, so a crashed
run is silently counted as "completed" and graded non-lazy on step count alone.

This does NOT change any of the paper's calculations. It only reports which runs
are safe to include. Run it alongside the grader and exclude the crashed runs by
hand when reporting.

Usage: uv run python scripts/check_complete.py <results_dir>

Lives here rather than in the paper repo so it sits next to run.py, which
produces the rollout.log this reads.
"""
import re
import sys
from pathlib import Path

# The harness prints this block only on a clean exit from the agent loop.
DONE = re.compile(r"FINAL RESULTS|Status:\s*COMPLETED")
CRASH = re.compile(r"Traceback \(most recent call last\)|Error code: \d+|tenacity\.RetryError")


def check(run_dir: Path) -> dict:
    log = run_dir / "rollout.log"
    text = log.read_text(errors="replace") if log.exists() else ""
    steps = len([d for d in run_dir.glob("step-*") if d.is_dir()])
    finished = bool(DONE.search(text))
    crashed = bool(CRASH.search(text)) and not finished
    err = CRASH.search(text).group(0) if crashed else ""
    return {"run": run_dir.name, "steps": steps, "finished": finished,
            "crashed": crashed, "error": err}


def main(results_dir: str) -> None:
    runs = sorted(Path(results_dir).glob("run-*"), key=lambda p: p.name)
    rows = [check(r) for r in runs if r.is_dir()]
    ok = [r for r in rows if r["finished"]]
    bad = [r for r in rows if not r["finished"]]
    for r in sorted(rows, key=lambda x: x["steps"]):
        mark = "ok     " if r["finished"] else "CRASHED"
        print(f"  {r['run']:8s} steps={r['steps']:3d}  {mark}  {r['error']}")
    print(f"\nusable: {len(ok)}/{len(rows)}   excluded (crashed): {len(bad)}")
    if bad:
        print("Exclude these from any rate you report:", ", ".join(r["run"] for r in bad))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
