#!/usr/bin/env python3
"""Command-line lab runner for perf-mystery."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BUILD_ROOT = ROOT / "build"
RUNS_ROOT = ROOT / "runs"

PUZZLES = {
    "01": {
        "slug": "01-syscall-storm",
        "name": "Syscall Storm",
        "category": "syscall overhead",
        "objective": "Learn when strace is more useful than perf.",
        "language": "c",
        "input": "input/data.txt",
        "quiz": [
            {
                "question": "What bottleneck category is this?",
                "choices": ["Syscall overhead", "Cache locality", "Branch prediction"],
                "answer": 1,
                "explanation": "One-byte reads spend most of their time crossing the kernel boundary.",
            },
            {
                "question": "Which tool gives the strongest evidence?",
                "choices": ["strace -c", "perf report", "A disk capacity tool"],
                "answer": 1,
                "explanation": "strace -c counts calls and time by syscall.",
            },
            {
                "question": "Which output pattern matters most?",
                "choices": [
                    "A huge read() call count",
                    "A high branch-miss rate",
                    "A large executable file",
                ],
                "answer": 1,
                "explanation": "Millions of read() calls for one file expose the one-byte I/O pattern.",
            },
        ],
    },
    "02": {
        "slug": "02-cache-maze",
        "name": "Cache Maze",
        "category": "memory locality",
        "objective": "Recognize pointer chasing and poor locality in perf evidence.",
        "language": "cpp",
        "quiz": [
            {
                "question": "What bottleneck category is this?",
                "choices": ["Syscall overhead", "Poor memory locality", "Lock contention"],
                "answer": 2,
                "explanation": "Dependent accesses jump through a randomized node layout.",
            },
            {
                "question": "Which tool gives the strongest evidence?",
                "choices": ["strace -c", "perf stat -d and perf record -g", "du"],
                "answer": 2,
                "explanation": "perf exposes CPU, cache, TLB, and hot-function behavior.",
            },
            {
                "question": "Which metric pattern matters most?",
                "choices": [
                    "Many open() calls",
                    "Lower IPC with worse cache/TLB symptoms",
                    "High branch misses only",
                ],
                "answer": 2,
                "explanation": "Random dependent loads stall execution and reduce useful work per cycle.",
            },
        ],
    },
    "03": {
        "slug": "03-branch-lottery",
        "name": "Branch Lottery",
        "category": "branch misprediction",
        "objective": "Identify unpredictable branches with hardware counters.",
        "language": "c",
        "quiz": [
            {
                "question": "What bottleneck category is this?",
                "choices": ["Branch misprediction", "Syscall overhead", "Disk latency"],
                "answer": 1,
                "explanation": "The data makes the hot branch close to a random 50/50 decision.",
            },
            {
                "question": "Which tool gives the strongest evidence?",
                "choices": ["strace -c", "perf stat with branch events", "ls -l"],
                "answer": 2,
                "explanation": "Hardware branch and branch-miss counters directly test the hypothesis.",
            },
            {
                "question": "Which metric matters most?",
                "choices": [
                    "read() call count",
                    "Branch misses as a percentage of branches",
                    "Page-cache file size",
                ],
                "answer": 2,
                "explanation": "A high miss rate in the bad version is the defining evidence.",
            },
        ],
    },
}

ALIASES = {meta["slug"]: puzzle_id for puzzle_id, meta in PUZZLES.items()}


class LabError(RuntimeError):
    pass


def resolve_id(value: str) -> str:
    normalized = value.zfill(2) if value.isdigit() else value
    puzzle_id = normalized if normalized in PUZZLES else ALIASES.get(normalized)
    if puzzle_id is None:
        choices = ", ".join(PUZZLES)
        raise LabError(f"unknown puzzle {value!r}; choose one of: {choices}")
    return puzzle_id


def puzzle_dir(puzzle_id: str) -> Path:
    return ROOT / "puzzles" / PUZZLES[puzzle_id]["slug"]


def binary_path(puzzle_id: str, variant: str) -> Path:
    return BUILD_ROOT / puzzle_id / variant


def require_program(name: str, purpose: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise LabError(
            f"{name} is not installed or not on PATH. Install it to {purpose}; "
            "on Debian/Ubuntu, use the system package manager."
        )
    return path


def run_checked(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, check=True, text=True, **kwargs)
    except FileNotFoundError as exc:
        raise LabError(f"could not run {command[0]!r}: {exc}") from exc
    except subprocess.CalledProcessError as exc:
        raise LabError(f"command failed with exit status {exc.returncode}: {' '.join(command)}") from exc


def ensure_input(puzzle_id: str) -> None:
    input_rel = PUZZLES[puzzle_id].get("input")
    if input_rel is None:
        return
    destination = puzzle_dir(puzzle_id) / str(input_rel)
    if destination.exists():
        return
    generator = destination.parent / "make_input.py"
    print(f"Generating deterministic input: {destination.relative_to(ROOT)}", flush=True)
    run_checked([sys.executable, str(generator), str(destination)])


def build_puzzle(puzzle_id: str) -> None:
    meta = PUZZLES[puzzle_id]
    ensure_input(puzzle_id)
    output_dir = BUILD_ROOT / puzzle_id
    output_dir.mkdir(parents=True, exist_ok=True)

    if meta["language"] == "c":
        compiler = require_program("gcc", "compile the C puzzles")
        flags = [
            "-O3",
            "-fno-omit-frame-pointer",
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
        ]
        extension = "c"
    else:
        compiler = require_program("g++", "compile the C++ puzzles")
        flags = [
            "-O3",
            "-fno-omit-frame-pointer",
            "-std=c++17",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
        ]
        extension = "cpp"

    for variant in ("bad", "fixed"):
        source = puzzle_dir(puzzle_id) / "src" / f"{variant}.{extension}"
        output = binary_path(puzzle_id, variant)
        command = [compiler, *flags, str(source), "-o", str(output)]
        print(f"Building {puzzle_id} {variant}: {' '.join(command)}")
        run_checked(command)


def ensure_built(puzzle_id: str, variant: str) -> Path:
    binary = binary_path(puzzle_id, variant)
    if not binary.exists():
        build_puzzle(puzzle_id)
    ensure_input(puzzle_id)
    return binary


def benchmark_command(puzzle_id: str, variant: str) -> list[str]:
    command = [str(ensure_built(puzzle_id, variant))]
    input_rel = PUZZLES[puzzle_id].get("input")
    if input_rel is not None:
        command.append(str(puzzle_dir(puzzle_id) / str(input_rel)))
    return command


def timed_run(puzzle_id: str, variant: str, *, show_output: bool) -> tuple[float, str]:
    command = benchmark_command(puzzle_id, variant)
    started = time.perf_counter()
    result = run_checked(command, capture_output=True)
    elapsed = time.perf_counter() - started
    output = result.stdout.strip()
    if show_output and output:
        print(output)
    return elapsed, output


def command_list(_: argparse.Namespace) -> None:
    print("ID  Name             Category              Learning objective")
    print("--  ---------------  --------------------  ----------------------------------------------")
    for puzzle_id, meta in PUZZLES.items():
        print(
            f"{puzzle_id}  {meta['name']:<15}  {meta['category']:<20}  {meta['objective']}"
        )


def command_build(args: argparse.Namespace) -> None:
    build_puzzle(resolve_id(args.id))


def command_run(args: argparse.Namespace) -> None:
    puzzle_id = resolve_id(args.id)
    elapsed, _ = timed_run(puzzle_id, args.variant, show_output=True)
    print(f"Elapsed wall time: {elapsed:.3f} s")


def command_compare(args: argparse.Namespace) -> None:
    puzzle_id = resolve_id(args.id)
    bad_time, bad_output = timed_run(puzzle_id, "bad", show_output=False)
    fixed_time, fixed_output = timed_run(puzzle_id, "fixed", show_output=False)
    if bad_output != fixed_output:
        raise LabError(
            "bad and fixed variants produced different results:\n"
            f"  bad:   {bad_output}\n"
            f"  fixed: {fixed_output}"
        )
    speedup = bad_time / fixed_time if fixed_time > 0 else float("inf")
    print(f"Result: {bad_output}")
    print(f"bad:    {bad_time:.3f} s")
    print(f"fixed:  {fixed_time:.3f} s")
    print(f"speedup: {speedup:.2f}x")


def variant_run_dir(puzzle_id: str, variant: str) -> Path:
    destination = RUNS_ROOT / puzzle_id / variant
    destination.mkdir(parents=True, exist_ok=True)
    return destination


def command_strace(args: argparse.Namespace) -> None:
    puzzle_id = resolve_id(args.id)
    strace = require_program("strace", "profile syscall behavior")
    destination = variant_run_dir(puzzle_id, args.variant) / "strace-summary.txt"
    destination.unlink(missing_ok=True)
    command = [
        strace,
        "-c",
        "-o",
        str(destination),
        "--",
        *benchmark_command(puzzle_id, args.variant),
    ]
    result = subprocess.run(command, text=True)
    if result.returncode != 0:
        raise LabError(
            "strace failed. Check ptrace/container permissions and try again. "
            f"Exit status: {result.returncode}"
        )
    print(f"\nSaved strace summary to {destination.relative_to(ROOT)}")
    print(destination.read_text(encoding="utf-8"))


def perf_failure_message(stderr: str, destination: Path) -> str:
    details = stderr.strip()
    if destination.exists():
        file_details = destination.read_text(encoding="utf-8", errors="replace").strip()
        if file_details:
            details = f"{details}\n{file_details}".strip()
    suffix = f"\n\nperf output:\n{details}" if details else ""
    return (
        "perf could not collect counters. Check /proc/sys/kernel/perf_event_paranoid, "
        "container capabilities, and whether the kernel's perf tools match the running kernel."
        f"{suffix}"
    )


def command_perf_stat(args: argparse.Namespace) -> None:
    puzzle_id = resolve_id(args.id)
    perf = require_program("perf", "collect hardware performance counters")
    destination = variant_run_dir(puzzle_id, args.variant) / "perf-stat.txt"
    destination.unlink(missing_ok=True)
    command = [perf, "stat", "-d"]
    command.extend(["-o", str(destination), "--", *benchmark_command(puzzle_id, args.variant)])
    result = subprocess.run(command, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.returncode != 0:
        raise LabError(perf_failure_message(result.stderr, destination))
    print(f"\nSaved perf stat output to {destination.relative_to(ROOT)}")
    output = destination.read_text(encoding="utf-8")
    print(output)
    if "<not supported>" in output or "<not counted>" in output:
        print(
            "Warning: one or more hardware counters were unavailable. "
            "Check perf_event_paranoid, VM/container PMU exposure, and kernel support.",
            file=sys.stderr,
        )


def command_perf_record(args: argparse.Namespace) -> None:
    puzzle_id = resolve_id(args.id)
    perf = require_program("perf", "sample the running program")
    destination = variant_run_dir(puzzle_id, args.variant) / "perf.data"
    destination.unlink(missing_ok=True)
    command = [
        perf,
        "record",
        "-g",
        "-o",
        str(destination),
        "--",
        *benchmark_command(puzzle_id, args.variant),
    ]
    result = subprocess.run(command, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        raise LabError(
            "perf record failed. Check perf_event_paranoid and container capabilities. "
            f"Exit status: {result.returncode}"
        )
    print(f"Recorded samples in {destination.relative_to(ROOT)}")
    print(f"Next: perf report -i {destination.relative_to(ROOT)}")


def command_lesson(args: argparse.Namespace) -> None:
    puzzle_id = resolve_id(args.id)
    meta = PUZZLES[puzzle_id]
    readme = puzzle_dir(puzzle_id) / "README.md"
    print(f"Learning objective: {meta['objective']}")
    print("Suggested workflow: hypothesis -> tool -> evidence -> diagnosis -> fix -> validation\n")
    print(readme.read_text(encoding="utf-8"))


def command_hint(args: argparse.Namespace) -> None:
    puzzle_id = resolve_id(args.id)
    hint = puzzle_dir(puzzle_id) / "hints" / f"{args.level}.md"
    print(hint.read_text(encoding="utf-8"))


def command_diagnose(args: argparse.Namespace) -> None:
    puzzle_id = resolve_id(args.id)
    score = 0
    questions = PUZZLES[puzzle_id]["quiz"]
    print(f"Diagnosis quiz: Puzzle {puzzle_id}\n")
    for number, item in enumerate(questions, start=1):
        print(f"{number}. {item['question']}")
        for choice_number, choice in enumerate(item["choices"], start=1):
            print(f"   {choice_number}. {choice}")
        try:
            raw_answer = input("Your answer: ").strip()
        except EOFError as exc:
            raise LabError("quiz input ended before all questions were answered") from exc
        try:
            answer = int(raw_answer)
        except ValueError:
            answer = -1
        if answer == item["answer"]:
            score += 1
            print("Correct.")
        else:
            correct_text = item["choices"][item["answer"] - 1]
            print(f"Not quite. Correct answer: {item['answer']}. {correct_text}")
        print(f"{item['explanation']}\n")
    print(f"Score: {score}/{len(questions)}")


JOURNAL_TEMPLATE = """# Lab notes: Puzzle {puzzle_id}

