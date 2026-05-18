#!/usr/bin/env python3
"""Autoresearch-style loop runner for emoji-witty-zh-tw."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[4]

MUTABLE_FILES = [
    ".agents/skills/emoji-witty-zh-tw/SKILL.md",
    ".agents/skills/emoji-witty-zh-tw/references/emoji-witty-zh-tw/test-cases.md",
    ".agents/skills/emoji-witty-zh-tw/references/emoji-witty-zh-tw/target-metrics.md",
]

DEFAULT_CASES = [
    {"id": "osaka", "target": "大阪旅遊", "category": "travel", "sentinel": True},
    {"id": "hongkong", "target": "香港旅遊", "category": "travel", "sentinel": False},
]

ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
TRAILING_CLI_NOISE_RE = re.compile(r"\nChanges\s+[^\n]+(?:\nAI Units[^\n]+)?(?:\nTokens[^\n]+)?\s*$", re.S)


@dataclass
class CaseConfig:
    id: str
    target: str
    category: str
    sentinel: bool = False


@dataclass
class PromptRun:
    model: str
    prompt: str
    stdout: str
    returncode: int
    parsed: dict[str, Any] | None = None


@dataclass
class SolverCaseResult:
    tier: str
    label: str
    provider: str
    model: str
    solver: PromptRun
    judge: PromptRun | None


@dataclass
class CaseResult:
    case: CaseConfig
    generator: PromptRun
    solvers: list[SolverCaseResult] = field(default_factory=list)


@dataclass
class BenchmarkSummary:
    total_cases: int
    invalid_cases: int
    objective: float
    full_total_avg: float
    mini_total_avg: float
    full_alignment_avg: float
    mini_alignment_avg: float
    full_difficulty_avg: float
    mini_difficulty_avg: float
    total_gap: float
    alignment_gap: float
    difficulty_gap: float
    sentinel_bonus: float
    control_penalty: float


@dataclass
class BackendSpec:
    provider: str
    tier: str
    label: str
    model: str | None = None
    reasoning_effort: str | None = None


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def strip_cli_noise(text: str) -> str:
    text = ANSI_ESCAPE_RE.sub("", text)
    return TRAILING_CLI_NOISE_RE.sub("", text).strip()


def extract_json_object(text: str) -> dict[str, Any]:
    cleaned = strip_cli_noise(text)

    fence_match = re.findall(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", cleaned)
    best_match: tuple[int, dict[str, Any]] | None = None
    for chunk in fence_match:
        try:
            parsed = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            score = len(chunk)
            if best_match is None or score > best_match[0]:
                best_match = (score, parsed)

    decoder = json.JSONDecoder()
    for index, char in enumerate(cleaned):
        if char != "{":
            continue
        try:
            parsed, end = decoder.raw_decode(cleaned[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            score = end
            if best_match is None or score > best_match[0]:
                best_match = (score, parsed)
    if best_match is not None:
        return best_match[1]
    raise ValueError("No JSON object found in Copilot output")


def run_command(command: list[str], cwd: Path, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        return subprocess.CompletedProcess(command, 124, stdout=stdout + "\n[TIMEOUT]")


def run_copilot(
    workspace: Path,
    prompt: str,
    *,
    model: str,
    timeout: int,
    parse_json: bool,
) -> PromptRun:
    command = [
        "copilot",
        "-C",
        str(workspace),
        "--allow-all-tools",
        "--no-color",
        "--model",
        model,
        "-p",
        prompt,
    ]
    result = run_command(command, cwd=workspace, timeout=timeout)
    parsed = None
    if parse_json and result.returncode == 0:
        parsed = extract_json_object(result.stdout)
    return PromptRun(
        model=model,
        prompt=prompt,
        stdout=result.stdout,
        returncode=result.returncode,
        parsed=parsed,
    )


def run_codex(
    workspace: Path,
    prompt: str,
    *,
    model: str | None,
    reasoning_effort: str | None,
    timeout: int,
    parse_json: bool,
) -> PromptRun:
    with tempfile.NamedTemporaryFile("r+", encoding="utf-8", delete=False) as handle:
        output_path = Path(handle.name)
    command = [
        "codex",
        "exec",
        "-C",
        str(workspace),
        "--skip-git-repo-check",
        "--dangerously-bypass-approvals-and-sandbox",
        "--color",
        "never",
        "-o",
        str(output_path),
    ]
    if model:
        command.extend(["-m", model])
    if reasoning_effort:
        command.extend(["-c", f'model_reasoning_effort="{reasoning_effort}"'])
    command.append(prompt)
    result = run_command(command, cwd=workspace, timeout=timeout)
    try:
        message = output_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        message = result.stdout
    finally:
        output_path.unlink(missing_ok=True)
    parsed = None
    if parse_json and result.returncode == 0:
        parsed = extract_json_object(message)
    return PromptRun(
        model=model or "default",
        prompt=prompt,
        stdout=message if message.strip() else result.stdout,
        returncode=result.returncode,
        parsed=parsed,
    )


def run_gemini(
    workspace: Path,
    prompt: str,
    *,
    model: str | None,
    timeout: int,
    parse_json: bool,
) -> PromptRun:
    command = [
        "gemini",
        "--skip-trust",
        "--yolo",
        "--prompt",
        prompt,
    ]
    if model:
        command.extend(["--model", model])
    result = run_command(command, cwd=workspace, timeout=timeout)
    parsed = None
    if parse_json and result.returncode == 0:
        parsed = extract_json_object(result.stdout)
    return PromptRun(
        model=model or "default",
        prompt=prompt,
        stdout=result.stdout,
        returncode=result.returncode,
        parsed=parsed,
    )


def run_copilot_json(
    workspace: Path,
    prompt: str,
    *,
    backend: BackendSpec,
    timeout: int,
    retries: int = 2,
) -> PromptRun:
    last_run: PromptRun | None = None
    retry_prompt = prompt
    for attempt in range(retries + 1):
        try:
            if backend.provider == "copilot":
                run = run_copilot(
                    workspace,
                    retry_prompt,
                    model=backend.model or "gpt-5.4",
                    timeout=timeout,
                    parse_json=True,
                )
            elif backend.provider == "codex":
                run = run_codex(
                    workspace,
                    retry_prompt,
                    model=backend.model,
                    reasoning_effort=backend.reasoning_effort,
                    timeout=timeout,
                    parse_json=True,
                )
            elif backend.provider == "gemini":
                run = run_gemini(
                    workspace,
                    retry_prompt,
                    model=backend.model,
                    timeout=timeout,
                    parse_json=True,
                )
            else:
                raise ValueError(f"Unsupported provider: {backend.provider}")
        except Exception as exc:  # noqa: BLE001
            if attempt == retries:
                raise
            retry_prompt = (
                prompt
                + "\n\n上一次回傳不可解析。這次只允許輸出單一 JSON 物件，不要 markdown、不要 code fence、不要補充說明。"
            )
            last_run = PromptRun(
                model=backend.model or backend.provider,
                prompt=retry_prompt,
                stdout=str(exc),
                returncode=1,
                parsed=None,
            )
            continue
        if run.returncode == 0 and run.parsed is not None:
            return run
        last_run = run
        retry_prompt = (
            prompt
            + "\n\n上一次回傳不可解析。這次只允許輸出單一 JSON 物件，不要 markdown、不要 code fence、不要補充說明。"
        )
    assert last_run is not None
    return last_run


def copy_repo(source: Path, destination: Path, ignore_output_dir: Path | None) -> None:
    ignore_names = {".git", ".autoresearch-runs"}
    if ignore_output_dir and ignore_output_dir.is_relative_to(source):
        ignore_names.add(ignore_output_dir.relative_to(source).parts[0])

    def ignore(_dir: str, entries: list[str]) -> set[str]:
        return {entry for entry in entries if entry in ignore_names}

    shutil.copytree(source, destination, ignore=ignore)


def list_changed_files(source: Path, candidate: Path) -> list[str]:
    changed: list[str] = []
    for path in source.rglob("*"):
        if path.is_dir():
            continue
        if ".git" in path.parts or ".autoresearch-runs" in path.parts:
            continue
        relative = path.relative_to(source)
        candidate_path = candidate / relative
        if not candidate_path.exists():
            changed.append(str(relative))
            continue
        if path.read_bytes() != candidate_path.read_bytes():
            changed.append(str(relative))
    for path in candidate.rglob("*"):
        if path.is_dir():
            continue
        if ".git" in path.parts or ".autoresearch-runs" in path.parts:
            continue
        relative = path.relative_to(candidate)
        if not (source / relative).exists():
            changed.append(str(relative))
    return sorted(set(changed))


def build_mutation_prompt(
    iteration: int,
    cases: list[CaseConfig],
    best_summary: BenchmarkSummary,
    history: list[dict[str, Any]],
) -> str:
    case_lines = "\n".join(
        f"- {case.target} ({case.category}, sentinel={'yes' if case.sentinel else 'no'})" for case in cases
    )
    recent_history = history[-3:]
    history_json = json.dumps(recent_history, ensure_ascii=False, indent=2) if recent_history else "[]"
    summary_json = json.dumps(best_summary.__dict__, ensure_ascii=False, indent=2)
    mutable_list = "\n".join(f"- {path}" for path in MUTABLE_FILES)
    return textwrap.dedent(
        f"""
        你正在替 repo 中的 `emoji-witty-zh-tw` 執行第 {iteration} 輪 autoresearch。

        目標：
        - 提升 full-tier 與 mini-tier 在 reasoning gap 上的差距
        - 特別照顧 weak-case sentinel
        - 避免 control case collapse（不要讓題目縮成猜單一交通卡、單一商場或單一子物件）

        這輪只允許修改以下檔案：
        {mutable_list}

        Benchmark cases:
        {case_lines}

        目前最佳 benchmark summary:
        {summary_json}

        最近幾輪 keep/discard 紀錄:
        {history_json}

        編修規則：
        1. 只做小而清楚的修改。
        2. 只能改上面列出的三個檔案。
        3. 優先強化 generator 在 travel 題上的 rule clarity，而不是擴大 scope。
        4. 若某個 clue 組合容易坍縮成單一子物件，請補 anti-collapse 規則。
        5. 不要加入新的 benchmark framework 或新工具依賴。

        完成後，請在最後輸出一個 JSON 物件，格式如下：
        {{
          "iteration_hypothesis": "一句話說明這輪假說",
          "files_touched": ["..."],
          "expected_win": "這輪預期會改善什麼",
          "expected_risk": "這輪最可能造成的副作用"
        }}

        除了最後那個 JSON 物件外，前面可以照常使用工具與簡短說明。
        """
    ).strip()


def build_generator_prompt(case: CaseConfig) -> str:
    return textwrap.dedent(
        f"""
        請使用目前啟用的 emoji-witty-zh-tw skill，將「{case.target}」轉成 1 組繁體中文 4-emoji 表意設計。

        只輸出單一 JSON 物件，不要 markdown、不要 code fence、不要額外說明。

        JSON schema:
        {{
          "target": "{case.target}",
          "emoji": ["😀", "😀", "😀", "😀"],
          "emoji_compact": "😀😀😀😀",
          "rationale": {{
            "😀": "這個 emoji 的設計理由"
          }},
          "difficulty_comment": "為什麼 full model 較容易講對，mini model 較容易停在表面理由"
        }}

        要求：
        - `emoji` 必須剛好 4 個 emoji
        - `emoji_compact` 必須是同一組 emoji 連在一起
        - `rationale` 要能對到每個 emoji
        """
    ).strip()


def build_solver_prompt(emoji_compact: str) -> str:
    return textwrap.dedent(
        f"""
        請作為 solver agent 解題，不要重新設計題目，也不要補題。看到這組 emoji：{emoji_compact}

        只輸出單一 JSON 物件，不要 markdown、不要 code fence、不要額外說明。

        JSON schema:
        {{
          "guess": "你的猜測答案",
          "confidence": 0.0,
          "reasoning": {{
            "😀": "這個 emoji 在你推理中的角色"
          }},
          "alternatives": ["備選答案 1", "備選答案 2"],
          "turning_point": "哪個 clue 是轉折、誤導或側面文化線索；若沒有就寫空字串"
        }}
        """
    ).strip()


def build_judge_prompt(case: CaseConfig, generator: dict[str, Any], solver: dict[str, Any], tier: str) -> str:
    payload = {
        "target": case.target,
        "category": case.category,
        "generator": generator,
        "solver": solver,
        "solver_tier": tier,
    }
    return textwrap.dedent(
        f"""
        你是 judge agent，請評估 solver 是否真的讀懂 generator 的設計。

        評分規則：
        - `answer_correctness`: 0-2
        - `reason_alignment`: 0-4
        - `reason_quality`: 0-3
        - `difficulty_awareness`: 0-1
        - `total`: 以上總和
        - `guessed_but_shallow`: 布林值；若只是猜對但理由很表層則為 true
        - `identified_city_system`: 布林值；若 solver 明確抓到 city-system clue 則為 true
        - `identified_traveler_friction`: 布林值；若 solver 明確抓到 traveler-friction clue 則為 true
        - `collapse_warning`: 布林值；若題目被 solver 讀成單一子物件或單一系統，而不是 target 本身則為 true

        資料如下：
        {json.dumps(payload, ensure_ascii=False, indent=2)}

        只輸出單一 JSON 物件，不要 markdown、不要 code fence、不要額外說明。
        """
    ).strip()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def validate_generator_payload(payload: dict[str, Any], target: str) -> None:
    emoji = payload.get("emoji")
    if payload.get("target") != target:
        raise ValueError(f"Generator returned mismatched target: {payload.get('target')!r}")
    if not isinstance(emoji, list) or len(emoji) != 4 or not all(isinstance(item, str) and item for item in emoji):
        raise ValueError("Generator returned invalid emoji array")
    compact = payload.get("emoji_compact")
    if not isinstance(compact, str) or not compact:
        raise ValueError("Generator returned invalid emoji_compact")


def score_summary(case_results: list[CaseResult]) -> BenchmarkSummary:
    full_totals: list[float] = []
    mini_totals: list[float] = []
    full_alignment: list[float] = []
    mini_alignment: list[float] = []
    full_difficulty: list[float] = []
    mini_difficulty: list[float] = []
    sentinel_bonus = 0.0
    control_penalty = 0.0
    invalid_cases = 0

    for case_result in case_results:
        full_case_scores = [
            solver.judge.parsed for solver in case_result.solvers if solver.tier == "full" and solver.judge and solver.judge.parsed
        ]
        mini_case_scores = [
            solver.judge.parsed for solver in case_result.solvers if solver.tier == "mini" and solver.judge and solver.judge.parsed
        ]
        if not full_case_scores or not mini_case_scores:
            invalid_cases += 1
            continue

        def case_avg(items: list[dict[str, Any]], key: str) -> float:
            return statistics.fmean(float(item[key]) for item in items)

        full_totals.append(case_avg(full_case_scores, "total"))
        mini_totals.append(case_avg(mini_case_scores, "total"))
        full_alignment.append(case_avg(full_case_scores, "reason_alignment"))
        mini_alignment.append(case_avg(mini_case_scores, "reason_alignment"))
        full_difficulty.append(case_avg(full_case_scores, "difficulty_awareness"))
        mini_difficulty.append(case_avg(mini_case_scores, "difficulty_awareness"))

        if case_result.case.sentinel:
            sentinel_bonus += (
                case_avg(full_case_scores, "reason_alignment") - case_avg(mini_case_scores, "reason_alignment")
            ) + 0.5 * (
                case_avg(full_case_scores, "difficulty_awareness") - case_avg(mini_case_scores, "difficulty_awareness")
            )

        control_penalty += 0.5 * sum(1 for item in full_case_scores if item.get("collapse_warning"))
        control_penalty += 1.0 * sum(1 for item in mini_case_scores if item.get("collapse_warning"))

    def avg(values: list[float]) -> float:
        return statistics.fmean(values) if values else 0.0

    full_total_avg = avg(full_totals)
    mini_total_avg = avg(mini_totals)
    full_alignment_avg = avg(full_alignment)
    mini_alignment_avg = avg(mini_alignment)
    full_difficulty_avg = avg(full_difficulty)
    mini_difficulty_avg = avg(mini_difficulty)
    total_gap = full_total_avg - mini_total_avg
    alignment_gap = full_alignment_avg - mini_alignment_avg
    difficulty_gap = full_difficulty_avg - mini_difficulty_avg

    objective = (
        2.0 * alignment_gap
        + 1.0 * total_gap
        + 0.75 * difficulty_gap
        + 0.75 * sentinel_bonus
        - 1.5 * control_penalty
        - 2.0 * invalid_cases
    )

    return BenchmarkSummary(
        total_cases=len(case_results),
        invalid_cases=invalid_cases,
        objective=objective,
        full_total_avg=full_total_avg,
        mini_total_avg=mini_total_avg,
        full_alignment_avg=full_alignment_avg,
        mini_alignment_avg=mini_alignment_avg,
        full_difficulty_avg=full_difficulty_avg,
        mini_difficulty_avg=mini_difficulty_avg,
        total_gap=total_gap,
        alignment_gap=alignment_gap,
        difficulty_gap=difficulty_gap,
        sentinel_bonus=sentinel_bonus,
        control_penalty=control_penalty,
    )


def benchmark_workspace(
    workspace: Path,
    cases: list[CaseConfig],
    *,
    generator_backend: BackendSpec,
    solver_backends: list[BackendSpec],
    judge_backend: BackendSpec,
    timeout: int,
    artifact_dir: Path,
) -> tuple[list[CaseResult], BenchmarkSummary]:
    results: list[CaseResult] = []
    artifact_dir.mkdir(parents=True, exist_ok=True)

    for case in cases:
        case_dir = artifact_dir / case.id
        case_dir.mkdir(parents=True, exist_ok=True)

        generator = run_copilot_json(
            workspace,
            build_generator_prompt(case),
            backend=generator_backend,
            timeout=timeout,
        )
        write_json(case_dir / "generator.json", generator.parsed or {"raw_output": generator.stdout, "returncode": generator.returncode})

        case_result = CaseResult(case=case, generator=generator)
        if generator.returncode != 0 or generator.parsed is None:
            results.append(case_result)
            continue

        try:
            validate_generator_payload(generator.parsed, case.target)
        except ValueError as exc:
            write_json(case_dir / "generator-invalid.json", {"error": str(exc), "parsed": generator.parsed})
            results.append(case_result)
            continue
        emoji_compact = generator.parsed["emoji_compact"]

        for solver_backend in solver_backends:
            solver = run_copilot_json(
                workspace,
                build_solver_prompt(emoji_compact),
                backend=solver_backend,
                timeout=timeout,
            )
            write_json(
                case_dir / f"solver-{solver_backend.label}.json",
                solver.parsed or {"raw_output": solver.stdout, "returncode": solver.returncode},
            )

            judge = None
            if solver.returncode == 0 and solver.parsed is not None:
                judge = run_copilot_json(
                    workspace,
                    build_judge_prompt(case, generator.parsed, solver.parsed, solver_backend.tier),
                    backend=judge_backend,
                    timeout=timeout,
                )
                write_json(
                    case_dir / f"judge-{solver_backend.label}.json",
                    judge.parsed or {"raw_output": judge.stdout, "returncode": judge.returncode},
                )

            case_result.solvers.append(
                SolverCaseResult(
                    tier=solver_backend.tier,
                    label=solver_backend.label,
                    provider=solver_backend.provider,
                    model=solver_backend.model or "default",
                    solver=solver,
                    judge=judge,
                )
            )

        results.append(case_result)

    summary = score_summary(results)
    write_json(artifact_dir / "summary.json", summary.__dict__)
    write_json(artifact_dir / "results.json", serialize_case_results(results))
    return results, summary


def serialize_prompt_run(run: PromptRun) -> dict[str, Any]:
    return {
        "model": run.model,
        "returncode": run.returncode,
        "parsed": run.parsed,
        "stdout": run.stdout,
    }


def serialize_case_results(results: list[CaseResult]) -> list[dict[str, Any]]:
    serialized: list[dict[str, Any]] = []
    for case_result in results:
        serialized.append(
            {
                "case": case_result.case.__dict__,
                "generator": serialize_prompt_run(case_result.generator),
                "solvers": [
                    {
                        "tier": solver.tier,
                        "label": solver.label,
                        "provider": solver.provider,
                        "model": solver.model,
                        "solver": serialize_prompt_run(solver.solver),
                        "judge": serialize_prompt_run(solver.judge) if solver.judge else None,
                    }
                    for solver in case_result.solvers
                ],
            }
        )
    return serialized


def copy_mutable_files(source_workspace: Path, destination_repo: Path) -> None:
    for relative in MUTABLE_FILES:
        source_path = source_workspace / relative
        destination_path = destination_repo / relative
        ensure_parent(destination_path)
        shutil.copy2(source_path, destination_path)


def decide_keep(best: BenchmarkSummary, candidate: BenchmarkSummary) -> tuple[bool, str]:
    if candidate.invalid_cases > best.invalid_cases:
        return False, "candidate produced more invalid benchmark cases"
    if candidate.objective <= best.objective + 0.1:
        return False, "candidate objective did not improve enough"
    if candidate.control_penalty > best.control_penalty + 0.5:
        return False, "candidate increased collapse risk"
    return True, "candidate improved objective without worse collapse risk"


def parse_cases(case_ids: str) -> list[CaseConfig]:
    configured = {entry["id"]: CaseConfig(**entry) for entry in DEFAULT_CASES}
    selected: list[CaseConfig] = []
    for case_id in [item.strip() for item in case_ids.split(",") if item.strip()]:
        if case_id not in configured:
            raise ValueError(f"Unknown case id: {case_id}")
        selected.append(configured[case_id])
    if not selected:
        raise ValueError("At least one case is required")
    return selected


def parse_backend_spec(spec: str) -> BackendSpec:
    parts = [part.strip() for part in spec.split(":")]
    if len(parts) < 3:
        raise ValueError(f"Invalid backend spec: {spec}")
    provider, tier, label = parts[:3]
    model = parts[3] if len(parts) > 3 and parts[3] else None
    reasoning_effort = parts[4] if len(parts) > 4 and parts[4] else None
    return BackendSpec(
        provider=provider,
        tier=tier,
        label=label,
        model=model,
        reasoning_effort=reasoning_effort,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run autoresearch loops for emoji-witty-zh-tw")
    parser.add_argument("--repo", default=str(DEFAULT_REPO_ROOT), help="Path to the agents repo")
    parser.add_argument("--iterations", type=int, default=3, help="Number of mutation loops to run")
    parser.add_argument(
        "--cases",
        default="osaka,hongkong",
        help="Comma-separated case ids to benchmark (default: osaka,hongkong)",
    )
    parser.add_argument(
        "--output-dir",
        default=".autoresearch-runs/emoji-witty-zh-tw",
        help="Directory for logs and iteration artifacts",
    )
    parser.add_argument(
        "--mutation-backend",
        default="codex:full:mutation::high",
        help="Backend spec for mutation loops: provider:tier:label[:model[:reasoning_effort]]",
    )
    parser.add_argument(
        "--generator-backend",
        default="codex:full:generator::high",
        help="Backend spec for generator benchmark runs",
    )
    parser.add_argument(
        "--judge-backend",
        default="codex:full:judge::high",
        help="Backend spec for judge scoring",
    )
    parser.add_argument(
        "--solver-backend",
        action="append",
        default=[],
        help="Repeatable backend spec for solver runs. Defaults to codex/copilot/gemini full plus copilot mini.",
    )
    parser.add_argument("--timeout", type=int, default=300, help="Per-Copilot-call timeout in seconds")
    parser.add_argument(
        "--baseline-only",
        action="store_true",
        help="Only run the baseline benchmark without mutation iterations",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo = Path(args.repo).resolve()
    output_dir = (repo / args.output_dir).resolve()
    cases = parse_cases(args.cases)
    mutation_backend = parse_backend_spec(args.mutation_backend)
    generator_backend = parse_backend_spec(args.generator_backend)
    judge_backend = parse_backend_spec(args.judge_backend)
    solver_specs = args.solver_backend or [
        "codex:full:codex-full::high",
        "copilot:full:copilot-full:gpt-5.4",
        "gemini:full:gemini-full",
        "copilot:mini:copilot-mini:gpt-5.4-mini",
    ]
    solver_backends = [parse_backend_spec(spec) for spec in solver_specs]

    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "run_id": run_id,
        "started_at": utc_now(),
        "repo": str(repo),
        "iterations": args.iterations,
        "cases": [case.__dict__ for case in cases],
        "backends": {
            "mutation": mutation_backend.__dict__,
            "generator": generator_backend.__dict__,
            "judge": judge_backend.__dict__,
            "solvers": [backend.__dict__ for backend in solver_backends],
        },
        "mutable_files": MUTABLE_FILES,
    }
    write_json(run_dir / "config.json", config)

    _, best_summary = benchmark_workspace(
        repo,
        cases,
        generator_backend=generator_backend,
        solver_backends=solver_backends,
        judge_backend=judge_backend,
        timeout=args.timeout,
        artifact_dir=run_dir / "baseline",
    )

    history: list[dict[str, Any]] = [{"iteration": 0, "decision": "baseline", "summary": best_summary.__dict__}]

    if args.baseline_only or args.iterations <= 0:
        write_json(run_dir / "run-summary.json", {"history": history, "best_summary": best_summary.__dict__})
        print(json.dumps({"run_dir": str(run_dir), "best_summary": best_summary.__dict__}, ensure_ascii=False, indent=2))
        return 0

    for iteration in range(1, args.iterations + 1):
        workspace = run_dir / f"iteration-{iteration:03d}" / "workspace"
        copy_repo(repo, workspace, output_dir)

        mutation_prompt = build_mutation_prompt(iteration, cases, best_summary, history)
        mutation_run = run_copilot_json(
            workspace,
            mutation_prompt,
            backend=mutation_backend,
            timeout=args.timeout,
        )

        iteration_dir = workspace.parent
        write_json(
            iteration_dir / "mutation.json",
            mutation_run.parsed or {"raw_output": mutation_run.stdout, "returncode": mutation_run.returncode},
        )

        changed_files = list_changed_files(repo, workspace)
        write_json(iteration_dir / "changed-files.json", changed_files)

        invalid_changes = [path for path in changed_files if path not in MUTABLE_FILES]
        if mutation_run.returncode != 0 or mutation_run.parsed is None or invalid_changes:
            history.append(
                {
                    "iteration": iteration,
                    "decision": "discard",
                    "reason": "mutation failed or touched files outside the allowed surface",
                    "invalid_changes": invalid_changes,
                }
            )
            continue

        _, candidate_summary = benchmark_workspace(
            workspace,
            cases,
            generator_backend=generator_backend,
            solver_backends=solver_backends,
            judge_backend=judge_backend,
            timeout=args.timeout,
            artifact_dir=iteration_dir / "benchmark",
        )

        keep, reason = decide_keep(best_summary, candidate_summary)
        decision_record = {
            "iteration": iteration,
            "decision": "keep" if keep else "discard",
            "reason": reason,
            "candidate_summary": candidate_summary.__dict__,
            "mutation_summary": mutation_run.parsed,
        }
        history.append(decision_record)
        write_json(iteration_dir / "decision.json", decision_record)

        if keep:
            copy_mutable_files(workspace, repo)
            best_summary = candidate_summary

    write_json(run_dir / "run-summary.json", {"history": history, "best_summary": best_summary.__dict__})
    print(json.dumps({"run_dir": str(run_dir), "best_summary": best_summary.__dict__}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
