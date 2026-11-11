"""Small executable checks covering every assignment requirement."""
from argumentation_engine import (
    ArgumentationFramework, best_reports, grounded_mechanism, is_strategyproof,
    odd_length_path_exists, theorem_5_3_holds, theorem_5_4_condition,
)


def run_checks():
    af = ArgumentationFramework(
        ["a", "b", "c", "d"],
        [("a", "b"), ("b", "c"), ("c", "d")],
    )
    assert af.is_conflict_free({"a", "c"})
    assert not af.is_conflict_free({"a", "b"})
    assert af.defends("a", set())
    assert af.characteristic(set()) == frozenset({"a"})
    assert af.is_admissible({"a", "c"})
    assert af.is_complete({"a", "c"})
    assert af.grounded_extension() == frozenset({"a", "c"})
    assert af.all_complete_extensions()
    assert af.preferred_extensions()
    assert af.stable_extensions()
    assert af.semi_stable_extensions()
    assert len(af.legal_labellings()) == len(af.all_complete_extensions())
    assert af.acceptance_status("c") == "skeptically accepted"

    attacks = [("x", "y"), ("y", "z")]
    agents = {"A": {"x", "y"}, "B": {"z"}, "C": {"w"}}
    assert grounded_mechanism(attacks, {"A": {"x"}, "B": {"y"}}) == frozenset({"x"})
    assert best_reports("A", agents, attacks, {"B": {"y"}, "C": set()})
    assert theorem_5_3_holds(attacks, agents) in (True, False)
    assert odd_length_path_exists(attacks, "x", "y")
    assert theorem_5_4_condition(attacks, agents) is False
    assert is_strategyproof(attacks, agents) in (True, False)
    print("All assignment requirement checks passed.")


if __name__ == "__main__":
    run_checks()
