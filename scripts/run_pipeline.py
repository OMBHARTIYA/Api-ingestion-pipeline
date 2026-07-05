from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    "generate_fake_api_data.py",
    "ingest_raw.py",
    "transform_bronze.py",
    "transform_silver.py",
    "build_gold_summary.py",
    "write_validation_report.py",
]


def main() -> None:
    for step in STEPS:
        print(f"\n=== Running {step} ===")
        subprocess.run([sys.executable, str(ROOT / "scripts" / step)], cwd=ROOT, check=True)

    print("\nPipeline finished successfully.")
    print("Validation report: docs/validation-report.md")


if __name__ == "__main__":
    main()
