"""Sinh bàn cờ Pipes luôn có nghiệm: dựng cây khung ngẫu nhiên rồi xáo trộn góc xoay."""

import random

from pipes_solver import (
    NORTH, EAST, SOUTH, WEST, OPPOSITE, DELTAS, get_rotations_for_piece,
)

# Số lần sinh lại tối đa trước khi báo lỗi (tránh treo vô hạn).
MAX_ATTEMPTS = 500

# Bậc tối đa của một ô: 3 đầu nối (End = 1, Straight = 2, Corner = 2, T = 3).
MAX_DEGREE = 3


def _build_spanning_tree(rows, cols, rng):
    """Dựng cây khung phủ kín bàn cờ bằng Prim ngẫu nhiên, khống chế bậc <= 3."""
    tree_grid = [[0] * cols for _ in range(rows)]
    degree = [[0] * cols for _ in range(rows)]
    visited = {(0, 0)}
    walls = []

    def add_walls(r, c):
        for direction, (dr, dc) in DELTAS.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                walls.append((r, c, direction, nr, nc))

    add_walls(0, 0)

    while walls:
        idx = rng.randrange(len(walls))
        r1, c1, direction, r2, c2 = walls.pop(idx)

        if (r2, c2) not in visited:
            if degree[r1][c1] < MAX_DEGREE and degree[r2][c2] < MAX_DEGREE:
                visited.add((r2, c2))
                tree_grid[r1][c1] |= direction
                tree_grid[r2][c2] |= OPPOSITE[direction]
                degree[r1][c1] += 1
                degree[r2][c2] += 1
                add_walls(r2, c2)

    return tree_grid, len(visited) == rows * cols


def generate_random_pipes(rows, cols, seed=None):
    """Sinh bàn cờ rows x cols luôn có ít nhất một lời giải.

    seed cho trước thì kết quả tất định và không đụng tới RNG toàn cục.
    """
    if rows < 2 or cols < 2:
        raise ValueError("Kích thước bàn cờ tối thiểu là 2x2.")

    # RNG cục bộ để cùng seed cho cùng bàn cờ mà không làm đổi trạng thái RNG chung.
    rng = random.Random(seed)

    tree_grid = None
    for _ in range(MAX_ATTEMPTS):
        candidate, ok = _build_spanning_tree(rows, cols, rng)
        if ok:
            tree_grid = candidate
            break

    if tree_grid is None:
        raise RuntimeError(
            f"Không sinh được cây khung phủ kín bàn cờ {rows}x{cols} sau "
            f"{MAX_ATTEMPTS} lần thử. Hãy thử seed khác."
        )

    # Xáo trộn góc xoay: phép xoay bảo toàn số đầu nối nên bàn cờ vẫn có nghiệm.
    scrambled_grid = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            base_mask = tree_grid[r][c]
            allowed_rotations = get_rotations_for_piece(base_mask)
            scrambled_grid[r][c] = rng.choice(allowed_rotations)

    return scrambled_grid
