import os
import time
import warnings
from pathlib import Path
from typing import Any

import numpy as np

from Parameters import Parameters
from Matrix import Matrix
from Path_Planner import Path_Planner
from Function_Frame import Function_Frame
from Forward_Greedy_Allocator import Forward_Greedy_Allocator
from Reverse_Greedy_Allocator import Reverse_Greedy_Allocator

try:
    from shapely.geometry import MultiLineString, Point

    SHAPELY_AVAILABLE = True
except Exception:
    SHAPELY_AVAILABLE = False


def generate_Tau_X(self):
    p_stay = self.p_stay

    for u in self.U_x.U:
        matrix_u = Matrix(self.domain_matrix, np.zeros(tuple([len(e) for e in self.domain_matrix])))
        if u == "0":
            for x in self.X:
                matrix_u.set([x, x], 1)
        else:
            for x in self.X:
                if self.U_x.is_u_in_U_x_(u, x):
                    xx = self.U_x.get_xx_u(x, u)
                    matrix_u.set([x, x], p_stay)
                    matrix_u.set([x, xx], 1 - p_stay)
        self[u] = matrix_u


def sample_Tau_Ys(self, p_f, ys_k_1):
    ys_0 = ~ys_k_1
    ys_1 = ys_k_1

    N_ys = self.X.adj_matrix.T.dot(ys_1.T.astype(int)).T
    D_ys = self.X.adj_diag_matrix.T.dot(ys_1.T.astype(int)).T

    p_cont = 1 - (((1 - p_f) ** N_ys) * ((1 - p_f / np.sqrt(2)) ** D_ys))
    rand = np.random.rand(*ys_1.shape)
    ys_cont = rand <= p_cont

    ys_k = ys_k_1
    ys_k[ys_0] = ys_cont[ys_0]
    return ys_k


class LabGridworld:
    def __init__(self, width, height, x_min=-1.5, x_max=1.5, y_min=-3.0, y_max=3.0):
        self.width = width
        self.height = height
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.dx = (x_max - x_min) / width
        self.dy = (y_max - y_min) / height
        self.gridsize = max(self.dx, self.dy)

    def get_dim(self):
        return self.width, self.height

    def get_center(self, cell):
        x, y = cell
        cx = self.x_min + (x + 0.5) * self.dx
        cy = self.y_min + (y + 0.5) * self.dy
        return (cx, cy)

    def world_to_cell(self, pt):
        x, y = pt
        cx = int((x - self.x_min) / self.dx)
        cy = int((y - self.y_min) / self.dy)
        cx = max(0, min(self.width - 1, cx))
        cy = max(0, min(self.height - 1, cy))
        return (cx, cy)


LAB_OBSTACLE_LINES = [
    [[-1.498, 3.001], [0.001, 3.000]],
    [[1.051, 3.001], [1.494, 3.000]],
    [[1.494, 3.000], [1.493, 0.430]],
    [[1.494, -0.374], [1.497, -2.998]],
    [[0.002, -2.999], [1.497, -2.998]],
    [[-1.498, -2.999], [-1.047, -2.999]],
    [[-1.496, -0.500], [-1.498, -2.999]],
    [[-1.496, 0.750], [-1.495, 0.299]],
    [[-1.498, 2.998], [-1.498, 1.553]],
    [[-0.481, 2.382], [0.879, 1.356]],
    [[-1.498, 1.553], [-0.700, 1.551]],
    [[1.018, 0.429], [1.493, 0.430]],
    [[0.141, 1.040], [-0.269, 0.524]],
    [[-1.496, 0.526], [-0.269, 0.524]],
    [[-0.269, 0.524], [-0.261, -0.008]],
    [[-0.261, -0.008], [0.480, -0.008]],
    [[0.011, -0.008], [0.011, -0.486]],
    [[-1.496, -0.859], [-0.492, -0.860]],
    [[0.922, -0.613], [0.924, -2.093]],
    [[0.260, -1.084], [0.260, -2.093]],
    [[-0.665, -2.094], [0.924, -2.093]],
    [[-0.685, -2.103], [-0.931, -2.414]],
]

LAB_EXIT_LINES = [
    [[-1.498, 1.553], [-1.496, 0.750]],
    [[-1.495, 0.299], [-1.494, -0.500]],
    [[-1.050, -2.999], [0.002, -2.999]],
    [[1.494, -0.374], [1.497, 0.430]],
    [[0.001, 3.001], [1.051, 3.001]],
]

ROBOT_LINESTYLES = [
    (0, ()),
    (0, (3, 3)),
    (0, (1, 2)),
    (0, (5, 2)),
    (0, (3, 1, 1, 1)),
]


