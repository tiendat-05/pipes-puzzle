import time
import tracemalloc
import heapq

# ==========================================
# 1. ĐỊNH NGHĨA HƯỚNG VÀ BITMASK CHUẨN
# ==========================================
NORTH = 1
EAST  = 2
SOUTH = 4
WEST  = 8

OPPOSITE = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST: WEST,
    WEST: EAST
}

DELTAS = {
    NORTH: (-1, 0),
    SOUTH: (1, 0),
    EAST: (0, 1),
    WEST: (0, -1)
}

VALID_PIECE_ROTATIONS = {
    "END": [NORTH, EAST, SOUTH, WEST],
    
    "STRAIGHT": [NORTH | SOUTH, EAST | WEST],

    "CORNER": [
        NORTH | EAST,
        EAST | SOUTH,
        SOUTH | WEST,
        WEST | NORTH
    ],
    
    "T_PIECE": [
        NORTH | EAST | SOUTH,
        EAST | SOUTH | WEST,
        SOUTH | WEST | NORTH,
        WEST | NORTH | EAST
    ]
}

def identify_piece_type(mask):
    """Xác định loại mảnh ống dựa trên bitmask ban đầu (bắt buộc thuộc 4 loại chuẩn)"""
    bit_count = bin(mask).count('1')
    if bit_count == 1:
        return "END"
    elif bit_count == 2:
        if mask in (NORTH | SOUTH, EAST | WEST):
            return "STRAIGHT"
        else:
            return "CORNER"
    elif bit_count == 3:
        return "T_PIECE"
    else:
        raise ValueError(f"Mảnh có mask {mask} không hợp lệ! Trò chơi chỉ gồm 4 loại: End (1), Straight (2), Corner (2), T-piece (3). Không hỗ trợ Cross (4).")

def get_rotations_for_piece(initial_mask):
    """Lấy danh sách các góc xoay hợp lệ tương ứng với loại mảnh"""
    p_type = identify_piece_type(initial_mask)
    return VALID_PIECE_ROTATIONS[p_type]

# ==========================================
# 2. LỚP BÀI TOÁN PIPES (PUZZLE MODEL)
# ==========================================
class PipesPuzzle:
    def __init__(self, grid):
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.initial_grid = grid
        
        self.possible_rotations = [
            [get_rotations_for_piece(grid[r][c]) for c in range(self.cols)]
            for r in range(self.rows)
        ]

    def is_consistent(self, board, r, c, mask):
        """
        Kiểm tra tính tương thích 2 chiều nghiêm ngặt:
        1. Không đâm đầu nối ra 4 bức tường biên.
        2. Ăn khớp hoàn toàn với ô phía trên (r-1, c) và ô phía trái (r, c-1) đã đặt trước.
        """
        if r == 0 and (mask & NORTH): return False
        if r == self.rows - 1 and (mask & SOUTH): return False
        if c == 0 and (mask & WEST): return False
        if c == self.cols - 1 and (mask & EAST): return False

        if r > 0:
            top_mask = board[r - 1][c]
            top_has_south = bool(top_mask & SOUTH)
            curr_has_north = bool(mask & NORTH)
            if top_has_south != curr_has_north:
                return False

        if c > 0:
            left_mask = board[r][c - 1]
            left_has_east = bool(left_mask & EAST)
            curr_has_west = bool(mask & WEST)
            if left_has_east != curr_has_west:
                return False

        return True

    def is_connected(self, board):
        """Kiểm tra toàn bộ mạng lưới tạo thành 1 đồ thị liên thông duy nhất"""
        start = (0, 0)
        visited = set([start])
        queue = [start]

        while queue:
            cr, cc = queue.pop(0)
            c_mask = board[cr][cc]

            for direction, (dr, dc) in DELTAS.items():
                if c_mask & direction:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        n_mask = board[nr][nc]
                        if (n_mask & OPPOSITE[direction]) and (nr, nc) not in visited:
                            visited.add((nr, nc))
                            queue.append((nr, nc))

        return len(visited) == (self.rows * self.cols)

    def format_board(self, board):
        """Chuyển bàn cờ sang ký tự đồ họa đường ống"""
        symbols = {
            NORTH: "╵", EAST: "╶", SOUTH: "╷", WEST: "╴",
            NORTH | SOUTH: "│", EAST | WEST: "─",
            NORTH | EAST: "└", EAST | SOUTH: "┌",
            SOUTH | WEST: "┐", WEST | NORTH: "┘",
            NORTH | EAST | SOUTH: "├", EAST | SOUTH | WEST: "┬",
            SOUTH | WEST | NORTH: "┤", WEST | NORTH | EAST: "┴"
        }
        res = []
        for row in board:
            res.append(" ".join(symbols.get(val, " ") for val in row))
        return "\n".join(res)