## Before profiling
My hypothesis:

## Commands I ran

## Observations
Runtime:

strace:

perf stat:

perf report:

## Diagnosis

## Fix prediction

## After comparing fixed version
Did the expected metric improve?

## Takeaway
"""


def command_journal(args: argparse.Namespace) -> None:
    puzzle_id = resolve_id(args.id)
    destination = variant_run_dir(puzzle_id, args.variant) / "lab.md"
    if destination.exists():
        print(f"Journal already exists; left it unchanged: {destination.relative_to(ROOT)}")
        return
    destination.write_text(JOURNAL_TEMPLATE.format(puzzle_id=puzzle_id), encoding="utf-8")
    print(f"Created {destination.relative_to(ROOT)}")


def command_reveal(args: argparse.Namespace) -> None:
    puzzle_id = resolve_id(args.id)
    answer = puzzle_dir(puzzle_id) / "answer.md"
    print(answer.read_text(encoding="utf-8"))


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pmystery.py",
        description="Build, profile, and diagnose Linux performance puzzles.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list available puzzles")
    list_parser.set_defaults(handler=command_list)

    build_parser = subparsers.add_parser("build", help="build both puzzle variants")
    build_parser.add_argument("id")
    build_parser.set_defaults(handler=command_build)

    for name, handler, help_text in (
        ("run", command_run, "run one puzzle variant"),
        ("strace", command_strace, "collect a strace syscall summary"),
        ("perf-stat", command_perf_stat, "collect perf stat counters"),
        ("perf-record", command_perf_record, "record perf samples"),
        ("journal", command_journal, "create a lab notebook"),
    ):
        subparser = subparsers.add_parser(name, help=help_text)
        subparser.add_argument("id")
        subparser.add_argument("variant", choices=("bad", "fixed"))
        subparser.set_defaults(handler=handler)

    compare_parser = subparsers.add_parser("compare", help="compare bad and fixed runtimes")
    compare_parser.add_argument("id")
    compare_parser.set_defaults(handler=command_compare)

    lesson_parser = subparsers.add_parser("lesson", help="show a puzzle lesson")
    lesson_parser.add_argument("id")
    lesson_parser.set_defaults(handler=command_lesson)

    hint_parser = subparsers.add_parser("hint", help="show a progressive hint")
    hint_parser.add_argument("id")
    hint_parser.add_argument("level", nargs="?", default=1, type=int, choices=(1, 2, 3))
    hint_parser.set_defaults(handler=command_hint)

    diagnose_parser = subparsers.add_parser("diagnose", help="take the diagnosis quiz")
    diagnose_parser.add_argument("id")
    diagnose_parser.set_defaults(handler=command_diagnose)

    reveal_parser = subparsers.add_parser("reveal", help="show the answer explanation")
    reveal_parser.add_argument("id")
    reveal_parser.set_defaults(handler=command_reveal)
    return parser


def main() -> int:
    parser = make_parser()
    args = parser.parse_args()
    try:
        args.handler(args)
    except LabError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