def point_segment_distance(px, py, ax, ay, bx, by):
    abx = bx - ax
    aby = by - ay
    apx = px - ax
    apy = py - ay
    ab2 = abx * abx + aby * aby
    if ab2 == 0:
        return np.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, (apx * abx + apy * aby) / ab2))
    qx = ax + t * abx
    qy = ay + t * aby
    return np.hypot(px - qx, py - qy)


def add_points(gridworld, state, lines, obst=None):
    width, height = gridworld.get_dim()
    threshold = gridworld.gridsize / 2 + 0.03

    if SHAPELY_AVAILABLE:
        linestrings = MultiLineString(lines)
        for x in range(width):
            for y in range(height):
                center = Point(gridworld.get_center((x, y)))
                if center.distance(linestrings) < threshold:
                    if obst is not None and obst[x, y] == 1:
                        continue
                    state[x, y] = 1
        return state

    for x in range(width):
        for y in range(height):
            px, py = gridworld.get_center((x, y))
            min_d = min(
                point_segment_distance(px, py, line[0][0], line[0][1], line[1][0], line[1][1])
                for line in lines
            )
            if min_d < threshold:
                if obst is not None and obst[x, y] == 1:
                    continue
                state[x, y] = 1
    return state


def build_lab_obstacle_map(width=30, height=60):
    gridworld = LabGridworld(width, height)
    obstacles_xy = np.zeros((width, height), dtype=int)
    add_points(gridworld, obstacles_xy, LAB_OBSTACLE_LINES)
    return gridworld, obstacles_xy.T.astype(int)


def build_exit_cells(gridworld, map_yx):
    width, height = gridworld.get_dim()
    exits_xy = np.zeros((width, height), dtype=int)
    add_points(gridworld, exits_xy, LAB_EXIT_LINES, obst=map_yx.T)
    exit_cells = [(x, y) for x in range(width) for y in range(height) if exits_xy[x, y] == 1]
    if len(exit_cells) == 0:
        midpoints = [((e[0][0] + e[1][0]) / 2.0, (e[0][1] + e[1][1]) / 2.0) for e in LAB_EXIT_LINES]
        return world_points_to_free_cells(gridworld, map_yx, midpoints)
    return sorted(list(set(exit_cells)))


def nearest_free_cell(map_yx, cell):
    width = map_yx.shape[1]
    height = map_yx.shape[0]
    x0, y0 = cell
    x0 = max(0, min(width - 1, x0))
    y0 = max(0, min(height - 1, y0))
    if map_yx[y0, x0] == 0:
        return (x0, y0)

    max_r = max(width, height)
    for r in range(1, max_r + 1):
        x_min = max(0, x0 - r)
        x_max = min(width - 1, x0 + r)
        y_min = max(0, y0 - r)
        y_max = min(height - 1, y0 + r)
        for x in range(x_min, x_max + 1):
            for y in (y_min, y_max):
                if map_yx[y, x] == 0:
                    return (x, y)
        for y in range(y_min + 1, y_max):
            for x in (x_min, x_max):
                if map_yx[y, x] == 0:
                    return (x, y)
    raise ValueError("No free cell found in the map.")


def world_points_to_free_cells(gridworld, map_yx, points):
    out = []
    for pt in points:
        cell = gridworld.world_to_cell(pt)
        out.append(nearest_free_cell(map_yx, cell))
    return out


def _make_experiment_name(seed, num_agents, num_tasks, map_width, map_height, num_hazards, p_f):
    p_f_tag = str(p_f).replace(".", "p")
    return (
        f"lab_exp_seed{seed}_a{num_agents}_t{num_tasks}_"
        f"m{map_width}x{map_height}_h{num_hazards}_pf{p_f_tag}"
    )


def _get_free_cells(map_yx):
    free_cells_yx = np.argwhere(map_yx == 0)
    return [(int(x), int(y)) for y, x in free_cells_yx]


def _sample_unique_free_cells(map_yx, count, rng, excluded=None):
    excluded_cells = set() if excluded is None else set(excluded)
    candidates = [cell for cell in _get_free_cells(map_yx) if cell not in excluded_cells]
    if count > len(candidates):
        raise ValueError(
            f"Requested {count} unique cells but only {len(candidates)} free cells are available."
        )

    order = rng.permutation(len(candidates))[:count]
    return [candidates[int(idx)] for idx in order]