# ==========================================
# 3. GIẢI THUẬT TÌM KIẾM MÙ: DFS (BLIND SEARCH)
# ==========================================
def solve_dfs(puzzle):
    explored_nodes = 0
    history_steps = []
    board = [[0] * puzzle.cols for _ in range(puzzle.rows)]

    def dfs(index):
        nonlocal explored_nodes
        explored_nodes += 1

        if index == puzzle.rows * puzzle.cols:
            return puzzle.is_connected(board)

        r = index // puzzle.cols
        c = index % puzzle.cols

        for rot in puzzle.possible_rotations[r][c]:
            if puzzle.is_consistent(board, r, c, rot):
                board[r][c] = rot
                history_steps.append((r, c, rot))
                
                if dfs(index + 1):
                    return True
                
                history_steps.pop()
                board[r][c] = 0

        return False

    success = dfs(0)
    return success, board, explored_nodes, history_steps

# ==========================================
# 4. GIẢI THUẬT HEURISTIC SEARCH: A*
# ==========================================
def compute_heuristic(puzzle, board, index):
    """
    Hàm Heuristic h(n): 
    - Cơ sở: Số ô chưa gán góc xoay còn lại.
    - Điểm phạt (Penalties): Cộng thêm phạt nặng nếu các ô đã đặt ở mép đáy 
      hoặc mép phải có đầu nối chĩa ra ngoài tường biên.
    """
    total_cells = puzzle.rows * puzzle.cols
    remaining_cells = total_cells - index
    penalties = 0

    for r in range(puzzle.rows):
        for c in range(puzzle.cols):
            if (r * puzzle.cols + c) < index:
                mask = board[r][c]
                if r == puzzle.rows - 1 and (mask & SOUTH):
                    penalties += 2
                if c == puzzle.cols - 1 and (mask & EAST):
                    penalties += 2

    return remaining_cells + penalties

def solve_astar(puzzle):
    explored_nodes = 0
    initial_board = tuple(0 for _ in range(puzzle.rows * puzzle.cols))
    initial_h = puzzle.rows * puzzle.cols
    
    pq = []
    counter = 0
    heapq.heappush(pq, (initial_h, 0, counter, 0, initial_board, []))

    while pq:
        f, g, _, idx, board_tuple, history = heapq.heappop(pq)
        explored_nodes += 1

        if idx == puzzle.rows * puzzle.cols:
            board_2d = [
                list(board_tuple[r * puzzle.cols:(r + 1) * puzzle.cols])
                for r in range(puzzle.rows)
            ]
            if puzzle.is_connected(board_2d):
                return True, board_2d, explored_nodes, history
            continue

        r = idx // puzzle.cols
        c = idx % puzzle.cols

        board_2d = [
            list(board_tuple[i * puzzle.cols:(i + 1) * puzzle.cols])
            for i in range(puzzle.rows)
        ]

        for rot in puzzle.possible_rotations[r][c]:
            if puzzle.is_consistent(board_2d, r, c, rot):
                new_board = list(board_tuple)
                new_board[idx] = rot
                new_history = history + [(r, c, rot)]
                
                new_g = g + 1
                new_board_2d = [
                    new_board[i * puzzle.cols:(i + 1) * puzzle.cols]
                    for i in range(puzzle.rows)
                ]
                new_h = compute_heuristic(puzzle, new_board_2d, idx + 1)
                new_f = new_g + new_h
                counter += 1
                heapq.heappush(pq, (new_f, new_g, counter, idx + 1, tuple(new_board), new_history))

    return False, None, explored_nodes, []

# ==========================================
# 5. HÀM BENCHMARK THỰC NGHIỆM ĐO ĐẠC
# ==========================================
def benchmark_algorithm(name, solver_fn, puzzle):
    tracemalloc.start()
    t_start = time.perf_counter()

    success, result_board, nodes, steps = solver_fn(puzzle)

    t_end = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    execution_time = (t_end - t_start) * 1000
    peak_mem_kb = peak_mem / 1024

    print(f"\n--- KẾT QUẢ ĐO ĐẠC: {name} ---")
    print(f"Trạng thái: {'THÀNH CÔNG' if success else 'THẤT BẠI'}")
    print(f"Thời gian thực thi: {execution_time:.3f} ms")
    print(f"Bộ nhớ tiêu tốn cao nhất (Peak Memory): {peak_mem_kb:.2f} KB")
    print(f"Số node mở rộng (Nodes expanded): {nodes}")
    print(f"Độ dài lời giải (Solution length): {len(steps)}")
    
    return {
        "algorithm": name,
        "time_ms": execution_time,
        "memory_kb": peak_mem_kb,
        "nodes": nodes,
        "board": result_board,
        "steps": steps
    }