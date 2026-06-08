# File for setting values of experiment
# list of agents candidate, list of tasks candidate, map ratio, list of map scale candidate, list of hazard count candidate, list of p_f candidate
# shared success seeds, time experiment seeds
# basis map to fix/ robot / target / hazard position-related values, saved repository values

from pathlib import Path

# ============================================================
# experiment_config.py
# Store all experiment settings in one place.
# ============================================================

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
TABLES_DIR = RESULTS_DIR / "tables"
TABLES_NEW_DIR = RESULTS_DIR / "tables_new"
RAW_DIR = RESULTS_DIR / "raw"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_NEW_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Common options
# -----------------------------
SAVE_TABLES = True
SAVE_FIGURES = True
SAVE_RAW_DATA = True
VERBOSE = True

# -----------------------------
# Seeds
# 2-a and 2-b must use the same seeds
# -----------------------------
SHARED_SUCCESS_SEEDS = [0, 1, 2, 3, 4, 5, 6, 7] # modified to increase number of trials

# Separate seeds for time experiments
TIME_EXPERIMENT_SEEDS = [0, 1, 2, 3, 4, 5, 6, 7]

# Separate seeds for map-size time means
MAP_TIME_EXPERIMENT_SEEDS = TIME_EXPERIMENT_SEEDS

# -----------------------------
# Default environment settings
# These are the default fixed values
# -----------------------------
DEFAULT_NUM_AGENTS = 2
DEFAULT_NUM_TASKS = 2

DEFAULT_MAP_WIDTH = 16
DEFAULT_MAP_HEIGHT = 32

# Default map ratio: width : height = 1 : 2
DEFAULT_MAP_RATIO = (1, 2)

# Default hazard settings
DEFAULT_NUM_HAZARDS = 1
DEFAULT_P_F = 0.02

# Number of repeated initial conditions
DEFAULT_NUM_INITIAL_CONDITIONS = 2

# Keep hazard positions fixed or not
FIX_HAZARD_POSITIONS = True

# Keep robot, task, and map fixed or not
FIX_ROBOT_TASK_MAP = True

# -----------------------------
# 1-a. Time table experiment
# x-axis: number of agents
# y-axis: number of tasks
# cell values: setup_time and calculation_time
# -----------------------------
TIME_TABLE_AGENT_COUNTS = [1, 2, 3]
TIME_TABLE_TASK_COUNTS = [1, 2, 3]

# Fixed values for 1-a
TIME_TABLE_FIXED_MAP_WIDTH = DEFAULT_MAP_WIDTH
TIME_TABLE_FIXED_MAP_HEIGHT = DEFAULT_MAP_HEIGHT
TIME_TABLE_FIXED_NUM_HAZARDS = DEFAULT_NUM_HAZARDS
TIME_TABLE_FIXED_P_F = DEFAULT_P_F

# -----------------------------
# 1-b. Map size vs time
# Keep width:height ratio fixed
# scale means the width multiplier
# -----------------------------
MAP_SIZE_RATIO = (1, 2)
MAP_SIZE_SCALES = [8, 12, 16, 20, 24]

# Fixed values for 1-b
MAP_TIME_FIXED_NUM_AGENTS = DEFAULT_NUM_AGENTS
MAP_TIME_FIXED_NUM_TASKS = DEFAULT_NUM_TASKS
MAP_TIME_FIXED_NUM_HAZARDS = DEFAULT_NUM_HAZARDS
MAP_TIME_FIXED_P_F = DEFAULT_P_F

# -----------------------------
# 2-a. Number of hazards vs success rate
# Keep agents, tasks, map, and p_f fixed
# Change only the number of hazards
# -----------------------------
SUCCESS_HAZARD_COUNT_LIST = [1, 2, 3, 4, 5]

SUCCESS_HAZARD_FIXED_NUM_AGENTS = DEFAULT_NUM_AGENTS
SUCCESS_HAZARD_FIXED_NUM_TASKS = DEFAULT_NUM_TASKS
SUCCESS_HAZARD_FIXED_MAP_WIDTH = DEFAULT_MAP_WIDTH
SUCCESS_HAZARD_FIXED_MAP_HEIGHT = DEFAULT_MAP_HEIGHT
SUCCESS_HAZARD_FIXED_P_F = DEFAULT_P_F

# -----------------------------
# 2-b. p_f vs success rate
# Keep agents, tasks, map, and hazard count fixed
# Change only p_f
# -----------------------------
SUCCESS_PF_LIST = [0.02, 0.04, 0.06, 0.08, 0.1]

SUCCESS_PF_FIXED_NUM_AGENTS = DEFAULT_NUM_AGENTS
SUCCESS_PF_FIXED_NUM_TASKS = DEFAULT_NUM_TASKS
SUCCESS_PF_FIXED_MAP_WIDTH = DEFAULT_MAP_WIDTH
SUCCESS_PF_FIXED_MAP_HEIGHT = DEFAULT_MAP_HEIGHT
SUCCESS_PF_FIXED_NUM_HAZARDS = DEFAULT_NUM_HAZARDS

# -----------------------------
# 2-c. Number of tasks vs success rate
# Keep agents (=2), map, hazards, and p_f fixed
# Change only the number of tasks
# -----------------------------
SUCCESS_TASK_COUNT_LIST = [2, 3, 4, 5]

