"""Tự kiểm tra: lời giải hợp lệ, hồi quy số node, giới hạn đệ quy, RNG cục bộ."""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random

from pipes_solver import (
    enable_utf8_stdout, PipesPuzzle, solve_dfs, solve_astar, validate_solution,
)
from puzzle_generator import generate_random_pipes

enable_utf8_stdout()

SIZES = [(5, [101, 102, 103, 104, 105]),
         (8, [201, 202, 203, 204, 205]),
         (12, [301, 302, 303, 304, 305])]

# Số node chuẩn dùng để kiểm tra hồi quy.
BASELINE_DFS_NODES = {
    (5, 101): 40, (5, 102): 122, (5, 103): 27, (5, 104): 26, (5, 105): 26,
    (8, 201): 179, (8, 202): 147, (8, 203): 93, (8, 204): 82, (8, 205): 98,
    (12, 301): 439, (12, 302): 342, (12, 303): 890, (12, 304): 239, (12, 305): 1023,
}
BASELINE_ASTAR_NODES = {
    (5, 101): 40, (5, 102): 123, (5, 103): 35, (5, 104): 26, (5, 105): 26,
    (8, 201): 203, (8, 202): 152, (8, 203): 102, (8, 204): 175, (8, 205): 118,
    (12, 301): 1296, (12, 302): 614, (12, 303): 1432, (12, 304): 497, (12, 305): 2378,
}

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print(f"   [FAIL] {msg}")


print("=" * 78)
print("1. TÍNH ĐÚNG ĐẮN CỦA LỜI GIẢI (DFS và A* mặc định)")
print("=" * 78)
for size, seeds in SIZES:
    for seed in seeds:
        grid = generate_random_pipes(size, size, seed=seed)
        puzzle = PipesPuzzle(grid)

        ok_d, board_d, n_d, st_d = solve_dfs(puzzle)
        check(ok_d, f"DFS không có lời giải {size}x{size} seed={seed}")
        vd, md = validate_solution(puzzle, board_d)
        check(vd, f"DFS lời giải KHÔNG hợp lệ {size}x{size} seed={seed}: {md}")
        check(len(st_d) == size * size, f"DFS sai độ dài {size}x{size} seed={seed}")

        ok_a, board_a, n_a, st_a = solve_astar(puzzle)
        check(ok_a, f"A* không có lời giải {size}x{size} seed={seed}")
        va, ma = validate_solution(puzzle, board_a)
        check(va, f"A* lời giải KHÔNG hợp lệ {size}x{size} seed={seed}: {ma}")
        check(len(st_a) == size * size, f"A* sai độ dài {size}x{size} seed={seed}")

        print(f"  {size:2d}x{size:<2d} seed={seed}  DFS nodes={n_d:<5d} | "
              f"A* nodes={n_a:<5d}")

print()
print("=" * 78)
print("2. HỒI QUY: số node phải khớp với số liệu chuẩn")
print("=" * 78)
for size, seeds in SIZES:
    for seed in seeds:
        grid = generate_random_pipes(size, size, seed=seed)
        puzzle = PipesPuzzle(grid)

        _, _, n_dfs, _ = solve_dfs(puzzle)
        check(n_dfs == BASELINE_DFS_NODES[(size, seed)],
              f"DFS {size}x{size} seed={seed}: {n_dfs} != "
              f"{BASELINE_DFS_NODES[(size, seed)]}")

        _, _, n_old, _ = solve_astar(puzzle, tie_mode="none")
        check(n_old == BASELINE_ASTAR_NODES[(size, seed)],
              f"A* (none) {size}x{size} seed={seed}: {n_old} != "
              f"{BASELINE_ASTAR_NODES[(size, seed)]}")

print(f"  Đã đối chiếu {len(BASELINE_DFS_NODES) * 2} giá trị (15 DFS + 15 A*).")

print()
print("=" * 78)
print("3. DFS KHÔNG CÒN RecursionError TRÊN BÀN CỜ LỚN")
print("=" * 78)

_observed = {"limit": None}
_original_is_consistent = PipesPuzzle.is_consistent


def _recording_is_consistent(self, board, r, c, mask):
    if _observed["limit"] is None:
        _observed["limit"] = sys.getrecursionlimit()
    return _original_is_consistent(self, board, r, c, mask)


PipesPuzzle.is_consistent = _recording_is_consistent
try:
    for size in (20, 22):
        grid = generate_random_pipes(size, size, seed=7)
        puzzle = PipesPuzzle(grid)
        _observed["limit"] = None
        t0 = time.perf_counter()
        ok, board, nodes, steps = solve_dfs(puzzle)
        dt = (time.perf_counter() - t0) * 1000
        valid, msg = validate_solution(puzzle, board)
        check(ok and valid, f"DFS {size}x{size} sai: {msg}")
        check(_observed["limit"] is not None and _observed["limit"] > 1000,
              f"DFS {size}x{size} không nâng giới hạn đệ quy "
              f"(quan sát: {_observed['limit']})")
        print(f"  DFS {size:2d}x{size:<2d} ({size * size:>4d} ô): ok={ok} "
              f"nodes={nodes:<7d} {dt:>8.1f} ms  "
              f"giới_hạn_đệ_quy_lúc_chạy={_observed['limit']}  hợp_lệ={valid}")
finally:
    PipesPuzzle.is_consistent = _original_is_consistent

check(sys.getrecursionlimit() < 5000,
      f"Giới hạn đệ quy KHÔNG được phục hồi: {sys.getrecursionlimit()}")
print(f"  Giới hạn đệ quy sau khi chạy xong: {sys.getrecursionlimit()} "
      f"(đã phục hồi)")

old = sys.getrecursionlimit()
try:
    sys.setrecursionlimit(3000)

    def deep(n):
        return 0 if n == 0 else 1 + deep(n - 1)

    reached = deep(2500)
    check(reached == 2500, "Đệ quy sâu 2500 không chạy được")
    print(f"  Đệ quy sâu 2500 khung hình: chạy được (kết quả {reached})")
finally:
    sys.setrecursionlimit(old)

print()
print("  Ghi chú: bàn cờ từ ~26x26 trở lên không còn là vấn đề ĐỆ QUY mà là vấn")
print("  đề ĐỘ PHỨC TẠP MŨ của bài toán -- cả DFS lẫn A* đều có thể chạy rất lâu.")

print()
print("=" * 78)
print("4. BỘ SINH BÀN CỜ KHÔNG ĐỤNG RNG TOÀN CỤC")
print("=" * 78)
random.seed(12345)
expected_next = random.Random(12345).random()
generate_random_pipes(8, 8, seed=999)
actual_next = random.random()
check(abs(actual_next - expected_next) < 1e-12,
      "generate_random_pipes() đã làm thay đổi trạng thái RNG toàn cục!")
print(f"  RNG toàn cục sau khi sinh bàn cờ: "
      f"{'GIỮ NGUYÊN' if abs(actual_next - expected_next) < 1e-12 else 'BỊ THAY ĐỔI'}")

print()
print("=" * 78)
if failures:
    print(f"KẾT QUẢ: {len(failures)} LỖI")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("KẾT QUẢ: TẤT CẢ KIỂM TRA ĐỀU ĐẠT")
