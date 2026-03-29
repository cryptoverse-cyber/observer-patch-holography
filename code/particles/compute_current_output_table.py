#!/usr/bin/env python3
"""Build the current particle status surface in a disposable runtime workspace.

This wrapper keeps `reverse-engineering-reality/code/particles` source-only.
It stages a temporary working copy under the top-level `temp/particles_runtime`
directory, runs the active build chain there, and writes the latest rendered
status outputs into `temp/particles_runtime/current`.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


CODE_ROOT = Path(__file__).resolve().parent
RER_ROOT = CODE_ROOT.parents[1]
WORKSPACE_ROOT = CODE_ROOT.parents[2]
DEFAULT_RUNTIME_ROOT = WORKSPACE_ROOT / "temp" / "particles_runtime"

EXCLUDE_NAMES = {
    "__pycache__",
    ".pytest_cache",
    "runs",
    "RESULTS_STATUS.md",
    "results_status.json",
    "particle_mass_derivation_graph.svg",
    "HADRON_SYSTEMATICS_STATUS.md",
}

CURRENT_QUARK_FORWARD = {
    "artifact": "oph_forward_yukawas",
    "public_surface_candidate_allowed": True,
    "source_mode": "factorized_descent",
    "singular_values_u": [
        0.002287663517422587,
        1.2566920642121726,
        172.38864559527133,
    ],
    "singular_values_d": [
        0.005121438948009003,
        0.0916111424053981,
        3.82011787992005,
    ],
}

CURRENT_QUARK_MEAN_SPLIT = {
    "artifact": "oph_quark_sector_mean_split",
    "active_candidate": "ordered_affine_mean_readout_candidate",
}

GROUP_ORDER = ["Bosons", "Leptons", "Quarks", "Hadrons"]
STATUS_COLORS = {
    "structural": "\033[96m",
    "calibration": "\033[36m",
    "secondary_quantitative": "\033[95m",
    "continuation": "\033[33m",
    "simulation_dependent": "\033[91m",
}
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"


def _ignore(_src: str, names: list[str]) -> set[str]:
    return {name for name in names if name in EXCLUDE_NAMES}


def _run(cmd: list[str], *, cwd: Path, verbose: bool) -> None:
    completed = subprocess.run(
        cmd,
        check=False,
        cwd=cwd,
        text=True,
        capture_output=not verbose,
    )
    if completed.returncode != 0:
        if completed.stdout:
            sys.stdout.write(completed.stdout)
        if completed.stderr:
            sys.stderr.write(completed.stderr)
        raise subprocess.CalledProcessError(
            completed.returncode,
            cmd,
            output=completed.stdout,
            stderr=completed.stderr,
        )


def _copy_outputs(work_particles: Path, current_dir: Path) -> None:
    current_dir.mkdir(parents=True, exist_ok=True)
    outputs = [
        "RESULTS_STATUS.md",
        "results_status.json",
        "particle_mass_derivation_graph.svg",
        "runs/status/status_table_forward_current.json",
    ]
    for rel in outputs:
        src = work_particles / rel
        dst = current_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _seed_curated_quark_surface(work_particles: Path) -> None:
    flavor_dir = work_particles / "runs" / "flavor"
    flavor_dir.mkdir(parents=True, exist_ok=True)
    (flavor_dir / "forward_yukawas.json").write_text(
        json.dumps(CURRENT_QUARK_FORWARD, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (flavor_dir / "quark_sector_mean_split.json").write_text(
        json.dumps(CURRENT_QUARK_MEAN_SPLIT, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _read_status_markdown(current_dir: Path) -> str:
    return (current_dir / "RESULTS_STATUS.md").read_text(encoding="utf-8").rstrip()


def _read_status_json(current_dir: Path) -> dict[str, Any]:
    return json.loads((current_dir / "results_status.json").read_text(encoding="utf-8"))


def _use_color(mode: str) -> bool:
    if mode == "always":
        return True
    if mode == "never":
        return False
    return sys.stdout.isatty() and os.environ.get("TERM", "") != "dumb"


def _style(text: str, code: str, *, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{code}{text}{RESET}"


def _status_cell(status: str, *, enabled: bool) -> str:
    color = STATUS_COLORS.get(status, "")
    label = status.replace("_", " ")
    return _style(label, color, enabled=enabled) if color else label


def _flag_cell(value: bool, *, enabled: bool) -> str:
    if value:
        return _style("yes", GREEN, enabled=enabled)
    return _style("no", RED, enabled=enabled)


def _terminal_width() -> int:
    return shutil.get_terminal_size((120, 40)).columns


def _truncate(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    if width <= 1:
        return text[:width]
    return text[: width - 1] + "…"


def _render_box_table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    def hline(left: str, mid: str, right: str) -> str:
        return left + mid.join("─" * (width + 2) for width in widths) + right

    def render_row(values: list[str]) -> str:
        return "│ " + " │ ".join(value.ljust(widths[index]) for index, value in enumerate(values)) + " │"

    parts = [
        hline("┌", "┬", "┐"),
        render_row(headers),
        hline("├", "┼", "┤"),
    ]
    parts.extend(render_row(row) for row in rows)
    parts.append(hline("└", "┴", "┘"))
    return "\n".join(parts)


def _render_terminal_report(payload: dict[str, Any], *, color: bool) -> str:
    width = _terminal_width()
    lines: list[str] = []

    title = "OPH Particle Output Table"
    lines.append(_style(title, BOLD + BLUE, enabled=color))
    lines.append(_style("Current disposable-runtime surface vs PDG/reference values", DIM, enabled=color))
    lines.append("")

    inputs = payload["inputs"]
    lines.append(
        "Inputs: "
        f"P={inputs['P']} | log_dim_H={inputs['log_dim_H']:.0e} | loops={inputs['loops']} | "
        f"with_hadrons={inputs['with_hadrons']} | hadron_profile={inputs['hadron_profile']}"
    )
    surface = payload["surface_state"]
    lines.append(
        "Surface: "
        f"{surface['public_surface_kind']} | policy={surface['surface_policy']}"
    )
    candidates = surface["active_local_public_candidates"]
    lines.append(
        "Candidates: "
        f"D10={_flag_cell(candidates['d10_mass_pair'], enabled=color)} | "
        f"D11={_flag_cell(candidates['d11_forward_seed'], enabled=color)} | "
        f"charged={_flag_cell(candidates['charged_local_candidate'], enabled=color)} | "
        f"neutrinos={_flag_cell(candidates['neutrino_local_candidate'], enabled=color)} | "
        f"quarks={_flag_cell(candidates['quark_forward_candidate'], enabled=color)} | "
        f"hadrons={_flag_cell(candidates['hadrons_enabled'], enabled=color)}"
    )
    lines.append(
        _style(
            "Hadrons stay hidden here because that lane is execution-bound and deferred from the active exact-spectrum program.",
            DIM,
            enabled=color,
        )
    )

    grouped: dict[str, list[dict[str, Any]]] = {group: [] for group in GROUP_ORDER}
    for row in payload["rows"]:
        grouped.setdefault(row["group"], []).append(row)

    headers = ["Particle", "Status", "OPH (GeV)", "Reference", "Delta"]
    max_ref = max(20, min(34, width - 72))
    max_delta = max(14, min(24, width - 96))
    for group in GROUP_ORDER:
        rows = grouped.get(group, [])
        if not rows:
            continue
        lines.append("")
        lines.append(_style(group, BOLD, enabled=color))
        table_rows: list[list[str]] = []
        for row in rows:
            table_rows.append(
                [
                    row["particle"],
                    _status_cell(row["status"], enabled=False),
                    row["prediction_display_gev"],
                    _truncate(row["reference_display"], max_ref),
                    _truncate(row["delta_display"], max_delta),
                ]
            )
        table = _render_box_table(headers, table_rows)
        if color:
            colored_rows = []
            for original, row in zip(rows, table_rows):
                colored_rows.append(
                    [
                        row[0],
                        _status_cell(original["status"], enabled=True),
                        row[2],
                        row[3],
                        row[4],
                    ]
                )
            # Re-render with ANSI status cells while keeping column widths based on raw text.
            raw_widths = [len(header) for header in headers]
            for row in table_rows:
                for index, cell in enumerate(row):
                    raw_widths[index] = max(raw_widths[index], len(cell))

            def hline(left: str, mid: str, right: str) -> str:
                return left + mid.join("─" * (w + 2) for w in raw_widths) + right

            def render_row(values: list[str], raw_values: list[str]) -> str:
                padded = []
                for index, value in enumerate(values):
                    pad = raw_widths[index] - len(raw_values[index])
                    padded.append(value + (" " * pad))
                return "│ " + " │ ".join(padded) + " │"

            parts = [
                hline("┌", "┬", "┐"),
                render_row(headers, headers),
                hline("├", "┼", "┤"),
            ]
            for color_row, raw_row in zip(colored_rows, table_rows):
                parts.append(render_row(color_row, raw_row))
            parts.append(hline("└", "┴", "┘"))
            table = "\n".join(parts)
        lines.append(table)

    generated = payload["generated_utc"]
    lines.append("")
    lines.append(_style(f"Generated: {generated}", DIM, enabled=color))
    return "\n".join(lines).rstrip()


def build_runtime(runtime_root: Path, *, with_hadrons: bool, verbose: bool) -> Path:
    work_code = runtime_root / "work" / "code"
    work_particles = work_code / "particles"
    current_dir = runtime_root / "current"

    if work_code.exists():
        shutil.rmtree(work_code)
    work_code.mkdir(parents=True, exist_ok=True)
    shutil.copytree(CODE_ROOT, work_particles, ignore=_ignore, dirs_exist_ok=True)

    build_steps = [
        ["python3", "particles/calibration/derive_d10_ew_observable_family.py"],
        ["python3", "particles/calibration/derive_d10_ew_source_transport_pair.py"],
        ["python3", "particles/calibration/derive_d10_ew_source_transport_readout.py"],
        ["python3", "particles/calibration/derive_d10_ew_population_evaluator.py"],
        ["python3", "particles/calibration/derive_d10_ew_exact_closure_beyond_current_carrier.py"],
        ["python3", "particles/calibration/derive_d10_ew_fiberwise_population_tree_law_beneath_single_tree_identity.py"],
        ["python3", "particles/calibration/derive_d10_ew_tau2_current_carrier_obstruction.py"],
        ["python3", "particles/calibration/derive_d10_ew_exact_wz_coordinate_beyond_single_tree_identity.py"],
        ["python3", "particles/calibration/derive_d10_ew_exact_mass_pair_chart_current_carrier.py"],
        ["python3", "particles/calibration/derive_d10_ew_repair_branch_beyond_current_carrier.py"],
        ["python3", "particles/calibration/derive_d10_ew_repair_target_point_diagnostic.py"],
        ["python3", "particles/calibration/derive_d10_ew_w_anchor_neutral_shear_factorization.py"],
        ["python3", "particles/calibration/derive_d10_ew_minimal_conditional_promotion.py"],
        ["python3", "particles/calibration/derive_d10_ew_target_emitter_candidate.py"],
        ["python3", "particles/calibration/derive_d10_ew_target_free_repair_value_law.py"],
        ["python3", "particles/calibration/derive_d10_ew_source_transport_readout.py"],
        ["python3", "particles/calibration/derive_d10_ew_exactness_audit.py"],
        ["python3", "particles/calibration/derive_d11_critical_surface_readout.py"],
        ["python3", "particles/calibration/derive_d11_forward_seed.py"],
        ["python3", "particles/calibration/derive_d11_forward_seed_promotion_certificate.py"],
    ]

    if with_hadrons:
        build_steps.extend(
            [
                ["python3", "particles/qcd/derive_lambda_msbar_descendant.py"],
                ["python3", "particles/hadron/derive_full_unquenched_correlator.py"],
                ["python3", "particles/hadron/derive_runtime_schedule_receipt_n_therm_and_n_sep.py"],
                ["python3", "particles/hadron/derive_stable_channel_cfg_source_measure_payload.py"],
                ["python3", "particles/hadron/derive_stable_channel_sequence_population.py"],
                ["python3", "particles/hadron/derive_stable_channel_sequence_evaluation.py"],
                ["python3", "particles/hadron/derive_current_hadron_lane_audit.py"],
            ]
        )

    for step in build_steps:
        _run(step, cwd=work_code, verbose=verbose)

    _seed_curated_quark_surface(work_particles)

    status_cmd = ["python3", "particles/scripts/build_results_status_table.py"]
    svg_cmd = ["python3", "particles/scripts/generate_mass_derivation_svg.py"]
    if with_hadrons:
        status_cmd.append("--with-hadrons")
        svg_cmd.append("--with-hadrons")
    _run(status_cmd, cwd=work_code, verbose=verbose)
    _run(svg_cmd, cwd=work_code, verbose=verbose)
    _copy_outputs(work_particles, current_dir)
    return current_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the current particle status surface in a disposable runtime workspace.")
    parser.add_argument("--runtime-root", default=str(DEFAULT_RUNTIME_ROOT))
    parser.add_argument("--with-hadrons", action="store_true")
    parser.add_argument(
        "--format",
        choices=["terminal", "markdown", "json"],
        default="terminal",
        help="Output format for the rendered surface.",
    )
    parser.add_argument(
        "--color",
        choices=["auto", "always", "never"],
        default="auto",
        help="ANSI color mode for terminal output.",
    )
    parser.add_argument(
        "--no-print-table",
        action="store_true",
        help="Build the runtime surface without printing the rendered output.",
    )
    parser.add_argument(
        "--show-paths",
        action="store_true",
        help="Print the runtime work tree and output directory after the build.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Stream individual builder output instead of running quietly.",
    )
    args = parser.parse_args()

    runtime_root = Path(args.runtime_root).resolve()
    current_dir = build_runtime(runtime_root, with_hadrons=args.with_hadrons, verbose=args.verbose)
    if not args.no_print_table:
        if args.format == "markdown":
            print(_read_status_markdown(current_dir))
        elif args.format == "json":
            print(json.dumps(_read_status_json(current_dir), indent=2))
        else:
            print(_render_terminal_report(_read_status_json(current_dir), color=_use_color(args.color)))
    if args.show_paths:
        if not args.no_print_table:
            print()
        print(f"runtime work tree: {runtime_root / 'work' / 'code' / 'particles'}")
        print(f"current outputs: {runtime_root / 'current'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
