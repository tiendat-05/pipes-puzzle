"""Demo trực quan từng bước bằng Pygame: SPACE chạy tự động, -> từng bước, R đặt lại."""

import pygame

TITLE = "Pipes Puzzle Solver - Step-by-Step Visualizer"

# Bảng màu giao diện tối.
BG_COLOR = (24, 26, 27)
GRID_LINE = (65, 72, 78)
EMPTY_CELL_BG = (35, 39, 42)
PIPE_COLOR_UNSOLVED = (130, 140, 150)
PIPE_COLOR_SOLVED = (46, 204, 113)
CURRENT_HIGHLIGHT = (241, 196, 15)
TEXT_COLOR = (236, 240, 241)
SOURCE_COLOR = (231, 76, 60)

# Cỡ ô co giãn theo cửa sổ để luôn thấy toàn bộ bàn cờ.
MIN_CELL = 12
MAX_CELL = 90
MIN_MARGIN = 6
MAX_MARGIN = 30
MAX_STATUS_HEIGHT = 56
WINDOW_MARGIN = 24
MIN_WINDOW_W = 320
MIN_WINDOW_H = 240


def fit_layout(screen_w, screen_h, rows, cols):
    """Tính cỡ ô, chiều cao thanh trạng thái và gốc vẽ cho vừa cửa sổ hiện tại."""
    margin = int(min(screen_w, screen_h) * 0.035)
    margin = max(MIN_MARGIN, min(MAX_MARGIN, margin))
    status_h = max(30, min(MAX_STATUS_HEIGHT, int(screen_h * 0.08)))

    avail_w = max(1, screen_w - 2 * margin)
    avail_h = max(1, screen_h - 2 * margin - status_h)

    cell = max(1, min(avail_w // cols, avail_h // rows))
    origin_x = margin + (avail_w - cell * cols) // 2
    origin_y = margin + (avail_h - cell * rows) // 2

    return cell, status_h, origin_x, origin_y


def initial_window_size(rows, cols):
    """Chọn kích thước cửa sổ ban đầu vừa với độ phân giải màn hình."""
    try:
        info = pygame.display.Info()
        desk_w, desk_h = info.current_w, info.current_h
    except pygame.error:
        desk_w, desk_h = 0, 0

    if not desk_w or desk_w <= 0:
        desk_w = 1280
    if not desk_h or desk_h <= 0:
        desk_h = 800

    usable_w = max(MIN_WINDOW_W, desk_w - 80)
    usable_h = max(MIN_WINDOW_H, desk_h - 140)

    cell_w = (usable_w - 2 * WINDOW_MARGIN) // cols
    cell_h = (usable_h - 2 * WINDOW_MARGIN - MAX_STATUS_HEIGHT) // rows
    cell = max(MIN_CELL, min(MAX_CELL, cell_w, cell_h))

    width = cols * cell + 2 * WINDOW_MARGIN
    height = rows * cell + 2 * WINDOW_MARGIN + MAX_STATUS_HEIGHT

    return max(MIN_WINDOW_W, width), max(MIN_WINDOW_H, height)


def draw_pipe_cell(surface, x, y, size, mask, is_solved=False, is_current=False):
    """Vẽ một ô: nền, viền, tâm và các nhánh ống theo bitmask."""
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, EMPTY_CELL_BG, rect)

    border_color = CURRENT_HIGHLIGHT if is_current else GRID_LINE
    border_width = max(1, min(3, size // 24)) if is_current else 1
    pygame.draw.rect(surface, border_color, rect, border_width)

    if mask == 0:
        return

    center = (x + size // 2, y + size // 2)
    thickness = max(2, int(size * 0.14))
    color = PIPE_COLOR_SOLVED if is_solved else PIPE_COLOR_UNSOLVED

    pygame.draw.circle(surface, color, center, thickness // 2 + 1)

    if mask & 1:
        pygame.draw.line(surface, color, center, (center[0], y), thickness)
    if mask & 2:
        pygame.draw.line(surface, color, center, (x + size, center[1]), thickness)
    if mask & 4:
        pygame.draw.line(surface, color, center, (center[0], y + size), thickness)
    if mask & 8:
        pygame.draw.line(surface, color, center, (x, center[1]), thickness)


def run_gui(initial_grid, steps, source_pos=(2, 2)):
    """Mở cửa sổ demo và lặp vẽ cho tới khi người dùng thoát.

    ``steps`` là danh sách (hàng, cột, mask) do thuật toán trả về.
    """
    try:
        pygame.display.init()
        pygame.font.init()
    except pygame.error as exc:
        raise RuntimeError(
            f"Không khởi tạo được cửa sổ đồ hoạ ({exc}). "
            f"Máy không có màn hình? Hãy dùng chế độ chỉ in text."
        ) from exc

    rows = len(initial_grid)
    cols = len(initial_grid[0])

    flags = pygame.RESIZABLE | pygame.DOUBLEBUF
    # Cửa sổ mở với cỡ vừa màn hình; kéo giãn thì fit_layout tự tính lại.
    screen = pygame.display.set_mode(initial_window_size(rows, cols), flags)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    font_name = pygame.font.match_font('dejavusans') or pygame.font.match_font('liberationsans')
    fonts = {}

    def get_font(size):
        if size not in fonts:
            if font_name:
                fonts[size] = pygame.font.Font(font_name, size)
            else:
                fonts[size] = pygame.font.SysFont("Arial", size)
        return fonts[size]

    current_board = [row[:] for row in initial_grid]
    solved_flags = [[False] * cols for _ in range(rows)]

    step_idx = 0
    auto_play = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(
                    (max(MIN_WINDOW_W, event.w), max(MIN_WINDOW_H, event.h)), flags)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_SPACE:
                    auto_play = not auto_play
                elif event.key == pygame.K_RIGHT and step_idx < len(steps):
                    r, c, val = steps[step_idx]
                    current_board[r][c] = val
                    solved_flags[r][c] = True
                    step_idx += 1
                elif event.key == pygame.K_r:
                    current_board = [row[:] for row in initial_grid]
                    solved_flags = [[False] * cols for _ in range(rows)]
                    step_idx = 0
                    auto_play = False

        if not running:
            break

        if auto_play and step_idx < len(steps):
            r, c, val = steps[step_idx]
            current_board[r][c] = val
            solved_flags[r][c] = True
            step_idx += 1
            pygame.time.delay(150)

        screen_w, screen_h = screen.get_size()
        cell, status_h, origin_x, origin_y = fit_layout(screen_w, screen_h, rows, cols)

        curr_cell = steps[step_idx - 1][:2] if 0 < step_idx <= len(steps) else (-1, -1)

        screen.fill(BG_COLOR)

        for r in range(rows):
            for c in range(cols):
                px = origin_x + c * cell
                py = origin_y + r * cell
                is_curr = (r == curr_cell[0] and c == curr_cell[1])
                draw_pipe_cell(screen, px, py, cell, current_board[r][c],
                               solved_flags[r][c], is_curr)

                if (r, c) == source_pos:
                    center = (px + cell // 2, py + cell // 2)
                    pygame.draw.circle(screen, SOURCE_COLOR, center,
                                       max(3, int(cell * 0.1)))

        if step_idx < len(steps):
            status = f"Buoc: {step_idx}/{len(steps)} | Space: Tu dong chay | Phim ->: Tung buoc"
        else:
            status = f"HOAN THANH! ({len(steps)} buoc) - Nhan 'R' de chay lai tu dau"

        font_size = int(max(10, min(30, cell * 0.22, screen_w / 60)))
        font = get_font(font_size)
        text_surf = font.render(status, True, TEXT_COLOR)
        text_y = screen_h - status_h + (status_h - text_surf.get_height()) // 2
        screen.blit(text_surf, (origin_x, text_y))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