def _build_parameters(seed, num_agents, num_tasks, map_width, map_height, num_hazards, p_f):
    rng = np.random.default_rng(seed)
    example_name = _make_experiment_name(
        seed=seed,
        num_agents=num_agents,
        num_tasks=num_tasks,
        map_width=map_width,
        map_height=map_height,
        num_hazards=num_hazards,
        p_f=p_f,
    )

    parameters = Parameters(name=example_name)
    gridworld, parameters.map = build_lab_obstacle_map(width=map_width, height=map_height)
    parameters.goal = build_exit_cells(gridworld, parameters.map)

    reserved = set(parameters.goal)
    parameters.robot_positions = _sample_unique_free_cells(parameters.map, num_agents, rng, reserved)
    reserved.update(parameters.robot_positions)
    parameters.targets = _sample_unique_free_cells(parameters.map, num_tasks, rng, reserved)
    reserved.update(parameters.targets)
    hazard_cells = _sample_unique_free_cells(parameters.map, num_hazards, rng, reserved)

    parameters.task_ids = [f"t{i + 1}" for i in range(num_tasks)]
    parameters.robot_ids = [str(i + 1) for i in range(num_agents)]
    parameters.robot_linestyles = [
        ROBOT_LINESTYLES[i % len(ROBOT_LINESTYLES)] for i in range(num_agents)
    ]
    parameters.y_0 = [[cell] for cell in hazard_cells]
    parameters.hazard_ids = [f"h{i + 1}" for i in range(num_hazards)]
    parameters.p_f = [p_f for _ in range(num_hazards)]

    parameters.E = 1200
    parameters.N = 50
    parameters.p_stay = 0

    parameters.generate_obsticles()
    parameters.generate_Hazards()
    parameters.generate_Tasks()
    parameters.generate_Robots()
    parameters.generate_Tau_X = generate_Tau_X
    parameters.sample_Tau_Ys = sample_Tau_Ys

    return parameters


def _prepare_case_study_dir(parameters):
    base_dir = Path(__file__).resolve().parent
    path = base_dir / "case_studies" / parameters.name
    path.mkdir(parents=True, exist_ok=True)

    parameters.parameters_file = {"Read": False, "Name": "parameters"}
    parameters.samples_file = {"Read": False, "Name": "samples"}
    parameters.function_frame_file = {"Read": False, "Name": "function_frame"}
    parameters.solution_file = {"Read": False, "Name": "solution"}

    return str(path) + os.sep


def _extract_success(solution):
    objective_value = getattr(solution, "objective_value", None)
    if isinstance(objective_value, dict):
        group_value = objective_value.get("group", 0.0)
        return float(group_value)
    return float(objective_value)


def run_single_experiment(
    seed: int,
    num_agents: int,
    num_tasks: int,
    map_width: int,
    map_height: int,
    num_hazards: int,
    p_f: float,
    algorithm: str = "forward_greedy",
) -> dict[str, Any]:
    warnings.filterwarnings("ignore")

    parameters = _build_parameters(
        seed=seed,
        num_agents=num_agents,
        num_tasks=num_tasks,
        map_width=map_width,
        map_height=map_height,
        num_hazards=num_hazards,
        p_f=p_f,
    )
    path = _prepare_case_study_dir(parameters)

    setup_start = time.perf_counter()
    path_planner = Path_Planner(parameters)
    path_planner.set_up(path)
    function_frame = Function_Frame(parameters, path_planner)

    if algorithm == "forward_greedy":
        allocator = Forward_Greedy_Allocator(function_frame)
    elif algorithm == "reverse_greedy":
        allocator = Reverse_Greedy_Allocator(function_frame)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    setup_wallclock = time.perf_counter() - setup_start

    solution = allocator.solve_problem()
    allocator.add_optimal_policies(solution)
    allocator.add_optimal_paths(solution)
    allocator.add_group_objective(solution)

    function_frame_time = float(function_frame.instrument.data.get("calculation_time", 0.0))
    allocator_setup_time = float(solution.time_data.get("setup_time", 0.0))
    calculation_time = float(solution.time_data.get("calculation_time", 0.0))
    objective_value = getattr(solution, "objective_value", None)
    success_rate = objective_value.get("group", None) if isinstance(objective_value, dict) else None

    return {
        "time_dict": {
            "setup_time": max(setup_wallclock, function_frame_time + allocator_setup_time),
            "calculation_time": calculation_time,
        },
        # "success": _extract_success(solution),
        # "success_rate": success_rate,
        "success": float(success_rate) if success_rate is not None else 0.0,
    }


def main():
    result = run_single_experiment(
        seed=0,
        num_agents=2,
        num_tasks=2,
        map_width=16,
        map_height=32,
        num_hazards=1,
        p_f=0.05,
    )
    print(result)


if __name__ == "__main__":
    main()
