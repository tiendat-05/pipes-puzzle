# Pipes Puzzle Solver

Giải bài toán Pipes trên lưới N × M bằng hai hướng tiếp cận: tìm kiếm mù
(DFS kết hợp quay lui) và tìm kiếm có thông tin (A*).

## 1. Cài đặt và chạy

```bash
pip install -r requirements.txt      # pygame, matplotlib, numpy
```

| Việc cần làm | Lệnh |
|---|---|
| Chơi thử / demo từng bước | `python main.py` |
| Đo đạc thực nghiệm (5 input × 3 kích thước) | `python run_experiments.py` |
| Vẽ lại 3 biểu đồ | `python plot_results.py` |
| Chạy toàn bộ kiểm tra | `python tests/selfcheck.py` |
| So sánh các kiểu tie-breaking | `python tests/bench-tie-modes.py` |
| Khảo sát theo kích thước bàn cờ | `python tests/bench-sizes.py` |

Mã nguồn tự ép stdout sang UTF-8 nên chạy được trực tiếp trên Windows.

Cửa sổ demo tự chọn kích thước ô theo độ phân giải màn hình và tự căn lại khi
kéo giãn cửa sổ, nên toàn bộ bàn cờ cùng thanh trạng thái luôn hiển thị đầy đủ
ở mọi kích thước lưới từ 5×5 tới 30×30.

> **Chạy bằng VS Code:** mở đúng thư mục `btl1_pipes_main` và chọn interpreter
> có cài `pygame` (Ctrl+Shift+P → *Python: Select Interpreter*). Nếu chạy ở chế
> độ *Interactive Window* (Jupyter) thì cửa sổ pygame không hiện — phải chạy
> trong Terminal. Nếu cửa sổ đã mở mà không thấy, kiểm tra thanh taskbar hoặc
> Alt+Tab (cửa sổ có thể nằm dưới cửa sổ VS Code).

## 2. Cấu trúc

```
btl1_pipes_main/
├── pipes_solver.py        # bitmask, DFS, A*, kiểm tra lời giải
├── puzzle_generator.py    # sinh bàn cờ bằng Prim có khống chế bậc
├── pipes_gui.py           # demo trực quan Pygame
├── main.py                # giao diện dòng lệnh
├── run_experiments.py     # đo đạc, xuất benchmark_summary.json
├── plot_results.py        # vẽ 3 biểu đồ
├── benchmark_summary.json # số liệu trung bình
├── requirements.txt
├── README.md
└── tests/
    ├── selfcheck.py
    ├── bench-tie-modes.py
    └── bench-sizes.py
```

## 3. Mô hình bài toán

Mỗi ô là một mảnh ống thuộc đúng một trong bốn loại: End, Straight, Corner,
T-piece. Mỗi hướng nối được mã hóa bằng một bit (N = 1, E = 2, S = 4, W = 8),
trạng thái của một ô là phép OR các bit tương ứng. Mảnh chữ thập (4 đầu nối)
không được hỗ trợ nên bậc tối đa của một ô là 3.

Các ô được gán hướng xoay lần lượt theo thứ tự hàng, nên khi gán ô (r, c) thì
hai ô (r−1, c) và (r, c−1) đã có giá trị. Ràng buộc cục bộ chỉ cần kiểm tra:

- không có đầu nối nào chĩa ra ngoài biên;
- bit N của ô hiện tại khớp với bit S của ô phía trên;
- bit W của ô hiện tại khớp với bit E của ô bên trái.

Ràng buộc liên thông toàn cục được kiểm tra tại nút lá bằng BFS từ ô (0, 0).

Nhờ thứ tự gán này, hệ số nhánh hiệu dụng giảm từ 4 xuống không quá 2 với mỗi
ô, và nhiều ô chỉ còn đúng một lựa chọn.

## 4. Vì sao A* cần tie-breaking

Với `g(n) = k` (số ô đã gán) và `h(n) = N·M − k` (số ô còn lại):

```
f(n) = g(n) + h(n) = N·M        (hằng số, với mọi nút)
```

