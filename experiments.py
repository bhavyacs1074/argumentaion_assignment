"""Experiments required by Assignment 3."""
from __future__ import annotations
import csv
import random
from pathlib import Path
from argumentation_engine import is_strategyproof, theorem_5_4_condition


def random_instance(rng: random.Random, p: float):
    n = rng.randint(6, 8)
    args = [f"a{i}" for i in range(n)]
    attacks = [(a, b) for a in args for b in args if rng.random() < p]
    shuffled = args[:]
    rng.shuffle(shuffled)
    agents = {f"Agent {i + 1}": set() for i in range(3)}
    for i, arg in enumerate(shuffled):
        agents[f"Agent {(i % 3) + 1}"].add(arg)
    return args, attacks, agents


def run_experiments(instances_per_p=1000, seed=20261111):
    rng = random.Random(seed)
    rows, summary = [], []
    for p in (0.15, 0.25, 0.35):
        strategyproof_count = 0
        theorem_condition_count = 0
        theorem_true_but_sp_false = []
        sp_true_condition_false = []
        theorem_true_but_sp_false_count = 0
        sp_true_condition_false_count = 0
        theorem_true_but_sp_false_ids = []
        sp_true_condition_false_ids = []
        for index in range(instances_per_p):
            args, attacks, agents = random_instance(rng, p)
            sp = is_strategyproof(attacks, agents)
            condition = theorem_5_4_condition(attacks, agents)
            strategyproof_count += sp
            theorem_condition_count += condition
            if condition and not sp:
                theorem_true_but_sp_false_count += 1
                theorem_true_but_sp_false_ids.append(index + 1)
                if len(theorem_true_but_sp_false) < 10:
                    theorem_true_but_sp_false.append((args, attacks, agents))
            if sp and not condition:
                sp_true_condition_false_count += 1
                sp_true_condition_false_ids.append(index + 1)
                if len(sp_true_condition_false) < 10:
                    sp_true_condition_false.append((args, attacks, agents))
            rows.append({"p": p, "instance": index + 1, "strategyproof": sp, "theorem_5_4_condition": condition})
        summary.append({"p": p, "instances": instances_per_p, "strategyproof": strategyproof_count,
                        "strategyproof_fraction": strategyproof_count / instances_per_p,
                        "theorem_condition": theorem_condition_count,
                        "theorem_true_but_strategyproof_false": theorem_true_but_sp_false_count,
                        "theorem_true_but_strategyproof_false_instance_ids": ";".join(map(str, theorem_true_but_sp_false_ids)),
                        "strategyproof_true_but_theorem_condition_false": sp_true_condition_false_count,
                        "strategyproof_true_but_theorem_condition_false_instance_ids": ";".join(map(str, sp_true_condition_false_ids))})
    return rows, summary


def main():
    rows, summary = run_experiments()
    with Path("experiment_results.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0])
        writer.writeheader(); writer.writerows(rows)
    with Path("experiment_summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=summary[0])
        writer.writeheader(); writer.writerows(summary)
    print("p, strategyproof fraction, theorem-5.4 condition count")
    for row in summary:
        print(row["p"], f"{row['strategyproof_fraction']:.3f}", row["theorem_condition"])
    print("Created experiment_results.csv and experiment_summary.csv")


if __name__ == "__main__":
    main()
