# run_experiments.py
import time
import tracemalloc
import json
from pipes_solver import PipesPuzzle, solve_dfs, solve_astar
from puzzle_generator import generate_random_pipes

# Cấu hình 3 kích thước, mỗi kích thước chạy 5 bàn cờ độc lập (seed cố định)
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
    }
]

def run_benchmark_with_limit(solver_fn, puzzle):
    tracemalloc.start()
    t_start = time.perf_counter()

    success, board, nodes, steps = solver_fn(puzzle)

    t_end = time.perf_counter()
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    exec_time_ms = (t_end - t_start) * 1000
    peak_mem_kb = peak_mem / 1024

    return success, exec_time_ms, peak_mem_kb, nodes, len(steps)

if __name__ == "__main__":
    print("=" * 118)
    print("                 BẢNG KẾT QUẢ ĐO ĐẠC THỰC NGHIỆM PIPES (5 INSTANCES / SIZE)                       ")
    print("=" * 118)
    print(f"{'Kích thước':<10} | {'Mẫu Test':<14} | {'Thuật toán':<10} | {'Thời gian (ms)':<16} | {'Bộ nhớ (KB)':<13} | {'Nodes Expand':<14} | {'Độ dài (Steps)':<14}")
    print("-" * 118)

    summary_data = {
        "sizes": [],
        "steps": [],
        "dfs_time": [], "astar_time": [],
        "dfs_mem": [],  "astar_mem": [],
        "dfs_nodes": [], "astar_nodes": []
    }

    for item in BENCHMARK_CONFIG:
        size_str = item["size_label"]
        r, c = item["rows"], item["cols"]

        dfs_times, astar_times = [], []
        dfs_mems, astar_mems = [], []
        dfs_nodes_list, astar_nodes_list = [], []

        for inst_name, seed_val in item["instances"]:
            grid = generate_random_pipes(r, c, seed=seed_val)
            puzzle = PipesPuzzle(grid)

            # 1. Đo DFS
            s_dfs, t_dfs, m_dfs, n_dfs, len_dfs = run_benchmark_with_limit(solve_dfs, puzzle)
            dfs_times.append(t_dfs)
            dfs_mems.append(m_dfs)
            dfs_nodes_list.append(n_dfs)
            print(f"{size_str:<10} | {inst_name:<14} | {'DFS':<10} | {t_dfs:<16.2f} | {m_dfs:<13.2f} | {n_dfs:<14} | {len_dfs:<14}")

            # 2. Đo A*
            s_ast, t_ast, m_ast, n_ast, len_ast = run_benchmark_with_limit(solve_astar, puzzle)
            astar_times.append(t_ast)
            astar_mems.append(m_ast)
            astar_nodes_list.append(n_ast)
            print(f"{size_str:<10} | {inst_name:<14} | {'A*':<10} | {t_ast:<16.2f} | {m_ast:<13.2f} | {n_ast:<14} | {len_ast:<14}")
            print("-" * 118)

        # Tính trung bình cộng (AVG) của 5 mẫu
        avg_t_dfs = sum(dfs_times) / len(dfs_times)
        avg_m_dfs = sum(dfs_mems) / len(dfs_mems)
        avg_n_dfs = sum(dfs_nodes_list) / len(dfs_nodes_list)

        avg_t_ast = sum(astar_times) / len(astar_times)
        avg_m_ast = sum(astar_mems) / len(astar_mems)
        avg_n_ast = sum(astar_nodes_list) / len(astar_nodes_list)

        print(f"{size_str:<10} | {'* TRUNG BÌNH *':<14} | {'DFS':<10} | {avg_t_dfs:<16.2f} | {avg_m_dfs:<13.2f} | {avg_n_dfs:<14.1f} | {r*c:<14}")
        print(f"{size_str:<10} | {'* TRUNG BÌNH *':<14} | {'A*':<10} | {avg_t_ast:<16.2f} | {avg_m_ast:<13.2f} | {avg_n_ast:<14.1f} | {r*c:<14}")
        print("=" * 118)

        # Lưu lại để xuất JSON
        summary_data["sizes"].append(size_str)
        summary_data["steps"].append(r * c)
        summary_data["dfs_time"].append(round(avg_t_dfs, 2))
        summary_data["astar_time"].append(round(avg_t_ast, 2))
        summary_data["dfs_mem"].append(round(avg_m_dfs, 2))
        summary_data["astar_mem"].append(round(avg_m_ast, 2))
        summary_data["dfs_nodes"].append(round(avg_n_dfs, 1))
        summary_data["astar_nodes"].append(round(avg_n_ast, 1))

    # Ghi file JSON để plot_results.py tự đọc
    with open("benchmark_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=4)
    print("-> Đã lưu dữ liệu tổng hợp trung bình vào file: benchmark_summary.json")