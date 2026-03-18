# General Function to run existing planner once
# Input : seed, # robots, #tasks, map size, #hazards, P_f
# Output : setup_time, calculation_time, success, etc.

from __future__ import annotations

import random
import time
from dataclasses import dataclass, asdict
from typing import Any, Callable

import numpy as np

from experiment_config import (
    DEFAULT_NUM_INITIAL_CONDITIONS,
    VERBOSE,
)

# ============================================================
# experiment_runner.py
# Run one experiment with one setting.
# This file is the bridge between the experiment scripts
# and the existing planner code.
# ============================================================


@dataclass
class ExperimentInput:
    # Seed for random state
    seed: int

    # Main problem settings
    num_agents: int
    num_tasks: int
    map_width: int
    map_height: int
    num_hazards: int
    p_f: float

    # Extra options
    num_initial_conditions: int = DEFAULT_NUM_INITIAL_CONDITIONS
    experiment_name: str = "single_experiment"


@dataclass
class ExperimentResult:
    # Copy of input settings
    seed: int
    num_agents: int
    num_tasks: int
    map_width: int
    map_height: int
    num_hazards: int
    p_f: float

    # Measured values
    setup_time: float
    calculation_time: float
    success: int

    # Optional extra info
    total_runtime: float | None = None
    error_message: str | None = None


def set_global_seed(seed: int) -> None:
    # Set python and numpy seeds
    random.seed(seed)
    np.random.seed(seed)


def make_experiment_input(
    seed: int,
    num_agents: int,
    num_tasks: int,
    map_width: int,
    map_height: int,
    num_hazards: int,
    p_f: float,
    num_initial_conditions: int = DEFAULT_NUM_INITIAL_CONDITIONS,
    experiment_name: str = "single_experiment",
) -> ExperimentInput:
    # Build a typed input object
    return ExperimentInput(
        seed=seed,
        num_agents=num_agents,
        num_tasks=num_tasks,
        map_width=map_width,
        map_height=map_height,
        num_hazards=num_hazards,
        p_f=p_f,
        num_initial_conditions=num_initial_conditions,
        experiment_name=experiment_name,
    )


def _default_result_from_input(exp_input: ExperimentInput) -> ExperimentResult:
    # Build an empty result object
    return ExperimentResult(
        seed=exp_input.seed,
        num_agents=exp_input.num_agents,
        num_tasks=exp_input.num_tasks,
        map_width=exp_input.map_width,
        map_height=exp_input.map_height,
        num_hazards=exp_input.num_hazards,
        p_f=exp_input.p_f,
        setup_time=np.nan,
        calculation_time=np.nan,
        success=0,
        total_runtime=np.nan,
        error_message=None,
    )


def _extract_float(value: Any, default: float = np.nan) -> float:
    # Convert many numeric types into float
    try:
        return float(value)
    except Exception:
        return float(default)


def _extract_success(raw_result: dict[str, Any]) -> int:
    # Convert many possible success fields into 0 or 1

    # Case 1: direct success field
    if "success" in raw_result:
        return int(bool(raw_result["success"]))

    # Case 2: direct success_rate field
    if "success_rate" in raw_result:
        return int(float(raw_result["success_rate"]) > 0.0)

    # Case 3: status string
    if "status" in raw_result:
        status = str(raw_result["status"]).lower()
        if status in {"success", "succeeded", "done", "finished"}:
            return 1
        if status in {"fail", "failed", "failure", "error"}:
            return 0

    # Case 4: if there is no clear field, return 0
    return 0


def _normalize_raw_result(
    exp_input: ExperimentInput,
    raw_result: dict[str, Any],
    total_runtime: float,
) -> ExperimentResult:
    # Convert raw planner output into one fixed format

    result = _default_result_from_input(exp_input)

    if "time_dict" in raw_result and isinstance(raw_result["time_dict"], dict):
        time_dict = raw_result["time_dict"]
        result.setup_time = _extract_float(time_dict.get("setup_time", np.nan))
        result.calculation_time = _extract_float(time_dict.get("calculation_time", np.nan))
    else:
        result.setup_time = _extract_float(raw_result.get("setup_time", np.nan))
        result.calculation_time = _extract_float(raw_result.get("calculation_time", np.nan))

    result.success = _extract_success(raw_result)
    result.total_runtime = total_runtime
    result.error_message = raw_result.get("error_message", None)

    return result


