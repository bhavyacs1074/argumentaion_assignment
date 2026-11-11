"""Assignment 3: argumentation and strategic argumentation engine.

The implementation follows Dung's abstract argumentation semantics and the
grounded direct argumentation mechanism from the assignment brief.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, FrozenSet, Iterable, Iterator, List, Mapping, Sequence, Set, Tuple

Argument = str
Extension = FrozenSet[Argument]
Attack = Tuple[Argument, Argument]  # attacker, target
Labelling = Dict[Argument, str]


@dataclass(frozen=True)
class ArgumentationFramework:
    """A finite argumentation framework A = (Args, Attacks)."""

    arguments: FrozenSet[Argument]
    attacks: FrozenSet[Attack]

    def __init__(self, arguments: Iterable[Argument], attacks: Iterable[Attack] = ()):
        args = frozenset(arguments)
        edges = frozenset((str(a), str(b)) for a, b in attacks)
        invalid = sorted({x for edge in edges for x in edge if x not in args})
        if invalid:
            raise ValueError(f"Attack endpoints are not arguments: {invalid}")
        object.__setattr__(self, "arguments", args)
        object.__setattr__(self, "attacks", edges)

    def attackers(self, argument: Argument) -> FrozenSet[Argument]:
        return frozenset(a for a, b in self.attacks if b == argument)

    def targets(self, argument: Argument) -> FrozenSet[Argument]:
        return frozenset(b for a, b in self.attacks if a == argument)

    def is_conflict_free(self, S: Iterable[Argument]) -> bool:
        chosen = frozenset(S)
        return chosen <= self.arguments and not any(a in chosen and b in chosen for a, b in self.attacks)

    def defends(self, argument: Argument, S: Iterable[Argument]) -> bool:
        chosen = frozenset(S)
        return argument in self.arguments and all(any(defender in chosen for defender in self.attackers(attacker))
                                                  for attacker in self.attackers(argument))

    def characteristic(self, S: Iterable[Argument]) -> Extension:
        chosen = frozenset(S)
        return frozenset(a for a in self.arguments if self.defends(a, chosen))

    def is_admissible(self, S: Iterable[Argument]) -> bool:
        chosen = frozenset(S)
        return self.is_conflict_free(chosen) and chosen <= self.characteristic(chosen)

    def is_complete(self, S: Iterable[Argument]) -> bool:
        chosen = frozenset(S)
        return self.is_admissible(chosen) and self.characteristic(chosen) == chosen

    def grounded_extension(self) -> Extension:
        current: Extension = frozenset()
        while True:
            nxt = self.characteristic(current)
            if nxt == current:
                return current
            current = nxt

    def all_complete_extensions(self) -> List[Extension]:
        return [S for S in self._all_subsets() if self.is_complete(S)]

    def preferred_extensions(self) -> List[Extension]:
        admissible = [S for S in self._all_subsets() if self.is_admissible(S)]
        return [S for S in admissible if not any(S < T for T in admissible)]

    def stable_extensions(self) -> List[Extension]:
        return [S for S in self._all_subsets() if self.is_conflict_free(S) and
                all(a in S or any((s, a) in self.attacks for s in S) for a in self.arguments)]

    def semi_stable_extensions(self) -> List[Extension]:
        complete = self.all_complete_extensions()
        if not complete:
            return []
        ranges = {S: S | frozenset(b for a, b in self.attacks if a in S) for S in complete}
        max_size = max(len(r) for r in ranges.values())
        return [S for S, r in ranges.items() if len(r) == max_size]

    def all_extensions(self) -> Dict[str, List[Extension]]:
        return {
            "grounded": [self.grounded_extension()],
            "complete": self.all_complete_extensions(),
            "preferred": self.preferred_extensions(),
            "stable": self.stable_extensions(),
            "semi-stable": self.semi_stable_extensions(),
        }

    def labelling(self, extension: Iterable[Argument]) -> Labelling:
        ext = frozenset(extension)
        attacked_by_ext = {b for a, b in self.attacks if a in ext}
        return {a: ("in" if a in ext else "out" if a in attacked_by_ext else "undec") for a in sorted(self.arguments)}

    def legal_labellings(self) -> List[Labelling]:
        return [self.labelling(S) for S in self.all_complete_extensions()]

    def acceptance_status(self, argument: Argument, semantics: str = "preferred") -> str:
        extensions = self.all_extensions()[semantics]
        if not extensions or all(argument not in S for S in extensions):
            return "rejected"
        if all(argument in S for S in extensions):
            return "skeptically accepted"
        return "credulously accepted"

    def _all_subsets(self) -> Iterator[Extension]:
        args = sorted(self.arguments)
        for mask in range(1 << len(args)):
            yield frozenset(args[i] for i in range(len(args)) if mask & (1 << i))


def grounded_mechanism(global_attacks: Iterable[Attack], reports: Mapping[str, Iterable[Argument]]) -> Extension:
    """Return the grounded extension induced by the union of revealed reports."""
    revealed = frozenset(a for report in reports.values() for a in report)
    return ArgumentationFramework(revealed, ((a, b) for a, b in global_attacks if a in revealed and b in revealed)).grounded_extension()


def best_reports(agent: str, own_arguments: Mapping[str, Iterable[Argument]],
                 global_attacks: Iterable[Attack], fixed_reports: Mapping[str, Iterable[Argument]]) -> List[Extension]:
    """Return all reports by agent that maximise accepted own arguments."""
    names = list(own_arguments)
    if agent not in own_arguments:
        raise KeyError(agent)
    own = frozenset(own_arguments[agent])
    others = {k: frozenset(v) for k, v in fixed_reports.items() if k != agent}
    candidates: List[Tuple[Extension, Extension]] = []
    items = sorted(own)
    for mask in range(1 << len(items)):
        report = frozenset(items[i] for i in range(len(items)) if mask & (1 << i))
        reports = {**others, agent: report}
        accepted = grounded_mechanism(global_attacks, reports) & own
        candidates.append((report, accepted))
    max_utility = max(len(accepted) for _, accepted in candidates)
    return [report for report, accepted in candidates if len(accepted) == max_utility]


def theorem_5_3_holds(global_attacks: Iterable[Attack], agents: Mapping[str, Iterable[Argument]]) -> bool:
    """Exhaustively verify truthful reporting is a best response for every profile."""
    names = list(agents)
    domains = [list(_powerset(frozenset(agents[n]))) for n in names]
    for i, name in enumerate(names):
        others = [n for n in names if n != name]
        other_domains = [list(_powerset(frozenset(agents[n]))) for n in others]
        for profile in _product(other_domains):
            fixed = dict(zip(others, profile))
            truthful = frozenset(agents[name])
            truthful_ext = grounded_mechanism(global_attacks, {**fixed, name: truthful})
            truthful_utility = len(truthful_ext & truthful)
            for report in domains[i]:
                candidate_ext = grounded_mechanism(global_attacks, {**fixed, name: report})
                if len(candidate_ext & truthful) > truthful_utility:
                    return False
    return True


def odd_length_path_exists(attacks: Iterable[Attack], source: Argument, target: Argument) -> bool:
    """Check for an odd-length directed walk, tracking parity to handle cycles."""
    adjacency: Dict[Argument, Set[Argument]] = {}
    for a, b in attacks:
        adjacency.setdefault(a, set()).add(b)
    todo: List[Tuple[Argument, int]] = [(source, 0)]
    seen = {(source, 0)}
    while todo:
        node, parity = todo.pop(0)
        for nxt in adjacency.get(node, set()):
            state = (nxt, parity ^ 1)
            if nxt == target and state[1] == 1:
                return True
            if state not in seen:
                seen.add(state)
                todo.append(state)
    return False


def theorem_5_4_condition(global_attacks: Iterable[Attack], agents: Mapping[str, Iterable[Argument]]) -> bool:
    """Return True iff no agent owns two arguments joined by an odd path."""
    attacks = frozenset(global_attacks)
    for owned in agents.values():
        args = sorted(set(owned))
        for source, target in combinations(args, 2):
            if odd_length_path_exists(attacks, source, target) or odd_length_path_exists(attacks, target, source):
                return False
    return True


def is_strategyproof(global_attacks: Iterable[Attack], agents: Mapping[str, Iterable[Argument]]) -> bool:
    """Exhaustive strategyproofness test: no report can improve utility."""
    names = list(agents)
    domains = {n: list(_powerset(frozenset(agents[n]))) for n in names}
    for focal in names:
        others = [n for n in names if n != focal]
        own = frozenset(agents[focal])
        for profile in _product([domains[n] for n in others]):
            fixed = dict(zip(others, profile))
            truthful_ext = grounded_mechanism(global_attacks, {**fixed, focal: own})
            truthful_utility = len(truthful_ext & own)
            for report in domains[focal]:
                candidate_ext = grounded_mechanism(global_attacks, {**fixed, focal: report})
                if len(candidate_ext & own) > truthful_utility:
                    return False
    return True


def _powerset(items: FrozenSet[Argument]) -> Iterator[Extension]:
    values = sorted(items)
    for mask in range(1 << len(values)):
        yield frozenset(values[i] for i in range(len(values)) if mask & (1 << i))


def _product(domains: Sequence[Sequence[Extension]]) -> Iterator[Tuple[Extension, ...]]:
    if not domains:
        yield ()
        return
    for head in domains[0]:
        for tail in _product(domains[1:]):
            yield (head, *tail)


def fmt_extension(extension: Iterable[Argument]) -> str:
    return "{" + ", ".join(sorted(extension)) + "}"
