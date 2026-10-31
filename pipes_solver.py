"""Mô hình hoá và giải bài toán Pipes bằng DFS (tìm kiếm mù) và A* (tìm kiếm có thông tin)."""

import sys
import time
import tracemalloc
import heapq


def enable_utf8_stdout():
    """Ép stdout/stderr sang UTF-8 (console Windows mặc định dùng cp1252)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream is not None and hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


# Mỗi hướng nối là một bit; mask của một ô là tổng các bit tương ứng.
NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

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
    """Xác định loại mảnh (End / Straight / Corner / T) theo số đầu nối."""
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
        raise ValueError(
            f"Mảnh có mask {mask} không hợp lệ! Trò chơi chỉ gồm 4 loại: "
            f"End (1), Straight (2), Corner (2), T-piece (3). Không hỗ trợ Cross (4)."
        )


def get_rotations_for_piece(initial_mask):
    """Danh sách các hướng xoay hợp lệ của mảnh có mask ban đầu."""
    p_type = identify_piece_type(initial_mask)
    return VALID_PIECE_ROTATIONS[p_type]


_CELL_BYTES = {value: bytes((value,)) for value in range(16)}


class PipesPuzzle:
    """Trạng thái bài toán: kích thước lưới, mảnh ban đầu và miền giá trị từng ô."""

    def __init__(self, grid):
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.initial_grid = grid

        self.possible_rotations = [
            [get_rotations_for_piece(grid[r][c]) for c in range(self.cols)]
            for r in range(self.rows)
        ]

        # Bảng tra dùng cho A*: hướng xoay hợp lệ sau khi lọc ràng buộc biên,
        # và số lựa chọn của ô kế tiếp theo (bit trên, bit trái).
        self.candidates = []
        self.mrv_table = []

        for r in range(self.rows):
            for c in range(self.cols):
                allowed = []
                for rot in self.possible_rotations[r][c]:
                    if r == 0 and (rot & NORTH):
                        continue
                    if r == self.rows - 1 and (rot & SOUTH):
                        continue
                    if c == 0 and (rot & WEST):
                        continue
                    if c == self.cols - 1 and (rot & EAST):
                        continue
                    allowed.append(rot)
                allowed = tuple(allowed)
                self.candidates.append(allowed)

                counts = []
                for above in (False, True):
                    for left in (False, True):
                        n = 0
                        for rot in allowed:
                            if r > 0 and bool(rot & NORTH) != above:
                                continue
                            if c > 0 and bool(rot & WEST) != left:
                                continue
                            n += 1
                        counts.append(5 if n == 0 else n)
                self.mrv_table.append(tuple(counts))

    def is_consistent(self, board, r, c, mask):
        """Ô (r, c) có ăn khớp với biên và hai ô đã gán phía trên / bên trái."""
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
        """Mạng ống có liên thông không (duyệt từ ô (0, 0))."""
        flat = [mask for row in board for mask in row]
        return self.is_connected_flat(flat)

    def is_connected_flat(self, flat):
        """Như is_connected nhưng chạy trên mảng phẳng, dùng ở nút lá của A*."""
        rows, cols = self.rows, self.cols
        total = rows * cols
        seen = bytearray(total)
        seen[0] = 1
        stack = [0]
        count = 1

        while stack:
            cur = stack.pop()
            mask = flat[cur]
            r, c = divmod(cur, cols)

            if mask & NORTH and r > 0:
                nxt = cur - cols
                if not seen[nxt] and flat[nxt] & SOUTH:
                    seen[nxt] = 1
                    count += 1
                    stack.append(nxt)
            if mask & SOUTH and r < rows - 1:
                nxt = cur + cols
                if not seen[nxt] and flat[nxt] & NORTH:
                    seen[nxt] = 1
                    count += 1
                    stack.append(nxt)
            if mask & WEST and c > 0:
                nxt = cur - 1
                if not seen[nxt] and flat[nxt] & EAST:
                    seen[nxt] = 1
                    count += 1
                    stack.append(nxt)
            if mask & EAST and c < cols - 1:
                nxt = cur + 1
                if not seen[nxt] and flat[nxt] & WEST:
                    seen[nxt] = 1
                    count += 1
                    stack.append(nxt)

        return count == total

    def count_components_and_edges(self, flat, count):
        """Đếm số thành phần liên thông và số cạnh đã ghép trong count ô đầu."""
        rows, cols = self.rows, self.cols
        visited = bytearray(count)
        comps = 0
        edges = 0

        for start in range(count):
            if visited[start]:
                continue
            comps += 1
            visited[start] = 1
            stack = [start]

            while stack:
                cur = stack.pop()
                m = flat[cur]
                if m == 0:
                    continue
                r, c = divmod(cur, cols)

                for d, (dr, dc) in DELTAS.items():
                    if not (m & d):
                        continue
                    nr, nc = r + dr, c + dc
                    if nr < 0 or nr >= rows or nc < 0 or nc >= cols:
                        continue
                    nxt = nr * cols + nc
                    if nxt >= count:
                        continue
                    if not (flat[nxt] & OPPOSITE[d]):
                        continue
                    if d in (NORTH, WEST):
                        edges += 1
                    if not visited[nxt]:
                        visited[nxt] = 1
                        stack.append(nxt)

        return comps, edges

    def format_board(self, board):
        """In bàn cờ bằng ký tự đường ống."""
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


def solve_dfs(puzzle):
    """DFS quay lui, gán hướng xoay theo thứ tự hàng.

    Trả về (thành công, bàn cờ, số nút đã duyệt, danh sách bước).
    """
    explored_nodes = 0
    history_steps = []
    board = [[0] * puzzle.cols for _ in range(puzzle.rows)]
    total_cells = puzzle.rows * puzzle.cols

    # Đệ quy sâu đúng bằng số ô nên phải nới giới hạn, rồi phục hồi sau khi xong.
    old_limit = sys.getrecursionlimit()
    needed_limit = total_cells + 1000
    limit_changed = needed_limit > old_limit
    if limit_changed:
        sys.setrecursionlimit(needed_limit)

    def dfs(index):
        nonlocal explored_nodes
        explored_nodes += 1

        if index == total_cells:
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

    try:
        success = dfs(0)
    finally:
        if limit_changed:
            sys.setrecursionlimit(old_limit)

    return success, board, explored_nodes, history_steps


# Các cách phá thế đồng hạng khi nhiều nút có cùng f. Với h(n) = N*M - k thì
# f(n) = N*M ở mọi nút, nên tie-breaking là thứ quyết định A* có định hướng được.
TIE_MODES = ("none", "components", "edges", "nextmrv", "mixed")


def solve_astar(puzzle, tie_mode="nextmrv", prefer_deeper=True, tie_break=None):
    """A* có tie-breaking; mặc định phá hòa theo MRV của ô kế tiếp.

    tie_mode chọn cách phá hòa, prefer_deeper ưu tiên nút sâu khi mọi khóa bằng
    nhau, tie_break=False tương đương tie_mode="none".
    """
    if tie_break is False:
        tie_mode = "none"
    if tie_mode not in TIE_MODES:
        raise ValueError(f"tie_mode phải thuộc {TIE_MODES}, nhận được {tie_mode!r}")

    rows, cols = puzzle.rows, puzzle.cols
    total_cells = rows * cols
    candidates = puzzle.candidates
    mrv_table = puzzle.mrv_table
    keep_prefix = tie_mode == "components"

    explored_nodes = 0
    # store[node] = (cha, bước gán) để dựng lại đường đi bằng con trỏ cha.
    store = []
    counter = 0

    # Trạng thái chỉ giữ cửa sổ cols ô gần nhất: kiểm tra ràng buộc chỉ cần ô
    # phía trên (index - cols) và ô bên trái (index - 1).
    heap = [(total_cells, 0, 0, 0, 0, 0, b"", -1, -1, 0)]
    push = heapq.heappush
    pop = heapq.heappop
    connected = puzzle.is_connected_flat
    track_edges = tie_mode == "edges" or tie_mode == "mixed"

    while heap:
        (_f, _t1, _t2, _t3, _cnt, index, window, parent_id, code,
         edges) = pop(heap)
        explored_nodes += 1

        node_id = len(store)
        if keep_prefix:
            prefix = (store[parent_id][2] + (code & 15,)) if parent_id >= 0 else ()
            store.append((parent_id, code, prefix))
        else:
            store.append((parent_id, code))

        if index == total_cells:
            # Nút lá: dựng lại bàn cờ từ chuỗi cha rồi kiểm tra liên thông.
            flat = [0] * total_cells
            chain = []
            cur = node_id
            while store[cur][1] >= 0:
                node_code = store[cur][1]
                cell = node_code >> 4
                rot = node_code & 15
                flat[cell] = rot
                chain.append((cell // cols, cell % cols, rot))
                cur = store[cur][0]
            chain.reverse()

            if connected(flat):
                board_2d = [flat[r * cols:(r + 1) * cols] for r in range(rows)]
                return True, board_2d, explored_nodes, chain
            continue

        r, c = divmod(index, cols)
        new_index = index + 1
        g = new_index
        h = total_cells - new_index
        new_f = g + h

        up_has_south = bool(window[0] & SOUTH) if r > 0 else False
        left_has_east = bool(window[-1] & EAST) if c > 0 else False

        next_c = c + 1
        next_r = r
        if next_c == cols:
            next_c = 0
            next_r += 1

        has_next = new_index < total_cells
        next_lut = mrv_table[new_index] if has_next else None

        depth_key = -new_index if prefer_deeper else new_index

        # Thử các hướng xoay còn hợp lệ với biên và hai ô lân cận đã gán.
        for rot in candidates[index]:
            if r > 0 and bool(rot & NORTH) != up_has_south:
                continue
            if c > 0 and bool(rot & WEST) != left_has_east:
                continue

            child = (window + _CELL_BYTES[rot])[-cols:]

            if track_edges:
                new_edges = edges
                if r > 0 and (rot & NORTH):
                    new_edges += 1
                if c > 0 and (rot & WEST):
                    new_edges += 1
            else:
                new_edges = 0

            if tie_mode == "nextmrv" or tie_mode == "mixed":
                if has_next:
                    above = bool(child[0] & SOUTH) if next_r > 0 else False
                    left = bool(rot & EAST) if next_c > 0 else False
                    tie1 = next_lut[(above << 1) | left]
                else:
                    tie1 = 0
                if tie_mode == "nextmrv":
                    tie2, tie3 = depth_key, 0
                else:
                    tie2, tie3 = -new_edges, depth_key
            elif tie_mode == "none":
                tie1, tie2, tie3 = index, 0, 0
            elif tie_mode == "components":
                comps, _e = puzzle.count_components_and_edges(prefix + (rot,),
                                                              new_index)
                tie1, tie2, tie3 = comps, depth_key, 0
            else:
                tie1, tie2, tie3 = -new_edges, depth_key, 0

            counter += 1
            push(heap, (new_f, tie1, tie2, tie3, counter, new_index, child,
                        node_id, (index << 4) | rot, new_edges))

    return False, None, explored_nodes, []


def validate_solution(puzzle, board):
    """Kiểm tra một bàn cờ đã gán đủ có phải lời giải hợp lệ."""
    if board is None:
        return False, "bàn cờ rỗng"

    if len(board) != puzzle.rows:
        return False, f"sai số hàng: {len(board)} != {puzzle.rows}"

    for r in range(puzzle.rows):
        if len(board[r]) != puzzle.cols:
            return False, f"sai số cột ở hàng {r}"

        for c in range(puzzle.cols):
            mask = board[r][c]
            if mask == 0:
                return False, f"ô ({r},{c}) chưa được gán"

            initial = puzzle.initial_grid[r][c]
            if identify_piece_type(mask) != identify_piece_type(initial):
                return False, f"ô ({r},{c}) bị đổi loại mảnh"

            if not puzzle.is_consistent(board, r, c, mask):
                return False, f"ô ({r},{c}) không nhất quán với láng giềng/biên"

    if not puzzle.is_connected(board):
        return False, "mạng ống không liên thông toàn bàn cờ"

    return True, "hợp lệ"


def benchmark_algorithm(name, solver_fn, puzzle, measure_memory=True):
    """Chạy một giải thuật, đo thời gian (và bộ nhớ nếu measure_memory)."""
    enable_utf8_stdout()

    if measure_memory:
        # tracemalloc làm chương trình chậm khoảng 14 lần, chỉ bật khi cần số liệu.
        tracemalloc.start()

    t_start = time.perf_counter()

    success, result_board, nodes, steps = solver_fn(puzzle)

    t_end = time.perf_counter()

    if measure_memory:
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_mem_kb = peak_mem / 1024
    else:
        peak_mem_kb = None

    execution_time = (t_end - t_start) * 1000

    ok, msg = validate_solution(puzzle, result_board) if success else (False, "không có lời giải")

    print(f"\n--- KẾT QUẢ ĐO ĐẠC: {name} ---")
    print(f"Trạng thái: {'THÀNH CÔNG' if success else 'THẤT BẠI'}")
    print(f"Kiểm chứng lời giải: {msg}")
    print(f"Thời gian thực thi: {execution_time:.3f} ms")
    if peak_mem_kb is None:
        print("Bộ nhớ tiêu tốn cao nhất: (bỏ qua - tracemalloc làm chậm ~14 lần)")
    else:
        print(f"Bộ nhớ tiêu tốn cao nhất (Peak Memory): {peak_mem_kb:.2f} KB")
    print(f"Số node mở rộng (Nodes expanded): {nodes}")
    print(f"Độ dài lời giải (Solution length): {len(steps)}")

    return {
        "algorithm": name,
        "time_ms": execution_time,
        "memory_kb": peak_mem_kb,
        "nodes": nodes,
        "board": result_board,
        "steps": steps,
        "valid": ok,
    }
