"""So sánh 5 cách phá thế đồng hạng của A* trên 15 bàn cờ (5/8/12)."""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipes_solver import (
    enable_utf8_stdout, PipesPuzzle, solve_dfs, solve_astar, validate_solution,
)
from puzzle_generator import generate_random_pipes

enable_utf8_stdout()

SIZES = [(5, [101, 102, 103, 104, 105]),
         (8, [201, 202, 203, 204, 205]),
         (12, [301, 302, 303, 304, 305])]

MODES = ["none", "components", "edges", "nextmrv", "mixed"]

header = f"{'size':>5}{'seed':>6}{'DFS':>9}{'DFS ms':>8}"
for m in MODES:
    header += f"{m:>18}"
print(header)
print("-" * len(header))

tot = {m: [0, 0.0] for m in MODES}
tot_dfs = [0, 0.0]

for size, seeds in SIZES:
    for seed in seeds:
        grid = generate_random_pipes(size, size, seed=seed)
        puzzle = PipesPuzzle(grid)

        t = time.perf_counter()
        _, _, n_dfs, _ = solve_dfs(puzzle)
        dt_dfs = (time.perf_counter() - t) * 1000
        tot_dfs[0] += n_dfs
        tot_dfs[1] += dt_dfs

        row = f"{size:>5}{seed:>6}{n_dfs:>9}{dt_dfs:>8.2f}"
        for mode in MODES:
            t = time.perf_counter()
            ok, board, n, steps = solve_astar(puzzle, tie_mode=mode)
            dt = (time.perf_counter() - t) * 1000
            valid, _msg = validate_solution(puzzle, board)
            assert ok and valid, (mode, size, seed)
            tot[mode][0] += n
            tot[mode][1] += dt
            row += f"{n:>11}/{dt:>6.1f}"
        print(row)

print("-" * len(header))
row = f"{'TOTAL':>11}{tot_dfs[0]:>9}{tot_dfs[1]:>8.2f}"
for mode in MODES:
    row += f"{tot[mode][0]:>11}/{tot[mode][1]:>6.1f}"
print(row)

print()
print("Ghi chú: cột hiển thị dạng  <số node>/<thời gian ms>")
print("  none       : không phá hòa, khóa phụ là g (A* duyệt theo chiều rộng)")
print("  components : tie-break theo số thành phần liên thông (O(N)/nút)")
print("  edges      : tie-break theo số cạnh đã ghép     (O(1)/nút)")
print("  nextmrv    : tie-break theo MRV của ô kế tiếp   (O(1)/nút)")
print("  mixed      : MRV, rồi số cạnh, rồi độ sâu       (O(1)/nút)")
