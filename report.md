# Assignment 3 Report: Argumentation Engine and Strategic Argumentation

## 1. Overview

The submission implements a finite Dung argumentation framework `A = (Args, Attacks)` and the grounded direct argumentation mechanism. The code is intentionally dependency-free and uses exhaustive enumeration, which is practical for the assignment's small graphs (6-8 arguments).

## 2. Argumentation framework

`ArgumentationFramework` stores arguments as a set and attacks as ordered pairs `(attacker, target)`. Its public operations are:

1. `is_conflict_free(S)` checks that no attack has both endpoints in `S`.
2. `defends(a, S)` checks that every attacker of `a` is attacked by at least one member of `S`.
3. `characteristic(S)` returns every argument defended by `S`.
4. `is_admissible(S)` checks conflict-freeness and `S` is a subset of `characteristic(S)`.
5. `is_complete(S)` checks admissibility and `S = characteristic(S)`.
6. `grounded_extension()` repeatedly applies the characteristic function from the empty set until a fixed point is reached.
7. Complete, preferred, stable and semi-stable extensions are enumerated from all subsets.
8. Complete labellings are generated from complete extensions: members are `in`, attacked arguments are `out`, and the rest are `undec`.
9. Acceptance is reported as skeptical, credulous, or rejected relative to a chosen semantics (preferred by default).

The grounded construction is monotone, so the fixed point is the least complete extension. Preferred extensions are maximal admissible sets. Stable extensions conflict-free attack every argument outside the extension. Semi-stable extensions are complete extensions whose range `S union S+` is maximal.

## 3. Strategic argumentation

`grounded_mechanism` restricts the global attack graph to the union of revealed reports and computes its grounded extension. An agent's utility is the number of its own arguments in that extension.

`best_reports` enumerates every subset of the agent's arguments while keeping the other reports fixed and returns every utility-maximising report. `theorem_5_3_holds` checks that the truthful report is always among these best responses for every possible combination of other agents' reports.

`theorem_5_4_condition` checks whether any agent owns two arguments connected by an odd-length directed path. The search tracks `(node, parity)` states rather than only nodes, so cycles do not cause infinite traversal and odd/even reachability is preserved. `is_strategyproof` independently verifies that no false report gives a strictly larger utility.

## 4. Demonstration

Running `python demo.py` exercises the framework predicates, all extension semantics, labellings, acceptance status, grounded strategic mechanism, best-response enumeration, Theorems 5.3 and 5.4, and the independent strategyproofness check. It also writes `demo_output.html`, which contains an SVG graph with green `in`, red `out`, and gold `undec` nodes plus the computed results. `python test_assignment.py` provides executable checks covering every required function.

## 5. Experiments

`experiments.py` uses seed `20261111` for reproducibility. For each of `p ∈ {0.15, 0.25, 0.35}`, it generates 1,000 random instances with 6-8 arguments, includes each possible directed attack independently with probability `p`, and assigns arguments uniformly across three agents. It records strategyproofness and the Theorem 5.4 condition for each instance in `experiment_results.csv`; aggregate values are in `experiment_summary.csv`.

The two requested discrepancy checks are included in the summary columns. The corresponding `instance_ids` columns list the exact per-`p` instance numbers, so the cases can be located in `experiment_results.csv`:

- `theorem_true_but_strategyproof_false` records counterexamples to sufficiency.
- `strategyproof_true_but_theorem_condition_false` records strategyproof instances where the condition fails, which are possible because the theorem condition is a sufficient structural test rather than a necessary condition for a particular finite instance.

For the reproducible run with seed `20261111`, the measured results were:

| Attack probability | Strategyproof instances | Strategyproof fraction | Theorem 5.4 condition instances | Condition true but not strategyproof | Strategyproof but condition false |
|---:|---:|---:|---:|---:|---:|
| 0.15 | 554/1000 | 0.554 | 142 | 0 | 412 |
| 0.25 | 273/1000 | 0.273 | 27 | 0 | 246 |
| 0.35 | 163/1000 | 0.163 | 5 | 0 | 158 |

Thus, no sampled instance contradicted the sufficient direction tested by Theorem 5.4. There were strategyproof instances where the odd-path condition failed: 412, 246, and 158 for `p = 0.15, 0.25, 0.35`, respectively. These are not contradictions; in those graphs, the potentially harmful odd-path structure does not produce a profitable deviation under the particular reports and grounded outcomes available.

The generated CSV files are the primary numerical evidence. Re-run the experiment after any code change so the report and data remain synchronized.

## 6. Correctness and limitations

The implementation enumerates `2^n` subsets for extensions and reports. This is exact and transparent but not intended for large frameworks. For experiments, `n ≤ 8` makes exhaustive checking feasible. The odd-path test uses finite parity-state reachability and includes self-attacks and directed cycles correctly.

The book corrections supplied in the brief are not hard-coded into the engine; the implementation accepts the corrected examples as ordinary input. This keeps the semantics general and avoids embedding a mistaken utility assignment or the incorrect argument number from the text.

## 7. Reproducibility checklist

```text
python demo.py
python experiments.py
```

Expected outputs are the console extension tables, one HTML visualisation, one per-instance CSV, and one summary CSV. The random seed makes the reported fractions stable across runs with the same Python version.
