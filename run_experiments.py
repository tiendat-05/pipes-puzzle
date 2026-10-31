"""Đo đạc thực nghiệm: 3 kích thước x 5 bàn cờ, 3 cấu hình giải thuật.

Kết quả ghi ra benchmark_summary.json. Chạy: python run_experiments.py
"""

import json
import time
import tracemalloc

from pipes_solver import (
    PipesPuzzle, solve_dfs, solve_astar, validate_solution, enable_utf8_stdout,
)
from puzzle_generator import generate_random_pipes

# Cấu hình 3 kích thước, mỗi kích thước chạy 5 bàn cờ độc lập (seed cố định).
BENCHMARK_CONFIG = [
    {
        "size_label": "5x5",
        "rows": 5, "cols": 5,
        "instances": [
            ("Instance 1", 101),
            ("Instance 2", 102),
            ("Instance 3", 103),
            ("Instance 4", 104),
            ("Instance 5", 105),
        ]
    },
    {
        "size_label": "8x8",
        "rows": 8, "cols": 8,
        "instances": [
            ("Instance 1", 201),
            ("Instance 2", 202),
            ("Instance 3", 203),
            ("Instance 4", 204),
            ("Instance 5", 205),
        ]
    },
    {
        "size_label": "12x12",
        "rows": 12, "cols": 12,
        "instances": [
            ("Instance 1", 301),
            ("Instance 2", 302),
            ("Instance 3", 303),
            ("Instance 4", 304),
            ("Instance 5", 305),
        ]
    },
]

ALGORITHMS = [
    ("Blind Search (DFS)", "dfs", solve_dfs),
    ("Heuristic Search (A* + tie-break)", "astar", solve_astar),
    ("A* không tie-break", "astar_old",
     lambda p: solve_astar(p, tie_mode="none")),
]


def run_benchmark_with_limit(solver_fn, puzzle, repeat=1):
    """Chạy một giải thuật ``repeat`` lần và lấy trung vị thời gian, bộ nhớ đỉnh.

    Lặp lại là cần thiết vì với lưới nhỏ thời gian chỉ cỡ phần mười mili-giây,
    dao động giữa các lần chạy có thể lớn hơn khoảng cách giữa hai thuật toán.
    """
    times, mems = [], []
    nodes = n_steps = 0
    success = valid = False

    for _ in range(max(1, repeat)):
        tracemalloc.start()
        t_start = time.perf_counter()

        success, board, nodes, steps = solver_fn(puzzle)

        t_end = time.perf_counter()
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        times.append((t_end - t_start) * 1000)
        mems.append(peak_mem / 1024)
        n_steps = len(steps)

        if success:
            valid, _msg = validate_solution(puzzle, board)

    def median(vals):
        v = sorted(vals)
        mid = len(v) // 2
        return v[mid] if len(v) % 2 else (v[mid - 1] + v[mid]) / 2

    mean_time = sum(times) / len(times)
    std_time = (sum((t - mean_time) ** 2 for t in times) / len(times)) ** 0.5

    return {
        "success": success,
        "valid": valid,
        "time_ms": median(times),
        "std_ms": std_time,
        "mem_kb": median(mems),
        "nodes": nodes,
        "steps": n_steps,
    }


