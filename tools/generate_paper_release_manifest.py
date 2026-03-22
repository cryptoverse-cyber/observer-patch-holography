#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


RELEASE_INFO_RELATIVE = Path("paper/release_info.tex")
OUTPUT_RELATIVE = Path("paper/paper_release_manifest.json")
RELEASE_TRACKED_PDFS = {
    "observers_are_all_you_need": Path("paper/observers_are_all_you_need.pdf"),
    "reality_as_consensus_protocol": Path("paper/reality_as_consensus_protocol.pdf"),
    "recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact": Path(
        "paper/recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact.pdf"
    ),
    "screen_microphysics_and_observer_synchronization": Path(
        "paper/screen_microphysics_and_observer_synchronization.pdf"
    ),
}


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    release_info = (repo_root / RELEASE_INFO_RELATIVE).read_text(encoding="utf-8")
    release_id = extract_macro(release_info, "OPHPaperReleaseID")
    release_date = extract_macro(release_info, "OPHPaperReleaseDate")

    manifest = {
        "release_id": release_id,
        "released_at": release_date,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "papers": {},
    }
    for paper_id, relative_path in RELEASE_TRACKED_PDFS.items():
        pdf_path = repo_root / relative_path
        manifest["papers"][paper_id] = {
            "pdf_path": str(relative_path),
            "sha256": sha256(pdf_path),
            "size_bytes": pdf_path.stat().st_size,
        }

    output_path = repo_root / OUTPUT_RELATIVE
    previous_manifest = load_existing_manifest(output_path)
    enforce_release_bump(previous_manifest, manifest, args.allow_same_release)
    verify_pdf_release_lines(repo_root, manifest, args.skip_pdf_release_check)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output_path)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write the current release manifest for the synced paper PDFs.",
    )
    parser.add_argument(
        "--allow-same-release",
        action="store_true",
        help="Allow PDF hash changes without bumping the release ID first.",
    )
    parser.add_argument(
        "--skip-pdf-release-check",
        action="store_true",
        help="Skip checking that each local PDF exposes the visible release line.",
    )
    return parser.parse_args()


def extract_macro(text: str, macro_name: str) -> str:
    pattern = re.compile(r"\\newcommand\{\\%s\}\{([^}]*)\}" % re.escape(macro_name))
    match = pattern.search(text)
    if not match:
        raise SystemExit(f"missing macro {macro_name} in release info")
    return match.group(1).strip()


def load_existing_manifest(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def enforce_release_bump(previous_manifest: dict | None, manifest: dict, allow_same_release: bool) -> None:
    if previous_manifest is None or allow_same_release:
        return

    previous_release_id = str(previous_manifest.get("release_id", "")).strip()
    current_release_id = str(manifest.get("release_id", "")).strip()
    if previous_release_id != current_release_id:
        return

    previous_papers = previous_manifest.get("papers", {})
    changed_papers = [
        paper_id
        for paper_id, payload in manifest["papers"].items()
        if previous_papers.get(paper_id, {}).get("sha256") != payload["sha256"]
    ]
    if not changed_papers:
        return

    changed_list = ", ".join(sorted(changed_papers))
    raise SystemExit(
        "PDF hashes changed for the current release ID "
        f"{current_release_id}, but the release was not bumped first: {changed_list}. "
        "Run python3 tools/bump_paper_release.py, rebuild all current paper PDFs, and rerun this command. "
        "Use --allow-same-release only if the unchanged release ID is intentional."
    )


def verify_pdf_release_lines(repo_root: Path, manifest: dict, skip_pdf_release_check: bool) -> None:
    if skip_pdf_release_check:
        return

    release_id = str(manifest["release_id"]).strip()
    missing_release_line: list[str] = []
    tool_failures: list[str] = []
    for paper_id, payload in manifest["papers"].items():
        pdf_path = repo_root / payload["pdf_path"]
        contains_release = pdf_contains_text(pdf_path, f"Paper release: {release_id}")
        if contains_release is True:
            continue
        if contains_release is False:
            missing_release_line.append(paper_id)
        else:
            tool_failures.append(f"{paper_id}: {contains_release}")

    if missing_release_line:
        raise SystemExit(
            "Local PDFs do not expose the current visible release line "
            f"{release_id}: {', '.join(sorted(missing_release_line))}. "
            "Rebuild all current paper PDFs after bumping paper/release_info.tex, then rerun this command. "
            "Every release bump must propagate to every paper PDF so the release IDs stay in sync."
        )

    if tool_failures:
        failures = "; ".join(tool_failures)
        raise SystemExit(
            "Could not verify the visible release line in the local PDFs: "
            f"{failures}. Install pdftotext or rerun with --skip-pdf-release-check."
        )


def pdf_contains_text(path: Path, needle: str) -> bool | str:
    if shutil.which("pdftotext") is None:
        return "pdftotext not installed"
    try:
        result = subprocess.run(
            ["pdftotext", str(path), "-"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        return f"pdftotext failed: {exc}"

    if result.returncode != 0:
        stderr = result.stderr.strip() or f"exit code {result.returncode}"
        return f"pdftotext failed: {stderr}"
    return needle in result.stdout


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
