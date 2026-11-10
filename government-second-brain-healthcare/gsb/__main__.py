"""CLI: python -m gsb --stage 3 --output decision.json"""
import argparse
import json
from pathlib import Path
from .orchestrator import run_simulation


def main() -> None:
    parser = argparse.ArgumentParser(description="Government Second Brain healthcare demo")
    parser.add_argument("--stage", type=int, choices=[1, 2, 3], default=3)
    parser.add_argument("--output", help="Optional JSON results file")
    parser.add_argument("--audit", help="Optional JSONL audit file")
    args = parser.parse_args()
    report = run_simulation(args.stage)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
        print(f"Saved decision evidence to {args.output}")
    else:
        print(payload)
    if args.audit:
        Path(args.audit).write_text("\n".join(json.dumps(a, ensure_ascii=False) for a in report["audit"]) + "\n", encoding="utf-8")
        print(f"Saved audit chain to {args.audit}")


if __name__ == "__main__":
    main()
