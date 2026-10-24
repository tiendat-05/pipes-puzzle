import pygame
import sys

CELL_SIZE = 90
MARGIN = 30

# Bảng màu giao diện phẳng hiện đại
BG_COLOR = (24, 26, 27)
GRID_LINE = (65, 72, 78)
EMPTY_CELL_BG = (35, 39, 42)
PIPE_COLOR_UNSOLVED = (130, 140, 150) # Ống lúc chưa xoay đúng (màu xám xanh)
PIPE_COLOR_SOLVED = (46, 204, 113)    # Ống khi đã giải đúng (màu xanh lá)
CURRENT_HIGHLIGHT = (241, 196, 15)   # Ô đang xét (viền vàng)
TEXT_COLOR = (236, 240, 241)

def draw_pipe_cell(surface, x, y, size, mask, is_solved=False, is_current=False):
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, EMPTY_CELL_BG, rect)
    
    # Viền ô
    border_color = CURRENT_HIGHLIGHT if is_current else GRID_LINE
    border_width = 3 if is_current else 1
    pygame.draw.rect(surface, border_color, rect, border_width)

    if mask == 0:
        return

    center = (x + size // 2, y + size // 2)
    thickness = 12
    color = PIPE_COLOR_SOLVED if is_solved else PIPE_COLOR_UNSOLVED

    # Khớp nối ở tâm
    pygame.draw.circle(surface, color, center, thickness // 2 + 1)

    # North=1, East=2, South=4, West=8
    if mask & 1:
        pygame.draw.line(surface, color, center, (center[0], y), thickness)
    if mask & 2:
        pygame.draw.line(surface, color, center, (x + size, center[1]), thickness)
    if mask & 4:
        pygame.draw.line(surface, color, center, (center[0], y + size), thickness)
    if mask & 8:
        pygame.draw.line(surface, color, center, (x, center[1]), thickness)

def run_gui(initial_grid, steps, source_pos=(2, 2)):
    # Chỉ khởi tạo module display và font (tránh lỗi âm thanh ALSA trên WSL)
    pygame.display.init()
    pygame.font.init()

    rows = len(initial_grid)
    cols = len(initial_grid[0])

    width = cols * CELL_SIZE + 2 * MARGIN
    height = rows * CELL_SIZE + 2 * MARGIN + 70
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pipes Puzzle Solver - Step-by-Step Visualizer")
    clock = pygame.time.Clock()

    # Chọn font an toàn cho Linux/WSL
    font_name = pygame.font.match_font('dejavusans') or pygame.font.match_font('liberationsans')
    if font_name:
        font = pygame.font.Font(font_name, 16)
    else:
        font = pygame.font.SysFont("Arial", 16)

    # Khởi tạo bàn cờ bằng cấu hình ban đầu
    current_board = [row[:] for row in initial_grid]
    solved_flags = [[False] * cols for _ in range(rows)]
    
    step_idx = 0
    auto_play = False

    running = True
    while running:
        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    auto_play = not auto_play
                elif event.key == pygame.K_RIGHT and step_idx < len(steps):
                    r, c, val = steps[step_idx]
                    current_board[r][c] = val
                    solved_flags[r][c] = True
                    step_idx += 1
                elif event.key == pygame.K_r:  # Reset về ban đầu
                    current_board = [row[:] for row in initial_grid]
                    solved_flags = [[False] * cols for _ in range(rows)]
                    step_idx = 0
                    auto_play = False

        # Tự động bước nếu bật Space
        if auto_play and step_idx < len(steps):
            r, c, val = steps[step_idx]
            current_board[r][c] = val
            solved_flags[r][c] = True
            step_idx += 1
            pygame.time.delay(150)

        # Tọa độ ô vừa được xoay
        curr_cell = steps[step_idx - 1][:2] if 0 < step_idx <= len(steps) else (-1, -1)

        # Vẽ các ô trên bàn cờ
        for r in range(rows):
            for c in range(cols):
                px = MARGIN + c * CELL_SIZE
                py = MARGIN + r * CELL_SIZE
                is_curr = (r == curr_cell[0] and c == curr_cell[1])
                draw_pipe_cell(screen, px, py, CELL_SIZE, current_board[r][c], solved_flags[r][c], is_curr)

                # Nguồn nước (chấm tròn đỏ ở tâm)
                if (r, c) == source_pos:
                    center = (px + CELL_SIZE // 2, py + CELL_SIZE // 2)
                    pygame.draw.circle(screen, (231, 76, 60), center, 9)

        # Thanh trạng thái phía dưới (Dùng tiếng Việt không dấu để đảm bảo tương thích 100% mọi môi trường)
        if step_idx < len(steps):
            status = f"Buoc: {step_idx}/{len(steps)} | Space: Tu dong chay | Phim ->: Tung buoc"
        else:
            status = f"HOAN THANH! ({len(steps)} buoc) - Nhan 'R' de chay lai tu dau"

        text_surf = font.render(status, True, TEXT_COLOR)
        screen.blit(text_surf, (MARGIN, height - 48))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()