# Hướng dẫn cách chạy chương trình:

---

## Cài đặt môi trường
Yêu cầu **Python 3.8+**. Khuyến nghị chạy trên môi trường Linux/WSL2.
Cài đặt thư viện **pygame**:
```bash
pip install pygame matplotlib numpy
```
---
## Cách chạy chương trình

### Chạy chương trình chính (CLI + Demo trực quan):
```bash
python3 main.py
```

### Chạy đo đạc thực nghiệm:
```bash
python3 run_experiments.py
```

### Vẽ và xuất biểu đồ:
```bash
python3 plot_results.py
```

---

## Cấu trúc thư mục:

```text
pipes/
├── pipes_solver.py        # Mô hình hóa trạng thái, bitmask, giải thuật DFS và A*
├── pipes_gui.py           # Giao diện đồ họa Step-by-Step bằng Pygame
├── puzzle_generator.py    # Thuật toán Prim sinh bàn cờ ngẫu nhiên hợp lệ
├── main.py                # Giao diện dòng lệnh chính kết nối Solver và GUI
├── run_experiments.py     # Script đo đạc thực nghiệm 5 input/size
├── plot_results.py        # Script vẽ 3 biểu đồ từ dữ liệu JSON
├── benchmark_summary.json # File dữ liệu kết quả đo đạc trung bình
├── time_comparison.png    # Biểu đồ thời gian thực thi
├── memory_comparison.png  # Biểu đồ bộ nhớ RAM
├── nodes_comparison.png   # Biểu đồ số node mở rộng
├── run_experiments_old.py # Script đo đạc cũ (tạm thời không dùng)
└── README.md              # Tài liệu hướng dẫn
```