SUCCESS_TASK_FIXED_NUM_AGENTS = 2
SUCCESS_TASK_FIXED_MAP_WIDTH = DEFAULT_MAP_WIDTH
SUCCESS_TASK_FIXED_MAP_HEIGHT = DEFAULT_MAP_HEIGHT
SUCCESS_TASK_FIXED_NUM_HAZARDS = DEFAULT_NUM_HAZARDS
SUCCESS_TASK_FIXED_P_F = DEFAULT_P_F

# -----------------------------
# Output file names
# -----------------------------
TIME_TABLE_SETUP_FILENAME = "time_table_setup.csv"
TIME_TABLE_CALC_FILENAME = "time_table_calculation.csv"

MAP_TIME_RAW_FILENAME = "map_size_vs_time_raw.csv"
MAP_TIME_FIG_FILENAME = "map_size_vs_time.png"

SUCCESS_HAZARD_RAW_FILENAME = "hazard_count_vs_success_raw.csv"
SUCCESS_HAZARD_FIG_FILENAME = "hazard_count_vs_success_boxplot.png"
TASKS_RESCUED_HAZARD_FIG_FILENAME = "hazard_count_vs_tasks_rescued_boxplot.png"

SUCCESS_PF_RAW_FILENAME = "pf_vs_success_raw.csv"
SUCCESS_PF_FIG_FILENAME = "pf_vs_success_boxplot.png"
TASKS_RESCUED_PF_FIG_FILENAME = "pf_vs_tasks_rescued_boxplot.png"

SUCCESS_TASK_RAW_FILENAME = "task_count_vs_success_raw.csv"
SUCCESS_TASK_FIG_FILENAME = "task_count_vs_success_boxplot.png"
TASKS_RESCUED_TASK_FIG_FILENAME = "task_count_vs_tasks_rescued_boxplot.png"

# -----------------------------
# Helper functions
# -----------------------------
def get_map_size_from_scale(scale: int, ratio: tuple[int, int] = MAP_SIZE_RATIO) -> tuple[int, int]:
    # Make map size from scale and ratio
    ratio_w, ratio_h = ratio
    width = scale * ratio_w
    height = scale * ratio_h
    return width, height


def get_time_table_fixed_config() -> dict:
    # Fixed settings for 1-a
    return {
        "map_width": TIME_TABLE_FIXED_MAP_WIDTH,
        "map_height": TIME_TABLE_FIXED_MAP_HEIGHT,
        "num_hazards": TIME_TABLE_FIXED_NUM_HAZARDS,
        "p_f": TIME_TABLE_FIXED_P_F,
        "seeds": TIME_EXPERIMENT_SEEDS,
    }


def get_map_time_fixed_config() -> dict:
    # Fixed settings for 1-b
    return {
        "num_agents": MAP_TIME_FIXED_NUM_AGENTS,
        "num_tasks": MAP_TIME_FIXED_NUM_TASKS,
        "num_hazards": MAP_TIME_FIXED_NUM_HAZARDS,
        "p_f": MAP_TIME_FIXED_P_F,
        "seeds": MAP_TIME_EXPERIMENT_SEEDS,
        "map_ratio": MAP_SIZE_RATIO,
    }


def get_success_hazard_fixed_config() -> dict:
    # Fixed settings for 2-a
    return {
        "num_agents": SUCCESS_HAZARD_FIXED_NUM_AGENTS,
        "num_tasks": SUCCESS_HAZARD_FIXED_NUM_TASKS,
        "map_width": SUCCESS_HAZARD_FIXED_MAP_WIDTH,
        "map_height": SUCCESS_HAZARD_FIXED_MAP_HEIGHT,
        "p_f": SUCCESS_HAZARD_FIXED_P_F,
        "seeds": SHARED_SUCCESS_SEEDS,
        "num_initial_conditions": DEFAULT_NUM_INITIAL_CONDITIONS,
    }


def get_success_pf_fixed_config() -> dict:
    # Fixed settings for 2-b
    return {
        "num_agents": SUCCESS_PF_FIXED_NUM_AGENTS,
        "num_tasks": SUCCESS_PF_FIXED_NUM_TASKS,
        "map_width": SUCCESS_PF_FIXED_MAP_WIDTH,
        "map_height": SUCCESS_PF_FIXED_MAP_HEIGHT,
        "num_hazards": SUCCESS_PF_FIXED_NUM_HAZARDS,
        "seeds": SHARED_SUCCESS_SEEDS,
        "num_initial_conditions": DEFAULT_NUM_INITIAL_CONDITIONS,
    }


def get_success_task_count_fixed_config() -> dict:
    # Fixed settings for 2-c
    return {
        "num_agents": SUCCESS_TASK_FIXED_NUM_AGENTS,
        "map_width": SUCCESS_TASK_FIXED_MAP_WIDTH,
        "map_height": SUCCESS_TASK_FIXED_MAP_HEIGHT,
        "num_hazards": SUCCESS_TASK_FIXED_NUM_HAZARDS,
        "p_f": SUCCESS_TASK_FIXED_P_F,
        "seeds": SHARED_SUCCESS_SEEDS,
        "num_initial_conditions": DEFAULT_NUM_INITIAL_CONDITIONS,
    }
