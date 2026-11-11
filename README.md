# Assignment 3 - Argumentation Engine

This submission is a complete Python implementation of the Assignment 3 brief.

## Files

- `argumentation_engine.py` - reusable argumentation framework and strategic mechanism.
- `demo.py` - console demonstration and self-contained visual graph (`demo_output.html`).
- `test_assignment.py` - executable checks covering every required function.
- `experiments.py` - the required 3,000-instance experiment (1,000 for each `p`).
- `report.md` - report, design decisions, correctness notes, and experiment discussion.
- `experiment_results.csv`, `experiment_summary.csv` - generated experimental data.

## Run

```text
python demo.py
python test_assignment.py
python experiments.py
```

No third-party Python packages are required. The implementation uses exhaustive subset enumeration, so the experiments are deliberately limited to the assignment's 6-8 argument graphs.

## Semantics implemented

Conflict-free, defence, characteristic function, admissible, complete, grounded, preferred, stable, semi-stable, complete labellings, and skeptical/credulous/rejected status.

## Strategic mechanisms implemented

Grounded direct argumentation, best-response report enumeration, exhaustive verification of Theorem 5.3, odd-length-path verification of Theorem 5.4 with parity-aware cycle handling, and exhaustive strategyproofness checking.