def main():
    enable_utf8_stdout()

    import argparse
    parser = argparse.ArgumentParser(
        description="Đo đạc thực nghiệm bài toán Pipes.")
    parser.add_argument("--repeat", type=int, default=5,
                        help="Số lần lặp mỗi phép đo, lấy trung vị (mặc định 5).")
    args = parser.parse_args()
    repeat = max(1, args.repeat)
    print(f"(Mỗi phép đo lặp {repeat} lần, lấy trung vị thời gian và bộ nhớ)")

    print("=" * 118)
    print("           BẢNG KẾT QUẢ ĐO ĐẠC THỰC NGHIỆM PIPES (5 INPUT / SIZE)           ")
    print("=" * 118)
    print(f"{'Kích thước':<10} | {'Mẫu Test':<12} | {'Thuật toán':<34} | "
          f"{'Thời gian (ms)':>14} | {'± std':>7} | {'Bộ nhớ (KB)':>11} | "
          f"{'Nodes':>8} | {'Steps':>6} | {'OK':>3}")
    print("-" * 118)

    summary_data = {
        "sizes": [],
        "steps": [],
        "dfs_time": [], "astar_time": [],
        "dfs_mem": [], "astar_mem": [],
        "dfs_nodes": [], "astar_nodes": [],
        "algos": {key: {"time": [], "std": [], "mem": [], "nodes": [], "steps": []}
                  for _label, key, _fn in ALGORITHMS},
        "algo_labels": {key: label for label, key, _fn in ALGORITHMS},
    }

    for item in BENCHMARK_CONFIG:
        size_str = item["size_label"]
        r, c = item["rows"], item["cols"]

        per_algo = {key: {"time": [], "mem": [], "nodes": [], "steps": [], "std": []}
                    for _label, key, _fn in ALGORITHMS}
        all_valid = True

        for inst_name, seed_val in item["instances"]:
            grid = generate_random_pipes(r, c, seed=seed_val)
            puzzle = PipesPuzzle(grid)

            for label, key, solver_fn in ALGORITHMS:
                res = run_benchmark_with_limit(solver_fn, puzzle, repeat=repeat)
                if not res["valid"]:
                    all_valid = False

                per_algo[key]["time"].append(res["time_ms"])
                per_algo[key]["std"].append(res["std_ms"])
                per_algo[key]["mem"].append(res["mem_kb"])
                per_algo[key]["nodes"].append(res["nodes"])
                per_algo[key]["steps"].append(res["steps"])

                print(f"{size_str:<10} | {inst_name:<12} | {label:<34} | "
                      f"{res['time_ms']:>14.3f} | {res['std_ms']:>7.3f} | "
                      f"{res['mem_kb']:>11.2f} | "
                      f"{res['nodes']:>8} | {res['steps']:>6} | "
                      f"{'v' if res['valid'] else 'X':>3}")
            print("-" * 118)

        for label, key, _fn in ALGORITHMS:
            n = len(per_algo[key]["time"])
            avg_t = sum(per_algo[key]["time"]) / n
            avg_m = sum(per_algo[key]["mem"]) / n
            avg_n = sum(per_algo[key]["nodes"]) / n
            avg_s = sum(per_algo[key]["std"]) / n
            print(f"{size_str:<10} | {'* TRUNG BÌNH':<12} | {label:<34} | "
                  f"{avg_t:>14.3f} | {avg_s:>7.3f} | {avg_m:>11.2f} | "
                  f"{avg_n:>8.1f} | {r * c:>6} | {'v' if all_valid else 'X':>3}")

            summary_data["algos"][key]["time"].append(round(avg_t, 3))
            summary_data["algos"][key]["std"].append(round(avg_s, 3))
            summary_data["algos"][key]["mem"].append(round(avg_m, 2))
            summary_data["algos"][key]["nodes"].append(round(avg_n, 1))
            summary_data["algos"][key]["steps"].append(r * c)

        print("=" * 118)

        summary_data["sizes"].append(size_str)
        summary_data["steps"].append(r * c)
        summary_data["dfs_time"].append(summary_data["algos"]["dfs"]["time"][-1])
        summary_data["astar_time"].append(summary_data["algos"]["astar"]["time"][-1])
        summary_data["dfs_mem"].append(summary_data["algos"]["dfs"]["mem"][-1])
        summary_data["astar_mem"].append(summary_data["algos"]["astar"]["mem"][-1])
        summary_data["dfs_nodes"].append(summary_data["algos"]["dfs"]["nodes"][-1])
        summary_data["astar_nodes"].append(summary_data["algos"]["astar"]["nodes"][-1])

    with open("benchmark_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=4, ensure_ascii=False)
    print("-> Đã lưu dữ liệu tổng hợp trung bình vào file: benchmark_summary.json")

    print()
    print("TÓM TẮT TRUNG BÌNH THEO KÍCH THƯỚC")
    print(f"{'size':>6} | {'DFS nodes':>10} | {'A* nodes':>9} | {'A* không tie-break':>20} | "
          f"{'DFS ms':>8} | {'A* ms':>8} | {'A* không tie-break ms':>22}")
    for i, size_str in enumerate(summary_data["sizes"]):
        print(f"{size_str:>6} | "
              f"{summary_data['algos']['dfs']['nodes'][i]:>10} | "
              f"{summary_data['algos']['astar']['nodes'][i]:>9} | "
              f"{summary_data['algos']['astar_old']['nodes'][i]:>20} | "
              f"{summary_data['algos']['dfs']['time'][i]:>8.2f} | "
              f"{summary_data['algos']['astar']['time'][i]:>8.2f} | "
              f"{summary_data['algos']['astar_old']['time'][i]:>22.2f}")


if __name__ == "__main__":
    main()
