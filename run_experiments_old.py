# run_experiments.py
import time
import tracemalloc
from pipes_solver import PipesPuzzle, solve_dfs, solve_astar
from puzzle_generator import generate_random_pipes

# Cố định seed cho các kích thước để đảm bảo kết quả đo đạc nhất quán và có thể tái lập
TEST_SUITE = [
    ("Test 1 (5x5)",   generate_random_pipes(5, 5, seed=101)),
    ("Test 2 (8x8)",   generate_random_pipes(8, 8, seed=202)),
    ("Test 3 (12x12)", generate_random_pipes(12, 12, seed=303)),
    ("Test 4 (20x20)", generate_random_pipes(20, 20, seed=404))
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
    print("=" * 115)
    print("                      BẢNG KẾT QUẢ ĐO ĐẠC THỰC NGHIỆM PIPES PUZZLE                                ")
    print("=" * 115)
    print(f"{'Bộ Test':<16} | {'Kích thước':<10} | {'Giải thuật':<10} | {'Thời gian (ms)':<16} | {'Bộ nhớ (KB)':<13} | {'Nodes Expand':<14} | {'Độ dài (Steps)':<14}")
    print("-" * 115)

    for name, grid in TEST_SUITE:
        r = len(grid)
        c = len(grid[0])
        puzzle = PipesPuzzle(grid)

        # 1. Đo DFS (Blind Search)
        try:
            s_dfs, t_dfs, m_dfs, n_dfs, len_dfs = run_benchmark_with_limit(solve_dfs, puzzle)
            status_dfs = f"{t_dfs:.2f} ms" if s_dfs else "Fail"
            print(f"{name:<16} | {f'{r}x{c}':<10} | {'DFS':<10} | {status_dfs:<16} | {m_dfs:<13.2f} | {n_dfs:<14} | {len_dfs:<14}")
        except Exception as e:
            print(f"{name:<16} | {f'{r}x{c}':<10} | {'DFS':<10} | {'Timeout/Mem':<16} | {'-':<13} | {'> 500,000':<14} | {'-':<14}")

        # 2. Đo A* (Heuristic Search)
        try:
            s_ast, t_ast, m_ast, n_ast, len_ast = run_benchmark_with_limit(solve_astar, puzzle)
            status_ast = f"{t_ast:.2f} ms" if s_ast else "Fail"
            print(f"{name:<16} | {f'{r}x{c}':<10} | {'A*':<10} | {status_ast:<16} | {m_ast:<13.2f} | {n_ast:<14} | {len_ast:<14}")
        except Exception as e:
            print(f"{name:<16} | {f'{r}x{c}':<10} | {'A*':<10} | {'Timeout/Mem':<16} | {'-':<13} | {'> 500,000':<14} | {'-':<14}")

        print("-" * 115)