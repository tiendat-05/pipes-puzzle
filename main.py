"""Chương trình chính: sinh bàn cờ Pipes, giải bằng DFS hoặc A*, rồi mở demo Pygame.

Chạy: python main.py
"""

import os
import sys

try:
    from pipes_solver import (
        PipesPuzzle, solve_dfs, solve_astar, benchmark_algorithm,
        validate_solution, enable_utf8_stdout,
    )
    from puzzle_generator import generate_random_pipes
except ImportError as exc:
    print(f"Không import được module trong cùng thư mục: {exc}")
    print(f"Thư mục làm việc hiện tại: {os.getcwd()}")
    print("Hãy mở terminal tại thư mục chứa main.py rồi chạy lại:")
    print("    cd đường_dẫn_tới/btl1_pipes_main")
    print("    python main.py")
    sys.exit(1)

# Giới hạn kích thước để tránh treo máy: độ phức tạp của bài toán là hàm mũ.
MIN_SIZE = 2
MAX_SIZE = 30
# Từ mức này trở lên nên cảnh báo vì có thể chạy rất lâu.
WARN_SIZE = 16

# Ba cấu hình giải thuật cho người dùng chọn.
ALGORITHMS = {
    "1": ("Blind Search (DFS)", lambda p: solve_dfs(p)),
    "2": ("Heuristic Search (A* + tie-break)", lambda p: solve_astar(p)),
    "3": ("A* không tie-break (để so sánh)",
          lambda p: solve_astar(p, tie_mode="none")),
}


def choose_algorithm():
    print("\nChọn giải thuật để giải:")
    print("  [1] Blind Search (DFS)")
    print("  [2] Heuristic Search (A* + tie-break)   <- mặc định")
    print("  [3] A* không tie-break (để so sánh)")
    while True:
        choice = input("Lựa chọn giải thuật (1, 2 hoặc 3): ").strip()
        if choice in ALGORITHMS:
            name, fn = ALGORITHMS[choice]
            return name, fn
        print("Lựa chọn không hợp lệ. Vui lòng nhập 1, 2 hoặc 3.")


def ask_size():
    """Hỏi kích thước bàn cờ và kiểm tra nằm trong giới hạn an toàn."""
    while True:
        try:
            r_str = input("Nhập số hàng (ví dụ 4, 5, 8, 12): ").strip()
            c_str = input("Nhập số cột (ví dụ 4, 5, 8, 12): ").strip()
            r, c = int(r_str), int(c_str)
        except ValueError:
            print("Lỗi: Vui lòng nhập số nguyên hợp lệ!")
            continue

        if r < MIN_SIZE or c < MIN_SIZE:
            print(f"Kích thước bàn cờ tối thiểu là {MIN_SIZE}x{MIN_SIZE}!")
            continue

        if r > MAX_SIZE or c > MAX_SIZE:
            print(f"Kích thước tối đa là {MAX_SIZE}x{MAX_SIZE} "
                  f"(lớn hơn sẽ chạy rất lâu hoặc hết bộ nhớ)!")
            continue

        if r * c >= WARN_SIZE * WARN_SIZE:
            print(f"CẢNH BÁO: bàn cờ {r}x{c} có {r * c} ô, có thể mất nhiều "
                  f"thời gian. Nhấn Enter để tiếp tục, Ctrl+C để huỷ.")
            input()

        return r, c


def main():
    enable_utf8_stdout()

    while True:
        print("\n" + "=" * 60)
        print("   CHƯƠNG TRÌNH SINH VÀ GIẢI BÀI TOÁN PIPES (AI LAB)")
        print("=" * 60)
        print("1. Sinh ngẫu nhiên bàn cờ (Kích thước tùy chọn NxM)")
        print("0. Thoát chương trình")
        print("-" * 60)

        choice = input("Nhập lựa chọn của bạn (0-1): ").strip()

        if choice == "0":
            print("Đã thoát chương trình.")
            sys.exit(0)
        elif choice != "1":
            print("Lựa chọn không hợp lệ. Vui lòng chọn 1 hoặc 0!")
            continue

        r, c = ask_size()

        print(f"\nĐang sinh ngẫu nhiên bàn cờ {r}x{c} liên thông hợp lệ "
              f"(100% có nghiệm)...")
        try:
            grid = generate_random_pipes(r, c)
        except (ValueError, RuntimeError) as exc:
            print(f"Lỗi khi sinh bàn cờ: {exc}")
            continue

        puzzle = PipesPuzzle(grid)
        source_pos = (r // 2, c // 2)

        print("\nBÀN CỜ BAN ĐẦU (ĐÃ XÁO TRỘN GÓC XOAY):")
        print(puzzle.format_board(grid))

        algo_name, algo_func = choose_algorithm()

        # Bàn lớn thì bỏ đo bộ nhớ: tracemalloc làm chậm khoảng 14 lần.
        result = benchmark_algorithm(algo_name, algo_func, puzzle,
                                     measure_memory=(r * c <= WARN_SIZE * WARN_SIZE))

        if not result["steps"]:
            print("Không tìm thấy lời giải cho cấu hình này.")
            continue

        ok, msg = validate_solution(puzzle, result["board"])
        print(f"Kiểm chứng lời giải: {'HỢP LỆ' if ok else 'KHÔNG HỢP LỆ'} ({msg})")

        print("\nBÀN CỜ ĐÃ GIẢI XONG (DẠNG KÝ TỰ):")
        print(puzzle.format_board(result["board"]))

        print("\nĐang mở giao diện trực quan Pygame...")
        print("• Nhấn phím SPACE: Bật / Dừng chế độ tự động chạy")
        print("• Nhấn phím MŨI TÊN PHẢI: Chạy từng bước (step-by-step)")
        print("• Nhấn phím R: Đặt lại trạng thái ban đầu")
        print("• Kéo giãn cửa sổ: bàn cờ tự căn lại cho vừa cửa sổ")

        try:
            from pipes_gui import run_gui
            run_gui(grid, result["steps"], source_pos=source_pos)
        except ImportError:
            print("(Bỏ qua demo trực quan: chưa cài pygame. "
                  "Cài bằng: pip install pygame)")
            print(f"(Python đang dùng: {sys.executable})")
        except Exception as exc:
            print(f"(Bỏ qua demo trực quan: {exc})")
            print(f"(Python đang dùng: {sys.executable})")


if __name__ == "__main__":
    main()
