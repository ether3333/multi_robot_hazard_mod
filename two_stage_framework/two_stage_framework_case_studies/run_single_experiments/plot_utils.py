import matplotlib.pyplot as plt
import pandas as pd

from experiment_config import (
    SAVE_FIGURES,
    FIGURES_DIR,
    MAP_TIME_FIG_FILENAME,
    SUCCESS_HAZARD_FIG_FILENAME,
    SUCCESS_PF_FIG_FILENAME,
)

# ============================================================
# plot_utils.py
# Plot tables and experiment results.
# ============================================================


def plot_time_table_heatmap(
    table_df: pd.DataFrame,
    title: str,
    save_name: str | None = None,
    figsize: tuple[int, int] = (8, 6),
):
    # Plot a heatmap-like table with text values

    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(table_df.values)

    ax.set_title(title)
    ax.set_xlabel("Number of agents")
    ax.set_ylabel("Number of tasks")

    ax.set_xticks(range(len(table_df.columns)))
    ax.set_xticklabels(table_df.columns)

    ax.set_yticks(range(len(table_df.index)))
    ax.set_yticklabels(table_df.index)

    for i in range(table_df.shape[0]):
        for j in range(table_df.shape[1]):
            value = table_df.iloc[i, j]
            if pd.notna(value):
                ax.text(j, i, f"{value:.4f}", ha="center", va="center")

    fig.tight_layout()

    if SAVE_FIGURES and save_name is not None:
        fig.savefig(FIGURES_DIR / save_name, dpi=300, bbox_inches="tight")

    return fig, ax


def plot_map_size_time(
    summary_df: pd.DataFrame,
    x_col: str = "map_area",
    setup_col: str = "setup_time_mean",
    calc_col: str = "calculation_time_mean",
    save_name: str = MAP_TIME_FIG_FILENAME,
    figsize: tuple[int, int] = (8, 5),
):
    # Plot setup time and calculation time against map size

    fig, ax = plt.subplots(figsize=figsize)

    ax.plot(summary_df[x_col], summary_df[setup_col], marker="o", label="setup_time")
    ax.plot(summary_df[x_col], summary_df[calc_col], marker="s", label="calculation_time")

    ax.set_title("Map size vs computational time")
    ax.set_xlabel("Map area")
    ax.set_ylabel("Time")
    ax.legend()
    ax.grid(True)

    fig.tight_layout()

    if SAVE_FIGURES:
        fig.savefig(FIGURES_DIR / save_name, dpi=300, bbox_inches="tight")

    return fig, ax


def plot_success_boxplot(
    raw_df: pd.DataFrame,
    group_col: str,
    title: str,
    xlabel: str,
    save_name: str,
    success_col: str = "success",
    figsize: tuple[int, int] = (8, 5),
):
    # Plot a boxplot for grouped success values

    unique_groups = sorted(raw_df[group_col].dropna().unique())
    data = [raw_df.loc[raw_df[group_col] == value, success_col].tolist() for value in unique_groups]

    fig, ax = plt.subplots(figsize=figsize)

    ax.boxplot(data, labels=unique_groups)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Success")
    ax.grid(True)

    fig.tight_layout()

    if SAVE_FIGURES:
        fig.savefig(FIGURES_DIR / save_name, dpi=300, bbox_inches="tight")

    return fig, ax


def plot_hazard_count_success_boxplot(
    raw_df: pd.DataFrame,
    save_name: str = SUCCESS_HAZARD_FIG_FILENAME,
):
    # Plot boxplot for 2-a

    return plot_success_boxplot(
        raw_df=raw_df,
        group_col="hazard_count",
        title="Success rate vs number of hazards",
        xlabel="Number of hazards",
        save_name=save_name,
    )


def plot_pf_success_boxplot(
    raw_df: pd.DataFrame,
    save_name: str = SUCCESS_PF_FIG_FILENAME,
):
    # Plot boxplot for 2-b

    return plot_success_boxplot(
        raw_df=raw_df,
        group_col="pf_value",
        title="Success rate vs p_f",
        xlabel="p_f",
        save_name=save_name,
    )


def save_dataframe_as_csv(
    df: pd.DataFrame,
    save_path,
):
    # Save dataframe to csv
    df.to_csv(save_path, index=False)


def show_all_plots():
    # Show all open figures
    plt.show()