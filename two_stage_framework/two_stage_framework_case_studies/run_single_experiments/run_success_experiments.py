# 2-a,b : Success rate

import pandas as pd

from experiment_config import (
    SAVE_RAW_DATA,
    SAVE_TABLES,
    RAW_DIR,
    TABLES_DIR,
    DEFAULT_NUM_INITIAL_CONDITIONS,
    SUCCESS_HAZARD_COUNT_LIST,
    SUCCESS_HAZARD_RAW_FILENAME,
    SUCCESS_PF_LIST,
    SUCCESS_PF_RAW_FILENAME,
    get_success_hazard_fixed_config,
    get_success_pf_fixed_config,
)

from experiment_runner import (
    repeat_same_setting,
    results_to_list_of_dicts,
)

# ============================================================
# run_success_experiment.py
# Run 2-a and 2-b success-rate experiments.
# 2-a: number of hazards -> success rate
# 2-b: p_f -> success rate
# Both experiments use the same shared seeds.
# ============================================================


def _results_to_dataframe(results):
    # Convert result objects into a dataframe
    rows = results_to_list_of_dicts(results)
    return pd.DataFrame(rows)


def run_hazard_count_success_experiment():
    # Run 2-a
    # Change only the number of hazards

    fixed_cfg = get_success_hazard_fixed_config()
    raw_frames = []

    for num_hazards in SUCCESS_HAZARD_COUNT_LIST:
        results = repeat_same_setting(
            seeds=fixed_cfg["seeds"],
            num_agents=fixed_cfg["num_agents"],
            num_tasks=fixed_cfg["num_tasks"],
            map_width=fixed_cfg["map_width"],
            map_height=fixed_cfg["map_height"],
            num_hazards=num_hazards,
            p_f=fixed_cfg["p_f"],
            num_initial_conditions=fixed_cfg.get(
                "num_initial_conditions",
                DEFAULT_NUM_INITIAL_CONDITIONS,
            ),
            experiment_name="success_vs_hazard_count",
        )

        df = _results_to_dataframe(results)
        df["experiment_type"] = "2a_success_hazard_count"
        df["hazard_count"] = num_hazards
        raw_frames.append(df)

    raw_df = pd.concat(raw_frames, ignore_index=True) if raw_frames else pd.DataFrame()

    if raw_df.empty:
        summary_df = pd.DataFrame(
            columns=[
                "hazard_count",
                "num_trials",
                "success_rate_mean",
                "success_count",
                "failure_count",
            ]
        )
    else:
        summary_df = (
            raw_df.groupby("hazard_count", as_index=False)
            .agg(
                num_trials=("success", "size"),
                success_rate_mean=("success", "mean"),
                success_count=("success", "sum"),
            )
            .sort_values(by="hazard_count")
            .reset_index(drop=True)
        )
        summary_df["failure_count"] = (
            summary_df["num_trials"] - summary_df["success_count"]
        )

    if SAVE_RAW_DATA and not raw_df.empty:
        raw_df.to_csv(RAW_DIR / SUCCESS_HAZARD_RAW_FILENAME, index=False)

    if SAVE_TABLES and not summary_df.empty:
        summary_df.to_csv(
            TABLES_DIR / "hazard_count_success_summary.csv",
            index=False,
        )

    return summary_df, raw_df


def run_pf_success_experiment():
    # Run 2-b
    # Change only p_f

    fixed_cfg = get_success_pf_fixed_config()
    raw_frames = []

    for p_f in SUCCESS_PF_LIST:
        results = repeat_same_setting(
            seeds=fixed_cfg["seeds"],
            num_agents=fixed_cfg["num_agents"],
            num_tasks=fixed_cfg["num_tasks"],
            map_width=fixed_cfg["map_width"],
            map_height=fixed_cfg["map_height"],
            num_hazards=fixed_cfg["num_hazards"],
            p_f=p_f,
            num_initial_conditions=fixed_cfg.get(
                "num_initial_conditions",
                DEFAULT_NUM_INITIAL_CONDITIONS,
            ),
            experiment_name="success_vs_pf",
        )

        df = _results_to_dataframe(results)
        df["experiment_type"] = "2b_success_pf"
        df["pf_value"] = p_f
        raw_frames.append(df)

    raw_df = pd.concat(raw_frames, ignore_index=True) if raw_frames else pd.DataFrame()

    if raw_df.empty:
        summary_df = pd.DataFrame(
            columns=[
                "pf_value",
                "num_trials",
                "success_rate_mean",
                "success_count",
                "failure_count",
            ]
        )
    else:
        summary_df = (
            raw_df.groupby("pf_value", as_index=False)
            .agg(
                num_trials=("success", "size"),
                success_rate_mean=("success", "mean"),
                success_count=("success", "sum"),
            )
            .sort_values(by="pf_value")
            .reset_index(drop=True)
        )
        summary_df["failure_count"] = (
            summary_df["num_trials"] - summary_df["success_count"]
        )

    if SAVE_RAW_DATA and not raw_df.empty:
        raw_df.to_csv(RAW_DIR / SUCCESS_PF_RAW_FILENAME, index=False)

    if SAVE_TABLES and not summary_df.empty:
        summary_df.to_csv(
            TABLES_DIR / "pf_success_summary.csv",
            index=False,
        )

    return summary_df, raw_df


def main():
    # Run both 2-a and 2-b

    print("[2-a] Running hazard-count success experiment")
    hazard_summary_df, _ = run_hazard_count_success_experiment()

    print("\n[2-a] Hazard-count success summary")
    print(hazard_summary_df)

    print("\n[2-b] Running p_f success experiment")
    pf_summary_df, _ = run_pf_success_experiment()

    print("\n[2-b] p_f success summary")
    print(pf_summary_df)


if __name__ == "__main__":
    main()