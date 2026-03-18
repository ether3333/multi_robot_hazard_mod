# 1-a,b : Time complexity

import pandas as pd

from experiment_config import (
    SAVE_RAW_DATA,
    SAVE_TABLES,
    TABLES_DIR,
    RAW_DIR,
    TIME_TABLE_AGENT_COUNTS,
    TIME_TABLE_TASK_COUNTS,
    TIME_TABLE_SETUP_FILENAME,
    TIME_TABLE_CALC_FILENAME,
    MAP_TIME_RAW_FILENAME,
    TIME_EXPERIMENT_SEEDS,
    DEFAULT_NUM_INITIAL_CONDITIONS,
    get_time_table_fixed_config,
    get_map_time_fixed_config,
    get_map_size_from_scale,
    MAP_SIZE_SCALES,
)

from experiment_runner import (
    repeat_same_setting,
    results_to_list_of_dicts,
)

# ============================================================
# run_time_experiment.py
# Run 1-a and 1-b time experiments.
# 1-a: agents x tasks -> setup_time, calculation_time tables
# 1-b: map size -> setup_time, calculation_time data
# ============================================================


def _mean_or_nan(series: pd.Series) -> float:
    # Return mean value or NaN
    if len(series) == 0:
        return float("nan")
    return float(series.mean())


def _results_to_dataframe(results):
    # Convert result objects into a dataframe
    rows = results_to_list_of_dicts(results)
    return pd.DataFrame(rows)


def run_time_table_experiment():
    # Run 1-a experiment
    # x-axis: agents
    # y-axis: tasks

    fixed_cfg = get_time_table_fixed_config()

    setup_table = pd.DataFrame(
        index=TIME_TABLE_TASK_COUNTS,
        columns=TIME_TABLE_AGENT_COUNTS,
        dtype=float,
    )
    calc_table = pd.DataFrame(
        index=TIME_TABLE_TASK_COUNTS,
        columns=TIME_TABLE_AGENT_COUNTS,
        dtype=float,
    )

    raw_frames = []

    for num_tasks in TIME_TABLE_TASK_COUNTS:
        for num_agents in TIME_TABLE_AGENT_COUNTS:
            results = repeat_same_setting(
                seeds=fixed_cfg["seeds"],
                num_agents=num_agents,
                num_tasks=num_tasks,
                map_width=fixed_cfg["map_width"],
                map_height=fixed_cfg["map_height"],
                num_hazards=fixed_cfg["num_hazards"],
                p_f=fixed_cfg["p_f"],
                num_initial_conditions=DEFAULT_NUM_INITIAL_CONDITIONS,
                experiment_name="time_table",
            )

            print(results)

            df = _results_to_dataframe(results)
            df["experiment_type"] = "1a_time_table"
            raw_frames.append(df)

            setup_table.loc[num_tasks, num_agents] = _mean_or_nan(df["setup_time"])
            calc_table.loc[num_tasks, num_agents] = _mean_or_nan(df["calculation_time"])

    setup_table.index.name = "num_tasks"
    setup_table.columns.name = "num_agents"

    calc_table.index.name = "num_tasks"
    calc_table.columns.name = "num_agents"

    raw_df = pd.concat(raw_frames, ignore_index=True) if raw_frames else pd.DataFrame()

    if SAVE_TABLES:
        setup_table.to_csv(TABLES_DIR / TIME_TABLE_SETUP_FILENAME)
        calc_table.to_csv(TABLES_DIR / TIME_TABLE_CALC_FILENAME)

    if SAVE_RAW_DATA and not raw_df.empty:
        raw_df.to_csv(RAW_DIR / "time_table_raw.csv", index=False)

    return setup_table, calc_table, raw_df


def run_map_size_time_experiment():
    # Run 1-b experiment
    # Change map size and measure times

    fixed_cfg = get_map_time_fixed_config()
    raw_frames = []

    for scale in MAP_SIZE_SCALES:
        map_width, map_height = get_map_size_from_scale(
            scale=scale,
            ratio=fixed_cfg["map_ratio"],
        )

        results = repeat_same_setting(
            seeds=fixed_cfg["seeds"],
            num_agents=fixed_cfg["num_agents"],
            num_tasks=fixed_cfg["num_tasks"],
            map_width=map_width,
            map_height=map_height,
            num_hazards=fixed_cfg["num_hazards"],
            p_f=fixed_cfg["p_f"],
            num_initial_conditions=DEFAULT_NUM_INITIAL_CONDITIONS,
            experiment_name="map_size_time",
        )

        df = _results_to_dataframe(results)
        df["experiment_type"] = "1b_map_size_time"
        df["map_scale"] = scale
        df["map_ratio_w"] = fixed_cfg["map_ratio"][0]
        df["map_ratio_h"] = fixed_cfg["map_ratio"][1]
        df["map_area"] = map_width * map_height
        raw_frames.append(df)

    raw_df = pd.concat(raw_frames, ignore_index=True) if raw_frames else pd.DataFrame()

    if raw_df.empty:
        summary_df = pd.DataFrame(
            columns=[
                "map_scale",
                "map_width",
                "map_height",
                "map_area",
                "setup_time_mean",
                "calculation_time_mean",
            ]
        )
    else:
        summary_df = (
            raw_df.groupby(["map_scale", "map_width", "map_height", "map_area"], as_index=False)
            .agg(
                setup_time_mean=("setup_time", "mean"),
                calculation_time_mean=("calculation_time", "mean"),
            )
            .sort_values(by="map_scale")
            .reset_index(drop=True)
        )

    if SAVE_RAW_DATA and not raw_df.empty:
        raw_df.to_csv(RAW_DIR / MAP_TIME_RAW_FILENAME, index=False)

    if SAVE_TABLES and not summary_df.empty:
        summary_df.to_csv(TABLES_DIR / "map_size_time_summary.csv", index=False)

    return summary_df, raw_df


def main():
    # Run both 1-a and 1-b

    print("[1-a] Running time table experiment")
    setup_table, calc_table, _ = run_time_table_experiment()

    print("\n[1-a] Setup time table")
    print(setup_table)

    print("\n[1-a] Calculation time table")
    print(calc_table)

    print("\n[1-b] Running map size time experiment")
    summary_df, _ = run_map_size_time_experiment()

    print("\n[1-b] Map size time summary")
    print(summary_df)


if __name__ == "__main__":
    main()