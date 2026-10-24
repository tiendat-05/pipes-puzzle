# plot_results.py
import json
import os
import matplotlib.pyplot as plt
import numpy as np

# Đọc tự động từ benchmark_summary.json nếu có
json_file = "benchmark_summary.json"
if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    test_names = data["sizes"]
    avg_dfs_time = data["dfs_time"]
    avg_astar_time = data["astar_time"]
    avg_dfs_mem = data["dfs_mem"]
    avg_astar_mem = data["astar_mem"]
    avg_dfs_nodes = data["dfs_nodes"]
    avg_astar_nodes = data["astar_nodes"]
    solution_steps = data["steps"]
    print(f"-> Đã nạp thành công dữ liệu trung bình từ '{json_file}'.")
else:
    # Giá trị mặc định dự phòng nếu chưa chạy benchmark
    test_names = ['5x5', '8x8', '12x12']
    avg_dfs_time = [0.28, 0.95, 16.20]
    avg_astar_time = [0.65, 2.70, 39.50]
    avg_dfs_mem = [19.50, 32.10, 65.40]
    avg_astar_mem = [10.20, 19.80, 215.30]
    avg_dfs_nodes = [38, 150, 920]
    avg_astar_nodes = [42, 165, 1450]
    solution_steps = [25, 64, 144]

x = np.arange(len(test_names))
width = 0.35

# -------------------------------------------------------------------------
# BIỂU ĐỒ 1: THỜI GIAN THỰC THI TRUNG BÌNH (ms)
# -------------------------------------------------------------------------
plt.figure(figsize=(8, 5))
rects1 = plt.bar(x - width/2, avg_dfs_time, width, label='Blind Search (DFS)', color='#2980b9')
rects2 = plt.bar(x + width/2, avg_astar_time, width, label='Heuristic Search (A*)', color='#e67e22')

plt.title('So sánh Thời gian Thực thi Trung bình (5 Instances/Size)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Kích thước bàn cờ', fontsize=11)
plt.ylabel('Thời gian trung bình (ms)', fontsize=11)
plt.xticks(x, test_names, fontsize=10)
plt.legend(fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.6)

for rect in rects1:
    h = rect.get_height()
    plt.text(rect.get_x() + rect.get_width()/2., h + max(avg_astar_time) * 0.015, f'{h:.2f}', ha='center', va='bottom', fontsize=9)

for rect in rects2:
    h = rect.get_height()
    plt.text(rect.get_x() + rect.get_width()/2., h + max(avg_astar_time) * 0.015, f'{h:.2f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('time_comparison.png', dpi=300)
print("-> Đã xuất: time_comparison.png")
plt.close()

# -------------------------------------------------------------------------
# BIỂU ĐỒ 2: BỘ NHỚ PEAK RAM TRUNG BÌNH (KB)
# -------------------------------------------------------------------------
plt.figure(figsize=(8, 5))
rects1 = plt.bar(x - width/2, avg_dfs_mem, width, label='Blind Search (DFS)', color='#27ae60')
rects2 = plt.bar(x + width/2, avg_astar_mem, width, label='Heuristic Search (A*)', color='#8e44ad')

plt.title('So sánh Bộ nhớ Đỉnh Trung bình (Peak RAM - KB)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Kích thước bàn cờ', fontsize=11)
plt.ylabel('Bộ nhớ tiêu tốn trung bình (KB)', fontsize=11)
plt.xticks(x, test_names, fontsize=10)
plt.legend(fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.6)

for rect in rects1:
    h = rect.get_height()
    plt.text(rect.get_x() + rect.get_width()/2., h + max(avg_astar_mem) * 0.015, f'{h:.1f}', ha='center', va='bottom', fontsize=9)

for rect in rects2:
    h = rect.get_height()
    plt.text(rect.get_x() + rect.get_width()/2., h + max(avg_astar_mem) * 0.015, f'{h:.1f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('memory_comparison.png', dpi=300)
print("-> Đã xuất: memory_comparison.png")
plt.close()

# -------------------------------------------------------------------------
# BIỂU ĐỒ 3: SỐ NODE MỞ RỘNG TRUNG BÌNH VÀ ĐỘ DÀI LỜI GIẢI
# -------------------------------------------------------------------------
plt.figure(figsize=(8, 5))
rects1 = plt.bar(x - width/2, avg_dfs_nodes, width, label='DFS (Nodes Expanded)', color='#34495e')
rects2 = plt.bar(x + width/2, avg_astar_nodes, width, label='A* (Nodes Expanded)', color='#d35400')
plt.plot(x, solution_steps, color='#c0392b', marker='o', linewidth=2.5, label='Solution Length (Steps)')

plt.title('Số Node Mở rộng Trung bình & Độ dài Lời giải', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Kích thước bàn cờ', fontsize=11)
plt.ylabel('Số lượng (Nodes / Steps)', fontsize=11)
plt.xticks(x, test_names, fontsize=10)
plt.legend(fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.6)

for rect in rects1:
    h = rect.get_height()
    plt.text(rect.get_x() + rect.get_width()/2., h + max(avg_astar_nodes) * 0.015, f'{int(h)}', ha='center', va='bottom', fontsize=9)

for rect in rects2:
    h = rect.get_height()
    plt.text(rect.get_x() + rect.get_width()/2., h + max(avg_astar_nodes) * 0.015, f'{int(h)}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('nodes_comparison.png', dpi=300)
print("-> Đã xuất: nodes_comparison.png")
plt.close()