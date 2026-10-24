# puzzle_generator.py
import random
from pipes_solver import NORTH, EAST, SOUTH, WEST, OPPOSITE, DELTAS, get_rotations_for_piece

def generate_random_pipes(rows, cols, seed=None):
    """
    Sinh ngẫu nhiên ma trận Pipes kích thước rows x cols.
    Bảo đảm:
    - 100% liên thông.
    - Không có ô chữ thập (bậc tối đa của mỗi ô là 3).
    - Chỉ gồm đúng 4 loại mảnh chuẩn: End, Straight, Corner, T-piece.
    """
    if seed is not None:
        random.seed(seed)

    while True:
        tree_grid = [[0] * cols for _ in range(rows)]
        degree = [[0] * cols for _ in range(rows)]
        visited = set([(0, 0)])
        walls = []

        def add_walls(r, c):
            for direction, (dr, dc) in DELTAS.items():
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    walls.append((r, c, direction, nr, nc))

        add_walls(0, 0)

        while walls:
            idx = random.randrange(len(walls))
            r1, c1, direction, r2, c2 = walls.pop(idx)

            if (r2, c2) not in visited:
                # Chỉ nối nếu cả 2 ô chưa đạt bậc tối đa là 3 (ngăn tạo ống chữ thập)
                if degree[r1][c1] < 3 and degree[r2][c2] < 3:
                    visited.add((r2, c2))
                    tree_grid[r1][c1] |= direction
                    tree_grid[r2][c2] |= OPPOSITE[direction]
                    degree[r1][c1] += 1
                    degree[r2][c2] += 1
                    add_walls(r2, c2)

        # Nếu cây phủ kín toàn bộ bảng thì đạt chuẩn
        if len(visited) == rows * cols:
            break

    # Xáo trộn góc xoay ngẫu nhiên
    scrambled_grid = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            base_mask = tree_grid[r][c]
            allowed_rotations = get_rotations_for_piece(base_mask)
            scrambled_grid[r][c] = random.choice(allowed_rotations)

    return scrambled_grid