def _call_existing_single_experiment(exp_input: ExperimentInput) -> dict[str, Any]:
    # This function must call your real planner code.
    # Edit only this function when you connect your codebase.
    #
    # Expected return format:
    # {
    #     "setup_time": float,
    #     "calculation_time": float,
    #     "success": 0 or 1,
    # }
    #
    # If your planner already returns:
    # {
    #     "time_dict": {"setup_time": ..., "calculation_time": ...},
    #     "success": ...,
    # }
    # that also works.

    # --------------------------------------------------------
    # Example pattern:
    #
    # from some_existing_file import run_single_experiment
    #
    # return run_single_experiment(
    #     seed=exp_input.seed,
    #     num_agents=exp_input.num_agents,
    #     num_tasks=exp_input.num_tasks,
    #     map_width=exp_input.map_width,
    #     map_height=exp_input.map_height,
    #     num_hazards=exp_input.num_hazards,
    #     p_f=exp_input.p_f,
    #     num_initial_conditions=exp_input.num_initial_conditions,
    # )
    # --------------------------------------------------------

    raise NotImplementedError(
        "Connect _call_existing_single_experiment() to your real planner function."
    )


def run_one_experiment(exp_input: ExperimentInput) -> ExperimentResult:
    # Run one experiment safely and return one result row

    set_global_seed(exp_input.seed)

    if VERBOSE:
        print(
            f"[RUN] seed={exp_input.seed}, "
            f"agents={exp_input.num_agents}, "
            f"tasks={exp_input.num_tasks}, "
            f"map=({exp_input.map_width},{exp_input.map_height}), "
            f"hazards={exp_input.num_hazards}, "
            f"p_f={exp_input.p_f}"
        )

    start_time = time.perf_counter()

    try:
        raw_result = _call_existing_single_experiment(exp_input)
        total_runtime = time.perf_counter() - start_time

        if not isinstance(raw_result, dict):
            raise TypeError("Existing experiment function must return a dict.")

        result = _normalize_raw_result(exp_input, raw_result, total_runtime)

    except Exception as exc:
        total_runtime = time.perf_counter() - start_time
        result = _default_result_from_input(exp_input)
        result.total_runtime = total_runtime
        result.error_message = str(exc)

    return result


def run_one_experiment_from_kwargs(**kwargs: Any) -> ExperimentResult:
    # Small helper for direct calls from other scripts
    exp_input = make_experiment_input(**kwargs)
    return run_one_experiment(exp_input)


def result_to_dict(result: ExperimentResult) -> dict[str, Any]:
    # Convert result object into plain dict
    return asdict(result)


def results_to_list_of_dicts(results: list[ExperimentResult]) -> list[dict[str, Any]]:
    # Convert many result objects into list of dicts
    return [result_to_dict(result) for result in results]


def repeat_same_setting(
    seeds: list[int],
    num_agents: int,
    num_tasks: int,
    map_width: int,
    map_height: int,
    num_hazards: int,
    p_f: float,
    num_initial_conditions: int = DEFAULT_NUM_INITIAL_CONDITIONS,
    experiment_name: str = "repeated_experiment",
) -> list[ExperimentResult]:
    # Run the same setting with many seeds

    results: list[ExperimentResult] = []

    for seed in seeds:
        exp_input = make_experiment_input(
            seed=seed,
            num_agents=num_agents,
            num_tasks=num_tasks,
            map_width=map_width,
            map_height=map_height,
            num_hazards=num_hazards,
            p_f=p_f,
            num_initial_conditions=num_initial_conditions,
            experiment_name=experiment_name,
        )
        results.append(run_one_experiment(exp_input))

    return results


def inject_existing_runner(
    runner_func: Callable[[ExperimentInput], dict[str, Any]]
) -> Callable[[ExperimentInput], dict[str, Any]]:
    # Optional helper to replace the default adapter at runtime
    global _call_existing_single_experiment
    _call_existing_single_experiment = runner_func
    return runner_func