`h` ở đây là ước lượng **chính xác tuyệt đối**, nên không tồn tại heuristic
admissible nào làm `f` khác nhau giữa các nút cùng tầng. Hàng đợi ưu tiên khi đó
sắp xếp theo `(f, g)`, và vì `f` bằng nhau nên luôn lấy nút nông hơn trước —
A* duyệt đúng theo từng tầng, tức là tìm kiếm theo chiều rộng.

Kiểm chứng: trên bàn 12×12 seed 305, tập mọi giá trị `f` quan sát được chỉ là
`{144}` — đúng một giá trị, bằng `R×C`.

Cách xử lý là phá thế đồng hạng bằng một độ đo triển vọng của trạng thái
(tie-breaking). Tie-break chỉ đổi thứ tự giữa các nút **cùng** `f` nên không
ảnh hưởng tính đầy đủ và tính tối ưu của A*.

Chương trình cài đặt 5 kiểu tie-break, chọn qua tham số `tie_mode`:

| `tie_mode` | Ý tưởng | Chi phí |
|---|---|---|
| `"none"` | Không phá hòa, khóa phụ là `g` | — |
| `"components"` | Ưu tiên ít thành phần liên thông hơn | O(N)/nút |
| `"edges"` | Ưu tiên đã ghép nhiều cạnh hơn | O(1)/nút |
| `"nextmrv"` | Ưu tiên ô kế tiếp bị ràng buộc chặt nhất (forward checking) | O(1)/nút |
| `"mixed"` | MRV, rồi số cạnh, rồi độ sâu | O(1)/nút |

Mặc định là `"nextmrv"` vì cho ít nút nhất (xem `tests/bench-tie-modes.py`).

Kết quả đo trên bộ 15 mẫu (trung bình số node mở rộng):

| Cấu hình | 5×5 | 8×8 | 12×12 |
|---|---|---|---|
| A* không tie-break (`none`) | 50.0 | 150.0 | 1243.4 |
| A* có tie-break (`nextmrv`) | **43.2** | **99.8** | **367.6** |
| DFS (mốc so sánh) | 48.2 | 119.8 | 586.6 |

Ở 12×12, tie-breaking giảm khoảng 70% số nút so với không tie-break, và A* mở
rộng ít nút hơn DFS ở cả ba kích thước.

## 5. Kiểm chứng

`python tests/selfcheck.py` kiểm tra 4 nhóm:

1. **Lời giải hợp lệ:** cả 15 mẫu × 2 giải thuật đều cho lời giải đúng, đủ 25/64/144 bước.
2. **Hồi quy:** số node của DFS và của A* `none` (15 giá trị mỗi loại) trùng khớp
   chính xác với số liệu chuẩn.
3. **Đệ quy:** giới hạn đệ quy được nâng lên đúng lúc chạy và phục hồi sau khi xong;
   đệ quy sâu 2500 khung hình chạy được.
4. **RNG:** `generate_random_pipes()` không làm thay đổi trạng thái RNG toàn cục.

Kết quả hiện tại: tất cả đều đạt.

## 6. Giới hạn của bài toán

Bàn cờ từ khoảng 20×20 trở lên khiến cả DFS lẫn A* chạy rất lâu, vì độ phức tạp
của bài toán là hàm mũ theo số ô. Đây là bản chất bài toán, không phải lỗi cài đặt:

- `main.py` giới hạn kích thước 2×2 … 30×30 và cảnh báo từ 16×16.
- Bộ thực nghiệm chính thức dừng ở 12×12.

Từ 16×16 trở lên, chế độ demo **không đo bộ nhớ** nữa: `tracemalloc` làm chương
trình chậm khoảng 14 lần (24×24: 57,6 s → 5,0 s) trong khi số node và lời giải
không đổi. Phần đo bộ nhớ vẫn được giữ nguyên trong `run_experiments.py`, nên
các bảng số liệu thực nghiệm không bị ảnh hưởng.

Muốn mở rộng lên bàn lớn hơn thì cần cải tiến thuật toán (chọn biến động theo
MRV, heuristic dựa trên số thành phần liên thông, IDA* để giảm bộ nhớ).
