import sys
from pipes_solver import PipesPuzzle, solve_dfs, solve_astar, benchmark_algorithm
from pipes_gui import run_gui
from puzzle_generator import generate_random_pipes

def choose_algorithm():
    print("\nChọn giải thuật để giải:")
    print("  [1] Blind Search (DFS)")
    print("  [2] Heuristic Search (A*)")
    while True:
        choice = input("Lựa chọn giải thuật (1 hoặc 2): ").strip()
        if choice == '1':
            return "Blind Search (DFS)", solve_dfs
        elif choice == '2':
            return "Heuristic Search (A*)", solve_astar
        print("Lựa chọn không hợp lệ. Vui lòng nhập 1 hoặc 2.")

def main():
    while True:
        print("\n" + "=" * 55)
        print("      CHƯƠNG TRÌNH SINH VÀ GIẢI BÀI TOÁN PIPES (AI LAB)  ")
        print("=" * 55)
        print("1. Sinh ngẫu nhiên bàn cờ (Kích thước tùy chọn NxM)")
        print("0. Thoát chương trình")
        print("-" * 55)

        choice = input("Nhập lựa chọn của bạn (0-1): ").strip()

        if choice == '0':
            print("Đã thoát chương trình.")
            sys.exit(0)
        elif choice != '1':
            print("Lựa chọn không hợp lệ. Vui lòng chọn 1 hoặc 0!")
            continue

        # Nhập kích thước bàn cờ
        try:
            r_str = input("Nhập số hàng (ví dụ 4, 5, 8, 12): ").strip()
            c_str = input("Nhập số cột (ví dụ 4, 5, 8, 12): ").strip()
            r = int(r_str)
            c = int(c_str)
        except ValueError:
            print("Lỗi: Vui lòng nhập số nguyên hợp lệ!")
            continue

        if r < 2 or c < 2:
            print("Kích thước bàn cờ tối thiểu là 2x2!")
            continue

        print(f"\nĐang sinh ngẫu nhiên bàn cờ {r}x{c} liên thông hợp lệ (100% có nghiệm)...")
        grid = generate_random_pipes(r, c)
        source_pos = (r // 2, c // 2)

        # Chọn giải thuật
        algo_name, algo_func = choose_algorithm()

        # Khởi tạo bài toán và đo đạc
        puzzle = PipesPuzzle(grid)
        result = benchmark_algorithm(algo_name, algo_func, puzzle)

        if not result["steps"]:
            print("Không tìm thấy lời giải cho cấu hình này.")
            continue

        # In kết quả dạng text
        print("\nBÀN CỜ ĐÃ GIẢI XONG (DẠNG KÝ TỰ):")
        print(puzzle.format_board(result["board"]))

        # Mở giao diện trực quan Pygame
        print("\nĐang mở giao diện trực quan Pygame...")
        print("• Nhấn phím SPACE: Bật / Dừng chế độ tự động chạy")
        print("• Nhấn phím MŨI TÊN PHẢI: Chạy từng bước (step-by-step)")
        print("• Nhấn phím R: Đặt lại trạng thái ban đầu")
        run_gui(grid, result["steps"], source_pos=source_pos)

if __name__ == "__main__":
    main()