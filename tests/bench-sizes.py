"""So sánh DFS và A* (tie-break nextmrv) theo kích thước bàn cờ."""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipes_solver import (
    enable_utf8_stdout, PipesPuzzle, solve_dfs, solve_astar, validate_solution,
)
from puzzle_generator import generate_random_pipes

enable_utf8_stdout()

SIZES = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32]
SEEDS = [1, 2, 3]

header = f"{'size':>5}{'cells':>7}{'DFS nodes':>11}{'A* nodes':>10}{'node ratio':>12}{'DFS ms':>9}{'A* ms':>9}{'time ratio':>12}"
print(header)
print("-" * len(header))

for size in SIZES:
    dn = an = 0
    dt_ = at_ = 0.0
    ok_all = True
    for seed in SEEDS:
        grid = generate_random_pipes(size, size, seed=seed)
        puzzle = PipesPuzzle(grid)

        t = time.perf_counter()
        ok_d, board_d, n_d, _ = solve_dfs(puzzle)
        dt = (time.perf_counter() - t) * 1000

        t = time.perf_counter()
        ok_a, board_a, n_a, _ = solve_astar(puzzle, tie_mode="nextmrv")
        at = (time.perf_counter() - t) * 1000

        if not (ok_d and ok_a):
            ok_all = False
        v_d, _ = validate_solution(puzzle, board_d)
        v_a, _ = validate_solution(puzzle, board_a)
        if not (v_d and v_a):
            ok_all = False

        dn += n_d
        an += n_a
        dt_ += dt
        at_ += at

    flag = "" if ok_all else "  <-- NGHIỜ"
    print(f"{size:>5}{size*size:>7}{dn:>11}{an:>10}{dn/an:>12.2f}"
          f"{dt_:>9.2f}{at_:>9.2f}{dt_/at_:>12.2f}{flag}")

print()
print("node ratio = DFS nodes / A* nodes   (>1 nghĩa là A* mở rộng ít nút hơn)")
print("time ratio = DFS time  / A* time    (>1 nghĩa là A* chạy nhanh hơn)")
