"""Run a readable demonstration and generate an SVG/HTML visualisation."""
from pathlib import Path
from argumentation_engine import (
    ArgumentationFramework,
    best_reports,
    fmt_extension,
    grounded_mechanism,
    is_strategyproof,
    theorem_5_3_holds,
    theorem_5_4_condition,
)


def svg_graph(arguments, attacks, labelling, width=760, height=300):
    positions = {a: (80 + i * (width - 160) / max(1, len(arguments) - 1), 150 + (i % 2) * 35)
                 for i, a in enumerate(arguments)}
    colors = {"in": "#19a974", "out": "#e05252", "undec": "#d9a441"}
    lines = []
    for source, target in attacks:
        x1, y1 = positions[source]; x2, y2 = positions[target]
        lines.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#7b8794" marker-end="url(#arrow)"/>')
    nodes = []
    for a in arguments:
        x, y = positions[a]; status = labelling[a]
        nodes.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="27" fill="{colors[status]}" stroke="#102a43" stroke-width="2"/>')
        nodes.append(f'<text x="{x:.0f}" y="{y + 5:.0f}" text-anchor="middle" fill="white" font-weight="700">{a}</text>')
        nodes.append(f'<text x="{x:.0f}" y="{y + 50:.0f}" text-anchor="middle" fill="#243b53" font-size="12">{status}</text>')
    return f'''<svg viewBox="0 0 {width} {height}" role="img" aria-label="Argumentation graph">
    <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#7b8794"/></marker></defs>{''.join(lines)}{''.join(nodes)}</svg>'''


def main():
    af = ArgumentationFramework(
        ["a", "b", "c", "d", "e"],
        [("a", "b"), ("b", "a"), ("b", "c"), ("c", "d"), ("e", "d")],
    )
    print("ASSIGNMENT 3 - ARGUMENTATION ENGINE DEMO")
    print("Arguments:", sorted(af.arguments))
    print("Attacks:", sorted(af.attacks))
    print("Conflict-free {a, c, e}:", af.is_conflict_free({"a", "c", "e"}))
    print("Defends c from {a}:", af.defends("c", {"a"}))
    print("Characteristic({a}):", fmt_extension(af.characteristic({"a"})))
    print("Admissible {a, c, e}:", af.is_admissible({"a", "c", "e"}))
    print("Complete {a, c, e}:", af.is_complete({"a", "c", "e"}))
    print("Grounded:", fmt_extension(af.grounded_extension()))
    print("Complete:", [fmt_extension(x) for x in af.all_complete_extensions()])
    print("Preferred:", [fmt_extension(x) for x in af.preferred_extensions()])
    print("Stable:", [fmt_extension(x) for x in af.stable_extensions()])
    print("Semi-stable:", [fmt_extension(x) for x in af.semi_stable_extensions()])
    print("Labellings:", af.legal_labellings())
    for arg in sorted(af.arguments):
        print(f"Status({arg}):", af.acceptance_status(arg))

    agents = {"Alice": {"a", "c"}, "Bob": {"b", "d"}, "Cara": {"e"}}
    truthful = {name: set(args) for name, args in agents.items()}
    print("\nSTRATEGIC ARGUMENTATION")
    print("Truthful grounded outcome:", fmt_extension(grounded_mechanism(af.attacks, truthful)))
    print("Alice best reports:", [fmt_extension(x) for x in best_reports("Alice", agents, af.attacks, {"Bob": {"b"}, "Cara": {"e"}})])
    print("Theorem 5.3 holds:", theorem_5_3_holds(af.attacks, agents))
    print("Theorem 5.4 condition:", theorem_5_4_condition(af.attacks, agents))
    print("Strategyproof:", is_strategyproof(af.attacks, agents))

    labelling = af.labelling(af.grounded_extension())
    html = f'''<!doctype html><meta charset="utf-8"><title>Assignment 3 demonstration</title>
    <style>body{{font:16px system-ui;max-width:900px;margin:40px auto;color:#243b53}} svg{{background:#f5f7fa;border-radius:12px;padding:18px}} code{{background:#eef2f7;padding:2px 5px;border-radius:4px}}</style>
    <h1>Argumentation Engine Demonstration</h1><p>Green = in, red = out, gold = undecided.</p>
    {svg_graph(sorted(af.arguments), sorted(af.attacks), labelling)}
    <h2>Computed results</h2><ul><li>Grounded extension: <code>{fmt_extension(af.grounded_extension())}</code></li>
    <li>Complete extensions: <code>{', '.join(fmt_extension(x) for x in af.all_complete_extensions())}</code></li>
    <li>Preferred extensions: <code>{', '.join(fmt_extension(x) for x in af.preferred_extensions())}</code></li>
    <li>Theorem 5.4 condition: <code>{theorem_5_4_condition(af.attacks, agents)}</code></li>
    <li>Theorem 5.3 holds: <code>{theorem_5_3_holds(af.attacks, agents)}</code></li>
    <li>Strategyproof: <code>{is_strategyproof(af.attacks, agents)}</code></li></ul>'''
    Path("demo_output.html").write_text(html, encoding="utf-8")
    print("\nCreated demo_output.html")


if __name__ == "__main__":
    main()
