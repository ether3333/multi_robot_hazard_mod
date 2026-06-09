import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from os import PathLike

from experiment_config import (
    FIGURES_NEW_DIR,
    TABLES_NEW_DIR,
    MAP_TIME_NEW_FIG_FILENAME,
    TIME_TABLE_HEATMAP_FIG_FILENAME,
)


def _read_table_with_index(csv_path: str | PathLike) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    first_col = df.columns[0]
    if first_col in {"Unnamed: 0", "index", "", "Unnamed:0"}:
        df = df.set_index(first_col)
    return df


def plot_map_size_time_summary(summary_csv_path: str | PathLike) -> None:
    summary_df = pd.read_csv(summary_csv_path)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(summary_df["map_area"], summary_df["setup_time_mean"], marker="o", label="setup_time")
    ax.plot(summary_df["map_area"], summary_df["calculation_time_mean"], marker="s", label="calculation_time")

    ax.set_title("Map size vs computational time")
    ax.set_xlabel("Map area")
    ax.set_ylabel("Time")
    ax.legend()
    ax.grid(True)

    fig.tight_layout()
    output_path = FIGURES_NEW_DIR / MAP_TIME_NEW_FIG_FILENAME
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {output_path}")


def plot_time_table_heatmaps(setup_csv_path: str | PathLike, calc_csv_path: str | PathLike) -> None:
    setup_df = _read_table_with_index(setup_csv_path)
    calc_df = _read_table_with_index(calc_csv_path)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for ax, df, title in zip(
        axes,
        [setup_df, calc_df],
        ["Setup time", "Calculation time"],
    ):
        im = ax.imshow(df.values, cmap="viridis")
        ax.set_title(title)
        ax.set_xlabel("Number of agents")
        ax.set_ylabel("Number of tasks")

        ax.set_xticks(range(len(df.columns)))
        ax.set_xticklabels(df.columns)
        ax.set_yticks(range(len(df.index)))
        ax.set_yticklabels(df.index)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                value = df.iat[i, j]
                if pd.notna(value):
                    ax.text(j, i, f"{value:.4f}", ha="center", va="center", color="white")

    cbar = fig.colorbar(im, ax=axes.ravel().tolist(), orientation="vertical", fraction=0.05, pad=0.02)
    cbar.set_label("Time")

    fig.suptitle("Time table heatmaps")
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    output_path = FIGURES_NEW_DIR / TIME_TABLE_HEATMAP_FIG_FILENAME
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {output_path}")


def main() -> None:
    FIGURES_NEW_DIR.mkdir(parents=True, exist_ok=True)

    map_size_file = TABLES_NEW_DIR / "map_size_time_summary.csv"
    setup_file = TABLES_NEW_DIR / "time_table_setup.csv"
    calc_file = TABLES_NEW_DIR / "time_table_calculation.csv"

    if not map_size_file.exists():
        raise FileNotFoundError(f"Missing expected file: {map_size_file}")
    if not setup_file.exists():
        raise FileNotFoundError(f"Missing expected file: {setup_file}")
    if not calc_file.exists():
        raise FileNotFoundError(f"Missing expected file: {calc_file}")

    plot_map_size_time_summary(map_size_file)
    plot_time_table_heatmaps(setup_file, calc_file)

    print("All figures created in:", FIGURES_NEW_DIR)


if __name__ == "__main__":
    main()
